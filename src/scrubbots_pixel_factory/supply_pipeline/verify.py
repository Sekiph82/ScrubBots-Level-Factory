"""Verify an exported level + supply plan through the canonical game bridge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .game_rules import GameRules, find_godot
from .contracts import validate_column_count
from .scrubbots_solver import ScrubBotsSolver
from .solver_budget import normalize_solver_budget
from .solution_verifier import SolutionVerifier


def _hex(value: str) -> str:
    text_value = str(value).upper()
    if len(text_value) == 7:
        text_value += "FF"
    return text_value


def verify_exported_supply(
    level_path: str | Path,
    plan_path: str | Path,
    game_project: str | Path | None = None,
    *,
    max_visited: int | None = None,
    timeout_seconds: float | None = None,
    solver_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    level_file = Path(level_path).expanduser().resolve()
    plan_file = Path(plan_path).expanduser().resolve()
    try:
        level = json.loads(level_file.read_text(encoding="utf-8"))
        plan = json.loads(plan_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"state": "ERROR", "disposition": "ERROR", "reason": f"export is unreadable: {exc}"}
    if not isinstance(level, dict) or not isinstance(plan, dict):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "level and plan must be JSON objects"}
    cells = level.get("cells")
    if not isinstance(cells, list) or any(type(value) is not int for value in cells):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "LevelData cells must be integer palette IDs or VOID -1"}
    void_count = cells.count(-1)
    if any(value < -1 for value in cells) or (void_count and (level.get("version") != 2 or void_count == len(cells))) or (not void_count and level.get("version") != 1):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "LevelData V1/V2 VOID encoding is not canonical"}
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
    if rules.attestation is not None or max_visited is not None or timeout_seconds is not None:
        try:
            max_visited, timeout_seconds = normalize_solver_budget(max_visited, timeout_seconds)
        except ValueError as exc:
            return {"state": "ERROR", "disposition": "ERROR", "reason": f"invalid solver budget: {exc}"}
    if solver_evidence is None and find_godot() is None:
        return {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "reason": "Godot executable unavailable"}
    if plan["levelId"] != level.get("id") or plan["columnCount"] != selected_columns or plan["visiblePreviewDepth"] != 3:
        return {"state": "ERROR", "disposition": "ERROR", "reason": "plan and current game dimensions do not match"}
    if not rules.live_column_verification_available:
        return {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "reason": "live game column compatibility is pending the separate game task", "column_count": selected_columns, "authority": rules.authority}
    if void_count:
        gate = rules.void_capability()
        if gate.get("state") != "OPEN":
            return {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "reason": gate.get("reason", "current-game VOID capability gate is closed"), "capability": gate, "authority": rules.authority}
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
    if solver_evidence is not None:
        return _verify_export_against_solver_evidence(
            level_file, plan_file, level, plan, rules, columns, selected_columns, solver_evidence
        )
    counts: dict[int, int] = {}
    for value in cells:
        if value >= 0:
            counts[value] = counts.get(value, 0) + 1
    candidate = {"id": str(level["id"]), "columns": [[{"color": color, "count": amount} for color, amount in column] for column in columns]}
    try:
        response = ScrubBotsSolver(rules).run(
            level, [candidate], analyze=True, max_visited=max_visited, timeout=timeout_seconds
        )
    except (OSError, RuntimeError, ValueError) as exc:
        runner = getattr(exc, "telemetry", None)
        return {
            "state": "ERROR", "disposition": "ERROR", "reason": str(exc), "authority": rules.authority,
            "solver_runner": dict(runner) if isinstance(runner, dict) else None,
            "solver_invocations": int(runner.get("invocation_count", 0)) if isinstance(runner, dict) else 0,
            "solver_status": "TIMEOUT" if isinstance(runner, dict) and runner.get("timed_out") else "BLOCKED",
        }
    record = response.get("results", [{}])[0]
    verification = SolutionVerifier().verify(counts, sum(counts.values()), columns, record, selected_columns)
    loader_evidence = {
        "levelLoaderPass": response.get("levelLoaderPass") is True,
        "productionValidatorPass": response.get("productionValidatorPass") is True,
        "supplyPlanLoaderPass": record.get("supplyPlanLoaderPass") is True,
    }
    ready = record.get("status") == "SOLVED" and verification["all_ok"] and all(loader_evidence.values())
    return {
        "schema": "scrubbots-primary-supply-verification/v1",
        "state": "READY" if ready else "REJECTED",
        "disposition": "READY" if ready else "REJECTED",
        "authority": rules.authority,
        "solver": record,
        "solver_runner": response.get("_runner"),
        "solver_invocations": int(response.get("_runner", {}).get("invocation_count", 1)),
        "verification": verification,
        **loader_evidence,
        "difficulty_v1": record.get("difficultyV1"),
        "artworkCellCount": len(cells) - void_count,
        "voidCellCount": void_count,
        "supply_count_policy": "positive per-plan metadata bound; no global cap",
    }


def _verify_export_against_solver_evidence(level_file, plan_file, level, plan, rules, columns, selected_columns, evidence):
    """Bind deterministic exports to the already completed one-process proof."""
    if evidence.get("schema") != "scrubbots-invocation-proof/v1":
        return {"state": "ERROR", "disposition": "ERROR", "reason": "solver invocation proof schema is invalid"}
    proof = evidence.get("solver")
    runner = evidence.get("runner")
    if not isinstance(proof, dict) or not isinstance(runner, dict):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "solver invocation proof is incomplete"}
    if evidence.get("level_id") != level.get("id") or proof.get("status") != "SOLVED":
        return {"state": "ERROR", "disposition": "ERROR", "reason": "solver proof does not bind a solved exported level"}
    if (
        type(runner.get("process_invocation_count")) is not int
        or runner.get("process_invocation_count") != 1
        or type(runner.get("invocation_count")) is not int
        or runner.get("invocation_count") != 1
        or type(runner.get("process_exit_code")) is not int
        or runner.get("process_exit_code") != 0
        or runner.get("native_solve_completed") is not True
        or runner.get("native_solve_status") != "SOLVED"
        or runner.get("timed_out") is True
        or runner.get("cancelled") is True
    ):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "solver proof is not one completed native invocation"}
    if not all(evidence.get(key) is True for key in ("levelLoaderPass", "productionValidatorPass", "supplyPlanLoaderPass")):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "the completed solver invocation did not pass all game loaders"}
    source_sha = evidence.get("source_sha256")
    if source_sha is not None and level.get("source_sha256") != source_sha:
        return {"state": "ERROR", "disposition": "ERROR", "reason": "exported level source SHA does not match solver proof"}
    # The exported level and plan must represent the same logical cells and
    # ordered supply that the game loaders and solver saw in the single run.
    proof_level_sha = runner.get("source_sha256")
    if source_sha is not None and proof_level_sha != source_sha:
        return {"state": "ERROR", "disposition": "ERROR", "reason": "native runner receipt is not bound to the exported source"}
    proof_level = {
        "id": level.get("id"), "width": level.get("width"), "height": level.get("height"),
        "palette": level.get("palette"), "cells": level.get("cells"),
    }
    if source_sha is not None:
        proof_level["source_sha256"] = source_sha
    if hashlib.sha256(json.dumps(proof_level, sort_keys=True, separators=(",", ":")).encode()).hexdigest() != evidence.get("level_sha256"):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "exported logical level does not match the native solver input"}
    cid_by_hex = {_hex(color): str(cid) for cid, color in rules.palette}
    palette = [_hex(color) for color in level.get("palette", [])]
    export_columns = []
    plan_columns = []
    try:
        for column in columns:
            export_column = []
            plan_column = []
            for color_index, amount in column:
                cid = cid_by_hex[palette[color_index]]
                export_column.append({"color": cid, "amount": amount})
                plan_column.append({"cid": cid, "robots": amount})
            export_columns.append(export_column)
            plan_columns.append(plan_column)
    except (IndexError, KeyError):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "exported plan palette cannot be mapped to solver authority"}
    if hashlib.sha256(json.dumps(export_columns).encode()).hexdigest() != plan.get("ownerInputSha256"):
        return {"state": "ERROR", "disposition": "ERROR", "reason": "exported supply columns do not match the solver-bound plan digest"}
    if [[{"cid": row.get("cid"), "robots": row.get("robots")} for row in column] for column in plan.get("columns", [])] != plan_columns:
        return {"state": "ERROR", "disposition": "ERROR", "reason": "exported supply plan differs from the proven ordered columns"}
    verification = SolutionVerifier().verify(
        {index: level["cells"].count(index) for index in range(len(level.get("palette", []))) if level["cells"].count(index)},
        sum(1 for value in level["cells"] if value >= 0), columns, proof, selected_columns,
    )
    if not verification.get("all_ok"):
        return {"state": "REJECTED", "disposition": "REJECTED", "reason": "exported plan failed local conservation/replay proof checks", "verification": verification}
    difficulty = proof.get("difficultyV1")
    if not isinstance(difficulty, dict) or difficulty.get("ok") is not True:
        return {"state": "REJECTED", "disposition": "REJECTED", "reason": "the single native proof lacks official Difficulty V1 evidence"}
    return {
        "schema": "scrubbots-primary-supply-verification/v1",
        "state": "READY", "disposition": "READY", "authority": rules.authority,
        "solver": proof, "solver_runner": runner, "solver_invocations": 1,
        "verification": verification,
        "levelLoaderPass": True, "productionValidatorPass": True, "supplyPlanLoaderPass": True,
        "difficulty_v1": proof.get("difficultyV1"),
        "artworkCellCount": sum(1 for value in level["cells"] if value >= 0),
        "voidCellCount": sum(1 for value in level["cells"] if value == -1),
        "export_sha256": {
            "level": hashlib.sha256(level_file.read_bytes()).hexdigest(),
            "supply_plan": hashlib.sha256(plan_file.read_bytes()).hexdigest(),
        },
        "supply_count_policy": "positive per-plan metadata bound; no global cap",
    }


__all__ = ["verify_exported_supply"]
