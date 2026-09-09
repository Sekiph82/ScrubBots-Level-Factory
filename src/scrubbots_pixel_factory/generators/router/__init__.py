"""Deterministic explicit and composed generator routing for PAG-M06."""

from .hybrid import (
    HYBRID_ENGINE_ID,
    HYBRID_ENGINE_VERSION,
    HybridCandidate,
    HybridGenerator,
    HybridStageMetadata,
    HybridStrategy,
    reproduce_hybrid,
)
from .router import AutoCandidate, AutoAttempt, GeneratorRouter

__all__ = [
    "AutoAttempt",
    "AutoCandidate",
    "GeneratorRouter",
    "HYBRID_ENGINE_ID",
    "HYBRID_ENGINE_VERSION",
    "HybridCandidate",
    "HybridGenerator",
    "HybridStageMetadata",
    "HybridStrategy",
    "reproduce_hybrid",
]
