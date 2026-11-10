"""Owner 2026-11-10: Run Batch pressed while the Level Factory startup Final scan was
running was rejected as ALREADY_RUNNING and nothing ever started. It must wait and
open the batch review automatically when the scan finishes."""
import subprocess
from pathlib import Path

import pytest

from test_claude_p0a_pixellab_row_classification import _godot

ROOT = Path(__file__).resolve().parents[2]
GD = r'''
extends SceneTree
func _init() -> void:
	var ui = load("res://scripts/factory_studio_exact_ui.gd").new()
	ui.set("_operation_running", true)
	ui.set("_startup_source_inventory_loaded", false)
	ui.call("_run_batch")
	var events: Array = ui.get("_pixel_art_activity_events")
	var last: Dictionary = events[-1] if not events.is_empty() else {}
	var ok: bool = ui.get("_pixel_batch_start_after_startup") == true and str(last.get("state", "")) == "WAITING_FOR_STARTUP_SCAN"
	ui.free()
	print("WAIT_CHECK ", "PASS" if ok else "FAIL")
	quit(0 if ok else 1)
'''


def test_run_batch_during_startup_scan_is_remembered() -> None:
    godot = _godot()
    if godot is None:
        pytest.skip("Godot 4 executable not available")
    script = ROOT / "level_factory" / "tests" / "_claude_wait_check.gd"
    script.write_text(GD, encoding="utf-8")
    try:
        out = subprocess.run([godot, "--headless", "--path", str(ROOT / "level_factory"), "--script",
                              "res://tests/_claude_wait_check.gd"], capture_output=True, text=True, timeout=180)
    finally:
        script.unlink(missing_ok=True)
    assert "WAIT_CHECK PASS" in out.stdout + out.stderr, (out.stdout + out.stderr)[-2000:]
