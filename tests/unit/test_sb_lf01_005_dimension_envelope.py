import pytest

from scrubbots_pixel_factory import (
    Difficulty,
    GenerationRequest,
    GeneratorRouter,
    QualityPolicy,
    evaluate_grid,
    select_dimensions,
    validate_dimensions,
)
from scrubbots_pixel_factory.core import RequestContractError
from scrubbots_pixel_factory.generators.mask import MaskSpriteGenerator


DIFFICULTIES = tuple(Difficulty)
RECTANGLES = ((20, 20), (20, 59), (59, 20), (59, 59), (23, 47), (52, 31))


@pytest.mark.parametrize("difficulty", DIFFICULTIES)
@pytest.mark.parametrize("width,height", RECTANGLES)
def test_request_and_core_accept_all_required_current_rectangles(difficulty, width, height) -> None:
    request = GenerationRequest(difficulty, f"lf01-005-{difficulty.value}-{width}x{height}", "MASK", width=width, height=height)
    assert request.resolve_dimensions() == (width, height)
    assert validate_dimensions(difficulty, width, height) == (width, height)


@pytest.mark.parametrize("difficulty", DIFFICULTIES)
@pytest.mark.parametrize("width,height", ((19, 20), (20, 19), (60, 20), (20, 60)))
def test_request_rejects_each_axis_boundary_independently(difficulty, width, height) -> None:
    with pytest.raises(ValueError):
        GenerationRequest(difficulty, "invalid-boundary", "MASK", width=width, height=height)


def test_automatic_resolution_is_deterministic_separate_by_axis_and_not_difficulty_banded() -> None:
    values = {difficulty: select_dimensions(difficulty, "same-seed") for difficulty in DIFFICULTIES}
    assert len(set(values.values())) == 1
    width, height = values[Difficulty.EASY]
    assert 20 <= width <= 59 and 20 <= height <= 59
    assert select_dimensions(Difficulty.EASY, "same-seed") == select_dimensions(Difficulty.EASY, "same-seed")
    assert any(select_dimensions(Difficulty.EASY, seed)[0] != select_dimensions(Difficulty.EASY, seed)[1] for seed in range(128))


def test_dimension_selection_does_not_change_palette_or_difficulty_semantics() -> None:
    small = GenerationRequest("EASY", "palette-stable", "MASK", width=20, height=20)
    large = GenerationRequest("EASY", "palette-stable", "MASK", width=59, height=59)
    assert small.resolve_palette_subset() == large.resolve_palette_subset()
    cells = ["C01", "C02", "C03"] * (59 * 59 // 3) + ["C01"] * ((59 * 59) % 3)
    assert QualityPolicy(difficulty="EASY").difficulty is Difficulty.EASY
    assert "DIMENSION_MISMATCH" not in evaluate_grid(59, 59, cells, policy=QualityPolicy(difficulty="EASY")).rejection_codes


def test_59x59_mask_generation_is_supported_and_rectangular_core_is_executable() -> None:
    request = GenerationRequest("VERY_HARD", "lf01-005-59x59", "MASK", width=59, height=59)
    result = MaskSpriteGenerator().generate(request)
    assert result.is_success
    assert (result.width, result.height) == (59, 59)
    assert len(result.logical_grid) == 59 * 59


def test_legacy_request_schema_is_explicit_and_current_schema_is_not_an_unversioned_mutation() -> None:
    current = GenerationRequest("EASY", "version-gate", "MASK")
    historical = GenerationRequest("EASY", "version-gate", "MASK", schema_version=1)
    assert current.schema_version == 2 and historical.schema_version == 1
    assert current.resolve_dimensions() != historical.resolve_dimensions()
    with pytest.raises(RequestContractError):
        GenerationRequest("EASY", "version-gate", "MASK", width=20, height=30, schema_version=1)
    assert GenerationRequest("EASY", "version-gate", "MASK", width=20, height=30).resolve_dimensions() == (20, 30)


def test_rectangular_generation_preserves_width_height_identity() -> None:
    request = GenerationRequest("HARD", "router-rectangle", "MASK", width=23, height=47)
    first = GeneratorRouter().generate(request)
    second = GeneratorRouter().generate(request)
    assert first.is_success and second.is_success
    assert first.canonical_bytes() == second.canonical_bytes()
    assert (first.width, first.height) == (23, 47)
