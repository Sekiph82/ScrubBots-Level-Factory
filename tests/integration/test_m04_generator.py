import pytest

from scrubbots_pixel_factory import DeterministicRNG, FailureCode, GenerationRequest, GeneratorMode, PixelGenerator, offline_runtime
from scrubbots_pixel_factory.generators.rules import RECIPE_NAMES, RuleCandidate, RuleShapeGenerator, color_component_sizes


RECTANGLES = {"EASY": (29, 23), "MEDIUM": (30, 39), "HARD": (48, 41), "VERY_HARD": (59, 50)}


def _request(difficulty="EASY", seed=11, style="SYMMETRY", **kwargs):
    return GenerationRequest(difficulty=difficulty, seed=seed, generator_mode="RULES", style=style, **kwargs)


def test_rules_generator_integrates_with_m02_and_rejects_other_modes() -> None:
    generator = RuleShapeGenerator()
    assert isinstance(generator, PixelGenerator)
    assert generator.generate(_request()).is_success
    assert generator.generate(GenerationRequest(difficulty="EASY", seed=1, generator_mode="MASK")).failure_code is FailureCode.INVALID_REQUEST


def test_rules_root_rng_and_invalid_inputs_fail_closed() -> None:
    generator = RuleShapeGenerator()
    assert generator.generate(_request(), DeterministicRNG(11, "geometry")).failure_code is FailureCode.INVALID_REQUEST
    assert generator.generate(_request(style="UNKNOWN")).failure_code is FailureCode.INVALID_REQUEST
    assert generator.generate(_request(theme="theme")).failure_code is FailureCode.INVALID_REQUEST
    assert generator.generate(_request(generator_options={"namespace": "rules", "version": 1, "values": {"unknown": 1}})).failure_code is FailureCode.INVALID_REQUEST


def test_rules_rectangles_palette_and_provenance() -> None:
    generator = RuleShapeGenerator()
    for difficulty, (width, height) in RECTANGLES.items():
        result = generator.generate(_request(difficulty, 31, "CENTRAL_SUBJECT", width=width, height=height))
        assert result.is_success
        assert (result.width, result.height) == (width, height)
        assert len(result.logical_grid) == width * height
        assert set(result.logical_grid) == set(result.used_palette) == set(result.request.resolve_palette_subset())
        assert "BG01" not in result.logical_grid
        assert result.provenance["stage_seeds"] == DeterministicRNG(31).stage_seeds()


def test_rules_runs_inside_offline_runtime_and_repeats_byte_identically() -> None:
    generator = RuleShapeGenerator()
    request = _request("VERY_HARD", 734, "ORGANIC", width=59, height=59)
    with offline_runtime():
        first = generator.generate(request)
        second = generator.generate(request)
    assert first.is_success and first.canonical_bytes() == second.canonical_bytes()


def test_rules_acceptance_batch_has_140_successes_and_zero_contract_violations() -> None:
    generator = RuleShapeGenerator()
    accepted = 0
    violations = []
    for recipe in RECIPE_NAMES:
        for difficulty, (width, height) in RECTANGLES.items():
            for seed in (11, 23, 47, 71, 97):
                request = _request(difficulty, seed, recipe, width=width, height=height)
                candidate = generator.generate_candidate(request)
                if not isinstance(candidate, RuleCandidate):
                    violations.append((recipe, difficulty, seed, candidate.failure_code))
                    continue
                accepted += 1
                result = candidate.result
                sizes = color_component_sizes(result.logical_grid, width, height)
                counts = {color: result.logical_grid.count(color) for color in result.used_palette}
                if (result.width, result.height) != (width, height) or set(result.logical_grid) != set(result.used_palette) or "BG01" in result.logical_grid or any(size < 2 for values in sizes.values() for size in values) or max(counts.values()) * 100 > 82 * width * height or result.canonical_bytes() != generator.generate(request).canonical_bytes():
                    violations.append((recipe, difficulty, seed, "contract"))
    assert accepted == 140
    assert violations == []
