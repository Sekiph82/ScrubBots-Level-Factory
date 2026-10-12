from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from scrubbots_pixel_factory.supply_pipeline import r09_solver_attempts as r09
from scrubbots_pixel_factory.supply_pipeline.scrubbots_solver import ScrubBotsSolver, SolverBridgeError


SOURCE_SHA = "1" * 64
GAME_SHA = "2" * 40


def _candidate(name: str, columns=None) -> dict[str, Any]:
    layouts = [
        [[(0, 1), (0, 1)], [(0, 1), (1, 1)], [(1, 1), (1, 1)]],
        [[(0, 1), (1, 1)], [(0, 1), (0, 1)], [(1, 1), (1, 1)]],
        [[(1, 1), (1, 1)], [(0, 1), (0, 1)], [(0, 1), (1, 1)]],
        [[(1, 1), (1, 1)], [(0, 1), (1, 1)], [(0, 1), (0, 1)]],
        [[(0, 1), (1, 1)], [(1, 1), (1, 1)], [(0, 1), (0, 1)]],
        [[(0, 1), (0, 1)], [(1, 1), (1, 1)], [(0, 1), (1, 1)]],
    ]
    suffix = name.rsplit("-", 1)[-1]
    named_indexes = {"timeout": 0, "bound": 1, "deadlock": 2, "first": 0, "second": 1}
    index = int(suffix) % len(layouts) if suffix.isdigit() else named_indexes.get(name, 0)
    columns = columns or layouts[index]
    candidate = {"id": name, "columns": columns}
    candidate["plan_sha256"] = r09.candidate_plan_sha256(candidate, SOURCE_SHA, GAME_SHA)
    return candidate


def _response(candidate_id: str, status: str) -> dict[str, Any]:
    trace = [{"column": column, "color": color, "count": count}
             for column in range(3) for color, count in _candidate(candidate_id)["columns"][column]]
    record = {"id": candidate_id, "status": status, "trace": trace, "replay": {"ok": True, "solved": True, "finalActive": 0},
              "difficultyV1": {"ok": True}}
    return {
        "results": [record],
        "_runner": {"invocation_count": 1, "process_invocation_count": 1,
                    "native_solve_started": True, "native_solve_completed": True,
                    "native_solve_status": status, "elapsed_seconds": 0.25},
    }


class _SequencedSolver:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def run(self, level, candidates, **kwargs):
        self.calls.append((level, candidates, kwargs))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return _response(candidates[0]["id"], outcome)


def _timeout_error(*, native_started=True):
    telemetry = {"invocation_count": int(native_started), "process_invocation_count": 1,
                 "native_solve_started": native_started, "native_solve_completed": False,
                 "timed_out": True, "elapsed_seconds": 90.0, "process_exit_code": 1}
    return SolverBridgeError("bounded solver timeout", telemetry)


def _run(tmp_path: Path, solver, candidates, **kwargs):
    return r09.run_capped_candidate_queue(
        candidates=candidates, solver=solver,
        level={"id": "source-level", "column_count": 3}, counts={0: 3, 1: 3}, playable_cells=6,
        source_sha256=SOURCE_SHA, game_sha=GAME_SHA,
        receipt_dir=tmp_path / "campaign", timeout_seconds=90, max_visited=25_000,
        **kwargs,
    )


def test_pinned_solver_rejects_multiple_candidates_before_process_creation(tmp_path, monkeypatch):
    rules = type("Rules", (), {"project": tmp_path, "attestation": {"source_commit": GAME_SHA},
                               "palette": [("C04", "#000000")], "preview_depth": 3,
                               "column_count": 3, "authority": {}})()
    solver = ScrubBotsSolver(rules, godot="not-launched")
    launched = []
    monkeypatch.setattr("scrubbots_pixel_factory.supply_pipeline.scrubbots_solver.subprocess.Popen",
                        lambda *args, **kwargs: launched.append(True))
    with pytest.raises(ValueError, match="exactly one candidate"):
        solver.run({"id": "x"}, [_candidate("a"), _candidate("b")], max_visited=25_000, timeout=90)
    assert launched == []
    assert not (tmp_path / ".lf_solver_jobs").exists()


def test_candidate_fingerprint_binds_source_game_and_layout():
    candidate = _candidate("first")
    same_layout_other_name = _candidate("renamed")
    assert candidate["plan_sha256"] == same_layout_other_name["plan_sha256"]
    assert r09.candidate_plan_sha256(candidate, "3" * 64, GAME_SHA) != candidate["plan_sha256"]
    assert r09.candidate_plan_sha256(candidate, SOURCE_SHA, "4" * 40) != candidate["plan_sha256"]


def test_six_unique_candidates_run_serially_one_per_bridge_request(tmp_path):
    candidates = [_candidate(f"candidate-{index}") for index in range(6)]
    solver = _SequencedSolver(["BOUND"] * 6)
    result = _run(tmp_path, solver, candidates)
    assert result["status"] == "UNSOLVED_RETRY_BUDGET_EXHAUSTED"
    assert result["attempts_run"] == 6 and result["retries_run"] == 5
    assert result["primary_invocations"] == 6
    assert result["proof_of_global_unsolvability"] is False
    assert result["status_counts"] == {"UNKNOWN_BOUND": 6}
    assert len(solver.calls) == 6
    assert all(len(call[1]) == 1 and call[2]["stop_after"] == 1 for call in solver.calls)
    assert all(
        isinstance(batch, dict) and set(batch) == {"color", "count"}
        for call in solver.calls for column in call[1][0]["columns"] for batch in column
    )
    assert all(call[2]["timeout"] == 90 and call[2]["max_visited"] == 25_000 for call in solver.calls)
    assert len(list((tmp_path / "campaign").glob("attempt-*.json"))) == 6


def test_duplicate_plan_is_rejected_before_any_attempt(tmp_path):
    candidate = _candidate("duplicate")
    solver = _SequencedSolver(["BOUND"])
    with pytest.raises(r09.R09Blocked, match="distinct SHA-256"):
        _run(tmp_path, solver, [candidate, dict(candidate)])
    assert solver.calls == []


def test_timeout_unknown_bound_and_deadlock_remain_distinct(tmp_path):
    candidates = [_candidate("timeout"), _candidate("bound"), _candidate("deadlock")]
    solver = _SequencedSolver([_timeout_error(), "BOUND", "DEADLOCK"])
    result = _run(tmp_path, solver, candidates)
    assert [row["status"] for row in [
        json.loads((tmp_path / "campaign" / f"attempt-{index:02d}.json").read_text())
        for index in range(1, 4)
    ]] == ["TIMEOUT", "UNKNOWN_BOUND", "DEADLOCK"]
    assert result["status"] == "UNSOLVED_CANDIDATE_POOL_EXHAUSTED"
    assert result["primary_invocations"] == 3


def test_first_fully_verified_win_stops_and_uses_one_capped_load_check(tmp_path, monkeypatch):
    monkeypatch.setattr(r09.SolutionVerifier, "verify", lambda *args, **kwargs: {"all_ok": True, "checks": {}})
    candidates = [_candidate(f"winner-{index}") for index in range(4)]
    solver = _SequencedSolver(["SOLVED", "BOUND", "BOUND", "BOUND"])
    load_calls = []

    def load_check(candidate, timeout, max_visited):
        load_calls.append((candidate["id"], timeout, max_visited))
        return {"state": "READY", "solver_invocations": 1,
                "solver_runner": {"invocation_count": 1, "process_invocation_count": 1,
                                  "native_solve_started": True, "native_solve_completed": True,
                                  "elapsed_seconds": 1.0},
                "solver_status": "SOLVED",
                "solver": {"status": "SOLVED", "replay": {"ok": True, "solved": True, "finalActive": 0}},
                "difficulty_v1": {"ok": True}, "verification": {"all_ok": True},
                "levelLoaderPass": True, "productionValidatorPass": True, "supplyPlanLoaderPass": True}

    result = _run(tmp_path, solver, candidates, load_check=load_check)
    assert result["status"] == "OFFLINE_ONE_LEVEL_VALIDATED_CP_X002_PENDING"
    assert result["attempts_run"] == 1 and result["primary_invocations"] == 1
    assert result["optional_load_check_invocations"] == 1
    assert len(solver.calls) == 1
    assert load_calls == [("winner-0", 90, 25_000)]


def test_primary_win_with_unavailable_shipping_load_check_never_overclaims_ready(tmp_path, monkeypatch):
    monkeypatch.setattr(r09.SolutionVerifier, "verify", lambda *args, **kwargs: {"all_ok": True, "checks": {}})
    candidates = [_candidate("winner-0"), _candidate("unused-1")]
    solver = _SequencedSolver(["SOLVED"])
    load_calls = []

    def load_check(candidate, timeout, max_visited):
        load_calls.append((candidate["id"], timeout, max_visited))
        return {"state": "UNAVAILABLE", "solver_invocations": 0, "solver_runner": None}

    result = _run(tmp_path, solver, candidates, load_check=load_check)
    assert result["status"] == "OFFLINE_SOLVED_SHIPPING_LOAD_CHECK_NOT_READY"
    assert result["attempts_run"] == 1 and result["primary_invocations"] == 1
    assert result["optional_load_check_invocations"] == 0
    assert len(solver.calls) == 1
    assert load_calls == [("winner-0", 90, 25_000)]


def test_fatal_authority_or_pre_native_timeout_stops_without_retry(tmp_path):
    candidates = [_candidate("first"), _candidate("second")]
    solver = _SequencedSolver([_timeout_error(native_started=False), "SOLVED"])
    result = _run(tmp_path, solver, candidates)
    assert result["status"] == "BLOCKED"
    assert result["attempts_run"] == 1
    assert result["primary_invocations"] == 0
    assert len(solver.calls) == 1


def test_original_source_digest_is_checked_before_and_after_execution(tmp_path):
    digest = [SOURCE_SHA]
    solver = _SequencedSolver(["BOUND", "SOLVED"])

    def read_source():
        return digest[0]

    class MutatingSolver(_SequencedSolver):
        def run(self, level, candidates, **kwargs):
            result = super().run(level, candidates, **kwargs)
            digest[0] = "9" * 64
            return result

    solver = MutatingSolver(["BOUND", "SOLVED"])
    result = _run(tmp_path, solver, [_candidate("first"), _candidate("second")],
                  source_sha256_reader=read_source)
    assert result["status"] == "BLOCKED"
    assert result["source_unchanged"] is False
    assert len(solver.calls) == 1


def test_campaign_receipt_directory_cannot_be_reused(tmp_path):
    candidates = [_candidate("one")]
    solver = _SequencedSolver(["BOUND"])
    first = _run(tmp_path, solver, candidates)
    assert first["status"] == "UNSOLVED_CANDIDATE_POOL_EXHAUSTED"
    with pytest.raises(r09.R09Blocked, match="refusing to repeat"):
        _run(tmp_path, solver, candidates)
    assert len(solver.calls) == 1


def test_more_than_six_candidates_are_rejected_before_execution(tmp_path):
    candidates = [_candidate(f"candidate-{index}") for index in range(6)]
    candidates.append(_candidate("seventh", [[(0, 2), (0, 1)], [(0, 1), (1, 1)], [(1, 1), (1, 1)]]))
    solver = _SequencedSolver(["BOUND"] * 7)
    with pytest.raises(r09.R09Blocked, match="one to six"):
        _run(tmp_path, solver, candidates)
    assert solver.calls == []


def test_wrong_saved_game_authority_blocks_r08_plan_reuse(tmp_path):
    request = {"game_authority": {"git_head": "0" * 40}, "level": {"id": "r08_002_first_real"},
               "max_visited": 25_000, "candidates": []}
    (tmp_path / "req.json").write_text(json.dumps(request), encoding="utf-8")
    rules = type("Rules", (), {"palette": [("C04", "#000000")], "column_count": 3})()
    with pytest.raises(r09.R09Blocked, match="frozen game/source-level authority"):
        r09.load_r08_ranked_plan_refs(tmp_path, rules=rules, expected_game_sha=GAME_SHA,
                                      expected_level_id="r08_002_first_real")
