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
