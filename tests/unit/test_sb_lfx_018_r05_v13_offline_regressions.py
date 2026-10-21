from __future__ import annotations

import json
from pathlib import Path

from scrubbots_pixel_factory import alpix_batch
from scrubbots_pixel_factory import studio_extensions


def _virtual_files(monkeypatch, files: dict[str, str], executable: str) -> None:
    paths = {str(Path(name)): value for name, value in files.items()}
    original_is_file = Path.is_file
    original_read_text = Path.read_text

    def is_file(path: Path) -> bool:
        return str(path) == executable or str(path) in paths or original_is_file(path)

    def read_text(path: Path, *args, **kwargs) -> str:
        if str(path) in paths:
            return paths[str(path)]
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "is_file", is_file)
    monkeypatch.setattr(Path, "read_text", read_text)


def test_alpix_discovery_accepts_enabled_plugin_and_path_cli_without_temp_files(monkeypatch) -> None:
    home = Path("C:/v13-fixture/home")
    config = home / ".claude"
    install = config / "plugins" / "cache" / "alpix-tool"
    executable = str(home / ".local" / "bin" / "claude.exe")
    files = {
        str(config / "settings.json"): json.dumps({"enabledPlugins": {"owner/alpix@market": True}}),
        str(config / "plugins" / "installed_plugins.json"): json.dumps({
            "plugins": {"owner/alpix@market": [{"installPath": str(install)}]},
        }),
        str(install / ".claude-plugin" / "plugin.json"): json.dumps({"name": "Alpix Pixel Art"}),
        str(install / ".mcp.json"): json.dumps({"mcpServers": {"alpix-draw": {"command": "node"}}}),
    }
    _virtual_files(monkeypatch, files, executable)
    monkeypatch.setattr(alpix_batch.shutil, "which", lambda _name: None)

    result = alpix_batch.discover_alpix(user_home=home)

    assert result["available"] is True
    assert result["status"] == "ALPIX_CONFIGURED"
    assert result["executable"] == executable
    assert result["plugin_id"] == "owner/alpix@market"
    assert result["mcp_servers"] == "alpix-draw"
    assert "usage-limit health is not probed" in str(result["reason"]).lower()


def test_alpix_discovery_accepts_user_mcp_and_distinguishes_missing_route(monkeypatch) -> None:
    home = Path("C:/v13-fixture/profile")
    executable = "C:/fixture-bin/claude.exe"
    global_config = home / ".claude.json"
    monkeypatch.setenv("USERPROFILE", str(home))
    executable = "C:/fixture-bin/claude.exe"
    _virtual_files(monkeypatch, {str(global_config): json.dumps({
        "mcpServers": {"alpix-image-service": {"command": "node", "env": {"TOKEN": "never-return"}},
                        "other-service": {"command": "node"}},
    })}, executable)
    monkeypatch.setattr(alpix_batch.shutil, "which", lambda name: executable if name == "claude" else None)

    configured = alpix_batch.discover_alpix()
    assert configured["available"] is True
    assert configured["plugin_id"] == "claude-user-mcp@global-config"
    assert configured["mcp_servers"] == "alpix-image-service"
    assert "never-return" not in str(configured)

    _virtual_files(monkeypatch, {str(global_config): json.dumps({"mcpServers": {"n8n-local": {}}})}, executable)
    missing = alpix_batch.discover_alpix()
    assert missing["available"] is False
    assert missing["status"] == "ALPIX_PLUGIN_MISSING"


def test_pixellab_status_checks_presence_only_and_never_returns_secret(monkeypatch) -> None:
    token = "offline-test-secret-never-display"
    monkeypatch.setenv("PIXELLAB_API_TOKEN", token)
    monkeypatch.delenv("PIXELLAB_SECRET", raising=False)
    monkeypatch.setattr(studio_extensions, "_credential_manager_secret", lambda: "")

    status = studio_extensions.pixellab_secret_status()

    assert status["configured"] is True
    assert status["status"] == "READY_CREDENTIALS_CONFIGURED"
    assert "account credits" in str(status["reason"])
    assert token not in str(status)


def test_v13_live_ui_and_batch_guards_remain_source_bound() -> None:
    root = Path(__file__).resolve().parents[2]
    ui = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")

    assert '"Batch Complete · %d READY · %d FAILED · %d REJECTED\\n%d remaining"' in ui
    assert 'button.disabled = true' in ui[ui.index('elif state == "COMPLETE"'):ui.index("func _set_runtime_button")]
    assert '"BATCH ISSUES · %d"' in ui
    assert '"FAILED (%d)"' in ui and '"REJECTED (%d)"' in ui
    assert "_verified_batch_issue_for_source(source_id)" in ui
    assert "_source_png_sha256(str(source.get(\"path\", \"\"))) != expected_sha" in ui
    assert '"GenerationStyle"' not in ui and '_generation_style' not in ui
    assert '"Selected Size\\n%d × %d px"' in ui
    assert "Saved batch lookup could not be prepared" in ui
