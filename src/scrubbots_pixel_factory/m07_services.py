"""Deterministic, immutable M07 mutation contracts and evidence pipeline.

The mutation layer owns candidate identity, request/lineage binding and bounded
selection semantics.  It does not implement ScrubBots gameplay.  Operators are
small adapters to exact, read-only canonical authority contracts; gameplay
truth remains external and post-mutation evidence remains mandatory.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any

from .qa.source_preservation import OwnerSourceRecord as M05OwnerSourceRecord, SourcePreservationReport, verify_owner_source_preservation


MUTATION_SCHEMA = "scrubbots-mutation"
MUTATION_VERSION = 1
LINEAGE_SCHEMA = "scrubbots-mutation-lineage"
LINEAGE_VERSION = 1
PROVENANCE_SCHEMA = "scrubbots-mutation-provenance"
PROVENANCE_VERSION = 1
VALIDATION_SCHEMA = "scrubbots-mutation-validation"
VALIDATION_VERSION = 1
TARGETING_SCHEMA = "scrubbots-mutation-targeting"
TARGETING_VERSION = 1
ATTEMPT_BUDGET_SCHEMA = "scrubbots-mutation-attempt-budget"
ATTEMPT_BUDGET_VERSION = 1
EFFICIENCY_SCHEMA = "scrubbots-mutate-regenerate-efficiency"
EFFICIENCY_VERSION = 1
OWNER_SOURCE_SCHEMA = "scrubbots-owner-source-mutation-gate"
OWNER_SOURCE_VERSION = 1

CANONICAL_GAMEPLAY_REPOSITORY = "https://github.com/Sekiph82/Scrubbots"
# This is deliberately an unavailable capability marker, not a claim about the
# current ScrubBots branch.  Concrete operators must receive a binding from
# resolve_current_main_authority() at execution time.
CANONICAL_GAMEPLAY_SHA = "UNAVAILABLE"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_FORBIDDEN_PROXY_FIELDS = frozenset(
    {"width", "height", "dimensions", "color_count", "used_colors", "difficulty", "difficulty_label", "visual_complexity"}
)

from .mutation_base import (
    AuthorityIdentity, AuthorityResolution, AuthorityResolutionDisposition,
    CANONICAL_GAMEPLAY_REPOSITORY, CANONICAL_GAMEPLAY_SHA, CandidateIdentity,
    CurrentMainAuthorityResolver, LineageEdge, LineageRootRegistration,
    MutationCandidate, MutationContractError, MutationDisposition, MutationEngine,
    MutationIntent, MutationOperator, MutationRegistry, MutationRequest, MutationResult,
    resolve_current_main_authority,
    _canonical, _deep_freeze, _deep_thaw, _digest, _require_mapping, _sha, _text,
)

class EvidenceDisposition(str, Enum):
    SOLVED = "SOLVED"
    PROVEN_UNSOLVABLE = "PROVEN_UNSOLVABLE"
    UNKNOWN_BOUND = "UNKNOWN_BOUND"
    INCONCLUSIVE = "INCONCLUSIVE"
    AVAILABLE = "AVAILABLE"
    PASS = "PASS"
    REJECT = "REJECT"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class ValidationDisposition(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    REJECTED = "REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class TargetDisposition(str, Enum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class AttemptDisposition(str, Enum):
    TARGET_MATCH = "TARGET_MATCH"
    REJECTED = "REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNAVAILABLE = "UNAVAILABLE"
    EXHAUSTED = "EXHAUSTED"
    ERROR = "ERROR"

@dataclass(frozen=True, slots=True)
class TypedEvidenceReference:
    stage: str
    evidence_digest: str
    producer_digest: str

    def __post_init__(self) -> None:
        if self.stage not in {"M03_SOLVER", "M04_DIFFICULTY", "M05_QA"}:
            raise MutationContractError("typed provenance evidence stage is not accepted")
        _sha(self.evidence_digest, "typed provenance evidence digest")
        _sha(self.producer_digest, "typed provenance producer digest")

    def canonical_dict(self) -> dict[str, str]:
        return {"stage": self.stage, "evidence_digest": self.evidence_digest, "producer_digest": self.producer_digest}


@dataclass(frozen=True, slots=True)
class MutationProvenance:
    """Canonical reconstruction record for one mutation attempt."""

    request_digest: str
    seed: int
    seed_derivation_version: str
    lineage_root: str
    parent: CandidateIdentity
    child: CandidateIdentity
    operator_id: str
    operator_version: str
    intent: MutationIntent
    authority: AuthorityIdentity
    attempt_ordinal: int
    pre_state_digest: str
    post_state_digest: str
    disposition: MutationDisposition
    reason: str
    evidence_digests: tuple[str, ...] = ()
    evidence_references: tuple[TypedEvidenceReference, ...] = ()

    def __post_init__(self) -> None:
        _sha(self.request_digest, "provenance request digest")
        if type(self.seed) is not int or not -(2**63) <= self.seed <= 2**63 - 1:
            raise MutationContractError("provenance seed is malformed")
        object.__setattr__(self, "seed_derivation_version", _text(self.seed_derivation_version, "seed derivation version"))
        _sha(self.lineage_root, "provenance lineage root")
        if not isinstance(self.parent, CandidateIdentity) or not isinstance(self.child, CandidateIdentity):
            raise MutationContractError("provenance parent/child identity is malformed")
        if self.parent.lineage_root != self.child.lineage_root or self.parent.lineage_root != self.lineage_root:
            raise MutationContractError("provenance mixed lineage roots")
        if self.parent.candidate_id == self.child.candidate_id or self.child.parent_candidate_id != self.parent.candidate_id:
            raise MutationContractError("provenance self-parent or non-edge")
        object.__setattr__(self, "operator_id", _text(self.operator_id, "provenance operator id"))
        object.__setattr__(self, "operator_version", _text(self.operator_version, "provenance operator version"))
        if not isinstance(self.intent, MutationIntent) or not isinstance(self.authority, AuthorityIdentity):
            raise MutationContractError("provenance intent or authority is malformed")
        if type(self.attempt_ordinal) is not int or self.attempt_ordinal < 0:
            raise MutationContractError("provenance attempt ordinal must be non-negative")
        _sha(self.pre_state_digest, "provenance pre-state digest")
        _sha(self.post_state_digest, "provenance post-state digest")
        if self.pre_state_digest != self.parent.state_digest or self.post_state_digest != self.child.state_digest:
            raise MutationContractError("provenance pre/post digests do not bind exact parent and child")
        if not isinstance(self.disposition, MutationDisposition):
            raise MutationContractError("provenance disposition is not closed")
        object.__setattr__(self, "reason", _text(self.reason, "provenance reason"))
        digests = tuple(self.evidence_digests)
        for digest in digests:
            _sha(digest, "provenance evidence digest")
        object.__setattr__(self, "evidence_digests", digests)
        refs = tuple(self.evidence_references)
        if any(not isinstance(ref, TypedEvidenceReference) for ref in refs) or len({ref.stage for ref in refs}) != len(refs):
            raise MutationContractError("typed provenance evidence references must be unique by stage")
        object.__setattr__(self, "evidence_references", refs)

    @classmethod
    def from_result(cls, request: MutationRequest, result: MutationResult, *, attempt_ordinal: int = 0, evidence_digests: Iterable[str] = ()) -> "MutationProvenance":
        if result.disposition is not MutationDisposition.APPLIED or result.child is None or result.lineage is None or result.post_state_digest is None:
            raise MutationContractError("provenance requires an applied mutation result")
        if result.request_digest != request.digest() or request.parent != result.parent or result.authority != request.authority or result.operator_id != request.operator_id or result.operator_version != request.operator_version:
            raise MutationContractError("provenance request/result drift")
        return cls(request.digest(), request.seed, "M07_SEED_DERIVATION_V1", result.lineage.lineage_root, result.parent, result.child.identity, request.operator_id, request.operator_version, request.intent, request.authority, attempt_ordinal, result.pre_state_digest, result.post_state_digest, result.disposition, result.reason, tuple(evidence_digests), ())

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": PROVENANCE_SCHEMA, "version": PROVENANCE_VERSION, "request_digest": self.request_digest, "seed": self.seed, "seed_derivation_version": self.seed_derivation_version, "lineage_root": self.lineage_root, "parent": self.parent.canonical_dict(), "child": self.child.canonical_dict(), "operator_id": self.operator_id, "operator_version": self.operator_version, "intent": self.intent.value, "authority": self.authority.canonical_dict(), "attempt_ordinal": self.attempt_ordinal, "pre_state_digest": self.pre_state_digest, "post_state_digest": self.post_state_digest, "disposition": self.disposition.value, "reason": self.reason, "evidence_digests": list(self.evidence_digests), "evidence_references": [ref.canonical_dict() for ref in self.evidence_references]}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


class ProvenanceLedger:
    """Immutable-child ledger rejecting conflicting duplicate provenance."""

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], MutationProvenance] = {}
        self._roots: dict[str, LineageRootRegistration] = {}

    def register_root(self, registration: LineageRootRegistration) -> str:
        if not isinstance(registration, LineageRootRegistration):
            raise MutationContractError("lineage root registration is malformed")
        existing = self._roots.get(registration.lineage_root)
        if existing is not None and existing.digest() != registration.digest():
            raise MutationContractError("lineage root registration conflicts")
        self._roots[registration.lineage_root] = registration
        return registration.digest()

    def record(self, provenance: MutationProvenance) -> str:
        key = (provenance.lineage_root, provenance.child.candidate_id)
        if provenance.parent.parent_candidate_id is None:
            registered = self._roots.get(provenance.lineage_root)
            if registered is None or registered.root != provenance.parent:
                raise MutationContractError("first edge parent is not the explicitly registered lineage root")
        else:
            parent_key = (provenance.lineage_root, provenance.parent.candidate_id)
            if parent_key not in self._records:
                raise MutationContractError("provenance parent is missing from the lineage graph")
        cursor = provenance.parent.candidate_id
        seen = {provenance.child.candidate_id}
        while cursor in seen:
            raise MutationContractError("provenance lineage contains a cycle")
        seen.add(cursor)
        while True:
            parent_record = self._records.get((provenance.lineage_root, cursor))
            if parent_record is None:
                break
            cursor = parent_record.parent.candidate_id
            if cursor in seen:
                raise MutationContractError("provenance lineage contains a cycle")
            seen.add(cursor)
        existing = self._records.get(key)
        if existing is not None and existing.digest() != provenance.digest():
            raise MutationContractError("duplicate child has conflicting provenance")
        self._records[key] = provenance
        return provenance.digest()

    def get(self, lineage_root: str, child_candidate_id: str) -> MutationProvenance | None:
        return self._records.get((lineage_root, child_candidate_id))

    def snapshot(self) -> tuple[MutationProvenance, ...]:
        return tuple(self._records[key] for key in sorted(self._records))

def _copy_payload(payload: Mapping[str, object]) -> dict[str, object]:
    return _deep_thaw(payload)  # type: ignore[return-value]


def _gameplay(payload: Mapping[str, object]) -> dict[str, object] | None:
    value = payload.get("gameplay")
    return _copy_payload(value) if isinstance(value, Mapping) else None


def _allowed_gameplay_change(before: Mapping[str, object], after: Mapping[str, object], allowed: str) -> bool:
    before_all = _copy_payload(before)
    after_all = _copy_payload(after)
    if set(before_all) != set(after_all):
        return False
    for key in before_all:
        if key == allowed:
            continue
        if before_all[key] != after_all[key]:
            return False
    return True


def _slot_easing(payload: Mapping[str, object]) -> tuple[MutationDisposition, Mapping[str, object] | None, str]:
    gameplay = _gameplay(payload)
    if gameplay is None or type(gameplay.get("slot_capacity")) is not int:
        return MutationDisposition.INAPPLICABLE, None, "canonical M39 slot capacity state is absent"
    if gameplay.get("booster") != "+1_SLOT":
        return MutationDisposition.INAPPLICABLE, None, "canonical +1 Slot booster is not explicitly present"
    capacity = int(gameplay["slot_capacity"])
    if capacity < 5 or capacity > 6:
        return MutationDisposition.ERROR, None, "canonical M39 slot capacity bounds are invalid"
    if capacity == 6:
        return MutationDisposition.NO_CHANGE, None, "canonical M39 temporary sixth slot is already active"
    gameplay["slot_capacity"] = 6
    out = _copy_payload(payload)
    out["gameplay"] = gameplay
    if not _allowed_gameplay_change(_gameplay(payload) or {}, gameplay, "slot_capacity"):
        return MutationDisposition.ERROR, None, "easing transform changed an unauthorized gameplay field"
    return MutationDisposition.APPLIED, out, "activated the canonical M39 temporary sixth slot"


def _slot_hardening(payload: Mapping[str, object]) -> tuple[MutationDisposition, Mapping[str, object] | None, str]:
    """Reverse only the authority-defined, uncommitted +1 Slot transition."""

    gameplay = _gameplay(payload)
    if gameplay is None or type(gameplay.get("slot_capacity")) is not int:
        return MutationDisposition.INAPPLICABLE, None, "canonical M39 slot capacity state is absent"
    if gameplay.get("booster") != "+1_SLOT":
        return MutationDisposition.INAPPLICABLE, None, "canonical +1 Slot booster identity is not present"
    if gameplay.get("sixth_slot_state") != "EMPTY" or gameplay.get("live_work_on_sixth", 0) != 0:
        return MutationDisposition.INAPPLICABLE, None, "canonical M39 rollback requires an empty, uncommitted sixth slot"
    if int(gameplay["slot_capacity"]) != 6:
        return MutationDisposition.NO_CHANGE if int(gameplay["slot_capacity"]) == 5 else MutationDisposition.ERROR, None, "canonical M39 rollback requires active six-slot capacity"
    gameplay["slot_capacity"] = 5
    out = _copy_payload(payload)
    out["gameplay"] = gameplay
    if not _allowed_gameplay_change(_gameplay(payload) or {}, gameplay, "slot_capacity"):
        return MutationDisposition.ERROR, None, "hardening rollback changed an unauthorized gameplay field"
    return MutationDisposition.APPLIED, out, "rolled back the canonical M39 uncommitted temporary sixth slot to the five-slot baseline"


CANONICAL_M23_SOURCE_PATH = "scripts/gameplay/supply/batch_supply_engine.gd"
CANONICAL_M39_SOURCE_PATH = "scripts/gameplay/slots/five_slot_batch_engine.gd"
CANONICAL_M23_CONTRACT_VERSION = "M23_V02_FIFO_PREVIEW_DEPTH"
CANONICAL_M39_CONTRACT_VERSION = "M39_V04_PLUS_ONE_SLOT"
CANONICAL_M39_ROLLBACK_CONTRACT_VERSION = "M39_V04_PLUS_ONE_SLOT_ROLLBACK"
CANONICAL_M23_PREVIEW_AUTHORITY = AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, CANONICAL_GAMEPLAY_SHA, CANONICAL_M23_SOURCE_PATH, CANONICAL_M23_CONTRACT_VERSION)
CANONICAL_M39_SLOT_AUTHORITY = AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, CANONICAL_GAMEPLAY_SHA, CANONICAL_M39_SOURCE_PATH, CANONICAL_M39_CONTRACT_VERSION)


def _default_registry() -> MutationRegistry:
    # The base substrate deliberately installs no concrete future-task policy.
    # Concrete operator factories must install authority-bound operators.
    return MutationRegistry()


def canonical_mutation_registry(*, m23_authority: AuthorityIdentity | None = None, m39_authority: AuthorityIdentity | None = None) -> MutationRegistry:
    """Build the concrete operator layer from execution-time authority bindings.

    The base default registry remains empty.  A missing or unavailable binding
    produces an empty concrete registry, so callers cannot accidentally execute
    a mechanic under an unresolved current-main identity.
    """

    registry = MutationRegistry()
    if m39_authority is not None and m39_authority.commit_sha != "UNAVAILABLE" and m39_authority.source_blob_sha256 is not None:
        from .mutation_hardening import build_hardening_registry
        from .mutation_easing import build_easing_registry
        hardening = build_hardening_registry(m39_authority)
        for operator in hardening.snapshot():
            registry._install(operator, lambda payload, op=operator: hardening.transform(op, payload))
        easing = build_easing_registry(m39_authority)
        for operator in easing.snapshot():
            registry._install(operator, lambda payload, op=operator: easing.transform(op, payload))
    return registry


DEFAULT_MUTATION_REGISTRY = _default_registry()

@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    stage: str
    disposition: EvidenceDisposition
    child_state_digest: str
    request_digest: str
    parent_state_digest: str
    operator_id: str
    authority_digest: str
    payload: Mapping[str, object]
    evidence_digest: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage", _text(self.stage, "evidence stage"))
        if not isinstance(self.disposition, EvidenceDisposition):
            raise MutationContractError("evidence disposition is not closed")
        _sha(self.child_state_digest, "evidence child digest")
        _sha(self.request_digest, "evidence request digest")
        _sha(self.parent_state_digest, "evidence parent digest")
        _sha(self.authority_digest, "evidence authority digest")
        _require_mapping(self.payload, "evidence payload")
        derived = _digest({"stage": self.stage, "disposition": self.disposition.value, "child_state_digest": self.child_state_digest, "request_digest": self.request_digest, "parent_state_digest": self.parent_state_digest, "operator_id": self.operator_id, "authority_digest": self.authority_digest, "payload": self.payload})
        if self.evidence_digest is not None and self.evidence_digest != derived:
            raise MutationContractError("evidence digest is caller-overridable or stale")
        object.__setattr__(self, "evidence_digest", derived)
        object.__setattr__(self, "payload", _deep_freeze(_deep_thaw(self.payload)))

    def canonical_dict(self) -> dict[str, object]:
        return {"stage": self.stage, "disposition": self.disposition.value, "child_state_digest": self.child_state_digest, "request_digest": self.request_digest, "parent_state_digest": self.parent_state_digest, "operator_id": self.operator_id, "authority_digest": self.authority_digest, "payload": _deep_thaw(self.payload), "evidence_digest": self.evidence_digest}


@dataclass(frozen=True, slots=True)
class ValidationEnvelope:
    mutation_digest: str
    child: CandidateIdentity
    solver: EvidenceRecord
    difficulty: EvidenceRecord
    qa: EvidenceRecord
    disposition: ValidationDisposition
    reason: str
    evidence_digest: str

    def __post_init__(self) -> None:
        _sha(self.mutation_digest, "mutation digest")
        if not isinstance(self.child, CandidateIdentity):
            raise MutationContractError("validation child identity is malformed")
        records = (self.solver, self.difficulty, self.qa)
        if any(not isinstance(record, EvidenceRecord) for record in records):
            raise MutationContractError("validation evidence is malformed")
        if any(record.child_state_digest != self.child.state_digest for record in records):
            raise MutationContractError("validation evidence is not bound to the exact child")
        if not isinstance(self.disposition, ValidationDisposition):
            raise MutationContractError("validation disposition is not closed")
        _text(self.reason, "validation reason")
        expected = _digest({"schema": VALIDATION_SCHEMA, "version": VALIDATION_VERSION, "mutation_digest": self.mutation_digest, "child": self.child.canonical_dict(), "solver": self.solver.canonical_dict(), "difficulty": self.difficulty.canonical_dict(), "qa": self.qa.canonical_dict(), "disposition": self.disposition.value, "reason": self.reason})
        if self.evidence_digest != expected:
            raise MutationContractError("validation envelope digest mismatch")

    @property
    def challenge_score(self) -> float | None:
        value = self.difficulty.payload.get("challenge_score")
        return float(value) if type(value) in (int, float) and math.isfinite(float(value)) else None

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": VALIDATION_SCHEMA, "version": VALIDATION_VERSION, "mutation_digest": self.mutation_digest, "child": self.child.canonical_dict(), "solver": self.solver.canonical_dict(), "difficulty": self.difficulty.canonical_dict(), "qa": self.qa.canonical_dict(), "disposition": self.disposition.value, "reason": self.reason, "evidence_digest": self.evidence_digest}


def evidence(stage: str, disposition: EvidenceDisposition, mutation: MutationResult, payload: Mapping[str, object]) -> EvidenceRecord:
    if mutation.disposition is not MutationDisposition.APPLIED or mutation.child is None:
        raise MutationContractError("post-mutation evidence requires an applied mutation")
    return EvidenceRecord(stage, disposition, mutation.child.state_digest, mutation.request_digest, mutation.parent.state_digest, mutation.operator_id, mutation.authority.digest(), payload)


def revalidate_mutation(mutation: MutationResult, solver: EvidenceRecord, difficulty: EvidenceRecord, qa: EvidenceRecord) -> ValidationEnvelope:
    if mutation.disposition is not MutationDisposition.APPLIED or mutation.child is None:
        raise MutationContractError("only APPLIED mutations can be revalidated")
    records = (solver, difficulty, qa)
    expected_stages = ("M03_SOLVER", "M04_DIFFICULTY", "M05_QA")
    if tuple(record.stage for record in records) != expected_stages:
        raise MutationContractError("post-mutation evidence stages are incomplete or reordered")
    if any(record.request_digest != mutation.request_digest or record.parent_state_digest != mutation.parent.state_digest or record.operator_id != mutation.operator_id or record.authority_digest != mutation.authority.digest() for record in records):
        raise MutationContractError("post-mutation evidence has stale lineage or authority")
    if solver.disposition is EvidenceDisposition.PROVEN_UNSOLVABLE:
        disposition, reason = ValidationDisposition.REJECTED, "M03 proved the mutated child unsolvable"
    elif solver.disposition in (EvidenceDisposition.UNKNOWN_BOUND, EvidenceDisposition.INCONCLUSIVE):
        disposition, reason = ValidationDisposition.INCONCLUSIVE, "M03 could not prove the mutated child"
    elif solver.disposition is EvidenceDisposition.UNAVAILABLE:
        disposition, reason = ValidationDisposition.UNAVAILABLE, "M03 canonical solver capability is unavailable"
    elif solver.disposition is not EvidenceDisposition.SOLVED:
        disposition, reason = ValidationDisposition.ERROR, "M03 solver evidence is not an accepted child truth"
    elif difficulty.disposition is EvidenceDisposition.UNAVAILABLE or qa.disposition is EvidenceDisposition.UNAVAILABLE:
        disposition, reason = ValidationDisposition.UNAVAILABLE, "required M04/M05 capability is unavailable"
    elif difficulty.disposition in (EvidenceDisposition.UNKNOWN_BOUND, EvidenceDisposition.INCONCLUSIVE) or qa.disposition is EvidenceDisposition.INCONCLUSIVE:
        disposition, reason = ValidationDisposition.INCONCLUSIVE, "required M04/M05 evidence is inconclusive"
    elif difficulty.disposition is not EvidenceDisposition.AVAILABLE or qa.disposition is not EvidenceDisposition.PASS:
        disposition, reason = ValidationDisposition.REJECTED, "M04 difficulty or M05 QA rejected the mutated child"
    elif difficulty.payload.get("challenge_score") is None:
        disposition, reason = ValidationDisposition.INCONCLUSIVE, "M04 did not provide a real Challenge Score"
    else:
        disposition, reason = ValidationDisposition.ELIGIBLE, "mutated child passed the complete M03/M04/M05 evidence chain"
    expected_digest = _digest({"schema": VALIDATION_SCHEMA, "version": VALIDATION_VERSION, "mutation_digest": mutation.digest(), "child": mutation.child.identity.canonical_dict(), "solver": solver.canonical_dict(), "difficulty": difficulty.canonical_dict(), "qa": qa.canonical_dict(), "disposition": disposition.value, "reason": reason})
    return ValidationEnvelope(mutation.digest(), mutation.child.identity, solver, difficulty, qa, disposition, reason, expected_digest)


@dataclass(frozen=True, slots=True)
class ChallengeTarget:
    minimum: float
    maximum: float
    policy_version: str
    required_constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not all(type(value) in (int, float) and math.isfinite(float(value)) for value in (self.minimum, self.maximum)) or self.minimum > self.maximum:
            raise MutationContractError("Challenge Score target range is malformed")
        object.__setattr__(self, "policy_version", _text(self.policy_version, "Challenge Score policy version"))
        object.__setattr__(self, "required_constraints", tuple(sorted({_text(value, "required constraint") for value in self.required_constraints})))

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": TARGETING_SCHEMA, "version": TARGETING_VERSION, "minimum": self.minimum, "maximum": self.maximum, "policy_version": self.policy_version, "required_constraints": list(self.required_constraints)}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class TargetSelection:
    disposition: TargetDisposition
    target_digest: str
    candidate: ValidationEnvelope | None
    reason: str
    selection_digest: str


def select_target(target: ChallengeTarget, candidates: Sequence[ValidationEnvelope]) -> TargetSelection:
    if not isinstance(target, ChallengeTarget):
        raise MutationContractError("target is malformed")
    matches: list[ValidationEnvelope] = []
    saw_inconclusive = False
    saw_unavailable = False
    for candidate in candidates:
        if candidate.disposition is not ValidationDisposition.ELIGIBLE:
            saw_inconclusive |= candidate.disposition is ValidationDisposition.INCONCLUSIVE
            saw_unavailable |= candidate.disposition is ValidationDisposition.UNAVAILABLE
            continue
        if candidate.difficulty.payload.get("policy_version") != target.policy_version:
            saw_inconclusive = True
            continue
        score = candidate.challenge_score
        if score is None:
            saw_inconclusive = True
            continue
        missing = [key for key in target.required_constraints if candidate.difficulty.payload.get(key) is None]
        if missing:
            saw_inconclusive = True
            continue
        if any(candidate.difficulty.payload.get(key) is not True for key in target.required_constraints):
            continue
        if target.minimum <= score <= target.maximum:
            matches.append(candidate)
    if matches:
        midpoint = (target.minimum + target.maximum) / 2.0
        selected = min(matches, key=lambda item: (abs(float(item.challenge_score) - midpoint), item.child.state_digest, item.mutation_digest))
        reason = "deterministic score-distance then child-digest selection"
        digest = _digest({"target": target.canonical_dict(), "selected": selected.canonical_dict(), "reason": reason})
        return TargetSelection(TargetDisposition.MATCH, target.digest(), selected, reason, digest)
    disposition = TargetDisposition.UNAVAILABLE if saw_unavailable and not saw_inconclusive else TargetDisposition.INCONCLUSIVE if saw_inconclusive else TargetDisposition.NO_MATCH
    reason = {TargetDisposition.UNAVAILABLE: "required evidence capability is unavailable", TargetDisposition.INCONCLUSIVE: "no candidate had complete matching evidence", TargetDisposition.NO_MATCH: "no eligible candidate fell inside the requested range"}[disposition]
    digest = _digest({"target": target.canonical_dict(), "selected": None, "reason": reason})
    return TargetSelection(disposition, target.digest(), None, reason, digest)


@dataclass(frozen=True, slots=True)
class AttemptBudget:
    max_attempts: int
    version: str = "M07_ATTEMPT_BUDGET_V1"

    def __post_init__(self) -> None:
        if type(self.max_attempts) is not int or self.max_attempts <= 0 or self.max_attempts > 10000:
            raise MutationContractError("max_attempts must be a finite positive integer <= 10000")
        object.__setattr__(self, "version", _text(self.version, "attempt budget version"))

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": ATTEMPT_BUDGET_SCHEMA, "version": ATTEMPT_BUDGET_VERSION, "budget_version": self.version, "max_attempts": self.max_attempts}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class AttemptRecord:
    ordinal: int
    effective_seed: int
    mutation: MutationResult
    validation: ValidationEnvelope | None
    selection: TargetSelection | None
    provenance: MutationProvenance | None = None
    attempt_provenance: AttemptProvenance | None = None


@dataclass(frozen=True, slots=True)
class AttemptReport:
    disposition: AttemptDisposition
    budget: AttemptBudget
    attempts: tuple[AttemptRecord, ...]
    selected: ValidationEnvelope | None
    reason: str
    target: object | None = None
    seed_config_digest: str | None = None


def derive_attempt_seed(base_seed: int, ordinal: int) -> int:
    if type(base_seed) is not int or type(ordinal) is not int or ordinal < 0:
        raise MutationContractError("attempt seed inputs are malformed")
    derived = base_seed + ordinal * 2654435761
    if not -(2**63) <= derived <= 2**63 - 1:
        raise MutationContractError("derived attempt seed exceeds signed 64-bit range")
    return derived


def run_bounded_mutations(parent: MutationCandidate, *, base_seed: int, budget: AttemptBudget, request_factory: Callable[[MutationCandidate, int, int], MutationRequest], engine: MutationEngine, validator: Callable[[MutationResult], ValidationEnvelope], target: ChallengeTarget) -> AttemptReport:
    records: list[AttemptRecord] = []
    current = parent
    terminal_candidates: list[AttemptDisposition] = []
    for ordinal in range(budget.max_attempts):
        effective_seed = derive_attempt_seed(base_seed, ordinal)
        request = request_factory(current, ordinal, effective_seed)
        mutation = engine.apply(request, current)
        attempt_provenance = AttemptProvenance(ordinal, effective_seed, mutation.request_digest, mutation.parent.candidate_id, mutation.disposition, mutation.reason, mutation.operator_id, mutation.operator_version, mutation.authority.digest(), mutation.parent.state_digest)
        if mutation.disposition is not MutationDisposition.APPLIED:
            records.append(AttemptRecord(ordinal, effective_seed, mutation, None, None, None, attempt_provenance))
            terminal_candidates.append({MutationDisposition.ERROR: AttemptDisposition.ERROR, MutationDisposition.UNAVAILABLE: AttemptDisposition.UNAVAILABLE}.get(mutation.disposition, AttemptDisposition.REJECTED))
            continue
        validation = validator(mutation)
        selection = select_target(target, (validation,))
        provenance = MutationProvenance.from_result(request, mutation, attempt_ordinal=ordinal, evidence_digests=(validation.evidence_digest,))
        records.append(AttemptRecord(ordinal, effective_seed, mutation, validation, selection, provenance, attempt_provenance))
        if selection.disposition is TargetDisposition.MATCH:
            return AttemptReport(AttemptDisposition.TARGET_MATCH, budget, tuple(records), validation, "target matched before budget exhaustion")
        terminal_candidates.append({ValidationDisposition.UNAVAILABLE: AttemptDisposition.UNAVAILABLE, ValidationDisposition.INCONCLUSIVE: AttemptDisposition.INCONCLUSIVE, ValidationDisposition.REJECTED: AttemptDisposition.REJECTED, ValidationDisposition.ERROR: AttemptDisposition.ERROR}.get(validation.disposition, AttemptDisposition.REJECTED))
        if mutation.child is not None:
            current = mutation.child
    precedence = (AttemptDisposition.ERROR, AttemptDisposition.UNAVAILABLE, AttemptDisposition.INCONCLUSIVE, AttemptDisposition.REJECTED)
    terminal = next((value for value in precedence if value in terminal_candidates), AttemptDisposition.EXHAUSTED)
    reason = "finite mutation budget exhausted without target success" if terminal is AttemptDisposition.EXHAUSTED else f"strongest observed terminal disposition: {terminal.value}"
    return AttemptReport(terminal, budget, tuple(records), None, reason)


@dataclass(frozen=True, slots=True)
class EfficiencyCounters:
    attempts: int
    produced: int
    accepted: int
    inconclusive: int
    rejected: int
    solver_workload: int

    def __post_init__(self) -> None:
        if any(type(value) is not int or value < 0 for value in (self.attempts, self.produced, self.accepted, self.inconclusive, self.rejected, self.solver_workload)):
            raise MutationContractError("efficiency counters must be non-negative integers")

    def canonical_dict(self) -> dict[str, int]:
        return {"attempts": self.attempts, "produced": self.produced, "accepted": self.accepted, "inconclusive": self.inconclusive, "rejected": self.rejected, "solver_workload": self.solver_workload}


@dataclass(frozen=True, slots=True)
class EfficiencyWorkload:
    target_digest: str
    seed_config_digest: str
    validation_policy_digest: str
    budget_digest: str

    def __post_init__(self) -> None:
        for value, label in ((self.target_digest, "target"), (self.seed_config_digest, "seed/config"), (self.validation_policy_digest, "validation policy"), (self.budget_digest, "budget")):
            _sha(value, f"efficiency {label} digest")

    def canonical_dict(self) -> dict[str, str]:
        return {"target_digest": self.target_digest, "seed_config_digest": self.seed_config_digest, "validation_policy_digest": self.validation_policy_digest, "budget_digest": self.budget_digest}


@dataclass(frozen=True, slots=True)
class EfficiencyComparison:
    workload: EfficiencyWorkload
    mutation: EfficiencyCounters
    regenerate: EfficiencyCounters
    mutation_cost: Mapping[str, object] | None = None
    regenerate_cost: Mapping[str, object] | None = None
    telemetry: Mapping[str, object] | None = None

    def canonical_dict(self) -> dict[str, object]:
        def trusted(cost: Mapping[str, object] | None) -> Mapping[str, object] | None:
            if cost is None or cost.get("trusted") is not True:
                return None
            return {str(key): value for key, value in cost.items() if key != "trusted"}
        return {"schema": EFFICIENCY_SCHEMA, "version": EFFICIENCY_VERSION, "workload": self.workload.canonical_dict(), "mutation": self.mutation.canonical_dict(), "regenerate": self.regenerate.canonical_dict(), "mutation_cost": trusted(self.mutation_cost), "regenerate_cost": trusted(self.regenerate_cost)}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


def compare_efficiency(left: EfficiencyWorkload, right: EfficiencyWorkload, mutation: EfficiencyCounters, regenerate: EfficiencyCounters, *, mutation_cost: Mapping[str, object] | None = None, regenerate_cost: Mapping[str, object] | None = None, telemetry: Mapping[str, object] | None = None) -> EfficiencyComparison:
    if left != right:
        raise MutationContractError("mutate-vs-regenerate workloads are not matched")
    return EfficiencyComparison(left, mutation, regenerate, mutation_cost, regenerate_cost, telemetry)


OwnerSourceRecord = M05OwnerSourceRecord
OwnerSourceReport = SourcePreservationReport
verify_owner_source_immutable = verify_owner_source_preservation


# R01 typed boundaries.  The legacy EvidenceRecord constructor remains useful
# for historical fixtures, but production orchestration must use these sealed
# producer receipts.  A receipt carries the producer schema/version and its
# digest; labels supplied in a free-form payload are never sufficient.
@dataclass(frozen=True, slots=True)
class ProducerEvidenceReceipt:
    producer: str
    schema: str
    version: str
    producer_digest: str
    record: EvidenceRecord

    def __post_init__(self) -> None:
        object.__setattr__(self, "producer", _text(self.producer, "evidence producer"))
        object.__setattr__(self, "schema", _text(self.schema, "evidence producer schema"))
        object.__setattr__(self, "version", _text(self.version, "evidence producer version"))
        _sha(self.producer_digest, "evidence producer digest")
        if not isinstance(self.record, EvidenceRecord):
            raise MutationContractError("typed evidence receipt record is malformed")

    def canonical_dict(self) -> dict[str, object]:
        return {"producer": self.producer, "schema": self.schema, "version": self.version, "producer_digest": self.producer_digest, "record": self.record.canonical_dict()}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class M03SolverEvidenceReceipt(ProducerEvidenceReceipt):
    def __post_init__(self) -> None:
        ProducerEvidenceReceipt.__post_init__(self)
        if self.producer != "M03_SOLVER" or self.record.stage != "M03_SOLVER":
            raise MutationContractError("M03 receipt is not an accepted solver producer")


@dataclass(frozen=True, slots=True)
class M04DifficultyEvidenceReceipt(ProducerEvidenceReceipt):
    def __post_init__(self) -> None:
        ProducerEvidenceReceipt.__post_init__(self)
        if self.producer != "M04_DIFFICULTY" or self.record.stage != "M04_DIFFICULTY":
            raise MutationContractError("M04 receipt is not an accepted difficulty producer")
        if type(self.record.payload.get("challenge_score")) not in (int, float):
            raise MutationContractError("M04 receipt lacks typed Challenge Score")


@dataclass(frozen=True, slots=True)
class M05QAEvidenceReceipt(ProducerEvidenceReceipt):
    def __post_init__(self) -> None:
        ProducerEvidenceReceipt.__post_init__(self)
        if self.producer != "M05_QA" or self.record.stage != "M05_QA":
            raise MutationContractError("M05 receipt is not an accepted QA producer")


def revalidate_mutation_from_typed_receipts(mutation: MutationResult, solver: M03SolverEvidenceReceipt, difficulty: M04DifficultyEvidenceReceipt, qa: M05QAEvidenceReceipt) -> ValidationEnvelope:
    """Production validation entry point; generic/free-form records are rejected."""
    if not all(isinstance(item, ProducerEvidenceReceipt) for item in (solver, difficulty, qa)):
        raise MutationContractError("production validation requires typed M03/M04/M05 producer receipts")
    return revalidate_mutation(mutation, solver.record, difficulty.record, qa.record)


@dataclass(frozen=True, slots=True)
class SafetyConstraintEvidence:
    schema: str
    version: str
    policy_digest: str
    load_ok: bool
    risk_ok: bool
    retention_ok: bool
    producer_digest: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema", _text(self.schema, "safety evidence schema"))
        object.__setattr__(self, "version", _text(self.version, "safety evidence version"))
        _sha(self.policy_digest, "safety policy digest")
        _sha(self.producer_digest, "safety producer digest")
        if not all(type(value) is bool for value in (self.load_ok, self.risk_ok, self.retention_ok)):
            raise MutationContractError("safety constraints must be typed booleans")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "policy_digest": self.policy_digest, "load_ok": self.load_ok, "risk_ok": self.risk_ok, "retention_ok": self.retention_ok, "producer_digest": self.producer_digest}


@dataclass(frozen=True, slots=True)
class TypedChallengeTarget:
    minimum: float
    maximum: float
    policy_digest: str
    safety: SafetyConstraintEvidence

    def __post_init__(self) -> None:
        if not all(type(value) in (int, float) and math.isfinite(float(value)) for value in (self.minimum, self.maximum)) or self.minimum > self.maximum:
            raise MutationContractError("typed Challenge Score range is malformed")
        _sha(self.policy_digest, "typed target policy digest")
        if self.safety.policy_digest != self.policy_digest:
            raise MutationContractError("target safety evidence is bound to another policy")

    def digest(self) -> str:
        return _digest({"minimum": self.minimum, "maximum": self.maximum, "policy_digest": self.policy_digest, "safety": self.safety.canonical_dict()})


@dataclass(frozen=True, slots=True)
class AttemptProvenance:
    ordinal: int
    effective_seed: int
    request_digest: str
    parent_candidate_id: str
    mutation_disposition: MutationDisposition
    reason: str
    operator_id: str = "UNAVAILABLE"
    operator_version: str = "UNAVAILABLE"
    authority_digest: str = "0" * 64
    parent_state_digest: str = "0" * 64

    def __post_init__(self) -> None:
        if type(self.ordinal) is not int or self.ordinal < 0:
            raise MutationContractError("attempt provenance ordinal is malformed")
        if type(self.effective_seed) is not int or not -(2**63) <= self.effective_seed <= 2**63 - 1:
            raise MutationContractError("attempt provenance seed is outside signed 64-bit range")
        _sha(self.request_digest, "attempt provenance request digest")
        _text(self.parent_candidate_id, "attempt provenance parent candidate id")
        if not isinstance(self.mutation_disposition, MutationDisposition):
            raise MutationContractError("attempt provenance disposition is malformed")
        _text(self.reason, "attempt provenance reason")
        _text(self.operator_id, "attempt provenance operator id")
        _text(self.operator_version, "attempt provenance operator version")
        _sha(self.authority_digest, "attempt provenance authority digest")
        _sha(self.parent_state_digest, "attempt provenance parent state digest")


@dataclass(frozen=True, slots=True)
class GeneratorRouteEvidence:
    route: str
    workload_digest: str
    produced: int
    accepted: int
    rejected: int
    solver_workload: int
    accounting_digest: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "route", _text(self.route, "generator route"))
        _sha(self.workload_digest, "generator workload digest")
        _sha(self.accounting_digest, "generator accounting digest")
        if any(type(value) is not int or value < 0 for value in (self.produced, self.accepted, self.rejected, self.solver_workload)):
            raise MutationContractError("generator evidence counters are malformed")


def compare_efficiency_from_routes(mutation: GeneratorRouteEvidence, regenerate: GeneratorRouteEvidence) -> EfficiencyComparison:
    if mutation.workload_digest != regenerate.workload_digest:
        raise MutationContractError("route evidence workloads are not matched")
    workload = EfficiencyWorkload(mutation.workload_digest, mutation.workload_digest, mutation.workload_digest, mutation.workload_digest)
    return EfficiencyComparison(workload, EfficiencyCounters(mutation.produced, mutation.produced, mutation.accepted, 0, mutation.rejected, mutation.solver_workload), EfficiencyCounters(regenerate.produced, regenerate.produced, regenerate.accepted, 0, regenerate.rejected, regenerate.solver_workload), telemetry=None)


__all__ = [
    "ATTEMPT_BUDGET_SCHEMA", "ATTEMPT_BUDGET_VERSION", "AttemptBudget", "AttemptDisposition", "AttemptRecord", "AttemptReport", "AttemptProvenance", "AuthorityIdentity", "AuthorityResolution", "AuthorityResolutionDisposition", "CANONICAL_GAMEPLAY_REPOSITORY", "CANONICAL_GAMEPLAY_SHA", "CANONICAL_M23_CONTRACT_VERSION", "CANONICAL_M23_PREVIEW_AUTHORITY", "CANONICAL_M23_SOURCE_PATH", "CANONICAL_M39_CONTRACT_VERSION", "CANONICAL_M39_ROLLBACK_CONTRACT_VERSION", "CANONICAL_M39_SLOT_AUTHORITY", "CANONICAL_M39_SOURCE_PATH", "CandidateIdentity", "ChallengeTarget", "CurrentMainAuthorityResolver", "DEFAULT_MUTATION_REGISTRY", "EFFICIENCY_SCHEMA", "EFFICIENCY_VERSION", "EfficiencyComparison", "EfficiencyCounters", "EfficiencyWorkload", "EvidenceDisposition", "EvidenceRecord", "GeneratorRouteEvidence", "LineageEdge", "LineageRootRegistration", "M03SolverEvidenceReceipt", "M04DifficultyEvidenceReceipt", "M05QAEvidenceReceipt", "MutationCandidate", "MutationContractError", "MutationDisposition", "MutationEngine", "MutationIntent", "MutationOperator", "MutationProvenance", "MutationRegistry", "MutationRequest", "MutationResult", "OwnerSourceRecord", "OwnerSourceReport", "ProducerEvidenceReceipt", "SafetyConstraintEvidence", "TargetDisposition", "TargetSelection", "TypedChallengeTarget", "TypedEvidenceReference", "ValidationDisposition", "ValidationEnvelope", "ProvenanceLedger", "canonical_mutation_registry", "compare_efficiency", "compare_efficiency_from_routes", "derive_attempt_seed", "evidence", "resolve_current_main_authority", "revalidate_mutation", "revalidate_mutation_from_typed_receipts", "run_bounded_mutations", "select_target", "verify_owner_source_immutable",
]
