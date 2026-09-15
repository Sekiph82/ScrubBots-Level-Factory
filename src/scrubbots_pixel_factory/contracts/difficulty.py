"""Strict production difficulty and versioned independent board contracts."""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType

from ._stable_select import stable_index, validate_seed
from .dimensions import PRODUCTION_DIMENSION_ENVELOPE


class DimensionContractError(ValueError):
    """Raised when a production difficulty or dimension is illegal."""


class Difficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    VERY_HARD = "VERY_HARD"


@dataclass(frozen=True, slots=True)
class DimensionBand:
    """Compatibility-shaped view of the canonical independent envelope."""

    minimum: int
    maximum: int

    def contains(self, value: object) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and self.minimum <= value <= self.maximum


CURRENT_DIMENSION_SCHEMA_VERSION = 2
LEGACY_DIMENSION_SCHEMA_VERSION = 1
SUPPORTED_DIMENSION_SCHEMA_VERSIONS = (LEGACY_DIMENSION_SCHEMA_VERSION, CURRENT_DIMENSION_SCHEMA_VERSION)
_CURRENT_BAND = DimensionBand(PRODUCTION_DIMENSION_ENVELOPE.minimum, PRODUCTION_DIMENSION_ENVELOPE.maximum)
_LEGACY_DIFFICULTY_BANDS = MappingProxyType(
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


def _dimension_band(difficulty: Difficulty | str, schema_version: int) -> DimensionBand:
    selected = parse_difficulty(difficulty)
    if type(schema_version) is not int:
        raise DimensionContractError(f"unsupported dimension schema version {schema_version!r}")
    if schema_version == CURRENT_DIMENSION_SCHEMA_VERSION:
        return _CURRENT_BAND
    if schema_version == LEGACY_DIMENSION_SCHEMA_VERSION:
        return _LEGACY_DIFFICULTY_BANDS[selected]
    raise DimensionContractError(f"unsupported dimension schema version {schema_version!r}")


def dimension_band(difficulty: Difficulty | str) -> DimensionBand:
    """Return the current independent envelope; difficulty is classification only."""

    parse_difficulty(difficulty)
    return _CURRENT_BAND


def validate_width(
    difficulty: Difficulty | str,
    width: int,
    *,
    schema_version: int = CURRENT_DIMENSION_SCHEMA_VERSION,
) -> int:
    band = _dimension_band(difficulty, schema_version)
    axis = "production" if schema_version == CURRENT_DIMENSION_SCHEMA_VERSION else parse_difficulty(difficulty).value
    if isinstance(width, bool) or not isinstance(width, int) or not band.contains(width):
        raise DimensionContractError(
            f"{axis} width must be in {band.minimum}..{band.maximum}; received {width!r}"
        )
    return width


def validate_height(
    difficulty: Difficulty | str,
    height: int,
    *,
    schema_version: int = CURRENT_DIMENSION_SCHEMA_VERSION,
) -> int:
    band = _dimension_band(difficulty, schema_version)
    axis = "production" if schema_version == CURRENT_DIMENSION_SCHEMA_VERSION else parse_difficulty(difficulty).value
    if isinstance(height, bool) or not isinstance(height, int) or not band.contains(height):
        raise DimensionContractError(
            f"{axis} height must be in {band.minimum}..{band.maximum}; received {height!r}"
        )
    return height


def validate_dimensions(
    difficulty: Difficulty | str,
    width: int,
    height: int,
    *,
    schema_version: int = CURRENT_DIMENSION_SCHEMA_VERSION,
) -> tuple[int, int]:
    """Validate each axis independently for the selected request schema."""

    return (
        validate_width(difficulty, width, schema_version=schema_version),
        validate_height(difficulty, height, schema_version=schema_version),
    )


def is_legal_dimensions(
    difficulty: Difficulty | str,
    width: int,
    height: int,
    *,
    schema_version: int = CURRENT_DIMENSION_SCHEMA_VERSION,
) -> bool:
    try:
        validate_dimensions(difficulty, width, height, schema_version=schema_version)
    except (DimensionContractError, TypeError):
        return False
    return True


def select_dimensions(
    difficulty: Difficulty | str,
    seed: int | str,
    *,
    schema_version: int = CURRENT_DIMENSION_SCHEMA_VERSION,
) -> tuple[int, int]:
    """Select dimensions with separate stable width and height domains."""

    band = _dimension_band(difficulty, schema_version)
    validate_seed(seed)
    width = band.minimum + stable_index("dimensions.width", seed, band.maximum - band.minimum + 1)
    height = band.minimum + stable_index("dimensions.height", seed, band.maximum - band.minimum + 1)
    return width, height


def resolve_dimensions(
    difficulty: Difficulty | str,
    width: int | None = None,
    height: int | None = None,
    *,
    seed: int | str | None = None,
    schema_version: int = CURRENT_DIMENSION_SCHEMA_VERSION,
) -> tuple[int, int]:
    """Resolve explicit axes or fill missing axes from a stable versioned seed."""

    parse_difficulty(difficulty)
    if type(schema_version) is not int or schema_version not in SUPPORTED_DIMENSION_SCHEMA_VERSIONS:
        raise DimensionContractError(f"unsupported dimension schema version {schema_version!r}")
    if width is None or height is None:
        if seed is None:
            raise DimensionContractError("seed is required when width or height is omitted")
        automatic_width, automatic_height = select_dimensions(difficulty, seed, schema_version=schema_version)
        width = automatic_width if width is None else width
        height = automatic_height if height is None else height
    return validate_dimensions(difficulty, width, height, schema_version=schema_version)


__all__ = [
    "CURRENT_DIMENSION_SCHEMA_VERSION",
    "DimensionBand",
    "DimensionContractError",
    "Difficulty",
    "LEGACY_DIMENSION_SCHEMA_VERSION",
    "SUPPORTED_DIMENSION_SCHEMA_VERSIONS",
    "dimension_band",
    "is_legal_dimensions",
    "parse_difficulty",
    "resolve_dimensions",
    "select_dimensions",
    "validate_dimensions",
    "validate_height",
    "validate_width",
]
