from __future__ import annotations

import subprocess
from pathlib import Path

from scrubbots_pixel_factory.output.bundle import (
    METADATA_SCHEMA,
    METADATA_SCHEMA_VERSION,
)
from scrubbots_pixel_factory.quality.core import QUALITY_SCHEMA, QUALITY_VERSION


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
PANEL = FACTORY / "scripts" / "factory_studio_evidence_panel.gd"
TARGET = FACTORY / "scripts" / "factory_studio_target_controls.gd"
INTEGRATION = FACTORY / "tests" / "factory_studio_action_integration_suite.gd"


def test_evidence_panel_is_project_local_and_reads_canonical_metadata_only() -> None:
    assert PANEL.exists()
    assert PANEL.is_relative_to(FACTORY)
    source = PANEL.read_text(encoding="utf-8")
    lowered = source.lower()
    assert f'const metadata_schema := "{METADATA_SCHEMA}"' in lowered
    assert f"const metadata_schema_version := {METADATA_SCHEMA_VERSION}" in lowered
    assert f'const quality_schema := "{QUALITY_SCHEMA}"' in lowered
    assert f"const quality_version := {QUALITY_VERSION}" in lowered
    assert 'path_join("metadata.json")' in source or 'path_join("metadata.json")' in lowered
    assert "JSON.parse_string" in source
    assert "quality" in lowered and "report" in lowered and "metrics" in lowered
    assert "evaluate_grid" not in source
    assert "class GenerationRequest" not in source
    assert "GenerationResult" not in source
    assert "candidate_presentation" not in lowered
    for marker in (
        "httprequest",
        "httpclient",
        "websocket",
        "magnific",
        "pixellab",
        "perchance",
        "api_key",
        "credential",
        "preload(",
        'load("',
    ):
        assert marker not in lowered


def test_evidence_panel_keeps_semantic_gates_and_truth_separation() -> None:
    source = PANEL.read_text(encoding="utf-8")
    lowered = source.lower()
    target = TARGET.read_text(encoding="utf-8")
    for marker in (
        'const empty := "EMPTY"',
        'const ready := "READY"',
        'const error := "ERROR"',
        'if state == "SUCCESS"',
        'output_path", ""',
        'path_join("metadata.json")',
        'UNAVAILABLE — gameplay solver pending M03.',
        'UNAVAILABLE — Difficulty Intelligence pending M04.',
        'UNAVAILABLE — no canonical gameplay load/risk model exists yet.',
        "target/request difficulty",
        "Structural QA ACCEPT != OWNER ACCEPT",
        "retained_after_failure",
    ):
        assert marker.lower() in lowered
    assert "FactoryStudioEvidencePanel.new()" not in target
    assert "EVIDENCE_PANEL_SCRIPT_PATH" in target
    assert 'call("consume_action_result", _last_action_result)' in target


def test_integration_contains_canonical_metadata_and_error_evidence() -> None:
    source = INTEGRATION.read_text(encoding="utf-8")
    for marker in (
        'empty_evidence.get("state") == "EMPTY"',
        'evidence_after_generate.get("state") == "READY"',
        'quality_decision',
        'metadata_metrics.get(metric_name)',
        'evidence_after_failure.get("retained_after_failure") == true',
        'evidence_after_reproduce.get("source_action") == "Reproduce"',
        'corrupt_evidence.get("state") == "ERROR"',
        'mismatch_evidence.get("state") == "ERROR"',
        'SB-LF06-005-C001 canonical evidence integration PASS',
    ):
        assert marker in source


def test_real_studio_evidence_integration_passes() -> None:
    result = subprocess.run(
        [
            "godot",
            "--headless",
            "--path",
            "level_factory",
            "--script",
            "res://tests/factory_studio_action_integration_suite.gd",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SB-LF06-005-C001 canonical evidence integration PASS" in output
