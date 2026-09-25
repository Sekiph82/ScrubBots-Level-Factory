"""SB-LF07-001 true lower-level immutable mutation substrate.

This module owns only authority, identity, lineage edge, request/result,
registry and generic engine mechanics. It has no dependency on m07_services or
any higher M07 policy/evidence service.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
from pathlib import Path
import re
from types import MappingProxyType

MUTATION_SCHEMA = "scrubbots-mutation"
MUTATION_VERSION = 1
LINEAGE_SCHEMA = "scrubbots-mutation-lineage"
LINEAGE_VERSION = 1
CANONICAL_GAMEPLAY_REPOSITORY = "https://github.com/Sekiph82/Scrubbots"
CANONICAL_GAMEPLAY_SHA = "UNAVAILABLE"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")

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
    source_blob_sha256: str | None = None

    def __post_init__(self) -> None:
        if _text(self.repository, "authority repository") != CANONICAL_GAMEPLAY_REPOSITORY:
            raise MutationContractError("authority repository is not canonical ScrubBots")
        if type(self.commit_sha) is not str or (self.commit_sha != "UNAVAILABLE" and _SHA1.fullmatch(self.commit_sha) is None):
            raise MutationContractError("authority commit SHA must be a lowercase 40-character SHA or UNAVAILABLE")
        source = _text(self.source_path, "authority source path").replace("\\", "/")
        if source.startswith("/") or ".." in Path(source).parts:
            raise MutationContractError("authority source path must be a relative repository path")
        object.__setattr__(self, "source_path", source)
        object.__setattr__(self, "contract_version", _text(self.contract_version, "authority contract version"))
        if self.source_blob_sha256 is not None:
            _sha(self.source_blob_sha256, "authority source blob SHA-256")

    def canonical_dict(self) -> dict[str, str]:
        return {"repository": self.repository, "commit_sha": self.commit_sha, "source_path": self.source_path, "contract_version": self.contract_version, "source_blob_sha256": self.source_blob_sha256}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


class AuthorityResolutionDisposition(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    DRIFT = "DRIFT"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class AuthorityResolution:
    disposition: AuthorityResolutionDisposition
    authority: AuthorityIdentity
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, AuthorityResolutionDisposition) or not isinstance(self.authority, AuthorityIdentity):
            raise MutationContractError("authority resolution is malformed")
        _text(self.reason, "authority resolution reason")

    @property
    def available(self) -> bool:
        return self.disposition is AuthorityResolutionDisposition.AVAILABLE


class CurrentMainAuthorityResolver:
    """Read-only injected capability for resolving exact current main authority.

    The resolver has no network dependency of its own. Callers provide the
    checkout/API head and source-blob readers, so offline production paths can
    truthfully return UNAVAILABLE instead of silently using a stale SHA.
    """

    def __init__(self, head_reader: Callable[[], str], blob_reader: Callable[[str, str], bytes]) -> None:
        if not callable(head_reader) or not callable(blob_reader):
            raise MutationContractError("current-main resolver requires callable head/blob readers")
        self._head_reader = head_reader
        self._blob_reader = blob_reader

    def resolve(self, *, source_path: str, contract_version: str, expected_blob_sha256: str) -> AuthorityResolution:
        try:
            path = _text(source_path, "authority source path").replace("\\", "/")
            version = _text(contract_version, "authority contract version")
            expected = _sha(expected_blob_sha256, "expected authority source blob SHA-256")
            head = self._head_reader()
            if type(head) is not str or _SHA1.fullmatch(head) is None:
                return AuthorityResolution(AuthorityResolutionDisposition.UNAVAILABLE, AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, "UNAVAILABLE", path, version, None), "current ScrubBots main SHA is unavailable")
            blob = self._blob_reader(head, path)
            if type(blob) is not bytes:
                return AuthorityResolution(AuthorityResolutionDisposition.UNAVAILABLE, AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, "UNAVAILABLE", path, version, None), "current ScrubBots source blob capability returned no immutable bytes")
            actual = hashlib.sha256(blob).hexdigest()
            if actual != expected:
                authority = AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, head, path, version, actual)
                return AuthorityResolution(AuthorityResolutionDisposition.DRIFT, authority, "current ScrubBots source blob differs from the accepted mechanic contract")
            return AuthorityResolution(AuthorityResolutionDisposition.AVAILABLE, AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, head, path, version, actual), "current ScrubBots main and exact source blob resolved")
        except (MutationContractError, OSError, TypeError, ValueError) as exc:
            path = str(source_path).replace("\\", "/")
            return AuthorityResolution(AuthorityResolutionDisposition.ERROR, AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, "UNAVAILABLE", path, str(contract_version), None), f"current ScrubBots authority resolution failed: {exc}")


def resolve_current_main_authority(resolver: CurrentMainAuthorityResolver | None, *, source_path: str, contract_version: str, expected_blob_sha256: str) -> AuthorityResolution:
    if resolver is None:
        return AuthorityResolution(AuthorityResolutionDisposition.UNAVAILABLE, AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, "UNAVAILABLE", source_path, contract_version, None), "current ScrubBots main resolver capability is unavailable")
    return resolver.resolve(source_path=source_path, contract_version=contract_version, expected_blob_sha256=expected_blob_sha256)


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
class LineageRootRegistration:
    lineage_root: str
    root: CandidateIdentity

    def __post_init__(self) -> None:
        _sha(self.lineage_root, "registered lineage root")
        if not isinstance(self.root, CandidateIdentity) or self.root.lineage_root != self.lineage_root or self.root.parent_candidate_id is not None:
            raise MutationContractError("registered lineage root identity is malformed")

    def digest(self) -> str:
        return _digest({"lineage_root": self.lineage_root, "root": self.root.canonical_dict()})


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

    @property
    def is_empty(self) -> bool:
        return not self._operators

class MutationEngine:
    def __init__(self, registry: MutationRegistry | None = None) -> None:
        self.registry = registry if registry is not None else MutationRegistry()

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

__all__ = [
    "AuthorityIdentity", "AuthorityResolution", "AuthorityResolutionDisposition",
    "CANONICAL_GAMEPLAY_REPOSITORY", "CANONICAL_GAMEPLAY_SHA", "CandidateIdentity",
    "CurrentMainAuthorityResolver", "LineageEdge", "LineageRootRegistration",
    "MutationCandidate", "MutationContractError", "MutationDisposition",
    "MutationEngine", "MutationIntent", "MutationOperator", "MutationRegistry",
    "MutationRequest", "MutationResult", "resolve_current_main_authority",
]
