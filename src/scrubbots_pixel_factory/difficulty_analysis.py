"""Deterministic, provenance-bound M04 difficulty analysis contracts."""

from __future__ import annotations

from dataclasses import replace

from .baseline_search import SearchExecutionDisposition, SearchVerdict
from .level_metrics import LevelMetrics, LevelMetricsError, MetricValues
from .solver_evidence import SolverEvidenceReport


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


__all__ = ["populate_solution_depth_and_move_count"]
