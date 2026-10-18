from __future__ import annotations

import pytest

from scrubbots_pixel_factory.core.request import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.router import GeneratorRouter
from scrubbots_pixel_factory.generators.router.transparent_negative_space import (
    TransparentNegativeSpaceError,
    derive_transparent_negative_space,
)
from scrubbots_pixel_factory.quality.core import QualityPolicy, evaluate_grid


def test_generated_mask_negative_space_becomes_transparent_without_resampling():
    request = GenerationRequest(
        seed=6,
        width=20,
        height=20,
        generator_mode="MASK",
        palette_subset=("C01", "C02", "C03", "C04"),
        generator_options=GeneratorOptions(
            namespace="mask",
            version=1,
            values={"occupancy_floor_pct": 50, "occupancy_ceiling_pct": 75},
        ),
        background_intent="TRANSPARENT",
    )
    generated = GeneratorRouter().generate_candidate(request).result
    original_grid = tuple(generated.logical_grid or ())

    derived = derive_transparent_negative_space(generated)
    report = evaluate_grid(20, 20, derived.result.logical_grid or (), policy=QualityPolicy())

    assert derived.result.request.background_intent == "TRANSPARENT"
    assert (derived.result.width, derived.result.height) == (20, 20)
    assert len(derived.result.logical_grid or ()) == 400
    assert derived.artwork_cell_count >= 200
    assert derived.result.logical_grid.count("VOID") == 400 - derived.artwork_cell_count
    assert len(set(derived.result.logical_grid) - {"VOID"}) == 3
    assert report.accepted
    assert tuple(generated.logical_grid or ()) == original_grid
    assert all(
        old == derived.inferred_background_color if new == "VOID" else old == new
        for old, new in zip(original_grid, derived.result.logical_grid or ())
    )


def test_transparent_derivation_fails_closed_below_void_v2_minimum():
    request = GenerationRequest(
        seed=8,
        width=20,
        height=20,
        generator_mode="RULES",
        palette_subset=("C01", "C02", "C03"),
        background_intent="TRANSPARENT",
    )
    generated = GeneratorRouter().generate_candidate(request).result

    with pytest.raises(TransparentNegativeSpaceError, match="requires 200"):
        derive_transparent_negative_space(generated)
