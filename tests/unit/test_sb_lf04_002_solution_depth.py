from __future__ import annotations

import pytest

from scrubbots_pixel_factory.baseline_search import (
    BaselineSearchPolicy,
    BaselineSearchResult,
    SearchExecutionDisposition,
    SearchVerdict,
)
from scrubbots_pixel_factory.compact_solver_state import (
    CANONICAL_PROOF_STATE_AUTHORITY_SHA,
    LevelIdentity,
    SolverStateAuthority,
)
from scrubbots_pixel_factory.difficulty_analysis import populate_solution_depth_and_move_count
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, LevelMetricsError, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.legal_move_provider import LegalMove
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)
POLICY = BaselineSearchPolicy()


def make_report(verdict: SearchVerdict, path: tuple[LegalMove, ...], *, with_metrics: bool = True, elapsed: float = 9.5) -> SolverEvidenceReport:
    result = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, verdict, path, "fixture", POLICY)
    metrics = None
    if with_metrics:
        metrics = SolverMetrics((), False, 1, None, 0, len(path), tuple(), 0, tuple(move.canonical_dict() for move in path))
    budget = SolverBudgetPolicy()
    outcome = BudgetedSolverResult(
        SolverOutcomeDisposition.SOLVED if verdict is SearchVerdict.SOLVED else SolverOutcomeDisposition.PROVEN_UNSOLVABLE,
        budget,
        "fixture",
        verdict.value,
        "fixture",
    )
    return SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, result, metrics, elapsed, budget_policy=budget, budget_result=outcome)


def make_level(report: SolverEvidenceReport, metrics: MetricValues | None = None) -> LevelMetrics:
    return LevelMetrics(
        LevelIdentity("a" * 64, "lf04-002", 20, 21, 420),
        AUTHORITY,
        SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, report.digest()),
        AnalysisDisposition.AVAILABLE,
        metrics=metrics,
    )


def test_solved_witness_uses_canonical_path_length_for_both_values() -> None:
    report = make_report(SearchVerdict.SOLVED, (LegalMove(1), LegalMove(4), LegalMove(2)))
    result = populate_solution_depth_and_move_count(make_level(report), report)
    assert result.metrics == MetricValues(solution_depth=3, move_count=3)


def test_solved_at_start_is_zero_zero() -> None:
    report = make_report(SearchVerdict.SOLVED, ())
    result = populate_solution_depth_and_move_count(make_level(report), report)
    assert result.metrics == MetricValues(solution_depth=0, move_count=0)


@pytest.mark.parametrize("verdict", [SearchVerdict.PROVEN_UNSOLVABLE, SearchVerdict.INCONCLUSIVE])
def test_non_solved_dispositions_do_not_fabricate_zero(verdict: SearchVerdict) -> None:
    report = make_report(verdict, ())
    result = populate_solution_depth_and_move_count(make_level(report), report)
    assert result.metrics is None


def test_missing_witness_preserves_unrelated_metric_without_zero_values() -> None:
    report = make_report(SearchVerdict.SOLVED, (LegalMove(1),), with_metrics=False)
    result = populate_solution_depth_and_move_count(make_level(report, MetricValues(states_visited=8)), report)
    assert result.metrics == MetricValues(states_visited=8)


def test_recorded_witness_mismatch_does_not_populate_values() -> None:
    report = make_report(SearchVerdict.SOLVED, (LegalMove(1),), with_metrics=True)
    malformed_metrics = SolverMetrics((), False, 1, None, 0, 1, tuple(), 0, tuple())
    report = make_report(SearchVerdict.SOLVED, (LegalMove(1),), with_metrics=False)
    report = SolverEvidenceReport(report.execution, report.result, malformed_metrics, report.elapsed_seconds, report.search_policy, report.budget_policy, report.budget_result)
    result = populate_solution_depth_and_move_count(make_level(report), report)
    assert result.metrics is None


def test_evidence_digest_mismatch_is_rejected() -> None:
    report = make_report(SearchVerdict.SOLVED, (LegalMove(1),))
    level = make_level(report)
    wrong = LevelMetrics(level.level, level.authority, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, "b" * 64), level.disposition)
    with pytest.raises(LevelMetricsError):
        populate_solution_depth_and_move_count(wrong, report)


def test_timing_does_not_change_deterministic_measurements() -> None:
    first = make_report(SearchVerdict.SOLVED, (LegalMove(1),), elapsed=1.0)
    second = make_report(SearchVerdict.SOLVED, (LegalMove(1),), elapsed=999.0)
    assert populate_solution_depth_and_move_count(make_level(first), first).measurement_content() == populate_solution_depth_and_move_count(make_level(second), second).measurement_content()
