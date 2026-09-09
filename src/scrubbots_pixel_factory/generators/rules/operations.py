"""Bounded logical growth, morphology, fragmentation, and rewrite operations."""

from dataclasses import dataclass

from ...core import DeterministicRNG
from .model import RuleCanvas, RuleContractError


OPERATION_NAMES = (
    "SEEDED_FRONTIER_GROWTH", "CONSTRAINED_CONNECTED_GROWTH", "EROSION", "DILATION",
    "HOLE_CARVING", "CONTOUR_EXTRACTION", "NESTED_REGION", "CONTROLLED_FRAGMENTATION",
    "LOCAL_REWRITE", "BOUNDED_REPEAT",
)


def connected_components(indices: set[int] | frozenset[int], canvas: RuleCanvas) -> tuple[tuple[int, ...], ...]:
    remaining = set(indices)
    components: list[tuple[int, ...]] = []
    while remaining:
        start = min(remaining)
        remaining.remove(start)
        queue = [start]
        component = [start]
        while queue:
            current = queue.pop(0)
            for neighbor in canvas.neighbors(current):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
                    component.append(neighbor)
        components.append(tuple(sorted(component)))
    return tuple(components)


def seeded_frontier_growth(canvas: RuleCanvas, seeds: set[int] | frozenset[int], target: int, rng: DeterministicRNG, *, label: str = "growth", allowed: set[int] | frozenset[int] | None = None) -> set[int]:
    if not isinstance(rng, DeterministicRNG) or isinstance(target, bool) or not isinstance(target, int) or target < 1:
        raise RuleContractError("growth requires a positive target and project RNG")
    region = set(seeds)
    if not region or not region.issubset(set(range(canvas.size))):
        raise RuleContractError("growth seeds must be non-empty and in bounds")
    eligible = set(range(canvas.size)) if allowed is None else set(allowed)
    if not region.issubset(eligible):
        raise RuleContractError("growth seeds must be eligible")
    region.difference_update(canvas.protected_negative)
    for _ in range(max(0, target - len(region))):
        frontier = sorted({neighbor for index in region for neighbor in canvas.neighbors(index) if neighbor in eligible and neighbor not in region and neighbor not in canvas.protected_negative})
        if not frontier:
            break
        region.add(rng.choice(frontier))
    if len(region) < target:
        raise RuleContractError("seeded frontier growth could not reach target within bounds")
    canvas.mark_many(region, label)
    return region


def constrained_connected_growth(canvas: RuleCanvas, seeds: set[int] | frozenset[int], target_min: int, target_max: int, rng: DeterministicRNG, *, allowed: set[int] | frozenset[int] | None = None, label: str = "constrained") -> set[int]:
    if isinstance(target_min, bool) or isinstance(target_max, bool) or not isinstance(target_min, int) or not isinstance(target_max, int) or not 1 <= target_min <= target_max:
        raise RuleContractError("connected growth bounds are invalid")
    result = seeded_frontier_growth(canvas, seeds, target_min, rng.child("minimum"), label=label, allowed=allowed)
    for _ in range(target_max - target_min):
        frontier = sorted({neighbor for index in result for neighbor in canvas.neighbors(index) if neighbor not in result and (allowed is None or neighbor in allowed) and neighbor not in canvas.protected_negative})
        if not frontier:
            break
        chosen = rng.choice(frontier)
        result.add(chosen)
        canvas.mark(chosen, label)
    return result


def erosion(canvas: RuleCanvas, region: set[int] | frozenset[int], iterations: int = 1) -> set[int]:
    if isinstance(iterations, bool) or not isinstance(iterations, int) or not 0 <= iterations <= 32:
        raise RuleContractError("erosion iterations must be bounded to 0..32")
    result = set(region)
    for _ in range(iterations):
        boundary = {index for index in result if any(neighbor not in result for neighbor in canvas.neighbors(index))}
        removable = boundary - set(canvas.protected_occupied)
        if not removable or len(result - removable) < 1:
            break
        result.difference_update(removable)
    for index in set(region) - result:
        canvas.carve(index)
    return result


def dilation(canvas: RuleCanvas, region: set[int] | frozenset[int], iterations: int = 1, *, label: str = "dilation") -> set[int]:
    if isinstance(iterations, bool) or not isinstance(iterations, int) or not 0 <= iterations <= 32:
        raise RuleContractError("dilation iterations must be bounded to 0..32")
    result = set(region)
    for _ in range(iterations):
        result.update(neighbor for index in sorted(result) for neighbor in canvas.neighbors(index) if neighbor not in canvas.protected_negative)
    canvas.mark_many(result - set(canvas.protected_negative), label)
    return result


def hole_carving(canvas: RuleCanvas, region: set[int] | frozenset[int], holes: tuple[set[int], ...], *, minimum_size: int = 2) -> set[int]:
    if minimum_size < 2:
        raise RuleContractError("holes must have minimum size two")
    result = set(region)
    for hole in holes:
        if len(hole) < minimum_size or not hole.issubset(result) or hole.intersection(canvas.protected_occupied):
            raise RuleContractError("hole violates protected or minimum-size contract")
        result.difference_update(hole)
        for index in sorted(hole):
            canvas.carve(index)
    return result


def contour_extraction(canvas: RuleCanvas, region: set[int] | frozenset[int]) -> set[int]:
    selected = set(region)
    return {index for index in selected if any(neighbor not in selected for neighbor in canvas.neighbors(index))}


def nested_region(canvas: RuleCanvas, parent: set[int] | frozenset[int], target: int, rng: DeterministicRNG, *, label: str = "nested") -> set[int]:
    parent_set = set(parent)
    if target < 2 or not parent_set:
        raise RuleContractError("nested region requires a non-empty parent and target >=2")
    seed = min(parent_set)
    return seeded_frontier_growth(canvas, {seed}, min(target, len(parent_set)), rng, label=label, allowed=parent_set)


def controlled_fragmentation(canvas: RuleCanvas, region: set[int] | frozenset[int], max_fragments: int, min_fragment_size: int = 2, rng: DeterministicRNG | None = None, *, label: str = "fragment") -> dict[int, set[int]]:
    if isinstance(max_fragments, bool) or not isinstance(max_fragments, int) or not 1 <= max_fragments <= 16 or min_fragment_size < 2:
        raise RuleContractError("fragmentation bounds are invalid")
    source = sorted(region)
    if len(source) < max_fragments * min_fragment_size:
        raise RuleContractError("region is too small for requested coherent fragments")
    stream = rng or DeterministicRNG(0).child("fragmentation")
    seeds = [source[(index * len(source)) // max_fragments] for index in range(max_fragments)]
    fragments = {index: set() for index in range(max_fragments)}
    for cell in source:
        winner = min(
            range(max_fragments),
            key=lambda index: (
                abs(cell % canvas.width - seeds[index] % canvas.width)
                + abs(cell // canvas.width - seeds[index] // canvas.width),
                index,
            ),
        )
        fragments[winner].add(cell)
    if any(len(value) < min_fragment_size for value in fragments.values()):
        raise RuleContractError("fragmentation produced a fragment below minimum size")
    for index, cells in fragments.items():
        canvas.mark_many(cells, f"{label}-{index + 1}")
    return fragments


@dataclass(frozen=True, slots=True)
class RewriteRule:
    name: str
    max_passes: int = 2

    def __post_init__(self) -> None:
        if self.name not in {"FILL_NOTCH", "BRIDGE_GAP", "REMOVE_PROTRUSION"}:
            raise RuleContractError("unknown project rewrite rule")
        if not 1 <= self.max_passes <= 8:
            raise RuleContractError("rewrite max_passes must be 1..8")


def local_rewrite(canvas: RuleCanvas, rule: RewriteRule, *, label: str = "rewrite") -> set[int]:
    current = set(canvas.occupied)
    for _ in range(rule.max_passes):
        additions: set[int] = set()
        removals: set[int] = set()
        for index in range(canvas.size):
            neighbors = canvas.neighbors(index)
            occupied_neighbors = sum(neighbor in current for neighbor in neighbors)
            if rule.name == "FILL_NOTCH" and index not in current and occupied_neighbors >= 3 and index not in canvas.protected_negative:
                additions.add(index)
            elif rule.name == "BRIDGE_GAP" and index not in current and index not in canvas.protected_negative:
                left_right = len(neighbors) == 4 and neighbors[0] in current and neighbors[1] in current
                up_down = len(neighbors) == 4 and neighbors[2] in current and neighbors[3] in current
                if occupied_neighbors == 2 and (left_right or up_down):
                    additions.add(index)
            elif rule.name == "REMOVE_PROTRUSION" and index in current and occupied_neighbors <= 1 and index not in canvas.protected_occupied:
                removals.add(index)
        if not additions and not removals:
            break
        current.update(additions)
        current.difference_update(removals)
    for index in sorted(current - set(canvas.occupied)):
        canvas.mark(index, label)
    for index in sorted(set(canvas.occupied) - current):
        canvas.carve(index)
    return current


def bounded_repeat(canvas: RuleCanvas, operation: str, passes: int, *, region: set[int] | None = None) -> set[int]:
    """Expose a finite pass contract for callers composing operations."""
    if operation not in {"CONTOUR_EXTRACTION", "EROSION", "DILATION"}:
        raise RuleContractError("bounded repeat operation is not supported")
    if isinstance(passes, bool) or not isinstance(passes, int) or not 0 <= passes <= 32:
        raise RuleContractError("bounded repeat passes must be 0..32")
    current = set(canvas.occupied if region is None else region)
    for _ in range(passes):
        if operation == "CONTOUR_EXTRACTION":
            current = contour_extraction(canvas, current)
        elif operation == "EROSION":
            current = erosion(canvas, current, 1)
        else:
            current = dilation(canvas, current, 1)
    return current
