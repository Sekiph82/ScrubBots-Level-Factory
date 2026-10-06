"""Conditional STAGING manifest publication after M14 pack-integrity gates."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from .candidate_manifest import CandidateManifestBuildResult
from .config import Environment, EnvironmentTarget, validate_target_binding
from .manifest_parser import ManifestParseError, parse_content_manifest_v1
from .manifest_validation import validate_manifest_references
from .manifest_v1 import check_manifest_successor
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
from .publisher_validation import PublisherValidationCheck, PublisherValidationReport
from .release_state import (
    RELEASE_STATE_VERSION,
    ReleaseEvent,
    ReleaseState,
    make_release_event,
    replay_release_events,
)
from .secret_refs import _contains_obvious_secret
from .staging_pack_upload import (
    PackUploadReasonCode,
    StagingPackUploadReport,
    UploadedPackEvidence,
)


STAGING_MANIFEST_PUBLISH_VERSION = "1.0"
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_SAFE_OBJECT_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,511}$")
_REQUIRED_FEATURES = tuple(sorted((
    ProviderFeature.STAGING_PUBLISH,
    ProviderFeature.OBJECT_WRITE,
    ProviderFeature.INTEGRITY_VERIFY,
    ProviderFeature.CONDITIONAL_WRITE,
), key=lambda item: item.value))


class StagingManifestWriter(Protocol):
    """Narrow provider-neutral write surface for one conditional STAGING manifest."""

    @property
    def identity(self) -> ProviderIdentity: ...

    @property
    def capabilities(self) -> ProviderCapability: ...

    def write_manifest_conditionally(
        self,
        environment: Environment,
        target_id: str,
        object_key: str,
        content_digest: str,
        content_bytes: bytes,
        *,
        expected_prior_sha256: str | None,
    ) -> ProviderResult: ...


@dataclass(frozen=True, slots=True)
class StagingManifestPrecondition:
    """Exact target/object identity and observed prior manifest state for CAS."""

    target_id: str
    object_key: str
    expected_present: bool
    expected_prior_sha256: str | None
    expected_prior_content_version: int | None
    expected_prior_manifest_bytes: bytes | None


@dataclass(frozen=True, slots=True)
class StagingManifestPackDigest:
    pack_id: str
    object_key: str
    sha256: str
    byte_length: int

    def to_dict(self) -> dict[str, object]:
        return {
            "pack_id": self.pack_id,
            "object_key": self.object_key,
            "sha256": self.sha256,
            "byte_length": self.byte_length,
        }


@dataclass(frozen=True, slots=True)
class StagingManifestReceipt:
    """Immutable builder evidence for one conditionally written STAGING manifest."""

    schema_version: str
    manifest_bytes: bytes
    manifest_sha256: str
    content_version: int
    manifest_object_key: str
    referenced_pack_digests: tuple[StagingManifestPackDigest, ...]
    provider_id: str
    provider_version: str
    provider_contract_version: str
    capability_id: str
    capability_version: str
    target_environment: str
    target_id: str
    expected_prior_manifest_sha256: str | None
    expected_prior_content_version: int | None
    release_event_digests: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "manifest_bytes_base64": base64.b64encode(self.manifest_bytes).decode("ascii"),
            "manifest_sha256": self.manifest_sha256,
            "content_version": self.content_version,
            "manifest_object_key": self.manifest_object_key,
            "referenced_pack_digests": [item.to_dict() for item in self.referenced_pack_digests],
            "provider": {
                "provider_id": self.provider_id,
                "provider_version": self.provider_version,
                "contract_version": self.provider_contract_version,
            },
            "capability": {
                "capability_id": self.capability_id,
                "capability_version": self.capability_version,
            },
            "target": {"environment": self.target_environment, "target_id": self.target_id},
            "expected_prior_manifest_sha256": self.expected_prior_manifest_sha256,
            "expected_prior_content_version": self.expected_prior_content_version,
            "release_event_digests": list(self.release_event_digests),
        }


class StagingManifestReasonCode(StrEnum):
    STAGED = "STAGED"
    INVALID_CANDIDATE = "INVALID_CANDIDATE"
    VALIDATION_REJECTED = "VALIDATION_REJECTED"
    PACKS_NOT_VERIFIED = "PACKS_NOT_VERIFIED"
    INVALID_TARGET = "INVALID_TARGET"
    INVALID_PRECONDITION = "INVALID_PRECONDITION"
    CONTENT_VERSION_NOT_INCREASED = "CONTENT_VERSION_NOT_INCREASED"
    INVALID_PROVIDER = "INVALID_PROVIDER"
    CAPABILITY_REJECTED = "CAPABILITY_REJECTED"
    INVALID_RELEASE_HISTORY = "INVALID_RELEASE_HISTORY"
    STALE_PRECONDITION = "STALE_PRECONDITION"
    MANIFEST_WRITE_FAILED = "MANIFEST_WRITE_FAILED"


@dataclass(frozen=True, slots=True)
class StagingManifestPublishReport:
    accepted: bool
    reason_code: StagingManifestReasonCode
    receipt: StagingManifestReceipt | None
    appended_release_events: tuple[ReleaseEvent, ...]
    capability_negotiation: CapabilityNegotiationResult | None
    manifest_write_attempted: bool
    references_revalidated: bool


def serialize_staging_manifest_receipt(receipt: StagingManifestReceipt) -> str:
    if not _valid_receipt(receipt):
        raise ValueError("invalid STAGING manifest receipt")
    return json.dumps(receipt.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def publish_candidate_manifest_to_staging(
    *,
    candidate: object,
    validation_report: object,
    pack_upload_report: object,
    target: object,
    precondition: object,
    release_events: object,
    provider: StagingManifestWriter,
) -> StagingManifestPublishReport:
    """Write only a validated candidate manifest to STAGING under an explicit CAS guard."""
    if not _valid_candidate(candidate):
        return _failure(StagingManifestReasonCode.INVALID_CANDIDATE)
    assert isinstance(candidate, CandidateManifestBuildResult)

    if not _valid_validation_report(validation_report, candidate, target):
        return _failure(StagingManifestReasonCode.VALIDATION_REJECTED)
    if not _valid_pack_upload_report(pack_upload_report, candidate):
        return _failure(StagingManifestReasonCode.PACKS_NOT_VERIFIED)
    if (
        not isinstance(target, EnvironmentTarget)
        or target.environment is not Environment.STAGING
        or not validate_target_binding(Environment.STAGING, target).accepted
        or any(
            not _safe_identifier(value)
            for value in (target.logical_target_id, target.state_namespace, target.content_namespace)
        )
    ):
        return _failure(StagingManifestReasonCode.INVALID_TARGET)
    if not _valid_precondition(precondition, target, candidate):
        return _failure(StagingManifestReasonCode.INVALID_PRECONDITION)
    assert isinstance(precondition, StagingManifestPrecondition)
    if precondition.expected_present and not check_manifest_successor(
        precondition.expected_prior_content_version, candidate.manifest.to_dict()
    ).accepted:
        return _failure(StagingManifestReasonCode.CONTENT_VERSION_NOT_INCREASED)

    identity = getattr(provider, "identity", None)
    capability = getattr(provider, "capabilities", None)
    if not validate_provider_identity(identity) or not validate_provider_capability(capability):
        return _failure(StagingManifestReasonCode.INVALID_PROVIDER)
    negotiation = negotiate_capabilities(capability, Environment.STAGING, _REQUIRED_FEATURES)
    if not negotiation.accepted:
        return _failure(StagingManifestReasonCode.CAPABILITY_REJECTED, negotiation)

    history = _validated_history(release_events, candidate)
    if history is None:
        return _failure(StagingManifestReasonCode.INVALID_RELEASE_HISTORY, negotiation)
    assert isinstance(release_events, tuple)
    appended_before_write, staged_event = history

    # Recheck exact M13 references at the mutation boundary, after all other gates.
    references = validate_manifest_references(candidate.manifest, candidate.pack_builds)
    if not references.eligible:
        return _failure(StagingManifestReasonCode.INVALID_CANDIDATE, negotiation)

    try:
        result = provider.write_manifest_conditionally(
            Environment.STAGING,
            target.logical_target_id,
            precondition.object_key,
            candidate.manifest_sha256,
            candidate.manifest_bytes,
            expected_prior_sha256=precondition.expected_prior_sha256,
        )
    except Exception:
        return _write_failure(
            StagingManifestReasonCode.MANIFEST_WRITE_FAILED, negotiation,
            release_events, appended_before_write, candidate,
        )

    if (
        not _valid_write_result(result, identity)
        or result.category is not ProviderResultCategory.SUCCESS
        or result.content_digest != candidate.manifest_sha256
    ):
        reason = (
            StagingManifestReasonCode.STALE_PRECONDITION
            if isinstance(result, ProviderResult)
            and result.result_version == PROVIDER_CONTRACT_VERSION
            and result.provider_id == identity.provider_id
            and result.environment is Environment.STAGING
            and result.category is ProviderResultCategory.CONFLICT_STALE_PRECONDITION
            else StagingManifestReasonCode.MANIFEST_WRITE_FAILED
        )
        return _write_failure(reason, negotiation, release_events, appended_before_write, candidate)

    appended = (*appended_before_write, staged_event)
    receipt = StagingManifestReceipt(
        STAGING_MANIFEST_PUBLISH_VERSION,
        candidate.manifest_bytes,
        candidate.manifest_sha256,
        candidate.manifest.content_version,
        precondition.object_key,
        tuple(StagingManifestPackDigest(item.pack_id, item.object_key, item.sha256, item.byte_length)
              for item in sorted(candidate.manifest.packs, key=lambda pack: pack.pack_id.encode("ascii"))),
        identity.provider_id,
        identity.provider_version,
        identity.contract_version,
        capability.capability_id,
        capability.capability_version,
        Environment.STAGING.value,
        target.logical_target_id,
        precondition.expected_prior_sha256,
        precondition.expected_prior_content_version,
        tuple(event.event_digest for event in appended),
    )
    return StagingManifestPublishReport(
        True, StagingManifestReasonCode.STAGED, receipt, appended, negotiation, True, True
    )


def _valid_candidate(candidate: object) -> bool:
    if not isinstance(candidate, CandidateManifestBuildResult) or candidate.publishable is not True:
        return False
    if type(candidate.manifest_bytes) is not bytes or type(candidate.manifest_sha256) is not str:
        return False
    if hashlib.sha256(candidate.manifest_bytes).hexdigest() != candidate.manifest_sha256:
        return False
    try:
        parsed = parse_content_manifest_v1(candidate.manifest_bytes)
    except ManifestParseError:
        return False
    return (
        parsed == candidate.manifest
        and parsed.to_json_bytes() == candidate.manifest_bytes
        and candidate.strict_round_trip_valid is True
        and validate_manifest_references(parsed, candidate.pack_builds).eligible
        and bool(parsed.packs)
    )


def _valid_validation_report(report: object, candidate: CandidateManifestBuildResult, target: object) -> bool:
    return (
        isinstance(report, PublisherValidationReport)
        and report.schema_version == "1.0"
        and report.accepted is True
        and report.remote_mutation_performed is False
        and report.manifest_sha256 == candidate.manifest_sha256
        and report.content_version == candidate.manifest.content_version
        and report.target_environment == Environment.STAGING.value
        and isinstance(target, EnvironmentTarget)
        and report.target_id == target.logical_target_id
        and isinstance(report.checks, tuple)
        and bool(report.checks)
        and len({check.check_id for check in report.checks if isinstance(check, PublisherValidationCheck)}) == len(report.checks)
        and all(
            isinstance(check, PublisherValidationCheck)
            and type(check.accepted) is bool and check.accepted is True
            and isinstance(check.check_id, str) and bool(check.check_id)
            and isinstance(check.reason_code, str) and bool(re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", check.reason_code))
            for check in report.checks
        )
    )


def _valid_pack_upload_report(report: object, candidate: CandidateManifestBuildResult) -> bool:
    if not (
        isinstance(report, StagingPackUploadReport)
        and report.accepted is True
        and report.manifest_write_authorized is True
        and report.reason_code is PackUploadReasonCode.COMPLETE
        and report.manifest_sha256 == candidate.manifest_sha256
        and report.failed_object_key is None
        and report.object_write_attempted is True
        and isinstance(report.uploaded_packs, tuple)
        and report.negotiation is not None
        and report.negotiation.negotiation_version == PROVIDER_CONTRACT_VERSION
        and report.negotiation.accepted is True
        and report.negotiation.environment == Environment.STAGING.value
        and report.negotiation.required_features == tuple(
            sorted((ProviderFeature.OBJECT_WRITE.value, ProviderFeature.INTEGRITY_VERIFY.value,
                    ProviderFeature.CONDITIONAL_WRITE.value))
        )
        and report.negotiation.missing_features == ()
        and report.negotiation.result_category is ProviderResultCategory.SUCCESS
    ):
        return False
    expected_packs = sorted(candidate.manifest.packs, key=lambda pack: pack.pack_id.encode("ascii"))
    if len(report.uploaded_packs) != len(expected_packs):
        return False
    for sequence, (evidence, pack) in enumerate(zip(report.uploaded_packs, expected_packs), start=1):
        if not (
            isinstance(evidence, UploadedPackEvidence)
            and evidence.sequence == sequence
            and evidence.pack_id == pack.pack_id
            and evidence.object_key == pack.object_key
            and evidence.sha256 == pack.sha256
            and evidence.byte_length == pack.byte_length
            and type(evidence.idempotent_existing_object) is bool
        ):
            return False
    return True


def _valid_precondition(
    precondition: object, target: EnvironmentTarget, candidate: CandidateManifestBuildResult
) -> bool:
    if not isinstance(precondition, StagingManifestPrecondition):
        return False
    if (
        precondition.target_id != target.logical_target_id
        or not _safe_object_key(precondition.object_key)
        or type(precondition.expected_present) is not bool
    ):
        return False
    if not precondition.expected_present:
        return (
            precondition.expected_prior_sha256 is None
            and precondition.expected_prior_content_version is None
            and precondition.expected_prior_manifest_bytes is None
        )
    if (
        not isinstance(precondition.expected_prior_sha256, str)
        or not _SHA256.fullmatch(precondition.expected_prior_sha256)
        or type(precondition.expected_prior_content_version) is not int
        or precondition.expected_prior_content_version < 1
        or type(precondition.expected_prior_manifest_bytes) is not bytes
        or hashlib.sha256(precondition.expected_prior_manifest_bytes).hexdigest() != precondition.expected_prior_sha256
    ):
        return False
    try:
        prior = parse_content_manifest_v1(precondition.expected_prior_manifest_bytes)
    except ManifestParseError:
        return False
    return (
        prior.to_json_bytes() == precondition.expected_prior_manifest_bytes
        and prior.content_version == precondition.expected_prior_content_version
    )


def _validated_history(
    events_value: object, candidate: CandidateManifestBuildResult
) -> tuple[tuple[ReleaseEvent, ...], ReleaseEvent] | None:
    if not isinstance(events_value, tuple) or any(not isinstance(item, ReleaseEvent) for item in events_value):
        return None
    replay = replay_release_events(events_value)
    if not replay.accepted:
        return None
    content_id = f"manifest-v{candidate.manifest.content_version}-{candidate.manifest_sha256[:16]}"
    record_id = f"staging-{candidate.manifest_sha256[:32]}"
    matching_content = [snapshot for snapshot in replay.snapshots if snapshot.content_id == content_id]
    current = next((snapshot for snapshot in replay.snapshots if snapshot.record_id == record_id), None)
    if any(
        snapshot.content_digest != candidate.manifest_sha256
        or snapshot.environment is not Environment.STAGING
        for snapshot in matching_content
    ):
        return None
    if current is None:
        if matching_content:
            return None
        current_state: ReleaseState | None = None
    else:
        if current.content_id != content_id or current.content_digest != candidate.manifest_sha256:
            return None
        if current.environment is not Environment.STAGING or current.state not in {ReleaseState.DRAFT, ReleaseState.VALIDATED}:
            return None
        current_state = current.state

    appended: list[ReleaseEvent] = []
    sequence = len(events_value) + 1
    previous_digest = events_value[-1].event_digest if events_value else "0" * 64

    def add(to_state: ReleaseState, from_state: ReleaseState | None, expected_state: ReleaseState | None) -> ReleaseEvent:
        nonlocal sequence, previous_digest
        event_id = f"stage-{candidate.manifest_sha256[:16]}-e{sequence}"
        transition_id = f"stage-{candidate.manifest_sha256[:16]}-t{sequence}"
        event = make_release_event(
            sequence=sequence,
            event_id=event_id,
            transition_id=transition_id,
            record_id=record_id,
            content_id=content_id,
            content_digest=candidate.manifest_sha256,
            environment=Environment.STAGING,
            from_state=from_state,
            to_state=to_state,
            expected_state=expected_state,
            previous_event_digest=previous_digest,
        )
        appended.append(event)
        sequence += 1
        previous_digest = event.event_digest
        return event

    if current_state is None:
        add(ReleaseState.DRAFT, None, None)
        current_state = ReleaseState.DRAFT
    if current_state is ReleaseState.DRAFT:
        add(ReleaseState.VALIDATED, ReleaseState.DRAFT, ReleaseState.DRAFT)
    staged = add(ReleaseState.STAGED, ReleaseState.VALIDATED, ReleaseState.VALIDATED)
    if not replay_release_events((*events_value, *appended)).accepted:
        return None
    return tuple(appended[:-1]), staged


def _write_failure(
    reason: StagingManifestReasonCode,
    negotiation: CapabilityNegotiationResult,
    prior_events: tuple[ReleaseEvent, ...],
    validated_events: tuple[ReleaseEvent, ...],
    candidate: CandidateManifestBuildResult,
) -> StagingManifestPublishReport:
    complete_history = (*prior_events, *validated_events)
    replay = replay_release_events(complete_history)
    if not replay.accepted:
        return _failure(StagingManifestReasonCode.INVALID_RELEASE_HISTORY, negotiation, True, True)
    last = complete_history[-1]
    sequence = len(complete_history) + 1
    failed = make_release_event(
        sequence=sequence,
        event_id=f"stage-{candidate.manifest_sha256[:16]}-e{sequence}",
        transition_id=f"stage-{candidate.manifest_sha256[:16]}-t{sequence}",
        record_id=f"staging-{candidate.manifest_sha256[:32]}",
        content_id=f"manifest-v{candidate.manifest.content_version}-{candidate.manifest_sha256[:16]}",
        content_digest=candidate.manifest_sha256,
        environment=Environment.STAGING,
        from_state=ReleaseState.VALIDATED,
        to_state=ReleaseState.FAILED,
        expected_state=ReleaseState.VALIDATED,
        previous_event_digest=last.event_digest,
    )
    if not replay_release_events((*complete_history, failed)).accepted:
        return _failure(StagingManifestReasonCode.INVALID_RELEASE_HISTORY, negotiation, True, True)
    return StagingManifestPublishReport(False, reason, None, (*validated_events, failed), negotiation, True, True)


def _valid_write_result(result: object, identity: ProviderIdentity) -> bool:
    return (
        isinstance(result, ProviderResult)
        and result.result_version == PROVIDER_CONTRACT_VERSION
        and result.provider_id == identity.provider_id
        and result.environment is Environment.STAGING
        and isinstance(result.category, ProviderResultCategory)
        and (result.content_digest is None or _SHA256.fullmatch(result.content_digest) is not None)
    )


def _valid_receipt(receipt: object) -> bool:
    if not isinstance(receipt, StagingManifestReceipt) or receipt.schema_version != STAGING_MANIFEST_PUBLISH_VERSION:
        return False
    if (
        type(receipt.manifest_bytes) is not bytes
        or not isinstance(receipt.manifest_sha256, str)
        or not _SHA256.fullmatch(receipt.manifest_sha256)
        or hashlib.sha256(receipt.manifest_bytes).hexdigest() != receipt.manifest_sha256
        or type(receipt.content_version) is not int or receipt.content_version < 1
        or not _safe_object_key(receipt.manifest_object_key)
    ):
        return False
    try:
        manifest = parse_content_manifest_v1(receipt.manifest_bytes)
    except ManifestParseError:
        return False
    if manifest.to_json_bytes() != receipt.manifest_bytes:
        return False
    pack_digests = receipt.referenced_pack_digests
    if not isinstance(pack_digests, tuple) or len(pack_digests) != len(manifest.packs):
        return False
    expected = tuple(sorted(manifest.packs, key=lambda item: item.pack_id.encode("ascii")))
    if any(
        not isinstance(actual, StagingManifestPackDigest)
        or (actual.pack_id, actual.object_key, actual.sha256, actual.byte_length)
        != (pack.pack_id, pack.object_key, pack.sha256, pack.byte_length)
        for actual, pack in zip(pack_digests, expected)
    ):
        return False
    if (
        manifest.content_version != receipt.content_version
        or not validate_provider_identity(ProviderIdentity(
            receipt.provider_id, receipt.provider_version, receipt.provider_contract_version
        ))
        or not _safe_identifier(receipt.capability_id)
        or not _safe_identifier(receipt.capability_version)
        or receipt.target_environment != Environment.STAGING.value
        or not _safe_identifier(receipt.target_id)
    ):
        return False
    if receipt.expected_prior_manifest_sha256 is None:
        if receipt.expected_prior_content_version is not None:
            return False
    elif (
        not isinstance(receipt.expected_prior_manifest_sha256, str)
        or not _SHA256.fullmatch(receipt.expected_prior_manifest_sha256)
        or type(receipt.expected_prior_content_version) is not int
        or receipt.expected_prior_content_version < 1
        or manifest.content_version <= receipt.expected_prior_content_version
    ):
        return False
    return (
        isinstance(receipt.release_event_digests, tuple)
        and bool(receipt.release_event_digests)
        and all(isinstance(item, str) and _SHA256.fullmatch(item) for item in receipt.release_event_digests)
    )


def _safe_identifier(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value))
        and not _contains_obvious_secret(value)
    )


def _safe_object_key(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(_SAFE_OBJECT_KEY.fullmatch(value))
        and not _contains_obvious_secret(value)
        and not any(part in {"", ".", ".."} for part in value.split("/"))
    )


def _failure(
    reason: StagingManifestReasonCode,
    negotiation: CapabilityNegotiationResult | None = None,
    attempted: bool = False,
    references_revalidated: bool = False,
) -> StagingManifestPublishReport:
    return StagingManifestPublishReport(False, reason, None, (), negotiation, attempted, references_revalidated)


__all__ = [
    "STAGING_MANIFEST_PUBLISH_VERSION",
    "StagingManifestPrecondition",
    "StagingManifestPackDigest",
    "StagingManifestPublishReport",
    "StagingManifestReasonCode",
    "StagingManifestReceipt",
    "StagingManifestWriter",
    "publish_candidate_manifest_to_staging",
    "serialize_staging_manifest_receipt",
]
