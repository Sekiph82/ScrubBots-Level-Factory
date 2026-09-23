"""Bounded, provider-only solution-count and entropy evidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math

from .baseline_search import SearchExecutionDisposition, SearchTransitionProvider, TerminalTruth
from .compact_solver_state import CompactSolverState
from .legal_move_provider import LegalMove, LegalMoveProvider, LegalMoveQuery, ProviderDisposition
from .search_policy import BASELINE_SEARCH_POLICY, SearchPolicy


SOLUTION_ANALYSIS_SCHEMA = "scrubbots-solution-analysis"
SOLUTION_ANALYSIS_VERSION = 1
MOVE_SEQUENCE_EQUIVALENCE_V1 = "MOVE_SEQUENCE_V1"
ENTROPY_ANALYSIS_VERSION = "LOG2_COUNT_V1"


class SolutionAnalysisError(ValueError):
    """Raised when a bounded solution-analysis contract is malformed."""


class SolutionCountDisposition(str, Enum):
    EXACT = "EXACT"
    LOWER_BOUND = "LOWER_BOUND"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class EntropyDisposition(str, Enum):
    EXACT = "EXACT"
    LOWER_BOUND = "LOWER_BOUND"
    ZERO = "ZERO"
    NONE = "NONE"


@dataclass(frozen=True, slots=True)
class SolutionAnalysisBounds:
    max_depth: int = 64
    max_states: int = 10000
    max_solutions: int = 100

    def __post_init__(self) -> None:
        for name, value in (("max_depth", self.max_depth), ("max_states", self.max_states), ("max_solutions", self.max_solutions)):
            if type(value) is not int or isinstance(value, bool) or value < (0 if name == "max_depth" else 1):
                raise SolutionAnalysisError(f"{name} must be a deterministic positive/non-negative integer")

    def canonical_dict(self) -> dict[str, object]:
        return {"max_depth": self.max_depth, "max_states": self.max_states, "max_solutions": self.max_solutions}


@dataclass(frozen=True, slots=True)
class SolutionCountResult:
    disposition: SolutionCountDisposition
    solution_count: int | None
    solution_sequences: tuple[tuple[dict[str, object], ...], ...]
    nodes_visited: int
    bounds: SolutionAnalysisBounds
    search_policy: SearchPolicy
    equivalence: str
    entropy: float | None
    entropy_disposition: EntropyDisposition
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, SolutionCountDisposition):
            raise SolutionAnalysisError("solution-count disposition is malformed")
        if self.solution_count is not None and (type(self.solution_count) is not int or self.solution_count < 0):
            raise SolutionAnalysisError("solution count is malformed")
        if type(self.nodes_visited) is not int or self.nodes_visited < 0:
            raise SolutionAnalysisError("visited state count is malformed")
        if self.disposition in {SolutionCountDisposition.UNAVAILABLE, SolutionCountDisposition.ERROR} and self.solution_count is not None:
            raise SolutionAnalysisError("unavailable/error result cannot carry a solution count")
        if self.equivalence != MOVE_SEQUENCE_EQUIVALENCE_V1:
            raise SolutionAnalysisError("unsupported solution equivalence")
        if not isinstance(self.entropy_disposition, EntropyDisposition):
            raise SolutionAnalysisError("entropy disposition is malformed")
        if type(self.reason) is not str or not self.reason.strip():
            raise SolutionAnalysisError("solution-analysis reason is required")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": SOLUTION_ANALYSIS_SCHEMA,
            "version": SOLUTION_ANALYSIS_VERSION,
            "disposition": self.disposition.value,
            "solution_count": self.solution_count,
            "solution_sequences": [[dict(move) for move in sequence] for sequence in self.solution_sequences],
            "nodes_visited": self.nodes_visited,
            "bounds": self.bounds.canonical_dict(),
            "search_policy": self.search_policy.canonical_dict(),
            "equivalence": self.equivalence,
            "entropy": self.entropy,
            "entropy_disposition": self.entropy_disposition.value,
            "entropy_version": ENTROPY_ANALYSIS_VERSION,
            "reason": self.reason,
        }

    def digest(self) -> str:
        encoded = json.dumps(self.canonical_dict(), ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class _VisitDisposition(str, Enum):
    COMPLETE = "COMPLETE"
    INCONCLUSIVE = "INCONCLUSIVE"
    LOWER_BOUND = "LOWER_BOUND"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class SolutionCountEngine:
    """Enumerate provider-defined legal move sequences under deterministic caps."""

    def __init__(self, legal_provider: LegalMoveProvider, transition_provider: SearchTransitionProvider, bounds: SolutionAnalysisBounds | None = None, search_policy: SearchPolicy | None = None) -> None:
        self._legal_provider = legal_provider
        self._transition_provider = transition_provider
        self._bounds = bounds or SolutionAnalysisBounds()
        self._search_policy = search_policy or BASELINE_SEARCH_POLICY

    def analyze(self, initial_state: CompactSolverState) -> SolutionCountResult:
        if not isinstance(initial_state, CompactSolverState):
            return self._result(SolutionCountDisposition.ERROR, None, (), 0, "initial state is malformed")
        sequences: list[tuple[dict[str, object], ...]] = []
        nodes_visited = 0
        inconclusive_reason = ""

        def visit(state: CompactSolverState, path: tuple[LegalMove, ...], depth: int) -> _VisitDisposition:
            nonlocal nodes_visited, inconclusive_reason
            if nodes_visited >= self._bounds.max_states:
                inconclusive_reason = "state bound exhausted before exhaustive enumeration"
                return _VisitDisposition.INCONCLUSIVE
            if depth > self._bounds.max_depth:
                inconclusive_reason = "depth bound exhausted before exhaustive enumeration"
                return _VisitDisposition.INCONCLUSIVE
            nodes_visited += 1
            try:
                terminal = self._transition_provider.terminal(state)
            except Exception as exc:
                inconclusive_reason = f"terminal provider error: {type(exc).__name__}"
                return _VisitDisposition.ERROR
            if terminal.disposition is SearchExecutionDisposition.UNAVAILABLE:
                inconclusive_reason = terminal.reason
                return _VisitDisposition.UNAVAILABLE
            if terminal.disposition is SearchExecutionDisposition.ERROR:
                inconclusive_reason = terminal.reason
                return _VisitDisposition.ERROR
            if terminal.truth is TerminalTruth.SOLVED:
                sequences.append(tuple(move.canonical_dict() for move in path))
                if len(sequences) >= self._bounds.max_solutions:
                    inconclusive_reason = "solution-count cap reached; observed count is a lower bound"
                    return _VisitDisposition.LOWER_BOUND
                return _VisitDisposition.COMPLETE
            if terminal.truth is TerminalTruth.PROVEN_UNSOLVABLE:
                return _VisitDisposition.COMPLETE
            try:
                request = LegalMoveQuery(state, state.digest(), state.authority, self._legal_provider.provider_id, self._legal_provider.provider_version)
                move_result = self._legal_provider.query(request)
                move_result.validate_for_query(request)
            except Exception as exc:
                inconclusive_reason = f"legal provider error: {type(exc).__name__}"
                return _VisitDisposition.ERROR
            if move_result.disposition is ProviderDisposition.UNAVAILABLE:
                inconclusive_reason = move_result.reason
                return _VisitDisposition.UNAVAILABLE
            if move_result.disposition is ProviderDisposition.ERROR:
                inconclusive_reason = move_result.reason
                return _VisitDisposition.ERROR
            if not move_result.moves:
                inconclusive_reason = "provider reported no moves without a proof terminal"
                return _VisitDisposition.INCONCLUSIVE
            saw_inconclusive = False
            for move in self._search_policy.order_moves(move_result.moves):
                try:
                    transition = self._transition_provider.transition(state, move)
                except Exception as exc:
                    inconclusive_reason = f"transition provider error: {type(exc).__name__}"
                    return _VisitDisposition.ERROR
                if transition.disposition is SearchExecutionDisposition.UNAVAILABLE:
                    inconclusive_reason = transition.reason
                    return _VisitDisposition.UNAVAILABLE
                if transition.disposition is SearchExecutionDisposition.ERROR:
                    inconclusive_reason = transition.reason
                    return _VisitDisposition.ERROR
                if not isinstance(transition.state, CompactSolverState) or transition.state.authority != state.authority:
                    inconclusive_reason = "transition child state authority or type mismatch"
                    return _VisitDisposition.ERROR
                child = visit(transition.state, (*path, move), depth + 1)
                if child in {_VisitDisposition.ERROR, _VisitDisposition.UNAVAILABLE, _VisitDisposition.LOWER_BOUND}:
                    return child
                if child is _VisitDisposition.INCONCLUSIVE:
                    saw_inconclusive = True
            return _VisitDisposition.INCONCLUSIVE if saw_inconclusive else _VisitDisposition.COMPLETE

        status = visit(initial_state, (), 0)
        if status is _VisitDisposition.LOWER_BOUND:
            return self._result(SolutionCountDisposition.LOWER_BOUND, len(sequences), tuple(sequences), nodes_visited, inconclusive_reason)
        if status is _VisitDisposition.INCONCLUSIVE:
            return self._result(SolutionCountDisposition.INCONCLUSIVE, len(sequences), tuple(sequences), nodes_visited, inconclusive_reason or "enumeration was inconclusive")
        if status is _VisitDisposition.UNAVAILABLE:
            return self._result(SolutionCountDisposition.UNAVAILABLE, None, (), nodes_visited, inconclusive_reason)
        if status is _VisitDisposition.ERROR:
            return self._result(SolutionCountDisposition.ERROR, None, (), nodes_visited, inconclusive_reason)
        return self._result(SolutionCountDisposition.EXACT, len(sequences), tuple(sequences), nodes_visited, "all reachable provider branches were exhaustively counted")

    def _result(self, disposition: SolutionCountDisposition, count: int | None, sequences: tuple[tuple[dict[str, object], ...], ...], nodes_visited: int, reason: str) -> SolutionCountResult:
        entropy = None
        entropy_disposition = EntropyDisposition.NONE
        if disposition is SolutionCountDisposition.EXACT and count == 0:
            entropy_disposition = EntropyDisposition.ZERO
        elif disposition is SolutionCountDisposition.EXACT and count is not None and count > 0:
            entropy = math.log2(count)
            entropy_disposition = EntropyDisposition.EXACT
        elif disposition is SolutionCountDisposition.LOWER_BOUND and count is not None and count > 0:
            entropy = math.log2(count)
            entropy_disposition = EntropyDisposition.LOWER_BOUND
        return SolutionCountResult(disposition, count, sequences, nodes_visited, self._bounds, self._search_policy, MOVE_SEQUENCE_EQUIVALENCE_V1, entropy, entropy_disposition, reason)


__all__ = [
    "ENTROPY_ANALYSIS_VERSION",
    "EntropyDisposition",
    "MOVE_SEQUENCE_EQUIVALENCE_V1",
    "SOLUTION_ANALYSIS_SCHEMA",
    "SOLUTION_ANALYSIS_VERSION",
    "SolutionAnalysisBounds",
    "SolutionAnalysisError",
    "SolutionCountDisposition",
    "SolutionCountEngine",
    "SolutionCountResult",
]
