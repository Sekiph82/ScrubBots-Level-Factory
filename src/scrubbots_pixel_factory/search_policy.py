"""Versioned, deterministic, provider-only search ordering and pruning policy."""

from __future__ import annotations

from dataclasses import dataclass

from .legal_move_provider import LegalMove


SEARCH_POLICY_SCHEMA = "scrubbots-search-optimization-policy"
SEARCH_POLICY_VERSION = 1
PROVIDER_ORDER_V1 = "PROVIDER_ORDER_V1"
REVERSE_PROVIDER_ORDER_V1 = "REVERSE_PROVIDER_ORDER_V1"
NONE_PRUNING_V1 = "NONE_V1"


class SearchPolicyError(ValueError):
    """Raised when a search-policy contract value is malformed."""


@dataclass(frozen=True, slots=True)
class MoveOrderingPolicy:
    """Stable ordering over provider-produced moves; it does not derive moves."""

    version: str = PROVIDER_ORDER_V1

    def __post_init__(self) -> None:
        if type(self.version) is not str or self.version not in {PROVIDER_ORDER_V1, REVERSE_PROVIDER_ORDER_V1}:
            raise SearchPolicyError("unsupported move-ordering policy")

    def order(self, moves: tuple[LegalMove, ...]) -> tuple[LegalMove, ...]:
        if not isinstance(moves, tuple) or any(not isinstance(move, LegalMove) for move in moves):
            raise SearchPolicyError("ordering requires an immutable LegalMove tuple")
        if self.version == REVERSE_PROVIDER_ORDER_V1:
            return tuple(reversed(moves))
        return moves

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": SEARCH_POLICY_SCHEMA, "version": SEARCH_POLICY_VERSION, "kind": "ordering", "policy": self.version}


@dataclass(frozen=True, slots=True)
class PruningPolicy:
    """Explicit proof-safe control; no heuristic pruning is available in this contract."""

    version: str = NONE_PRUNING_V1

    def __post_init__(self) -> None:
        if type(self.version) is not str or self.version != NONE_PRUNING_V1:
            raise SearchPolicyError("unsupported pruning policy")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": SEARCH_POLICY_SCHEMA, "version": SEARCH_POLICY_VERSION, "kind": "pruning", "policy": self.version}


@dataclass(frozen=True, slots=True)
class SearchPolicy:
    """Opt-in ordering/pruning selection recorded with solver evidence."""

    ordering: MoveOrderingPolicy = MoveOrderingPolicy()
    pruning: PruningPolicy = PruningPolicy()

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": SEARCH_POLICY_SCHEMA,
            "version": SEARCH_POLICY_VERSION,
            "ordering": self.ordering.canonical_dict(),
            "pruning": self.pruning.canonical_dict(),
        }

    def order_moves(self, moves: tuple[LegalMove, ...]) -> tuple[LegalMove, ...]:
        return self.ordering.order(moves)


BASELINE_SEARCH_POLICY = SearchPolicy()
REVERSE_SEARCH_POLICY = SearchPolicy(MoveOrderingPolicy(REVERSE_PROVIDER_ORDER_V1))
OrderingPolicy = MoveOrderingPolicy
SearchOptimizationPolicy = SearchPolicy


__all__ = [
    "BASELINE_SEARCH_POLICY",
    "NONE_PRUNING_V1",
    "MoveOrderingPolicy",
    "OrderingPolicy",
    "PROVIDER_ORDER_V1",
    "PruningPolicy",
    "REVERSE_PROVIDER_ORDER_V1",
    "REVERSE_SEARCH_POLICY",
    "SEARCH_POLICY_SCHEMA",
    "SEARCH_POLICY_VERSION",
    "SearchOptimizationPolicy",
    "SearchPolicy",
    "SearchPolicyError",
]
