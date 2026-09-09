import json
from pathlib import Path

from scrubbots_pixel_factory import CANONICAL_PALETTE


REVIEW = Path("review/m03")


def test_review_manifest_is_review_only_and_covers_required_matrix() -> None:
    from scrubbots_pixel_factory.generators import FAMILY_NAMES
    manifest = json.loads((REVIEW / "m03_review_manifest.json").read_text(encoding="utf-8"))
    assert manifest["evidence_type"] == "review-only / non-production / M03 manual audit evidence"
    candidates = manifest["candidates"]
    assert manifest["candidate_count"] == 40 == len(candidates)
    assert {candidate["family"] for candidate in candidates} == set(FAMILY_NAMES)
    assert {candidate["difficulty"] for candidate in candidates} == {"EASY", "MEDIUM", "HARD", "VERY_HARD"}
    assert len({candidate["seed"] for candidate in candidates}) >= 3
    for candidate in candidates:
        width, height = candidate["width"], candidate["height"]
        palette = tuple(candidate["resolved_palette"])
        assert len(candidate["foreground_mask"]) == width * height
        assert len(candidate["logical_grid"]) == width * height
        assert set(candidate["logical_grid"]) == set(palette)
        assert set(candidate["logical_grid"]).issubset(set(CANONICAL_PALETTE.ids))
        assert "BG01" not in candidate["logical_grid"]
        assert 0 < sum(candidate["foreground_mask"]) < width * height
        diagnostics = candidate["diagnostics"]
        assert diagnostics["singleton_color_components"] == 0
        assert diagnostics["total_color_components"] >= len(palette)
        assert 0 < diagnostics["occupancy_pct"] < 100
        assert diagnostics["top_pairwise_jaccard"] < 1
        assert sum(diagnostics["role_counts"].values()) == width * height


def test_contact_sheet_is_self_contained_integer_block_presentation() -> None:
    html = (REVIEW / "M03_MASK_CONTACT_SHEET.html").read_text(encoding="utf-8")
    assert "<script>" in html and html.count("createElement('canvas')") >= 2 and "imageSmoothingEnabled=false" in html
    assert "http://" not in html and "https://" not in html and "cdn" not in html.lower()
    assert "C01" in html and "#E94B4B" in html
