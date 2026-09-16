from __future__ import annotations

import re
import subprocess
from pathlib import Path

from scrubbots_pixel_factory.core.request import (
    GENERATION_REQUEST_SCHEMA,
    SUPPORTED_GENERATION_REQUEST_SCHEMA_VERSIONS,
)


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "level_factory" / "scripts" / "factory_studio_evidence_panel.gd"
INTEGRATION = ROOT / "level_factory" / "tests" / "factory_studio_action_integration_suite.gd"


def test_studio_request_literals_match_canonical_python_contracts() -> None:
    source = PANEL.read_text(encoding="utf-8")
    schema_match = re.search(r'const GENERATION_REQUEST_SCHEMA := "([^"]+)"', source)
    versions_match = re.search(r"const SUPPORTED_GENERATION_REQUEST_SCHEMA_VERSIONS: Array\[int\] = \[(.*?)\]", source)
    assert schema_match is not None
    assert versions_match is not None
    assert schema_match.group(1) == GENERATION_REQUEST_SCHEMA
    studio_versions = tuple(int(value.strip()) for value in versions_match.group(1).split(",") if value.strip())
    assert studio_versions == tuple(SUPPORTED_GENERATION_REQUEST_SCHEMA_VERSIONS)


def test_presentation_gate_is_fail_closed_without_full_validator_duplication() -> None:
    source = PANEL.read_text(encoding="utf-8")
    lowered = source.lower()
    for marker in (
        'root.get("candidate_id")',
        'artwork_data.get("candidate_id")',
        "generation_request_schema",
        "supported_generation_request_schema_versions",
        "typeof(request_version_value)",
        "typeof(rejection_codes_value) != type_array",
        'return "canonical quality rejection_codes is not an array"',
        'return "unsupported canonical generationrequest schema"',
        'return "unsupported canonical generationrequest schema version"',
    ):
        assert marker in lowered
    assert "evaluate_grid" not in source
    assert "class GenerationRequest" not in source
    assert "GenerationResult" not in source


def test_real_godot_regression_covers_r01_metadata_error_mutations() -> None:
    source = INTEGRATION.read_text(encoding="utf-8")
    for marker in (
        "root_candidate_mutation",
        "artwork_type_mutation",
        "request_schema_mutation",
        "request_version_mutation",
        "request_type_mutation",
        "rejection_type_mutation",
        'restored_generate_evidence.get("state") == "READY"',
        'mismatch_evidence.get("state") == "ERROR"',
    ):
        assert marker in source


def test_real_studio_r01_integration_passes() -> None:
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
