from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace
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
    assert result["status"] == "ALPIX_AVAILABLE_DISCOVERY_ONLY"
    assert result["session_status"] == "CLAUDE_SESSION_UNVERIFIED"
    assert result["executable"] == executable
    assert result["plugin_id"] == "owner/alpix@market"
    assert result["mcp_servers"] == "alpix-draw"
    assert "usage-limit health is not probed" in str(result["reason"]).lower()


def test_alpix_discovery_accepts_user_mcp_and_distinguishes_missing_route(monkeypatch) -> None:
    home = Path("C:/v13-fixture/profile")
    executable = str(home / ".local" / "bin" / "claude.exe")
    global_config = home / ".claude.json"
    monkeypatch.setenv("USERPROFILE", str(home))
    _virtual_files(monkeypatch, {str(global_config): json.dumps({
        "mcpServers": {"alpix-image-service": {"command": "node", "env": {"TOKEN": "never-return"}},
                        "other-service": {"command": "node"}},
    })}, executable)
    monkeypatch.setattr(alpix_batch.shutil, "which", lambda name: executable if name == "claude" else None)

    configured = alpix_batch.discover_alpix(user_home=home)
    assert configured["available"] is True
    assert configured["plugin_id"] == "claude-user-mcp@global-config"
    assert configured["mcp_servers"] == "alpix-image-service"
    assert "never-return" not in str(configured)

    _virtual_files(monkeypatch, {str(global_config): json.dumps({"mcpServers": {"n8n-local": {}}})}, executable)
    missing = alpix_batch.discover_alpix(user_home=home)
    assert missing["available"] is False
    assert missing["status"] == "ALPIX_PLUGIN_MISSING"


def test_alpix_discovery_reads_project_mcp_names_without_exposing_config_values(monkeypatch) -> None:
    home = Path("C:/v13-fixture/project-profile")
    project = Path("C:/v13-fixture/scrubbots-project")
    executable = "C:/fixture-bin/claude.exe"
    global_config = home / ".claude.json"
    project_mcp = project / ".mcp.json"
    secret_marker = "never-return-project-token"
    monkeypatch.setenv("USERPROFILE", str(home))
    _virtual_files(monkeypatch, {
        str(global_config): json.dumps({"mcpServers": {"other-service": {"command": "node"}}}),
        str(project_mcp): json.dumps({"mcpServers": {
            "alpix-project-route": {"command": "node", "env": {"TOKEN": secret_marker}},
            "unrelated": {"command": "node"},
        }}),
    }, executable)
    monkeypatch.setattr(alpix_batch.shutil, "which", lambda name: executable if name == "claude" else None)

    result = alpix_batch.discover_alpix(project_root=project)

    assert result["available"] is True
    assert result["status"] == "ALPIX_AVAILABLE_DISCOVERY_ONLY"
    assert result["plugin_id"] == "claude-project-mcp@project-config"
    assert result["mcp_servers"] == "alpix-project-route"
    assert secret_marker not in str(result)


def test_alpix_discovery_reports_unread_project_scope_without_claiming_missing(monkeypatch) -> None:
    home = Path("C:/v13-fixture/unread-profile")
    project = Path("C:/v13-fixture/unread-project")
    executable = str(home / ".local" / "bin" / "claude.exe")
    monkeypatch.setenv("USERPROFILE", str(home))
    _virtual_files(monkeypatch, {}, executable)
    monkeypatch.setattr(alpix_batch.shutil, "which", lambda name: executable if name == "claude" else None)
    original_read_text = Path.read_text

    def unread_project_scope(path: Path, *args, **kwargs) -> str:
        if str(path) == str(project / ".mcp.json"):
            raise PermissionError("synthetic unreadable project config")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", unread_project_scope)

    result = alpix_batch.discover_alpix(user_home=home, project_root=project)

    assert result["available"] is False
    assert result["status"] == "CONFIG_SCOPE_UNREAD"


def test_alpix_discovery_recognizes_account_synced_claude_ai_connector(monkeypatch) -> None:
    home = Path("C:/account-sync-profile")
    executable = str(home / ".local" / "bin" / "claude.exe")
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    _virtual_files(monkeypatch, {}, executable)
    monkeypatch.setattr(alpix_batch.shutil, "which", lambda name: executable if name == "claude" else None)
    calls = []
    probe = alpix_batch._discover_account_synced_alpix

    def runner(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(
            returncode=0,
            stdout="claude.ai Alpix:\n  Scope: claude.ai config\n  Status: √ Connected\n",
            stderr="",
        )

    monkeypatch.setattr(alpix_batch, "_discover_account_synced_alpix",
                        lambda path: probe(path, runner=runner))
    result = alpix_batch.discover_alpix()

    assert result["available"] is True
    assert result["status"] == "ALPIX_AVAILABLE_DISCOVERY_ONLY"
    assert result["session_status"] == "CLAUDEAI_CONNECTOR_CONNECTED"
    assert result["plugin_id"] == "claude.ai connector"
    assert result["mcp_servers"] == "claude.ai Alpix"
    assert result["route_scope"] == "claude.ai config"
    assert result["route_kind"] == "claude.ai_connector"
    assert "capabilities and usage-limit health are not probed" in result["reason"]
    assert calls[0][0] == [executable, "mcp", "get", "claude.ai Alpix"]
    assert calls[0][1]["timeout"] == 10


def test_alpix_discovery_does_not_claim_missing_when_account_route_probe_fails(monkeypatch) -> None:
    home = Path("C:/account-sync-profile")
    executable = str(home / ".local" / "bin" / "claude.exe")
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    _virtual_files(monkeypatch, {}, executable)
    monkeypatch.setattr(alpix_batch.shutil, "which", lambda name: executable if name == "claude" else None)
    monkeypatch.setattr(alpix_batch, "_discover_account_synced_alpix",
                        lambda _path: {"state": "unverified", "reason": "offline fixture"})

    result = alpix_batch.discover_alpix()

    assert result["available"] is False
    assert result["status"] == "ALPIX_SYNC_UNVERIFIED"
    assert "offline fixture" in result["reason"]


def test_account_synced_alpix_probe_reports_authentication_required() -> None:
    def runner(_args, **_kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout="claude.ai Alpix:\n  Scope: claude.ai config\n  Status: ! Needs authentication\n",
            stderr="",
        )

    result = alpix_batch._discover_account_synced_alpix("C:/fixture/claude.exe", runner=runner)

    assert result is not None
    assert result["state"] == "auth_required"
    assert "needs authentication" in result["reason"].lower()


def test_unverified_account_synced_alpix_generation_fails_before_path_or_request(monkeypatch) -> None:
    identity = {
        "available": True,
        "status": "ALPIX_AVAILABLE_DISCOVERY_ONLY",
        "route_kind": "claude.ai_connector",
        "executable": "C:/fixture/claude.exe",
        "plugin_id": "claude.ai connector",
        "mcp_servers": "claude.ai Alpix",
        "route_scope": "claude.ai config",
    }
    calls = []

    def runner(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("Unverified account connector must not be invoked.")

    def forbidden_resolve(self, *args, **kwargs):
        raise AssertionError("Unverified connector must be rejected before touching output paths.")

    monkeypatch.setattr(Path, "resolve", forbidden_resolve)
    try:
        alpix_batch.generate_alpix_png(
            prompt="offline test",
            width=16,
            height=16,
            destination="unverified-account-route.png",
            discovery=identity,
            runner=runner,
        )
    except alpix_batch.AlpixUnavailable as exc:
        assert "ALPIX_CLAUDEAI_CAPABILITY_UNVERIFIED" in str(exc)
        assert "no request was sent" in str(exc)
    else:
        raise AssertionError("Unverified account connector unexpectedly proceeded.")

    assert calls == []


def test_alpix_discovery_applies_project_plugin_enablement(monkeypatch) -> None:
    home = Path("C:/v13-fixture/project-plugin-profile")
    project = Path("C:/v13-fixture/project-plugin")
    config = home / ".claude"
    install = config / "plugins" / "cache" / "alpix-tool"
    executable = str(home / ".local" / "bin" / "claude.exe")
    files = {
        str(config / "settings.json"): json.dumps({"enabledPlugins": {"owner/alpix@market": False}}),
        str(config / "plugins" / "installed_plugins.json"): json.dumps({
            "plugins": {"owner/alpix@market": [{"installPath": str(install)}]},
        }),
        str(install / ".claude-plugin" / "plugin.json"): json.dumps({"name": "Alpix Pixel Art"}),
        str(install / ".mcp.json"): json.dumps({"mcpServers": {"alpix-draw": {"command": "node"}}}),
        str(project / ".claude" / "settings.json"): json.dumps({
            "enabledPlugins": {"owner/alpix@market": True},
        }),
    }
    _virtual_files(monkeypatch, files, executable)
    monkeypatch.setattr(alpix_batch.shutil, "which", lambda _name: None)

    result = alpix_batch.discover_alpix(user_home=home, project_root=project)

    assert result["available"] is True
    assert result["plugin_id"] == "owner/alpix@market"
    assert result["status"] == "ALPIX_AVAILABLE_DISCOVERY_ONLY"


def test_alpix_discovery_distinguishes_missing_claude_cli(monkeypatch) -> None:
    monkeypatch.setattr(alpix_batch.shutil, "which", lambda _name: None)
    result = alpix_batch.discover_alpix(user_home=Path("C:/v13-fixture/no-claude"))
    assert result["available"] is False
    assert result["status"] == "CLAUDE_CLI_MISSING"


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
    assert '"Selected Size\\n%d × %d px%s"' in ui
    assert "Saved batch lookup could not be prepared" in ui
