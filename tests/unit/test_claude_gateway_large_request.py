"""P0-B regression: Studio requests larger than the Windows command-line limit
(32767 chars) failed to launch, returned ERROR, and the Level Factory restore
mapped that ERROR to "Batch mismatch" (196 Pending + 320 active source IDs)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from test_claude_p0a_pixellab_row_classification import _godot

ROOT = Path(__file__).resolve().parents[2]

GD = r'''
extends SceneTree
func _init() -> void:
	var gateway = load("res://scripts/factory_core_gateway.gd").new()
	var ids: Array = []
	for i in range(600):
		ids.append("owner-upload-%064x" % i)
	var prepared: Dictionary = gateway.prepare_studio_extension_call("claude-large-request-probe", {"source_ids": ids})
	var size := str(prepared.get("request_base64", "")).length()
	var result: Dictionary = gateway.execute_prepared_studio_extension_call(prepared)
	var err := str(result.get("error", ""))
	var ok := size > 32767 and "unsupported Studio extension operation: claude-large-request-probe" in err
	print("GATEWAY_CHECK ", "PASS" if ok else "FAIL", " b64=", size, " state=", result.get("state"), " err=", err.left(200))
	quit(0 if ok else 1)
'''


def test_large_studio_request_reaches_launcher() -> None:
    godot = _godot()
    if godot is None:
        pytest.skip("Godot 4 executable not available")
    script = ROOT / "level_factory" / "tests" / "_claude_gateway_check.gd"
    script.write_text(GD, encoding="utf-8")
    try:
        proc = subprocess.run(
            [godot, "--headless", "--path", str(ROOT / "level_factory"), "--script", "res://tests/_claude_gateway_check.gd"],
            capture_output=True, text=True, timeout=300,
        )
    finally:
        script.unlink(missing_ok=True)
    out = proc.stdout + proc.stderr
    assert "GATEWAY_CHECK PASS" in out, out[-3000:]
    leftovers = list((ROOT / "data/Level Factory/Runtime/studio-requests").glob("claude-large-request-probe-*.json"))
    assert leftovers == []
