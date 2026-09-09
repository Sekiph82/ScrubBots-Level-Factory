"""Deterministic coherent region coloring for resolved logical masks."""

from collections.abc import Sequence

from ...contracts import CANONICAL_PALETTE
from ...core.rng import DeterministicRNG
from .engine import classify_coordinates
from .model import MaskContractError, ResolvedMask


def _validate_selected_palette(palette: Sequence[str]) -> tuple[str, ...]:
    if isinstance(palette, (str, bytes, bytearray)) or not isinstance(palette, Sequence):
        raise MaskContractError("selected palette must be an ordered C-ID sequence")
    selected = tuple(palette)
    if not 3 <= len(selected) <= 12 or len(set(selected)) != len(selected):
        raise MaskContractError("selected palette must contain 3..12 unique IDs")
    for color_id in selected:
        CANONICAL_PALETTE.validate_logical_id(color_id)
    return tuple(sorted(selected, key=lambda value: int(value[1:])))


def colorize_mask(mask: ResolvedMask, palette: Sequence[str], rng: DeterministicRNG) -> tuple[str, ...]:
    """Map internal foreground/negative-space classes to only the selected C-IDs."""
    selected = _validate_selected_palette(palette)
    if not isinstance(rng, DeterministicRNG):
        raise MaskContractError("colorization requires the project DeterministicRNG")
    foreground = list(classify_coordinates(mask, True))
    if len(foreground) < len(selected) - 1:
        raise MaskContractError("foreground has too few cells for the selected palette")
    background_color = selected[rng.randbelow(len(selected))]
    foreground_colors = [color for color in selected if color != background_color]
    ordered = rng.shuffle(foreground)
    anchors = ordered[: len(foreground_colors)]
    anchor_colors = dict(zip(anchors, foreground_colors, strict=True))
    cells = [background_color] * (mask.width * mask.height)
    for x, y in foreground:
        if (x, y) in anchor_colors:
            cells[y * mask.width + x] = anchor_colors[(x, y)]
            continue
        nearest = min(
            anchors,
            key=lambda point: (abs(point[0] - x) + abs(point[1] - y), point[1], point[0]),
        )
        cells[y * mask.width + x] = anchor_colors[nearest]
    if set(cells) != set(selected):
        raise MaskContractError("colorization did not use every selected palette ID")
    return tuple(cells)
