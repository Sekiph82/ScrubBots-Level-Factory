"""OWNER_UPLOAD record, byte-preservation, dimension, and separation checks."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
import hashlib
from pathlib import Path

from .unified import QAContractError, _canonical_bytes, _sha

SOURCE_PRESERVATION_SCHEMA = "scrubbots-owner-source-preservation-qa"
SOURCE_PRESERVATION_VERSION = 2


@dataclass(frozen=True, slots=True)
class OwnerSourceRecord:
    source_id: str
    source_path: str
    source_sha256: str
    byte_length: int
    width: int
    height: int
    origin: str = "OWNER_UPLOAD"
    status: str = "SOURCE_ONLY"
    validation_state: str = "UNVALIDATED"
    schema: str = "scrubbots-owner-upload-source"
    version: int = 1

    def __post_init__(self) -> None:
        if type(self.source_id) is not str or not self.source_id.strip() or type(self.source_path) is not str or not self.source_path.strip():
            raise QAContractError("OWNER_UPLOAD source record identity is malformed")
        _sha(self.source_sha256, "OWNER_UPLOAD source SHA-256")
        if type(self.byte_length) is not int or self.byte_length < 0 or type(self.width) is not int or type(self.height) is not int or self.width < 1 or self.height < 1:
            raise QAContractError("OWNER_UPLOAD source record length/dimensions are malformed")
        if (self.origin, self.status, self.validation_state) != ("OWNER_UPLOAD", "SOURCE_ONLY", "UNVALIDATED"):
            raise QAContractError("source record is not accepted immutable OWNER_UPLOAD SOURCE_ONLY")

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "OwnerSourceRecord":
        if not isinstance(value, Mapping):
            raise QAContractError("OWNER_UPLOAD source record must be a mapping")
        return cls(str(value["source_id"]), str(value.get("source_path", value.get("immutable_path", ""))), value["source_sha256"], value["byte_length"], value.get("original_width", value.get("width")), value.get("original_height", value.get("height")), value.get("origin", "OWNER_UPLOAD"), value.get("status", "SOURCE_ONLY"), value.get("validation_state", "UNVALIDATED"), value.get("schema", "scrubbots-owner-upload-source"), value.get("version", 1))

    @classmethod
    def from_m05_owner_upload(cls, record: Mapping[str, object]) -> "OwnerSourceRecord":
        if not isinstance(record, Mapping):
            raise QAContractError("OWNER_UPLOAD source record must be a mapping")
        value = dict(record)
        value["source_path"] = value.get("source_path", value.get("immutable_relative_path", ""))
        return cls.from_mapping(value)

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "source_id": self.source_id, "source_sha256": self.source_sha256, "byte_length": self.byte_length, "width": self.width, "height": self.height, "origin": self.origin, "status": self.status, "validation_state": self.validation_state}


@dataclass(frozen=True, slots=True)
class SourcePreservationReport:
    source_id: str
    disposition: str
    source_sha256: str
    byte_length: int
    width: int
    height: int
    derived_artifact_paths: tuple[str, ...]
    reason: str
    schema: str = SOURCE_PRESERVATION_SCHEMA
    version: int = SOURCE_PRESERVATION_VERSION

    def __post_init__(self) -> None:
        if type(self.source_id) is not str or not self.source_id.strip() or self.disposition not in {"PASS", "FAIL", "ERROR"}:
            raise QAContractError("source-preservation identity/disposition is malformed")
        _sha(self.source_sha256, "source-preservation SHA-256")
        if type(self.byte_length) is not int or self.byte_length < 0 or type(self.width) is not int or type(self.height) is not int or self.width < 1 or self.height < 1:
            raise QAContractError("source-preservation dimensions/length are malformed")
        if type(self.derived_artifact_paths) is not tuple or any(type(path) is not str or not path.strip() for path in self.derived_artifact_paths) or type(self.reason) is not str or not self.reason.strip():
            raise QAContractError("source-preservation report is malformed")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "source_id": self.source_id, "disposition": self.disposition, "source_sha256": self.source_sha256, "byte_length": self.byte_length, "dimensions": {"width": self.width, "height": self.height}, "derived_artifact_paths": list(self.derived_artifact_paths), "reason": self.reason}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def verify_owner_source_preservation(record: OwnerSourceRecord | Mapping[str, object] | str, source_path: str | None = None, *, recorded_sha256: str | None = None, recorded_byte_length: int | None = None, width: int | None = None, height: int | None = None, analysis: Callable[[], object] | None = None, derived_artifact_paths: Iterable[str] = ()) -> SourcePreservationReport:
    """Verify accepted OWNER_UPLOAD bytes before/after bounded derived analysis."""

    try:
        if isinstance(record, OwnerSourceRecord):
            owner_record = record
        elif isinstance(record, Mapping):
            owner_record = OwnerSourceRecord.from_mapping(record)
        else:
            if source_path is None or recorded_sha256 is None or recorded_byte_length is None or width is None or height is None:
                raise QAContractError("accepted OWNER_UPLOAD source record is required")
            owner_record = OwnerSourceRecord(str(record), source_path, recorded_sha256, recorded_byte_length, width, height)
        source = Path(owner_record.source_path)
        derived = tuple(str(path) for path in derived_artifact_paths)
        source_resolved = source.resolve(strict=False)
        for path in derived:
            derived_resolved = Path(path).resolve(strict=False)
            if derived_resolved == source_resolved or (derived_resolved.exists() and source.exists() and derived_resolved.samefile(source_resolved)):
                return SourcePreservationReport(owner_record.source_id, "FAIL", owner_record.source_sha256, owner_record.byte_length, owner_record.width, owner_record.height, derived, "derived destination aliases immutable OWNER_UPLOAD source")
        before = source.read_bytes()
        if len(before) != owner_record.byte_length or hashlib.sha256(before).hexdigest() != owner_record.source_sha256:
            return SourcePreservationReport(owner_record.source_id, "FAIL", hashlib.sha256(before).hexdigest(), len(before), owner_record.width, owner_record.height, derived, "OWNER_UPLOAD source bytes do not match accepted immutable record")
        if analysis is not None:
            analysis()
        after = source.read_bytes()
        after_sha = hashlib.sha256(after).hexdigest()
        if after != before or len(after) != owner_record.byte_length or after_sha != owner_record.source_sha256:
            return SourcePreservationReport(owner_record.source_id, "FAIL", after_sha, len(after), owner_record.width, owner_record.height, derived, "analysis changed OWNER_UPLOAD source bytes")
        return SourcePreservationReport(owner_record.source_id, "PASS", owner_record.source_sha256, owner_record.byte_length, owner_record.width, owner_record.height, derived, "accepted OWNER_UPLOAD bytes, dimensions, and identity remained unchanged")
    except (OSError, TypeError, ValueError, KeyError, QAContractError) as exc:
        fallback_sha = recorded_sha256 if recorded_sha256 is not None else "0" * 64
        fallback_width = width if type(width) is int and width > 0 else 1
        fallback_height = height if type(height) is int and height > 0 else 1
        return SourcePreservationReport(str(record.get("source_id", "UNKNOWN") if isinstance(record, Mapping) else record), "ERROR", fallback_sha, recorded_byte_length if type(recorded_byte_length) is int and recorded_byte_length >= 0 else 0, fallback_width, fallback_height, tuple(str(path) for path in derived_artifact_paths), f"OWNER_UPLOAD preservation check failed closed: {exc}")


__all__ = ["SOURCE_PRESERVATION_SCHEMA", "SOURCE_PRESERVATION_VERSION", "OwnerSourceRecord", "SourcePreservationReport", "verify_owner_source_preservation"]
