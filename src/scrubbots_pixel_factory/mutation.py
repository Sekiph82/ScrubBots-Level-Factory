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
CANONICAL_GAMEPLAY_SHA = "edf672f61989d28fd1931917ab49b2d64cc416d6"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_FORBIDDEN_PROXY_FIELDS = frozenset(
    {"width", "height", "dimensions", "color_count", "used_colors", "difficulty", "difficulty_label", "visual_complexity"}
)


class MutationContractError(ValueError):
    """Raised when a closed M07 contract cannot be constructed."""


class MutationDisposition(str, Enum):
    APPLIED = "APPLIED"
    NO_CHANGE = "NO_CHANGE"
    INAPPLICABLE = "INAPPLICABLE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class MutationIntent(str, Enum):
    HARDEN = "HARDEN"
    EASE = "EASE"


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


def _canonical(value: object) -> bytes:
    """Return stable JSON bytes and reject values that cannot be identity data."""

    def check(item: object) -> object:
        if isinstance(item, Mapping):
            return {str(key): check(val) for key, val in item.items()}
        if isinstance(item, (list, tuple)):
            return [check(val) for val in item]
        if item is None or isinstance(item, (str, bool, int)):
            return item
        if isinstance(item, float):
            if not math.isfinite(item):
                raise MutationContractError("canonical identity cannot contain non-finite floats")
            return item
        raise MutationContractError(f"unsupported canonical identity value: {type(item).__name__}")

    return json.dumps(check(value), ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise MutationContractError(f"{label} must be a non-empty string")
    return value.strip()


def _sha(value: object, label: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise MutationContractError(f"{label} must be a lowercase SHA-256")
    return value


def _deep_freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _deep_freeze(val) for key, val in value.items()})
    if isinstance(value, list):
        return tuple(_deep_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_deep_freeze(item) for item in value)
    return value


def _deep_thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _deep_thaw(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_deep_thaw(item) for item in value]
    return value


def _require_mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise MutationContractError(f"{label} must be an object")
    return value


@dataclass(frozen=True, slots=True)
class AuthorityIdentity:
    repository: str
    commit_sha: str
    source_path: str
    contract_version: str

    def __post_init__(self) -> None:
        if _text(self.repository, "authority repository") != CANONICAL_GAMEPLAY_REPOSITORY:
            raise MutationContractError("authority repository is not canonical ScrubBots")
        if type(self.commit_sha) is not str or _SHA1.fullmatch(self.commit_sha) is None:
            raise MutationContractError("authority commit SHA must be a lowercase 40-character SHA")
        source = _text(self.source_path, "authority source path").replace("\\", "/")
        if source.startswith("/") or ".." in Path(source).parts:
            raise MutationContractError("authority source path must be a relative repository path")
        object.__setattr__(self, "source_path", source)
        object.__setattr__(self, "contract_version", _text(self.contract_version, "authority contract version"))

    def canonical_dict(self) -> dict[str, str]:
        return {"repository": self.repository, "commit_sha": self.commit_sha, "source_path": self.source_path, "contract_version": self.contract_version}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class CandidateIdentity:
    candidate_id: str
    state_digest: str
    level_data_sha256: str | None
    source_art_sha256: str | None
    lineage_root: str
    parent_candidate_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", _text(self.candidate_id, "candidate id"))
        _sha(self.state_digest, "candidate state digest")
        _sha(self.level_data_sha256, "LevelData digest", optional=True)
        _sha(self.source_art_sha256, "source/art digest", optional=True)
        _sha(self.lineage_root, "lineage root")
        if self.parent_candidate_id is not None:
            _text(self.parent_candidate_id, "parent candidate id")
        if self.parent_candidate_id == self.candidate_id:
            raise MutationContractError("candidate cannot parent itself")

    def canonical_dict(self) -> dict[str, object]:
        return {"candidate_id": self.candidate_id, "state_digest": self.state_digest, "level_data_sha256": self.level_data_sha256, "source_art_sha256": self.source_art_sha256, "lineage_root": self.lineage_root, "parent_candidate_id": self.parent_candidate_id}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class MutationCandidate:
    candidate_id: str
    payload: Mapping[str, object]
    level_data_sha256: str | None = None
    source_art_sha256: str | None = None
    lineage_root: str | None = None
    parent_candidate_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", _text(self.candidate_id, "candidate id"))
        payload = _require_mapping(self.payload, "candidate payload")
        frozen = _deep_freeze(_deep_thaw(payload))
        object.__setattr__(self, "payload", frozen)
        _sha(self.level_data_sha256, "LevelData digest", optional=True)
        _sha(self.source_art_sha256, "source/art digest", optional=True)
        if self.parent_candidate_id is not None:
            _text(self.parent_candidate_id, "parent candidate id")
        if self.lineage_root is not None:
            _sha(self.lineage_root, "lineage root")
        if self.parent_candidate_id == self.candidate_id:
            raise MutationContractError("candidate cannot parent itself")

    @property
    def state_digest(self) -> str:
        return _digest(self.payload)

    @property
    def identity(self) -> CandidateIdentity:
        root = self.lineage_root or _digest({"candidate_id": self.candidate_id, "state_digest": self.state_digest})
        return CandidateIdentity(self.candidate_id, self.state_digest, self.level_data_sha256, self.source_art_sha256, root, self.parent_candidate_id)

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": "scrubbots-mutation-candidate", "version": 1, "identity": self.identity.canonical_dict(), "payload": _deep_thaw(self.payload)}

    def digest(self) -> str:
        return _digest(self.canonical_dict())

    @classmethod
    def root(cls, candidate_id: str, payload: Mapping[str, object], *, level_data_sha256: str | None = None, source_art_sha256: str | None = None) -> "MutationCandidate":
        draft = cls(candidate_id, payload, level_data_sha256, source_art_sha256)
        root = _digest({"candidate_id": draft.candidate_id, "state_digest": draft.state_digest})
        return cls(candidate_id, payload, level_data_sha256, source_art_sha256, root)


@dataclass(frozen=True, slots=True)
class MutationRequest:
    parent: CandidateIdentity
    operator_id: str
    operator_version: str
    seed: int
    intent: MutationIntent
    authority: AuthorityIdentity

    def __post_init__(self) -> None:
        if not isinstance(self.parent, CandidateIdentity):
            raise MutationContractError("mutation request parent identity is malformed")
        object.__setattr__(self, "operator_id", _text(self.operator_id, "operator id"))
        object.__setattr__(self, "operator_version", _text(self.operator_version, "operator version"))
        if type(self.seed) is not int or not -(2**63) <= self.seed <= 2**63 - 1:
            raise MutationContractError("seed must be a signed 64-bit integer")
        if not isinstance(self.intent, MutationIntent) or not isinstance(self.authority, AuthorityIdentity):
            raise MutationContractError("mutation request intent or authority is malformed")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": MUTATION_SCHEMA, "version": MUTATION_VERSION, "parent": self.parent.canonical_dict(), "operator_id": self.operator_id, "operator_version": self.operator_version, "seed": self.seed, "intent": self.intent.value, "authority": self.authority.canonical_dict()}

    def digest(self) -> str:
        return _digest(self.canonical_dict())

    @classmethod
    def for_candidate(cls, parent: MutationCandidate, *, operator_id: str, operator_version: str, seed: int, intent: MutationIntent, authority: AuthorityIdentity) -> "MutationRequest":
        return cls(parent.identity, operator_id, operator_version, seed, intent, authority)


@dataclass(frozen=True, slots=True)
class LineageEdge:
    lineage_root: str
    parent: CandidateIdentity
    child: CandidateIdentity
    request_digest: str
    operator_id: str
    operator_version: str
    authority_digest: str

    def __post_init__(self) -> None:
        _sha(self.lineage_root, "lineage root")
        if not isinstance(self.parent, CandidateIdentity) or not isinstance(self.child, CandidateIdentity):
            raise MutationContractError("lineage edge identities are malformed")
        if self.parent.lineage_root != self.child.lineage_root or self.parent.lineage_root != self.lineage_root:
            raise MutationContractError("lineage root mismatch")
        if self.parent.candidate_id == self.child.candidate_id or self.child.parent_candidate_id != self.parent.candidate_id:
            raise MutationContractError("lineage edge is not a parent-to-distinct-child edge")
        _sha(self.request_digest, "request digest")
        _sha(self.authority_digest, "authority digest")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": LINEAGE_SCHEMA, "version": LINEAGE_VERSION, "lineage_root": self.lineage_root, "parent": self.parent.canonical_dict(), "child": self.child.canonical_dict(), "request_digest": self.request_digest, "operator_id": self.operator_id, "operator_version": self.operator_version, "authority_digest": self.authority_digest}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class MutationResult:
    disposition: MutationDisposition
    request_digest: str
    parent: CandidateIdentity
    child: MutationCandidate | None
    pre_state_digest: str
    post_state_digest: str | None
    lineage: LineageEdge | None
    reason: str
    operator_id: str
    operator_version: str
    authority: AuthorityIdentity

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, MutationDisposition):
            raise MutationContractError("mutation disposition is not closed")
        _sha(self.request_digest, "request digest")
        if not isinstance(self.parent, CandidateIdentity) or self.pre_state_digest != self.parent.state_digest:
            raise MutationContractError("mutation pre-state does not bind the parent")
        if not isinstance(self.authority, AuthorityIdentity):
            raise MutationContractError("mutation authority is malformed")
        _text(self.reason, "mutation reason")
        if self.disposition is MutationDisposition.APPLIED:
            if not isinstance(self.child, MutationCandidate) or self.lineage is None or self.post_state_digest != self.child.state_digest:
                raise MutationContractError("APPLIED mutation requires a distinct child and post-state binding")
        elif self.child is not None or self.lineage is not None or self.post_state_digest is not None:
            raise MutationContractError("non-applied mutation cannot carry child lineage")

    @property
    def eligible(self) -> bool:
        return False

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": MUTATION_SCHEMA, "version": MUTATION_VERSION, "disposition": self.disposition.value, "request_digest": self.request_digest, "parent": self.parent.canonical_dict(), "child": self.child.canonical_dict() if self.child else None, "pre_state_digest": self.pre_state_digest, "post_state_digest": self.post_state_digest, "lineage": self.lineage.canonical_dict() if self.lineage else None, "reason": self.reason, "operator_id": self.operator_id, "operator_version": self.operator_version, "authority": self.authority.canonical_dict()}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


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

    @classmethod
    def from_result(cls, request: MutationRequest, result: MutationResult, *, attempt_ordinal: int = 0, evidence_digests: Iterable[str] = ()) -> "MutationProvenance":
        if result.disposition is not MutationDisposition.APPLIED or result.child is None or result.lineage is None or result.post_state_digest is None:
            raise MutationContractError("provenance requires an applied mutation result")
        if result.request_digest != request.digest() or request.parent != result.parent or result.authority != request.authority:
            raise MutationContractError("provenance request/result drift")
        return cls(request.digest(), request.seed, "M07_SEED_DERIVATION_V1", result.lineage.lineage_root, result.parent, result.child.identity, request.operator_id, request.operator_version, request.intent, request.authority, attempt_ordinal, result.pre_state_digest, result.post_state_digest, result.disposition, result.reason, tuple(evidence_digests))

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": PROVENANCE_SCHEMA, "version": PROVENANCE_VERSION, "request_digest": self.request_digest, "seed": self.seed, "seed_derivation_version": self.seed_derivation_version, "lineage_root": self.lineage_root, "parent": self.parent.canonical_dict(), "child": self.child.canonical_dict(), "operator_id": self.operator_id, "operator_version": self.operator_version, "intent": self.intent.value, "authority": self.authority.canonical_dict(), "attempt_ordinal": self.attempt_ordinal, "pre_state_digest": self.pre_state_digest, "post_state_digest": self.post_state_digest, "disposition": self.disposition.value, "reason": self.reason, "evidence_digests": list(self.evidence_digests)}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


class ProvenanceLedger:
    """Immutable-child ledger rejecting conflicting duplicate provenance."""

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], MutationProvenance] = {}

    def record(self, provenance: MutationProvenance) -> str:
        key = (provenance.lineage_root, provenance.child.candidate_id)
        existing = self._records.get(key)
        if existing is not None and existing.digest() != provenance.digest():
            raise MutationContractError("duplicate child has conflicting provenance")
        self._records[key] = provenance
        return provenance.digest()

    def get(self, lineage_root: str, child_candidate_id: str) -> MutationProvenance | None:
        return self._records.get((lineage_root, child_candidate_id))

    def snapshot(self) -> tuple[MutationProvenance, ...]:
        return tuple(self._records[key] for key in sorted(self._records))


@dataclass(frozen=True, slots=True)
class MutationOperator:
    operator_id: str
    version: str
    intent: MutationIntent
    authority: AuthorityIdentity
    transform_name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "operator_id", _text(self.operator_id, "operator id"))
        object.__setattr__(self, "version", _text(self.version, "operator version"))
        object.__setattr__(self, "transform_name", _text(self.transform_name, "operator transform"))
        if not isinstance(self.intent, MutationIntent) or not isinstance(self.authority, AuthorityIdentity):
            raise MutationContractError("operator intent or authority is malformed")

    def canonical_dict(self) -> dict[str, object]:
        return {"operator_id": self.operator_id, "version": self.version, "intent": self.intent.value, "authority": self.authority.canonical_dict(), "transform": self.transform_name}


class MutationRegistry:
    """Closed registry: callers may inspect it, but cannot add transforms."""

    def __init__(self) -> None:
        self._operators: dict[tuple[str, str], MutationOperator] = {}
        self._transforms: dict[tuple[str, str], Callable[[Mapping[str, object]], tuple[MutationDisposition, Mapping[str, object] | None, str]]] = {}

    def _install(self, operator: MutationOperator, transform: Callable[[Mapping[str, object]], tuple[MutationDisposition, Mapping[str, object] | None, str]]) -> None:
        key = (operator.operator_id, operator.version)
        if key in self._operators:
            raise MutationContractError("duplicate mutation operator")
        self._operators[key] = operator
        self._transforms[key] = transform

    def get(self, operator_id: str, version: str) -> MutationOperator | None:
        return self._operators.get((operator_id, version))

    def transform(self, operator: MutationOperator, payload: Mapping[str, object]) -> tuple[MutationDisposition, Mapping[str, object] | None, str]:
        return self._transforms[(operator.operator_id, operator.version)](payload)

    def snapshot(self) -> tuple[MutationOperator, ...]:
        return tuple(self._operators[key] for key in sorted(self._operators))


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


def _preview_hardening(payload: Mapping[str, object]) -> tuple[MutationDisposition, Mapping[str, object] | None, str]:
    gameplay = _gameplay(payload)
    if gameplay is None or type(gameplay.get("preview_depth")) is not int:
        return MutationDisposition.INAPPLICABLE, None, "canonical M23 preview_depth state is absent"
    depth = int(gameplay["preview_depth"])
    if depth < 3 or depth > 4 or type(gameplay.get("column_count")) is not int or not 3 <= int(gameplay["column_count"]) <= 5:
        return MutationDisposition.ERROR, None, "canonical M23 preview/column bounds are invalid"
    if depth == 4:
        return MutationDisposition.NO_CHANGE, None, "canonical M23 preview depth is already at its hardening bound"
    gameplay["preview_depth"] = depth + 1
    out = _copy_payload(payload)
    out["gameplay"] = gameplay
    if not _allowed_gameplay_change(_gameplay(payload) or {}, gameplay, "preview_depth"):
        return MutationDisposition.ERROR, None, "hardening transform changed an unauthorized gameplay field"
    return MutationDisposition.APPLIED, out, "increased canonical M23 FIFO preview depth by one"


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


CANONICAL_M23_PREVIEW_AUTHORITY = AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, CANONICAL_GAMEPLAY_SHA, "scripts/gameplay/supply/batch_supply_engine.gd", "M23_V02_FIFO_PREVIEW_DEPTH")
CANONICAL_M39_SLOT_AUTHORITY = AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, CANONICAL_GAMEPLAY_SHA, "scripts/gameplay/slots/five_slot_batch_engine.gd", "M39_V04_PLUS_ONE_SLOT")


def _default_registry() -> MutationRegistry:
    registry = MutationRegistry()
    registry._install(MutationOperator("CANONICAL_PREVIEW_DEPTH_HARDEN_V1", "1", MutationIntent.HARDEN, CANONICAL_M23_PREVIEW_AUTHORITY, "increase_preview_depth"), _preview_hardening)
    registry._install(MutationOperator("CANONICAL_PLUS_ONE_SLOT_EASE_V1", "1", MutationIntent.EASE, CANONICAL_M39_SLOT_AUTHORITY, "activate_sixth_slot"), _slot_easing)
    return registry


DEFAULT_MUTATION_REGISTRY = _default_registry()


class MutationEngine:
    def __init__(self, registry: MutationRegistry = DEFAULT_MUTATION_REGISTRY) -> None:
        self.registry = registry

    def apply(self, request: MutationRequest, parent: MutationCandidate) -> MutationResult:
        try:
            if not isinstance(request, MutationRequest) or not isinstance(parent, MutationCandidate):
                raise MutationContractError("request or parent is malformed")
            if request.parent != parent.identity:
                return self._failure(request, parent, MutationDisposition.ERROR, "stale or mismatched parent identity")
            operator = self.registry.get(request.operator_id, request.operator_version)
            if operator is None:
                return self._failure(request, parent, MutationDisposition.INAPPLICABLE, "operator is not in the closed registry")
            if operator.intent is not request.intent or operator.authority != request.authority:
                return self._failure(request, parent, MutationDisposition.ERROR, "operator intent/version/authority drift")
            disposition, output, reason = self.registry.transform(operator, parent.payload)
            if disposition is not MutationDisposition.APPLIED:
                return self._failure(request, parent, disposition, reason)
            if output is None or output == _deep_thaw(parent.payload):
                return self._failure(request, parent, MutationDisposition.ERROR, "APPLIED operator returned no distinct state")
            child_id = f"{parent.candidate_id}::mutation::{request.digest()[:24]}"
            child = MutationCandidate(child_id, output, parent.level_data_sha256, parent.source_art_sha256, parent.identity.lineage_root, parent.candidate_id)
            if child.candidate_id == parent.candidate_id or child.source_art_sha256 != parent.source_art_sha256 or child.level_data_sha256 != parent.level_data_sha256:
                return self._failure(request, parent, MutationDisposition.ERROR, "child identity or immutable source identity is invalid")
            edge = LineageEdge(parent.identity.lineage_root, parent.identity, child.identity, request.digest(), operator.operator_id, operator.version, operator.authority.digest())
            return MutationResult(MutationDisposition.APPLIED, request.digest(), parent.identity, child, parent.state_digest, child.state_digest, edge, reason, operator.operator_id, operator.version, operator.authority)
        except MutationContractError as exc:
            return self._failure(request, parent, MutationDisposition.ERROR, str(exc))

    @staticmethod
    def _failure(request: MutationRequest, parent: MutationCandidate, disposition: MutationDisposition, reason: str) -> MutationResult:
        return MutationResult(disposition, request.digest(), parent.identity, None, parent.state_digest, None, None, reason, request.operator_id, request.operator_version, request.authority)


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


@dataclass(frozen=True, slots=True)
class AttemptReport:
    disposition: AttemptDisposition
    budget: AttemptBudget
    attempts: tuple[AttemptRecord, ...]
    selected: ValidationEnvelope | None
    reason: str


def derive_attempt_seed(base_seed: int, ordinal: int) -> int:
    if type(base_seed) is not int or type(ordinal) is not int or ordinal < 0:
        raise MutationContractError("attempt seed inputs are malformed")
    return base_seed + ordinal * 2654435761


def run_bounded_mutations(parent: MutationCandidate, *, base_seed: int, budget: AttemptBudget, request_factory: Callable[[MutationCandidate, int, int], MutationRequest], engine: MutationEngine, validator: Callable[[MutationResult], ValidationEnvelope], target: ChallengeTarget) -> AttemptReport:
    records: list[AttemptRecord] = []
    current = parent
    for ordinal in range(budget.max_attempts):
        effective_seed = derive_attempt_seed(base_seed, ordinal)
        request = request_factory(current, ordinal, effective_seed)
        mutation = engine.apply(request, current)
        if mutation.disposition is not MutationDisposition.APPLIED:
            records.append(AttemptRecord(ordinal, effective_seed, mutation, None, None))
            continue
        validation = validator(mutation)
        selection = select_target(target, (validation,))
        provenance = MutationProvenance.from_result(request, mutation, attempt_ordinal=ordinal, evidence_digests=(validation.evidence_digest,))
        records.append(AttemptRecord(ordinal, effective_seed, mutation, validation, selection, provenance))
        if selection.disposition is TargetDisposition.MATCH:
            return AttemptReport(AttemptDisposition.TARGET_MATCH, budget, tuple(records), validation, "target matched before budget exhaustion")
        if mutation.child is not None:
            current = mutation.child
    return AttemptReport(AttemptDisposition.EXHAUSTED, budget, tuple(records), None, "finite mutation budget exhausted without target success")


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


@dataclass(frozen=True, slots=True)
class OwnerSourceRecord:
    source_id: str
    source_sha256: str
    byte_length: int
    width: int
    height: int
    source_path: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", _text(self.source_id, "owner source id"))
        _sha(self.source_sha256, "owner source SHA-256")
        if any(type(value) is not int or value <= 0 for value in (self.byte_length, self.width, self.height)):
            raise MutationContractError("owner source length/dimensions are malformed")
        object.__setattr__(self, "source_path", _text(self.source_path, "owner source path").replace("\\", "/"))


@dataclass(frozen=True, slots=True)
class OwnerSourceReport:
    disposition: str
    source_id: str
    before_sha256: str | None
    after_sha256: str | None
    byte_length: int
    width: int
    height: int
    reason: str


def _path_identity(value: str) -> str:
    return "/".join(part for part in value.replace("\\", "/").split("/") if part not in ("", ".")).lower()


def verify_owner_source_immutable(record: OwnerSourceRecord, before: bytes, after: bytes, *, before_dimensions: tuple[int, int] | None = None, after_dimensions: tuple[int, int] | None = None, derived_paths: Iterable[str] = ()) -> OwnerSourceReport:
    before_sha = hashlib.sha256(before).hexdigest()
    after_sha = hashlib.sha256(after).hexdigest()
    derived = {_path_identity(str(path)) for path in derived_paths}
    source = _path_identity(record.source_path)
    if source in derived:
        return OwnerSourceReport("ERROR", record.source_id, before_sha, after_sha, len(after), record.width, record.height, "derived artifact aliases immutable OWNER_UPLOAD path")
    if before_sha != record.source_sha256 or len(before) != record.byte_length:
        return OwnerSourceReport("ERROR", record.source_id, before_sha, after_sha, len(after), record.width, record.height, "pre-operation OWNER_UPLOAD bytes do not match accepted record")
    if before_dimensions is not None and before_dimensions != (record.width, record.height):
        return OwnerSourceReport("ERROR", record.source_id, before_sha, after_sha, len(after), record.width, record.height, "pre-operation OWNER_UPLOAD dimensions do not match accepted record")
    if after_dimensions is not None and after_dimensions != (record.width, record.height):
        return OwnerSourceReport("FAIL", record.source_id, before_sha, after_sha, len(after), record.width, record.height, "M07 operation changed OWNER_UPLOAD dimensions")
    if before_dimensions is not None and after_dimensions is not None and before_dimensions != after_dimensions:
        return OwnerSourceReport("FAIL", record.source_id, before_sha, after_sha, len(after), record.width, record.height, "M07 operation changed OWNER_UPLOAD dimensions")
    if after_sha != before_sha or len(after) != len(before):
        return OwnerSourceReport("FAIL", record.source_id, before_sha, after_sha, len(after), record.width, record.height, "M07 operation changed immutable OWNER_UPLOAD bytes")
    return OwnerSourceReport("PASS", record.source_id, before_sha, after_sha, len(after), record.width, record.height, "OWNER_UPLOAD bytes, length, dimensions and source identity remained unchanged")


__all__ = [
    "ATTEMPT_BUDGET_SCHEMA", "ATTEMPT_BUDGET_VERSION", "AttemptBudget", "AttemptDisposition", "AttemptRecord", "AttemptReport", "AuthorityIdentity", "CANONICAL_GAMEPLAY_REPOSITORY", "CANONICAL_GAMEPLAY_SHA", "CANONICAL_M23_PREVIEW_AUTHORITY", "CANONICAL_M39_SLOT_AUTHORITY", "CandidateIdentity", "ChallengeTarget", "DEFAULT_MUTATION_REGISTRY", "EFFICIENCY_SCHEMA", "EFFICIENCY_VERSION", "EfficiencyComparison", "EfficiencyCounters", "EfficiencyWorkload", "EvidenceDisposition", "EvidenceRecord", "LineageEdge", "MutationCandidate", "MutationContractError", "MutationDisposition", "MutationEngine", "MutationIntent", "MutationOperator", "MutationRegistry", "MutationRequest", "MutationResult", "OwnerSourceRecord", "OwnerSourceReport", "TargetDisposition", "TargetSelection", "ValidationDisposition", "ValidationEnvelope", "compare_efficiency", "derive_attempt_seed", "evidence", "revalidate_mutation", "run_bounded_mutations", "select_target", "verify_owner_source_immutable",
]
