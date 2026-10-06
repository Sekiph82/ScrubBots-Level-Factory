"""Provider-neutral staging pack upload gate; it never writes a manifest."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from .candidate_manifest import CandidateManifestBuildResult
from .compatibility import AppContentCompatibilityResult
from .config import Environment
from .manifest_parser import ManifestParseError, parse_content_manifest_v1
from .manifest_validation import validate_manifest_references
from .provider import (
    PROVIDER_CONTRACT_VERSION,
    CapabilityNegotiationResult,
    ProviderCapability,
    ProviderFeature,
    ProviderIdentity,
    ProviderResult,
    ProviderResultCategory,
    negotiate_capabilities,
    validate_provider_capability,
    validate_provider_identity,
)


_REQUIRED_FEATURES = tuple(sorted(
    (ProviderFeature.OBJECT_WRITE, ProviderFeature.INTEGRITY_VERIFY, ProviderFeature.CONDITIONAL_WRITE),
    key=lambda feature: feature.value,
))


class StagingByteWriter(Protocol):
    """Narrow byte-write surface; real provider adapters are outside this milestone."""

    @property
    def identity(self) -> ProviderIdentity: ...

    @property
    def capabilities(self) -> ProviderCapability: ...

    def write_object_bytes(
        self,
        environment: Environment,
        object_key: str,
        content_digest: str,
        content_bytes: bytes,
        *,
        if_absent: bool,
    ) -> ProviderResult: ...

    def verify_object(
        self, environment: Environment, object_key: str, expected_digest: str
    ) -> ProviderResult: ...


class PackUploadReasonCode(StrEnum):
    COMPLETE = "COMPLETE"
    INVALID_CANDIDATE = "INVALID_CANDIDATE"
    INVALID_PROVIDER = "INVALID_PROVIDER"
    CAPABILITY_REJECTED = "CAPABILITY_REJECTED"
    OBJECT_WRITE_FAILED = "OBJECT_WRITE_FAILED"
    OBJECT_INTEGRITY_FAILED = "OBJECT_INTEGRITY_FAILED"


@dataclass(frozen=True, slots=True)
class UploadedPackEvidence:
    sequence: int
    pack_id: str
    object_key: str
    sha256: str
    byte_length: int
    idempotent_existing_object: bool


@dataclass(frozen=True, slots=True)
class StagingPackUploadReport:
    accepted: bool
    manifest_write_authorized: bool
    reason_code: PackUploadReasonCode
    manifest_sha256: str | None
    negotiation: CapabilityNegotiationResult | None
    uploaded_packs: tuple[UploadedPackEvidence, ...]
    failed_object_key: str | None
    object_write_attempted: bool


def _valid_candidate(candidate: object) -> bool:
    if not isinstance(candidate, CandidateManifestBuildResult) or not candidate.publishable:
        return False
    if (
        type(candidate.manifest_bytes) is not bytes
        or hashlib.sha256(candidate.manifest_bytes).hexdigest() != candidate.manifest_sha256
        or not candidate.strict_round_trip_valid
        or not candidate.compatibility.compatible
        or (candidate.successor is not None and not candidate.successor.accepted)
    ):
        return False
    try:
        parsed = parse_content_manifest_v1(candidate.manifest_bytes)
    except ManifestParseError:
        return False
    if parsed != candidate.manifest or parsed.to_json_bytes() != candidate.manifest_bytes:
        return False
    references = validate_manifest_references(parsed, candidate.pack_builds)
    if not references.eligible:
        return False
    if len(parsed.packs) != len(candidate.pack_builds) or not candidate.pack_builds:
        return False
    builds = {build.evidence.pack_id: build for build in candidate.pack_builds}
    if len(builds) != len(candidate.pack_builds):
        return False
    for pack in parsed.packs:
        build = builds.get(pack.pack_id)
        if (
            build is None
            or hashlib.sha256(build.archive_bytes).hexdigest() != pack.sha256
            or len(build.archive_bytes) != pack.byte_length
            or build.evidence.pack_version != pack.pack_version
        ):
            return False
    return True


def upload_candidate_packs_to_staging(
    candidate: object, provider: StagingByteWriter
) -> StagingPackUploadReport:
    """Conditionally upload each pack and authorize the next manifest step only after verification.

    The provider is called only for exact pack bytes. This function has no
    manifest-write method and does not target production or delete objects.
    """
    if not _valid_candidate(candidate):
        return StagingPackUploadReport(
            False, False, PackUploadReasonCode.INVALID_CANDIDATE, None, None, (), None, False
        )

    identity = getattr(provider, "identity", None)
    capability = getattr(provider, "capabilities", None)
    if not validate_provider_identity(identity) or not validate_provider_capability(capability):
        return StagingPackUploadReport(
            False, False, PackUploadReasonCode.INVALID_PROVIDER,
            candidate.manifest_sha256, None, (), None, False,
        )
    negotiation = negotiate_capabilities(capability, Environment.STAGING, _REQUIRED_FEATURES)
    if not negotiation.accepted:
        return StagingPackUploadReport(
            False, False, PackUploadReasonCode.CAPABILITY_REJECTED,
            candidate.manifest_sha256, negotiation, (), None, False,
        )

    builds = {build.evidence.pack_id: build for build in candidate.pack_builds}
    uploaded: list[UploadedPackEvidence] = []
    attempted = False
    for sequence, pack in enumerate(sorted(candidate.manifest.packs, key=lambda item: item.pack_id.encode("ascii")), start=1):
        build = builds[pack.pack_id]
        raw = build.archive_bytes
        digest = pack.sha256
        attempted = True
        try:
            write_result = provider.write_object_bytes(
                Environment.STAGING, pack.object_key, digest, raw, if_absent=True
            )
        except Exception:
            return StagingPackUploadReport(
                False, False, PackUploadReasonCode.OBJECT_WRITE_FAILED,
                candidate.manifest_sha256, negotiation, tuple(uploaded), pack.object_key, attempted,
            )
        if not _valid_provider_result(write_result, identity):
            return StagingPackUploadReport(
                False, False, PackUploadReasonCode.OBJECT_WRITE_FAILED,
                candidate.manifest_sha256, negotiation, tuple(uploaded), pack.object_key, attempted,
            )

        idempotent = write_result.category is ProviderResultCategory.CONFLICT_STALE_PRECONDITION
        if write_result.category not in {
            ProviderResultCategory.SUCCESS, ProviderResultCategory.CONFLICT_STALE_PRECONDITION
        }:
            return StagingPackUploadReport(
                False, False, PackUploadReasonCode.OBJECT_WRITE_FAILED,
                candidate.manifest_sha256, negotiation, tuple(uploaded), pack.object_key, attempted,
            )
        if write_result.category is ProviderResultCategory.SUCCESS and (
            write_result.content_digest is not None and write_result.content_digest != digest
        ):
            return StagingPackUploadReport(
                False, False, PackUploadReasonCode.OBJECT_INTEGRITY_FAILED,
                candidate.manifest_sha256, negotiation, tuple(uploaded), pack.object_key, attempted,
            )
        try:
            verify_result = provider.verify_object(Environment.STAGING, pack.object_key, digest)
        except Exception:
            verify_result = None
        if not _valid_provider_result(verify_result, identity) or (
            verify_result.category is not ProviderResultCategory.SUCCESS
            or verify_result.content_digest != digest
        ):
            reason = (
                PackUploadReasonCode.OBJECT_INTEGRITY_FAILED
                if verify_result is not None and verify_result.category is ProviderResultCategory.SUCCESS
                else PackUploadReasonCode.OBJECT_WRITE_FAILED
            )
            return StagingPackUploadReport(
                False, False, reason, candidate.manifest_sha256,
                negotiation, tuple(uploaded), pack.object_key, attempted,
            )
        uploaded.append(UploadedPackEvidence(
            sequence, pack.pack_id, pack.object_key, digest, len(raw), idempotent
        ))

    return StagingPackUploadReport(
        True, True, PackUploadReasonCode.COMPLETE, candidate.manifest_sha256,
        negotiation, tuple(uploaded), None, attempted,
    )


def _valid_provider_result(result: object, identity: ProviderIdentity) -> bool:
    return (
        isinstance(result, ProviderResult)
        and result.result_version == PROVIDER_CONTRACT_VERSION
        and result.provider_id == identity.provider_id
        and result.environment is Environment.STAGING
        and isinstance(result.category, ProviderResultCategory)
        and (
            result.content_digest is None
            or (isinstance(result.content_digest, str) and re.fullmatch(r"[a-f0-9]{64}", result.content_digest))
        )
    )


__all__ = [
    "PackUploadReasonCode",
    "StagingByteWriter",
    "StagingPackUploadReport",
    "UploadedPackEvidence",
    "upload_candidate_packs_to_staging",
]
