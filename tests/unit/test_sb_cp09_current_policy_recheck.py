from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/security/MOBILE_STORE_POLICY_RECHECK_2026-10-14.md"


def test_current_policy_recheck_is_dated_official_and_keeps_release_gates_open() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert "Checked on 2026-10-14 UTC" in report
    assert "https://support.google.com/googleplay/android-developer/answer/16559646?hl=en" in report
    assert "https://support.google.com/googleplay/android-developer/answer/17006354?hl=en" in report
    assert "https://developer.apple.com/app-store/review/guidelines/" in report
    assert "executable code" in report and "download size" in report
    assert "requires a separate owner decision" in report
    assert "Final platform policy review" in report
    assert "not legal advice, a store approval" in report
