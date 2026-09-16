from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
GATE = FACTORY / "scripts" / "factory_studio_puzzle_config_gate.gd"
TARGET = FACTORY / "scripts" / "factory_studio_target_controls.gd"
INTEGRATION = FACTORY / "tests" / "factory_studio_puzzle_config_gate_integration_suite.gd"


def test_puzzle_config_gate_is_truthful_and_label_only() -> None:
    assert GATE.exists()
    assert GATE.is_relative_to(FACTORY)
    source = GATE.read_text(encoding="utf-8")
    lowered = source.lower()
    for marker in (
        'const unavailable := "unavailable"',
        'const no_approved_contract := "unavailable — no approved canonical puzzle-config edit contract"',
        '"editable_fields": [],',
        '"controls_enabled": false',
        '"mutation_available": false',
        '"validation_disposition": unvalidated_disposition',
        "no mutation controls available",
        "generationrequest target fields",
        "wfc options",
        "artwork pixels",
        "presentation labels",
    ):
        assert marker in lowered
    for forbidden in (
        "lineedit.new",
        "spinbox.new",
        "optionbutton.new",
        "textedit.new",
        "fileaccess",
        "diraccess",
        "httprequest",
        "httpclient",
        "preload(",
        'load("',
    ):
        assert forbidden not in lowered


def test_target_controls_mount_dedicated_gate_without_request_conflation() -> None:
    target_source = TARGET.read_text(encoding="utf-8")
    lowered = target_source.lower()
    assert "puzzle_config_gate_script_path" in lowered
    assert 'name = "approvedpuzzleconfiggate"' in lowered
    assert "generationrequest" not in lowered


def test_committed_runtime_proves_unavailable_branch() -> None:
    source = INTEGRATION.read_text(encoding="utf-8")
    for marker in (
        'initial_gate.get("state") == "UNAVAILABLE"',
        'initial_gate.get("editable_fields") == []',
        'initial_gate.get("mutation_available") == false',
        'gate.get_child_count() == 3',
        'child is Label',
        'GenerationRequest target fields',
        "SB-LF06-007-C001 puzzle-config UNAVAILABLE integration PASS",
    ):
        assert marker in source


def test_real_puzzle_config_gate_integration_passes() -> None:
    result = subprocess.run(
        [
            "godot",
            "--headless",
            "--path",
            "level_factory",
            "--script",
            "res://tests/factory_studio_puzzle_config_gate_integration_suite.gd",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SB-LF06-007-C001 puzzle-config UNAVAILABLE integration PASS" in output
