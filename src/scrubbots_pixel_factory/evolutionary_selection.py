"""Offline experimental evolutionary selection over accepted M08 evidence.

This prototype selects existing, independently accepted candidate records.  It
does not mutate source art, synthesize candidates, run a provider, or create a
production-promotion record.  The explicit opt-in and separate module keep the
research path unreachable from the production generator and publication APIs.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any

from .m08_batch import CandidateEvidence, M08ContractError


SELECTION_SCHEMA = "scrubbots-experimental-evolutionary-selection"
SELECTION_VERSION = 1
SELECTION_POLICY_VERSION = "EVOLUTIONARY_SELECTION_V1"
EXPERIMENTAL_OPT_IN = "EXPERIMENTAL_EVOLUTIONARY_SELECTION_V1"
_SHA256_ZERO = "0" * 64


class EvolutionarySelectionError(ValueError):
    """Raised only when a selection policy itself is malformed."""


class SelectionDisposition(str, Enum):
    SELECTED = "SELECTED"
    OPT_IN_REQUIRED = "OPT_IN_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    INVALID_INPUT = "INVALID_INPUT"
    INSUFFICIENT_POPULATION = "INSUFFICIENT_POPULATION"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(value: Any, label: str) -> str:
    if type(value) is not str or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise EvolutionarySelectionError(f"{label} must be a lowercase SHA-256")
    return value


@dataclass(frozen=True, slots=True)
class EvolutionarySelectionPolicy:
    """Versioned finite policy for the experimental selection lane."""

    population_size: int = 4
    generations: int = 3
    evaluation_budget: int = 100
    elite_count: int = 1
    seed: int = 0
    policy_version: str = SELECTION_POLICY_VERSION
    schema: str = SELECTION_SCHEMA
    version: int = SELECTION_VERSION

    def __post_init__(self) -> None:
        if self.schema != SELECTION_SCHEMA or self.version != SELECTION_VERSION:
            raise EvolutionarySelectionError("unsupported evolutionary selection schema/version")
        if type(self.population_size) is not int or self.population_size < 1:
            raise EvolutionarySelectionError("population size must be positive")
        if type(self.generations) is not int or self.generations < 1:
            raise EvolutionarySelectionError("generation count must be positive")
        if type(self.evaluation_budget) is not int or self.evaluation_budget < 1:
            raise EvolutionarySelectionError("evaluation budget must be positive")
        if type(self.elite_count) is not int or not 1 <= self.elite_count <= self.population_size:
            raise EvolutionarySelectionError("elite count must be within the finite population")
        if type(self.seed) is not int or not -(2**63) <= self.seed <= 2**63 - 1:
            raise EvolutionarySelectionError("selection seed must be a signed 64-bit integer")
        if type(self.policy_version) is not str or not self.policy_version.strip():
            raise EvolutionarySelectionError("selection policy version is required")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "version": self.version,
            "population_size": self.population_size,
            "generations": self.generations,
            "evaluation_budget": self.evaluation_budget,
            "elite_count": self.elite_count,
            "seed": self.seed,
            "policy_version": self.policy_version,
        }

    def digest(self) -> str:
        return _digest(self.canonical_dict())


def _candidate_identity(candidate: CandidateEvidence) -> tuple[str, str, str, str]:
    return (
        candidate.candidate_id,
        candidate.lineage_digest,
        candidate.bundle_digest,
        candidate.generation_result_digest,
    )


def _validate_candidates(candidates: Sequence[CandidateEvidence]) -> tuple[CandidateEvidence, ...]:
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes, bytearray)):
        raise M08ContractError("selection candidates must be a sequence of accepted evidence")
    normalized = tuple(candidates)
    if any(not isinstance(candidate, CandidateEvidence) for candidate in normalized):
        raise M08ContractError("selection candidates contain unavailable or malformed evidence")
    ordered = tuple(sorted(normalized, key=lambda item: (item.candidate_id, item.lineage_digest)))
    identities = [_candidate_identity(candidate) for candidate in ordered]
    if len({identity[0] for identity in identities}) != len(identities):
        raise M08ContractError("duplicate candidate identity")
    if len({identity[1] for identity in identities}) != len(identities):
        raise M08ContractError("cross-candidate lineage identity collision")
    if len({identity[2] for identity in identities}) != len(identities):
        raise M08ContractError("duplicate accepted bundle identity")
    if len({identity[3] for identity in identities}) != len(identities):
        raise M08ContractError("duplicate accepted generation identity")
    return ordered


def _score(candidate: CandidateEvidence, policy: EvolutionarySelectionPolicy, generation: int) -> int:
    """Return a reproducible research ranking, never a gameplay metric."""

    return int(
        hashlib.sha256(
            _canonical(
                {
                    "policy_digest": policy.digest(),
                    "seed": policy.seed,
                    "generation": generation,
                    "candidate_identity": candidate.lineage_digest,
                }
            )
        ).hexdigest(),
        16,
    )


@dataclass(frozen=True, slots=True)
class SelectionProvenance:
    """Immutable replay binding for one experimental selection run."""

    policy_digest: str
    input_digest: str
    opt_in: str
    seed: int
    generations_completed: int
    evaluations: int
    selected_lineage_digests: tuple[str, ...]
    selection_digest: str

    def __post_init__(self) -> None:
        _sha(self.policy_digest, "selection policy digest")
        _sha(self.input_digest, "selection input digest")
        if self.opt_in != EXPERIMENTAL_OPT_IN:
            raise EvolutionarySelectionError("selection provenance requires the experimental opt-in")
        if type(self.seed) is not int or not -(2**63) <= self.seed <= 2**63 - 1:
            raise EvolutionarySelectionError("selection provenance seed is malformed")
        if type(self.generations_completed) is not int or self.generations_completed < 1:
            raise EvolutionarySelectionError("selection provenance generation count is malformed")
        if type(self.evaluations) is not int or self.evaluations < 1:
            raise EvolutionarySelectionError("selection provenance evaluation count is malformed")
        for digest in self.selected_lineage_digests:
            _sha(digest, "selected lineage digest")
        _sha(self.selection_digest, "selection digest")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": SELECTION_SCHEMA,
            "version": SELECTION_VERSION,
            "policy_digest": self.policy_digest,
            "input_digest": self.input_digest,
            "opt_in": self.opt_in,
            "seed": self.seed,
            "generations_completed": self.generations_completed,
            "evaluations": self.evaluations,
            "selected_lineage_digests": list(self.selected_lineage_digests),
            "selection_digest": self.selection_digest,
        }


@dataclass(frozen=True, slots=True)
class EvolutionarySelectionResult:
    disposition: SelectionDisposition
    policy_digest: str
    input_digest: str
    selected: tuple[CandidateEvidence, ...]
    generations_completed: int
    evaluations: int
    reason: str
    provenance: SelectionProvenance | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, SelectionDisposition):
            raise EvolutionarySelectionError("selection disposition is not closed")
        _sha(self.policy_digest, "selection result policy digest")
        _sha(self.input_digest, "selection result input digest")
        if type(self.generations_completed) is not int or self.generations_completed < 0:
            raise EvolutionarySelectionError("selection result generation count is malformed")
        if type(self.evaluations) is not int or self.evaluations < 0:
            raise EvolutionarySelectionError("selection result evaluation count is malformed")
        if type(self.reason) is not str or not self.reason.strip():
            raise EvolutionarySelectionError("selection result reason is required")
        if any(not isinstance(candidate, CandidateEvidence) for candidate in self.selected):
            raise EvolutionarySelectionError("selection result contains malformed evidence")
        if self.disposition is SelectionDisposition.SELECTED:
            if self.provenance is None or not self.selected or self.generations_completed < 1 or self.evaluations < 1:
                raise EvolutionarySelectionError("selected result lacks immutable provenance")
        elif self.selected or self.provenance is not None:
            raise EvolutionarySelectionError("non-selected result cannot expose a promotion-like selection")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": SELECTION_SCHEMA,
            "version": SELECTION_VERSION,
            "disposition": self.disposition.value,
            "policy_digest": self.policy_digest,
            "input_digest": self.input_digest,
            "selected": [candidate.as_dict() for candidate in self.selected],
            "generations_completed": self.generations_completed,
            "evaluations": self.evaluations,
            "reason": self.reason,
            "provenance": self.provenance.canonical_dict() if self.provenance is not None else None,
        }

    def digest(self) -> str:
        return _digest(self.canonical_dict())


def _closed_result(
    disposition: SelectionDisposition,
    policy: EvolutionarySelectionPolicy,
    reason: str,
    *,
    input_digest: str = _SHA256_ZERO,
) -> EvolutionarySelectionResult:
    return EvolutionarySelectionResult(disposition, policy.digest(), input_digest, (), 0, 0, reason)


def run_experimental_evolutionary_selection(
    candidates: Sequence[CandidateEvidence] | None,
    policy: EvolutionarySelectionPolicy,
    *,
    opt_in: str | None = None,
) -> EvolutionarySelectionResult:
    """Run the finite research selector; default invocation performs no work."""

    if not isinstance(policy, EvolutionarySelectionPolicy):
        raise EvolutionarySelectionError("selection policy is malformed")
    if opt_in != EXPERIMENTAL_OPT_IN:
        return _closed_result(SelectionDisposition.OPT_IN_REQUIRED, policy, "explicit experimental opt-in is required")
    if candidates is None:
        return _closed_result(SelectionDisposition.UNAVAILABLE, policy, "accepted candidate evidence is unavailable")
    try:
        normalized = _validate_candidates(candidates)
    except (M08ContractError, TypeError, ValueError) as exc:
        return _closed_result(SelectionDisposition.INVALID_INPUT, policy, str(exc) or "candidate evidence is invalid")
    input_digest = _digest([candidate.as_dict() for candidate in normalized])
    if len(normalized) < policy.population_size:
        return _closed_result(
            SelectionDisposition.INSUFFICIENT_POPULATION,
            policy,
            "accepted candidate population is smaller than the policy population",
            input_digest=input_digest,
        )
    required_evaluations = len(normalized) * policy.generations
    if required_evaluations > policy.evaluation_budget:
        return _closed_result(
            SelectionDisposition.BUDGET_EXCEEDED,
            policy,
            "finite evaluation budget cannot cover the requested generations",
            input_digest=input_digest,
        )

    survivors: tuple[CandidateEvidence, ...] = normalized[: policy.population_size]
    for generation in range(policy.generations):
        ranked = sorted(
            normalized,
            key=lambda candidate: (-_score(candidate, policy, generation), candidate.candidate_id, candidate.lineage_digest),
        )
        survivors = tuple(ranked[: policy.population_size])
    selected = tuple(
        sorted(
            survivors,
            key=lambda candidate: (-_score(candidate, policy, policy.generations), candidate.candidate_id, candidate.lineage_digest),
        )[: policy.elite_count]
    )
    selection_digest = _digest(
        {
            "policy_digest": policy.digest(),
            "input_digest": input_digest,
            "seed": policy.seed,
            "generations": policy.generations,
            "evaluations": required_evaluations,
            "selected": [candidate.lineage_digest for candidate in selected],
        }
    )
    provenance = SelectionProvenance(
        policy.digest(),
        input_digest,
        EXPERIMENTAL_OPT_IN,
        policy.seed,
        policy.generations,
        required_evaluations,
        tuple(candidate.lineage_digest for candidate in selected),
        selection_digest,
    )
    return EvolutionarySelectionResult(
        SelectionDisposition.SELECTED,
        policy.digest(),
        input_digest,
        selected,
        policy.generations,
        required_evaluations,
        "experimental selection completed over accepted evidence identities",
        provenance,
    )


__all__ = [
    "EXPERIMENTAL_OPT_IN",
    "EvolutionarySelectionError",
    "EvolutionarySelectionPolicy",
    "EvolutionarySelectionResult",
    "SELECTION_POLICY_VERSION",
    "SELECTION_SCHEMA",
    "SELECTION_VERSION",
    "SelectionDisposition",
    "SelectionProvenance",
    "run_experimental_evolutionary_selection",
]
