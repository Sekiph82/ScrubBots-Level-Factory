from __future__ import annotations

import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
import subprocess

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.contracts.difficulty import Difficulty
from scrubbots_pixel_factory.difficulty_analysis import (
    CalibrationDataset,
    ChallengeScoreResult,
    EvidenceDisposition,
    LaneClass,
    MetricEvidence,
    MetricProviderIdentity,
    ScoreComponent,
    SlotSnapshot,
    VolatilitySnapshot,
    bait_deadlock_from_children,
    bind_verified_metric_producer,
    build_difficulty_analysis,
    calculate_challenge_score,
    challenge_score_fixture,
    disabled_calibration_plan,
    map_challenge_score,
    populate_bait_deadlock,
    populate_dependency_depth,
    populate_search_complexity_metrics,
    populate_solution_depth_and_move_count,
    populate_slot_pressure,
    populate_volatility,
    slot_pressure_from_snapshots,
    unavailable_dependency_result,
    volatility_from_snapshots,
)
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, LevelMetricsError, MetricId, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.legal_move_provider import LegalMove
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures"
AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def corpus() -> dict[str, object]:
    return json.loads((FIXTURES / "sb_lf04_m04_regression_v1.json").read_text(encoding="utf-8"))


def report_for(payload: dict[str, object]) -> SolverEvidenceReport:
    path = tuple(LegalMove(column) for column in payload.get("path_columns", []))
    policy = BaselineSearchPolicy()
    search = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, path, "corpus fixture", policy)
    branch_counts = tuple(payload.get("branch_counts", []))
    metrics = SolverMetrics(
        (),
        False,
        int(payload.get("visited_count", 1)),
        None,
        int(payload.get("dead_end_count", 0)),
        len(path),
        branch_counts,
        0,
        tuple(move.canonical_dict() for move in path),
    )
    budget = SolverBudgetPolicy()
    budget_result = BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "corpus", "SOLVED", "corpus")
    return SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, search, metrics, 1.0, budget_policy=budget, budget_result=budget_result)


def level(report: SolverEvidenceReport | None = None, metrics: MetricValues | None = None) -> LevelMetrics:
    report = report or report_for({})
    return LevelMetrics(
        LevelIdentity("f" * 64, "lf04-012", 20, 20, 400),
        AUTHORITY,
        SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, report.digest()),
        AnalysisDisposition.AVAILABLE,
        metrics=metrics,
    )


def test_checksummed_corpus_is_versioned_and_covers_every_child() -> None:
    payload = corpus()
    assert payload["schema"] == "scrubbots-m04-regression-corpus" and payload["version"] == 1
    expected = hashlib.sha256(canonical({"schema": payload["schema"], "version": payload["version"], "cases": payload["cases"]})).hexdigest()
    assert payload["corpus_sha256"] == expected
    cases = payload["cases"]
    assert [case["id"] for case in cases] == [f"SB-LF04-{index:03d}" for index in range(1, 12)]
    assert all(set(case) == {"id", "contract", "payload", "mutation", "expected"} for case in cases)
    assert all(case["payload"]["fixture_version"] == 1 for case in cases)


def test_corpus_payloads_drive_all_m04_behaviors() -> None:
    cases = {case["id"]: case for case in corpus()["cases"]}

    case = cases["SB-LF04-001"]
    level_data = json.loads((FIXTURES / case["payload"]["level_data"]).read_text(encoding="utf-8"))
    assert level_data["version"] == case["payload"]["fixture_version"] and level().disposition is AnalysisDisposition.AVAILABLE

    case = cases["SB-LF04-002"]
    report = report_for(case["payload"])
    updated = populate_solution_depth_and_move_count(level(report), report)
    assert updated.metrics.solution_depth == case["expected"]["solution_depth"] and updated.metrics.move_count == case["expected"]["move_count"]

    case = cases["SB-LF04-003"]
    report = report_for(case["payload"])
    updated = populate_search_complexity_metrics(level(report), report)
    assert updated.metrics.states_visited == case["expected"]["states_visited"]
    assert updated.metrics.dead_ends == case["expected"]["dead_ends"]
    assert updated.metrics.branching == case["expected"]["branching"]
    assert updated.metrics.forced_moves == case["expected"]["forced_moves"]

    case = cases["SB-LF04-004"]
    metrics = level()
    unavailable = unavailable_dependency_result(metrics, case["payload"]["state_digest"], "corpus provider unavailable")
    assert unavailable.disposition.value == case["expected"]["disposition"] and populate_dependency_depth(metrics, unavailable).metrics is None
    with pytest.raises(LevelMetricsError):
        MetricEvidence(EvidenceDisposition.VERIFIED_CANONICAL, AUTHORITY, metrics.source_sha256, "0" * 64, metrics.solver_evidence.digest, "canonical-dependency-semantics", "CANONICAL_DEPENDENCY_SEMANTICS_V1", "1" * 64)

    case = cases["SB-LF04-005"]
    metrics = level()
    snapshots = tuple(SlotSnapshot(*snapshot) for snapshot in case["payload"]["snapshots"])
    result = slot_pressure_from_snapshots(metrics, case["payload"]["state_digest"], snapshots)
    assert result.slot_pressure == case["expected"]["slot_pressure"]
    assert result.evidence.disposition is EvidenceDisposition.FIXTURE
    with pytest.raises(LevelMetricsError):
        populate_slot_pressure(metrics, result)

    case = cases["SB-LF04-006"]
    metrics = level()
    children = tuple(SolverOutcomeDisposition[name] for name in case["payload"]["child_dispositions"])
    result = bait_deadlock_from_children(metrics, case["payload"]["state_digest"], children)
    assert result.bait_deadlock == case["expected"]["exact_ratio"]
    assert result.evidence.disposition is EvidenceDisposition.FIXTURE
    inconclusive = bait_deadlock_from_children(metrics, case["payload"]["state_digest"], tuple(SolverOutcomeDisposition[name] for name in case["payload"]["inconclusive_children"]))
    assert inconclusive.disposition.value == case["expected"]["inconclusive_disposition"]
    with pytest.raises(LevelMetricsError):
        populate_bait_deadlock(metrics, result)

    case = cases["SB-LF04-007"]
    metrics = level()
    result = volatility_from_snapshots(metrics, case["payload"]["state_digest"], tuple(VolatilitySnapshot(*snapshot) for snapshot in case["payload"]["snapshots"]))
    assert result.volatility == case["expected"]["volatility"]
    assert result.evidence.disposition is EvidenceDisposition.FIXTURE
    with pytest.raises(LevelMetricsError):
        populate_volatility(metrics, result)

    case = cases["SB-LF04-008"]
    score = calculate_challenge_score(level(metrics=MetricValues(**case["payload"]["metrics"])))
    assert score.score == case["expected"]["score"]
    with pytest.raises(LevelMetricsError):
        replace(score, score=case["payload"]["invalid_result"]["score"])

    case = cases["SB-LF04-009"]
    for threshold in case["payload"]["thresholds"]:
        assert map_challenge_score(challenge_score_fixture(threshold)).lane is not None
    valid = map_challenge_score(challenge_score_fixture(50.0), Difficulty.HARD)
    with pytest.raises(LevelMetricsError):
        replace(valid, lane=LaneClass[case["payload"]["invalid_lane"]])
    with pytest.raises(LevelMetricsError):
        replace(valid, requested_class=Difficulty.EASY, comparison=case["payload"]["invalid_comparison"])

    case = cases["SB-LF04-010"]
    metrics = level(metrics=MetricValues(move_count=2, states_visited=3, dead_ends=1, branching=1.0, forced_moves=1, dependency_depth=4))
    with pytest.raises(LevelMetricsError):
        build_difficulty_analysis(metrics)
    with pytest.raises(LevelMetricsError):
        build_difficulty_analysis(metrics, metric_provenance={case["payload"]["unknown_metric"]: MetricProviderIdentity("fixture", "v1")})
    provider = MetricProviderIdentity(case["payload"]["optional_provider"]["provider_id"], case["payload"]["optional_provider"]["provider_version"])
    with pytest.raises(LevelMetricsError):
        build_difficulty_analysis(metrics, metric_provenance={case["payload"]["optional_metric"]: provider})
    with pytest.raises(LevelMetricsError):
        bind_verified_metric_producer(MetricId.DEPENDENCY_DEPTH, unavailable_dependency_result(metrics, "4" * 64, "fixture unavailable"), metrics)

    case = cases["SB-LF04-011"]
    plan = disabled_calibration_plan(CalibrationDataset("DIFFICULTY_V1", case["payload"]["cohort_label"], case["payload"]["completion_count"], case["payload"]["failure_count"], case["payload"]["move_count_sum"], case["payload"]["sample_count"], case["payload"]["minimum_sample_count"]))
    assert plan.state == case["expected"]["state"] and not plan.network_enabled and not plan.collection_enabled


def test_regression_analysis_preserves_level_data_and_logical_art_bytes() -> None:
    paths = [FIXTURES / "level_data_v1.json", FIXTURES / "logical_art_v1.json", FIXTURES / "lf03_solver_regression_v1.json"]
    before = {path: (path.read_bytes(), hashlib.sha256(path.read_bytes()).hexdigest()) for path in paths}
    metrics = level(metrics=MetricValues(move_count=0, states_visited=0, dead_ends=0, branching=0.0, forced_moves=0))
    score = calculate_challenge_score(metrics)
    lane = map_challenge_score(score)
    build_difficulty_analysis(metrics, score, lane)
    after = {path: (path.read_bytes(), hashlib.sha256(path.read_bytes()).hexdigest()) for path in paths}
    assert after == before


def test_canonical_checkout_non_mutation_is_capability_gated() -> None:
    configured = os.environ.get("SCRUBBOTS_CANONICAL_CHECKOUT")
    if not configured:
        pytest.skip("canonical ScrubBots checkout capability was not supplied; no bridge was exercised")
    checkout = Path(configured)
    if not checkout.is_dir():
        pytest.fail("configured canonical checkout does not exist")
    source = checkout / AUTHORITY.proof_state_source_path
    if not source.is_file():
        pytest.fail("configured canonical checkout lacks the locked ProofState source")
    before_status = subprocess.run(["git", "-C", str(checkout), "status", "--porcelain=v1"], check=True, capture_output=True, text=True).stdout
    before_bytes = source.read_bytes()
    before_sha = hashlib.sha256(before_bytes).hexdigest()
    after_status = subprocess.run(["git", "-C", str(checkout), "status", "--porcelain=v1"], check=True, capture_output=True, text=True).stdout
    after_bytes = source.read_bytes()
    assert after_status == before_status and after_bytes == before_bytes and hashlib.sha256(after_bytes).hexdigest() == before_sha
