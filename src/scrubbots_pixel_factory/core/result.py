"""Immutable validated success/failure results for the deterministic core."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from ..contracts import validate_dimensions, validate_used_color_count
from .request import (
    GenerationRequest,
    GeneratorMode,
    RequestContractError,
    _freeze_json_value,
    _thaw_json_value,
    _typed_seed,
)
from .rng import RNG_ALGORITHM, STAGE_DOMAINS


GENERATION_RESULT_SCHEMA = "scrubbots-generation-result"
GENERATION_RESULT_SCHEMA_VERSION = 1
_HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class ResultContractError(ValueError):
    """Raised when a generation result violates the M02 contract."""


class ResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class FailureCode(str, Enum):
    INVALID_REQUEST = "INVALID_REQUEST"
    GENERATION_FAILED = "GENERATION_FAILED"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"


GenerationFailureCode = FailureCode


def _nonblank(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ResultContractError(f"{label} must be a non-empty string")
    return value


def _validate_provenance(value: object, request: GenerationRequest) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResultContractError("provenance must be a JSON-compatible mapping")
    try:
        frozen = _freeze_json_value(value, "provenance")
    except RequestContractError as exc:
        raise ResultContractError(str(exc)) from exc
    if not isinstance(frozen, Mapping):
        raise ResultContractError("provenance must be a mapping")
    if not set(frozen).issubset({"stage_seeds", "retry_seeds"}):
        raise ResultContractError("provenance contains unsupported fields")
    stage_seeds = frozen.get("stage_seeds")
    if not isinstance(stage_seeds, Mapping) or set(stage_seeds) != set(STAGE_DOMAINS):
        raise ResultContractError(
            "provenance.stage_seeds must contain exactly the five named M02 stages"
        )
    for stage in STAGE_DOMAINS:
        seed = stage_seeds[stage]
        if type(seed) is not str or _HEX_DIGEST.fullmatch(seed) is None:
            raise ResultContractError(f"provenance stage seed is malformed: {stage}")
    from .rng import DeterministicRNG

    if dict(stage_seeds) != DeterministicRNG(request.seed).stage_seeds():
        raise ResultContractError("provenance stage seeds do not match the request seed")
    if "retry_seeds" in frozen:
        retry_seeds = frozen["retry_seeds"]
        if not isinstance(retry_seeds, Mapping):
            raise ResultContractError("provenance.retry_seeds must be a mapping")
        expected_rng = DeterministicRNG(request.seed)
        for attempt_key, retry_seed in retry_seeds.items():
            if type(attempt_key) is not str or re.fullmatch(r"(?:0|[1-9][0-9]*)", attempt_key) is None:
                raise ResultContractError("retry provenance attempt keys must be canonical non-negative integers")
            try:
                expected_retry_seed = expected_rng.retry_seed(int(attempt_key))
            except (TypeError, ValueError, OverflowError) as exc:
                raise ResultContractError("retry provenance attempt is invalid") from exc
            if type(retry_seed) is not str or _HEX_DIGEST.fullmatch(retry_seed) is None:
                raise ResultContractError("retry provenance seed is malformed")
            if retry_seed != expected_retry_seed:
                raise ResultContractError("retry provenance seed does not match the request seed/attempt")
    return frozen


@dataclass(frozen=True, slots=True, init=False)
class GenerationResult:
    """A complete immutable result or a fail-closed result without partial output."""

    schema: str
    schema_version: int
    status: ResultStatus
    request: GenerationRequest | None
    width: int | None
    height: int | None
    logical_grid: tuple[str, ...] | None
    used_palette: tuple[str, ...]
    generator_mode: str | None
    generator_id: str | None
    generator_version: str | None
    seed: int | str | None
    rng_algorithm: str | None
    provenance: Mapping[str, object] | None
    failure_code: FailureCode | None
    failure_reason: str | None

    @classmethod
    def _from_validated_fields(
        cls,
        *,
        status: ResultStatus,
        request: GenerationRequest | None,
        width: int | None,
        height: int | None,
        logical_grid: tuple[str, ...] | None,
        used_palette: tuple[str, ...],
        generator_mode: str | None,
        generator_id: str | None,
        generator_version: str | None,
        seed: int | str | None,
        rng_algorithm: str | None,
        provenance: Mapping[str, object] | None,
        failure_code: FailureCode | None,
        failure_reason: str | None,
    ) -> "GenerationResult":
        result = object.__new__(cls)
        object.__setattr__(result, "schema", GENERATION_RESULT_SCHEMA)
        object.__setattr__(result, "schema_version", GENERATION_RESULT_SCHEMA_VERSION)
        object.__setattr__(result, "status", status)
        object.__setattr__(result, "request", request)
        object.__setattr__(result, "width", width)
        object.__setattr__(result, "height", height)
        object.__setattr__(result, "logical_grid", logical_grid)
        object.__setattr__(result, "used_palette", used_palette)
        object.__setattr__(result, "generator_mode", generator_mode)
        object.__setattr__(result, "generator_id", generator_id)
        object.__setattr__(result, "generator_version", generator_version)
        object.__setattr__(result, "seed", seed)
        object.__setattr__(result, "rng_algorithm", rng_algorithm)
        object.__setattr__(result, "provenance", provenance)
        object.__setattr__(result, "failure_code", failure_code)
        object.__setattr__(result, "failure_reason", failure_reason)
        return result

    @classmethod
    def success(
        cls,
        *,
        request: GenerationRequest,
        width: int,
        height: int,
        logical_grid: object,
        generator_id: str,
        generator_version: str,
        generator_mode: str | None = None,
        seed: int | str | None = None,
        rng_algorithm: str,
        provenance: Mapping[str, object],
    ) -> "GenerationResult":
        if not isinstance(request, GenerationRequest):
            raise ResultContractError("successful result requires a GenerationRequest")
        if isinstance(logical_grid, (str, bytes, bytearray)):
            raise ResultContractError("logical_grid must be an iterable of C-ID cells")
        try:
            cells = tuple(logical_grid)  # type: ignore[arg-type]
        except TypeError as exc:
            raise ResultContractError("logical_grid must be an iterable of C-ID cells") from exc
        try:
            validate_dimensions(request.difficulty, width, height)
            if request.width is not None and width != request.width:
                raise ResultContractError("result width does not match explicit request width")
            if request.height is not None and height != request.height:
                raise ResultContractError("result height does not match explicit request height")
            if len(cells) != width * height or any(type(cell) is not str for cell in cells):
                raise ResultContractError("logical_grid length must equal width multiplied by height")
            used = validate_used_color_count(request.difficulty, cells)
        except ResultContractError:
            raise
        except (TypeError, ValueError) as exc:
            raise ResultContractError(str(exc)) from exc
        if request.palette_subset is not None and not set(used).issubset(request.palette_subset):
            raise ResultContractError("logical_grid uses a color outside the requested palette subset")
        if type(rng_algorithm) is not str or rng_algorithm != RNG_ALGORITHM:
            raise ResultContractError("result must record the project RNG algorithm/version")
        mode = GeneratorMode.parse(request.generator_mode if generator_mode is None else generator_mode)
        if mode != request.generator_mode:
            raise ResultContractError("result generator mode does not match the request")
        identifier = _nonblank(generator_id, "generator_id")
        version = _nonblank(generator_version, "generator_version")
        checked_provenance = _validate_provenance(provenance, request)
        result_seed = request.seed if seed is None else seed
        if type(result_seed) is bool or not isinstance(result_seed, (int, str)) or result_seed != request.seed:
            raise ResultContractError("result seed does not match the request")
        return cls._from_validated_fields(
            status=ResultStatus.SUCCESS,
            request=request,
            width=width,
            height=height,
            logical_grid=cells,
            used_palette=used,
            generator_mode=mode,
            generator_id=identifier,
            generator_version=version,
            seed=result_seed,
            rng_algorithm=rng_algorithm,
            provenance=checked_provenance,
            failure_code=None,
            failure_reason=None,
        )

    @classmethod
    def failure(
        cls,
        *,
        code: FailureCode | str,
        reason: str,
        request: GenerationRequest | None = None,
    ) -> "GenerationResult":
        try:
            failure_code = code if isinstance(code, FailureCode) else FailureCode(code)
        except ValueError as exc:
            raise ResultContractError("failure code must be a stable M02 failure code") from exc
        failure_reason = _nonblank(reason, "failure reason")
        if request is not None and not isinstance(request, GenerationRequest):
            raise ResultContractError("failure request must be a GenerationRequest or None")
        return cls._from_validated_fields(
            status=ResultStatus.FAILURE,
            request=request,
            width=None,
            height=None,
            logical_grid=None,
            used_palette=(),
            generator_mode=request.generator_mode if request is not None else None,
            generator_id=None,
            generator_version=None,
            seed=request.seed if request is not None else None,
            rng_algorithm=None,
            provenance=None,
            failure_code=failure_code,
            failure_reason=failure_reason,
        )

    @property
    def is_success(self) -> bool:
        return self.status is ResultStatus.SUCCESS

    @property
    def ok(self) -> bool:
        return self.is_success

    def canonical_dict(self) -> dict[str, object]:
        if self.is_success:
            return {
                "schema": self.schema,
                "schema_version": self.schema_version,
                "status": self.status.value,
                "request": self.request.canonical_dict(),  # type: ignore[union-attr]
                "resolved_dimensions": {"width": self.width, "height": self.height},
                "logical_grid": list(self.logical_grid or ()),
                "used_palette": list(self.used_palette),
                "generator": {
                    "mode": self.generator_mode,
                    "id": self.generator_id,
                    "version": self.generator_version,
                },
                "seed": _typed_seed(self.seed),  # type: ignore[arg-type]
                "rng": {
                    "algorithm": self.rng_algorithm,
                    "provenance": _thaw_json_value(self.provenance),
                },
            }
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "status": self.status.value,
            "request": self.request.canonical_dict() if self.request is not None else None,
            "resolved_dimensions": None,
            "logical_grid": None,
            "used_palette": [],
            "generator": None,
            "seed": _typed_seed(self.seed) if self.seed is not None else None,
            "rng": None,
            "failure": {"code": self.failure_code.value, "reason": self.failure_reason},
        }

    def canonical_bytes(self) -> bytes:
        return json.dumps(
            self.canonical_dict(),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def canonical_json(self) -> str:
        return self.canonical_bytes().decode("utf-8")

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
