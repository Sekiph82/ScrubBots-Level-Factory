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


def test_very_hard_plus_band_ranks_more_pressuring_plans_higher() -> None:
    # Owner 2026-11-24: VERY_HARD variants rank screened plans by a band above VERY_HARD.
    from scrubbots_pixel_factory.supply_pipeline.supply_scorer import TARGETS, _band
    plus, vh = TARGETS["VERY_HARD_PLUS"], TARGETS["VERY_HARD"]
    assert all(plus[k][0] > vh[k][0] for k in ("dead", "forced", "slot"))
    assert _band(0.75, *plus["slot"]) == 1.0 and _band(0.75, *vh["slot"]) == 1.0
    assert _band(0.9, *plus["slot"]) > _band(0.9, *vh["slot"])
    rules = GameRules(pinned_game_source.expected_runtime_root(), column_count=3)
    assert SupplyOptimizer(rules, score_band="VERY_HARD_PLUS").score_band == "VERY_HARD_PLUS"
