import json
from pathlib import Path

from scrubbots_pixel_factory.generators.rules import RECIPE_NAMES, PRIMITIVE_NAMES


REVIEW = Path("review/m04")


def test_m04_review_manifest_covers_primitives_recipes_and_difficulties() -> None:
    manifest = json.loads((REVIEW / "m04_review_manifest.json").read_text(encoding="utf-8"))
    assert manifest["evidence_type"] == "review-only / non-production / M04 manual audit evidence"
    assert manifest["primitive_count"] == 12 and manifest["recipe_count"] == 7
    assert manifest["candidate_count"] == 40
    candidates = manifest["candidates"]
    assert {c["primitive"] for c in candidates if c["kind"] == "primitive"} == set(PRIMITIVE_NAMES)
    recipes = [c for c in candidates if c["kind"] == "recipe"]
    assert {c["recipe"] for c in recipes} == set(RECIPE_NAMES)
    assert {c["difficulty"] for c in recipes} == {"EASY", "MEDIUM", "HARD", "VERY_HARD"}
    assert len({c["seed"] for c in recipes}) >= 7
    for candidate in recipes:
        width, height = candidate["dimensions"]
        diagnostics = candidate["diagnostics"]
        assert len(candidate["geometry_mask"]) == width * height
        assert len(candidate["logical_grid"]) == width * height
        assert diagnostics["singleton_count"] == 0
        assert diagnostics["geometry_color_fidelity"] is True
        assert diagnostics["base_on_occupied"] == 0
        assert diagnostics["non_base_on_negative"] == 0
        assert diagnostics["max_color_dominance_pct"] <= diagnostics["effective_max_dominance_pct"]
        if len(candidate["resolved_palette"]) >= 4:
            assert diagnostics["accent_component_sizes"] and min(diagnostics["accent_component_sizes"]) >= 2
        assert set(candidate["logical_grid"]) == set(candidate["resolved_palette"])

    pocket = next(c for c in candidates if c["kind"] == "primitive" and c["primitive"] == "POCKET")
    assert pocket["diagnostics"]["pocket_carves_only"] is True
    assert pocket["diagnostics"]["carved_cells"] >= 2


def test_m04_contact_sheet_is_self_contained_integer_block_rendering() -> None:
    html = (REVIEW / "M04_RULES_CONTACT_SHEET.html").read_text(encoding="utf-8")
    assert html.count("createElement('canvas')") >= 1
    assert "['geometry_mask','logical_grid']" in html
    assert "imageSmoothingEnabled=false" in html
    assert "http://" not in html and "https://" not in html and "cdn" not in html.lower()
