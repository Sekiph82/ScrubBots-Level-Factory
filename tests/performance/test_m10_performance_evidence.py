import json
from pathlib import Path


REPORT = Path("review/m10/M10_PERFORMANCE_REPORT.json")


def test_m10_performance_report_contains_measured_statistics_and_budgets() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["schema"] == "scrubbots-m10-performance-report"
    assert report["methodology"]["clock"] == "time.perf_counter_ns"
    assert report["methodology"]["memory"] == "tracemalloc peak"
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
    assert "distinct cases" in gate["budget_derivation"]
    for summary in summaries:
        group = next(group for group in report["groups"] if group["mode"] == summary["mode"] and group["strategy"] == summary["strategy"] and group["difficulty"] == summary["difficulty"] and group["dimensions"] == summary["dimensions"])
        assert summary["sample_count"] == len(group["samples"])
        assert all("elapsed_ns" in sample and "peak_memory_bytes" in sample for sample in group["samples"])
