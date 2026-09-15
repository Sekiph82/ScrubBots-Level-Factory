"""Canonical production dimension envelope shared by all contract layers."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DimensionEnvelope:
    """Inclusive independent width/height bounds for production boards."""

    minimum: int
    maximum: int

    def contains(self, value: object) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and self.minimum <= value <= self.maximum

    @property
    def span(self) -> int:
        return self.maximum - self.minimum + 1


PRODUCTION_DIMENSION_ENVELOPE = DimensionEnvelope(20, 59)

__all__ = ["DimensionEnvelope", "PRODUCTION_DIMENSION_ENVELOPE"]
