from dataclasses import replace

import pytest

from scrubbots_pixel_factory import DeterministicRNG, GenerationRequest, GenerationResult, GeneratorOptions
from scrubbots_pixel_factory.core.rng import RNG_ALGORITHM
from scrubbots_pixel_factory.generators.router import AutoCandidate, GeneratorRouter
from scrubbots_pixel_factory.output import OutputContractError, build_export_bundle
from scrubbots_pixel_factory.quality import QualityPolicy


def _request(seed="m02-01-seed", *, budget=2, quality_policy=None):
    return GenerationRequest(
        seed=seed, width=20, height=20, generator_mode="AUTO",
        generator_options=GeneratorOptions(
            "auto", 1,
            {
                "candidates": ["MASK"],
                "evaluator_guided": {
                    "version": 1,
                    "proposal_budget": budget,
                    "quality_policy": (quality_policy or QualityPolicy(max_largest_region_ratio=0.6)).as_dict(),
                },
            },
        ),
    )


def _grid(slab, width=20, height=20):
    cells = ["C01"] * (width * height)
    if slab:
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                cells[y * width + x] = "C02"
        cells[(height // 2) * width + width // 2] = "C03"
    else:
        for y in range(5, min(10, height - 1)):
            for x in range(5, min(10, width - 1)):
                cells[y * width + x] = "C02"
            for x in range(11, min(16, width - 1)):
                cells[y * width + x] = "C03"
    return tuple(cells)


class SyntheticMask:
    generator_id = "synthetic-mask"
    generator_version = "1.0"

    def __init__(self, root_seed, *, reject_all=False):
        self.seeds = {
            DeterministicRNG(root_seed).child(f"evaluator-guided/proposal/{index}").next_bytes(32).hex(): index
            for index in range(8)
        }
        self.reject_all = reject_all

    def generate_candidate(self, request, rng):
        index = self.seeds[request.seed]
        return GenerationResult.success(
            request=request, width=request.width, height=request.height,
            logical_grid=_grid(self.reject_all or index == 0, request.width, request.height),
            generator_id=self.generator_id, generator_version=self.generator_version,
            generator_mode="MASK", seed=request.seed, rng_algorithm=RNG_ALGORITHM,
            provenance={"stage_seeds": rng.stage_seeds(), "retry_seeds": {}},
        )


def _router(request, *, reject_all=False):
    return GeneratorRouter(mask_generator=SyntheticMask(request.seed, reject_all=reject_all))


def test_evaluator_guided_replay_is_byte_identical_and_selects_quality_winner():
    request = _request()
    first = _router(request).generate_candidate(request)
    replay = _router(request).generate_candidate(request)
    assert isinstance(first, AutoCandidate)
    assert first.result.canonical_bytes() == replay.result.canonical_bytes()
    assert first.metadata == replay.metadata
    assert first.metadata["selected_index"] == 1
    assert first.metadata["attempts"][0]["quality"]["accepted"] is False
    assert first.metadata["attempts"][1]["quality"]["accepted"] is True
    bundle = build_export_bundle(first, "m02-01-test")
    replay_bundle = build_export_bundle(replay, "m02-01-test")
    assert bundle.metadata_json == replay_bundle.metadata_json
    assert bundle.artwork_png == replay_bundle.artwork_png
    assert bundle.metadata["generator_metadata"]["classification"]["candidate_class"] == "TEST"


def test_evaluator_guided_all_rejected_fails_closed():
    request = _request()
    result = _router(request, reject_all=True).generate_candidate(request)
    assert isinstance(result, GenerationResult)
    assert not result.is_success
    assert result.failure_code.value == "QUALITY_REJECTED"


@pytest.mark.parametrize("budget", [True, 1, 9, 2.0])
def test_evaluator_guided_rejects_invalid_budget(budget):
    request = _request(budget=budget)
    result = GeneratorRouter().generate_candidate(request)
    assert isinstance(result, GenerationResult)
    assert result.failure_code.value == "INVALID_REQUEST"


def test_evaluator_guided_bundle_rejects_tampered_winner_identity():
    request = _request()
    candidate = _router(request).generate_candidate(request)
    assert isinstance(candidate, AutoCandidate)
    metadata = dict(candidate.metadata)
    metadata["selected_index"] = 0
    tampered = replace(candidate, metadata=metadata)
    with pytest.raises(OutputContractError):
        build_export_bundle(tampered, "m02-01-tampered")


def test_evaluator_guided_59_square_budget_remains_bounded():
    request = GenerationRequest(
        seed="m02-01-59", width=59, height=59, generator_mode="AUTO",
        generator_options=GeneratorOptions("auto", 1, {
            "candidates": ["MASK"],
            "evaluator_guided": {"version": 1, "proposal_budget": 2, "quality_policy": QualityPolicy(max_largest_region_ratio=0.6).as_dict()},
        }),
    )
    engine = SyntheticMask(request.seed)
    candidate = GeneratorRouter(mask_generator=engine).generate_candidate(request)
    assert isinstance(candidate, AutoCandidate)
    assert len(candidate.metadata["attempts"]) == 2
