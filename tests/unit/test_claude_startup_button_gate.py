"""Owner 2026-11-10: action buttons stay disabled until startup has settled, then enable."""
import subprocess
from pathlib import Path

import pytest

from test_claude_p0a_pixellab_row_classification import _godot

ROOT = Path(__file__).resolve().parents[2]
GD = r'''
extends SceneTree
func _init() -> void:
	var ui = load("res://scripts/factory_studio_exact_ui.gd").new()
	var run := Button.new(); run.name = "RunBatch"
	var tab := Button.new(); tab.name = "PixelArtTab"
	var pool := Button.new(); pool.name = "ReleaseStaging"
	var buttons: Array = ui.get("_master_buttons")
	buttons.append(run); buttons.append(tab); buttons.append(pool)
	ui.call("_apply_startup_gate")
	var loading: bool = run.disabled and pool.disabled and not tab.disabled
	ui.set("_startup_inventory_settled", true); ui.set("_startup_source_inventory_loaded", true)
	ui.set("_startup_release_archive_settled", true)
	ui.set("_startup_pending_batch_restore_started", true); ui.set("_batch_restore_pending", false)
	ui.call("_apply_startup_gate")
	var core_open: bool = not run.disabled and pool.disabled
	ui.set("_release_pool_loaded", true)
	ui.call("_apply_startup_gate")
	var all_open: bool = not run.disabled and not pool.disabled and ui.get("_startup_gate_released") == true
	var ui2 = load("res://scripts/factory_studio_exact_ui.gd").new()
	ui2.set("_startup_inventory_settled", true); ui2.set("_startup_source_inventory_loaded", false)
	var failed_unlocks: bool = ui2.call("_startup_core_ready")
	print("GATE_CHECK ", "PASS" if loading and core_open and all_open and failed_unlocks else "FAIL", " ", [loading, core_open, all_open, failed_unlocks])
	run.free(); tab.free(); pool.free(); ui2.free()
	quit(0)
'''


def test_action_buttons_wait_for_startup_and_never_stay_locked() -> None:
    godot = _godot()
    if godot is None:
        pytest.skip("Godot 4 executable not available")
    script = ROOT / "level_factory" / "tests" / "_claude_gate_check.gd"
    script.write_text(GD, encoding="utf-8")
    try:
        out = subprocess.run([godot, "--headless", "--path", str(ROOT / "level_factory"), "--script",
                              "res://tests/_claude_gate_check.gd"], capture_output=True, text=True, timeout=180)
    finally:
        script.unlink(missing_ok=True)
    assert "GATE_CHECK PASS" in out.stdout + out.stderr, (out.stdout + out.stderr)[-2500:]
