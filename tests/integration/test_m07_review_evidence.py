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


def test_contact_sheet_is_self_contained_and_nearest_neighbor_only() -> None:
    contact = (REVIEW_ROOT / "M07_QUALITY_CONTACT_SHEET.html").read_text(encoding="utf-8")
    lowered = contact.lower()
    assert "<script" not in lowered
    assert "<link" not in lowered
    assert "http://" not in lowered and "https://" not in lowered
    assert "image-rendering:pixelated" in lowered
    assert "interpolation" not in lowered
    assert "cdn" not in lowered


def test_review_serialization_is_reproducible_without_machine_paths() -> None:
    entries = [ReviewEntry("fixture", 5, 5, ["C01"] * 25, mode="FIXTURE", seed=1)]
    first = json.dumps(build_review_manifest(entries), sort_keys=True, separators=(",", ":"))
    second = json.dumps(build_review_manifest(entries), sort_keys=True, separators=(",", ":"))
    assert first == second
    assert "C:\\" not in first
    assert "/Users/" not in first
    assert build_contact_sheet(entries) == build_contact_sheet(entries)
