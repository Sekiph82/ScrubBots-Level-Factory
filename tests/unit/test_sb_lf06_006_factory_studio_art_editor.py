from __future__ import annotations

import re
import subprocess
from pathlib import Path

from scrubbots_pixel_factory.contracts.palette import CANONICAL_PALETTE


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
EDITOR = FACTORY / "scripts" / "factory_studio_art_editor.gd"
TARGET = FACTORY / "scripts" / "factory_studio_target_controls.gd"
INTEGRATION = FACTORY / "tests" / "factory_studio_action_integration_suite.gd"


def test_editor_is_local_memory_only_and_has_no_scope_creep() -> None:
    assert EDITOR.exists()
    assert EDITOR.is_relative_to(FACTORY)
    source = EDITOR.read_text(encoding="utf-8")
    lowered = source.lower()
    assert 'class_name factorystudioarteditor' in lowered
    assert 'const empty := "empty"' in lowered
    assert 'const clean := "clean"' in lowered
    assert 'const dirty := "dirty"' in lowered
    assert 'const error := "error"' in lowered
    assert 'unvalidated — revalidation pending sb-lf06-008' in lowered
    assert 'image.load_from_file' in lowered
    assert 'fileaccess.get_file_as_bytes' in lowered
    assert 'func load_current_canonical_artwork' in lowered
    assert 'func paint_cell' in lowered
    assert 'func reset_to_source' in lowered
    assert 'working_image' in lowered
    assert 'candidate_presentation' not in lowered
    assert 'generationrequest' not in lowered
    assert 'generationresult' not in lowered
    assert 'evaluate_grid' not in lowered
    assert 'revision history' not in lowered
    assert 'undo' not in lowered
    assert 'FileAccess.WRITE'.lower() not in lowered
    assert 'store_buffer' not in lowered
    assert 'store_string' not in lowered
    assert 'preload(' not in lowered
    assert not re.search(r'(?<![a-z_])load\("', lowered)
    for marker in (
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
        assert marker not in lowered


def test_studio_palette_mapping_matches_canonical_python_and_excludes_bg01() -> None:
    source = EDITOR.read_text(encoding="utf-8")
    ids_match = re.search(r"const LOGICAL_PALETTE_IDS: Array\[String\] = \[(.*?)\n\s*\]", source, re.DOTALL)
    assert ids_match
    studio_ids = re.findall(r'"(C\d{2})"', ids_match.group(1))
    assert studio_ids == list(CANONICAL_PALETTE.ids)
    mapping = dict(
        (color_id, tuple(int(channel) for channel in channels))
        for color_id, *channels in re.findall(
            r'"(C\d{2})": \[(\d+), (\d+), (\d+)\]', source
        )
    )
    expected = {color.id: color.rgb for color in CANONICAL_PALETTE.colors}
    assert mapping == expected
    assert '"BG01"' not in ids_match.group(1)
    assert 'color_id == "BG01"' in source
    assert 'const CANONICAL_PALETTE_RGB' in source


def test_target_controls_observe_editor_without_silent_action_replacement() -> None:
    target = TARGET.read_text(encoding="utf-8")
    assert 'ART_EDITOR_SCRIPT_PATH := "res://scripts/factory_studio_art_editor.gd"' in target
    assert '_art_editor.call("observe_action_result", _last_action_result)' in target
    assert 'editor_script.new()' in target
    assert 'CanonicalArtEditor' in target


def test_committed_integration_contains_real_pixel_editor_regressions() -> None:
    source = INTEGRATION.read_text(encoding="utf-8")
    for marker in (
        'empty_editor.get("state") == "EMPTY"',
        'editor.call("load_current_canonical_artwork")',
        'source_image_snapshot',
        'source_bytes_before',
        'editor_dirty.get("dirty_cell_count") == 1',
        'canonical_color_id_for_pixel',
        'editor_clean_after_reversal.get("state") == "CLEAN"',
        'editor_multi_dirty.get("dirty_cell_count") == 2',
        'editor_partial_restore.get("dirty_cell_count") == 1',
        'FileAccess.get_file_as_bytes(source_artwork_path) == source_bytes_before',
        '"BG01"',
        '"RGB_NOT_CANONICAL"',
        'No-op paint created false dirty evidence',
        'Failed action erased the DIRTY editor state',
        'Successful Reproduce silently replaced the DIRTY editor',
        'reset_to_source',
        'Explicit current-source load did not switch editor source action',
        '_images_equal',
    ):
        assert marker in source


def test_real_studio_pixel_editor_integration_passes() -> None:
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
    assert "SB-LF06-005-C001 canonical evidence integration PASS" in output
    assert "SB-LF06-006-C001 non-destructive pixel editor integration PASS" in output
