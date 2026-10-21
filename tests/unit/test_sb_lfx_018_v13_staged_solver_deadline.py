from __future__ import annotations

from dataclasses import dataclass

import pytest

from scrubbots_pixel_factory.supply_pipeline.solver_budget import (
    MAX_SOLVER_HARD_TIMEOUT_SECONDS,
    MAX_SOLVER_TIMEOUT_SECONDS,
    normalize_staged_solver_budget,
    staged_solver_deadline_state,
    staged_solver_timeout_limit,
)


@dataclass
class FakeClock:
    now: float = 0.0

    def monotonic(self) -> float:
        return self.now


class FakeProcess:
    def __init__(self, pid: int, clock: FakeClock, terminal_at: float | None = None, result: str = "SOLVED") -> None:
        self.pid = pid
        self.clock = clock
        self.terminal_at = terminal_at
        self.result = result
        self.termination_count = 0

    def poll(self) -> str | None:
        if self.terminal_at is not None and self.clock.monotonic() >= self.terminal_at:
            return self.result
        return None

    def terminate_tree(self) -> None:
        self.termination_count += 1


def _drive_fake_process(*, terminal_at: float | None = None, terminal_result: str = "SOLVED", cancel_at: float | None = None):
    clock = FakeClock()
    process_launch_count = 1
    process = FakeProcess(731, clock, terminal_at, terminal_result)
    extension_events: list[tuple[int, float]] = []
    phase = "RUNNING"
    for moment in (20.0, 239.99, 240.0, 400.0, 479.99, 480.0):
        clock.now = moment
        if process.poll() is not None:
            phase = "TERMINAL"
            break
        if cancel_at is not None and moment >= cancel_at:
            process.terminate_tree()
            phase = "CANCELLED"
            break
        state = staged_solver_deadline_state(moment, 240.0, 480.0)
        if state == "EXTENDED" and phase != "EXTENDED":
            phase = "EXTENDED"
            extension_events.append((process.pid, moment))
        if state == "TIMEOUT":
            process.terminate_tree()
            phase = "TIMEOUT_480"
            break
    return process_launch_count, process, extension_events, phase


def test_staged_budget_keeps_240_initial_and_caps_absolute_total_at_480() -> None:
    assert normalize_staged_solver_budget(25_000, 240, auto_extend=True) == (25_000, 240.0, 480.0)
    assert normalize_staged_solver_budget(25_000, 240, auto_extend=False) == (25_000, 240.0, 240.0)
    assert MAX_SOLVER_TIMEOUT_SECONDS == 240.0
    assert MAX_SOLVER_HARD_TIMEOUT_SECONDS == 480.0
    assert staged_solver_timeout_limit(240.0, 480.0, attested=True) == 480.0
    assert staged_solver_timeout_limit(240.0, 240.0, attested=True) == 240.0
    assert staged_solver_timeout_limit(240.0, 300.0, attested=False) == 300.0
    with pytest.raises(ValueError, match="240-second initial"):
        normalize_staged_solver_budget(25_000, 90, auto_extend=True)
    with pytest.raises(ValueError, match=r"240\]"):
        normalize_staged_solver_budget(25_000, 480, auto_extend=False)


def test_one_fake_process_transitions_once_at_240_and_times_out_at_480() -> None:
    launches, process, extensions, phase = _drive_fake_process()
    assert launches == 1
    assert process.pid == 731
    assert extensions == [(731, 240.0)]
    assert process.termination_count == 1
    assert phase == "TIMEOUT_480"


@pytest.mark.parametrize(
    ("terminal_at", "terminal_result", "expected_phase"),
    [(20.0, "SOLVED", "TERMINAL"), (239.0, "UNSOLVABLE", "TERMINAL"), (310.0, "SOLVED", "TERMINAL")],
)
def test_terminal_result_before_or_during_extension_does_not_wait_for_timeout(
    terminal_at: float, terminal_result: str, expected_phase: str
) -> None:
    launches, process, extensions, phase = _drive_fake_process(terminal_at=terminal_at, terminal_result=terminal_result)
    assert launches == 1
    assert process.poll() == terminal_result
    assert phase == expected_phase
    assert process.termination_count == 0
    assert len(extensions) == (1 if terminal_at > 240 else 0)


def test_manual_cancel_after_extension_terminates_same_process_without_timeout() -> None:
    launches, process, extensions, phase = _drive_fake_process(cancel_at=300.0)
    assert launches == 1
    assert process.pid == extensions[0][0] == 731
    assert phase == "CANCELLED"
    assert process.termination_count == 1
    assert extensions == [(731, 240.0)]


def test_solver_process_crash_before_initial_deadline_is_terminal_without_retry() -> None:
    launches, process, extensions, phase = _drive_fake_process(terminal_at=20.0, terminal_result="CRASHED")
    assert launches == 1
    assert process.poll() == "CRASHED"
    assert phase == "TERMINAL"
    assert extensions == []
    assert process.termination_count == 0


def test_staged_deadline_exact_transition_boundaries() -> None:
    assert staged_solver_deadline_state(239.99, 240.0, 480.0) == "RUNNING"
    assert staged_solver_deadline_state(240.0, 240.0, 480.0) == "EXTENDED"
    assert staged_solver_deadline_state(400.0, 240.0, 480.0) == "EXTENDED"
    assert staged_solver_deadline_state(479.99, 240.0, 480.0) == "EXTENDED"
    assert staged_solver_deadline_state(480.0, 240.0, 480.0) == "TIMEOUT"
    # A native solve-end marker alone must not disable the process hard deadline.
    assert staged_solver_deadline_state(480.0, 240.0, 480.0) == "TIMEOUT"
