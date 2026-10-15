"""Typed candidate classification bound to deterministic generation evidence."""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
import hashlib
import json
import re
from typing import Any


CANDIDATE_CLASSIFICATION_SCHEMA = "scrubbots-candidate-classification"
CANDIDATE_CLASSIFICATION_VERSION = 1
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class CandidateClass(str, Enum):
    TEST = "TEST"
    DEVELOPMENT = "DEVELOPMENT"
    PREVIEW = "PREVIEW"
    PRODUCTION_CANDIDATE = "PRODUCTION_CANDIDATE"
    UNAVAILABLE = "UNAVAILABLE"


class CandidateProvenanceError(ValueError):
    """Raised when candidate class cannot be bound to canonical evidence."""


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CandidateProvenanceError(f"{label} must be an object")
    return value


def _digest(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_candidate_classification(
    result: Mapping[str, Any],
    *,
    candidate_id: str,
    grid_hash: str,
    generator_metadata: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Classify a bundle from its actual request and source lineage.

    Ordinary generated bundles are TEST by default. Only the exact owner-upload
    derivation receives PRODUCTION_CANDIDATE; it still requires a separate valid
    owner ACCEPT at the Release Pool boundary.
    """

    request = _mapping(result.get("request"), "generation request")
    generator = _mapping(result.get("generator"), "generation identity")
    rng = _mapping(result.get("rng"), "generation RNG")
    rng_provenance = _mapping(rng.get("provenance"), "generation RNG provenance")
    if not candidate_id or not _SHA256.fullmatch(grid_hash):
        raise CandidateProvenanceError("candidate identity or logical source hash is invalid")
    request_hash = _digest(request)
    generation_payload = _mapping(generator_metadata or {}, "generator metadata")
    data = generation_payload.get("data", {})
    data = _mapping(data, "generator metadata data")
    lineage = data.get("source_lineage")
    candidate_class = CandidateClass.TEST
    source_hash = grid_hash
    if generation_payload.get("namespace") == "owner-upload":
        lineage = _mapping(lineage, "owner-upload source lineage")
        if (lineage.get("derivation") != "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE"
                or lineage.get("source_bytes_unchanged") is not True
                or type(lineage.get("source_id")) is not str
                or not lineage.get("source_id")
                or type(lineage.get("source_sha256")) is not str
                or _SHA256.fullmatch(lineage["source_sha256"]) is None
                or lineage["source_sha256"] != str(_mapping(request.get("seed"), "generation request seed").get("value", ""))
                or generator.get("id") != "owner-upload-canonical-derive"
                or generator.get("version") != "1"
                or request.get("generator_mode") != "MASK"
                or candidate_id != f"candidate-owner-{lineage['source_sha256'][:48]}"):
            raise CandidateProvenanceError("owner-upload classification lacks exact request-bound source lineage")
        candidate_class = CandidateClass.PRODUCTION_CANDIDATE
        source_hash = lineage["source_sha256"]
    retry_seeds = rng_provenance.get("retry_seeds", {})
    if not isinstance(retry_seeds, Mapping):
        raise CandidateProvenanceError("retry attempt provenance is malformed")
    attempt = max((int(key) for key in retry_seeds if type(key) is str and key.isdigit()), default=0)
    return {
        "schema": CANDIDATE_CLASSIFICATION_SCHEMA,
        "version": CANDIDATE_CLASSIFICATION_VERSION,
        "candidate_class": candidate_class.value,
        "candidate_id": candidate_id,
        "attempt_id": f"{candidate_id}:attempt:{attempt}",
        "request_id": f"request-{request_hash[:24]}",
        "request_sha256": request_hash,
        "source_sha256": source_hash,
        "generator_id": generator.get("id"),
        "generator_version": generator.get("version"),
        "seed": result.get("seed"),
    }


def validate_candidate_classification(
    value: object,
    result: Mapping[str, Any],
    *,
    candidate_id: str,
    grid_hash: str,
    generator_metadata: Mapping[str, Any] | None = None,
) -> CandidateClass:
    actual = _mapping(value, "candidate classification")
    expected = build_candidate_classification(
        result,
        candidate_id=candidate_id,
        grid_hash=grid_hash,
        generator_metadata=generator_metadata,
    )
    if dict(actual) != expected:
        raise CandidateProvenanceError("candidate classification does not match request, source, generator, attempt, and candidate identity")
    return CandidateClass(expected["candidate_class"])


__all__ = [
    "CANDIDATE_CLASSIFICATION_SCHEMA",
    "CANDIDATE_CLASSIFICATION_VERSION",
    "CandidateClass",
    "CandidateProvenanceError",
    "build_candidate_classification",
    "validate_candidate_classification",
]
