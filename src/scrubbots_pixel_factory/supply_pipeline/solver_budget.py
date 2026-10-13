"""Strict shared limits for owner-triggered native solver work."""

from __future__ import annotations

import math


MAX_SOLVER_VISITED = 25_000
MAX_SOLVER_TIMEOUT_SECONDS = 90.0


def normalize_solver_budget(real_max_visited: object, timeout_seconds: object) -> tuple[int, float]:
    """Return a validated visit/time budget; reject coercions and missing values."""

    if type(real_max_visited) is not int or not 0 < real_max_visited <= MAX_SOLVER_VISITED:
        raise ValueError("real_max_visited must be an integer in 1..25000")
    if isinstance(timeout_seconds, bool) or type(timeout_seconds) not in (int, float):
        raise ValueError("solver_timeout_seconds must be a finite number in (0, 90]")
    timeout = float(timeout_seconds)
    if not math.isfinite(timeout) or not 0 < timeout <= MAX_SOLVER_TIMEOUT_SECONDS:
        raise ValueError("solver_timeout_seconds must be a finite number in (0, 90]")
    return real_max_visited, timeout
