"""Durable owner-triggered sequential PNG batch orchestration.

This module contains no solver. Each queued source is dispatched exactly once
at a time through the existing Studio ``run_pipeline`` contract after an
explicit Run Entire Batch command. Pipeline calls remain the canonical solver,
replay, Difficulty V1, QA, and READY_AUTO Release Pool implementation.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import threading
import uuid
from typing import Any


JOB_SCHEMA = "scrubbots-studio-png-sequential-batch"
JOB_VERSION = 1
MAX_BATCH_ITEMS = 150
MAX_JOB_BYTES = 1024 * 1024
_PROCESS_LOCKS: dict[str, threading.Lock] = {}
_PROCESS_LOCKS_GUARD = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def largest_remainder_quotas(count: int) -> dict[int, int]:
    """Return exact integer quotas for 45/40/15, with stable 3/4/5 ties."""
    if type(count) is not int or count < 0 or count > MAX_BATCH_ITEMS:
        raise ValueError(f"batch size must be an integer between 0 and {MAX_BATCH_ITEMS}")
    weights = ((3, 45), (4, 40), (5, 15))
    exact = {columns: count * weight / 100.0 for columns, weight in weights}
    quotas = {columns: int(exact[columns]) for columns, _weight in weights}
    remaining = count - sum(quotas.values())
    order = sorted(weights, key=lambda pair: (-(exact[pair[0]] - quotas[pair[0]]), pair[0]))
    for columns, _weight in order[:remaining]:
        quotas[columns] += 1
    return quotas


def assign_columns(source_ids: Sequence[str]) -> list[int]:
    """Distribute exact quotas evenly through input order, deterministically."""
    quotas = largest_remainder_quotas(len(source_ids))
    assigned = Counter()
    output: list[int] = []
    total = len(source_ids)
    for index in range(total):
        remaining_slots = total - index
        choices = [columns for columns in (3, 4, 5) if assigned[columns] < quotas[columns]]
        # Highest cumulative deficit spreads each mode while preserving its quota.
        columns = max(choices, key=lambda value: ((index + 1) * quotas[value] / total - assigned[value], -value))
        assigned[columns] += 1
        output.append(columns)
    return output


def _root() -> Path:
    from .studio_extensions import extensions_root

    return extensions_root() / "png-batches"


def _job_path(job_id: str) -> Path:
    if not isinstance(job_id, str) or not job_id.startswith("png-batch-") or len(job_id) > 80 or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in job_id):
        raise ValueError("PNG batch job identity is malformed")
    return _root() / "jobs" / f"{job_id}.json"


def _control_path(job_id: str) -> Path:
    return _root() / "control" / f"{job_id}.json"


def _seal(payload: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result.pop("state_digest", None)
    result["state_digest"] = hashlib.sha256(_canonical(result)).hexdigest()
    return result


def _read_job(job_id: str) -> dict[str, Any]:
    path = _job_path(job_id)
    raw = path.read_bytes()
    if len(raw) > MAX_JOB_BYTES:
        raise ValueError("PNG batch job exceeds the bounded one-megabyte state limit")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict) or value.get("schema") != JOB_SCHEMA or value.get("version") != JOB_VERSION or value.get("job_id") != job_id:
        raise ValueError("PNG batch job schema or identity is invalid")
    digest = value.get("state_digest")
    unsigned = dict(value)
    unsigned.pop("state_digest", None)
    if not isinstance(digest, str) or hashlib.sha256(_canonical(unsigned)).hexdigest() != digest:
        raise ValueError("PNG batch job state digest is invalid")
    return value


def _write_job(payload: Mapping[str, Any]) -> dict[str, Any]:
    sealed = _seal(payload)
    raw = _canonical(sealed)
    if len(raw) > MAX_JOB_BYTES:
        raise ValueError("PNG batch job exceeds the bounded one-megabyte state limit")
    path = _job_path(str(sealed.get("job_id", "")))
    path.parent.mkdir(parents=True, exist_ok=True)
    write_path = path.with_name(path.name + f".{uuid.uuid4().hex}.part")
    try:
        with write_path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(write_path, path)
    finally:
        if write_path.exists():
            write_path.unlink()
    return sealed


@contextmanager
def _job_lock(job_id: str):
    key = str(_job_path(job_id))
    with _PROCESS_LOCKS_GUARD:
        lock = _PROCESS_LOCKS.setdefault(key, threading.Lock())
    if not lock.acquire(blocking=False):
        raise ValueError("another sequential runner already owns this PNG batch")
    lock_path = _root() / "locks" / f"{job_id}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    try:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, BlockingIOError) as exc:
            raise ValueError("another process is already running this PNG batch") from exc
        yield
    finally:
        try:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        handle.close()
        lock.release()


def _counts(items: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    states = Counter(str(item.get("status", "UNKNOWN")) for item in items)
    return {
        "total": len(items), "ready": states["READY"], "failed": states["FAILED"],
        "rejected": states["REJECTED"], "skipped": states["SKIPPED_DUPLICATE"],
        "remaining": sum(states[name] for name in ("QUEUED", "RUNNING", "VERIFYING_EXISTING")),
    }


def _has_ready_pipeline_proof(
    pipeline: Mapping[str, Any],
    source_id: str,
    *,
    expected_columns: int | None = None,
    source_record_sha256: str | None = None,
    job: Mapping[str, Any] | None = None,
    item: Mapping[str, Any] | None = None,
) -> bool:
    """Require canonical solver, replay, Difficulty V1, load-check, and QA proof."""
    primary = pipeline.get("primary", {})
    if not isinstance(primary, Mapping):
        return False
    result = primary.get("result", {})
    if not isinstance(result, Mapping):
        return False
    replay = result.get("solution_replay", {})
    if not isinstance(replay, Mapping):
        return False
    load_check = primary.get("load_check", {})
    if not isinstance(load_check, Mapping):
        return False
    stages = pipeline.get("stages", [])
    qa_pass = isinstance(stages, Sequence) and not isinstance(stages, (str, bytes)) and any(
        isinstance(stage, Mapping) and stage.get("stage") == "QA" and stage.get("disposition") == "PASS"
        for stage in stages
    )
    request = pipeline.get("request", {})
    if not isinstance(request, Mapping):
        return False
    if pipeline.get("source_id") not in (None, source_id) or request.get("source_id") != source_id:
        return False
    if item is not None and request.get("activity_source_sha256") != str(item.get("source_sha256", "")):
        return False
    if item is not None and request.get("activity_source_record_sha256") not in (None, item.get("source_record_sha256")):
        return False
    if source_record_sha256 is not None:
        binding = pipeline.get("owner_source_binding")
        if binding is not None and (
            not isinstance(binding, Mapping)
            or binding.get("source_id") != source_id
            or binding.get("source_sha256") != item.get("source_sha256")
            or binding.get("source_record_sha256") != source_record_sha256
        ):
            return False
    if job is not None and (
        request.get("png_batch_job_id") != job.get("job_id")
        or request.get("png_batch_item_index") != item.get("index")
        or request.get("png_batch_attempt_id") != item.get("attempt_id")
        or request.get("column_count") != item.get("column_count")
        or not request.get("activity_run_id")
    ):
        return False
    actual_columns = result.get("column_count")
    if actual_columns is None:
        actual_columns = primary.get("column_count")
    if expected_columns is not None and actual_columns != expected_columns:
        return False
    return (
        pipeline.get("disposition") == "READY"
        and bool(pipeline.get("candidate_id"))
        and primary.get("state") == "READY"
        and result.get("solver_status") == "SOLVED"
        and result.get("solution_final") == "WIN"
        and replay.get("ok") is True
        and replay.get("solved") is True
        and replay.get("finalActive") == 0
        and str(result.get("difficulty_basis", "")).startswith("ScrubBots Difficulty V1")
        and load_check.get("state") == "READY"
        and qa_pass
    )


def _verify_column_artifacts(pipeline: Mapping[str, Any], expected_columns: int) -> bool:
    """Verify the persisted result and supply-plan agree with the assigned quota."""
    primary = pipeline.get("primary", {})
    result = primary.get("result", {}) if isinstance(primary, Mapping) else {}
    files = primary.get("files", {}) if isinstance(primary, Mapping) else {}
    if not isinstance(result, Mapping) or not isinstance(files, Mapping):
        return False
    if result.get("column_count") != expected_columns or primary.get("column_count") != expected_columns:
        return False
    try:
        result_path = Path(str(files.get("result", "")))
        plan_path = Path(str(files.get("supply_plan", "")))
        level_path = Path(str(files.get("level", "")))
        if not result_path.is_file() or not plan_path.is_file() or not level_path.is_file():
            return False
        stored_result = json.loads(result_path.read_text(encoding="utf-8"))
        supply_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        artifact_hashes = {
            "level": hashlib.sha256(level_path.read_bytes()).hexdigest(),
            "supply_plan": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
            "result": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        }
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    saved_hashes = primary.get("artifact_sha256")
    if saved_hashes is not None and saved_hashes != artifact_hashes:
        return False
    if stored_result != dict(result) or supply_plan.get("columnCount") != expected_columns:
        return False
    try:
        from .supply_pipeline.scrubpack_identity import derive_solver_supply_identity

        identity = derive_solver_supply_identity(
            level_path.read_bytes(), plan_path.read_bytes(), stored_result, primary.get("authority", {}),
        )
    except (OSError, ValueError, TypeError):
        return False
    return identity == primary.get("solver_supply_identity")


def _candidate_has_source_lineage(candidate: Mapping[str, Any], source_id: str, source_sha256: str) -> bool:
    from .studio_extensions import _repository_root
    from .output.bundle import read_bundle

    try:
        bundle_path = (_repository_root() / str(candidate.get("source_path", ""))).resolve()
        bundle = read_bundle(bundle_path)
    except (OSError, ValueError, KeyError):
        return False
    metadata = bundle.metadata.get("generator_metadata", {})
    payload = metadata.get("payload", {}) if isinstance(metadata, Mapping) else {}
    data = payload.get("data", {}) if isinstance(payload, Mapping) else {}
    lineage = data.get("source_lineage", {}) if isinstance(data, Mapping) else {}
    return (
        isinstance(lineage, Mapping)
        and lineage.get("source_id") == source_id
        and lineage.get("source_sha256") == source_sha256
        and lineage.get("derivation") == "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE"
        and candidate.get("artwork_sha256") == hashlib.sha256(bundle.artwork_png).hexdigest()
        and candidate.get("grid_hash") == bundle.artwork.grid_hash
    )


def _pool_row_matches(run: Mapping[str, Any], candidate: Mapping[str, Any], source_id: str, expected_columns: int) -> bool:
    from .studio_extensions import _read_json, extensions_root
    from .supply_pipeline.release_pool import release_entries

    run_id = run.get("run_id")
    candidate_id = candidate.get("candidate_id")
    try:
        entries = release_entries()
        entry = next((row for row in entries if row.get("candidate_id") == candidate_id and row.get("pipeline_run_id") == run_id), None)
        if entry is None:
            return False
        if entry.get("source_id", source_id) != source_id or entry.get("column_count", expected_columns) != expected_columns:
            return False
        binding = run.get("owner_source_binding", {})
        if binding and binding.get("source_id") != source_id:
            return False
        files = run.get("primary", {}).get("files", {})
        plan = json.loads(Path(str(files.get("supply_plan", ""))).read_text(encoding="utf-8"))
        if plan.get("columnCount") != expected_columns:
            return False
        row = next(
            path for path in (extensions_root() / "release-pool").glob("*.json")
            if _read_json(path).get("candidate_id") == candidate_id
            and _read_json(path).get("pipeline_run_id") == run_id
        )
        saved = _read_json(row)
        pipeline_path = extensions_root() / "pipelines" / f"{run_id}.json"
        if not pipeline_path.is_file() or saved.get("pipeline_sha256") != hashlib.sha256(pipeline_path.read_bytes()).hexdigest():
            return False
        return (
            saved.get("entry_digest") == entry.get("entry_digest")
            and saved.get("candidate_id") == candidate_id
            and saved.get("pipeline_run_id") == run_id
            and saved.get("source_id", source_id) == source_id
            and saved.get("column_count", expected_columns) == expected_columns
            and all(saved.get("files", {}).get(key, {}).get("sha256") == hashlib.sha256(Path(str(files.get(key, ""))).read_bytes()).hexdigest() for key in ("level", "supply_plan"))
        )
    except (OSError, ValueError, StopIteration, TypeError, KeyError, AttributeError, json.JSONDecodeError):
        return False


def _verify_sources(items: Sequence[Mapping[str, Any]], settings: Mapping[str, Any]) -> list[dict[str, Any]]:
    from .studio_extensions import validate_owner_source, verify_owner_source

    result: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for index, raw in enumerate(items):
        source_id = str(raw.get("source_id", ""))
        display_name = str(raw.get("display_path", raw.get("display_filename", source_id)))[:240]
        item: dict[str, Any] = {"index": index, "source_id": source_id, "display_name": display_name, "status": "REJECTED", "reason": "SOURCE_IDENTITY_INVALID"}
        if raw.get("disposition") not in {"IMPORTED", "ALREADY_IMPORTED"}:
            item["reason"] = str(raw.get("error", raw.get("disposition", "IMPORT_REJECTED")))[:512]
            result.append(item)
            continue
        try:
            proof = verify_owner_source(source_id, source_directory=settings.get("source_directory"))
            source_sha = str(proof.get("source_sha256", ""))
            if source_id != "owner-upload-" + source_sha or len(source_sha) != 64:
                raise ValueError("source ID and verified PNG SHA-256 disagree")
            from .studio_extensions import _source_record_paths

            record_path, _source_path = _source_record_paths(source_id, settings.get("source_directory"))
            record_sha = hashlib.sha256(record_path.read_bytes()).hexdigest()
            if raw.get("source_sha256") not in (None, source_sha):
                raise ValueError("SOURCE_SNAPSHOT_PNG_SHA256_MISMATCH")
            if raw.get("source_record_sha256") not in (None, record_sha):
                raise ValueError("SOURCE_SNAPSHOT_RECORD_SHA256_MISMATCH")
            item.update({"source_sha256": source_sha, "source_record_sha256": record_sha, "original_filename": str(proof.get("original_filename", display_name))[:240]})
            proof = validate_owner_source(
                source_id, persist=False, game_project=settings.get("game_project"),
                source_directory=settings.get("source_directory"),
            )
            if (not proof.get("exact_logical_source")
                    or proof.get("structural", {}).get("disposition") != "PASS"
                    or proof.get("void_capability", {}).get("state") not in (None, "OPEN", "NOT_REQUIRED")):
                raise ValueError(str(proof.get("reason", proof.get("structural", {}).get("reason", "CANONICAL_SOURCE_VALIDATION_FAILED"))))
            item.update({"status": "QUEUED", "reason": ""})
            if source_sha in seen:
                item.update({"status": "SKIPPED_DUPLICATE", "reason": "DUPLICATE_SOURCE_SHA256", "duplicate_of": seen[source_sha]})
            else:
                seen[source_sha] = source_id
        except Exception as exc:
            item["reason"] = str(exc)[:512]
        result.append(item)
    return result


def create_png_batch(batch_id: str, settings: Mapping[str, Any] | None = None) -> dict[str, Any]:
    from .studio_extensions import _digest, batch_load

    imported = batch_load(batch_id)["batch"]
    if not isinstance(imported.get("items"), list) or len(imported["items"]) > MAX_BATCH_ITEMS:
        raise ValueError(f"an imported PNG batch must contain at most {MAX_BATCH_ITEMS} entries")
    snapshot = dict(settings or {})
    # The UI may configure only canonical bounded pipeline request fields.
    allowed = {"game_project", "source_directory", "background_intent", "seed", "candidates", "verify_top", "screen_budget", "metric_top", "viability_budget", "real_max_visited", "solver_timeout_seconds"}
    if set(snapshot) - allowed:
        raise ValueError("PNG batch settings include unsupported fields")
    source_items = _verify_sources(imported["items"], snapshot)
    eligible = [item for item in source_items if item["status"] == "QUEUED"]
    assignments = assign_columns([str(item["source_id"]) for item in eligible])
    assignment_by_id = {str(item["source_id"]): columns for item, columns in zip(eligible, assignments, strict=True)}
    for item in source_items:
        item["column_count"] = assignment_by_id.get(str(item["source_id"]))
    immutable_plan = {"batch_id": batch_id, "batch_digest": _digest(imported), "settings": snapshot, "items": source_items}
    plan_digest = _digest(immutable_plan)
    job_id = f"png-batch-{plan_digest[:32]}"
    path = _job_path(job_id)
    if path.exists():
        existing = _read_job(job_id)
        if existing.get("plan_digest") != plan_digest:
            raise ValueError("PNG batch ID collides with an existing plan")
        return {"state": "SUCCESS", "disposition": "EXISTING", "job": existing}
    job = {
        "schema": JOB_SCHEMA, "version": JOB_VERSION, "job_id": job_id,
        "import_batch_id": batch_id, "batch_digest": immutable_plan["batch_digest"],
        "snapshot_source_count": len(imported["items"]),
        "plan_digest": plan_digest, "settings": snapshot, "state": "QUEUED",
        "created_at": _now(), "updated_at": _now(), "current_index": None,
        "items": source_items, "counts": _counts(source_items),
        "planned_quotas": {str(key): value for key, value in largest_remainder_quotas(len(eligible)).items()},
        "ready_mix": {"3": 0, "4": 0, "5": 0},
    }
    saved = _write_job(job)
    return {"state": "SUCCESS", "disposition": "CREATED", "job": saved}


def retry_failed_png_batch(job_id: str) -> dict[str, Any]:
    """Create a separate deterministic retry job for FAILED items only."""
    from .studio_extensions import _digest

    original = _read_job(job_id)
    if original.get("state") != "COMPLETE":
        return {"state": "BLOCKED", "disposition": "BATCH_NOT_FINISHED", "job": original}
    failed = [item for item in original.get("items", []) if item.get("status") == "FAILED"]
    if not failed:
        return {"state": "BLOCKED", "disposition": "NO_RETRYABLE_FAILURES", "job": original}
    items: list[dict[str, Any]] = []
    for index, previous in enumerate(failed):
        items.append({
            "index": index, "prior_item_index": previous.get("index"),
            "source_id": previous.get("source_id"), "source_sha256": previous.get("source_sha256"),
            "source_record_sha256": previous.get("source_record_sha256"),
            "display_name": previous.get("display_name", previous.get("original_filename", "")),
            "original_filename": previous.get("original_filename", previous.get("display_name", "")),
            "status": "QUEUED", "reason": "", "column_count": previous.get("column_count"),
            "prior_attempt": {key: previous.get(key) for key in (
                "attempt_id", "activity_run_id", "run_id", "status", "reason", "started_at", "finished_at",
            )},
        })
    retry_basis = {
        "retry_of_job_id": job_id, "retry_of_state_digest": original.get("state_digest"),
        "batch_digest": original.get("batch_digest"), "items": items,
    }
    plan_digest = _digest(retry_basis)
    retry_id = f"png-batch-retry-{plan_digest[:32]}"
    path = _job_path(retry_id)
    if path.exists():
        existing = _read_job(retry_id)
        if existing.get("plan_digest") != plan_digest:
            raise ValueError("retry job identity collides with a different failed-item snapshot")
        return {"state": "SUCCESS", "disposition": "EXISTING_RETRY", "job": existing}
    quotas = Counter(int(item["column_count"]) for item in items if item.get("column_count") in (3, 4, 5))
    job = {
        "schema": JOB_SCHEMA, "version": JOB_VERSION, "job_id": retry_id,
        "import_batch_id": original.get("import_batch_id"), "batch_digest": original.get("batch_digest"),
        "parent_job_id": job_id, "parent_job_state_digest": original.get("state_digest"),
        "retry_of_failed_only": True, "plan_digest": plan_digest,
        "settings": dict(original.get("settings", {})), "state": "QUEUED",
        "created_at": _now(), "updated_at": _now(), "current_index": None,
        "items": items, "counts": _counts(items),
        "planned_quotas": {str(columns): quotas[columns] for columns in (3, 4, 5)},
        "ready_mix": {"3": 0, "4": 0, "5": 0},
    }
    return {"state": "SUCCESS", "disposition": "RETRY_CREATED", "job": _write_job(job)}


def batch_terminal_message(job: Mapping[str, Any], loaded_count: int | None = None) -> str:
    counts = job.get("counts", {})
    total = int(counts.get("total", 0))
    ready = int(counts.get("ready", 0))
    failed = int(counts.get("failed", 0))
    rejected = int(counts.get("rejected", 0))
    skipped = int(counts.get("skipped", 0))
    remaining = int(counts.get("remaining", 0))
    loaded = int(job.get("snapshot_source_count", total) if loaded_count is None else loaded_count)
    prefix = "FINISHED WITH FAILURES · " if job.get("state") == "COMPLETE" and (failed or rejected) else ""
    return f"{prefix}Loaded {loaded} · Job {total} · {ready} READY · {failed} FAILED · {rejected} REJECTED · {skipped} SKIPPED · {remaining} remaining"


def png_batch_status(job_id: str) -> dict[str, Any]:
    job = _read_job(job_id)
    public = dict(job)
    public["mutated"] = False
    return {"state": "SUCCESS", "disposition": "STATUS", "job": public}


def png_batch_latest(batch_id: str | None = None) -> dict[str, Any]:
    jobs: list[dict[str, Any]] = []
    job_root = _root() / "jobs"
    if job_root.exists():
        for path in sorted(job_root.glob("png-batch-*.json"), key=lambda item: item.stat().st_mtime, reverse=True)[:20]:
            try:
                jobs.append(_read_job(path.stem))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
    resumable = next((job for job in jobs if job.get("state") not in {"COMPLETE", "STOPPED"}), None)
    if batch_id is None:
        return {"state": "SUCCESS", "disposition": "LATEST", "job": resumable, "jobs": jobs, "mutated": False}
    from .studio_extensions import _digest, batch_load

    try:
        expected_digest = _digest(batch_load(batch_id)["batch"])
    except (OSError, ValueError, KeyError):
        return {"state": "BLOCKED", "disposition": "BATCH_JOB_SOURCE_MISMATCH", "job": None, "mismatch_job": resumable, "jobs": jobs, "mutated": False}
    matching = next((
        job for job in jobs
        if job.get("import_batch_id") == batch_id and job.get("batch_digest") == expected_digest
        and job.get("state") not in {"COMPLETE", "STOPPED"}
    ), None)
    mismatch = resumable if resumable is not None and matching is None else None
    return {
        "state": "SUCCESS" if matching is not None or mismatch is None else "BLOCKED",
        "disposition": "MATCHED" if matching is not None else "BATCH_JOB_SOURCE_MISMATCH" if mismatch is not None else "NO_MATCHING_JOB",
        "job": matching, "mismatch_job": mismatch, "jobs": jobs, "batch_id": batch_id,
        "batch_digest": expected_digest, "mutated": False,
    }


def png_batch_control(job_id: str, action: str) -> dict[str, Any]:
    if action not in {"PAUSE_AFTER_CURRENT", "STOP_AFTER_CURRENT"}:
        raise ValueError("batch control action is not supported")
    job = _read_job(job_id)
    if job.get("state") in {"COMPLETE", "STOPPED"}:
        return {"state": "SUCCESS", "disposition": str(job["state"]), "job": job}
    control = {"job_id": job_id, "action": action, "requested_at": _now()}
    path = _control_path(job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical(control))
    return {"state": "SUCCESS", "disposition": action, "job_id": job_id}


def _control_action(job_id: str) -> str:
    path = _control_path(job_id)
    try:
        control = json.loads(path.read_text(encoding="utf-8"))
        return str(control.get("action", "")) if control.get("job_id") == job_id else ""
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ""


def _clear_control(job_id: str) -> None:
    path = _control_path(job_id)
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _recover_attempt(job: Mapping[str, Any], item: Mapping[str, Any]) -> dict[str, Any] | None:
    from .studio_extensions import _read_json, _enter_candidate_release_pool, extensions_root, list_candidates

    pipeline_root = extensions_root() / "pipelines"
    matches = []
    if pipeline_root.exists():
        for path in pipeline_root.glob("*.json"):
            try:
                payload = _read_json(path)
            except Exception:
                continue
            request = payload.get("request", {})
            if (request.get("png_batch_job_id") == job.get("job_id")
                    and request.get("png_batch_item_index") == item.get("index")
                    and request.get("png_batch_attempt_id") == item.get("attempt_id")
                    and request.get("source_id") == item.get("source_id")
                    and request.get("activity_source_sha256") == item.get("source_sha256")
                    and request.get("activity_run_id") == item.get("activity_run_id")
                    and request.get("column_count") == item.get("column_count")
                    and payload.get("source_id") in (None, item.get("source_id"))):
                matches.append(payload)
    if len(matches) > 1:
        raise ValueError("multiple canonical runs match the interrupted batch item; refusing ambiguous resume")
    if not matches:
        return None
    run = matches[0]
    source_id = str(item.get("source_id", ""))
    source_sha = str(item.get("source_sha256", ""))
    source_record_sha = str(item.get("source_record_sha256", ""))
    binding = run.get("owner_source_binding")
    if binding is not None and (
        not isinstance(binding, Mapping)
        or binding.get("source_id") != source_id
        or binding.get("source_sha256") != source_sha
        or binding.get("source_record_sha256") != source_record_sha
    ):
        return None
    if (not _has_ready_pipeline_proof(
            run, source_id, expected_columns=int(item.get("column_count", 0)),
            source_record_sha256=source_record_sha, job=job, item=item)
            or not _verify_column_artifacts(run, int(item.get("column_count", 0)))):
        return None
    candidate_id = str(run.get("candidate_id", ""))
    candidate = next((row for row in list_candidates() if row.get("candidate_id") == candidate_id), None)
    if candidate is None:
        raise ValueError("interrupted READY run has no exact canonical candidate")
    if not _candidate_has_source_lineage(candidate, source_id, source_sha):
        raise ValueError("interrupted READY run candidate lineage does not match the immutable imported source")
    pool = _enter_candidate_release_pool(candidate, pipeline=run)
    if not pool.get("readback_verified") or not _pool_row_matches(run, candidate, source_id, int(item.get("column_count", 0))):
        raise ValueError("interrupted READY run could not be verified in Release Pool")
    return {"pipeline": run, "release_pool": pool, "recovered_after_interruption": True}


def _reuse_existing_ready(job: Mapping[str, Any], item: Mapping[str, Any]) -> dict[str, Any] | None:
    """Reuse only a read-back-ready source run whose artifacts and Pool proof verify."""
    from .studio_extensions import _enter_candidate_release_pool, list_candidates, restore_source_run

    restored = restore_source_run(
        str(item["source_id"]),
        game_project=job.get("settings", {}).get("game_project"),
        source_directory=job.get("settings", {}).get("source_directory"),
    )
    if restored.get("state") != "READY" or restored.get("source_sha256") != item.get("source_sha256"):
        return None
    if restored.get("owner_review_status", {}).get("pool_state") == "EXCLUDED_FROM_RELEASE_POOL":
        return {"rejected": True, "reason": "SOURCE_CANDIDATE_IS_OWNER_REJECTED"}
    pipeline = restored.get("pipeline", {})
    source_id = str(item.get("source_id", ""))
    columns = int(item.get("column_count", 0))
    source_record_sha = str(item.get("source_record_sha256", ""))
    if (not _has_ready_pipeline_proof(
            pipeline, source_id, expected_columns=columns,
            source_record_sha256=source_record_sha, item=item)
            or not _verify_column_artifacts(pipeline, columns)):
        return None
    candidate_id = str(restored.get("candidate_id", ""))
    candidate = next((row for row in list_candidates() if row.get("candidate_id") == candidate_id), None)
    if candidate is None:
        return None
    if not _candidate_has_source_lineage(candidate, source_id, str(item.get("source_sha256", ""))):
        return None
    if not _pool_row_matches(pipeline, candidate, source_id, columns):
        return None
    pool = _enter_candidate_release_pool(candidate, pipeline=pipeline)
    if not pool.get("readback_verified"):
        raise ValueError("existing READY source has no exact READY_AUTO Release Pool readback")
    return {"pipeline": pipeline, "release_pool": pool}


def run_png_batch(
    job_id: str,
    *,
    expected_batch_id: str | None = None,
    pipeline_runner: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from . import studio_extensions as extensions

    runner = pipeline_runner or extensions.run_pipeline
    with _job_lock(job_id):
        job = _read_job(job_id)
        if expected_batch_id is not None and expected_batch_id != job.get("import_batch_id"):
            return {"state": "BLOCKED", "disposition": "BATCH_JOB_SOURCE_MISMATCH", "reason": "Displayed import batch does not match this resumable job."}
        if job.get("state") == "COMPLETE":
            disposition = "FINISHED_WITH_FAILURES" if int(job.get("counts", {}).get("failed", 0)) or int(job.get("counts", {}).get("rejected", 0)) else "COMPLETE"
            return {"state": "SUCCESS", "disposition": disposition, "job": job, "mutated": False}
        batch = extensions.batch_load(str(job.get("import_batch_id", "")))["batch"]
        if extensions._digest(batch) != job.get("batch_digest"):
            return {"state": "BLOCKED", "disposition": "BATCH_JOB_SOURCE_MISMATCH", "job": job, "reason": "Import batch manifest digest changed after the immutable PNG solver plan was created."}
        _clear_control(job_id)
        job["state"] = "RUNNING"
        job["updated_at"] = _now()
        job = _write_job(job)
        for item_index, item in enumerate(job["items"]):
            if item.get("status") in {"READY", "FAILED", "REJECTED", "SKIPPED_DUPLICATE"}:
                continue
            action = _control_action(job_id)
            if action:
                job["state"] = "PAUSED" if action == "PAUSE_AFTER_CURRENT" else "STOPPED"
                job["current_index"] = None
                job["updated_at"] = _now()
                _clear_control(job_id)
                job = _write_job(job)
                return {"state": "SUCCESS", "disposition": job["state"], "job": job}
            try:
                proof = extensions.validate_owner_source(
                    str(item["source_id"]), persist=False,
                    game_project=job.get("settings", {}).get("game_project"),
                    source_directory=job.get("settings", {}).get("source_directory"),
                )
                if (proof.get("source_sha256") != item.get("source_sha256")
                        or proof.get("structural", {}).get("disposition") != "PASS"
                        or not proof.get("exact_logical_source")):
                    raise ValueError("source changed or failed canonical pinned-runtime validation")
                record_path, _source_path = extensions._source_record_paths(
                    str(item["source_id"]), job.get("settings", {}).get("source_directory"))
                if hashlib.sha256(record_path.read_bytes()).hexdigest() != item.get("source_record_sha256"):
                    raise ValueError("source record SHA-256 changed after batch planning")
            except Exception as exc:
                item.update({"status": "REJECTED", "reason": f"SOURCE_REVALIDATION_FAILED: {str(exc)[:400]}", "finished_at": _now()})
                job["counts"] = _counts(job["items"])
                job["current_index"] = None
                job["updated_at"] = _now()
                job = _write_job(job)
                continue
            if item.get("status") == "RUNNING":
                recovered = _recover_attempt(job, item)
                if recovered is not None:
                    pipeline = recovered["pipeline"]
                    item.update({"status": "READY", "run_id": pipeline.get("run_id"), "candidate_id": pipeline.get("candidate_id"), "artifact_refs": pipeline.get("primary", {}).get("files", {}), "release_pool": recovered["release_pool"], "recovered_after_interruption": True, "finished_at": _now()})
                    job["counts"] = _counts(job["items"])
                    job["ready_mix"][str(item["column_count"])] = int(job["ready_mix"].get(str(item["column_count"]), 0)) + 1
                    job["current_index"] = None
                    job["updated_at"] = _now()
                    job = _write_job(job)
                    continue
                item["status"] = "QUEUED"
                item["reason"] = "PRIOR_ATTEMPT_INTERRUPTED_WITHOUT_COMPLETE_CANONICAL_RUN"
                job["updated_at"] = _now()
                job = _write_job(job)
            item.update({"status": "VERIFYING_EXISTING", "reason": "Checking for already complete artifact-verified READY evidence."})
            job["current_index"] = item_index
            job["updated_at"] = _now()
            job = _write_job(job)
            try:
                reused = _reuse_existing_ready(job, item)
            except Exception as exc:
                reused = None
                item["existing_ready_check_error"] = str(exc)[:400]
            if reused is not None and reused.get("rejected"):
                item.update({"status": "REJECTED", "reason": str(reused.get("reason", "SOURCE_CANDIDATE_IS_OWNER_REJECTED")), "finished_at": _now()})
                job["counts"] = _counts(job["items"])
                job["current_index"] = None
                job["updated_at"] = _now()
                job = _write_job(job)
                continue
            if reused is not None:
                pipeline = reused["pipeline"]
                item.update({"status": "READY", "run_id": pipeline.get("run_id"), "candidate_id": pipeline.get("candidate_id"), "artifact_refs": pipeline.get("primary", {}).get("files", {}), "release_pool": reused["release_pool"], "reused_existing_ready": True, "finished_at": _now()})
                job["counts"] = _counts(job["items"])
                job["ready_mix"][str(item["column_count"])] = int(job["ready_mix"].get(str(item["column_count"]), 0)) + 1
                job["current_index"] = None
                job["updated_at"] = _now()
                job = _write_job(job)
                continue
            item["status"] = "QUEUED"
            job["current_index"] = None
            job["updated_at"] = _now()
            job = _write_job(job)
            attempt_id = "batch-%s-%03d-%s" % (job_id.removeprefix("png-batch-")[:12], item_index + 1, uuid.uuid4().hex[:12])
            activity_id = "pipeline-ui-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + hashlib.sha256(attempt_id.encode()).hexdigest()[:12]
            item.update({"status": "RUNNING", "attempt_id": attempt_id, "activity_run_id": activity_id, "started_at": _now(), "reason": ""})
            job["state"] = "RUNNING"
            job["current_index"] = item_index
            job["counts"] = _counts(job["items"])
            job["updated_at"] = _now()
            job = _write_job(job)
            request = dict(job.get("settings", {}))
            request.update({
                "column_count": int(item["column_count"]),
                "png_batch_job_id": job_id,
                "png_batch_item_index": item_index,
                "png_batch_attempt_id": attempt_id,
                "activity_run_id": activity_id,
                "activity_source_sha256": str(item["source_sha256"]),
                "activity_source_record_sha256": str(item["source_record_sha256"]),
                "candidates": min(int(request.get("candidates", 300)), 300),
                "real_max_visited": min(int(request.get("real_max_visited", 25_000)), 25_000),
                "solver_timeout_seconds": min(float(request.get("solver_timeout_seconds", 90)), 90),
            })
            try:
                pipeline = runner(source_id=str(item["source_id"]), request=request)
                primary = pipeline.get("primary", {}) if isinstance(pipeline, Mapping) else {}
                pool = pipeline.get("release_pool", {}) if isinstance(pipeline, Mapping) else {}
                ready = (
                    _has_ready_pipeline_proof(
                        pipeline, str(item["source_id"]), expected_columns=int(item["column_count"]),
                        source_record_sha256=str(item["source_record_sha256"]), job=job, item=item)
                    and _verify_column_artifacts(pipeline, int(item["column_count"]))
                    and pool.get("readback_verified") is True
                )
                if ready:
                    item.update({"status": "READY", "run_id": pipeline.get("run_id"), "candidate_id": pipeline.get("candidate_id"), "artifact_refs": primary.get("files", {}), "release_pool": pool, "finished_at": _now()})
                    job["ready_mix"][str(item["column_count"])] = int(job["ready_mix"].get(str(item["column_count"]), 0)) + 1
                else:
                    item.update({"status": "FAILED", "run_id": pipeline.get("run_id") if isinstance(pipeline, Mapping) else None, "reason": str(pipeline.get("error", pipeline.get("reason", pipeline.get("disposition", "CANONICAL_READY_PROOF_MISSING"))) if isinstance(pipeline, Mapping) else "CANONICAL_PIPELINE_RETURNED_NO_RESULT")[:512], "finished_at": _now()})
            except Exception as exc:
                item.update({"status": "FAILED", "reason": str(exc)[:512], "finished_at": _now()})
            job["current_index"] = None
            job["counts"] = _counts(job["items"])
            job["updated_at"] = _now()
            job = _write_job(job)
        job["state"] = "COMPLETE"
        job["current_index"] = None
        job["counts"] = _counts(job["items"])
        job["updated_at"] = _now()
        job = _write_job(job)
        disposition = "FINISHED_WITH_FAILURES" if int(job.get("counts", {}).get("failed", 0)) or int(job.get("counts", {}).get("rejected", 0)) else "COMPLETE"
        return {"state": "SUCCESS", "disposition": disposition, "job": job}
