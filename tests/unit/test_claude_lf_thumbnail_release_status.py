"""Owner 2026-11-10: LF thumbnails of already-solved PNGs said SOURCE_ONLY whenever no
batch job was restored; they must show the current Release Pool status."""
import subprocess
from pathlib import Path

import pytest

from test_claude_p0a_pixellab_row_classification import _godot

ROOT = Path(__file__).resolve().parents[2]
GD = r'''
extends SceneTree
func _init() -> void:
	var ui = load("res://scripts/factory_studio_exact_ui.gd").new()
	ui.set("_owner_release_archive", {"records": [{"source_id": "owner-upload-x", "status": "READY"}]})
	var ok: bool = ui.call("_runtime_source_status_caption", "owner-upload-x", "ALREADY_IMPORTED") == "READY" \
		and ui.call("_runtime_source_status_caption", "owner-upload-y", "ALREADY_IMPORTED") == "REUSED"
	ui.free()
	print("THUMB_CHECK ", "PASS" if ok else "FAIL")
	quit(0 if ok else 1)
'''


def test_thumbnail_caption_uses_release_pool_status_without_restored_batch() -> None:
    godot = _godot()
    if godot is None:
        pytest.skip("Godot 4 executable not available")
    script = ROOT / "level_factory" / "tests" / "_claude_thumb_check.gd"
    script.write_text(GD, encoding="utf-8")
    try:
        out = subprocess.run([godot, "--headless", "--path", str(ROOT / "level_factory"), "--script",
                              "res://tests/_claude_thumb_check.gd"], capture_output=True, text=True, timeout=180)
    finally:
        script.unlink(missing_ok=True)
    assert "THUMB_CHECK PASS" in out.stdout + out.stderr, (out.stdout + out.stderr)[-2000:]
