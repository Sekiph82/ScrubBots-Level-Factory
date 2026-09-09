"""Deterministic geometry-derived semantic regions and role-bound coloring."""

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
class ColorRoleAssignment:
    color_id: str
    role: ColorRole
    slot: int


@dataclass(frozen=True, slots=True)
class ColorizedMask:
    """Final C-ID grid and the immutable role data used to paint it."""

    cells: tuple[str, ...]
    roles: tuple[ColorRole, ...]
    role_assignments: tuple[ColorRoleAssignment, ...]

    @property
    def role_colors(self) -> tuple[ColorRoleAssignment, ...]:
        """Backward-compatible name for the complete explicit mapping."""
        return self.role_assignments


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


def _components(indices: set[int], width: int, height: int) -> tuple[tuple[int, ...], ...]:
    found: set[int] = set()
    components: list[tuple[int, ...]] = []
    for start in sorted(indices):
        if start in found:
            continue
        queue = deque([start])
        found.add(start)
        component = []
        while queue:
            index = queue.popleft()
            component.append(index)
            for neighbor in _neighbors(index, width, height):
                if neighbor in indices and neighbor not in found:
                    found.add(neighbor)
                    queue.append(neighbor)
        components.append(tuple(component))
    return tuple(components)


def color_component_sizes(cells: Sequence[str], width: int, height: int) -> dict[str, tuple[int, ...]]:
    """Return deterministic 4-neighbor component sizes for each rendered C-ID."""
    if len(cells) != width * height:
        raise MaskContractError("color component grid dimensions are inconsistent")
    return {
        color: tuple(sorted((len(component) for component in _components(
            {index for index, cell in enumerate(cells) if cell == color}, width, height
        )), reverse=True))
        for color in sorted(set(cells), key=lambda value: int(value[1:]))
    }


def _geometry_role(index: int, width: int, height: int, foreground: set[int]) -> ColorRole:
    x, y = index % width, index // width
    if x in (0, width - 1) or y in (0, height - 1):
        return ColorRole.OUTLINE
    if any(neighbor not in foreground for neighbor in _neighbors(index, width, height)):
        return ColorRole.OUTLINE
    return ColorRole.BODY_PRIMARY


def _role_slots(selected: tuple[str, ...]) -> tuple[ColorRoleAssignment, ...]:
    """Assign each selected C-ID a broad role and deterministic sub-role slot."""
    foreground_colors = selected[1:]
    roles = [ColorRole.OUTLINE]
    if len(foreground_colors) >= 2:
        roles.append(ColorRole.BODY_PRIMARY)
    if len(foreground_colors) >= 3:
        roles.append(ColorRole.SECONDARY)
    if len(foreground_colors) >= 4:
        roles.append(ColorRole.DETAIL_ACCENT)
    extra_roles = (ColorRole.BODY_PRIMARY, ColorRole.SECONDARY, ColorRole.DETAIL_ACCENT)
    for index in range(4, len(foreground_colors)):
        roles.append(extra_roles[(index - 4) % len(extra_roles)])
    counts: dict[ColorRole, int] = {}
    assignments = [ColorRoleAssignment(selected[0], ColorRole.NEGATIVE_SPACE, 0)]
    for color, role in zip(foreground_colors, roles, strict=True):
        slot = counts.get(role, 0)
        assignments.append(ColorRoleAssignment(color, role, slot))
        counts[role] = slot + 1
    return tuple(assignments)


def _grow_patch(
    available: set[int],
    width: int,
    height: int,
    target: int,
    rng: DeterministicRNG,
) -> set[int]:
    if target <= 0:
        return set()
    region: set[int] = set()
    while len(region) < target:
        components = [
            component for component in _components(available - region, width, height)
            if len(component) >= 2
        ]
        if not components:
            raise MaskContractError("semantic role region cannot grow coherently")
        component = max(components, key=lambda value: (len(value), -min(value)))
        need = min(target - len(region), len(component))
        local = {rng.child("seed").choice(sorted(component))}
        while len(local) < need:
            frontier = sorted({
                neighbor
                for index in local
                for neighbor in _neighbors(index, width, height)
                if neighbor in component and neighbor not in local
            })
            if not frontier:
                break
            local.add(rng.choice(frontier))
        if len(local) < 2:
            raise MaskContractError("semantic role region cannot grow coherently")
        region.update(local)
    return region


def _pair_candidates(indices: set[int], width: int, height: int) -> list[tuple[int, int]]:
    return [
        (index, neighbor)
        for index in sorted(indices)
        for neighbor in _neighbors(index, width, height)
        if neighbor > index and neighbor in indices
    ]


def _select_disjoint_pairs(
    pairs: list[tuple[int, int]],
    count: int,
    available: set[int],
    rng: DeterministicRNG,
) -> list[tuple[int, int]]:
    candidates = [
        pair for pair in rng.shuffle(pairs)
        if pair[0] in available and pair[1] in available
    ]

    def search(start: int, chosen: list[tuple[int, int]], used: set[int]) -> list[tuple[int, int]] | None:
        if len(chosen) == count:
            return list(chosen)
        for position in range(start, len(candidates)):
            pair = candidates[position]
            if pair[0] in used or pair[1] in used:
                continue
            used.update(pair)
            chosen.append(pair)
            result = search(position + 1, chosen, used)
            if result is not None:
                return result
            chosen.pop()
            used.difference_update(pair)
        return None

    selected = search(0, [], set())
    if selected is None:
        raise MaskContractError("role geometry cannot allocate disjoint connected color regions")
    return selected


def _stabilize_outline(outline: set[int], foreground: set[int], width: int, height: int) -> set[int]:
    """Give every boundary lobe at least one adjacent outline partner."""
    outline = set(outline)
    while True:
        singleton = next(
            (component[0] for component in _components(outline, width, height) if len(component) == 1),
            None,
        )
        if singleton is None:
            return outline
        neighbors = sorted(
            neighbor
            for neighbor in _neighbors(singleton, width, height)
            if neighbor in foreground and neighbor not in outline
        )
        if not neighbors:
            raise MaskContractError("outline geometry contains an unpairable boundary cell")
        outline.add(neighbors[0])


def _partition_role_region(
    indices: set[int],
    colors: tuple[str, ...],
    role: ColorRole,
    width: int,
    height: int,
    rng: DeterministicRNG,
) -> dict[int, str]:
    if not colors:
        return {}
    components = _components(indices, width, height)
    if any(len(component) < 2 for component in components):
        raise MaskContractError(f"{role.value} geometry contains a singleton region")
    available = set(indices)
    labels: dict[int, str] = {}
    pairs = _pair_candidates(indices, width, height)
    selected_pairs = _select_disjoint_pairs(pairs, len(colors), available, rng)
    for color, pair in zip(colors, selected_pairs, strict=True):
        for index in pair:
            labels[index] = color
            available.remove(index)
    for component in components:
        if any(index in labels for index in component):
            continue
        candidates = [
            pair for pair in _pair_candidates(set(component), width, height)
            if pair[0] in available and pair[1] in available
        ]
        if not candidates:
            raise MaskContractError(f"{role.value} island cannot receive a connected color")
        for index in candidates[0]:
            labels[index] = colors[0]
            available.remove(index)
    while available:
        frontier = sorted({
            index
            for index in available
            if any(neighbor in labels for neighbor in _neighbors(index, width, height))
        })
        if not frontier:
            raise MaskContractError(f"{role.value} propagation lost connectivity")
        index = frontier[0]
        adjacent_colors = [
            labels[neighbor]
            for neighbor in _neighbors(index, width, height)
            if neighbor in labels
        ]
        selected = min(
            colors,
            key=lambda color: (-adjacent_colors.count(color), colors.index(color)),
        )
        labels[index] = selected
        available.remove(index)
    return labels


def _build_role_regions(
    mask: ResolvedMask,
    assignments: tuple[ColorRoleAssignment, ...],
    rng: DeterministicRNG,
) -> dict[ColorRole, set[int]]:
    foreground = {index for index, value in enumerate(mask.foreground_cells) if value}
    components = _components(foreground, mask.width, mask.height)
    if any(len(component) < 2 for component in components):
        raise MaskContractError("foreground contains a singleton geometric component")
    outline = {
        index for index in foreground
        if _geometry_role(index, mask.width, mask.height, foreground) is ColorRole.OUTLINE
    }
    outline = _stabilize_outline(outline, foreground, mask.width, mask.height)
    interior = foreground - outline
    counts: dict[ColorRole, int] = {}
    for assignment in assignments:
        if assignment.role is not ColorRole.NEGATIVE_SPACE:
            counts[assignment.role] = counts.get(assignment.role, 0) + 1
    regions = {
        ColorRole.NEGATIVE_SPACE: set(range(mask.width * mask.height)) - foreground,
        ColorRole.OUTLINE: outline,
        ColorRole.BODY_PRIMARY: set(),
        ColorRole.SECONDARY: set(),
        ColorRole.DETAIL_ACCENT: set(),
    }
    available = set(interior)
    for role in (ColorRole.SECONDARY, ColorRole.DETAIL_ACCENT):
        target = 2 * counts.get(role, 0) + (4 if counts.get(role, 0) else 0)
        if target:
            patch = _grow_patch(available, mask.width, mask.height, target, rng.child(role.value))
            regions[role] = patch
            available.difference_update(patch)
    if counts.get(ColorRole.BODY_PRIMARY, 0) and len(available) < 2 * counts[ColorRole.BODY_PRIMARY]:
        raise MaskContractError("body role has too few cells for its selected colors")
    regions[ColorRole.BODY_PRIMARY] = available
    # Carving coherent secondary/detail patches can leave a one-cell body
    # remainder. Rebind it to its adjacent structural region so no role
    # region—and therefore no final color region—contains a singleton.
    for component in _components(regions[ColorRole.BODY_PRIMARY], mask.width, mask.height):
        if len(component) != 1:
            continue
        index = component[0]
        target_role = next(
            (
                role for role in (ColorRole.OUTLINE, ColorRole.SECONDARY, ColorRole.DETAIL_ACCENT)
                if any(neighbor in regions[role] for neighbor in _neighbors(index, mask.width, mask.height))
            ),
            None,
        )
        if target_role is not None:
            regions[ColorRole.BODY_PRIMARY].remove(index)
            regions[target_role].add(index)
    for role, count in counts.items():
        if count and len(regions[role]) < 2 * count:
            raise MaskContractError(f"{role.value} has too few cells for its selected colors")
    return regions


def colorize_with_roles(mask: ResolvedMask, palette: Sequence[str], rng: DeterministicRNG) -> ColorizedMask:
    """Paint only within precomputed semantic role regions."""
    selected = _validate_selected_palette(palette)
    if not isinstance(rng, DeterministicRNG):
        raise MaskContractError("colorization requires the project DeterministicRNG")
    assignments = _role_slots(selected)
    regions = _build_role_regions(mask, assignments, rng.child("role-regions"))
    cells = [selected[0]] * (mask.width * mask.height)
    roles = [ColorRole.NEGATIVE_SPACE] * (mask.width * mask.height)
    for role in (
        ColorRole.OUTLINE,
        ColorRole.BODY_PRIMARY,
        ColorRole.SECONDARY,
        ColorRole.DETAIL_ACCENT,
    ):
        role_colors = tuple(item.color_id for item in assignments if item.role is role)
        if not role_colors:
            continue
        labels = _partition_role_region(
            regions[role],
            role_colors,
            role,
            mask.width,
            mask.height,
            rng.child(f"role-colors/{role.value}"),
        )
        for index, color in labels.items():
            cells[index] = color
            roles[index] = role
    if any((value and cells[index] == selected[0]) for index, value in enumerate(mask.foreground_cells)):
        raise MaskContractError("foreground role painting left base color in the subject")
    if tuple(value != selected[0] for value in cells) != mask.foreground_cells:
        raise MaskContractError("role painting changed foreground geometry")
    if set(cells) != set(selected):
        raise MaskContractError("role painting did not use every selected palette ID")
    component_sizes = color_component_sizes(cells, mask.width, mask.height)
    if any(size == 1 for sizes in component_sizes.values() for size in sizes):
        raise MaskContractError("role painting produced a singleton color component")
    observed: dict[str, set[ColorRole]] = {assignment.color_id: set() for assignment in assignments}
    for color, role in zip(cells, roles, strict=True):
        observed[color].add(role)
    for assignment in assignments:
        if observed[assignment.color_id] != {assignment.role}:
            raise MaskContractError(f"color {assignment.color_id} crossed its {assignment.role.value} boundary")
    return ColorizedMask(tuple(cells), tuple(roles), assignments)


def colorize_mask(mask: ResolvedMask, palette: Sequence[str], rng: DeterministicRNG) -> tuple[str, ...]:
    """Map internal geometry to only selected canonical C-IDs."""
    return colorize_with_roles(mask, palette, rng).cells
