from __future__ import annotations

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.difficulty_analysis import bait_deadlock_from_children, populate_bait_deadlock
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, LevelMetricsError, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def level() -> LevelMetrics:
    policy = BaselineSearchPolicy()
    search = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, (), "fixture", policy)
    budget = SolverBudgetPolicy()
    evidence = SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, search, SolverMetrics((), False, 1, None, 0, 0, (), 0, ()), 1.0, budget_policy=budget, budget_result=BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "fixture", "SOLVED", "fixture"))
    return LevelMetrics(LevelIdentity("7" * 64, "lf04-006", 20, 20, 400), AUTHORITY, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, evidence.digest()), AnalysisDisposition.AVAILABLE)


def test_zero_and_partial_deadlocks_are_exact() -> None:
    metrics = level()
    zero = bait_deadlock_from_children(metrics, "8" * 64, (SolverOutcomeDisposition.SOLVED, SolverOutcomeDisposition.SOLVED))
    partial = bait_deadlock_from_children(metrics, "8" * 64, (SolverOutcomeDisposition.PROVEN_UNSOLVABLE, SolverOutcomeDisposition.SOLVED, SolverOutcomeDisposition.PROVEN_UNSOLVABLE, SolverOutcomeDisposition.SOLVED))
    assert zero.bait_deadlock == 0.0
    assert partial.bait_deadlock == 0.5


def test_all_deadlocks_populate_metric() -> None:
    metrics = level()
    result = bait_deadlock_from_children(metrics, "8" * 64, (SolverOutcomeDisposition.PROVEN_UNSOLVABLE,) * 3)
    assert result.bait_deadlock == 1.0
    with pytest.raises(LevelMetricsError):
        populate_bait_deadlock(metrics, result)


def test_fixture_counterfactual_tuple_cannot_claim_canonical_proof() -> None:
    result = bait_deadlock_from_children(level(), "8" * 64, (SolverOutcomeDisposition.PROVEN_UNSOLVABLE,))
    assert result.evidence.disposition.value == "FIXTURE"


def test_copied_canonical_provider_string_does_not_elevate_fixture_tuple() -> None:
    metrics = level()
    result = bait_deadlock_from_children(metrics, "8" * 64, (SolverOutcomeDisposition.PROVEN_UNSOLVABLE,), provider_id="canonical-counterfactual", provider_version="CANONICAL_COUNTERFACTUAL_V1")
    with pytest.raises(LevelMetricsError):
        populate_bait_deadlock(metrics, result)


def test_inconclusive_child_prevents_exact_claim_and_remains_absent() -> None:
    metrics = level()
    result = bait_deadlock_from_children(metrics, "8" * 64, (SolverOutcomeDisposition.PROVEN_UNSOLVABLE, SolverOutcomeDisposition.INCONCLUSIVE))
    assert result.disposition is AnalysisDisposition.INCONCLUSIVE and result.bait_deadlock is None and not result.exact
    assert populate_bait_deadlock(metrics, result).metrics is None


def test_unavailable_child_is_not_counted_as_proven_deadlock() -> None:
    result = bait_deadlock_from_children(level(), "8" * 64, (SolverOutcomeDisposition.UNAVAILABLE,))
    assert result.disposition is AnalysisDisposition.UNAVAILABLE and result.proven_deadlock_move_count == 0


def test_repeat_and_authority_binding_are_deterministic() -> None:
    metrics = level()
    first = bait_deadlock_from_children(metrics, "8" * 64, (SolverOutcomeDisposition.PROVEN_UNSOLVABLE, SolverOutcomeDisposition.SOLVED))
    second = bait_deadlock_from_children(metrics, "8" * 64, (SolverOutcomeDisposition.PROVEN_UNSOLVABLE, SolverOutcomeDisposition.SOLVED))
    assert first.canonical_bytes() == second.canonical_bytes()
    bad = type(first)(first.disposition, first.authority, "9" * 64, first.state_digest, first.evidence_digest, first.provider_id, first.provider_version, first.legal_move_count, first.proven_deadlock_move_count, first.bait_deadlock, first.exact, first.reason)
    with pytest.raises(LevelMetricsError):
        populate_bait_deadlock(metrics, bad)
