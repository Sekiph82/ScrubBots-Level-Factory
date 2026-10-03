"""Separate Content Platform control-plane project.

This package defines declarative validation and orchestration contracts only.
It does not connect to a provider or mutate remote content.
"""

from .config import Environment, PipelineConfig, serialize_config
from .orchestration import (
    EvidenceSink,
    PromotionOrchestrator,
    PublishOrchestrator,
    RollbackOrchestrator,
)
from .validation import DryRunReport, validate_only

__all__ = [
    "DryRunReport",
    "Environment",
    "EvidenceSink",
    "PipelineConfig",
    "PromotionOrchestrator",
    "PublishOrchestrator",
    "RollbackOrchestrator",
    "serialize_config",
    "validate_only",
]
