"""Immutable logical mask structures used by the M03 generator."""

from dataclasses import dataclass
from enum import Enum


class MaskContractError(ValueError):
    """Raised when a mask or bounded MASK option is invalid."""


class MaskCellState(str, Enum):
    REQUIRED = "REQUIRED"
    FORBIDDEN = "FORBIDDEN"
    RANDOM = "RANDOM"


class SymmetryMode(str, Enum):
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"
    HORIZONTAL_VERTICAL = "HORIZONTAL_VERTICAL"
    ASYMMETRIC = "ASYMMETRIC"

    @classmethod
    def parse(cls, value: object) -> "SymmetryMode":
        if isinstance(value, cls):
            return value
        if type(value) is not str:
            raise MaskContractError("symmetry must be a supported MASK symmetry name")
        try:
            return cls(value)
        except ValueError as exc:
            raise MaskContractError("symmetry must be HORIZONTAL, VERTICAL, HORIZONTAL_VERTICAL, or ASYMMETRIC") from exc


@dataclass(frozen=True, slots=True)
class MaskConfig:
    """Strict integer MASK controls; occupancy values are whole percentages."""

    symmetry: SymmetryMode = SymmetryMode.HORIZONTAL
    mutation: int = 3
    offset_x: int = 0
    offset_y: int = 0
    occupancy_floor_pct: int = 2
    occupancy_ceiling_pct: int = 95

    def __post_init__(self) -> None:
        symmetry = SymmetryMode.parse(self.symmetry)
        for label, value in (("mutation", self.mutation), ("offset_x", self.offset_x), ("offset_y", self.offset_y), ("occupancy_floor_pct", self.occupancy_floor_pct), ("occupancy_ceiling_pct", self.occupancy_ceiling_pct)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise MaskContractError(f"{label} must be an integer")
        if self.mutation < 0 or self.mutation > 256:
            raise MaskContractError("mutation must be bounded to 0..256")
        if not -4 <= self.offset_x <= 4 or not -4 <= self.offset_y <= 4:
            raise MaskContractError("placement offsets must be bounded to -4..4")
        if not 0 <= self.occupancy_floor_pct <= self.occupancy_ceiling_pct <= 100:
            raise MaskContractError("occupancy floor and ceiling must satisfy 0..floor..ceiling..100")
        object.__setattr__(self, "symmetry", symmetry)


@dataclass(frozen=True, slots=True)
class MaskDefinition:
    """A target-board mask whose cells are hard or RNG-resolvable states."""

    width: int
    height: int
    cells: tuple[MaskCellState, ...]

    def __post_init__(self) -> None:
        if isinstance(self.width, bool) or not isinstance(self.width, int) or self.width <= 0:
            raise MaskContractError("mask width must be a positive integer")
        if isinstance(self.height, bool) or not isinstance(self.height, int) or self.height <= 0:
            raise MaskContractError("mask height must be a positive integer")
        try:
            cells = tuple(cell if isinstance(cell, MaskCellState) else MaskCellState(cell) for cell in self.cells)
        except (TypeError, ValueError) as exc:
            raise MaskContractError("mask cells must use REQUIRED, FORBIDDEN, or RANDOM") from exc
        if len(cells) != self.width * self.height:
            raise MaskContractError("mask cells must equal width multiplied by height")
        object.__setattr__(self, "cells", cells)

    def index(self, x: int, y: int) -> int:
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise MaskContractError("mask coordinate is out of bounds")
        return y * self.width + x

    def get(self, x: int, y: int) -> MaskCellState:
        return self.cells[self.index(x, y)]

    def row_major(self) -> tuple[MaskCellState, ...]:
        return self.cells

    def foreground(self, x: int, y: int) -> bool:
        return self.get(x, y) is MaskCellState.REQUIRED


@dataclass(frozen=True, slots=True)
class ResolvedMask:
    """Immutable foreground classification; background is internal negative space."""

    width: int
    height: int
    foreground_cells: tuple[bool, ...]
    source_states: tuple[MaskCellState, ...]

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise MaskContractError("resolved mask dimensions must be positive")
        foreground = tuple(bool(value) for value in self.foreground_cells)
        try:
            states = tuple(value if isinstance(value, MaskCellState) else MaskCellState(value) for value in self.source_states)
        except (TypeError, ValueError) as exc:
            raise MaskContractError("resolved mask source states are invalid") from exc
        if len(foreground) != self.width * self.height or len(states) != len(foreground):
            raise MaskContractError("resolved mask row-major lengths are inconsistent")
        object.__setattr__(self, "foreground_cells", foreground)
        object.__setattr__(self, "source_states", states)

    def index(self, x: int, y: int) -> int:
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise MaskContractError("resolved mask coordinate is out of bounds")
        return y * self.width + x

    def is_foreground(self, x: int, y: int) -> bool:
        return self.foreground_cells[self.index(x, y)]

    @property
    def foreground_count(self) -> int:
        return sum(self.foreground_cells)

    @property
    def occupancy_pct(self) -> int:
        return (self.foreground_count * 100) // (self.width * self.height)

    def row_major(self) -> tuple[bool, ...]:
        return self.foreground_cells
