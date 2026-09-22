"""Deterministic search evidence with separate non-canonical timing telemetry."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import time

from .baseline_search import BaselineSearchEngine, BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition
from .compact_solver_state import CompactSolverState
from .legal_move_provider import LegalMoveProvider
from .visited_memoization import CanonicalStateKeyProvider, DeterministicVisitedMemo, MemoDisposition


SOLVER_EVIDENCE_SCHEMA = "scrubbots-solver-evidence"
SOLVER_EVIDENCE_VERSION = 1
MAX_STATE_REFERENCES = 256


def _canonical_bytes(value: dict[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True, slots=True)
class SolverMetrics:
    state_references: tuple[str, ...]
    state_reference_truncated: bool
    visited_count: int
    memo_hits: int | None
    dead_end_count: int
    maximum_depth: int
    branch_counts: tuple[int, ...]
    frontier_peak: int
    path: tuple[dict[str, object], ...]

    def canonical_dict(self) -> dict[str, object]:
        return {
            "state_references": list(self.state_references),
            "state_reference_truncated": self.state_reference_truncated,
            "visited_count": self.visited_count,
            "memo_hits": self.memo_hits,
            "dead_end_count": self.dead_end_count,
            "maximum_depth": self.maximum_depth,
            "branch_counts": list(self.branch_counts),
            "frontier_peak": self.frontier_peak,
            "path": list(self.path),
        }


@dataclass(frozen=True, slots=True)
class SolverEvidenceReport:
    execution: SearchExecutionDisposition
    result: BaselineSearchResult
    metrics: SolverMetrics | None
    elapsed_seconds: float

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": SOLVER_EVIDENCE_SCHEMA,
            "version": SOLVER_EVIDENCE_VERSION,
            "execution": self.execution.value,
            "result": self.result.canonical_dict(),
            "metrics": self.metrics.canonical_dict() if self.metrics is not None else None,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def telemetry_dict(self) -> dict[str, object]:
        return {"schema": SOLVER_EVIDENCE_SCHEMA, "version": SOLVER_EVIDENCE_VERSION, "elapsed_seconds": self.elapsed_seconds, "canonical": False}


class _EvidenceCollector:
    def __init__(self, key_provider: CanonicalStateKeyProvider | None, memo: DeterministicVisitedMemo | None) -> None:
        self.key_provider = key_provider
        self.memo = memo
        self.state_references: list[str] = []
        self.state_reference_truncated = False
        self.visited_count = 0
        self.memo_hits: int | None = 0 if memo is not None else None
        self.dead_end_count = 0
        self.maximum_depth = 0
        self.branch_counts: list[int] = []
        self.frontier_peak = 0

    def on_node(self, state: CompactSolverState, depth: int) -> None:
        self.visited_count += 1
        self.maximum_depth = max(self.maximum_depth, depth)
        self.frontier_peak = max(self.frontier_peak, depth + 1)
        if len(self.state_references) < MAX_STATE_REFERENCES:
            self.state_references.append(state.digest())
        else:
            self.state_reference_truncated = True
        if self.key_provider is not None and self.memo is not None:
            try:
                observation = self.memo.observe(self.key_provider.key(state))
                if observation.disposition is MemoDisposition.MEMO_HIT:
                    self.memo_hits = observation.memo_hits
                elif observation.disposition in {MemoDisposition.UNAVAILABLE, MemoDisposition.ERROR}:
                    self.memo_hits = None
            except Exception:
                self.memo_hits = None

    def on_branch(self, count: int, _depth: int) -> None:
        self.branch_counts.append(count)

    def on_terminal(self, terminal: object) -> None:
        truth = getattr(terminal, "truth", None)
        if truth is not None and getattr(truth, "value", None) == "PROVEN_UNSOLVABLE":
            self.dead_end_count += 1

    def on_dead_end(self, _state: CompactSolverState, _depth: int) -> None:
        self.dead_end_count += 1

    def metrics(self, result: BaselineSearchResult) -> SolverMetrics:
        return SolverMetrics(
            tuple(self.state_references),
            self.state_reference_truncated,
            self.visited_count,
            self.memo_hits,
            self.dead_end_count,
            self.maximum_depth,
            tuple(self.branch_counts),
            self.frontier_peak,
            tuple(move.canonical_dict() for move in result.path),
        )


class EvidenceSearchEngine:
    """Run accepted baseline search and collect only observed evidence."""

    def __init__(self, legal_provider: LegalMoveProvider, transition_provider: object, policy: BaselineSearchPolicy | None = None, key_provider: CanonicalStateKeyProvider | None = None) -> None:
        self._engine = BaselineSearchEngine(legal_provider, transition_provider, policy)
        self._key_provider = key_provider
        self._legal_provider = legal_provider

    def search(self, initial_state: CompactSolverState) -> SolverEvidenceReport:
        memo = None
        if self._key_provider is not None:
            memo = DeterministicVisitedMemo(initial_state.authority, self._key_provider.provider_id, self._key_provider.provider_version)
        collector = _EvidenceCollector(self._key_provider, memo)
        started = time.monotonic()
        result = self._engine.search(initial_state, observer=collector)
        elapsed = max(0.0, time.monotonic() - started)
        metrics = collector.metrics(result) if result.execution is SearchExecutionDisposition.AVAILABLE else None
        return SolverEvidenceReport(result.execution, result, metrics, elapsed)


__all__ = [
    "MAX_STATE_REFERENCES",
    "SOLVER_EVIDENCE_SCHEMA",
    "SOLVER_EVIDENCE_VERSION",
    "EvidenceSearchEngine",
    "SolverEvidenceReport",
    "SolverMetrics",
]
