"""Strict shared limits for owner-triggered native solver work."""

from __future__ import annotations

import math


MAX_SOLVER_VISITED = 25_000
MAX_SOLVER_TIMEOUT_SECONDS = 240.0
MAX_SOLVER_HARD_TIMEOUT_SECONDS = 480.0


def normalize_solver_budget(real_max_visited: object, timeout_seconds: object) -> tuple[int, float]:
    """Return a validated visit/time budget; reject coercions and missing values."""

    if type(real_max_visited) is not int or not 0 < real_max_visited <= MAX_SOLVER_VISITED:
        raise ValueError("real_max_visited must be an integer in 1..25000")
    if isinstance(timeout_seconds, bool) or type(timeout_seconds) not in (int, float):
        raise ValueError("solver_timeout_seconds must be a finite number in (0, 240]")
    timeout = float(timeout_seconds)
    if not math.isfinite(timeout) or not 0 < timeout <= MAX_SOLVER_TIMEOUT_SECONDS:
        raise ValueError("solver_timeout_seconds must be a finite number in (0, 240]")
    return real_max_visited, timeout


def normalize_staged_solver_budget(
    real_max_visited: object, initial_timeout_seconds: object, *, auto_extend: bool
) -> tuple[int, float, float]:
    """Validate the bounded 240s initial / 480s absolute native policy."""
    visited, initial = normalize_solver_budget(real_max_visited, initial_timeout_seconds)
    if not auto_extend:
        return visited, initial, initial
    if initial != MAX_SOLVER_TIMEOUT_SECONDS:
        raise ValueError("automatic solver extension requires the 240-second initial budget")
    return visited, initial, MAX_SOLVER_HARD_TIMEOUT_SECONDS


def staged_solver_timeout_limit(initial_timeout_seconds: float, hard_timeout_seconds: float, *, attested: bool) -> float:
    """Return the policy ceiling matching the normalized effective deadline."""
    if not attested:
        return 300.0
    return MAX_SOLVER_HARD_TIMEOUT_SECONDS if hard_timeout_seconds > initial_timeout_seconds else MAX_SOLVER_TIMEOUT_SECONDS


def staged_solver_deadline_state(
    elapsed_seconds: float, initial_timeout_seconds: float, hard_timeout_seconds: float,
) -> str:
    """Return the native runner phase without mutating or extending a deadline."""
    if elapsed_seconds >= hard_timeout_seconds:
        return "TIMEOUT"
    if hard_timeout_seconds > initial_timeout_seconds and elapsed_seconds >= initial_timeout_seconds:
        return "EXTENDED"
    return "RUNNING"
