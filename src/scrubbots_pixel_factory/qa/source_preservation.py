"""OWNER_UPLOAD byte-preservation checks for Unified QA."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import hashlib

from .unified import QAContractError, _canonical_bytes, _sha


SOURCE_PRESERVATION_SCHEMA = "scrubbots-owner-source-preservation-qa"
SOURCE_PRESERVATION_VERSION = 1


@dataclass(frozen=True, slots=True)
class SourcePreservationReport:
    source_id: str
    disposition: str
    source_sha256: str
    byte_length: int
    derived_artifact_paths: tuple[str, ...]
    reason: str
    schema: str = SOURCE_PRESERVATION_SCHEMA
    version: int = SOURCE_PRESERVATION_VERSION

    def __post_init__(self) -> None:
        if type(self.source_id) is not str or not self.source_id.strip():
            raise QAContractError("source_id is required")
        if self.disposition not in {"PASS", "FAIL", "ERROR"}:
            raise QAContractError("source-preservation disposition is closed")
        _sha(self.source_sha256, "source-preservation SHA-256")
        if type(self.byte_length) is not int or self.byte_length < 0:
            raise QAContractError("source-preservation byte length is malformed")
        if type(self.derived_artifact_paths) is not tuple or any(type(path) is not str or not path.strip() for path in self.derived_artifact_paths):
            raise QAContractError("derived artifact paths are malformed")
        if type(self.reason) is not str or not self.reason.strip():
            raise QAContractError("source-preservation reason is required")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "source_id": self.source_id, "disposition": self.disposition, "source_sha256": self.source_sha256, "byte_length": self.byte_length, "derived_artifact_paths": list(self.derived_artifact_paths), "reason": self.reason}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def verify_owner_source_preservation(
    source_id: str,
    source_path: str,
    *,
    recorded_sha256: str,
    recorded_byte_length: int,
    analysis: Callable[[], object] | None = None,
    derived_artifact_paths: Iterable[str] = (),
) -> SourcePreservationReport:
    """Verify exact source bytes before/after a bounded derived analysis."""

    from pathlib import Path

    _sha(recorded_sha256, "recorded source SHA-256")
    path = Path(source_path)
    try:
        before = path.read_bytes()
        if len(before) != recorded_byte_length or hashlib.sha256(before).hexdigest() != recorded_sha256:
            return SourcePreservationReport(source_id, "FAIL", hashlib.sha256(before).hexdigest(), len(before), tuple(derived_artifact_paths), "OWNER_UPLOAD source bytes do not match the immutable source record")
        if analysis is not None:
            analysis()
        after = path.read_bytes()
        after_sha = hashlib.sha256(after).hexdigest()
        if after != before or len(after) != recorded_byte_length or after_sha != recorded_sha256:
            return SourcePreservationReport(source_id, "FAIL", after_sha, len(after), tuple(derived_artifact_paths), "analysis changed OWNER_UPLOAD source bytes")
        return SourcePreservationReport(source_id, "PASS", recorded_sha256, recorded_byte_length, tuple(derived_artifact_paths), "OWNER_UPLOAD bytes and immutable identity remained unchanged")
    except (OSError, TypeError, ValueError) as exc:
        return SourcePreservationReport(source_id, "ERROR", recorded_sha256, 0, tuple(derived_artifact_paths), f"OWNER_UPLOAD preservation check failed closed: {exc}")


__all__ = ["SOURCE_PRESERVATION_SCHEMA", "SOURCE_PRESERVATION_VERSION", "SourcePreservationReport", "verify_owner_source_preservation"]
