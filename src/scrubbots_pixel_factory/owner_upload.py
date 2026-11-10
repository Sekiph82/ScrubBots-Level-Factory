"""Immutable, content-addressed OWNER_UPLOAD source ingestion.

This module stores the exact selected PNG bytes as a SOURCE_ONLY artifact. It
does not normalize, palette-snap, compile, validate, or promote the image.
"""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from pathlib import Path
import re
import stat
import time

from .semantic.normalization.core import (
    RAW_ARTIFACT_MAX_BYTES,
    SUPPORTED_MEDIA_TYPE,
    SemanticRawArtifact,
)


OWNER_UPLOAD_OPERATION = "owner-upload-import"
OWNER_UPLOAD_SCHEMA = "scrubbots-owner-upload-source"
OWNER_UPLOAD_SCHEMA_VERSION = 1
OWNER_UPLOAD_ORIGIN = "OWNER_UPLOAD"
OWNER_UPLOAD_STATUS = "SOURCE_ONLY"
OWNER_UPLOAD_VALIDATION_STATE = "UNVALIDATED"
OWNER_UPLOAD_FILENAME = "source.png"  # Legacy constant retained for historical contracts.
_SOURCE_ID = re.compile(r"owner-upload-[0-9a-f]{64}\Z")
_RECORD_KEYS = frozenset(
    {
        "schema",
        "version",
        "source_id",
        "origin",
        "source_sha256",
        "byte_length",
        "media_type",
        "original_filename",
        "original_width",
        "original_height",
        "immutable_relative_path",
        "source_record_relative_path",
        "status",
        "validation_state",
    }
)


class OwnerUploadError(ValueError):
    """Raised when an owner-selected source cannot be trusted or stored."""


def _canonical_json_bytes(value: Mapping[str, object]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _repository_root() -> Path:
    # The packaged Factory Studio lives under ``Release``. Its module path is
    # an executable install location, never the mutable-art repository root.
    # Resolve the same canonical Desktop checkout used by the rest of the app.
    from .owner_art_storage import factory_repository_root

    return factory_repository_root(__file__)


def _path_is_reparse_point(path: Path) -> bool:
    """Detect symlinks and Windows reparse points without following the final path."""

    try:
        info = path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    except OSError:
        return True
    if stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400):
        return True
    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction):
        try:
            return bool(is_junction())
        except OSError:
            return True
    return False


_RESOLVED_PATHS: dict[str, Path] = {}


def _cached_resolve(path: Path) -> Path:
    # Windows realpath walks dominated startup (~5,000 per refresh). Only the
    # resolution is memoised; the reparse-point checks below run on every call.
    key = str(path)
    resolved = _RESOLVED_PATHS.get(key)
    if resolved is None:
        resolved = path.resolve()
        _RESOLVED_PATHS[key] = resolved
    return resolved


def owner_upload_root(repository_root: str | Path | None = None) -> Path:
    repository = _cached_resolve(Path(repository_root) if repository_root is not None else _repository_root())
    root = repository / "data" / "Level Factory" / "Imported"
    for component in (repository / "data", repository / "data" / "Level Factory", root):
        if _path_is_reparse_point(component):
            raise OwnerUploadError("canonical OWNER_UPLOAD path contains a symlink or reparse point")
    try:
        resolved_root = _cached_resolve(root)
    except (OSError, RuntimeError) as exc:
        raise OwnerUploadError("canonical OWNER_UPLOAD path cannot be resolved safely") from exc
    if resolved_root != root or not resolved_root.is_relative_to(repository):
        raise OwnerUploadError("canonical OWNER_UPLOAD path escaped its repository root")
    return resolved_root


def _error(message: str) -> dict[str, object]:
    return {
        "operation": OWNER_UPLOAD_OPERATION,
        "state": "ERROR",
        "disposition": "ERROR",
        "error": f"ERROR — OWNER_UPLOAD source ingestion: {message[:512]}",
    }


def _source_bytes(source_path: str | Path) -> tuple[Path, bytes, str, int, int, str]:
    raw_path = str(source_path)
    if not raw_path.strip() or "\x00" in raw_path or "://" in raw_path:
        raise OwnerUploadError("source must be an explicitly selected local filesystem path")
    source = Path(source_path)
    if not source.is_file():
        raise OwnerUploadError("source must be an existing local file, not a directory or missing path")
    try:
        if source.stat().st_size > RAW_ARTIFACT_MAX_BYTES:
            raise OwnerUploadError("source exceeds the bounded raw-artifact size policy")
        # This is the existing strict PNG decoder boundary. The transient
        # LOCAL_FILE raw artifact is only used to decode and bind dimensions;
        # it is never persisted or relabeled as OWNER_UPLOAD.
        decoded = SemanticRawArtifact.from_local_file(source, media_type=SUPPORTED_MEDIA_TYPE)
    except OwnerUploadError:
        raise
    except (OSError, TypeError, ValueError) as exc:
        raise OwnerUploadError(f"source is not a supported strict PNG: {exc}") from exc
    raw = bytes(decoded.raw_bytes)
    return source, raw, hashlib.sha256(raw).hexdigest(), decoded.returned_width, decoded.returned_height, source.name


def _record(
    source_id: str,
    source_sha256: str,
    byte_length: int,
    original_filename: str,
    width: int,
    height: int,
) -> dict[str, object]:
    if Path(original_filename).name != original_filename or original_filename in {".", ".."} or not original_filename.lower().endswith(".png"):
        raise OwnerUploadError("selected canonical source filename is unsafe")
    immutable_relative_path = f"data/Level Factory/Imported/{source_id}/{original_filename}"
    return {
        "schema": OWNER_UPLOAD_SCHEMA,
        "version": OWNER_UPLOAD_SCHEMA_VERSION,
        "source_id": source_id,
        "origin": OWNER_UPLOAD_ORIGIN,
        "source_sha256": source_sha256,
        "byte_length": byte_length,
        "media_type": SUPPORTED_MEDIA_TYPE,
        "original_filename": original_filename,
        "original_width": width,
        "original_height": height,
        "immutable_relative_path": immutable_relative_path,
        "source_record_relative_path": f"data/Level Factory/Imported/{source_id}/source.json",
        "status": OWNER_UPLOAD_STATUS,
        "validation_state": OWNER_UPLOAD_VALIDATION_STATE,
    }


def _exact_text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise OwnerUploadError(f"{label} is malformed")
    return value


def _verify_existing(destination: Path, expected: Mapping[str, object], raw: bytes) -> dict[str, object]:
    record_path = destination / "source.json"
    if any(_path_is_reparse_point(path) for path in (destination, record_path)):
        raise OwnerUploadError("content-addressed source destination contains a symlink or reparse point")
    if not record_path.is_file():
        raise OwnerUploadError("content-addressed source destination is incomplete")
    try:
        parsed = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OwnerUploadError(f"existing content-addressed source is unreadable: {exc}") from exc
    if not isinstance(parsed, Mapping) or set(parsed) != _RECORD_KEYS:
        raise OwnerUploadError("existing content-addressed source record is malformed")
    record = dict(parsed)
    filename = str(record.get("original_filename", ""))
    if Path(filename).name != filename or filename in {".", ".."} or not filename.lower().endswith(".png"):
        raise OwnerUploadError("existing canonical imported source filename is unsafe")
    source_path = destination / filename
    if _path_is_reparse_point(source_path) or not source_path.is_file():
        raise OwnerUploadError("content-addressed source destination is incomplete")
    try:
        stored = source_path.read_bytes()
    except OSError as exc:
        raise OwnerUploadError("existing content-addressed source is unreadable") from exc
    expected_immutable = f"data/Level Factory/Imported/{expected['source_id']}/{filename}"
    if (record.get("immutable_relative_path") != expected_immutable
            or record.get("source_record_relative_path") != f"data/Level Factory/Imported/{expected['source_id']}/source.json"
            or any(record.get(key) != expected.get(key) for key in ("schema", "version", "source_id", "origin", "source_sha256", "byte_length", "media_type", "original_width", "original_height", "source_record_relative_path", "status", "validation_state"))):
        raise OwnerUploadError("existing content-addressed source record identity is inconsistent")
    if not _SOURCE_ID.fullmatch(str(record.get("source_id", ""))):
        raise OwnerUploadError("existing source ID is malformed")
    if record.get("origin") != OWNER_UPLOAD_ORIGIN or record.get("status") != OWNER_UPLOAD_STATUS or record.get("validation_state") != OWNER_UPLOAD_VALIDATION_STATE:
        raise OwnerUploadError("existing source provenance or status is not OWNER_UPLOAD SOURCE_ONLY")
    if type(record.get("byte_length")) is not int or record["byte_length"] != len(stored):
        raise OwnerUploadError("existing source byte length does not bind stored bytes")
    if hashlib.sha256(stored).hexdigest() != record.get("source_sha256") or stored != raw:
        raise OwnerUploadError("existing source bytes do not match the content identity")
    if record.get("source_sha256") != expected.get("source_sha256"):
        raise OwnerUploadError("existing source hash does not match the selected bytes")
    return record


def _verify_concurrent_existing(destination: Path, expected: Mapping[str, object], raw: bytes) -> dict[str, object]:
    """Wait briefly for an atomic competing import to finish, never overwrite it."""
    deadline = time.monotonic() + 1.0
    while True:
        try:
            return _verify_existing(destination, expected, raw)
        except OwnerUploadError as exc:
            if not any(marker in str(exc) for marker in ("destination is incomplete", "existing content-addressed source is unreadable")):
                raise
            if time.monotonic() >= deadline:
                raise OwnerUploadError("concurrent OWNER_UPLOAD did not finish a complete immutable source record") from exc
            time.sleep(0.01)


def _result(record: Mapping[str, object], state: str) -> dict[str, object]:
    payload = dict(record)
    payload.update(
        {
            "operation": OWNER_UPLOAD_OPERATION,
            "state": state,
            "disposition": state,
            "source_only_notice": "SOURCE ONLY — validation and candidate derivation are explicit downstream pipeline stages.",
            "claims": {
                "candidate": "NOT AVAILABLE — this task stores source bytes only.",
                "quality": "NOT AVAILABLE — canonical validation has not been run.",
                "solver": "NOT AVAILABLE — canonical ZIP solver evidence is not connected.",
                "difficulty": "NOT AVAILABLE — official Difficulty V1 evidence is not connected.",
                "owner_acceptance": "NOT AVAILABLE — owner acceptance is not performed by source ingestion.",
            },
        }
    )
    return payload


def align_owner_upload_filename(source_id: str, canonical_filename: str, *,
                                repository_root: str | Path | None = None) -> dict[str, object]:
    """Give one Imported record the canonical PixelLab Final filename; bytes never change.

    Generation used to import slices under their per-atlas staging name
    (sprite-NN.png). The readable name everywhere downstream must be the Final
    file name (LF-xxxxxx.png), so the immutable copy and source.json are renamed.
    """
    if not _SOURCE_ID.fullmatch(source_id):
        raise OwnerUploadError("source ID is malformed")
    destination = owner_upload_root(repository_root) / source_id
    record_path = destination / "source.json"
    current = json.loads(record_path.read_text(encoding="utf-8"))
    old_name = str(current.get("original_filename", ""))
    if old_name == canonical_filename:
        return current
    old_file = destination / old_name
    raw = old_file.read_bytes()
    _verify_existing(destination, current, raw)
    if source_id != f"owner-upload-{hashlib.sha256(raw).hexdigest()}":
        raise OwnerUploadError("imported bytes do not match the source identity")
    expected = _record(source_id, str(current["source_sha256"]), len(raw), canonical_filename,
                       int(current["original_width"]), int(current["original_height"]))
    new_file = destination / canonical_filename
    if _path_is_reparse_point(new_file):
        raise OwnerUploadError("canonical imported source target is a reparse point")
    if new_file.exists():
        if new_file.read_bytes() != raw:
            raise OwnerUploadError("canonical imported filename already holds different bytes")
    else:
        new_file.write_bytes(raw)
    temporary = record_path.with_name(".source.json.align.partial")
    temporary.write_bytes(_canonical_json_bytes(expected))
    temporary.replace(record_path)
    old_file.unlink()
    return _verify_existing(destination, expected, raw)


def import_owner_upload(source_path: str | Path, *, repository_root: str | Path | None = None) -> dict[str, object]:
    """Import one explicitly selected strict PNG without transforming it."""

    try:
        source, raw, source_sha256, width, height, original_filename = _source_bytes(source_path)
        source_id = f"owner-upload-{source_sha256}"
        if not _SOURCE_ID.fullmatch(source_id):
            raise OwnerUploadError("derived source identity is malformed")
        destination = owner_upload_root(repository_root) / source_id
        expected = _record(source_id, source_sha256, len(raw), original_filename, width, height)
        if destination.exists():
            record = _verify_concurrent_existing(destination, expected, raw)
            return _result(record, "ALREADY_IMPORTED")
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            destination.mkdir()
        except FileExistsError:
            record = _verify_concurrent_existing(destination, expected, raw)
            return _result(record, "ALREADY_IMPORTED")
        source_path = destination / str(expected["original_filename"])
        if _path_is_reparse_point(source_path):
            raise OwnerUploadError("canonical imported source target is a reparse point")
        source_path.write_bytes(raw)
        (destination / "source.json").write_bytes(_canonical_json_bytes(expected))
        record = _verify_concurrent_existing(destination, expected, raw)
        return _result(record, "IMPORTED")
    except OwnerUploadError as exc:
        return _error(str(exc))
    except (OSError, TypeError, ValueError) as exc:
        return _error(str(exc))


__all__ = [
    "OWNER_UPLOAD_OPERATION",
    "OWNER_UPLOAD_ORIGIN",
    "OWNER_UPLOAD_SCHEMA",
    "OWNER_UPLOAD_SCHEMA_VERSION",
    "OWNER_UPLOAD_STATUS",
    "OWNER_UPLOAD_VALIDATION_STATE",
    "OwnerUploadError",
    "import_owner_upload",
    "owner_upload_root",
]
