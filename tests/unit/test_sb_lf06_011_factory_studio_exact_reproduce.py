from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
GATEWAY = FACTORY / "scripts" / "factory_core_gateway.gd"
TARGET = FACTORY / "scripts" / "factory_studio_target_controls.gd"
LAUNCHER = FACTORY / "scripts" / "factory_core_launcher.py"
CLI = ROOT / "src" / "scrubbots_pixel_factory" / "cli" / "main.py"
INTEGRATION = FACTORY / "tests" / "factory_studio_exact_reproduce_integration_suite.gd"


def test_reproduce_uses_retained_metadata_authority_only() -> None:
    source = GATEWAY.read_text(encoding="utf-8")
    start = source.index("func _reproduce_arguments")
    end = source.index("func _execute_core", start)
    reproduce_args = source[start:end]
    assert "metadata_path" in reproduce_args
    assert "_last_successful_metadata_path" in source
    assert "--output" in reproduce_args
    assert "draft" not in reproduce_args.lower()
    assert "candidate-id" not in reproduce_args.lower()
    assert "candidate_presentation" not in reproduce_args.lower()
    assert "working_cells" not in reproduce_args.lower()
    assert "working_image" not in reproduce_args.lower()


def test_canonical_python_reproduce_remains_the_exact_authority() -> None:
    cli = CLI.read_text(encoding="utf-8")
    launcher = LAUNCHER.read_text(encoding="utf-8")
    assert "def _reproduce(" in cli
    assert "_request_from_canonical" in cli
    assert "logical_grid_hash" in cli
    assert "regenerated.metadata_json != bundle.metadata_json" in cli
    assert "regenerated.artwork_json != bundle.artwork_json" in cli
    assert "regenerated.artwork_png != bundle.artwork_png" in cli
    assert "regenerated.preview_png != bundle.preview_png" in cli
    assert "canonical_main()" in launcher
    assert "scrubbots_pixel_factory.cli.main" in launcher
    assert "GenerationRequest" not in GATEWAY.read_text(encoding="utf-8")


def test_studio_draft_and_manual_editor_values_do_not_cross_reproduce_boundary() -> None:
    target = TARGET.read_text(encoding="utf-8").lower()
    gateway = GATEWAY.read_text(encoding="utf-8").lower()
    assert 'call("run_action", action, draft_snapshot())' in target
    assert "candidate_presentation" in target
    assert '"--candidate-id"' not in gateway
    assert "candidate_presentation" not in gateway
    assert "working_cells" not in gateway
    assert "working_image" not in gateway
    assert "manual" not in gateway.split("func _reproduce_arguments", 1)[1].split("func _execute_core", 1)[0]


def test_committed_real_exact_reproduce_integration_passes() -> None:
    source = INTEGRATION.read_text(encoding="utf-8")
    for marker in (
        "Reproduce unavailable before a successful canonical source exists",
        "Source A",
        "Draft divergence before reproducing A",
        "Source B transition",
        "Unavailable action retention and subsequent reproduction source",
        "_generation_request(reproduced_a_metadata) == source_a_request",
        "_artifact_bytes(str(reproduced_a.get(\"output_path\", \"\"))) == source_a_bytes",
        "gateway.call(\"last_successful_metadata_path\") == source_b_metadata_path",
        "pre_source_reproduce.get(\"state\") == \"UNAVAILABLE\"",
    ):
        assert marker in source
    result = subprocess.run(
        [
            "godot",
            "--headless",
            "--path",
            "level_factory",
            "--script",
            "res://tests/factory_studio_exact_reproduce_integration_suite.gd",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SB-LF06-011-C001 exact recorded seed/config reproduction integration PASS" in output
