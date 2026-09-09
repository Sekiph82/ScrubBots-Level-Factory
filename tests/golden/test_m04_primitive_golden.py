import hashlib
import json
from pathlib import Path

from scrubbots_pixel_factory import DeterministicRNG
from scrubbots_pixel_factory.generators.rules import RuleCanvas, apply_primitive, connected_components


FIXTURES = json.loads(Path(__file__).with_name("m04_primitive_fixtures.json").read_text(encoding="utf-8"))


def test_all_m04_primitive_goldens_are_deterministic() -> None:
    for fixture in FIXTURES:
        width, height = fixture["dimensions"]
        canvas = RuleCanvas(width, height)
        geometry = apply_primitive(canvas, fixture["primitive"], DeterministicRNG(fixture["seed"]), **fixture["parameters"])
        digest = canvas.region_digest() if isinstance(geometry, dict) else canvas.geometry_digest()
        count = sum(map(len, geometry.values())) if isinstance(geometry, dict) else len(geometry)
        component_count = len(geometry) if isinstance(geometry, dict) else len(connected_components(set(geometry), canvas))
        assert digest == fixture["geometry_sha256"]
        assert count == fixture["occupied_cells"]
        assert component_count == fixture["component_count"]
        assert hashlib.sha256(canvas.geometry_bytes()).hexdigest() == canvas.geometry_digest()
