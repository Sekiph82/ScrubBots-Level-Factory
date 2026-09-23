"""Closed, provenance-bound LevelMetrics V1 data contract.

This module records accepted M03 identities and reserves typed M04 metric
slots.  It deliberately does not run gameplay or calculate any metric.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re

from .compact_solver_state import (
    CANONICAL_PROOF_STATE_AUTHORITY_SHA,
    LevelIdentity,
    SolverStateAuthority,
)
from .contracts.difficulty import Difficulty, parse_difficulty
from .contracts.production import (
    PRODUCTION_COLOR_MAX,
    PRODUCTION_COLOR_MIN,
    PRODUCTION_DIMENSION_MAX,
    PRODUCTION_DIMENSION_MIN,
)
from .solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION


LEVEL_METRICS_SCHEMA = "scrubbots-level-metrics"
LEVEL_METRICS_VERSION = 1
METRICS_CONTRACT_SCHEMA = "scrubbots-level-metrics-contract"
METRICS_CONTRACT_VERSION = 1
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class LevelMetricsError(ValueError):
    """Raised when a LevelMetrics envelope or nested value is malformed."""


class AnalysisDisposition(str, Enum):
    AVAILABLE = "AVAILABLE"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class MetricId(str, Enum):
    """Closed catalog of metric slots planned for M04."""

    SOLUTION_DEPTH = "solution_depth"
    MOVE_COUNT = "move_count"
    STATES_VISITED = "states_visited"
    DEAD_ENDS = "dead_ends"
    BRANCHING = "branching"
    FORCED_MOVES = "forced_moves"
    DEPENDENCY_DEPTH = "dependency_depth"
    SLOT_PRESSURE = "slot_pressure"
    BAIT_DEADLOCK = "bait_deadlock"
    VOLATILITY = "volatility"
    SOLUTION_COUNT = "solution_count"
    SOLUTION_ENTROPY = "solution_entropy"
    CHALLENGE_SCORE_REFERENCE = "challenge_score_reference"


_INTEGER_METRICS = frozenset(
    {
        MetricId.SOLUTION_DEPTH.value,
        MetricId.MOVE_COUNT.value,
        MetricId.STATES_VISITED.value,
        MetricId.DEAD_ENDS.value,
        MetricId.FORCED_MOVES.value,
        MetricId.DEPENDENCY_DEPTH.value,
        MetricId.SOLUTION_COUNT.value,
    }
)
_FLOAT_METRICS = frozenset(
    {
        MetricId.BRANCHING.value,
        MetricId.SLOT_PRESSURE.value,
        MetricId.BAIT_DEADLOCK.value,
        MetricId.VOLATILITY.value,
        MetricId.SOLUTION_ENTROPY.value,
    }
)


def _canonical_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _closed_mapping(value: object, fields: frozenset[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise LevelMetricsError(f"{label} must be an object")
    if set(value) - fields:
        raise LevelMetricsError(f"{label} contains unknown fields")
    return dict(value)


def _required_mapping(value: object, fields: frozenset[str], label: str) -> Mapping[str, object]:
    mapping = _closed_mapping(value, fields, label)
    if set(mapping) != fields:
        raise LevelMetricsError(f"{label} has unknown or missing fields")
    return mapping


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise LevelMetricsError(f"{label} must be a non-empty string")
    return value.strip()


def _exact_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise LevelMetricsError(f"{label} must be an integer")
    return value


def _non_negative_int(value: object, label: str) -> int:
    result = _exact_int(value, label)
    if result < 0:
        raise LevelMetricsError(f"{label} must be non-negative")
    return result


def _finite_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LevelMetricsError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise LevelMetricsError(f"{label} must be a finite non-negative number")
    return result


@dataclass(frozen=True, slots=True)
class SolverEvidenceIdentity:
    """Exact accepted solver evidence identity, without copying evidence."""

    schema: str
    version: int
    digest: str

    def __post_init__(self) -> None:
        schema = _text(self.schema, "solver evidence schema")
        version = _exact_int(self.version, "solver evidence version")
        digest = _text(self.digest, "solver evidence digest")
        if schema != SOLVER_EVIDENCE_SCHEMA or version != SOLVER_EVIDENCE_VERSION:
            raise LevelMetricsError("unsupported solver evidence schema/version")
        if _SHA256_PATTERN.fullmatch(digest) is None:
            raise LevelMetricsError("solver evidence digest must be a lowercase SHA-256")
        object.__setattr__(self, "schema", schema)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "digest", digest)

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "digest": self.digest}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "SolverEvidenceIdentity":
        value = _required_mapping(payload, frozenset({"schema", "version", "digest"}), "solver evidence identity")
        return cls(value["schema"], value["version"], value["digest"])


@dataclass(frozen=True, slots=True)
class MetricsContractIdentity:
    """Versioned identity for the metric-slot catalog itself."""

    schema: str = METRICS_CONTRACT_SCHEMA
    version: int = METRICS_CONTRACT_VERSION

    def __post_init__(self) -> None:
        schema = _text(self.schema, "metrics contract schema")
        version = _exact_int(self.version, "metrics contract version")
        if schema != METRICS_CONTRACT_SCHEMA or version != METRICS_CONTRACT_VERSION:
            raise LevelMetricsError("unsupported metrics contract schema/version")
        object.__setattr__(self, "schema", schema)
        object.__setattr__(self, "version", version)

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "MetricsContractIdentity":
        value = _required_mapping(payload, frozenset({"schema", "version"}), "metrics contract identity")
        return cls(value["schema"], value["version"])


@dataclass(frozen=True, slots=True)
class MetricValues:
    """Typed optional M04 slots; no arbitrary metric bag is permitted."""

    solution_depth: int | None = None
    move_count: int | None = None
    states_visited: int | None = None
    dead_ends: int | None = None
    branching: float | None = None
    forced_moves: int | None = None
    dependency_depth: int | None = None
    slot_pressure: float | None = None
    bait_deadlock: float | None = None
    volatility: float | None = None
    solution_count: int | None = None
    solution_entropy: float | None = None
    challenge_score_reference: str | None = None

    def __post_init__(self) -> None:
        for name in _INTEGER_METRICS:
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, _non_negative_int(value, f"metric {name}"))
        for name in _FLOAT_METRICS:
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, _finite_number(value, f"metric {name}"))
        reference = self.challenge_score_reference
        if reference is not None:
            object.__setattr__(self, "challenge_score_reference", _text(reference, "challenge score reference"))

    def canonical_dict(self) -> dict[str, object]:
        return {
            name: value
            for name, value in (
                (metric.value, getattr(self, metric.value)) for metric in MetricId
            )
            if value is not None
        }

    def is_empty(self) -> bool:
        return not self.canonical_dict()

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "MetricValues":
        value = _closed_mapping(payload, frozenset(metric.value for metric in MetricId), "metrics")
        return cls(**value)


@dataclass(frozen=True, slots=True)
class DifficultyMetadata:
    """Descriptive lineage only; never used to infer or calculate metrics."""

    difficulty: Difficulty | str
    width: int | None = None
    height: int | None = None
    used_color_count: int | None = None

    def __post_init__(self) -> None:
        difficulty = parse_difficulty(self.difficulty)
        object.__setattr__(self, "difficulty", difficulty)
        for name in ("width", "height"):
            value = getattr(self, name)
            if value is not None:
                value = _exact_int(value, f"difficulty metadata {name}")
                if not PRODUCTION_DIMENSION_MIN <= value <= PRODUCTION_DIMENSION_MAX:
                    raise LevelMetricsError(f"difficulty metadata {name} must be in {PRODUCTION_DIMENSION_MIN}..{PRODUCTION_DIMENSION_MAX}")
                object.__setattr__(self, name, value)
        if self.used_color_count is not None:
            colors = _exact_int(self.used_color_count, "difficulty metadata used_color_count")
            if not PRODUCTION_COLOR_MIN <= colors <= PRODUCTION_COLOR_MAX:
                raise LevelMetricsError(f"difficulty metadata used_color_count must be in {PRODUCTION_COLOR_MIN}..{PRODUCTION_COLOR_MAX}")
            object.__setattr__(self, "used_color_count", colors)

    def canonical_dict(self) -> dict[str, object]:
        return {
            name: value.value if isinstance(value, Enum) else value
            for name, value in (
                ("difficulty", self.difficulty),
                ("width", self.width),
                ("height", self.height),
                ("used_color_count", self.used_color_count),
            )
            if value is not None
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "DifficultyMetadata":
        value = _closed_mapping(payload, frozenset({"difficulty", "width", "height", "used_color_count"}), "difficulty metadata")
        return cls(
            difficulty=value["difficulty"],
            width=value.get("width"),
            height=value.get("height"),
            used_color_count=value.get("used_color_count"),
        )


@dataclass(frozen=True, slots=True)
class LevelMetrics:
    """Immutable Factory-side LevelMetrics V1 envelope."""

    level: LevelIdentity
    authority: SolverStateAuthority
    solver_evidence: SolverEvidenceIdentity
    disposition: AnalysisDisposition
    metrics: MetricValues | None = None
    metrics_contract: MetricsContractIdentity = MetricsContractIdentity()
    difficulty_metadata: DifficultyMetadata | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.level, LevelIdentity):
            raise LevelMetricsError("LevelMetrics level identity is malformed")
        if not isinstance(self.authority, SolverStateAuthority):
            raise LevelMetricsError("LevelMetrics gameplay authority is malformed")
        if self.authority.commit_sha != CANONICAL_PROOF_STATE_AUTHORITY_SHA:
            raise LevelMetricsError("LevelMetrics gameplay authority is not the accepted canonical M03 authority")
        if not isinstance(self.solver_evidence, SolverEvidenceIdentity):
            raise LevelMetricsError("LevelMetrics solver evidence identity is malformed")
        if not isinstance(self.disposition, AnalysisDisposition):
            raise LevelMetricsError("LevelMetrics disposition is malformed")
        if not isinstance(self.metrics_contract, MetricsContractIdentity):
            raise LevelMetricsError("LevelMetrics metrics contract identity is malformed")
        if self.metrics is not None and not isinstance(self.metrics, MetricValues):
            raise LevelMetricsError("LevelMetrics metrics are malformed")
        if self.difficulty_metadata is not None and not isinstance(self.difficulty_metadata, DifficultyMetadata):
            raise LevelMetricsError("LevelMetrics difficulty metadata is malformed")
        if self.disposition is not AnalysisDisposition.AVAILABLE and self.metrics is not None:
            raise LevelMetricsError("only AVAILABLE LevelMetrics may carry measurements")
        if self.reason is not None:
            object.__setattr__(self, "reason", _text(self.reason, "LevelMetrics reason"))
        if self.disposition is not AnalysisDisposition.AVAILABLE and self.reason is None:
            raise LevelMetricsError("non-AVAILABLE LevelMetrics requires a reason")

    @property
    def source_sha256(self) -> str:
        return self.level.source_sha256

    @property
    def evidence_digest(self) -> str:
        return self.solver_evidence.digest

    def measurement_content(self) -> dict[str, object]:
        """Return measurement-only content, independent of descriptive metadata."""

        return dict(self.metrics.canonical_dict()) if self.metrics is not None else {}

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": LEVEL_METRICS_SCHEMA,
            "version": LEVEL_METRICS_VERSION,
            "level": self.level.canonical_dict(),
            "authority": self.authority.canonical_dict(),
            "solver_evidence": self.solver_evidence.canonical_dict(),
            "metrics_contract": self.metrics_contract.canonical_dict(),
            "disposition": self.disposition.value,
            "metrics": self.metrics.canonical_dict() if self.metrics is not None else None,
            "difficulty_metadata": self.difficulty_metadata.canonical_dict() if self.difficulty_metadata is not None else None,
            "reason": self.reason,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LevelMetrics":
        fields = frozenset(
            {
                "schema",
                "version",
                "level",
                "authority",
                "solver_evidence",
                "metrics_contract",
                "disposition",
                "metrics",
                "difficulty_metadata",
                "reason",
            }
        )
        value = _required_mapping(payload, fields, "LevelMetrics")
        if value["schema"] != LEVEL_METRICS_SCHEMA or type(value["version"]) is not int or value["version"] != LEVEL_METRICS_VERSION:
            raise LevelMetricsError("LevelMetrics schema/version is unsupported")

        level_data = _required_mapping(value["level"], frozenset({"source_sha256", "level_id", "width", "height", "cell_count"}), "LevelData identity")
        authority_data = _required_mapping(value["authority"], frozenset({"schema", "version", "repository", "commit_sha", "proof_state_source_path"}), "gameplay authority")
        authority_schema = _text(authority_data["schema"], "gameplay authority schema")
        if authority_schema != "scrubbots-proof-state-authority":
            raise LevelMetricsError("gameplay authority schema is unsupported")
        evidence_data = _required_mapping(value["solver_evidence"], frozenset({"schema", "version", "digest"}), "solver evidence identity")
        metrics_contract = MetricsContractIdentity.from_dict(value["metrics_contract"])
        try:
            disposition = AnalysisDisposition(value["disposition"])
        except (TypeError, ValueError) as exc:
            raise LevelMetricsError("LevelMetrics disposition is unsupported") from exc
        metrics_value = value["metrics"]
        if metrics_value is not None and not isinstance(metrics_value, Mapping):
            raise LevelMetricsError("metrics must be an object or null")
        metadata_value = value["difficulty_metadata"]
        if metadata_value is not None and not isinstance(metadata_value, Mapping):
            raise LevelMetricsError("difficulty_metadata must be an object or null")
        return cls(
            level=LevelIdentity(**level_data),
            authority=SolverStateAuthority(
                repository=authority_data["repository"],
                commit_sha=authority_data["commit_sha"],
                proof_state_source_path=authority_data["proof_state_source_path"],
                authority_version=authority_data["version"],
            ),
            solver_evidence=SolverEvidenceIdentity.from_dict(evidence_data),
            disposition=disposition,
            metrics=MetricValues.from_dict(metrics_value) if metrics_value is not None else None,
            metrics_contract=metrics_contract,
            difficulty_metadata=DifficultyMetadata.from_dict(metadata_value) if metadata_value is not None else None,
            reason=value["reason"],
        )


__all__ = [
    "AnalysisDisposition",
    "DifficultyMetadata",
    "LEVEL_METRICS_SCHEMA",
    "LEVEL_METRICS_VERSION",
    "LevelMetrics",
    "LevelMetricsError",
    "MetricId",
    "MetricValues",
    "METRICS_CONTRACT_SCHEMA",
    "METRICS_CONTRACT_VERSION",
    "MetricsContractIdentity",
    "SolverEvidenceIdentity",
]
