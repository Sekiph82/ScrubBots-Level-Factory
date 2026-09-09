"""Region-driven canonical color assignment for M04 logical canvases."""

from collections import deque
from dataclasses import dataclass

from ...contracts import CANONICAL_PALETTE
from ...core import DeterministicRNG
from .model import RuleCanvas, RuleContractError


@dataclass(frozen=True, slots=True)
class ColorizedRules:
    cells: tuple[str, ...]
    region_labels: tuple[str, ...]
    color_components: dict[str, tuple[int, ...]]
    max_dominance_pct: float


def color_component_sizes(cells: tuple[str, ...] | list[str], width: int, height: int) -> dict[str, tuple[int, ...]]:
    if len(cells) != width * height:
        raise RuleContractError("RULES color grid dimensions are inconsistent")
    remaining_by_color = {color: {index for index, value in enumerate(cells) if value == color} for color in sorted(set(cells), key=lambda value: int(value[1:]))}
    result: dict[str, tuple[int, ...]] = {}
    for color, remaining in remaining_by_color.items():
        sizes: list[int] = []
        while remaining:
            start = min(remaining)
            remaining.remove(start)
            queue = deque([start])
            size = 1
            while queue:
                index = queue.popleft()
                x, y = index % width, index // width
                neighbors = []
                if x: neighbors.append(index - 1)
                if x + 1 < width: neighbors.append(index + 1)
                if y: neighbors.append(index - width)
                if y + 1 < height: neighbors.append(index + width)
                for neighbor in neighbors:
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        queue.append(neighbor)
                        size += 1
            sizes.append(size)
        result[color] = tuple(sorted(sizes, reverse=True))
    return result


def _grow_patch(seed: int, available: set[int], canvas: RuleCanvas, target: int, rng: DeterministicRNG) -> set[int]:
    patch = {seed}
    available.remove(seed)
    for _ in range(max(0, target - 1)):
        frontier = sorted({neighbor for index in patch for neighbor in canvas.neighbors(index) if neighbor in available})
        if not frontier:
            break
        chosen = rng.choice(frontier)
        patch.add(chosen)
        available.remove(chosen)
    return patch


def _largest_available_component(available: set[int], canvas: RuleCanvas) -> set[int]:
    remaining = set(available)
    components: list[set[int]] = []
    while remaining:
        start = min(remaining)
        remaining.remove(start)
        component = {start}
        frontier = [start]
        while frontier:
            current = frontier.pop()
            for neighbor in canvas.neighbors(current):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    frontier.append(neighbor)
        components.append(component)
    return max(components, key=lambda value: (len(value), -min(value)), default=set())


def colorize_canvas(canvas: RuleCanvas, palette: tuple[str, ...] | list[str], rng: DeterministicRNG, *, min_region_size: int = 2, max_dominance_pct: int = 82) -> ColorizedRules:
    if not isinstance(canvas, RuleCanvas) or not isinstance(rng, DeterministicRNG):
        raise RuleContractError("RULES colorization requires RuleCanvas and project DeterministicRNG")
    selected = tuple(sorted(palette, key=lambda value: int(value[1:])))
    if not 3 <= len(selected) <= 12 or len(set(selected)) != len(selected):
        raise RuleContractError("RULES palette must contain 3..12 unique canonical IDs")
    for color in selected:
        CANONICAL_PALETTE.validate_logical_id(color)
    if min_region_size < 2 or not 50 <= max_dominance_pct <= 100:
        raise RuleContractError("RULES color-region bounds are invalid")
    total = canvas.size
    max_count = total * max_dominance_pct // 100
    cells = [selected[0]] * total
    available = set(range(total))
    patches: dict[str, set[int]] = {}
    target = max(min_region_size, total // (2 * len(selected)))
    for color_index, color in enumerate(selected[1:]):
        component = _largest_available_component(available, canvas)
        preferred = sorted(set(canvas.occupied) & component)
        candidates = preferred or sorted(component)
        if not candidates:
            raise RuleContractError("RULES color-region capacity exhausted")
        # Prefer a cell with a broad available frontier. This keeps every
        # seeded patch growable even when geometry is a one-cell contour.
        ranked = sorted(
            candidates,
            key=lambda index: (-sum(neighbor in available for neighbor in canvas.neighbors(index)), index),
        )
        seed = rng.child(f"seed/{color_index}").choice(ranked[: min(16, len(ranked))])
        patch = _grow_patch(seed, available, canvas, min(target, max_count), rng.child(f"patch/{color_index}"))
        if len(patch) < min_region_size:
            raise RuleContractError("RULES accent region is smaller than configured minimum")
        patches[color] = patch
        for index in patch:
            cells[index] = color
    # Keep the base/negative-space color below the documented cap by growing the
    # final coherent region through adjacent remaining cells.
    base_remaining = {index for index, color in enumerate(cells) if color == selected[0]}
    if len(base_remaining) > max_count:
        grow_color = selected[-1]
        grow = set(patches[grow_color])
        need = len(base_remaining) - max_count
        for _ in range(need):
            frontier = sorted({neighbor for index in grow for neighbor in range(total) if neighbor in base_remaining and neighbor in canvas.neighbors(index)})
            if not frontier:
                raise RuleContractError("RULES base dominance cannot be reduced coherently")
            index = frontier[0]
            grow.add(index)
            base_remaining.remove(index)
            cells[index] = grow_color
        patches[grow_color] = grow
    components = color_component_sizes(cells, canvas.width, canvas.height)
    # Merge any accidental one-cell base island into the adjacent largest patch.
    for color, sizes in components.items():
        if color != selected[0] or all(size >= min_region_size for size in sizes):
            continue
        visited: set[int] = set()
        for index in range(total):
            if cells[index] != color or index in visited:
                continue
            same = {index}
            frontier = [index]
            while frontier:
                current = frontier.pop()
                for neighbor in canvas.neighbors(current):
                    if neighbor not in same and cells[neighbor] == color:
                        same.add(neighbor)
                        frontier.append(neighbor)
            visited.update(same)
            if len(same) != 1:
                continue
            neighbor_colors = [cells[neighbor] for neighbor in canvas.neighbors(index) if cells[neighbor] != color]
            if neighbor_colors:
                cells[index] = min(neighbor_colors, key=lambda value: (neighbor_colors.count(value), value))
    components = color_component_sizes(cells, canvas.width, canvas.height)
    if set(cells) != set(selected):
        raise RuleContractError("RULES colorization did not use every selected canonical ID")
    if any(size < min_region_size for sizes in components.values() for size in sizes):
        raise RuleContractError("RULES colorization produced a sub-minimum component")
    largest = max(sum(1 for value in cells if value == color) for color in selected)
    if largest > max_count:
        raise RuleContractError("RULES color dominance exceeded configured cap")
    labels = tuple(canvas._regions.get(index, "NEGATIVE") if index in canvas._occupied else "NEGATIVE" for index in range(total))
    return ColorizedRules(tuple(cells), labels, components, largest * 100 / total)
