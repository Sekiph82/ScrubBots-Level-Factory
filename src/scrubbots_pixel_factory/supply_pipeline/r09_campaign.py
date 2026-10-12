"""One owner-authorized R09 bounded solver campaign for the original 002 PNG."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
import inspect

from .game_rules import GameRules
from .pinned_game_source import PINNED_MAIN_SHA, expected_runtime_root, verify_attested_runtime
from .r09_solver_attempts import (
    MAX_PRIMARY_ATTEMPTS,
    MAX_NATIVE_TIMEOUT_SECONDS,
    MAX_NATIVE_VISITED,
    build_ranked_candidate_queue,
    load_r08_ranked_plan_refs,
    run_capped_candidate_queue,
    serialize_bridge_candidate,
)
from .scrubbots_solver import ScrubBotsSolver
from .screening import ScreeningSimulator
from .supply_optimizer import SupplyOptimizer
from .verify import verify_exported_supply


SOURCE_ID = "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
SOURCE_SHA256 = "49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
SOURCE_RECORD_SHA256 = "858d302c10281ab2d70d4a9e22043e4eac216ebc6b6b0d89131b6e5930c232bb"
R08_JOB_NAME = "job-95dff6b4554644bebf0251d6a347201e"
R09_PRENATIVE_JOB_NAME = "job-578061aa0411437d9668732a833be02f"
LEVEL_ID = "r09_002_first_real"
EXPECTED_R09_RANKED_PLANS = (
    ("r09-s17018-p01-m0", 7.9694, "1fe73587608908aacf39a84f79b8b01e36d0ab8608940081799e10c50ae62ddb"),
    ("s17018-r0-c8-m0", 7.7027, "c48deed323257c1ebfb15bb83b0534c32b685bb39ff19d99cd0b4137b8357443"),
    ("s17018-r0-c2-m0", 7.6560, "78440b8055206e1ed9e4860e76b0cdcd8843ae7429d7ff1867aa0b792729fb26"),
    ("s17018-r0-c0-m0", 7.6272, "04bfc0944b125c1c6dcdff60d66f62041515b84396cea3fabee6c7c57eff9a08"),
    ("s17018-r0-c11-m0", 7.3212, "b4941bc437ff71bb1592295f7dae6ac4de20c09e4313432caf2caf3b5daed02e"),
    ("r09-s17018-p00-m0", 6.8384, "b87e0298a87f0026b924a734fddffacb1ca555bc3758b7d484b379762a036336"),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _historical_r09_predecessor_proof(root: Path) -> dict[str, Any]:
    """Read-only proof that the fixed R09 dispatch spent zero native solve calls."""
    from .r09_solver_attempts import MAX_PRIMARY_ATTEMPTS, R09Blocked

    predecessor = root / "level_factory" / "output" / "r09-capped-solver" / f"{SOURCE_SHA256}-{PINNED_MAIN_SHA}"
    summary_path = predecessor / "summary.json"
    attempt_path = predecessor / "attempt-01.json"
    try:
        summary_bytes = summary_path.read_bytes()
        attempt_bytes = attempt_path.read_bytes()
        summary = json.loads(summary_bytes.decode("utf-8"))
        attempt = json.loads(attempt_bytes.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise R09Blocked(f"R09_QUEUE_IDENTITY_UNVERIFIED: historical predecessor is unreadable: {exc}") from exc
    job = root / "level_factory" / "output" / "current-game-runtime" / PINNED_MAIN_SHA / ".lf_solver_jobs" / R09_PRENATIVE_JOB_NAME
    try:
        job_entries = list(job.iterdir())
    except OSError as exc:
        raise R09Blocked(f"R09_QUEUE_IDENTITY_UNVERIFIED: prior empty native job record is unavailable: {exc}") from exc
    details = _validate_predecessor_records(summary, attempt, job, len(job_entries))
    return {
        **details,
        "predecessor_summary_sha256": hashlib.sha256(summary_bytes).hexdigest(),
        "predecessor_attempt_sha256": hashlib.sha256(attempt_bytes).hexdigest(),
    }


def _validate_predecessor_records(summary: dict[str, Any], attempt: dict[str, Any], job: Path,
                                  job_entry_count: int) -> dict[str, Any]:
    from .r09_solver_attempts import MAX_PRIMARY_ATTEMPTS, R09Blocked

    if not (
        summary.get("status") == "BLOCKED"
        and summary.get("game_sha") == PINNED_MAIN_SHA
        and summary.get("source_sha256") == SOURCE_SHA256
        and summary.get("attempts_run") == 1
        and summary.get("primary_invocations") == 0
        and summary.get("optional_load_check_invocations") == 0
        and attempt.get("attempt_index") == 1
        and attempt.get("candidate_id") == EXPECTED_R09_RANKED_PLANS[0][0]
        and attempt.get("candidate_plan_sha256") == EXPECTED_R09_RANKED_PLANS[0][2]
        and attempt.get("source_sha256") == SOURCE_SHA256
        and attempt.get("game_sha") == PINNED_MAIN_SHA
        and attempt.get("max_visited") == MAX_NATIVE_VISITED
        and attempt.get("timeout_seconds") == MAX_NATIVE_TIMEOUT_SECONDS
        and attempt.get("status") == "BLOCKED"
        and attempt.get("process") is None
        and attempt.get("reason") == "tuple indices must be integers or slices, not str"
    ):
        raise R09Blocked("R09_QUEUE_IDENTITY_UNVERIFIED: predecessor does not prove exactly zero native starts")
    if job_entry_count != 0:
        raise R09Blocked("R09_QUEUE_IDENTITY_UNVERIFIED: prior pre-native job directory is not empty")
    return {
        "logical_attempts_run": summary["attempts_run"],
        "native_primary_calls_consumed": summary["primary_invocations"],
        "native_load_check_calls_consumed": summary["optional_load_check_invocations"],
        "remaining_authorized_primary_calls": MAX_PRIMARY_ATTEMPTS - summary["primary_invocations"],
        "predecessor_job_directory": str(job),
        "predecessor_job_entry_count": job_entry_count,
    }


def _assert_original_queue_identity(ranked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reject any regenerated candidate queue that differs from the published R09 evidence."""
    from .r09_solver_attempts import R09Blocked

    try:
        actual_queue = tuple(
            (str(item.get("id", "")), round(float(item.get("score", float("nan"))), 4),
             str(item.get("plan_sha256", "")))
            for item in ranked
        )
    except (TypeError, ValueError, OverflowError) as exc:
        raise R09Blocked("R09_QUEUE_IDENTITY_UNVERIFIED: ranked queue has an invalid score or identity") from exc
    if actual_queue != EXPECTED_R09_RANKED_PLANS:
        raise R09Blocked("R09_QUEUE_IDENTITY_UNVERIFIED: deterministic queue did not match all six original ranks, scores and plan hashes")
    return ranked


def _assert_continuation_output_available(output_dir: Path) -> None:
    from .r09_solver_attempts import R09Blocked

    if output_dir.exists():
        raise R09Blocked("R09-R01 continuation output already exists; refusing to repeat the sequence")


def _build_r09_r01_campaign_context(root: Path | None = None) -> dict[str, Any]:
    """Build and validate the exact live campaign inputs without creating outputs or a solver."""
    from .. import studio_extensions as studio
    from ..contracts.palette import CANONICAL_PALETTE, VOID_CELL_ID
    from .r09_solver_attempts import R09Blocked

    root = (root or studio._repository_root()).resolve()
    runtime = expected_runtime_root().resolve()
    manifest = verify_attested_runtime(runtime)
    if manifest.get("source_commit") != PINNED_MAIN_SHA or manifest.get("full_game_checkout_verified") is not False:
        raise R09Blocked("pinned mini-runtime identity is not the accepted R08 source authority")

    source_dir = (root / "Release" / "ScrubBots Factory Studio" / "level_factory" / "output"
                  / "owner-uploads" / SOURCE_ID)
    output_dir = root / "level_factory" / "output" / f"r09-r01-continuation-{SOURCE_SHA256}-{PINNED_MAIN_SHA}"
    _assert_continuation_output_available(output_dir)
    predecessor_proof = _historical_r09_predecessor_proof(root)
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
    _assert_original_queue_identity(ranked)
    bridge_candidates = [serialize_bridge_candidate(candidate) for candidate in ranked]
    if len(bridge_candidates) != 6 or [item["id"] for item in bridge_candidates] != [item["id"] for item in ranked]:
        raise R09Blocked("serialized six-candidate native queue does not preserve ranked identities")

    metadata = optimizer.analyzer.analyze(grid, used)
    level = {
        "id": LEVEL_ID, "width": width, "height": height,
        "palette": [rules.palette[global_index][1].upper() + "FF" for global_index in used],
        "cells": [int(value) for value in grid.ravel()],
        "column_count": 3,
    }
    campaign_metadata = {
        "schema": "scrubbots.r09-r01-continuation.v1",
        "source_sha256": SOURCE_SHA256,
        "source_record_sha256": SOURCE_RECORD_SHA256,
        "game_sha": PINNED_MAIN_SHA,
        "predecessor": predecessor_proof,
        "candidate_queue": [
            {"rank": index, "candidate_id": item["id"], "score": round(float(item["score"]), 4),
             "plan_sha256": item["plan_sha256"]}
            for index, item in enumerate(ranked, 1)
        ],
        "native_primary_call_budget": min(MAX_PRIMARY_ATTEMPTS, predecessor_proof["remaining_authorized_primary_calls"]),
    }
    json.dumps(campaign_metadata, sort_keys=True, separators=(",", ":"), allow_nan=False)
    required_args = {"candidates", "solver", "level", "counts", "playable_cells", "source_sha256", "game_sha", "receipt_dir", "timeout_seconds", "max_visited", "load_check", "source_sha256_reader", "progress", "campaign_metadata"}
    if not required_args.issubset(inspect.signature(run_capped_candidate_queue).parameters):
        raise R09Blocked("bounded runner interface no longer accepts the attested campaign argument shape")
    if campaign_metadata["native_primary_call_budget"] != 6 or MAX_NATIVE_TIMEOUT_SECONDS != 90 or MAX_NATIVE_VISITED != 25000:
        raise R09Blocked("authorized native budget differs from the six-call 90s/25,000-visit cap")
    print("R09_RANKED_QUEUE " + json.dumps([
        {"rank": index, "candidate_id": item["id"], "score": item["score"], "plan_sha256": item["plan_sha256"]}
        for index, item in enumerate(ranked, 1)
    ], sort_keys=True), flush=True)
    return {
        "root": root, "runtime": runtime, "manifest": manifest, "source_dir": source_dir,
        "output_dir": output_dir, "predecessor_proof": predecessor_proof,
        "png_path": png_path, "record_path": record_path, "source": source,
        "validation": validation, "width": width, "height": height, "cells": cells,
        "rules": rules, "grid": grid, "used": used, "optimizer": optimizer,
        "ranked": ranked, "bridge_candidates": bridge_candidates,
        "metadata": metadata, "level": level, "campaign_metadata": campaign_metadata,
    }


def preflight_original_002_r09_r01_continuation() -> dict[str, Any]:
    """Read-only report for the same verified inputs used by the live continuation."""
    from .r09_solver_attempts import R09Blocked

    try:
        context = _build_r09_r01_campaign_context()
    except R09Blocked as exc:
        return {"state": "BLOCKED", "disposition": "BLOCKED_PRECONDITION", "reason": str(exc), "native_calls": 0}
    return {
        "state": "PRE_NATIVE_READY", "disposition": "PRE_NATIVE_READY",
        "source_sha256": SOURCE_SHA256, "source_record_sha256": SOURCE_RECORD_SHA256,
        "game_sha": PINNED_MAIN_SHA,
        "candidate_ids": [item["id"] for item in context["ranked"]],
        "candidate_plan_sha256": [item["plan_sha256"] for item in context["ranked"]],
        "native_primary_call_budget": context["campaign_metadata"]["native_primary_call_budget"],
        "timeout_seconds": MAX_NATIVE_TIMEOUT_SECONDS, "max_visited": MAX_NATIVE_VISITED,
        "native_calls": 0, "output_created": False,
    }


def _run_original_002_r09_campaign(*, continuation: bool) -> dict[str, Any]:
    """Shared exact-source route with separate no-reuse R09 and R09-R01 outputs."""
    from .. import studio_extensions as studio
    from ..contracts.palette import CANONICAL_PALETTE, VOID_CELL_ID
    from .r09_solver_attempts import R09Blocked

    if continuation:
        context = _build_r09_r01_campaign_context()
        root, runtime = context["root"], context["runtime"]
        output_dir, predecessor_proof = context["output_dir"], context["predecessor_proof"]
        png_path, record_path = context["png_path"], context["record_path"]
        width, height = context["width"], context["height"]
        rules, grid, used, optimizer = context["rules"], context["grid"], context["used"], context["optimizer"]
        ranked, metadata, level = context["ranked"], context["metadata"], context["level"]
        campaign_metadata = context["campaign_metadata"]
    else:
        root = studio._repository_root().resolve()
        runtime = expected_runtime_root().resolve()
        manifest = verify_attested_runtime(runtime)
        if manifest.get("source_commit") != PINNED_MAIN_SHA or manifest.get("full_game_checkout_verified") is not False:
            raise R09Blocked("pinned mini-runtime identity is not the accepted R08 source authority")
        source_dir = (root / "Release" / "ScrubBots Factory Studio" / "level_factory" / "output" / "owner-uploads" / SOURCE_ID)
        output_dir = root / "level_factory" / "output" / "r09-capped-solver" / f"{SOURCE_SHA256}-{PINNED_MAIN_SHA}"
        if output_dir.exists():
            raise R09Blocked("fixed R09 campaign output already exists; refusing to repeat the source budget")
        predecessor_proof = None
        png_path, record_path = source_dir / "source.png", source_dir / "source.json"
        if _sha256(png_path) != SOURCE_SHA256 or _sha256(record_path) != SOURCE_RECORD_SHA256:
            raise R09Blocked("original installed 002 source identity changed")
        source = studio.verify_owner_source(SOURCE_ID, source_directory=source_dir)
        if source.get("source_sha256") != SOURCE_SHA256:
            raise R09Blocked("immutable OWNER_UPLOAD record does not match the approved PNG")
        validation = studio.validate_owner_source(SOURCE_ID, persist=False, game_project=runtime, source_directory=source_dir)
        if validation.get("exact_logical_source") is not True or validation.get("structural", {}).get("disposition") != "PASS" or validation.get("alpha") != {"transparent_count": 288, "semi_alpha_count": 0, "opaque_count": 736}:
            raise R09Blocked("source validation no longer matches the accepted 736-artwork / 288-VOID R08 proof")
        width, height, rgba = studio._validation_pixels(png_path.read_bytes())
        cells: list[str] = []
        for index in range(width * height):
            red, green, blue, alpha = rgba[index * 4:index * 4 + 4]
            if alpha == 0: cells.append(VOID_CELL_ID)
            elif alpha == 255: cells.append(CANONICAL_PALETTE.id_for_rgb((red, green, blue)))
            else: raise R09Blocked("original PNG contains semitransparent pixels")
        rules = GameRules(runtime, column_count=3)
        grid, used = studio._canonical_cells_to_grid(cells, width, height, rules)
        optimizer = SupplyOptimizer(rules)
        r08_refs = load_r08_ranked_plan_refs(runtime / ".lf_solver_jobs" / R08_JOB_NAME, rules=rules, expected_game_sha=PINNED_MAIN_SHA, expected_level_id="r08_002_first_real")
        ranked = build_ranked_candidate_queue(optimizer, grid, used, r08_refs, seed=17018, source_sha256=SOURCE_SHA256, game_sha=PINNED_MAIN_SHA, target_count=6, screen_budget=1200, viability_budget=600, max_generated_plans=12)
        print("R09_RANKED_QUEUE " + json.dumps([{"rank": index, "candidate_id": item["id"], "score": item["score"], "plan_sha256": item["plan_sha256"]} for index, item in enumerate(ranked, 1)], sort_keys=True), flush=True)
        metadata = optimizer.analyzer.analyze(grid, used)
        level = {"id": LEVEL_ID, "width": width, "height": height, "palette": [rules.palette[global_index][1].upper() + "FF" for global_index in used], "cells": [int(value) for value in grid.ravel()], "column_count": 3}
        campaign_metadata = None
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
        campaign_metadata=campaign_metadata,
    )
    record_after = _sha256(record_path)
    predecessor_after = _historical_r09_predecessor_proof(root) if continuation else None
    if record_after != SOURCE_RECORD_SHA256 or (continuation and predecessor_after != predecessor_proof):
        result["status"] = "BLOCKED_SOURCE_RECORD_CHANGED"
        result["source_record_unchanged"] = False
        summary_path = output_dir / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["status"] = result["status"]
        summary["source_record_unchanged"] = False
        summary["historical_predecessor_unchanged"] = False
        _write(summary_path, summary)
    else:
        result["source_record_unchanged"] = True
        summary_path = output_dir / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["source_record_unchanged"] = True
        if continuation:
            summary["historical_predecessor_unchanged"] = True
        _write(summary_path, summary)
    return result


def run_original_002_r09_campaign() -> dict[str, Any]:
    """Run the original one-use fixed R09 campaign; its output collision guard remains."""
    return _run_original_002_r09_campaign(continuation=False)


def run_original_002_r09_r01_continuation() -> dict[str, Any]:
    """Resume only the six-call R09 authorization after the proved pre-native block."""
    return _run_original_002_r09_campaign(continuation=True)


__all__ = ["run_original_002_r09_campaign", "run_original_002_r09_r01_continuation"]
