"""Durable owner-triggered PNG batch orchestration (bounded parallel workers).

This module contains no solver. Each queued source is dispatched exactly once
at a time through the existing Studio ``run_pipeline`` contract after an
explicit Run Entire Batch command. Pipeline calls remain the canonical solver,
replay, Difficulty V1, QA, and READY_AUTO Release Pool implementation.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
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
MAX_JOB_BYTES = 1024 * 1024
_PROCESS_LOCKS: dict[str, threading.Lock] = {}
_PROCESS_LOCKS_GUARD = threading.Lock()


MAX_PARALLEL_WORKERS = 8


def parallel_workers(settings: Mapping[str, Any] | None = None) -> int:
    """Concurrent canonical pipelines per batch: settings, env override, else cores // 4 (max 4)."""
    requested = (settings or {}).get("parallel_workers") or os.environ.get("SCRUBBOTS_FACTORY_BATCH_WORKERS")
    if requested:
        return max(1, min(MAX_PARALLEL_WORKERS, int(requested)))
    return max(1, min(4, (os.cpu_count() or 4) // 4))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def largest_remainder_quotas(count: int) -> dict[int, int]:
    """Return exact integer quotas for 45/40/15, with stable 3/4/5 ties."""
    if type(count) is not int or count < 0:
        raise ValueError("batch size must be a non-negative integer")
    weights = ((3, 45), (4, 40), (5, 15))
    # Keep mathematically equal remainders equal; float rounding otherwise
    # makes the tie break platform-dependent for large batches.
    remainders = {columns: count * weight % 100 for columns, weight in weights}
    quotas = {columns: count * weight // 100 for columns, weight in weights}
    remaining = count - sum(quotas.values())
    order = sorted(weights, key=lambda pair: (-remainders[pair[0]], pair[0]))
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
    from .owner_art_storage import owner_art_paths
    from . import studio_extensions
    return owner_art_paths(studio_extensions._repository_root())["batches"] / "Jobs"


def _job_path(job_id: str) -> Path:
    if not isinstance(job_id, str) or not job_id.startswith("png-batch-") or len(job_id) > 80 or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in job_id):
        raise ValueError("PNG batch job identity is malformed")
    from . import studio_extensions
    from .owner_art_storage import OwnerArtStorageError, _is_reparse_point, _verify_path_under_root

    filename = f"{job_id}.json"
    canonical_root = _root()
    canonical = canonical_root / "jobs" / filename
    try:
        _verify_path_under_root(Path(studio_extensions._repository_root()).resolve(), canonical.parent)
    except OwnerArtStorageError as exc:
        raise ValueError("canonical PNG batch path contains a reparse point or escapes the repository") from exc
    if _is_reparse_point(canonical):
        raise ValueError("PNG batch job path is a symlink or reparse point")
    return canonical


def _control_path(job_id: str) -> Path:
    return _job_path(job_id).parent.parent / "control" / f"{job_id}.json"


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
    lock_path = _job_path(job_id).parent.parent / "locks" / f"{job_id}.lock"
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


def _failure_reason(pipeline: Any) -> str:
    """Batch row reason: the pipeline error, else the solver's own reason, never a bare disposition."""
    if not isinstance(pipeline, Mapping):
        return "CANONICAL_PIPELINE_RETURNED_NO_RESULT"
    primary = pipeline.get("primary", {})
    primary_reason = primary.get("reason") if isinstance(primary, Mapping) else None
    disposition = str(pipeline.get("disposition", "CANONICAL_READY_PROOF_MISSING"))
    reason = pipeline.get("error") or pipeline.get("reason") or primary_reason
    if not reason:
        return disposition[:512]
    # The Godot bridge prefixes its banner; keep only the meaningful lines.
    lines = [line for line in str(reason).splitlines() if line.strip() and not line.startswith("Godot Engine v")]
    return f"{disposition}: {' '.join(lines)}"[:512]


def _counts(items: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    states = Counter(str(item.get("status", "UNKNOWN")) for item in items)
    return {
        "total": len(items), "ready": states["READY"], "failed": states["FAILED"],
        "rejected": states["REJECTED"],
        "skipped": states["SKIPPED_DUPLICATE"] + states["SKIPPED"],
        "remaining": sum(states[name] for name in ("QUEUED", "RUNNING", "VERIFYING_EXISTING", "RETRYABLE", "INCONCLUSIVE")),
    }


class OwnerReleaseProjectionError(RuntimeError):
    """A terminal solver outcome could not be mirrored to Release Pool."""


def _persist_owner_release_item(job: Mapping[str, Any], item: dict[str, Any]) -> None:
    """Immediately project a terminal item into its current Release Pool status."""
    if item.get("status") not in {"READY", "FAILED", "REJECTED"}:
        return
    try:
        from .owner_release_library import record_batch_item_outcome

        event = record_batch_item_outcome(job, item)
        item["owner_release_projection"] = {
            "state": "RECORDED" if event else "NOT_APPLICABLE",
            "status": event.get("status") if event else None,
            "event_sha256": event.get("event_sha256") if event else None,
        }
    except Exception as exc:
        detail = f"{type(exc).__name__}: {str(exc)[:400]}"
        item["owner_release_projection"] = {"state": "ERROR", "reason": detail}
        raise OwnerReleaseProjectionError(detail) from exc


def _persist_projection_or_pause(job: dict[str, Any], item: dict[str, Any]) -> dict[str, Any] | None:
    """Persist a terminal source status before allowing the batch to advance."""
    try:
        _persist_owner_release_item(job, item)
    except OwnerReleaseProjectionError as exc:
        job["state"] = "PROJECTION_ERROR"
        job["current_index"] = item.get("index")
        job["projection_error"] = {
            "source_id": item.get("source_id"), "status": item.get("status"),
            "reason": str(exc)[:512], "retryable": True,
        }
        job["updated_at"] = _now()
        saved = _write_job(job)
        return {"state": "ERROR", "disposition": "OWNER_RELEASE_PROJECTION_ERROR",
                "job": saved, "reason": str(exc)[:512]}
    job.pop("projection_error", None)
    return None


def _persist_owner_release_attempt(job: Mapping[str, Any], item: dict[str, Any]) -> None:
    """Durably keep an item in Pending before invoking its solver attempt."""
    from .owner_release_library import begin_batch_item_attempt

    event = begin_batch_item_attempt(job, item)
    item["owner_release_projection"] = {
        "state": "RECORDED" if event else "NOT_APPLICABLE",
        "status": event.get("status") if event else None,
        "event_sha256": event.get("event_sha256") if event else None,
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
    if saved_hashes is not None:
        if not isinstance(saved_hashes, Mapping) or any(saved_hashes.get(key) != digest for key, digest in artifact_hashes.items()):
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
    from .studio_extensions import _pipeline_path, _read_json, extensions_root
    from .supply_pipeline.release_pool import release_entries

    run_id = run.get("run_id")
    candidate_id = candidate.get("candidate_id")
    try:
        entries = release_entries(str(candidate_id))
        entry = next((row for row in entries if row.get("pipeline_run_id") == run_id), None)
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
        from .supply_pipeline import release_pool as release_pool_store
        row = next(
            path for path in release_pool_store.entry_paths(str(candidate_id))
            if _read_json(path).get("candidate_id") == candidate_id
            and _read_json(path).get("pipeline_run_id") == run_id
        )
        saved = _read_json(row)
        pipeline_path = _pipeline_path(run_id)
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


def _verified_ready_sources(imported_items: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, str]]:
    """Find current source SHAs with prior READY status and intact canonical proof.

    A historical job status alone is not enough to suppress work. The source PNG
    and source record must still match, as must the exact canonical pipeline,
    solver artifacts, candidate lineage, and Release Pool row.
    """
    from . import studio_extensions as studio

    current_by_sha: dict[str, str] = {}
    for item in imported_items:
        if not isinstance(item, Mapping):
            continue
        source_id = str(item.get("source_id", ""))
        source_sha = str(item.get("source_sha256", ""))
        if source_id == f"owner-upload-{source_sha}" and len(source_sha) == 64:
            current_by_sha[source_sha] = source_id
    if not current_by_sha:
        return {}

    jobs_root = _root() / "jobs"
    if not jobs_root.is_dir():
        return {}
    ready_history: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for path in sorted(jobs_root.glob("png-batch-*.json")):
        try:
            job = _read_job(path.stem)
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
            continue
        for item in job.get("items", []):
            if (isinstance(item, dict) and item.get("status") == "READY"
                    and str(item.get("source_sha256", "")) in current_by_sha
                    and item.get("source_id") == current_by_sha.get(str(item.get("source_sha256", "")))):
                ready_history.append((job, item))
    if not ready_history:
        return {}

    try:
        candidates_by_id = {str(row.get("candidate_id", "")): row for row in studio.list_candidates()}
        from .supply_pipeline import release_pool as release_pool_store
        from .supply_pipeline.release_pool import release_entries

        entries_by_pair = {
            (str(row.get("candidate_id", "")), str(row.get("pipeline_run_id", ""))): row
            for row in release_entries()
        }
        pool_paths_by_pair: dict[tuple[str, str], Path] = {}
        for pool_path in release_pool_store.entry_paths():
            try:
                saved_entry = studio._read_json(pool_path)
            except Exception:
                continue
            pair = (str(saved_entry.get("candidate_id", "")), str(saved_entry.get("pipeline_run_id", "")))
            if all(pair):
                pool_paths_by_pair[pair] = pool_path
        latest_ready_by_candidate: dict[str, dict[str, Any]] = {}
        for pipeline_path in studio._pipeline_paths():
            try:
                pipeline_value = studio._read_json(pipeline_path)
            except Exception:
                continue
            candidate_key = str(pipeline_value.get("candidate_id", ""))
            if (candidate_key and pipeline_value.get("disposition") == "READY"
                    and pipeline_value.get("primary", {}).get("state") == "READY"):
                current = latest_ready_by_candidate.get(candidate_key)
                if current is None or str(pipeline_value.get("created_at", "")) > str(current.get("created_at", "")):
                    latest_ready_by_candidate[candidate_key] = pipeline_value
    except Exception:
        return {}
    verified: dict[str, dict[str, str]] = {}
    for job, item in ready_history:
        source_id = str(item.get("source_id", ""))
        source_sha = str(item.get("source_sha256", ""))
        record_sha = str(item.get("source_record_sha256", ""))
        run_id = str(item.get("run_id", ""))
        candidate_id = str(item.get("candidate_id", ""))
        columns = item.get("column_count")
        if (source_sha in verified or len(record_sha) != 64 or len(run_id) == 0
                or not run_id.startswith("pipeline-") or len(candidate_id) == 0
                or columns not in (3, 4, 5)):
            continue
        try:
            source = studio.verify_owner_source(
                source_id, source_directory=job.get("settings", {}).get("source_directory")
            )
            record_path, source_path = studio._source_record_paths(
                source_id, job.get("settings", {}).get("source_directory")
            )
            if (source.get("source_sha256") != source_sha
                    or hashlib.sha256(source_path.read_bytes()).hexdigest() != source_sha
                    or hashlib.sha256(record_path.read_bytes()).hexdigest() != record_sha):
                continue
            pipeline = studio._read_json(studio._pipeline_path(run_id))
            latest = latest_ready_by_candidate.get(candidate_id)
            candidate = candidates_by_id.get(candidate_id)
            pair = (candidate_id, run_id)
            pool_entry = entries_by_pair.get(pair)
            pool_path = pool_paths_by_pair.get(pair)
            pool_row_ok = False
            if candidate is not None and pool_entry is not None and pool_path is not None:
                saved = studio._read_json(pool_path)
                request = pipeline.get("request", {})
                binding = pipeline.get("owner_source_binding", {})
                files = pipeline.get("primary", {}).get("files", {})
                plan = json.loads(Path(str(files.get("supply_plan", ""))).read_text(encoding="utf-8"))
                pipeline_path = studio._pipeline_path(run_id)
                pool_row_ok = (
                    pool_entry.get("source_id", source_id) == source_id
                    and pool_entry.get("column_count", int(columns)) == int(columns)
                    and (not binding or binding.get("source_id") == source_id)
                    and plan.get("columnCount") == int(columns)
                    and saved.get("entry_digest") == pool_entry.get("entry_digest")
                    and saved.get("candidate_id") == candidate_id
                    and saved.get("pipeline_run_id") == run_id
                    and saved.get("source_id", source_id) == source_id
                    and saved.get("column_count", int(columns)) == int(columns)
                    and saved.get("pipeline_sha256") == hashlib.sha256(pipeline_path.read_bytes()).hexdigest()
                    and all(
                        saved.get("files", {}).get(key, {}).get("sha256")
                        == hashlib.sha256(Path(str(files.get(key, ""))).read_bytes()).hexdigest()
                        for key in ("level", "supply_plan")
                    )
                )
            if (candidate is None or not isinstance(latest, Mapping)
                    or latest.get("run_id") != run_id
                    or not _has_ready_pipeline_proof(
                        pipeline, source_id, expected_columns=int(columns),
                        source_record_sha256=record_sha, job=job, item=item,
                    )
                    or not _verify_column_artifacts(pipeline, int(columns))
                    or not _candidate_has_source_lineage(candidate, source_id, source_sha)
                    or not pool_row_ok):
                continue
        except Exception:
            continue
        verified[source_sha] = {
            "source_id": source_id,
            "candidate_id": candidate_id,
            "pipeline_run_id": run_id,
            "ready_job_id": str(job.get("job_id", "")),
        }
    return verified


def _configured_game_project(settings: Mapping[str, Any]) -> str | None:
    """Resolve the pinned game root and reject a missing project before job writes."""
    from .supply_pipeline.pinned_game_source import expected_runtime_root

    configured = settings.get("game_project")
    project_root = Path(str(configured)).expanduser() if configured else expected_runtime_root()
    try:
        project_root = project_root.resolve(strict=True)
    except OSError:
        return None
    if not project_root.is_dir() or not (project_root / "project.godot").is_file():
        return None
    return str(project_root)


def _rebind_superseded_runtime(job: dict[str, Any]) -> None:
    """Resume solves the remaining items with the current pinned runtime.

    Owner re-pin 2026-11-12: a batch planned with the previous attested runtime
    would otherwise keep solving with the old game rules. Finished items keep
    their own evidence; only items solved from now on use the new pin.
    """
    from .supply_pipeline import pinned_game_source as pins

    settings = job.setdefault("settings", {})
    configured = settings.get("game_project")
    if not configured:
        return
    try:
        root = Path(str(configured)).expanduser().resolve()
        current = pins.expected_runtime_root().resolve()
    except OSError:
        return
    if root != current and pins.is_pinned_runtime(root):
        settings["game_project"] = str(current)
        job.setdefault("runtime_rebinds", []).append({"from": root.name, "to": current.name, "at": _now()})


def create_png_batch(batch_id: str, settings: Mapping[str, Any] | None = None) -> dict[str, Any]:
    from .studio_extensions import _digest, batch_load, create_loaded_png_batch
    from .owner_release_library import list_records as list_release_records

    imported = batch_load(batch_id)["batch"]
    if not isinstance(imported.get("items"), list):
        raise ValueError("an imported PNG batch must contain an items list")
    pending_by_id = {
        str(row.get("source_id", "")): row
        for row in list_release_records("PENDING").get("records", [])
        if isinstance(row, Mapping)
    }
    pending_status_snapshot: list[dict[str, str]] = []
    for source_item in imported["items"]:
        if not isinstance(source_item, Mapping):
            return {"state": "BLOCKED", "disposition": "PENDING_QUEUE_ITEM_INVALID", "job": {}}
        source_id = str(source_item.get("source_id", ""))
        source_sha = str(source_item.get("source_sha256", ""))
        status_row = pending_by_id.get(source_id)
        if (not status_row or status_row.get("source_sha256") != source_sha
                or str(status_row.get("provider", "")).upper() not in {"PIXELLAB", "OWNER_UPLOAD"}):
            return {
                "state": "BLOCKED", "disposition": "SOURCE_NOT_CURRENTLY_PENDING",
                "reason": "Every new PNG solver job must be built from the exact current PixelLab Pending status and SHA.",
                "source_id": source_id, "job": {},
            }
        pending_status_snapshot.append({
            "source_id": source_id, "source_sha256": source_sha,
            "pending_event_sha256": str(status_row.get("event_sha256", "")),
        })
    inventory_batch_id = batch_id
    inventory_source_count = len(imported["items"])
    snapshot = dict(settings or {})
    # The UI may configure only canonical bounded pipeline request fields.
    allowed = {"game_project", "source_directory", "background_intent", "seed", "candidates", "verify_top", "screen_budget", "metric_top", "viability_budget", "real_max_visited", "solver_timeout_seconds"}
    if set(snapshot) - allowed:
        raise ValueError("PNG batch settings include unsupported fields")
    configured_game_project = _configured_game_project(snapshot)
    if configured_game_project is None:
        return {
            "state": "BLOCKED", "disposition": "PINNED_GAME_PROJECT_MISSING",
            "reason": "Configured ScrubBots project is missing project.godot; no PNG batch was created.",
            "job": {},
        }
    snapshot["game_project"] = configured_game_project
    previously_ready = _verified_ready_sources(imported["items"])
    excluded_ready = [
        {"source_sha256": sha, **previously_ready[sha]}
        for sha in sorted(previously_ready)
    ]
    if previously_ready:
        remaining_source_ids = [
            str(item.get("source_id", "")) for item in imported["items"]
            if isinstance(item, Mapping)
            and str(item.get("source_sha256", "")) not in previously_ready
        ]
        if not remaining_source_ids:
            return {
                "state": "SUCCESS", "disposition": "ALL_SOURCES_ALREADY_READY",
                "job": {}, "excluded_ready_sources": excluded_ready,
            }
        imported = create_loaded_png_batch(remaining_source_ids)
        batch_id = str(imported.get("batch_id", ""))
        if not batch_id:
            raise ValueError("READY-excluded source snapshot could not be persisted")
    source_items = _verify_sources(imported["items"], snapshot)
    eligible = [item for item in source_items if item["status"] == "QUEUED"]
    assignments = assign_columns([str(item["source_id"]) for item in eligible])
    assignment_by_id = {str(item["source_id"]): columns for item, columns in zip(eligible, assignments, strict=True)}
    for item in source_items:
        item["column_count"] = assignment_by_id.get(str(item["source_id"]))
    immutable_plan = {
        "batch_id": batch_id, "inventory_batch_id": inventory_batch_id,
        "batch_digest": _digest(imported), "settings": snapshot,
        "queue_authority": "CURRENT_RELEASE_POOL_PENDING",
        "pending_status_snapshot": pending_status_snapshot,
        "excluded_ready_sources": excluded_ready, "items": source_items,
    }
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
        "inventory_batch_id": inventory_batch_id,
        "inventory_source_count": inventory_source_count,
        "snapshot_source_count": len(imported["items"]),
        "excluded_ready_sources": excluded_ready,
        "plan_digest": plan_digest, "settings": snapshot, "state": "QUEUED",
        "created_at": _now(), "updated_at": _now(), "current_index": None,
        "items": source_items, "counts": _counts(source_items),
        "planned_quotas": {str(key): value for key, value in largest_remainder_quotas(len(eligible)).items()},
        "ready_mix": {"3": 0, "4": 0, "5": 0},
    }
    saved = _write_job(job)
    superseded = _supersede_covered_jobs(saved)
    return {"state": "SUCCESS", "disposition": "CREATED", "job": saved, "superseded_job_ids": superseded}


_SUPERSEDABLE_STATES = {"QUEUED", "PAUSED", "STOPPED", "INTERRUPTED", "PROJECTION_ERROR"}
_UNFINISHED_ITEM_STATES = {"QUEUED", "RUNNING", "VERIFYING_EXISTING"}


def _supersede_covered_jobs(new_job: Mapping[str, Any]) -> list[str]:
    """Retire older unfinished jobs whose remaining sources the new Pending job covers.

    A new batch is built from every current Pending PNG. An older paused or
    interrupted job whose unfinished rows are all in that batch would otherwise
    stay "resumable" and make startup discovery ambiguous. Its finished rows and
    history are kept; only its state becomes SUPERSEDED (never run again).
    """
    covered = {str(item.get("source_id", "")) for item in new_job.get("items", [])
               if isinstance(item, Mapping) and item.get("status") == "QUEUED"}
    # Rows another job already finished are no longer Pending. They must not keep
    # an old job alive: on 2026-11-13 two 8 November jobs (99 and 100 such rows)
    # were never superseded and made startup discovery ambiguous ("Batch mismatch").
    from .owner_release_library import list_records
    still_pending = {str(row.get("source_id", "")) for row in list_records().get("records", [])
                     if isinstance(row, Mapping) and str(row.get("status", "")) == "PENDING"}
    superseded: list[str] = []
    job_root = _root() / "jobs"
    for path in sorted(job_root.glob("png-batch-*.json")) if job_root.exists() else []:
        job_id = path.stem
        if job_id == new_job.get("job_id"):
            continue
        try:
            with _job_lock(job_id):
                old = _read_job(job_id)
                if old.get("state") not in _SUPERSEDABLE_STATES:
                    continue
                unfinished = {str(item.get("source_id", "")) for item in old.get("items", [])
                              if isinstance(item, Mapping) and item.get("status") in _UNFINISHED_ITEM_STATES}
                if not unfinished or not unfinished & still_pending <= covered:
                    continue
                old["state"] = "SUPERSEDED"
                old["superseded_by"] = str(new_job.get("job_id", ""))
                old["updated_at"] = _now()
                _write_job(old)
                superseded.append(job_id)
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return superseded


def retry_failed_png_batch(job_id: str, source_ids: Sequence[str] | None = None) -> dict[str, Any]:
    """Create an explicit retry for all failed/rejected items or a selected subset."""
    from .studio_extensions import _digest, _source_record_paths, batch_load, verify_owner_source

    original = _read_job(job_id)
    if original.get("state") != "COMPLETE":
        return {"state": "BLOCKED", "disposition": "BATCH_NOT_FINISHED", "job": original}
    all_retryable = [item for item in original.get("items", []) if item.get("status") in {"FAILED", "REJECTED"}]
    if source_ids is None:
        retryable_items = all_retryable
    else:
        requested = [str(source_id) for source_id in source_ids]
        if not requested or len(set(requested)) != len(requested):
            return {"state": "BLOCKED", "disposition": "RETRY_SOURCE_SELECTION_INVALID", "job": original}
        retryable_by_source = {str(item.get("source_id", "")): item for item in all_retryable}
        if any(source_id not in retryable_by_source for source_id in requested):
            return {"state": "BLOCKED", "disposition": "RETRY_SOURCE_NOT_FAILED_OR_REJECTED", "job": original}
        retryable_items = [retryable_by_source[source_id] for source_id in requested]
    if not retryable_items:
        return {"state": "BLOCKED", "disposition": "NO_RETRYABLE_FAILED_OR_REJECTED_ITEMS", "job": original}
    batch_id = str(original.get("import_batch_id", ""))
    batch = batch_load(batch_id)["batch"]
    if _digest(batch) != original.get("batch_digest"):
        return {"state": "BLOCKED", "disposition": "BATCH_JOB_SOURCE_MISMATCH", "job": original,
                "reason": "Original immutable composite digest no longer matches this retry chain."}
    if not _job_lineage_matches_snapshot(original, batch):
        return {"state": "BLOCKED", "disposition": "RETRY_PARENT_MISMATCH", "job": original,
                "reason": "Retry ancestry or original source membership is not SHA-authenticated."}
    if original.get("parent_job_id"):
        parent = _read_job(str(original.get("parent_job_id", "")))
        if (parent.get("state") != "COMPLETE"
                or parent.get("state_digest") != original.get("parent_job_state_digest")
                or parent.get("import_batch_id") != batch_id
                or parent.get("batch_digest") != original.get("batch_digest")):
            return {"state": "BLOCKED", "disposition": "RETRY_PARENT_MISMATCH", "job": original,
                    "reason": "Retry parent state or source authority changed; failed/rejected subset was not retried."}
        parent_by_index = {str(item.get("index")): item for item in parent.get("items", []) if isinstance(item, Mapping)}
        for item in original.get("items", []):
            if not isinstance(item, Mapping):
                return {"state": "BLOCKED", "disposition": "RETRY_PARENT_MISMATCH", "job": original}
            parent_item = parent_by_index.get(str(item.get("prior_item_index")))
            if (parent_item is None
                    or parent_item.get("source_id") != item.get("source_id")
                    or parent_item.get("source_sha256") != item.get("source_sha256")
                    or parent_item.get("source_record_sha256") != item.get("source_record_sha256")
                    or parent_item.get("column_count") != item.get("column_count")):
                return {"state": "BLOCKED", "disposition": "RETRY_PARENT_MISMATCH", "job": original,
                        "reason": "Retry item no longer matches its SHA-bound parent assignment."}
    batch_items = {str(item.get("source_id", "")): item for item in batch.get("items", []) if isinstance(item, Mapping)}
    source_paths: dict[str, str] = {}
    for item in retryable_items:
        source_id = str(item.get("source_id", ""))
        source = batch_items.get(source_id)
        try:
            current = verify_owner_source(source_id, source_directory=original.get("settings", {}).get("source_directory"))
            record_path, png_path = _source_record_paths(source_id, original.get("settings", {}).get("source_directory"))
            record_sha = hashlib.sha256(record_path.read_bytes()).hexdigest()
        except Exception as exc:
            return {"state": "BLOCKED", "disposition": "RETRY_SOURCE_CHANGED", "job": original,
                    "reason": f"Current source could not be reverified: {str(exc)[:240]}"}
        if (source is None
                or current.get("source_sha256") != item.get("source_sha256")
                or source.get("source_sha256") != item.get("source_sha256")
                or source.get("source_record_sha256") != item.get("source_record_sha256")
                or record_sha != item.get("source_record_sha256")):
            return {"state": "BLOCKED", "disposition": "RETRY_SOURCE_CHANGED", "job": original,
                    "reason": "Current PNG or source-record SHA differs from the original nine-source composite."}
        source_paths[source_id] = str(png_path.resolve())
    items: list[dict[str, Any]] = []
    for index, previous in enumerate(retryable_items):
        items.append({
            "index": index, "prior_item_index": previous.get("index"),
            "source_id": previous.get("source_id"), "source_sha256": previous.get("source_sha256"),
            "source_record_sha256": previous.get("source_record_sha256"),
            "original_source_path": source_paths[str(previous.get("source_id", ""))],
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
            raise ValueError("retry job identity collides with a different failed/rejected-item snapshot")
        return {"state": "SUCCESS", "disposition": "EXISTING_RETRY", "job": existing}
    from .owner_release_library import list_records, transition

    status_rows = {str(row.get("source_id", "")): row for row in list_records()["records"]}
    for item in items:
        source_id = str(item["source_id"])
        prior = status_rows.get(source_id)
        if (prior is None or prior.get("status") not in {"FAILED", "REJECTED"}
                or prior.get("source_sha256") != item.get("source_sha256")):
            return {"state": "BLOCKED", "disposition": "RETRY_RELEASE_STATUS_MISMATCH", "job": original,
                    "reason": "Current Release Pool status must be the exact FAILED/REJECTED source SHA before retry."}
    quotas = Counter(int(item["column_count"]) for item in items if item.get("column_count") in (3, 4, 5))
    job = {
        "schema": JOB_SCHEMA, "version": JOB_VERSION, "job_id": retry_id,
        "import_batch_id": original.get("import_batch_id"), "batch_digest": original.get("batch_digest"),
        "parent_job_id": job_id, "parent_job_state_digest": original.get("state_digest"),
        "retry_of_failed_or_rejected_only": True, "plan_digest": plan_digest,
        "settings": dict(original.get("settings", {})), "state": "QUEUED",
        "created_at": _now(), "updated_at": _now(), "current_index": None,
        "items": items, "counts": _counts(items),
        "planned_quotas": {str(columns): quotas[columns] for columns in (3, 4, 5)},
        "ready_mix": {"3": 0, "4": 0, "5": 0},
    }
    saved = _write_job(job)
    for item in items:
        source_id = str(item["source_id"])
        prior = status_rows.get(source_id)
        try:
            transition(
                source_id, "PENDING", source_sha256=str(item["source_sha256"]),
                provider=str(prior.get("provider", "PIXELLAB")) if prior else "PIXELLAB",
                original_source_path=source_paths[source_id], reason="Explicit retry queued; previous outcome remains in immutable history.",
                batch_id=str(saved.get("import_batch_id", "")) or None,
                retry_of=str(prior.get("event_sha256", "")) if prior else None,
                evidence={"explicit_retry": True, "retry_job_id": retry_id,
                          "retry_parent_job_id": job_id, "retry_item_index": int(item["index"])},
            )
        except Exception as exc:
            return {"state": "BLOCKED", "disposition": "RETRY_RELEASE_STATUS_WRITE_FAILED", "job": saved,
                    "reason": str(exc)[:400]}
    return {"state": "SUCCESS", "disposition": "RETRY_CREATED", "job": saved}


def retry_release_pool_sources(source_ids: Sequence[str], settings: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Queue explicit current FAILED/REJECTED Release Pool sources for a new verified run.

    This entry point deliberately does not depend on the Studio's last in-memory
    batch. Current status event hashes, immutable source bytes and a fresh
    Pending-only PNG batch establish the retry authority.
    """
    from . import studio_extensions as extensions
    from .owner_release_library import OwnerReleaseLibraryError, list_records, transition

    requested = [str(source_id) for source_id in source_ids]
    if not requested or len(requested) != len(set(requested)):
        return {"state": "BLOCKED", "disposition": "RETRY_SOURCE_SELECTION_INVALID", "reason": "Select one or more unique failed/rejected PixelLab sources."}
    snapshot = dict(settings or {})
    configured_game_project = _configured_game_project(snapshot)
    if configured_game_project is None:
        return {"state": "BLOCKED", "disposition": "PINNED_GAME_PROJECT_MISSING", "reason": "Configured ScrubBots project is missing project.godot; no retry was queued."}
    snapshot["game_project"] = configured_game_project

    current = {
        str(row.get("source_id", "")): row
        for row in list_records(repository_root=extensions._repository_root()).get("records", [])
        if isinstance(row, Mapping)
    }
    selected: list[dict[str, Any]] = []
    for source_id in requested:
        row = current.get(source_id)
        if (row is None or row.get("status") not in {"FAILED", "REJECTED"}
                or str(row.get("provider", "")).upper() != "PIXELLAB"):
            return {"state": "BLOCKED", "disposition": "RETRY_SOURCE_NOT_FAILED_OR_REJECTED",
                    "source_id": source_id,
                    "reason": "Retry requires a current SHA-matched PIXELLAB Release Pool record whose latest status is FAILED or REJECTED."}
        source_sha = str(row.get("source_sha256", ""))
        try:
            source = extensions.verify_owner_source(source_id)
        except Exception as exc:
            return {"state": "BLOCKED", "disposition": "RETRY_SOURCE_CHANGED", "source_id": source_id,
                    "reason": f"Current source could not be verified: {str(exc)[:240]}"}
        if (source_id != "owner-upload-" + source_sha
                or source.get("source_sha256") != source_sha
                or not str(source.get("original_filename", "")).lower().endswith(".png")):
            return {"state": "BLOCKED", "disposition": "RETRY_SOURCE_CHANGED", "source_id": source_id,
                    "reason": "Current source bytes or filename no longer match the saved Release Pool identity."}
        selected.append(dict(row))

    # Persist the immutable source snapshot before changing any current status.
    composite = extensions.create_loaded_png_batch(requested)
    batch_id = str(composite.get("batch_id", ""))
    if not batch_id:
        return {"state": "BLOCKED", "disposition": "RETRY_SNAPSHOT_FAILED", "reason": "An immutable retry source snapshot could not be created."}

    retry_events: list[dict[str, Any]] = []
    for row in selected:
        source_id = str(row["source_id"])
        try:
            retry_events.append(transition(
                source_id, "PENDING", source_sha256=str(row["source_sha256"]),
                provider="PIXELLAB", original_source_path=str(row["original_source_path"]),
                reason="Explicit Solve Again retry queued; prior %s result and reason remain in immutable history." % row["status"],
                batch_id=batch_id, retry_of=str(row["event_sha256"]),
                evidence={"explicit_retry": True, "retry_source": "CURRENT_RELEASE_POOL_STATUS",
                          "prior_status": str(row["status"]), "prior_reason": str(row.get("reason", ""))[:512],
                          "retry_source_event_sha256": str(row["event_sha256"]), "retry_snapshot_batch_id": batch_id},
                repository_root=extensions._repository_root(),
            ))
        except (OwnerReleaseLibraryError, OSError, ValueError) as exc:
            return {"state": "ERROR", "disposition": "RETRY_PENDING_PROJECTION_FAILED",
                    "queued_source_ids": [str(event.get("source_id", "")) for event in retry_events],
                    "source_id": source_id, "reason": str(exc)[:512]}

    created = create_png_batch(batch_id, snapshot)
    if str(created.get("state", "")) != "SUCCESS" or not isinstance(created.get("job"), Mapping):
        return {"state": "ERROR", "disposition": "RETRY_QUEUED_JOB_CREATION_FAILED",
                "queued_source_ids": [str(event.get("source_id", "")) for event in retry_events],
                "reason": str(created.get("reason", created.get("disposition", "Retry remains safely Pending; no solver ran."))),
                "job": created.get("job", {})}
    return {"state": "SUCCESS", "disposition": "RETRY_CREATED_FROM_RELEASE_POOL",
            "retry_events": retry_events, "composite": composite, "job": created["job"]}


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


def find_resumable_pending_batch(
    pending_snapshot: Mapping[str, Any],
    active_source_ids: Sequence[str],
) -> dict[str, Any]:
    """Find a durable in-flight job whose unfinished rows still match current Pending.

    The immutable batch snapshot remains the original job's full source set. As
    rows finish, Pending shrinks, so an exact snapshot lookup cannot recover the
    job after restart. This read-only matcher binds every persisted row to its
    original snapshot, the current Final source set, and its latest Release Pool
    status before offering that job for resume.
    """
    from . import studio_extensions as extensions
    from .owner_release_library import list_records

    pending_rows = [row for row in pending_snapshot.get("items", []) if isinstance(row, Mapping)]
    pending_by_id = {
        str(row.get("source_id", "")): (str(row.get("source_sha256", "")), str(row.get("source_record_sha256", "")))
        for row in pending_rows
    }
    if not pending_by_id or len(pending_by_id) != len(pending_rows):
        return {"state": "SUCCESS", "disposition": "NO_MATCHING_COMPOSITE", "batch": None, "mutated": False}
    active_ids = {str(source_id) for source_id in active_source_ids if str(source_id)}
    if not pending_by_id.keys() <= active_ids:
        return {"state": "BLOCKED", "disposition": "ACTIVE_FINAL_SET_MISMATCH", "batch": None, "mutated": False}

    status_by_id = {
        str(row.get("source_id", "")): row
        for row in list_records().get("records", [])
        if isinstance(row, Mapping)
    }
    pending_candidate_ids = set(pending_by_id)
    job_root = _root() / "jobs"
    if not job_root.exists():
        return {"state": "SUCCESS", "disposition": "NO_MATCHING_COMPOSITE", "batch": None, "mutated": False}

    resumable: list[tuple[dict[str, Any], dict[str, Any], set[str]]] = []
    conflicting_overlap: list[str] = []
    # PROJECTION_ERROR is retryable: a durable solver result exists and only its
    # Release Pool status projection still needs repair (run_png_batch resumes it).
    resumable_states = {"QUEUED", "PAUSED", "STOPPED", "INTERRUPTED", "RUNNING", "PROJECTION_ERROR"}
    unfinished_states = {"QUEUED", "RUNNING", "VERIFYING_EXISTING"}
    terminal_states = {"READY", "FAILED", "REJECTED"}
    for path in sorted(job_root.glob("png-batch-*.json")):
        try:
            job = _read_job(path.stem)
            if str(job.get("state", "")) not in resumable_states:
                continue
            batch_id = str(job.get("import_batch_id", ""))
            batch = extensions.batch_load(batch_id)["batch"]
            if (batch.get("version") != 2 or batch.get("kind") != "COMPOSITE_LOADED_SOURCE_SNAPSHOT"
                    or extensions._digest(batch) != job.get("batch_digest")
                    or not _job_lineage_matches_snapshot(job, batch)):
                continue
            batch_rows = [row for row in batch.get("items", []) if isinstance(row, Mapping)]
            job_rows = [row for row in job.get("items", []) if isinstance(row, Mapping)]
            if len(batch_rows) != len(job_rows) or not job_rows:
                continue
            needs_resume: set[str] = set()
            valid = True
            overlap: set[str] = set()
            for index, (item, source) in enumerate(zip(job_rows, batch_rows, strict=True)):
                source_id = str(item.get("source_id", ""))
                source_sha = str(item.get("source_sha256", ""))
                record_sha = str(item.get("source_record_sha256", ""))
                status = status_by_id.get(source_id)
                if (int(item.get("index", -1)) != index
                        or source_id != str(source.get("source_id", ""))
                        or source_sha != str(source.get("source_sha256", ""))
                        or record_sha != str(source.get("source_record_sha256", ""))
                        or source_id not in active_ids
                        or not isinstance(status, Mapping)
                        or str(status.get("source_sha256", "")) != source_sha):
                    valid = False
                    break
                item_state = str(item.get("status", ""))
                current_state = str(status.get("status", ""))
                if item_state in unfinished_states:
                    if current_state != "PENDING":
                        valid = False
                        break
                    needs_resume.add(source_id)
                elif item_state in terminal_states:
                    projection = item.get("owner_release_projection", {})
                    if current_state == "PENDING" and isinstance(projection, Mapping) and projection.get("state") != "RECORDED":
                        # A durable solver result exists but its current status
                        # projection still needs repair before the next item.
                        needs_resume.add(source_id)
                    elif current_state != item_state:
                        valid = False
                        break
                else:
                    valid = False
                    break
                if source_id in pending_candidate_ids:
                    if pending_by_id[source_id] != (source_sha, record_sha):
                        valid = False
                        break
                    overlap.add(source_id)
                elif item_state in unfinished_states or source_id in needs_resume:
                    valid = False
                    break
            if not valid or not overlap:
                if overlap:
                    conflicting_overlap.extend([str(job.get("job_id", path.stem))])
                continue
            if not needs_resume <= pending_candidate_ids:
                conflicting_overlap.append(str(job.get("job_id", path.stem)))
                continue
            resumable.append((job, batch, needs_resume))
        except (OSError, ValueError, KeyError, TypeError):
            continue

    if len(resumable) == 1 and pending_candidate_ids - resumable[0][2]:
        # Newer Pending PNGs exist that this saved job does not contain. Offer a
        # fresh Pending batch over all of them; creating it supersedes this job.
        job, batch, needs_resume = resumable[0]
        # Owner request 2026-11-13: also offer the stopped job itself (for example
        # a half-finished retry) so the owner can choose it or all Pending PNGs.
        return {"state": "SUCCESS", "disposition": "NO_MATCHING_COMPOSITE", "batch": None,
                "superseded_candidate_job_id": str(job.get("job_id", "")),
                "pending_count": len(pending_candidate_ids),
                "uncovered_pending_count": len(pending_candidate_ids - needs_resume),
                "resume_batch": batch, "resume_job_id": str(job.get("job_id", "")),
                "resume_count": len(needs_resume), "mutated": False}
    if len(resumable) == 1:
        job, batch, needs_resume = resumable[0]
        return {"state": "SUCCESS", "disposition": "RESUMABLE_PENDING_SUBSET", "batch": batch,
                "resume_job_id": str(job.get("job_id", "")),
                "resume_count": len(needs_resume), "pending_count": len(pending_candidate_ids),
                "ignored_stale_job_ids": sorted(set(conflicting_overlap)), "mutated": False}
    if len(resumable) > 1 or conflicting_overlap:
        ids = sorted({str(job.get("job_id", "")) for job, _batch, _rows in resumable} | set(conflicting_overlap))
        return {"state": "BLOCKED", "disposition": "PENDING_BATCH_RESUME_AMBIGUOUS",
                "candidate_job_ids": ids, "batch": None, "mutated": False}
    return {"state": "SUCCESS", "disposition": "NO_MATCHING_COMPOSITE", "batch": None, "mutated": False}


def png_batch_status(job_id: str) -> dict[str, Any]:
    job = _read_job(job_id)
    public = dict(job)
    public["mutated"] = False
    return {"state": "SUCCESS", "disposition": "STATUS", "job": public}


def _job_lineage_matches_snapshot(job: Mapping[str, Any], batch: Mapping[str, Any]) -> bool:
    """Validate the whole persisted retry chain against the immutable composite."""
    from .studio_extensions import _digest, batch_load

    batch_id = str(job.get("import_batch_id", ""))
    try:
        exact_batch = batch_load(batch_id)["batch"]
    except Exception:
        return False
    expected_digest = _digest(exact_batch)
    if (job.get("batch_digest") != expected_digest
            or job.get("import_batch_id") != batch.get("batch_id")):
        return False
    current = dict(job)
    visited: set[str] = set()
    while current.get("parent_job_id"):
        parent_id = str(current.get("parent_job_id", ""))
        if parent_id in visited:
            return False
        visited.add(parent_id)
        try:
            parent = _read_job(parent_id)
        except Exception:
            return False
        if (parent.get("state") != "COMPLETE"
                or parent.get("state_digest") != current.get("parent_job_state_digest")
                or parent.get("import_batch_id") != batch_id
                or parent.get("batch_digest") != expected_digest):
            return False
        parent_items = {str(item.get("index")): item for item in parent.get("items", []) if isinstance(item, Mapping)}
        expected_failed = [str(item.get("index")) for item in parent.get("items", [])
                           if isinstance(item, Mapping) and item.get("status") in {"FAILED", "REJECTED"}]
        actual_parent_indexes = [str(item.get("prior_item_index", "")) for item in current.get("items", [])
                                 if isinstance(item, Mapping)]
        if (not actual_parent_indexes or len(set(actual_parent_indexes)) != len(actual_parent_indexes)
                or any(index not in expected_failed for index in actual_parent_indexes)):
            return False
        for item in current.get("items", []):
            if not isinstance(item, Mapping):
                return False
            previous = parent_items.get(str(item.get("prior_item_index")))
            if (previous is None or previous.get("status") not in {"FAILED", "REJECTED"}
                    or previous.get("source_id") != item.get("source_id")
                    or previous.get("source_sha256") != item.get("source_sha256")
                    or previous.get("source_record_sha256") != item.get("source_record_sha256")
                    or previous.get("column_count") != item.get("column_count")
                    or item.get("prior_attempt", {}).get("status") not in {"FAILED", "REJECTED"}):
                return False
        current = parent
    rows = [item for item in exact_batch.get("items", []) if isinstance(item, Mapping)]
    root_items = current.get("items", [])
    if (current.get("snapshot_source_count") != len(rows)
            or len(root_items) != len(rows)
            or [str(item.get("source_id", "")) for item in root_items] != [str(row.get("source_id", "")) for row in rows]):
        return False
    is_composite = exact_batch.get("version") == 2 and exact_batch.get("kind") == "COMPOSITE_LOADED_SOURCE_SNAPSHOT"
    eligible_ids = [str(item.get("source_id", "")) for item in root_items if item.get("column_count") in (3, 4, 5)]
    assignments = dict(zip(eligible_ids, assign_columns(eligible_ids), strict=True)) if is_composite else {}
    for root_item, row in zip(root_items, rows, strict=True):
        if root_item.get("source_id") != row.get("source_id"):
            return False
        if is_composite and (root_item.get("source_sha256") != row.get("source_sha256")
                or root_item.get("source_record_sha256") != row.get("source_record_sha256")
                or root_item.get("column_count") != assignments.get(str(row.get("source_id", "")))):
            return False
        if not is_composite and root_item.get("column_count") not in (None, 3, 4, 5):
            return False
    return True


def _record_legacy_resume_choice(job: Mapping[str, Any], batch: Mapping[str, Any]) -> None:
    """Append immutable evidence only after an explicit owner resume request."""
    if (batch.get("version") != 2 or batch.get("kind") != "COMPOSITE_LOADED_SOURCE_SNAPSHOT"
            or batch.get("provenance_policy") == "ORIGINAL_V1_IMPORT_MEMBERSHIP_SOURCE_IDENTITY_V1"):
        return
    basis = {"job_id": job.get("job_id"), "batch_id": batch.get("batch_id"),
             "batch_digest": job.get("batch_digest"), "owner_action": "EXPLICIT_RESUME"}
    choice_id = hashlib.sha256(_canonical(basis)).hexdigest()
    payload = {"schema": "scrubbots-png-batch-legacy-reconciliation", "version": 1,
               "choice_id": choice_id, **basis, "recorded_at": _now()}
    path = _root() / "reconciliations" / f"legacy-resume-{choice_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = _canonical(payload)
    if path.exists():
        if path.read_bytes() != encoded:
            # The first explicit choice is immutable; don't overwrite it with a new timestamp.
            existing = json.loads(path.read_text(encoding="utf-8"))
            if any(existing.get(key) != value for key, value in {"schema": payload["schema"], **basis, "choice_id": choice_id}.items()):
                raise ValueError("legacy reconciliation evidence conflicts with the current SHA-bound owner choice")
        return
    path.write_bytes(encoded)


def png_batch_latest(batch_id: str | None = None) -> dict[str, Any]:
    jobs: list[dict[str, Any]] = []
    job_root = _root() / "jobs"
    if job_root.exists():
        candidates = sorted(job_root.glob("png-batch-*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        if batch_id is None:
            candidates = candidates[:20]
        for path in candidates:
            try:
                jobs.append(_read_job(path.stem))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
    resumable = next((job for job in jobs if job.get("state") not in {"COMPLETE", "STOPPED", "SUPERSEDED"}), None)
    if batch_id is None:
        return {"state": "SUCCESS", "disposition": "LATEST", "job": resumable, "jobs": jobs, "mutated": False}
    from .studio_extensions import _digest, batch_load

    try:
        expected_digest = _digest(batch_load(batch_id)["batch"])
    except Exception:
        return {"state": "BLOCKED", "disposition": "BATCH_JOB_SOURCE_MISMATCH", "job": None, "mismatch_job": resumable, "jobs": jobs, "mutated": False}
    matching_candidates = [
        job for job in jobs
        if job.get("import_batch_id") == batch_id and job.get("batch_digest") == expected_digest
    ]
    matching = max(matching_candidates, key=lambda job: str(job.get("updated_at", "")), default=None)
    mismatch = resumable if resumable is not None and matching is None else None
    if matching is not None and not _job_lineage_matches_snapshot(matching, batch_load(batch_id)["batch"]):
        return {"state": "BLOCKED", "disposition": "BATCH_JOB_SOURCE_MISMATCH", "job": None,
                "mismatch_job": matching, "jobs": jobs, "batch_id": batch_id,
                "batch_digest": expected_digest, "mutated": False}
    return {
        "state": "SUCCESS" if matching is not None or mismatch is None else "BLOCKED",
        "disposition": "MATCHED" if matching is not None else "BATCH_JOB_SOURCE_MISMATCH" if mismatch is not None else "NO_MATCHING_JOB",
        "job": ({**matching, "lineage_verified": True} if matching is not None else None), "mismatch_job": mismatch, "jobs": jobs, "batch_id": batch_id,
        "batch_digest": expected_digest, "mutated": False,
    }


def png_batch_control(job_id: str, action: str) -> dict[str, Any]:
    if action not in {"PAUSE_AFTER_CURRENT", "STOP_AFTER_CURRENT", "CANCEL_NOW"}:
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
    from .studio_extensions import _read_json, _enter_candidate_release_pool, _pipeline_paths, list_candidates

    matches = []
    for path in _pipeline_paths():
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
    from .studio_extensions import (
        _enter_candidate_release_pool, _latest_ready_pipeline, _pipeline_path,
        _read_json, _source_record_paths, list_candidates, restore_source_run,
    )

    source_id = str(item["source_id"])
    source_sha256 = str(item.get("source_sha256", ""))
    source_record_sha256 = str(item.get("source_record_sha256", ""))
    columns = int(item.get("column_count", 0))
    restored: dict[str, Any] | None = None
    run_id = item.get("run_id")
    if isinstance(run_id, str) and run_id.startswith("pipeline-"):
        try:
            exact_run = _read_json(_pipeline_path(run_id))
            exact_candidate_id = str(exact_run.get("candidate_id", ""))
            record_path, source_path = _source_record_paths(
                source_id, job.get("settings", {}).get("source_directory")
            )
            source_unchanged = (
                hashlib.sha256(record_path.read_bytes()).hexdigest() == source_record_sha256
                and hashlib.sha256(source_path.read_bytes()).hexdigest() == source_sha256
            )
            latest = _latest_ready_pipeline(exact_candidate_id) if exact_candidate_id else None
            if (
                source_unchanged
                and latest is not None and latest.get("run_id") == run_id
                and _has_ready_pipeline_proof(
                    exact_run, source_id, expected_columns=columns,
                    source_record_sha256=source_record_sha256,
                    job=job, item=item,
                )
                and _verify_column_artifacts(exact_run, columns)
            ):
                restored = {
                    "state": "READY", "source_id": source_id,
                    "source_sha256": source_sha256, "candidate_id": exact_candidate_id,
                    "pipeline": exact_run,
                }
        except (OSError, ValueError, TypeError, KeyError):
            restored = None
    if restored is None:
        restored = restore_source_run(
            source_id,
            game_project=job.get("settings", {}).get("game_project"),
            source_directory=job.get("settings", {}).get("source_directory"),
        )
    if restored.get("state") != "READY" or restored.get("source_sha256") != item.get("source_sha256"):
        return None
    if restored.get("owner_review_status", {}).get("pool_state") == "EXCLUDED_FROM_RELEASE_POOL":
        return {"rejected": True, "reason": "SOURCE_CANDIDATE_IS_OWNER_REJECTED"}
    pipeline = restored.get("pipeline", {})
    source_record_sha = source_record_sha256
    if (not _has_ready_pipeline_proof(
            pipeline, source_id, expected_columns=columns,
            source_record_sha256=source_record_sha, job=job, item=item)
            or not _verify_column_artifacts(pipeline, columns)):
        return None
    candidate_id = str(restored.get("candidate_id", ""))
    try:
        candidate = next((row for row in list_candidates() if row.get("candidate_id") == candidate_id), None)
    except Exception as exc:
        return {
            "pipeline": pipeline,
            "release_pool": {"disposition": "NOT_ENTERED", "readback_verified": False},
            "pool_retryable_error": f"Candidate read-back failed: {str(exc)[:320]}",
        }
    if candidate is None:
        return {
            "pipeline": pipeline,
            "release_pool": {"disposition": "NOT_ENTERED", "readback_verified": False},
            "pool_retryable_error": "READY pipeline references a candidate missing from canonical candidate read-back.",
        }
    if not _candidate_has_source_lineage(candidate, source_id, str(item.get("source_sha256", ""))):
        return None
    try:
        pool = _enter_candidate_release_pool(candidate, pipeline=pipeline)
    except Exception as exc:
        pool = {"disposition": "NOT_ENTERED", "readback_verified": False, "reason": str(exc)[:400]}
    if not pool.get("readback_verified"):
        return {
            "pipeline": pipeline,
            "release_pool": pool,
            "pool_retryable_error": str(pool.get("reason") or "Release Pool did not confirm the exact READY_AUTO candidate/run row.")[:400],
        }
    try:
        matches_pool = _pool_row_matches(pipeline, candidate, source_id, columns)
    except Exception as exc:
        return {
            "pipeline": pipeline,
            "release_pool": pool,
            "pool_retryable_error": f"Release Pool row verification failed: {str(exc)[:320]}",
        }
    if not matches_pool:
        return {
            "pipeline": pipeline,
            "release_pool": pool,
            "pool_retryable_error": "Release Pool read-back did not match this READY source identity and selected column count.",
        }
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
        if job.get("state") == "SUPERSEDED":
            return {"state": "BLOCKED", "disposition": "BATCH_JOB_SUPERSEDED", "job": job,
                    "reason": f"This job was replaced by {job.get('superseded_by', 'a newer Pending batch')}."}
        if job.get("state") == "COMPLETE":
            disposition = "FINISHED_WITH_FAILURES" if int(job.get("counts", {}).get("failed", 0)) or int(job.get("counts", {}).get("rejected", 0)) else "COMPLETE"
            return {"state": "SUCCESS", "disposition": disposition, "job": job, "mutated": False}
        batch = extensions.batch_load(str(job.get("import_batch_id", "")))["batch"]
        if extensions._digest(batch) != job.get("batch_digest"):
            return {"state": "BLOCKED", "disposition": "BATCH_JOB_SOURCE_MISMATCH", "job": job, "reason": "Import batch manifest digest changed after the immutable PNG solver plan was created."}
        if batch.get("version") == 2 and batch.get("kind") == "COMPOSITE_LOADED_SOURCE_SNAPSHOT" and not _job_lineage_matches_snapshot(job, batch):
            return {"state": "BLOCKED", "disposition": "BATCH_JOB_SOURCE_MISMATCH", "job": job,
                    "reason": "Persisted plan or retry parent does not match the exact SHA-bound source snapshot."}
        # Resume continues only unfinished queue items. FAILED and REJECTED are
        # terminal current outcomes; only the explicit Solve Again action may
        # move them back to Pending and create a retry snapshot.
        _record_legacy_resume_choice(job, batch)
        _rebind_superseded_runtime(job)
        _clear_control(job_id)
        job["state"] = "RUNNING"
        job["updated_at"] = _now()
        job = _write_job(job)
        # Recover a previous crash or Release Pool write error before solving
        # another PNG. Terminal solver evidence is immutable; only its current
        # status projection is repaired here.
        for terminal_item in job.get("items", []):
            if (not isinstance(terminal_item, dict)
                    or terminal_item.get("status") not in {"READY", "FAILED", "REJECTED"}
                    or terminal_item.get("owner_release_projection", {}).get("state") == "RECORDED"):
                continue
            projection_error = _persist_projection_or_pause(job, terminal_item)
            if projection_error is not None:
                return projection_error
            job = _write_job(job)
        # Owner request 2026-11-12: one level took ~13 minutes, almost all of it
        # inside one solver Godot process, so a sequential queue could not reach
        # 100 levels a day. Up to ``workers`` items now solve concurrently. Every
        # item still runs the identical canonical pipeline; solver jobs, run
        # output folders, activity files and Release Pool entries are already
        # per-item, and all job-state writes stay on this thread.
        workers = parallel_workers(job.get("settings", {}))
        in_flight: dict[Future, tuple[int, dict[str, Any]]] = {}
        stop_state: str | None = None

        def running_index() -> int | None:
            return min((index for index, _item in in_flight.values()), default=None)

        def finish(item_index: int, item: dict[str, Any], pipeline: Any, error: Exception | None) -> dict[str, Any] | None:
            nonlocal job
            if error is not None:
                item.update({"status": "FAILED", "reason": str(error)[:512], "finished_at": _now()})
            else:
                primary = pipeline.get("primary", {}) if isinstance(pipeline, Mapping) else {}
                pool = pipeline.get("release_pool", {}) if isinstance(pipeline, Mapping) else {}
                try:
                    ready = (
                        _has_ready_pipeline_proof(
                            pipeline, str(item["source_id"]), expected_columns=int(item["column_count"]),
                            source_record_sha256=str(item["source_record_sha256"]), job=job, item=item)
                        and _verify_column_artifacts(pipeline, int(item["column_count"]))
                    )
                except Exception as exc:
                    item.update({"status": "FAILED", "reason": str(exc)[:512], "finished_at": _now()})
                    ready = None
                if ready is None:
                    pass
                elif ready and pool.get("readback_verified") is True:
                    item.update({"status": "READY", "run_id": pipeline.get("run_id"), "candidate_id": pipeline.get("candidate_id"), "artifact_refs": primary.get("files", {}), "release_pool": pool, "finished_at": _now()})
                    job["ready_mix"][str(item["column_count"])] = int(job["ready_mix"].get(str(item["column_count"]), 0)) + 1
                elif ready:
                    pool_reason = str(pool.get("reason") or pool.get("disposition") or "Release Pool did not confirm the exact READY_AUTO candidate/run row.")
                    item.update({"status": "FAILED", "run_id": pipeline.get("run_id"), "candidate_id": pipeline.get("candidate_id"), "release_pool": pool, "reason": f"READY_POOL_ENTRY_FAILED: {pool_reason[:400]}", "finished_at": _now()})
                else:
                    item.update({"status": "FAILED", "run_id": pipeline.get("run_id") if isinstance(pipeline, Mapping) else None, "reason": _failure_reason(pipeline), "finished_at": _now()})
            job["current_index"] = running_index()
            job["counts"] = _counts(job["items"])
            job["updated_at"] = _now()
            job = _write_job(job)
            projection_error = _persist_projection_or_pause(job, item)
            if projection_error is not None:
                return projection_error
            job = _write_job(job)
            return None

        def collect(return_when: str) -> dict[str, Any] | None:
            """Record finished items; a CANCEL_NOW leaves the cancelled items RUNNING for recovery."""
            nonlocal job
            done, _pending = wait(list(in_flight), return_when=return_when)
            if _control_action(job_id) == "CANCEL_NOW":
                wait(list(in_flight))
                job["state"] = "INTERRUPTED"
                job["current_index"] = running_index()
                job["counts"] = _counts(job["items"])
                job["updated_at"] = _now()
                _clear_control(job_id)
                job = _write_job(job)
                return {"state": "SUCCESS", "disposition": "INTERRUPTED", "job": job}
            for future in sorted(done, key=lambda value: in_flight[value][0]):
                item_index, item = in_flight.pop(future)
                try:
                    pipeline, error = future.result(), None
                except Exception as exc:
                    pipeline, error = None, exc
                outcome = finish(item_index, item, pipeline, error)
                if outcome is not None:
                    return outcome
            return None

        control_env = "SCRUBBOTS_FACTORY_BATCH_CONTROL_FILE"
        previous_control_file = os.environ.get(control_env)
        os.environ[control_env] = str(_control_path(job_id))
        executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="png-batch")
        try:
            for item_index, item in enumerate(job["items"]):
                from .studio_lifecycle import studio_shutdown_requested
                if studio_shutdown_requested():
                    stop_state = "INTERRUPTED"
                    break
                if item.get("status") in {"READY", "FAILED", "REJECTED", "SKIPPED_DUPLICATE", "SKIPPED"}:
                    continue
                action = _control_action(job_id)
                if action:
                    stop_state = "PAUSED" if action == "PAUSE_AFTER_CURRENT" else "INTERRUPTED" if action == "CANCEL_NOW" else "STOPPED"
                    break
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
                    job["current_index"] = running_index()
                    job["updated_at"] = _now()
                    job = _write_job(job)
                    projection_error = _persist_projection_or_pause(job, item)
                    if projection_error is not None:
                        return projection_error
                    job = _write_job(job)
                    continue
                if item.get("status") == "RUNNING":
                    recovered = _recover_attempt(job, item)
                    if recovered is not None:
                        pipeline = recovered["pipeline"]
                        item.update({"status": "READY", "run_id": pipeline.get("run_id"), "candidate_id": pipeline.get("candidate_id"), "artifact_refs": pipeline.get("primary", {}).get("files", {}), "release_pool": recovered["release_pool"], "recovered_after_interruption": True, "finished_at": _now()})
                        job["counts"] = _counts(job["items"])
                        job["ready_mix"][str(item["column_count"])] = int(job["ready_mix"].get(str(item["column_count"]), 0)) + 1
                        job["current_index"] = running_index()
                        job["updated_at"] = _now()
                        job = _write_job(job)
                        projection_error = _persist_projection_or_pause(job, item)
                        if projection_error is not None:
                            return projection_error
                        job = _write_job(job)
                        continue
                    item["status"] = "QUEUED"
                    item["reason"] = "PRIOR_ATTEMPT_INTERRUPTED_WITHOUT_COMPLETE_CANONICAL_RUN"
                    job["updated_at"] = _now()
                    job = _write_job(job)
                item.update({"status": "VERIFYING_EXISTING", "reason": "Checking for already complete artifact-verified READY evidence."})
                job["current_index"] = item_index if running_index() is None else running_index()
                job["updated_at"] = _now()
                job = _write_job(job)
                try:
                    reused = _reuse_existing_ready(job, item)
                except Exception as exc:
                    reused = None
                    item["existing_ready_check_error"] = str(exc)[:400]
                if reused is not None and reused.get("pool_retryable_error"):
                    pipeline = reused.get("pipeline", {})
                    item.update({
                        "status": "FAILED",
                        "run_id": pipeline.get("run_id") if isinstance(pipeline, Mapping) else None,
                        "candidate_id": pipeline.get("candidate_id") if isinstance(pipeline, Mapping) else None,
                        "release_pool": reused.get("release_pool", {}),
                        "reason": f"READY_POOL_ENTRY_FAILED: {reused['pool_retryable_error']}",
                        "finished_at": _now(),
                    })
                    job["counts"] = _counts(job["items"])
                    job["current_index"] = running_index()
                    job["updated_at"] = _now()
                    job = _write_job(job)
                    projection_error = _persist_projection_or_pause(job, item)
                    if projection_error is not None:
                        return projection_error
                    job = _write_job(job)
                    continue
                if reused is not None and reused.get("rejected"):
                    item.update({"status": "REJECTED", "reason": str(reused.get("reason", "SOURCE_CANDIDATE_IS_OWNER_REJECTED")), "finished_at": _now()})
                    job["counts"] = _counts(job["items"])
                    job["current_index"] = running_index()
                    job["updated_at"] = _now()
                    job = _write_job(job)
                    projection_error = _persist_projection_or_pause(job, item)
                    if projection_error is not None:
                        return projection_error
                    job = _write_job(job)
                    continue
                if reused is not None:
                    pipeline = reused["pipeline"]
                    item.update({"status": "READY", "run_id": pipeline.get("run_id"), "candidate_id": pipeline.get("candidate_id"), "artifact_refs": pipeline.get("primary", {}).get("files", {}), "release_pool": reused["release_pool"], "reused_existing_ready": True, "finished_at": _now()})
                    job["counts"] = _counts(job["items"])
                    job["ready_mix"][str(item["column_count"])] = int(job["ready_mix"].get(str(item["column_count"]), 0)) + 1
                    job["current_index"] = running_index()
                    job["updated_at"] = _now()
                    job = _write_job(job)
                    projection_error = _persist_projection_or_pause(job, item)
                    if projection_error is not None:
                        return projection_error
                    job = _write_job(job)
                    continue
                attempt_id = "batch-%s-%03d-%s" % (job_id.removeprefix("png-batch-")[:12], item_index + 1, uuid.uuid4().hex[:12])
                activity_id = "pipeline-ui-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + hashlib.sha256(attempt_id.encode()).hexdigest()[:12]
                item.update({"status": "RUNNING", "attempt_id": attempt_id, "activity_run_id": activity_id, "started_at": _now(), "reason": ""})
                job["state"] = "RUNNING"
                job["current_index"] = item_index if running_index() is None else running_index()
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
                    # Batch runs use a smaller default search budget to keep one hard
                    # image from monopolizing a worker. Explicit owner settings
                    # remain honored up to the existing canonical maximum.
                    "candidates": min(int(request.get("candidates", 48)), 300),
                    "real_max_visited": min(int(request.get("real_max_visited", 25_000)), 25_000),
                    "solver_timeout_seconds": min(float(request.get("solver_timeout_seconds", 900)), 900),
                })
                try:
                    _persist_owner_release_attempt(job, item)
                    job["updated_at"] = _now()
                    job = _write_job(job)
                except Exception as exc:
                    outcome = finish(item_index, item, None, exc)
                    if outcome is not None:
                        return outcome
                    continue
                in_flight[executor.submit(runner, source_id=str(item["source_id"]), request=request)] = (item_index, item)
                job["current_index"] = running_index()
                job = _write_job(job)
                while len(in_flight) >= workers:
                    outcome = collect(FIRST_COMPLETED)
                    if outcome is not None:
                        return outcome
            # Stop/Pause "after current" lets every already running item finish.
            while in_flight:
                outcome = collect(FIRST_COMPLETED)
                if outcome is not None:
                    return outcome
        finally:
            executor.shutdown(wait=True)
            if previous_control_file is None:
                os.environ.pop(control_env, None)
            else:
                os.environ[control_env] = previous_control_file
        if stop_state is not None:
            job["state"] = stop_state
            job["current_index"] = None
            job["counts"] = _counts(job["items"])
            job["updated_at"] = _now()
            _clear_control(job_id)
            job = _write_job(job)
            return {"state": "SUCCESS", "disposition": stop_state, "job": job}
        job["state"] = "COMPLETE"
        job["current_index"] = None
        job["counts"] = _counts(job["items"])
        job["updated_at"] = _now()
        job = _write_job(job)
        disposition = "FINISHED_WITH_FAILURES" if int(job.get("counts", {}).get("failed", 0)) or int(job.get("counts", {}).get("rejected", 0)) else "COMPLETE"
        return {"state": "SUCCESS", "disposition": disposition, "job": job}
