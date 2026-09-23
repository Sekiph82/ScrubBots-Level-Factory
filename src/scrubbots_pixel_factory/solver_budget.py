"""Versioned deterministic solver budgets and outcome mapping."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math

from .baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from .solution_analysis import SolutionAnalysisBounds, SolutionCountDisposition, SolutionCountResult


SOLVER_BUDGET_SCHEMA = "scrubbots-solver-budget-policy"
SOLVER_BUDGET_VERSION = 1
SOLVER_OUTCOME_SCHEMA = "scrubbots-solver-budgeted-outcome"
SOLVER_OUTCOME_VERSION = 1
OPERATIONAL_TIMEOUT_POLICY_VERSION = "MONOTONIC_OPERATIONAL_TIMEOUT_V1"


class SolverBudgetError(ValueError):
    """Raised when a solver budget contract is malformed."""


class SolverOutcomeDisposition(str, Enum):
    SOLVED = "SOLVED"
    PROVEN_UNSOLVABLE = "PROVEN_UNSOLVABLE"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class OperationalExecutionDisposition(str, Enum):
    COMPLETED = "COMPLETED"
    INCONCLUSIVE = "INCONCLUSIVE"
    ERROR = "ERROR"


class BudgetExhaustionReason(str, Enum):
    MAX_VISITED_STATES = "MAX_VISITED_STATES"
    MAX_DEPTH = "MAX_DEPTH"
    MAX_SOLUTIONS = "MAX_SOLUTIONS"
    UNKNOWN_BOUND = "UNKNOWN_BOUND"


def _positive_int(value: object, name: str) -> int:
    if type(value) is not int or isinstance(value, bool) or value < 1:
        raise SolverBudgetError(f"{name} must be a positive exact integer")
    return value


def _non_negative_int(value: object, name: str) -> int:
    if type(value) is not int or isinstance(value, bool) or value < 0:
        raise SolverBudgetError(f"{name} must be a non-negative exact integer")
    return value


def _canonical_bytes(value: dict[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True, slots=True)
class SolverBudgetPolicy:
    max_visited_states: int = 10000
    max_depth: int = 64
    max_solutions: int = 100
    def __post_init__(self) -> None:
        object.__setattr__(self, "max_visited_states", _positive_int(self.max_visited_states, "max visited states"))
        object.__setattr__(self, "max_depth", _non_negative_int(self.max_depth, "max depth"))
        object.__setattr__(self, "max_solutions", _positive_int(self.max_solutions, "max solutions"))

    @classmethod
    def from_solution_bounds(cls, bounds: SolutionAnalysisBounds) -> "SolverBudgetPolicy":
        if not isinstance(bounds, SolutionAnalysisBounds):
            raise SolverBudgetError("solution bounds are malformed")
        return cls(bounds.max_states, bounds.max_depth, bounds.max_solutions)

    def to_baseline_policy(self) -> BaselineSearchPolicy:
        return BaselineSearchPolicy(max_depth=self.max_depth)

    def to_solution_bounds(self) -> SolutionAnalysisBounds:
        return SolutionAnalysisBounds(max_depth=self.max_depth, max_states=self.max_visited_states, max_solutions=self.max_solutions)

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": SOLVER_BUDGET_SCHEMA,
            "version": SOLVER_BUDGET_VERSION,
            "max_visited_states": self.max_visited_states,
            "max_depth": self.max_depth,
            "max_solutions": self.max_solutions,
        }

    def digest(self) -> str:
        return hashlib.sha256(_canonical_bytes(self.canonical_dict())).hexdigest()

@dataclass(frozen=True, slots=True)
class BudgetedSolverResult:
    disposition: SolverOutcomeDisposition
    policy: SolverBudgetPolicy
    source: str
    source_disposition: str
    reason: str
    exhaustion: BudgetExhaustionReason | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, SolverOutcomeDisposition):
            raise SolverBudgetError("solver outcome disposition is malformed")
        if not isinstance(self.policy, SolverBudgetPolicy):
            raise SolverBudgetError("solver budget policy is malformed")
        if type(self.source) is not str or not self.source.strip():
            raise SolverBudgetError("solver outcome source is required")
        if type(self.source_disposition) is not str or not self.source_disposition.strip():
            raise SolverBudgetError("solver outcome source disposition is required")
        if type(self.reason) is not str or not self.reason.strip():
            raise SolverBudgetError("solver outcome reason is required")
        if self.exhaustion is not None and not isinstance(self.exhaustion, BudgetExhaustionReason):
            raise SolverBudgetError("solver outcome exhaustion reason is malformed")
        if self.disposition is SolverOutcomeDisposition.PROVEN_UNSOLVABLE and self.exhaustion is not None:
            raise SolverBudgetError("budget exhaustion cannot produce proven unsolvability")
    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": SOLVER_OUTCOME_SCHEMA,
            "version": SOLVER_OUTCOME_VERSION,
            "disposition": self.disposition.value,
            "policy": self.policy.canonical_dict(),
            "source": self.source,
            "source_disposition": self.source_disposition,
            "reason": self.reason,
            "exhaustion": self.exhaustion.value if self.exhaustion is not None else None,
        }

    def digest(self) -> str:
        return hashlib.sha256(_canonical_bytes(self.canonical_dict())).hexdigest()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class OperationalTimeoutTelemetry:
    timeout_seconds: float
    occurred: bool = True

    def __post_init__(self) -> None:
        if type(self.timeout_seconds) not in {int, float} or isinstance(self.timeout_seconds, bool) or not math.isfinite(float(self.timeout_seconds)) or self.timeout_seconds <= 0:
            raise SolverBudgetError("operational timeout must be a finite positive number")
        object.__setattr__(self, "timeout_seconds", float(self.timeout_seconds))
        if type(self.occurred) is not bool:
            raise SolverBudgetError("operational timeout occurrence must be boolean")

    def operational_dict(self) -> dict[str, object]:
        return {"version": OPERATIONAL_TIMEOUT_POLICY_VERSION, "timeout_seconds": self.timeout_seconds, "occurred": self.occurred, "canonical": False}


@dataclass(frozen=True, slots=True)
class OperationalSolverOutcome:
    disposition: OperationalExecutionDisposition
    canonical_result: BudgetedSolverResult | None
    timeout: OperationalTimeoutTelemetry | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, OperationalExecutionDisposition):
            raise SolverBudgetError("operational execution disposition is malformed")
        if self.canonical_result is not None and not isinstance(self.canonical_result, BudgetedSolverResult):
            raise SolverBudgetError("operational canonical result is malformed")
        if self.timeout is not None and not isinstance(self.timeout, OperationalTimeoutTelemetry):
            raise SolverBudgetError("operational timeout telemetry is malformed")
        if self.canonical_result is None and self.disposition is not OperationalExecutionDisposition.INCONCLUSIVE:
            raise SolverBudgetError("missing canonical result must be operationally inconclusive")

    def canonical_dict(self) -> dict[str, object] | None:
        return self.canonical_result.canonical_dict() if self.canonical_result is not None else None

    def canonical_bytes(self) -> bytes | None:
        return self.canonical_result.canonical_bytes() if self.canonical_result is not None else None

    def digest(self) -> str | None:
        return self.canonical_result.digest() if self.canonical_result is not None else None

    def operational_dict(self) -> dict[str, object]:
        return {"disposition": self.disposition.value, "timeout": self.timeout.operational_dict() if self.timeout is not None else None, "canonical": False}


def wrap_operational_execution(
    result: BudgetedSolverResult | None,
    *,
    timeout_seconds: float | None = None,
    timeout_occurred: bool = False,
) -> OperationalSolverOutcome:
    timeout = OperationalTimeoutTelemetry(timeout_seconds, timeout_occurred) if timeout_seconds is not None else None
    if result is None:
        if not timeout_occurred:
            return OperationalSolverOutcome(OperationalExecutionDisposition.ERROR, None, timeout)
        return OperationalSolverOutcome(OperationalExecutionDisposition.INCONCLUSIVE, None, timeout)
    return OperationalSolverOutcome(OperationalExecutionDisposition.COMPLETED, result, timeout)


def classify_search_result(
    result: BaselineSearchResult,
    metrics: object | None = None,
    policy: SolverBudgetPolicy | None = None,
) -> BudgetedSolverResult:
    budget = policy or SolverBudgetPolicy()
    if not isinstance(result, BaselineSearchResult):
        return BudgetedSolverResult(SolverOutcomeDisposition.ERROR, budget, "baseline_search", "MALFORMED", "search result is malformed")
    if result.execution is SearchExecutionDisposition.UNAVAILABLE:
        return BudgetedSolverResult(SolverOutcomeDisposition.UNAVAILABLE, budget, "baseline_search", result.execution.value, result.reason)
    if result.execution is SearchExecutionDisposition.ERROR:
        return BudgetedSolverResult(SolverOutcomeDisposition.ERROR, budget, "baseline_search", result.execution.value, result.reason)
    visited = getattr(metrics, "visited_count", None)
    if type(visited) is int and visited >= budget.max_visited_states and result.verdict is SearchVerdict.INCONCLUSIVE:
        return BudgetedSolverResult(
            SolverOutcomeDisposition.INCONCLUSIVE,
            budget,
            "baseline_search",
            result.verdict.value if result.verdict is not None else result.execution.value,
            "deterministic visited-state budget exhausted",
            BudgetExhaustionReason.MAX_VISITED_STATES,
        )
    if result.verdict is SearchVerdict.SOLVED:
        return BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "baseline_search", result.verdict.value, result.reason)
    if result.verdict is SearchVerdict.PROVEN_UNSOLVABLE:
        return BudgetedSolverResult(SolverOutcomeDisposition.PROVEN_UNSOLVABLE, budget, "baseline_search", result.verdict.value, result.reason)
    exhaustion = None
    reason_lower = result.reason.lower()
    if "depth" in reason_lower:
        exhaustion = BudgetExhaustionReason.MAX_DEPTH
    elif "unknown_bound" in reason_lower:
        exhaustion = BudgetExhaustionReason.UNKNOWN_BOUND
    return BudgetedSolverResult(
        SolverOutcomeDisposition.INCONCLUSIVE,
        budget,
        "baseline_search",
        result.verdict.value if result.verdict is not None else result.execution.value,
        result.reason,
        exhaustion,
    )


def classify_solution_count_result(
    result: SolutionCountResult,
    policy: SolverBudgetPolicy | None = None,
) -> BudgetedSolverResult:
    budget = policy or (SolverBudgetPolicy.from_solution_bounds(result.bounds) if isinstance(result, SolutionCountResult) else SolverBudgetPolicy())
    if not isinstance(result, SolutionCountResult):
        return BudgetedSolverResult(SolverOutcomeDisposition.ERROR, budget, "solution_count", "MALFORMED", "solution-count result is malformed")
    if result.disposition is SolutionCountDisposition.UNAVAILABLE:
        return BudgetedSolverResult(SolverOutcomeDisposition.UNAVAILABLE, budget, "solution_count", result.disposition.value, result.reason)
    if result.disposition is SolutionCountDisposition.ERROR:
        return BudgetedSolverResult(SolverOutcomeDisposition.ERROR, budget, "solution_count", result.disposition.value, result.reason)
    if result.disposition is SolutionCountDisposition.EXACT and result.solution_count == 0:
        return BudgetedSolverResult(SolverOutcomeDisposition.PROVEN_UNSOLVABLE, budget, "solution_count", result.disposition.value, result.reason)
    if result.disposition is SolutionCountDisposition.EXACT and result.solution_count is not None and result.solution_count > 0:
        return BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, budget, "solution_count", result.disposition.value, result.reason)
    exhaustion = None
    reason_lower = result.reason.lower()
    if result.disposition is SolutionCountDisposition.LOWER_BOUND:
        exhaustion = BudgetExhaustionReason.MAX_SOLUTIONS
    elif "state" in reason_lower:
        exhaustion = BudgetExhaustionReason.MAX_VISITED_STATES
    elif "depth" in reason_lower:
        exhaustion = BudgetExhaustionReason.MAX_DEPTH
    elif "unknown_bound" in reason_lower:
        exhaustion = BudgetExhaustionReason.UNKNOWN_BOUND
    return BudgetedSolverResult(SolverOutcomeDisposition.INCONCLUSIVE, budget, "solution_count", result.disposition.value, result.reason, exhaustion)


__all__ = [
    "BudgetExhaustionReason",
    "BudgetedSolverResult",
    "OperationalExecutionDisposition",
    "OperationalSolverOutcome",
    "OperationalTimeoutTelemetry",
    "OPERATIONAL_TIMEOUT_POLICY_VERSION",
    "SOLVER_BUDGET_SCHEMA",
    "SOLVER_BUDGET_VERSION",
    "SOLVER_OUTCOME_SCHEMA",
    "SOLVER_OUTCOME_VERSION",
    "SolverBudgetError",
    "SolverBudgetPolicy",
    "SolverOutcomeDisposition",
    "classify_search_result",
    "classify_solution_count_result",
    "wrap_operational_execution",
]
