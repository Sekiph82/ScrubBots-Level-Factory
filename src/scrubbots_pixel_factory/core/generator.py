"""Common headless generator interface; no production engines are defined in M02."""

from typing import Protocol, runtime_checkable

from .request import GenerationRequest
from .result import GenerationResult
from .rng import DeterministicRNG


@runtime_checkable
class PixelGenerator(Protocol):
    """A generator receives validated immutable input and an explicit RNG stream."""

    generator_id: str
    generator_version: str

    def generate(self, request: GenerationRequest, rng: DeterministicRNG) -> GenerationResult:
        """Return a complete validated result or an explicit failure result."""
