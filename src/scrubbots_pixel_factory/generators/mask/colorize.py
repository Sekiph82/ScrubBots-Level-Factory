"""Deterministic geometry-derived semantic roles and connected coloring."""

from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from ...contracts import CANONICAL_PALETTE
from ...core.rng import DeterministicRNG
from .model import MaskContractError, ResolvedMask


class ColorRole(str, Enum):
    NEGATIVE_SPACE = "NEGATIVE_SPACE"
    OUTLINE = "OUTLINE"
    BODY_PRIMARY = "BODY_PRIMARY"
    SECONDARY = "SECONDARY"
    DETAIL_ACCENT = "DETAIL_ACCENT"


@dataclass(frozen=True, slots=True)
class ColorizedMask:
    """Final C-ID grid plus internal role diagnostics, never serialized as cells."""

    cells: tuple[str, ...]
    roles: tuple[ColorRole, ...]
    role_colors: tuple[tuple[ColorRole, str], ...]


def _validate_selected_palette(palette: Sequence[str]) -> tuple[str, ...]:
    if isinstance(palette, (str, bytes, bytearray)) or not isinstance(palette, Sequence):
        raise MaskContractError("selected palette must be an ordered C-ID sequence")
    selected = tuple(palette)
    if not 3 <= len(selected) <= 12 or len(set(selected)) != len(selected):
        raise MaskContractError("selected palette must contain 3..12 unique IDs")
    for color_id in selected:
        CANONICAL_PALETTE.validate_logical_id(color_id)
    return tuple(sorted(selected, key=lambda value: int(value[1:])))


def _neighbors(index: int, width: int, height: int) -> tuple[int, ...]:
    x, y = index % width, index // width
    result = []
    if x:
        result.append(index - 1)
    if x + 1 < width:
        result.append(index + 1)
    if y:
        result.append(index - width)
    if y + 1 < height:
        result.append(index + width)
    return tuple(result)


def _components(cells: Sequence[object], width: int, height: int, value: object) -> tuple[tuple[int, ...], ...]:
    matching = {index for index, cell in enumerate(cells) if cell == value}
    found: set[int] = set()
    components: list[tuple[int, ...]] = []
    for start in sorted(matching):
        if start in found:
            continue
        queue = deque([start])
        found.add(start)
        component = []
        while queue:
            index = queue.popleft()
            component.append(index)
            for neighbor in _neighbors(index, width, height):
                if neighbor in matching and neighbor not in found:
                    found.add(neighbor)
                    queue.append(neighbor)
        components.append(tuple(component))
    return tuple(components)


def color_component_sizes(cells: Sequence[str], width: int, height: int) -> dict[str, tuple[int, ...]]:
    """Return deterministic 4-neighbor component sizes for each rendered C-ID."""
    if len(cells) != width * height:
        raise MaskContractError("color component grid dimensions are inconsistent")
    return {
        color: tuple(sorted((len(component) for component in _components(cells, width, height, color)), reverse=True))
        for color in sorted(set(cells), key=lambda value: int(value[1:]))
    }


def _role_for_index(index: int, width: int, height: int, foreground: set[int]) -> ColorRole:
    x, y = index % width, index // width
    if x in (0, width - 1) or y in (0, height - 1) or any(neighbor not in foreground for neighbor in _neighbors(index, width, height)):
        return ColorRole.OUTLINE
    if (x * 3 + y * 5) % 11 == 0:
        return ColorRole.DETAIL_ACCENT
    if (x * 5 + y * 3) % 7 == 0:
        return ColorRole.SECONDARY
    return ColorRole.BODY_PRIMARY


def _pair_candidates(indices: set[int], width: int, height: int) -> list[tuple[int, int]]:
    pairs = []
    for index in sorted(indices):
        for neighbor in _neighbors(index, width, height):
            if neighbor > index and neighbor in indices:
                pairs.append((index, neighbor))
    return pairs


def _preferred_role(color_index: int) -> ColorRole:
    if color_index == 0:
        return ColorRole.OUTLINE
    if color_index == 1:
        return ColorRole.BODY_PRIMARY
    if color_index == 2:
        return ColorRole.SECONDARY
    return ColorRole.DETAIL_ACCENT


def colorize_with_roles(mask: ResolvedMask, palette: Sequence[str], rng: DeterministicRNG) -> ColorizedMask:
    """Color a mask with connected seeded regions and geometry-derived roles."""
    selected = _validate_selected_palette(palette)
    if not isinstance(rng, DeterministicRNG):
        raise MaskContractError("colorization requires the project DeterministicRNG")
    foreground = {index for index, value in enumerate(mask.foreground_cells) if value}
    if len(foreground) < 2 * (len(selected) - 1):
        raise MaskContractError("foreground has too few cells for the selected palette regions")
    foreground_components = _components(mask.foreground_cells, mask.width, mask.height, True)
    if any(len(component) < 2 for component in foreground_components):
        raise MaskContractError("foreground contains a singleton geometric component")

    background_color = selected[rng.randbelow(len(selected))]
    foreground_colors = [color for color in selected if color != background_color]
    labels: dict[int, tuple[str, ColorRole]] = {}
    available = set(foreground)
    pair_stream = rng.child("region-seeds")
    all_pairs = _pair_candidates(foreground, mask.width, mask.height)
    for color_index, color in enumerate(foreground_colors):
        role = _preferred_role(color_index)
        preferred = [
            pair for pair in all_pairs
            if pair[0] in available and pair[1] in available
            and (role is not ColorRole.OUTLINE or _role_for_index(pair[0], mask.width, mask.height, foreground) is ColorRole.OUTLINE)
        ]
        candidates = preferred or [pair for pair in all_pairs if pair[0] in available and pair[1] in available]
        if not candidates:
            raise MaskContractError("foreground cannot allocate connected palette regions")
        pair = pair_stream.shuffle(candidates)[0]
        for index in pair:
            labels[index] = (color, _role_for_index(index, mask.width, mask.height, foreground))
            available.remove(index)

    for component in foreground_components:
        if not any(index in labels for index in component):
            pairs = [pair for pair in _pair_candidates(set(component), mask.width, mask.height) if pair[0] in available and pair[1] in available]
            if not pairs:
                raise MaskContractError("foreground island cannot receive a connected color region")
            for index in pairs[0]:
                labels[index] = (foreground_colors[0], _role_for_index(index, mask.width, mask.height, foreground))
                available.remove(index)

    while available:
        frontier = [
            index for index in available
            if any(neighbor in labels for neighbor in _neighbors(index, mask.width, mask.height))
        ]
        if not frontier:
            raise MaskContractError("foreground region propagation lost connectivity")
        index = max(
            frontier,
            key=lambda candidate: (
                sum(neighbor in labels for neighbor in _neighbors(candidate, mask.width, mask.height)),
                -candidate,
            ),
        )
        adjacent = [labels[neighbor] for neighbor in _neighbors(index, mask.width, mask.height) if neighbor in labels]
        counts = {color: sum(1 for label, _ in adjacent if label == color) for color in foreground_colors}
        selected_color = max(foreground_colors, key=lambda color: (counts[color], -foreground_colors.index(color)))
        labels[index] = (selected_color, _role_for_index(index, mask.width, mask.height, foreground))
        available.remove(index)

    cells = [background_color] * (mask.width * mask.height)
    roles = [ColorRole.NEGATIVE_SPACE] * (mask.width * mask.height)
    for index, (color, role) in labels.items():
        cells[index] = color
        roles[index] = role
    if set(cells) != set(selected):
        raise MaskContractError("colorization did not use every selected palette ID")
    component_sizes = color_component_sizes(cells, mask.width, mask.height)
    if any(size == 1 for sizes in component_sizes.values() for size in sizes):
        raise MaskContractError(f"colorization produced a singleton color component: {component_sizes}")
    role_colors = tuple((role, color) for role, color in zip(
        (ColorRole.NEGATIVE_SPACE, ColorRole.OUTLINE, ColorRole.BODY_PRIMARY, ColorRole.SECONDARY, ColorRole.DETAIL_ACCENT),
        (background_color, *foreground_colors[:4]),
    ))
    return ColorizedMask(tuple(cells), tuple(roles), role_colors)


def colorize_mask(mask: ResolvedMask, palette: Sequence[str], rng: DeterministicRNG) -> tuple[str, ...]:
    """Map internal geometry to only selected canonical C-IDs."""
    return colorize_with_roles(mask, palette, rng).cells
