"""Canonical legal-move transport contracts for the LF03 solver boundary.

This module transports decisions returned by a verified canonical provider. It
does not derive legal moves, apply moves, or implement gameplay semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
from typing import Mapping, Protocol, Sequence

from .compact_solver_state import (
    AUTHORITY_CONTRACT_VERSION,
    AuthorityVerificationDisposition,
    CompactSolverState,
    CompactStateContractError,
    SolverStateAuthority,
    verify_authority_checkout,
    verify_authority_source_contract,
)


LEGAL_MOVE_PROVIDER_SCHEMA = "scrubbots-legal-move-provider"
LEGAL_MOVE_PROVIDER_VERSION = 1
LEGAL_MOVE_QUERY_SCHEMA = "scrubbots-legal-move-query"
LEGAL_MOVE_RESULT_SCHEMA = "scrubbots-legal-move-result"
LEGAL_MOVE_KIND = "CANONICAL_COLUMN_FRONT_V1"
CANONICAL_PROVIDER_ID = "scrubbots-canonical-gameplay"
CANONICAL_PROVIDER_VERSION = "canonical-headless-provider-v1"


class LegalMoveProviderError(ValueError):
    """Raised when a legal-move boundary value is malformed."""


class ProviderDisposition(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


def _canonical_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: Mapping[str, object]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise LegalMoveProviderError(f"{label} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class ProviderEvidence:
    """Capability evidence required before a provider can be AVAILABLE."""

    provider_id: str
    provider_version: str
    authority: SolverStateAuthority
    disposition: ProviderDisposition
    authority_verification: AuthorityVerificationDisposition
    source_contract_verification: AuthorityVerificationDisposition
    execution_mode: str
    reason: str

    def __post_init__(self) -> None:
        provider_id = _text(self.provider_id, "provider id")
        provider_version = _text(self.provider_version, "provider version")
        execution_mode = _text(self.execution_mode, "execution mode")
        reason = _text(self.reason, "provider evidence reason")
        if not isinstance(self.authority, SolverStateAuthority):
            raise LegalMoveProviderError("provider authority is malformed")
        if not isinstance(self.disposition, ProviderDisposition):
            raise LegalMoveProviderError("provider disposition is malformed")
        if not isinstance(self.authority_verification, AuthorityVerificationDisposition):
            raise LegalMoveProviderError("authority verification is malformed")
        if not isinstance(self.source_contract_verification, AuthorityVerificationDisposition):
            raise LegalMoveProviderError("source contract verification is malformed")
        if self.disposition is ProviderDisposition.AVAILABLE and (
            self.authority_verification is not AuthorityVerificationDisposition.VERIFIED
            or self.source_contract_verification is not AuthorityVerificationDisposition.VERIFIED
            or execution_mode != "CANONICAL_RUNTIME"
        ):
            raise LegalMoveProviderError("AVAILABLE requires verified authority, source contract, and canonical runtime")
        object.__setattr__(self, "provider_id", provider_id)
        object.__setattr__(self, "provider_version", provider_version)
        object.__setattr__(self, "execution_mode", execution_mode)
        object.__setattr__(self, "reason", reason[:512])

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": LEGAL_MOVE_PROVIDER_SCHEMA,
            "version": LEGAL_MOVE_PROVIDER_VERSION,
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "authority": self.authority.canonical_dict(),
            "disposition": self.disposition.value,
            "authority_verification": self.authority_verification.value,
            "source_contract_verification": self.source_contract_verification.value,
            "execution_mode": self.execution_mode,
            "reason": self.reason,
        }

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class LegalMoveQuery:
    """Immutable query bound to one compact state digest and authority."""

    state: CompactSolverState
    state_digest: str
    authority: SolverStateAuthority
    provider_id: str
    provider_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.state, CompactSolverState):
            raise LegalMoveProviderError("legal-move query state is malformed")
        state_digest = _text(self.state_digest, "state digest")
        if state_digest != self.state.digest():
            raise LegalMoveProviderError("legal-move query state digest does not match state")
        if self.authority != self.state.authority:
            raise LegalMoveProviderError("legal-move query authority does not match state authority")
        provider_id = _text(self.provider_id, "query provider id")
        provider_version = _text(self.provider_version, "query provider version")
        object.__setattr__(self, "state_digest", state_digest)
        object.__setattr__(self, "provider_id", provider_id)
        object.__setattr__(self, "provider_version", provider_version)

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": LEGAL_MOVE_QUERY_SCHEMA,
            "version": LEGAL_MOVE_PROVIDER_VERSION,
            "state_digest": self.state_digest,
            "authority": self.authority.canonical_dict(),
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
        }

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class LegalMove:
    """Narrow canonical player decision: select a supply column/front."""

    column: int
    kind: str = LEGAL_MOVE_KIND

    def __post_init__(self) -> None:
        if type(self.column) is not int or self.column < 0:
            raise LegalMoveProviderError("legal move column must be a non-negative exact integer")
        if self.kind != LEGAL_MOVE_KIND:
            raise LegalMoveProviderError("legal move kind is unsupported")

    def canonical_dict(self) -> dict[str, object]:
        return {"kind": self.kind, "column": self.column}


@dataclass(frozen=True, slots=True)
class LegalMoveResult:
    """Immutable provider result; zero AVAILABLE moves carry no solver verdict."""

    disposition: ProviderDisposition
    query_digest: str
    state_digest: str
    authority: SolverStateAuthority
    provider_id: str
    provider_version: str
    capability: ProviderEvidence
    moves: tuple[LegalMove, ...]
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, ProviderDisposition):
            raise LegalMoveProviderError("legal-move result disposition is malformed")
        query_digest = _text(self.query_digest, "query digest")
        state_digest = _text(self.state_digest, "result state digest")
        if not isinstance(self.authority, SolverStateAuthority) or self.authority != self.capability.authority:
            raise LegalMoveProviderError("result authority does not match capability")
        if self.provider_id != self.capability.provider_id or self.provider_version != self.capability.provider_version:
            raise LegalMoveProviderError("result provider identity does not match capability")
        if not isinstance(self.moves, tuple) or any(not isinstance(move, LegalMove) for move in self.moves):
            raise LegalMoveProviderError("result moves must be an immutable LegalMove tuple")
        columns = [move.column for move in self.moves]
        if len(columns) != len(set(columns)):
            raise LegalMoveProviderError("duplicate legal moves are not allowed")
        if columns != sorted(columns):
            raise LegalMoveProviderError("canonical legal move ordering must be ascending")
        if self.disposition is ProviderDisposition.AVAILABLE:
            if self.capability.disposition is not ProviderDisposition.AVAILABLE:
                raise LegalMoveProviderError("AVAILABLE result requires AVAILABLE capability")
        elif self.moves:
            raise LegalMoveProviderError("UNAVAILABLE/ERROR results cannot carry moves")
        object.__setattr__(self, "query_digest", query_digest)
        object.__setattr__(self, "state_digest", state_digest)
        object.__setattr__(self, "reason", _text(self.reason, "result reason")[:512])

    @classmethod
    def from_query(
        cls,
        query: LegalMoveQuery,
        disposition: ProviderDisposition,
        capability: ProviderEvidence,
        moves: Sequence[LegalMove] = (),
        reason: str = "provider returned no legal moves",
    ) -> "LegalMoveResult":
        prepared = tuple(moves)
        if any(move.column >= query.state.column_count for move in prepared):
            raise LegalMoveProviderError("legal move column is outside the compact state column count")
        return cls(
            disposition=disposition,
            query_digest=query.digest(),
            state_digest=query.state_digest,
            authority=query.authority,
            provider_id=query.provider_id,
            provider_version=query.provider_version,
            capability=capability,
            moves=prepared,
            reason=reason,
        )

    def validate_for_query(self, query: LegalMoveQuery) -> None:
        """Fail closed unless this result answers the exact supplied query."""
        if not isinstance(query, LegalMoveQuery):
            raise LegalMoveProviderError("legal-move validation query is malformed")
        if self.query_digest != query.digest() or self.state_digest != query.state_digest:
            raise LegalMoveProviderError("legal-move result is bound to a different query or state")
        if self.authority != query.authority or self.provider_id != query.provider_id or self.provider_version != query.provider_version:
            raise LegalMoveProviderError("legal-move result authority or provider identity mismatch")
        capability = self.capability
        if capability.authority != query.authority or capability.provider_id != query.provider_id or capability.provider_version != query.provider_version:
            raise LegalMoveProviderError("legal-move capability identity mismatch")
        if capability.disposition is not self.disposition:
            raise LegalMoveProviderError("legal-move disposition does not match capability")
        if self.disposition is ProviderDisposition.AVAILABLE:
            if capability.authority_verification is not AuthorityVerificationDisposition.VERIFIED or capability.source_contract_verification is not AuthorityVerificationDisposition.VERIFIED or capability.execution_mode != "CANONICAL_RUNTIME":
                raise LegalMoveProviderError("AVAILABLE legal-move evidence is not verified canonical runtime evidence")
        if any(move.column >= query.state.column_count for move in self.moves):
            raise LegalMoveProviderError("legal-move result contains a column outside the queried state")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": LEGAL_MOVE_RESULT_SCHEMA,
            "version": LEGAL_MOVE_PROVIDER_VERSION,
            "disposition": self.disposition.value,
            "query_digest": self.query_digest,
            "state_digest": self.state_digest,
            "authority": self.authority.canonical_dict(),
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "capability": self.capability.canonical_dict(),
            "moves": [move.canonical_dict() for move in self.moves],
            "reason": self.reason,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())


class LegalMoveProvider(Protocol):
    provider_id: str
    provider_version: str

    def capability(self, state: CompactSolverState) -> ProviderEvidence:
        ...

    def query(self, request: LegalMoveQuery) -> LegalMoveResult:
        ...


class CanonicalLegalMoveProvider:
    """Truthful production boundary; no stable canonical execution is assumed."""

    provider_id = CANONICAL_PROVIDER_ID
    provider_version = CANONICAL_PROVIDER_VERSION

    def __init__(self, checkout_path: str | os.PathLike[str] | None = None) -> None:
        self._checkout_path = os.fspath(checkout_path) if checkout_path is not None else None

    def capability(self, state: CompactSolverState) -> ProviderEvidence:
        if not isinstance(state, CompactSolverState):
            return ProviderEvidence(self.provider_id, self.provider_version, _fallback_authority(), ProviderDisposition.ERROR, AuthorityVerificationDisposition.ERROR, AuthorityVerificationDisposition.ERROR, "NOT_CONFIGURED", "compact solver state is malformed")
        authority = state.authority
        if self._checkout_path is None:
            return ProviderEvidence(self.provider_id, self.provider_version, authority, ProviderDisposition.UNAVAILABLE, AuthorityVerificationDisposition.UNAVAILABLE, AuthorityVerificationDisposition.UNAVAILABLE, "NOT_CONFIGURED", "canonical gameplay checkout is not configured")
        verified = verify_authority_checkout(authority, self._checkout_path)
        source_status = AuthorityVerificationDisposition.UNAVAILABLE
        if verified.disposition is AuthorityVerificationDisposition.VERIFIED:
            try:
                source = (Path(self._checkout_path) / authority.proof_state_source_path).read_bytes()
                source_status = verify_authority_source_contract(authority, source).disposition
            except OSError:
                source_status = AuthorityVerificationDisposition.ERROR
        return ProviderEvidence(self.provider_id, self.provider_version, authority, ProviderDisposition.UNAVAILABLE, verified.disposition, source_status, "VERIFIED_BUT_NO_EXECUTOR", "canonical source is verified but no stable headless gameplay executor is configured")

    def query(self, request: LegalMoveQuery) -> LegalMoveResult:
        capability = self.capability(request.state)
        if capability.authority != request.authority or capability.provider_id != request.provider_id or capability.provider_version != request.provider_version:
            raise LegalMoveProviderError("query provider or authority identity does not match canonical capability")
        return LegalMoveResult.from_query(request, ProviderDisposition.UNAVAILABLE, capability, reason=capability.reason)


def _fallback_authority() -> SolverStateAuthority:
    from .compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA

    return SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)


__all__ = [
    "CANONICAL_PROVIDER_ID",
    "CANONICAL_PROVIDER_VERSION",
    "LEGAL_MOVE_KIND",
    "LEGAL_MOVE_PROVIDER_SCHEMA",
    "LEGAL_MOVE_PROVIDER_VERSION",
    "CanonicalLegalMoveProvider",
    "LegalMove",
    "LegalMoveProvider",
    "LegalMoveProviderError",
    "LegalMoveQuery",
    "LegalMoveResult",
    "ProviderDisposition",
    "ProviderEvidence",
]
