import json
import re
from pathlib import Path


ROOT = Path("review/m10")


def test_c002_metrics_report_contains_attempt_diversity_and_structure_evidence() -> None:
    report = json.loads((ROOT / "M10_METRICS_REPORT.json").read_text(encoding="utf-8"))
    assert report["attempts_total"] >= 100
    assert report["accepted_count"] == 100
    assert report["rejected_count"] >= 0
    assert report["duplicate_count"] >= 0
    assert len(report["attempt_ledger"]) == report["attempts_total"]
    assert sum(item["status"] == "ACCEPTED" for item in report["attempt_ledger"]) == 100
    assert all(item["rejection_codes"] == [] for item in report["attempt_ledger"] if item["status"] == "ACCEPTED")
    assert report["diversity"]["occupancy_mask_similarity"]["median"] is not None
    assert report["diversity"]["color_layout_similarity"]["median"] is not None
    assert len(report["diversity"]["nearest_neighbors"]) == 100
    assert report["zero_grid_mutation"]["verified"] is True
    assert report["root_seed_and_selection"]["all_formulas_executed"] is True
    assert report["family_counts"] and report["recipe_counts"] and report["strategy_counts"]


def test_c002_metrics_markdown_and_html_are_local_and_card_complete() -> None:
    markdown = (ROOT / "M10_METRICS_REPORT.md").read_text(encoding="utf-8")
    html = (ROOT / "M10_REVIEW_INDEX.html").read_text(encoding="utf-8")
    assert "M10_METRICS_REPORT" in markdown
    assert "https://" not in html and "http://" not in html
    cards = re.findall(r'<article class="card".*?</article>', html, flags=re.DOTALL)
    assert len(cards) == 100
    manifest = json.loads((ROOT / "M10_REVIEW_MANIFEST.json").read_text(encoding="utf-8"))
    for entry in manifest["entries"]:
        card = next(card for card in cards if f'data-candidate="{entry["candidate_id"]}"' in card)
        assert entry["grid_hash"] in card
        assert entry["difficulty"] in card and entry["mode"] in card
        assert "PENDING_OWNER_REVIEW" in card
        assert f'{entry["resolved_dimensions"]["width"]}x{entry["resolved_dimensions"]["height"]}' in card


def test_c002_gate_matrix_enumerates_every_release_gate_without_self_acceptance() -> None:
    matrix = json.loads((ROOT / "M10_V1_GATE_MATRIX.json").read_text(encoding="utf-8"))
    assert {gate["id"] for gate in matrix["release_gates"]} == {f"PAG-{number}" for number in range(1035, 1050)}
    assert next(gate for gate in matrix["release_gates"] if gate["id"] == "PAG-1048")["status"] == "PENDING_INDEPENDENT_ACCEPTANCE"
    assert {gate["status"] for gate in matrix["owner_gates"]} == {"PENDING_OWNER_REVIEW"}
    assert matrix["review_status"] == "PENDING_OWNER_REVIEW"


def test_c002_attribution_reaudit_is_per_reference_and_explicit() -> None:
    report = json.loads((ROOT / "M10_THIRD_PARTY_ATTRIBUTION_REAUDIT.json").read_text(encoding="utf-8"))
    assert len(report["references"]) == 4
    for reference in report["references"]:
        assert reference["expected_pinned_source"].startswith("https://github.com/")
        assert len(reference["commit"]) == 40
        assert reference["license_notice_presence"]["THIRD_PARTY_NOTICES.md"] is True
        assert reference["adapted_source_comment_evidence"]
        assert reference["findings"] == {"stale": [], "missing": [], "extra": []}
