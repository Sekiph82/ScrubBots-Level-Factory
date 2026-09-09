"""Bounded deterministic wave propagation and overlapping-pattern solving."""

from collections import deque
from dataclasses import dataclass

from ...core import DeterministicRNG
from .model import DIRECTIONS, PatternTable, WFCContractError


class WFCContradiction(WFCContractError):
    """A stable, bounded solver contradiction that may be retried."""

    def __init__(self, code: str, placement: tuple[int, int], detail: str) -> None:
        self.code = code
        self.placement = placement
        self.detail = detail
        super().__init__(f"{code} at {placement[0]},{placement[1]}: {detail}")


@dataclass(frozen=True, slots=True)
class SolveOutcome:
    logical_grid: tuple[str, ...]
    placement_width: int
    placement_height: int
    propagation_steps: int
    observations: int


def _neighbors(x: int, y: int, width: int, height: int, periodic: bool):
    for direction, dx, dy in (("LEFT", -1, 0), ("RIGHT", 1, 0), ("UP", 0, -1), ("DOWN", 0, 1)):
        nx, ny = x + dx, y + dy
        if periodic:
            yield direction, nx % width, ny % height
        elif 0 <= nx < width and 0 <= ny < height:
            yield direction, nx, ny


def _weighted_pattern_id(allowed: set[int], table: PatternTable, rng: DeterministicRNG) -> int:
    ordered = sorted(allowed)
    total = sum(table.patterns[index].frequency for index in ordered)
    pick = rng.randbelow(total)
    for index in ordered:
        pick -= table.patterns[index].frequency
        if pick < 0:
            return index
    raise WFCContractError("weighted WFC choice failed to select a pattern")


def solve_pattern_table(table: PatternTable, width: int, height: int, rng: DeterministicRNG, output_periodic: bool) -> SolveOutcome:
    if width < table.pattern_size or height < table.pattern_size:
        raise WFCContractError("requested output is smaller than the WFC pattern size")
    if not isinstance(rng, DeterministicRNG):
        raise WFCContractError("WFC solver requires the project DeterministicRNG")
    placement_width = width if output_periodic else width - table.pattern_size + 1
    placement_height = height if output_periodic else height - table.pattern_size + 1
    pattern_count = len(table.patterns)
    waves: list[set[int]] = [set(range(pattern_count)) for _ in range(placement_width * placement_height)]
    queue: deque[tuple[int, int, str]] = deque()
    operation_limit = max(1, len(waves) * pattern_count * 8 + len(waves) + 1)
    operations = 0

    def index(x: int, y: int) -> int:
        return y * placement_width + x

    def propagate() -> int:
        nonlocal operations
        changed = 0
        while queue:
            x, y, direction = queue.popleft()
            source = waves[index(x, y)]
            for neighbor_direction, nx, ny in _neighbors(x, y, placement_width, placement_height, output_periodic):
                if neighbor_direction != direction:
                    continue
                destination_index = index(nx, ny)
                supported: set[int] = set()
                adjacency = table.adjacency[direction]
                for source_pattern in sorted(source):
                    supported.update(adjacency[source_pattern])
                before = waves[destination_index]
                reduced = before.intersection(supported)
                operations += 1
                if operations > operation_limit:
                    raise WFCContradiction("PROPAGATION_LIMIT", (x, y), "bounded propagation operation limit exceeded")
                if not reduced:
                    raise WFCContradiction("EMPTY_WAVE", (nx, ny), f"no patterns remain from {direction} constraint")
                if reduced != before:
                    waves[destination_index] = reduced
                    changed += 1
                    queue.extend(
                        (nx, ny, next_direction)
                        for next_direction, _, _ in _neighbors(nx, ny, placement_width, placement_height, output_periodic)
                    )
        return changed

    observations = 0
    propagation_steps = 0
    while True:
        unresolved = [(index % placement_width, index // placement_width, allowed) for index, allowed in enumerate(waves) if len(allowed) > 1]
        if not unresolved:
            break
        x, y, allowed = min(unresolved, key=lambda item: (len(item[2]), item[1], item[0]))
        chosen = _weighted_pattern_id(allowed, table, rng.child(f"observe/{observations}"))
        waves[index(x, y)] = {chosen}
        observations += 1
        queue.extend((x, y, direction) for direction, _, _ in _neighbors(x, y, placement_width, placement_height, output_periodic))
        propagation_steps += propagate()

    if output_periodic:
        grid = tuple(table.patterns[next(iter(waves[index(x, y)]))].cells[0] for y in range(height) for x in range(width))
        return SolveOutcome(grid, placement_width, placement_height, propagation_steps, observations)

    cells: list[str | None] = [None] * (width * height)
    for py in range(placement_height):
        for px in range(placement_width):
            pattern = table.patterns[next(iter(waves[index(px, py)]))]
            for row in range(table.pattern_size):
                for column in range(table.pattern_size):
                    cell_index = (py + row) * width + px + column
                    value = pattern.cells[row * table.pattern_size + column]
                    if cells[cell_index] is not None and cells[cell_index] != value:
                        raise WFCContradiction("RECONSTRUCTION_CONFLICT", (px, py), "overlapping singleton patterns disagree")
                    cells[cell_index] = value
    if any(cell is None for cell in cells):
        raise WFCContradiction("INCOMPLETE_RECONSTRUCTION", (0, 0), "non-periodic placement did not cover every output cell")
    return SolveOutcome(tuple(cells), placement_width, placement_height, propagation_steps, observations)  # type: ignore[arg-type]
