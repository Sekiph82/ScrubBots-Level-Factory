from __future__ import annotations

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.difficulty_analysis import populate_search_complexity_metrics
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, LevelMetricsError, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def report(branch_counts: tuple[int, ...], *, verdict: SearchVerdict = SearchVerdict.SOLVED, visited: int = 12, dead_ends: int = 3) -> SolverEvidenceReport:
    policy = BaselineSearchPolicy()
    result = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, verdict, (), "fixture", policy)
    metrics = SolverMetrics((), False, visited, None, dead_ends, 0, branch_counts, 0, ())
    budget = SolverBudgetPolicy()
    outcome = BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "fixture", verdict.value, "fixture")
    return SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, result, metrics, 1.0, budget_policy=budget, budget_result=outcome)


def level(evidence: SolverEvidenceReport, metrics: MetricValues | None = None) -> LevelMetrics:
    return LevelMetrics(
        LevelIdentity("c" * 64, "lf04-003", 20, 21, 420),
        AUTHORITY,
        SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, evidence.digest()),
        AnalysisDisposition.AVAILABLE,
        metrics=metrics,
    )


def test_known_branch_tuple_populates_mean_and_forced_count() -> None:
    evidence = report((1, 2, 5, 1))
    result = populate_search_complexity_metrics(level(evidence), evidence)
    assert result.metrics == MetricValues(states_visited=12, dead_ends=3, branching=2.25, forced_moves=2)


def test_no_branch_observation_leaves_branching_and_forced_absent() -> None:
    evidence = report(())
    result = populate_search_complexity_metrics(level(evidence, MetricValues(solution_depth=4, move_count=4)), evidence)
    assert result.metrics == MetricValues(solution_depth=4, move_count=4, states_visited=12, dead_ends=3)


def test_inconclusive_accepted_metrics_are_still_observed_without_zero_fabrication() -> None:
    evidence = report((1,), verdict=SearchVerdict.INCONCLUSIVE, visited=0, dead_ends=0)
    result = populate_search_complexity_metrics(level(evidence), evidence)
    assert result.metrics == MetricValues(states_visited=0, dead_ends=0, branching=1.0, forced_moves=1)


def test_evidence_mismatch_is_rejected() -> None:
    evidence = report((1,))
    envelope = level(evidence)
    wrong = LevelMetrics(envelope.level, envelope.authority, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, "d" * 64), envelope.disposition)
    with pytest.raises(LevelMetricsError):
        populate_search_complexity_metrics(wrong, evidence)


def test_repeat_is_deterministic_and_preserves_002_values() -> None:
    evidence = report((1, 3))
    seed = MetricValues(solution_depth=2, move_count=2)
    first = populate_search_complexity_metrics(level(evidence, seed), evidence)
    second = populate_search_complexity_metrics(level(evidence, seed), evidence)
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.metrics is not None and first.metrics.solution_depth == 2 and first.metrics.move_count == 2
