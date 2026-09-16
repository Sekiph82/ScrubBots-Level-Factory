from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
SCENE = FACTORY / "scenes" / "factory_studio.tscn"
NAVIGATION = FACTORY / "scripts" / "factory_studio_navigation.gd"
SHELL = FACTORY / "scripts" / "factory_studio_shell.gd"
WORKSPACE = FACTORY / "scripts" / "factory_studio_workspace_page.gd"
GATEWAY = FACTORY / "scripts" / "factory_core_gateway.gd"
TARGET_CONTROLS = FACTORY / "scripts" / "factory_studio_target_controls.gd"
RUNTIME_CONTRACT = ROOT / "tests" / "support" / "factory_studio_runtime_contract.gd"


def _runtime_sources() -> list[Path]:
    return [SCENE, NAVIGATION, SHELL, WORKSPACE, GATEWAY, TARGET_CONTROLS]


def test_factory_project_points_to_real_studio_shell() -> None:
    project = (FACTORY / "project.godot").read_text(encoding="utf-8")
    scene = SCENE.read_text(encoding="utf-8")

    assert 'run/main_scene="res://scenes/factory_studio.tscn"' in project
    assert SCENE.exists()
    assert SCENE.stat().st_size > 69
    assert '[node name="FactoryStudio" type="Control"]' in scene
    assert 'res://scenes/bootstrap.tscn' not in project


def test_shell_is_split_into_navigation_page_and_gateway_contracts() -> None:
    assert 'factory_studio_navigation.gd' in SCENE.read_text(encoding="utf-8")
    assert 'factory_studio_workspace_page.gd' in SCENE.read_text(encoding="utf-8")
    assert SHELL.exists() and WORKSPACE.exists() and GATEWAY.exists()
    assert TARGET_CONTROLS.exists()
    shell = SHELL.read_text(encoding="utf-8")
    assert 'ResourceLoader.call("load", "res://scripts/factory_core_gateway.gd")' in shell
    assert "core_gateway = gateway_script.new()" in shell
    assert 'NodePath("Frame/Layout/Body/NavigationPanel/Navigation")' in shell
    assert 'NodePath("Frame/Layout/Body/Workspace")' in shell
    assert "_resolve_navigation()" in shell
    assert "_resolve_workspace()" in shell


def test_executable_runtime_contract_is_committed_and_binds_scene_hierarchy() -> None:
    scene = SCENE.read_text(encoding="utf-8")
    runtime = RUNTIME_CONTRACT.read_text(encoding="utf-8")
    assert RUNTIME_CONTRACT.exists()
    assert '[node name="NavigationPanel" type="PanelContainer" parent="Frame/Layout/Body"]' in scene
    assert '[node name="Navigation" type="VBoxContainer" parent="Frame/Layout/Body/NavigationPanel"]' in scene
    assert 'NodePath("Frame/Layout/Body/NavigationPanel/Navigation")' in runtime
    assert 'NodePath("Frame/Layout/Body/Workspace")' in runtime
    assert 'MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"' in runtime
    assert "surface_selected.is_connected" in runtime
    assert "quit(1)" in runtime
    assert runtime.startswith("extends Node")


def test_navigation_is_single_deterministic_future_surface_list() -> None:
    expected = [
        "Dashboard",
        "Generate",
        "Import",
        "Library",
        "Batches",
        "Candidates",
        "Review",
        "QA",
        "Providers",
        "Outputs",
        "Settings",
    ]
    source = NAVIGATION.read_text(encoding="utf-8")
    assert "const NAVIGATION_SURFACES" in source
    assert source.count('"Dashboard"') == 1
    for surface in expected:
        assert source.count(f'"{surface}"') == 1
    assert source.index('"Dashboard"') < source.index('"Settings"')


def test_unimplemented_surfaces_are_truthful_placeholders() -> None:
    source = WORKSPACE.read_text(encoding="utf-8")
    assert "NOT AVAILABLE" in source
    assert "NOT IMPLEMENTED" in source
    assert "No generated data is loaded" in source
    assert "metrics" not in source.lower() or "not connected" in source.lower()


def test_gateway_is_a_truthful_local_canonical_core_bridge() -> None:
    source = GATEWAY.read_text(encoding="utf-8")
    assert "AVAILABLE" in source
    assert "UNAVAILABLE" in source
    assert "ERROR" in source
    assert 'LAUNCHER_PATH := "res://scripts/factory_core_launcher.py"' in source
    assert "OS.execute" in source
    assert "func run_action" in source
    assert '"Generate"' in source and '"Reproduce"' in source
    forbidden = (
        "HTTPRequest",
        "HTTPClient",
        "WebSocket",
        "FileAccess",
        "DirAccess",
        "api_key",
        "credential",
        "http://",
        "https://",
        "Magnific",
        "PixelLab",
        "Perchance",
    )
    for marker in forbidden:
        assert marker.lower() not in source.lower()


def test_no_gdscript_factory_core_clone_or_main_game_dependency() -> None:
    runtime = "\n".join(path.read_text(encoding="utf-8") for path in _runtime_sources()).lower()
    for marker in ("scrubbots/", "scrubbots\\", "subprocess", "import ", "generate(", "solve(", "validate("):
        assert marker not in runtime


def test_root_tracker_is_untouched_and_canonical_python_core_remains_present() -> None:
    changed = subprocess.run(
        ["git", "diff", "HEAD", "--name-only", "--", "TASKS.md"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert changed == []
    assert (ROOT / "src").exists()


def test_factory_cache_is_not_tracked() -> None:
    tracked = subprocess.run(
        ["git", "ls-files", "level_factory/.godot"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert tracked == ""
