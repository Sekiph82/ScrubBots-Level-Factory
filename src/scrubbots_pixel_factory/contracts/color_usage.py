"""Actual-used-color legality and deterministic canonical subset selection."""

from collections.abc import Iterable

from ._stable_select import stable_digest, stable_index, validate_seed
from .difficulty import Difficulty, parse_difficulty
from .palette import CANONICAL_PALETTE, PaletteContractError


class ColorUsageContractError(ValueError):
    """Raised when logical cell colors or a palette subset is illegal."""


def _flatten_cells(cells: object) -> Iterable[object]:
    if isinstance(cells, str):
        yield cells
        return
    if isinstance(cells, (bytes, bytearray)):
        raise ColorUsageContractError("logical cells must use canonical C-ID strings")
    try:
        iterator = iter(cells)  # type: ignore[arg-type]
    except TypeError:
        yield cells
        return
    for cell in iterator:
        if isinstance(cell, str):
            yield cell
        else:
            yield from _flatten_cells(cell)


def actual_used_palette_ids(cells: object) -> tuple[str, ...]:
    try:
        return CANONICAL_PALETTE.used_ids(_flatten_cells(cells))
    except PaletteContractError as exc:
        raise ColorUsageContractError(str(exc)) from exc


def count_used_colors(cells: object) -> int:
    return len(actual_used_palette_ids(cells))


def validate_used_color_count(difficulty: Difficulty | str, cells: object) -> tuple[str, ...]:
    parse_difficulty(difficulty)
    used = actual_used_palette_ids(cells)
    minimum, maximum = CANONICAL_PALETTE.used_color_envelope
    if not minimum <= len(used) <= maximum:
        raise ColorUsageContractError(
            f"V1 used-color envelope requires {minimum}..{maximum} distinct used colors; received {len(used)}"
        )
    return used


def validate_palette_subset(difficulty: Difficulty | str, subset: Iterable[str]) -> tuple[str, ...]:
    parse_difficulty(difficulty)
    if isinstance(subset, str):
        raise ColorUsageContractError("explicit palette subset must be an iterable of C-ID strings")
    try:
        values = tuple(subset)
    except TypeError as exc:
        raise ColorUsageContractError("explicit palette subset must be iterable") from exc
    try:
        has_duplicates = len(set(values)) != len(values)
    except TypeError as exc:
        raise ColorUsageContractError("explicit palette subset must contain C-ID strings") from exc
    if has_duplicates:
        raise ColorUsageContractError("explicit palette subset contains duplicate IDs")
    try:
        for value in values:
            CANONICAL_PALETTE.validate_logical_id(value)
    except (PaletteContractError, TypeError) as exc:
        raise ColorUsageContractError(str(exc)) from exc
    minimum, maximum = CANONICAL_PALETTE.used_color_envelope
    if not minimum <= len(values) <= maximum:
        raise ColorUsageContractError(
            f"explicit palette subset must contain {minimum}..{maximum} IDs; received {len(values)}"
        )
    return tuple(sorted(values, key=lambda value: int(value[1:])))


def select_palette_subset(difficulty: Difficulty | str, seed: int | str) -> tuple[str, ...]:
    """Select a stable legal subset and return it in canonical ascending order."""

    parse_difficulty(difficulty)
    validate_seed(seed)
    minimum, maximum = CANONICAL_PALETTE.used_color_envelope
    size = minimum + stable_index("palette-subset.size", seed, maximum - minimum + 1)
    ranked = sorted(
        CANONICAL_PALETTE.ids,
        key=lambda value: (stable_digest("palette-subset.member", seed, value), value),
    )
    chosen = ranked[:size]
    return tuple(sorted(chosen, key=lambda value: int(value[1:])))


def resolve_palette_subset(
    difficulty: Difficulty | str,
    *,
    seed: int | str | None = None,
    subset: Iterable[str] | None = None,
) -> tuple[str, ...]:
    if subset is not None:
        return validate_palette_subset(difficulty, subset)
    if seed is None:
        raise ColorUsageContractError("seed is required when palette subset is not supplied")
    return select_palette_subset(difficulty, seed)
