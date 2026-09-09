"""Committed M06 review-pack coverage checks."""

import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).parents[2]


def _topology_digest(cells: list[int]) -> str:
    return hashlib.sha256(bytes(cells)).hexdigest()


def test_m06_review_manifest_is_self_contained_and_complete() -> None:
    manifest = json.loads((ROOT / "review/m06/m06_review_manifest.json").read_text(encoding="utf-8"))
    entries = manifest["entries"]
    assert manifest["candidate_count"] == len(entries) >= 12
    assert {entry["strategy"] for entry in entries} == {
        "MASK_GEOMETRY_RULE_COLOR_REGIONS", "RULE_GEOMETRY_MASK_SYMMETRY",
        "RULE_BASE_WFC_DETAIL", "MASK_BASE_WFC_DETAIL",
    }
    assert {entry["difficulty"] for entry in entries} == {"EASY", "MEDIUM", "HARD", "VERY_HARD"}
    assert any(entry["dimensions"][0] != entry["dimensions"][1] for entry in entries)
    for entry in entries:
        assert entry["final_topology_digest"] and entry["final_logical_grid_digest"] and entry["final_result_digest"]
        width, height = entry["dimensions"]
        topology = entry["topology_evidence"]
        assert set(topology) == {"before", "after", "final"}
        assert all(len(topology[name]) == width * height for name in topology)
        assert topology["before"] == topology["final"] if entry["strategy"] in {"MASK_GEOMETRY_RULE_COLOR_REGIONS", "RULE_BASE_WFC_DETAIL"} else topology["after"] == topology["final"]
        assert _topology_digest(topology["final"]) == entry["final_topology_digest"]
        assert all(len(stage["derived_seed"]) == 64 for stage in entry["stages"])
    html = (ROOT / "review/m06/M06_HYBRID_CONTACT_SHEET.html").read_text(encoding="utf-8")
    assert "<script" not in html.lower()
    assert "https://" not in html
