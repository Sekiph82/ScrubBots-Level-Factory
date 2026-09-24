from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.difficulty_analysis import (
    CalibrationDataset,
    AnalysisDisposition,
    build_difficulty_analysis,
    calculate_challenge_score,
    disabled_calibration_plan,
    map_challenge_score,
)
from scrubbots_pixel_factory.level_metrics import LevelMetrics, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def level() -> LevelMetrics:
    policy = BaselineSearchPolicy()
    search = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, (), "fixture", policy)
    budget = SolverBudgetPolicy()
    evidence = SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, search, SolverMetrics((), False, 1, None, 0, 0, (), 0, ()), 1.0, budget_policy=budget, budget_result=BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "fixture", "SOLVED", "fixture"))
    return LevelMetrics(LevelIdentity("f" * 64, "lf04-012", 20, 20, 400), AUTHORITY, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, evidence.digest()), AnalysisDisposition.AVAILABLE, metrics=MetricValues(move_count=0, states_visited=0, dead_ends=0, branching=0.0, forced_moves=0))


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def test_checksummed_m04_corpus_covers_every_child() -> None:
    path = ROOT / "tests" / "fixtures" / "sb_lf04_m04_regression_v1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "scrubbots-m04-regression-corpus" and payload["version"] == 1
    expected = hashlib.sha256(canonical({"schema": payload["schema"], "version": payload["version"], "cases": payload["cases"]})).hexdigest()
    assert payload["corpus_sha256"] == expected
    assert [case["id"] for case in payload["cases"]] == ["SB-LF04-001", "SB-LF04-002", "SB-LF04-003", "SB-LF04-004", "SB-LF04-005", "SB-LF04-006", "SB-LF04-007", "SB-LF04-008", "SB-LF04-009", "SB-LF04-010", "SB-LF04-011"]


def test_representative_analysis_preserves_exact_source_fixture_bytes() -> None:
    source = ROOT / "tests" / "fixtures" / "lf03_solver_regression_v1.json"
    before = source.read_bytes()
    before_sha = hashlib.sha256(before).hexdigest()
    metrics = level()
    score = calculate_challenge_score(metrics)
    lane = map_challenge_score(score)
    build_difficulty_analysis(metrics, score, lane)
    disabled_calibration_plan(CalibrationDataset("DIFFICULTY_V1", "future-cohort-a", 2, 0, 1, 2, 2))
    after = source.read_bytes()
    assert after == before and hashlib.sha256(after).hexdigest() == before_sha


def test_regression_outputs_are_deterministic_and_analysis_does_not_mutate_level_metrics() -> None:
    metrics = level()
    before = metrics.canonical_bytes()
    first = calculate_challenge_score(metrics)
    first_lane = map_challenge_score(first)
    second = calculate_challenge_score(metrics)
    second_lane = map_challenge_score(second)
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first_lane.canonical_bytes() == second_lane.canonical_bytes()
    assert metrics.canonical_bytes() == before
