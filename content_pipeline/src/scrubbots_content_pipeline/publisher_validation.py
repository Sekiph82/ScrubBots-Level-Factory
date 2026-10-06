"""Local publisher candidate validation with no provider or mutation path."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
import re

from .compatibility import check_app_content_compatibility
from .config import Environment, EnvironmentTarget, validate_target_binding
from .manifest_parser import ManifestParseError, parse_content_manifest_v1
from .manifest_validation import validate_manifest_references
from .manifest_v1 import check_manifest_successor
from .publication_plan import PlanCheck, PublicationPlan, validate_plan_current
from .provider import ProviderCapability, validate_provider_capability
from .release_state import ReleaseReplayResult
from .secret_refs import _contains_obvious_secret

PUBLISHER_VALIDATION_VERSION = "1.0"
_SAFE_REASON = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")
_SAFE_TARGET_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


@dataclass(frozen=True, slots=True)
class PublisherValidationCheck:
    """One ordered, deterministic publisher gate result."""

    check_id: str
    accepted: bool
    reason_code: str

    def to_dict(self) -> dict[str, object]:
        return {"check_id": self.check_id, "accepted": self.accepted, "reason_code": self.reason_code}


@dataclass(frozen=True, slots=True)
class PublisherValidationReport:
    """Immutable report for a local candidate validation; it never mutates remotely."""

    schema_version: str
    accepted: bool
    manifest_sha256: str | None
    content_version: int | None
    target_environment: str
    target_id: str | None
    checks: tuple[PublisherValidationCheck, ...]
    remote_mutation_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "accepted": self.accepted is True,
            "checks": [check.to_dict() for check in self.checks],
            "content_version": self.content_version,
            "manifest_sha256": self.manifest_sha256,
            "remote_mutation_performed": False,
            "schema_version": self.schema_version,
            "target_environment": self.target_environment,
            "target_id": self.target_id,
        }


def serialize_publisher_validation_report(report: PublisherValidationReport) -> str:
    """Serialize only fixed report fields in deterministic, secret-free JSON."""
    if not isinstance(report, PublisherValidationReport):
        report = PublisherValidationReport(
            PUBLISHER_VALIDATION_VERSION,
            False,
            None,
            None,
            "unknown",
            None,
            (PublisherValidationCheck("report_contract", False, "INVALID_REPORT"),),
        )
    return json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def validate_publisher_candidate(
    *,
    manifest_bytes: object,
    pack_builds: object,
    previous_content_version: object,
    current_game_version: object,
    supported_manifest_schema_versions: object,
    publication_plan: object,
    current_target: object,
    current_replay: object,
    current_state: object,
    current_content_digest: object,
    capability: object,
    owner_approved: object,
) -> PublisherValidationReport:
    """Validate an explicit candidate against current local M11-M13 authorities.

    Only immutable plan/capability values are accepted. There is deliberately no
    provider object, callback, filesystem path, network client, or clock input.
    """
    checks: list[PublisherValidationCheck] = []

    def add(check_id: str, accepted: bool, reason_code: object) -> None:
        code = getattr(reason_code, "value", reason_code)
        safe_code = code if isinstance(code, str) and _SAFE_REASON.fullmatch(code) else "INVALID_REASON_CODE"
        checks.append(PublisherValidationCheck(check_id, type(accepted) is bool and accepted, safe_code))

    raw_bytes_ok = type(manifest_bytes) is bytes
    if raw_bytes_ok:
        manifest_sha256: str | None = hashlib.sha256(manifest_bytes).hexdigest()
        try:
            manifest = parse_content_manifest_v1(manifest_bytes)
        except ManifestParseError as exc:
            manifest = None
            parse_reason = exc.reason_code.value
        else:
            parse_reason = "VALID"
    else:
        manifest_sha256 = None
        manifest = None
        parse_reason = "INPUT_NOT_BYTES"
    add("candidate_manifest", raw_bytes_ok and manifest is not None, parse_reason)

    if manifest is None:
        content_version: int | None = None
        reference_result = validate_manifest_references(None, pack_builds)
        add("manifest_references", False, "INVALID_MANIFEST")
        add("content_version", False, "INVALID_CANDIDATE_MANIFEST")
        add("content_compatibility", False, "INVALID_MANIFEST_COMPATIBILITY_FIELDS")
    else:
        content_version = manifest.content_version
        reference_result = validate_manifest_references(manifest, pack_builds)
        add("manifest_references", reference_result.eligible, "VALID" if reference_result.eligible else "REFERENCE_REJECTED")
        for reference_check in reference_result.checks:
            add(f"manifest_references.{reference_check.check_id}", reference_check.accepted, reference_check.reason_code)

        successor = check_manifest_successor(previous_content_version, manifest.to_dict())
        add("content_version", successor.accepted, successor.reason_code)
        compatibility = check_app_content_compatibility(
            current_game_version=current_game_version,
            supported_manifest_schema_versions=supported_manifest_schema_versions,
            manifest_schema=manifest.schema,
            manifest_schema_version=manifest.schema_version,
            minimum_game_version=manifest.minimum_game_version,
        )
        add("content_compatibility", compatibility.compatible, compatibility.reason_code)

    target_ok = isinstance(current_target, EnvironmentTarget)
    target_usable = target_ok and isinstance(current_target.environment, Environment)
    target_result = validate_target_binding(
        current_target.environment if target_usable else None,
        current_target if target_usable else None,
    )
    add("current_target", target_result.accepted, target_result.reason_code)

    replay_ok = isinstance(current_replay, ReleaseReplayResult) and current_replay.accepted is True
    state_member = current_state is None or (
        replay_ok and current_state in current_replay.snapshots
    )
    replay_reason = current_replay.reason_code if isinstance(current_replay, ReleaseReplayResult) else "INVALID_REPLAY"
    add("release_state_replay", replay_ok and state_member, "VALID" if replay_ok and state_member else replay_reason)

    plan_ok = isinstance(publication_plan, PublicationPlan)
    plan_checks_valid = (
        plan_ok
        and isinstance(publication_plan.checks, tuple)
        and all(
            isinstance(item, PlanCheck)
            and isinstance(item.check_id, str)
            and type(item.accepted) is bool
            and isinstance(item.reason_code, str)
            and _SAFE_REASON.fullmatch(item.reason_code) is not None
            for item in publication_plan.checks
        )
        and len({item.check_id for item in publication_plan.checks}) == len(publication_plan.checks)
    )
    plan_checks = {check.check_id: check for check in publication_plan.checks} if plan_checks_valid else {}
    required_plan_checks = {
        "payload_validation", "target_binding", "release_replay", "content_binding",
        "release_state", "provider_capability", "capability_negotiation", "owner_approval",
        "secret_free_inputs",
    }
    if isinstance(current_target, EnvironmentTarget):
        required_plan_checks.add(
            "production_promotion_source"
            if getattr(current_target.environment, "value", None) == "production"
            else "staging_capability"
        )
    plan_checks_complete = plan_checks_valid and required_plan_checks <= set(plan_checks)
    plan_complete = (
        plan_ok
        and plan_checks_complete
        and type(publication_plan.accepted) is bool
        and publication_plan.accepted is True
        and type(publication_plan.complete) is bool
        and publication_plan.complete is True
        and publication_plan.remote_mutation_performed is False
        and all(item.accepted for item in publication_plan.checks)
    )
    m11_reason = "VALID" if plan_complete else "INVALID_PLAN"
    if plan_ok and not plan_complete:
        m11_reason = next((item.reason_code for item in publication_plan.checks if not item.accepted), "INVALID_PLAN")
    add("m11_publication_plan", plan_complete, m11_reason)

    capability_ok = validate_provider_capability(capability)
    capability_matches_plan = (
        capability_ok
        and plan_ok
        and publication_plan.capability_id == capability.capability_id
        and publication_plan.capability_version == capability.capability_version
        and publication_plan.capability_supports_staging_publish is capability.supports_staging_publish
        and publication_plan.capability_supports_production_promotion is capability.supports_production_promotion
        and publication_plan.capability_environments == tuple(item.value for item in capability.environments)
        and publication_plan.capability_features == tuple(item.value for item in capability.features)
    )
    add("provider_capability", capability_matches_plan, "VALID" if capability_matches_plan else "INVALID_CAPABILITY")

    approval_ok = type(owner_approved) is bool and owner_approved is True and plan_ok and publication_plan.owner_approved is True
    add("owner_approval", approval_ok, "VALID" if approval_ok else "OWNER_APPROVAL_REQUIRED")

    digest_ok = isinstance(current_content_digest, str)
    if plan_ok and target_usable and isinstance(current_replay, ReleaseReplayResult) and digest_ok:
        current_plan = validate_plan_current(
            publication_plan,
            current_target=current_target,
            current_replay=current_replay,
            current_state=current_state,
            current_content_digest=current_content_digest,
        )
        current_plan_ok = current_plan.accepted
        current_plan_reason = current_plan.reason_code
    else:
        current_plan_ok = False
        current_plan_reason = "STALE_PLAN"
    add("current_plan_binding", current_plan_ok, current_plan_reason)

    secret_check = plan_checks.get("secret_free_inputs")
    secret_free = plan_ok and secret_check is not None and secret_check.accepted is True
    add("secret_free_inputs", secret_free, "VALID" if secret_free else "SECRET_BEARING_OR_UNCHECKED_INPUT")

    ordered = tuple(checks)
    return PublisherValidationReport(
        PUBLISHER_VALIDATION_VERSION,
        all(check.accepted for check in ordered),
        manifest_sha256,
        content_version,
        current_target.environment.value
        if target_usable
        else "unknown",
        publication_plan.target_id
        if plan_complete
        and isinstance(publication_plan.target_id, str)
        and _SAFE_TARGET_ID.fullmatch(publication_plan.target_id)
        and not _contains_obvious_secret(publication_plan.target_id)
        else None,
        ordered,
        False,
    )


__all__ = [
    "PUBLISHER_VALIDATION_VERSION",
    "PublisherValidationCheck",
    "PublisherValidationReport",
    "serialize_publisher_validation_report",
    "validate_publisher_candidate",
]
