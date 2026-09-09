"""Deterministic mask resolution, symmetry, mutation, and occupancy checks."""

from collections.abc import Iterable

from ...core.rng import DeterministicRNG
from .model import MaskCellState, MaskConfig, MaskContractError, MaskDefinition, ResolvedMask, SymmetryMode


def _mirror_coordinates(x: int, y: int, width: int, height: int, mode: SymmetryMode) -> set[tuple[int, int]]:
    points = {(x, y)}
    if mode in (SymmetryMode.HORIZONTAL, SymmetryMode.HORIZONTAL_VERTICAL):
        points.add((width - 1 - x, y))
    if mode in (SymmetryMode.VERTICAL, SymmetryMode.HORIZONTAL_VERTICAL):
        points.add((x, height - 1 - y))
    if mode is SymmetryMode.HORIZONTAL_VERTICAL:
        points.add((width - 1 - x, height - 1 - y))
    return points


def symmetry_orbits(width: int, height: int, mode: SymmetryMode) -> tuple[tuple[int, ...], ...]:
    """Return deterministic row-major coordinate orbits for the requested mirrors."""
    groups: list[tuple[int, ...]] = []
    seen: set[int] = set()
    for y in range(height):
        for x in range(width):
            index = y * width + x
            if index in seen:
                continue
            orbit = tuple(sorted(py * width + px for px, py in _mirror_coordinates(x, y, width, height, mode)))
            seen.update(orbit)
            groups.append(orbit)
    return tuple(groups)


def _symmetric_states(definition: MaskDefinition, config: MaskConfig) -> tuple[MaskCellState, ...]:
    states = list(definition.cells)
    for orbit in symmetry_orbits(definition.width, definition.height, config.symmetry):
        values = {states[index] for index in orbit}
        if MaskCellState.REQUIRED in values and MaskCellState.FORBIDDEN in values:
            raise MaskContractError("symmetry orbit contains both REQUIRED and FORBIDDEN cells")
        if MaskCellState.REQUIRED in values:
            value = MaskCellState.REQUIRED
        elif MaskCellState.FORBIDDEN in values:
            value = MaskCellState.FORBIDDEN
        else:
            value = MaskCellState.RANDOM
        for index in orbit:
            states[index] = value
    return tuple(states)


def resolve_mask(definition: MaskDefinition, rng: DeterministicRNG, config: MaskConfig | None = None) -> ResolvedMask:
    """Resolve optional cells and bounded mutation without violating hard cells."""
    if not isinstance(rng, DeterministicRNG):
        raise MaskContractError("mask resolution requires the project DeterministicRNG")
    config = config or MaskConfig()
    states = _symmetric_states(definition, config)
    foreground = [state is MaskCellState.REQUIRED for state in states]
    mutable_orbits = [
        orbit for orbit in symmetry_orbits(definition.width, definition.height, config.symmetry)
        if all(states[index] is MaskCellState.RANDOM for index in orbit)
    ]
    random_stream = rng.child("random-cells")
    for orbit in symmetry_orbits(definition.width, definition.height, config.symmetry):
        if all(states[index] is MaskCellState.RANDOM for index in orbit):
            value = random_stream.randbelow(100) < 42
            for index in orbit:
                foreground[index] = value
    mutation_stream = rng.child("mutation")
    mutation_count = min(config.mutation, len(mutable_orbits))
    for orbit in mutation_stream.shuffle(mutable_orbits)[:mutation_count]:
        for index in orbit:
            foreground[index] = not foreground[index]
    total = definition.width * definition.height
    count = sum(foreground)
    if count == 0:
        raise MaskContractError("resolved mask must contain foreground")
    if count * 100 < config.occupancy_floor_pct * total:
        raise MaskContractError("resolved mask is below the occupancy floor")
    if count * 100 > config.occupancy_ceiling_pct * total:
        raise MaskContractError("resolved mask exceeds the occupancy ceiling")
    return ResolvedMask(definition.width, definition.height, tuple(foreground), states)


def classify_coordinates(mask: ResolvedMask, foreground: bool) -> tuple[tuple[int, int], ...]:
    """Return row-major coordinates for a foreground or negative-space class."""
    return tuple(
        (index % mask.width, index // mask.width)
        for index, value in enumerate(mask.foreground_cells)
        if value is foreground
    )
