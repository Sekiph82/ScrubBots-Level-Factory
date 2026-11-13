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
_ATLAS_TRANSACTION_SCHEMA = "scrubbots-pixellab-atlas-transaction/v1"
_RELEASE_POOL_ENTRY_SCHEMA = "scrubbots-release-pool-entry/v1"
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

def _is_release_pool_entry_projection(path: Path, state: str, value: object) -> bool:
    """Recognize an intact canonical candidate entry sharing the Ready folder.

    Release Pool candidate entries and owner status projections share the
    canonical status directories, but have separate schemas and identity
    contracts. Only a READY candidate entry with a matching filename and
    content digest is excluded from the owner-status view.
    """
    if not isinstance(value, dict) or value.get("schema") != _RELEASE_POOL_ENTRY_SCHEMA:
        return False
    candidate_id = value.get("candidate_id")
    pipeline_run_id = value.get("pipeline_run_id")
    review_id = value.get("review_id")
    suffix = review_id if isinstance(review_id, str) and review_id else "ready"
    expected_name = f"{candidate_id}-{pipeline_run_id}-{suffix}.json"
    if (state != "READY"
            or not isinstance(candidate_id, str) or not _ID.fullmatch(candidate_id)
            or not isinstance(pipeline_run_id, str) or not _ID.fullmatch(pipeline_run_id)
            or (suffix != "ready" and not _ID.fullmatch(suffix))
            or path.name != expected_name):
        raise OwnerReleaseLibraryError("Release Pool entry identity is invalid")
    entry_digest = value.get("entry_digest")
    if not isinstance(entry_digest, str) or not _SHA.fullmatch(entry_digest):
        raise OwnerReleaseLibraryError("Release Pool entry digest is invalid")
    payload = dict(value)
    payload.pop("entry_digest", None)
    actual_digest = hashlib.sha256(json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if actual_digest != entry_digest:
        raise OwnerReleaseLibraryError("Release Pool entry digest is invalid")
    return True

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

def _status_artwork_name(source_id: str, original_source_path: str) -> str:
    """Keep the owner's readable PNG basename across status-folder moves."""
    name = Path(original_source_path).name
    if (not name or name in {".", ".."} or Path(name).name != name
            or Path(name).suffix.lower() != ".png"):
        raise OwnerReleaseLibraryError("status artwork source filename is unsafe")
    return name


def _ensure_status_artwork(root: Path, status: str, source_id: str, artifact: Mapping[str, Any],
                           original_source_path: str) -> Path | None:
    if artifact.get("state") != "VERIFIED": return
    relative = Path(str(artifact.get("relative_path", "")))
    source = root / relative
    if not relative.parts or not relative.is_relative_to(Path(".objects")) or _reparse(source) or not source.is_file():
        raise OwnerReleaseLibraryError("status artwork object is unavailable or unsafe")
    digest = str(artifact.get("sha256", ""))
    if _hash(source.read_bytes()) != digest: raise OwnerReleaseLibraryError("status artwork object SHA mismatch")
    folder = root / status.title(); _safe_directory(root, folder)
    target = _status_artwork_target(folder, source_id, original_source_path, digest)
    if _reparse(target): raise OwnerReleaseLibraryError("status artwork link is a reparse point")
    try: os.link(source, target)
    except FileExistsError:
        if not target.is_file() or _hash(target.read_bytes()) != digest:
            raise OwnerReleaseLibraryError("readable status artwork name conflicts with different source bytes")
    return target

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


def _status_artwork_candidates(root: Path, status: str, source_id: str,
                               original_source_path: str) -> tuple[Path, ...]:
    folder = root / status.title()
    legacy = folder / f"{source_id}.png"
    try:
        readable = folder / _status_artwork_name(source_id, original_source_path)
    except OwnerReleaseLibraryError:
        # Older history can lack a safe original basename. Such records may
        # still be recovered by their source-ID projection, but new verified
        # artwork writes remain strict in _ensure_status_artwork().
        return (legacy,)
    distinct = folder / _distinct_artwork_name(source_id, readable.name)
    return (readable,) if readable == legacy else (readable, distinct, legacy)


def _distinct_artwork_name(source_id: str, readable_name: str) -> str:
    """Readable name for a source whose basename another source already holds."""
    stem = Path(readable_name).stem
    return f"{stem}--{source_id[-12:]}.png"


def _status_artwork_target(folder: Path, source_id: str, original_source_path: str, digest: str) -> Path:
    readable = folder / _status_artwork_name(source_id, original_source_path)
    if _belongs_to_other_source(readable, source_id, original_source_path, {digest}):
        return folder / _distinct_artwork_name(source_id, readable.name)
    return readable


def _belongs_to_other_source(path: Path, source_id: str, original_source_path: str, digests: set[str]) -> bool:
    """True for an existing shared basename file holding another source's bytes.

    Source identities are content hashes, so different bytes under the shared
    readable basename belong to a different source: never claim, verify or
    unlink them as this source's artwork. Source-ID-bound names are never shared.
    """
    try:
        shared = path.name == _status_artwork_name(source_id, original_source_path)
    except OwnerReleaseLibraryError:
        return False
    if not shared or path.name == f"{source_id}.png" or not path.is_file() or _reparse(path):
        return False
    return _hash(path.read_bytes()) not in digests


def _recover_latest_status_projection(root: Path, source_id: str, events: list[dict[str, Any]]) -> bool:
    """Finish an interrupted status projection using its immutable event chain.

    The history append is the commit authority. This repairs only projections
    that are byte-for-byte represented in that chain and refuses unknown files.
    """
    if not events:
        return False
    latest = events[-1]
    latest_digest = _hash(_json_bytes(latest))
    known_events = {_hash(_json_bytes(event)): event for event in events}
    own_digests = {str(event["artifact"].get("sha256", "")) for event in events
                   if isinstance(event.get("artifact"), Mapping) and event["artifact"].get("state") == "VERIFIED"}
    projection_digests: dict[str, str] = {}
    artwork_digests: dict[str, str] = {}
    changed = False

    for state in STATUSES:
        projection_path = root / state.title() / f"{source_id}.json"
        if projection_path.exists():
            if _reparse(projection_path):
                raise OwnerReleaseLibraryError("owner release status projection is a reparse point")
            try:
                value = json.loads(projection_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise OwnerReleaseLibraryError("owner release status projection is unreadable during recovery") from exc
            if not isinstance(value, dict) or value.get("schema") != SCHEMA or value.get("source_id") != source_id:
                raise OwnerReleaseLibraryError("owner release projection collides with an unverified status record")
            digest = str(value.pop("event_sha256", ""))
            if (digest not in known_events or value.get("status") != state
                    or _hash(_json_bytes(value)) != digest
                    or _json_bytes(value) != _json_bytes(known_events[digest])):
                raise OwnerReleaseLibraryError("owner release status projection is not represented in immutable history")
            projection_digests[state] = digest

        event_for_state = next((event for event in reversed(events) if event.get("status") == state), None)
        if event_for_state is not None:
            for artwork_path in _status_artwork_candidates(
                    root, state, source_id, str(event_for_state.get("original_source_path", ""))):
                if not artwork_path.exists() or _belongs_to_other_source(
                        artwork_path, source_id, str(event_for_state.get("original_source_path", "")), own_digests):
                    continue
                if _reparse(artwork_path) or not artwork_path.is_file():
                    raise OwnerReleaseLibraryError("owner release artwork projection is unsafe during recovery")
                actual = _hash(artwork_path.read_bytes())
                matching_history = any(
                    event.get("status") == state
                    and isinstance(event.get("artifact"), Mapping)
                    and event["artifact"].get("state") == "VERIFIED"
                    and event["artifact"].get("sha256") == actual
                    for event in events
                )
                if not matching_history:
                    raise OwnerReleaseLibraryError("owner release artwork projection is not represented in immutable history")
                artwork_digests[state] = actual

    desired_state = str(latest.get("status", ""))
    if desired_state not in STATUSES:
        raise OwnerReleaseLibraryError("latest owner release history status is unsupported")
    artifact = latest.get("artifact", {})
    if isinstance(artifact, Mapping) and artifact.get("state") == "VERIFIED":
        expected_artwork_path = _status_artwork_target(
            root / desired_state.title(), source_id, str(latest.get("original_source_path", "")),
            str(artifact.get("sha256", "")))
        legacy_artwork_path = root / desired_state.title() / f"{source_id}.png"
        changed = changed or not expected_artwork_path.exists() or legacy_artwork_path.exists()
        _ensure_status_artwork(root, desired_state, source_id, artifact,
                               str(latest.get("original_source_path", "")))
        if legacy_artwork_path.exists() and legacy_artwork_path != expected_artwork_path:
            if _reparse(legacy_artwork_path) or _hash(legacy_artwork_path.read_bytes()) != str(artifact.get("sha256", "")):
                raise OwnerReleaseLibraryError("legacy status artwork name is not bound to the latest immutable source")
            legacy_artwork_path.unlink()
    elif desired_state in artwork_digests:
        raise OwnerReleaseLibraryError("latest owner release status has artwork without a verified immutable object")

    desired_projection = root / desired_state.title() / f"{source_id}.json"
    current_digest = projection_digests.get(desired_state)
    if current_digest != latest_digest:
        changed = True
        _replace_projection(
            desired_projection, _json_bytes({**latest, "event_sha256": latest_digest}), root,
            expected_event_sha256=current_digest,
        )

    for state in STATUSES - {desired_state}:
        for suffix in (".json", ".png"):
            stale_paths = [root / state.title() / f"{source_id}{suffix}"]
            state_source_path = ""
            if suffix == ".png":
                event_for_state = next((event for event in reversed(events) if event.get("status") == state), None)
                if event_for_state is not None:
                    state_source_path = str(event_for_state.get("original_source_path", ""))
                    stale_paths.extend(_status_artwork_candidates(root, state, source_id, state_source_path))
            for stale in set(stale_paths):
                if stale.exists() and not _belongs_to_other_source(stale, source_id, state_source_path, own_digests):
                    if _reparse(stale):
                        raise OwnerReleaseLibraryError("stale owner status projection is unsafe during recovery")
                    stale.unlink()
                    changed = True
    return changed


def reconcile_status_projections(*, repository_root: str | Path | None = None) -> dict[str, Any]:
    """Repair interrupted current-status files from their verified immutable histories."""
    root = _root(repository_root)
    if not root.exists():
        return {"state": "RECONCILED", "repaired": 0, "errors": []}
    history_root = root / ".history"
    _verify_existing_path(root, history_root)
    repaired: list[str] = []
    checked = 0
    errors: list[dict[str, str]] = []
    for directory in sorted((path for path in history_root.iterdir() if path.is_dir()), key=lambda path: path.name):
        source_id = directory.name
        try:
            with _lock(root / ".locks" / f"{source_id}.lock", root):
                events = _history(root, source_id)
                checked += 1
                if _recover_latest_status_projection(root, source_id, events):
                    repaired.append(source_id)
        except (OSError, ValueError) as exc:
            errors.append({"source_id": source_id, "reason": str(exc)[:512]})
    return {"state": "RECONCILED" if not errors else "PARTIAL", "checked": checked, "repaired": len(repaired),
            "repaired_source_ids": repaired, "errors": errors}

def _verified_ready_entry(source_id: str, run_id: str | None, candidate_id: str | None = None) -> dict[str, Any]:
    if not run_id: raise OwnerReleaseLibraryError("READY needs a canonical pipeline run and pool receipt")
    from .supply_pipeline.release_pool import release_entries
    # Restrict the read to the candidate bound by this solver result. A single
    # unrelated/corrupt Ready receipt must not hide every other verified level.
    entries = release_entries(candidate_id_filter=candidate_id) if candidate_id else release_entries()
    for entry in entries:
        candidate = entry.get("candidate", {})
        lineage = candidate.get("source_lineage", candidate.get("provenance", {})) if isinstance(candidate, Mapping) else {}
        if (isinstance(lineage, Mapping) and str(lineage.get("source_id", "")) == source_id
                and (not candidate_id or str(entry.get("candidate_id", "")) == candidate_id)
                and str(entry.get("pipeline_run_id", "")) == run_id
                and entry.get("pipeline", {}).get("disposition") == "READY"
                and entry.get("pipeline", {}).get("primary", {}).get("state") == "READY"):
            return dict(entry)
    raise OwnerReleaseLibraryError("READY needs exact canonical solver/replay/difficulty/QA and owner-eligibility evidence")


def _assert_ready_entry_binding(entry: Mapping[str, Any], source_id: str, run_id: str | None) -> dict[str, Any]:
    """Recheck a receipt returned by the full canonical Release Pool reader."""
    candidate = entry.get("candidate", {})
    lineage = candidate.get("source_lineage", candidate.get("provenance", {})) if isinstance(candidate, Mapping) else {}
    if (entry.get("schema") != _RELEASE_POOL_ENTRY_SCHEMA
            or not run_id or str(entry.get("pipeline_run_id", "")) != run_id
            or str(entry.get("candidate_id", "")) == ""
            or entry.get("pipeline", {}).get("disposition") != "READY"
            or entry.get("pipeline", {}).get("primary", {}).get("state") != "READY"
            or not isinstance(lineage, Mapping) or str(lineage.get("source_id", "")) != source_id):
        raise OwnerReleaseLibraryError("prevalidated Release Pool receipt does not match the exact READY source/run")
    expected = entry.get("entry_digest")
    payload = dict(entry)
    payload.pop("entry_digest", None)
    actual = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if not isinstance(expected, str) or not _SHA.fullmatch(expected) or expected != actual:
        raise OwnerReleaseLibraryError("prevalidated Release Pool receipt digest changed")
    return dict(entry)

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
               _verified_entry: Mapping[str, Any] | None = None,
               repository_root: str | Path | None = None) -> dict[str, Any]:
    if not isinstance(source_id, str) or not _ID.fullmatch(source_id): raise OwnerReleaseLibraryError("source identity is malformed")
    if status not in STATUSES: raise OwnerReleaseLibraryError("status is unsupported")
    if source_sha256 is not None and not _SHA.fullmatch(source_sha256): raise OwnerReleaseLibraryError("source SHA is malformed")
    if any(type(v) is not str or len(v) > 2048 for v in (provider, original_source_path, reason)): raise OwnerReleaseLibraryError("provenance exceeds its bound")
    root = owner_art_storage.ensure_owner_art_layout(repository_root)["release_pool"]
    evidence_value = dict(evidence or {})
    if status == "READY":
        candidate_id = str(evidence_value.get("candidate_id", "")) or None
        if _verified_entry is not None:
            entry = _assert_ready_entry_binding(_verified_entry, source_id, pipeline_run_id)
        elif candidate_id:
            entry = _verified_ready_entry(source_id, pipeline_run_id, candidate_id)
        else:
            # Keep the historical two-argument call shape for integrations and
            # test adapters that wrap the canonical verifier.
            entry = _verified_ready_entry(source_id, pipeline_run_id)
        evidence_value.update({"canonical_release_entry_digest": entry.get("entry_digest"), "canonical_pipeline_sha256": entry.get("pipeline_sha256")})
    with _lock(root / ".locks" / f"{source_id}.lock", root):
        events = _history(root, source_id)
        _recover_latest_status_projection(root, source_id, events)
        events = _history(root, source_id); previous = events[-1] if events else None
        artifact = _object_for_source(root, original_source_path, source_sha256)
        if (artifact.get("state") == "NOT_AVAILABLE" and previous
                and previous.get("source_sha256") == source_sha256
                and isinstance(previous.get("artifact"), Mapping)
                and previous["artifact"].get("state") == "VERIFIED"):
            artifact = dict(previous["artifact"])
        verified_sha = artifact.get("sha256", source_sha256)
        own_digests = {str(value) for value in (verified_sha, artifact.get("sha256")) if value}
        if source_sha256 and verified_sha not in {None, source_sha256}: raise OwnerReleaseLibraryError("source object identity mismatch")
        prior_status = str(previous.get("status", "")) if previous else ""
        allowed = {"": {"PENDING", "FAILED", "REJECTED"}, "PENDING": STATUSES,
                   "FAILED": {"PENDING", "FAILED", "REJECTED"}, "READY": {"READY", "REJECTED"},
                   "REJECTED": {"PENDING", "REJECTED"}}
        if status not in allowed.get(prior_status, set()): raise OwnerReleaseLibraryError(f"invalid status transition {prior_status or 'NEW'} -> {status}")
        if prior_status in {"FAILED", "REJECTED"} and status == "PENDING":
            prior_digest = _hash(_json_bytes(previous)) if previous else None
            if (retry_of != prior_digest or evidence_value.get("explicit_retry") is not True):
                raise OwnerReleaseLibraryError("FAILED/REJECTED -> PENDING requires an explicit retry bound to the prior event SHA-256")
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
        prior_path = str(previous.get("original_source_path", "")) if previous else original_source_path
        for prior_status_name in STATUSES:
            for prior_artwork in _status_artwork_candidates(root, prior_status_name, source_id, prior_path):
                if not prior_artwork.exists() or _belongs_to_other_source(prior_artwork, source_id, prior_path, own_digests):
                    continue
                if prior_status_name != prior_status or _reparse(prior_artwork) or not prior_artwork.is_file():
                    raise OwnerReleaseLibraryError("owner release artwork projection collides with an unverified status record")
                prior_artifact = previous.get("artifact", {}) if previous else {}
                prior_digest = str(prior_artifact.get("sha256", "")) if isinstance(prior_artifact, Mapping) else ""
                if not prior_digest or _hash(prior_artwork.read_bytes()) != prior_digest:
                    raise OwnerReleaseLibraryError("prior owner release artwork projection does not match immutable source bytes")
        if artifact.get("state") == "VERIFIED":
            target = _status_artwork_target(root / status.title(), source_id, original_source_path,
                                            str(artifact.get("sha256", "")))
            if _reparse(target):
                raise OwnerReleaseLibraryError("status artwork target is a reparse point")
            if target.exists() and (not target.is_file() or _hash(target.read_bytes()) != str(artifact.get("sha256", ""))):
                raise OwnerReleaseLibraryError("readable status artwork name conflicts with different source bytes")
        event = {"schema": SCHEMA, "version": 1, "source_id": source_id, **fields, "status": status,
                 "sequence": len(events) + 1, "created_at": datetime.now(timezone.utc).isoformat(),
                 "previous_event_sha256": expected_previous_sha}
        raw = _json_bytes(event); digest = _hash(raw)
        _create_immutable(root / ".history" / source_id / f"{event['sequence']:06d}-{digest}.json", raw, root)
        projection = {**event, "event_sha256": digest}
        current_artwork = _ensure_status_artwork(root, status, source_id, artifact, original_source_path)
        _replace_projection(root / status.title() / f"{source_id}.json", _json_bytes(projection), root,
                            expected_event_sha256=expected_previous_sha if status == prior_status else None)
        for old in STATUSES - {status}:
            stale_paths = [root / old.title() / f"{source_id}.json"]
            previous_source_path = str(previous.get("original_source_path", original_source_path)) if previous else ""
            if previous is not None:
                stale_paths.extend(_status_artwork_candidates(root, old, source_id, previous_source_path))
            for stale in set(stale_paths):
                if stale.exists() and not _belongs_to_other_source(stale, source_id, previous_source_path, own_digests):
                    if _reparse(stale): raise OwnerReleaseLibraryError("old status projection is unsafe; immutable history retained")
                    stale.unlink()
        if current_artwork is not None and previous is not None:
            previous_paths = _status_artwork_candidates(
                root, prior_status, source_id,
                str(previous.get("original_source_path", original_source_path)))
            for stale in previous_paths:
                if stale != current_artwork and stale.exists() and not _belongs_to_other_source(
                        stale, source_id, str(previous.get("original_source_path", original_source_path)), own_digests):
                    if _reparse(stale) or _hash(stale.read_bytes()) != str(artifact.get("sha256", "")):
                        raise OwnerReleaseLibraryError("legacy current-status artwork does not match immutable source bytes")
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
            # PixelLab's durable atlas transaction manifests also live directly
            # in Release Pool/Pending. They are not source-status projections.
            # Ignore only that explicitly recognized artifact schema; malformed
            # owner-library projections remain fail-closed below.
            if isinstance(value, dict) and value.get("schema") == _ATLAS_TRANSACTION_SCHEMA:
                continue
            if _is_release_pool_entry_projection(path, state, value):
                continue
            if (not isinstance(value, dict) or value.get("schema") != SCHEMA
                    or value.get("status") != state or path.stem != value.get("source_id")):
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


def reconcile_ready_projections(*, repository_root: str | Path | None = None) -> dict[str, Any]:
    """Repair intake-only Pending rows from one canonical Ready receipt snapshot.

    This is deliberately conservative: it promotes only the first, import-time
    PENDING event. Explicit retries, active attempts, and later failures or
    rejections remain the latest owner action and are never overwritten.
    """
    from . import studio_extensions
    from .supply_pipeline.release_pool import release_entries

    entries = release_entries()
    entry_by_source: dict[str, dict[str, Any]] = {}
    for entry in entries:
        candidate = entry.get("candidate", {})
        lineage = candidate.get("source_lineage", candidate.get("provenance", {})) if isinstance(candidate, Mapping) else {}
        source_id = str(lineage.get("source_id", "")) if isinstance(lineage, Mapping) else ""
        if source_id:
            existing = entry_by_source.get(source_id)
            if existing is None or str(entry.get("pipeline_run_id", "")) > str(existing.get("pipeline_run_id", "")):
                entry_by_source[source_id] = entry

    current = {str(row.get("source_id", "")): row
               for row in list_records(repository_root=repository_root).get("records", [])
               if isinstance(row, Mapping)}
    promoted: list[str] = []
    skipped = 0
    for source_id, entry in entry_by_source.items():
        row = current.get(source_id)
        row_evidence = row.get("evidence", {}) if isinstance(row, Mapping) else {}
        row_evidence = row_evidence if isinstance(row_evidence, Mapping) else {}
        if (row is None or row.get("status") != "PENDING" or row.get("sequence") != 1
                or row.get("pipeline_run_id") or row_evidence.get("batch_attempt_started")):
            skipped += 1
            continue
        candidate = entry.get("candidate", {})
        lineage = candidate.get("source_lineage", candidate.get("provenance", {})) if isinstance(candidate, Mapping) else {}
        source_sha = str(lineage.get("source_sha256", lineage.get("source_sha", ""))) if isinstance(lineage, Mapping) else ""
        if source_sha != str(row.get("source_sha256", "")):
            skipped += 1
            continue
        try:
            source = studio_extensions.verify_owner_source(source_id)
            if str(source.get("source_sha256", "")) != source_sha:
                skipped += 1
                continue
            event = transition(
                source_id, "READY", source_sha256=source_sha,
                provider=str(row.get("provider", "PIXELLAB")),
                original_source_path=str(row.get("original_source_path", source.get("source_path", ""))),
                pipeline_run_id=str(entry.get("pipeline_run_id", "")),
                evidence={"candidate_id": str(entry.get("candidate_id", "")),
                          "startup_ready_receipt_reconciliation": True},
                _verified_entry=entry, repository_root=repository_root,
            )
            if event.get("status") == "READY":
                promoted.append(source_id)
            else:
                skipped += 1
        except (OSError, ValueError, OwnerReleaseLibraryError):
            skipped += 1
    return {"state": "RECONCILED", "canonical_ready_receipts": len(entries),
            "owner_rows_promoted": len(promoted), "promoted_source_ids": promoted,
            "skipped_newer_or_unmatched_rows": skipped}


def reconcile_terminal_batch_projections(*, repository_root: str | Path | None = None) -> dict[str, Any]:
    """Restore missing FAILED/REJECTED projections from sealed batch outcomes.

    Older Studio builds could persist a terminal PNG batch item without also
    recording its Release Pool status event. On startup, use only a digest-
    verified batch job whose immutable import snapshot, source PNG SHA, and
    source-record SHA still match. READY is intentionally handled by
    ``reconcile_ready_projections`` because it additionally requires a
    canonical Release Pool receipt.

    Existing retries, attempts, and terminal owner decisions are never
    overwritten. Only intake-time PENDING events (sequence 1, with no solver
    attempt) can be restored by this compatibility path.
    """
    from . import studio_extensions
    from .png_batch import _job_lineage_matches_snapshot, _read_job, _root as batch_root

    root = _root(repository_root)
    jobs_root = batch_root() / "jobs"
    if not jobs_root.is_dir():
        return {"state": "RECONCILED", "checked_jobs": 0, "repaired": 0,
                "skipped": 0, "errors": []}

    current = {str(row.get("source_id", "")): row
               for row in list_records(repository_root=repository_root).get("records", [])
               if isinstance(row, Mapping)}
    latest_by_source: dict[str, tuple[str, str, str, dict[str, Any], dict[str, Any]]] = {}
    checked_jobs = 0
    errors: list[dict[str, str]] = []
    for path in sorted(jobs_root.glob("png-batch-*.json"), key=lambda item: item.name):
        try:
            job = _read_job(path.stem)
            checked_jobs += 1
            batch_id = str(job.get("import_batch_id", ""))
            if not batch_id:
                continue
            batch = studio_extensions.batch_load(batch_id)["batch"]
            if not _job_lineage_matches_snapshot(job, batch):
                continue
            # Job creation establishes which batch/retry supersedes older work;
            # updated_at alone would let an old batch that resumed later hide a
            # newer explicitly created job.
            job_stamp = str(job.get("created_at", ""))
            for item in job.get("items", []):
                if (not isinstance(item, Mapping)
                        or item.get("status") not in {"QUEUED", "RUNNING", "VERIFYING_EXISTING", "READY", "FAILED", "REJECTED"}):
                    continue
                source_id = str(item.get("source_id", ""))
                source_sha = str(item.get("source_sha256", ""))
                record_sha = str(item.get("source_record_sha256", ""))
                if (not _ID.fullmatch(source_id) or not _SHA.fullmatch(source_sha)
                        or not _SHA.fullmatch(record_sha) or source_id != "owner-upload-" + source_sha):
                    continue
                row = current.get(source_id)
                evidence = row.get("evidence", {}) if isinstance(row, Mapping) else {}
                evidence = evidence if isinstance(evidence, Mapping) else {}
                if (row is None or row.get("status") != "PENDING" or row.get("sequence") != 1
                        or row.get("pipeline_run_id") or evidence.get("batch_attempt_started")):
                    continue
                source = studio_extensions.verify_owner_source(
                    source_id, source_directory=job.get("settings", {}).get("source_directory"),
                )
                record_path, source_path = studio_extensions._source_record_paths(
                    source_id, job.get("settings", {}).get("source_directory"),
                )
                if (str(source.get("source_sha256", "")) != source_sha
                        or _hash(source_path.read_bytes()) != source_sha
                        or _hash(record_path.read_bytes()) != record_sha
                        or str(row.get("source_sha256", "")) != source_sha):
                    continue
                stamp = str(item.get("finished_at", "")) or job_stamp
                previous = latest_by_source.get(source_id)
                if (previous is None or
                        (job_stamp, stamp, str(job.get("job_id", ""))) > (previous[1], previous[0], previous[2])):
                    latest_by_source[source_id] = (
                        stamp, job_stamp, str(job.get("job_id", "")),
                        dict(job), dict(item),
                    )
        except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
            errors.append({"job_id": path.stem, "reason": str(exc)[:320]})

    repaired: list[str] = []
    skipped = 0
    for source_id, (_stamp, _job_stamp, _job_id, job, item) in latest_by_source.items():
        if item.get("status") not in {"FAILED", "REJECTED"}:
            continue
        row = current.get(source_id)
        if row is None or row.get("status") != "PENDING" or row.get("sequence") != 1:
            skipped += 1
            continue
        try:
            status = str(item.get("status"))
            event = transition(
                source_id, status, source_sha256=str(item.get("source_sha256", "")),
                provider=str(row.get("provider", "PIXELLAB")),
                original_source_path=str(row.get("original_source_path", "")),
                reason=str(item.get("reason", "")) or "Recovered from a SHA-verified durable PNG batch outcome.",
                batch_id=str(job.get("import_batch_id", "")) or None,
                pipeline_run_id=str(item.get("run_id", "")) or None,
                evidence={
                    "startup_terminal_batch_reconciliation": True,
                    "reconciled_job_id": str(job.get("job_id", "")),
                    "reconciled_job_state_digest": str(job.get("state_digest", "")),
                    "reconciled_item_index": int(item.get("index", -1)),
                    "source_record_sha256": str(item.get("source_record_sha256", "")),
                },
                repository_root=repository_root,
            )
            if event.get("status") == status:
                repaired.append(source_id)
            else:
                skipped += 1
        except (OSError, ValueError, TypeError, KeyError) as exc:
            errors.append({"source_id": source_id, "reason": str(exc)[:320]})
    terminal_sources = sum(item.get("status") in {"FAILED", "REJECTED"}
                           for _stamp, _job_stamp, _job_id, _job, item in latest_by_source.values())
    pending_preserved = sum(item.get("status") not in {"FAILED", "REJECTED", "READY"}
                            for _stamp, _job_stamp, _job_id, _job, item in latest_by_source.values())
    return {"state": "RECONCILED" if not errors else "PARTIAL", "checked_jobs": checked_jobs,
            "terminal_sources": terminal_sources, "pending_preserved": pending_preserved, "repaired": len(repaired),
            "repaired_source_ids": repaired, "skipped": skipped, "errors": errors}

def transition_pipeline(source_id: str, pipeline: Mapping[str, Any], *, repository_root: str | Path | None = None) -> dict[str, Any]:
    from . import studio_extensions
    source = studio_extensions.verify_owner_source(source_id)
    run_id = str(pipeline.get("run_id", "")) or None
    outcome = str(pipeline.get("disposition", pipeline.get("state", "PENDING"))).upper()
    status = (
        "READY" if outcome == "READY" else
        "REJECTED" if outcome == "REJECTED" else
        "PENDING" if outcome in {"PENDING", "QUEUED", "INTERRUPTED", "INCONCLUSIVE"} else
        "FAILED" if outcome in {"ERROR", "FAILED", "BLOCKED"} or outcome.startswith("PARTIAL") else
        "PENDING"
    )
    reason = "" if status == "READY" else str(pipeline.get("reason", pipeline.get("stop_reason", outcome)))
    evidence: dict[str, Any] = {"pipeline_run_id": run_id, "solution": {"state": "NOT_AVAILABLE"}, "plan": {"state": "NOT_AVAILABLE"}}
    primary = pipeline.get("primary", {}); files = primary.get("files", {}) if isinstance(primary, Mapping) else {}
    if isinstance(files, Mapping):
        for key, label in (("level", "solution"), ("supply_plan", "plan")):
            text = str(files.get(key, "")); path = Path(text) if text else None
            if path and path.is_file() and not _reparse(path): evidence[label] = {"state": "VERIFIED", "path": text, "sha256": _hash(path.read_bytes())}
    current = next((row for row in list_records(repository_root=repository_root)["records"] if row.get("source_id") == source_id), None)
    args = {"source_sha256": str(source.get("source_sha256", "")), "provider": str(current.get("provider", "OWNER_UPLOAD")) if current else "OWNER_UPLOAD",
            "original_source_path": str(current.get("original_source_path", source.get("source_path", ""))) if current else str(source.get("source_path", "")), "pipeline_run_id": run_id,
            "reason": reason, "evidence": evidence}
    if current and current.get("status") in {"FAILED", "REJECTED"} and status == "PENDING":
        retry_id = str(current.get("event_sha256", ""))
        transition(source_id, "PENDING", **{**args, "reason": "Explicit Retry %s attempt started." % current.get("status"),
                    "retry_of": retry_id or None, "evidence": {**evidence, "explicit_retry": True},
                    "repository_root": repository_root})
    if status == "READY":
        evidence["candidate_id"] = str(pipeline.get("candidate_id", ""))
        try: return transition(source_id, "READY", **{**args, "evidence": evidence, "repository_root": repository_root})
        except OwnerReleaseLibraryError as exc:
            # A run that solved but did not receive an exact current canonical
            # Release Pool receipt is a failed processing outcome. Keeping it
            # in Pending made the same PNG appear runnable forever.
            return transition(source_id, "FAILED", **{**args, "reason": f"RELEASE_POOL_VERIFICATION_FAILED: {str(exc)[:360]}", "evidence": evidence, "repository_root": repository_root})
    return transition(source_id, status, **{**args, "repository_root": repository_root})

def assert_solver_allowed(source_ids: list[str] | tuple[str, ...], *, repository_root: str | Path | None = None) -> None:
    """Reject explicit owner-rejected source identities before solver dispatch."""
    rejected = {str(row.get("source_id")) for row in list_records("REJECTED", repository_root=repository_root)["records"]}
    if any(str(source_id) in rejected for source_id in source_ids):
        raise OwnerReleaseLibraryError("owner-rejected artwork is excluded from solver retry")

def record_batch_outcomes(job: Mapping[str, Any], *, repository_root: str | Path | None = None) -> list[dict[str, Any]]:
    """Record terminal solver outcomes already verified by the canonical PNG batch engine.

    Safe to call after each item or at batch completion. Each status projection is
    updated atomically while the complete immutable event chain is preserved.
    """
    results = []
    for item in job.get("items", []):
        if not isinstance(item, Mapping) or item.get("status") not in {"READY", "FAILED", "REJECTED"}:
            continue
        # The batch engine records each terminal item when it finishes; re-projecting
        # all of them after Stop took minutes on a 1256-PNG batch (2026-11-13).
        projection = item.get("owner_release_projection")
        if isinstance(projection, Mapping) and projection.get("state") == "RECORDED" and projection.get("status") == item.get("status"):
            continue
        source_id = str(item.get("source_id", ""))
        run_id = str(item.get("run_id", "")) or None
        outcome = str(item.get("status"))
        pipeline = {"run_id": run_id, "disposition": outcome,
                    "primary": {"state": outcome,
                                "files": item.get("artifact_refs", {})},
                    "reason": str(item.get("reason", "")), "candidate_id": item.get("candidate_id"),
                    "batch_id": str(job.get("batch_id", ""))}
        results.append(transition_pipeline(source_id, pipeline, repository_root=repository_root))
    return results


def begin_batch_item_attempt(job: Mapping[str, Any], item: Mapping[str, Any], *, repository_root: str | Path | None = None) -> dict[str, Any] | None:
    """Move an explicit retry back to Pending before its solver attempt starts."""
    source_id = str(item.get("source_id", ""))
    source_sha = str(item.get("source_sha256", ""))
    original_path = str(item.get("original_source_path", ""))
    if not source_id or not _SHA.fullmatch(source_sha):
        raise OwnerReleaseLibraryError("batch item lacks a verified source identity for Pending projection")
    if not original_path:
        from .studio_extensions import verify_owner_source

        source = verify_owner_source(source_id)
        original_path = str(source.get("source_path", ""))
        path_value = Path(original_path)
        if original_path and not path_value.is_absolute():
            base = Path(repository_root).resolve() if repository_root is not None else owner_art_storage.factory_repository_root()
            original_path = str((base / path_value).resolve())
    if not original_path:
        raise OwnerReleaseLibraryError("batch item source path could not be resolved for Pending projection")
    view = list_records(repository_root=repository_root)
    current = next((row for row in view["records"] if row.get("source_id") == source_id), None)
    if current and current.get("source_sha256") != source_sha:
        raise OwnerReleaseLibraryError("batch item source SHA differs from the current Release Pool status")
    prior_status = str(current.get("status", "")) if current else ""
    retry_of = str(current.get("event_sha256", "")) if prior_status in {"FAILED", "REJECTED"} else None
    evidence = {"batch_attempt_started": True, "batch_id": str(job.get("batch_id", "")),
                "explicit_retry": prior_status in {"FAILED", "REJECTED"}}
    return transition(
        source_id, "PENDING", source_sha256=source_sha, provider=str(current.get("provider", item.get("source_provider", "PIXELLAB"))) if current else str(item.get("source_provider", "PIXELLAB")),
        original_source_path=original_path, reason="Solver attempt started; source remains Pending until a terminal verified outcome.",
        batch_id=str(job.get("batch_id", "")) or None, pipeline_run_id=str(item.get("run_id", "")) or None,
        retry_of=retry_of, evidence=evidence, repository_root=repository_root,
    )


def record_batch_item_outcome(job: Mapping[str, Any], item: Mapping[str, Any], *, repository_root: str | Path | None = None) -> dict[str, Any] | None:
    """Immediately project one terminal PNG outcome into its Release Pool folder."""
    if item.get("status") not in {"READY", "FAILED", "REJECTED"}:
        return None
    one_item_job = {"batch_id": job.get("batch_id"), "items": [item]}
    result = record_batch_outcomes(one_item_job, repository_root=repository_root)
    return result[0] if result else None

__all__ = ["OwnerReleaseLibraryError", "assert_solver_allowed", "begin_batch_item_attempt", "list_records", "record_batch_item_outcome", "record_batch_outcomes", "record_import_items", "transition", "transition_pipeline"]
