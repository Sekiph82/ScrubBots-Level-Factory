"""Static, offline contract checks for the SB-LF00-001 Godot project shell."""

from __future__ import annotations

import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = REPOSITORY_ROOT / "level_factory"
PROJECT_FILE = PROJECT_ROOT / "project.godot"
MAIN_SCENE_RE = re.compile(r'^run/main_scene\s*=\s*"([^"]+)"$', re.MULTILINE)
RESOURCE_REFERENCE_RE = re.compile(r"res://[^\s\"'(),\[\]]+")
WINDOWS_ABSOLUTE_PATH_RE = re.compile(
    r"(?i)(?<![a-z0-9_])(?:[a-z]:[\\/]|\\\\)"
)


def _project_files() -> tuple[Path, ...]:
    """Return source project files while excluding any local Godot cache."""

    return tuple(
        path
        for path in PROJECT_ROOT.rglob("*")
        if path.is_file() and ".godot" not in path.relative_to(PROJECT_ROOT).parts
    )


def _project_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8") for path in _project_files()
    )


def test_nested_project_descriptor_exists_and_targets_godot_4() -> None:
    assert PROJECT_FILE.is_file()
    descriptor = PROJECT_FILE.read_text(encoding="utf-8")
    match = re.search(r"^config_version\s*=\s*(\d+)\s*$", descriptor, re.MULTILINE)
    assert match is not None
    assert int(match.group(1)) >= 4


def test_configured_main_scene_is_contained_and_exists() -> None:
    descriptor = PROJECT_FILE.read_text(encoding="utf-8")
    match = MAIN_SCENE_RE.search(descriptor)
    assert match is not None
    scene_reference = match.group(1)
    assert scene_reference.startswith("res://")
    assert ".." not in Path(scene_reference[6:]).parts
    scene_path = PROJECT_ROOT / Path(scene_reference[6:])
    assert scene_path.is_file()


def test_all_resource_references_are_project_relative_and_contained() -> None:
    for path in _project_files():
        text = path.read_text(encoding="utf-8")
        for reference in RESOURCE_REFERENCE_RE.findall(text):
            assert not reference.startswith("res://../")
            relative_path = Path(reference[6:])
            assert ".." not in relative_path.parts
            assert (PROJECT_ROOT / relative_path).resolve().is_relative_to(
                PROJECT_ROOT.resolve()
            )


def test_nested_project_has_no_absolute_owner_local_or_main_game_paths() -> None:
    text = _project_text()
    assert WINDOWS_ABSOLUTE_PATH_RE.search(text) is None
    assert r"c:\users\sekip\desktop\scrubbots" not in text.lower()


def test_nested_project_has_no_external_addon_or_plugin_dependency() -> None:
    assert not (PROJECT_ROOT / "addons").exists()
    assert not any(path.name == "plugin.cfg" for path in _project_files())
    text = PROJECT_FILE.read_text(encoding="utf-8").lower()
    assert "[editor_plugins]" not in text
    assert "editor_plugins/" not in text


def test_nested_project_has_no_network_provider_or_credential_path() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in _project_files()
        if path.suffix.lower() in {".godot", ".tscn", ".gd", ".tres", ".res", ".cfg", ".json"}
    )
    forbidden_patterns = (
        "http://",
        "https://",
        "httprequest",
        "websocket",
        "api_key",
        "api-key",
        "credential",
    )
    assert not any(pattern in text for pattern in forbidden_patterns)


def test_factory_python_source_layout_remains_outside_nested_project() -> None:
    assert (REPOSITORY_ROOT / "src" / "scrubbots_pixel_factory").is_dir()
    assert (REPOSITORY_ROOT / "tests").is_dir()
    assert not (PROJECT_ROOT / "src").exists()
    assert all(
        path.relative_to(PROJECT_ROOT).as_posix() == "scripts/factory_core_launcher.py"
        for path in _project_files()
        if path.suffix == ".py"
    )
    assert not (PROJECT_ROOT / "src").exists()
