"""Local builder for validated, declarative .scrubpack V1 level inputs."""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .content_boundary import ContentDisposition, classify_content
from .payload_validation import PayloadReasonCode, validate_remote_payload
from .scrubpack_spec import (
    PACK_MANIFEST_PATH,
    SCRUBPACK_VERSION,
    ScrubpackLevelV1,
    ScrubpackManifestV1,
    ScrubpackSpecError,
    expected_member_names,
    validate_member_names,
)


_CONTENT_TYPES = {
    "level_data": "level_data",
    "supply_plan": "supply_plan_data",
    "metadata": "approved_metadata",
}


class ScrubpackBuildError(ValueError):
    """Raised when an explicit input is not an eligible current data payload."""


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class ScrubpackPayloadInput:
    """One descriptor and its exact payload bytes, supplied explicitly."""

    descriptor: Mapping[str, object]
    payload: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.descriptor, Mapping):
            raise ScrubpackBuildError("descriptor must be a mapping")
        if type(self.payload) is not bytes:
            raise ScrubpackBuildError("payload must be immutable bytes")
        object.__setattr__(self, "descriptor", _freeze(self.descriptor))

    @classmethod
    def from_path(cls, descriptor: Mapping[str, object], path: str | Path) -> ScrubpackPayloadInput:
        """Read only the caller-named local regular file; no discovery is done."""
        source = Path(path)
        raw_path = str(path)
        if raw_path.startswith(("\\\\", "//")) or source.is_symlink() or not source.is_file():
            raise ScrubpackBuildError("source path must name a local regular file")
        try:
            payload = source.read_bytes()
        except OSError as exc:
            raise ScrubpackBuildError("source file could not be read") from exc
        return cls(descriptor=descriptor, payload=payload)


@dataclass(frozen=True, slots=True)
class ScrubpackLevelInput:
    """The three explicit, descriptor-bound payloads for one level."""

    level_id: str
    level_data: ScrubpackPayloadInput
    supply_plan: ScrubpackPayloadInput
    metadata: ScrubpackPayloadInput

    def __post_init__(self) -> None:
        ScrubpackLevelV1(self.level_id)
        for name in ("level_data", "supply_plan", "metadata"):
            if not isinstance(getattr(self, name), ScrubpackPayloadInput):
                raise ScrubpackBuildError(f"{name} must be an explicit payload input")


@dataclass(frozen=True, slots=True)
class ScrubpackPayloadEvidence:
    member_path: str
    payload_sha256: str
    byte_length: int
    validation_reason: str


@dataclass(frozen=True, slots=True)
class ScrubpackLevelEvidence:
    level_id: str
    payloads: tuple[ScrubpackPayloadEvidence, ...]


@dataclass(frozen=True, slots=True)
class ScrubpackBuildEvidence:
    version: int
    pack_id: str
    pack_version: int
    created_at_utc: str
    level_count: int
    level_ids: tuple[str, ...]
    member_names: tuple[str, ...]
    levels: tuple[ScrubpackLevelEvidence, ...]


@dataclass(frozen=True, slots=True)
class ScrubpackBuildResult:
    archive_bytes: bytes
    evidence: ScrubpackBuildEvidence


def _validated_payload(
    level_id: str,
    role: str,
    source: ScrubpackPayloadInput,
    member_path: str,
) -> tuple[bytes, ScrubpackPayloadEvidence]:
    expected_type = _CONTENT_TYPES[role]
    classification = classify_content(source.descriptor)
    if classification.disposition is not ContentDisposition.REMOTE_DECLARATIVE:
        reason = ",".join(code.value for code in classification.reason_codes)
        raise ScrubpackBuildError(f"{member_path}: descriptor rejected ({reason})")
    if source.descriptor.get("content_type") != expected_type:
        raise ScrubpackBuildError(f"{member_path}: unsupported payload family")
    attributes = source.descriptor.get("attributes")
    if not isinstance(attributes, Mapping) or attributes.get("level_id") != level_id:
        raise ScrubpackBuildError(f"{member_path}: descriptor level identity mismatch")
    validation = validate_remote_payload(source.descriptor, source.payload)
    if not validation.accepted:
        if validation.reason_code is PayloadReasonCode.EXECUTABLE_CONTENT:
            raise ScrubpackBuildError(f"{member_path}: executable content rejected")
        raise ScrubpackBuildError(f"{member_path}: payload rejected ({validation.reason_code.value})")
    evidence = ScrubpackPayloadEvidence(
        member_path=member_path,
        payload_sha256=hashlib.sha256(source.payload).hexdigest(),
        byte_length=len(source.payload),
        validation_reason=validation.reason_code.value,
    )
    return source.payload, evidence


def build_scrubpack(
    levels: Sequence[ScrubpackLevelInput],
    *,
    pack_id: str,
    pack_version: int,
    created_at_utc: str | datetime,
) -> ScrubpackBuildResult:
    """Build an in-memory V1 ZIP using explicit immutable identity/time inputs."""
    if isinstance(levels, (str, bytes, bytearray)) or not isinstance(levels, Sequence):
        raise ScrubpackBuildError("levels must be an explicit sequence")
    level_inputs = tuple(levels)
    if not level_inputs:
        raise ScrubpackBuildError("at least one level is required")
    if any(not isinstance(level, ScrubpackLevelInput) for level in level_inputs):
        raise ScrubpackBuildError("every level must be an explicit ScrubpackLevelInput")

    level_specs = tuple(ScrubpackLevelV1(level.level_id) for level in level_inputs)
    try:
        manifest = ScrubpackManifestV1(
            levels=level_specs,
            pack_id=pack_id,
            pack_version=pack_version,
            created_at_utc=created_at_utc,
        )
    except ScrubpackSpecError as exc:
        raise ScrubpackBuildError(str(exc)) from exc
    member_names = expected_member_names(level_specs)
    if not validate_member_names(member_names):
        raise ScrubpackBuildError("generated archive member layout is invalid")

    members: list[tuple[str, bytes]] = []
    level_evidence: list[ScrubpackLevelEvidence] = []
    for level_input, level_spec in zip(level_inputs, level_specs, strict=True):
        payload_evidence: list[ScrubpackPayloadEvidence] = []
        for role, source, path in (
            ("level_data", level_input.level_data, level_spec.level_data_path),
            ("supply_plan", level_input.supply_plan, level_spec.supply_plan_path),
            ("metadata", level_input.metadata, level_spec.metadata_path),
        ):
            payload, evidence = _validated_payload(level_input.level_id, role, source, path)
            members.append((path, payload))
            payload_evidence.append(evidence)
        level_evidence.append(ScrubpackLevelEvidence(level_input.level_id, tuple(payload_evidence)))

    manifest_bytes = json.dumps(manifest.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        archive.writestr(PACK_MANIFEST_PATH, manifest_bytes)
        for member_path, payload in members:
            archive.writestr(member_path, payload)

    evidence = ScrubpackBuildEvidence(
        version=SCRUBPACK_VERSION,
        pack_id=manifest.pack_id,
        pack_version=manifest.pack_version,
        created_at_utc=manifest.created_at_utc,
        level_count=len(manifest.levels),
        level_ids=tuple(level.level_id for level in level_inputs),
        member_names=member_names,
        levels=tuple(level_evidence),
    )
    return ScrubpackBuildResult(archive_bytes=output.getvalue(), evidence=evidence)


__all__ = [
    "ScrubpackBuildError",
    "ScrubpackBuildEvidence",
    "ScrubpackBuildResult",
    "ScrubpackLevelEvidence",
    "ScrubpackLevelInput",
    "ScrubpackPayloadEvidence",
    "ScrubpackPayloadInput",
    "build_scrubpack",
]
