import json
import re
from pathlib import Path

from scrubbots_pixel_factory import logical_grid_hash


ROOT = Path("review/m10")


def test_m10_review_pack_has_exact_owner_review_shape() -> None:
    manifest = json.loads((ROOT / "M10_REVIEW_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "scrubbots-m10-review-manifest"
    assert manifest["entry_count"] == 100
    assert manifest["counts_by_difficulty"] == {"EASY": 25, "HARD": 25, "MEDIUM": 25, "VERY_HARD": 25}
    assert manifest["wfc_visual_status"] == "WFC_VISUAL_PACK_SKIPPED_NO_APPROVED_EXEMPLAR"
    entries = manifest["entries"]
    assert all(entry["status"] == "PENDING_OWNER_REVIEW" for entry in entries)
    assert len({entry["candidate_id"] for entry in entries}) == 100
    assert len({entry["grid_hash"] for entry in entries}) == 100
    for entry in entries:
        assert entry["grid_hash"] == logical_grid_hash(entry["resolved_dimensions"]["width"], entry["resolved_dimensions"]["height"], entry["logical_grid"])
        assert entry["quality"]["accepted"] is True
        assert entry["owner_notes"] == ""


def test_m10_review_html_binds_each_card_to_its_own_hash() -> None:
    manifest = json.loads((ROOT / "M10_REVIEW_MANIFEST.json").read_text(encoding="utf-8"))
    document = (ROOT / "M10_REVIEW_INDEX.html").read_text(encoding="utf-8")
    assert "https://" not in document and "http://" not in document
    cards = re.findall(r'<article class="card".*?</article>', document, flags=re.DOTALL)
    assert len(cards) == 100
    for entry in manifest["entries"]:
        card = next(card for card in cards if f'data-candidate="{entry["candidate_id"]}"' in card)
        assert entry["candidate_id"] in card
        assert entry["grid_hash"] in card
        assert "PENDING_OWNER_REVIEW" in card
        assert "ACCEPT (owner review pending)" in card


def test_m10_gate_matrix_preserves_owner_boundaries_and_attribution() -> None:
    matrix = json.loads((ROOT / "M10_V1_GATE_MATRIX.json").read_text(encoding="utf-8"))
    assert matrix["review_status"] == "PENDING_OWNER_REVIEW"
    assert {gate["id"] for gate in matrix["gates"]} == {"PAG-1033", "PAG-1034", "PAG-1050"}
    assert all(gate["status"] == "PENDING_OWNER_REVIEW" for gate in matrix["gates"])
    attribution = json.loads((ROOT / "M10_THIRD_PARTY_ATTRIBUTION_REAUDIT.json").read_text(encoding="utf-8"))
    assert attribution["result"] == "PASS"
    assert attribution["copied_source"] is False
    assert attribution["copied_artwork"] is False
    assert attribution["runtime_dependency_added"] is False
