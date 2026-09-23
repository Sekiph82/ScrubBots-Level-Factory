from __future__ import annotations

from copy import deepcopy

import pytest

from scrubbots_pixel_factory.compact_solver_state import (
    CANONICAL_PROOF_STATE_AUTHORITY_SHA,
    LevelIdentity,
    SolverStateAuthority,
)
from scrubbots_pixel_factory.contracts.difficulty import Difficulty
from scrubbots_pixel_factory.level_metrics import (
    AnalysisDisposition,
    DifficultyMetadata,
    LEVEL_METRICS_SCHEMA,
    LEVEL_METRICS_VERSION,
    LevelMetrics,
    LevelMetricsError,
    MetricValues,
    SolverEvidenceIdentity,
)
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION


def authority() -> SolverStateAuthority:
    return SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def level() -> LevelIdentity:
    return LevelIdentity("a" * 64, "metrics-level", 20, 21, 420)


def evidence() -> SolverEvidenceIdentity:
    return SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, "b" * 64)


def available(**kwargs: object) -> LevelMetrics:
    return LevelMetrics(level(), authority(), evidence(), AnalysisDisposition.AVAILABLE, **kwargs)


def test_v1_is_frozen_provenance_bound_and_deterministic() -> None:
    metrics = available(metrics=MetricValues(states_visited=12, branching=1.5))
    restored = LevelMetrics.from_dict(metrics.canonical_dict())

    assert metrics.canonical_dict()["schema"] == LEVEL_METRICS_SCHEMA
    assert metrics.canonical_dict()["version"] == LEVEL_METRICS_VERSION
    assert metrics.canonical_bytes() == restored.canonical_bytes()
    assert metrics.digest() == restored.digest()
    assert metrics.source_sha256 == level().source_sha256
    assert metrics.evidence_digest == "b" * 64
    assert metrics.authority == authority()
    with pytest.raises(AttributeError):
        metrics.disposition = AnalysisDisposition.ERROR  # type: ignore[misc]
    with pytest.raises(LevelMetricsError):
        LevelMetrics(
            level(),
            SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", "0" * 40),
            evidence(),
            AnalysisDisposition.AVAILABLE,
        )


def test_available_without_metric_values_is_legal_and_missing_is_not_zero() -> None:
    metrics = available()
    assert metrics.metrics is None
    assert metrics.measurement_content() == {}
    assert metrics.canonical_dict()["metrics"] is None


@pytest.mark.parametrize("disposition", tuple(d for d in AnalysisDisposition if d is not AnalysisDisposition.AVAILABLE))
def test_non_available_dispositions_preserve_truth_without_measurements(disposition: AnalysisDisposition) -> None:
    envelope = LevelMetrics(level(), authority(), evidence(), disposition, reason="accepted upstream evidence is not usable")
    assert envelope.metrics is None
    with pytest.raises(LevelMetricsError):
        LevelMetrics(level(), authority(), evidence(), disposition, metrics=MetricValues(states_visited=1), reason="not available")


def test_closed_parsing_rejects_unknown_fields_versions_hashes_and_metric_ids() -> None:
    payload = available(metrics=MetricValues(solution_depth=4)).canonical_dict()
    malformed = [
        {**payload, "unexpected": True},
        {**payload, "version": 99},
        {**payload, "solver_evidence": {**payload["solver_evidence"], "digest": "not-a-sha"}},  # type: ignore[index]
        {**payload, "metrics": {"unknown_metric": 1}},
        {**payload, "metrics_contract": {"schema": "unknown", "version": 1}},
    ]
    for candidate in malformed:
        with pytest.raises((LevelMetricsError, ValueError)):
            LevelMetrics.from_dict(candidate)


def test_nan_and_infinity_are_rejected() -> None:
    with pytest.raises(LevelMetricsError):
        MetricValues(volatility=float("nan"))
    with pytest.raises(LevelMetricsError):
        MetricValues(solution_entropy=float("inf"))


def test_mutable_input_is_copied_and_cannot_alias_accepted_object() -> None:
    payload = available(metrics=MetricValues(states_visited=7)).canonical_dict()
    copied = deepcopy(payload)
    accepted = LevelMetrics.from_dict(copied)
    copied["metrics"]["states_visited"] = 99  # type: ignore[index]
    copied["level"]["level_id"] = "mutated"  # type: ignore[index]
    assert accepted.metrics is not None and accepted.metrics.states_visited == 7
    assert accepted.level.level_id == "metrics-level"


def test_difficulty_metadata_is_descriptive_and_does_not_change_measurements() -> None:
    easy = available(
        metrics=MetricValues(states_visited=12, branching=1.5),
        difficulty_metadata=DifficultyMetadata(Difficulty.EASY, width=20, height=59, used_color_count=3),
    )
    hard = available(
        metrics=MetricValues(states_visited=12, branching=1.5),
        difficulty_metadata=DifficultyMetadata(Difficulty.VERY_HARD, width=59, height=20, used_color_count=12),
    )
    assert easy.measurement_content() == hard.measurement_content()
    assert easy.solver_evidence == hard.solver_evidence
    assert easy.canonical_dict()["difficulty_metadata"] != hard.canonical_dict()["difficulty_metadata"]


def test_dimensions_and_used_colors_are_not_difficulty_inference() -> None:
    metadata = DifficultyMetadata(Difficulty.EASY, width=59, height=20, used_color_count=12)
    assert metadata.difficulty is Difficulty.EASY
    assert metadata.width == 59 and metadata.height == 20 and metadata.used_color_count == 12
    assert DifficultyMetadata(Difficulty.VERY_HARD, width=20, height=59, used_color_count=3)


def test_operational_and_runtime_values_are_not_canonical_fields() -> None:
    canonical = available(metrics=MetricValues(states_visited=1)).canonical_dict()
    forbidden = {
        "elapsed_seconds",
        "timestamp",
        "wall_clock",
        "timeout_seconds",
        "timeout_occurred",
        "absolute_path",
        "process_id",
        "object_id",
        "ui_state",
    }
    assert forbidden.isdisjoint(canonical)
    assert forbidden.isdisjoint(canonical["metrics"])
