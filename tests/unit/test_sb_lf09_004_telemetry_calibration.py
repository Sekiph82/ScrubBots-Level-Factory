from __future__ import annotations

from dataclasses import replace

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.difficulty_analysis import build_difficulty_analysis, calculate_challenge_score, map_challenge_score
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics
from scrubbots_pixel_factory.telemetry_calibration import (
    AGGREGATE_CALIBRATION_RETENTION_DAYS,
    MINIMUM_VALID_SESSIONS,
    RAW_TELEMETRY_RETENTION_DAYS,
    AggregateRetentionRecord,
    CalibrationDisposition,
    M04DifficultyBinding,
    TelemetryAggregate,
    TelemetryCalibrationError,
    TelemetryEvent,
    TelemetryEventKind,
    TelemetrySession,
    build_calibration_report,
)


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def m04_binding() -> M04DifficultyBinding:
    policy = BaselineSearchPolicy()
    search = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, (), "fixture", policy)
    budget = SolverBudgetPolicy()
    evidence = SolverEvidenceReport(
        SearchExecutionDisposition.AVAILABLE,
        search,
        SolverMetrics((), False, 1, None, 0, 0, (), 0, ()),
        1.0,
        budget_policy=budget,
        budget_result=BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "fixture", "SOLVED", "fixture"),
    )
    metrics = MetricValues(move_count=8, states_visited=16, dead_ends=2, branching=1.5, forced_moves=3)
    level = LevelMetrics(LevelIdentity("c" * 64, "lf09-004", 20, 20, 400), AUTHORITY, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, evidence.digest()), AnalysisDisposition.AVAILABLE, metrics=metrics)
    score = calculate_challenge_score(level)
    lane = map_challenge_score(score)
    return M04DifficultyBinding.from_results(build_difficulty_analysis(level, score, lane), score, lane)


def session(binding: M04DifficultyBinding, number: int, *, recorded_at: str = "2026-09-30T00:00:00Z", level_id: str = "level-a", cohort: str = "cohort-v1", outcome: TelemetryEventKind = TelemetryEventKind.WIN) -> TelemetrySession:
    return TelemetrySession(
        f"anon-session-{number:04d}",
        level_id,
        "candidate-a",
        "build-1",
        recorded_at,
        (TelemetryEvent(TelemetryEventKind.LEVEL_START, "2026-09-30T00:00:00Z"), TelemetryEvent(TelemetryEventKind.RESTART, "2026-09-30T00:01:00Z") if number % 2 else TelemetryEvent(TelemetryEventKind.BOOSTER_USAGE, "2026-09-30T00:01:00Z"), TelemetryEvent(outcome, "2026-09-30T00:02:00Z")),
        1 + number % 3,
        5 + number,
        120000 + number,
        binding.challenge_score,
        binding.challenge_score_policy_version,
        binding.lane,
        binding.lane_mapping_policy_version,
        cohort,
        binding.analysis_digest,
        binding.challenge_score_digest,
        binding.lane_mapping_digest,
    )


def test_closed_session_schema_round_trips_and_rejects_unknown_or_pii_fields() -> None:
    binding = m04_binding()
    value = session(binding, 1)
    restored = TelemetrySession.from_dict(value.canonical_dict())
    assert value.canonical_bytes() == restored.canonical_bytes()
    for field in ("email", "player_name", "raw_ip", "free_text", "credentials", "unknown"):
        payload = {**value.canonical_dict(), field: "forbidden"}
        with pytest.raises(TelemetryCalibrationError):
            TelemetrySession.from_dict(payload)


def test_malformed_pseudonymous_id_and_invalid_event_are_rejected() -> None:
    binding = m04_binding()
    with pytest.raises(TelemetryCalibrationError):
        replace(session(binding, 1), session_id="bad")
    with pytest.raises(TelemetryCalibrationError):
        TelemetryEvent("NOT_APPROVED", "2026-09-30T00:00:00Z")


def test_unavailable_analytics_preserves_exact_m04_binding() -> None:
    binding = m04_binding()
    report = build_calibration_report(binding, None, as_of="2026-10-01T00:00:00Z")
    assert report.disposition is CalibrationDisposition.UNAVAILABLE
    assert report.m04_binding == binding
    assert report.aggregate is None and report.valid_session_count == 0


def test_below_threshold_is_insufficient_and_exactly_100_is_advisory_ready() -> None:
    binding = m04_binding()
    below = build_calibration_report(binding, tuple(session(binding, index) for index in range(MINIMUM_VALID_SESSIONS - 1)), as_of="2026-10-01T00:00:00Z")
    ready = build_calibration_report(binding, tuple(session(binding, index) for index in range(MINIMUM_VALID_SESSIONS)), as_of="2026-10-01T00:00:00Z")
    assert below.disposition is CalibrationDisposition.INSUFFICIENT_DATA
    assert below.valid_session_count == MINIMUM_VALID_SESSIONS - 1
    assert ready.disposition is CalibrationDisposition.ADVISORY_READY
    assert ready.valid_session_count == MINIMUM_VALID_SESSIONS
    assert ready.advisory_review == "REVIEW_ADVISORY_DIVERGENCE"


def test_duplicates_and_expired_raw_records_do_not_inflate_sample() -> None:
    binding = m04_binding()
    current = session(binding, 1)
    expired = session(binding, 2, recorded_at="2026-06-30T00:00:00Z")
    report = build_calibration_report(binding, (current, current, expired), as_of="2026-10-01T00:00:00Z")
    assert report.disposition is CalibrationDisposition.INSUFFICIENT_DATA
    assert report.valid_session_count == 1
    assert RAW_TELEMETRY_RETENTION_DAYS == 90


def test_scope_or_m04_mismatch_is_inconclusive_not_calibrated() -> None:
    binding = m04_binding()
    report = build_calibration_report(binding, (session(binding, 1, level_id="other-level"),), as_of="2026-10-01T00:00:00Z", level_id="level-a")
    assert report.disposition is CalibrationDisposition.INCONCLUSIVE
    wrong_binding = replace(binding, challenge_score_digest="d" * 64)
    report = build_calibration_report(binding, (session(wrong_binding, 1),), as_of="2026-10-01T00:00:00Z")
    assert report.disposition is CalibrationDisposition.INCONCLUSIVE


def test_aggregate_and_report_are_tamper_evident_and_deterministic() -> None:
    binding = m04_binding()
    sessions = tuple(session(binding, index) for index in range(MINIMUM_VALID_SESSIONS))
    first = build_calibration_report(binding, sessions, as_of="2026-10-01T00:00:00Z")
    second = build_calibration_report(binding, tuple(reversed(sessions)), as_of="2026-10-01T00:00:00Z")
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.aggregate is not None
    with pytest.raises(TelemetryCalibrationError):
        replace(first.aggregate, win_rate=0.0)
    with pytest.raises(TelemetryCalibrationError):
        replace(first, reason="tampered")


def test_aggregate_retention_is_explicit_and_capped_at_12_months() -> None:
    aggregate = TelemetryAggregate("level-a", "candidate-a", "build-1", "cohort-v1", 0, 0.0, 0.0, 0.0, None, 0.0, 0.0, 0.0, (), (), 0.0, 0.0, 0.0)
    current = AggregateRetentionRecord(aggregate, "2026-01-01T00:00:00Z")
    assert current.is_active("2026-10-01T00:00:00Z")
    assert not AggregateRetentionRecord(aggregate, "2024-12-31T00:00:00Z").is_active("2026-10-01T00:00:00Z")
    assert current.retention_days == AGGREGATE_CALIBRATION_RETENTION_DAYS
    with pytest.raises(TelemetryCalibrationError):
        AggregateRetentionRecord(aggregate, "2026-01-01T00:00:00Z", AGGREGATE_CALIBRATION_RETENTION_DAYS + 1)
