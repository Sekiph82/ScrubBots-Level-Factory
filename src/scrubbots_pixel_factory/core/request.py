"""Immutable, versioned and canonical generation requests."""

from collections.abc import Mapping
from dataclasses import dataclass, field
import hashlib
import json
import math
from enum import Enum
from types import MappingProxyType
from typing import Any

from ..contracts import (
    Difficulty,
    resolve_dimensions,
    resolve_palette_subset,
    validate_palette_subset,
    parse_difficulty,
)


GENERATION_REQUEST_SCHEMA = "scrubbots-generation-request"
GENERATION_REQUEST_SCHEMA_VERSION = 1


class RequestContractError(ValueError):
    """Raised when a request or generator option violates the M02 contract."""


class GeneratorMode(str, Enum):
    """Strict explicit production modes; AUTO is intentionally absent."""

    MASK = "MASK"
    RULES = "RULES"
    WFC = "WFC"
    HYBRID = "HYBRID"

    @classmethod
    def parse(cls, value: object) -> str:
        if isinstance(value, cls):
            return value.value
        if type(value) is not str or value not in {
            cls.MASK,
            cls.RULES,
            cls.WFC,
            cls.HYBRID,
        }:
            raise RequestContractError(
                "generator_mode must be exactly MASK, RULES, WFC, or HYBRID"
            )
        return value


def _require_nonblank_string(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise RequestContractError(f"{label} must be a non-empty string")
    return value


def _freeze_json_value(value: object, path: str = "value") -> object:
    """Convert supported JSON values into recursively immutable values."""

    if value is None or type(value) is bool or type(value) is str:
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise RequestContractError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise RequestContractError(f"{path} mapping keys must be strings")
            frozen[key] = _freeze_json_value(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json_value(item, f"{path}[{index}]") for index, item in enumerate(value))
    raise RequestContractError(
        f"{path} contains unsupported value type {type(value).__name__}; use JSON-compatible values"
    )


def _thaw_json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _thaw_json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json_value(item) for item in value]
    return value


def _typed_seed(seed: int | str) -> dict[str, int | str]:
    return {"type": "int", "value": seed} if isinstance(seed, int) else {"type": "string", "value": seed}


@dataclass(frozen=True, slots=True)
class GeneratorOptions:
    """Versioned, deeply immutable generator-specific JSON options."""

    namespace: str = "default"
    version: int = 1
    values: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        namespace = _require_nonblank_string(self.namespace, "generator option namespace")
        if isinstance(self.version, bool) or not isinstance(self.version, int) or self.version < 1:
            raise RequestContractError("generator option version must be a positive integer")
        frozen = _freeze_json_value(self.values, "generator options")
        if not isinstance(frozen, Mapping):
            raise RequestContractError("generator options values must be a mapping")
        object.__setattr__(self, "namespace", namespace)
        object.__setattr__(self, "values", frozen)

    def canonical_dict(self) -> dict[str, object]:
        return {
            "namespace": self.namespace,
            "version": self.version,
            "values": _thaw_json_value(self.values),
        }


def _coerce_options(value: GeneratorOptions | Mapping[str, object] | None) -> GeneratorOptions:
    if value is None:
        return GeneratorOptions()
    if isinstance(value, GeneratorOptions):
        return value
    if not isinstance(value, Mapping):
        raise RequestContractError("generator_options must be a versioned mapping")
    required = {"namespace", "version", "values"}
    if set(value) != required:
        raise RequestContractError("generator_options requires exactly namespace, version, and values")
    return GeneratorOptions(
        namespace=value["namespace"],  # type: ignore[arg-type]
        version=value["version"],  # type: ignore[arg-type]
        values=value["values"],  # type: ignore[arg-type]
    )


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """A validated request whose nested configuration cannot be mutated."""

    difficulty: Difficulty | str
    seed: int | str
    generator_mode: str
    width: int | None = None
    height: int | None = None
    style: str | None = None
    theme: str | None = None
    palette_subset: tuple[str, ...] | list[str] | None = None
    generator_options: GeneratorOptions | Mapping[str, object] | None = None
    schema_version: int = GENERATION_REQUEST_SCHEMA_VERSION

    def __post_init__(self) -> None:
        try:
            difficulty = parse_difficulty(self.difficulty)
        except (TypeError, ValueError) as exc:
            raise RequestContractError(str(exc)) from exc
        if isinstance(self.seed, bool) or not isinstance(self.seed, (int, str)):
            raise RequestContractError("seed must be an integer or string, excluding bool")
        mode = GeneratorMode.parse(self.generator_mode)
        if isinstance(self.schema_version, bool) or self.schema_version != GENERATION_REQUEST_SCHEMA_VERSION:
            raise RequestContractError("unsupported generation request schema version")
        for label, value in (("style", self.style), ("theme", self.theme)):
            if value is not None:
                _require_nonblank_string(value, label)
        try:
            if self.width is not None and self.height is not None:
                resolve_dimensions(difficulty, self.width, self.height)
            elif self.width is not None:
                resolve_dimensions(difficulty, self.width, None, seed=self.seed)
            elif self.height is not None:
                resolve_dimensions(difficulty, None, self.height, seed=self.seed)
            normalized_subset = (
                None
                if self.palette_subset is None
                else validate_palette_subset(difficulty, self.palette_subset)
            )
        except (TypeError, ValueError) as exc:
            raise RequestContractError(str(exc)) from exc
        object.__setattr__(self, "difficulty", difficulty)
        object.__setattr__(self, "generator_mode", mode)
        object.__setattr__(self, "palette_subset", normalized_subset)
        object.__setattr__(self, "generator_options", _coerce_options(self.generator_options))

    @property
    def options(self) -> GeneratorOptions:
        return self.generator_options  # type: ignore[return-value]

    @property
    def requested_palette_subset(self) -> tuple[str, ...] | None:
        return self.palette_subset  # type: ignore[return-value]

    def stage_seed(self, stage: str) -> str:
        from .rng import DeterministicRNG

        return DeterministicRNG(self.seed).stage_seed(stage)

    def resolve_dimensions(self) -> tuple[int, int]:
        return resolve_dimensions(
            self.difficulty,
            self.width,
            self.height,
            seed=self.stage_seed("dimension"),
        )

    def resolve_palette_subset(self) -> tuple[str, ...]:
        if self.palette_subset is not None:
            return self.palette_subset
        return resolve_palette_subset(self.difficulty, seed=self.stage_seed("palette"))

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": GENERATION_REQUEST_SCHEMA,
            "schema_version": self.schema_version,
            "difficulty": self.difficulty.value,
            "width": self.width,
            "height": self.height,
            "seed": _typed_seed(self.seed),
            "generator_mode": self.generator_mode,
            "style": self.style,
            "theme": self.theme,
            "palette_subset": list(self.palette_subset) if self.palette_subset is not None else None,
            "generator_options": self.generator_options.canonical_dict(),
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
