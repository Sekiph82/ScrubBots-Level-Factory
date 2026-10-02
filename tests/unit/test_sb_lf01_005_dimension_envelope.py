from pathlib import Path

import pytest

from scrubbots_pixel_factory import GenerationRequest, QualityPolicy, evaluate_grid
from scrubbots_pixel_factory.contracts import validate_current_dimensions
from scrubbots_pixel_factory.contracts import PRODUCTION_DIMENSION_ENVELOPE
from scrubbots_pixel_factory.core import RequestContractError
from scrubbots_pixel_factory.core.request import LegacyGenerationRequest
from scrubbots_pixel_factory.generators.mask import MaskSpriteGenerator


RECTANGLES = ((20, 20), (20, 59), (59, 20), (59, 59), (23, 47), (52, 31))


@pytest.mark.parametrize("width,height", RECTANGLES)
def test_current_request_accepts_explicit_legal_rectangles(width, height) -> None:
    request = GenerationRequest(seed=f"lf01-005-{width}x{height}", width=width, height=height)
    assert request.resolve_dimensions() == (width, height)
    assert validate_current_dimensions(width, height) == (width, height)


@pytest.mark.parametrize("width,height", ((19, 20), (20, 19), (60, 20), (20, 60)))
def test_current_request_rejects_each_axis_boundary_independently(width, height) -> None:
    with pytest.raises(RequestContractError):
        GenerationRequest(seed="invalid-boundary", width=width, height=height)


def test_current_request_never_selects_dimensions_from_seed() -> None:
    first = GenerationRequest(seed="same-seed", width=20, height=59)
    second = GenerationRequest(seed="same-seed", width=59, height=20)
    assert first.resolve_dimensions() == (20, 59)
    assert second.resolve_dimensions() == (59, 20)
    assert first.canonical_dict()["width"] == 20
    assert first.canonical_dict()["height"] == 59


def test_current_request_has_no_difficulty_semantics() -> None:
    small = GenerationRequest(seed="palette-stable", width=20, height=20)
    large = GenerationRequest(seed="palette-stable", width=59, height=59)
    assert small.resolve_palette_subset() == large.resolve_palette_subset()
    cells = ["C01", "C02", "C03"] * (59 * 59 // 3) + ["C01"] * ((59 * 59) % 3)
    report = evaluate_grid(59, 59, cells, policy=QualityPolicy())
    assert "DIMENSION_MISMATCH" not in report.rejection_codes


def test_59x59_mask_generation_is_supported_and_rectangular_core_is_executable() -> None:
    request = GenerationRequest(seed="lf01-005-59x59", width=59, height=59)
    result = MaskSpriteGenerator().generate(request)
    assert result.is_success
    assert (result.width, result.height) == (59, 59)
    assert len(result.logical_grid) == 59 * 59


def test_legacy_request_remains_explicit_and_does_not_define_current_defaults() -> None:
    historical = LegacyGenerationRequest("EASY", "legacy-v2", "MASK", schema_version=2)
    current = GenerationRequest(seed="legacy-v2", width=20, height=20)
    assert historical.schema_version == 2
    assert current.schema_version == 3
    assert historical.canonical_dict()["difficulty"] == "EASY"
    with pytest.raises(RequestContractError):
        LegacyGenerationRequest("EASY", "version-gate", "MASK", width=20, height=30, schema_version=1)


def test_rectangular_generation_preserves_width_height_identity() -> None:
    request = GenerationRequest(seed="router-rectangle", width=23, height=47, generator_mode="MASK")
    first = MaskSpriteGenerator().generate(request)
    second = MaskSpriteGenerator().generate(request)
    assert first.is_success and second.is_success
    assert first.canonical_bytes() == second.canonical_bytes()
    assert (first.width, first.height) == (23, 47)


def test_workload_guidance_is_advisory_and_uses_canonical_envelope() -> None:
    readme = (Path(__file__).parents[2] / "README.md").read_text(encoding="utf-8")
    guidance = " ".join(readme.split("### Dimension and workload guidance", 1)[1].split("Stable domain exit codes are:", 1)[0].split())
    envelope = f"`{PRODUCTION_DIMENSION_ENVELOPE.minimum}..{PRODUCTION_DIMENSION_ENVELOPE.maximum}`"
    assert f"width and height are independently legal from {envelope} inclusive" in guidance
    assert "Every rectangle inside this envelope remains legal regardless of difficulty label." in guidance
    assert "Larger board area may require more processing/resources than smaller board area." in guidance
    assert "advisory only" in guidance
    assert "never changes legality" in guidance
    assert "not difficulty" in guidance
