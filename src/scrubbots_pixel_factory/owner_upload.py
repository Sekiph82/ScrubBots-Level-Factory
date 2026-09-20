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
OWNER_UPLOAD_FILENAME = "source.png"
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
    return Path(__file__).resolve().parents[2]


def owner_upload_root() -> Path:
    return (_repository_root() / "level_factory" / "output" / "owner-uploads").resolve()


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
    immutable_relative_path = f"owner-uploads/{source_id}/{OWNER_UPLOAD_FILENAME}"
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
        "source_record_relative_path": f"owner-uploads/{source_id}/source.json",
        "status": OWNER_UPLOAD_STATUS,
        "validation_state": OWNER_UPLOAD_VALIDATION_STATE,
    }


def _exact_text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise OwnerUploadError(f"{label} is malformed")
    return value


def _verify_existing(destination: Path, expected: Mapping[str, object], raw: bytes) -> dict[str, object]:
    source_path = destination / OWNER_UPLOAD_FILENAME
    record_path = destination / "source.json"
    if not source_path.is_file() or not record_path.is_file():
        raise OwnerUploadError("content-addressed source destination is incomplete")
    try:
        stored = source_path.read_bytes()
        parsed = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OwnerUploadError(f"existing content-addressed source is unreadable: {exc}") from exc
    if not isinstance(parsed, Mapping) or set(parsed) != _RECORD_KEYS:
        raise OwnerUploadError("existing content-addressed source record is malformed")
    record = dict(parsed)
    if record != dict(expected) and any(record.get(key) != expected.get(key) for key in ("schema", "version", "source_id", "origin", "source_sha256", "byte_length", "media_type", "original_width", "original_height", "immutable_relative_path", "source_record_relative_path", "status", "validation_state")):
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


def _result(record: Mapping[str, object], state: str) -> dict[str, object]:
    payload = dict(record)
    payload.update(
        {
            "operation": OWNER_UPLOAD_OPERATION,
            "state": state,
            "disposition": state,
            "source_only_notice": "SOURCE ONLY — validation/candidate creation pending SB-LFX-004",
            "claims": {
                "candidate": "NOT AVAILABLE — this task stores source bytes only.",
                "quality": "NOT AVAILABLE — validation is pending SB-LFX-004.",
                "solver": "NOT AVAILABLE — gameplay solver is pending M03.",
                "difficulty": "NOT AVAILABLE — measured difficulty is pending M04.",
                "owner_acceptance": "NOT AVAILABLE — owner acceptance is not performed by source ingestion.",
            },
        }
    )
    return payload


def import_owner_upload(source_path: str | Path) -> dict[str, object]:
    """Import one explicitly selected strict PNG without transforming it."""

    try:
        source, raw, source_sha256, width, height, original_filename = _source_bytes(source_path)
        source_id = f"owner-upload-{source_sha256}"
        if not _SOURCE_ID.fullmatch(source_id):
            raise OwnerUploadError("derived source identity is malformed")
        destination = owner_upload_root() / source_id
        expected = _record(source_id, source_sha256, len(raw), original_filename, width, height)
        if destination.exists():
            record = _verify_existing(destination, expected, raw)
            return _result(record, "ALREADY_IMPORTED")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.mkdir()
        (destination / OWNER_UPLOAD_FILENAME).write_bytes(raw)
        (destination / "source.json").write_bytes(_canonical_json_bytes(expected))
        record = _verify_existing(destination, expected, raw)
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
