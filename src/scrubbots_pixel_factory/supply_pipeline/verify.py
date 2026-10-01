"""Verify an exported level + supply plan through the canonical game bridge."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .game_rules import GameRules, find_godot
from .contracts import validate_column_count
from .scrubbots_solver import ScrubBotsSolver
from .solution_verifier import SolutionVerifier


def _hex(value: str) -> str:
    text_value = str(value).upper()
    if len(text_value) == 7:
        text_value += "FF"
    return text_value


def verify_exported_supply(level_path: str | Path, plan_path: str | Path, game_project: str | Path | None = None) -> dict[str, Any]:
    level_file = Path(level_path).expanduser().resolve()
    plan_file = Path(plan_path).expanduser().resolve()
    try:
        level = json.loads(level_file.read_text(encoding="utf-8"))
        plan = json.loads(plan_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"state": "ERROR", "disposition": "ERROR", "reason": f"export is unreadable: {exc}"}
    if not isinstance(level, dict) or not isinstance(plan, dict):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "level and plan must be JSON objects"}
    required = {"schema", "version", "levelId", "columnCount", "visiblePreviewDepth", "maxRobotsPerBatch", "columns"}
    if plan.get("schema") != "scrubbots.level_supply_plan.v1" or not required.issubset(plan):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "supply plan schema or fields are invalid"}
    bound = plan.get("maxRobotsPerBatch")
    if type(bound) is not int or bound < 1:
        return {"state": "ERROR", "disposition": "ERROR", "reason": "maxRobotsPerBatch must be a positive integer per-plan bound"}
    try:
        selected_columns = validate_column_count(plan.get("columnCount"))
        if plan.get("visiblePreviewDepth") != 3:
            return {"state": "ERROR", "disposition": "ERROR", "reason": "visiblePreviewDepth must be exactly 3"}
        rules = GameRules(game_project, column_count=selected_columns)
    except FileNotFoundError as exc:
        return {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "reason": str(exc)}
    if find_godot() is None:
        return {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "reason": "Godot executable unavailable"}
    if plan["levelId"] != level.get("id") or plan["columnCount"] != selected_columns or plan["visiblePreviewDepth"] != 3:
        return {"state": "ERROR", "disposition": "ERROR", "reason": "plan and current game dimensions do not match"}
    if not rules.live_column_verification_available:
        return {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "reason": "live game column compatibility is pending the separate game task", "column_count": selected_columns, "authority": rules.authority}
    level_palette = [_hex(value) for value in level.get("palette", [])]
    cid_to_hex = {cid: _hex(color) for cid, color in rules.palette}
    local_by_hex = {value: index for index, value in enumerate(level_palette)}
    columns: list[list[tuple[int, int]]] = []
    try:
        for column in plan["columns"]:
            parsed: list[tuple[int, int]] = []
            for batch in column:
                cid = str(batch["cid"])
                amount = batch["robots"]
                if type(amount) is not int or amount < 1 or amount > bound:
                    raise ValueError("batch amount violates the positive per-plan bound")
                if cid not in cid_to_hex or cid_to_hex[cid] not in local_by_hex:
                    raise ValueError(f"batch color is absent from level palette: {cid}")
                parsed.append((local_by_hex[cid_to_hex[cid]], amount))
            if not parsed:
                raise ValueError("supply columns must be non-empty")
            columns.append(parsed)
    except (KeyError, TypeError, ValueError) as exc:
        return {"state": "ERROR", "disposition": "ERROR", "reason": str(exc)}
    if len(columns) != selected_columns:
        return {"state": "ERROR", "disposition": "ERROR", "reason": "supply column count mismatch"}
    cells = [int(value) for value in level.get("cells", [])]
    counts: dict[int, int] = {}
    for value in cells:
        counts[value] = counts.get(value, 0) + 1
    candidate = {"id": str(level["id"]), "columns": [[{"color": color, "count": amount} for color, amount in column] for column in columns]}
    try:
        response = ScrubBotsSolver(rules).run(level, [candidate], analyze=True)
    except (OSError, RuntimeError, ValueError) as exc:
        return {"state": "ERROR", "disposition": "ERROR", "reason": str(exc), "authority": rules.authority}
    record = response.get("results", [{}])[0]
    verification = SolutionVerifier().verify(counts, sum(counts.values()), columns, record, selected_columns)
    ready = record.get("status") == "SOLVED" and verification["all_ok"]
    return {
        "schema": "scrubbots-primary-supply-verification/v1",
        "state": "READY" if ready else "REJECTED",
        "disposition": "READY" if ready else "REJECTED",
        "authority": rules.authority,
        "solver": record,
        "verification": verification,
        "difficulty_v1": record.get("difficultyV1"),
        "supply_count_policy": "positive per-plan metadata bound; no global cap",
    }


__all__ = ["verify_exported_supply"]
