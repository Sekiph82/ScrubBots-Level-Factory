"""Versioned, deterministic configuration for the control-plane boundary."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum


class Environment(StrEnum):
    """Logical target labels; they do not identify or contact real services."""

    STAGING = "staging"
    PRODUCTION = "production"


TARGET_MODEL_VERSION = "1.0"


class TargetReasonCode(StrEnum):
    VALID_TARGET = "VALID_TARGET"
    UNKNOWN_ENVIRONMENT = "UNKNOWN_ENVIRONMENT"
    ENVIRONMENT_MISMATCH = "ENVIRONMENT_MISMATCH"
    INVALID_TARGET_IDENTITY = "INVALID_TARGET_IDENTITY"
    NAMESPACE_COLLISION = "NAMESPACE_COLLISION"
    PROMOTION_REQUIRED = "PROMOTION_REQUIRED"


@dataclass(frozen=True, slots=True)
class EnvironmentTarget:
    """Secret-free, deterministic logical target; it names no provider endpoint."""

    environment: Environment
    logical_target_id: str
    state_namespace: str
    content_namespace: str
    direct_publication_permitted: bool
    promotion_required: bool
    target_version: str = TARGET_MODEL_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "target_version": self.target_version,
            "environment": self.environment.value,
            "logical_target_id": self.logical_target_id,
            "state_namespace": self.state_namespace,
            "content_namespace": self.content_namespace,
            "direct_publication_permitted": self.direct_publication_permitted,
            "promotion_required": self.promotion_required,
        }


@dataclass(frozen=True, slots=True)
class TargetValidationResult:
    validation_version: str
    accepted: bool
    reason_code: TargetReasonCode


def _target(environment: Environment) -> EnvironmentTarget:
    return EnvironmentTarget(
        environment=environment,
        logical_target_id=f"{environment.value}:default",
        state_namespace=f"{environment.value}:state",
        content_namespace=f"{environment.value}:content",
        direct_publication_permitted=environment is Environment.STAGING,
        promotion_required=environment is Environment.PRODUCTION,
    )


STAGING_TARGET = _target(Environment.STAGING)
PRODUCTION_TARGET = _target(Environment.PRODUCTION)


def target_for(environment: Environment | str) -> EnvironmentTarget:
    """Return the canonical local identity or fail closed for unknown labels."""
    try:
        resolved = environment if isinstance(environment, Environment) else Environment(environment)
    except (TypeError, ValueError) as exc:
        raise ValueError("unknown content-pipeline environment") from exc
    return STAGING_TARGET if resolved is Environment.STAGING else PRODUCTION_TARGET


def _target_is_valid(target: object) -> bool:
    if not isinstance(target, EnvironmentTarget) or not isinstance(target.environment, Environment):
        return False
    if target.target_version != TARGET_MODEL_VERSION:
        return False
    values = (target.logical_target_id, target.state_namespace, target.content_namespace)
    if any(not isinstance(value, str) or not value for value in values):
        return False
    other_prefix = "production:" if target.environment is Environment.STAGING else "staging:"
    if any(value.startswith(other_prefix) for value in values):
        return False
    if target.environment is Environment.STAGING:
        return target.direct_publication_permitted is True and target.promotion_required is False
    return target.direct_publication_permitted is False and target.promotion_required is True


def _target_result(accepted: bool, reason: TargetReasonCode) -> TargetValidationResult:
    return TargetValidationResult(TARGET_MODEL_VERSION, accepted, reason)


def validate_environment_pair(staging: object, production: object) -> TargetValidationResult:
    """Require valid, distinct staging and production target identities."""
    if not _target_is_valid(staging) or not _target_is_valid(production):
        return _target_result(False, TargetReasonCode.INVALID_TARGET_IDENTITY)
    assert isinstance(staging, EnvironmentTarget) and isinstance(production, EnvironmentTarget)
    if staging.environment is not Environment.STAGING or production.environment is not Environment.PRODUCTION:
        return _target_result(False, TargetReasonCode.ENVIRONMENT_MISMATCH)
    left = {staging.logical_target_id, staging.state_namespace, staging.content_namespace}
    right = {production.logical_target_id, production.state_namespace, production.content_namespace}
    if left & right:
        return _target_result(False, TargetReasonCode.NAMESPACE_COLLISION)
    return _target_result(True, TargetReasonCode.VALID_TARGET)


def validate_target_binding(environment: object, target: object) -> TargetValidationResult:
    """Check that a plan/report environment is explicit and matches its target."""
    if not isinstance(environment, (Environment, str)):
        return _target_result(False, TargetReasonCode.UNKNOWN_ENVIRONMENT)
    try:
        resolved = environment if isinstance(environment, Environment) else Environment(environment)
    except ValueError:
        return _target_result(False, TargetReasonCode.UNKNOWN_ENVIRONMENT)
    if not _target_is_valid(target):
        return _target_result(False, TargetReasonCode.INVALID_TARGET_IDENTITY)
    assert isinstance(target, EnvironmentTarget)
    if target.environment is not resolved:
        return _target_result(False, TargetReasonCode.ENVIRONMENT_MISMATCH)
    return _target_result(True, TargetReasonCode.VALID_TARGET)


def validate_target_use(target: object, source_environment: object | None, promotion_intent: bool = False) -> TargetValidationResult:
    """Refuse cross-environment use without explicit promotion intent."""
    if not _target_is_valid(target):
        return _target_result(False, TargetReasonCode.INVALID_TARGET_IDENTITY)
    assert isinstance(target, EnvironmentTarget)
    if source_environment is not None:
        if not isinstance(source_environment, (Environment, str)):
            return _target_result(False, TargetReasonCode.UNKNOWN_ENVIRONMENT)
        try:
            source = source_environment if isinstance(source_environment, Environment) else Environment(source_environment)
        except ValueError:
            return _target_result(False, TargetReasonCode.UNKNOWN_ENVIRONMENT)
        if source is not target.environment:
            if target.environment is Environment.PRODUCTION and source is Environment.STAGING and promotion_intent is True:
                return _target_result(True, TargetReasonCode.VALID_TARGET)
            return _target_result(False, TargetReasonCode.PROMOTION_REQUIRED if target.environment is Environment.PRODUCTION else TargetReasonCode.ENVIRONMENT_MISMATCH)
    if target.promotion_required and promotion_intent is not True:
        return _target_result(False, TargetReasonCode.PROMOTION_REQUIRED)
    return _target_result(True, TargetReasonCode.VALID_TARGET)


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Secret-free configuration for validation and future orchestration."""

    schema_version: str = "1.0"
    environment: Environment = Environment.STAGING
    input_contract: str = "scrubbots.level_factory.accepted-content.v1"
    require_owner_approval: bool = True
    target: EnvironmentTarget | None = None

    @property
    def resolved_target(self) -> EnvironmentTarget | None:
        if self.target is not None:
            return self.target
        try:
            return target_for(self.environment)
        except ValueError:
            return None


def serialize_config(config: PipelineConfig) -> str:
    """Serialize configuration to stable UTF-8-compatible JSON text."""

    environment = config.environment.value if isinstance(config.environment, Environment) else config.environment
    target = config.resolved_target
    value = {
        "schema_version": config.schema_version,
        "environment": environment,
        "input_contract": config.input_contract,
        "require_owner_approval": config.require_owner_approval,
        "target": target.to_dict() if target is not None else None,
    }
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
