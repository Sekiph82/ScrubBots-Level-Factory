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
    color_roles: tuple[tuple[str, str], ...] = ()
    accent_color: str | None = None


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
        frontier = sorted({neighbor for index in sorted(patch) for neighbor in canvas.neighbors(index) if neighbor in available})
        if not frontier:
            break
        chosen = rng.choice(frontier)
        patch.add(chosen)
        available.remove(chosen)
    return patch


def _components(available: set[int], canvas: RuleCanvas) -> tuple[tuple[int, ...], ...]:
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
    return tuple(sorted((tuple(sorted(component)) for component in components), key=lambda value: (-len(value), value[0])))


def _contour(occupied: set[int], canvas: RuleCanvas) -> set[int]:
    return {index for index in occupied if any(neighbor not in occupied for neighbor in canvas.neighbors(index))}


def _role_name(color_index: int, color_count: int) -> str:
    if color_index == 0:
        return "NEGATIVE_SPACE"
    if color_index == 1:
        return "OUTLINE"
    if color_index == 2:
        return "BODY"
    if color_index == color_count - 1:
        return "ACCENT"
    return "SECONDARY"


def _seed_candidates(available: set[int], preferred: set[int], canvas: RuleCanvas) -> list[int]:
    candidates = sorted(preferred & available) or sorted(available)
    return sorted(
        candidates,
        key=lambda index: (
            -sum(neighbor in available for neighbor in canvas.neighbors(index)),
            index,
        ),
    )


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
    occupied = set(canvas.occupied)
    if len(occupied) < (len(selected) - 1) * min_region_size:
        raise RuleContractError("RULES occupied geometry cannot accommodate the selected palette")
    cells = [selected[0]] * total
    available = set(occupied)
    contour = _contour(occupied, canvas)
    body = occupied - contour
    patches: dict[str, set[int]] = {}
    # Seed one connected patch per non-base color. Every patch is grown only
    # through occupied cells, so the base color remains an exact negative-space
    # classification and all semantic colors remain geometry-derived.
    for color_index, color in enumerate(selected[1:], start=1):
        role = _role_name(color_index, len(selected))
        preferred = contour if role == "OUTLINE" else body
        if not preferred:
            preferred = occupied
        components = _components(available, canvas)
        viable = [component for component in components if len(component) >= min_region_size]
        if not viable:
            raise RuleContractError("RULES color-region capacity exhausted")
        component = viable[0]
        candidates = _seed_candidates(set(component), preferred, canvas)
        seed = rng.child(f"seed/{role}/{color_index}").choice(candidates[: min(16, len(candidates))])
        patch = _grow_patch(seed, available, canvas, min_region_size, rng.child(f"patch/{role}/{color_index}"))
        if len(patch) < min_region_size:
            raise RuleContractError("RULES color region is smaller than configured minimum")
        patches[color] = patch
        for index in sorted(patch):
            cells[index] = color

    # Flood all remaining occupied cells from the existing semantic patches.
    # A labeled cell is only added adjacent to its own color, preserving
    # connected color regions while keeping assignment deterministic.
    unlabeled = set(available)
    while unlabeled:
        frontier = []
        for index in sorted(unlabeled):
            choices = sorted({cells[neighbor] for neighbor in canvas.neighbors(index) if neighbor in occupied and neighbor not in unlabeled and cells[neighbor] != selected[0]})
            if choices:
                frontier.append((index, choices))
        if frontier:
            index, choices = frontier[0]
            color = choices[0]
            cells[index] = color
            patches[color].add(index)
            unlabeled.remove(index)
            continue
        # An unseeded disconnected geometry component is assigned as one
        # complete component to the accent color; it cannot create a singleton
        # unless the source geometry itself is an invalid singleton component.
        component = _components(unlabeled, canvas)[0]
        # Keep the explicit accent as one connected semantic subregion. Extra
        # disconnected source components belong to outline/secondary support
        # rather than splitting the accent across unrelated structures.
        color = selected[1] if len(selected) >= 4 else selected[-1]
        for index in component:
            cells[index] = color
            patches[color].add(index)
            unlabeled.remove(index)

    components = color_component_sizes(cells, canvas.width, canvas.height)
    if set(cells) != set(selected):
        raise RuleContractError("RULES colorization did not use every selected canonical ID")
    if any(size < min_region_size for sizes in components.values() for size in sizes):
        raise RuleContractError("RULES colorization produced a sub-minimum component")
    largest = max(sum(1 for value in cells if value == color) for color in selected)
    if largest * 100 > max_dominance_pct * total:
        raise RuleContractError("RULES color dominance exceeded configured cap")
    base = selected[0]
    if any((cells[index] == base) != (index not in occupied) for index in range(total)):
        raise RuleContractError("RULES base color is not faithful to RuleCanvas negative space")
    if any(cells[index] != base and index not in occupied for index in range(total)):
        raise RuleContractError("RULES foreground color escaped occupied geometry")
    labels = tuple(canvas._regions.get(index, "NEGATIVE_SPACE") if index in canvas._occupied else "NEGATIVE_SPACE" for index in range(total))
    roles = tuple((color, _role_name(index, len(selected))) for index, color in enumerate(selected))
    accent = selected[-1] if len(selected) >= 4 else None
    return ColorizedRules(tuple(cells), labels, components, largest * 100 / total, roles, accent)
