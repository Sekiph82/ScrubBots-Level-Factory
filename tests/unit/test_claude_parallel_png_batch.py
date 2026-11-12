"""Owner request 2026-11-12: solve several batch PNGs at the same time.

One level took ~13 minutes inside one solver process, so the sequential queue
could not reach 100 levels a day. run_png_batch now keeps up to
``parallel_workers`` canonical pipelines in flight; job state is still written
only by the orchestrating thread.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from scrubbots_pixel_factory import png_batch

from test_sb_lfx_018_r09_r02_r04_r02_png_batch import _make_batch, _ready_result


def _prepare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, count: int, workers: int) -> tuple[dict, list]:
    batch_id, items = _make_batch(tmp_path, monkeypatch, count)
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda _pipeline, _columns: True)
    monkeypatch.setattr(png_batch, "_recover_attempt", lambda _job, _item: None)
    monkeypatch.setenv("SCRUBBOTS_FACTORY_BATCH_WORKERS", str(workers))
    return png_batch.create_png_batch(batch_id)["job"], items


def test_parallel_batch_keeps_worker_count_pipelines_in_flight(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    job, items = _prepare(tmp_path, monkeypatch, 8, workers=3)
    guard = threading.Lock()
    three_running = threading.Event()
    active = {"now": 0, "peak": 0}

    def slow_runner(*, source_id: str, request: dict[str, object]) -> dict[str, object]:
        with guard:
            active["now"] += 1
            active["peak"] = max(active["peak"], active["now"])
            if active["now"] == 3:
                three_running.set()
        # The first items wait (bounded) until three run at once; timing-free.
        three_running.wait(10)
        with guard:
            active["now"] -= 1
        return _ready_result(source_id, f"run-{request['png_batch_item_index']}", request)

    # Act
    result = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=slow_runner)

    # Assert
    assert result["disposition"] == "COMPLETE"
    assert active["peak"] == 3
    assert [item["status"] for item in result["job"]["items"]] == ["READY"] * 8
    assert result["job"]["current_index"] is None
    stored = png_batch._read_job(str(job["job_id"]))
    assert stored["counts"]["ready"] == 8 and stored["state"] == "COMPLETE"


def test_parallel_pause_finishes_running_items_and_starts_no_new_one(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    job, _items = _prepare(tmp_path, monkeypatch, 6, workers=3)
    all_started = threading.Barrier(3, timeout=10)
    calls: list[str] = []

    def pausing_runner(*, source_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append(source_id)
        if all_started.wait() == 0:
            png_batch.png_batch_control(str(job["job_id"]), "PAUSE_AFTER_CURRENT")
        time.sleep(0.1)
        return _ready_result(source_id, f"run-{request['png_batch_item_index']}", request)

    # Act
    paused = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=pausing_runner)

    # Assert
    assert paused["disposition"] == "PAUSED"
    assert len(calls) == 3
    assert [item["status"] for item in paused["job"]["items"][:3]] == ["READY"] * 3
    assert paused["job"]["counts"]["remaining"] == 3


def test_parallel_worker_failure_is_recorded_for_that_item_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    job, items = _prepare(tmp_path, monkeypatch, 5, workers=2)
    broken = str(items[2]["source_id"])

    def runner(*, source_id: str, request: dict[str, object]) -> dict[str, object]:
        if source_id == broken:
            raise RuntimeError("solver crashed")
        return _ready_result(source_id, f"run-{request['png_batch_item_index']}", request)

    # Act
    result = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=runner)

    # Assert
    statuses = {item["source_id"]: item["status"] for item in result["job"]["items"]}
    assert result["disposition"] == "FINISHED_WITH_FAILURES"
    assert statuses.pop(broken) == "FAILED"
    assert set(statuses.values()) == {"READY"}


@pytest.mark.parametrize(("setting", "env", "cores", "expected"), [
    (None, None, 16, 6), (None, None, 8, 4), (None, None, 4, 2), (None, "2", 16, 2), (6, None, 16, 6), (99, None, 16, 8), (None, None, None, 2),
])
def test_parallel_workers_default_and_bounds(monkeypatch: pytest.MonkeyPatch, setting, env, cores, expected) -> None:
    if env is None:
        monkeypatch.delenv("SCRUBBOTS_FACTORY_BATCH_WORKERS", raising=False)
    else:
        monkeypatch.setenv("SCRUBBOTS_FACTORY_BATCH_WORKERS", env)
    monkeypatch.setattr(png_batch.os, "cpu_count", lambda: cores)
    assert png_batch.parallel_workers({"parallel_workers": setting} if setting else {}) == expected


def test_failed_item_reason_carries_the_solver_reason_not_a_bare_disposition(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Real app 2026-11-12: retry rows showed only "UNAVAILABLE" while the solver
    # said the game validator rejected the artwork ratio.
    job, _items = _prepare(tmp_path, monkeypatch, 1, workers=1)
    solver_reason = ("solver bridge failed:\nGodot Engine v4.7.2.stable.official - https://godotengine.org\n\n"
                     "ProductionLevelValidator rejected bridge LevelData: production artwork needs >= 200 non-VOID cells and >= 1/4 of the board; got 719 of 3136")

    result = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=lambda **_args: {
        "disposition": "UNAVAILABLE", "primary": {"state": "UNAVAILABLE", "reason": solver_reason}})

    reason = result["job"]["items"][0]["reason"]
    assert reason.startswith("UNAVAILABLE: solver bridge failed:")
    assert "got 719 of 3136" in reason and "Godot Engine" not in reason


def test_resume_rebinds_a_batch_planned_with_the_previous_runtime(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Owner re-pin 2026-11-12: a STOPPED batch planned with aef60a61 must not keep
    # solving its remaining items with the old game rules after Resume.
    from scrubbots_pixel_factory.supply_pipeline import pinned_game_source as pins

    job, _items = _prepare(tmp_path, monkeypatch, 2, workers=1)
    old_root = pins.runtime_root("aef60a616d4ac401e9dfac15df6fe56e671c0053")
    stored = png_batch._read_job(str(job["job_id"]))
    stored["settings"]["game_project"] = str(old_root)
    png_batch._write_job(stored)
    seen: list[str] = []

    def runner(*, source_id: str, request: dict[str, object]) -> dict[str, object]:
        seen.append(str(request["game_project"]))
        return _ready_result(source_id, f"run-{request['png_batch_item_index']}", request)

    result = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=runner)

    current = str(pins.expected_runtime_root().resolve())
    assert seen == [current, current]
    assert result["job"]["runtime_rebinds"][0]["from"] == old_root.name
