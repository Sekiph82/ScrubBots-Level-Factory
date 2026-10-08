from __future__ import annotations

import hashlib
import json
import os
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from scrubbots_pixel_factory import owner_upload, studio_extensions as studio
from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE
from scrubbots_pixel_factory.owner_upload import import_owner_upload
from scrubbots_pixel_factory.supply_pipeline.game_rules import GameRules
from scrubbots_pixel_factory.supply_pipeline.scrubbots_solver import ScrubBotsSolver
from scrubbots_pixel_factory.supply_pipeline.screening import ScreeningSimulator
from scrubbots_pixel_factory.supply_pipeline.verify import verify_exported_supply


OWNER_OWL = Path(__file__).parents[1] / "fixtures" / "owner_void" / "017_a_single_brown_owl_centered_simple_clear_32px.png"
OWNER_OWL_SHA256 = "9f3cff525745cd0623997cb0c2d99084e3c2ddb110457042ebdefe58cdcb7214"


def _configure_studio_roots(repository: Path, monkeypatch) -> tuple[Path, Path]:
    uploads = repository / "level_factory" / "output" / "owner-uploads"
    evidence = repository / "level_factory" / "output" / "studio-extensions"
    uploads.mkdir(parents=True)
    evidence.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: uploads)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "owner_upload_root", lambda: uploads)
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence)
    return uploads, evidence


def _topology_fixture_png(name: str) -> bytes:
    rgba = np.zeros((20, 20, 4), dtype=np.uint8)
    for x in range(20):
        color_id = "C01" if x < 7 else "C02" if x < 14 else "C03"
        rgba[:, x, :3] = CANONICAL_PALETTE.rgb_for(color_id)
        rgba[:, x, 3] = 255
    void = np.zeros((20, 20), dtype=bool)
    if name == "ring":
        void[0, :] = void[-1, :] = True
        void[:, 0] = void[:, -1] = True
    elif name == "enclosed-hole":
        void[8:12, 8:12] = True
    elif name == "border-touching":
        void[0:4, 0:3] = True
    elif name == "void-row-column":
        void[10, :] = True
        void[:, 10] = True
    elif name == "corridor":
        void[8:12, 8:12] = True
        void[11:20, 9] = True
    else:
        raise AssertionError(f"unknown topology fixture: {name}")
    rgba[void] = (0, 0, 0, 0)
    buffer = BytesIO()
    Image.fromarray(rgba, "RGBA").save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def test_void_corridor_screening_trace_replays_step_exactly_in_current_game() -> None:
    assert os.environ.get("SCRUBBOTS_PROJECT"), "set SCRUBBOTS_PROJECT to the clean exact-current game authority"
    rules = GameRules(os.environ["SCRUBBOTS_PROJECT"], column_count=3)
    gate = rules.void_capability()
    assert gate["state"] == "OPEN", gate

    grid = np.zeros((20, 20), dtype=np.int16)
    grid[8:12, 8:12] = 1  # enclosed C02 4x4 target block
    grid[12:20, 9] = -1  # the legal one-cell VOID corridor to the outside
    c01_count = int(np.count_nonzero(grid == 0))
    c02_sizes = ((1, 1, 1, 1, 2), (1, 1, 1, 1, 1), (1, 1, 1, 1, 1))
    c01_sizes = (c01_count // 3, c01_count // 3, c01_count - 2 * (c01_count // 3))
    columns: list[list[tuple[int, int]]] = []
    for column_index in range(3):
        batches = [(1, amount) for amount in c02_sizes[column_index]]
        left = c01_sizes[column_index]
        while left:
            amount = min(left, 40)
            batches.append((0, amount))
            left -= amount
        columns.append(batches)

    level = {
        "id": "void-corridor-parity",
        "width": 20,
        "height": 20,
        "palette": [rules.palette[0][1] + "FF", rules.palette[1][1] + "FF"],
        "cells": [int(value) for value in grid.ravel()],
    }
    candidate = {
        "id": "void-corridor-parity",
        "columns": [[{"color": color, "count": count} for color, count in column] for column in columns],
    }
    response = ScrubBotsSolver(rules).run(level, [candidate], analyze=False)
    record = response["results"][0]
    assert record["status"] == "SOLVED"
    game_trace = record["trace"]
    screened_solved, screened_steps = ScreeningSimulator(grid, rules.slot_count).replay(columns, game_trace)
    assert screened_solved is True
    assert len(screened_steps) == len(game_trace)
    assert all("diverged" not in step for step in screened_steps)
    assert screened_steps[-1]["active_after"] == 0


@pytest.mark.parametrize(
    "fixture_name",
    ("ring", "enclosed-hole", "border-touching", "void-row-column", "corridor"),
)
def test_void_topology_fixtures_pass_the_current_game_pipeline(
    fixture_name: str, tmp_path: Path, monkeypatch,
) -> None:
    assert os.environ.get("SCRUBBOTS_PROJECT"), "set SCRUBBOTS_PROJECT to the clean exact-current game authority"
    repository = tmp_path / "factory"
    uploads, _evidence = _configure_studio_roots(repository, monkeypatch)
    source_path = tmp_path / f"{fixture_name}.png"
    source_bytes = _topology_fixture_png(fixture_name)
    source_path.write_bytes(source_bytes)
    imported = import_owner_upload(source_path)
    source_id = str(imported["source_id"])
    stored_source = uploads / source_id / "source.png"
    assert stored_source.read_bytes() == source_bytes
    validation = studio.validate_owner_source(source_id, persist=False, game_project=os.environ["SCRUBBOTS_PROJECT"])
    assert validation["exact_logical_source"] is True, validation
    assert validation["alpha"]["semi_alpha_count"] == 0
    assert validation["palette"]["used_color_count"] == 3
    assert validation["artwork"]["cell_count"] >= 200
    assert validation["artwork"]["minimum_rule_pass"] is True

    run = studio.run_pipeline(
        source_id=source_id,
        request={
            "game_project": os.environ["SCRUBBOTS_PROJECT"],
            "seed": 19019,
            "candidates": 40,
            "verify_top": 1,
            "screen_budget": 3000,
            "metric_top": 4,
            "viability_budget": 3000,
            "column_count": 3,
            "level_id": f"void-fixture-{fixture_name}",
            "output_dir": str(tmp_path / "canonical-supply"),
        },
    )
    assert run["disposition"] == "READY", run
    primary = run["primary"]
    assert primary["state"] == "READY"
    assert primary["acceptance"]["solver_status"] == "SOLVED"
    assert primary["acceptance"]["replay"] == "WIN"
    assert primary["difficulty"]["basis"].startswith("ScrubBots Difficulty V1")
    load_check = primary["load_check"]
    assert load_check["state"] == "READY", load_check
    assert load_check["levelLoaderPass"] is True
    assert load_check["productionValidatorPass"] is True
    assert load_check["supplyPlanLoaderPass"] is True
    assert load_check["solver"]["status"] == "SOLVED"
    assert load_check["solver"]["replay"]["solved"] is True
    assert load_check["difficulty_v1"]["ok"] is True

    level_bytes = Path(primary["files"]["level"]).read_bytes()
    plan_bytes = Path(primary["files"]["supply_plan"]).read_bytes()
    level = json.loads(level_bytes)
    plan = json.loads(plan_bytes)
    source_alpha = np.array(Image.open(source_path).convert("RGBA"))[:, :, 3]
    void_count = int(np.count_nonzero(source_alpha == 0))
    artwork_count = 400 - void_count
    assert level["version"] == 2
    assert level["cells"].count(-1) == void_count
    assert len(level["cells"]) - void_count == artwork_count
    assert plan["columnCount"] == 3
    assert primary["result"]["level_metadata"] == {"artworkCellCount": artwork_count, "voidCellCount": void_count}
    identity = primary["solver_supply_identity"]
    assert identity["level_data_sha256"] == hashlib.sha256(level_bytes).hexdigest()
    assert identity["supply_plan_sha256"] == hashlib.sha256(plan_bytes).hexdigest()
    assert identity["artwork_cell_count"] == artwork_count
    assert identity["void_cell_count"] == void_count
    assert stored_source.read_bytes() == source_bytes


def test_owner_upload_transparent_fixture_reaches_ready_with_three_four_five_columns(
    tmp_path: Path, monkeypatch,
) -> None:
    assert os.environ.get("SCRUBBOTS_PROJECT"), "set SCRUBBOTS_PROJECT to the clean exact-current game authority"
    repository = tmp_path / "factory"
    uploads = repository / "level_factory" / "output" / "owner-uploads"
    evidence = repository / "level_factory" / "output" / "studio-extensions"
    uploads.mkdir(parents=True)
    evidence.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: uploads)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "owner_upload_root", lambda: uploads)
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence)

    source_path = OWNER_OWL
    source_bytes = source_path.read_bytes()
    assert hashlib.sha256(source_bytes).hexdigest() == OWNER_OWL_SHA256
    source_image = Image.open(source_path).convert("RGBA")
    source_pixels = list(source_image.get_flattened_data())
    assert source_image.size == (32, 32)
    assert sum(pixel[3] == 0 for pixel in source_pixels) == 354
    assert sum(pixel[3] == 255 for pixel in source_pixels) == 670
    assert sum(0 < pixel[3] < 255 for pixel in source_pixels) == 0
    assert len({pixel[:3] for pixel in source_pixels if pixel[3] == 255}) == 7
    imported = import_owner_upload(source_path)
    source_id = str(imported["source_id"])
    stored_source = uploads / source_id / "source.png"
    assert stored_source.read_bytes() == source_bytes

    request_base = {
        "game_project": os.environ["SCRUBBOTS_PROJECT"],
        "seed": 19,
        "candidates": 50,
        "verify_top": 1,
        "screen_budget": 3000,
        "metric_top": 8,
        "viability_budget": 3000,
    }
    initial = studio.run_pipeline(
        source_id=source_id,
        request={**request_base, "column_count": 3, "level_id": "void-32x32-c3"},
    )
    assert initial["disposition"] == "READY", initial
    candidate_id = str(initial["candidate_id"])
    candidate = next(item for item in studio.list_candidates() if item["candidate_id"] == candidate_id)
    decoded = Image.open(stored_source).convert("RGBA")
    assert sum(1 for alpha in decoded.getchannel("A").get_flattened_data() if alpha == 0) == 354

    for column_count in (3, 4, 5):
        run = initial if column_count == 3 else studio.run_pipeline(
            candidate_id=candidate_id,
            request={**request_base, "column_count": column_count, "level_id": f"void-32x32-c{column_count}"},
        )
        assert run["disposition"] == "READY", run
        primary = run["primary"]
        assert primary["state"] == "READY"
        assert primary["acceptance"]["solver_status"] == "SOLVED"
        assert primary["acceptance"]["replay"] == "WIN"
        assert primary["difficulty"]["basis"].startswith("ScrubBots Difficulty V1")
        assert primary["load_check"]["state"] == "READY"
        assert primary["load_check"]["levelLoaderPass"] is True
        assert primary["load_check"]["productionValidatorPass"] is True
        assert primary["load_check"]["supplyPlanLoaderPass"] is True
        assert primary["column_count"] == column_count
        assert primary["load_check"]["artworkCellCount"] == 670
        assert primary["load_check"]["voidCellCount"] == 354
        assert primary["result"]["playable_pixels"] == 670
        assert primary["result"]["solver_supply_identity"]["artwork_cell_count"] == 670
        assert primary["result"]["solver_supply_identity"]["void_cell_count"] == 354
        assert primary["result"]["level_metadata"] == {"artworkCellCount": 670, "voidCellCount": 354}
        level_bytes = Path(primary["files"]["level"]).read_bytes()
        plan_bytes = Path(primary["files"]["supply_plan"]).read_bytes()
        level = json.loads(level_bytes)
        plan = json.loads(plan_bytes)
        assert level["version"] == 2
        assert level["cells"].count(-1) == 354
        assert len(level["cells"]) - level["cells"].count(-1) == 670
        assert plan["columnCount"] == column_count
        assert primary["solver_supply_identity"]["level_data_sha256"] == hashlib.sha256(level_bytes).hexdigest()
        assert primary["solver_supply_identity"]["supply_plan_sha256"] == hashlib.sha256(plan_bytes).hexdigest()
        exported_check = verify_exported_supply(primary["files"]["level"], primary["files"]["supply_plan"], os.environ["SCRUBBOTS_PROJECT"])
        assert exported_check["state"] == "READY", exported_check
        assert exported_check["levelLoaderPass"] is True
        assert exported_check["productionValidatorPass"] is True
        assert exported_check["supplyPlanLoaderPass"] is True
        assert exported_check["solver"]["status"] == "SOLVED"
        assert exported_check["solver"]["replay"]["solved"] is True
        assert exported_check["difficulty_v1"]["ok"] is True
        assert stored_source.read_bytes() == source_bytes
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == OWNER_OWL_SHA256
    assert candidate["background_intent"] == "TRANSPARENT"
