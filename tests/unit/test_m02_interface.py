from scrubbots_pixel_factory.core import DeterministicRNG, GenerationRequest, PixelGenerator
from tests.support.deterministic_probe import DeterministicContractProbeGenerator


def test_test_only_probe_implements_explicit_pixel_generator_protocol() -> None:
    generator = DeterministicContractProbeGenerator()
    assert isinstance(generator, PixelGenerator)
    request = GenerationRequest(difficulty="EASY", seed=17, generator_mode="HYBRID")
    result = generator.generate(request, DeterministicRNG(request.seed))
    assert result.is_success
