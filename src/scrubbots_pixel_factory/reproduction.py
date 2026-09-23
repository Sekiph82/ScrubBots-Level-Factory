"""Closed deterministic reproduction manifests for accepted solver layers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re
from typing import Mapping

from .compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, CANONICAL_PROOF_STATE_SOURCE_SHA256, SolverStateAuthority
from .search_policy import MoveOrderingPolicy, PruningPolicy, SearchPolicy
from .solution_analysis import SolutionAnalysisBounds
from .solver_budget import SolverBudgetPolicy


REPRODUCTION_SCHEMA = "scrubbots-solver-reproduction"
REPRODUCTION_VERSION = 1
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_KEY_NAMES = {"api_key", "apikey", "access_token", "oauth_token", "password", "secret", "token"}
_ABSOLUTE_PATH_PATTERN = re.compile(r"^(?:[A-Za-z]:[\\/]|[\\]{2}|/)")


class ReproductionContractError(ValueError):
    """Raised when a reproduction manifest or bundle is malformed."""


class ReplayDisposition(str, Enum):
    MATCH = "MATCH"
    DIVERGED = "DIVERGED"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


def _canonical_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _digest(value: Mapping[str, object]) -> str:
    return _sha256(_canonical_bytes(value))


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ReproductionContractError(f"{label} must be a non-empty string")
    return value.strip()


def _sha(value: object, label: str) -> str:
    text = _text(value, label)
    if _SHA256_PATTERN.fullmatch(text) is None:
        raise ReproductionContractError(f"{label} must be a lowercase SHA-256 digest")
    return text


def _normalize_config(value: object, key: str = "") -> object:
    if isinstance(value, Mapping):
        normalized: dict[str, object] = {}
        for raw_key, raw_value in value.items():
            if type(raw_key) is not str or not raw_key.strip():
                raise ReproductionContractError("normalized config keys must be non-empty strings")
            name = raw_key.strip()
            if name.lower() in _FORBIDDEN_KEY_NAMES:
                raise ReproductionContractError("normalized config cannot contain secrets")
            normalized[name] = _normalize_config(raw_value, name)
        return {name: normalized[name] for name in sorted(normalized)}
    if isinstance(value, (list, tuple)):
        return [_normalize_config(item, key) for item in value]
    if isinstance(value, bool) or value is None or type(value) is int:
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ReproductionContractError("normalized config cannot contain non-finite numbers")
        return value
    if type(value) is str:
        text = value.strip()
        if _ABSOLUTE_PATH_PATTERN.match(text):
            raise ReproductionContractError("normalized config cannot contain absolute machine paths")
        return text
    raise ReproductionContractError(f"normalized config value for {key or 'root'} is not JSON-compatible")


def _path_tuple(value: object, label: str) -> tuple[dict[str, object], ...]:
    if not isinstance(value, (list, tuple)):
        raise ReproductionContractError(f"{label} must be an array")
    result: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, Mapping) or any(type(key) is not str for key in item):
            raise ReproductionContractError(f"{label} contains a malformed step")
        result.append(dict(item))
    return tuple(result)


@dataclass(frozen=True, slots=True)
class ReproductionManifest:
    candidate_source_sha256: str
    level_data_source_sha256: str
    seed: int
    normalized_config: Mapping[str, object]
    generator_version: str
    authority: SolverStateAuthority
    source_contract_sha256: str
    provider_id: str
    provider_version: str
    bridge_version: str
    search_version: str
    memo_provider_id: str | None
    memo_provider_version: str | None
    search_policy: SearchPolicy
    budgets: SolverBudgetPolicy | SolutionAnalysisBounds
    operation: str
    goal: str
    expected_disposition: str
    observed_evidence_digest: str | None = None
    observed_path: tuple[dict[str, object], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_source_sha256", _sha(self.candidate_source_sha256, "candidate source SHA-256"))
        object.__setattr__(self, "level_data_source_sha256", _sha(self.level_data_source_sha256, "LevelData source SHA-256"))
        if type(self.seed) is not int or isinstance(self.seed, bool):
            raise ReproductionContractError("seed must be an exact integer")
        object.__setattr__(self, "normalized_config", _normalize_config(self.normalized_config))
        object.__setattr__(self, "generator_version", _text(self.generator_version, "generator version"))
        if not isinstance(self.authority, SolverStateAuthority):
            raise ReproductionContractError("authority is malformed")
        object.__setattr__(self, "source_contract_sha256", _sha(self.source_contract_sha256, "source contract SHA-256"))
        if self.authority.commit_sha != CANONICAL_PROOF_STATE_AUTHORITY_SHA or self.source_contract_sha256 != CANONICAL_PROOF_STATE_SOURCE_SHA256:
            raise ReproductionContractError("reproduction authority/source contract is not the locked canonical identity")
        for name in ("provider_id", "provider_version", "bridge_version", "search_version", "operation", "goal", "expected_disposition"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        if (self.memo_provider_id is None) != (self.memo_provider_version is None):
            raise ReproductionContractError("memo provider identity must be complete or absent")
        if self.memo_provider_id is not None:
            object.__setattr__(self, "memo_provider_id", _text(self.memo_provider_id, "memo provider ID"))
            object.__setattr__(self, "memo_provider_version", _text(self.memo_provider_version, "memo provider version"))
        if isinstance(self.budgets, SolutionAnalysisBounds):
            object.__setattr__(self, "budgets", SolverBudgetPolicy.from_solution_bounds(self.budgets))
        if not isinstance(self.search_policy, SearchPolicy) or not isinstance(self.budgets, SolverBudgetPolicy):
            raise ReproductionContractError("search policy or budgets are malformed")
        if self.observed_evidence_digest is not None:
            object.__setattr__(self, "observed_evidence_digest", _sha(self.observed_evidence_digest, "observed evidence SHA-256"))
        object.__setattr__(self, "observed_path", _path_tuple(self.observed_path, "observed path"))

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": REPRODUCTION_SCHEMA,
            "version": REPRODUCTION_VERSION,
            "candidate_source_sha256": self.candidate_source_sha256,
            "level_data_source_sha256": self.level_data_source_sha256,
            "seed": self.seed,
            "normalized_config": self.normalized_config,
            "generator_version": self.generator_version,
            "authority": self.authority.canonical_dict(),
            "source_contract_sha256": self.source_contract_sha256,
            "provider": {"id": self.provider_id, "version": self.provider_version},
            "bridge_version": self.bridge_version,
            "search_version": self.search_version,
            "memo_provider": {"id": self.memo_provider_id, "version": self.memo_provider_version} if self.memo_provider_id is not None else None,
            "search_policy": self.search_policy.canonical_dict(),
            "budgets": self.budgets.canonical_dict(),
            "operation": self.operation,
            "goal": self.goal,
            "expected_disposition": self.expected_disposition,
            "observed_evidence_digest": self.observed_evidence_digest,
            "observed_path": list(self.observed_path),
        }

    def digest(self) -> str:
        return _digest(self.canonical_dict())

    def execution_context(self) -> dict[str, object]:
        """Identity inputs that a replay executor must revalidate before MATCH."""
        return {
            "candidate_source_sha256": self.candidate_source_sha256,
            "level_data_source_sha256": self.level_data_source_sha256,
            "seed": self.seed,
            "normalized_config": self.normalized_config,
            "generator_version": self.generator_version,
            "authority": self.authority.canonical_dict(),
            "source_contract_sha256": self.source_contract_sha256,
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "bridge_version": self.bridge_version,
            "search_version": self.search_version,
            "memo_provider_id": self.memo_provider_id,
            "memo_provider_version": self.memo_provider_version,
            "search_policy": self.search_policy.canonical_dict(),
            "budgets": self.budgets.canonical_dict(),
            "operation": self.operation,
            "goal": self.goal,
        }


@dataclass(frozen=True, slots=True)
class ReproductionBundle:
    manifest: ReproductionManifest
    manifest_digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.manifest, ReproductionManifest) or self.manifest_digest != self.manifest.digest():
            raise ReproductionContractError("reproduction bundle manifest digest does not match manifest bytes")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": REPRODUCTION_SCHEMA + ".bundle", "version": REPRODUCTION_VERSION, "manifest": self.manifest.canonical_dict(), "manifest_digest": self.manifest_digest}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    @classmethod
    def create(cls, manifest: ReproductionManifest) -> "ReproductionBundle":
        return cls(manifest, manifest.digest())


@dataclass(frozen=True, slots=True)
class ReplayObservation:
    disposition: str
    evidence_digest: str | None = None
    path: tuple[dict[str, object], ...] = ()
    context: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "disposition", _text(self.disposition, "replay disposition"))
        if self.evidence_digest is not None:
            object.__setattr__(self, "evidence_digest", _sha(self.evidence_digest, "replay evidence SHA-256"))
        object.__setattr__(self, "path", _path_tuple(self.path, "replay path"))
        if self.context is not None and not isinstance(self.context, Mapping):
            raise ReproductionContractError("replay context must be an object")


@dataclass(frozen=True, slots=True)
class ReplayResult:
    disposition: ReplayDisposition
    bundle_digest: str
    reason: str

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": REPRODUCTION_SCHEMA + ".replay", "version": REPRODUCTION_VERSION, "disposition": self.disposition.value, "bundle_digest": self.bundle_digest, "reason": self.reason}


class ReproductionReplay:
    """Compare observations produced by existing canonical/provider/search layers."""

    def replay(self, bundle: ReproductionBundle | object, observation: ReplayObservation | None) -> ReplayResult:
        if not isinstance(bundle, ReproductionBundle):
            return ReplayResult(ReplayDisposition.ERROR, "", "reproduction bundle is malformed")
        if observation is None:
            return ReplayResult(ReplayDisposition.UNAVAILABLE, bundle.manifest_digest, "replay execution capability is unavailable")
        if observation.disposition == "UNAVAILABLE":
            return ReplayResult(ReplayDisposition.UNAVAILABLE, bundle.manifest_digest, "replay provider or canonical bridge is unavailable")
        if observation.disposition == "ERROR":
            return ReplayResult(ReplayDisposition.ERROR, bundle.manifest_digest, "replay provider returned an error")
        manifest = bundle.manifest
        context = dict(observation.context) if observation.context is not None else manifest.execution_context()
        if context != manifest.execution_context():
            return ReplayResult(ReplayDisposition.DIVERGED, bundle.manifest_digest, "replay execution identity diverged")
        if observation.disposition != manifest.expected_disposition:
            return ReplayResult(ReplayDisposition.DIVERGED, bundle.manifest_digest, "replay disposition diverged")
        if manifest.observed_evidence_digest is not None and observation.evidence_digest != manifest.observed_evidence_digest:
            return ReplayResult(ReplayDisposition.DIVERGED, bundle.manifest_digest, "replay evidence digest diverged")
        if manifest.observed_path and observation.path != manifest.observed_path:
            return ReplayResult(ReplayDisposition.DIVERGED, bundle.manifest_digest, "replay evidence path diverged")
        return ReplayResult(ReplayDisposition.MATCH, bundle.manifest_digest, "replay observation matches the immutable manifest")


__all__ = [
    "REPRODUCTION_SCHEMA",
    "REPRODUCTION_VERSION",
    "ReplayDisposition",
    "ReplayObservation",
    "ReplayResult",
    "ReproductionBundle",
    "ReproductionContractError",
    "ReproductionManifest",
    "ReproductionReplay",
]
