from __future__ import annotations

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.difficulty_analysis import DependencyDepthResult, populate_dependency_depth, unavailable_dependency_result
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, LevelMetricsError, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


def evidence() -> SolverEvidenceReport:
    policy = BaselineSearchPolicy()
    result = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, (), "fixture", policy)
    metrics = SolverMetrics((), False, 1, None, 0, 0, (), 0, ())
    budget = SolverBudgetPolicy()
    outcome = BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "fixture", "SOLVED", "fixture")
    return SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, result, metrics, 1.0, budget_policy=budget, budget_result=outcome)


def level() -> LevelMetrics:
    report = evidence()
    return LevelMetrics(LevelIdentity("e" * 64, "lf04-004", 20, 20, 400), AUTHORITY, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, report.digest()), AnalysisDisposition.AVAILABLE)


def result(level_metrics: LevelMetrics, *, disposition: AnalysisDisposition = AnalysisDisposition.AVAILABLE, depth: int | None = 4) -> DependencyDepthResult:
    return DependencyDepthResult(disposition, level_metrics.authority, level_metrics.source_sha256, "f" * 64, level_metrics.evidence_digest, "fixture-dependency-provider", "fixture-v1", depth, "fixture")


def test_explicit_provider_measurement_is_applied() -> None:
    metrics = level()
    updated = populate_dependency_depth(metrics, result(metrics))
    assert updated.metrics == MetricValues(dependency_depth=4)


def test_unavailable_canonical_semantics_remain_absent() -> None:
    metrics = level()
    unavailable = unavailable_dependency_result(metrics, "f" * 64, "canonical dependency semantics are not executable")
    assert unavailable.disposition is AnalysisDisposition.UNAVAILABLE
    assert populate_dependency_depth(metrics, unavailable).metrics is None


def test_path_depth_is_not_accepted_as_dependency_without_provider_result() -> None:
    metrics = level()
    unavailable = unavailable_dependency_result(metrics, "f" * 64, "no dependency provider")
    assert unavailable.dependency_depth is None


def test_authority_source_or_evidence_mismatch_is_rejected() -> None:
    metrics = level()
    candidates = [
        DependencyDepthResult(AnalysisDisposition.AVAILABLE, SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", "0" * 40), metrics.source_sha256, "f" * 64, metrics.evidence_digest, "fixture", "v1", 1, "fixture"),
        DependencyDepthResult(AnalysisDisposition.AVAILABLE, metrics.authority, "1" * 64, "f" * 64, metrics.evidence_digest, "fixture", "v1", 1, "fixture"),
        DependencyDepthResult(AnalysisDisposition.AVAILABLE, metrics.authority, metrics.source_sha256, "f" * 64, "2" * 64, "fixture", "v1", 1, "fixture"),
    ]
    for candidate in candidates:
        with pytest.raises(LevelMetricsError):
            populate_dependency_depth(metrics, candidate)


def test_unknown_or_malformed_measurements_are_rejected() -> None:
    metrics = level()
    with pytest.raises(LevelMetricsError):
        DependencyDepthResult(AnalysisDisposition.AVAILABLE, metrics.authority, metrics.source_sha256, "f" * 64, metrics.evidence_digest, "fixture", "v1", -1, "fixture")
    with pytest.raises(LevelMetricsError):
        DependencyDepthResult(AnalysisDisposition.UNAVAILABLE, metrics.authority, metrics.source_sha256, "f" * 64, metrics.evidence_digest, "fixture", "v1", 0, "fixture")
