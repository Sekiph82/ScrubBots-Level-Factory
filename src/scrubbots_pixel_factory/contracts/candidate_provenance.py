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

    This metadata projection is not source authority. Ordinary generated
    bundles, including bundles carrying owner-upload-shaped caller metadata,
    remain TEST here. The export boundary can elevate a verified owner-upload
    derivation only after it reads the canonical source record and proves the
    exported logical grid equals the decoded source bytes. Release Pool still
    requires a separate valid owner ACCEPT.
    """

    request = _mapping(result.get("request"), "generation request")
    generator = _mapping(result.get("generator"), "generation identity")
    rng = _mapping(result.get("rng"), "generation RNG")
    rng_provenance = _mapping(rng.get("provenance"), "generation RNG provenance")
    if not candidate_id or not _SHA256.fullmatch(grid_hash):
        raise CandidateProvenanceError("candidate identity or logical source hash is invalid")
    request_hash = _digest(request)
    generation_payload = _mapping(generator_metadata or {}, "generator metadata")
    candidate_class = CandidateClass.TEST
    source_hash = grid_hash
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


def build_verified_owner_upload_classification(
    result: Mapping[str, Any],
    *,
    candidate_id: str,
    grid_hash: str,
    generator_metadata: Mapping[str, Any],
    verified_source_sha256: str,
) -> dict[str, object]:
    """Project production-candidate class after a caller verified source bytes/grid."""

    if not _SHA256.fullmatch(verified_source_sha256):
        raise CandidateProvenanceError("verified owner-upload source hash is malformed")
    request = _mapping(result.get("request"), "generation request")
    request_seed = _mapping(request.get("seed"), "generation request seed")
    generator = _mapping(result.get("generator"), "generation identity")
    data = _mapping(generator_metadata.get("data"), "generator metadata data")
    lineage = _mapping(data.get("source_lineage"), "owner-upload source lineage")
    if (
        generator_metadata.get("namespace") != "owner-upload"
        or lineage.get("source_id") != f"owner-upload-{verified_source_sha256}"
        or lineage.get("source_sha256") != verified_source_sha256
        or lineage.get("derivation") != "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE"
        or lineage.get("source_bytes_unchanged") is not True
        or request_seed.get("type") != "string"
        or request_seed.get("value") != verified_source_sha256
        or request.get("generator_mode") != "MASK"
        or generator.get("id") != "owner-upload-canonical-derive"
        or generator.get("version") != "1"
        or candidate_id != f"candidate-owner-{verified_source_sha256[:48]}"
    ):
        raise CandidateProvenanceError("owner-upload classification does not match verified source evidence")
    classification = build_candidate_classification(
        result,
        candidate_id=candidate_id,
        grid_hash=grid_hash,
        generator_metadata=generator_metadata,
    )
    classification["candidate_class"] = CandidateClass.PRODUCTION_CANDIDATE.value
    classification["source_sha256"] = verified_source_sha256
    return classification


def validate_verified_owner_upload_classification(
    value: object,
    result: Mapping[str, Any],
    *,
    candidate_id: str,
    grid_hash: str,
    generator_metadata: Mapping[str, Any],
    verified_source_sha256: str,
) -> CandidateClass:
    """Validate the classification projection against caller-verified source evidence."""

    actual = _mapping(value, "candidate classification")
    expected = build_verified_owner_upload_classification(
        result,
        candidate_id=candidate_id,
        grid_hash=grid_hash,
        generator_metadata=generator_metadata,
        verified_source_sha256=verified_source_sha256,
    )
    if dict(actual) != expected:
        raise CandidateProvenanceError("owner-upload classification does not match verified source evidence")
    return CandidateClass.PRODUCTION_CANDIDATE


__all__ = [
    "CANDIDATE_CLASSIFICATION_SCHEMA",
    "CANDIDATE_CLASSIFICATION_VERSION",
    "CandidateClass",
    "CandidateProvenanceError",
    "build_candidate_classification",
    "validate_candidate_classification",
]
