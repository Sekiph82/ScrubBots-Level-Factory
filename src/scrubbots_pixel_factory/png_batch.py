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


def _has_ready_pipeline_proof(pipeline: Mapping[str, Any], source_id: str) -> bool:
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
    return (
        pipeline.get("disposition") == "READY"
        and pipeline.get("source_id") == source_id
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


def _verify_sources(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    from .studio_extensions import verify_owner_source

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
            proof = verify_owner_source(source_id)
            source_sha = str(proof.get("source_sha256", ""))
            if source_id != "owner-upload-" + source_sha or len(source_sha) != 64:
                raise ValueError("source ID and verified PNG SHA-256 disagree")
            from .studio_extensions import _source_record_paths

            record_path, _source_path = _source_record_paths(source_id)
            record_sha = hashlib.sha256(record_path.read_bytes()).hexdigest()
            item.update({"source_sha256": source_sha, "source_record_sha256": record_sha, "original_filename": str(proof.get("original_filename", display_name))[:240], "status": "QUEUED", "reason": ""})
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
    source_items = _verify_sources(imported["items"])
    eligible = [item for item in source_items if item["status"] == "QUEUED"]
    assignments = assign_columns([str(item["source_id"]) for item in eligible])
    assignment_by_id = {str(item["source_id"]): columns for item, columns in zip(eligible, assignments, strict=True)}
    for item in source_items:
        item["column_count"] = assignment_by_id.get(str(item["source_id"]))
    snapshot = dict(settings or {})
    # The UI may configure only canonical bounded pipeline request fields.
    allowed = {"game_project", "source_directory", "background_intent", "seed", "candidates", "verify_top", "screen_budget", "metric_top", "viability_budget", "real_max_visited", "solver_timeout_seconds"}
    if set(snapshot) - allowed:
        raise ValueError("PNG batch settings include unsupported fields")
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
        "plan_digest": plan_digest, "settings": snapshot, "state": "QUEUED",
        "created_at": _now(), "updated_at": _now(), "current_index": None,
        "items": source_items, "counts": _counts(source_items),
        "planned_quotas": {str(key): value for key, value in largest_remainder_quotas(len(eligible)).items()},
        "ready_mix": {"3": 0, "4": 0, "5": 0},
    }
    saved = _write_job(job)
    return {"state": "SUCCESS", "disposition": "CREATED", "job": saved}


def png_batch_status(job_id: str) -> dict[str, Any]:
    job = _read_job(job_id)
    public = dict(job)
    public["mutated"] = False
    return {"state": "SUCCESS", "disposition": "STATUS", "job": public}


def png_batch_latest() -> dict[str, Any]:
    jobs: list[dict[str, Any]] = []
    job_root = _root() / "jobs"
    if job_root.exists():
        for path in sorted(job_root.glob("png-batch-*.json"), key=lambda item: item.stat().st_mtime, reverse=True)[:20]:
            try:
                jobs.append(_read_job(path.stem))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
    resumable = next((job for job in jobs if job.get("state") not in {"COMPLETE", "STOPPED"}), None)
    return {"state": "SUCCESS", "disposition": "LATEST", "job": resumable, "jobs": jobs, "mutated": False}


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
                    and payload.get("source_id") == item.get("source_id")):
                matches.append(payload)
    if len(matches) > 1:
        raise ValueError("multiple canonical runs match the interrupted batch item; refusing ambiguous resume")
    if not matches:
        return None
    run = matches[0]
    if not _has_ready_pipeline_proof(run, str(item.get("source_id", ""))):
        return None
    candidate_id = str(run.get("candidate_id", ""))
    candidate = next((row for row in list_candidates() if row.get("candidate_id") == candidate_id), None)
    if candidate is None:
        raise ValueError("interrupted READY run has no exact canonical candidate")
    pool = _enter_candidate_release_pool(candidate, pipeline=run)
    if not pool.get("readback_verified"):
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
    if not _has_ready_pipeline_proof(pipeline, str(item.get("source_id", ""))):
        return None
    candidate_id = str(restored.get("candidate_id", ""))
    candidate = next((row for row in list_candidates() if row.get("candidate_id") == candidate_id), None)
    if candidate is None:
        return None
    pool = _enter_candidate_release_pool(candidate, pipeline=pipeline)
    if not pool.get("readback_verified"):
        raise ValueError("existing READY source has no exact READY_AUTO Release Pool readback")
    return {"pipeline": pipeline, "release_pool": pool}


def run_png_batch(job_id: str, *, pipeline_runner: Callable[..., dict[str, Any]] | None = None) -> dict[str, Any]:
    from . import studio_extensions as extensions

    runner = pipeline_runner or extensions.run_pipeline
    with _job_lock(job_id):
        job = _read_job(job_id)
        if job.get("state") == "COMPLETE":
            return {"state": "SUCCESS", "disposition": "COMPLETE", "job": job, "mutated": False}
        batch = extensions.batch_load(str(job.get("import_batch_id", "")))["batch"]
        if extensions._digest(batch) != job.get("batch_digest"):
            raise ValueError("import batch manifest changed after the immutable PNG solver plan was created")
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
            try:
                proof = extensions.verify_owner_source(str(item["source_id"]))
                if proof.get("source_sha256") != item.get("source_sha256"):
                    raise ValueError("source SHA-256 changed after import")
                record_path, _source_path = extensions._source_record_paths(str(item["source_id"]))
                if hashlib.sha256(record_path.read_bytes()).hexdigest() != item.get("source_record_sha256"):
                    raise ValueError("source record SHA-256 changed after batch planning")
            except Exception as exc:
                item.update({"status": "REJECTED", "reason": f"SOURCE_REVALIDATION_FAILED: {str(exc)[:400]}", "finished_at": _now()})
                job["counts"] = _counts(job["items"])
                job["current_index"] = None
                job["updated_at"] = _now()
                job = _write_job(job)
                continue
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
            item.update({"status": "RUNNING", "attempt_id": attempt_id, "started_at": _now(), "reason": ""})
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
                "candidates": min(int(request.get("candidates", 300)), 300),
                "real_max_visited": min(int(request.get("real_max_visited", 25_000)), 25_000),
                "solver_timeout_seconds": min(float(request.get("solver_timeout_seconds", 90)), 90),
            })
            try:
                pipeline = runner(source_id=str(item["source_id"]), request=request)
                primary = pipeline.get("primary", {}) if isinstance(pipeline, Mapping) else {}
                pool = pipeline.get("release_pool", {}) if isinstance(pipeline, Mapping) else {}
                ready = _has_ready_pipeline_proof(pipeline, str(item["source_id"])) and pool.get("readback_verified") is True
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
        return {"state": "SUCCESS", "disposition": "COMPLETE", "job": job}
