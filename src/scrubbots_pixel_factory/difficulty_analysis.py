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


__all__ = ["populate_search_complexity_metrics", "populate_solution_depth_and_move_count"]
