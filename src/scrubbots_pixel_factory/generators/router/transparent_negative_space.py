"""Explicitly derive transparent negative space from a generated logical grid."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from ...contracts.palette import VOID_CELL_ID
from ...core.result import GenerationResult
from ...quality.core import QualityPolicy, analyze_grid, evaluate_grid, logical_grid_hash


MIN_VOID_ARTWORK_CELLS = 200
MIN_VOID_ARTWORK_RATIO = 0.25


class TransparentNegativeSpaceError(ValueError):
    """Raised when a generated grid cannot safely express transparent space."""


@dataclass(frozen=True, slots=True)
class TransparentNegativeSpaceDerivation:
    result: GenerationResult
    inferred_background_color: str
    source_grid_sha256: str
    artwork_cell_count: int


def derive_transparent_negative_space(
    result: GenerationResult,
) -> TransparentNegativeSpaceDerivation:
    """Replace only the quality analyzer's inferred negative-space color with VOID.

    Dimensions and every non-background logical cell remain unchanged. The
    derived result is accepted only when the current VOID V2 artwork and normal
    structural quality requirements still pass.
    """

    if not isinstance(result, GenerationResult) or not result.is_success:
        raise TransparentNegativeSpaceError("a successful GenerationResult is required")
    request = result.request
    if request is None or request.background_intent != "TRANSPARENT":
        raise TransparentNegativeSpaceError("the request must explicitly declare TRANSPARENT background intent")
    if result.width is None or result.height is None or result.logical_grid is None:
        raise TransparentNegativeSpaceError("successful generation result is missing its logical grid")

    source_grid = tuple(result.logical_grid)
    source_quality = evaluate_grid(result.width, result.height, source_grid, policy=QualityPolicy())
    if not source_quality.accepted or source_quality.analysis is None:
        raise TransparentNegativeSpaceError("opaque generated source does not pass the current structural quality policy")
    background = source_quality.analysis.negative_space.inferred_color
    if background not in result.used_palette:
        raise TransparentNegativeSpaceError("quality analyzer inferred a background outside the generated palette")

    cells = tuple(VOID_CELL_ID if color == background else color for color in source_grid)
    artwork_count = len(cells) - cells.count(VOID_CELL_ID)
    required_count = max(MIN_VOID_ARTWORK_CELLS, math.ceil(result.width * result.height * MIN_VOID_ARTWORK_RATIO))
    if artwork_count < required_count:
        raise TransparentNegativeSpaceError(
            f"transparent artwork has {artwork_count} cells; current VOID V2 requires {required_count}"
        )
    if len(set(cells) - {VOID_CELL_ID}) < 3:
        raise TransparentNegativeSpaceError("transparent artwork must retain at least three gameplay colors")

    final_quality = evaluate_grid(result.width, result.height, cells, policy=QualityPolicy())
    if not final_quality.accepted:
        raise TransparentNegativeSpaceError(
            "transparent derived grid fails current structural quality policy: "
            + ", ".join(final_quality.rejection_codes)
        )

    transparent_request = replace(request, background_intent="TRANSPARENT")
    derived = GenerationResult.success(
        request=transparent_request,
        width=result.width,
        height=result.height,
        logical_grid=cells,
        generator_id="transparent-negative-space-v1",
        generator_version="1",
        generator_mode=result.generator_mode,
        seed=result.seed,
        rng_algorithm=str(result.rng_algorithm),
        provenance=result.provenance or {},
    )
    return TransparentNegativeSpaceDerivation(
        result=derived,
        inferred_background_color=background,
        source_grid_sha256=logical_grid_hash(result.width, result.height, source_grid),
        artwork_cell_count=artwork_count,
    )


__all__ = [
    "MIN_VOID_ARTWORK_CELLS",
    "MIN_VOID_ARTWORK_RATIO",
    "TransparentNegativeSpaceDerivation",
    "TransparentNegativeSpaceError",
    "derive_transparent_negative_space",
]
