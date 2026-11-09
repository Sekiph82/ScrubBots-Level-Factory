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


def test_alpix_job_stats_separate_retired_provider_rows() -> None:
    root = Path(__file__).resolve().parent / ".r10-alpix-retired-counter-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        root.mkdir(parents=True)
        csv_path = root / "requests.csv"
        csv_path.write_text(
            "prompt,size,provider\nOld bird,8x8,MAGNIFIC\nCurrent owl,8x8,ALPIX (Claude)\nRetry fox,8x8,ALPIX (Claude)\n",
            encoding="utf-8",
        )
        renderer_prompts: list[str] = []

        def renderer(prompt: str, width: int, height: int, destination: Path):
            renderer_prompts.append(prompt)
            Image.new("RGBA", (width, height), (255, 69, 0, 255)).save(destination, format="PNG")
            return {"path": str(destination)}

        def importer(path: Path):
            return {} if path.name == "row-00003.png" else {"source_id": "offline-fixture-source"}

        result = alpix_batch.run_csv_job(
            csv_path,
            root / "jobs",
            renderer=renderer,
            importer=importer,
        )

        assert renderer_prompts == ["Current owl", "Retry fox"]
        assert [row["state"] for row in result.rows] == ["PROVIDER_RETIRED", "IMPORTED", "FAILED"]
        assert result.state == "NEEDS_RETRY"
        assert result.completed == 1
        assert result.failed == 1
        assert result.retired == 1
        assert result.remaining == 1
        assert result.to_dict()["retired"] == 1
        ui_source = (Path(__file__).resolve().parents[2] / "level_factory" / "scripts" /
                     "factory_studio_exact_ui.gd").read_text(encoding="utf-8")
        assert '"retired": job.get("retired", 0)' in ui_source
        assert "%d retired · %d left" in ui_source
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("ALPIX test output escaped its owned directory")
            shutil.rmtree(root)


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


def test_alpix_generation_reports_safe_cli_exit_and_missing_output_diagnostics() -> None:
    destination = Path(__file__).resolve().parent / ".codex-alpix-diagnostic-never-created.png"
    if destination.exists():
        raise AssertionError(f"Refusing pre-existing diagnostic output: {destination}")
    identity = {
        "available": True,
        "executable": "claude",
        "plugin_id": "claude.ai connector",
        "mcp_servers": "claude.ai Alpix",
        "route_kind": "claude.ai_connector",
        "route_scope": "claude.ai config",
    }

    def runner_with_exit_code(exit_code: int):
        def runner(*_args, **_kwargs):
            return SimpleNamespace(returncode=exit_code, stdout="private CLI output", stderr="private CLI error")
        return runner

    with pytest.raises(alpix_batch.AlpixUnavailable, match="CLAUDE_EXIT_NONZERO.*code 17"):
        alpix_batch.generate_alpix_png(
            prompt="offline diagnostic", width=56, height=56, destination=destination,
            discovery=identity, runner=runner_with_exit_code(17),
        )

    with pytest.raises(alpix_batch.AlpixUnavailable, match="ALPIX_OUTPUT_MISSING"):
        alpix_batch.generate_alpix_png(
            prompt="offline diagnostic", width=56, height=56, destination=destination,
            discovery=identity, runner=runner_with_exit_code(0),
        )

    assert not destination.exists()


def test_alpix_workspace_trust_failure_is_actionable_and_never_auto_accepted() -> None:
    destination = Path(__file__).resolve().parent / ".codex-alpix-trust-diagnostic-never-created.png"
    if destination.exists():
        raise AssertionError(f"Refusing pre-existing diagnostic output: {destination}")
    identity = {
        "available": True,
        "executable": "claude",
        "plugin_id": "claude.ai connector",
        "mcp_servers": "claude.ai Alpix",
        "route_kind": "claude.ai_connector",
        "route_scope": "claude.ai config",
    }

    def runner_with(stderr: str):
        return lambda *_args, **_kwargs: SimpleNamespace(returncode=1, stdout="", stderr=stderr)

    with pytest.raises(alpix_batch.AlpixUnavailable, match="CLAUDE_WORKSPACE_TRUST_REQUIRED") as trust_error:
        alpix_batch.generate_alpix_png(
            prompt="offline trust diagnostic", width=56, height=56, destination=destination,
            discovery=identity,
            runner=runner_with("This workspace has not been trusted. Accept the trust dialog interactively."),
        )
    assert alpix_batch._safe_unavailable_reason(trust_error.value) == (
        "CLAUDE_WORKSPACE_TRUST_REQUIRED: Accept the workspace trust dialog interactively in Claude Code; "
        "Factory will not change user trust settings."
    )

    with pytest.raises(alpix_batch.AlpixUnavailable, match="CLAUDE_TRUST_AND_SESSION_LIMIT") as combined_error:
        alpix_batch.generate_alpix_png(
            prompt="offline trust diagnostic", width=56, height=56, destination=destination,
            discovery=identity,
            runner=runner_with("This workspace has not been trusted. You've hit your session limit."),
        )
    assert alpix_batch._safe_unavailable_reason(combined_error.value) == (
        "CLAUDE_TRUST_AND_SESSION_LIMIT: Accept workspace trust interactively and retry after the Claude "
        "session limit resets."
    )
    assert not destination.exists()


def test_alpix_unavailable_reason_is_safe_and_actionable() -> None:
    safe = alpix_batch._safe_unavailable_reason(
        "CLAUDE_EXIT_NONZERO: Claude Code exited with code 17; no PNG was produced. private-secret"
    )
    assert safe == "CLAUDE_EXIT_NONZERO: Claude Code exited with code 17; no PNG was produced."
    assert "private-secret" not in safe
    assert alpix_batch._safe_unavailable_reason("provider response contained private-secret") == (
        "ALPIX_UNAVAILABLE: Claude Alpix did not produce a validated PNG."
    )


def test_alpix_csv_keeps_safe_unavailable_reason_for_studio_status() -> None:
    root = Path(__file__).resolve().parent / ".r10-alpix-unavailable-message-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        root.mkdir(parents=True)
        csv_path = root / "requests.csv"
        csv_path.write_text("prompt,size,provider\nJade dragon,56x56,ALPIX (Claude)\n", encoding="utf-8")

        def renderer(*_args):
            raise alpix_batch.AlpixUnavailable(
                "CLAUDE_EXIT_NONZERO: Claude Code exited with code 17; no PNG was produced. private-secret"
            )

        result = alpix_batch.run_csv_job(
            csv_path, root / "jobs", renderer=renderer,
            importer=lambda _path: (_ for _ in ()).throw(AssertionError("unavailable art must not import")),
        )
        assert result.state == "UNAVAILABLE"
        assert result.rows[0]["state"] == "PENDING"
        assert result.rows[0]["error"] == "CLAUDE_EXIT_NONZERO: Claude Code exited with code 17; no PNG was produced."
        assert result.remaining == 1 and result.completed == 0 and result.failed == 0

        ui = (Path(__file__).resolve().parents[2] / "level_factory" / "scripts" /
              "factory_studio_exact_ui.gd").read_text(encoding="utf-8")
        assert 'var provider_error := ""' in ui
        assert 'summary += " · " + provider_error' in ui
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("ALPIX test output escaped its owned directory")
            shutil.rmtree(root)


def test_alpix_sb_sprite_catalog_uses_descriptions_v3_palette_and_fixed_56px() -> None:
    raw = (
        'SB_SPRITE_014,"A jade-inlaid dragon, in a proud pose. Create one original visible sprite. '
        'use only the fixed C01-C16 (C01 `#E94B4B`, C02 `#F28C3C`) '
        '(C01 `#E94B4B`, C02 `#F28C3C`) palette and keep detail readable.",40,48\n'
        'SB_SPRITE_015,"A pearl-adorned dragon, facing forward. Fuse only the fixed C01-C16 '
        '(C01 `#E94B4B`) (C01 `#E94B4B`) palette and use crisp clusters.",44,52\n'
    ).encode("utf-8")

    rows = alpix_batch.read_rows(raw, default_size=(32, 32))

    assert [row["prompt_id"] for row in rows] == ["SB_SPRITE_014", "SB_SPRITE_015"]
    assert [row["width"] for row in rows] == [56, 56]
    assert [row["height"] for row in rows] == [56, 56]
    assert "jade-inlaid dragon" in rows[0]["prompt"]
    assert "pearl-adorned dragon" in rows[1]["prompt"]
    assert all("only canonical ScrubBots Palette V3" in row["prompt"] for row in rows)
    assert all("#E94B4B" not in row["prompt"] and "#F28C3C" not in row["prompt"] for row in rows)


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


def test_alpix_resume_revalidates_persisted_validated_png_before_import() -> None:
    root = Path(__file__).resolve().parent / ".r10-alpix-validated-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        fake_repo = root / "fake-repo"
        fake_repo.mkdir(parents=True)
        csv_path = fake_repo / "data" / "input" / "requests.csv"
        csv_path.parent.mkdir(parents=True)
        raw_csv = b"prompt,size\nBlue owl,8x8\n"
        csv_path.write_bytes(raw_csv)
        job_root = root / "jobs"
        job_id = hashlib.sha256(raw_csv).hexdigest()
        job_dir = job_root / job_id
        job_dir.mkdir(parents=True)
        artifact = job_dir / "row-00001.png"
        Image.new("RGBA", (2, 2), (0, 0, 0, 255)).save(artifact, format="PNG")
        foreign_palette = root / "foreign-palette.png"
        foreign_image = Image.new("RGBA", (8, 8), (255, 69, 0, 255))
        foreign_image.putpixel((0, 0), (40, 80, 120, 255))
        foreign_image.save(foreign_palette, format="PNG")
        with pytest.raises(ValueError, match="outside ScrubBots Palette V3"):
            alpix_batch._validate_png(foreign_palette, 8, 8)
        state_path = job_root / f"{job_id}.json"
        state = alpix_batch._read_job(state_path, job_id, raw_csv, alpix_batch.read_rows(raw_csv))
        state["rows"][0].update({
            "state": "VALIDATED",
            "artifact_path": str(artifact),
            "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        })
        alpix_batch._save_job(state_path, state)

        renderer_calls: list[tuple[int, int]] = []
        importer_calls: list[Path] = []

        def paused_renderer(_prompt: str, width: int, height: int, _destination: Path):
            renderer_calls.append((width, height))
            raise alpix_batch.AlpixUnavailable("offline fixture pause")

        first = alpix_batch.run_csv_job(
            csv_path, job_root, renderer=paused_renderer,
            importer=lambda path: importer_calls.append(path) or {"source_id": "unexpected"},
        )
        assert first.state == "UNAVAILABLE"
        assert first.rows[0]["state"] == "PENDING"
        assert renderer_calls == [(8, 8)]
        assert importer_calls == []
        assert not artifact.exists()

        def valid_renderer(_prompt: str, width: int, height: int, destination: Path):
            renderer_calls.append((width, height))
            Image.new("RGBA", (width, height), (255, 69, 0, 255)).save(destination, format="PNG")
            return {"path": str(destination)}

        resumed = alpix_batch.run_csv_job(
            csv_path, job_root, renderer=valid_renderer,
            importer=lambda path: importer_calls.append(path) or {"source_id": "verified-source"},
        )
        assert resumed.state == "COMPLETE"
        assert resumed.rows[0]["state"] == "IMPORTED"
        assert len(importer_calls) == 1
        assert Image.open(importer_calls[0]).size == (8, 8)
        assert renderer_calls == [(8, 8), (8, 8)]
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("ALPIX test output escaped its owned directory")
            shutil.rmtree(root)


def test_factory_alpix_wrapper_rejects_and_removes_off_palette_output_before_import(monkeypatch) -> None:
    root = Path(__file__).resolve().parent / ".r10-alpix-wrapper-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        import sys

        scripts = str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        output = root / "alpix-output.png"
        launcher = __import__("factory_core_launcher")
        monkeypatch.setattr(launcher, "_alpix_output_path", lambda _value: output)
        monkeypatch.setattr(launcher, "_repository_root", lambda: root / "fake-repo")
        identity = {
            "available": True,
            "route_kind": "claude.ai_connector",
            "executable": "C:/fixture/claude.exe",
            "plugin_id": "claude.ai connector",
            "mcp_servers": "claude.ai Alpix",
            "route_scope": "claude.ai config",
        }
        monkeypatch.setattr(alpix_batch, "discover_alpix", lambda **_kwargs: identity)
        real_generate = alpix_batch.generate_alpix_png

        def write_off_palette_png(_args, **_kwargs):
            Image.new("RGBA", (8, 8), (40, 80, 120, 255)).save(output, format="PNG")
            return SimpleNamespace(returncode=0, stdout="saved", stderr="")

        def generate_with_mocked_cli(**kwargs):
            return real_generate(**kwargs, discovery=identity, runner=write_off_palette_png)

        monkeypatch.setattr(alpix_batch, "generate_alpix_png", generate_with_mocked_cli)
        monkeypatch.setattr(
            studio_extensions, "batch_import",
            lambda _paths: pytest.fail("invalid ALPIX palette must not reach canonical import"),
        )

        with pytest.raises(ValueError, match="outside ScrubBots Palette V3"):
            launcher._alpix_generate({"prompt": "blue owl", "width": 8, "height": 8})

        assert not output.exists()
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("ALPIX wrapper test output escaped its owned directory")
            shutil.rmtree(root)


def test_alpix_csv_archive_ignores_forged_persisted_artifact_path(monkeypatch) -> None:
    root = Path(__file__).resolve().parent / ".r10-alpix-csv-archive-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        import sys

        scripts = str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        launcher = __import__("factory_core_launcher")
        fake_repo = root / "fake-repo"
        fake_repo.mkdir(parents=True)
        csv_path = fake_repo / "data" / "input" / "requests.csv"
        csv_path.parent.mkdir(parents=True)
        raw_csv = b"prompt\nBlue owl\n"
        csv_path.write_bytes(raw_csv)
        job_id = hashlib.sha256(raw_csv).hexdigest()
        extensions_root = root / "runtime"
        job_root = extensions_root / "alpix-jobs"
        state_path = job_root / f"{job_id}.json"
        state = alpix_batch._read_job(state_path, job_id, raw_csv, alpix_batch.read_rows(raw_csv))
        outside = root / "untrusted-owner-file.png"
        Image.new("RGBA", (2, 2), (255, 69, 0, 255)).save(outside, format="PNG")
        state["rows"][0].update({
            "state": "IMPORTED",
            "source_id": "already-imported-source",
            "artifact_path": str(outside),
            "artifact_sha256": hashlib.sha256(outside.read_bytes()).hexdigest(),
        })
        alpix_batch._save_job(state_path, state)
        monkeypatch.setattr(studio_extensions, "extensions_root", lambda: extensions_root)
        monkeypatch.setattr(launcher, "_repository_root", lambda: fake_repo)
        monkeypatch.setattr(
            studio_extensions, "batch_import",
            lambda _paths: pytest.fail("persisted imported row must not call provider/importer"),
        )

        result = launcher._alpix_csv_job({"csv_path": str(csv_path)})

        assert result["state"] == "COMPLETE"
        row = result["rows"][0]
        assert row["owner_catalog_status"] == "ARTIFACT_MISSING_OR_UNSAFE"
        assert row["artifact_path"] == str(job_root.resolve() / job_id / "row-00001.png")
        assert row["artifact_path"] != str(outside)
        assert "owner_catalog_path" not in row
        assert not (root / "fake-repo" / "data" / "output" / "Alpix").exists()

        expected_artifact = job_root / job_id / "row-00001.png"
        expected_artifact.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (32, 32), (255, 69, 0, 255)).save(expected_artifact, format="PNG")
        expected_sha = hashlib.sha256(expected_artifact.read_bytes()).hexdigest()
        state["rows"][0]["artifact_sha256"] = expected_sha
        state["rows"][0]["source_id"] = f"owner-upload-{expected_sha}"
        alpix_batch._save_job(state_path, state)
        monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda _source_id: {
            "source_sha256": expected_sha, "source_bytes_sha256": expected_sha,
        })
        archived_result = launcher._alpix_csv_job({"csv_path": str(csv_path)})
        archived_row = archived_result["rows"][0]
        assert archived_row["owner_catalog_status"] == "ARCHIVED"
        assert Path(archived_row["owner_catalog_path"]).read_bytes() == expected_artifact.read_bytes()
        assert archived_row["artifact_path"] == str(expected_artifact.resolve())
        assert archived_row["artifact_path"] != str(outside)
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("ALPIX CSV test output escaped its owned directory")
            shutil.rmtree(root)


def test_alpix_csv_resume_restores_csv_intent_and_verifies_imported_source(monkeypatch) -> None:
    root = Path(__file__).resolve().parent / ".r10-alpix-csv-state-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        import sys

        scripts = str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        launcher = __import__("factory_core_launcher")
        fake_repo = root / "fake-repo"
        fake_repo.mkdir(parents=True)
        csv_path = fake_repo / "data" / "input" / "requests.csv"
        csv_path.parent.mkdir(parents=True)
        raw_csv = b"prompt,size,provider\nOriginal owl,8x9,ALPIX (Claude)\n"
        csv_path.write_bytes(raw_csv)
        job_id = hashlib.sha256(raw_csv).hexdigest()
        extensions_root = root / "runtime"
        job_root = extensions_root / "alpix-jobs"
        state_path = job_root / f"{job_id}.json"
        state = alpix_batch._read_job(state_path, job_id, raw_csv, alpix_batch.read_rows(raw_csv))
        state["rows"][0].update({
            "prompt": "Injected replacement prompt",
            "width": 99,
            "height": 99,
            "reference": "C:/owner/private/reference.png",
            "provider_id": "MAGNIFIC",
            "state": "PENDING",
        })
        alpix_batch._save_job(state_path, state)
        monkeypatch.setattr(studio_extensions, "extensions_root", lambda: extensions_root)
        monkeypatch.setattr(launcher, "_repository_root", lambda: fake_repo)
        renderer_calls: list[tuple[str, int, int]] = []

        def render(prompt: str, width: int, height: int, destination: Path, **_kwargs):
            renderer_calls.append((prompt, width, height))
            Image.new("RGBA", (width, height), (255, 69, 0, 255)).save(destination, format="PNG")
            return {"path": str(destination)}

        monkeypatch.setattr(alpix_batch, "generate_alpix_png", render)
        importer_calls: list[bytes] = []

        def import_png(paths: list[str]) -> dict[str, object]:
            raw = Path(paths[0]).read_bytes()
            importer_calls.append(raw)
            return {"items": [{"disposition": "IMPORTED", "source_id": "owner-upload-" + "0" * 64}]}

        monkeypatch.setattr(studio_extensions, "batch_import", import_png)
        monkeypatch.setattr(
            studio_extensions, "verify_owner_source",
            lambda _source_id: pytest.fail("mismatched imported source must not be verified or archived"),
        )

        mismatched = launcher._alpix_csv_job({"csv_path": str(csv_path)})

        assert renderer_calls == [("Original owl", 8, 9)]
        assert len(importer_calls) == 1
        row = mismatched["rows"][0]
        assert row["prompt"] == "Original owl"
        assert (row["width"], row["height"], row["provider_id"]) == (8, 9, "ALPIX (Claude)")
        assert row["owner_catalog_status"] == "SOURCE_IDENTITY_MISMATCH"
        assert not (fake_repo / "data" / "output" / "Alpix").exists()

        expected_sha = hashlib.sha256(importer_calls[0]).hexdigest()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["rows"][0]["source_id"] = f"owner-upload-{expected_sha}"
        alpix_batch._save_job(state_path, state)
        monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda _source_id: {
            "source_sha256": expected_sha, "source_bytes_sha256": expected_sha,
        })

        verified = launcher._alpix_csv_job({"csv_path": str(csv_path)})

        assert renderer_calls == [("Original owl", 8, 9)]
        verified_row = verified["rows"][0]
        assert verified_row["owner_catalog_status"] == "ARCHIVED"
        assert Path(verified_row["owner_catalog_path"]).read_bytes() == importer_calls[0]
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("ALPIX CSV state test output escaped its owned directory")
            shutil.rmtree(root)


def test_connected_account_synced_alpix_generation_uses_cli_and_validates_output(monkeypatch) -> None:
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

    class MemoryOutputPath:
        def __init__(self, value: str) -> None:
            self.value = value
            self.parent = self

        def resolve(self):
            return self

        def mkdir(self, **_kwargs):
            return None

        def exists(self):
            return False

        def is_file(self):
            return True

        def read_bytes(self):
            return bytes((137, 80, 78, 71, 13, 10, 26, 10)) + b"fixture"

    def runner(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout="saved", stderr="")

    validations = []
    monkeypatch.setattr(alpix_batch, "Path", MemoryOutputPath)
    monkeypatch.setattr(alpix_batch, "_validate_png", lambda path, width, height: validations.append((path.value, width, height)))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "must-not-reach-child")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "must-not-reach-child")
    result = alpix_batch.generate_alpix_png(
        prompt="offline fake-cli test", width=16, height=16,
        destination="account-route-proof.png", discovery=identity, runner=runner,
    )

    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[0][0] == "C:/fixture/claude.exe"
    assert args[0][1] == "-p"
    assert "account-synced Claude Code MCP connector 'claude.ai Alpix'" in args[0][2]
    assert "16x16" in args[0][2]
    assert "Use only opaque ScrubBots Palette V3 colors" in args[0][2]
    assert "#FF4500" in args[0][2] and "#000000" in args[0][2]
    assert kwargs["env"].get("ANTHROPIC_API_KEY") is None
    assert kwargs["env"].get("ANTHROPIC_AUTH_TOKEN") is None
    assert validations == [("account-route-proof.png", 16, 16)]
    assert result["provider_id"] == "ALPIX_CLAUDE"
    assert len(str(result["sha256"])) == 64


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
    assert paths["pixellab_grid_files"] == root / "data/output/Pixellab/Grid Files"
    assert paths["pixellab_final"] == root / "data/output/Pixellab/Final"
    assert "alpix" not in paths and "owner_suggestions" not in paths
    assert paths["pending"] == root / "data/Release Pool/Pending"
    assert paths["ready"] == root / "data/Release Pool/Ready"
    assert paths["failed"] == root / "data/Release Pool/Failed"
    assert paths["rejected"] == root / "data/Release Pool/Rejected"


def test_packaged_owner_upload_resolves_data_root_outside_release_directory(tmp_path: Path, monkeypatch) -> None:
    from scrubbots_pixel_factory import owner_upload

    canonical = tmp_path / "Desktop" / "Scrubbots - Pixel Art Generator"
    canonical.mkdir(parents=True)
    (canonical / ".git").mkdir()
    (canonical / "TASKS.md").write_text("test authority\n", encoding="utf-8")
    installed_module = canonical / "Release" / "ScrubBots Factory Studio" / "scripts" / "owner_upload.py"
    installed_module.parent.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "__file__", str(installed_module))

    assert owner_upload._repository_root() == canonical
    assert owner_upload.owner_upload_root() == canonical / "data" / "Level Factory" / "Imported"


def test_packaged_data_root_fails_closed_when_canonical_checkout_is_unavailable(monkeypatch) -> None:
    from scrubbots_pixel_factory import owner_art_storage

    release_module = Path("C:/Users/sekip/Desktop/Factory-Release-Fixture/scripts/owner_upload.py")
    monkeypatch.setattr(owner_art_storage, "__file__", str(release_module))
    monkeypatch.setenv("USERPROFILE", "C:/Users/sekip/Factory-profile-without-checkout")

    with pytest.raises(owner_art_storage.OwnerArtStorageError, match="canonical Factory data checkout"):
        owner_art_storage.factory_repository_root(release_module)


def test_owner_csv_path_is_restricted_to_direct_canonical_input_files(tmp_path: Path) -> None:
    repository = tmp_path / "factory"
    canonical_input = repository / "data" / "input"
    canonical_input.mkdir(parents=True)
    csv_path = canonical_input / "prompts.csv"
    csv_path.write_text("prompt,width,height\nflower,56,56\n", encoding="utf-8")

    assert owner_art_storage.validate_owner_input_csv(csv_path, repository_root=repository) == csv_path
    with pytest.raises(owner_art_storage.OwnerArtStorageError, match="outside the canonical"):
        owner_art_storage.validate_owner_input_csv(tmp_path / "old-input" / "prompts.csv", repository_root=repository)
    with pytest.raises(owner_art_storage.OwnerArtStorageError, match="direct .csv"):
        owner_art_storage.validate_owner_input_csv(canonical_input / "nested" / "prompts.csv", repository_root=repository)
    with pytest.raises(owner_art_storage.OwnerArtStorageError, match="direct .csv"):
        owner_art_storage.validate_owner_input_csv(canonical_input / "prompts.txt", repository_root=repository)


def test_level_factory_auto_sync_scans_only_pixellab_final(tmp_path: Path, monkeypatch) -> None:
    repository = tmp_path / "factory"
    paths = owner_art_storage.owner_art_paths(repository)
    final_png = paths["pixellab_final"] / "new-sprite.png"
    final_png.parent.mkdir(parents=True)
    Image.new("RGBA", (56, 56), (255, 69, 0, 255)).save(final_png, format="PNG")
    final_bytes = final_png.read_bytes()

    legacy_png = repository / "level_factory" / "output" / "legacy" / "old-sprite.png"
    legacy_png.parent.mkdir(parents=True)
    Image.new("RGBA", (56, 56), (0, 204, 120, 255)).save(legacy_png, format="PNG")
    grid_atlas = paths["pixellab_grid_files"] / "raw-atlas.png"
    grid_atlas.parent.mkdir(parents=True)
    Image.new("RGBA", (224, 224), (54, 144, 234, 255)).save(grid_atlas, format="PNG")

    imported_paths: list[str] = []

    def fake_import(path, *, repository_root):
        imported_paths.append(str(Path(path).resolve()))
        digest = hashlib.sha256(final_bytes).hexdigest()
        return {"state": "IMPORTED", "source_id": f"owner-upload-{digest}"}

    monkeypatch.setattr(studio_extensions, "import_owner_upload", fake_import)
    monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(studio_extensions, "validate_owner_source", lambda *_args, **_kwargs: {
        "exact_logical_source": True,
        "structural": {"disposition": "PASS"},
        "void_capability": {"state": "NOT_REQUIRED"},
    })

    active, invalid = studio_extensions._sync_current_pixellab_final_sources(repository)

    expected_id = "owner-upload-" + hashlib.sha256(final_bytes).hexdigest()
    assert active == {expected_id}
    assert invalid == []
    assert imported_paths == [str(final_png.resolve())]
    assert str(legacy_png.resolve()) not in imported_paths
    assert final_png.read_bytes() == final_bytes


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


def test_owner_art_outputs_route_only_through_explicit_catalog_functions() -> None:
    root = Path(__file__).resolve().parents[2]
    launcher = (root / "level_factory/scripts/factory_core_launcher.py").read_text(encoding="utf-8")
    ui = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    ignore = (root / ".gitignore").read_text(encoding="utf-8")

    assert "archive_pixellab_export(source_root, manifest)" in launcher
    assert "archive_pixellab_export(output_directory, manifest)" in launcher
    assert "alpix" not in launcher.casefold()
    assert "owner_suggestions" not in launcher.casefold()
    csv_picker = ui.split("func _open_batch_csv() -> void:", 1)[1].split("func _process_level_csv", 1)[0]
    assert '_factory_data_path("input")' in csv_picker
    assert 'func _is_canonical_input_csv(path: String)' in ui
    assert 'validate_owner_input_csv(csv_path_value, repository_root=_repository_root())' in launcher
    owner_source_menu = ui.split("func _open_owner_folder_sources() -> void:", 1)[1].split("func _on_owner_folder_selected", 1)[0]
    assert "Compatibility binding only" in owner_source_menu
    assert "_restore_imported_sources()" in owner_source_menu
    assert "menu.add_item" not in owner_source_menu
    assert "data/output/Alpix/**" not in ignore
    assert "data/output/Pixellab/Grid Files/**" in ignore
    assert "data/output/Pixellab/Final/**" in ignore
    assert "data/output/Owner Suggestions/**" not in ignore
    assert "data/Release Pool/**" in ignore


def test_owner_art_layout_is_pixellab_only_and_repo_local() -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-art-storage-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        repository = root / "repo"
        repository.mkdir(parents=True)
        paths = owner_art_storage.ensure_owner_art_layout(repository)
        assert all(path.is_dir() for path in paths.values())
        assert "alpix" not in paths and "owner_suggestions" not in paths
        assert not (repository / "data/output/Alpix").exists()
        assert not (repository / "data/output/Owner Suggestions").exists()
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner-art test output escaped its owned directory")
            shutil.rmtree(root)


def test_pixellab_catalog_archives_exact_slices_and_finalizes_atomically() -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-art-storage-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        repository = root / "repo"
        source = root / "source"
        (repository / "unused").mkdir(parents=True)
        source.mkdir(parents=True)
        atlas = Image.new("RGBA", (208, 208), (0, 0, 0, 0))
        frames = []
        for index in range(1, 17):
            filename = f"sprite-{index:02d}.png"
            color = (index * 11, index * 7, index * 5, 255)
            sprite = Image.new("RGBA", (52, 52), color)
            buffer = BytesIO()
            sprite.save(buffer, format="PNG")
            raw_sprite = buffer.getvalue()
            (source / filename).write_bytes(raw_sprite)
            x = ((index - 1) % 4) * 52
            y = ((index - 1) // 4) * 52
            atlas.paste(sprite, (x, y))
            frames.append({"index": index, "filename": filename, "sha256": hashlib.sha256(raw_sprite).hexdigest()})
        atlas_buffer = BytesIO()
        atlas.save(atlas_buffer, format="PNG")
        raw_png = atlas_buffer.getvalue()
        digest = hashlib.sha256(raw_png).hexdigest()
        (source / "original-atlas.png").write_bytes(raw_png)
        manifest = {
            "schema": "scrubbots-pixellab-pro-4x4-source/v2",
            "source_atlas_sha256": digest,
            "source_kind": "IMPORTED_ATLAS",
            "source_dimensions": [208, 208],
            "frame_dimensions": [52, 52],
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
        assert Path(first["catalog_path"]).parent == source
        assert first["transaction_state"] == "FINALIZED"
        transaction = json.loads(Path(first["transaction_path"]).read_text(encoding="utf-8"))
        assert transaction["state"] == "FINALIZED"
        assert len(transaction["slices"]) == 16
        assert owner_art_storage.pixellab_asset_name_manifest(repository).is_file()
        assert json.loads(Path(first["catalog_path"]).read_text(encoding="utf-8")) == {
            key: value for key, value in first.items() if key not in {"catalog_path", "transaction_path", "transaction_state"}
        }
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner-art test output escaped its owned directory")
            shutil.rmtree(root)


def test_pixellab_atlas_frame_dimensions_follow_approved_51_to_59_range() -> None:
    assert owner_art_storage._dimension_pair([51, 59], "fixture") == (51, 59)
    for dimensions in ([50, 56], [56, 60], [True, 56], [56, 56.0]):
        with pytest.raises(owner_art_storage.OwnerArtStorageError, match="approved 51..59"):
            owner_art_storage._dimension_pair(dimensions, "fixture")


def test_pixellab_interrupted_archive_rolls_back_new_pngs_and_keeps_in_progress_marker(tmp_path: Path, monkeypatch) -> None:
    repository = tmp_path / "repo"
    source = tmp_path / "source"
    repository.mkdir()
    source.mkdir()
    atlas = Image.new("RGBA", (208, 208), (0, 0, 0, 0))
    frames = []
    for index in range(1, 17):
        sprite = Image.new("RGBA", (52, 52), (index * 11, index * 7, index * 5, 255))
        buffer = BytesIO()
        sprite.save(buffer, format="PNG")
        raw = buffer.getvalue()
        filename = f"sprite-{index:02d}.png"
        (source / filename).write_bytes(raw)
        atlas.paste(sprite, (((index - 1) % 4) * 52, ((index - 1) // 4) * 52))
        frames.append({"index": index, "filename": filename, "sha256": hashlib.sha256(raw).hexdigest()})
    atlas_buffer = BytesIO()
    atlas.save(atlas_buffer, format="PNG")
    raw_atlas = atlas_buffer.getvalue()
    (source / "original-atlas.png").write_bytes(raw_atlas)
    atlas_sha = hashlib.sha256(raw_atlas).hexdigest()
    manifest = {
        "schema": "scrubbots-pixellab-pro-4x4-source/v2", "source_atlas_sha256": atlas_sha,
        "source_kind": "IMPORTED_ATLAS", "source_dimensions": [208, 208],
        "frame_dimensions": [52, 52], "frames": frames,
    }
    original_write = owner_art_storage._write_content_addressed
    calls = 0

    def interrupt_on_fourth_write(directory: Path, filename: str, raw: bytes, digest: str) -> Path:
        nonlocal calls
        calls += 1
        if calls == 4:
            raise OSError("fixture interrupted publication")
        return original_write(directory, filename, raw, digest)

    monkeypatch.setattr(owner_art_storage, "_write_content_addressed", interrupt_on_fourth_write)
    with pytest.raises(OSError, match="fixture interrupted"):
        owner_art_storage.archive_pixellab_export(source, manifest, repository_root=repository)
    paths = owner_art_storage.owner_art_paths(repository)
    assert not list(paths["pixellab_grid_files"].glob("*.png"))
    assert not list(paths["pixellab_final"].glob("*.png"))
    transaction_path = paths["pending"] / f"pixellab-atlas-{atlas_sha}.json"
    transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
    assert transaction["state"] == "IN_PROGRESS"
    partial_name = f"atlas-{atlas_sha}-sprite-01-{frames[0]['sha256']}.png"
    (paths["pixellab_final"] / partial_name).write_bytes((source / frames[0]["filename"]).read_bytes())
    scanned = owner_folder_batch.scan_owner_source_folder(paths["pixellab_final"], repository_root=repository)
    assert scanned["entries"][0]["disposition"] == "REJECTED"
    assert scanned["entries"][0]["reason"] == "PIXELLAB_ATLAS_TRANSACTION_INCOMPLETE_OR_INVALID"


def test_owner_folder_scan_is_non_recursive_pixellab_only_and_uncapped(monkeypatch) -> None:
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
        Image.new("RGBA", (56, 56), (10, 20, 30, 255)).save(png_bytes, format="PNG")
        for name in ("b.png", "A.PNG"):
            (folders["PIXELLAB"] / name).write_bytes(png_bytes.getvalue())
        nested = folders["PIXELLAB"] / "nested"
        nested.mkdir()
        (nested / "ignored.png").write_bytes(png_bytes.getvalue())
        (grid / "raw-atlas.png").write_bytes(png_bytes.getvalue())

        def transaction_index(paths):
            return {
                item.name: {"state": "FINALIZED", "sha256": hashlib.sha256(item.read_bytes()).hexdigest(),
                            "group_valid": "true"}
                for item in paths["pixellab_final"].glob("*.png")
            }

        monkeypatch.setattr(owner_folder_batch, "_pixellab_transaction_index", transaction_index)

        scanned = owner_folder_batch.scan_owner_source_folder(folders["PIXELLAB"], repository_root=repository)

        assert scanned["provider"] == "PIXELLAB"
        assert [Path(path).name for path in scanned["paths"]] == ["A.PNG", "b.png"]
        assert scanned["png_count"] == 2
        invalid = folders["PIXELLAB"] / "invalid.png"
        invalid.write_bytes(b"not a PNG")
        rescanned = owner_folder_batch.scan_owner_source_folder(folders["PIXELLAB"], repository_root=repository)
        assert rescanned["png_count"] == 3
        assert any(item.get("disposition") == "REJECTED" and item.get("display_path") == "invalid.png" for item in rescanned["entries"])
        with pytest.raises(owner_folder_batch.OwnerFolderBatchError, match="raw atlases"):
            owner_folder_batch.scan_owner_source_folder(grid, repository_root=repository, explicit_alternative=True)
        alternative = root / "manually-selected"
        alternative.mkdir()
        with pytest.raises(owner_folder_batch.OwnerFolderBatchError, match="canonical owner artwork folders"):
            owner_folder_batch.scan_owner_source_folder(alternative, repository_root=repository, explicit_alternative=True)
        large_folder = root / "large-repo" / "data" / "output" / "Pixellab" / "Final"
        large_folder.mkdir(parents=True)
        for index in range(151):
            (large_folder / f"{index:03d}.png").write_bytes(b"")
        progress_events = []
        large_scan = owner_folder_batch.scan_owner_source_folder(
            large_folder, repository_root=root / "large-repo", progress_callback=progress_events.append,
        )
        assert large_scan["png_count"] == 151
        assert len(large_scan["entries"]) == 151
        assert all(item["disposition"] == "REJECTED" for item in large_scan["entries"])
        assert progress_events[0]["stage"] == "FOLDER"
        discovery_event = next(event for event in progress_events if event["stage"] == "DISCOVERY")
        assert discovery_event["total"] == 151
        file_events = [event for event in progress_events if event["stage"] == "FILE CHECK"]
        assert len(file_events) == 151
        assert file_events[-1]["completed"] == 151
        assert file_events[-1]["total"] == 151
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner-folder test output escaped its owned directory")
            shutil.rmtree(root)


def test_owner_folder_import_keeps_original_indices_for_already_imported_files(monkeypatch) -> None:
    paths = [r"C:\owner\Final\first.png", r"C:\owner\Final\second.png"]
    entries = [
        {"index": 0, "path": paths[0], "display_path": "first.png", "disposition": "ALREADY_IMPORTED"},
        {"index": 1, "path": paths[1], "display_path": "second.png", "disposition": "ALREADY_IMPORTED"},
    ]
    monkeypatch.setattr(
        owner_folder_batch,
        "scan_owner_source_folder",
        lambda *_args, **_kwargs: {
            "paths": paths, "entries": entries, "pre_rejected": [],
            "provider": "PIXELLAB", "selected_folder": r"C:\owner\Final", "png_count": 2,
        },
    )
    received: dict[str, object] = {}

    def batch_import(selected_paths, **kwargs):
        received["paths"] = list(selected_paths)
        received.update(kwargs)
        return {"items": [
            {"index": index, "source_id": f"owner-upload-{index}", "disposition": "ALREADY_IMPORTED"}
            for index, _path in zip(kwargs["path_indices"], selected_paths)
        ]}

    monkeypatch.setattr(studio_extensions, "batch_import", batch_import)
    result = owner_folder_batch.import_owner_source_folder(r"C:\owner\Final")

    assert received["paths"] == paths
    assert received["path_indices"] == [0, 1]
    assert [item["index"] for item in result["items"]] == [0, 1]
    assert result["png_count"] == 2


def test_batch_import_classifies_repeat_and_same_batch_sha_as_skip(monkeypatch) -> None:
    root = Path(__file__).resolve().parent / ".r10-owner-folder-dedupe-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    root.mkdir()
    ledger = root / "ledger"
    calls = {}

    def fake_import(path, **_kwargs):
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

        first = studio_extensions.batch_import(files, source_provider="PIXELLAB", source_folder="approved")
        second = studio_extensions.batch_import(files, source_provider="PIXELLAB", source_folder="approved")

        assert first["items"][0]["disposition"] == "IMPORTED"
        assert first["items"][1]["disposition"] == "SKIPPED_DUPLICATE"
        assert first["items"][0]["filename_collision"] is True
        assert first["items"][2]["filename_collision"] is True
        assert first["items"][2]["source_id"] != first["items"][0]["source_id"]
        assert first["counts"]["imported"] == 2 and first["counts"]["skipped"] == 1
        another_folder_file = root / "four" / "same.png"
        another_folder_file.parent.mkdir()
        another_folder_file.write_bytes(b"different provider folder identity")
        cross_folder = studio_extensions.batch_import([another_folder_file], source_provider="PIXELLAB", source_folder="other-approved-folder")
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
        monkeypatch.setattr(owner_upload, "owner_upload_root", lambda *_args: upload_root)

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _index: owner_upload.import_owner_upload(source_path), range(8)))

        states = [item["state"] for item in results]
        assert states.count("IMPORTED") == 1
        assert states.count("ALREADY_IMPORTED") == 7
        source_id = "owner-upload-" + hashlib.sha256(raw).hexdigest()
        assert len(list(upload_root.glob(f"{source_id}/same.png"))) == 1

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
        atlas_manifest = root / "data/Release Pool/Pending" / ("pixellab-atlas-" + "c" * 64 + ".json")
        atlas_manifest.write_text(json.dumps({
            "schema": "scrubbots-pixellab-atlas-transaction/v1", "state": "FINALIZED",
            "source_atlas_sha256": "c" * 64,
        }), encoding="utf-8")
        assert owner_release_library.list_records(repository_root=root)["counts"]["PENDING"] == 1
        repeated = owner_release_library.transition(source_id, "PENDING", **kwargs)
        assert repeated["idempotent"] is True
        failed = owner_release_library.transition(source_id, "FAILED", **{**kwargs, "reason": "synthetic solver timeout",
            "pipeline_run_id": "run-first", "evidence": {"solution": {"state": "NOT_AVAILABLE"}}})
        with pytest.raises(owner_release_library.OwnerReleaseLibraryError, match="explicit retry bound to the prior event"):
            owner_release_library.transition(source_id, "PENDING", **{**kwargs, "retry_of": failed["event_sha256"]})
        retried = owner_release_library.transition(source_id, "PENDING", **{**kwargs, "reason": "explicit retry",
            "pipeline_run_id": "run-retry", "retry_of": failed["event_sha256"], "evidence": {"explicit_retry": True}})

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
        # The canonical Release Pool candidate entry shares Ready with owner
        # status projections; it must be recognized by identity and digest.
        candidate_entry = {"schema": "scrubbots-release-pool-entry/v1",
            "candidate_id": "candidate-owner-import-test", "pipeline_run_id": "pipeline-import-test",
            "review_id": None, "entry_digest": ""}
        candidate_entry["entry_digest"] = hashlib.sha256(json.dumps(
            {key: value for key, value in candidate_entry.items() if key != "entry_digest"}, ensure_ascii=False,
            sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        candidate_entry_path = root / "data/Release Pool/Ready/candidate-owner-import-test-pipeline-import-test-ready.json"
        candidate_entry_path.write_text(json.dumps(candidate_entry), encoding="utf-8")
        repeat_import = owner_release_library.record_import_items({"batch_id": "batch-import-repeat",
            "source_provider": "ALPIX", "items": [{"source_id": source_id, "source_sha256": digest,
            "original_source_path": str(source), "disposition": "ALREADY_IMPORTED"}]}, repository_root=root)
        assert repeat_import["records"][0]["status"] == "READY" and repeat_import["records"][0]["idempotent"] is True
        view = owner_release_library.list_records(repository_root=root)
        assert view["counts"] == {"FAILED": 0, "PENDING": 0, "READY": 1, "REJECTED": 0}
        assert view["records"][0]["artifact"]["sha256"] == digest
        candidate_entry["entry_digest"] = "0" * 64
        candidate_entry_path.write_text(json.dumps(candidate_entry), encoding="utf-8")
        with pytest.raises(owner_release_library.OwnerReleaseLibraryError, match="Release Pool entry digest is invalid"):
            owner_release_library.list_records(repository_root=root)
        candidate_entry["entry_digest"] = hashlib.sha256(json.dumps(
            {key: value for key, value in candidate_entry.items() if key != "entry_digest"},
            ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        candidate_entry_path.write_text(json.dumps(candidate_entry), encoding="utf-8")
        assert (root / "data/Release Pool/Ready" / f"{source_id}.json").is_file()
        assert hashlib.sha256((root / "data/Release Pool/Ready" / source.name).read_bytes()).hexdigest() == digest
        assert not (root / "data/Release Pool/Pending" / f"{source_id}.json").exists()
        assert len(list((root / "data/Release Pool/.history" / source_id).glob("*.json"))) == 4

        rejected = owner_release_library.transition(source_id, "REJECTED", **{**kwargs, "reason": "owner rejected"})
        assert rejected["status"] == "REJECTED"
        assert not (root / "data/Release Pool/Ready" / f"{source_id}.json").exists()
        assert not (root / "data/Release Pool/Ready" / source.name).exists()
        assert (root / "data/Release Pool/Rejected" / f"{source_id}.json").is_file()
        assert hashlib.sha256((root / "data/Release Pool/Rejected" / source.name).read_bytes()).hexdigest() == digest
        with pytest.raises(owner_release_library.OwnerReleaseLibraryError, match="excluded from solver retry"):
            owner_release_library.assert_solver_allowed([source_id], repository_root=root)
        with pytest.raises(owner_release_library.OwnerReleaseLibraryError, match="explicit retry bound to the prior event"):
            owner_release_library.transition(source_id, "PENDING", **kwargs)
        retried_rejection = owner_release_library.transition(source_id, "PENDING", **{**kwargs,
            "reason": "explicit retry after reviewing rejection", "retry_of": rejected["event_sha256"],
            "evidence": {"explicit_retry": True}})
        assert retried_rejection["status"] == "PENDING"
        assert not (root / "data/Release Pool/Rejected" / f"{source_id}.json").exists()
        final = owner_release_library.list_records(repository_root=root)
        assert final["counts"] == {"FAILED": 0, "PENDING": 1, "READY": 0, "REJECTED": 0}
        assert final["records"][0]["retry_of"] == rejected["event_sha256"]
        assert len(list((root / "data/Release Pool/.history" / source_id).glob("*.json"))) == 6

        from scrubbots_pixel_factory import studio_extensions
        monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda _source_id: {
            "source_id": source_id, "source_sha256": digest, "source_path": str(source), "original_filename": "frog.png"
        })
        job = {"batch_id": "batch-live-projection", "items": []}
        item = {"source_id": source_id, "source_sha256": digest, "original_source_path": str(source),
                "source_provider": "PIXELLAB", "status": "RUNNING", "run_id": "run-live-projection"}
        started = owner_release_library.begin_batch_item_attempt(job, item, repository_root=root)
        assert started["status"] == "PENDING"
        item["status"] = "FAILED"
        item["reason"] = "synthetic canonical solver failure"
        failed_projection = owner_release_library.record_batch_item_outcome(job, item, repository_root=root)
        assert failed_projection["status"] == "FAILED"
        assert owner_release_library.list_records(repository_root=root)["counts"]["FAILED"] == 1
        item["status"] = "REJECTED"
        item["reason"] = "synthetic source identity rejection"
        rejected_projection = owner_release_library.record_batch_item_outcome(job, item, repository_root=root)
        assert rejected_projection["status"] == "REJECTED"
        assert owner_release_library.list_records(repository_root=root)["counts"] == {
            "FAILED": 0, "PENDING": 0, "READY": 0, "REJECTED": 1
        }
        assert not (root / "data/Release Pool/Failed" / f"{source_id}.json").exists()
        assert (root / "data/Release Pool/Rejected" / f"{source_id}.json").is_file()
        assert len(list((root / "data/Release Pool/.history" / source_id).glob("*.json"))) == 9
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Owner release library test output escaped its owned directory")
            shutil.rmtree(root)


def test_owner_release_startup_reconciles_interrupted_status_projection_from_history() -> None:
    root = Path(__file__).resolve().parent / ".codex-owner-release-projection-recovery-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        source_dir = root / "source"
        source_dir.mkdir(parents=True)
        image = BytesIO()
        Image.new("RGBA", (32, 32), (30, 60, 90, 255)).save(image, format="PNG")
        raw = image.getvalue()
        source = source_dir / "recovery.png"
        source.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        source_id = "owner-upload-" + digest
        kwargs = {"source_sha256": digest, "provider": "PIXELLAB",
                  "original_source_path": str(source), "repository_root": root}
        pending = owner_release_library.transition(source_id, "PENDING", **kwargs)
        failed = owner_release_library.transition(source_id, "FAILED", **{**kwargs, "reason": "synthetic interrupted projection"})

        release_root = root / "data/Release Pool"
        failed_json = release_root / "Failed" / f"{source_id}.json"
        failed_png = release_root / "Failed" / source.name
        failed_json.unlink()
        failed_png.unlink()

        # Simulate a crash after immutable FAILED history was committed but
        # before the status-folder projection move replaced the prior PENDING row.
        pending_projection = {**pending}
        pending_digest = pending_projection.pop("event_sha256")
        pending_path = release_root / "Pending" / f"{source_id}.json"
        pending_path.write_bytes(owner_release_library._json_bytes({**pending_projection, "event_sha256": pending_digest}))
        object_path = release_root / ".objects" / f"{digest}.png"
        legacy_pending_png = release_root / "Pending" / f"{source_id}.png"
        legacy_pending_png.hardlink_to(object_path)

        recovered = owner_release_library.reconcile_status_projections(repository_root=root)
        assert recovered["state"] == "RECONCILED"
        assert recovered["checked"] == 1
        assert recovered["repaired"] == 1
        view = owner_release_library.list_records(repository_root=root)
        assert view["counts"] == {"FAILED": 1, "PENDING": 0, "READY": 0, "REJECTED": 0}
        assert view["records"][0]["event_sha256"] == failed["event_sha256"]
        assert hashlib.sha256(failed_png.read_bytes()).hexdigest() == digest
        assert not pending_path.exists()
        assert not legacy_pending_png.exists()
        assert (release_root / "Failed" / source.name).is_file()
        assert not (release_root / "Failed" / f"{source_id}.png").exists()
        history_before = sorted(path.read_bytes() for path in (release_root / ".history" / source_id).glob("*.json"))

        repeated = owner_release_library.reconcile_status_projections(repository_root=root)
        assert repeated["state"] == "RECONCILED"
        assert repeated["checked"] == 1
        assert repeated["repaired"] == 0
        assert sorted(path.read_bytes() for path in (release_root / ".history" / source_id).glob("*.json")) == history_before
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Release projection recovery fixture escaped its owned directory")
            shutil.rmtree(root)


def test_owner_release_startup_restores_terminal_batch_outcome_without_overwriting_newer_status(monkeypatch) -> None:
    root = Path(__file__).resolve().parent / ".codex-owner-release-terminal-batch-reconcile-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        from scrubbots_pixel_factory import png_batch

        source_dir = root / "source"
        source_dir.mkdir(parents=True)

        def make_png(name: str, color: tuple[int, int, int, int]):
            image = BytesIO()
            Image.new("RGBA", (32, 32), color).save(image, format="PNG")
            raw = image.getvalue()
            source = source_dir / name
            source.write_bytes(raw)
            digest = hashlib.sha256(raw).hexdigest()
            return source, raw, digest, "owner-upload-" + digest

        source, _raw, digest, source_id = make_png("recovered.png", (30, 60, 90, 255))
        protected_source, _protected_raw, protected_digest, protected_id = make_png("newer.png", (90, 60, 30, 255))
        queued_source, _queued_raw, queued_digest, queued_id = make_png("still-queued.png", (15, 120, 30, 255))
        pending_kwargs = {"source_sha256": digest, "provider": "PIXELLAB",
                          "original_source_path": str(source), "repository_root": root}
        protected_kwargs = {"source_sha256": protected_digest, "provider": "PIXELLAB",
                            "original_source_path": str(protected_source), "repository_root": root}
        owner_release_library.transition(source_id, "PENDING", **pending_kwargs)
        protected_failure = owner_release_library.transition(
            protected_id, "FAILED", **{**protected_kwargs, "reason": "newer explicit solver result"},
        )
        queued_kwargs = {"source_sha256": queued_digest, "provider": "PIXELLAB",
                         "original_source_path": str(queued_source), "repository_root": root}
        owner_release_library.transition(queued_id, "PENDING", **queued_kwargs)
        records = {}
        for sid in (source_id, protected_id, queued_id):
            record = source_dir / f"{sid}.json"
            record.write_text("{}", encoding="utf-8")
            records[sid] = record

        job_id = "png-batch-reconcile-test"
        item = {"index": 7, "source_id": source_id, "source_sha256": digest,
                "source_record_sha256": hashlib.sha256(records[source_id].read_bytes()).hexdigest(), "original_filename": "recovered.png",
                "status": "FAILED", "reason": "canonical run timed out", "run_id": "pipeline-reconcile-test",
                "finished_at": "2026-11-09T11:00:00+00:00"}
        protected_item = {**item, "index": 8, "source_id": protected_id,
                          "source_sha256": protected_digest, "original_filename": "newer.png",
                          "reason": "stale older job must not replace status"}
        queued_failure = {**item, "index": 9, "source_id": queued_id,
                          "source_sha256": queued_digest, "source_record_sha256": hashlib.sha256(records[queued_id].read_bytes()).hexdigest(),
                          "original_filename": "still-queued.png", "reason": "older failure",
                          "finished_at": "2026-11-09T10:05:00+00:00"}
        old_job = {"job_id": "png-batch-older", "import_batch_id": "batch-older", "batch_digest": "a" * 64,
                   "state_digest": "b" * 64, "created_at": "2026-11-09T10:00:00+00:00",
                   "updated_at": "2026-11-09T10:10:00+00:00", "settings": {},
                   "items": [queued_failure]}
        queued_item = {**queued_failure, "status": "QUEUED", "reason": "awaiting solver", "finished_at": None}
        job = {"job_id": job_id, "import_batch_id": "batch-reconcile-test", "batch_digest": "a" * 64,
               "state_digest": "b" * 64, "updated_at": "2026-11-09T11:01:00+00:00",
               "created_at": "2026-11-09T11:00:00+00:00", "settings": {},
               "items": [item, protected_item, queued_item]}
        jobs_root = root / "data/Level Factory/Batches/Jobs/jobs"
        jobs_root.mkdir(parents=True)
        (jobs_root / f"{job_id}.json").write_text("{}", encoding="utf-8")
        (jobs_root / f"{old_job['job_id']}.json").write_text("{}", encoding="utf-8")

        monkeypatch.setattr(png_batch, "_root", lambda: root / "data/Level Factory/Batches/Jobs")
        jobs_by_id = {job_id: job, old_job["job_id"]: old_job}
        monkeypatch.setattr(png_batch, "_read_job", lambda current_job_id: jobs_by_id[current_job_id])
        monkeypatch.setattr(png_batch, "_job_lineage_matches_snapshot", lambda _job, _batch: True)
        monkeypatch.setattr(studio_extensions, "batch_load", lambda batch_id: {"batch": {"batch_id": batch_id}})
        monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda sid, **_kwargs: {
            "source_id": sid,
            "source_sha256": {source_id: digest, protected_id: protected_digest, queued_id: queued_digest}[sid],
        })
        monkeypatch.setattr(studio_extensions, "_source_record_paths", lambda sid, *_args: (
            records[sid], {source_id: source, protected_id: protected_source, queued_id: queued_source}[sid],
        ))

        recovered = owner_release_library.reconcile_terminal_batch_projections(repository_root=root)
        assert recovered["state"] == "RECONCILED"
        assert recovered["terminal_sources"] == 1
        assert recovered["repaired"] == 1
        assert recovered["repaired_source_ids"] == [source_id]
        view = owner_release_library.list_records(repository_root=root)
        assert view["counts"] == {"FAILED": 2, "PENDING": 1, "READY": 0, "REJECTED": 0}
        rows = {row["source_id"]: row for row in view["records"]}
        assert rows[source_id]["reason"] == "canonical run timed out"
        assert rows[source_id]["evidence"]["reconciled_job_id"] == job_id
        assert rows[protected_id]["event_sha256"] == protected_failure["event_sha256"]
        assert rows[queued_id]["status"] == "PENDING"
        assert len(list((root / "data/Release Pool/.history" / source_id).glob("*.json"))) == 2
        assert len(list((root / "data/Release Pool/.history" / protected_id).glob("*.json"))) == 1
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("Batch outcome reconciliation fixture escaped its owned directory")
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


def test_pixellab_final_inventory_is_sha_reconciled_into_pending() -> None:
    from scrubbots_pixel_factory import studio_extensions

    root = Path(__file__).resolve().parent / ".r10-pixellab-final-pending-reconcile-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test-owned output: {root}")
    try:
        final = root / "data/output/Pixellab/Final"
        final.mkdir(parents=True)
        release_pool = root / "data/Release Pool"
        release_pool.mkdir(parents=True)
        source_path = final / "robot.png"
        image = BytesIO()
        Image.new("RGBA", (32, 32), (20, 40, 60, 255)).save(image, format="PNG")
        raw = image.getvalue()
        source_path.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        source_id = "owner-upload-" + digest
        imported_root = root / "data/Level Factory/Imported"
        imported_source = imported_root / source_id / source_path.name

        from scrubbots_pixel_factory import owner_art_storage, owner_folder_batch

        real_paths = owner_art_storage.owner_art_paths
        # The normal resolver already targets this fixture root when passed explicitly.
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(owner_folder_batch, "scan_owner_source_folder", lambda _folder, **_kwargs: {
            "provider": "PIXELLAB", "entries": [{"disposition": "ELIGIBLE", "source_sha256": digest,
                "path": str(source_path), "display_path": source_path.name}]
        })

        def import_source(_path: str, *, repository_root: str | Path | None = None) -> dict[str, str]:
            imported_source.parent.mkdir(parents=True, exist_ok=True)
            imported_source.write_bytes(raw)
            return {"state": "IMPORTED", "source_id": source_id}

        monkeypatch.setattr(studio_extensions, "owner_upload_root", lambda _root=None: imported_root)
        monkeypatch.setattr(studio_extensions, "import_owner_upload", import_source)
        monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda _source_id, **_kwargs: {
            "source_id": source_id, "source_sha256": digest, "source_path": str(imported_source),
            "original_filename": source_path.name,
        })
        monkeypatch.setattr(studio_extensions, "validate_owner_source", lambda *_args, **_kwargs: {
            "exact_logical_source": True, "structural": {"disposition": "PASS"},
            "void_capability": {"state": "NOT_REQUIRED"},
        })
        active, invalid = studio_extensions._sync_current_pixellab_final_sources(root)
        assert active == {source_id}
        assert invalid == []
        first = owner_release_library.list_records(repository_root=root)
        assert first["counts"]["PENDING"] == 1
        pending_png = root / "data/Release Pool/Pending" / source_path.name
        assert pending_png.read_bytes() == raw

        active_again, invalid_again = studio_extensions._sync_current_pixellab_final_sources(root)
        assert active_again == {source_id}
        assert invalid_again == []
        assert owner_release_library.list_records(repository_root=root)["counts"]["PENDING"] == 1
        assert len(list((root / "data/Release Pool/.history" / source_id).glob("*.json"))) == 1
        assert source_path.read_bytes() == raw
        assert real_paths(root)["pixellab_final"] == final
        monkeypatch.undo()
    finally:
        if root.exists():
            if root.resolve().parent != root.parent.resolve():
                raise AssertionError("PixelLab Pending reconciliation fixture escaped its owned directory")
            shutil.rmtree(root)


def test_new_lf_batch_snapshot_requires_current_pending_sha_bound_pixellab_sources(monkeypatch) -> None:
    digest_a = "a" * 64
    digest_b = "b" * 64
    source_a = "owner-upload-" + digest_a
    source_b = "owner-upload-" + digest_b
    rows = {
        "records": [
            {"source_id": source_a, "source_sha256": digest_a, "provider": "PIXELLAB",
             "status": "PENDING", "original_source_path": r"C:\Factory\Imported\a.png"},
            {"source_id": source_b, "source_sha256": digest_b, "provider": "PIXELLAB",
             "status": "READY", "original_source_path": r"C:\Factory\Imported\b.png"},
        ]
    }
    monkeypatch.setattr(owner_release_library, "list_records", lambda status=None: {
        "records": [row for row in rows["records"] if row["status"] == status]
    })
    monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda source_id: {
        "source_sha256": source_id.removeprefix("owner-upload-"),
        "original_filename": "a.png" if source_id == source_a else "b.png",
    })
    monkeypatch.setattr(studio_extensions, "create_loaded_png_batch", lambda source_ids: {
        "batch_id": "batch-loaded-pending-only", "items": [{"source_id": item} for item in source_ids]
    })
    created = studio_extensions.create_pending_png_batch([source_a])
    assert created["queue_authority"] == "CURRENT_RELEASE_POOL_PENDING"
    assert created["pending_verified_count"] == 1
    assert [item["source_id"] for item in created["items"]] == [source_a]
    with pytest.raises(studio_extensions.StudioExtensionError, match="Pending queue changed"):
        studio_extensions.create_pending_png_batch([source_b])
    with pytest.raises(studio_extensions.StudioExtensionError, match="duplicate source IDs"):
        studio_extensions.create_pending_png_batch([source_a, source_a])


def test_solve_again_can_queue_release_pool_failures_without_the_last_ui_batch(monkeypatch) -> None:
    from scrubbots_pixel_factory import png_batch

    sha_failed = "a" * 64
    sha_rejected = "b" * 64
    failed_id = "owner-upload-" + sha_failed
    rejected_id = "owner-upload-" + sha_rejected
    records = [
        {"source_id": failed_id, "source_sha256": sha_failed, "provider": "PIXELLAB", "status": "FAILED",
         "original_source_path": r"C:\Factory\data\Level Factory\Imported\failed.png", "event_sha256": "c" * 64,
         "reason": "canonical game-host timeout"},
        {"source_id": rejected_id, "source_sha256": sha_rejected, "provider": "PIXELLAB", "status": "REJECTED",
         "original_source_path": r"C:\Factory\data\Level Factory\Imported\rejected.png", "event_sha256": "d" * 64,
         "reason": "palette validation failed"},
    ]
    monkeypatch.setattr(png_batch, "_configured_game_project", lambda _settings: r"C:\Factory\game")
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda: Path(r"C:\Factory"))
    monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda source_id: {
        "source_sha256": source_id.removeprefix("owner-upload-"),
        "original_filename": "failed.png" if source_id == failed_id else "rejected.png",
    })
    monkeypatch.setattr(owner_release_library, "list_records", lambda **_kwargs: {"records": records})
    snapshots: list[list[str]] = []
    monkeypatch.setattr(studio_extensions, "create_loaded_png_batch", lambda source_ids: (
        snapshots.append(list(source_ids)) or {"batch_id": "batch-retry-snapshot", "items": []}
    ))
    transitions: list[dict[str, object]] = []

    def record_transition(source_id, status, **kwargs):
        transitions.append({"source_id": source_id, "status": status, **kwargs})
        return {"source_id": source_id, "status": status, "event_sha256": "e" * 64}

    monkeypatch.setattr(owner_release_library, "transition", record_transition)
    monkeypatch.setattr(png_batch, "create_png_batch", lambda batch_id, settings: {
        "state": "SUCCESS", "disposition": "CREATED",
        "job": {"job_id": "png-batch-retry-from-release", "import_batch_id": batch_id,
                "settings": settings, "items": []},
    })

    result = png_batch.retry_release_pool_sources([failed_id, rejected_id], {
        "game_project": r"C:\Factory\game", "solver_timeout_seconds": 900,
    })

    assert result["disposition"] == "RETRY_CREATED_FROM_RELEASE_POOL"
    assert snapshots == [[failed_id, rejected_id]]
    assert [event["status"] for event in transitions] == ["PENDING", "PENDING"]
    assert [event["retry_of"] for event in transitions] == ["c" * 64, "d" * 64]
    assert [event["evidence"]["prior_reason"] for event in transitions] == [
        "canonical game-host timeout", "palette validation failed",
    ]
    assert result["job"]["job_id"] == "png-batch-retry-from-release"


def test_solve_again_rejects_non_pixel_lab_or_non_failed_archive_records_without_mutation(monkeypatch) -> None:
    from scrubbots_pixel_factory import png_batch

    source_id = "owner-upload-" + "a" * 64
    row = {"source_id": source_id, "source_sha256": "a" * 64, "provider": "OWNER_UPLOAD",
           "status": "FAILED", "original_source_path": r"C:\Factory\failed.png", "event_sha256": "b" * 64}
    monkeypatch.setattr(png_batch, "_configured_game_project", lambda _settings: r"C:\Factory\game")
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda: Path(r"C:\Factory"))
    monkeypatch.setattr(owner_release_library, "list_records", lambda **_kwargs: {"records": [row]})
    monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda _source_id: {
        "source_sha256": "a" * 64, "original_filename": "failed.png",
    })
    monkeypatch.setattr(studio_extensions, "create_loaded_png_batch", lambda _source_ids: pytest.fail("must not snapshot"))

    result = png_batch.retry_release_pool_sources([source_id], {"game_project": r"C:\Factory\game"})
    assert result["disposition"] == "RETRY_SOURCE_NOT_FAILED_OR_REJECTED"


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
    assert 'state in ["FAILED", "REJECTED"]' in ui
    assert '"Retry Failed / Rejected (%d)"' in ui
    assert '"Retry This PNG"' in ui
    assert 'func _pending_gameplay_sources()' in ui
    assert '"Run Pending Batch (%d)"' in ui
    assert '_startup_source_inventory_loaded' in ui
    assert 'STARTUP_INVENTORY_COMPLETE' in ui
    assert "_refresh_owner_release_library_panel()" in ui
    assert "Keep prior loaded-batch failures visible" in ui
    assert 'str(record.get("status", "")) in ["FAILED", "REJECTED"]' in ui
    assert 'pipeline.get("disposition") != "READY"' in canonical_pool
    assert "canonical solver/replay/difficulty/QA and owner-eligibility evidence" in Path("src/scrubbots_pixel_factory/owner_release_library.py").read_text(encoding="utf-8")


def test_solve_again_retries_only_current_pixel_lab_rows_with_verified_imported_png_bytes() -> None:
    ui = Path("level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    retry = ui.split("func _retry_failed_png_batch(", 1)[1].split("func _dispatch_png_batch_job(", 1)[0]
    verifier = retry.split("func _verified_retryable_release_sources(", 1)[1]
    solve_again = ui.split("func _solve_again()", 1)[1].split("func _preview_replay()", 1)[0]
    panel = ui.split("func _refresh_owner_release_library_panel()", 1)[1].split("func _select_owner_archive_record(", 1)[0]

    assert 'str(record.get("provider", "")).to_upper() != "PIXELLAB"' in verifier
    assert 'str(record.get("status", "")) not in ["FAILED", "REJECTED"]' in verifier
    assert 'source_id != "owner-upload-" + source_sha' in verifier
    assert 'active_source_id == "owner-upload-" + active_source_sha' in verifier
    assert 'not active_final_shas.has(source_id)' in verifier
    assert 'str(active_final_shas.get(source_id, "")) != source_sha' in verifier
    assert '"Level Factory/Imported/%s/source.json" % source_id' in verifier
    assert '"Level Factory/Imported/%s/%s" % [source_id, filename]' in verifier
    assert "hash_context.finish().hex_encode() != source_sha" in verifier
    assert '"skipped": skipped' in verifier
    assert 'not active_final_shas.has(source_id)' in panel
    assert 'str(item.get("source_sha256", "")) != str(active_final_shas.get(source_id, ""))' in panel
    assert 'for record in records:' in panel
    assert '_retry_failed_png_batch()' in solve_again


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


def test_new_solve_gate_accepts_only_current_canonical_final_sources(monkeypatch) -> None:
    import sys

    scripts = str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    launcher = __import__("factory_core_launcher")
    from scrubbots_pixel_factory import studio_extensions

    current = "owner-upload-" + "1" * 64
    legacy = "owner-upload-" + "2" * 64
    monkeypatch.setattr(studio_extensions, "_sync_current_pixellab_final_sources",
                        lambda _root, *, game_project=None: ({current}, []))
    assert launcher._canonical_final_source_gate([current]) is None
    blocked = launcher._canonical_final_source_gate([legacy])
    assert blocked is not None
    assert blocked["state"] == "BLOCKED"
    assert blocked["disposition"] == "PIXELLAB_FINAL_ONLY"
    assert blocked["excluded_source_ids"] == [legacy]


def test_new_solve_gate_fails_closed_when_final_inventory_cannot_be_verified(monkeypatch) -> None:
    import sys

    scripts = str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    launcher = __import__("factory_core_launcher")
    from scrubbots_pixel_factory import studio_extensions

    monkeypatch.setattr(studio_extensions, "_sync_current_pixellab_final_sources",
                        lambda _root, *, game_project=None: (_ for _ in ()).throw(OSError("synthetic inventory failure")))
    blocked = launcher._canonical_final_source_gate(["owner-upload-" + "3" * 64])
    assert blocked is not None
    assert blocked["state"] == "BLOCKED"
    assert blocked["disposition"] == "CANONICAL_FINAL_INVENTORY_UNAVAILABLE"


def test_new_pipeline_records_use_release_pool_status_folders_and_ignore_legacy_paths(tmp_path: Path, monkeypatch) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    extension_root = repository / "level_factory" / "output" / "studio-extensions"
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: extension_root)

    ready = studio_extensions._write_pipeline_record({"run_id": "pipeline-ready-fixture", "disposition": "READY"})
    failed = studio_extensions._write_pipeline_record({"run_id": "pipeline-failed-fixture", "disposition": "UNAVAILABLE"})
    pending = studio_extensions._write_pipeline_record({"run_id": "pipeline-pending-fixture", "disposition": "INTERRUPTED"})
    assert ready == repository / "data/Release Pool/Ready/Pipelines/pipeline-ready-fixture.json"
    assert failed == repository / "data/Release Pool/Failed/Pipelines/pipeline-failed-fixture.json"
    assert pending == repository / "data/Release Pool/Pending/Pipelines/pipeline-pending-fixture.json"
    assert studio_extensions._pipeline_path("pipeline-ready-fixture") == ready

    legacy = extension_root / "pipelines" / "pipeline-legacy-fixture.json"
    legacy.parent.mkdir(parents=True)
    legacy.write_text('{"run_id":"pipeline-legacy-fixture"}', encoding="utf-8")
    assert studio_extensions._pipeline_path("pipeline-legacy-fixture") == repository / "data/Release Pool/Pending/Pipelines/pipeline-legacy-fixture.json"
    assert legacy not in studio_extensions._pipeline_paths()
    conflicting_legacy = extension_root / "pipelines" / ready.name
    conflicting_legacy.write_text('{"run_id":"pipeline-ready-fixture","disposition":"FAILED"}', encoding="utf-8")
    assert studio_extensions._pipeline_path("pipeline-ready-fixture") == ready
    assert conflicting_legacy.is_file()  # Legacy history is preserved but cannot override canonical status.
    with pytest.raises(studio_extensions.StudioExtensionError, match="unsafe"):
        studio_extensions._pipeline_path("../escape")


def test_pixellab_status_dialog_is_fixed_provider_without_selection_controls() -> None:
    ui = Path("level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    dialog = ui.split("func _choose_provider() -> void:", 1)[1].split("func _provider_status_for", 1)[0]
    assert '_provider_model = "PIXELLAB"' in dialog
    assert 'dialog.title = "PixelLab Pro · 4×4"' in dialog
    assert 'dialog.add_button("Refresh status"' in dialog
    assert 'dialog.add_button("Open Credential Manager"' in dialog
    assert "choice" not in dialog
    assert "ALPIX" not in dialog


def test_pixellab_details_gallery_spacing_is_fixed_and_alpix_is_unmodified_by_helper() -> None:
    ui = Path("level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    layout = ui.split("func _layout_pixellab_details_artwork_gap() -> void:", 1)[1].split("func _layout_level_factory_thumbnail_dock", 1)[0]
    assert 'if _screen != "PIXEL ART" or _provider_model != "PIXELLAB":' in layout
    assert "const DETAILS_ARTWORK_GAP := 38.0" in layout
    assert "details.get_content_height()" in layout
    assert "details.scroll_active = content_height > viewport_height + 0.5" in layout
    assert "artwork_top := details.position.y + viewport_height + DETAILS_ARTWORK_GAP" in layout
    assert "card.position.y = float(card_base.get(\"position\", card.position).y) * scale_y + artwork_delta" in layout
    assert "actions[index].position.y = float(action_base.get(\"position\", actions[index].position).y) * scale_y + artwork_delta" in layout
