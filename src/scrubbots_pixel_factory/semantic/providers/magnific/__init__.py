"""Magnific external orchestration and local result-ingestion bridge."""

from .bridge import (
    MAGNIFIC_ADAPTER_VERSION,
    MAGNIFIC_ASPECT_RATIO_VOCABULARY_VERSION,
    MAGNIFIC_CONFIG_VERSION,
    MAGNIFIC_EXECUTION_SURFACE,
    MAGNIFIC_PROVIDER_ID,
    MAGNIFIC_RESULT_SCHEMA,
    MAGNIFIC_SUPPORTED_ASPECT_RATIOS,
    MagnificExecutionBinding,
    MagnificJobSpec,
    MagnificProvider,
    MagnificReferenceBinding,
    MagnificResultManifest,
    map_magnific_aspect_ratio,
)

__all__ = [
    "MAGNIFIC_ADAPTER_VERSION",
    "MAGNIFIC_ASPECT_RATIO_VOCABULARY_VERSION",
    "MAGNIFIC_CONFIG_VERSION",
    "MAGNIFIC_EXECUTION_SURFACE",
    "MAGNIFIC_PROVIDER_ID",
    "MAGNIFIC_RESULT_SCHEMA",
    "MAGNIFIC_SUPPORTED_ASPECT_RATIOS",
    "MagnificExecutionBinding",
    "MagnificJobSpec",
    "MagnificProvider",
    "MagnificReferenceBinding",
    "MagnificResultManifest",
    "map_magnific_aspect_ratio",
]
