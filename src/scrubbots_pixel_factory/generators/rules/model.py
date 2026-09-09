"""Immutable recipe metadata and controlled logical geometry for M04."""

from dataclasses import dataclass, field
import hashlib


class RuleContractError(ValueError):
    """Raised when a RULES geometry or recipe contract cannot be satisfied."""


@dataclass(frozen=True, slots=True)
class RecipeStep:
    operation: str
    parameters: tuple[tuple[str, int | str | bool], ...] = ()
    domain: str = "step"

    def __post_init__(self) -> None:
        if type(self.operation) is not str or not self.operation:
            raise RuleContractError("recipe step operation must be non-empty")
        if type(self.domain) is not str or not self.domain:
            raise RuleContractError("recipe step domain must be non-empty")
        keys = tuple(key for key, _ in self.parameters)
        if any(type(key) is not str or not key for key in keys) or len(set(keys)) != len(keys):
            raise RuleContractError("recipe step parameters require unique non-empty keys")
        object.__setattr__(self, "parameters", tuple(sorted(self.parameters, key=lambda item: item[0])))


@dataclass(frozen=True, slots=True)
class CompositionRecipe:
    recipe_id: str
    version: int
    layers: tuple[RecipeStep, ...]
    occupancy_floor_pct: int
    occupancy_ceiling_pct: int
    max_color_dominance_pct: int = 82
    min_color_region_size: int = 2

    def __post_init__(self) -> None:
        if type(self.recipe_id) is not str or not self.recipe_id:
            raise RuleContractError("recipe ID must be non-empty")
        if type(self.version) is not int or isinstance(self.version, bool) or self.version < 1:
            raise RuleContractError("recipe version must be a positive integer")
        if not self.layers:
            raise RuleContractError("recipe must contain at least one layer")
        if not 0 <= self.occupancy_floor_pct <= self.occupancy_ceiling_pct <= 100:
            raise RuleContractError("recipe occupancy bounds must be ordered percentages")
        if not 50 <= self.max_color_dominance_pct <= 100:
            raise RuleContractError("recipe dominance cap must be 50..100 percent")
        if self.min_color_region_size < 2:
            raise RuleContractError("M04 minimum color region size must be at least two cells")
        object.__setattr__(self, "layers", tuple(self.layers))


class RuleCanvas:
    """Mutable only through checked methods; all geometry is logical cells."""

    __slots__ = ("width", "height", "_occupied", "_regions", "_protected_occupied", "_protected_negative")

    def __init__(self, width: int, height: int) -> None:
        if isinstance(width, bool) or not isinstance(width, int) or width <= 0:
            raise RuleContractError("canvas width must be a positive integer")
        if isinstance(height, bool) or not isinstance(height, int) or height <= 0:
            raise RuleContractError("canvas height must be a positive integer")
        self.width = width
        self.height = height
        self._occupied: set[int] = set()
        self._regions: dict[int, str] = {}
        self._protected_occupied: set[int] = set()
        self._protected_negative: set[int] = set()

    @property
    def size(self) -> int:
        return self.width * self.height

    def index(self, x: int, y: int) -> int:
        if isinstance(x, bool) or isinstance(y, bool) or not isinstance(x, int) or not isinstance(y, int):
            raise RuleContractError("canvas coordinates must be integers")
        if not self.in_bounds(x, y):
            raise RuleContractError("canvas coordinate is out of bounds")
        return y * self.width + x

    def coord(self, index: int) -> tuple[int, int]:
        if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < self.size:
            raise RuleContractError("canvas index is out of bounds")
        return index % self.width, index // self.width

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def neighbors(self, index: int) -> tuple[int, ...]:
        x, y = self.coord(index)
        result: list[int] = []
        if x:
            result.append(index - 1)
        if x + 1 < self.width:
            result.append(index + 1)
        if y:
            result.append(index - self.width)
        if y + 1 < self.height:
            result.append(index + self.width)
        return tuple(result)

    @property
    def occupied(self) -> frozenset[int]:
        return frozenset(self._occupied)

    @property
    def negative(self) -> frozenset[int]:
        return frozenset(set(range(self.size)) - self._occupied)

    @property
    def protected_occupied(self) -> frozenset[int]:
        return frozenset(self._protected_occupied)

    @property
    def protected_negative(self) -> frozenset[int]:
        return frozenset(self._protected_negative)

    @property
    def regions(self) -> dict[str, frozenset[int]]:
        labels = sorted(set(self._regions.values()))
        return {label: frozenset(index for index, value in self._regions.items() if value == label) for label in labels}

    def mark(self, index: int, label: str = "occupied", *, protected: bool = False) -> None:
        self.coord(index)
        if index in self._protected_negative:
            raise RuleContractError("protected negative-space cell cannot be occupied")
        self._occupied.add(index)
        self._regions[index] = label
        if protected:
            self._protected_occupied.add(index)

    def mark_many(self, indices: set[int] | frozenset[int], label: str = "occupied", *, protected: bool = False) -> None:
        for index in sorted(indices):
            self.mark(index, label, protected=protected)

    def carve(self, index: int, *, protected: bool = False) -> None:
        self.coord(index)
        if index in self._protected_occupied:
            raise RuleContractError("protected occupied cell cannot be carved")
        self._occupied.discard(index)
        self._regions.pop(index, None)
        if protected:
            self._protected_negative.add(index)

    def protect_negative(self, indices: set[int] | frozenset[int]) -> None:
        for index in sorted(indices):
            self.coord(index)
            if index in self._occupied:
                raise RuleContractError("protected negative-space cell must be empty")
            self._protected_negative.add(index)

    def protect_occupied(self, indices: set[int] | frozenset[int], label: str = "protected") -> None:
        self.mark_many(indices, label, protected=True)

    def set_region(self, index: int, label: str) -> None:
        if index not in self._occupied:
            raise RuleContractError("only occupied cells may receive a region label")
        if type(label) is not str or not label:
            raise RuleContractError("region label must be non-empty")
        self._regions[index] = label

    def copy(self) -> "RuleCanvas":
        other = RuleCanvas(self.width, self.height)
        other._occupied = set(self._occupied)
        other._regions = dict(self._regions)
        other._protected_occupied = set(self._protected_occupied)
        other._protected_negative = set(self._protected_negative)
        return other

    def geometry_bytes(self) -> bytes:
        return bytes(1 if index in self._occupied else 0 for index in range(self.size))

    def geometry_digest(self) -> str:
        return hashlib.sha256(self.geometry_bytes()).hexdigest()

    def region_digest(self) -> str:
        payload = "\n".join(f"{index}:{self._regions.get(index, 'NEGATIVE')}" for index in range(self.size))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class RuleCandidate:
    canvas: RuleCanvas
    recipe: CompositionRecipe
    colors: tuple[str, ...]
    logical_grid: tuple[str, ...]
    result: object
    attempt: int
    primitive_id: str
    region_labels: tuple[str, ...] = field(default_factory=tuple)
