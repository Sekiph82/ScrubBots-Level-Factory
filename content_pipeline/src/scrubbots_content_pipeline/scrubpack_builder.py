"""Local builder for validated, declarative .scrubpack V1 level inputs."""

from __future__ import annotations

import hashlib
import io
import json
import stat
import zipfile
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .content_boundary import ContentDisposition, classify_content
from .payload_validation import validate_remote_payload
from .scrubpack_spec import (
    PACK_MANIFEST_PATH,
    SCRUBPACK_VERSION,
    ScrubpackLevelV1,
    ScrubpackManifestV1,
    ScrubpackSpecError,
    canonical_json_bytes,
    canonical_level_sort_key,
    expected_member_names,
    validate_member_names,
)


_CONTENT_TYPES = {
    "level_data": "level_data",
    "supply_plan": "supply_plan_data",
    "metadata": "approved_metadata",
}

_SCRUBPACK_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
_SCRUBPACK_ZIP_MODE = (stat.S_IFREG | 0o644) << 16


def _canonical_zip_info(member_name: str) -> zipfile.ZipInfo:
    """Return a ZIP entry with every builder-controlled metadata field fixed."""
    try:
        member_name.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ScrubpackBuildError("scrubpack member names must be canonical ASCII") from exc
    info = zipfile.ZipInfo(member_name, date_time=_SCRUBPACK_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.create_version = 20
    info.extract_version = 20
    info.flag_bits = 0
    info.volume = 0
    info.internal_attr = 0
    info.external_attr = _SCRUBPACK_ZIP_MODE
    info.extra = b""
    info.comment = b""
    return info


class ScrubpackBuildError(ValueError):
    """Raised when an explicit input is not an eligible current data payload."""

    def __init__(self, message: str, *, validation_report: ScrubpackValidationReport | None = None) -> None:
        super().__init__(message)
        self.validation_report = validation_report


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
class ScrubpackRoleDiagnostic:
    role: str
    accepted: bool
    reason_code: str


@dataclass(frozen=True, slots=True)
class ScrubpackLevelDiagnostic:
    level_id: str
    accepted: bool
    roles: tuple[ScrubpackRoleDiagnostic, ...]


@dataclass(frozen=True, slots=True)
class ScrubpackValidationReport:
    accepted: bool
    levels: tuple[ScrubpackLevelDiagnostic, ...]


@dataclass(frozen=True, slots=True)
class ScrubpackBuildEvidence:
    version: int
    pack_id: str
    pack_version: int
    created_at_utc: str
    archive_sha256: str
    archive_byte_length: int
    level_count: int
    level_ids: tuple[str, ...]
    member_names: tuple[str, ...]
    levels: tuple[ScrubpackLevelEvidence, ...]
    validation_report: ScrubpackValidationReport


@dataclass(frozen=True, slots=True)
class ScrubpackBuildResult:
    archive_bytes: bytes
    evidence: ScrubpackBuildEvidence


def _validated_payload(
    level_id: str,
    role: str,
    source: ScrubpackPayloadInput,
    member_path: str,
) -> tuple[bytes | None, ScrubpackPayloadEvidence | None, str]:
    expected_type = _CONTENT_TYPES[role]
    classification = classify_content(source.descriptor)
    if classification.disposition is not ContentDisposition.REMOTE_DECLARATIVE:
        return None, None, "CONTENT_BOUNDARY_REJECTED"
    if source.descriptor.get("content_type") != expected_type:
        return None, None, "PAYLOAD_FAMILY_MISMATCH"
    attributes = source.descriptor.get("attributes")
    if not isinstance(attributes, Mapping) or attributes.get("level_id") != level_id:
        return None, None, "LEVEL_IDENTITY_MISMATCH"
    validation = validate_remote_payload(source.descriptor, source.payload)
    if not validation.accepted:
        return None, None, validation.reason_code.value
    evidence = ScrubpackPayloadEvidence(
        member_path=member_path,
        payload_sha256=hashlib.sha256(source.payload).hexdigest(),
        byte_length=len(source.payload),
        validation_reason=validation.reason_code.value,
    )
    return source.payload, evidence, "VALIDATED"


def _normalize_level_inputs(levels: Sequence[ScrubpackLevelInput]) -> tuple[ScrubpackLevelInput, ...]:
    if isinstance(levels, (str, bytes, bytearray)) or not isinstance(levels, Sequence):
        raise ScrubpackBuildError("levels must be an explicit sequence")
    level_inputs = tuple(levels)
    if not level_inputs:
        raise ScrubpackBuildError("at least one level is required")
    if any(not isinstance(level, ScrubpackLevelInput) for level in level_inputs):
        raise ScrubpackBuildError("every level must be an explicit ScrubpackLevelInput")
    return level_inputs


def _preflight_levels(
    level_inputs: tuple[ScrubpackLevelInput, ...],
) -> tuple[
    tuple[ScrubpackLevelInput, ...],
    ScrubpackValidationReport,
    list[tuple[str, bytes]],
    list[ScrubpackLevelEvidence],
]:
    ordered_inputs = tuple(sorted(level_inputs, key=lambda level: canonical_level_sort_key(level.level_id)))
    ids = [level.level_id for level in ordered_inputs]
    exact_counts = Counter(ids)
    folded_groups: dict[str, set[str]] = {}
    for level_id in ids:
        folded_groups.setdefault(level_id.casefold(), set()).add(level_id)
    duplicate_codes: dict[str, str] = {}
    for level_id, count in exact_counts.items():
        if count > 1:
            duplicate_codes[level_id] = "DUPLICATE_LEVEL_ID"
    for group in folded_groups.values():
        if len(group) > 1:
            for level_id in group:
                duplicate_codes[level_id] = "CASE_NORMALIZED_LEVEL_ID_COLLISION"
    if duplicate_codes:
        diagnostics = tuple(
            ScrubpackLevelDiagnostic(
                level_id=level_id,
                accepted=False,
                roles=(ScrubpackRoleDiagnostic("membership", False, duplicate_codes[level_id]),),
            )
            for level_id in sorted(duplicate_codes, key=canonical_level_sort_key)
        )
        return ordered_inputs, ScrubpackValidationReport(False, diagnostics), [], []

    members: list[tuple[str, bytes]] = []
    evidence_levels: list[ScrubpackLevelEvidence] = []
    level_diagnostics: list[ScrubpackLevelDiagnostic] = []
    for level_input in ordered_inputs:
        level_spec = ScrubpackLevelV1(level_input.level_id)
        role_diagnostics: list[ScrubpackRoleDiagnostic] = []
        payload_evidence: list[ScrubpackPayloadEvidence] = []
        for role, source, member_path in (
            ("level_data", level_input.level_data, level_spec.level_data_path),
            ("supply_plan", level_input.supply_plan, level_spec.supply_plan_path),
            ("metadata", level_input.metadata, level_spec.metadata_path),
        ):
            payload, evidence, reason_code = _validated_payload(
                level_input.level_id, role, source, member_path
            )
            accepted = reason_code == "VALIDATED"
            role_diagnostics.append(ScrubpackRoleDiagnostic(role, accepted, reason_code))
            if accepted:
                assert payload is not None and evidence is not None
                members.append((member_path, payload))
                payload_evidence.append(evidence)
        level_accepted = all(role.accepted for role in role_diagnostics)
        level_diagnostics.append(
            ScrubpackLevelDiagnostic(level_input.level_id, level_accepted, tuple(role_diagnostics))
        )
        evidence_levels.append(ScrubpackLevelEvidence(level_input.level_id, tuple(payload_evidence)))
    report = ScrubpackValidationReport(
        accepted=all(level.accepted for level in level_diagnostics),
        levels=tuple(level_diagnostics),
    )
    if not report.accepted:
        return ordered_inputs, report, [], []
    return ordered_inputs, report, members, evidence_levels


def validate_scrubpack_levels(levels: Sequence[ScrubpackLevelInput]) -> ScrubpackValidationReport:
    """Validate every explicit level triplet and return deterministic safe diagnostics."""
    level_inputs = _normalize_level_inputs(levels)
    _, report, _, _ = _preflight_levels(level_inputs)
    return report


def _validation_failure_message(report: ScrubpackValidationReport) -> str:
    for level in report.levels:
        for role in level.roles:
            if role.accepted:
                continue
            messages = {
                "DUPLICATE_LEVEL_ID": "duplicate level ID",
                "CASE_NORMALIZED_LEVEL_ID_COLLISION": "case-normalized level ID collision",
                "CONTENT_BOUNDARY_REJECTED": "descriptor rejected",
                "PAYLOAD_FAMILY_MISMATCH": "unsupported payload family",
                "LEVEL_IDENTITY_MISMATCH": "descriptor level identity mismatch",
            }
            detail = messages.get(role.reason_code, role.reason_code)
            return f"pre-pack validation failed: {detail}"
    return "pre-pack validation failed"


def build_scrubpack(
    levels: Sequence[ScrubpackLevelInput],
    *,
    pack_id: str,
    pack_version: int,
    created_at_utc: str | datetime,
) -> ScrubpackBuildResult:
    """Build an in-memory V1 ZIP using explicit immutable identity/time inputs."""
    level_inputs = _normalize_level_inputs(levels)
    level_inputs, validation_report, members, level_evidence = _preflight_levels(level_inputs)
    if not validation_report.accepted:
        raise ScrubpackBuildError(
            _validation_failure_message(validation_report), validation_report=validation_report
        )

    level_specs = tuple(ScrubpackLevelV1(level.level_id) for level in level_inputs)
    try:
        member_names = expected_member_names(level_specs)
    except ScrubpackSpecError as exc:
        raise ScrubpackBuildError(str(exc)) from exc
    if not validate_member_names(member_names):
        raise ScrubpackBuildError("generated archive member layout is invalid")

    member_sha256 = {
        payload.member_path: payload.payload_sha256
        for level in level_evidence
        for payload in level.payloads
    }
    try:
        manifest = ScrubpackManifestV1(
            levels=level_specs,
            pack_id=pack_id,
            pack_version=pack_version,
            created_at_utc=created_at_utc,
            member_sha256=member_sha256,
        )
    except ScrubpackSpecError as exc:
        raise ScrubpackBuildError(str(exc)) from exc

    try:
        manifest_bytes = canonical_json_bytes(manifest.to_dict())
    except ScrubpackSpecError as exc:
        raise ScrubpackBuildError(str(exc)) from exc
    output = io.BytesIO()
    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_STORED,
        compresslevel=None,
        allowZip64=False,
        strict_timestamps=True,
    ) as archive:
        archive.comment = b""
        archive.writestr(_canonical_zip_info(PACK_MANIFEST_PATH), manifest_bytes)
        for member_path, payload in members:
            archive.writestr(_canonical_zip_info(member_path), payload)

    archive_bytes = output.getvalue()
    evidence = ScrubpackBuildEvidence(
        version=SCRUBPACK_VERSION,
        pack_id=manifest.pack_id,
        pack_version=manifest.pack_version,
        created_at_utc=manifest.created_at_utc,
        archive_sha256=hashlib.sha256(archive_bytes).hexdigest(),
        archive_byte_length=len(archive_bytes),
        level_count=len(manifest.levels),
        level_ids=tuple(level.level_id for level in level_inputs),
        member_names=member_names,
        levels=tuple(level_evidence),
        validation_report=validation_report,
    )
    return ScrubpackBuildResult(archive_bytes=archive_bytes, evidence=evidence)


def verify_scrubpack_build(archive_bytes: bytes, evidence: ScrubpackBuildEvidence) -> bool:
    """Verify exact archive bytes, receipt identity, and each manifest member digest."""
    if type(archive_bytes) is not bytes or not isinstance(evidence, ScrubpackBuildEvidence):
        return False
    if len(archive_bytes) != evidence.archive_byte_length:
        return False
    if hashlib.sha256(archive_bytes).hexdigest() != evidence.archive_sha256:
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes), mode="r") as archive:
            names = tuple(archive.namelist())
            if names != evidence.member_names or not validate_member_names(names):
                return False
            manifest = ScrubpackManifestV1.from_dict(json.loads(archive.read(PACK_MANIFEST_PATH)))
            if (
                manifest.pack_id != evidence.pack_id
                or manifest.pack_version != evidence.pack_version
                or manifest.version != evidence.version
                or manifest.created_at_utc != evidence.created_at_utc
                or len(manifest.levels) != evidence.level_count
                or tuple(level.level_id for level in manifest.levels) != evidence.level_ids
                or not evidence.validation_report.accepted
                or tuple(level.level_id for level in evidence.validation_report.levels) != evidence.level_ids
                or any(
                    not level.accepted
                    or tuple((role.role, role.reason_code) for role in level.roles)
                    != (
                        ("level_data", "VALIDATED"),
                        ("supply_plan", "VALIDATED"),
                        ("metadata", "VALIDATED"),
                    )
                    for level in evidence.validation_report.levels
                )
                or archive.testzip() is not None
            ):
                return False
            evidence_member_digests = {
                payload.member_path: payload.payload_sha256
                for level in evidence.levels
                for payload in level.payloads
            }
            if evidence_member_digests != dict(manifest.member_sha256):
                return False
            return all(
                hashlib.sha256(archive.read(path)).hexdigest() == digest
                for path, digest in manifest.member_sha256.items()
            )
    except (OSError, RuntimeError, ValueError, TypeError, KeyError, zipfile.BadZipFile):
        return False


__all__ = [
    "ScrubpackBuildError",
    "ScrubpackBuildEvidence",
    "ScrubpackBuildResult",
    "ScrubpackLevelEvidence",
    "ScrubpackLevelInput",
    "ScrubpackPayloadEvidence",
    "ScrubpackPayloadInput",
    "ScrubpackLevelDiagnostic",
    "ScrubpackRoleDiagnostic",
    "ScrubpackValidationReport",
    "build_scrubpack",
    "validate_scrubpack_levels",
    "verify_scrubpack_build",
]
