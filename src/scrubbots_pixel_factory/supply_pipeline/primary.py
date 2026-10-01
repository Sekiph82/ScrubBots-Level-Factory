"""Primary ZIP-derived supply/solve/difficulty route.

Python screening is advisory ranking only.  A result becomes READY only after
the current canonical ScrubBots checkout proves solve + replay and returns the
official Difficulty V1 measurement for a full-canvas level.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .game_rules import GameRules, find_godot
from .supply_exporter import SupplyExporter
from .supply_optimizer import NoValidSupply, SupplyOptimizer


PIPELINE_SCHEMA = "scrubbots-primary-supply-pipeline/v1"
ROUTE_ID = "ZIP_PRIMARY_SUPPLY_SOLVER_DIFFICULTY"


def _unavailable(reason: str, *, image: Path, level_id: str) -> dict[str, Any]:
    return {
        "schema": PIPELINE_SCHEMA,
        "route": ROUTE_ID,
        "state": "UNAVAILABLE",
        "disposition": "UNAVAILABLE",
        "level_id": level_id,
        "image_path": str(image),
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
    target: str | None = None,
    verify_top: int = 1,
    screen_budget: int = 3000,
    metric_top: int = 12,
    viability_budget: int = 3000,
    real_max_visited: int | None = None,
    level_number: int = 1,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    image_path = Path(image).expanduser().resolve()
    output_path = Path(output).expanduser().resolve()
    if not image_path.is_file():
        return _unavailable("local image input does not exist", image=image_path, level_id=level_id)
    try:
        rules = GameRules()
    except FileNotFoundError as exc:
        return _unavailable(f"canonical ScrubBots project unavailable: {exc}", image=image_path, level_id=level_id)
    if find_godot() is None:
        return _unavailable("Godot executable unavailable; Python screening cannot accept a supply", image=image_path, level_id=level_id)

    try:
        result = SupplyOptimizer(rules).run(
            image_path,
            seed=seed,
            candidates=candidates,
            target=target,
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
    except (NoValidSupply, OSError, RuntimeError, ValueError) as exc:
        return {
            "schema": PIPELINE_SCHEMA,
            "route": ROUTE_ID,
            "state": "ERROR",
            "disposition": "ERROR",
            "level_id": level_id,
            "image_path": str(image_path),
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
