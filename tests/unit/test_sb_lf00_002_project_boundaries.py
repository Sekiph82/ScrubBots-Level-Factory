"""Static, offline contract checks for the SB-LF00-002 project boundary."""

from __future__ import annotations

import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = REPOSITORY_ROOT / "level_factory"
PROJECT_FILE = PROJECT_ROOT / "project.godot"
SCENE_FILE = PROJECT_ROOT / "scenes" / "factory_studio.tscn"
RESOURCE_REFERENCE_RE = re.compile(r"res://[^\s\"'(),\[\]]+")
WINDOWS_ABSOLUTE_PATH_RE = re.compile(
    r"(?i)(?<![a-z0-9_])(?:[a-z]:[\\/]|\\\\)"
)


def _project_files() -> tuple[Path, ...]:
    return tuple(
        path
        for path in PROJECT_ROOT.rglob("*")
        if path.is_file() and ".godot" not in path.relative_to(PROJECT_ROOT).parts
    )


def _project_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in _project_files())


def test_required_project_local_boundaries_exist() -> None:
    required = (
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "GOVERNANCE.md",
        PROJECT_ROOT / "docs",
        PROJECT_ROOT / "scenes",
        PROJECT_ROOT / "scripts",
        PROJECT_ROOT / "tests",
        PROJECT_ROOT / "output",
    )
    assert all(path.exists() for path in required)
    assert all(path.is_dir() for path in required[2:])


def test_project_readme_defines_ownership_and_root_tracker_authority() -> None:
    text = " ".join(
        (PROJECT_ROOT / "README.md").read_text(encoding="utf-8").lower().split()
    )
    required_phrases = (
        "independently openable godot 4",
        "python factory core",
        "not moved, copied, or reimplemented in gdscript",
        "root `tasks.md` is the sole live task ledger",
        "second tracker or acceptance authority",
        "sekiph82/scrubbots",
        "provider-backed features are not implied",
    )
    assert all(phrase in text for phrase in required_phrases)


def test_project_governance_defers_authority_and_rejects_self_acceptance() -> None:
    text = " ".join(
        (PROJECT_ROOT / "GOVERNANCE.md").read_text(encoding="utf-8").lower().split()
    )
    required_phrases = (
        "defers to the root `governance.md` and root `tasks.md`",
        "task status",
        "milestone/sprint/cycle acceptance",
        "audit authority",
        "builder/auditor separation",
        "chatgpt remains the independent auditor and tracker owner",
        "codex remains the implementation builder only",
        "does not create a competing h!veai control plane",
    )
    assert all(phrase in text for phrase in required_phrases)
    assert "self-acceptance" not in text
    assert "audit_passed" not in text


def test_directory_contract_documents_all_project_local_roles() -> None:
    text = (PROJECT_ROOT / "docs" / "DIRECTORY_BOUNDARIES.md").read_text(
        encoding="utf-8"
    ).lower()
    for role in ("scenes/", "scripts/", "tests/", "output/", "docs/"):
        assert role in text
    assert "sb-lf00-006" in text
    assert "not tracker truth" in text


def test_factory_studio_scene_and_main_scene_reference_use_scene_boundary() -> None:
    assert SCENE_FILE.is_file()
    assert not (PROJECT_ROOT / "bootstrap.tscn").exists()
    descriptor = PROJECT_FILE.read_text(encoding="utf-8")
    assert 'run/main_scene="res://scenes/factory_studio.tscn"' in descriptor


def test_project_local_resource_references_are_contained() -> None:
    for path in _project_files():
        for reference in RESOURCE_REFERENCE_RE.findall(path.read_text(encoding="utf-8")):
            assert not reference.startswith("res://../")
            relative_path = Path(reference[6:])
            assert ".." not in relative_path.parts
            assert (PROJECT_ROOT / relative_path).resolve().is_relative_to(
                PROJECT_ROOT.resolve()
            )


def test_project_local_files_have_no_external_dependency_markers() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in _project_files()
        if path.suffix.lower() in {".godot", ".tscn", ".gd", ".tres", ".res", ".cfg", ".json"}
    )
    forbidden = (
        "http://",
        "https://",
        "HTTPRequest",
        "WebSocket",
        "api_key",
        "api-key",
        "credential",
        "plugin.cfg",
        "[editor_plugins]",
        "addons/",
        "preload(\"",
        "load(\"",
    )
    lower_text = text.lower()
    assert WINDOWS_ABSOLUTE_PATH_RE.search(text) is None
    assert not any(marker.lower() in lower_text for marker in forbidden)
    assert "res://../" not in lower_text


def test_python_and_gdscript_implementation_is_not_duplicated() -> None:
    assert (REPOSITORY_ROOT / "src" / "scrubbots_pixel_factory").is_dir()
    assert all(
        path.relative_to(PROJECT_ROOT).as_posix() == "scripts/factory_core_launcher.py"
        for path in _project_files()
        if path.suffix == ".py"
    )
    assert all(
        path.name
        in {
            "factory_core_gateway.gd",
            "factory_studio_navigation.gd",
            "factory_studio_shell.gd",
                "factory_studio_workspace_page.gd",
                    "factory_studio_target_controls.gd",
            "factory_studio_art_preview.gd",
            "factory_studio_evidence_panel.gd",
            "factory_studio_art_editor.gd",
            "factory_studio_puzzle_config_gate.gd",
            "factory_studio_runtime_suite.gd",
            "factory_studio_action_integration_suite.gd",
            "factory_studio_puzzle_config_gate_integration_suite.gd",
            "factory_studio_art_revalidation.gd",
            "factory_studio_art_revalidation_integration_suite.gd",
            "factory_studio_truth_separation_integration_suite.gd",
            "factory_studio_exact_reproduce_integration_suite.gd",
            "factory_studio_dashboard.gd",
            "factory_studio_dashboard_integration_suite.gd",
        }
        for path in _project_files()
        if path.suffix == ".gd"
    )
    assert not any(path.is_symlink() for path in PROJECT_ROOT.rglob("*"))


def test_project_local_docs_do_not_create_a_competing_task_ledger() -> None:
    text = _project_text()
    assert "root `TASKS.md` is the sole live task ledger" in text
    assert "Current Task:" not in text
    assert re.search(r"(?m)^\s*[-*]\s+\[[ x~!]\]", text) is None
    assert "task denominator" not in (PROJECT_ROOT / "README.md").read_text(
        encoding="utf-8"
    ).lower()
