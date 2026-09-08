"""Deterministic, headless generation contracts for PAG-M02."""

from .generator import PixelGenerator
from .request import (
    GENERATION_REQUEST_SCHEMA,
    GENERATION_REQUEST_SCHEMA_VERSION,
    GenerationRequest,
    GeneratorMode,
    GeneratorOptions,
    RequestContractError,
)
from .result import (
    GENERATION_RESULT_SCHEMA,
    GENERATION_RESULT_SCHEMA_VERSION,
    FailureCode,
    GenerationFailureCode,
    GenerationResult,
    ResultContractError,
    ResultStatus,
)
from .rng import (
    RNG_ALGORITHM,
    STAGE_DOMAINS,
    DeterministicRNG,
    RNGContractError,
)

__all__ = [
    "DeterministicRNG",
    "FailureCode",
    "GenerationFailureCode",
    "GenerationRequest",
    "GenerationResult",
    "GENERATION_REQUEST_SCHEMA",
    "GENERATION_REQUEST_SCHEMA_VERSION",
    "GENERATION_RESULT_SCHEMA",
    "GENERATION_RESULT_SCHEMA_VERSION",
    "GeneratorMode",
    "GeneratorOptions",
    "PixelGenerator",
    "RNG_ALGORITHM",
    "RNGContractError",
    "RequestContractError",
    "ResultContractError",
    "ResultStatus",
    "STAGE_DOMAINS",
]
