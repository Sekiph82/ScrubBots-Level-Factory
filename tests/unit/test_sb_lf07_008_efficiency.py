from __future__ import annotations

import pytest

from scrubbots_pixel_factory import (
    EfficiencyCounters,
    EfficiencyWorkload,
    GeneratorRouteEvidence,
    MutationContractError,
    compare_efficiency,
    compare_efficiency_from_routes,
    EfficiencyComparison,
    GeneratorRouter,
    GenerationRequest,
    MutationAttemptRouteEvidence,
    RegenerationRouteEvidence,
    TrustedAccountingEvidence,
)
from scrubbots_pixel_factory.mutation_efficiency import compare_efficiency_from_authentic_routes
from scrubbots_pixel_factory.semantic.qualification.models import CostUsageRecord
from test_sb_lf07_007_attempts import _authentic_runner_fixture, _run_authentic


def _workload() -> EfficiencyWorkload:
    return EfficiencyWorkload("a" * 64, "b" * 64, "c" * 64, "d" * 64)


def test_matched_efficiency_comparison_is_reproducible_and_telemetry_free() -> None:
    workload = _workload()
    mutation = EfficiencyCounters(5, 5, 2, 1, 2, 90)
    regenerate = EfficiencyCounters(5, 5, 1, 2, 2, 110)
    first = compare_efficiency(workload, workload, mutation, regenerate, mutation_cost={"trusted": True, "credits": 2}, regenerate_cost={"trusted": False, "credits": 999}, telemetry={"wall_clock_ms": 999999, "machine": "local"})
    second = compare_efficiency(workload, workload, mutation, regenerate, mutation_cost={"trusted": True, "credits": 2}, regenerate_cost={"trusted": False, "credits": 999}, telemetry={"wall_clock_ms": 1})
    assert first.digest() == second.digest()
    assert first.canonical_dict()["mutation_cost"] == {"credits": 2}
    assert first.canonical_dict()["regenerate_cost"] is None
    assert "wall_clock_ms" not in str(first.canonical_dict())


def test_mismatched_target_or_budget_is_rejected() -> None:
    left = _workload()
    right = EfficiencyWorkload("e" * 64, left.seed_config_digest, left.validation_policy_digest, left.budget_digest)
    with pytest.raises(MutationContractError):
        compare_efficiency(left, right, EfficiencyCounters(1, 1, 0, 0, 1, 1), EfficiencyCounters(1, 1, 0, 0, 1, 1))


def test_zero_acceptance_and_inconclusive_counts_remain_truthful() -> None:
    comparison = compare_efficiency(_workload(), _workload(), EfficiencyCounters(2, 2, 0, 2, 0, 10), EfficiencyCounters(2, 2, 0, 1, 1, 20))
    assert comparison.mutation.accepted == 0
    assert comparison.mutation.inconclusive == 2
    assert comparison.regenerate.rejected == 1


def test_negative_or_non_integer_counters_fail_closed() -> None:
    with pytest.raises(MutationContractError):
        EfficiencyCounters(-1, 0, 0, 0, 0, 0)
    with pytest.raises(MutationContractError):
        EfficiencyCounters(1.0, 0, 0, 0, 0, 0)  # type: ignore[arg-type]


def test_route_evidence_compares_real_matched_workload_and_digests() -> None:
    left = GeneratorRouteEvidence("mutation", "a" * 64, 5, 2, 1, 90, "b" * 64)
    right = GeneratorRouteEvidence("regenerate", "a" * 64, 5, 1, 2, 110, "c" * 64)
    comparison = compare_efficiency_from_routes(left, right)
    assert comparison.mutation.accepted == 2
    assert comparison.regenerate.rejected == 2


def test_route_evidence_rejects_unmatched_workload_identity() -> None:
    left = GeneratorRouteEvidence("mutation", "a" * 64, 1, 1, 0, 1, "b" * 64)
    right = GeneratorRouteEvidence("regenerate", "c" * 64, 1, 1, 0, 1, "d" * 64)
    with pytest.raises(MutationContractError):
        compare_efficiency_from_routes(left, right)


def test_real_generation_result_and_accepted_accounting_are_required_for_regeneration_route() -> None:
    parent, request, mutation, candidate, target, _ = _authentic_runner_fixture()
    report = _run_authentic(parent, request, mutation, candidate, target, budget=1)
    mutation_route = MutationAttemptRouteEvidence.from_attempt_report(report)
    result = GeneratorRouter().generate(GenerationRequest("EASY", request.seed, "MASK", width=20, height=20))
    route = RegenerationRouteEvidence.from_generation_result(result, target=target, budget=report.budget)
    assert route.counters.produced == 1
    assert route.accounting is None
    comparison = compare_efficiency_from_authentic_routes(mutation_route, route)
    assert comparison.regenerate_cost is None
    with pytest.raises(MutationContractError):
        TrustedAccountingEvidence.from_cost_usage(CostUsageRecord(provider_attempt_count=1))
    with pytest.raises(MutationContractError):
        RegenerationRouteEvidence.from_generation_result(object(), target=target, budget=report.budget, config_digest="e" * 64)  # type: ignore[arg-type]


def test_actual_route_rejects_forged_workload_and_config_identity() -> None:
    parent, request, mutation, candidate, target, _ = _authentic_runner_fixture()
    report = _run_authentic(parent, request, mutation, candidate, target, budget=1)
    actual = MutationAttemptRouteEvidence.from_attempt_report(report)
    forged = EfficiencyWorkload("f" * 64, actual.workload.seed_config_digest, actual.workload.validation_policy_digest, actual.workload.budget_digest)
    with pytest.raises(MutationContractError):
        MutationAttemptRouteEvidence.from_attempt_report(report, forged)
    result = GeneratorRouter().generate(GenerationRequest("EASY", request.seed, "MASK", width=20, height=20))
    with pytest.raises(MutationContractError):
        RegenerationRouteEvidence.from_generation_result(result, target=target, budget=report.budget, config_digest="e" * 64)


def test_mutation_route_rejects_caller_counter_dto_and_requires_attempt_report() -> None:
    with pytest.raises(MutationContractError):
        MutationAttemptRouteEvidence.from_attempt_report(object(), _workload())  # type: ignore[arg-type]
