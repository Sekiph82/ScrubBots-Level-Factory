"""Owner-locked contracts shared by every ZIP-derived production stage."""

MIN_COLUMN_COUNT = 3
MAX_COLUMN_COUNT = 5
DEFAULT_COLUMN_COUNT = 3
VISIBLE_PREVIEW_DEPTH = 3
BASELINE_SLOT_COUNT = 5


def validate_column_count(value: object) -> int:
    """Return an explicitly selected 3/4/5 supply column count."""

    if type(value) is not int or not MIN_COLUMN_COUNT <= value <= MAX_COLUMN_COUNT:
        raise ValueError("column_count must be exactly 3, 4, or 5")
    return value


__all__ = [
    "BASELINE_SLOT_COUNT",
    "DEFAULT_COLUMN_COUNT",
    "MAX_COLUMN_COUNT",
    "MIN_COLUMN_COUNT",
    "VISIBLE_PREVIEW_DEPTH",
    "validate_column_count",
]
