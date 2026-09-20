from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
LAUNCHER = FACTORY / "scripts" / "factory_core_launcher.py"
GATEWAY = FACTORY / "scripts" / "factory_core_gateway.gd"
DASHBOARD = FACTORY / "scripts" / "factory_studio_dashboard.gd"
WORKSPACE = FACTORY / "scripts" / "factory_studio_workspace_page.gd"
INTEGRATION = FACTORY / "tests" / "factory_studio_dashboard_integration_suite.gd"


def test_dashboard_projection_reuses_canonical_manifest_validation_and_is_read_only() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")
    start = source.index("def _dashboard_manifest_path")
    end = source.index("def _validate_studio_request")
    dashboard_section = source[start:end]
    assert 'DASHBOARD_OPERATION = "factory-operations-dashboard-inspection"' in source
    assert "_validate_manifest" in dashboard_section
    assert "_validate_attempt_history" in dashboard_section
    assert "_accepted_grids" in dashboard_section
    assert "_resume_registry" in dashboard_section
    for forbidden in ("write_text", "mkdir", "unlink", "rmdir", "open(..., \"w\")", "FileAccess.WRITE"):
        assert forbidden not in dashboard_section


def test_dashboard_gateway_and_ui_have_bounded_read_only_contracts() -> None:
    gateway = GATEWAY.read_text(encoding="utf-8").lower()
    dashboard = DASHBOARD.read_text(encoding="utf-8").lower()
    workspace = WORKSPACE.read_text(encoding="utf-8").lower()
    assert "run_dashboard_inspection" in gateway
    assert "dashboard-inspect" in gateway
    assert 'res://output/' in gateway
    assert "_find_dashboard_result" in gateway
    assert "refresh_manifest" in dashboard
    assert "snapshot" in dashboard
    assert "read-only" in dashboard
    assert "res://output/" in dashboard
    assert "operationsdashboard" in workspace
    for source in (gateway, dashboard):
        for forbidden in ("http://", "https://", "httprequest", "fileaccess.write", "sqlite", "database", "task.md"):
            assert forbidden not in source


def test_dashboard_integration_is_committed_and_uses_real_factory_studio() -> None:
    source = INTEGRATION.read_text(encoding="utf-8")
    for marker in (
        'ResourceLoader.call("load", MAIN_SCENE_PATH)',
        '"batch"',
        '"--quality-policy-json"',
        'set_manifest_relative_path',
        'refresh_manifest',
        'get("batch_id")',
        'get("rejection_code_counts")',
        'state") == "ERROR"',
        'state") == "EMPTY"',
        "original_bytes",
        "studio_evidence",
        "PASS_MARKER",
    ):
        assert marker in source
    assert INTEGRATION.is_file()


def test_committed_dashboard_integration_passes_headlessly() -> None:
    result = subprocess.run(
        [
            "godot_console.exe",
            "--headless",
            "--path",
            "level_factory",
            "--script",
            "res://tests/factory_studio_dashboard_integration_suite.gd",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SB-LFX-001-C001 Factory Operations Dashboard derived-view integration PASS" in output
    for forbidden in ("Parse Error", "SCRIPT ERROR", "No such file or directory", "Missing resource"):
        assert forbidden not in output
