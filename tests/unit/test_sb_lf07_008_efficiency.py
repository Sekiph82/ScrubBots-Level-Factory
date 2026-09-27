from __future__ import annotations

import pytest

from scrubbots_pixel_factory import AttemptBudget, EfficiencyCounters, EfficiencyWorkload, GeneratorRouter, GenerationRequest, MutationContractError, MutationAttemptRouteEvidence, RegenerationRouteEvidence, TrustedAccountingEvidence
from scrubbots_pixel_factory.mutation_efficiency import compare_efficiency_from_authentic_routes
from scrubbots_pixel_factory.semantic.qualification.models import CostUsageRecord
from test_sb_lf07_007_attempts import _fixture, _run


def test_full_workload_identity_includes_configuration_and_is_not_seed_only() -> None:
    parent, request, mutation, candidate, target = _fixture()
    report = _run(parent, request, mutation, candidate, target)
    route = MutationAttemptRouteEvidence.from_attempt_report(report)
    assert route.workload.availability == "UNAVAILABLE"
    first = GeneratorRouter().generate(GenerationRequest("EASY", request.seed, "MASK", width=20, height=20))
    second = GeneratorRouter().generate(GenerationRequest("EASY", request.seed, "MASK", width=21, height=21))
    left = RegenerationRouteEvidence.from_generation_result(first, target=target, budget=report.budget)
    right = RegenerationRouteEvidence.from_generation_result(second, target=target, budget=report.budget)
    assert left.config_digest != right.config_digest
    comparison = compare_efficiency_from_authentic_routes(route, left)
    assert comparison.disposition == "UNAVAILABLE"


def test_mutation_and_regeneration_can_match_on_one_exact_workload_identity() -> None:
    parent, request, mutation, candidate, target = _fixture()
    generation_request = GenerationRequest("EASY", request.seed, "MASK", width=20, height=20)
    report = _run(parent, request, mutation, candidate, target, generation_request=generation_request)
    mutation_route = MutationAttemptRouteEvidence.from_attempt_report(report)
    result = GeneratorRouter().generate(generation_request)
    regeneration_route = RegenerationRouteEvidence.from_generation_result(result, target=target, budget=report.budget)
    comparison = compare_efficiency_from_authentic_routes(mutation_route, regeneration_route)
    assert mutation_route.workload == regeneration_route.workload
    assert comparison.disposition == "MATCHED"
    assert comparison.mutation_cost is None
    assert comparison.regenerate_cost is None


def test_same_seed_different_generation_configuration_is_not_matched() -> None:
    parent, request, mutation, candidate, target = _fixture()
    base = GenerationRequest("EASY", request.seed, "MASK", width=20, height=20)
    variants = (
        GenerationRequest("EASY", request.seed, "MASK", width=21, height=21),
        GenerationRequest("EASY", request.seed, "RULES", width=20, height=20),
        GenerationRequest("EASY", request.seed, "MASK", width=20, height=20, style="ROBOT"),
        GenerationRequest("EASY", request.seed, "MASK", width=20, height=20, theme="NIGHT"),
        GenerationRequest("EASY", request.seed, "MASK", width=20, height=20, palette_subset=("C01", "C02", "C03")),
        GenerationRequest("EASY", request.seed, "MASK", width=20, height=20, generator_options={"namespace": "r05", "version": 1, "values": {"variant": "different"}}),
    )
    report = _run(parent, request, mutation, candidate, target, generation_request=base)
    mutation_route = MutationAttemptRouteEvidence.from_attempt_report(report)
    for variant in variants:
        result = GeneratorRouter().generate(variant)
        regeneration_route = RegenerationRouteEvidence.from_generation_result(result, target=target, budget=report.budget)
        assert compare_efficiency_from_authentic_routes(mutation_route, regeneration_route).disposition == "UNAVAILABLE"


def test_regeneration_success_without_the_same_accepted_chain_is_inconclusive() -> None:
    parent, request, mutation, candidate, target = _fixture()
    report = _run(parent, request, mutation, candidate, target)
    result = GeneratorRouter().generate(GenerationRequest("EASY", request.seed, "MASK", width=20, height=20))
    route = RegenerationRouteEvidence.from_generation_result(result, target=target, budget=report.budget)
    assert route.counters.produced == 1
    assert route.counters.accepted == 0
    assert route.counters.inconclusive == 1


def test_efficiency_accounting_is_unavailable_and_caller_identity_cannot_be_supplied() -> None:
    with pytest.raises(MutationContractError):
        TrustedAccountingEvidence.from_cost_usage(CostUsageRecord(provider_attempt_count=1))
    with pytest.raises(MutationContractError):
        EfficiencyCounters(-1, 0, 0, 0, 0, 0)
    with pytest.raises(MutationContractError):
        EfficiencyWorkload("a" * 64, "b" * 64, "c" * 64, "d" * 64, "FORGED")
