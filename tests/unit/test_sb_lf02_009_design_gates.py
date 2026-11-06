"""Unresolved generation semantics stay outside the supported request contract."""

from __future__ import annotations

import pytest

from scrubbots_pixel_factory.core import GenerationRequest, RequestContractError


@pytest.mark.parametrize(
    "unsupported_mode",
    ("PUZZLE_FIRST", "REVERSE_CONSTRUCTION", "DEPENDENCY_FIRST", "SLOT_STACK"),
)
def test_design_gated_generation_modes_are_rejected_before_dispatch(unsupported_mode: str) -> None:
    with pytest.raises(RequestContractError, match="generator_mode must be exactly"):
        GenerationRequest(
            seed="m02-design-gate",
            width=56,
            height=56,
            generator_mode=unsupported_mode,
        )
