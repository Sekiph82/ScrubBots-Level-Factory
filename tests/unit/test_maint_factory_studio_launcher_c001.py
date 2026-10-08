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
    assert "$shortcut.WorkingDirectory = $runtimeRoot" in installer
    assert "$shortcut.Description = 'ScrubBots Factory Studio'" in installer
    assert "ScrubBots_Factory_Studio.ico" in installer
    assert "$stableIconPath" in installer
    assert "$shortcut.Save()" in installer


def test_installer_uses_the_authorized_stable_runtime_and_rejects_temp() -> None:
    installer = (ROOT / "scripts" / "install_factory_studio_shortcut.ps1").read_text(encoding="utf-8")

    assert "$runtimeRoot = 'C:\\Users\\sekip\\Desktop\\Scrubbots - Pixel Art Generator\\Release\\ScrubBots Factory Studio'" in installer
    assert "$releaseRoot = Split-Path -Parent $runtimeRoot" in installer
    assert "Test-PathWithin -Path $runtimeRoot -Parent $tempRoot" in installer
    assert "Factory Studio runtime may not be installed under TEMP" in installer
    assert "Join-Path $runtimeRoot 'scripts\\launch_factory_studio.ps1'" in installer
    assert "--editor" not in installer


def test_installer_binds_runtime_to_published_tracked_source() -> None:
    installer = (ROOT / "scripts" / "install_factory_studio_shortcut.ps1").read_text(encoding="utf-8")

    assert "remote get-url origin" in installer
    assert "$originExitCode = $LASTEXITCODE" in installer
    assert "rev-parse origin/main" in installer
    assert "published clean revision" in installer
    assert "ls-files --cached" in installer
    assert "sourceRevision = $source.Revision" in installer
    assert "$manifestName = '.factory-studio-install-manifest.json'" in installer


def test_installer_fails_closed_on_unknown_or_changed_owner_files() -> None:
    installer = (ROOT / "scripts" / "install_factory_studio_shortcut.ps1").read_text(encoding="utf-8")

    assert "already contains unknown owner data without an installer manifest" in installer
    assert "Unmanaged owner file conflicts with a new runtime file" in installer
    assert "Previously managed runtime file was modified" in installer
    assert "Owner-authoritative ICO is missing" in installer
    assert "Committed runtime ICO does not match the owner-authoritative ICO" in installer
    assert "Remove-Item -LiteralPath $stageRoot -Recurse -Force" in installer


def test_installer_repair_preserves_unchanged_managed_files_and_unknown_outputs() -> None:
    installer = (ROOT / "scripts" / "install_factory_studio_shortcut.ps1").read_text(encoding="utf-8")

    assert "$previousFiles[$file.Path] -eq $file.Sha256" in installer
    assert "$previousManifest.sourceRevision -eq $source.Revision" in installer
    assert "$installedAtUtc = [string]$previousManifest.installedAtUtc" in installer
    assert "foreach ($relativePath in $previousFiles.Keys)" in installer
    assert "Remove-Item -LiteralPath $targetPath -Force" in installer
    assert "Remove-Item -LiteralPath $runtimeRoot" not in installer
