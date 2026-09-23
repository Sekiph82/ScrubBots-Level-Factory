"""Opaque canonical state-key and deterministic visited-set contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Protocol

from .compact_solver_state import AuthorityVerificationDisposition, CompactSolverState, SolverStateAuthority


STATE_KEY_SCHEMA = "scrubbots-canonical-state-key"
STATE_KEY_VERSION = 1
MEMO_SCHEMA = "scrubbots-visited-memo"
MEMO_VERSION = 1
CANONICAL_KEY_PROVIDER_ID = "scrubbots-canonical-key"
CANONICAL_KEY_PROVIDER_VERSION = "canonical-key-provider-v1"
_OPAQUE_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_.:=-]{1,256}$")


class StateKeyDisposition(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class MemoDisposition(str, Enum):
    FIRST_VISIT = "FIRST_VISIT"
    MEMO_HIT = "MEMO_HIT"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class MemoizationContractError(ValueError):
    """Raised when canonical-key or visited-set evidence is malformed."""


@dataclass(frozen=True, slots=True)
class StateKeyEvidence:
    provider_id: str
    provider_version: str
    authority: SolverStateAuthority
    disposition: StateKeyDisposition
    authority_verification: AuthorityVerificationDisposition
    source_contract_verification: AuthorityVerificationDisposition
    reason: str

    def __post_init__(self) -> None:
        if type(self.provider_id) is not str or not self.provider_id.strip() or type(self.provider_version) is not str or not self.provider_version.strip():
            raise MemoizationContractError("key provider identity is malformed")
        if not isinstance(self.authority, SolverStateAuthority) or not isinstance(self.disposition, StateKeyDisposition):
            raise MemoizationContractError("key provider evidence identity is malformed")
        if not isinstance(self.authority_verification, AuthorityVerificationDisposition) or not isinstance(self.source_contract_verification, AuthorityVerificationDisposition):
            raise MemoizationContractError("key authority verification is malformed")
        if self.disposition is StateKeyDisposition.AVAILABLE and (
            self.authority_verification is not AuthorityVerificationDisposition.VERIFIED
            or self.source_contract_verification is not AuthorityVerificationDisposition.VERIFIED
        ):
            raise MemoizationContractError("AVAILABLE key evidence requires verified authority and source contract")
        if type(self.reason) is not str or not self.reason.strip():
            raise MemoizationContractError("key provider reason is required")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": STATE_KEY_SCHEMA,
            "version": STATE_KEY_VERSION,
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "authority": self.authority.canonical_dict(),
            "disposition": self.disposition.value,
            "authority_verification": self.authority_verification.value,
            "source_contract_verification": self.source_contract_verification.value,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class StateKeyResult:
    disposition: StateKeyDisposition
    state_digest: str
    authority: SolverStateAuthority
    provider_id: str
    provider_version: str
    evidence: StateKeyEvidence
    opaque_key: str | None
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, StateKeyDisposition) or not isinstance(self.authority, SolverStateAuthority):
            raise MemoizationContractError("state-key result identity is malformed")
        if type(self.state_digest) is not str or not re.fullmatch(r"[0-9a-f]{64}", self.state_digest):
            raise MemoizationContractError("state digest is malformed")
        if self.authority != self.evidence.authority or self.provider_id != self.evidence.provider_id or self.provider_version != self.evidence.provider_version:
            raise MemoizationContractError("state-key result does not match provider evidence")
        if self.disposition is StateKeyDisposition.AVAILABLE:
            if self.evidence.disposition is not StateKeyDisposition.AVAILABLE or type(self.opaque_key) is not str or _OPAQUE_KEY_PATTERN.fullmatch(self.opaque_key) is None:
                raise MemoizationContractError("AVAILABLE state-key result requires a bounded opaque key")
        elif self.opaque_key is not None:
            raise MemoizationContractError("UNAVAILABLE/ERROR state-key result cannot carry an opaque key")
        if type(self.reason) is not str or not self.reason.strip():
            raise MemoizationContractError("state-key result reason is required")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": STATE_KEY_SCHEMA,
            "version": STATE_KEY_VERSION,
            "disposition": self.disposition.value,
            "state_digest": self.state_digest,
            "authority": self.authority.canonical_dict(),
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "evidence": self.evidence.canonical_dict(),
            "opaque_key": self.opaque_key,
            "reason": self.reason,
        }

    def validate_for_state(self, state: CompactSolverState, provider_id: str, provider_version: str) -> None:
        if not isinstance(state, CompactSolverState):
            raise MemoizationContractError("key validation state is malformed")
        if self.state_digest != state.digest() or self.authority != state.authority:
            raise MemoizationContractError("canonical key result is bound to a different state")
        if self.provider_id != provider_id or self.provider_version != provider_version:
            raise MemoizationContractError("canonical key provider identity mismatch")
        if self.evidence.authority != state.authority or self.evidence.provider_id != provider_id or self.evidence.provider_version != provider_version:
            raise MemoizationContractError("canonical key evidence identity mismatch")
        if self.disposition is StateKeyDisposition.AVAILABLE and (self.evidence.disposition is not StateKeyDisposition.AVAILABLE or self.evidence.authority_verification is not AuthorityVerificationDisposition.VERIFIED or self.evidence.source_contract_verification is not AuthorityVerificationDisposition.VERIFIED):
            raise MemoizationContractError("canonical key evidence is not verified")


class CanonicalStateKeyProvider(Protocol):
    provider_id: str
    provider_version: str

    def key(self, state: CompactSolverState) -> StateKeyResult:
        ...


class UnavailableCanonicalStateKeyProvider:
    """Production boundary that never substitutes a Factory structural digest."""

    provider_id = CANONICAL_KEY_PROVIDER_ID
    provider_version = CANONICAL_KEY_PROVIDER_VERSION

    def key(self, state: CompactSolverState) -> StateKeyResult:
        if not isinstance(state, CompactSolverState):
            raise MemoizationContractError("canonical key request state is malformed")
        evidence = StateKeyEvidence(
            self.provider_id,
            self.provider_version,
            state.authority,
            StateKeyDisposition.UNAVAILABLE,
            AuthorityVerificationDisposition.UNAVAILABLE,
            AuthorityVerificationDisposition.UNAVAILABLE,
            "canonical runtime key authority is not configured",
        )
        return StateKeyResult(StateKeyDisposition.UNAVAILABLE, state.digest(), state.authority, self.provider_id, self.provider_version, evidence, None, evidence.reason)


@dataclass(frozen=True, slots=True)
class MemoObservation:
    disposition: MemoDisposition
    state_digest: str
    opaque_key: str | None
    visited_count: int
    memo_hits: int
    reason: str

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": MEMO_SCHEMA,
            "version": MEMO_VERSION,
            "disposition": self.disposition.value,
            "state_digest": self.state_digest,
            "opaque_key": self.opaque_key,
            "visited_count": self.visited_count,
            "memo_hits": self.memo_hits,
            "reason": self.reason,
        }


class DeterministicVisitedMemo:
    """Ordered, deterministic bookkeeping over opaque provider keys only."""

    def __init__(self, authority: SolverStateAuthority, provider_id: str, provider_version: str) -> None:
        self._authority = authority
        self._provider_id = provider_id
        self._provider_version = provider_version
        self._keys: set[str] = set()
        self._memo_hits = 0

    def observe(self, state: CompactSolverState, result: StateKeyResult) -> MemoObservation:
        if not isinstance(state, CompactSolverState):
            return self._observation(MemoDisposition.ERROR, "", None, "canonical memo state is malformed")
        if not isinstance(result, StateKeyResult):
            return self._observation(MemoDisposition.ERROR, "", None, "canonical key result is malformed")
        try:
            result.validate_for_state(state, self._provider_id, self._provider_version)
        except MemoizationContractError as exc:
            return self._observation(MemoDisposition.ERROR, result.state_digest, None, str(exc))
        if result.authority != self._authority or result.provider_id != self._provider_id or result.provider_version != self._provider_version:
            return self._observation(MemoDisposition.ERROR, result.state_digest, None, "key provider or authority mismatch")
        if result.disposition is StateKeyDisposition.UNAVAILABLE:
            return self._observation(MemoDisposition.UNAVAILABLE, result.state_digest, None, result.reason)
        if result.disposition is StateKeyDisposition.ERROR:
            return self._observation(MemoDisposition.ERROR, result.state_digest, None, result.reason)
        if result.opaque_key == result.state_digest:
            return self._observation(MemoDisposition.ERROR, result.state_digest, None, "Factory compact-state digest cannot substitute for canonical semantic key")
        assert result.opaque_key is not None
        if result.opaque_key in self._keys:
            self._memo_hits += 1
            return self._observation(MemoDisposition.MEMO_HIT, result.state_digest, result.opaque_key, "canonical opaque key was already visited")
        self._keys.add(result.opaque_key)
        return self._observation(MemoDisposition.FIRST_VISIT, result.state_digest, result.opaque_key, "canonical opaque key recorded")

    def _observation(self, disposition: MemoDisposition, state_digest: str, key: str | None, reason: str) -> MemoObservation:
        return MemoObservation(disposition, state_digest, key, len(self._keys), self._memo_hits, reason)


__all__ = [
    "CANONICAL_KEY_PROVIDER_ID",
    "CANONICAL_KEY_PROVIDER_VERSION",
    "CanonicalStateKeyProvider",
    "DeterministicVisitedMemo",
    "MemoDisposition",
    "MemoObservation",
    "MemoizationContractError",
    "STATE_KEY_SCHEMA",
    "STATE_KEY_VERSION",
    "StateKeyDisposition",
    "StateKeyEvidence",
    "StateKeyResult",
    "UnavailableCanonicalStateKeyProvider",
]
