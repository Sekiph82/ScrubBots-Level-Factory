import html
import json
from pathlib import Path

from scrubbots_pixel_factory.quality import QualityCode, ReviewEntry, build_contact_sheet, build_review_manifest


REPO_ROOT = Path(__file__).parents[2]
REVIEW_ROOT = REPO_ROOT / "review" / "m07"


def _card_html(contact: str, candidate_id: str) -> str:
    marker = f'<article class="card" data-candidate-id="{html.escape(candidate_id, quote=True)}">'
    start = contact.index(marker)
    end = contact.index("</article>", start) + len("</article>")
    card = contact[start:end]
    assert card.count('<article class="card"') == 1
    return card


def test_committed_m07_review_manifest_is_deterministic_and_complete() -> None:
    manifest_path = REVIEW_ROOT / "m07_review_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema"] == "scrubbots-m07-review-manifest"
    assert manifest["version"] == 1
    assert len(manifest["entries"]) >= 20
    assert any(entry["quality_decision"] == "ACCEPT" for entry in manifest["entries"])
    assert any(entry["quality_decision"] == "REJECT" for entry in manifest["entries"])
    required = {
        "candidate_id", "generator_mode", "seed", "difficulty", "width", "height",
        "used_color_count", "negative_space_color", "metrics", "quality_decision",
        "rejection_codes", "grid_hash", "diversity", "human_review",
    }
    for entry in manifest["entries"]:
        assert required.issubset(entry)
        assert entry["human_review"] == ""
        assert entry["quality_decision"] in {"ACCEPT", "REJECT"}
        order = {code.value: index for index, code in enumerate(QualityCode)}
        assert entry["rejection_codes"] == sorted(entry["rejection_codes"], key=order.__getitem__)

    by_id = {entry["candidate_id"]: entry for entry in manifest["entries"]}
    assert by_id["good-02-sparse"]["metrics"]["occupied_ratio"] < 0.20
    assert by_id["good-03-multi-island"]["metrics"]["occupied_component_count"] >= 2
    assert by_id["good-04-symmetric"]["metrics"]["horizontal_symmetry_score"] == 1.0
    assert by_id["good-05-asymmetric-organic"]["metrics"]["horizontal_symmetry_score"] < 1.0
    assert by_id["good-05-asymmetric-organic"]["metrics"]["vertical_symmetry_score"] < 1.0
    assert by_id["good-06-rectangular"]["width"] != by_id["good-06-rectangular"]["height"]
    assert by_id["bad-09-exact-duplicate-a"]["diversity"]["exact_duplicate_group"] == [
        "bad-09-exact-duplicate-a", "bad-10-exact-duplicate-b"
    ]


def test_contact_sheet_is_self_contained_and_nearest_neighbor_only() -> None:
    contact = (REVIEW_ROOT / "M07_QUALITY_CONTACT_SHEET.html").read_text(encoding="utf-8")
    lowered = contact.lower()
    assert "<script" not in lowered
    assert "<link" not in lowered
    assert "http://" not in lowered and "https://" not in lowered
    assert "image-rendering:pixelated" in lowered
    assert "interpolation" not in lowered
    assert "cdn" not in lowered
    manifest = json.loads((REVIEW_ROOT / "m07_review_manifest.json").read_text(encoding="utf-8"))
    generated = next(entry for entry in manifest["entries"] if entry["candidate_id"] == "generated-01-mask")
    generated_card = _card_html(contact, "generated-01-mask")
    assert 'data-candidate-id="generated-01-mask"' in generated_card
    assert f"grid SHA-256: {generated['grid_hash']}" in generated_card
    assert f"mode={generated['generator_mode']}" in generated_card
    assert f"seed={generated['seed']}" in generated_card
    assert f"dimensions={generated['width']}×{generated['height']}" in generated_card
    assert generated["quality_decision"] in generated_card
    assert f"occupied ratio {generated['metrics']['occupied_ratio']:.4f}" in generated_card
    assert "isolated " in contact and "tiny " in contact and "dominance region/color" in contact


def test_contact_sheet_card_local_duplicate_near_duplicate_and_invalid_evidence() -> None:
    contact = (REVIEW_ROOT / "M07_QUALITY_CONTACT_SHEET.html").read_text(encoding="utf-8")
    manifest = json.loads((REVIEW_ROOT / "m07_review_manifest.json").read_text(encoding="utf-8"))
    by_id = {entry["candidate_id"]: entry for entry in manifest["entries"]}

    exact = by_id["bad-09-exact-duplicate-a"]
    exact_card = _card_html(contact, "bad-09-exact-duplicate-a")
    exact_group = exact["diversity"]["exact_duplicate_group"]
    assert f"grid SHA-256: {exact['grid_hash']}" in exact_card
    assert f"exact duplicate group: {html.escape(str(exact_group))}" in exact_card
    assert "bad-09-exact-duplicate-a" in exact_card
    assert "bad-10-exact-duplicate-b" in exact_card
    assert "bad-11-near-duplicate" not in exact_group

    near = by_id["bad-11-near-duplicate"]
    near_card = _card_html(contact, "bad-11-near-duplicate")
    partner = near["diversity"]["near_duplicate_pairs"][0]
    near_evidence = (
        f"{partner['candidate_id']} occ={partner['occupancy_mask_similarity']:.4f} "
        f"color={partner['color_layout_similarity']:.4f}"
    )
    assert f"grid SHA-256: {near['grid_hash']}" in near_card
    assert near_evidence in near_card
    assert f"{partner['occupancy_mask_similarity']:.4f}" in near_card
    assert f"{partner['color_layout_similarity']:.4f}" in near_card

    invalid = by_id["bad-08-dimension-mismatch"]
    invalid_card = _card_html(contact, "bad-08-dimension-mismatch")
    assert "UNAVAILABLE: INVALID_INPUT" in invalid_card
    assert invalid["rejection_codes"] == ["DIMENSION_MISMATCH"]
    assert "DIMENSION_MISMATCH" in invalid_card
    assert "grid SHA-256: None" not in invalid_card


def test_contact_sheet_evidence_cannot_float_across_cards() -> None:
    contact = (REVIEW_ROOT / "M07_QUALITY_CONTACT_SHEET.html").read_text(encoding="utf-8")
    manifest = json.loads((REVIEW_ROOT / "m07_review_manifest.json").read_text(encoding="utf-8"))
    near = next(entry for entry in manifest["entries"] if entry["candidate_id"] == "bad-11-near-duplicate")
    partner = near["diversity"]["near_duplicate_pairs"][0]
    near_evidence = (
        f"{partner['candidate_id']} occ={partner['occupancy_mask_similarity']:.4f} "
        f"color={partner['color_layout_similarity']:.4f}"
    )
    assert near_evidence in _card_html(contact, "bad-11-near-duplicate")

    moved = contact.replace(near_evidence, "near-evidence-removed", 1)
    moved = moved.replace("</article>", f"<p>{near_evidence}</p></article>", 1)
    assert near_evidence in moved
    assert near_evidence not in _card_html(moved, "bad-11-near-duplicate")


def test_review_serialization_is_reproducible_without_machine_paths() -> None:
    entries = [ReviewEntry("fixture", 5, 5, ["C01"] * 25, mode="FIXTURE", seed=1)]
    first = json.dumps(build_review_manifest(entries), sort_keys=True, separators=(",", ":"))
    second = json.dumps(build_review_manifest(entries), sort_keys=True, separators=(",", ":"))
    assert first == second
    assert "C:\\" not in first
    assert "/Users/" not in first
    assert build_contact_sheet(entries) == build_contact_sheet(entries)
