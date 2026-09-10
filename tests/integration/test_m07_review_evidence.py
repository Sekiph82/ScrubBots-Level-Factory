import json
from pathlib import Path

from scrubbots_pixel_factory.quality import QualityCode, ReviewEntry, build_contact_sheet, build_review_manifest


REPO_ROOT = Path(__file__).parents[2]
REVIEW_ROOT = REPO_ROOT / "review" / "m07"


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
    assert f"grid SHA-256: {generated['grid_hash']}" in contact
    assert "exact duplicate group:" in contact
    assert "near-duplicate partners:" in contact
    assert "UNAVAILABLE: INVALID_INPUT" in contact
    assert "isolated " in contact and "tiny " in contact and "dominance region/color" in contact


def test_review_serialization_is_reproducible_without_machine_paths() -> None:
    entries = [ReviewEntry("fixture", 5, 5, ["C01"] * 25, mode="FIXTURE", seed=1)]
    first = json.dumps(build_review_manifest(entries), sort_keys=True, separators=(",", ":"))
    second = json.dumps(build_review_manifest(entries), sort_keys=True, separators=(",", ":"))
    assert first == second
    assert "C:\\" not in first
    assert "/Users/" not in first
    assert build_contact_sheet(entries) == build_contact_sheet(entries)
