"""Primary ZIP-derived supply/solve/difficulty route.

Python screening is advisory ranking only.  A result becomes READY only after
the current canonical ScrubBots checkout proves solve + replay and returns the
official Difficulty V1 measurement for a full-canvas level.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from .game_rules import GameRules, find_godot
from .contracts import DEFAULT_COLUMN_COUNT, validate_column_count
from .supply_exporter import SupplyExporter
from .supply_optimizer import NoValidSupply, SupplyOptimizer


PIPELINE_SCHEMA = "scrubbots-primary-supply-pipeline/v1"
ROUTE_ID = "ZIP_PRIMARY_SUPPLY_SOLVER_DIFFICULTY"


def _unavailable(reason: str, *, image: Path, level_id: str, column_count: int = DEFAULT_COLUMN_COUNT) -> dict[str, Any]:
    return {
        "schema": PIPELINE_SCHEMA,
        "route": ROUTE_ID,
        "state": "UNAVAILABLE",
        "disposition": "UNAVAILABLE",
        "level_id": level_id,
        "image_path": str(image),
        "column_count": column_count,
        "visible_preview_depth": 3,
        "reason": reason[:512],
        "screening": {"role": "RANKING_ONLY", "acceptance_authority": "NOT AVAILABLE"},
    }


def run_primary_supply_pipeline(
    image: str | Path,
    *,
    output: str | Path,
    level_id: str = "pixelart_level",
    seed: int = 0,
    candidates: int = 300,
    column_count: int = DEFAULT_COLUMN_COUNT,
    verify_top: int = 1,
    screen_budget: int = 3000,
    metric_top: int = 12,
    viability_budget: int = 3000,
    real_max_visited: int | None = None,
    level_number: int = 1,
    progress: Callable[[str], None] | None = None,
    game_project: str | Path | None = None,
    rules: GameRules | None = None,
    solver: Any | None = None,
) -> dict[str, Any]:
    image_path = Path(image).expanduser().resolve()
    output_path = Path(output).expanduser().resolve()
    try:
        selected_columns = validate_column_count(column_count)
    except ValueError as exc:
        return _unavailable(str(exc), image=image_path, level_id=level_id)
    if not image_path.is_file():
        return _unavailable("local image input does not exist", image=image_path, level_id=level_id, column_count=selected_columns)
    try:
        rules = rules or GameRules(game_project, column_count=selected_columns)
    except FileNotFoundError as exc:
        return _unavailable(f"canonical ScrubBots project unavailable: {exc}", image=image_path, level_id=level_id, column_count=selected_columns)
    if getattr(rules, "column_count", selected_columns) != selected_columns:
        return _unavailable("rules column_count does not match the explicit product selection", image=image_path, level_id=level_id, column_count=selected_columns)
    if solver is None and find_godot() is None:
        return _unavailable("Godot executable unavailable; live game solve/replay verification is pending", image=image_path, level_id=level_id, column_count=selected_columns)
    if solver is None and not getattr(rules, "live_column_verification_available", True):
        return _unavailable("live game 4/5-column verification is pending the separate game compatibility task", image=image_path, level_id=level_id, column_count=selected_columns)

    try:
        result = SupplyOptimizer(rules, solver=solver).run(
            image_path,
            seed=seed,
            candidates=candidates,
            level_id=level_id,
            verify_top=verify_top,
            screen_budget=screen_budget,
            metric_top=metric_top,
            viability_budget=viability_budget,
            real_max_visited=real_max_visited,
            level_number=level_number,
            progress=progress,
        )
        files = SupplyExporter(rules).export(result, output_path, level_id)
        if files.get("level") and files.get("supply_plan"):
            from .scrubpack_identity import derive_solver_supply_identity

            identity = derive_solver_supply_identity(
                Path(files["level"]).read_bytes(),
                Path(files["supply_plan"]).read_bytes(),
                result,
                rules.authority,
            )
            result["solver_supply_identity"] = identity
            Path(files["result"]).write_text(
                json.dumps(
                    {key: value for key, value in result.items() if not key.startswith("_")},
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
    except (NoValidSupply, OSError, RuntimeError, ValueError) as exc:
        return {
            "schema": PIPELINE_SCHEMA,
            "route": ROUTE_ID,
            "state": "ERROR",
            "disposition": "ERROR",
            "level_id": level_id,
            "image_path": str(image_path),
            "column_count": selected_columns,
            "visible_preview_depth": 3,
            "reason": str(exc)[:512],
            "authority": rules.authority,
            "screening": {"role": "RANKING_ONLY", "acceptance_authority": "ScrubBots game solver"},
        }

    return {
        "schema": PIPELINE_SCHEMA,
        "route": ROUTE_ID,
        "state": "READY",
        "disposition": "READY",
        "level_id": level_id,
        "image_path": str(image_path),
        "column_count": selected_columns,
        "visible_preview_depth": 3,
        "output": str(output_path),
        "files": files,
        "authority": rules.authority,
        "screening": {"role": "RANKING_ONLY", "candidates": result["screening_solvable_candidates"]},
        "acceptance": {
            "solver": "ScrubBots SolvabilitySolver",
            "replay": result["solution_final"],
            "difficulty": result["difficulty_basis"],
            "solver_status": result["solver_status"],
        },
        "solver_supply_identity": result.get("solver_supply_identity"),
        "difficulty": {
            "class": result["difficulty"],
            "score": result["difficulty_score"],
            "basis": result["difficulty_basis"],
        },
        "supply": {
            "rows": result["supply_rows"],
            "columns": result["supply_columns"],
            "total_batches": result["total_batches"],
            "batch_count_policy": "positive per-plan metadata bound; no global cap",
        },
        "result": {key: value for key, value in result.items() if not key.startswith("_")},
    }


__all__ = ["PIPELINE_SCHEMA", "ROUTE_ID", "run_primary_supply_pipeline"]
