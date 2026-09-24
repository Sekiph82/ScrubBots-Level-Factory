from __future__ import annotations

from pathlib import Path

import pytest

from scrubbots_pixel_factory.difficulty_analysis import CALIBRATION_POLICY_STATE, CalibrationDataset, LevelMetricsError, disabled_calibration_plan


def dataset() -> CalibrationDataset:
    return CalibrationDataset("DIFFICULTY_V1", "future-cohort-a", 8, 2, 120, 10, 10)


def test_calibration_is_disabled_and_round_trips_offline_aggregates() -> None:
    value = dataset()
    restored = CalibrationDataset.from_dict(value.canonical_dict())
    plan = disabled_calibration_plan(restored)
    assert plan.state == CALIBRATION_POLICY_STATE
    assert not plan.network_enabled and not plan.collection_enabled
    assert value.canonical_bytes() == restored.canonical_bytes()


@pytest.mark.parametrize("field", ["name", "email", "device_id", "account_id", "ip_address", "raw_events", "pii"])
def test_forbidden_identity_and_raw_event_fields_are_rejected(field: str) -> None:
    payload = {**dataset().canonical_dict(), field: "forbidden"}
    with pytest.raises(LevelMetricsError):
        CalibrationDataset.from_dict(payload)


def test_minimum_sample_count_and_safe_cohort_label_are_enforced() -> None:
    with pytest.raises(LevelMetricsError):
        CalibrationDataset("DIFFICULTY_V1", "future-cohort-a", 1, 0, 2, 1, 10)
    with pytest.raises(LevelMetricsError):
        CalibrationDataset("DIFFICULTY_V1", "person@example.com", 1, 0, 2, 1, 1)


def test_current_module_has_no_runtime_network_or_collection_hooks() -> None:
    source = Path(__file__).resolve().parents[2].joinpath("src", "scrubbots_pixel_factory", "difficulty_analysis.py").read_text(encoding="utf-8").lower()
    assert all(token not in source for token in ("requests.", "urllib", "httpx", "socket", "telemetry", "collect_player"))
