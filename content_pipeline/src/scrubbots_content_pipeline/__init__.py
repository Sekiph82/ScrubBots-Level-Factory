"""Separate Content Platform control-plane project.

This package defines declarative validation and orchestration contracts only.
It does not connect to a provider or mutate remote content.
"""

from .config import (
    PRODUCTION_TARGET,
    STAGING_TARGET,
    TARGET_MODEL_VERSION,
    Environment,
    EnvironmentTarget,
    PipelineConfig,
    TargetReasonCode,
    TargetValidationResult,
    serialize_config,
    target_for,
    validate_environment_pair,
    validate_target_binding,
    validate_target_use,
)
from .content_boundary import (
    BOUNDARY_VERSION,
    ClassificationResult,
    ContentDisposition,
    ReasonCode,
    classify_content,
    serialize_result,
)
from .orchestration import (
    EvidenceSink,
    PromotionOrchestrator,
    PublishOrchestrator,
    RollbackOrchestrator,
)
from .payload_validation import (
    PAYLOAD_VALIDATION_VERSION,
    PayloadReasonCode,
    PayloadValidationResult,
    serialize_payload_result,
    validate_remote_payload,
)
from .validation import DryRunReport, validate_only

__all__ = [
    "DryRunReport",
    "BOUNDARY_VERSION",
    "ClassificationResult",
    "ContentDisposition",
    "Environment",
    "EnvironmentTarget",
    "EvidenceSink",
    "PipelineConfig",
    "PRODUCTION_TARGET",
    "PromotionOrchestrator",
    "PublishOrchestrator",
    "RollbackOrchestrator",
    "ReasonCode",
    "STAGING_TARGET",
    "TARGET_MODEL_VERSION",
    "TargetReasonCode",
    "TargetValidationResult",
    "classify_content",
    "serialize_config",
    "serialize_result",
    "PAYLOAD_VALIDATION_VERSION",
    "PayloadReasonCode",
    "PayloadValidationResult",
    "serialize_payload_result",
    "validate_remote_payload",
    "validate_only",
    "target_for",
    "validate_environment_pair",
    "validate_target_binding",
    "validate_target_use",
]
