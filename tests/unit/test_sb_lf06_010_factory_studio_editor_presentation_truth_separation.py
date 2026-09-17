from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
TARGET = FACTORY / "scripts" / "factory_studio_target_controls.gd"
GATEWAY = FACTORY / "scripts" / "factory_core_gateway.gd"
PREVIEW = FACTORY / "scripts" / "factory_studio_art_preview.gd"
EVIDENCE = FACTORY / "scripts" / "factory_studio_evidence_panel.gd"
EDITOR = FACTORY / "scripts" / "factory_studio_art_editor.gd"
REVALIDATION = FACTORY / "scripts" / "factory_studio_art_revalidation.gd"
PUZZLE_GATE = FACTORY / "scripts" / "factory_studio_puzzle_config_gate.gd"
INTEGRATION = FACTORY / "tests" / "factory_studio_truth_separation_integration_suite.gd"


def test_truth_domains_are_explicit_and_non_persistent() -> None:
    target = TARGET.read_text(encoding="utf-8")
    gateway = GATEWAY.read_text(encoding="utf-8")
    assert "Generate target — presentation draft" in target
    assert "candidate_presentation" in target
    assert 'call("run_action", action, draft_snapshot())' in target
    assert "candidate-id" not in target.lower()
    assert "candidate_presentation" not in gateway
    assert "--candidate-id" not in gateway
    assert "var _last_successful_core_evidence" in target
    assert "last_successful_core_evidence_snapshot" in target
    assert "singleton" not in target.lower()
    assert "autoload" not in target.lower()
    assert "FileAccess.WRITE" not in target


def test_canonical_surfaces_do_not_consume_manual_or_draft_truth() -> None:
    preview = PREVIEW.read_text(encoding="utf-8").lower()
    evidence = EVIDENCE.read_text(encoding="utf-8").lower()
    assert "working_image" not in preview
    assert "working_logical_cells" not in preview
    assert "draft_snapshot" not in preview
    assert "factorystudioarteditor" not in preview
    assert "working_image" not in evidence
    assert "working_logical_cells" not in evidence
    assert "draft_snapshot" not in evidence
    assert "revalidation" not in evidence
    assert "fileaccess.write" not in evidence
    assert "store_string" not in evidence


def test_editor_and_revalidation_remain_memory_only_and_source_scoped() -> None:
    editor = EDITOR.read_text(encoding="utf-8").lower()
    revalidation = REVALIDATION.read_text(encoding="utf-8").lower()
    assert "func load_current_canonical_artwork" in editor
    assert "func observe_action_result" in editor
    assert "working_image" in editor
    assert "fileaccess.write" not in editor
    assert "store_buffer" not in editor
    assert "store_string" not in editor
    assert 'path_join("metadata.json")' not in revalidation
    assert "source_candidate_id" in revalidation
    assert "working_grid_hash" in revalidation
    assert "source_bytes_unchanged" in revalidation
    assert "structural art qa only" in revalidation


def test_dependency_gates_remain_truthful() -> None:
    target = TARGET.read_text(encoding="utf-8")
    puzzle_gate = PUZZLE_GATE.read_text(encoding="utf-8")
    assert '"Validate"' in target
    assert '"Analyze"' in target
    assert '"Solve"' in target
    assert "no approved canonical puzzle-config edit contract" in puzzle_gate
    assert '"controls_enabled": false' in puzzle_gate


def test_committed_real_truth_separation_integration_passes() -> None:
    source = INTEGRATION.read_text(encoding="utf-8")
    for marker in (
        "Candidate A",
        "Candidate B while editor A is DIRTY",
        "Draft-only mutation",
        "Manual A revalidation",
        'unavailable.get("state") == "UNAVAILABLE"',
        'load_current_canonical_artwork", true',
        "_bundle_bytes(source_a_bundle) == source_a_bytes",
        "changed-draft-label",
    ):
        assert marker in source
    result = subprocess.run(
        [
            "godot",
            "--headless",
            "--path",
            "level_factory",
            "--script",
            "res://tests/factory_studio_truth_separation_integration_suite.gd",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SB-LF06-010-C001 editor presentation/truth separation integration PASS" in output
