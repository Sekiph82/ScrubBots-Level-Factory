"""Owner idea 2026-11-23: repair a real-play slot jam instead of failing the PNG.

At the stuck click every WAITING slot batch keeps only the robots it used; the rest go to
a new batch at the end of the same column (one more click). Experiment on the 21
REAL_PLAY_NO_WINNING_PLAN levels: 16 won in real play after this repair.
"""
from __future__ import annotations

import numpy as np

from scrubbots_pixel_factory.supply_pipeline import supply_optimizer as so
from scrubbots_pixel_factory.supply_pipeline.screening import ScreeningSimulator

LEVEL = "candidate-owner-" + "e" * 48


def _slot(column: int, row: int, remaining: int, state: str = "WAITING") -> dict:
    return {"batchId": f"{LEVEL}-K{column}-{row:02d}", "occupied": True, "state": state, "remaining": remaining}


def test_every_waiting_slot_keeps_its_used_robots_and_moves_the_rest_to_its_column_end() -> None:
    # Arrange: two columns; slots hold K1-02 (5 of 9 unused) and K2-01 (all 4 unused).
    columns = [[(0, 3), (1, 9)], [(2, 4), (0, 2)]]
    clicks = [1, 1, 2]
    slots = [_slot(1, 2, 5), _slot(2, 1, 4), _slot(1, 1, 0, "WORKING"), {"occupied": False}]

    # Act
    repaired = so._repair_slot_jam(columns, clicks, slots)

    # Assert: robot totals per colour are conserved; one extra click per moved batch.
    assert repaired is not None
    new_columns, new_clicks = repaired
    assert new_columns == [[(0, 3), (1, 4), (1, 5)], [(2, 2), (0, 2), (2, 2)]]
    assert new_clicks == [1, 1, 2, 1, 2]
    assert columns == [[(0, 3), (1, 9)], [(2, 4), (0, 2)]]  # input untouched


def test_nothing_to_repair_returns_none() -> None:
    assert so._repair_slot_jam([[(0, 1)]], [1], [_slot(1, 1, 0)]) is None
    assert so._repair_slot_jam([[(0, 1)]], [1], [_slot(1, 1, 1)]) is None  # a 1-robot batch cannot shrink


def test_click_trace_replays_the_screening_kernel_and_requires_a_solved_board() -> None:
    # Arrange: 1x2 board, colours 0 and 1 on the border; one batch each.
    sim = ScreeningSimulator(np.array([[0, 1]]), slot_count=2)

    # Act
    solved = so._trace_for_clicks(sim, [[(0, 1)], [(1, 1)]], [1, 2])
    short = so._trace_for_clicks(sim, [[(0, 1)], [(1, 1)]], [1])

    # Assert
    assert [step["column"] for step in solved] == [0, 1]
    assert solved[-1]["active_after"] == 0 and sum(step["clears"] for step in solved) == 2
    assert short is None
