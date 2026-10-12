"""Bounded one-candidate native solver retries for the R05-R09 owner task."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .screening import ScreeningSimulator
from .solution_verifier import SolutionVerifier
from .supply_scorer import SupplyScorer


MAX_PRIMARY_ATTEMPTS = 6
MAX_NATIVE_TIMEOUT_SECONDS = 90.0
MAX_NATIVE_VISITED = 25_000


class R09Blocked(RuntimeError):
    """A precondition or execution-safety fault that must stop the attempt queue."""


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def candidate_plan_sha256(candidate: Mapping[str, Any], source_sha256: str, game_sha: str) -> str:
    """Hash the supply layout and its immutable source/game identities, independent of its label."""
    columns = [
        [[int(color), int(count)] for color, count in column]
        for column in candidate.get("columns", [])
    ]
    return hashlib.sha256(_json_bytes({
        "source_sha256": source_sha256,
        "game_sha": game_sha,
        "column_count": len(columns),
        "columns": columns,
    })).hexdigest()


def load_r08_ranked_plan_refs(
    job_directory: str | Path,
    *,
    rules: Any,
    expected_game_sha: str,
    expected_level_id: str,
) -> list[tuple[str, Path]]:
    """Read and identity-check the four saved R08 plans without modifying that history."""
    job = Path(job_directory).resolve()
    try:
        request = json.loads((job / "req.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise R09Blocked(f"saved R08 request is unreadable: {exc}") from exc
    authority = request.get("game_authority", {})
    level = request.get("level", {})
    candidates = request.get("candidates")
    if authority.get("git_head") != expected_game_sha or level.get("id") != expected_level_id:
        raise R09Blocked("saved R08 request does not match the frozen game/source-level authority")
    if request.get("max_visited") != MAX_NATIVE_VISITED or not isinstance(candidates, list) or len(candidates) != 4:
        raise R09Blocked("saved R08 request is not the expected bounded four-plan history")
    if len({str(candidate.get("id", "")) for candidate in candidates}) != 4:
        raise R09Blocked("saved R08 ranked candidate identities are duplicated")
    cid_by_hex = {str(color).upper()[:7]: str(cid) for cid, color in rules.palette}
    refs: list[tuple[str, Path]] = []
    for candidate in candidates:
        raw_path = Path(str(candidate.get("supply_plan_path", ""))).resolve()
        if raw_path.parent != job or not raw_path.is_file():
            raise R09Blocked("saved R08 candidate plan escaped its retained job or is missing")
        try:
            plan = json.loads(raw_path.read_text(encoding="utf-8"))
            if plan.get("levelId") != expected_level_id or len(plan.get("columns", [])) != rules.column_count:
                raise ValueError("plan level identity or column count mismatch")
            expected_columns = []
            for column in candidate["columns"]:
                expected_column = []
                for batch in column:
                    local = int(batch["color"])
                    color_hex = str(level["palette"][local]).upper()[:7]
                    expected_column.append({"cid": cid_by_hex[color_hex], "robots": int(batch["count"])})
                expected_columns.append(expected_column)
            actual_columns = [
                [{"cid": str(batch["cid"]), "robots": int(batch["robots"])} for batch in column]
                for column in plan["columns"]
            ]
            if actual_columns != expected_columns:
                raise ValueError("retained request candidate and plan bytes disagree")
        except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise R09Blocked(f"saved R08 plan identity failed: {raw_path.name}: {exc}") from exc
        refs.append((str(candidate["id"]), raw_path))
    return refs


def _score_candidate(
    candidate_id: str,
    columns: list[list[tuple[int, int]]],
    sim: ScreeningSimulator,
    scorer: SupplyScorer,
    band: str,
    *,
    screen_budget: int,
) -> dict[str, Any]:
    screened = sim.solve(columns, max_visited=screen_budget)
    if screened.get("status") != "SOLVED":
        raise R09Blocked(f"ranked candidate {candidate_id} did not pass bounded offline screening")
    metrics = scorer.metrics(columns, screened["trace"])
    score, parts = scorer.score(metrics, band)
    return {
        "id": candidate_id,
        "columns": columns,
        "score": score,
        "score_parts": parts,
        "screen": screened,
        "metrics": metrics,
    }


def build_ranked_candidate_queue(
    optimizer: Any,
    grid: Any,
    used: Sequence[int],
    r08_plan_paths: Sequence[Any],
    *,
    seed: int,
    source_sha256: str,
    game_sha: str,
    target_count: int = MAX_PRIMARY_ATTEMPTS,
    screen_budget: int = 1200,
    viability_budget: int = 600,
    max_generated_plans: int = 12,
) -> list[dict[str, Any]]:
    """Reuse and re-rank R08 plans, screening only enough deterministic plans to fill six."""
    if target_count < 1 or target_count > MAX_PRIMARY_ATTEMPTS:
        raise R09Blocked("primary candidate queue target must be between 1 and six")
    if screen_budget < 1 or screen_budget > MAX_NATIVE_VISITED:
        raise R09Blocked("offline screen budget must be within the per-candidate visit ceiling")
    if viability_budget < 1 or viability_budget > MAX_NATIVE_VISITED:
        raise R09Blocked("offline viability budget must be positive and bounded")
    if max_generated_plans < 0 or max_generated_plans > 24:
        raise R09Blocked("offline generation limit must be between zero and 24")

    _grid, _used, metadata, band, mean, total, _rows = optimizer.prepare_grid(grid, list(used))
    sim = ScreeningSimulator(grid, optimizer.rules.slot_count)
    scorer = SupplyScorer(sim, optimizer.rules.slot_count, viability_budget)
    cid_global = {str(cid): index for index, (cid, _hex) in enumerate(optimizer.rules.palette)}
    global_local = {int(global_index): local for local, global_index in enumerate(used)}
    ranked: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(candidate_id: str, columns: list[list[tuple[int, int]]]) -> None:
        candidate = _score_candidate(candidate_id, columns, sim, scorer, band, screen_budget=screen_budget)
        fingerprint = candidate_plan_sha256(candidate, source_sha256, game_sha)
        if fingerprint in seen:
            return
        seen.add(fingerprint)
        candidate["plan_sha256"] = fingerprint
        ranked.append(candidate)

    for saved in r08_plan_paths:
        saved_candidate_id = None
        plan_path = saved
        if isinstance(saved, (tuple, list)) and len(saved) == 2:
            saved_candidate_id, plan_path = str(saved[0]), saved[1]
        path = Path(plan_path).resolve()
        try:
            plan = json.loads(path.read_text(encoding="utf-8"))
            raw_columns = plan["columns"]
            candidate_id = saved_candidate_id or str(plan["levelId"])
            columns = []
            for column in raw_columns:
                local_column = []
                for batch in column:
                    global_index = cid_global[str(batch["cid"])]
                    local_column.append((global_local[global_index], int(batch["robots"])))
                columns.append(local_column)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise R09Blocked(f"saved R08 ranked plan is unreadable or malformed: {path.name}: {exc}") from exc
        if len(columns) != optimizer.column_count:
            raise R09Blocked(f"saved R08 ranked plan has an unexpected column count: {path.name}")
        add(candidate_id, columns)

    generated = 0
    proposal = 0
    while len(ranked) < target_count and generated < max_generated_plans:
        columns, generator = optimizer.candidate(
            metadata, mean, total, f"{seed}:r09-retry:{proposal}", 1.0
        )
        proposal += 1
        for mutation in range(4):
            generated += 1
            candidate_id = f"r09-s{seed}-p{proposal - 1:02d}-m{mutation}"
            try:
                candidate = _score_candidate(
                    candidate_id, columns, sim, scorer, band, screen_budget=screen_budget
                )
            except R09Blocked as exc:
                # An ordinary DEADLOCK/BOUND from the bounded offline screen just
                # rejects that proposal; malformed data is caught above at load.
                if "did not pass bounded offline screening" not in str(exc):
                    raise
                columns = generator.mutate(columns)
                if generated >= max_generated_plans:
                    break
                continue
            fingerprint = candidate_plan_sha256(candidate, source_sha256, game_sha)
            if fingerprint not in seen:
                candidate["plan_sha256"] = fingerprint
                ranked.append(candidate)
                seen.add(fingerprint)
            break

    if not ranked:
        raise R09Blocked("CANDIDATE_POOL_EXHAUSTED: no distinct screened plans are available")
    ranked.sort(key=lambda item: (-float(item["score"]), str(item["id"]), item["plan_sha256"]))
    return ranked[:target_count]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _normalize_status(status: str) -> str:
    value = str(status).upper()
    if value in {"BOUND", "UNKNOWN_BOUND", "TIMEOUT"}:
        return "UNKNOWN_BOUND" if value == "BOUND" else value
    if value in {"SOLVED", "DEADLOCK"}:
        return value
    return "BLOCKED"


def serialize_bridge_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one LF tuple-form plan and serialize the native adapter's dict form."""
    raw_columns = candidate.get("columns")
    if not isinstance(raw_columns, (list, tuple)) or len(raw_columns) != 3:
        raise R09Blocked("candidate must contain exactly three supply columns")
    columns: list[list[dict[str, int]]] = []
    for column in raw_columns:
        if not isinstance(column, (list, tuple)) or not column:
            raise R09Blocked("candidate supply columns must be non-empty ordered batches")
        batches: list[dict[str, int]] = []
        for batch in column:
            if not isinstance(batch, (list, tuple)) or len(batch) != 2:
                raise R09Blocked("candidate supply batch must be a (color, count) pair")
            color, count = batch
            if type(color) is not int or color < 0 or type(count) is not int or count <= 0:
                raise R09Blocked("candidate supply batch color/count must be bounded nonnegative integers")
            batches.append({"color": color, "count": count})
        columns.append(batches)
    return {"id": str(candidate.get("id", "")), "columns": columns}


def _load_check_proves_ready(checked: Mapping[str, Any]) -> bool:
    """Require every native and LF export gate before reporting local pipeline READY."""
    runner = checked.get("solver_runner")
    solver = checked.get("solver")
    replay = solver.get("replay") if isinstance(solver, Mapping) else None
    difficulty = checked.get("difficulty_v1")
    verification = checked.get("verification")
    return bool(
        checked.get("state") == "READY"
        and (checked.get("solver_status") or (solver.get("status") if isinstance(solver, Mapping) else None)) == "SOLVED"
        and checked.get("solver_invocations") == 1
        and isinstance(runner, Mapping)
        and runner.get("invocation_count") == 1
        and runner.get("process_invocation_count") == 1
        and runner.get("native_solve_started") is True
        and runner.get("native_solve_completed") is True
        and isinstance(runner.get("elapsed_seconds"), (int, float))
        and 0 <= float(runner["elapsed_seconds"]) <= MAX_NATIVE_TIMEOUT_SECONDS
        and isinstance(replay, Mapping)
        and replay.get("ok") is True
        and replay.get("solved") is True
        and replay.get("finalActive") == 0
        and isinstance(difficulty, Mapping)
        and difficulty.get("ok") is True
        and isinstance(verification, Mapping)
        and verification.get("all_ok") is True
        and checked.get("levelLoaderPass") is True
        and checked.get("productionValidatorPass") is True
        and checked.get("supplyPlanLoaderPass") is True
    )


def run_capped_candidate_queue(
    *,
    candidates: Sequence[Mapping[str, Any]],
    solver: Any,
    level: Mapping[str, Any],
    counts: Mapping[int, int],
    playable_cells: int,
    source_sha256: str,
    game_sha: str,
    receipt_dir: str | Path,
    timeout_seconds: float = MAX_NATIVE_TIMEOUT_SECONDS,
    max_visited: int = MAX_NATIVE_VISITED,
    load_check: Callable[[Mapping[str, Any], float, int], Mapping[str, Any]] | None = None,
    source_sha256_reader: Callable[[], str] | None = None,
    progress: Callable[[str], None] | None = None,
    campaign_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run unique candidates serially, stop safely, and retain one receipt per call."""
    if not 1 <= len(candidates) <= MAX_PRIMARY_ATTEMPTS:
        raise R09Blocked("primary attempt queue must contain one to six candidates")
    if not 0 < timeout_seconds <= MAX_NATIVE_TIMEOUT_SECONDS:
        raise R09Blocked("each native solver attempt must be capped at 90 seconds")
    if not 0 < max_visited <= MAX_NATIVE_VISITED:
        raise R09Blocked("each candidate must be capped at 25,000 visited states")
    identities = [str(item.get("plan_sha256", "")) for item in candidates]
    if any(len(value) != 64 for value in identities) or len(set(identities)) != len(identities):
        raise R09Blocked("candidate queue requires distinct SHA-256-bound plans")
    if source_sha256_reader is not None and source_sha256_reader() != source_sha256:
        raise R09Blocked("original owner source SHA-256 changed before execution")

    output = Path(receipt_dir).resolve()
    if output.exists():
        raise R09Blocked("attempt campaign receipt directory already exists; refusing to repeat a sequence")
    output.mkdir(parents=True, exist_ok=False)
    if campaign_metadata is not None:
        _write_json(output / "campaign.json", campaign_metadata)
    attempts: list[dict[str, Any]] = []
    winner: dict[str, Any] | None = None
    blocked_reason: str | None = None
    for index, candidate in enumerate(candidates, 1):
        if source_sha256_reader is not None and source_sha256_reader() != source_sha256:
            blocked_reason = "original owner source SHA-256 changed during execution"
            break
        started_at = _utc_now()
        receipt: dict[str, Any] = {
            "schema": "scrubbots.r09-solver-attempt.v1",
            "attempt_index": index,
            "candidate_id": str(candidate.get("id", "")),
            "source_sha256": source_sha256,
            "candidate_plan_sha256": identities[index - 1],
            "game_sha": game_sha,
            "timeout_seconds": float(timeout_seconds),
            "max_visited": int(max_visited),
            "started_at": started_at,
            "status": "BLOCKED",
            "replay_status": "NOT_RUN",
            "difficulty_v1": None,
            "process": None,
        }
        if progress:
            progress(f"R09_ATTEMPT_START index={index} candidate={receipt['candidate_id']} plan_sha256={identities[index - 1]}")
        try:
            bridge_candidate = serialize_bridge_candidate(candidate)
            if bridge_candidate["id"] != receipt["candidate_id"]:
                raise R09Blocked("serialized bridge candidate identity mismatch")
            response = solver.run(
                dict(level), [bridge_candidate],
                stop_after=1, max_visited=max_visited, analyze=True, timeout=timeout_seconds, progress=progress,
            )
            runner = response.get("_runner", {}) if isinstance(response, Mapping) else {}
            receipt["process"] = runner
            if not isinstance(runner, Mapping) or runner.get("invocation_count") != 1 \
                    or runner.get("process_invocation_count") != 1 \
                    or runner.get("native_solve_started") is not True \
                    or runner.get("native_solve_completed") is not True:
                raise R09Blocked("native start/completion telemetry does not prove exactly one completed solve")
            records = response.get("results") if isinstance(response, Mapping) else None
            if not isinstance(records, list) or len(records) != 1:
                raise R09Blocked("single-candidate bridge returned a missing or multi-result response")
            record = records[0]
            if str(record.get("id")) != receipt["candidate_id"]:
                raise R09Blocked("single-candidate bridge response identity mismatch")
            status = _normalize_status(record.get("status", "UNKNOWN"))
            receipt["status"] = status
            receipt["native_status"] = str(record.get("status", "UNKNOWN"))
            receipt["native_result"] = {
                "solver": record.get("solver"),
                "trace_hash": record.get("traceHash"),
                "replay": record.get("replay"),
            }
            if status == "SOLVED":
                replay = record.get("replay", {})
                receipt["replay_status"] = "WIN" if (
                    replay.get("ok") is True and replay.get("solved") is True
                    and int(replay.get("finalActive", -1)) == 0
                ) else "FAIL"
                receipt["difficulty_v1"] = record.get("difficultyV1")
                verification = SolutionVerifier().verify(
                    dict(counts), playable_cells, candidate["columns"], record,
                    int(level.get("column_count", len(candidate["columns"]))),
                )
                receipt["conservation"] = verification
                if receipt["replay_status"] == "WIN" and verification.get("all_ok") is True \
                        and isinstance(receipt["difficulty_v1"], Mapping) \
                        and receipt["difficulty_v1"].get("ok") is True:
                    winner = {"candidate": candidate, "record": record, "verification": verification}
                    receipt["verified_offline_win"] = True
                else:
                    receipt["verified_offline_win"] = False
                    receipt["status"] = "UNKNOWN_BOUND"
                    receipt["reason"] = "SOLVED response lacked fresh WIN replay, Difficulty V1, or conservation proof"
            elif status == "BLOCKED":
                raise R09Blocked(f"unsupported native solver status: {record.get('status')}")
        except R09Blocked as exc:
            blocked_reason = str(exc)
            receipt["status"] = "BLOCKED"
            receipt["reason"] = blocked_reason
        except Exception as exc:  # bridge exception is classified from its attached bounded process telemetry.
            telemetry = getattr(exc, "telemetry", None)
            if isinstance(telemetry, Mapping):
                receipt["process"] = dict(telemetry)
                if telemetry.get("timed_out") is True and telemetry.get("native_solve_started") is True:
                    receipt["status"] = "TIMEOUT"
                    receipt["reason"] = str(exc)[:512]
                else:
                    receipt["status"] = "BLOCKED"
                    receipt["reason"] = str(exc)[:512]
                    blocked_reason = receipt["reason"]
            else:
                receipt["status"] = "BLOCKED"
                receipt["reason"] = str(exc)[:512]
                blocked_reason = receipt["reason"]
        receipt["completed_at"] = _utc_now()
        receipt["elapsed_seconds"] = (receipt.get("process") or {}).get("elapsed_seconds")
        _write_json(output / f"attempt-{index:02d}.json", receipt)
        attempts.append(receipt)
        if progress:
            process = receipt.get("process") or {}
            progress(
                f"R09_ATTEMPT_END index={index} status={receipt['status']} "
                f"elapsed={process.get('elapsed_seconds')} native_started={process.get('native_solve_started')} "
                f"native_completed={process.get('native_solve_completed')}"
            )
        if winner is not None or blocked_reason is not None:
            break

    load_receipt = None
    if winner is not None and load_check is not None:
        load_started = _utc_now()
        try:
            checked = load_check(winner["candidate"], timeout_seconds, max_visited)
            checked_runner = checked.get("solver_runner", {})
            checked_invocations = checked.get("solver_invocations")
            checked_elapsed = checked_runner.get("elapsed_seconds") if isinstance(checked_runner, Mapping) else None
            if checked_invocations != 1 or not isinstance(checked_runner, Mapping) \
                    or checked_runner.get("invocation_count") != 1 \
                    or checked_runner.get("process_invocation_count") != 1 \
                    or checked_runner.get("native_solve_started") is not True \
                    or checked_elapsed is None or float(checked_elapsed) > timeout_seconds:
                raise R09Blocked("load-check telemetry does not prove one capped independent native invocation")
            load_receipt = {
                "schema": "scrubbots.r09-load-check.v1", "started_at": load_started,
                "completed_at": _utc_now(), "timeout_seconds": timeout_seconds,
                "max_visited": max_visited,
                "state": str(checked.get("state", checked.get("disposition", "UNKNOWN"))),
                "solver_invocations": checked_invocations,
                "solver_runner": dict(checked_runner),
                "solver_status": checked.get("solver_status") or (checked.get("solver") or {}).get("status"),
                "replay": (checked.get("solver") or {}).get("replay"),
                "difficulty_v1": checked.get("difficulty_v1"),
                "verification": checked.get("verification"),
                "levelLoaderPass": checked.get("levelLoaderPass"),
                "productionValidatorPass": checked.get("productionValidatorPass"),
                "supplyPlanLoaderPass": checked.get("supplyPlanLoaderPass"),
                "readiness_proven": _load_check_proves_ready(checked),
            }
        except Exception as exc:
            load_receipt = {
                "schema": "scrubbots.r09-load-check.v1", "started_at": load_started,
                "completed_at": _utc_now(), "timeout_seconds": timeout_seconds,
                "max_visited": max_visited, "state": "BLOCKED", "reason": str(exc)[:512],
            }
        _write_json(output / "load-check.json", load_receipt)

    source_unchanged = source_sha256_reader is None or source_sha256_reader() == source_sha256
    if not source_unchanged:
        blocked_reason = "original owner source SHA-256 changed during execution"
    status_counts: dict[str, int] = {}
    for receipt in attempts:
        status_counts[receipt["status"]] = status_counts.get(receipt["status"], 0) + 1
    retries_run = max(0, len(attempts) - 1)
    if blocked_reason:
        final_status = "BLOCKED"
    elif winner is not None and load_receipt and load_receipt.get("readiness_proven") is True:
        final_status = "OFFLINE_ONE_LEVEL_VALIDATED_CP_X002_PENDING"
    elif winner is not None:
        final_status = "OFFLINE_SOLVED_SHIPPING_LOAD_CHECK_NOT_READY"
    elif len(attempts) < MAX_PRIMARY_ATTEMPTS and len(candidates) < MAX_PRIMARY_ATTEMPTS:
        final_status = "UNSOLVED_CANDIDATE_POOL_EXHAUSTED"
    else:
        final_status = "UNSOLVED_RETRY_BUDGET_EXHAUSTED"
    summary = {
        "schema": "scrubbots.r09-solver-attempt-summary.v1",
        "status": final_status,
        "attempts_run": len(attempts), "retries_run": retries_run,
        "native_primary_calls": sum(
            int(bool((receipt.get("process") or {}).get("native_solve_started"))) for receipt in attempts
        ),
        "primary_invocations": sum(
            int(bool((receipt.get("process") or {}).get("native_solve_started"))) for receipt in attempts
        ),
        "native_load_check_calls": int(
            bool(load_receipt and load_receipt.get("solver_invocations") == 1)
        ),
        "optional_load_check_invocations": int(
            bool(load_receipt and load_receipt.get("solver_invocations") == 1)
        ),
        "status_counts": status_counts,
        "proof_of_global_unsolvability": False,
        "source_sha256": source_sha256, "game_sha": game_sha,
        "source_unchanged": source_unchanged,
        "winner_candidate_id": winner["candidate"]["id"] if winner is not None else None,
        "winner_plan_sha256": winner["candidate"]["plan_sha256"] if winner is not None else None,
        "load_check": load_receipt,
        "local_pipeline_ready": bool(winner is not None and load_receipt and load_receipt.get("readiness_proven") is True),
        "release_pool_eligible": False,
        "cpx002_full_game_replay": "PENDING",
        "blocked_reason": blocked_reason,
        "attempt_receipts": [f"attempt-{index:02d}.json" for index in range(1, len(attempts) + 1)],
    }
    _write_json(output / "summary.json", summary)
    return {**summary, "winner": winner}


__all__ = [
    "MAX_PRIMARY_ATTEMPTS", "MAX_NATIVE_TIMEOUT_SECONDS", "MAX_NATIVE_VISITED",
    "R09Blocked", "candidate_plan_sha256", "serialize_bridge_candidate", "_load_check_proves_ready",
    "load_r08_ranked_plan_refs", "build_ranked_candidate_queue",
    "run_capped_candidate_queue",
]
