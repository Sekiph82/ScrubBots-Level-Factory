import hashlib
import json
from pathlib import Path

from scrubbots_pixel_factory.core import GenerationRequest
from tests.support.deterministic_probe import DeterministicContractProbeGenerator


FIXTURES = json.loads((Path(__file__).with_name("m02_fixtures.json")).read_text(encoding="utf-8"))


def test_four_difficulty_golden_fixtures_are_byte_stable() -> None:
    generator = DeterministicContractProbeGenerator()
    for fixture in FIXTURES:
        request = GenerationRequest(
            difficulty=fixture["difficulty"],
            seed=fixture["seed"],
            generator_mode=fixture["generator_mode"],
            generator_options={"namespace": "probe", "version": 1, "values": {"fixture": fixture["name"]}},
        )
        result = generator.generate(request)
        assert (result.width, result.height) == tuple(fixture["dimensions"])
        assert list(result.used_palette) == fixture["palette"]
        assert dict(result.provenance["stage_seeds"]) == fixture["stage_seeds"]
        assert hashlib.sha256("\n".join(result.logical_grid).encode("utf-8")).hexdigest() == fixture["grid_sha256"]
        assert result.digest() == fixture["result_sha256"]
        assert result.canonical_bytes() == generator.generate(request).canonical_bytes()
