"""One owner-authorized R09 bounded solver campaign for the original 002 PNG."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .game_rules import GameRules
from .pinned_game_source import PINNED_MAIN_SHA, expected_runtime_root, verify_attested_runtime
from .r09_solver_attempts import (
    MAX_NATIVE_TIMEOUT_SECONDS,
    MAX_NATIVE_VISITED,
    build_ranked_candidate_queue,
    load_r08_ranked_plan_refs,
    run_capped_candidate_queue,
)
from .scrubbots_solver import ScrubBotsSolver
from .screening import ScreeningSimulator
from .supply_optimizer import SupplyOptimizer
from .verify import verify_exported_supply


SOURCE_ID = "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
SOURCE_SHA256 = "49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
SOURCE_RECORD_SHA256 = "858d302c10281ab2d70d4a9e22043e4eac216ebc6b6b0d89131b6e5930c232bb"
R08_JOB_NAME = "job-95dff6b4554644bebf0251d6a347201e"
LEVEL_ID = "r09_002_first_real"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_original_002_r09_campaign() -> dict[str, Any]:
    """Reattest R08 inputs, build at most six distinct plans, and run one fixed campaign."""
    from .. import studio_extensions as studio
    from ..contracts.palette import CANONICAL_PALETTE, VOID_CELL_ID
    from .r09_solver_attempts import R09Blocked

    root = studio._repository_root().resolve()
    runtime = expected_runtime_root().resolve()
    manifest = verify_attested_runtime(runtime)
    if manifest.get("source_commit") != PINNED_MAIN_SHA or manifest.get("full_game_checkout_verified") is not False:
        raise R09Blocked("pinned mini-runtime identity is not the accepted R08 source authority")

    source_dir = (root / "Release" / "ScrubBots Factory Studio" / "level_factory" / "output"
                  / "owner-uploads" / SOURCE_ID)
    output_dir = root / "level_factory" / "output" / "r09-capped-solver" / f"{SOURCE_SHA256}-{PINNED_MAIN_SHA}"
    if output_dir.exists():
        raise R09Blocked("fixed R09 campaign output already exists; refusing to repeat the source budget")
    png_path = source_dir / "source.png"
    record_path = source_dir / "source.json"
    if _sha256(png_path) != SOURCE_SHA256 or _sha256(record_path) != SOURCE_RECORD_SHA256:
        raise R09Blocked("original installed 002 source identity changed")
    source = studio.verify_owner_source(SOURCE_ID, source_directory=source_dir)
    if source.get("source_sha256") != SOURCE_SHA256:
        raise R09Blocked("immutable OWNER_UPLOAD record does not match the approved PNG")
    validation = studio.validate_owner_source(
        SOURCE_ID, persist=False, game_project=runtime, source_directory=source_dir
    )
    if validation.get("exact_logical_source") is not True \
            or validation.get("structural", {}).get("disposition") != "PASS" \
            or validation.get("alpha") != {"transparent_count": 288, "semi_alpha_count": 0, "opaque_count": 736}:
        raise R09Blocked("source validation no longer matches the accepted 736-artwork / 288-VOID R08 proof")

    width, height, rgba = studio._validation_pixels(png_path.read_bytes())
    cells: list[str] = []
    for index in range(width * height):
        red, green, blue, alpha = rgba[index * 4:index * 4 + 4]
        if alpha == 0:
            cells.append(VOID_CELL_ID)
        elif alpha == 255:
            cells.append(CANONICAL_PALETTE.id_for_rgb((red, green, blue)))
        else:
            raise R09Blocked("original PNG contains semitransparent pixels")

    rules = GameRules(runtime, column_count=3)
    grid, used = studio._canonical_cells_to_grid(cells, width, height, rules)
    optimizer = SupplyOptimizer(rules)
    r08_job = runtime / ".lf_solver_jobs" / R08_JOB_NAME
    r08_refs = load_r08_ranked_plan_refs(
        r08_job, rules=rules, expected_game_sha=PINNED_MAIN_SHA, expected_level_id="r08_002_first_real"
    )
    ranked = build_ranked_candidate_queue(
        optimizer, grid, used, r08_refs,
        seed=17018, source_sha256=SOURCE_SHA256, game_sha=PINNED_MAIN_SHA,
        target_count=6, screen_budget=1200, viability_budget=600, max_generated_plans=12,
    )
    print("R09_RANKED_QUEUE " + json.dumps([
        {"rank": index, "candidate_id": item["id"], "score": item["score"],
         "plan_sha256": item["plan_sha256"]}
        for index, item in enumerate(ranked, 1)
    ], sort_keys=True), flush=True)

    metadata = optimizer.analyzer.analyze(grid, used)
    level = {
        "id": LEVEL_ID, "width": width, "height": height,
        "palette": [rules.palette[global_index][1].upper() + "FF" for global_index in used],
        "cells": [int(value) for value in grid.ravel()],
        "column_count": 3,
    }
    source_png_reader = lambda: _sha256(png_path)

    def load_check(candidate: dict[str, Any], timeout: float, visited: int) -> dict[str, Any]:
        winner_dir = output_dir / "offline-winner"
        winner_dir.mkdir(parents=True, exist_ok=False)
        candidate_id = str(candidate["id"])
        metrics_scorer = optimizer
        sim = ScreeningSimulator(grid, rules.slot_count)
        from .supply_scorer import SupplyScorer
        scorer = SupplyScorer(sim, rules.slot_count, viability_budget=600)
        gameplay = scorer.metrics(candidate["columns"], candidate["record"]["trace"])
        difficulty, _score, _basis = metrics_scorer.model.final(
            candidate["record"].get("difficultyV1"), metadata["image_complexity_score"], gameplay
        )
        if difficulty is None:
            raise R09Blocked("official Difficulty V1 result cannot form a load-check level")
        exported_level = {
            "version": 2, "id": LEVEL_ID, "name": "R09 002 First Real", "difficulty": difficulty,
            "width": width, "height": height, "palette": level["palette"], "cells": level["cells"],
        }
        columns = []
        all_colors = []
        for column_index, column in enumerate(candidate["columns"]):
            exported_column = []
            for batch_index, (local_color, amount) in enumerate(column):
                cid = rules.palette[used[local_color]][0]
                all_colors.append({"color": cid, "amount": int(amount)})
                exported_column.append({
                    "batchId": f"C0000-K{column_index:02d}-B{batch_index:03d}",
                    "cid": cid, "robots": int(amount),
                })
            columns.append(exported_column)
        exported_plan = {
            "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": LEVEL_ID,
            "ownerInput": "R09 one-source offline solver campaign",
            "ownerInputSha256": hashlib.sha256(json.dumps(all_colors).encode()).hexdigest(),
            "columnCount": 3, "visiblePreviewDepth": 3,
            "maxRobotsPerBatch": max(batch["robots"] for column in columns for batch in column),
            "intendedColumnClicks": [int(action["column"]) for action in candidate["record"]["trace"]],
            "columns": columns,
        }
        level_path, plan_path = winner_dir / "level.json", winner_dir / "supply-plan.json"
        _write(level_path, exported_level)
        _write(plan_path, exported_plan)
        checked = verify_exported_supply(
            level_path, plan_path, runtime, max_visited=visited, timeout_seconds=timeout
        )
        return checked

    def load_check_adapter(candidate: dict[str, Any], timeout: float, visited: int) -> dict[str, Any]:
        candidate["record"] = winning_record[0]
        return load_check(candidate, timeout, visited)

    winning_record: list[dict[str, Any]] = []

    class _RecordingSolver:
        def __init__(self, real_solver):
            self.real_solver = real_solver

        def run(self, *args, **kwargs):
            response = self.real_solver.run(*args, **kwargs)
            records = response.get("results", [])
            if records and records[0].get("status") == "SOLVED":
                winning_record[:] = [records[0]]
            return response

    solver = _RecordingSolver(ScrubBotsSolver(rules))
    result = run_capped_candidate_queue(
        candidates=ranked, solver=solver, level=level, counts=metadata["_local_counts"],
        playable_cells=metadata["playable_pixels"], source_sha256=SOURCE_SHA256,
        game_sha=PINNED_MAIN_SHA, receipt_dir=output_dir, timeout_seconds=MAX_NATIVE_TIMEOUT_SECONDS,
        max_visited=MAX_NATIVE_VISITED, load_check=load_check_adapter,
        source_sha256_reader=source_png_reader,
        progress=lambda line: print(line, flush=True),
    )
    record_after = _sha256(record_path)
    if record_after != SOURCE_RECORD_SHA256:
        result["status"] = "BLOCKED_SOURCE_RECORD_CHANGED"
        result["source_record_unchanged"] = False
        summary_path = output_dir / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["status"] = result["status"]
        summary["source_record_unchanged"] = False
        _write(summary_path, summary)
    else:
        result["source_record_unchanged"] = True
        summary_path = output_dir / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["source_record_unchanged"] = True
        _write(summary_path, summary)
    return result


__all__ = ["run_original_002_r09_campaign"]
