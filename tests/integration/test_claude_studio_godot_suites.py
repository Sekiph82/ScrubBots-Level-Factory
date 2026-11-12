"""Every headless Factory Studio Godot suite runs in an isolated checkout copy.

Before 2026-11-12 only 8 of the 41 suites under level_factory/tests had a
pytest wrapper; the others were never executed and silently drifted from the
product (removed controls, the Pending-only batch flow, the canonical data
layout). This module runs each suite that has no dedicated wrapper, through the
same isolated-copy fixture, so they cannot drift again.
"""
from __future__ import annotations

from pathlib import Path

import pytest

SUITES_DIR = Path(__file__).resolve().parents[2] / "level_factory" / "tests"
# Already run (with suite-specific assertions) by a dedicated tests/unit wrapper.
WRAPPED = {
    "factory_studio_action_integration_suite.gd",
    "factory_studio_art_revalidation_integration_suite.gd",
    "factory_studio_dashboard_integration_suite.gd",
    "factory_studio_exact_reproduce_integration_suite.gd",
    "factory_studio_import_integration_suite.gd",
    "factory_studio_puzzle_config_gate_integration_suite.gd",
    "factory_studio_runtime_suite.gd",
    "factory_studio_truth_separation_integration_suite.gd",
}
# Scripts in the folder that are not Studio test suites.
NOT_SUITES = {
    "factory_test_paths.gd",  # shared path helper
    "factory_test_ready_fixture.gd",  # shared READY fixture helper
    "factory_studio_owner_visual_evidence_suite.gd",  # screenshot tool: needs a display and SB_LFX_018_SCREENSHOT_DIR
    "factory_studio_r09_r02_r04_r01_profile_derivation_suite.gd",  # runs inside the pinned game runtime, not the Factory project
}
SUITES = sorted(
    path.name for path in SUITES_DIR.glob("*.gd")
    if path.name not in WRAPPED | NOT_SUITES and not path.name.startswith("_claude")
)


def test_every_studio_suite_is_covered() -> None:
    assert len(SUITES) + len(WRAPPED) + len(NOT_SUITES) == len(list(SUITES_DIR.glob("*.gd"))) - len(
        [p for p in SUITES_DIR.glob("_claude*.gd")])
    assert all((SUITES_DIR / name).is_file() for name in WRAPPED | NOT_SUITES)


@pytest.mark.parametrize("suite", SUITES)
def test_studio_godot_suite_passes_in_isolation(run_isolated_godot_suite, suite: str) -> None:
    result = run_isolated_godot_suite(suite, timeout=420)
    output = result.stdout + result.stderr
    assert result.returncode == 0, output[-4000:]
    for forbidden in ("SCRIPT ERROR", "Parse Error"):
        assert forbidden not in output, output[-4000:]
