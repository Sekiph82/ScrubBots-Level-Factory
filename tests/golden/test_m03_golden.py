import hashlib
import json
from pathlib import Path

from scrubbots_pixel_factory.core import GenerationRequest


FIXTURES = json.loads(Path(__file__).with_name("m03_fixtures.json").read_text(encoding="utf-8"))


def test_m03_family_goldens_are_byte_stable() -> None:
    from scrubbots_pixel_factory.generators import MaskSpriteGenerator
    from scrubbots_pixel_factory.generators.mask import MaskCandidate
    generator = MaskSpriteGenerator()
    for fixture in FIXTURES:
        request = GenerationRequest(
            difficulty=fixture["difficulty"],
            seed=fixture["seed"],
            generator_mode="MASK",
            style=fixture["family"],
            width=fixture["dimensions"][0],
            height=fixture["dimensions"][1],
        )
        candidate = generator.generate_candidate(request)
        assert isinstance(candidate, MaskCandidate)
        result = candidate.result
        assert result.is_success
        assert list(result.used_palette) == fixture["palette"]
        assert hashlib.sha256(bytes(candidate.mask.foreground_cells)).hexdigest() == fixture["foreground_mask_sha256"]
        assert hashlib.sha256("\n".join(result.logical_grid).encode("utf-8")).hexdigest() == fixture["grid_sha256"]
        assert result.digest() == fixture["result_sha256"]
        assert result.canonical_bytes() == generator.generate(request).canonical_bytes()
