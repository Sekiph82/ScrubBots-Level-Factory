"""Owner decision 2026-11-12: a level ships only if the game wins it with slots refilled at once.

Before, the optimizer accepted the first solver-proven plan; when real play then
deadlocked (all five slots WAITING) the gate ran a blind order search that
gave up after 900 s and the PNG was lost. Now each solver-proven, quality-ranked
plan gets a cheap real-play pre-check, the official Difficulty V1 analysis runs
only for the first plan the game wins, and at most MAX_REAL_PLAY_ALTERNATIVES
plans are tried.
"""
from __future__ import annotations

import numpy as np
import pytest

from scrubbots_pixel_factory.supply_pipeline import pinned_game_source
from scrubbots_pixel_factory.supply_pipeline.game_rules import GameRules
from scrubbots_pixel_factory.supply_pipeline.screening import ScreeningSimulator
from scrubbots_pixel_factory.supply_pipeline.scrubbots_solver import SolverBridgeError
from scrubbots_pixel_factory.supply_pipeline.supply_optimizer import (
    MAX_REAL_PLAY_ALTERNATIVES, NoValidSupply, SupplyOptimizer,
)

OFFICIAL = {"ok": True, "challengeScore": 30.0, "vector": [0.1] * 7, "profile": {}, "targetChallenge": 20.0,
            "sessionLoad": 10.0, "B": {}, "S": {}, "U": {}, "path": {}}


def _grid() -> np.ndarray:
    grid = np.zeros((20, 20), dtype=int)
    grid[:, 7:14] = 1
    grid[:, 14:] = 2
    grid[5:9, 2:5] = 2
    return grid


class FakeSolver:
    """Proves each plan with the screening trace; never runs Godot."""

    def __init__(self, grid: np.ndarray, slot_count: int, broken: set[int] = frozenset()) -> None:
        self.sim = ScreeningSimulator(grid, slot_count)
        self.calls: list[tuple[str, str, bool]] = []
        self.broken = broken

    def run(self, level, candidates, **options):
        candidate = candidates[0]
        if "analyze_trace" in candidate:
            self.calls.append((candidate["id"], "ANALYZE", bool(options.get("analyze"))))
            return {"results": [{"id": candidate["id"], "status": "ANALYZED", "difficultyV1": dict(OFFICIAL)}],
                    "_runner": {"invocation_count": 0}}
        self.calls.append((candidate["id"], "SOLVE", bool(options.get("analyze"))))
        if len([call for call in self.calls if call[1] == "SOLVE"]) in self.broken:
            raise SolverBridgeError("bounded Godot solver timed out after 900.0s (TIMEOUT_900)", {"cancelled": False})
        columns = [[(batch["color"], batch["count"]) for batch in column] for column in candidate["columns"]]
        screened = self.sim.solve(columns, max_visited=3000)
        pointer, trace = [0] * len(columns), []
        for action in screened["trace"]:
            color, count = columns[action["column"]][pointer[action["column"]]]
            pointer[action["column"]] += 1
            trace.append({"column": action["column"], "color": color, "count": count,
                          "clears": action["clears"], "active_after": action["active_after"]})
        record = {"id": candidate["id"], "status": "SOLVED", "trace": trace, "solver": {"visited": 1},
                  "replay": {"ok": True, "solved": True, "finalActive": 0, "steps": len(trace), "divergedAt": -1}}
        return {"results": [record], "levelLoaderPass": True, "productionValidatorPass": True,
                "_runner": {"invocation_count": 1}}


def _optimizer(grid, broken=frozenset()) -> tuple[SupplyOptimizer, FakeSolver, list]:
    rules = GameRules(pinned_game_source.expected_runtime_root(), column_count=3)
    optimizer = SupplyOptimizer(rules)
    optimizer.solver = FakeSolver(grid, rules.slot_count, broken)
    return optimizer, optimizer.solver, list(range(3))


def _run(optimizer, grid, used, precheck):
    return optimizer.run_grid(grid, used, seed=3, candidates=60, level_id="alt_test", metric_top=12,
                              real_max_visited=25_000, progress=None, real_timeout_seconds=900,
                              max_native_solver_invocations=1, real_play_precheck=precheck,
                              alternative_budget_seconds=1800)


def test_first_plan_the_game_wins_is_analysed_and_accepted() -> None:
    grid = _grid()
    optimizer, solver, used = _optimizer(grid)
    seen: list[list[int]] = []

    def precheck(level, supply_columns, solution_trace):
        seen.append([step["column"] for step in solution_trace])
        return {"won": len(seen) == 3, "verdict": "WON_CANONICAL" if len(seen) == 3 else "LOST", "stuck_click": 5}

    result = _run(optimizer, grid, used, precheck)

    solves = [call for call in solver.calls if call[1] == "SOLVE"]
    analyses = [call for call in solver.calls if call[1] == "ANALYZE"]
    assert len(solves) == 3 and not any(analyze for _id, _kind, analyze in solves)
    assert analyses == [(solves[2][0], "ANALYZE", True)]
    assert [check["won"] for check in result["real_play_prechecks"]] == [False, False, True]
    assert result["solver_evidence"]["solver"]["id"] == solves[2][0]
    assert result["difficulty_basis"].startswith("ScrubBots Difficulty V1")
    assert [step["column"] for step in result["solution_trace"]] == seen[2]


def test_png_is_rejected_only_after_every_alternative_loses() -> None:
    grid = _grid()
    optimizer, solver, used = _optimizer(grid, broken={2})

    with pytest.raises(NoValidSupply, match="REAL_PLAY_NO_WINNING_PLAN"):
        _run(optimizer, grid, used, lambda *_args: {"won": False, "verdict": "LOST", "stuck_click": 1})

    solves = [call for call in solver.calls if call[1] == "SOLVE"]
    assert 2 < len(solves) <= MAX_REAL_PLAY_ALTERNATIVES  # a solver timeout on plan 2 did not stop the search
    assert not any(call[1] == "ANALYZE" for call in solver.calls)


def test_without_precheck_the_first_plan_is_solved_with_analysis_as_before() -> None:
    grid = _grid()
    optimizer, solver, used = _optimizer(grid)

    class AnalyzingSolver(FakeSolver):
        def run(self, level, candidates, **options):
            response = super().run(level, candidates, **options)
            response["results"][0]["difficultyV1"] = dict(OFFICIAL)
            return response

    optimizer.solver = AnalyzingSolver(grid, optimizer.rules.slot_count)
    result = _run(optimizer, grid, used, None)
    assert [call[1:] for call in optimizer.solver.calls] == [("SOLVE", True)]
    assert result["real_play_prechecks"] == []
