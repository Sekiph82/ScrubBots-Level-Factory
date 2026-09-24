from __future__ import annotations

import pytest

from scrubbots_pixel_factory.difficulty_analysis import (
    CHALLENGE_SCORE_POLICY_VERSION,
    ChallengeScoreResult,
    LaneClass,
    ScoreComponent,
    map_challenge_score,
)
from scrubbots_pixel_factory.contracts.difficulty import Difficulty
from scrubbots_pixel_factory.level_metrics import LevelMetricsError


def score(value: float) -> ChallengeScoreResult:
    component = ScoreComponent(0.0, 0.0, 0.0)
    return ChallengeScoreResult(CHALLENGE_SCORE_POLICY_VERSION, "a" * 64, (("move", component), ("states", component), ("dead_end", component), ("branching", component), ("forced", component)), value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0.0, LaneClass.EASY), (24.999999, LaneClass.EASY), (25.0, LaneClass.MEDIUM), (49.999999, LaneClass.MEDIUM), (50.0, LaneClass.HARD), (74.999999, LaneClass.HARD), (75.0, LaneClass.VERY_HARD), (100.0, LaneClass.VERY_HARD)],
)
def test_exact_threshold_edges(value: float, expected: LaneClass) -> None:
    assert map_challenge_score(score(value)).lane is expected


@pytest.mark.parametrize("value", [-0.01, 100.01])
def test_out_of_range_score_is_rejected(value: float) -> None:
    with pytest.raises(LevelMetricsError):
        # The score result itself is closed to [0, 100].
        score(value)


def test_requested_class_comparison_is_neutral_and_serialization_is_deterministic() -> None:
    first = map_challenge_score(score(50.0), Difficulty.HARD)
    second = map_challenge_score(score(50.0), Difficulty.HARD)
    assert first.lane is LaneClass.HARD and first.comparison == "MATCH"
    assert first.canonical_bytes() == second.canonical_bytes()


def test_mapping_carries_score_lineage_and_does_not_touch_any_level_data() -> None:
    result = map_challenge_score(score(25.0), "EASY")
    assert result.score_digest == score(25.0).digest()
    assert result.lane is LaneClass.MEDIUM and result.comparison == "MISMATCH"
