"""Append-only owner-facing artwork outcomes, separate from canonical READY release authority."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time
from typing import Any, Iterator, Mapping

from . import owner_art_storage

SCHEMA = "scrubbots-owner-release-library-event/v1"
STATUSES = {"PENDING", "READY", "FAILED", "REJECTED"}
_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")

class OwnerReleaseLibraryError(ValueError):
    """Owner archive evidence is malformed or conflicts with immutable history."""

def _root(repository_root: str | Path | None = None) -> Path:
    return owner_art_storage.owner_art_paths(repository_root)["release_pool"]

def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def _reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    except OSError:
        return True
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)

def _safe_directory(root: Path, target: Path) -> None:
    if not root.exists() or _reparse(root): raise OwnerReleaseLibraryError("owner release root is missing or unsafe")
    base = root.resolve(); current = base
    try: relative = target.relative_to(root)
    except ValueError as exc: raise OwnerReleaseLibraryError("owner release path escaped its root") from exc
    for part in relative.parts:
        current = current / part
        if _reparse(current): raise OwnerReleaseLibraryError("owner release path contains a reparse point")
        if current.exists():
            if not current.is_dir() or current.resolve() != current: raise OwnerReleaseLibraryError("owner release component is not a canonical directory")
        else:
            current.mkdir()

def _verify_existing_path(root: Path, target: Path) -> None:
    if not root.exists() or _reparse(root): raise OwnerReleaseLibraryError("owner release root is missing or unsafe")
    try: relative = target.relative_to(root)
    except ValueError as exc: raise OwnerReleaseLibraryError("owner release read escaped its root") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if _reparse(current): raise OwnerReleaseLibraryError("owner release read path contains a reparse point")
        if current.exists() and current.resolve() != current:
            raise OwnerReleaseLibraryError("owner release read path is not canonical")

@contextmanager
def _lock(path: Path, root: Path) -> Iterator[None]:
    _safe_directory(root, path.parent)
    if _reparse(path):
        raise OwnerReleaseLibraryError("owner release lock path is unsafe")
    with path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt
            if path.stat().st_size == 0:
                handle.seek(0); handle.write(b"\0"); handle.flush()
            handle.seek(0); deadline = time.monotonic() + 12
            while True:
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1); break
                except OSError as exc:
                    if time.monotonic() >= deadline:
                        raise OwnerReleaseLibraryError("owner release source lock timed out") from exc
                    time.sleep(.025)
            try:
                yield
            finally:
                handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try: yield
            finally: fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

def _create_immutable(path: Path, raw: bytes, root: Path) -> None:
    if _reparse(path):
        raise OwnerReleaseLibraryError("owner release immutable target is a reparse point")
    _safe_directory(root, path.parent)
    temp = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.partial")
    try:
        with temp.open("xb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        try: os.link(temp, path)
        except FileExistsError:
            if not path.is_file() or path.read_bytes() != raw:
                raise OwnerReleaseLibraryError("owner release immutable target has conflicting bytes")
    finally:
        temp.unlink(missing_ok=True)

def _replace_projection(path: Path, raw: bytes, root: Path, *, expected_event_sha256: str | None = None) -> None:
    if _reparse(path):
        raise OwnerReleaseLibraryError("owner release status projection is a reparse point")
    _safe_directory(root, path.parent)
    if path.exists():
        if expected_event_sha256 is None:
            raise OwnerReleaseLibraryError("owner release status projection already exists without a verified prior event")
        try:
            current = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise OwnerReleaseLibraryError("prior owner release status projection is unreadable") from exc
        if not isinstance(current, dict) or current.get("event_sha256") != expected_event_sha256:
            raise OwnerReleaseLibraryError("prior owner release status projection does not match immutable history")
        current_digest = str(current.pop("event_sha256", ""))
        if _hash(_json_bytes(current)) != current_digest:
            raise OwnerReleaseLibraryError("prior owner release status projection digest is invalid")
    temp = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.partial")
    try:
        with temp.open("xb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)

def _ensure_status_artwork(root: Path, status: str, source_id: str, artifact: Mapping[str, Any]) -> None:
    if artifact.get("state") != "VERIFIED": return
    relative = Path(str(artifact.get("relative_path", "")))
    source = root / relative
    if not relative.parts or not relative.is_relative_to(Path(".objects")) or _reparse(source) or not source.is_file():
        raise OwnerReleaseLibraryError("status artwork object is unavailable or unsafe")
    digest = str(artifact.get("sha256", ""))
    if _hash(source.read_bytes()) != digest: raise OwnerReleaseLibraryError("status artwork object SHA mismatch")
    folder = root / status.title(); _safe_directory(root, folder)
    target = folder / f"{source_id}.png"
    if _reparse(target): raise OwnerReleaseLibraryError("status artwork link is a reparse point")
    try: os.link(source, target)
    except FileExistsError:
        if not target.is_file() or _hash(target.read_bytes()) != digest:
            raise OwnerReleaseLibraryError("active status artwork link conflicts with immutable source bytes")

def _history(root: Path, source_id: str) -> list[dict[str, Any]]:
    folder = root / ".history" / source_id
    _verify_existing_path(root, folder)
    events: list[dict[str, Any]] = []
    previous_hash = None
    for sequence, path in enumerate(sorted(folder.glob("*.json")) if folder.exists() else [], 1):
        if _reparse(path): raise OwnerReleaseLibraryError("owner release history event is unsafe")
        raw = path.read_bytes()
        try: event = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc: raise OwnerReleaseLibraryError("owner release history is unreadable") from exc
        if (not isinstance(event, dict) or _json_bytes(event) != raw or event.get("schema") != SCHEMA
                or event.get("source_id") != source_id or event.get("sequence") != sequence
                or event.get("previous_event_sha256") != previous_hash or event.get("status") not in STATUSES):
            raise OwnerReleaseLibraryError("owner release event chain failed integrity validation")
        previous_hash = _hash(raw); events.append(event)
    return events

def _verified_ready_entry(source_id: str, run_id: str | None) -> dict[str, Any]:
    if not run_id: raise OwnerReleaseLibraryError("READY needs a canonical pipeline run and pool receipt")
    from .supply_pipeline.release_pool import release_entries
    for entry in release_entries():
        candidate = entry.get("candidate", {})
        lineage = candidate.get("source_lineage", candidate.get("provenance", {})) if isinstance(candidate, Mapping) else {}
        if (isinstance(lineage, Mapping) and str(lineage.get("source_id", "")) == source_id
                and str(entry.get("pipeline_run_id", "")) == run_id
                and entry.get("pipeline", {}).get("disposition") == "READY"
                and entry.get("pipeline", {}).get("primary", {}).get("state") == "READY"):
            return dict(entry)
    raise OwnerReleaseLibraryError("READY needs exact canonical solver/replay/difficulty/QA and owner-eligibility evidence")

def _object_for_source(root: Path, path_text: str, source_sha: str | None) -> dict[str, Any]:
    if not path_text: return {"state": "NOT_AVAILABLE", "reason": "Original source path is unavailable."}
    path = Path(path_text)
    if _reparse(path) or not path.is_file(): return {"state": "NOT_AVAILABLE", "reason": "Original source is missing or unsafe."}
    raw = path.read_bytes(); digest = _hash(raw)
    if source_sha and digest != source_sha: raise OwnerReleaseLibraryError("source bytes changed after import")
    objects = root / ".objects"
    target = objects / f"{digest}.png"; _create_immutable(target, raw, root)
    if _hash(target.read_bytes()) != digest: raise OwnerReleaseLibraryError("owner release PNG read-back SHA mismatch")
    return {"state": "VERIFIED", "relative_path": target.relative_to(root).as_posix(), "sha256": digest, "byte_length": len(raw)}

def transition(source_id: str, status: str, *, source_sha256: str | None, provider: str,
               original_source_path: str, reason: str = "", batch_id: str | None = None,
               pipeline_run_id: str | None = None, retry_of: str | None = None,
               evidence: Mapping[str, Any] | None = None,
               repository_root: str | Path | None = None) -> dict[str, Any]:
    if not isinstance(source_id, str) or not _ID.fullmatch(source_id): raise OwnerReleaseLibraryError("source identity is malformed")
    if status not in STATUSES: raise OwnerReleaseLibraryError("status is unsupported")
    if source_sha256 is not None and not _SHA.fullmatch(source_sha256): raise OwnerReleaseLibraryError("source SHA is malformed")
    if any(type(v) is not str or len(v) > 2048 for v in (provider, original_source_path, reason)): raise OwnerReleaseLibraryError("provenance exceeds its bound")
    root = owner_art_storage.ensure_owner_art_layout(repository_root)["release_pool"]
    evidence_value = dict(evidence or {})
    if status == "READY":
        entry = _verified_ready_entry(source_id, pipeline_run_id)
        evidence_value.update({"canonical_release_entry_digest": entry.get("entry_digest"), "canonical_pipeline_sha256": entry.get("pipeline_sha256")})
    with _lock(root / ".locks" / f"{source_id}.lock", root):
        events = _history(root, source_id); previous = events[-1] if events else None
        artifact = _object_for_source(root, original_source_path, source_sha256)
        if (artifact.get("state") == "NOT_AVAILABLE" and previous
                and previous.get("source_sha256") == source_sha256
                and isinstance(previous.get("artifact"), Mapping)
                and previous["artifact"].get("state") == "VERIFIED"):
            artifact = dict(previous["artifact"])
        verified_sha = artifact.get("sha256", source_sha256)
        if source_sha256 and verified_sha not in {None, source_sha256}: raise OwnerReleaseLibraryError("source object identity mismatch")
        prior_status = str(previous.get("status", "")) if previous else ""
        allowed = {"": {"PENDING", "FAILED", "REJECTED"}, "PENDING": STATUSES,
                   "FAILED": {"PENDING", "FAILED", "REJECTED"}, "READY": {"READY", "REJECTED"},
                   "REJECTED": {"REJECTED"}}
        if status not in allowed.get(prior_status, set()): raise OwnerReleaseLibraryError(f"invalid status transition {prior_status or 'NEW'} -> {status}")
        fields = {"source_sha256": verified_sha, "provider": provider, "original_source_path": original_source_path,
                  "reason": reason[:512], "batch_id": batch_id, "pipeline_run_id": pipeline_run_id,
                  "retry_of": retry_of, "evidence": evidence_value, "artifact": artifact}
        if previous and status == prior_status and all(previous.get(k) == v for k, v in fields.items()): return {**previous, "idempotent": True}
        expected_previous_sha = _hash(_json_bytes(previous)) if previous else None
        for prior_status_name in STATUSES:
            prior_projection = root / prior_status_name.title() / f"{source_id}.json"
            if not prior_projection.exists():
                continue
            if prior_status is None or prior_status_name != prior_status or _reparse(prior_projection):
                raise OwnerReleaseLibraryError("owner release projection collides with an unverified status record")
            try:
                projection_value = json.loads(prior_projection.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise OwnerReleaseLibraryError("prior owner release status projection is unreadable") from exc
            if (not isinstance(projection_value, dict)
                    or projection_value.get("event_sha256") != expected_previous_sha
                    or _json_bytes({key: value for key, value in projection_value.items() if key != "event_sha256"}) != _json_bytes(previous)):
                raise OwnerReleaseLibraryError("prior owner release status projection does not match immutable history")
        for prior_status_name in STATUSES:
            prior_artwork = root / prior_status_name.title() / f"{source_id}.png"
            if not prior_artwork.exists():
                continue
            if prior_status_name != prior_status or _reparse(prior_artwork) or not prior_artwork.is_file():
                raise OwnerReleaseLibraryError("owner release artwork projection collides with an unverified status record")
            prior_artifact = previous.get("artifact", {}) if previous else {}
            prior_digest = str(prior_artifact.get("sha256", "")) if isinstance(prior_artifact, Mapping) else ""
            if not prior_digest or _hash(prior_artwork.read_bytes()) != prior_digest:
                raise OwnerReleaseLibraryError("prior owner release artwork projection does not match immutable source bytes")
        event = {"schema": SCHEMA, "version": 1, "source_id": source_id, **fields, "status": status,
                 "sequence": len(events) + 1, "created_at": datetime.now(timezone.utc).isoformat(),
                 "previous_event_sha256": expected_previous_sha}
        raw = _json_bytes(event); digest = _hash(raw)
        _create_immutable(root / ".history" / source_id / f"{event['sequence']:06d}-{digest}.json", raw, root)
        projection = {**event, "event_sha256": digest}
        _ensure_status_artwork(root, status, source_id, artifact)
        _replace_projection(root / status.title() / f"{source_id}.json", _json_bytes(projection), root,
                            expected_event_sha256=expected_previous_sha if status == prior_status else None)
        for old in STATUSES - {status}:
            for suffix in (".json", ".png"):
                stale = root / old.title() / f"{source_id}{suffix}"
                if stale.exists():
                    if _reparse(stale): raise OwnerReleaseLibraryError("old status projection is unsafe; immutable history retained")
                    stale.unlink()
        return projection

def record_import_items(batch: Mapping[str, Any], *, repository_root: str | Path | None = None) -> dict[str, Any]:
    batch_id = str(batch.get("batch_id", "")); fallback_provider = str(batch.get("source_provider", "OWNER_UPLOAD")); records = []
    existing = {str(row.get("source_id", "")): row for row in list_records(repository_root=repository_root)["records"]}
    for item in batch.get("items", []):
        if not isinstance(item, Mapping): continue
        disposition = str(item.get("disposition", "REJECTED")); digest = str(item.get("source_sha256") or "") or None
        path = str(item.get("original_source_path", ""))
        source_id = str(item.get("source_id") or (f"owner-source-{digest}" if digest else "missing-source-" + _hash(path.encode())[:32]))
        if source_id in existing:
            # Re-import is a read-only skip; preserve the known status and original provenance.
            records.append({**existing[source_id], "idempotent": True})
            continue
        status = "PENDING" if disposition in {"IMPORTED", "ALREADY_IMPORTED"} else "FAILED" if disposition == "FAILED" else "REJECTED"
        records.append(transition(source_id, status, source_sha256=digest,
            provider=str(item.get("source_provider", fallback_provider)), original_source_path=path,
            reason=str(item.get("error") or ""), batch_id=batch_id,
            evidence={"import_disposition": disposition, "filename_collision": bool(item.get("filename_collision", False)),
                      "collision_with_source_id": item.get("collision_with_source_id")}, repository_root=repository_root))
    return {"state": "RECORDED", "batch_id": batch_id, "records": records}

def record_review_outcome(candidate_id: str, disposition: str, publication: Mapping[str, Any]) -> dict[str, Any] | None:
    """Mirror an explicit owner rejection or an exact accepted READY receipt."""
    from . import studio_extensions
    candidate = next((item for item in studio_extensions.list_candidates() if item.get("candidate_id") == candidate_id), None)
    if candidate is None: return None
    lineage = candidate.get("source_lineage", {})
    source_id = str(lineage.get("source_id", "")) if isinstance(lineage, Mapping) else ""
    if not source_id: return None
    source = studio_extensions.verify_owner_source(source_id)
    path = str(source.get("source_path", ""))
    receipt = publication.get("publication", {})
    receipt = receipt if isinstance(receipt, Mapping) else {}
    run_id = str(receipt.get("pipeline_run_id", "")) or None
    if disposition == "REJECT":
        return transition(source_id, "REJECTED", source_sha256=str(source.get("source_sha256", "")),
            provider="OWNER_UPLOAD", original_source_path=path, pipeline_run_id=run_id,
            reason="Owner explicitly rejected this candidate.", evidence={"owner_review_id": publication.get("review_id"), "owner_review": "REJECT"})
    if disposition == "ACCEPT" and receipt.get("readback_verified") is True:
        return transition(source_id, "READY", source_sha256=str(source.get("source_sha256", "")),
            provider="OWNER_UPLOAD", original_source_path=path, pipeline_run_id=run_id,
            evidence={"owner_review_id": publication.get("review_id"), "owner_review": "ACCEPT"})
    return None

def list_records(status: str | None = None, *, repository_root: str | Path | None = None) -> dict[str, Any]:
    if status is not None and status not in STATUSES: raise OwnerReleaseLibraryError("status filter is unsupported")
    root = _root(repository_root); states = {status} if status else STATUSES; rows = []
    if not root.exists():
        return {"schema": "scrubbots-owner-release-library-view/v1", "state": "READY", "read_only": True,
                "counts": {key: 0 for key in sorted(STATUSES)}, "records": []}
    for state in sorted(states):
        folder = root / state.title()
        _verify_existing_path(root, folder)
        for path in sorted(folder.glob("*.json"), key=lambda p: p.name.casefold()) if folder.exists() else []:
            if _reparse(path): raise OwnerReleaseLibraryError("status projection is unsafe")
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict) or value.get("status") != state or path.stem != value.get("source_id"):
                raise OwnerReleaseLibraryError("status projection identity is invalid")
            event_digest = str(value.pop("event_sha256", ""))
            if _hash(_json_bytes(value)) != event_digest:
                raise OwnerReleaseLibraryError("status projection event digest is invalid")
            history = _history(root, str(value["source_id"]))
            if not history or _json_bytes(history[-1]) != _json_bytes(value):
                raise OwnerReleaseLibraryError("status projection does not match immutable history")
            value["event_sha256"] = event_digest
            rows.append(value)
    rows.sort(key=lambda row: (str(row.get("created_at", "")), str(row.get("source_id", ""))), reverse=True)
    counts = {key: sum(row.get("status") == key for row in rows) for key in sorted(STATUSES)}
    return {"schema": "scrubbots-owner-release-library-view/v1", "state": "READY", "read_only": True, "counts": counts, "records": rows}

def transition_pipeline(source_id: str, pipeline: Mapping[str, Any]) -> dict[str, Any]:
    from . import studio_extensions
    source = studio_extensions.verify_owner_source(source_id)
    run_id = str(pipeline.get("run_id", "")) or None
    outcome = str(pipeline.get("disposition", pipeline.get("state", "PENDING"))).upper()
    status = "READY" if outcome == "READY" else "FAILED" if outcome in {"ERROR", "FAILED", "BLOCKED", "INTERRUPTED"} or outcome.startswith("PARTIAL") else "PENDING"
    reason = "" if status == "READY" else str(pipeline.get("reason", pipeline.get("stop_reason", outcome)))
    evidence: dict[str, Any] = {"pipeline_run_id": run_id, "solution": {"state": "NOT_AVAILABLE"}, "plan": {"state": "NOT_AVAILABLE"}}
    primary = pipeline.get("primary", {}); files = primary.get("files", {}) if isinstance(primary, Mapping) else {}
    if isinstance(files, Mapping):
        for key, label in (("level", "solution"), ("supply_plan", "plan")):
            text = str(files.get(key, "")); path = Path(text) if text else None
            if path and path.is_file() and not _reparse(path): evidence[label] = {"state": "VERIFIED", "path": text, "sha256": _hash(path.read_bytes())}
    current = next((row for row in list_records()["records"] if row.get("source_id") == source_id), None)
    args = {"source_sha256": str(source.get("source_sha256", "")), "provider": str(current.get("provider", "OWNER_UPLOAD")) if current else "OWNER_UPLOAD",
            "original_source_path": str(current.get("original_source_path", source.get("source_path", ""))) if current else str(source.get("source_path", "")), "pipeline_run_id": run_id,
            "reason": reason, "evidence": evidence}
    if current and current.get("status") == "REJECTED":
        raise OwnerReleaseLibraryError("explicitly rejected artwork cannot be sent to the solver")
    if current and current.get("status") == "FAILED":
        retry_id = str(current.get("event_sha256", ""))
        transition(source_id, "PENDING", **{**args, "reason": "Explicit Retry Failed attempt started.",
                    "retry_of": retry_id or None, "evidence": {**evidence, "explicit_retry": True}})
    if status == "READY":
        try: return transition(source_id, "READY", **args)
        except OwnerReleaseLibraryError as exc:
            return transition(source_id, "PENDING", **{**args, "reason": f"READY deferred until canonical Release Pool eligibility verifies: {str(exc)[:380]}"})
    return transition(source_id, status, **args)

def assert_solver_allowed(source_ids: list[str] | tuple[str, ...], *, repository_root: str | Path | None = None) -> None:
    """Reject explicit owner-rejected source identities before solver dispatch."""
    rejected = {str(row.get("source_id")) for row in list_records("REJECTED", repository_root=repository_root)["records"]}
    if any(str(source_id) in rejected for source_id in source_ids):
        raise OwnerReleaseLibraryError("owner-rejected artwork is excluded from solver retry")

def record_batch_outcomes(job: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Record terminal solver outcomes already verified by the canonical PNG batch engine."""
    results = []
    for item in job.get("items", []):
        if not isinstance(item, Mapping) or item.get("status") not in {"READY", "FAILED"}:
            continue
        source_id = str(item.get("source_id", ""))
        run_id = str(item.get("run_id", "")) or None
        pipeline = {"run_id": run_id, "disposition": "READY" if item.get("status") == "READY" else "FAILED",
                    "primary": {"state": "READY" if item.get("status") == "READY" else "FAILED",
                                "files": item.get("artifact_refs", {})},
                    "reason": str(item.get("reason", "")), "candidate_id": item.get("candidate_id")}
        results.append(transition_pipeline(source_id, pipeline))
    return results

__all__ = ["OwnerReleaseLibraryError", "assert_solver_allowed", "list_records", "record_batch_outcomes", "record_import_items", "transition", "transition_pipeline"]
