"""Offline tracked-dependency checks for SB-LF00-008."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = REPOSITORY_ROOT / "level_factory"
PROJECT_FILE = PROJECT_ROOT / "project.godot"
BOOT_SCENE = PROJECT_ROOT / "scenes" / "bootstrap.tscn"
BOOT_DOC = PROJECT_ROOT / "docs" / "CLEAN_CHECKOUT_BOOT.md"
RESOURCE_REFERENCE_RE = re.compile(r"res://[^\s\"'(),\[\]]+")
MAIN_SCENE_RE = re.compile(
    r'^run/main_scene\s*=\s*"([^\"]+)"$', re.MULTILINE
)
WINDOWS_ABSOLUTE_PATH_RE = re.compile(
    r"(?i)(?<![a-z0-9_])(?:[a-z]:[\\/]|\\\\)"
)


def _tracked_project_paths() -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "ls-files", "--", "level_factory"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return tuple(line for line in result.stdout.splitlines() if line)


def _tracked_project_files() -> tuple[Path, ...]:
    return tuple(REPOSITORY_ROOT / path for path in _tracked_project_paths())


def _tracked_set() -> set[str]:
    return set(_tracked_project_paths())


def _runtime_project_files() -> tuple[Path, ...]:
    """Return tracked Godot source/config files, excluding prose contracts."""

    suffixes = {".godot", ".tscn", ".gd", ".tres", ".res", ".cfg", ".json"}
    return tuple(
        path
        for path in _tracked_project_files()
        if path.suffix.lower() in suffixes
    )


def test_boot_descriptor_and_scene_are_tracked_by_git() -> None:
    tracked = _tracked_set()
    assert "level_factory/project.godot" in tracked
    assert "level_factory/scenes/bootstrap.tscn" in tracked

    descriptor = PROJECT_FILE.read_text(encoding="utf-8")
    match = MAIN_SCENE_RE.search(descriptor)
    assert match is not None
    assert match.group(1) == "res://scenes/factory_studio.tscn"
    assert BOOT_SCENE.is_file()


def test_every_tracked_resource_reference_is_contained_and_tracked() -> None:
    tracked = _tracked_set()
    project_root = PROJECT_ROOT.resolve()

    for path in _tracked_project_files():
        text = path.read_text(encoding="utf-8")
        for reference in RESOURCE_REFERENCE_RE.findall(text):
            assert not reference.startswith("res://../")
            relative = Path(reference[6:])
            assert ".." not in relative.parts
            resolved = (PROJECT_ROOT / relative).resolve()
            assert resolved.is_relative_to(project_root)
            tracked_name = (Path("level_factory") / relative).as_posix()
            assert tracked_name in tracked


def test_tracked_project_has_no_local_cache_output_secret_or_sibling_dependency() -> None:
    tracked = _tracked_set()
    assert not any(
        ".godot" in Path(path).parts for path in tracked
    )
    assert not any(Path(path).is_symlink() for path in _tracked_project_files())

    for path in _runtime_project_files():
        text = path.read_text(encoding="utf-8")
        lower_text = text.lower()
        assert WINDOWS_ABSOLUTE_PATH_RE.search(text) is None
        assert "res://../" not in lower_text
        assert "res://.godot" not in lower_text
        assert "res://output" not in lower_text
        assert "res://.secrets" not in lower_text
        assert "res://secrets" not in lower_text
        assert "sekiph82/scrubbots" not in lower_text
        assert "addons/" not in lower_text
        assert "plugin.cfg" not in lower_text
        assert "[editor_plugins]" not in lower_text


def test_tracked_boot_contract_has_no_provider_network_or_credential_dependency() -> None:
    forbidden = (
        "http://",
        "https://",
        "httprequest",
        "websocket",
        "api_key",
        "api-key",
        "preload(",
        "load(",
    )
    runtime_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in _runtime_project_files()
    ).lower()
    assert not any(marker in runtime_text for marker in forbidden)


def test_clean_checkout_documentation_states_the_durable_contract() -> None:
    assert BOOT_DOC.is_file()
    text = " ".join(BOOT_DOC.read_text(encoding="utf-8").lower().split())
    required = (
        "committed tracked files alone",
        "`.godot/` directory is generated cache and is not required before first boot",
        "local generated output is not required",
        "local secrets or provider authentication material are not required",
        "sibling or main-game repository are not required",
        "isolated tracked-only snapshot",
        "git archive",
        "exit code `0`",
        "no parse, missing-resource, or external-dependency failure",
        "disposable snapshot",
        "root `tasks.md` remains the sole live task ledger",
    )
    assert all(phrase in text for phrase in required)


def test_python_factory_core_is_not_duplicated_into_the_nested_project() -> None:
    assert (REPOSITORY_ROOT / "src" / "scrubbots_pixel_factory").is_dir()
    assert not any(path.suffix.lower() == ".py" for path in _tracked_project_files())
