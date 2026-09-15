from __future__ import annotations

import re
from pathlib import Path

from scrubbots_pixel_factory import Difficulty, GeneratorMode
from scrubbots_pixel_factory.contracts import PRODUCTION_DIMENSION_ENVELOPE


ROOT = Path(__file__).resolve().parents[2]
TARGET_CONTROLS = ROOT / "level_factory" / "scripts" / "factory_studio_target_controls.gd"
TARGET_RUNTIME_CONTRACT = ROOT / "tests" / "support" / "factory_studio_target_controls_contract.gd"
RUNTIME_RUNNER = ROOT / "level_factory" / "tests" / "factory_studio_runtime_suite.gd"


def _constant_strings(source: str, name: str) -> list[str]:
    match = re.search(rf"const {name}: Array\[String\] = \[(.*?)\]", source, re.DOTALL)
    assert match is not None, f"missing {name} constant"
    return re.findall(r'"([^"]+)"', match.group(1))


def _constant_int(source: str, name: str) -> int:
    match = re.search(rf"const {name} := (\d+)", source)
    assert match is not None, f"missing {name} constant"
    return int(match.group(1))


def test_target_controls_bind_to_canonical_python_choices_and_dimensions() -> None:
    source = TARGET_CONTROLS.read_text(encoding="utf-8")

    assert _constant_strings(source, "CANONICAL_DIFFICULTIES") == [difficulty.value for difficulty in Difficulty]
    assert _constant_strings(source, "CANONICAL_MODES") == [mode.value for mode in GeneratorMode]
    assert _constant_int(source, "MIN_DIMENSION") == PRODUCTION_DIMENSION_ENVELOPE.minimum
    assert _constant_int(source, "MAX_DIMENSION") == PRODUCTION_DIMENSION_ENVELOPE.maximum


def test_target_controls_keep_draft_state_and_do_not_clone_core() -> None:
    source = TARGET_CONTROLS.read_text(encoding="utf-8")

    assert '"DRAFT"' in source
    assert '"UNAVAILABLE"' in source
    assert '"NOT EXECUTED — presentation draft only"' in source
    assert "func draft_snapshot()" in source
    assert "GenerationRequest" not in source
    for marker in (
        "OS.execute",
        "HTTPRequest",
        "HTTPClient",
        "WebSocket",
        "FileAccess",
        "DirAccess",
        "generate(",
        "solve(",
        "validate(",
        "Magnific",
        "PixelLab",
        "Perchance",
        "api_key",
        "credential",
    ):
        assert marker.lower() not in source.lower()


def test_target_controls_have_an_executable_scene_instantiation_contract() -> None:
    runtime = TARGET_RUNTIME_CONTRACT.read_text(encoding="utf-8")
    assert TARGET_RUNTIME_CONTRACT.exists()
    assert runtime.startswith("extends Node")
    assert 'load(MAIN_SCENE_PATH) as PackedScene' in runtime
    assert 'get_tree().root.add_child(instance)' in runtime


def test_committed_project_local_runtime_runner_is_clean_checkout_safe() -> None:
    source = RUNTIME_RUNNER.read_text(encoding="utf-8")
    assert RUNTIME_RUNNER.exists()
    assert RUNTIME_RUNNER.is_relative_to(ROOT / "level_factory")
    assert source.startswith("extends SceneTree")
    assert 'MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"' in source
    assert "res://../" not in source
    assert "quit(1)" in source and "quit(0)" in source
    assert 'emit_signal("surface_selected", "Generate")' in source
    assert 'target.call("draft_snapshot")' in source
