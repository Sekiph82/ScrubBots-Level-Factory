"""Owner decision 2026-11-12: re-pin new solves to game main dd54007a.

Existing READY runs were solved with the 2026-10-12 runtime aef60a61. They must
keep being verified and classified with that exact runtime, while new solves
use dd54007a, where ADR-030 D2 no longer has the 25%-of-board ratio.
"""
from scrubbots_pixel_factory.supply_pipeline import pinned_game_source as pins
from scrubbots_pixel_factory.supply_pipeline.void_capability import void_capability

OLD = "aef60a616d4ac401e9dfac15df6fe56e671c0053"
MID = "dd54007abb59863bc753c1a029b9db227fb4f89f"
# Owner re-pin 2026-11-13: game 6534537c (faster ProofKernel / Difficulty V1).
NEW = "6534537ceb4c71c63286614b74e4801145d5fb4d"


def test_new_solves_use_dd54007a_and_old_runs_keep_their_runtime() -> None:
    assert pins.PINNED_MAIN_SHA == NEW
    assert pins.expected_runtime_root().name == NEW
    assert pins.runtime_root_for_run({"authority": {"git_head": OLD}}).name == OLD
    assert pins.runtime_root_for_run({"authority": {"git_head": MID}}).name == MID
    assert pins.runtime_root_for_run({"authority": {"git_head": NEW}}).name == NEW
    # A run without a recorded or known authority falls back to the current pin.
    assert pins.runtime_root_for_run({}).name == NEW
    assert pins.runtime_root_for_run({"authority": {"git_head": "0" * 40}}).name == NEW


def test_both_runtimes_are_attested_and_report_their_own_artwork_rule() -> None:
    old_gate = void_capability(pins.runtime_root(OLD))
    new_gate = void_capability(pins.runtime_root(NEW))
    assert old_gate["state"] == new_gate["state"] == "OPEN"
    assert old_gate["git_head"] == OLD and new_gate["git_head"] == NEW
    assert old_gate["d2"] == {"minimum_artwork_cells": 200, "minimum_artwork_ratio": 0.25}
    assert new_gate["d2"] == {"minimum_artwork_cells": 200}
    assert new_gate["audited_commit"] == "0b6dfc359d3bf34afa4e78d53a68b788088a863a"
    mid_gate = void_capability(pins.runtime_root(MID))
    assert mid_gate["state"] == "OPEN" and mid_gate["git_head"] == MID and mid_gate["d2"] == {"minimum_artwork_cells": 200}


def test_new_runtime_validator_no_longer_enforces_the_ratio() -> None:
    source = (pins.runtime_root(NEW) / "scripts" / "data" / "production_level_validator.gd").read_text(encoding="utf-8")
    assert "MIN_ARTWORK_FRACTION" not in source
    old_source = (pins.runtime_root(OLD) / "scripts" / "data" / "production_level_validator.gd").read_text(encoding="utf-8")
    assert "MIN_ARTWORK_FRACTION_DEN" in old_source
