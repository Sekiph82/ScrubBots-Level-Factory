from dataclasses import replace
import hashlib
import json

import pytest

from scrubbots_pixel_factory import DeterministicRNG, GenerationRequest, GenerationResult, GeneratorOptions
from scrubbots_pixel_factory.core.rng import RNG_ALGORITHM
from scrubbots_pixel_factory.generators.router import AutoCandidate, GeneratorRouter
from scrubbots_pixel_factory.output import OutputContractError, build_export_bundle
from scrubbots_pixel_factory.quality import QualityPolicy, evaluate_grid


def _request(seed="m02-01-seed", *, budget=2, quality_policy=None, width=20, height=20, color_count=3):
    return GenerationRequest(
        seed=seed, width=width, height=height, generator_mode="AUTO",
        palette_subset=tuple(f"C{index:02d}" for index in range(1, color_count + 1)),
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


def _grid(slab, width=20, height=20, colors=("C01", "C02", "C03")):
    cells = ["C01"] * (width * height)
    if slab:
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                cells[y * width + x] = colors[1]
        cells[(height // 2) * width + width // 2] = colors[2]
    else:
        for y in range(5, min(10, height - 1)):
            for x in range(5, min(10, width - 1)):
                cells[y * width + x] = colors[1]
            for x in range(11, min(16, width - 1)):
                cells[y * width + x] = colors[2]
        for color_index, color in enumerate(colors[3:], start=0):
            start_x = 5 + color_index * 6
            start_y = 12
            for y in range(start_y, min(start_y + 3, height - 1)):
                for x in range(start_x, min(start_x + 3, width - 1)):
                    cells[y * width + x] = color
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
            logical_grid=_grid(self.reject_all or index == 0, request.width, request.height, request.palette_subset),
            generator_id=self.generator_id, generator_version=self.generator_version,
            generator_mode="MASK", seed=request.seed, rng_algorithm=RNG_ALGORITHM,
            provenance={"stage_seeds": rng.stage_seeds(), "retry_seeds": {}},
        )


class OnePassMask:
    generator_id = "one-pass-mask"
    generator_version = "1.0"

    def generate_candidate(self, request, rng):
        return GenerationResult.success(
            request=request, width=request.width, height=request.height,
            logical_grid=_grid(False, request.width, request.height, request.palette_subset),
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
    alternate_request = _request("m02-01-alternate-seed")
    alternate = _router(alternate_request).generate_candidate(alternate_request)
    assert first.metadata["attempts"][0]["seed"] != alternate.metadata["attempts"][0]["seed"]
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


@pytest.mark.parametrize("difficulty", ["EASY", "MEDIUM", "VERY_HARD"])
def test_evaluator_guided_rejects_legacy_difficulty_policy(difficulty):
    policy = QualityPolicy(difficulty=difficulty, max_largest_region_ratio=0.6).as_dict()
    request = _request(quality_policy=policy, width=38, height=38)
    result = GeneratorRouter().generate_candidate(request)
    assert isinstance(result, GenerationResult)
    assert result.failure_code.value == "INVALID_REQUEST"


def test_evaluator_guided_rejects_noncanonical_policy_round_trip():
    policy = QualityPolicy(max_largest_region_ratio=0.6).as_dict()
    policy["max_isolated_ratio"] = 0.200000001
    request = _request(quality_policy=policy)
    result = GeneratorRouter().generate_candidate(request)
    assert isinstance(result, GenerationResult)
    assert result.failure_code.value == "INVALID_REQUEST"


@pytest.mark.parametrize("width,height,color_count", [(38, 38, 3), (24, 24, 5), (38, 24, 3)])
def test_modern_dimensions_and_colors_are_difficulty_independent(width, height, color_count):
    request = _request(
        f"modern-envelope-{width}-{color_count}",
        width=width, height=height, color_count=color_count,
        quality_policy=QualityPolicy(max_largest_region_ratio=0.6).as_dict(),
    )
    candidate = _router(request).generate_candidate(request)
    assert isinstance(candidate, AutoCandidate)
    assert candidate.result.is_success
    assert len(candidate.result.used_palette) == color_count
    assert candidate.metadata["selected_quality"]["accepted"] is True
    assert build_export_bundle(candidate, f"modern-{width}-{color_count}").artwork.width == width


def test_evaluator_guided_bundle_rejects_forged_nonnull_difficulty():
    request = _request(width=38, height=38)
    candidate = _router(request).generate_candidate(request)
    assert isinstance(candidate, AutoCandidate)
    original_policy = dict(candidate.metadata["policy"])
    invalid_quality_policy = dict(original_policy["quality_policy"])
    invalid_quality_policy["difficulty"] = "EASY"
    invalid_policy = {**original_policy, "quality_policy": invalid_quality_policy}
    invalid_request = _request(seed=request.seed, width=38, height=38, quality_policy=QualityPolicy(difficulty="EASY", max_largest_region_ratio=0.6).as_dict())
    bad_result = GenerationResult.success(
        request=invalid_request, width=candidate.result.width, height=candidate.result.height,
        logical_grid=candidate.result.logical_grid, generator_id=candidate.result.generator_id,
        generator_version=candidate.result.generator_version, generator_mode="AUTO",
        seed=invalid_request.seed, rng_algorithm=candidate.result.rng_algorithm,
        provenance=candidate.result.provenance,
    )
    metadata = dict(candidate.metadata)
    metadata["policy"] = invalid_policy
    metadata["request_digest"] = invalid_request.digest()
    metadata["policy_digest"] = hashlib.sha256(json.dumps(invalid_policy, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    forged = replace(candidate, result=bad_result, metadata=metadata)
    with pytest.raises(OutputContractError, match="difficulty must be null"):
        build_export_bundle(forged, "m02-01-legacy-policy")


def test_non_opt_in_auto_keeps_existing_fallback_contract():
    request = GenerationRequest(
        seed="non-opt-in-auto", width=20, height=20, generator_mode="AUTO",
        palette_subset=("C01", "C02", "C03"),
        generator_options=GeneratorOptions("auto", 1, {"candidates": ["MASK"]}),
    )
    candidate = GeneratorRouter(mask_generator=OnePassMask()).generate_candidate(request)
    assert isinstance(candidate, AutoCandidate)
    assert candidate.metadata["schema"] == "scrubbots-auto-metadata"
    assert "evaluator_guided" not in request.options.values
    assert build_export_bundle(candidate, "non-opt-in-auto").metadata["generator_metadata"]["payload"]["data"]["schema"] == "scrubbots-auto-metadata"


def test_m07_legacy_difficulty_api_remains_available():
    report = evaluate_grid(38, 38, _grid(False, 38, 38), policy=QualityPolicy(difficulty="EASY"))
    assert report.accepted is False
    assert "DIMENSION_MISMATCH" in report.rejection_codes


def test_evaluator_guided_bundle_rejects_tampered_winner_identity():
    request = _request()
    candidate = _router(request).generate_candidate(request)
    assert isinstance(candidate, AutoCandidate)
    metadata = dict(candidate.metadata)
    metadata["selected_index"] = 0
    tampered = replace(candidate, metadata=metadata)
    with pytest.raises(OutputContractError):
        build_export_bundle(tampered, "m02-01-tampered")


def test_evaluator_guided_bundle_rejects_gameplay_claim_fields():
    request = _request()
    candidate = _router(request).generate_candidate(request)
    assert isinstance(candidate, AutoCandidate)
    metadata = dict(candidate.metadata)
    metadata["solver_evidence"] = {"solvable": True}
    tampered = replace(candidate, metadata=metadata)
    with pytest.raises(OutputContractError):
        build_export_bundle(tampered, "m02-01-game-claim")


def test_evaluator_guided_59_square_budget_remains_bounded():
    request = GenerationRequest(
        seed="m02-01-59", width=59, height=59, generator_mode="AUTO",
        palette_subset=("C01", "C02", "C03"),
        generator_options=GeneratorOptions("auto", 1, {
            "candidates": ["MASK"],
            "evaluator_guided": {"version": 1, "proposal_budget": 2, "quality_policy": QualityPolicy(max_largest_region_ratio=0.6).as_dict()},
        }),
    )
    engine = SyntheticMask(request.seed)
    candidate = GeneratorRouter(mask_generator=engine).generate_candidate(request)
    assert isinstance(candidate, AutoCandidate)
    assert len(candidate.metadata["attempts"]) == 2
