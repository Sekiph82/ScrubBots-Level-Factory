"""Deterministic generic search orchestration for canonical provider boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .compact_solver_state import CompactSolverState
from .legal_move_provider import LegalMove, LegalMoveProvider, LegalMoveProviderError, LegalMoveQuery, ProviderDisposition


BASELINE_SEARCH_SCHEMA = "scrubbots-baseline-search"
BASELINE_SEARCH_VERSION = 1
BASELINE_SEARCH_POLICY = "DFS_CANONICAL_PROVIDER_ORDER_V1"


class SearchExecutionDisposition(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class SearchVerdict(str, Enum):
    SOLVED = "SOLVED"
    PROVEN_UNSOLVABLE = "PROVEN_UNSOLVABLE"
    INCONCLUSIVE = "INCONCLUSIVE"


class TerminalTruth(str, Enum):
    CONTINUE = "CONTINUE"
    SOLVED = "SOLVED"
    PROVEN_UNSOLVABLE = "PROVEN_UNSOLVABLE"
    UNKNOWN_BOUND = "UNKNOWN_BOUND"


class SearchContractError(ValueError):
    """Raised when a search boundary value is malformed."""


@dataclass(frozen=True, slots=True)
class BaselineSearchPolicy:
    algorithm_version: str = BASELINE_SEARCH_POLICY
    max_depth: int = 64

    def __post_init__(self) -> None:
        if type(self.algorithm_version) is not str or self.algorithm_version != BASELINE_SEARCH_POLICY:
            raise SearchContractError("unsupported baseline search policy")
        if type(self.max_depth) is not int or isinstance(self.max_depth, bool) or self.max_depth < 0:
            raise SearchContractError("max depth must be a non-negative exact integer")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": BASELINE_SEARCH_SCHEMA, "version": BASELINE_SEARCH_VERSION, "algorithm_version": self.algorithm_version, "max_depth": self.max_depth}


@dataclass(frozen=True, slots=True)
class TerminalObservation:
    disposition: SearchExecutionDisposition
    truth: TerminalTruth | None
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, SearchExecutionDisposition):
            raise SearchContractError("terminal disposition is malformed")
        if self.disposition is SearchExecutionDisposition.AVAILABLE and not isinstance(self.truth, TerminalTruth):
            raise SearchContractError("AVAILABLE terminal observation requires provider truth")
        if self.disposition is not SearchExecutionDisposition.AVAILABLE and self.truth is not None:
            raise SearchContractError("unavailable/error terminal observation cannot carry truth")
        if type(self.reason) is not str or not self.reason.strip():
            raise SearchContractError("terminal reason is required")


@dataclass(frozen=True, slots=True)
class TransitionObservation:
    disposition: SearchExecutionDisposition
    state: CompactSolverState | None
    terminal: TerminalTruth | None
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, SearchExecutionDisposition):
            raise SearchContractError("transition disposition is malformed")
        if self.disposition is SearchExecutionDisposition.AVAILABLE and self.state is None:
            raise SearchContractError("AVAILABLE transition requires a child state")
        if self.disposition is not SearchExecutionDisposition.AVAILABLE and self.state is not None:
            raise SearchContractError("unavailable/error transition cannot carry a child state")
        if type(self.reason) is not str or not self.reason.strip():
            raise SearchContractError("transition reason is required")


class SearchTransitionProvider(Protocol):
    def terminal(self, state: CompactSolverState) -> TerminalObservation:
        ...

    def transition(self, state: CompactSolverState, move: LegalMove) -> TransitionObservation:
        ...


@dataclass(frozen=True, slots=True)
class BaselineSearchResult:
    execution: SearchExecutionDisposition
    verdict: SearchVerdict | None
    path: tuple[LegalMove, ...]
    reason: str
    policy: BaselineSearchPolicy

    def __post_init__(self) -> None:
        if not isinstance(self.execution, SearchExecutionDisposition):
            raise SearchContractError("search execution disposition is malformed")
        if self.execution is SearchExecutionDisposition.AVAILABLE and not isinstance(self.verdict, SearchVerdict):
            raise SearchContractError("AVAILABLE search requires a provider/search verdict")
        if self.execution is not SearchExecutionDisposition.AVAILABLE and self.verdict is not None:
            raise SearchContractError("unavailable/error search cannot carry a verdict")
        if not isinstance(self.path, tuple) or any(not isinstance(move, LegalMove) for move in self.path):
            raise SearchContractError("search path must be an immutable LegalMove tuple")
        if type(self.reason) is not str or not self.reason.strip():
            raise SearchContractError("search reason is required")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": BASELINE_SEARCH_SCHEMA,
            "version": BASELINE_SEARCH_VERSION,
            "execution": self.execution.value,
            "verdict": self.verdict.value if self.verdict is not None else None,
            "path": [move.canonical_dict() for move in self.path],
            "reason": self.reason,
            "policy": self.policy.canonical_dict(),
        }


class BaselineSearchEngine:
    """DFS orchestration that never interprets gameplay state itself."""

    def __init__(self, legal_provider: LegalMoveProvider, transition_provider: SearchTransitionProvider, policy: BaselineSearchPolicy | None = None) -> None:
        self._legal_provider = legal_provider
        self._transition_provider = transition_provider
        self._policy = policy or BaselineSearchPolicy()

    def search(self, initial_state: CompactSolverState) -> BaselineSearchResult:
        if not isinstance(initial_state, CompactSolverState):
            return BaselineSearchResult(SearchExecutionDisposition.ERROR, None, (), "initial state is malformed", self._policy)
        path: list[LegalMove] = []
        return self._visit(initial_state, path, 0)

    def _visit(self, state: CompactSolverState, path: list[LegalMove], depth: int) -> BaselineSearchResult:
        if depth > self._policy.max_depth:
            return BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.INCONCLUSIVE, tuple(path), "deterministic depth bound exhausted", self._policy)
        try:
            terminal = self._transition_provider.terminal(state)
        except Exception as exc:
            return BaselineSearchResult(SearchExecutionDisposition.ERROR, None, tuple(path), f"terminal provider error: {type(exc).__name__}", self._policy)
        if terminal.disposition is SearchExecutionDisposition.UNAVAILABLE:
            return BaselineSearchResult(SearchExecutionDisposition.UNAVAILABLE, None, tuple(path), terminal.reason, self._policy)
        if terminal.disposition is SearchExecutionDisposition.ERROR:
            return BaselineSearchResult(SearchExecutionDisposition.ERROR, None, tuple(path), terminal.reason, self._policy)
        if terminal.truth is TerminalTruth.SOLVED:
            return BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, tuple(path), terminal.reason, self._policy)
        if terminal.truth is TerminalTruth.PROVEN_UNSOLVABLE:
            return BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.PROVEN_UNSOLVABLE, tuple(path), terminal.reason, self._policy)
        try:
            request = LegalMoveQuery(state, state.digest(), state.authority, self._legal_provider.provider_id, self._legal_provider.provider_version)
            moves = self._legal_provider.query(request)
        except Exception as exc:
            return BaselineSearchResult(SearchExecutionDisposition.ERROR, None, tuple(path), f"legal provider error: {type(exc).__name__}", self._policy)
        if moves.disposition is ProviderDisposition.UNAVAILABLE:
            return BaselineSearchResult(SearchExecutionDisposition.UNAVAILABLE, None, tuple(path), moves.reason, self._policy)
        if moves.disposition is ProviderDisposition.ERROR:
            return BaselineSearchResult(SearchExecutionDisposition.ERROR, None, tuple(path), moves.reason, self._policy)
        if not moves.moves:
            if terminal.truth is TerminalTruth.UNKNOWN_BOUND:
                return BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.INCONCLUSIVE, tuple(path), "provider reported UNKNOWN_BOUND at a zero-move node", self._policy)
            return BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.INCONCLUSIVE, tuple(path), "provider reported CONTINUE with zero legal moves", self._policy)

        saw_inconclusive = False
        for move in moves.moves:
            try:
                transition = self._transition_provider.transition(state, move)
            except Exception as exc:
                return BaselineSearchResult(SearchExecutionDisposition.ERROR, None, tuple(path), f"transition provider error: {type(exc).__name__}", self._policy)
            if transition.disposition is SearchExecutionDisposition.UNAVAILABLE:
                return BaselineSearchResult(SearchExecutionDisposition.UNAVAILABLE, None, tuple(path), transition.reason, self._policy)
            if transition.disposition is SearchExecutionDisposition.ERROR:
                return BaselineSearchResult(SearchExecutionDisposition.ERROR, None, tuple(path), transition.reason, self._policy)
            next_path = [*path, move]
            child = self._visit(transition.state, next_path, depth + 1)
            if child.execution is not SearchExecutionDisposition.AVAILABLE:
                return child
            if child.verdict is SearchVerdict.SOLVED:
                return child
            if child.verdict is SearchVerdict.INCONCLUSIVE:
                saw_inconclusive = True
        if saw_inconclusive:
            return BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.INCONCLUSIVE, tuple(path), "one or more branches were inconclusive", self._policy)
        return BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.PROVEN_UNSOLVABLE, tuple(path), "all provider branches proved unsolvable", self._policy)


__all__ = [
    "BASELINE_SEARCH_POLICY",
    "BASELINE_SEARCH_SCHEMA",
    "BASELINE_SEARCH_VERSION",
    "BaselineSearchEngine",
    "BaselineSearchPolicy",
    "BaselineSearchResult",
    "SearchContractError",
    "SearchExecutionDisposition",
    "SearchTransitionProvider",
    "SearchVerdict",
    "TerminalObservation",
    "TerminalTruth",
    "TransitionObservation",
]
