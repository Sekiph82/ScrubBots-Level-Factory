from __future__ import annotations

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.difficulty_analysis import EvidenceDisposition, VolatilitySnapshot, populate_volatility, unavailable_volatility_result, volatility_from_snapshots
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, LevelMetricsError, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def level() -> LevelMetrics:
    policy = BaselineSearchPolicy()
    search = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, (), "fixture", policy)
    budget = SolverBudgetPolicy()
    evidence = SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, search, SolverMetrics((), False, 1, None, 0, 0, (), 0, ()), 1.0, budget_policy=budget, budget_result=BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "fixture", "SOLVED", "fixture"))
    return LevelMetrics(LevelIdentity("a" * 64, "lf04-007", 20, 20, 400), AUTHORITY, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, evidence.digest()), AnalysisDisposition.AVAILABLE)


def test_stable_trace_has_zero_volatility() -> None:
    snapshot = VolatilitySnapshot(5, 10, 2, 4, 1, 4)
    result = volatility_from_snapshots(level(), "b" * 64, (snapshot, snapshot))
    assert result.volatility == 0.0


def test_changing_trace_uses_closed_normalized_signature() -> None:
    first = VolatilitySnapshot(10, 10, 4, 4, 0, 4)
    second = VolatilitySnapshot(5, 10, 2, 4, 2, 4)
    result = volatility_from_snapshots(level(), "b" * 64, (first, second))
    assert result.volatility == pytest.approx((0.5 + 0.5 + 0.5) / 3.0)
    with pytest.raises(LevelMetricsError):
        populate_volatility(level(), result)


def test_fixture_ordered_trace_is_explicitly_non_production() -> None:
    result = volatility_from_snapshots(level(), "b" * 64, (VolatilitySnapshot(1, 2, 1, 2, 1, 2), VolatilitySnapshot(1, 2, 1, 2, 1, 2)))
    assert result.evidence.disposition.value == "FIXTURE"


def test_copied_provider_identity_does_not_elevate_snapshot_trace() -> None:
    metrics = level()
    result = volatility_from_snapshots(metrics, "b" * 64, (VolatilitySnapshot(1, 2, 1, 2, 1, 2), VolatilitySnapshot(1, 2, 1, 2, 1, 2)), provider_id="canonical-state-trace", provider_version="CANONICAL_STATE_TRACE_V1")
    assert result.evidence.disposition is EvidenceDisposition.FIXTURE
    with pytest.raises(LevelMetricsError):
        populate_volatility(metrics, result)


def test_bounds_and_determinism() -> None:
    snapshots = (VolatilitySnapshot(0, 10, 0, 4, 0, 4), VolatilitySnapshot(10, 10, 4, 4, 4, 4))
    first = volatility_from_snapshots(level(), "b" * 64, snapshots)
    second = volatility_from_snapshots(level(), "b" * 64, snapshots)
    assert 0.0 <= first.volatility <= 1.0
    assert first.canonical_bytes() == second.canonical_bytes()


def test_one_state_and_unavailable_trace_are_absent() -> None:
    metrics = level()
    with pytest.raises(LevelMetricsError):
        volatility_from_snapshots(metrics, "b" * 64, (VolatilitySnapshot(1, 2, 1, 2, 1, 2),))
    unavailable = unavailable_volatility_result(metrics, "b" * 64, "canonical ordered trace unavailable")
    assert unavailable.disposition is AnalysisDisposition.UNAVAILABLE
    assert populate_volatility(metrics, unavailable).metrics is None


def test_malformed_snapshot_is_rejected() -> None:
    with pytest.raises(LevelMetricsError):
        VolatilitySnapshot(3, 2, 0, 1, 0, 1)
