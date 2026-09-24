from __future__ import annotations

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.difficulty_analysis import DifficultyAnalysis, MetricProviderIdentity, build_difficulty_analysis, calculate_challenge_score, map_challenge_score
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, LevelMetricsError, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def level(move_count: int = 2) -> LevelMetrics:
    policy = BaselineSearchPolicy()
    search = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, (), "fixture", policy)
    budget = SolverBudgetPolicy()
    evidence = SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, search, SolverMetrics((), False, 3, None, 1, 0, (1,), 0, ()), 1.0, budget_policy=budget, budget_result=BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "fixture", "SOLVED", "fixture"))
    return LevelMetrics(LevelIdentity("d" * 64, "lf04-010", 20, 20, 400), AUTHORITY, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, evidence.digest()), AnalysisDisposition.AVAILABLE, metrics=MetricValues(move_count=move_count, states_visited=3, dead_ends=1, branching=1.0, forced_moves=1))


def test_valid_round_trip_is_deterministic_and_closed() -> None:
    metrics = level()
    score = calculate_challenge_score(metrics)
    lane = map_challenge_score(score)
    envelope = build_difficulty_analysis(metrics, score, lane, {"move_count": MetricProviderIdentity("solver-evidence", "SOLVER_EVIDENCE_V1")})
    restored = DifficultyAnalysis.from_dict(envelope.canonical_dict())
    assert envelope.canonical_bytes() == restored.canonical_bytes()
    assert envelope.digest() == restored.digest()


def test_score_and_lane_cross_binding_is_rejected() -> None:
    first = level(2)
    second = level(3)
    score_first = calculate_challenge_score(first)
    score_second = calculate_challenge_score(second)
    with pytest.raises(LevelMetricsError):
        build_difficulty_analysis(first, score_second)
    with pytest.raises(LevelMetricsError):
        build_difficulty_analysis(first, score_first, map_challenge_score(score_second))


def test_unknown_fields_versions_and_operational_telemetry_are_rejected_or_absent() -> None:
    envelope = build_difficulty_analysis(level(), calculate_challenge_score(level()))
    payload = envelope.canonical_dict()
    with pytest.raises(LevelMetricsError):
        DifficultyAnalysis.from_dict({**payload, "unexpected": True})
    with pytest.raises(LevelMetricsError):
        DifficultyAnalysis.from_dict({**payload, "version": 99})
    forbidden = {"elapsed_seconds", "timeout_seconds", "local_path", "machine_id", "ui_state"}
    assert forbidden.isdisjoint(str(payload))


def test_populated_metric_has_provider_identity_and_unavailable_slots_are_explicit() -> None:
    envelope = build_difficulty_analysis(level())
    provenance = dict(envelope.metric_provenance)
    availability = dict(envelope.component_availability)
    assert provenance["move_count"].provider_id == "solver-evidence"
    assert availability["dependency_depth"] is AnalysisDisposition.UNAVAILABLE
