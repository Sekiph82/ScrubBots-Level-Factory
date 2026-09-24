from __future__ import annotations

import math

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.contracts.difficulty import Difficulty
from scrubbots_pixel_factory.difficulty_analysis import CHALLENGE_SCORE_POLICY_VERSION, calculate_challenge_score
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, DifficultyMetadata, LevelMetrics, LevelMetricsError, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def level(metrics: MetricValues, metadata: DifficultyMetadata | None = None) -> LevelMetrics:
    policy = BaselineSearchPolicy()
    search = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, (), "fixture", policy)
    budget = SolverBudgetPolicy()
    evidence = SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, search, SolverMetrics((), False, 1, None, 0, 0, (), 0, ()), 1.0, budget_policy=budget, budget_result=BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "fixture", "SOLVED", "fixture"))
    return LevelMetrics(LevelIdentity("c" * 64, "lf04-008", 20, 20, 400), AUTHORITY, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, evidence.digest()), AnalysisDisposition.AVAILABLE, metrics=metrics, difficulty_metadata=metadata)


def test_fixed_formula_matches_hand_calculated_components() -> None:
    metrics = MetricValues(move_count=4, states_visited=100, dead_ends=20, branching=2.0, forced_moves=10, dependency_depth=99, slot_pressure=1.0)
    result = calculate_challenge_score(level(metrics))
    move = math.log1p(4) / math.log1p(64)
    states = math.log1p(100) / math.log1p(10000)
    expected = 100.0 * (0.25 * move + 0.25 * states + 0.15 * 0.2 + 0.15 * 0.5 + 0.20 * 0.9)
    assert result.policy_version == CHALLENGE_SCORE_POLICY_VERSION
    assert result.score == pytest.approx(expected)
    assert tuple(name for name, _ in result.components) == ("move", "states", "dead_end", "branching", "forced")


def test_bounds_and_zero_state_edge_are_deterministic() -> None:
    metrics = MetricValues(move_count=10**9, states_visited=0, dead_ends=10**9, branching=10**9, forced_moves=10**9)
    result = calculate_challenge_score(level(metrics))
    assert 0.0 <= result.score <= 100.0
    assert result.canonical_bytes() == calculate_challenge_score(level(metrics)).canonical_bytes()


def test_all_five_required_metrics_are_required_and_optional_are_not_inputs() -> None:
    with pytest.raises(LevelMetricsError):
        calculate_challenge_score(level(MetricValues(move_count=1, states_visited=1, dead_ends=0, branching=1.0)))
    base = MetricValues(move_count=1, states_visited=2, dead_ends=0, branching=1.0, forced_moves=1)
    optional = MetricValues(move_count=1, states_visited=2, dead_ends=0, branching=1.0, forced_moves=1, dependency_depth=7, slot_pressure=0.9, bait_deadlock=0.8, volatility=0.7)
    assert calculate_challenge_score(level(base)).score == calculate_challenge_score(level(optional)).score


def test_metadata_does_not_change_score_formula() -> None:
    metrics = MetricValues(move_count=8, states_visited=16, dead_ends=2, branching=1.5, forced_moves=3)
    easy = calculate_challenge_score(level(metrics, DifficultyMetadata(Difficulty.EASY, 20, 59, 3)))
    hard = calculate_challenge_score(level(metrics, DifficultyMetadata(Difficulty.VERY_HARD, 59, 20, 12)))
    assert easy.score == hard.score
    assert easy.source_metrics_digest != hard.source_metrics_digest
