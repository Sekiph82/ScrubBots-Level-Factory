from __future__ import annotations

from scrubbots_pixel_factory.core.request import LegacyGenerationRequest as _LegacyGenerationRequest  # explicit legacy/research fixture

from dataclasses import replace

import pytest

from scrubbots_pixel_factory import AttemptBudget, EfficiencyCounters, EfficiencyWorkload, GeneratorRouter, GenerationRequest, MutationCandidate, MutationContractError, MutationAttemptRouteEvidence, RegenerationRouteEvidence, TrustedAccountingEvidence
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
    generation_request = GenerationRequest("EASY", 41, "MASK", width=20, height=20)
    parent, request, mutation, candidate, target = _fixture(generation_request)
    report = _run(parent, request, mutation, candidate, target, generation_request=generation_request)
    mutation_route = MutationAttemptRouteEvidence.from_attempt_report(report)
    result = GeneratorRouter().generate(generation_request)
    regeneration_route = RegenerationRouteEvidence.from_generation_result(result, target=target, budget=report.budget)
    comparison = compare_efficiency_from_authentic_routes(mutation_route, regeneration_route)
    assert mutation_route.workload == regeneration_route.workload
    assert comparison.disposition == "MATCHED"
    assert comparison.mutation_cost is None
    assert comparison.regenerate_cost is None


def test_mutation_seed_a_cannot_match_workload_seed_b() -> None:
    aligned = GenerationRequest("EASY", 41, "MASK", width=20, height=20)
    parent, request, mutation, candidate, target = _fixture(aligned)
    workload_seed_b = GenerationRequest("EASY", 42, "MASK", width=20, height=20)
    report = _run(parent, request, mutation, candidate, target, generation_request=workload_seed_b)
    mutation_route = MutationAttemptRouteEvidence.from_attempt_report(report)
    regeneration_route = RegenerationRouteEvidence.from_generation_result(GeneratorRouter().generate(workload_seed_b), target=target, budget=report.budget)
    comparison = compare_efficiency_from_authentic_routes(mutation_route, regeneration_route)
    assert report.disposition.value == "ERROR"
    assert mutation_route.workload.availability == "UNAVAILABLE"
    assert comparison.disposition != "MATCHED"


def test_same_seed_parent_bound_configuration_digest_mismatch_fails_closed() -> None:
    aligned = GenerationRequest("EASY", 41, "MASK", width=20, height=20)
    parent, request, mutation, candidate, target = _fixture(aligned)
    wrong_config = GenerationRequest("EASY", 41, "MASK", width=21, height=21)
    report = _run(parent, request, mutation, candidate, target, generation_request=wrong_config)
    assert report.disposition.value == "ERROR"
    assert "parent generation provenance" in report.reason
    assert report.workload is None


def test_generation_request_without_parent_provenance_remains_unavailable() -> None:
    parent, request, mutation, candidate, target = _fixture()
    generation_request = GenerationRequest("EASY", 41, "MASK", width=20, height=20)
    report = _run(parent, request, mutation, candidate, target, generation_request=generation_request)
    mutation_route = MutationAttemptRouteEvidence.from_attempt_report(report)
    assert report.workload is None
    assert mutation_route.workload.availability == "UNAVAILABLE"


def test_forged_raw_parent_digest_cannot_establish_workload_or_match() -> None:
    aligned = GenerationRequest("EASY", 41, "MASK", width=20, height=20)
    parent, request, mutation, candidate, target = _fixture()
    forged_parent = MutationCandidate.root(
        parent.candidate_id,
        {**dict(parent.payload), "generation_request_digest": aligned.digest()},
        level_data_sha256=parent.level_data_sha256,
        source_art_sha256=parent.source_art_sha256,
    )
    report = _run(forged_parent, request, mutation, candidate, target, generation_request=aligned)
    mutation_route = MutationAttemptRouteEvidence.from_attempt_report(report)
    regeneration_route = RegenerationRouteEvidence.from_generation_result(GeneratorRouter().generate(aligned), target=target, budget=report.budget)
    assert mutation_route.workload.availability == "UNAVAILABLE"
    assert compare_efficiency_from_authentic_routes(mutation_route, regeneration_route).disposition != "MATCHED"


def test_sealed_parent_binding_rejects_wrong_parent_and_tampered_digests() -> None:
    aligned = GenerationRequest("EASY", 41, "MASK", width=20, height=20)
    result = GeneratorRouter().generate(aligned)
    parent, *_ = _fixture()
    sealed = parent.with_accepted_generation_result(result)
    other = MutationCandidate.root("other-parent", dict(parent.payload))
    with pytest.raises(MutationContractError):
        replace(other, generation_provenance=sealed.generation_provenance)
    with pytest.raises(MutationContractError):
        replace(sealed.generation_provenance, request_digest="f" * 64)
    with pytest.raises(MutationContractError):
        replace(sealed.generation_provenance, result_digest="e" * 64)


def test_sealed_result_for_another_request_cannot_authorize_aligned_workload() -> None:
    aligned = GenerationRequest("EASY", 41, "MASK", width=20, height=20)
    other_request = GenerationRequest("EASY", 41, "MASK", width=21, height=21)
    parent, request, mutation, candidate, target = _fixture()
    parent = parent.with_accepted_generation_result(GeneratorRouter().generate(other_request))
    report = _run(parent, request, mutation, candidate, target, generation_request=aligned)
    assert report.disposition.value == "ERROR"
    assert report.workload is None


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

# These tests exercise explicit historical/research behavior, not the current production request.
GenerationRequest = _LegacyGenerationRequest
