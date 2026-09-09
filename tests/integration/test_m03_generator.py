import hashlib

import pytest

from scrubbots_pixel_factory import CANONICAL_PALETTE
from scrubbots_pixel_factory.core import DeterministicRNG, FailureCode, GenerationRequest, GeneratorMode, PixelGenerator

def _generator():
    from scrubbots_pixel_factory.generators import MaskSpriteGenerator
    return MaskSpriteGenerator()


def _family_names():
    from scrubbots_pixel_factory.generators import FAMILY_NAMES
    return FAMILY_NAMES


RECTANGLES = {
    "EASY": (29, 23),
    "MEDIUM": (30, 39),
    "HARD": (48, 41),
    "VERY_HARD": (59, 50),
}


def request(difficulty="EASY", seed=11, **kwargs):
    return GenerationRequest(difficulty=difficulty, seed=seed, generator_mode="MASK", **kwargs)


def test_mask_generator_implements_protocol_and_accepts_only_mask() -> None:
    generator = _generator()
    assert isinstance(generator, PixelGenerator)
    result = generator.generate(request())
    assert result.is_success
    rules = generator.generate(GenerationRequest(difficulty="EASY", seed=11, generator_mode="RULES"))
    assert rules.failure_code is FailureCode.INVALID_REQUEST


def test_mask_generation_runs_inside_offline_runtime() -> None:
    from scrubbots_pixel_factory import offline_runtime
    with offline_runtime():
        result = _generator().generate(request(seed=77, style="FISH"))
    assert result.is_success


def test_mask_generator_fails_closed_for_rng_style_theme_and_options() -> None:
    generator = _generator()
    mismatch = generator.generate(request(seed=11), DeterministicRNG(12))
    assert mismatch.failure_code is FailureCode.INVALID_REQUEST
    unsupported_style = generator.generate(request(style="UNKNOWN"))
    assert unsupported_style.failure_code is FailureCode.INVALID_REQUEST
    unsupported_theme = generator.generate(request(theme="underwater"))
    assert unsupported_theme.failure_code is FailureCode.INVALID_REQUEST
    unsupported_options = generator.generate(request(generator_options={"namespace": "mask", "version": 1, "values": {"unknown": 1}}))
    assert unsupported_options.failure_code is FailureCode.INVALID_REQUEST


def test_style_none_selects_a_deterministic_family() -> None:
    generator = _generator()
    first = generator.generate(request(seed=91))
    second = generator.generate(request(seed=91))
    assert first.canonical_bytes() == second.canonical_bytes()


def test_explicit_options_are_immutable_and_participate_in_output() -> None:
    generator = _generator()
    base = generator.generate(request(seed=21, style="ROBOT"))
    configured = generator.generate(request(seed=21, style="ROBOT", generator_options={"namespace": "mask", "version": 1, "values": {"symmetry": "ASYMMETRIC", "mutation": 8, "offset_x": 2, "offset_y": -1}}))
    assert base.is_success and configured.is_success
    assert base.canonical_bytes() != configured.canonical_bytes()


@pytest.mark.parametrize("difficulty", RECTANGLES)
def test_legal_rectangles_preserve_dimensions_palette_and_result_contract(difficulty: str) -> None:
    width, height = RECTANGLES[difficulty]
    result = _generator().generate(request(difficulty=difficulty, seed=31, style="ROBOT", width=width, height=height))
    assert result.is_success
    assert (result.width, result.height) == (width, height)
    assert len(result.logical_grid) == width * height
    assert set(result.logical_grid) == set(result.used_palette) == set(result.request.resolve_palette_subset())
    assert all(cell in CANONICAL_PALETTE.ids for cell in result.logical_grid)
    assert "BG01" not in result.logical_grid
    assert result.generator_mode == GeneratorMode.MASK.value
    assert result.provenance["stage_seeds"] == DeterministicRNG(result.request.seed).stage_seeds()


def test_same_request_rng_is_byte_identical_and_fixed_seeds_vary() -> None:
    generator = _generator()
    first = generator.generate(request(seed=44, style="CREATURE"), DeterministicRNG(44))
    second = generator.generate(request(seed=44, style="CREATURE"), DeterministicRNG(44))
    assert first.canonical_bytes() == second.canonical_bytes()
    outputs = {generator.generate(request(seed=seed, style="CREATURE")).canonical_bytes() for seed in (1, 2, 3, 4)}
    assert len(outputs) > 1


def test_fixed_acceptance_batch_has_120_accepted_candidates_and_zero_contract_violations() -> None:
    generator = _generator()
    accepted = 0
    violations = []
    for difficulty, (width, height) in RECTANGLES.items():
        for family in _family_names():
            for seed in (11, 23, 47):
                result = generator.generate(request(difficulty=difficulty, seed=seed, style=family, width=width, height=height))
                if not result.is_success:
                    continue
                accepted += 1
                palette = result.request.resolve_palette_subset()
                if ((result.width, result.height) != (width, height) or len(result.logical_grid) != width * height or set(result.logical_grid) != set(palette) or "BG01" in result.logical_grid):
                    violations.append((difficulty, family, seed))
                assert result.canonical_bytes() == generator.generate(request(difficulty=difficulty, seed=seed, style=family, width=width, height=height)).canonical_bytes()
    assert accepted >= 100
    assert accepted == 120
    assert violations == []


def test_review_candidate_digest_inputs_are_stable() -> None:
    result = _generator().generate(request(style="FACE_EMBLEM"))
    assert hashlib.sha256(result.canonical_bytes()).hexdigest() == result.digest()
