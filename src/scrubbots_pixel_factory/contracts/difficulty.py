"""Strict production difficulty and independent board-dimension contracts."""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType

from ._stable_select import stable_index, validate_seed


class DimensionContractError(ValueError):
    """Raised when a production difficulty or dimension is illegal."""


class Difficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    VERY_HARD = "VERY_HARD"


@dataclass(frozen=True, slots=True)
class DimensionBand:
    minimum: int
    maximum: int

    def contains(self, value: object) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and self.minimum <= value <= self.maximum


DIFFICULTY_BANDS = MappingProxyType(
    {
        Difficulty.EASY: DimensionBand(20, 29),
        Difficulty.MEDIUM: DimensionBand(30, 39),
        Difficulty.HARD: DimensionBand(40, 49),
        Difficulty.VERY_HARD: DimensionBand(50, 59),
    }
)


def parse_difficulty(value: Difficulty | str) -> Difficulty:
    if isinstance(value, Difficulty):
        return value
    if type(value) is str:
        try:
            return Difficulty(value)
        except ValueError as exc:
            raise DimensionContractError(
                f"unsupported production difficulty {value!r}; use EASY, MEDIUM, HARD, or VERY_HARD"
            ) from exc
    raise DimensionContractError(f"difficulty must be a strict production name: {value!r}")


def dimension_band(difficulty: Difficulty | str) -> DimensionBand:
    return DIFFICULTY_BANDS[parse_difficulty(difficulty)]


def validate_width(difficulty: Difficulty | str, width: int) -> int:
    band = dimension_band(difficulty)
    if isinstance(width, bool) or not isinstance(width, int) or not band.contains(width):
        raise DimensionContractError(
            f"{parse_difficulty(difficulty).value} width must be in {band.minimum}..{band.maximum}; received {width!r}"
        )
    return width


def validate_height(difficulty: Difficulty | str, height: int) -> int:
    band = dimension_band(difficulty)
    if isinstance(height, bool) or not isinstance(height, int) or not band.contains(height):
        raise DimensionContractError(
            f"{parse_difficulty(difficulty).value} height must be in {band.minimum}..{band.maximum}; received {height!r}"
        )
    return height


def validate_dimensions(difficulty: Difficulty | str, width: int, height: int) -> tuple[int, int]:
    """Validate each axis independently and return the unchanged rectangle."""

    return validate_width(difficulty, width), validate_height(difficulty, height)


def is_legal_dimensions(difficulty: Difficulty | str, width: int, height: int) -> bool:
    try:
        validate_dimensions(difficulty, width, height)
    except (DimensionContractError, TypeError):
        return False
    return True


def select_dimensions(difficulty: Difficulty | str, seed: int | str) -> tuple[int, int]:
    """Select width and height with separate stable hash domains."""

    selected = parse_difficulty(difficulty)
    validate_seed(seed)
    band = DIFFICULTY_BANDS[selected]
    span = band.maximum - band.minimum + 1
    width = band.minimum + stable_index("dimensions.width", seed, span)
    height = band.minimum + stable_index("dimensions.height", seed, span)
    return width, height


def resolve_dimensions(
    difficulty: Difficulty | str,
    width: int | None = None,
    height: int | None = None,
    *,
    seed: int | str | None = None,
) -> tuple[int, int]:
    """Resolve explicit axes or fill missing axes from a stable seed."""

    selected = parse_difficulty(difficulty)
    if width is None or height is None:
        if seed is None:
            raise DimensionContractError("seed is required when width or height is omitted")
        automatic_width, automatic_height = select_dimensions(selected, seed)
        width = automatic_width if width is None else width
        height = automatic_height if height is None else height
    return validate_dimensions(selected, width, height)
