import json
from pathlib import Path


REVIEW = Path(__file__).parents[2] / "review" / "m05"


def test_m05_review_pack_has_paired_exemplar_and_output_evidence() -> None:
    manifest = json.loads((REVIEW / "m05_review_manifest.json").read_text(encoding="utf-8"))
    candidates = manifest["candidates"]
    assert manifest["candidate_count"] >= 12
    assert len(candidates) == manifest["candidate_count"]
    assert {candidate["exemplar_id"] for candidate in candidates} == {
        "wfc-synthetic-easy-3", "wfc-synthetic-medium-6", "wfc-synthetic-hard-8", "wfc-synthetic-very-hard-10"
    }
    assert any(candidate["dimensions"][0] != candidate["dimensions"][1] for candidate in candidates)
    assert all(candidate["exemplar"]["width"] * candidate["exemplar"]["height"] == len(candidate["exemplar"]["logical_pixels"]) for candidate in candidates)
    assert all(candidate["dimensions"][0] * candidate["dimensions"][1] == len(candidate["logical_grid"]) for candidate in candidates)
    assert all(candidate["metadata"]["extracted_pattern_count"] == candidate["metadata"]["raw_extracted_window_count"] for candidate in candidates)
    html = (REVIEW / "M05_WFC_CONTACT_SHEET.html").read_text(encoding="utf-8")
    assert "Exemplar motif" in html and "Generated WFC output" in html
