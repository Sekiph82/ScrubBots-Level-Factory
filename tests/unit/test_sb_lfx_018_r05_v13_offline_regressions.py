from __future__ import annotations

import json
import hashlib
from io import BytesIO
import shutil
import subprocess
from types import SimpleNamespace
from pathlib import Path
import pytest

from scrubbots_pixel_factory import alpix_batch
from scrubbots_pixel_factory import owner_art_storage
from scrubbots_pixel_factory import owner_folder_batch
from scrubbots_pixel_factory import owner_release_library
from scrubbots_pixel_factory import owner_upload
from scrubbots_pixel_factory import studio_extensions
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


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


def test_batch_issues_panel_starts_below_level_factory_details() -> None:
    root = Path(__file__).resolve().parents[2]
    ui = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    panel = ui.split("func _build_batch_issue_panel() -> void:", 1)[1].split("func _refresh_batch_issue_panel()", 1)[0]
    layout = ui.split("func _layout_batch_issue_panel() -> void:", 1)[1].split("func _layout_level_factory_thumbnail_dock", 1)[0]

    assert "details.add_child(_batch_issue_panel)" in panel
    assert "_batch_issue_panel.offset_top = 286" in panel
    assert "_batch_issue_panel.offset_top = 0" not in panel
    assert '"PreviewReplay", "ExpandSupplyPlan", "SolveAgain", "AcceptLevel", "RejectLevel"' in layout
    assert "button.position.y + button.size.y" in layout
    assert "const BATCH_ISSUES_GAP := 38.0" in layout
    assert "upper_section_bottom - details.position.y + BATCH_ISSUES_GAP" in layout


def test_owner_art_folder_contract_uses_exact_owner_spelling() -> None:
    root = Path(__file__).resolve().parents[2]
    paths = owner_art_storage.owner_art_paths(root)

    assert paths["input"] == root / "data/input"
    assert paths["alpix"] == root / "data/output/Alpix"
    assert paths["pixellab_grid_files"] == root / "data/output/Pixellab/Grid Files"
    assert paths["pixellab_final"] == root / "data/output/Pixellab/Final"
    assert paths["owner_suggestions"] == root / "data/output/Owner Suggestions"
    assert paths["pending"] == root / "data/Release Pool/Pending"
    assert paths["ready"] == root / "data/Release Pool/Ready"
    assert paths["failed"] == root / "data/Release Pool/Failed"
    assert paths["rejected"] == root / "data/Release Pool/Rejected"


def test_owner_art_archivers_reject_invalid_inputs_before_filesystem_access(monkeypatch) -> None:
    def forbidden_layout(*_args, **_kwargs):
        pytest.fail("invalid artifact must be rejected before creating owner folders")

    monkeypatch.setattr(owner_art_storage, "ensure_owner_art_layout", forbidden_layout)
    with pytest.raises(owner_art_storage.OwnerArtStorageError, match="manifest schema"):
        owner_art_storage.archive_pixellab_export("unused", {"schema": "wrong"})
    with pytest.raises(owner_art_storage.OwnerArtStorageError, match="exactly sixteen"):
        owner_art_storage.archive_pixellab_export("unused", {
            "schema": "scrubbots-pixellab-pro-4x4-source/v2",
            "source_atlas_sha256": "0" * 64,
            "source_kind": "IMPORTED_ATLAS",
            "frames": [],
        })
    with pytest.raises(owner_art_storage.OwnerArtStorageError, match="PNG byte stream"):
        owner_art_storage.archive_alpix_png(b"not a png")


def test_owner_art_outputs_route_only_through_explicit_catalog_functions() -> None:
    root = Path(__file__).resolve().parents[2]
    launcher = (root / "level_factory/scripts/factory_core_launcher.py").read_text(encoding="utf-8")
    ui = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    ignore = (root / ".gitignore").read_text(encoding="utf-8")

    assert "archive_pixellab_export(source_root, manifest)" in launcher
    assert "archive_pixellab_export(output_directory, manifest)" in launcher
    assert 'ensure_owner_art_layout(_repository_root())["alpix"]' in launcher
    assert 'archive_alpix_png(raw_png, repository_root=_repository_root())' in launcher
    csv_picker = ui.split("func _open_batch_csv() -> void:", 1)[1].split("func _process_level_csv", 1)[0]
    assert 'globalize_path("res://../data/input")' in csv_picker
    assert "data/output/Alpix/**" in ignore
    assert "data/output/Pixellab/Grid Files/**" in ignore
    assert "data/output/Pixellab/Final/**" in ignore
    assert "data/output/Owner Suggestions/**" in ignore
    assert "data/Release Pool/**" in ignore


def test_owner_art_layout_and_alpix_archive_are_idempotent_and_repo_local() -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-art-storage-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        repository = root / "repo"
        repository.mkdir(parents=True)
        paths = owner_art_storage.ensure_owner_art_layout(repository)
        assert all(path.is_dir() for path in paths.values())
        raw_png = b"\x89PNG\r\n\x1a\nowner-art-storage-offline-test"

        first = owner_art_storage.archive_alpix_png(raw_png, repository_root=repository)
        second = owner_art_storage.archive_alpix_png(raw_png, repository_root=repository)

        assert first == second
        assert first.read_bytes() == raw_png
        assert first.parent == paths["alpix"]
        assert first.name == f"alpix-{hashlib.sha256(raw_png).hexdigest()}.png"
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner-art test output escaped its owned directory")
            shutil.rmtree(root)


def test_pixellab_catalog_archives_all_sixteen_verified_slices_without_overwrite() -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-art-storage-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        repository = root / "repo"
        source = root / "source"
        (repository / "unused").mkdir(parents=True)
        source.mkdir(parents=True)
        raw_png = b"\x89PNG\r\n\x1a\nowner-art-storage-offline-test"
        digest = hashlib.sha256(raw_png).hexdigest()
        (source / "original-atlas.png").write_bytes(raw_png)
        frames = []
        for index in range(1, 17):
            filename = f"sprite-{index:02d}.png"
            (source / filename).write_bytes(raw_png)
            frames.append({"index": index, "filename": filename, "sha256": digest})
        manifest = {
            "schema": "scrubbots-pixellab-pro-4x4-source/v2",
            "source_atlas_sha256": digest,
            "source_kind": "IMPORTED_ATLAS",
            "frame_dimensions": {"width": 52, "height": 52},
            "frames": frames,
        }

        first = owner_art_storage.archive_pixellab_export(source, manifest, repository_root=repository)
        second = owner_art_storage.archive_pixellab_export(source, manifest, repository_root=repository)

        final_paths = owner_art_storage.owner_art_paths(repository)
        assert first == second
        assert Path(first["atlas_path"]).parent == final_paths["pixellab_grid_files"]
        assert len(first["slices"]) == 16
        assert [item["index"] for item in first["slices"]] == list(range(1, 17))
        assert all(Path(item["path"]).parent == final_paths["pixellab_final"] for item in first["slices"])
        assert len(list(final_paths["pixellab_final"].glob("*.png"))) == 16
        assert json.loads(Path(first["catalog_path"]).read_text(encoding="utf-8")) == {
            key: value for key, value in first.items() if key != "catalog_path"
        }
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner-art test output escaped its owned directory")
            shutil.rmtree(root)


def test_owner_folder_scan_is_non_recursive_provider_bounded_and_excludes_grid_files() -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-folder-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        repository = root / "repo"
        folders = owner_folder_batch.approved_owner_source_folders(repository)
        for folder in folders.values():
            folder.mkdir(parents=True, exist_ok=True)
        grid = owner_art_storage.owner_art_paths(repository)["pixellab_grid_files"]
        grid.mkdir(parents=True, exist_ok=True)
        png_bytes = BytesIO()
        Image.new("RGBA", (32, 32), (10, 20, 30, 255)).save(png_bytes, format="PNG")
        for name in ("b.png", "A.PNG"):
            (folders["ALPIX"] / name).write_bytes(png_bytes.getvalue())
        nested = folders["ALPIX"] / "nested"
        nested.mkdir()
        (nested / "ignored.png").write_bytes(png_bytes.getvalue())
        (grid / "raw-atlas.png").write_bytes(png_bytes.getvalue())

        scanned = owner_folder_batch.scan_owner_source_folder(folders["ALPIX"], repository_root=repository)

        assert scanned["provider"] == "ALPIX"
        assert [Path(path).name for path in scanned["paths"]] == ["A.PNG", "b.png"]
        assert scanned["png_count"] == 2
        invalid = folders["ALPIX"] / "invalid.png"
        invalid.write_bytes(b"not a PNG")
        rescanned = owner_folder_batch.scan_owner_source_folder(folders["ALPIX"], repository_root=repository)
        assert rescanned["png_count"] == 3
        assert any(item.get("disposition") == "REJECTED" and item.get("display_path") == "invalid.png" for item in rescanned["entries"])
        with pytest.raises(owner_folder_batch.OwnerFolderBatchError, match="raw atlases"):
            owner_folder_batch.scan_owner_source_folder(grid, repository_root=repository, explicit_alternative=True)
        alternative = root / "manually-selected"
        alternative.mkdir()
        explicit = owner_folder_batch.scan_owner_source_folder(alternative, repository_root=repository, explicit_alternative=True)
        assert explicit["provider"] == "OWNER_SELECTED_ALTERNATIVE"
        for index in range(owner_folder_batch.MAX_OWNER_FOLDER_PNGS + 1):
            (alternative / f"{index:03d}.png").write_bytes(b"")
        with pytest.raises(owner_folder_batch.OwnerFolderBatchError, match="no files were imported"):
            owner_folder_batch.scan_owner_source_folder(alternative, repository_root=repository, explicit_alternative=True)
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner-folder test output escaped its owned directory")
            shutil.rmtree(root)


def test_batch_import_classifies_repeat_and_same_batch_sha_as_skip(monkeypatch) -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-folder-dedupe-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    root.mkdir()
    ledger = root / "ledger"
    calls = {}

    def fake_import(path):
        raw = Path(path).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        seen_before = digest in calls
        calls[digest] = calls.get(digest, 0) + 1
        return {
            "state": "ALREADY_IMPORTED" if seen_before else "IMPORTED",
            "source_id": f"owner-upload-{digest}", "source_sha256": digest,
            "original_width": 32, "original_height": 32,
        }

    try:
        files = [root / "one" / "same.png", root / "two" / "same.png", root / "three" / "same.png"]
        for item in files:
            item.parent.mkdir()
            item.write_bytes(b"different identity" if item.parent.name == "three" else b"same valid test identity")
        monkeypatch.setattr(studio_extensions, "extensions_root", lambda: ledger)
        monkeypatch.setattr(studio_extensions, "import_owner_upload", fake_import)

        first = studio_extensions.batch_import(files, source_provider="ALPIX", source_folder="approved")
        second = studio_extensions.batch_import(files, source_provider="ALPIX", source_folder="approved")

        assert first["items"][0]["disposition"] == "IMPORTED"
        assert first["items"][1]["disposition"] == "SKIPPED_DUPLICATE"
        assert first["items"][0]["filename_collision"] is True
        assert first["items"][2]["filename_collision"] is True
        assert first["items"][2]["source_id"] != first["items"][0]["source_id"]
        assert first["counts"]["imported"] == 2 and first["counts"]["skipped"] == 1
        another_folder_file = root / "four" / "same.png"
        another_folder_file.parent.mkdir()
        another_folder_file.write_bytes(b"different provider folder identity")
        cross_folder = studio_extensions.batch_import([another_folder_file], source_provider="OWNER_SUGGESTIONS", source_folder="other-approved-folder")
        assert cross_folder["items"][0]["filename_collision"] is True
        assert cross_folder["items"][0]["collision_with_source_id"] in {
            first["items"][0]["source_id"], first["items"][2]["source_id"],
        }
        assert second["counts"]["skipped"] == 3
        assert second["items"][0]["source_sha256"] == hashlib.sha256(b"same valid test identity").hexdigest()
        assert all(Path(item["original_source_path"]).name == "same.png" for item in second["items"])
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner-folder test output escaped its owned directory")
            shutil.rmtree(root)


def test_concurrent_and_interrupted_owner_uploads_fail_or_reuse_without_overwrite(monkeypatch) -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-upload-concurrency-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        source_dir = root / "source"
        source_dir.mkdir(parents=True)
        image_bytes = BytesIO()
        Image.new("RGBA", (32, 32), (44, 55, 66, 255)).save(image_bytes, format="PNG")
        raw = image_bytes.getvalue()
        source_path = source_dir / "same.png"
        source_path.write_bytes(raw)
        upload_root = root / "owner-uploads"
        monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: upload_root)

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _index: owner_upload.import_owner_upload(source_path), range(8)))

        states = [item["state"] for item in results]
        assert states.count("IMPORTED") == 1
        assert states.count("ALREADY_IMPORTED") == 7
        source_id = "owner-upload-" + hashlib.sha256(raw).hexdigest()
        assert len(list(upload_root.glob(f"{source_id}/source.png"))) == 1

        interrupted_bytes = BytesIO()
        Image.new("RGBA", (32, 32), (77, 88, 99, 255)).save(interrupted_bytes, format="PNG")
        interrupted_path = source_dir / "interrupted.png"
        interrupted_path.write_bytes(interrupted_bytes.getvalue())
        interrupted_id = "owner-upload-" + hashlib.sha256(interrupted_bytes.getvalue()).hexdigest()
        partial = upload_root / interrupted_id
        partial.mkdir(parents=True)
        before = sorted(path.name for path in partial.iterdir())
        interrupted = owner_upload.import_owner_upload(interrupted_path)
        after = sorted(path.name for path in partial.iterdir())
        assert interrupted["state"] == "ERROR"
        assert "did not finish a complete immutable source record" in str(interrupted.get("error", ""))
        assert before == after == []
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner-upload concurrency test escaped its owned directory")
            shutil.rmtree(root)


def test_owner_release_library_keeps_status_history_separate_and_ready_gated(monkeypatch) -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-release-library-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        source_dir = root / "source"
        source_dir.mkdir(parents=True)
        image = BytesIO()
        Image.new("RGBA", (32, 32), (30, 60, 90, 255)).save(image, format="PNG")
        raw = image.getvalue()
        source = source_dir / "frog.png"
        source.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        source_id = "owner-upload-" + digest
        kwargs = {"source_sha256": digest, "provider": "ALPIX", "original_source_path": str(source),
                  "repository_root": root, "batch_id": "batch-import-test"}

        pending = owner_release_library.transition(source_id, "PENDING", **kwargs)
        repeated = owner_release_library.transition(source_id, "PENDING", **kwargs)
        assert repeated["idempotent"] is True
        failed = owner_release_library.transition(source_id, "FAILED", **{**kwargs, "reason": "synthetic solver timeout",
            "pipeline_run_id": "run-first", "evidence": {"solution": {"state": "NOT_AVAILABLE"}}})
        retried = owner_release_library.transition(source_id, "PENDING", **{**kwargs, "reason": "explicit retry",
            "pipeline_run_id": "run-retry", "retry_of": failed["event_sha256"]})

        real_ready_check = owner_release_library._verified_ready_entry
        monkeypatch.setattr(owner_release_library, "_verified_ready_entry", lambda _source, _run: (_ for _ in ()).throw(owner_release_library.OwnerReleaseLibraryError("canonical evidence absent")))
        with pytest.raises(owner_release_library.OwnerReleaseLibraryError, match="canonical evidence absent"):
            owner_release_library.transition(source_id, "READY", **{**kwargs, "pipeline_run_id": "run-retry"})
        monkeypatch.setattr(owner_release_library, "_verified_ready_entry", real_ready_check)
        ready_entry = {"pipeline_run_id": "run-retry", "entry_digest": "a" * 64,
                       "pipeline_sha256": "b" * 64, "pipeline": {"disposition": "READY", "primary": {"state": "READY"}}}
        monkeypatch.setattr(owner_release_library, "_verified_ready_entry", lambda _source, _run: ready_entry)
        ready = owner_release_library.transition(source_id, "READY", **{**kwargs, "pipeline_run_id": "run-retry",
            "evidence": {"solver": "synthetic canonical release-entry test"}})
        repeat_import = owner_release_library.record_import_items({"batch_id": "batch-import-repeat",
            "source_provider": "ALPIX", "items": [{"source_id": source_id, "source_sha256": digest,
            "original_source_path": str(source), "disposition": "ALREADY_IMPORTED"}]}, repository_root=root)
        assert repeat_import["records"][0]["status"] == "READY" and repeat_import["records"][0]["idempotent"] is True
        view = owner_release_library.list_records(repository_root=root)
        assert view["counts"] == {"FAILED": 0, "PENDING": 0, "READY": 1, "REJECTED": 0}
        assert view["records"][0]["artifact"]["sha256"] == digest
        assert (root / "data/Release Pool/Ready" / f"{source_id}.json").is_file()
        assert hashlib.sha256((root / "data/Release Pool/Ready" / f"{source_id}.png").read_bytes()).hexdigest() == digest
        assert not (root / "data/Release Pool/Pending" / f"{source_id}.json").exists()
        assert len(list((root / "data/Release Pool/.history" / source_id).glob("*.json"))) == 4

        rejected = owner_release_library.transition(source_id, "REJECTED", **{**kwargs, "reason": "owner rejected"})
        assert rejected["status"] == "REJECTED"
        assert not (root / "data/Release Pool/Ready" / f"{source_id}.json").exists()
        assert not (root / "data/Release Pool/Ready" / f"{source_id}.png").exists()
        assert (root / "data/Release Pool/Rejected" / f"{source_id}.json").is_file()
        assert hashlib.sha256((root / "data/Release Pool/Rejected" / f"{source_id}.png").read_bytes()).hexdigest() == digest
        with pytest.raises(owner_release_library.OwnerReleaseLibraryError, match="REJECTED -> PENDING"):
            owner_release_library.transition(source_id, "PENDING", **kwargs)
        final = owner_release_library.list_records(repository_root=root)
        assert final["counts"]["REJECTED"] == 1 and final["counts"]["READY"] == 0
        assert final["records"][0]["retry_of"] is None
        assert len(list((root / "data/Release Pool/.history" / source_id).glob("*.json"))) == 5
        with pytest.raises(owner_release_library.OwnerReleaseLibraryError, match="excluded from solver retry"):
            owner_release_library.assert_solver_allowed([source_id], repository_root=root)
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner release library test output escaped its owned directory")
            shutil.rmtree(root)


def test_owner_release_library_concurrent_same_import_creates_one_event() -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-release-library-concurrency-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        source_dir = root / "source"
        source_dir.mkdir(parents=True)
        image = BytesIO()
        Image.new("RGBA", (32, 32), (10, 100, 200, 255)).save(image, format="PNG")
        raw = image.getvalue(); source = source_dir / "same.png"; source.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest(); source_id = "owner-upload-" + digest
        request = {"source_sha256": digest, "provider": "PIXELLAB", "original_source_path": str(source), "repository_root": root}
        with ThreadPoolExecutor(max_workers=8) as pool:
            values = list(pool.map(lambda _index: owner_release_library.transition(source_id, "PENDING", **request), range(8)))
        assert sum(bool(value.get("idempotent")) for value in values) == 7
        assert len(list((root / "data/Release Pool/.history" / source_id).glob("*.json"))) == 1
        assert owner_release_library.list_records(repository_root=root)["counts"]["PENDING"] == 1
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner release concurrency fixture escaped its owned directory")
            shutil.rmtree(root)


def test_owner_release_library_refuses_to_replace_unverified_owner_projection() -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-release-library-collision-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        source_dir = root / "source"
        source_dir.mkdir(parents=True)
        image = BytesIO()
        Image.new("RGBA", (32, 32), (70, 80, 90, 255)).save(image, format="PNG")
        raw = image.getvalue()
        source = source_dir / "owner.png"
        source.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        source_id = "owner-upload-" + digest
        root.joinpath("data/Release Pool/Pending").mkdir(parents=True)
        projection = root / "data/Release Pool/Pending" / f"{source_id}.json"
        projection.write_text("owner data that is not a verified archive projection", encoding="utf-8")
        before = projection.read_bytes()

        with pytest.raises(owner_release_library.OwnerReleaseLibraryError, match="collides with an unverified"):
            owner_release_library.transition(source_id, "PENDING", source_sha256=digest, provider="OWNER_UPLOAD",
                original_source_path=str(source), repository_root=root)
        assert projection.read_bytes() == before
        assert not list((root / "data/Release Pool/.history").glob(f"{source_id}/*.json"))
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner release collision fixture escaped its owned directory")
            shutil.rmtree(root)


def test_owner_release_library_is_wired_without_weakening_canonical_pool() -> None:
    launcher = Path("level_factory/scripts/factory_core_launcher.py").read_text(encoding="utf-8")
    ui = Path("level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    canonical_pool = Path("src/scrubbots_pixel_factory/supply_pipeline/release_pool.py").read_text(encoding="utf-8")
    assert 'operation == "owner-release-library"' in launcher
    assert "record_import_items(payload)" in launcher
    assert "record_batch_outcomes(completed_job)" in launcher
    assert "assert_solver_allowed(sources)" in launcher
    assert 'state == "REJECTED"' in ui and "cannot be sent to the solver" in ui
    assert 'solve_again.text = "Retry Failed"' in ui
    assert "_refresh_owner_release_library_panel()" in ui
    assert "Keep prior loaded-batch failures visible" in ui
    assert 'status not in ["FAILED", "REJECTED"]' in ui
    assert 'pipeline.get("disposition") != "READY"' in canonical_pool
    assert "canonical solver/replay/difficulty/QA and owner-eligibility evidence" in Path("src/scrubbots_pixel_factory/owner_release_library.py").read_text(encoding="utf-8")


def test_owner_release_ready_verification_requires_exact_source_run_entry(monkeypatch) -> None:
    from scrubbots_pixel_factory.supply_pipeline import release_pool

    source_id = "owner-upload-" + "a" * 64
    good = {"candidate": {"source_lineage": {"source_id": source_id}}, "pipeline_run_id": "run-exact",
            "pipeline": {"disposition": "READY", "primary": {"state": "READY"}}}
    monkeypatch.setattr(release_pool, "release_entries", lambda _candidate_id_filter=None: [good])
    assert owner_release_library._verified_ready_entry(source_id, "run-exact") == good
    with pytest.raises(owner_release_library.OwnerReleaseLibraryError, match="exact canonical"):
        owner_release_library._verified_ready_entry(source_id, "different-run")
    bad = {**good, "pipeline": {"disposition": "FAILED", "primary": {"state": "FAILED"}}}
    monkeypatch.setattr(release_pool, "release_entries", lambda _candidate_id_filter=None: [bad])
    with pytest.raises(owner_release_library.OwnerReleaseLibraryError, match="exact canonical"):
        owner_release_library._verified_ready_entry(source_id, "run-exact")
