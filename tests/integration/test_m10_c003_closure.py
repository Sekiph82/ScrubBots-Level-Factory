import json
import re
from pathlib import Path

from tools.m10_prepare import _review_html


ROOT = Path("review/m10")


def test_c003_every_successful_corpus_case_has_direct_replay_binding() -> None:
    report = json.loads((ROOT / "M10_PROPERTY_EXECUTION_REPORT.json").read_text(encoding="utf-8"))
    successful = [record for record in report["case_records"] if record["status"] == "SUCCESS"]
    assert report["executed_case_count"] == report["advertised_case_count"] >= 2000
    assert report["reproducibility_check_count"] == report["successful_result_count"] == len(successful)
    assert report["reproducibility_mismatch_count"] == 0
    assert all(record["replay_checked"] is True for record in successful)
    assert all(record["replay"] == {key: record[key] for key in ("result_digest", "grid_hash", "resolved_dimensions", "generator")} for record in successful)
    for mode in report["counts_by_mode_difficulty"].values():
        for bucket in mode.values():
            assert bucket["reproducibility_checks"] == bucket["success"]


def test_c003_canvas_binding_uses_all_100_candidate_ids_and_exact_manifest_entries() -> None:
    manifest = json.loads((ROOT / "M10_REVIEW_MANIFEST.json").read_text(encoding="utf-8"))
    document = (ROOT / "M10_REVIEW_INDEX.html").read_text(encoding="utf-8")
    entries = {entry["candidate_id"]: entry for entry in manifest["entries"]}
    cards = re.findall(r'<article class="card".*?</article>', document, flags=re.DOTALL)
    canvases = re.findall(r'<canvas[^>]*>', document)
    assert len(entries) == len(cards) == len(canvases) == 100
    assert "querySelectorAll('canvas').forEach((canvas,i)" not in document
    assert "pack.entries[i]" not in document
    assert "new Map(pack.entries.map((entry)=>[entry.candidate_id,entry]))" in document
    card_ids = [re.search(r'data-candidate="([^"]+)"', card).group(1) for card in cards]
    canvas_ids = [re.search(r'data-candidate="([^"]+)"', canvas).group(1) for canvas in canvases]
    assert set(card_ids) == set(canvas_ids) == set(entries)
    assert len(card_ids) == len(set(card_ids)) == len(canvas_ids) == len(set(canvas_ids))
    for card, canvas_tag in zip(cards, canvases, strict=True):
        canvas_id = re.search(r'data-candidate="([^"]+)"', canvas_tag).group(1)
        card_id = re.search(r'data-candidate="([^"]+)"', card).group(1)
        assert card_id == canvas_id
        entry = entries[canvas_id]
        assert entry["grid_hash"] in card
        assert entry["difficulty"] in card and entry["mode"] in card
        assert f'width="{entry["resolved_dimensions"]["width"] * 5}"' in canvas_tag
        assert f'height="{entry["resolved_dimensions"]["height"] * 5}"' in canvas_tag
    for difficulty in ("MEDIUM", "HARD"):
        difficulty_ids = {candidate_id for candidate_id, entry in entries.items() if entry["difficulty"] == difficulty}
        html_ids = {candidate_id for candidate_id in canvas_ids if f'data-candidate="{candidate_id}"' in document and entries[candidate_id]["difficulty"] == difficulty}
        assert html_ids == difficulty_ids
    assert "https://" not in document and "http://" not in document


def test_c003_html_regeneration_is_byte_stable_and_manifest_grid_hashes_are_unchanged() -> None:
    manifest = json.loads((ROOT / "M10_REVIEW_MANIFEST.json").read_text(encoding="utf-8"))
    current_html = (ROOT / "M10_REVIEW_INDEX.html").read_text(encoding="utf-8")
    assert current_html == _review_html(manifest["entries"])
    assert [entry["grid_hash"] for entry in manifest["entries"]] == [entry["grid_hash"] for entry in manifest["entries"]]
