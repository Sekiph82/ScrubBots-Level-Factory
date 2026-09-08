import pytest

from scrubbots_pixel_factory.contracts.color_usage import (
    ColorUsageContractError,
    actual_used_palette_ids,
    count_used_colors,
    resolve_palette_subset,
    select_palette_subset,
    validate_palette_subset,
    validate_used_color_count,
)
from scrubbots_pixel_factory.contracts.difficulty import Difficulty


COLOR_BANDS = {
    Difficulty.EASY: (3, 5),
    Difficulty.MEDIUM: (6, 7),
    Difficulty.HARD: (8, 9),
    Difficulty.VERY_HARD: (10, 12),
}


@pytest.mark.parametrize("difficulty,bounds", COLOR_BANDS.items())
def test_actual_used_color_minimum_and_maximum(difficulty, bounds) -> None:
    minimum, maximum = bounds
    cells = [f"C{i:02d}" for i in range(1, maximum + 1)]
    assert len(validate_used_color_count(difficulty, cells[:minimum])) == minimum
    assert len(validate_used_color_count(difficulty, cells)) == maximum
    with pytest.raises(ColorUsageContractError):
        validate_used_color_count(difficulty, cells[: minimum - 1])
    with pytest.raises(ColorUsageContractError):
        validate_used_color_count(difficulty, cells + [f"C{maximum + 1:02d}"])


def test_duplicate_cells_do_not_inflate_count_and_used_ids_are_sorted() -> None:
    cells = [["C03", "C01"], ["C03", "C02"]]
    assert count_used_colors(cells) == 3
    assert actual_used_palette_ids(cells) == ("C01", "C02", "C03")


@pytest.mark.parametrize("bad_cell", ["BG01", "C17", "#E94B4B", "not-a-color"])
def test_bg01_and_off_palette_cells_are_rejected(bad_cell: str) -> None:
    with pytest.raises(ColorUsageContractError):
        actual_used_palette_ids(["C01", bad_cell])


def test_explicit_subsets_are_validated_and_canonically_ordered() -> None:
    assert validate_palette_subset("EASY", ["C05", "C01", "C03"]) == ("C01", "C03", "C05")
    assert resolve_palette_subset("MEDIUM", subset=[f"C{i:02d}" for i in range(8, 1, -1)]) == tuple(
        f"C{i:02d}" for i in range(2, 9)
    )


@pytest.mark.parametrize(
    "subset",
    [["C01", "C01", "C02"], ["C01", "C02"], ["BG01", "C02", "C03"], ["C01", "C02", "C17"]],
)
def test_invalid_explicit_subsets_fail_closed(subset) -> None:
    with pytest.raises(ColorUsageContractError):
        validate_palette_subset("EASY", subset)


def test_seeded_subsets_are_stable_legal_sorted_and_vary() -> None:
    samples = [select_palette_subset(Difficulty.VERY_HARD, seed) for seed in range(64)]
    assert samples == [select_palette_subset(Difficulty.VERY_HARD, seed) for seed in range(64)]
    assert len(set(samples)) > 1
    assert all(10 <= len(subset) <= 12 for subset in samples)
    assert all(subset == tuple(sorted(subset, key=lambda value: int(value[1:]))) for subset in samples)


def test_subset_requires_seed_when_not_explicit() -> None:
    with pytest.raises(ColorUsageContractError, match="seed"):
        resolve_palette_subset("EASY")
