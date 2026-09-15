import pytest

from scrubbots_pixel_factory.contracts import (
    CURRENT_DIMENSION_SCHEMA_VERSION,
    Difficulty,
    DimensionContractError,
    LEGACY_DIMENSION_SCHEMA_VERSION,
    PRODUCTION_DIMENSION_MAX,
    PRODUCTION_DIMENSION_MIN,
    is_legal_dimensions,
    parse_difficulty,
    resolve_dimensions,
    select_dimensions,
    validate_dimensions,
)


DIFFICULTIES = tuple(Difficulty)
REQUIRED_RECTANGLES = ((20, 20), (20, 59), (59, 20), (59, 59), (23, 47), (52, 31))


@pytest.mark.parametrize("difficulty", DIFFICULTIES)
@pytest.mark.parametrize("width,height", REQUIRED_RECTANGLES)
def test_current_production_envelope_accepts_every_legal_rectangle_for_every_difficulty(difficulty, width, height) -> None:
    assert validate_dimensions(difficulty, width, height) == (width, height)
    assert is_legal_dimensions(difficulty, width, height)


def test_current_envelope_is_exactly_twenty_through_fifty_nine_on_each_axis() -> None:
    assert (PRODUCTION_DIMENSION_MIN, PRODUCTION_DIMENSION_MAX) == (20, 59)
    for difficulty in DIFFICULTIES:
        assert validate_dimensions(difficulty, 20, 59) == (20, 59)
        with pytest.raises(DimensionContractError):
            validate_dimensions(difficulty, 19, 20)
        with pytest.raises(DimensionContractError):
            validate_dimensions(difficulty, 20, 19)
        with pytest.raises(DimensionContractError):
            validate_dimensions(difficulty, 60, 20)
        with pytest.raises(DimensionContractError):
            validate_dimensions(difficulty, 20, 60)


@pytest.mark.parametrize("value", ["EXTRA_HARD", "easy", "Very_Hard", "TEST", "VERYHARD"])
def test_production_difficulty_parser_rejects_aliases_and_legacy_names(value: str) -> None:
    with pytest.raises(DimensionContractError):
        parse_difficulty(value)


def test_current_seeded_selection_is_stable_independent_of_difficulty_and_can_be_rectangular() -> None:
    by_difficulty = {difficulty: [select_dimensions(difficulty, seed) for seed in range(128)] for difficulty in DIFFICULTIES}
    assert all(values == by_difficulty[Difficulty.EASY] for values in by_difficulty.values())
    samples = by_difficulty[Difficulty.EASY]
    assert all(20 <= width <= 59 and 20 <= height <= 59 for width, height in samples)
    assert any(width != height for width, height in samples)
    assert samples == [select_dimensions(Difficulty.EASY, seed) for seed in range(128)]


def test_current_partial_resolution_uses_global_envelope_without_difficulty_coupling() -> None:
    width, height = resolve_dimensions("HARD", width=48, seed="partial")
    assert width == 48 and 20 <= height <= 59
    assert resolve_dimensions("EASY", height=52, seed="partial") == resolve_dimensions("VERY_HARD", height=52, seed="partial")


def test_legacy_schema_one_preserves_historical_difficulty_band_resolution() -> None:
    assert resolve_dimensions("EASY", seed="historical", schema_version=LEGACY_DIMENSION_SCHEMA_VERSION) == resolve_dimensions("EASY", seed="historical", schema_version=1)
    width, height = resolve_dimensions("HARD", width=48, seed="historical", schema_version=1)
    assert width == 48 and 40 <= height <= 49
    with pytest.raises(DimensionContractError):
        validate_dimensions("EASY", 20, 30, schema_version=LEGACY_DIMENSION_SCHEMA_VERSION)
    assert CURRENT_DIMENSION_SCHEMA_VERSION == 2


def test_missing_axis_without_seed_fails_closed() -> None:
    with pytest.raises(DimensionContractError, match="seed"):
        resolve_dimensions("MEDIUM", width=33)
