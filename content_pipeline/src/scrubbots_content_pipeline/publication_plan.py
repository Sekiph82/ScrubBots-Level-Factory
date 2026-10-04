"""Deterministic local publication plans; this module has no mutation path."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .config import Environment, EnvironmentTarget, validate_target_binding
from .content_boundary import ContentDisposition, classify_content
from .payload_validation import PayloadReasonCode, PayloadValidationResult, validate_remote_payload
from .provider import ProviderCapability, ProviderFeature, negotiate_capabilities, validate_provider_capability
from .release_state import ReleaseReplayResult, ReleaseState, ReleaseStateSnapshot
from .secret_refs import _contains_obvious_secret, redact_for_evidence

PUBLICATION_PLAN_VERSION = "1.0"
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class PlanReasonCode(StrEnum):
    ACCEPTED = "ACCEPTED"
    INVALID_INPUT = "INVALID_INPUT"
    UNVALIDATED_PAYLOAD = "UNVALIDATED_PAYLOAD"
    INVALID_REPLAY = "INVALID_REPLAY"
    INVALID_TARGET = "INVALID_TARGET"
    ENVIRONMENT_MISMATCH = "ENVIRONMENT_MISMATCH"
    CONTENT_MISMATCH = "CONTENT_MISMATCH"
    STATE_MISMATCH = "STATE_MISMATCH"
    PROMOTION_REQUIRED = "PROMOTION_REQUIRED"
    OWNER_APPROVAL_REQUIRED = "OWNER_APPROVAL_REQUIRED"
    INVALID_CAPABILITY = "INVALID_CAPABILITY"
    SECRET_BEARING_INPUT = "SECRET_BEARING_INPUT"
    STALE_PLAN = "STALE_PLAN"


@dataclass(frozen=True, slots=True)
class PlanCheck:
    check_id: str
    accepted: bool
    reason_code: str


@dataclass(frozen=True, slots=True)
class PublicationOperation:
    sequence: int
    operation: str
    content_id: str
    content_digest: str
    source_record_id: str | None


@dataclass(frozen=True, slots=True)
class ExpectedReleaseState:
    record_version: str
    record_id: str | None
    content_id: str | None
    content_digest: str | None
    environment: str
    state: str | None
    last_sequence: int


@dataclass(frozen=True, slots=True)
class PublicationPlan:
    plan_version: str
    accepted: bool
    complete: bool
    target_environment: str
    target_id: str
    capability_id: str | None
    capability_version: str | None
    capability_supports_staging_publish: bool
    capability_supports_production_promotion: bool
    capability_environments: tuple[str, ...]
    capability_features: tuple[str, ...]
    content_id: str
    content_digest: str
    operations: tuple[PublicationOperation, ...]
    checks: tuple[PlanCheck, ...]
    expected_release_state: ExpectedReleaseState
    owner_approved: bool
    mutation_eligible_in_principle: bool
    remote_mutation_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_version": self.plan_version,
            "accepted": self.accepted,
            "complete": self.complete,
            "target_environment": self.target_environment,
            "target_id": self.target_id,
            "provider_capability": {
                "capability_id": self.capability_id,
                "capability_version": self.capability_version,
                "supports_staging_publish": self.capability_supports_staging_publish,
                "supports_production_promotion": self.capability_supports_production_promotion,
                "environments": list(self.capability_environments),
                "features": list(self.capability_features),
            },
            "content_id": self.content_id,
            "content_digest": self.content_digest,
            "operations": [
                {
                    "sequence": operation.sequence,
                    "operation": operation.operation,
                    "content_id": operation.content_id,
                    "content_digest": operation.content_digest,
                    "source_record_id": operation.source_record_id,
                }
                for operation in self.operations
            ],
            "checks": [
                {"check_id": check.check_id, "accepted": check.accepted, "reason_code": check.reason_code}
                for check in self.checks
            ],
            "expected_release_state": {
                "record_version": self.expected_release_state.record_version,
                "record_id": self.expected_release_state.record_id,
                "content_id": self.expected_release_state.content_id,
                "content_digest": self.expected_release_state.content_digest,
                "environment": self.expected_release_state.environment,
                "state": self.expected_release_state.state,
                "last_sequence": self.expected_release_state.last_sequence,
            },
            "owner_approved": self.owner_approved,
            "mutation_eligible_in_principle": self.mutation_eligible_in_principle,
            "remote_mutation_performed": False,
        }


def serialize_publication_plan(plan: PublicationPlan) -> str:
    """Serialize the fixed plan schema deterministically; no input mapping is echoed."""
    return json.dumps(plan.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def _snapshot(replay: ReleaseReplayResult, current: ReleaseStateSnapshot | None) -> ExpectedReleaseState:
    if isinstance(current, ReleaseStateSnapshot):
        return ExpectedReleaseState(
            current.record_version, current.record_id, current.content_id,
            current.content_digest, current.environment.value, current.state.value,
            current.last_sequence,
        )
    latest_sequence = max((snapshot.last_sequence for snapshot in replay.snapshots), default=0)
    if current is not None:
        return ExpectedReleaseState("invalid", None, None, None, "unknown", None, latest_sequence)
    return ExpectedReleaseState("1.0", None, None, None, "none", None, latest_sequence)


def _safe_identifier(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value)) and not _contains_obvious_secret(value)


def build_publication_plan(
    *, descriptor: object,
    payload: bytes | bytearray | memoryview | object,
    payload_result: PayloadValidationResult,
    target: EnvironmentTarget,
    replay: ReleaseReplayResult,
    current_state: ReleaseStateSnapshot | None,
    capability: ProviderCapability,
    owner_approved: bool,
) -> PublicationPlan:
    """Build a local-only plan from independently validated content and release evidence."""
    checks: list[PlanCheck] = []

    def check(name: str, passed: bool, reason: PlanReasonCode | str) -> None:
        checks.append(PlanCheck(name, passed, reason.value if isinstance(reason, PlanReasonCode) else reason))

    identity: Mapping[str, Any] = descriptor if isinstance(descriptor, Mapping) else {}
    attrs = identity.get("attributes") if isinstance(identity.get("attributes"), Mapping) else {}
    content_id = attrs.get("level_id") if _safe_identifier(attrs.get("level_id")) else "invalid-content"
    digest_field = "supply_plan_sha256" if identity.get("content_type") == "supply_plan_data" else "payload_sha256"
    content_digest = attrs.get(digest_field) if isinstance(attrs.get(digest_field), str) and _SHA256.fullmatch(attrs[digest_field]) else "0" * 64
    classification = classify_content(descriptor)
    recomputed = validate_remote_payload(descriptor, payload)
    validation_ok = (
        isinstance(payload_result, PayloadValidationResult)
        and payload_result.accepted is True
        and payload_result.reason_code is PayloadReasonCode.VALID_PAYLOAD
        and payload_result == recomputed
        and classification.disposition is ContentDisposition.REMOTE_DECLARATIVE
    )
    check("payload_validation", validation_ok, PlanReasonCode.ACCEPTED if validation_ok else PlanReasonCode.UNVALIDATED_PAYLOAD)

    valid_target = isinstance(target, EnvironmentTarget)
    target_result = validate_target_binding(target.environment if valid_target else None, target)
    target_is_safe = valid_target and all(
        _safe_identifier(value)
        for value in (target.logical_target_id, target.state_namespace, target.content_namespace)
    )
    target_ok = target_result.accepted and target_is_safe
    check("target_binding", target_ok, PlanReasonCode.ACCEPTED if target_ok else PlanReasonCode.INVALID_TARGET)
    replay_ok = isinstance(replay, ReleaseReplayResult) and replay.accepted is True
    snapshot_member = current_state is None or (replay_ok and current_state in replay.snapshots)
    check("release_replay", replay_ok and snapshot_member, PlanReasonCode.ACCEPTED if replay_ok and snapshot_member else PlanReasonCode.INVALID_REPLAY)

    if current_state is None:
        content_matches = valid_target and target.environment is Environment.STAGING and replay_ok and not any(
            item.content_id == content_id and item.environment is target.environment for item in replay.snapshots
        )
        state_matches = content_matches
    else:
        content_matches = (
            replay_ok and snapshot_member and current_state.content_id == content_id
            and current_state.content_digest == content_digest
        )
        promoting = valid_target and target.environment is Environment.PRODUCTION
        expected_state = ReleaseState.STAGED if promoting else ReleaseState.VALIDATED
        state_matches = (
            replay_ok and snapshot_member and current_state.environment is Environment.STAGING
            and current_state.state is expected_state
        )
    check("content_binding", content_matches, PlanReasonCode.ACCEPTED if content_matches else PlanReasonCode.CONTENT_MISMATCH)
    check("release_state", state_matches, PlanReasonCode.ACCEPTED if state_matches else PlanReasonCode.STATE_MISMATCH)

    capability_ok = validate_provider_capability(capability)
    check("provider_capability", capability_ok, PlanReasonCode.ACCEPTED if capability_ok else PlanReasonCode.INVALID_CAPABILITY)
    if valid_target:
        required_features = (
            (ProviderFeature.PRODUCTION_PROMOTION, ProviderFeature.INTEGRITY_VERIFY,
             ProviderFeature.CONDITIONAL_WRITE, ProviderFeature.ATOMIC_MANIFEST_PUBLISH)
            if target.environment is Environment.PRODUCTION
            else (ProviderFeature.STAGING_PUBLISH, ProviderFeature.OBJECT_WRITE,
                  ProviderFeature.INTEGRITY_VERIFY, ProviderFeature.CONDITIONAL_WRITE)
        )
        capability_negotiation = negotiate_capabilities(capability, target.environment, required_features) if capability_ok else None
    else:
        capability_negotiation = None
    capability_negotiated = capability_ok and capability_negotiation is not None and capability_negotiation.accepted
    check("capability_negotiation", capability_negotiated, PlanReasonCode.ACCEPTED if capability_negotiated else PlanReasonCode.INVALID_CAPABILITY)
    approval_ok = type(owner_approved) is bool and owner_approved is True
    check("owner_approval", approval_ok, PlanReasonCode.ACCEPTED if approval_ok else PlanReasonCode.OWNER_APPROVAL_REQUIRED)

    secret_bearing = False
    try:
        descriptor_json = json.dumps(descriptor, sort_keys=True, separators=(",", ":"), default=str)
        payload_text = bytes(payload).decode("utf-8") if isinstance(payload, (bytes, bytearray, memoryview)) else ""
        target_text = json.dumps(target.to_dict(), sort_keys=True, separators=(",", ":")) if valid_target else ""
        capability_text = capability.capability_id if isinstance(capability, ProviderCapability) else ""
        redacted_descriptor = json.dumps(redact_for_evidence(descriptor), sort_keys=True, separators=(",", ":"), default=str)
        secret_bearing = (
            redacted_descriptor != descriptor_json
            or any(_contains_obvious_secret(value) for value in (descriptor_json, payload_text, target_text, capability_text))
        )
    except (TypeError, ValueError):
        secret_bearing = True
    check("secret_free_inputs", not secret_bearing, PlanReasonCode.ACCEPTED if not secret_bearing else PlanReasonCode.SECRET_BEARING_INPUT)

    source_record_id: str | None = None
    if valid_target and target.environment is Environment.PRODUCTION:
        source = current_state
        promotion_ok = (
            target.promotion_required is True and target.direct_publication_permitted is False
            and isinstance(source, ReleaseStateSnapshot)
            and source.environment is Environment.STAGING
            and source.state is ReleaseState.STAGED
            and source.content_id == content_id and source.content_digest == content_digest
            and capability_ok and capability_negotiated and capability.supports_production_promotion is True
            and validation_ok and replay_ok and snapshot_member
        )
        if promotion_ok:
            source_record_id = source.record_id
        check("production_promotion_source", promotion_ok, PlanReasonCode.ACCEPTED if promotion_ok else PlanReasonCode.PROMOTION_REQUIRED)
        operation_name = "promote_staged_record"
    else:
        promotion_ok = True
        capability_stage_ok = capability_ok and capability_negotiated and capability.supports_staging_publish is True
        check("staging_capability", capability_stage_ok, PlanReasonCode.ACCEPTED if capability_stage_ok else PlanReasonCode.INVALID_CAPABILITY)
        operation_name = "publish_to_staging"

    accepted = all(item.accepted for item in checks)
    operation = PublicationOperation(1, operation_name, content_id, content_digest, source_record_id)
    environment_value = target.environment.value if isinstance(target, EnvironmentTarget) else "invalid"
    target_id = target.logical_target_id if valid_target and _safe_identifier(target.logical_target_id) else "invalid-target"
    expected = _snapshot(replay, current_state) if isinstance(replay, ReleaseReplayResult) else ExpectedReleaseState("1.0", None, None, None, "unknown", None, 0)
    return PublicationPlan(
        PUBLICATION_PLAN_VERSION, accepted, True, environment_value, target_id,
        capability.capability_id if capability_ok else None,
        capability.capability_version if capability_ok else None,
        capability.supports_staging_publish if capability_ok else False,
        capability.supports_production_promotion if capability_ok else False,
        tuple(environment.value for environment in capability.environments) if capability_ok else (),
        tuple(feature.value for feature in capability.features) if capability_ok else (),
        content_id, content_digest, (operation,), tuple(checks), expected,
        approval_ok, accepted and approval_ok and promotion_ok, False,
    )


def validate_plan_current(
    plan: PublicationPlan,
    *,
    current_target: EnvironmentTarget,
    current_replay: ReleaseReplayResult,
    current_state: ReleaseStateSnapshot | None,
    current_content_digest: str,
) -> PlanCheck:
    """Recheck exact target, digest, and replayed state before any future gate consumer."""
    current = _snapshot(current_replay, current_state) if isinstance(current_replay, ReleaseReplayResult) else None
    state_is_current = (
        current_state is None
        or (isinstance(current_replay, ReleaseReplayResult) and current_state in current_replay.snapshots)
    )
    matches = (
        isinstance(plan, PublicationPlan) and plan.accepted and plan.complete
        and plan.remote_mutation_performed is False
        and isinstance(current_target, EnvironmentTarget)
        and plan.target_environment == current_target.environment.value
        and plan.target_id == current_target.logical_target_id
        and _SHA256.fullmatch(current_content_digest or "") is not None
        and plan.content_digest == current_content_digest
        and isinstance(current_replay, ReleaseReplayResult)
        and current_replay.accepted is True
        and state_is_current
        and current == plan.expected_release_state
    )
    return PlanCheck("current_plan", bool(matches), PlanReasonCode.ACCEPTED.value if matches else PlanReasonCode.STALE_PLAN.value)


__all__ = [
    "PUBLICATION_PLAN_VERSION", "ExpectedReleaseState", "PlanCheck", "PlanReasonCode",
    "PublicationOperation", "PublicationPlan", "build_publication_plan",
    "serialize_publication_plan", "validate_plan_current",
]
