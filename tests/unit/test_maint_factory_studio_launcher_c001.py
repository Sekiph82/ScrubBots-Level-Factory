from __future__ import annotations

import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
ICON_DIR = FACTORY / "assets" / "icons"


def test_project_settings_use_supported_studio_identity_and_icons() -> None:
    project = (FACTORY / "project.godot").read_text(encoding="utf-8")

    assert 'config/name="ScrubBots Factory Studio"' in project
    assert 'config/icon="res://assets/icons/ScrubBots_Factory_Studio_256.png"' in project
    assert 'config/windows_native_icon="res://assets/icons/ScrubBots_Factory_Studio.ico"' in project
    assert 'run/main_scene="res://scenes/factory_studio.tscn"' in project


def test_owner_ico_copy_and_derived_png_keep_dimensions_and_alpha() -> None:
    ico = (ICON_DIR / "ScrubBots_Factory_Studio.ico").read_bytes()
    png = (ICON_DIR / "ScrubBots_Factory_Studio_256.png").read_bytes()

    assert ico[:6] == struct.pack("<HHH", 0, 1, 7)
    frames = [struct.unpack_from("<BBBBHHII", ico, 6 + index * 16) for index in range(7)]
    assert [(frame[0] or 256, frame[1] or 256) for frame in frames] == [
        (16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)
    ]
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    width, height, bit_depth, color_type = struct.unpack_from(">IIBB", png, 16)
    assert (width, height, bit_depth, color_type) == (256, 256, 8, 6)


def test_factory_studio_header_uses_derived_icon_without_distortion() -> None:
    scene = (FACTORY / "scenes" / "factory_studio.tscn").read_text(encoding="utf-8")

    assert 'path="res://assets/icons/ScrubBots_Factory_Studio_256.png"' in scene
    assert '[node name="Identity" type="HBoxContainer" parent="Frame/Layout/Header"]' in scene
    assert '[node name="Icon" type="TextureRect" parent="Frame/Layout/Header/Identity"]' in scene
    assert "custom_minimum_size = Vector2(46, 46)" in scene
    assert "stretch_mode = 6" in scene
    assert 'text = "SCRUBBOTS FACTORY STUDIO"' in scene
    shell = (FACTORY / "scripts" / "factory_studio_shell.gd").read_text(encoding="utf-8")
    assert "DisplayServer.FEATURE_NATIVE_ICON" in shell
    assert "DisplayServer.set_native_icon(icon_path)" in shell
    assert "FileAccess.file_exists(icon_path)" in shell


def test_launcher_resolves_from_script_location_and_runs_project_not_editor() -> None:
    launcher = (ROOT / "scripts" / "launch_factory_studio.ps1").read_text(encoding="utf-8")

    assert "Join-Path $PSScriptRoot '..'" in launcher
    assert "SCRUBBOTS_FACTORY_GODOT" in launcher
    assert "Test-Godot4Executable" in launcher
    assert "$versionInfo.ProductVersion" in launcher
    assert "Get-Command -Name $commandName" in launcher
    assert "Start-Process -FilePath $godotPath" in launcher
    assert "'--path', $quotedProjectPath" in launcher
    assert "--editor" not in launcher
    assert "$ResolveOnly" in launcher


def test_shortcut_installer_repairs_one_named_com_shortcut() -> None:
    installer = (ROOT / "scripts" / "install_factory_studio_shortcut.ps1").read_text(encoding="utf-8")

    assert "WScript.Shell" in installer
    assert "ScrubBots Factory Studio.lnk" in installer
    assert "$shortcut.TargetPath = $powerShellPath" in installer
    assert "$shortcut.Arguments = $arguments" in installer
    assert "$shortcut.WorkingDirectory = $repoRoot" in installer
    assert "$shortcut.Description = 'ScrubBots Factory Studio'" in installer
    assert "ScrubBots_Factory_Studio.ico" in installer
    assert "$shortcut.Save()" in installer
