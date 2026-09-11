import json
from pathlib import Path


ROOT = Path("review/m10")


def test_c002_benchmark_manifest_has_distinct_required_sets() -> None:
    manifest = json.loads((ROOT / "M10_BENCHMARK_MANIFEST.json").read_text(encoding="utf-8"))
    groups = manifest["groups"]
    for group in groups:
        digests = [case["generator_options"] | {"seed": case["seed"]} for case in group["cases"]]
        assert len({json.dumps(value, sort_keys=True, separators=(",", ":")) for value in digests}) == len(digests)
    for difficulty in ("EASY", "MEDIUM", "HARD", "VERY_HARD"):
        for mode in ("MASK", "RULES"):
            group = next(item for item in groups if item["group"] == f"{mode}/{difficulty}")
            assert len(group["cases"]) >= 20
        for strategy in ("MASK_GEOMETRY_RULE_COLOR_REGIONS", "RULE_GEOMETRY_MASK_SYMMETRY"):
            group = next(item for item in groups if item["group"] == f"HYBRID/{strategy}/{difficulty}")
            assert len(group["cases"]) >= 20
        assert len(next(item for item in groups if item["group"] == f"WFC/{difficulty}")["cases"]) >= 10
        for strategy in ("RULE_BASE_WFC_DETAIL", "MASK_BASE_WFC_DETAIL"):
            assert len(next(item for item in groups if item["group"] == f"HYBRID/{strategy}/{difficulty}/technical")["cases"]) >= 3
    assert len(next(item for item in groups if item["group"] == "RULES/VERY_HARD/59x59/PAG-0441")["cases"]) >= 20


def test_c002_performance_report_preserves_distinct_raw_samples_and_failures() -> None:
    report = json.loads((ROOT / "M10_PERFORMANCE_REPORT.json").read_text(encoding="utf-8"))
    assert report["version"] == 2
    assert report["methodology"]["failure_denominator"].startswith("all measured cases")
    for group in report["groups"]:
        samples = group["samples"]
        assert len(samples) == len({sample["request_digest"] for sample in samples})
        assert all(sample["elapsed_ns"] > 0 and sample["peak_memory_bytes"] > 0 for sample in samples)
        summary = next(item for item in report["summaries"] if item["group"] == group["group"])
        assert summary["distinct_request_count"] == summary["sample_count"]
        assert summary["measured_max_ns"] >= summary["p95_ns"] >= summary["median_ns"]
    gate = report["PAG-0441_RULES_59x59"]
    assert gate["sample_count"] >= 20
    assert gate["distinct_request_count"] == gate["sample_count"]
    assert gate["dimensions"] == [59, 59]
    assert gate["retry_exhaustion_rate"] >= 0
