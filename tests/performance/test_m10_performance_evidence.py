import json
from pathlib import Path


REPORT = Path("review/m10/M10_PERFORMANCE_REPORT.json")


def test_m10_performance_report_contains_measured_statistics_and_budgets() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["schema"] == "scrubbots-m10-performance-report"
    assert report["harness"]["clock"] == "time.perf_counter_ns"
    assert report["harness"]["memory"] == "tracemalloc peak"
    summaries = report["summaries"]
    assert len(summaries) >= 20
    assert {summary["mode"] for summary in summaries} >= {"MASK", "RULES", "WFC", "HYBRID"}
    for difficulty in ("EASY", "MEDIUM", "HARD", "VERY_HARD"):
        assert any(summary["mode"] == "MASK" and summary["difficulty"] == difficulty for summary in summaries)
        assert any(summary["mode"] == "RULES" and summary["difficulty"] == difficulty for summary in summaries)
        assert any(summary["mode"] == "WFC" and summary["difficulty"] == difficulty for summary in summaries)
    gate = report["PAG-0441_RULES_59x59"]
    assert gate["mode"] == "RULES"
    assert gate["dimensions"] == [59, 59]
    assert gate["sample_count"] >= 5
    assert gate["median_ns"] > 0 and gate["p95_ns"] >= gate["median_ns"]
    assert gate["peak_memory_bytes"] > 0
    assert gate["proposed_budget_ns"] >= gate["p95_ns"]
    assert "measured" in gate["derivation"]
    for summary in summaries:
        assert summary["sample_count"] == len(next(case["samples"] for case in report["cases"] if case["mode"] == summary["mode"] and case["strategy"] == summary["strategy"] and case["difficulty"] == summary["difficulty"] and case["dimensions"] == summary["dimensions"]))
        assert all("elapsed_ns" in sample and "peak_memory_bytes" in sample for case in report["cases"] for sample in case["samples"] if case["mode"] == summary["mode"] and case["strategy"] == summary["strategy"] and case["difficulty"] == summary["difficulty"] and case["dimensions"] == summary["dimensions"])
