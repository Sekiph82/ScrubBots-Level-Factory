from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

import pytest

from scrubbots_pixel_factory.supply_pipeline.game_publisher import publish_batch
from scrubbots_pixel_factory.supply_pipeline.game_rules import find_godot
from scrubbots_pixel_factory.supply_pipeline.progression import describe_target, load_progression_authority


def _is_scrubbots_origin(remote_url: str) -> bool:
    normalized = remote_url.strip().removesuffix(".git").rstrip("/").casefold()
    return normalized in {
        "https://github.com/sekiph82/scrubbots",
        "http://github.com/sekiph82/scrubbots",
        "git@github.com:sekiph82/scrubbots",
        "ssh://git@github.com/sekiph82/scrubbots",
    }


def _game_authority_checkout() -> Path:
    configured = os.environ.get("SCRUBBOTS_PROJECT", "").strip()
    if not configured:
        pytest.skip("SCRUBBOTS_PROJECT was not explicitly provided for this run")
    candidate = Path(configured).expanduser().resolve()
    if not candidate.is_dir():
        pytest.fail("explicit SCRUBBOTS_PROJECT is not an existing directory")
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"], cwd=candidate, capture_output=True, text=True, check=False
    )
    if result.returncode != 0 or not _is_scrubbots_origin(result.stdout):
        pytest.fail("explicit SCRUBBOTS_PROJECT origin must resolve to Sekiph82/Scrubbots")
    return candidate


def _godot_executable() -> str | None:
    return find_godot()


def test_batch_published_catalog_loads_through_current_level_catalog(tmp_path: Path):
    authority_repo = _game_authority_checkout()
    godot = _godot_executable()
    if godot is None:
        pytest.skip("Godot executable is unavailable")
    before_status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=authority_repo, check=True, capture_output=True, text=True,
    ).stdout
    authority_commit = subprocess.run(["git", "rev-parse", "origin/main"], cwd=authority_repo, check=True, capture_output=True, text=True).stdout.strip()
    archive_path = tmp_path / "scrubbots-authority.tar"
    with archive_path.open("wb") as archive_file:
        subprocess.run(["git", "archive", "--format=tar", "origin/main"], cwd=authority_repo, check=True, stdout=archive_file, timeout=180)
    project = tmp_path / "scrubbots-authority"
    project.mkdir()
    with tarfile.open(archive_path, mode="r:") as bundle:
        bundle.extractall(project, filter="data")

    catalog_path = project / "data/levels/catalog/production_catalog_v1.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    template = next(entry for entry in catalog["entries"] if entry.get("supply_plan_path"))
    level_path = project / str(template["level_path"]).removeprefix("res://")
    plan_path = project / str(template["supply_plan_path"]).removeprefix("res://")
    preview_path = project / str(template["preview_path"]).removeprefix("res://")
    level = json.loads(level_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    identity = "campaign-catalog-fixture"
    level["id"] = identity
    plan["levelId"] = identity
    test_level = tmp_path / "candidate-level.json"
    test_level.write_text(json.dumps(level), encoding="utf-8")
    test_plan = tmp_path / "candidate-supply.json"
    test_plan.write_text(json.dumps(plan), encoding="utf-8")
    source_bundle = tmp_path / "source-bundle"
    source_bundle.mkdir()
    shutil.copy2(preview_path, source_bundle / "artwork.png")

    current = load_progression_authority(project)
    next_order = max(entry["order"] for entry in catalog["entries"]) + 1
    target = describe_target(next_order, current)
    pipeline = {"run_id": "catalog-load-fixture", "disposition": "READY", "primary": {"state": "READY", "level_id": identity, "load_check": {"state": "READY", "disposition": "READY"}, "files": {"level": str(test_level), "supply_plan": str(test_plan)}, "difficulty": {"score": target["target_challenge"], "class": target["class"]}, "solver_metrics": {}}}
    candidate = {"candidate_id": identity, "artwork_sha256": "a" * 64, "grid_hash": "b" * 64, "background_intent": "BACKGROUND", "used_colors": level.get("palette", []), "source_lineage": {"source_sha256": "c" * 64}}
    result = publish_batch(game_project=project, items=[{"candidate": candidate, "pipeline": pipeline, "source_bundle": source_bundle, "level_number": next_order}])
    assert result["orders"] == [next_order]

    runner = project / "tests/campaign_catalog_load_check.gd"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text('''extends SceneTree
func _initialize():
\tvar catalog = load("res://scripts/data/level_catalog.gd").new()
\tvar result = catalog.load_manifest()
\tif not result.ok:
\t\tfor err in result.errors: push_error(str(err))
\t\tquit(1)
\telse:
\t\tprint("CAMPAIGN_LEVEL_CATALOG_PASS")
\t\tquit(0)
''', encoding="utf-8")
    try:
        loaded = subprocess.run([godot, "--headless", "--path", str(project), "--script", "res://tests/campaign_catalog_load_check.gd"], capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired as exc:
        pytest.fail(f"current-game LevelCatalog/validate_all/DifficultyV1CatalogCheck timed out after 300 seconds (Godot capability existed; authority origin/main={authority_commit}); stdout={exc.stdout!r}; stderr={exc.stderr!r}")
    assert loaded.returncode == 0 and "CAMPAIGN_LEVEL_CATALOG_PASS" in loaded.stdout, f"authority origin/main={authority_commit}; stdout={loaded.stdout}\nstderr={loaded.stderr}"
    after_status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=authority_repo, check=True, capture_output=True, text=True,
    ).stdout
    assert after_status == before_status, "explicit game authority checkout must remain read-only"


def test_missing_capability_ignores_existing_fake_home_desktop_checkout(monkeypatch, tmp_path: Path) -> None:
    fake_home = tmp_path / "fake-home"
    fake_checkout = fake_home / "Desktop" / "ScrubBots"
    fake_checkout.mkdir(parents=True)
    (fake_checkout / "project.godot").write_text("fake", encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    monkeypatch.delenv("SCRUBBOTS_PROJECT", raising=False)

    def unexpected_git(*args, **kwargs):
        pytest.fail("missing capability must skip before any git access")

    monkeypatch.setattr(subprocess, "run", unexpected_git)
    with pytest.raises(pytest.skip.Exception, match="not explicitly provided"):
        _game_authority_checkout()


@pytest.mark.parametrize(
    "remote_url, expected",
    [
        ("https://github.com/Sekiph82/Scrubbots.git", True),
        ("git@github.com:Sekiph82/Scrubbots.git", True),
        ("https://evil.invalid/Sekiph82/Scrubbots.git", False),
        ("https://github.com/other/Scrubbots.git", False),
    ],
)
def test_game_authority_origin_identity_is_exact(remote_url: str, expected: bool) -> None:
    assert _is_scrubbots_origin(remote_url) is expected
