"""Immutable contracts for the project-owned overlapping-pattern WFC engine."""

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Mapping

from ...contracts import CANONICAL_PALETTE, validate_dimensions


class WFCContractError(ValueError):
    """Raised when WFC configuration, exemplars, or derived tables are invalid."""


EXEMPLAR_ROLES = ("TRAINING_MOTIF", "PRODUCTION_ARTIFACT")
OWNERSHIP_CLASSES = ("SYNTHETIC_TEST_ONLY", "OWNER_SUPPLIED_UNAPPROVED", "OWNER_APPROVED")
DIRECTIONS = ("LEFT", "RIGHT", "UP", "DOWN")


def _require_text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise WFCContractError(f"{label} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class Exemplar:
    schema: str
    version: int
    exemplar_id: str
    role: str
    width: int
    height: int
    pixels: tuple[str, ...]
    provenance_type: str
    provenance_description: str
    ownership: str
    approved_by: str | None = None
    production_difficulty: str | None = None

    def __post_init__(self) -> None:
        if self.schema != "scrubbots-wfc-exemplar" or self.version != 1:
            raise WFCContractError("unsupported WFC exemplar schema/version")
        _require_text(self.exemplar_id, "exemplar_id")
        if self.role not in EXEMPLAR_ROLES:
            raise WFCContractError("unknown WFC exemplar role")
        if isinstance(self.width, bool) or not isinstance(self.width, int) or self.width < 2:
            raise WFCContractError("exemplar width must be at least two cells")
        if isinstance(self.height, bool) or not isinstance(self.height, int) or self.height < 2:
            raise WFCContractError("exemplar height must be at least two cells")
        pixels = tuple(self.pixels)
        if len(pixels) != self.width * self.height:
            raise WFCContractError("exemplar pixel count does not match dimensions")
        for pixel in pixels:
            if type(pixel) is not str:
                raise WFCContractError("exemplar pixels must be canonical logical C-IDs")
            try:
                CANONICAL_PALETTE.validate_logical_id(pixel)
            except (TypeError, ValueError) as exc:
                raise WFCContractError("exemplar pixels must be canonical logical C-IDs") from exc
        if self.ownership not in OWNERSHIP_CLASSES:
            raise WFCContractError("unknown exemplar ownership/use classification")
        _require_text(self.provenance_type, "provenance_type")
        _require_text(self.provenance_description, "provenance_description")
        if self.ownership == "SYNTHETIC_TEST_ONLY" and self.approved_by is not None:
            raise WFCContractError("synthetic test exemplars cannot be owner-approved")
        if self.ownership == "OWNER_APPROVED":
            _require_text(self.approved_by, "approved_by")
        elif self.approved_by is not None:
            raise WFCContractError("approved_by is only valid for owner-approved exemplars")
        if self.role == "PRODUCTION_ARTIFACT":
            _require_text(self.production_difficulty, "production_difficulty")
            try:
                validate_dimensions(self.production_difficulty, self.width, self.height)
            except (TypeError, ValueError) as exc:
                raise WFCContractError("production exemplar dimensions are illegal for its difficulty") from exc
        object.__setattr__(self, "pixels", pixels)

    @property
    def source_palette(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.pixels), key=lambda value: int(value[1:])))

    @property
    def provenance_identity(self) -> str:
        return f"{self.provenance_type}:{self.provenance_description}"

    @property
    def digest(self) -> str:
        canonical = {
            "schema": self.schema, "version": self.version, "exemplar_id": self.exemplar_id,
            "role": self.role, "width": self.width, "height": self.height, "pixels": self.pixels,
            "provenance_type": self.provenance_type, "provenance_description": self.provenance_description,
            "ownership": self.ownership, "approved_by": self.approved_by, "production_difficulty": self.production_difficulty,
        }
        return hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


class ExemplarRegistry:
    """Immutable ordered registry; it never reads paths or performs network lookup."""

    __slots__ = ("_exemplars", "_by_id")

    def __init__(self, exemplars: tuple[Exemplar, ...] | list[Exemplar] = ()) -> None:
        if any(not isinstance(exemplar, Exemplar) for exemplar in exemplars):
            raise WFCContractError("registry entries must be Exemplar values")
        ordered = tuple(sorted(exemplars, key=lambda exemplar: exemplar.exemplar_id))
        if len({exemplar.exemplar_id for exemplar in ordered}) != len(ordered):
            raise WFCContractError("exemplar IDs must be unique")
        object.__setattr__(self, "_exemplars", ordered)
        object.__setattr__(self, "_by_id", MappingProxyType({exemplar.exemplar_id: exemplar for exemplar in ordered}))

    def __setattr__(self, _name: str, _value: object) -> None:
        raise AttributeError("exemplar registry is immutable")

    @property
    def exemplars(self) -> tuple[Exemplar, ...]:
        return self._exemplars

    def get(self, exemplar_id: str) -> Exemplar:
        try:
            return self._by_id[exemplar_id]
        except (KeyError, TypeError) as exc:
            raise WFCContractError("unknown WFC exemplar") from exc

    def eligible(self) -> tuple[Exemplar, ...]:
        return tuple(exemplar for exemplar in self._exemplars if exemplar.ownership in {"SYNTHETIC_TEST_ONLY", "OWNER_APPROVED"})


@dataclass(frozen=True, slots=True)
class WFCConfig:
    pattern_size: int = 2
    input_periodic: bool = False
    output_periodic: bool = False
    allow_rotations: bool = False
    allow_reflections: bool = False
    experimental_n4: bool = False
    max_attempts: int = 4
    palette_mapping: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.pattern_size not in {2, 3, 4} or isinstance(self.pattern_size, bool):
            raise WFCContractError("WFC pattern_size must be N=2, N=3, or experimental N=4")
        if self.pattern_size == 4 and self.experimental_n4 is not True:
            raise WFCContractError("N=4 requires experimental_n4=true")
        if self.pattern_size != 4 and self.experimental_n4:
            raise WFCContractError("experimental_n4 is only valid with pattern_size=4")
        for label, value in (("input_periodic", self.input_periodic), ("output_periodic", self.output_periodic), ("allow_rotations", self.allow_rotations), ("allow_reflections", self.allow_reflections), ("experimental_n4", self.experimental_n4)):
            if type(value) is not bool:
                raise WFCContractError(f"{label} must be boolean")
        if isinstance(self.max_attempts, bool) or not isinstance(self.max_attempts, int) or not 1 <= self.max_attempts <= 8:
            raise WFCContractError("WFC max_attempts must be bounded to 1..8")
        try:
            mapping = tuple(tuple(pair) for pair in self.palette_mapping)
        except (TypeError, ValueError) as exc:
            raise WFCContractError("palette_mapping must contain source/target string pairs") from exc
        if any(len(pair) != 2 or any(type(value) is not str for value in pair) for pair in mapping):
            raise WFCContractError("palette_mapping must contain source/target string pairs")
        if len({pair[0] for pair in mapping}) != len(mapping) or len({pair[1] for pair in mapping}) != len(mapping):
            raise WFCContractError("palette_mapping must be one-to-one")
        mapping = tuple(sorted(mapping, key=lambda pair: int(pair[0][1:]) if pair[0].startswith("C") and pair[0][1:].isdigit() else pair[0]))
        object.__setattr__(self, "palette_mapping", mapping)


@dataclass(frozen=True, slots=True)
class Pattern:
    pattern_id: int
    cells: tuple[str, ...]
    frequency: int


@dataclass(frozen=True, slots=True)
class PatternTable:
    pattern_size: int
    patterns: tuple[Pattern, ...]
    adjacency: Mapping[str, tuple[tuple[int, ...], ...]]
    source_palette: tuple[str, ...]
    target_palette: tuple[str, ...]
    digest: str
    raw_extracted_window_count: int = 0
    transformed_observation_count: int = 0

    def __post_init__(self) -> None:
        if not self.patterns:
            raise WFCContractError("WFC pattern table cannot be empty")
        for label, value in (("raw_extracted_window_count", self.raw_extracted_window_count), ("transformed_observation_count", self.transformed_observation_count)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise WFCContractError(f"{label} must be a non-negative integer")
        if self.transformed_observation_count and self.transformed_observation_count < self.raw_extracted_window_count:
            raise WFCContractError("transformed observations cannot be fewer than raw windows")
        object.__setattr__(self, "adjacency", MappingProxyType(dict(self.adjacency)))


@dataclass(frozen=True, slots=True)
class WFCAttemptRecord:
    """Immutable stable diagnostic for one bounded WFC attempt."""

    attempt: int
    code: str
    placement: tuple[int, int]
    detail: str

    def __post_init__(self) -> None:
        if isinstance(self.attempt, bool) or not isinstance(self.attempt, int) or self.attempt < 0:
            raise WFCContractError("WFC attempt diagnostic index must be non-negative")
        _require_text(self.code, "WFC attempt diagnostic code")
        if len(self.placement) != 2 or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in self.placement):
            raise WFCContractError("WFC attempt diagnostic placement must be a non-negative pair")
        _require_text(self.detail, "WFC attempt diagnostic detail")

    def as_dict(self) -> dict[str, object]:
        return {"attempt": self.attempt, "code": self.code, "placement": list(self.placement), "detail": self.detail}

    def compact(self) -> str:
        return f"{self.attempt}:{self.code}@{self.placement[0]},{self.placement[1]}"


@dataclass(frozen=True, slots=True)
class WFCCandidate:
    result: object
    exemplar: Exemplar
    config: WFCConfig
    logical_grid: tuple[str, ...]
    metadata: Mapping[str, object]
    pattern_table: PatternTable
    attempt: int
    attempt_history: tuple[WFCAttemptRecord, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        object.__setattr__(self, "attempt_history", tuple(self.attempt_history))

    @property
    def wfc_metadata(self) -> Mapping[str, object]:
        return self.metadata
