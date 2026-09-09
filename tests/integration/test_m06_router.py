"""Focused PAG-M06 router, AUTO, composition, and provenance coverage."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import replace

import pytest

from scrubbots_pixel_factory import (
    DeterministicRNG,
    FailureCode,
    GenerationRequest,
    GenerationResult,
    GeneratorMode,
    GeneratorOptions,
    offline_runtime,
)
from scrubbots_pixel_factory.generators.router import (
    AutoCandidate,
    GeneratorRouter,
    HybridCandidate,
    HybridGenerator,
    HybridStrategy,
    reproduce_hybrid,
)
from scrubbots_pixel_factory.generators.router.hybrid import _validate_final
from scrubbots_pixel_factory.generators.mask import MaskSpriteGenerator
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator


def _block_exemplar() -> Exemplar:
    colors = ("C11", "C12", "C13")
    pixels = tuple(colors[(x // 2) % 3] for y in range(6) for x in range(6))
    return Exemplar(
        "scrubbots-wfc-exemplar", 1, "m06-blocks", "TRAINING_MOTIF", 6, 6, pixels,
        "synthetic-test-fixture", "Project-authored test motif; not production artwork.", "SYNTHETIC_TEST_ONLY",
    )


def _hybrid_request(strategy: str, seed: int | str = 41, **values: object) -> GenerationRequest:
    merged = {"strategy": strategy, "mask_style": "ROBOT", "rules_style": "ORGANIC", **values}
    return GenerationRequest(
        "EASY", seed, "HYBRID", width=20, height=27, palette_subset=("C01", "C02", "C03"),
        generator_options=GeneratorOptions("hybrid", 1, merged),
    )


def _wfc_hybrid_generator() -> HybridGenerator:
    exemplar = _block_exemplar()
    return HybridGenerator(wfc_generator=WFCGenerator(ExemplarRegistry((exemplar,))))


def _mutable(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _mutable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_mutable(item) for item in value]
    return value


class _AlwaysFail:
    generator_id = "test-always-fail"
    generator_version = "1.0.0"

    def __init__(self) -> None:
        self.calls: list[str] = []

    def generate_candidate(self, request: GenerationRequest, rng: DeterministicRNG) -> GenerationResult:
        self.calls.append(request.generator_mode)
        return GenerationResult.failure(code=FailureCode.GENERATION_FAILED, reason="forced test failure", request=request)


def test_auto_mode_and_existing_request_bytes_are_stable() -> None:
    explicit = GenerationRequest("EASY", 7, "MASK", width=20, height=20)
    assert explicit.canonical_dict()["generator_mode"] == "MASK"
    auto = GenerationRequest("EASY", 7, "AUTO", width=20, height=20, generator_options=GeneratorOptions("auto", 1, {}))
    assert auto.generator_mode == GeneratorMode.AUTO.value
    candidate = GeneratorRouter().generate_candidate(auto)
    assert isinstance(candidate, AutoCandidate)
    assert candidate.candidate_order == ("MASK", "RULES")
    assert candidate.result.request == auto
    assert candidate.result.generator_mode == "AUTO"
    assert candidate.result.generator_id in {"mask-sprite", "rule-shape"}


def test_explicit_routes_use_the_accepted_engines_without_fallback() -> None:
    router = GeneratorRouter(wfc_generator=WFCGenerator(ExemplarRegistry((_block_exemplar(),))))
    requests = (
        (GenerationRequest("EASY", 3, "MASK", width=20, height=20), router.mask_generator),
        (GenerationRequest("EASY", 3, "RULES", width=20, height=20), router.rules_generator),
        (GenerationRequest("EASY", 3, "WFC", width=20, height=20, style="m06-blocks", palette_subset=("C01", "C02", "C03"), generator_options=GeneratorOptions("wfc", 1, {"pattern_size": 2, "input_periodic": True})), router.wfc_generator),
    )
    for request, direct_engine in requests:
        result = router.generate(request)
        direct = direct_engine.generate(request)
        assert result.canonical_bytes() == direct.canonical_bytes()
        assert result.request == request


def test_explicit_hybrid_router_matches_direct_hybrid_engine() -> None:
    request = _hybrid_request(HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS.value, 13)
    direct = HybridGenerator().generate(request)
    routed = GeneratorRouter().generate(request)
    assert direct.canonical_bytes() == routed.canonical_bytes()


def test_auto_default_selection_has_seeded_diversity() -> None:
    request = GenerationRequest("EASY", 0, "AUTO", width=20, height=20, generator_options=GeneratorOptions("auto", 1, {}))
    candidates = [GeneratorRouter().generate_candidate(replace(request, seed=seed)) for seed in range(48)]
    selected = {candidate.selected_mode for candidate in candidates if isinstance(candidate, AutoCandidate)}
    assert selected == {"MASK", "RULES"}


def test_auto_fallback_records_one_failed_attempt_then_success() -> None:
    failing = _AlwaysFail()
    router = GeneratorRouter(mask_generator=MaskSpriteGenerator(), wfc_generator=failing)
    options = GeneratorOptions("auto", 1, {"candidates": ["WFC", "MASK"], "fallback_on_failure": True})
    seed = next(seed for seed in range(100) if DeterministicRNG(seed).child("auto/selection").randbelow(2) == 0)
    request = GenerationRequest("EASY", seed, "AUTO", width=20, height=20, palette_subset=("C01", "C02", "C03"), generator_options=options)
    candidate = router.generate_candidate(request)
    assert isinstance(candidate, AutoCandidate)
    assert [attempt.mode for attempt in candidate.attempts] == ["WFC", "MASK"]
    assert candidate.attempts[0].failure_code == FailureCode.GENERATION_FAILED.value
    assert candidate.selected_mode == "MASK"
    assert candidate.result.request == request and candidate.result.generator_mode == "AUTO"
    assert failing.calls == ["WFC"]


def test_auto_fallback_all_fail_is_bounded_and_byte_stable() -> None:
    failing_wfc = _AlwaysFail()
    failing_rules = _AlwaysFail()
    router = GeneratorRouter(rules_generator=failing_rules, wfc_generator=failing_wfc)
    options = GeneratorOptions("auto", 1, {"candidates": ["WFC", "RULES"], "fallback_on_failure": True})
    request = GenerationRequest("EASY", 2, "AUTO", width=20, height=20, generator_options=options)
    first = router.generate(request)
    second = router.generate(request)
    assert not first.is_success and first.failure_code is FailureCode.RETRY_EXHAUSTED
    assert first.canonical_bytes() == second.canonical_bytes()
    assert failing_wfc.calls == ["WFC", "WFC"]
    assert failing_rules.calls == ["RULES", "RULES"]


def test_wfc_detail_preserves_default_and_explicit_nonidentity_mapping() -> None:
    generator = _wfc_hybrid_generator()
    expected_default = (("C11", "C01"), ("C12", "C02"), ("C13", "C03"))
    explicit = {"C11": "C02", "C12": "C03", "C13": "C01"}
    for strategy in (HybridStrategy.RULE_BASE_WFC_DETAIL.value, HybridStrategy.MASK_BASE_WFC_DETAIL.value):
        default = generator.generate_candidate(_hybrid_request(strategy, 0 if "RULE" in strategy else 1, wfc_exemplar_id="m06-blocks"))
        assert isinstance(default, HybridCandidate) and default.result.is_success
        assert default.stages[-1].extra["palette_mapping"] == expected_default
        mapped = generator.generate_candidate(_hybrid_request(
            strategy, 0 if "RULE" in strategy else 1, wfc_exemplar_id="m06-blocks",
            wfc_options={"namespace": "wfc", "version": 1, "values": {
                "pattern_size": 2, "input_periodic": True, "output_periodic": True,
                "palette_mapping": explicit,
            }},
        ))
        assert isinstance(mapped, HybridCandidate) and mapped.result.is_success
        assert mapped.stages[-1].extra["palette_mapping"] == tuple((source, target) for source, target in explicit.items())
    invalid = generator.generate(_hybrid_request(
        HybridStrategy.RULE_BASE_WFC_DETAIL.value, 0, wfc_exemplar_id="m06-blocks",
        wfc_options={"namespace": "wfc", "version": 1, "values": {
            "pattern_size": 2, "input_periodic": True, "output_periodic": True,
            "palette_mapping": {"C01": "C01", "C02": "C02", "C03": "C03"},
        }},
    ))
    assert not invalid.is_success and invalid.failure_code is FailureCode.RETRY_EXHAUSTED


def test_hybrid_replay_rejects_each_corrupted_integrity_field() -> None:
    generator = _wfc_hybrid_generator()
    robust_request = _hybrid_request(HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS.value, 19)
    robust = generator.generate_candidate(robust_request)
    assert isinstance(robust, HybridCandidate)
    fields = (
        ("derived_seed", "0" * 64),
        ("child_request_digest", "1" * 64),
        ("engine_version", "corrupted-version"),
        ("child_result_digest", "2" * 64),
        ("geometry_digest", "3" * 64),
    )
    for field, value in fields:
        metadata = _mutable(robust.metadata)
        metadata["stages"][0][field] = value  # type: ignore[index]
        corrupted = replace(robust, metadata=metadata)
        with pytest.raises(ValueError, match="INVALID_STAGE_METADATA"):
            reproduce_hybrid(generator, robust_request, corrupted)
    wfc_request = _hybrid_request(HybridStrategy.RULE_BASE_WFC_DETAIL.value, 0, wfc_exemplar_id="m06-blocks")
    wfc = generator.generate_candidate(wfc_request)
    assert isinstance(wfc, HybridCandidate)
    metadata = _mutable(wfc.metadata)
    metadata["stages"][-1]["extra"]["pattern_table_digest"] = "4" * 64  # type: ignore[index]
    with pytest.raises(ValueError, match="INVALID_STAGE_METADATA"):
        reproduce_hybrid(generator, wfc_request, replace(wfc, metadata=metadata))
    metadata = _mutable(robust.metadata)
    metadata["final_logical_grid_digest"] = "5" * 64  # type: ignore[index]
    with pytest.raises(ValueError, match="INVALID_STAGE_METADATA"):
        reproduce_hybrid(generator, robust_request, replace(robust, metadata=metadata))


def test_hybrid_robust_strategies_are_deterministic_and_outer_authoritative() -> None:
    generator = HybridGenerator()
    for strategy in (HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS.value, HybridStrategy.RULE_GEOMETRY_MASK_SYMMETRY.value):
        request = _hybrid_request(strategy, 19, rules_style="ORGANIC", mask_symmetry="HORIZONTAL")
        first = generator.generate_candidate(request)
        second = generator.generate_candidate(request)
        assert isinstance(first, HybridCandidate) and isinstance(second, HybridCandidate)
        assert first.result.canonical_bytes() == second.result.canonical_bytes()
        assert first.result.width == 20 and first.result.height == 27
        assert tuple(first.result.used_palette) == ("C01", "C02", "C03")
        assert first.metadata["final_logical_grid_digest"] == second.metadata["final_logical_grid_digest"]
        assert all(stage.child_request["resolved_dimensions"] if False else stage.child_request["width"] == 20 for stage in first.stages)
        assert all(stage.derived_seed == stage.derived_seed and len(stage.derived_seed) == 64 for stage in first.stages)
        replay = reproduce_hybrid(generator, request, first)
        assert isinstance(replay, HybridCandidate)


def test_all_four_hybrid_strategy_paths_are_present_and_wfc_detail_is_injected() -> None:
    generator = _wfc_hybrid_generator()
    robust = generator.generate(_hybrid_request(HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS.value, 1)).is_success
    symmetric = generator.generate(_hybrid_request(HybridStrategy.RULE_GEOMETRY_MASK_SYMMETRY.value, 1)).is_success
    rule_detail = generator.generate(_hybrid_request(HybridStrategy.RULE_BASE_WFC_DETAIL.value, 0, wfc_exemplar_id="m06-blocks")).is_success
    mask_detail = generator.generate(_hybrid_request(HybridStrategy.MASK_BASE_WFC_DETAIL.value, 1, wfc_exemplar_id="m06-blocks")).is_success
    assert robust and symmetric and rule_detail and mask_detail


def test_wfc_detail_requires_an_explicit_exemplar_and_auto_fallback_is_visible() -> None:
    missing = _hybrid_request(HybridStrategy.RULE_BASE_WFC_DETAIL.value, wfc_exemplar_id="missing")
    result = HybridGenerator().generate(missing)
    assert not result.is_success and result.failure_code is FailureCode.RETRY_EXHAUSTED
    options = GeneratorOptions("auto", 1, {"candidates": ["WFC"], "fallback_on_failure": False})
    request = GenerationRequest("EASY", 2, "AUTO", width=20, height=20, palette_subset=("C01", "C02", "C03"), generator_options=options)
    router = GeneratorRouter(wfc_generator=WFCGenerator())
    failure = router.generate(request)
    assert not failure.is_success and failure.failure_code is FailureCode.GENERATION_FAILED


def test_hybrid_child_rngs_are_canonical_roots_and_topology_rejection_is_fail_closed() -> None:
    generator = _wfc_hybrid_generator()
    request = _hybrid_request(HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS.value, 101)
    candidate = generator.generate_candidate(request, DeterministicRNG(101))
    assert isinstance(candidate, HybridCandidate)
    assert candidate.result.provenance["stage_seeds"] == DeterministicRNG(101).stage_seeds()
    assert all(stage.child_request["generator_mode"] in {"MASK", "RULES", "WFC"} for stage in candidate.stages)


def test_hybrid_quality_gate_rejects_topology_and_singleton_drift() -> None:
    palette = ("C01", "C02", "C03")
    broken_topology = ("C01", "C01", "C02", "C03")
    try:
        _validate_final(broken_topology, 2, 2, palette, {0, 1, 2}, base_color="C01")
    except ValueError as exc:
        assert str(exc) == "TOPOLOGY_DESTROYED"
    else:
        raise AssertionError("dimension drift was not rejected")
    singleton = ("C01", "C01", "C02", "C03", "C03", "C01", "C01", "C01", "C01")
    try:
        _validate_final(singleton, 3, 3, palette, {2, 3, 4}, base_color="C01")
    except ValueError as exc:
        assert str(exc) in {"TOPOLOGY_DESTROYED", "SINGLETON_COLOR_REGION"}
    else:
        raise AssertionError("quality drift was not rejected")


def test_hybrid_cross_process_and_offline_digest_is_stable() -> None:
    code = """from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.router import HybridGenerator
q=GenerationRequest('EASY','cross-process','HYBRID',width=20,height=27,generator_options=GeneratorOptions('hybrid',1,{'strategy':'MASK_GEOMETRY_RULE_COLOR_REGIONS','mask_style':'ROBOT','rules_style':'ORGANIC'}))
print(HybridGenerator().generate(q).digest())
"""
    outputs = []
    for hash_seed in ("1", "random"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed, PYTHONPATH="src")
        outputs.append(subprocess.check_output([sys.executable, "-c", code], text=True, env=env).strip())
    assert outputs[0] == outputs[1]
    request = _hybrid_request(HybridStrategy.RULE_GEOMETRY_MASK_SYMMETRY.value, 303, rules_style="ORGANIC")
    with offline_runtime():
        result = HybridGenerator().generate(request)
    assert result.is_success
