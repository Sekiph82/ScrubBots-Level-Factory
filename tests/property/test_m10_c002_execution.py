import json
from pathlib import Path

from scrubbots_pixel_factory import DeterministicRNG, logical_grid_hash


ROOT = Path("review/m10")


def test_c002_report_proves_full_valid_corpus_execution() -> None:
    corpus = json.loads((ROOT / "M10_PROPERTY_CORPUS.json").read_text(encoding="utf-8"))
    report = json.loads((ROOT / "M10_PROPERTY_EXECUTION_REPORT.json").read_text(encoding="utf-8"))
    assert corpus["case_count"] >= 2000
    assert report["advertised_case_count"] == corpus["case_count"]
    assert report["executed_case_count"] == corpus["case_count"]
    assert report["reproducibility_mismatch_count"] == 0
    assert report["invalid_corpus"]["all_rejected_without_traceback"] is True
    for mode in ("MASK", "RULES", "HYBRID", "AUTO", "WFC"):
        assert sum(report["counts_by_mode_difficulty"][mode][difficulty]["total"] for difficulty in ("EASY", "MEDIUM", "HARD", "VERY_HARD")) > 0
    assert any(record["grid_hash"] for record in report["case_records"] if record["difficulty"] == "VERY_HARD")


def test_c002_review_seed_formula_matches_manifest() -> None:
    manifest = json.loads((ROOT / "M10_REVIEW_MANIFEST.json").read_text(encoding="utf-8"))
    entry = next(item for item in manifest["entries"] if item["difficulty"] == "HARD" and item["candidate_id"].endswith("-07"))
    metrics = json.loads((ROOT / "M10_METRICS_REPORT.json").read_text(encoding="utf-8"))
    attempt = next(item["attempt_index"] for item in metrics["attempt_ledger"] if item["difficulty"] == "HARD" and item["candidate_id"].endswith("-07") and item["status"] == "ACCEPTED")
    expected = DeterministicRNG(manifest["root_seed"]).child(f"slot/HARD/07/attempt/{attempt:02d}").next_bytes(32).hex()
    assert entry["seed"] == {"type": "string", "value": expected}
    assert manifest["root_seed"] == "m10-review-root-v2"
    assert manifest["root_rng_algorithm"] == "SCRUBBOTS_SHA256_COUNTER_V1"
