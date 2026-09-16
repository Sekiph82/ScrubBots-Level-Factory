from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
PREVIEW = FACTORY / "scripts" / "factory_studio_art_preview.gd"
TARGET = FACTORY / "scripts" / "factory_studio_target_controls.gd"
INTEGRATION = FACTORY / "tests" / "factory_studio_action_integration_suite.gd"


def test_preview_is_a_local_canonical_artwork_presentation_component() -> None:
    assert PREVIEW.exists()
    assert PREVIEW.is_relative_to(FACTORY)
    source = PREVIEW.read_text(encoding="utf-8").lower()
    assert 'class_name factorystudioartpreview' in source
    assert 'image.load_from_file' in source
    assert 'path_join("artwork.png")' in source
    assert 'image.interpolate_nearest' in source
    assert "max_presentation_scale := 16" in source
    assert "max_preview_edge := 512" in source
    assert 'texture_filter_nearest' in source
    assert 'candidate_presentation' not in source
    for marker in (
        "httprequest",
        "httpclient",
        "websocket",
        "magnific",
        "pixellab",
        "perchance",
        "api_key",
        "credential",
        "preload(",
        'load("',
    ):
        assert marker not in source


def test_preview_source_is_only_successful_action_output_and_not_core_duplication() -> None:
    preview = PREVIEW.read_text(encoding="utf-8")
    target = TARGET.read_text(encoding="utf-8")
    assert 'if state == "SUCCESS"' in preview
    assert 'var output_path := str(result.get("output_path", ""))' in preview
    assert 'var attempted_path := output_path.path_join("artwork.png")' in preview
    assert 'func consume_action_result(result: Dictionary)' in preview
    assert "GenerationRequest" not in preview
    assert "logical_grid" not in preview
    assert 'preview_script.new()' in target
    assert 'call("consume_action_result", _last_action_result)' in target
    assert 'candidate_presentation' not in preview


def test_committed_integration_contains_real_pixel_and_retention_assertions() -> None:
    source = INTEGRATION.read_text(encoding="utf-8")
    for marker in (
        'empty_preview.get("state") == "EMPTY"',
        'expected_scale := maxi(1, mini(16, floori(512.0 / 21.0)))',
        "displayed_texture.get_image()",
		"RETAINED LAST SUCCESS",
        'corrupt_preview.get("state") == "ERROR"',
        'Reproduce MATCH preview pixels differ from Generate artwork',
    ):
        assert marker in source


def test_real_studio_preview_integration_passes() -> None:
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
    assert "SB-LF06-004-C001 crisp preview integration PASS" in output
