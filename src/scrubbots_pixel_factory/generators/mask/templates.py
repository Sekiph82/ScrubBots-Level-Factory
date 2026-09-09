"""Ten original procedural SCRUBBOTS mask families."""

from dataclasses import dataclass
from enum import Enum

from .model import MaskCellState, MaskContractError, MaskDefinition


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

    def build(self, width: int, height: int, offset_x: int = 0, offset_y: int = 0) -> MaskDefinition:
        return _BUILDERS[self.family](width, height, offset_x, offset_y)


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


def _optional_ring(cells: list[MaskCellState], width: int, height: int) -> None:
    required = {index for index, state in enumerate(cells) if state is MaskCellState.REQUIRED}
    for index in tuple(required):
        x, y = index % width, index // width
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    target = ny * width + nx
                    if cells[target] is MaskCellState.FORBIDDEN:
                        cells[target] = MaskCellState.RANDOM


def _finish(family: TemplateFamily, cells: list[MaskCellState], width: int, height: int) -> MaskDefinition:
    if not any(state is MaskCellState.REQUIRED for state in cells):
        raise MaskContractError(f"{family.value} template has no required subject cells")
    required = [index for index, state in enumerate(cells) if state is MaskCellState.REQUIRED]
    for index in required:
        x, y = index % width, index // width
        for mirror_x, mirror_y in ((width - 1 - x, y), (x, height - 1 - y), (width - 1 - x, height - 1 - y)):
            _mark(cells, width, height, mirror_x, mirror_y)
    _optional_ring(cells, width, height)
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
    _line(cells, width, height, [(x1 - 3, center_y - 3), (x1, center_y - 6), (x1, center_y), (x1, center_y + 6), (x1 - 3, center_y + 3)])
    _line(cells, width, height, [(width - 1 - (x1 - 3), center_y - 3), (width - 1 - x1, center_y - 6), (width - 1 - x1, center_y), (width - 1 - x1, center_y + 6), (width - 1 - (x1 - 3), center_y + 3)])
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
    _rect(cells, width, height, center - 2, y0, center + 2, y1)
    for row in range(5):
        y = y0 + 3 + row * 3
        span = 5 + row
        _rect(cells, width, height, center - span, y, center - 3, y + 2)
        _rect(cells, width, height, center + 3, y, center + span, y + 2)
    _line(cells, width, height, [(center - 2, y0 - 1), (center - 5, y0 - 3), (center + 2, y0 - 1), (center + 5, y0 - 3)])
    return _finish(TemplateFamily.INSECT, cells, width, height)


def _face_emblem(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 58, 58, ox, oy)
    center = (width - 1) // 2
    spans = (4, 6, 7, 8, 8, 7, 6, 4)
    for row, span in enumerate(spans):
        y = y0 + 1 + row * max(1, (y1 - y0 - 3) // max(1, len(spans) - 1))
        _rect(cells, width, height, center - span, y, center + span, y + 1)
    _rect(cells, width, height, center - 6, y0 + 8, center - 3, y0 + 10)
    _rect(cells, width, height, center + 3, y0 + 8, center + 6, y0 + 10)
    _rect(cells, width, height, center - 5, y1 - 5, center + 5, y1 - 3)
    return _finish(TemplateFamily.FACE_EMBLEM, cells, width, height)


def _tree_plant(width: int, height: int, ox: int, oy: int) -> MaskDefinition:
    cells = _canvas(width, height)
    x0, y0, x1, y1 = _center_box(width, height, 55, 72, ox, oy)
    center = (width - 1) // 2
    for row in range(8):
        y = y0 + row * 2
        span = 4 + row // 2
        _rect(cells, width, height, center - span, y, center + span, y + 2)
    _rect(cells, width, height, center - 3, y0 + 13, center + 3, y1)
    _rect(cells, width, height, center - 9, y0 + 17, center - 4, y0 + 19)
    _rect(cells, width, height, center + 4, y0 + 17, center + 9, y0 + 19)
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


def template_for(family: TemplateFamily | str, width: int, height: int, offset_x: int = 0, offset_y: int = 0) -> MaskDefinition:
    try:
        selected = family if isinstance(family, TemplateFamily) else TemplateFamily(family)
    except (TypeError, ValueError) as exc:
        raise MaskContractError("unknown MASK template family") from exc
    if isinstance(offset_x, bool) or not isinstance(offset_x, int) or isinstance(offset_y, bool) or not isinstance(offset_y, int):
        raise MaskContractError("template placement offsets must be integers")
    return TemplateDefinition(selected).build(width, height, offset_x, offset_y)
