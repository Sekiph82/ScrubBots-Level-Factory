"""Separate Content Platform control-plane project.

This package defines declarative validation and orchestration contracts only.
It does not connect to a provider or mutate remote content.
"""

from .config import Environment, PipelineConfig, serialize_config
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
from .validation import DryRunReport, validate_only

__all__ = [
    "DryRunReport",
    "BOUNDARY_VERSION",
    "ClassificationResult",
    "ContentDisposition",
    "Environment",
    "EvidenceSink",
    "PipelineConfig",
    "PromotionOrchestrator",
    "PublishOrchestrator",
    "RollbackOrchestrator",
    "ReasonCode",
    "classify_content",
    "serialize_config",
    "serialize_result",
    "validate_only",
]
