from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from scrubbots_pixel_factory import alpix_batch


def _png(path: Path, size: tuple[int, int]) -> None:
    image = Image.new("RGBA", size, (40, 80, 120, 255))
    image.save(path, format="PNG")


def test_alpix_discovery_uses_installed_enabled_plugin_and_server_names(tmp_path: Path) -> None:
    home = tmp_path
    config = home / ".claude"
    install = config / "plugins" / "cache" / "alpix-art"
    manifest = install / ".claude-plugin" / "plugin.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"name": "Alpix image tool"}), encoding="utf-8")
    (install / ".mcp.json").write_text(json.dumps({"mcpServers": {"alpix-draw-native": {"command": "node"}}}), encoding="utf-8")
    settings = {"enabledPlugins": {"alpix-art@owner-marketplace": True}}
    (config / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    plugins = {"version": 2, "plugins": {"alpix-art@owner-marketplace": [{"installPath": str(install)}]}}
    installed = config / "plugins" / "installed_plugins.json"
    installed.write_text(json.dumps(plugins), encoding="utf-8")
    cli = home / ".local" / "bin" / "claude.exe"
    cli.parent.mkdir(parents=True)
    cli.write_bytes(b"fixture")

    result = alpix_batch.discover_alpix(user_home=home)

    assert result["available"] is True
    assert result["plugin_id"] == "alpix-art@owner-marketplace"
    assert result["mcp_servers"] == "alpix-draw-native"
    assert result["executable"] == str(cli)


def test_alpix_single_uses_discovered_claude_and_never_passes_api_keys(tmp_path: Path, monkeypatch) -> None:
    destination = tmp_path / "one.png"
    captured: dict[str, object] = {}
    discovery = {"available": True, "executable": "claude", "plugin_id": "owner/alpix",
                 "mcp_servers": "alpix-image-tool"}

    def runner(args, **kwargs):
        captured["args"] = args
        captured["env"] = kwargs["env"]
        _png(destination, (24, 32))
        return SimpleNamespace(returncode=0, stdout="done", stderr="")

    monkeypatch.setenv("ANTHROPIC_API_KEY", "must-not-be-forwarded")
    result = alpix_batch.generate_alpix_png(prompt="a blue owl", width=24, height=32,
                                            destination=destination, discovery=discovery, runner=runner)

    assert result["provider_id"] == "ALPIX_CLAUDE"
    assert result["sha256"] == hashlib.sha256(destination.read_bytes()).hexdigest()
    assert "a blue owl" in captured["args"][2]
    assert "24x32" in captured["args"][2]
    assert "must-not-be-forwarded" not in captured["env"]


def test_legacy_csv_forms_normalize_prompts_size_aliases_and_disabled_rows() -> None:
    rows = alpix_batch.read_rows(
        b"prompt;size;enabled\nBlue owl;24x32;yes\nSkipped;32x32;no\nRed fish;;true\n",
        default_size=(28, 28),
    )
    assert rows == [
        {"prompt": "Blue owl", "width": 24, "height": 32, "reference": ""},
        {"prompt": "Red fish", "width": 28, "height": 28, "reference": ""},
    ]
    plain = alpix_batch.read_rows(b"prompt;size\nTree;20x22\n", default_size=(30, 30))
    assert plain[0]["width"] == 20 and plain[0]["height"] == 22


def test_csv_job_limit_resume_and_restart_never_redraw_completed_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "requests.csv"
    csv_path.write_text("prompt,size\nOwl,20x21\nFish,22x23\n", encoding="utf-8")
    job_root = tmp_path / "jobs"
    render_calls: list[str] = []
    import_calls: list[str] = []

    def renderer(prompt: str, width: int, height: int, output: Path):
        render_calls.append(prompt)
        if prompt == "Fish" and render_calls.count("Fish") == 1:
            raise alpix_batch.AlpixUsageLimit()
        _png(output, (width, height))
        return {"path": str(output)}

    def importer(path: Path):
        import_calls.append(path.name)
        return {"source_id": "source-" + path.stem}

    limited = alpix_batch.run_csv_job(csv_path, job_root, renderer=renderer, importer=importer)
    assert limited.state == "LIMIT"
    assert [row["state"] for row in limited.rows] == ["IMPORTED", "PENDING"]
    assert limited.completed == 1 and limited.remaining == 1

    resumed = alpix_batch.run_csv_job(csv_path, job_root, renderer=renderer, importer=importer)
    assert resumed.state == "COMPLETE"
    assert render_calls == ["Owl", "Fish", "Fish"]
    assert import_calls == ["row-00001.png", "row-00002.png"]

    restarted = alpix_batch.run_csv_job(csv_path, job_root, renderer=renderer, importer=importer)
    assert restarted.state == "COMPLETE"
    assert render_calls == ["Owl", "Fish", "Fish"]
    assert import_calls == ["row-00001.png", "row-00002.png"]


def test_csv_job_sha_changes_with_csv_bytes_and_unavailable_preserves_pending(tmp_path: Path) -> None:
    csv_path = tmp_path / "requests.csv"
    csv_path.write_text("prompt\nOwl\n", encoding="utf-8")
    root = tmp_path / "jobs"

    def unavailable(*_args):
        raise alpix_batch.AlpixUnavailable("Alpix is not installed")

    def importer(_path):
        raise AssertionError("unavailable generation cannot import")

    first = alpix_batch.run_csv_job(csv_path, root, renderer=unavailable, importer=importer)
    assert first.state == "UNAVAILABLE" and first.rows[0]["state"] == "PENDING"
    old_id = first.job_id
    csv_path.write_text("prompt\nDifferent owl\n", encoding="utf-8")

    def draw(prompt, width, height, output):
        _png(output, (width, height))
        return {"path": str(output)}

    second = alpix_batch.run_csv_job(csv_path, root, renderer=draw,
                                    importer=lambda _path: {"source_id": "source-new"})
    assert second.job_id != old_id
    assert len(list(root.glob("*.json"))) == 2


def test_provider_registry_reuse_keeps_magnific_external_and_pixel_lab_direct_contracts() -> None:
    from scrubbots_pixel_factory.semantic.providers.registry import available_provider_ids
    from scrubbots_pixel_factory.semantic.providers.magnific.bridge import MagnificProvider
    from scrubbots_pixel_factory.semantic.providers.pixellab.bridge import PixelLabProvider

    assert available_provider_ids() == ("MAGNIFIC", "PIXELLAB")
    assert callable(getattr(MagnificProvider, "prepare_job", None))
    assert callable(getattr(PixelLabProvider, "generate", None))


def test_magnific_ui_route_prepares_existing_external_job_without_claiming_generation() -> None:
    from level_factory.scripts.factory_core_launcher import _magnific_prepare

    result = _magnific_prepare({"prompt": "blue owl", "width": 32, "height": 32,
                                "background_intent": "BACKGROUND"})

    assert result["state"] == "PREPARED_FOR_EXTERNAL_EXECUTION"
    assert result["provider_id"] == "MAGNIFIC"
    assert result["request"]["model_slug"] == "recraft-v4-1"


def test_master_ui_uses_auto_batch_numbering_and_exact_owner_production_confirmation() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    ui = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")

    assert '_level_number_label.text = "Auto"' in ui
    assert 'PackedStringArray(["artwork_path", "supply_columns", "background_intent"])' in ui
    assert '"action": "publish-production"' in ui
    assert 'Confirm Production Promotion' in ui
    assert '"production-promotion"' not in ui


def test_ready_auto_enters_pool_reject_excludes_and_accept_restores_without_publish(tmp_path: Path, monkeypatch) -> None:
    from scrubbots_pixel_factory import studio_extensions as studio
    from scrubbots_pixel_factory.supply_pipeline import game_publisher
    from scrubbots_pixel_factory.supply_pipeline.release_pool import release_entries

    root = tmp_path / "extensions"
    monkeypatch.setattr(studio, "extensions_root", lambda: root)
    monkeypatch.setattr(studio, "_repository_root", lambda: tmp_path)
    candidate = {"candidate_id": "ready-auto-candidate", "artwork_sha256": "a" * 64,
        "grid_hash": "b" * 64, "width": 20, "height": 20, "used_colors": ["C01", "C02", "C03"],
        "source_path": "bundle", "source_lineage": {"source_sha256": "c" * 64}, "background_intent": "BACKGROUND"}
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _png(bundle / "artwork.png", (20, 20))
    level_file, supply_file = tmp_path / "level.json", tmp_path / "supply.json"
    level_file.write_text("{}", encoding="utf-8")
    supply_file.write_text("{}", encoding="utf-8")
    pipeline = {"schema": studio.PIPELINE_SCHEMA, "version": 2, "run_id": "pipeline-ready-auto",
        "candidate_id": candidate["candidate_id"], "request": {}, "disposition": "READY",
        "primary": {"state": "READY", "difficulty": {"score": 50.0, "class": "FLOW"},
            "files": {"level": str(level_file), "supply_plan": str(supply_file)},
            "solver_metrics": {"official_difficulty_v1": {"ok": True, "vector": [0.1] * 7,
                "challengeScore": 50.0, "sessionLoad": 20, "profile": {"dominant": "FLOW", "scores": {"FLOW": 0.8}, "runnerUp": "COLOR"}}}}}
    path = studio._pipeline_path(pipeline["run_id"])
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(pipeline), encoding="utf-8")
    monkeypatch.setattr(studio, "list_candidates", lambda: [candidate])
    monkeypatch.setattr(game_publisher, "publish_level", lambda **_kwargs: (_ for _ in ()).throw(AssertionError("pool actions never publish")))

    included = studio._enter_candidate_release_pool(candidate, pipeline=pipeline)
    assert included["disposition"] == "ENTERED_RELEASE_POOL"
    assert release_entries()[0]["eligibility_source"] == "READY_AUTO"

    rejected = studio.record_owner_review(candidate["candidate_id"], "REJECT", "exclude", "")
    assert rejected["publication"]["disposition"] == "EXCLUDED_FROM_RELEASE_POOL"
    assert release_entries() == []

    accepted = studio.record_owner_review(candidate["candidate_id"], "ACCEPT", "restore", "")
    assert accepted["publication"]["disposition"] == "ENTERED_RELEASE_POOL"
    pool = release_entries()
    assert len(pool) == 1 and pool[0]["eligibility_source"] == "OWNER_ACCEPT"
