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
        assignments = diagnostics["role_to_color_assignments"]
        observed = diagnostics["observed_roles_by_color"]
        assert {item["color_id"] for item in assignments} == set(palette)
        assert diagnostics["role_color_purity"] is True
        assert all(observed[item["color_id"]] == [item["role"]] for item in assignments)


def test_contact_sheet_is_self_contained_integer_block_presentation() -> None:
    html = (REVIEW / "M03_MASK_CONTACT_SHEET.html").read_text(encoding="utf-8")
    assert "<script>" in html and html.count("createElement('canvas')") >= 2 and "imageSmoothingEnabled=false" in html
    assert "http://" not in html and "https://" not in html and "cdn" not in html.lower()
    assert "C01" in html and "#E94B4B" in html


def test_weak_family_review_masks_are_materially_distinct() -> None:
    manifest = json.loads((REVIEW / "m03_review_manifest.json").read_text(encoding="utf-8"))
    easy = {
        candidate["family"]: candidate["foreground_mask"]
        for candidate in manifest["candidates"]
        if candidate["difficulty"] == "EASY"
    }
    insect = easy["INSECT"]
    tree = easy["TREE_PLANT"]
    insect_tree = sum(left and right for left, right in zip(insect, tree)) / sum(
        left or right for left, right in zip(insect, tree)
    )
    assert insect_tree < 0.70
    candidates = manifest["candidates"]
    for index, candidate in enumerate(candidates):
        for other in candidates[index + 1:]:
            if (candidate["width"], candidate["height"]) != (other["width"], other["height"]):
                continue
            left, right = candidate["foreground_mask"], other["foreground_mask"]
            similarity = sum(a and b for a, b in zip(left, right)) / sum(a or b for a, b in zip(left, right))
            assert similarity < 0.80
