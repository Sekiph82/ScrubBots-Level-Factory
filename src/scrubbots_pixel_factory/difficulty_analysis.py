"""Deterministic, provenance-bound M04 difficulty analysis contracts."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import hashlib
import json
import math
import re
from collections.abc import Mapping

from .baseline_search import SearchExecutionDisposition, SearchVerdict
from .level_metrics import AnalysisDisposition, LevelMetrics, LevelMetricsError, MetricId, MetricValues, SolverEvidenceIdentity
from .contracts.difficulty import Difficulty, parse_difficulty
from .solver_evidence import SolverEvidenceReport


DEPENDENCY_DEPTH_SCHEMA = "scrubbots-canonical-dependency-depth"
DEPENDENCY_DEPTH_VERSION = 1
SLOT_PRESSURE_SCHEMA = "scrubbots-canonical-slot-pressure"
SLOT_PRESSURE_VERSION = 1
BAIT_DEADLOCK_SCHEMA = "scrubbots-canonical-bait-deadlock"
BAIT_DEADLOCK_VERSION = 1
VOLATILITY_SCHEMA = "scrubbots-canonical-state-volatility"
VOLATILITY_VERSION = 1
CHALLENGE_SCORE_SCHEMA = "scrubbots-difficulty-challenge-score"
CHALLENGE_SCORE_VERSION = 1
CHALLENGE_SCORE_POLICY_VERSION = "DIFFICULTY_V1"
LANE_MAPPING_SCHEMA = "scrubbots-score-lane-mapping"
LANE_MAPPING_VERSION = 1
LANE_MAPPING_POLICY_VERSION = "SCORE_LANE_V1"
ANALYSIS_SCHEMA = "scrubbots-difficulty-analysis"
ANALYSIS_VERSION = 1
PROVIDER_IDENTITY_SCHEMA = "scrubbots-metric-provider"
PROVIDER_IDENTITY_VERSION = 1
CALIBRATION_SCHEMA = "scrubbots-future-calibration"
CALIBRATION_VERSION = 1
CALIBRATION_POLICY_STATE = "DISABLED_UNTIL_POLICY_APPROVED"
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _canonical_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: Mapping[str, object]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _digest_text(value: object, label: str) -> str:
    if type(value) is not str or _SHA256_PATTERN.fullmatch(value) is None:
        raise LevelMetricsError(f"{label} must be a lowercase SHA-256")
    return value


def _provider_text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise LevelMetricsError(f"{label} must be a non-empty string")
    return value.strip()


class _DependencyResultMixin:
    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class DependencyDepthResult(_DependencyResultMixin):
    """A provider-owned dependency measurement, never a gameplay heuristic."""

    disposition: AnalysisDisposition
    authority: object
    level_source_sha256: str
    state_digest: str
    evidence_digest: str
    provider_id: str
    provider_version: str
    dependency_depth: int | None
    reason: str

    def __post_init__(self) -> None:
        from .compact_solver_state import SolverStateAuthority

        if not isinstance(self.disposition, AnalysisDisposition):
            raise LevelMetricsError("dependency result disposition is malformed")
        if not isinstance(self.authority, SolverStateAuthority):
            raise LevelMetricsError("dependency result authority is malformed")
        _digest_text(self.level_source_sha256, "dependency level source SHA-256")
        _digest_text(self.state_digest, "dependency state digest")
        _digest_text(self.evidence_digest, "dependency evidence digest")
        _provider_text(self.provider_id, "dependency provider id")
        _provider_text(self.provider_version, "dependency provider version")
        if type(self.reason) is not str or not self.reason.strip():
            raise LevelMetricsError("dependency result reason is required")
        if self.disposition is AnalysisDisposition.AVAILABLE:
            if type(self.dependency_depth) is not int or self.dependency_depth < 0:
                raise LevelMetricsError("AVAILABLE dependency result requires a non-negative depth")
        elif self.dependency_depth is not None:
            raise LevelMetricsError("unavailable dependency result cannot carry a measurement")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": DEPENDENCY_DEPTH_SCHEMA,
            "version": DEPENDENCY_DEPTH_VERSION,
            "disposition": self.disposition.value,
            "authority": self.authority.canonical_dict(),
            "level_source_sha256": self.level_source_sha256,
            "state_digest": self.state_digest,
            "evidence_digest": self.evidence_digest,
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "dependency_depth": self.dependency_depth,
            "reason": self.reason,
        }


def unavailable_dependency_result(level_metrics: LevelMetrics, state_digest: str, reason: str) -> DependencyDepthResult:
    """Create the production-safe result used when canonical semantics are absent."""

    if not isinstance(level_metrics, LevelMetrics):
        raise LevelMetricsError("LevelMetrics is required")
    return DependencyDepthResult(
        AnalysisDisposition.UNAVAILABLE,
        level_metrics.authority,
        level_metrics.source_sha256,
        _digest_text(state_digest, "dependency state digest"),
        level_metrics.evidence_digest,
        "canonical-dependency-semantics",
        "CANONICAL_DEPENDENCY_SEMANTICS_V1",
        None,
        reason,
    )


def populate_dependency_depth(level_metrics: LevelMetrics, result: DependencyDepthResult) -> LevelMetrics:
    """Apply an explicitly bound provider result; unavailable remains absent."""

    if not isinstance(level_metrics, LevelMetrics) or not isinstance(result, DependencyDepthResult):
        raise LevelMetricsError("LevelMetrics and DependencyDepthResult are required")
    if result.authority != level_metrics.authority or result.level_source_sha256 != level_metrics.source_sha256 or result.evidence_digest != level_metrics.evidence_digest:
        raise LevelMetricsError("dependency result provenance does not match LevelMetrics")
    if result.disposition is not AnalysisDisposition.AVAILABLE:
        return level_metrics
    return replace(level_metrics, metrics=replace(level_metrics.metrics or MetricValues(), dependency_depth=result.dependency_depth))


@dataclass(frozen=True, slots=True)
class SlotSnapshot:
    occupied_slots: int
    capacity: int

    def __post_init__(self) -> None:
        if type(self.occupied_slots) is not int or type(self.capacity) is not int or self.capacity <= 0 or not 0 <= self.occupied_slots <= self.capacity:
            raise LevelMetricsError("slot snapshot occupancy must be within a positive canonical capacity")

    def ratio(self) -> float:
        return self.occupied_slots / self.capacity

    def canonical_dict(self) -> dict[str, int]:
        return {"occupied_slots": self.occupied_slots, "capacity": self.capacity}


@dataclass(frozen=True, slots=True)
class SlotPressureResult(_DependencyResultMixin):
    disposition: AnalysisDisposition
    authority: object
    level_source_sha256: str
    state_digest: str
    evidence_digest: str
    provider_id: str
    provider_version: str
    snapshots: tuple[SlotSnapshot, ...]
    slot_pressure: float | None
    reason: str

    def __post_init__(self) -> None:
        from .compact_solver_state import SolverStateAuthority

        if not isinstance(self.disposition, AnalysisDisposition) or not isinstance(self.authority, SolverStateAuthority):
            raise LevelMetricsError("slot pressure disposition or authority is malformed")
        _digest_text(self.level_source_sha256, "slot pressure level source SHA-256")
        _digest_text(self.state_digest, "slot pressure state digest")
        _digest_text(self.evidence_digest, "slot pressure evidence digest")
        _provider_text(self.provider_id, "slot pressure provider id")
        _provider_text(self.provider_version, "slot pressure provider version")
        if type(self.snapshots) is not tuple or any(not isinstance(snapshot, SlotSnapshot) for snapshot in self.snapshots):
            raise LevelMetricsError("slot pressure snapshots must be an immutable canonical trace")
        if type(self.reason) is not str or not self.reason.strip():
            raise LevelMetricsError("slot pressure reason is required")
        if self.disposition is AnalysisDisposition.AVAILABLE:
            if not self.snapshots or self.slot_pressure is None or not 0.0 <= self.slot_pressure <= 1.0:
                raise LevelMetricsError("AVAILABLE slot pressure requires non-empty bounded snapshots and a ratio")
        elif self.slot_pressure is not None:
            raise LevelMetricsError("unavailable slot pressure cannot carry a measurement")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": SLOT_PRESSURE_SCHEMA,
            "version": SLOT_PRESSURE_VERSION,
            "disposition": self.disposition.value,
            "authority": self.authority.canonical_dict(),
            "level_source_sha256": self.level_source_sha256,
            "state_digest": self.state_digest,
            "evidence_digest": self.evidence_digest,
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "snapshots": [snapshot.canonical_dict() for snapshot in self.snapshots],
            "slot_pressure": self.slot_pressure,
            "reason": self.reason,
        }


def slot_pressure_from_snapshots(
    level_metrics: LevelMetrics,
    state_digest: str,
    snapshots: tuple[SlotSnapshot, ...],
    *,
    provider_id: str = "canonical-slot-trace",
    provider_version: str = "CANONICAL_SLOT_TRACE_V1",
) -> SlotPressureResult:
    if not isinstance(snapshots, tuple) or not snapshots:
        raise LevelMetricsError("slot pressure requires a non-empty canonical trace")
    if any(not isinstance(snapshot, SlotSnapshot) for snapshot in snapshots):
        raise LevelMetricsError("slot pressure trace contains a malformed snapshot")
    pressure = max(snapshot.ratio() for snapshot in snapshots)
    return SlotPressureResult(AnalysisDisposition.AVAILABLE, level_metrics.authority, level_metrics.source_sha256, _digest_text(state_digest, "slot pressure state digest"), level_metrics.evidence_digest, provider_id, provider_version, snapshots, pressure, "canonical slot-state trace accepted")


def unavailable_slot_pressure_result(level_metrics: LevelMetrics, state_digest: str, reason: str) -> SlotPressureResult:
    if not isinstance(level_metrics, LevelMetrics):
        raise LevelMetricsError("LevelMetrics is required")
    return SlotPressureResult(AnalysisDisposition.UNAVAILABLE, level_metrics.authority, level_metrics.source_sha256, _digest_text(state_digest, "slot pressure state digest"), level_metrics.evidence_digest, "canonical-slot-trace", "CANONICAL_SLOT_TRACE_V1", (), None, reason)


def populate_slot_pressure(level_metrics: LevelMetrics, result: SlotPressureResult) -> LevelMetrics:
    if not isinstance(level_metrics, LevelMetrics) or not isinstance(result, SlotPressureResult):
        raise LevelMetricsError("LevelMetrics and SlotPressureResult are required")
    if result.authority != level_metrics.authority or result.level_source_sha256 != level_metrics.source_sha256 or result.evidence_digest != level_metrics.evidence_digest:
        raise LevelMetricsError("slot pressure result provenance does not match LevelMetrics")
    if result.disposition is not AnalysisDisposition.AVAILABLE:
        return level_metrics
    return replace(level_metrics, metrics=replace(level_metrics.metrics or MetricValues(), slot_pressure=result.slot_pressure))


@dataclass(frozen=True, slots=True)
class BaitDeadlockResult(_DependencyResultMixin):
    disposition: AnalysisDisposition
    authority: object
    level_source_sha256: str
    state_digest: str
    evidence_digest: str
    provider_id: str
    provider_version: str
    legal_move_count: int
    proven_deadlock_move_count: int
    bait_deadlock: float | None
    exact: bool
    reason: str

    def __post_init__(self) -> None:
        from .compact_solver_state import SolverStateAuthority

        if not isinstance(self.disposition, AnalysisDisposition) or not isinstance(self.authority, SolverStateAuthority):
            raise LevelMetricsError("bait/deadlock disposition or authority is malformed")
        _digest_text(self.level_source_sha256, "bait/deadlock level source SHA-256")
        _digest_text(self.state_digest, "bait/deadlock state digest")
        _digest_text(self.evidence_digest, "bait/deadlock evidence digest")
        _provider_text(self.provider_id, "bait/deadlock provider id")
        _provider_text(self.provider_version, "bait/deadlock provider version")
        if type(self.legal_move_count) is not int or self.legal_move_count < 0 or type(self.proven_deadlock_move_count) is not int or not 0 <= self.proven_deadlock_move_count <= self.legal_move_count:
            raise LevelMetricsError("bait/deadlock counts are malformed")
        if type(self.exact) is not bool or type(self.reason) is not str or not self.reason.strip():
            raise LevelMetricsError("bait/deadlock exactness or reason is malformed")
        if self.disposition is AnalysisDisposition.AVAILABLE:
            if not self.exact or self.bait_deadlock is None or not 0.0 <= self.bait_deadlock <= 1.0:
                raise LevelMetricsError("AVAILABLE bait/deadlock requires an exact bounded ratio")
        elif self.bait_deadlock is not None or self.exact:
            raise LevelMetricsError("non-AVAILABLE bait/deadlock cannot claim an exact ratio")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": BAIT_DEADLOCK_SCHEMA,
            "version": BAIT_DEADLOCK_VERSION,
            "disposition": self.disposition.value,
            "authority": self.authority.canonical_dict(),
            "level_source_sha256": self.level_source_sha256,
            "state_digest": self.state_digest,
            "evidence_digest": self.evidence_digest,
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "legal_move_count": self.legal_move_count,
            "proven_deadlock_move_count": self.proven_deadlock_move_count,
            "bait_deadlock": self.bait_deadlock,
            "exact": self.exact,
            "reason": self.reason,
        }


def bait_deadlock_from_children(
    level_metrics: LevelMetrics,
    state_digest: str,
    child_dispositions: tuple[object, ...],
    *,
    provider_id: str = "canonical-counterfactual",
    provider_version: str = "CANONICAL_COUNTERFACTUAL_V1",
) -> BaitDeadlockResult:
    from .solver_budget import SolverOutcomeDisposition

    if not isinstance(child_dispositions, tuple):
        raise LevelMetricsError("counterfactual child classifications must be immutable")
    if any(not isinstance(item, SolverOutcomeDisposition) for item in child_dispositions):
        raise LevelMetricsError("counterfactual child classification is malformed")
    if any(item in {SolverOutcomeDisposition.UNAVAILABLE, SolverOutcomeDisposition.ERROR} for item in child_dispositions):
        disposition = AnalysisDisposition.UNAVAILABLE if SolverOutcomeDisposition.UNAVAILABLE in child_dispositions else AnalysisDisposition.ERROR
        return BaitDeadlockResult(disposition, level_metrics.authority, level_metrics.source_sha256, _digest_text(state_digest, "bait/deadlock state digest"), level_metrics.evidence_digest, provider_id, provider_version, len(child_dispositions), 0, None, False, "canonical counterfactual child classification is unavailable")
    proven = sum(item is SolverOutcomeDisposition.PROVEN_UNSOLVABLE for item in child_dispositions)
    if any(item is SolverOutcomeDisposition.INCONCLUSIVE for item in child_dispositions):
        return BaitDeadlockResult(AnalysisDisposition.INCONCLUSIVE, level_metrics.authority, level_metrics.source_sha256, _digest_text(state_digest, "bait/deadlock state digest"), level_metrics.evidence_digest, provider_id, provider_version, len(child_dispositions), proven, None, False, "inconclusive child prevents an exact bait/deadlock ratio")
    legal = len(child_dispositions)
    ratio = proven / legal if legal else 0.0
    return BaitDeadlockResult(AnalysisDisposition.AVAILABLE, level_metrics.authority, level_metrics.source_sha256, _digest_text(state_digest, "bait/deadlock state digest"), level_metrics.evidence_digest, provider_id, provider_version, legal, proven, ratio, True, "all canonical counterfactual children classified exactly")


def populate_bait_deadlock(level_metrics: LevelMetrics, result: BaitDeadlockResult) -> LevelMetrics:
    if not isinstance(level_metrics, LevelMetrics) or not isinstance(result, BaitDeadlockResult):
        raise LevelMetricsError("LevelMetrics and BaitDeadlockResult are required")
    if result.authority != level_metrics.authority or result.level_source_sha256 != level_metrics.source_sha256 or result.evidence_digest != level_metrics.evidence_digest:
        raise LevelMetricsError("bait/deadlock result provenance does not match LevelMetrics")
    if result.disposition is not AnalysisDisposition.AVAILABLE:
        return level_metrics
    return replace(level_metrics, metrics=replace(level_metrics.metrics or MetricValues(), bait_deadlock=result.bait_deadlock))


@dataclass(frozen=True, slots=True)
class VolatilitySnapshot:
    remaining_active_cells: int
    active_capacity: int
    supply_remaining: int
    supply_capacity: int
    occupied_slots: int
    slot_capacity: int

    def __post_init__(self) -> None:
        values = (self.remaining_active_cells, self.active_capacity, self.supply_remaining, self.supply_capacity, self.occupied_slots, self.slot_capacity)
        if any(type(value) is not int for value in values) or self.active_capacity <= 0 or self.supply_capacity <= 0 or self.slot_capacity <= 0:
            raise LevelMetricsError("volatility snapshot capacities and counts must be exact integers")
        if not 0 <= self.remaining_active_cells <= self.active_capacity or not 0 <= self.supply_remaining <= self.supply_capacity or not 0 <= self.occupied_slots <= self.slot_capacity:
            raise LevelMetricsError("volatility snapshot values exceed canonical capacities")

    def normalized_signature(self) -> tuple[float, float, float]:
        return (self.remaining_active_cells / self.active_capacity, self.supply_remaining / self.supply_capacity, self.occupied_slots / self.slot_capacity)

    def canonical_dict(self) -> dict[str, int]:
        return {"remaining_active_cells": self.remaining_active_cells, "active_capacity": self.active_capacity, "supply_remaining": self.supply_remaining, "supply_capacity": self.supply_capacity, "occupied_slots": self.occupied_slots, "slot_capacity": self.slot_capacity}


@dataclass(frozen=True, slots=True)
class VolatilityResult(_DependencyResultMixin):
    disposition: AnalysisDisposition
    authority: object
    level_source_sha256: str
    state_digest: str
    evidence_digest: str
    provider_id: str
    provider_version: str
    snapshots: tuple[VolatilitySnapshot, ...]
    volatility: float | None
    reason: str

    def __post_init__(self) -> None:
        from .compact_solver_state import SolverStateAuthority

        if not isinstance(self.disposition, AnalysisDisposition) or not isinstance(self.authority, SolverStateAuthority):
            raise LevelMetricsError("volatility disposition or authority is malformed")
        _digest_text(self.level_source_sha256, "volatility level source SHA-256")
        _digest_text(self.state_digest, "volatility state digest")
        _digest_text(self.evidence_digest, "volatility evidence digest")
        _provider_text(self.provider_id, "volatility provider id")
        _provider_text(self.provider_version, "volatility provider version")
        if type(self.snapshots) is not tuple or any(not isinstance(snapshot, VolatilitySnapshot) for snapshot in self.snapshots):
            raise LevelMetricsError("volatility snapshots must be an immutable canonical trace")
        if type(self.reason) is not str or not self.reason.strip():
            raise LevelMetricsError("volatility reason is required")
        if self.disposition is AnalysisDisposition.AVAILABLE:
            if len(self.snapshots) < 2 or self.volatility is None or not 0.0 <= self.volatility <= 1.0:
                raise LevelMetricsError("AVAILABLE volatility requires at least two bounded snapshots")
        elif self.volatility is not None:
            raise LevelMetricsError("unavailable volatility cannot carry a measurement")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": VOLATILITY_SCHEMA, "version": VOLATILITY_VERSION, "disposition": self.disposition.value, "authority": self.authority.canonical_dict(), "level_source_sha256": self.level_source_sha256, "state_digest": self.state_digest, "evidence_digest": self.evidence_digest, "provider_id": self.provider_id, "provider_version": self.provider_version, "snapshots": [snapshot.canonical_dict() for snapshot in self.snapshots], "volatility": self.volatility, "reason": self.reason}


def volatility_from_snapshots(level_metrics: LevelMetrics, state_digest: str, snapshots: tuple[VolatilitySnapshot, ...], *, provider_id: str = "canonical-state-trace", provider_version: str = "CANONICAL_STATE_TRACE_V1") -> VolatilityResult:
    if not isinstance(snapshots, tuple) or len(snapshots) < 2 or any(not isinstance(snapshot, VolatilitySnapshot) for snapshot in snapshots):
        raise LevelMetricsError("volatility requires at least two canonical trace snapshots")
    deltas = []
    for previous, current in zip(snapshots, snapshots[1:]):
        before = previous.normalized_signature()
        after = current.normalized_signature()
        deltas.append(sum(abs(a - b) for a, b in zip(before, after)) / 3.0)
    return VolatilityResult(AnalysisDisposition.AVAILABLE, level_metrics.authority, level_metrics.source_sha256, _digest_text(state_digest, "volatility state digest"), level_metrics.evidence_digest, provider_id, provider_version, snapshots, sum(deltas) / len(deltas), "canonical ordered state trace accepted")


def unavailable_volatility_result(level_metrics: LevelMetrics, state_digest: str, reason: str) -> VolatilityResult:
    return VolatilityResult(AnalysisDisposition.UNAVAILABLE, level_metrics.authority, level_metrics.source_sha256, _digest_text(state_digest, "volatility state digest"), level_metrics.evidence_digest, "canonical-state-trace", "CANONICAL_STATE_TRACE_V1", (), None, reason)


def populate_volatility(level_metrics: LevelMetrics, result: VolatilityResult) -> LevelMetrics:
    if not isinstance(level_metrics, LevelMetrics) or not isinstance(result, VolatilityResult):
        raise LevelMetricsError("LevelMetrics and VolatilityResult are required")
    if result.authority != level_metrics.authority or result.level_source_sha256 != level_metrics.source_sha256 or result.evidence_digest != level_metrics.evidence_digest:
        raise LevelMetricsError("volatility result provenance does not match LevelMetrics")
    if result.disposition is not AnalysisDisposition.AVAILABLE:
        return level_metrics
    return replace(level_metrics, metrics=replace(level_metrics.metrics or MetricValues(), volatility=result.volatility))


@dataclass(frozen=True, slots=True)
class ScoreComponent:
    normalized: float
    coefficient: float
    contribution: float

    def __post_init__(self) -> None:
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) for value in (self.normalized, self.coefficient, self.contribution)):
            raise LevelMetricsError("challenge score component contains a non-finite value")
        if not 0.0 <= float(self.normalized) <= 1.0 or float(self.coefficient) < 0.0:
            raise LevelMetricsError("challenge score component is outside its policy bounds")

    def canonical_dict(self) -> dict[str, float]:
        return {"normalized": float(self.normalized), "coefficient": float(self.coefficient), "contribution": float(self.contribution)}


@dataclass(frozen=True, slots=True)
class ChallengeScoreResult(_DependencyResultMixin):
    policy_version: str
    source_metrics_digest: str
    components: tuple[tuple[str, ScoreComponent], ...]
    score: float

    def __post_init__(self) -> None:
        if self.policy_version != CHALLENGE_SCORE_POLICY_VERSION:
            raise LevelMetricsError("unsupported challenge score policy version")
        _digest_text(self.source_metrics_digest, "challenge score source metrics digest")
        expected = ("move", "states", "dead_end", "branching", "forced")
        if tuple(name for name, _ in self.components) != expected:
            raise LevelMetricsError("challenge score components are not the closed V1 catalog")
        if not isinstance(self.score, (int, float)) or isinstance(self.score, bool) or not math.isfinite(float(self.score)) or not 0.0 <= self.score <= 100.0:
            raise LevelMetricsError("challenge score must be in [0, 100]")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": CHALLENGE_SCORE_SCHEMA, "version": CHALLENGE_SCORE_VERSION, "policy_version": self.policy_version, "source_metrics_digest": self.source_metrics_digest, "components": {name: component.canonical_dict() for name, component in self.components}, "score": float(self.score)}


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def calculate_challenge_score(level_metrics: LevelMetrics) -> ChallengeScoreResult:
    """Calculate the fixed engineering-policy Difficulty V1 score."""

    if not isinstance(level_metrics, LevelMetrics) or level_metrics.disposition is not AnalysisDisposition.AVAILABLE or level_metrics.metrics is None:
        raise LevelMetricsError("AVAILABLE LevelMetrics with core metrics is required for Challenge Score V1")
    metrics = level_metrics.metrics
    required = (metrics.move_count, metrics.states_visited, metrics.dead_ends, metrics.branching, metrics.forced_moves)
    if any(value is None for value in required):
        raise LevelMetricsError("Challenge Score V1 requires move_count, states_visited, dead_ends, branching, and forced_moves")
    move_count, states_visited, dead_ends, branching, forced_moves = required
    normalized = {
        "move": _clamp_unit(math.log1p(move_count) / math.log1p(64)),
        "states": _clamp_unit(math.log1p(states_visited) / math.log1p(10000)),
        "dead_end": _clamp_unit(dead_ends / max(states_visited, 1)),
        "branching": _clamp_unit(branching / 4.0),
        "forced": 1.0 - _clamp_unit(forced_moves / max(states_visited, 1)),
    }
    coefficients = {"move": 0.25, "states": 0.25, "dead_end": 0.15, "branching": 0.15, "forced": 0.20}
    components = tuple((name, ScoreComponent(normalized[name], coefficients[name], normalized[name] * coefficients[name])) for name in ("move", "states", "dead_end", "branching", "forced"))
    score = _clamp_unit(sum(component.contribution for _, component in components)) * 100.0
    return ChallengeScoreResult(CHALLENGE_SCORE_POLICY_VERSION, level_metrics.digest(), components, score)


class LaneClass(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    VERY_HARD = "VERY_HARD"


@dataclass(frozen=True, slots=True)
class LaneMappingResult(_DependencyResultMixin):
    score_digest: str
    score_policy_version: str
    mapping_policy_version: str
    score: float
    lane: LaneClass
    requested_class: LaneClass | None = None
    comparison: str | None = None

    def __post_init__(self) -> None:
        _digest_text(self.score_digest, "lane mapping score digest")
        if self.score_policy_version != CHALLENGE_SCORE_POLICY_VERSION or self.mapping_policy_version != LANE_MAPPING_POLICY_VERSION:
            raise LevelMetricsError("unsupported lane mapping policy identity")
        if not isinstance(self.score, (int, float)) or isinstance(self.score, bool) or not math.isfinite(float(self.score)) or not 0.0 <= self.score <= 100.0:
            raise LevelMetricsError("lane mapping score must be in [0, 100]")
        if not isinstance(self.lane, LaneClass) or (self.requested_class is not None and not isinstance(self.requested_class, LaneClass)):
            raise LevelMetricsError("lane mapping class is malformed")
        if self.comparison not in {None, "MATCH", "MISMATCH"}:
            raise LevelMetricsError("lane comparison is malformed")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": LANE_MAPPING_SCHEMA, "version": LANE_MAPPING_VERSION, "score_digest": self.score_digest, "score_policy_version": self.score_policy_version, "mapping_policy_version": self.mapping_policy_version, "score": float(self.score), "lane": self.lane.value, "requested_class": self.requested_class.value if self.requested_class else None, "comparison": self.comparison}


def map_challenge_score(score_result: ChallengeScoreResult, requested_class: Difficulty | str | None = None) -> LaneMappingResult:
    if not isinstance(score_result, ChallengeScoreResult):
        raise LevelMetricsError("ChallengeScoreResult is required")
    score = float(score_result.score)
    if score < 0.0 or score > 100.0:
        raise LevelMetricsError("score is outside the lane mapping range")
    lane = LaneClass.EASY if score < 25.0 else LaneClass.MEDIUM if score < 50.0 else LaneClass.HARD if score < 75.0 else LaneClass.VERY_HARD
    requested = LaneClass(parse_difficulty(requested_class).value) if requested_class is not None else None
    comparison = None if requested is None else ("MATCH" if requested is lane else "MISMATCH")
    return LaneMappingResult(score_result.digest(), score_result.policy_version, LANE_MAPPING_POLICY_VERSION, score, lane, requested, comparison)


@dataclass(frozen=True, slots=True)
class MetricProviderIdentity:
    provider_id: str
    provider_version: str

    def __post_init__(self) -> None:
        _provider_text(self.provider_id, "metric provider id")
        _provider_text(self.provider_version, "metric provider version")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": PROVIDER_IDENTITY_SCHEMA, "version": PROVIDER_IDENTITY_VERSION, "provider_id": self.provider_id, "provider_version": self.provider_version}


@dataclass(frozen=True, slots=True)
class DifficultyAnalysis(_DependencyResultMixin):
    level_source_sha256: str
    authority: object
    solver_evidence: SolverEvidenceIdentity
    level_metrics_schema: str
    level_metrics_version: int
    level_metrics_digest: str
    metric_provenance: tuple[tuple[str, MetricProviderIdentity], ...]
    component_availability: tuple[tuple[str, AnalysisDisposition], ...]
    disposition: AnalysisDisposition
    reason: str | None
    challenge_score_digest: str | None = None
    challenge_score_policy_version: str | None = None
    lane_mapping_digest: str | None = None
    lane_mapping_policy_version: str | None = None

    def __post_init__(self) -> None:
        from .compact_solver_state import SolverStateAuthority

        _digest_text(self.level_source_sha256, "analysis level source SHA-256")
        if not isinstance(self.authority, SolverStateAuthority) or not isinstance(self.solver_evidence, SolverEvidenceIdentity):
            raise LevelMetricsError("analysis authority or solver evidence is malformed")
        _provider_text(self.level_metrics_schema, "analysis LevelMetrics schema")
        if type(self.level_metrics_version) is not int or self.level_metrics_version < 1:
            raise LevelMetricsError("analysis LevelMetrics version is malformed")
        _digest_text(self.level_metrics_digest, "analysis LevelMetrics digest")
        if type(self.metric_provenance) is not tuple or any(type(name) is not str or not isinstance(provider, MetricProviderIdentity) for name, provider in self.metric_provenance):
            raise LevelMetricsError("analysis metric provenance is malformed")
        if type(self.component_availability) is not tuple or any(type(name) is not str or not isinstance(value, AnalysisDisposition) for name, value in self.component_availability):
            raise LevelMetricsError("analysis component availability is malformed")
        if not isinstance(self.disposition, AnalysisDisposition):
            raise LevelMetricsError("analysis disposition is malformed")
        if self.reason is not None and (type(self.reason) is not str or not self.reason.strip()):
            raise LevelMetricsError("analysis reason is malformed")
        for value, label in ((self.challenge_score_digest, "challenge score digest"), (self.lane_mapping_digest, "lane mapping digest")):
            if value is not None:
                _digest_text(value, label)
        if (self.challenge_score_digest is None) != (self.challenge_score_policy_version is None) or (self.lane_mapping_digest is None) != (self.lane_mapping_policy_version is None):
            raise LevelMetricsError("analysis result digest and policy version must be paired")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": ANALYSIS_SCHEMA,
            "version": ANALYSIS_VERSION,
            "level_source_sha256": self.level_source_sha256,
            "authority": self.authority.canonical_dict(),
            "solver_evidence": self.solver_evidence.canonical_dict(),
            "level_metrics": {"schema": self.level_metrics_schema, "version": self.level_metrics_version, "digest": self.level_metrics_digest},
            "metric_provenance": {name: provider.canonical_dict() for name, provider in self.metric_provenance},
            "component_availability": {name: value.value for name, value in self.component_availability},
            "challenge_score": None if self.challenge_score_digest is None else {"digest": self.challenge_score_digest, "policy_version": self.challenge_score_policy_version},
            "lane_mapping": None if self.lane_mapping_digest is None else {"digest": self.lane_mapping_digest, "policy_version": self.lane_mapping_policy_version},
            "disposition": self.disposition.value,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "DifficultyAnalysis":
        fields = frozenset({"schema", "version", "level_source_sha256", "authority", "solver_evidence", "level_metrics", "metric_provenance", "component_availability", "challenge_score", "lane_mapping", "disposition", "reason"})
        value = payload if isinstance(payload, Mapping) and set(payload) == fields else None
        if value is None or value["schema"] != ANALYSIS_SCHEMA or value["version"] != ANALYSIS_VERSION:
            raise LevelMetricsError("analysis schema/version or fields are unsupported")
        from .compact_solver_state import SolverStateAuthority

        authority_data = value["authority"]
        if not isinstance(authority_data, Mapping) or set(authority_data) != {"schema", "version", "repository", "commit_sha", "proof_state_source_path"}:
            raise LevelMetricsError("analysis authority fields are malformed")
        authority = SolverStateAuthority(authority_data["repository"], authority_data["commit_sha"], authority_data["proof_state_source_path"], authority_data["version"])
        evidence = SolverEvidenceIdentity.from_dict(value["solver_evidence"])
        metric_data = value["level_metrics"]
        if not isinstance(metric_data, Mapping) or set(metric_data) != {"schema", "version", "digest"}:
            raise LevelMetricsError("analysis LevelMetrics identity is malformed")
        provenance_data = value["metric_provenance"]
        if not isinstance(provenance_data, Mapping):
            raise LevelMetricsError("analysis metric provenance is malformed")
        provenance = tuple((name, MetricProviderIdentity(item["provider_id"], item["provider_version"])) for name, item in sorted(provenance_data.items()))
        availability_data = value["component_availability"]
        if not isinstance(availability_data, Mapping):
            raise LevelMetricsError("analysis availability is malformed")
        try:
            availability = tuple((name, AnalysisDisposition(item)) for name, item in sorted(availability_data.items()))
            disposition = AnalysisDisposition(value["disposition"])
        except (TypeError, ValueError) as exc:
            raise LevelMetricsError("analysis disposition is malformed") from exc
        score_data = value["challenge_score"]
        lane_data = value["lane_mapping"]
        if score_data is not None and (not isinstance(score_data, Mapping) or set(score_data) != {"digest", "policy_version"}):
            raise LevelMetricsError("analysis challenge score identity is malformed")
        if lane_data is not None and (not isinstance(lane_data, Mapping) or set(lane_data) != {"digest", "policy_version"}):
            raise LevelMetricsError("analysis lane mapping identity is malformed")
        return cls(value["level_source_sha256"], authority, evidence, metric_data["schema"], metric_data["version"], metric_data["digest"], provenance, availability, disposition, value["reason"], score_data["digest"] if score_data is not None else None, score_data["policy_version"] if score_data is not None else None, lane_data["digest"] if lane_data is not None else None, lane_data["policy_version"] if lane_data is not None else None)


def build_difficulty_analysis(
    level_metrics: LevelMetrics,
    score_result: ChallengeScoreResult | None = None,
    lane_result: LaneMappingResult | None = None,
    metric_provenance: Mapping[str, MetricProviderIdentity] | None = None,
) -> DifficultyAnalysis:
    if not isinstance(level_metrics, LevelMetrics):
        raise LevelMetricsError("LevelMetrics is required")
    if score_result is not None and (not isinstance(score_result, ChallengeScoreResult) or score_result.source_metrics_digest != level_metrics.digest()):
        raise LevelMetricsError("challenge score is not bound to this LevelMetrics digest")
    if lane_result is not None and (score_result is None or not isinstance(lane_result, LaneMappingResult) or lane_result.score_digest != score_result.digest()):
        raise LevelMetricsError("lane mapping is not bound to this Challenge Score digest")
    supplied = dict(metric_provenance or {})
    populated = level_metrics.measurement_content()
    unknown = set(supplied) - {metric.value for metric in MetricId}
    if unknown or any(not isinstance(provider, MetricProviderIdentity) for provider in supplied.values()):
        raise LevelMetricsError("metric provenance contains an unknown or malformed metric")
    for name in populated:
        supplied.setdefault(name, MetricProviderIdentity("solver-evidence" if name in {"solution_depth", "move_count", "states_visited", "dead_ends", "branching", "forced_moves"} else "canonical-provider", "BOUND_PROVIDER_V1"))
    provenance = tuple(sorted(supplied.items()))
    availability = tuple((metric.value, AnalysisDisposition.AVAILABLE if metric.value in populated else AnalysisDisposition.UNAVAILABLE) for metric in MetricId)
    return DifficultyAnalysis(level_metrics.source_sha256, level_metrics.authority, level_metrics.solver_evidence, "scrubbots-level-metrics", 1, level_metrics.digest(), provenance, availability, level_metrics.disposition, level_metrics.reason, score_result.digest() if score_result else None, score_result.policy_version if score_result else None, lane_result.digest() if lane_result else None, lane_result.mapping_policy_version if lane_result else None)


@dataclass(frozen=True, slots=True)
class CalibrationDataset(_DependencyResultMixin):
    score_policy_version: str
    cohort_label: str
    completion_count: int
    failure_count: int
    move_count_sum: int
    sample_count: int
    minimum_sample_count: int

    def __post_init__(self) -> None:
        _provider_text(self.score_policy_version, "calibration score policy version")
        if type(self.cohort_label) is not str or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", self.cohort_label) or "@" in self.cohort_label:
            raise LevelMetricsError("calibration cohort label must be an anonymous safe token")
        values = (self.completion_count, self.failure_count, self.move_count_sum, self.sample_count, self.minimum_sample_count)
        if any(type(value) is not int or value < 0 for value in values) or self.minimum_sample_count < 1 or self.sample_count < self.minimum_sample_count or self.completion_count + self.failure_count > self.sample_count:
            raise LevelMetricsError("calibration aggregate counts are malformed or below minimum sample count")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": CALIBRATION_SCHEMA, "version": CALIBRATION_VERSION, "score_policy_version": self.score_policy_version, "cohort_label": self.cohort_label, "completion_count": self.completion_count, "failure_count": self.failure_count, "move_count_sum": self.move_count_sum, "sample_count": self.sample_count, "minimum_sample_count": self.minimum_sample_count}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "CalibrationDataset":
        fields = {"schema", "version", "score_policy_version", "cohort_label", "completion_count", "failure_count", "move_count_sum", "sample_count", "minimum_sample_count"}
        if not isinstance(payload, Mapping) or set(payload) != fields or payload["schema"] != CALIBRATION_SCHEMA or payload["version"] != CALIBRATION_VERSION:
            raise LevelMetricsError("calibration dataset schema/version or fields are unsupported")
        return cls(payload["score_policy_version"], payload["cohort_label"], payload["completion_count"], payload["failure_count"], payload["move_count_sum"], payload["sample_count"], payload["minimum_sample_count"])


@dataclass(frozen=True, slots=True)
class CalibrationPlan(_DependencyResultMixin):
    state: str = CALIBRATION_POLICY_STATE
    score_policy_version: str = CHALLENGE_SCORE_POLICY_VERSION
    dataset: CalibrationDataset | None = None
    network_enabled: bool = False
    collection_enabled: bool = False

    def __post_init__(self) -> None:
        if self.state != CALIBRATION_POLICY_STATE or self.score_policy_version != CHALLENGE_SCORE_POLICY_VERSION or self.network_enabled or self.collection_enabled:
            raise LevelMetricsError("calibration is design-only and disabled until policy approval")
        if self.dataset is not None and not isinstance(self.dataset, CalibrationDataset):
            raise LevelMetricsError("calibration dataset is malformed")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": CALIBRATION_SCHEMA + ".plan", "version": CALIBRATION_VERSION, "state": self.state, "score_policy_version": self.score_policy_version, "dataset": self.dataset.canonical_dict() if self.dataset else None, "network_enabled": False, "collection_enabled": False}


def disabled_calibration_plan(dataset: CalibrationDataset | None = None) -> CalibrationPlan:
    return CalibrationPlan(dataset=dataset)


def _accepted_report(level_metrics: LevelMetrics, report: SolverEvidenceReport) -> None:
    if not isinstance(level_metrics, LevelMetrics) or not isinstance(report, SolverEvidenceReport):
        raise LevelMetricsError("LevelMetrics and SolverEvidenceReport are required")
    if level_metrics.evidence_digest != report.digest():
        raise LevelMetricsError("solver evidence digest does not match LevelMetrics identity")


def populate_solution_depth_and_move_count(
    level_metrics: LevelMetrics,
    report: SolverEvidenceReport,
) -> LevelMetrics:
    """Populate witness edge depth and move count without interpreting gameplay."""

    _accepted_report(level_metrics, report)
    current = level_metrics.metrics or MetricValues()
    if report.execution is not SearchExecutionDisposition.AVAILABLE:
        return level_metrics
    if report.result.verdict is not SearchVerdict.SOLVED or report.metrics is None:
        return level_metrics
    witness = report.result.path
    recorded = report.metrics.path
    if len(recorded) != len(witness) or tuple(move.canonical_dict() for move in witness) != recorded:
        return level_metrics
    return replace(
        level_metrics,
        metrics=replace(current, solution_depth=len(witness), move_count=len(witness)),
    )


def populate_search_complexity_metrics(
    level_metrics: LevelMetrics,
    report: SolverEvidenceReport,
) -> LevelMetrics:
    """Populate observed search metrics without reconstructing legal moves."""

    _accepted_report(level_metrics, report)
    if report.execution is not SearchExecutionDisposition.AVAILABLE or report.metrics is None:
        return level_metrics
    observed = report.metrics
    branch_counts = tuple(observed.branch_counts)
    current = level_metrics.metrics or MetricValues()
    if not branch_counts:
        return replace(
            level_metrics,
            metrics=replace(
                current,
                states_visited=observed.visited_count,
                dead_ends=observed.dead_end_count,
            ),
        )
    branching = sum(branch_counts) / len(branch_counts)
    forced_moves = sum(1 for count in branch_counts if count == 1)
    return replace(
        level_metrics,
        metrics=replace(
            current,
            states_visited=observed.visited_count,
            dead_ends=observed.dead_end_count,
            branching=branching,
            forced_moves=forced_moves,
        ),
    )


__all__ = [
    "DEPENDENCY_DEPTH_SCHEMA",
    "DEPENDENCY_DEPTH_VERSION",
    "DependencyDepthResult",
    "BAIT_DEADLOCK_SCHEMA",
    "BAIT_DEADLOCK_VERSION",
    "BaitDeadlockResult",
    "VOLATILITY_SCHEMA",
    "VOLATILITY_VERSION",
    "VolatilityResult",
    "VolatilitySnapshot",
    "CHALLENGE_SCORE_SCHEMA",
    "CHALLENGE_SCORE_VERSION",
    "CHALLENGE_SCORE_POLICY_VERSION",
    "ChallengeScoreResult",
    "ScoreComponent",
    "LANE_MAPPING_SCHEMA",
    "LANE_MAPPING_VERSION",
    "LANE_MAPPING_POLICY_VERSION",
    "LaneClass",
    "LaneMappingResult",
    "ANALYSIS_SCHEMA",
    "ANALYSIS_VERSION",
    "PROVIDER_IDENTITY_SCHEMA",
    "PROVIDER_IDENTITY_VERSION",
    "MetricProviderIdentity",
    "DifficultyAnalysis",
    "CALIBRATION_SCHEMA",
    "CALIBRATION_VERSION",
    "CALIBRATION_POLICY_STATE",
    "CalibrationDataset",
    "CalibrationPlan",
    "SLOT_PRESSURE_SCHEMA",
    "SLOT_PRESSURE_VERSION",
    "SlotPressureResult",
    "SlotSnapshot",
    "populate_dependency_depth",
    "populate_bait_deadlock",
    "populate_volatility",
    "calculate_challenge_score",
    "map_challenge_score",
    "build_difficulty_analysis",
    "disabled_calibration_plan",
    "populate_slot_pressure",
    "populate_search_complexity_metrics",
    "populate_solution_depth_and_move_count",
    "slot_pressure_from_snapshots",
    "bait_deadlock_from_children",
    "volatility_from_snapshots",
    "unavailable_volatility_result",
    "unavailable_slot_pressure_result",
    "unavailable_dependency_result",
]
