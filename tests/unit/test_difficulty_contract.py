import pytest

from scrubbots_pixel_factory.contracts.difficulty import (
    Difficulty,
    DimensionContractError,
    is_legal_dimensions,
    parse_difficulty,
    resolve_dimensions,
    select_dimensions,
    validate_dimensions,
)


BANDS = {
    Difficulty.EASY: (20, 29),
    Difficulty.MEDIUM: (30, 39),
    Difficulty.HARD: (40, 49),
    Difficulty.VERY_HARD: (50, 59),
}


@pytest.mark.parametrize("difficulty,bounds", BANDS.items())
def test_each_difficulty_accepts_independent_boundary_axes(difficulty, bounds) -> None:
    minimum, maximum = bounds
    assert validate_dimensions(difficulty, minimum, maximum) == (minimum, maximum)
    assert validate_dimensions(difficulty, maximum, minimum) == (maximum, minimum)
    assert is_legal_dimensions(difficulty, minimum, maximum)


@pytest.mark.parametrize("value", [19, 60])
def test_outer_boundaries_are_rejected_for_every_difficulty(value: int) -> None:
    for difficulty, (minimum, maximum) in BANDS.items():
        with pytest.raises(DimensionContractError):
            validate_dimensions(difficulty, value, minimum)
        with pytest.raises(DimensionContractError):
            validate_dimensions(difficulty, minimum, value)


@pytest.mark.parametrize(
    "difficulty,width,height",
    [
        (Difficulty.EASY, 20, 30),
        (Difficulty.MEDIUM, 39, 40),
        (Difficulty.HARD, 49, 50),
        (Difficulty.VERY_HARD, 49, 59),
    ],
)
def test_cross_band_rectangles_fail_on_either_axis(difficulty, width, height) -> None:
    with pytest.raises(DimensionContractError):
        validate_dimensions(difficulty, width, height)


@pytest.mark.parametrize("value", ["EXTRA_HARD", "easy", "Very_Hard", "TEST", "VERYHARD"])
def test_production_difficulty_parser_rejects_aliases_and_legacy_names(value: str) -> None:
    with pytest.raises(DimensionContractError):
        parse_difficulty(value)


def test_seeded_dimension_selection_is_stable_and_can_be_rectangular() -> None:
    samples = [select_dimensions(Difficulty.MEDIUM, seed) for seed in range(64)]
    assert samples == [select_dimensions(Difficulty.MEDIUM, seed) for seed in range(64)]
    assert all(30 <= width <= 39 and 30 <= height <= 39 for width, height in samples)
    assert any(width != height for width, height in samples)


def test_resolve_dimensions_supports_explicit_and_partial_values() -> None:
    assert resolve_dimensions("HARD", 48, 41) == (48, 41)
    width, height = resolve_dimensions("EASY", width=22, seed="partial")
    assert width == 22 and 20 <= height <= 29


def test_missing_axis_without_seed_fails_closed() -> None:
    with pytest.raises(DimensionContractError, match="seed"):
        resolve_dimensions("MEDIUM", width=33)
