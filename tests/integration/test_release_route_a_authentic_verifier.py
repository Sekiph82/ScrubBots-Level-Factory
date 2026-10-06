from __future__ import annotations

import json
import hashlib
from pathlib import Path
import subprocess
import tarfile

import pytest

from scrubbots_pixel_factory.supply_pipeline.game_rules import find_godot
from scrubbots_pixel_factory.supply_pipeline.release_route_a import RouteAError, _verify_game


_GAME_REMOTE = "https://github.com/Sekiph82/Scrubbots.git"


def _resolve_canonical_main() -> str | None:
    try:
        result = subprocess.run(
            ["git", "ls-remote", _GAME_REMOTE, "refs/heads/main"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.split()[0]


def test_default_route_a_verifier_runs_against_full_isolated_current_game_archive(tmp_path: Path) -> None:
    godot = find_godot()
    authority_sha = _resolve_canonical_main()
    if godot is None or authority_sha is None:
        pytest.skip("Godot or read-only canonical Sekiph82/Scrubbots origin/main was unavailable before the integration began")

    source = tmp_path / "scrubbots-source"
    clone = subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", "main", _GAME_REMOTE, str(source)],
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert clone.returncode == 0, f"canonical game clone failed after capability was confirmed: {clone.stdout}\n{clone.stderr}"
    cloned_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=source, capture_output=True, text=True, check=True
    ).stdout.strip()
    assert cloned_sha == authority_sha, f"canonical origin/main drifted during test: ls-remote={authority_sha}, clone={cloned_sha}"

    archive = tmp_path / "scrubbots-origin-main.tar"
    with archive.open("wb") as stream:
        result = subprocess.run(
            ["git", "archive", "--format=tar", cloned_sha],
            cwd=source,
            stdout=stream,
            stderr=subprocess.PIPE,
            timeout=300,
        )
    assert result.returncode == 0, f"full game archive creation failed: {result.stderr.decode(errors='replace')}"
    project = tmp_path / "scrubbots-isolated"
    project.mkdir()
    with tarfile.open(archive, mode="r:") as bundle:
        bundle.extractall(project, filter="data")
    assert (project / "project.godot").is_file()

    # Select a real current production-catalog row with a canonical supply plan.
    # The entire current-game archive remains untouched while the default
    # verifier exercises the row's authentic level, plan, and metadata files.
    catalog_path = project / "data/levels/catalog/production_catalog_v1.json"
    catalog_bytes = catalog_path.read_bytes()
    catalog = json.loads(catalog_bytes)
    selected = next(
        entry for entry in catalog["entries"]
        if entry.get("supply_plan_path")
        and all((project / entry[key].removeprefix("res://")).is_file()
                for key in ("level_path", "metadata_path", "supply_plan_path"))
    )
    row = {"n": int(selected["order"]), "chosen_id": str(selected["id"])}
    protected_paths = [catalog_path] + [project / selected[key].removeprefix("res://")
                                       for key in ("level_path", "metadata_path", "supply_plan_path")]
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected_paths}

    # No injected verifier, synthesized level, or stubbed game project: this
    # exercises the production default against one non-empty canonical row.
    verification = _verify_game(project, [row], [row["n"]])
    assert verification["state"] == "PASS"
    assert "FACTORY_ROUTE_A_VERIFY_PASS" in verification["output"]
    assert row["chosen_id"] in selected["id"]
    assert all(check in verification["summary"] for check in (
        "LevelCatalog", "LevelLoader", "SupplyPlanLoader", "solver/replay", "Difficulty V1 parity"
    ))
    assert catalog_path.read_bytes() == catalog_bytes
    assert {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected_paths} == before
    assert not (project / "tests/factory_route_a_verify.gd").exists()

    # The same real verifier must fail closed on an unknown plan identity and
    # still remove its temporary Godot runner.
    invalid_order = max(int(entry["order"]) for entry in catalog["entries"]) + 1
    with pytest.raises(RouteAError, match="current-game verification failed"):
        _verify_game(project, [{"n": invalid_order, "chosen_id": "route-a-missing-level"}], [invalid_order])
    assert not (project / "tests/factory_route_a_verify.gd").exists()
