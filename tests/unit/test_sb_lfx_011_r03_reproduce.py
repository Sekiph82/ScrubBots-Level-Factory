from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).parents[2]


def test_r03_real_studio_reproduce_survives_draft_divergence_and_source_only_record() -> None:
    result = subprocess.run(
        ["godot_console.exe", "--headless", "--path", "level_factory", "--script", "res://tests/factory_studio_exact_reproduce_r03_integration_suite.gd"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SB-LFX-011-C001-R03 EXACT REPRODUCE divergence integration PASS" in result.stdout
