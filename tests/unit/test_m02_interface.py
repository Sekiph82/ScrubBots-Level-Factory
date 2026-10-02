from dataclasses import fields

import pytest

from scrubbots_pixel_factory.core import DeterministicRNG
from scrubbots_pixel_factory.core import PixelGenerator
from scrubbots_pixel_factory.core.request import GenerationRequest, RequestContractError
from scrubbots_pixel_factory.core.request import LegacyGenerationRequest
from tests.support.deterministic_probe import DeterministicContractProbeGenerator


def test_test_only_probe_implements_explicit_pixel_generator_protocol() -> None:
    generator = DeterministicContractProbeGenerator()
    request = GenerationRequest(seed=17, width=20, height=20, generator_mode="HYBRID")
    assert isinstance(generator, PixelGenerator)
    result = generator.generate(request, DeterministicRNG(request.seed))
    assert result.is_success


def test_current_request_is_difficulty_free_and_requires_explicit_dimensions() -> None:
    request = GenerationRequest(seed="current-v3", width=20, height=59)
    assert request.schema_version == 3
    assert "difficulty" not in {field.name for field in fields(GenerationRequest)}
    assert not hasattr(request, "difficulty")
    canonical = request.canonical_dict()
    assert "difficulty" not in canonical
    assert canonical["schema_version"] == 3
    assert canonical["background_intent"] == "BACKGROUND"
    with pytest.raises(TypeError):
        GenerationRequest(seed=1)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        GenerationRequest(seed=1, width=20, height=20, difficulty="EASY")  # type: ignore[call-arg]


def test_legacy_difficulty_request_is_explicitly_separate() -> None:
    historical = LegacyGenerationRequest("EASY", 17, "HYBRID", width=20, height=20, schema_version=2)
    assert historical.difficulty.value == "EASY"
    assert historical.canonical_dict()["difficulty"] == "EASY"
    with pytest.raises(TypeError):
        GenerationRequest(seed=17, width=20, height=20, generator_mode="HYBRID", difficulty="EASY")  # type: ignore[call-arg]
