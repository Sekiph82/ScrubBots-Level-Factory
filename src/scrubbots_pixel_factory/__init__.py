"""Offline-only SCRUBBOTS Pixel Art Generator V1 foundation.

M00 intentionally exposes policy and local smoke utilities only. Generator
families and SCRUBBOTS contract modules belong to later milestones.
"""

from .offline import OfflinePolicyError, guarded_network_request, offline_runtime
from .local import deterministic_digest
from .contracts import (
    BG01,
    CANONICAL_PALETTE,
    ColorUsageContractError,
    Difficulty,
    DimensionContractError,
    PaletteContractError,
    actual_used_palette_ids,
    count_used_colors,
    resolve_dimensions,
    resolve_palette_subset,
    select_dimensions,
    select_palette_subset,
    validate_dimensions,
    validate_palette_subset,
    validate_used_color_count,
)
from .core import (
    DeterministicRNG,
    FailureCode,
    GenerationFailureCode,
    GenerationRequest,
    GenerationResult,
    GeneratorMode,
    GeneratorOptions,
    PixelGenerator,
    RNG_ALGORITHM,
    ResultStatus,
)

__all__ = [
    "OfflinePolicyError",
    "guarded_network_request",
    "offline_runtime",
    "deterministic_digest",
    "BG01",
    "CANONICAL_PALETTE",
    "ColorUsageContractError",
    "Difficulty",
    "DimensionContractError",
    "PaletteContractError",
    "actual_used_palette_ids",
    "count_used_colors",
    "resolve_dimensions",
    "resolve_palette_subset",
    "select_dimensions",
    "select_palette_subset",
    "validate_dimensions",
    "validate_palette_subset",
    "validate_used_color_count",
    "DeterministicRNG",
    "FailureCode",
    "GenerationFailureCode",
    "GenerationRequest",
    "GenerationResult",
    "GeneratorMode",
    "GeneratorOptions",
    "PixelGenerator",
    "RNG_ALGORITHM",
    "ResultStatus",
]

__version__ = "0.1.0"
OFFLINE_ONLY = True
