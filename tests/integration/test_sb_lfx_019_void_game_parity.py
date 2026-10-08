from __future__ import annotations

import os
from pathlib import Path
from io import BytesIO

import numpy as np
from PIL import Image

from scrubbots_pixel_factory import owner_upload, studio_extensions as studio
from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE
from scrubbots_pixel_factory.owner_upload import import_owner_upload
from scrubbots_pixel_factory.supply_pipeline.game_rules import GameRules
from scrubbots_pixel_factory.supply_pipeline.scrubbots_solver import ScrubBotsSolver
from scrubbots_pixel_factory.supply_pipeline.screening import ScreeningSimulator


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

    rgba = np.zeros((32, 32, 4), dtype=np.uint8)
    for y in range(6, 26):
        for x in range(4, 28):
            color_id = "C01" if x < 13 else "C02" if x < 22 else "C03"
            rgba[y, x, :3] = CANONICAL_PALETTE.rgb_for(color_id)
            rgba[y, x, 3] = 255
    buffer = BytesIO()
    Image.fromarray(rgba, "RGBA").save(buffer, format="PNG", optimize=False)
    source_bytes = buffer.getvalue()
    source_path = tmp_path / "transparent-32x32-fixture.png"
    source_path.write_bytes(source_bytes)
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
    assert sum(1 for alpha in decoded.getchannel("A").getdata() if alpha == 0) == 544

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
        assert primary["result"]["playable_pixels"] == 480
        assert primary["result"]["solver_supply_identity"]["artwork_cell_count"] == 480
        assert primary["result"]["solver_supply_identity"]["void_cell_count"] == 544
        assert stored_source.read_bytes() == source_bytes
    assert candidate["background_intent"] == "TRANSPARENT"
