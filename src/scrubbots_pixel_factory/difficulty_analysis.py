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
    "populate_dependency_depth",
    "populate_search_complexity_metrics",
    "populate_solution_depth_and_move_count",
    "unavailable_dependency_result",
]
