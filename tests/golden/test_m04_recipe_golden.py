import hashlib
import json
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest
from scrubbots_pixel_factory.generators.rules import RuleCandidate, RuleShapeGenerator, color_component_sizes


FIXTURES = json.loads(Path(__file__).with_name("m04_recipe_fixtures.json").read_text(encoding="utf-8"))


def test_all_m04_recipe_goldens_are_byte_stable() -> None:
    generator = RuleShapeGenerator()
    for fixture in FIXTURES:
        width, height = fixture["dimensions"]
        request = GenerationRequest(difficulty=fixture["difficulty"], seed=fixture["seed"], generator_mode="RULES", style=fixture["recipe"], width=width, height=height)
        candidate = generator.generate_candidate(request)
        assert isinstance(candidate, RuleCandidate)
        assert candidate.recipe.version == fixture["version"]
        assert list(candidate.colors) == fixture["palette"]
        assert candidate.canvas.geometry_digest() == fixture["geometry_sha256"]
        assert hashlib.sha256("\n".join(candidate.logical_grid).encode()).hexdigest() == fixture["grid_sha256"]
        assert candidate.result.digest() == fixture["result_sha256"]
        assert len(candidate.canvas.occupied) == fixture["occupancy"]
        assert {key: list(value) for key, value in color_component_sizes(candidate.logical_grid, width, height).items()} == fixture["color_components"]
