"""Closed, offline fitness metrics for the experimental LF09 lane.

Fitness is deliberately limited to accepted-evidence integrity signals.  It
does not inspect or derive gameplay semantics, difficulty, source-art meaning,
or production-promotion state.  All scores use integer basis points so the
contract has no floating-point or non-finite behavior.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .m08_batch import CandidateEvidence, M08ContractError, verify_artifact_set


FITNESS_SCHEMA = "scrubbots-experimental-fitness"
FITNESS_VERSION = 1
FITNESS_POLICY_VERSION = "EXPERIMENTAL_FITNESS_V1"
FITNESS_SCORE_SCALE = 1_000_000
FITNESS_AGGREGATION = "WEIGHTED_MEAN_FLOOR"
_SHA256_ZERO = "0" * 64

FITNESS_ARTIFACT_IDENTITY_FIELDS = (
    ("level_data_ref", "level_data_digest"),
    ("logical_art_ref", "logical_art_digest"),
    ("bundle_ref", "bundle_digest"),
    ("source_provenance_ref", "source_provenance_digest"),
    ("m03_ref", "m03_digest"),
    ("m04_ref", "m04_digest"),
    ("m05_ref", "m05_digest"),
    ("generation_request_ref", "generation_request_digest"),
    ("generation_result_ref", "generation_result_digest"),
    ("generation_metadata_ref", "generation_metadata_digest"),
    ("preview_ref", "preview_digest"),
    ("mutation_ref", "mutation_digest"),
)
_OPTIONAL_ARTIFACT_PAIRS = (("preview_ref", "preview_digest"), ("mutation_ref", "mutation_digest"))


class FitnessMetricError(ValueError):
    """Raised when fitness policy or evidence cannot be accepted."""


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(value: Any, label: str) -> str:
    if type(value) is not str or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise FitnessMetricError(f"{label} must be a lowercase SHA-256")
    return value


@dataclass(frozen=True, slots=True)
class FitnessMetricDefinition:
    """One closed metric definition included in the policy digest."""

    metric_id: str
    meaning: str
    unit: str
    normalization: str
    direction: str
    aggregation: str
    weight: int

    def __post_init__(self) -> None:
        if any(type(value) is not str or not value.strip() for value in (
            self.metric_id, self.meaning, self.unit, self.normalization,
            self.direction, self.aggregation,
        )):
            raise FitnessMetricError("fitness metric definition text is required")
        if self.direction not in {"MAXIMIZE", "MINIMIZE"}:
            raise FitnessMetricError("fitness metric direction is not closed")
        if self.aggregation != FITNESS_AGGREGATION:
            raise FitnessMetricError("fitness metric aggregation is not closed")
        if type(self.weight) is not int or self.weight < 1:
            raise FitnessMetricError("fitness metric weight must be positive")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "metric_id": self.metric_id,
            "meaning": self.meaning,
            "unit": self.unit,
            "normalization": self.normalization,
            "direction": self.direction,
            "aggregation": self.aggregation,
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "FitnessMetricDefinition":
        required = {"metric_id", "meaning", "unit", "normalization", "direction", "aggregation", "weight"}
        if set(value) != required:
            raise FitnessMetricError("fitness metric definition fields are unsupported or incomplete")
        return cls(*(value[key] for key in ("metric_id", "meaning", "unit", "normalization", "direction", "aggregation", "weight")))


DEFAULT_FITNESS_METRIC_CATALOG = (
    FitnessMetricDefinition(
        "artifact_identity_coverage",
        "verified references in the closed candidate artifact identity set",
        "basis_points",
        "verified candidate-specific references / 12 * 1,000,000",
        "MAXIMIZE",
        FITNESS_AGGREGATION,
        3,
    ),
    FitnessMetricDefinition(
        "optional_artifact_coverage",
        "verified optional preview and mutation artifact pairs",
        "basis_points",
        "verified optional pairs / 2 * 1,000,000",
        "MAXIMIZE",
        FITNESS_AGGREGATION,
        1,
    ),
)


@dataclass(frozen=True, slots=True)
class FitnessPolicy:
    """Closed versioned metric catalog and aggregation policy."""

    metric_catalog: tuple[FitnessMetricDefinition, ...] = DEFAULT_FITNESS_METRIC_CATALOG
    policy_version: str = FITNESS_POLICY_VERSION
    schema: str = FITNESS_SCHEMA
    version: int = FITNESS_VERSION
    score_scale: int = FITNESS_SCORE_SCALE
    aggregation: str = FITNESS_AGGREGATION

    def __post_init__(self) -> None:
        if self.schema != FITNESS_SCHEMA or self.version != FITNESS_VERSION:
            raise FitnessMetricError("unsupported fitness schema/version")
        if self.policy_version != FITNESS_POLICY_VERSION:
            raise FitnessMetricError("unsupported fitness policy version")
        if self.score_scale != FITNESS_SCORE_SCALE or self.aggregation != FITNESS_AGGREGATION:
            raise FitnessMetricError("unsupported fitness scale or aggregation")
        if not isinstance(self.metric_catalog, tuple) or self.metric_catalog != DEFAULT_FITNESS_METRIC_CATALOG:
            raise FitnessMetricError("fitness metric catalog is not the closed canonical catalog")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "version": self.version,
            "policy_version": self.policy_version,
            "score_scale": self.score_scale,
            "aggregation": self.aggregation,
            "metric_catalog": [item.canonical_dict() for item in self.metric_catalog],
            "artifact_identity_fields": [list(pair) for pair in FITNESS_ARTIFACT_IDENTITY_FIELDS],
        }

    def digest(self) -> str:
        return _digest(self.canonical_dict())

    def aggregate(self, values: Mapping[str, int]) -> int:
        if set(values) != {item.metric_id for item in self.metric_catalog}:
            raise FitnessMetricError("fitness metric values do not match the closed catalog")
        weighted = sum(values[item.metric_id] * item.weight for item in self.metric_catalog)
        total_weight = sum(item.weight for item in self.metric_catalog)
        return weighted // total_weight

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "FitnessPolicy":
        required = {"schema", "version", "policy_version", "score_scale", "aggregation", "metric_catalog", "artifact_identity_fields"}
        if (
            set(value) != required
            or not isinstance(value["metric_catalog"], list)
            or value["artifact_identity_fields"] != [list(pair) for pair in FITNESS_ARTIFACT_IDENTITY_FIELDS]
        ):
            raise FitnessMetricError("fitness policy fields are unsupported or incomplete")
        return cls(
            tuple(FitnessMetricDefinition.from_dict(item) for item in value["metric_catalog"]),
            value["policy_version"], value["schema"], value["version"], value["score_scale"], value["aggregation"],
        )


@dataclass(frozen=True, slots=True)
class FitnessMetricValue:
    metric_id: str
    normalized_value: int

    def __post_init__(self) -> None:
        if type(self.metric_id) is not str or not self.metric_id.strip():
            raise FitnessMetricError("fitness metric identity is malformed")
        if type(self.normalized_value) is not int or not 0 <= self.normalized_value <= FITNESS_SCORE_SCALE:
            raise FitnessMetricError("fitness metric value must be finite integer basis points")

    def canonical_dict(self) -> dict[str, object]:
        return {"metric_id": self.metric_id, "normalized_value": self.normalized_value}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "FitnessMetricValue":
        if set(value) != {"metric_id", "normalized_value"}:
            raise FitnessMetricError("fitness metric value fields are unsupported or incomplete")
        return cls(value["metric_id"], value["normalized_value"])


@dataclass(frozen=True, slots=True)
class CandidateFitness:
    """A policy- and lineage-bound fitness result for one accepted candidate."""

    candidate_id: str
    lineage_digest: str
    policy_digest: str
    metrics: tuple[FitnessMetricValue, ...]
    aggregate_score: int
    fitness_digest: str

    def __post_init__(self) -> None:
        if type(self.candidate_id) is not str or not self.candidate_id.strip():
            raise FitnessMetricError("fitness candidate identity is malformed")
        _sha(self.lineage_digest, "fitness lineage digest")
        _sha(self.policy_digest, "fitness policy digest")
        if type(self.metrics) is not tuple or not self.metrics:
            raise FitnessMetricError("fitness metric values are missing")
        if any(not isinstance(item, FitnessMetricValue) for item in self.metrics):
            raise FitnessMetricError("fitness metric values are malformed")
        if len({item.metric_id for item in self.metrics}) != len(self.metrics):
            raise FitnessMetricError("fitness metric values contain duplicate identities")
        expected_metric_ids = tuple(item.metric_id for item in DEFAULT_FITNESS_METRIC_CATALOG)
        if tuple(item.metric_id for item in self.metrics) != expected_metric_ids:
            raise FitnessMetricError("fitness metric values do not match the closed catalog order")
        if type(self.aggregate_score) is not int or not 0 <= self.aggregate_score <= FITNESS_SCORE_SCALE:
            raise FitnessMetricError("fitness aggregate must be finite integer basis points")
        expected_aggregate = FitnessPolicy().aggregate({item.metric_id: item.normalized_value for item in self.metrics})
        if self.aggregate_score != expected_aggregate:
            raise FitnessMetricError("fitness aggregate does not match the closed policy")
        _sha(self.fitness_digest, "fitness result digest")
        if self.fitness_digest != _digest(self._payload_dict()):
            raise FitnessMetricError("fitness result digest does not bind its payload")

    def _payload_dict(self) -> dict[str, object]:
        return {
            "schema": FITNESS_SCHEMA,
            "version": FITNESS_VERSION,
            "candidate_id": self.candidate_id,
            "lineage_digest": self.lineage_digest,
            "policy_digest": self.policy_digest,
            "metrics": [item.canonical_dict() for item in self.metrics],
            "aggregate_score": self.aggregate_score,
        }

    def canonical_dict(self) -> dict[str, object]:
        return {**self._payload_dict(), "fitness_digest": self.fitness_digest}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CandidateFitness":
        required = {"schema", "version", "candidate_id", "lineage_digest", "policy_digest", "metrics", "aggregate_score", "fitness_digest"}
        if set(value) != required or value["schema"] != FITNESS_SCHEMA or value["version"] != FITNESS_VERSION:
            raise FitnessMetricError("fitness result fields are unsupported or incomplete")
        return cls(
            value["candidate_id"], value["lineage_digest"], value["policy_digest"],
            tuple(FitnessMetricValue.from_dict(item) for item in value["metrics"]),
            value["aggregate_score"], value["fitness_digest"],
        )


@dataclass(frozen=True, slots=True)
class FitnessEvaluation:
    """Canonical ordered fitness evaluation for one accepted population."""

    policy_digest: str
    results: tuple[CandidateFitness, ...]
    evaluation_digest: str

    def __post_init__(self) -> None:
        _sha(self.policy_digest, "fitness evaluation policy digest")
        if type(self.results) is not tuple or not self.results:
            raise FitnessMetricError("fitness evaluation results are missing")
        if any(not isinstance(item, CandidateFitness) for item in self.results):
            raise FitnessMetricError("fitness evaluation results are malformed")
        candidate_ids = tuple(item.candidate_id for item in self.results)
        if len(set(candidate_ids)) != len(candidate_ids):
            raise FitnessMetricError("fitness evaluation results contain duplicate candidate IDs")
        lineage_digests = tuple(item.lineage_digest for item in self.results)
        if len(set(lineage_digests)) != len(lineage_digests):
            raise FitnessMetricError("fitness evaluation results contain duplicate lineage identities")
        if self.policy_digest != FitnessPolicy().digest():
            raise FitnessMetricError("fitness evaluation policy is unsupported")
        if any(item.policy_digest != self.policy_digest for item in self.results):
            raise FitnessMetricError("fitness results have mismatched policy bindings")
        if candidate_ids != tuple(sorted(candidate_ids)):
            raise FitnessMetricError("fitness results are not canonically ordered")
        _sha(self.evaluation_digest, "fitness evaluation digest")
        if self.evaluation_digest != _digest(self._payload_dict()):
            raise FitnessMetricError("fitness evaluation digest does not bind its payload")

    def _payload_dict(self) -> dict[str, object]:
        return {
            "schema": FITNESS_SCHEMA,
            "version": FITNESS_VERSION,
            "policy_digest": self.policy_digest,
            "results": [item.canonical_dict() for item in self.results],
        }

    def canonical_dict(self) -> dict[str, object]:
        return {**self._payload_dict(), "evaluation_digest": self.evaluation_digest}

    def for_candidate(
        self,
        candidate: CandidateEvidence,
        policy: FitnessPolicy,
        artifacts: Mapping[str, bytes],
    ) -> CandidateFitness:
        """Retrieve a result only after exact artifact-bound recomputation."""

        if policy.digest() != self.policy_digest:
            raise FitnessMetricError("fitness evaluation policy binding is stale")
        match = next((item for item in self.results if item.candidate_id == candidate.candidate_id), None)
        if match is None or match.lineage_digest != candidate.lineage_digest:
            raise FitnessMetricError("fitness result is missing or bound to another candidate")
        return validate_fitness_result(candidate, match, policy, artifacts)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "FitnessEvaluation":
        required = {"schema", "version", "policy_digest", "results", "evaluation_digest"}
        if set(value) != required or value["schema"] != FITNESS_SCHEMA or value["version"] != FITNESS_VERSION:
            raise FitnessMetricError("fitness evaluation fields are unsupported or incomplete")
        return cls(value["policy_digest"], tuple(CandidateFitness.from_dict(item) for item in value["results"]), value["evaluation_digest"])


def _normalize_candidates(candidates: Sequence[CandidateEvidence]) -> tuple[CandidateEvidence, ...]:
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes, bytearray)):
        raise FitnessMetricError("fitness candidates must be a sequence of accepted evidence")
    normalized = tuple(candidates)
    if any(not isinstance(candidate, CandidateEvidence) for candidate in normalized):
        raise FitnessMetricError("fitness candidates contain unavailable or malformed evidence")
    ordered = tuple(sorted(normalized, key=lambda item: (item.candidate_id, item.lineage_digest)))
    if len({item.candidate_id for item in ordered}) != len(ordered):
        raise FitnessMetricError("fitness candidates contain duplicate identity")
    if len({item.lineage_digest for item in ordered}) != len(ordered):
        raise FitnessMetricError("fitness candidates contain cross-candidate lineage collision")
    if len({item.bundle_digest for item in ordered}) != len(ordered):
        raise FitnessMetricError("fitness candidates contain duplicate accepted bundle identity")
    if len({item.generation_result_digest for item in ordered}) != len(ordered):
        raise FitnessMetricError("fitness candidates contain duplicate accepted generation identity")
    seen: dict[str, dict[str, str]] = {field: {} for pair in FITNESS_ARTIFACT_IDENTITY_FIELDS for field in pair}
    for candidate in ordered:
        for reference_field, digest_field in FITNESS_ARTIFACT_IDENTITY_FIELDS:
            reference = getattr(candidate, reference_field)
            digest = getattr(candidate, digest_field)
            if reference is None and digest is None:
                continue
            if reference is None or digest is None:
                raise FitnessMetricError(f"candidate-specific artifact identity is incomplete for {reference_field}")
            for field, value in ((reference_field, reference), (digest_field, digest)):
                prior = seen[field].get(value)
                if prior is not None and prior != candidate.candidate_id:
                    raise FitnessMetricError(f"cross-candidate {field} identity collision")
                seen[field][value] = candidate.candidate_id
    return ordered


def evaluate_fitness(
    candidates: Sequence[CandidateEvidence],
    policy: FitnessPolicy,
    artifacts: Mapping[str, bytes],
) -> FitnessEvaluation:
    """Evaluate finite evidence-only fitness and return an immutable receipt."""

    if not isinstance(policy, FitnessPolicy):
        raise FitnessMetricError("fitness policy is malformed")
    if not isinstance(artifacts, Mapping):
        raise FitnessMetricError("canonical artifact bytes are unavailable")
    normalized = _normalize_candidates(candidates)
    computed: list[CandidateFitness] = []
    for candidate in normalized:
        try:
            verified = verify_artifact_set(candidate, artifacts)
        except (M08ContractError, TypeError, AttributeError) as exc:
            raise FitnessMetricError(str(exc) or "canonical artifact evidence is unavailable or stale") from exc
        verified_references = set(verified["verified_references"])
        coverage = (len(verified_references) * FITNESS_SCORE_SCALE) // len(FITNESS_ARTIFACT_IDENTITY_FIELDS)
        optional_pairs = sum(
            getattr(candidate, reference_field) is not None and getattr(candidate, reference_field) in verified_references
            for reference_field, _ in _OPTIONAL_ARTIFACT_PAIRS
        )
        optional_coverage = (optional_pairs * FITNESS_SCORE_SCALE) // len(_OPTIONAL_ARTIFACT_PAIRS)
        values = (
            FitnessMetricValue("artifact_identity_coverage", coverage),
            FitnessMetricValue("optional_artifact_coverage", optional_coverage),
        )
        aggregate_score = policy.aggregate({item.metric_id: item.normalized_value for item in values})
        payload = {
            "schema": FITNESS_SCHEMA,
            "version": FITNESS_VERSION,
            "candidate_id": candidate.candidate_id,
            "lineage_digest": candidate.lineage_digest,
            "policy_digest": policy.digest(),
            "metrics": [item.canonical_dict() for item in values],
            "aggregate_score": aggregate_score,
        }
        computed.append(CandidateFitness(
            candidate.candidate_id,
            candidate.lineage_digest,
            policy.digest(),
            values,
            aggregate_score,
            _digest(payload),
        ))
    results = tuple(computed)
    evaluation_payload = {
        "schema": FITNESS_SCHEMA,
        "version": FITNESS_VERSION,
        "policy_digest": policy.digest(),
        "results": [item.canonical_dict() for item in results],
    }
    return FitnessEvaluation(policy.digest(), results, _digest(evaluation_payload))


def validate_fitness_result(
    candidate: CandidateEvidence,
    result: CandidateFitness,
    policy: FitnessPolicy,
    artifacts: Mapping[str, bytes],
) -> CandidateFitness:
    """Recompute one result and fail closed on forged, stale, or cross-bound data."""

    if not isinstance(candidate, CandidateEvidence) or not isinstance(result, CandidateFitness):
        raise FitnessMetricError("fitness result input is malformed")
    expected = evaluate_fitness((candidate,), policy, artifacts).results[0]
    if result.canonical_dict() != expected.canonical_dict():
        raise FitnessMetricError("fitness result is forged, stale, or bound to another candidate")
    return result


__all__ = [
    "CandidateFitness",
    "DEFAULT_FITNESS_METRIC_CATALOG",
    "FITNESS_AGGREGATION",
    "FITNESS_ARTIFACT_IDENTITY_FIELDS",
    "FITNESS_POLICY_VERSION",
    "FITNESS_SCHEMA",
    "FITNESS_SCORE_SCALE",
    "FITNESS_VERSION",
    "FitnessEvaluation",
    "FitnessMetricDefinition",
    "FitnessMetricError",
    "FitnessMetricValue",
    "FitnessPolicy",
    "evaluate_fitness",
    "validate_fitness_result",
]
