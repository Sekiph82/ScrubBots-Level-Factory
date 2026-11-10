"""P0-A regression: a generated PixelLab 4x4 atlas with a per-frame Level Factory
intake rejection must count as a completed (billed) batch row, not a failure.

Owner incident 2026-11-10: row 1/176 produced a 224x224 atlas, 16 Final PNGs
(LF-000305..320) and 15 imported sources; frame 07 failed MINIMUM_ARTWORK.
The UI required pass_count == 16 and stopped the batch (STOPPED_AFTER_FAILURE,
"Provider returned no detailed reason.").
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "level_factory/scripts/factory_studio_exact_ui.gd"


def _function(source: str, name: str) -> str:
    start = source.index(name)
    end = source.find("\nfunc ", start + len(name))
    end2 = source.find("\nstatic func ", start + len(name))
    ends = [e for e in (end, end2) if e >= 0]
    return source[start:min(ends)] if ends else source[start:]


def test_row_success_uses_atlas_generation_not_full_intake_pass() -> None:
    source = UI.read_text(encoding="utf-8")
    poll = _function(source, "func _poll_pixel_art_worker")
    assert "int(result.get(\"pass_count\", 0)) == 16" not in poll
    assert "var row_succeeded := str(result.get(\"state\", \"\")) == \"IMPORTED\" or atlas_generated" in poll
    assert "_pixellab_result_detail(result) if atlas_generated" in poll
    # Genuine provider/transport errors still stop without retry.
    assert '"STOPPED_AFTER_FAILURE"' in poll
    assert "No retry or additional paid request was sent." in poll


def _godot() -> str | None:
    candidate = os.environ.get("GODOT_BIN") or shutil.which("godot")
    if candidate:
        return candidate
    winget = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
    for path in winget.glob("GodotEngine.GodotEngine_*/Godot_v4*_win64.exe") if winget.exists() else []:
        if "console" not in path.name:
            return str(path)
    return None


GD_CHECK = r'''
extends SceneTree
func _init() -> void:
	var ui = load("res://scripts/factory_studio_exact_ui.gd")
	var frames: Array = []
	for i in range(1, 17):
		frames.append({"index": i, "intake_status": "REJECTED" if i == 7 else "PASS", "reasons": ["MINIMUM_ARTWORK"] if i == 7 else []})
	var row1 := {"state": "SOURCES_IMPORTED_NOT_READY", "pass_count": 15, "rejected_count": 1, "atlas_path": "C:/x/PX-ATLAS-000020.png", "frame_statuses": frames}
	var all_rejected := {"state": "FRAMES_REJECTED", "pass_count": 0, "atlas_path": "C:/x/a.png", "frame_statuses": frames}
	var provider_error := {"state": "ERROR", "error": "PIXELLAB_HTTP_500"}
	var blocked := {"state": "NEEDS_OWNER_REVIEW_ACCEPTED_JOB", "reason": "x"}
	var no_atlas := {"state": "SOURCES_IMPORTED_NOT_READY", "pass_count": 15, "frame_statuses": frames}
	var ok: bool = ui._pixellab_atlas_generated(row1) and ui._pixellab_atlas_generated(all_rejected) \
		and not ui._pixellab_atlas_generated(provider_error) and not ui._pixellab_atlas_generated(blocked) \
		and not ui._pixellab_atlas_generated(no_atlas)
	var detail: String = ui._pixellab_result_detail(row1)
	ok = ok and "15/16 passed" in detail and "07 MINIMUM_ARTWORK" in detail
	print("P0A_CHECK ", "PASS" if ok else "FAIL", " ", detail)
	quit(0 if ok else 1)
'''


def test_godot_headless_classifier_on_real_row1_shape(tmp_path: Path) -> None:
    godot = _godot()
    if godot is None:
        pytest.skip("Godot 4 executable not available")
    script = ROOT / "level_factory" / "tests" / "_claude_p0a_check.gd"
    script.write_text(GD_CHECK, encoding="utf-8")
    try:
        proc = subprocess.run(
            [godot, "--headless", "--path", str(ROOT / "level_factory"), "--script", "res://tests/_claude_p0a_check.gd"],
            capture_output=True, text=True, timeout=180,
        )
    finally:
        script.unlink(missing_ok=True)
    out = proc.stdout + proc.stderr
    assert "P0A_CHECK PASS" in out, out[-3000:]
    assert proc.returncode == 0, out[-3000:]
