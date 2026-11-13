"""The incremental-eligibility ScreeningSimulator (2026-11-13) must return exactly what the
frozen previous implementation returned: solve status/visited/trace, replay steps and
peel waves, on boards with and without transparent cells."""
import random

import numpy as np
import pytest

from scrubbots_pixel_factory.supply_pipeline.screening import ScreeningSimulator
from tests.unit._screening_reference_v1 import ScreeningSimulator as ReferenceSimulator


def _board(rng, h, w, colors, holes):
    grid = np.array([[rng.randrange(colors) for _ in range(w)] for _ in range(h)], dtype=np.int16)
    for _ in range(holes):
        grid[rng.randrange(h), rng.randrange(w)] = -1
    return grid


def _columns(rng, grid, n_columns, max_batch):
    batches = []
    for color in sorted({int(v) for v in grid.ravel() if v >= 0}):
        left = int((grid == color).sum())
        while left:
            amount = min(left, rng.randint(1, max_batch))
            batches.append((color, amount))
            left -= amount
    rng.shuffle(batches)
    return [batches[i::n_columns] for i in range(n_columns)]


def _compare(grid, columns, slots, budget):
    new, old = ScreeningSimulator(grid, slots), ReferenceSimulator(grid, slots)
    got, want = new.solve(columns, max_visited=budget), old.solve(columns, max_visited=budget)

    assert got == want
    assert new.replay(columns, want["trace"]) == old.replay(columns, want["trace"])
    assert np.array_equal(new.peel_waves(), old.peel_waves())
    assert new.key(new.initial(columns)) == old.key(old.initial(columns))
    return got["status"]


@pytest.mark.parametrize("seed", range(80))
def test_new_simulator_matches_frozen_reference(seed):
    # 72 SOLVED, 7 BOUND, 1 DEADLOCK across these seeds.
    rng = random.Random(seed)
    h, w = rng.randint(5, 14), rng.randint(5, 14)
    grid = _board(rng, h, w, rng.randint(3, 7), rng.randint(0, h * w // 4))
    columns = _columns(rng, grid, rng.randint(2, 4), rng.randint(3, 14))
    _compare(grid, columns, rng.randint(1, 4), rng.choice([30, 300, 3000]))


def test_forced_unreachable_batch_deadlocks_identically():
    grid = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=np.int16)
    assert _compare(grid, [[(1, 1), (0, 8)]], 1, 3000) == "DEADLOCK"
