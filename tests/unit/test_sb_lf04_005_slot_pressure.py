from __future__ import annotations

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.difficulty_analysis import SlotSnapshot, SlotPressureResult, populate_slot_pressure, slot_pressure_from_snapshots, unavailable_slot_pressure_result
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, LevelMetricsError, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def level() -> LevelMetrics:
    policy = BaselineSearchPolicy()
    search = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, (), "fixture", policy)
    evidence = SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, search, SolverMetrics((), False, 1, None, 0, 0, (), 0, ()), 1.0, budget_policy=SolverBudgetPolicy(), budget_result=BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, SolverBudgetPolicy(), "fixture", "SOLVED", "fixture"))
    return LevelMetrics(LevelIdentity("5" * 64, "lf04-005", 20, 20, 400), AUTHORITY, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, evidence.digest()), AnalysisDisposition.AVAILABLE)


def test_empty_partial_and_full_snapshots_are_bounded() -> None:
    metrics = level()
    result = slot_pressure_from_snapshots(metrics, "6" * 64, (SlotSnapshot(0, 5), SlotSnapshot(2, 5), SlotSnapshot(5, 5)))
    assert result.slot_pressure == 1.0
    assert populate_slot_pressure(metrics, result).metrics == MetricValues(slot_pressure=1.0)


def test_maximum_is_deterministic_and_trace_is_immutable() -> None:
    metrics = level()
    snapshots = (SlotSnapshot(1, 4), SlotSnapshot(3, 8))
    first = slot_pressure_from_snapshots(metrics, "6" * 64, snapshots)
    second = slot_pressure_from_snapshots(metrics, "6" * 64, snapshots)
    assert first.slot_pressure == 0.375
    assert first.canonical_bytes() == second.canonical_bytes()


def test_unavailable_trace_stays_absent() -> None:
    metrics = level()
    unavailable = unavailable_slot_pressure_result(metrics, "6" * 64, "canonical slot trace is unavailable")
    assert populate_slot_pressure(metrics, unavailable).metrics is None


def test_authority_binding_mismatch_is_rejected() -> None:
    metrics = level()
    accepted = slot_pressure_from_snapshots(metrics, "6" * 64, (SlotSnapshot(1, 2),))
    wrong = SlotPressureResult(accepted.disposition, accepted.authority, "7" * 64, accepted.state_digest, accepted.evidence_digest, accepted.provider_id, accepted.provider_version, accepted.snapshots, accepted.slot_pressure, accepted.reason)
    with pytest.raises(LevelMetricsError):
        populate_slot_pressure(metrics, wrong)


@pytest.mark.parametrize("snapshot", [(1, 0), (-1, 2), (3, 2)])
def test_malformed_capacity_or_occupancy_is_rejected(snapshot: tuple[int, int]) -> None:
    with pytest.raises(LevelMetricsError):
        SlotSnapshot(*snapshot)


def test_unavailable_result_cannot_carry_value() -> None:
    metrics = level()
    with pytest.raises(LevelMetricsError):
        SlotPressureResult(AnalysisDisposition.UNAVAILABLE, metrics.authority, metrics.source_sha256, "6" * 64, metrics.evidence_digest, "fixture", "v1", (), 0.0, "bad")
