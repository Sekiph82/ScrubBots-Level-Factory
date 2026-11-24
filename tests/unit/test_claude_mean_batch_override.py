"""EASY difficulty variants re-solve with a forced mean batch size (owner 2026-11-24)."""
import numpy as np

from scrubbots_pixel_factory.supply_pipeline import pinned_game_source
from scrubbots_pixel_factory.supply_pipeline.game_rules import GameRules
from scrubbots_pixel_factory.supply_pipeline.supply_optimizer import SupplyOptimizer


def test_mean_batch_override_replaces_the_band_seed_and_sizes_the_plan() -> None:
    grid = np.zeros((20, 20), dtype=int)
    grid[:, 10:] = 1
    rules = GameRules(pinned_game_source.expected_runtime_root(), column_count=3)
    default = SupplyOptimizer(rules).prepare_grid(grid, [0, 1])
    forced = SupplyOptimizer(rules, mean_batch=7).prepare_grid(grid, [0, 1])
    assert forced[4] == 7.0 and default[4] != 7.0
    assert forced[5] == round(400 / 7)  # total batches follow the forced mean
