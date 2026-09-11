"""Optional, lazy PixelLab official-API bridge."""

from .bridge import (
    PIXELLAB_ADAPTER_VERSION,
    PIXELLAB_CONFIG_VERSION,
    PIXELLAB_PROVIDER_ID,
    PIXELLAB_RESULT_SCHEMA,
    PixelLabExecutionBinding,
    PixelLabJobSpec,
    PixelLabProvider,
    PixelLabResultManifest,
    PixelLabRuntimeConfig,
)

__all__ = [
    "PIXELLAB_ADAPTER_VERSION",
    "PIXELLAB_CONFIG_VERSION",
    "PIXELLAB_PROVIDER_ID",
    "PIXELLAB_RESULT_SCHEMA",
    "PixelLabExecutionBinding",
    "PixelLabJobSpec",
    "PixelLabProvider",
    "PixelLabResultManifest",
    "PixelLabRuntimeConfig",
]
