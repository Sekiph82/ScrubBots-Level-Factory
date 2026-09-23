"""Deterministic, provenance-bound M04 difficulty analysis contracts."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import re
from collections.abc import Mapping

from .baseline_search import SearchExecutionDisposition, SearchVerdict
from .level_metrics import AnalysisDisposition, LevelMetrics, LevelMetricsError, MetricValues
from .solver_evidence import SolverEvidenceReport


DEPENDENCY_DEPTH_SCHEMA = "scrubbots-canonical-dependency-depth"
DEPENDENCY_DEPTH_VERSION = 1
SLOT_PRESSURE_SCHEMA = "scrubbots-canonical-slot-pressure"
SLOT_PRESSURE_VERSION = 1
BAIT_DEADLOCK_SCHEMA = "scrubbots-canonical-bait-deadlock"
BAIT_DEADLOCK_VERSION = 1
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
    "SLOT_PRESSURE_SCHEMA",
    "SLOT_PRESSURE_VERSION",
    "SlotPressureResult",
    "SlotSnapshot",
    "populate_dependency_depth",
    "populate_bait_deadlock",
    "populate_slot_pressure",
    "populate_search_complexity_metrics",
    "populate_solution_depth_and_move_count",
    "slot_pressure_from_snapshots",
    "bait_deadlock_from_children",
    "unavailable_slot_pressure_result",
    "unavailable_dependency_result",
]
