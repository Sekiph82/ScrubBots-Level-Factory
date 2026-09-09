"""Ten original procedural SCRUBBOTS mask families."""

from dataclasses import dataclass
from enum import Enum

from .model import MaskCellState, MaskContractError, MaskDefinition, SymmetryMode


class TemplateFamily(str, Enum):
    ROBOT = "ROBOT"
    CREATURE = "CREATURE"
    FISH = "FISH"
    SEA_CREATURE = "SEA_CREATURE"
    SPACE_SHIP = "SPACE_SHIP"
    INSECT = "INSECT"
    FACE_EMBLEM = "FACE_EMBLEM"
    TREE_PLANT = "TREE_PLANT"
    CORAL = "CORAL"
    ABSTRACT_SYMBOL = "ABSTRACT_SYMBOL"


FAMILY_NAMES = tuple(family.value for family in TemplateFamily)


@dataclass(frozen=True, slots=True)
class TemplateDefinition:
    family: TemplateFamily

    def build(
        self,
        width: int,
        height: int,
        offset_x: int = 0,
        offset_y: int = 0,
        symmetry: SymmetryMode = SymmetryMode.ASYMMETRIC,
    ) -> MaskDefinition:
        definition = _BUILDERS[self.family](width, height, offset_x, offset_y)
        if symmetry is SymmetryMode.ASYMMETRIC:
            return definition
        cells = list(definition.cells)
        for index, state in enumerate(tuple(cells)):
            if state is not MaskCellState.REQUIRED:
                continue
            x, y = index % width, index // width
            points = {(x, y)}
            if symmetry in (SymmetryMode.HORIZONTAL, SymmetryMode.HORIZONTAL_VERTICAL):
                points.add((width - 1 - x, y))
            if symmetry in (SymmetryMode.VERTICAL, SymmetryMode.HORIZONTAL_VERTICAL):
                points.add((x, height - 1 - y))
            if symmetry is SymmetryMode.HORIZONTAL_VERTICAL:
                points.add((width - 1 - x, height - 1 - y))
            for px, py in points:
                target = py * width + px
                if cells[target] is MaskCellState.FORBIDDEN:
                    cells[target] = MaskCellState.RANDOM
        return MaskDefinition(width, height, tuple(cells))


def _canvas(width: int, height: int) -> list[MaskCellState]:
    return [MaskCellState.FORBIDDEN] * (width * height)


def _mark(cells: list[MaskCellState], width: int, height: int, x: int, y: int, state: MaskCellState = MaskCellState.REQUIRED) -> None:
    if 0 <= x < width and 0 <= y < height:
        cells[y * width + x] = state


def _rect(cells: list[MaskCellState], width: int, height: int, x0: int, y0: int, x1: int, y1: int, state: MaskCellState = MaskCellState.REQUIRED) -> None:
    for y in range(max(0, y0), min(height, y1 + 1)):
        for x in range(max(0, x0), min(width, x1 + 1)):
            _mark(cells, width, height, x, y, state)


def _line(cells: list[MaskCellState], width: int, height: int, points: list[tuple[int, int]], state: MaskCellState = MaskCellState.REQUIRED) -> None:
    for x, y in points:
        _mark(cells, width, height, x, y, state)


def _center_box(width: int, height: int, width_pct: int, height_pct: int, offset_x: int, offset_y: int) -> tuple[int, int, int, int]:
    box_width = max(5, min(width - 2, width * width_pct // 100))
    box_height = max(5, min(height - 2, height * height_pct // 100))
    x0 = (width - box_width) // 2 + offset_x
    y0 = (height - box_height) // 2 + offset_y
    return x0, y0, x0 + box_width - 1, y0 + box_height - 1


def _symmetric_rows(cells: list[MaskCellState], width: int, height: int, y0: int, y1: int, half_width: int, center: int) -> None:
    for y in range(max(0, y0), min(height, y1 + 1)):
        for dx in range(-half_width, half_width + 1):
            _mark(cells, width, height, center + dx, y)
            _mark(cells, width, height, center - dx, y)


def _optional_ring(
    cells: list[MaskCellState],
    width: int,
    height: int,
    protected: set[int] | None = None,
) -> None:
    required = {index for index, state in enumerate(cells) if state is MaskCellState.REQUIRED}
    protected = protected or set()
    for index in tuple(required):
        x, y = index % width, index // width
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                target = ny * width + nx
                if cells[target] is MaskCellState.FORBIDDEN and target not in protected:
                    cells[target] = MaskCellState.RANDOM


def _finish(
    family: TemplateFamily,
    cells: list[MaskCellState],
    width: int,
    height: int,
    protected: set[int] | None = None,
) -> MaskDefinition:
    if not any(state is MaskCellState.REQUIRED for state in cells):
        raise MaskContractError(f"{family.value} template has no required subject cells")
    # Geometry is authored once. Symmetry is an engine option, never a hidden
    # four-way post-process that erases directional or organic family cues.
    # Tiny required islands are connected; larger lobes retain their negative
    # space and are handled independently by the color-region allocator.
    required = {index for index, state in enumerate(cells) if state is MaskCellState.REQUIRED}
    components: list[set[int]] = []
    unseen = set(required)
    while unseen:
        component = {unseen.pop()}
        frontier = list(component)
        while frontier:
            index = frontier.pop()
            x, y = index % width, index // width
            for neighbor in (
                index - 1 if x else -1,
                index + 1 if x + 1 < width else -1,
                index - width if y else -1,
                index + width if y + 1 < height else -1,
            ):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    frontier.append(neighbor)
        components.append(component)
    for component in components:
        if len(component) != 1:
            continue
        if len(components) == 1:
            break
        island = next(iter(component))
        nearest = min(
            (index for other in components if other is not component for index in other),
            key=lambda index: (
                abs(index % width - island % width) + abs(index // width - island // width),
                index,
            ),
        )
        ix, iy = island % width, island // width
        nx, ny = nearest % width, nearest // width
        for x in range(min(ix, nx), max(ix, nx) + 1):
            cells[iy * width + x] = MaskCellState.REQUIRED
        for y in range(min(iy, ny), max(iy, ny) + 1):
            cells[y * width + nx] = MaskCellState.REQUIRED
    # A one-cell enclosed negative-space pocket would necessarily become a
    # singleton rendered color region, so close only those tiny hard pockets.
    changed = True
    while changed:
        changed = False
        for index, state in enumerate(tuple(cells)):
            if state is not MaskCellState.FORBIDDEN:
                continue
            x, y = index % width, index // width
            neighbors = tuple(
                neighbor for neighbor in (
                    index - 1 if x else -1,
                    index + 1 if x + 1 < width else -1,
                    index - width if y else -1,
                    index + width if y + 1 < height else -1,
                ) if neighbor >= 0
            )
            if len(neighbors) == 4 and all(cells[neighbor] is MaskCellState.REQUIRED for neighbor in neighbors):
                cells[index] = MaskCellState.REQUIRED
                changed = True
    _optional_ring(cells, width, height, protected)
    return MaskDefinition(width, height, tuple(cells))


def _robot(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 38, 62, ox, oy)
    center = (width - 1) // 2
    _rect(cells, width, height, x0 + 2, y0, x1 - 2, y0 + max(2, (y1 - y0) // 4))
    _rect(cells, width, height, x0, y0 + max(2, (y1 - y0) // 3), x1, y1 - 2)
    _rect(cells, width, height, center - 2, y1 - 1, center + 2, y1)
    _rect(cells, width, height, x0 - 2, y0 + 5, x0, y0 + 10)
    _rect(cells, width, height, x1, y0 + 5, x1 + 2, y0 + 10)
    _mark(cells, width, height, center - 3, y0 - 2)
    _mark(cells, width, height, center + 3, y0 - 2)
    return _finish(TemplateFamily.ROBOT, cells, width, height)


def _creature(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 52, 58, ox, oy)
    center = (width - 1) // 2
    spans = (3, 5, 7, 8, 8, 7, 6, 5, 4)
    body_top = y0 + 2
    for row, span in enumerate(spans):
        y = body_top + row * max(1, (y1 - y0 - 5) // max(1, len(spans) - 1))
        for dx in range(-span, span + 1):
            _mark(cells, width, height, center + dx, y)
    _line(cells, width, height, [(center - 5, y0), (center - 6, y0 - 1), (center + 5, y0), (center + 6, y0 - 1)])
    _rect(cells, width, height, center - 8, y1 - 3, center - 5, y1 + 1)
    _rect(cells, width, height, center + 5, y1 - 3, center + 8, y1 + 1)
    return _finish(TemplateFamily.CREATURE, cells, width, height)


def _fish(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 66, 35, ox, oy)
    center_y = (y0 + y1) // 2
    center_x = (width - 1) // 2
    for y in range(y0 + 2, y1 - 1):
        distance = abs(y - center_y)
        half = max(2, (y1 - y0) // 2 - distance)
        for x in range(center_x - half, center_x + half + 1):
            _mark(cells, width, height, x, y)
    # A single tail and offset eye preserve the fish's reading under the
    # family-preferred vertical symmetry without inventing a second head.
    _line(cells, width, height, [(x1 - 3, center_y - 3), (x1, center_y - 6), (x1, center_y), (x1, center_y + 6), (x1 - 3, center_y + 3)])
    _mark(cells, width, height, center_x - 5, center_y - 2)
    _rect(cells, width, height, center_x - 1, y0 - 2, center_x + 3, y0)
    _rect(cells, width, height, center_x - 1, y1, center_x + 3, y1 + 2)
    return _finish(TemplateFamily.FISH, cells, width, height)


def _sea_creature(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 42, 66, ox, oy)
    center = (width - 1) // 2
    _symmetric_rows(cells, width, height, y0 + 1, y0 + 7, 5, center)
    _symmetric_rows(cells, width, height, y0 + 8, y0 + 12, 7, center)
    for side in (-1, 1):
        for step in range(7):
            _mark(cells, width, height, center + side * (7 + step // 2), y0 + 12 + step)
            if step % 2 == 0:
                _mark(cells, width, height, center + side * (9 + step // 2), y0 + 13 + step)
    _rect(cells, width, height, center - 3, y0 - 2, center - 1, y0)
    _rect(cells, width, height, center + 1, y0 - 2, center + 3, y0)
    return _finish(TemplateFamily.SEA_CREATURE, cells, width, height)


def _space_ship(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 64, 48, ox, oy)
    center = (width - 1) // 2
    _rect(cells, width, height, center - 4, y0, center + 4, y1)
    _rect(cells, width, height, center - 8, y0 + 5, center + 8, y1 - 4)
    for step in range(6):
        _rect(cells, width, height, center - 12 + step, y0 + 8 + step, center - 9 + step, y0 + 10 + step)
        _rect(cells, width, height, center + 9 - step, y0 + 8 + step, center + 12 - step, y0 + 10 + step)
    _rect(cells, width, height, center - 2, y1 + 1, center + 2, y1 + 3)
    return _finish(TemplateFamily.SPACE_SHIP, cells, width, height)


def _insect(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 58, 68, ox, oy)
    center = (width - 1) // 2
    # Narrow segmented thorax with deliberately separated paired wing lobes.
    _rect(cells, width, height, center - 1, y0 + 2, center + 1, y1 - 2)
    for row in range(4):
        y = y0 + 3 + row * 4
        span = 8 - row
        _rect(cells, width, height, center - span, y, center - 4, y + 1)
        _rect(cells, width, height, center + 4, y, center + span, y + 1)
    _line(cells, width, height, [
        (center - 1, y0 + 1), (center - 4, y0 - 1), (center - 6, y0 - 2),
        (center + 1, y0 + 1), (center + 4, y0 - 1), (center + 6, y0 - 2),
        (center - 1, y0 + 8), (center - 5, y0 + 10),
        (center + 1, y0 + 13), (center + 5, y0 + 15),
    ])
    return _finish(TemplateFamily.INSECT, cells, width, height)


def _face_emblem(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 58, 58, ox, oy)
    center = (width - 1) // 2
    spans = (3, 5, 7, 8, 9, 9, 8, 7, 5, 3)
    for row, span in enumerate(spans):
        y = y0 + row * max(1, (y1 - y0 - 2) // max(1, len(spans) - 1))
        _rect(cells, width, height, center - span, y, center + span, y + 1)
    # Negative-space eye sockets and a mouth slot are structural holes, not
    # foreground rectangles that depend on later color paint to read.
    eye_y = y0 + 5
    protected = set()
    for x_start, x_end in ((center - 6, center - 3), (center + 3, center + 6)):
        _rect(cells, width, height, x_start, eye_y, x_end, eye_y + 1, MaskCellState.FORBIDDEN)
        protected.update(y * width + x for y in range(eye_y, eye_y + 2) for x in range(x_start, x_end + 1))
    _rect(cells, width, height, center - 4, y1 - 5, center + 4, y1 - 3, MaskCellState.FORBIDDEN)
    protected.update(y * width + x for y in range(y1 - 5, y1 - 2) for x in range(center - 4, center + 5))
    _rect(cells, width, height, center - 5, y0 + 3, center - 2, y0 + 4)
    _rect(cells, width, height, center + 2, y0 + 3, center + 5, y0 + 4)
    return _finish(TemplateFamily.FACE_EMBLEM, cells, width, height, protected)


def _tree_plant(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 55, 72, ox, oy)
    center = (width - 1) // 2
    # A narrow stem and separated, uneven crown lobes distinguish the plant
    # from the insect's paired wings.
    _rect(cells, width, height, center - 1, y0 + 11, center + 1, y1 - 1)
    _rect(cells, width, height, center - 5, y1 - 2, center + 5, y1)
    _rect(cells, width, height, center - 3, y0, center + 3, y0 + 3)
    _rect(cells, width, height, center - 10, y0 + 5, center - 4, y0 + 8)
    _rect(cells, width, height, center + 4, y0 + 4, center + 11, y0 + 7)
    _rect(cells, width, height, center - 7, y0 + 9, center - 3, y0 + 11)
    _rect(cells, width, height, center + 2, y0 + 9, center + 7, y0 + 12)
    _line(cells, width, height, [
        (center - 1, y0 + 10), (center - 4, y0 + 9),
        (center + 1, y0 + 12), (center + 4, y0 + 10),
    ])
    return _finish(TemplateFamily.TREE_PLANT, cells, width, height)


def _coral(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 62, 70, ox, oy)
    center = (width - 1) // 2
    _rect(cells, width, height, center - 3, y1 - 8, center + 3, y1)
    for side in (-1, 1):
        for branch in range(4):
            start_x = center + side * (3 + branch)
            start_y = y1 - 9 - branch * 3
            for step in range(8 - branch):
                _mark(cells, width, height, start_x + side * (step // 3), start_y - step)
            _mark(cells, width, height, start_x + side * (3 + branch), start_y - 8 + branch)
    _rect(cells, width, height, center - 10, y1, center + 10, y1 + 2)
    return _finish(TemplateFamily.CORAL, cells, width, height)


def _abstract_symbol(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 58, 58, ox, oy)
    center = (width - 1) // 2
    middle = (y0 + y1) // 2
    for distance in range(0, min((x1 - x0) // 2, (y1 - y0) // 2) + 1):
        _mark(cells, width, height, center - distance, middle)
        _mark(cells, width, height, center + distance, middle)
        _mark(cells, width, height, center, middle - distance)
        _mark(cells, width, height, center, middle + distance)
    _rect(cells, width, height, center - 2, y0 + 3, center + 2, y0 + 5)
    _rect(cells, width, height, center - 2, y1 - 5, center + 2, y1 - 3)
    _rect(cells, width, height, x0 + 3, middle - 2, x0 + 5, middle + 2)
    _rect(cells, width, height, x1 - 5, middle - 2, x1 - 3, middle + 2)
    return _finish(TemplateFamily.ABSTRACT_SYMBOL, cells, width, height)


_BUILDERS = {
    TemplateFamily.ROBOT: _robot,
    TemplateFamily.CREATURE: _creature,
    TemplateFamily.FISH: _fish,
    TemplateFamily.SEA_CREATURE: _sea_creature,
    TemplateFamily.SPACE_SHIP: _space_ship,
    TemplateFamily.INSECT: _insect,
    TemplateFamily.FACE_EMBLEM: _face_emblem,
    TemplateFamily.TREE_PLANT: _tree_plant,
    TemplateFamily.CORAL: _coral,
    TemplateFamily.ABSTRACT_SYMBOL: _abstract_symbol,
}


_PREFERRED_SYMMETRY = {
    TemplateFamily.ROBOT: SymmetryMode.HORIZONTAL,
    TemplateFamily.CREATURE: SymmetryMode.ASYMMETRIC,
    TemplateFamily.FISH: SymmetryMode.VERTICAL,
    TemplateFamily.SEA_CREATURE: SymmetryMode.ASYMMETRIC,
    TemplateFamily.SPACE_SHIP: SymmetryMode.HORIZONTAL,
    TemplateFamily.INSECT: SymmetryMode.HORIZONTAL,
    TemplateFamily.FACE_EMBLEM: SymmetryMode.HORIZONTAL,
    TemplateFamily.TREE_PLANT: SymmetryMode.ASYMMETRIC,
    TemplateFamily.CORAL: SymmetryMode.ASYMMETRIC,
    TemplateFamily.ABSTRACT_SYMBOL: SymmetryMode.HORIZONTAL_VERTICAL,
}


def preferred_symmetry(family: TemplateFamily | str) -> SymmetryMode:
    try:
        selected = family if isinstance(family, TemplateFamily) else TemplateFamily(family)
    except (TypeError, ValueError) as exc:
        raise MaskContractError("unknown MASK template family") from exc
    return _PREFERRED_SYMMETRY[selected]


def template_for(
    family: TemplateFamily | str,
    width: int,
    height: int,
    offset_x: int = 0,
    offset_y: int = 0,
    symmetry: SymmetryMode | str = SymmetryMode.ASYMMETRIC,
) -> MaskDefinition:
    try:
        selected = family if isinstance(family, TemplateFamily) else TemplateFamily(family)
    except (TypeError, ValueError) as exc:
        raise MaskContractError("unknown MASK template family") from exc
    if isinstance(offset_x, bool) or not isinstance(offset_x, int) or isinstance(offset_y, bool) or not isinstance(offset_y, int):
        raise MaskContractError("template placement offsets must be integers")
    return TemplateDefinition(selected).build(width, height, offset_x, offset_y, SymmetryMode.parse(symmetry))
