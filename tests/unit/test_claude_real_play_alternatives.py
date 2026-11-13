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

    def __init__(self, grid: np.ndarray, slot_count: int, broken: set[int] = frozenset(), diverge: bool = True) -> None:
        self.sim = ScreeningSimulator(grid, slot_count)
        self.calls: list[tuple[str, str, bool]] = []
        self.broken = broken
        self.diverge = diverge  # default: replay fails, so the native-search path is exercised

    def run(self, level, candidates, **options):
        candidate = candidates[0]
        if "verify_trace" in candidate:
            # Kernel replay of the screening order; every plan here replays cleanly
            # unless the test marks it as diverging.
            self.calls.append((candidate["id"], "VERIFY", bool(options.get("analyze"))))
            if self.diverge:
                return {"results": [{"id": candidate["id"], "status": "TRACE_DIVERGED", "divergedAt": 3}],
                        "_runner": {"invocation_count": 0}}
            response = self._solve(candidate)
            response["results"][0]["solver"] = {"visited": 0, "proof": "KERNEL_REPLAY"}
            response["_runner"] = {"invocation_count": 0, "trace_verify_completed": True, "trace_verify_status": "SOLVED"}
            return response
        if "analyze_trace" in candidate:
            self.calls.append((candidate["id"], "ANALYZE", bool(options.get("analyze"))))
            return {"results": [{"id": candidate["id"], "status": "ANALYZED", "difficultyV1": dict(OFFICIAL)}],
                    "_runner": {"invocation_count": 0}}
        self.calls.append((candidate["id"], "SOLVE", bool(options.get("analyze"))))
        if len([call for call in self.calls if call[1] == "SOLVE"]) in self.broken:
            raise SolverBridgeError("bounded Godot solver timed out after 900.0s (TIMEOUT_900)", {"cancelled": False})
        return self._solve(candidate)

    def _solve(self, candidate):
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


class Clock:
    def __init__(self, start: float) -> None:
        self.now = start

    def time(self) -> float:
        return self.now


def test_png_stops_at_the_twenty_minute_limit(monkeypatch) -> None:
    # Owner decision 2026-11-13: LF-000047 held a worker for 69 minutes; a PNG not
    # solved within 30 minutes in total counts as unsolvable.
    from scrubbots_pixel_factory.supply_pipeline import supply_optimizer
    grid = _grid()
    optimizer, solver, used = _optimizer(grid)
    clock = Clock(1_000_000.0)
    monkeypatch.setattr(supply_optimizer.time, "time", clock.time)
    original_run = solver.run

    def slow_run(level, candidates, **options):
        if "verify_trace" not in candidates[0]:
            clock.now += 400  # every native search takes 400 s
        return original_run(level, candidates, **options)

    solver.run = slow_run
    with pytest.raises(NoValidSupply, match="PNG_TIME_LIMIT"):
        optimizer.run_grid(grid, used, seed=3, candidates=60, level_id="alt_test", metric_top=12,
                           real_max_visited=25_000, progress=None, real_timeout_seconds=900,
                           max_native_solver_invocations=1, wall_deadline=clock.now + supply_optimizer.PNG_SOLVE_TIME_LIMIT_SECONDS,
                           real_play_precheck=lambda *_args: {"won": False, "verdict": "LOST", "stuck_click": 3})
    assert len([call for call in solver.calls if call[1] == "SOLVE"]) == 5  # 0..1600 s; at 2000 s (> 1800) no new plan


def test_running_solver_gets_only_the_time_that_is_left(monkeypatch) -> None:
    from scrubbots_pixel_factory.supply_pipeline import supply_optimizer
    from scrubbots_pixel_factory.supply_pipeline.scrubbots_solver import ScrubBotsSolver
    grid = _grid()
    optimizer, fake, used = _optimizer(grid)
    seen: list[dict] = []

    class BoundedSolver(ScrubBotsSolver):
        def __init__(self) -> None:  # no Godot lookup
            pass

        def run(self, level, candidates, **options):
            seen.append(dict(options))
            return fake.run(level, candidates, **options)

    optimizer.solver = BoundedSolver()
    clock = Clock(2_000_000.0)
    monkeypatch.setattr(supply_optimizer.time, "time", clock.time)
    optimizer.run_grid(grid, used, seed=3, candidates=60, level_id="alt_test", metric_top=12,
                       real_max_visited=25_000, progress=None, real_timeout_seconds=900,
                       max_native_solver_invocations=1, auto_extend_solver_timeout=True,
                       wall_deadline=clock.now + 500,
                       real_play_precheck=lambda *_args: {"won": True, "verdict": "WON_CANONICAL"})
    # Kernel replay (diverges in this fixture), native search, then the analysis.
    assert seen[0]["timeout"] == 500 and seen[0]["analyze"] is False
    assert seen[1]["timeout"] == 500 and seen[1]["auto_extend_timeout"] is False
    # The analysis of a won plan gets the 15-minute grace on top (capped at 900 s per call).
    assert seen[2]["timeout"] == 900 and seen[2]["analyze"] is True


def test_kernel_replay_proof_skips_the_native_search() -> None:
    # Owner decision 2026-11-13: when the official kernel replays the screening order
    # to a finished board, the plan needs no native search.
    grid = _grid()
    optimizer, solver, used = _optimizer(grid)
    solver.diverge = False

    result = _run(optimizer, grid, used, lambda *_args: {"won": True, "verdict": "WON_CANONICAL"})

    kinds = [call[1] for call in solver.calls]
    assert kinds == ["VERIFY", "ANALYZE"]
    assert result["solver_evidence"]["solver"]["solver"]["proof"] == "KERNEL_REPLAY"
    assert result["solver_evidence"]["runner"]["trace_verify_status"] == "SOLVED"


def test_a_won_plan_gets_fifteen_more_minutes_for_the_analysis(monkeypatch) -> None:
    # Owner decision 2026-11-13: LF-000047 won real play at minute 21; the analysis
    # must not be cut at minute 30 and throw the won level away.
    from scrubbots_pixel_factory.supply_pipeline import supply_optimizer
    from scrubbots_pixel_factory.supply_pipeline.scrubbots_solver import ScrubBotsSolver
    grid = _grid()
    optimizer, fake, used = _optimizer(grid)
    seen: list[dict] = []

    class BoundedSolver(ScrubBotsSolver):
        def __init__(self) -> None:
            pass

        def run(self, level, candidates, **options):
            seen.append(dict(options))
            return fake.run(level, candidates, **options)

    optimizer.solver = BoundedSolver()
    clock = Clock(3_000_000.0)
    monkeypatch.setattr(supply_optimizer.time, "time", clock.time)
    result = optimizer.run_grid(grid, used, seed=3, candidates=60, level_id="alt_test", metric_top=12,
                                real_max_visited=25_000, progress=None, real_timeout_seconds=900,
                                max_native_solver_invocations=1, wall_deadline=clock.now + 60,
                                real_play_precheck=lambda *_args: {"won": True, "verdict": "WON_CANONICAL"})
    analysis = [options for options in seen if options.get("analyze")]
    assert analysis
    assert analysis[0]["timeout"] == min(900, 60 + supply_optimizer.ANALYSIS_GRACE_SECONDS)
    assert result["difficulty_basis"].startswith("ScrubBots Difficulty V1")
