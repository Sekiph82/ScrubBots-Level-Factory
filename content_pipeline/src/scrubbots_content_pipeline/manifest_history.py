"""Append-only, deterministic local history for exact manifest bytes."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


MANIFEST_HISTORY_SCHEMA = "scrubbots.content.manifest.history.v1"
_HISTORY_KEYS = {"schema", "records", "tip_sha256"}
_RECORD_KEYS = {
    "sequence", "content_version", "manifest_sha256", "manifest_bytes_base64",
    "previous_record_sha256", "recorded_at_utc", "record_sha256",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_UTC = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")


class ManifestHistoryReasonCode(str, Enum):
    VALID = "VALID"
    INVALID_HISTORY = "INVALID_HISTORY"
    INVALID_RECORD = "INVALID_RECORD"
    INVALID_MANIFEST_BYTES = "INVALID_MANIFEST_BYTES"
    INVALID_CONTENT_VERSION = "INVALID_CONTENT_VERSION"
    INVALID_RECORD_TIME = "INVALID_RECORD_TIME"
    SEQUENCE_MISMATCH = "SEQUENCE_MISMATCH"
    CONTENT_VERSION_NOT_INCREASED = "CONTENT_VERSION_NOT_INCREASED"
    MANIFEST_SHA256_MISMATCH = "MANIFEST_SHA256_MISMATCH"
    PREVIOUS_RECORD_MISMATCH = "PREVIOUS_RECORD_MISMATCH"
    RECORD_SHA256_MISMATCH = "RECORD_SHA256_MISMATCH"
    EXPECTED_TIP_MISMATCH = "EXPECTED_TIP_MISMATCH"


class ManifestHistoryError(ValueError):
    """Raised when history input cannot be safely parsed or appended."""

    def __init__(self, reason_code: ManifestHistoryReasonCode) -> None:
        super().__init__(reason_code.value)
        self.reason_code = reason_code


@dataclass(frozen=True, slots=True)
class ManifestHistoryRecord:
    sequence: int
    content_version: int
    manifest_sha256: str
    manifest_bytes: bytes
    previous_record_sha256: str | None
    recorded_at_utc: str
    record_sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "content_version": self.content_version,
            "manifest_sha256": self.manifest_sha256,
            "manifest_bytes_base64": base64.b64encode(self.manifest_bytes).decode("ascii"),
            "previous_record_sha256": self.previous_record_sha256,
            "recorded_at_utc": self.recorded_at_utc,
            "record_sha256": self.record_sha256,
        }

    def _digest_fields(self) -> dict[str, object]:
        fields = self.to_dict()
        del fields["record_sha256"]
        return fields


@dataclass(frozen=True, slots=True)
class ManifestHistoryV1:
    records: tuple[ManifestHistoryRecord, ...] = ()
    tip_sha256: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.records, tuple) or any(
            not isinstance(record, ManifestHistoryRecord) for record in self.records
        ):
            raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_HISTORY)


@dataclass(frozen=True, slots=True)
class ManifestHistoryValidationResult:
    accepted: bool
    reason_code: ManifestHistoryReasonCode
    verified_records: tuple[ManifestHistoryRecord, ...]
    tip_sha256: str | None


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _manifest_content_version(manifest_bytes: bytes) -> int:
    if type(manifest_bytes) is not bytes:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_MANIFEST_BYTES)
    try:
        value = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_MANIFEST_BYTES) from exc
    if not isinstance(value, dict):
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_MANIFEST_BYTES)
    version = value.get("content_version")
    if type(version) is not int or version < 1:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_CONTENT_VERSION)
    return version


def _normalize_record_time(value: str | datetime) -> str:
    if isinstance(value, str):
        if not _UTC.fullmatch(value):
            raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_RECORD_TIME)
        try:
            parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError as exc:
            raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_RECORD_TIME) from exc
        if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
            raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_RECORD_TIME)
        return value
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_RECORD_TIME)
    normalized = value.astimezone(timezone.utc)
    if normalized.microsecond:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_RECORD_TIME)
    return normalized.strftime("%Y-%m-%dT%H:%M:%SZ")


def _record_digest(record: ManifestHistoryRecord) -> str:
    return hashlib.sha256(_canonical_json(record._digest_fields())).hexdigest()


def append_manifest_history(
    history: ManifestHistoryV1, manifest_bytes: bytes, *, recorded_at_utc: str | datetime
) -> ManifestHistoryV1:
    """Return a new history with one exact-byte manifest record appended."""
    if not isinstance(history, ManifestHistoryV1):
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_HISTORY)
    verification = verify_manifest_history(history)
    if not verification.accepted:
        raise ManifestHistoryError(verification.reason_code)
    if type(manifest_bytes) is not bytes:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_MANIFEST_BYTES)
    content_version = _manifest_content_version(manifest_bytes)
    if history.records and content_version <= history.records[-1].content_version:
        raise ManifestHistoryError(ManifestHistoryReasonCode.CONTENT_VERSION_NOT_INCREASED)
    timestamp = _normalize_record_time(recorded_at_utc)
    previous = history.records[-1].record_sha256 if history.records else None
    provisional = ManifestHistoryRecord(
        sequence=len(history.records) + 1,
        content_version=content_version,
        manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        manifest_bytes=manifest_bytes,
        previous_record_sha256=previous,
        recorded_at_utc=timestamp,
        record_sha256="",
    )
    record = ManifestHistoryRecord(
        sequence=provisional.sequence,
        content_version=provisional.content_version,
        manifest_sha256=provisional.manifest_sha256,
        manifest_bytes=provisional.manifest_bytes,
        previous_record_sha256=provisional.previous_record_sha256,
        recorded_at_utc=provisional.recorded_at_utc,
        record_sha256=_record_digest(provisional),
    )
    return ManifestHistoryV1((*history.records, record), record.record_sha256)


def verify_manifest_history(
    history: ManifestHistoryV1, *, expected_tip_sha256: str | None = None
) -> ManifestHistoryValidationResult:
    """Replay and verify the entire append-only chain, optionally against a pinned tip."""
    if not isinstance(history, ManifestHistoryV1):
        return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.INVALID_HISTORY, (), None)
    previous_digest: str | None = None
    previous_version = 0
    verified: list[ManifestHistoryRecord] = []
    for expected_sequence, record in enumerate(history.records, start=1):
        if not isinstance(record, ManifestHistoryRecord):
            return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.INVALID_RECORD, tuple(verified), previous_digest)
        if type(record.sequence) is not int or record.sequence != expected_sequence:
            return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.SEQUENCE_MISMATCH, tuple(verified), previous_digest)
        if type(record.content_version) is not int or record.content_version <= previous_version:
            return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.CONTENT_VERSION_NOT_INCREASED, tuple(verified), previous_digest)
        if type(record.manifest_bytes) is not bytes:
            return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.INVALID_MANIFEST_BYTES, tuple(verified), previous_digest)
        try:
            embedded_version = _manifest_content_version(record.manifest_bytes)
        except ManifestHistoryError as exc:
            return ManifestHistoryValidationResult(False, exc.reason_code, tuple(verified), previous_digest)
        if embedded_version != record.content_version:
            return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.INVALID_CONTENT_VERSION, tuple(verified), previous_digest)
        if not isinstance(record.manifest_sha256, str) or not _SHA256.fullmatch(record.manifest_sha256) or hashlib.sha256(record.manifest_bytes).hexdigest() != record.manifest_sha256:
            return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.MANIFEST_SHA256_MISMATCH, tuple(verified), previous_digest)
        if record.previous_record_sha256 != previous_digest:
            return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.PREVIOUS_RECORD_MISMATCH, tuple(verified), previous_digest)
        try:
            if _normalize_record_time(record.recorded_at_utc) != record.recorded_at_utc:
                raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_RECORD_TIME)
        except (ManifestHistoryError, TypeError):
            return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.INVALID_RECORD_TIME, tuple(verified), previous_digest)
        try:
            computed_record_digest = _record_digest(record)
        except (TypeError, ValueError):
            return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.INVALID_RECORD, tuple(verified), previous_digest)
        if not isinstance(record.record_sha256, str) or not _SHA256.fullmatch(record.record_sha256) or computed_record_digest != record.record_sha256:
            return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.RECORD_SHA256_MISMATCH, tuple(verified), previous_digest)
        verified.append(record)
        previous_digest = record.record_sha256
        previous_version = record.content_version
    if expected_tip_sha256 is not None and expected_tip_sha256 != previous_digest:
        return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.EXPECTED_TIP_MISMATCH, tuple(verified), previous_digest)
    if history.tip_sha256 != previous_digest:
        return ManifestHistoryValidationResult(False, ManifestHistoryReasonCode.EXPECTED_TIP_MISMATCH, tuple(verified), previous_digest)
    return ManifestHistoryValidationResult(True, ManifestHistoryReasonCode.VALID, tuple(verified), previous_digest)


def serialize_manifest_history(history: ManifestHistoryV1) -> bytes:
    """Serialize valid history to deterministic JSON while retaining exact manifest bytes."""
    result = verify_manifest_history(history)
    if not result.accepted:
        raise ManifestHistoryError(result.reason_code)
    return _canonical_json({
        "schema": MANIFEST_HISTORY_SCHEMA,
        "records": [record.to_dict() for record in result.verified_records],
        "tip_sha256": result.tip_sha256,
    })


def parse_manifest_history(raw: bytes) -> ManifestHistoryV1:
    """Parse canonical history JSON and reject any malformed or invalid chain."""
    if type(raw) is not bytes:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_HISTORY)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_HISTORY) from exc
    if not isinstance(value, dict) or set(value) != _HISTORY_KEYS or value.get("schema") != MANIFEST_HISTORY_SCHEMA:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_HISTORY)
    raw_records = value.get("records")
    if not isinstance(raw_records, list):
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_HISTORY)
    records: list[ManifestHistoryRecord] = []
    for item in raw_records:
        if not isinstance(item, dict) or set(item) != _RECORD_KEYS:
            raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_RECORD)
        try:
            encoded = item["manifest_bytes_base64"]
            if not isinstance(encoded, str):
                raise ValueError
            manifest_bytes = base64.b64decode(encoded, validate=True)
            record = ManifestHistoryRecord(
                sequence=item["sequence"],
                content_version=item["content_version"],
                manifest_sha256=item["manifest_sha256"],
                manifest_bytes=manifest_bytes,
                previous_record_sha256=item["previous_record_sha256"],
                recorded_at_utc=item["recorded_at_utc"],
                record_sha256=item["record_sha256"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_RECORD) from exc
        records.append(record)
    tip_sha256 = value.get("tip_sha256")
    if tip_sha256 is not None and (not isinstance(tip_sha256, str) or not _SHA256.fullmatch(tip_sha256)):
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_HISTORY)
    history = ManifestHistoryV1(tuple(records), tip_sha256)
    result = verify_manifest_history(history)
    if not result.accepted:
        raise ManifestHistoryError(result.reason_code)
    if serialize_manifest_history(history) != raw:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_HISTORY)
    return history


def historical_manifest_json(record: ManifestHistoryRecord) -> object:
    """Decode exact historical JSON without applying current application-schema policy."""
    if not isinstance(record, ManifestHistoryRecord):
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_RECORD)
    try:
        return json.loads(record.manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestHistoryError(ManifestHistoryReasonCode.INVALID_MANIFEST_BYTES) from exc


__all__ = [
    "MANIFEST_HISTORY_SCHEMA",
    "ManifestHistoryError",
    "ManifestHistoryReasonCode",
    "ManifestHistoryRecord",
    "ManifestHistoryV1",
    "ManifestHistoryValidationResult",
    "append_manifest_history",
    "historical_manifest_json",
    "parse_manifest_history",
    "serialize_manifest_history",
    "verify_manifest_history",
]
