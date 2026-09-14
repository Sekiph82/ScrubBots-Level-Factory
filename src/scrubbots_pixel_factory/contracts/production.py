"""Current production legality for semantic LEVEL_ART artifacts."""

from collections.abc import Iterable

from .color_usage import actual_used_palette_ids


PRODUCTION_DIMENSION_MIN = 20
PRODUCTION_DIMENSION_MAX = 59
PRODUCTION_COLOR_MIN = 3
PRODUCTION_COLOR_MAX = 12


class ProductionContractError(ValueError):
    """Raised when current production LEVEL_ART legality is violated."""


def validate_production_width(width: int) -> int:
    if isinstance(width, bool) or not isinstance(width, int) or not PRODUCTION_DIMENSION_MIN <= width <= PRODUCTION_DIMENSION_MAX:
        raise ProductionContractError(
            f"production width must be in {PRODUCTION_DIMENSION_MIN}..{PRODUCTION_DIMENSION_MAX}; received {width!r}"
        )
    return width


def validate_production_height(height: int) -> int:
    if isinstance(height, bool) or not isinstance(height, int) or not PRODUCTION_DIMENSION_MIN <= height <= PRODUCTION_DIMENSION_MAX:
        raise ProductionContractError(
            f"production height must be in {PRODUCTION_DIMENSION_MIN}..{PRODUCTION_DIMENSION_MAX}; received {height!r}"
        )
    return height


def validate_production_dimensions(width: int, height: int) -> tuple[int, int]:
    """Validate independent production axes; rectangular boards are legal."""

    return validate_production_width(width), validate_production_height(height)


def validate_production_used_color_count(cells: Iterable[str]) -> tuple[str, ...]:
    """Validate the global 3..12 canonical-color envelope."""

    used = actual_used_palette_ids(cells)
    if not PRODUCTION_COLOR_MIN <= len(used) <= PRODUCTION_COLOR_MAX:
        raise ProductionContractError(
            f"production LEVEL_ART requires {PRODUCTION_COLOR_MIN}..{PRODUCTION_COLOR_MAX} distinct used colors; received {len(used)}"
        )
    return used


__all__ = [
    "PRODUCTION_COLOR_MAX",
    "PRODUCTION_COLOR_MIN",
    "PRODUCTION_DIMENSION_MAX",
    "PRODUCTION_DIMENSION_MIN",
    "ProductionContractError",
    "validate_production_dimensions",
    "validate_production_height",
    "validate_production_used_color_count",
    "validate_production_width",
]
