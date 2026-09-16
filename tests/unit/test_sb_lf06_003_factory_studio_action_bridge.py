from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
GATEWAY = FACTORY / "scripts" / "factory_core_gateway.gd"
LAUNCHER = FACTORY / "scripts" / "factory_core_launcher.py"
TARGET = FACTORY / "scripts" / "factory_studio_target_controls.gd"
INTEGRATION = FACTORY / "tests" / "factory_studio_action_integration_suite.gd"


def test_action_bridge_is_narrow_offline_and_discrete() -> None:
    source = GATEWAY.read_text(encoding="utf-8").lower()
    assert 'launcher_path := "res://scripts/factory_core_launcher.py"' in source
    assert "os.execute" in source
    assert "packedstringarray" in source
    assert '"--help"' in source
    assert "read_stderr := true" in source
    assert "candidate-id" not in source
    assert "candidate_presentation" not in source
    for marker in (
        "cmd /c",
        "powershell",
        "bash",
        "shell=true",
        "httprequest",
        "httpclient",
        "websocket",
        "magnific",
        "pixellab",
        "perchance",
        "api_key",
        "credential",
        "http://",
        "https://",
    ):
        assert marker not in source


def test_launcher_only_delegates_to_the_canonical_python_cli() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")
    assert "sys.path.insert" in source
    assert "scrubbots_pixel_factory.cli.main" in source
    assert "canonical_main()" in source
    assert "requests" not in source.lower()
    result = subprocess.run(
        [sys.executable, str(LAUNCHER), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "generate" in result.stdout
    assert "reproduce" in result.stdout


def test_studio_exposes_exact_action_set_and_does_not_forward_presentation_id() -> None:
    source = TARGET.read_text(encoding="utf-8")
    for action in ("Generate", "Solve", "Validate", "Analyze", "Reproduce"):
        assert f'"{action}"' in source
        assert f'button.name = action + "Action"' in source
    assert "candidate_presentation" in source
    assert "candidate-id" not in source.lower()
    assert 'call("run_action", action, draft_snapshot())' in source


def test_committed_integration_runner_covers_unavailable_and_real_core_paths() -> None:
    source = INTEGRATION.read_text(encoding="utf-8")
    assert source.startswith("extends SceneTree")
    assert 'FactoryCoreGateway.new(str(gateway.get("python_executable")), "res://tests/factory_studio_action_integration_suite.gd")' in source
    assert '"state") == "FAILED"' in source
    assert '"disposition") == "MATCH"' in source
    assert "PRESENTATION_LABEL" in source
    assert "last_successful_core_evidence_snapshot" in source


def test_workspace_wording_stays_true_after_core_execution() -> None:
    source = (FACTORY / "scripts" / "factory_studio_workspace_page.gd").read_text(encoding="utf-8")
    assert "No generation has occurred" not in source
    assert "canonical execution evidence is shown separately" in source


def test_real_studio_core_generate_and_reproduce_boundary() -> None:
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
    assert "SB-LF06-003-C001 Studio/Core action integration PASS" in output
