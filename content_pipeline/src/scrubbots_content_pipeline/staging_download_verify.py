"""Read back and verify exact staged manifest and pack bytes."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from .candidate_manifest import CandidateManifestBuildResult
from .config import Environment
from .manifest_parser import ManifestParseError, parse_content_manifest_v1
from .manifest_validation import validate_manifest_references
from .provider import (
    PROVIDER_CONTRACT_VERSION,
    CapabilityNegotiationResult,
    ProviderCapability,
    ProviderFeature,
    ProviderIdentity,
    ProviderObjectBytesResult,
    ProviderResultCategory,
    negotiate_capabilities,
    validate_provider_capability,
    validate_provider_identity,
)
from .scrubpack_inspection import inspect_scrubpack
from .secret_refs import _contains_obvious_secret
from .staging_manifest_publish import (
    STAGING_MANIFEST_PUBLISH_VERSION,
    StagingManifestPackDigest,
    StagingManifestReceipt,
    serialize_staging_manifest_receipt,
)


STAGING_DOWNLOAD_VERIFY_VERSION = "1.0"
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SAFE_OBJECT_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,511}$")
_REQUIRED_FEATURES = (ProviderFeature.INTEGRITY_VERIFY,)


class StagingManifestReader(Protocol):
    """Read-only provider-neutral interface for exact STAGING object bytes."""

    @property
    def identity(self) -> ProviderIdentity: ...

    @property
    def capabilities(self) -> ProviderCapability: ...

    def read_object_bytes(
        self, environment: Environment, object_key: str
    ) -> ProviderObjectBytesResult: ...


@dataclass(frozen=True, slots=True)
class StagingDownloadedPackEvidence:
    pack_id: str
    object_key: str
    sha256: str
    byte_length: int
    level_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "pack_id": self.pack_id,
            "object_key": self.object_key,
            "sha256": self.sha256,
            "byte_length": self.byte_length,
            "level_ids": list(self.level_ids),
        }


@dataclass(frozen=True, slots=True)
class StagingDownloadVerificationReceipt:
    schema_version: str
    manifest_bytes: bytes
    manifest_sha256: str
    manifest_byte_length: int
    content_version: int
    manifest_object_key: str
    target_environment: str
    target_id: str
    provider_id: str
    provider_version: str
    provider_contract_version: str
    capability_id: str
    capability_version: str
    minimum_game_version: str
    disabled_levels: tuple[str, ...]
    schedules: tuple[object, ...]
    packs: tuple[StagingDownloadedPackEvidence, ...]
    release_event_digests: tuple[str, ...]
    reference_check_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "manifest_bytes_base64": base64.b64encode(self.manifest_bytes).decode("ascii"),
            "manifest_sha256": self.manifest_sha256,
            "manifest_byte_length": self.manifest_byte_length,
            "content_version": self.content_version,
            "manifest_object_key": self.manifest_object_key,
            "target": {"environment": self.target_environment, "target_id": self.target_id},
            "provider": {
                "provider_id": self.provider_id,
                "provider_version": self.provider_version,
                "contract_version": self.provider_contract_version,
            },
            "capability": {"capability_id": self.capability_id, "capability_version": self.capability_version},
            "manifest_fields": {
                "minimum_game_version": self.minimum_game_version,
                "disabled_levels": list(self.disabled_levels),
                "schedules": [item.to_dict() for item in self.schedules],
            },
            "packs": [item.to_dict() for item in self.packs],
            "release_event_digests": list(self.release_event_digests),
            "reference_check_ids": list(self.reference_check_ids),
        }


class StagingDownloadReasonCode(StrEnum):
    VERIFIED = "VERIFIED"
    INVALID_CANDIDATE = "INVALID_CANDIDATE"
    INVALID_STAGING_RECEIPT = "INVALID_STAGING_RECEIPT"
    INVALID_PROVIDER = "INVALID_PROVIDER"
    CAPABILITY_REJECTED = "CAPABILITY_REJECTED"
    MANIFEST_READ_FAILED = "MANIFEST_READ_FAILED"
    MANIFEST_INTEGRITY_FAILED = "MANIFEST_INTEGRITY_FAILED"
    MANIFEST_PARSE_FAILED = "MANIFEST_PARSE_FAILED"
    CANDIDATE_MISMATCH = "CANDIDATE_MISMATCH"
    PACK_READ_FAILED = "PACK_READ_FAILED"
    PACK_INTEGRITY_FAILED = "PACK_INTEGRITY_FAILED"
    PACK_INVALID = "PACK_INVALID"
    REFERENCE_VALIDATION_FAILED = "REFERENCE_VALIDATION_FAILED"


@dataclass(frozen=True, slots=True)
class StagingDownloadVerificationReport:
    accepted: bool
    reason_code: StagingDownloadReasonCode
    receipt: StagingDownloadVerificationReceipt | None
    capability_negotiation: CapabilityNegotiationResult | None
    manifest_read: bool
    downloaded_pack_ids: tuple[str, ...]


def verify_staged_manifest_download(
    *,
    candidate: object,
    staging_receipt: object,
    provider: StagingManifestReader,
) -> StagingDownloadVerificationReport:
    """Download and independently verify the manifest and every referenced STAGING pack."""
    if not _valid_candidate(candidate):
        return _failure(StagingDownloadReasonCode.INVALID_CANDIDATE)
    assert isinstance(candidate, CandidateManifestBuildResult)
    if not _valid_staging_receipt(staging_receipt, candidate):
        return _failure(StagingDownloadReasonCode.INVALID_STAGING_RECEIPT)
    assert isinstance(staging_receipt, StagingManifestReceipt)

    try:
        identity = getattr(provider, "identity", None)
        capability = getattr(provider, "capabilities", None)
    except Exception:
        return _failure(StagingDownloadReasonCode.INVALID_PROVIDER)
    if not validate_provider_identity(identity) or not validate_provider_capability(capability):
        return _failure(StagingDownloadReasonCode.INVALID_PROVIDER)
    if (
        identity.provider_id != staging_receipt.provider_id
        or identity.provider_version != staging_receipt.provider_version
        or identity.contract_version != staging_receipt.provider_contract_version
    ):
        return _failure(StagingDownloadReasonCode.INVALID_PROVIDER)
    negotiation = negotiate_capabilities(capability, Environment.STAGING, _REQUIRED_FEATURES)
    if not negotiation.accepted:
        return _failure(StagingDownloadReasonCode.CAPABILITY_REJECTED, negotiation)

    try:
        manifest_result = provider.read_object_bytes(Environment.STAGING, staging_receipt.manifest_object_key)
    except Exception:
        return _failure(StagingDownloadReasonCode.MANIFEST_READ_FAILED, negotiation)
    if not _valid_bytes_result(manifest_result, identity, staging_receipt.manifest_object_key):
        return _failure(StagingDownloadReasonCode.MANIFEST_READ_FAILED, negotiation)
    manifest_bytes = manifest_result.content_bytes
    assert type(manifest_bytes) is bytes
    if (
        len(manifest_bytes) != len(staging_receipt.manifest_bytes)
        or hashlib.sha256(manifest_bytes).hexdigest() != staging_receipt.manifest_sha256
        or manifest_bytes != staging_receipt.manifest_bytes
    ):
        return _failure(StagingDownloadReasonCode.MANIFEST_INTEGRITY_FAILED, negotiation, True)
    try:
        manifest = parse_content_manifest_v1(manifest_bytes)
    except ManifestParseError:
        return _failure(StagingDownloadReasonCode.MANIFEST_PARSE_FAILED, negotiation, True)
    if (
        manifest.to_json_bytes() != manifest_bytes
        or manifest != candidate.manifest
        or manifest_bytes != candidate.manifest_bytes
        or manifest.content_version != staging_receipt.content_version
    ):
        return _failure(StagingDownloadReasonCode.CANDIDATE_MISMATCH, negotiation, True)

    candidate_builds = {build.evidence.pack_id: build for build in candidate.pack_builds}
    staged_pack_rows = tuple(sorted(staging_receipt.referenced_pack_digests, key=lambda item: item.pack_id.encode("ascii")))
    manifest_packs = tuple(sorted(manifest.packs, key=lambda item: item.pack_id.encode("ascii")))
    if len(staged_pack_rows) != len(manifest_packs) or any(
        not isinstance(receipt_pack, StagingManifestPackDigest)
        or (receipt_pack.pack_id, receipt_pack.object_key, receipt_pack.sha256, receipt_pack.byte_length)
        != (pack.pack_id, pack.object_key, pack.sha256, pack.byte_length)
        for receipt_pack, pack in zip(staged_pack_rows, manifest_packs)
    ):
        return _failure(StagingDownloadReasonCode.INVALID_STAGING_RECEIPT, negotiation, True)

    downloaded_packs: list[StagingDownloadedPackEvidence] = []
    downloaded_ids: list[str] = []
    for pack in manifest_packs:
        try:
            pack_result = provider.read_object_bytes(Environment.STAGING, pack.object_key)
        except Exception:
            return _failure(StagingDownloadReasonCode.PACK_READ_FAILED, negotiation, True, tuple(downloaded_ids))
        if not _valid_bytes_result(pack_result, identity, pack.object_key):
            return _failure(StagingDownloadReasonCode.PACK_READ_FAILED, negotiation, True, tuple(downloaded_ids))
        pack_bytes = pack_result.content_bytes
        assert type(pack_bytes) is bytes
        build = candidate_builds.get(pack.pack_id)
        if (
            build is None
            or len(pack_bytes) != pack.byte_length
            or hashlib.sha256(pack_bytes).hexdigest() != pack.sha256
            or pack_bytes != build.archive_bytes
        ):
            return _failure(StagingDownloadReasonCode.PACK_INTEGRITY_FAILED, negotiation, True, tuple(downloaded_ids))
        inspection = inspect_scrubpack(pack_bytes)
        if not (
            inspection.accepted
            and inspection.pack_id == pack.pack_id == build.evidence.pack_id
            and inspection.pack_version == pack.pack_version == build.evidence.pack_version
            and inspection.level_ids == build.evidence.level_ids
            and inspection.archive_sha256 == pack.sha256
        ):
            return _failure(StagingDownloadReasonCode.PACK_INVALID, negotiation, True, tuple(downloaded_ids))
        downloaded_ids.append(pack.pack_id)
        downloaded_packs.append(StagingDownloadedPackEvidence(
            pack.pack_id, pack.object_key, hashlib.sha256(pack_bytes).hexdigest(), len(pack_bytes), inspection.level_ids
        ))

    # CP02-009 validates the exact downloaded archives because each was proven byte-identical
    # to the immutable M12 candidate archive whose evidence is passed to this gate.
    references = validate_manifest_references(manifest, candidate.pack_builds)
    if not references.eligible:
        return _failure(StagingDownloadReasonCode.REFERENCE_VALIDATION_FAILED, negotiation, True, tuple(downloaded_ids))
    receipt = StagingDownloadVerificationReceipt(
        STAGING_DOWNLOAD_VERIFY_VERSION,
        manifest_bytes,
        hashlib.sha256(manifest_bytes).hexdigest(),
        len(manifest_bytes),
        manifest.content_version,
        staging_receipt.manifest_object_key,
        Environment.STAGING.value,
        staging_receipt.target_id,
        identity.provider_id,
        identity.provider_version,
        identity.contract_version,
        capability.capability_id,
        capability.capability_version,
        manifest.minimum_game_version,
        manifest.disabled_levels,
        manifest.schedules,
        tuple(downloaded_packs),
        staging_receipt.release_event_digests,
        tuple(check.check_id for check in references.checks),
    )
    return StagingDownloadVerificationReport(
        True, StagingDownloadReasonCode.VERIFIED, receipt, negotiation, True, tuple(downloaded_ids)
    )


def serialize_staging_download_verification_receipt(receipt: StagingDownloadVerificationReceipt) -> str:
    if not _valid_download_receipt(receipt):
        raise ValueError("invalid STAGING download verification receipt")
    return json.dumps(receipt.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def _valid_candidate(candidate: object) -> bool:
    if not isinstance(candidate, CandidateManifestBuildResult):
        return False
    try:
        if (
            candidate.publishable is not True
            or type(candidate.manifest_bytes) is not bytes
            or not isinstance(candidate.manifest_sha256, str)
            or hashlib.sha256(candidate.manifest_bytes).hexdigest() != candidate.manifest_sha256
            or candidate.strict_round_trip_valid is not True
            or candidate.references.eligible is not True
            or candidate.compatibility.compatible is not True
        ):
            return False
        parsed = parse_content_manifest_v1(candidate.manifest_bytes)
        return (
            parsed == candidate.manifest
            and parsed.to_json_bytes() == candidate.manifest_bytes
            and validate_manifest_references(parsed, candidate.pack_builds).eligible is True
        )
    except (AttributeError, ManifestParseError, TypeError, ValueError):
        return False


def _valid_staging_receipt(receipt: object, candidate: CandidateManifestBuildResult) -> bool:
    if not isinstance(receipt, StagingManifestReceipt):
        return False
    try:
        serialize_staging_manifest_receipt(receipt)
    except (AttributeError, TypeError, ValueError):
        return False
    return (
        receipt.schema_version == STAGING_MANIFEST_PUBLISH_VERSION
        and receipt.target_environment == Environment.STAGING.value
        and isinstance(receipt.target_id, str) and bool(_SAFE_ID.fullmatch(receipt.target_id))
        and receipt.manifest_bytes == candidate.manifest_bytes
        and receipt.manifest_sha256 == candidate.manifest_sha256
        and receipt.content_version == candidate.manifest.content_version
    )


def _valid_bytes_result(result: object, identity: ProviderIdentity, object_key: str) -> bool:
    return (
        isinstance(result, ProviderObjectBytesResult)
        and result.result_version == PROVIDER_CONTRACT_VERSION
        and result.category is ProviderResultCategory.SUCCESS
        and result.provider_id == identity.provider_id
        and result.environment is Environment.STAGING
        and result.object_key == object_key
        and type(result.content_bytes) is bytes
    )


def _valid_download_receipt(receipt: object) -> bool:
    if not isinstance(receipt, StagingDownloadVerificationReceipt) or receipt.schema_version != STAGING_DOWNLOAD_VERIFY_VERSION:
        return False
    if (
        type(receipt.manifest_bytes) is not bytes
        or not isinstance(receipt.manifest_sha256, str)
        or not _SHA256.fullmatch(receipt.manifest_sha256)
        or hashlib.sha256(receipt.manifest_bytes).hexdigest() != receipt.manifest_sha256
        or type(receipt.manifest_byte_length) is not int
        or receipt.manifest_byte_length != len(receipt.manifest_bytes)
        or type(receipt.content_version) is not int or receipt.content_version < 1
        or not _safe_object_key(receipt.manifest_object_key)
        or receipt.target_environment != Environment.STAGING.value
        or not _safe_id(receipt.target_id)
        or not _safe_id(receipt.provider_id)
        or not _safe_id(receipt.provider_version)
        or receipt.provider_contract_version != PROVIDER_CONTRACT_VERSION
        or not _safe_id(receipt.capability_id)
        or not _safe_id(receipt.capability_version)
    ):
        return False
    try:
        manifest = parse_content_manifest_v1(receipt.manifest_bytes)
    except ManifestParseError:
        return False
    if (
        manifest.to_json_bytes() != receipt.manifest_bytes
        or manifest.content_version != receipt.content_version
        or manifest.minimum_game_version != receipt.minimum_game_version
        or manifest.disabled_levels != receipt.disabled_levels
        or manifest.schedules != receipt.schedules
    ):
        return False
    packs = receipt.packs
    expected = tuple(sorted(manifest.packs, key=lambda item: item.pack_id.encode("ascii")))
    if not isinstance(packs, tuple) or len(packs) != len(expected):
        return False
    if any(
        not isinstance(actual, StagingDownloadedPackEvidence)
        or (actual.pack_id, actual.object_key, actual.sha256, actual.byte_length)
        != (pack.pack_id, pack.object_key, pack.sha256, pack.byte_length)
        or actual.level_ids != tuple(level.level_id for level in manifest.levels if level.pack_id == pack.pack_id)
        for actual, pack in zip(packs, expected)
    ):
        return False
    return (
        isinstance(receipt.release_event_digests, tuple)
        and bool(receipt.release_event_digests)
        and all(isinstance(item, str) and _SHA256.fullmatch(item) for item in receipt.release_event_digests)
        and isinstance(receipt.reference_check_ids, tuple)
        and bool(receipt.reference_check_ids)
        and len(set(receipt.reference_check_ids)) == len(receipt.reference_check_ids)
        and all(isinstance(item, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,63}", item) for item in receipt.reference_check_ids)
    )


def _safe_id(value: object) -> bool:
    return isinstance(value, str) and bool(_SAFE_ID.fullmatch(value))


def _safe_object_key(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(_SAFE_OBJECT_KEY.fullmatch(value))
        and not _contains_obvious_secret(value)
        and not any(part in {"", ".", ".."} for part in value.split("/"))
    )


def _failure(
    reason: StagingDownloadReasonCode,
    negotiation: CapabilityNegotiationResult | None = None,
    manifest_read: bool = False,
    downloaded_pack_ids: tuple[str, ...] = (),
) -> StagingDownloadVerificationReport:
    return StagingDownloadVerificationReport(False, reason, None, negotiation, manifest_read, downloaded_pack_ids)


__all__ = [
    "STAGING_DOWNLOAD_VERIFY_VERSION",
    "StagingDownloadedPackEvidence",
    "StagingDownloadReasonCode",
    "StagingDownloadVerificationReceipt",
    "StagingDownloadVerificationReport",
    "StagingManifestReader",
    "serialize_staging_download_verification_receipt",
    "verify_staged_manifest_download",
]
