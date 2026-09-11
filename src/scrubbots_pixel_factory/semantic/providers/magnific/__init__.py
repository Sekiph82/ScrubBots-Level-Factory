"""Magnific external orchestration and local result-ingestion bridge."""

from .bridge import (
    MAGNIFIC_ADAPTER_VERSION,
    MAGNIFIC_CONFIG_VERSION,
    MAGNIFIC_EXECUTION_SURFACE,
    MAGNIFIC_PROVIDER_ID,
    MAGNIFIC_RESULT_SCHEMA,
    MagnificExecutionBinding,
    MagnificJobSpec,
    MagnificProvider,
    MagnificReferenceBinding,
    MagnificResultManifest,
)

__all__ = [
    "MAGNIFIC_ADAPTER_VERSION",
    "MAGNIFIC_CONFIG_VERSION",
    "MAGNIFIC_EXECUTION_SURFACE",
    "MAGNIFIC_PROVIDER_ID",
    "MAGNIFIC_RESULT_SCHEMA",
    "MagnificExecutionBinding",
    "MagnificJobSpec",
    "MagnificProvider",
    "MagnificReferenceBinding",
    "MagnificResultManifest",
]
