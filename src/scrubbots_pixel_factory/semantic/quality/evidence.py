"""Strict durable evidence and explicit acceptance gate for SP06 quality."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from types import MappingProxyType
from typing import Any, Mapping

from ...contracts import CANONICAL_PALETTE
from ..normalization.level_art import SemanticLevelArtArtifact
from .core import (
    RecognizabilityDisposition,
    SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION,
    SemanticQualityAssessment,
    SemanticQualityError,
    _canonical_bytes,
    _request_digest,
    assess_semantic_quality,
)


SEMANTIC_QUALITY_EVIDENCE_SCHEMA = "scrubbots-semantic-quality-evidence"
SEMANTIC_QUALITY_EVIDENCE_SCHEMA_VERSION = 1
_EVIDENCE_TOKEN = object()
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_EVIDENCE_KEYS = frozenset(
    {
        "schema",
        "schema_version",
        "trusted_artifact_digest",
        "final_logical_grid_digest",
        "target_dimensions",
        "final_used_palette_ids",
        "final_used_color_count",
        "diagnostic_policy_version",
        "diagnostics",
        "diagnostics_digest",
        "structural_assessment_identity_digest",
        "semantic_request_digest",
        "review_disposition",
        "reviewer",
        "review_reason",
        "review_notes",
        "review_identity_digest",
        "assessment_identity_digest",
    }
)
_DIAGNOSTICS_KEYS = frozenset(
    {
        "schema",
        "schema_version",
        "policy_version",
        "dimensions",
        "used_palette_ids",
        "cell_counts",
        "horizontal_transition_count",
        "vertical_transition_count",
        "total_adjacency_edge_count",
        "transition_density",
        "component_counts",
        "total_component_count",
        "singleton_component_count",
        "largest_component_sizes",
        "largest_component_shares",
    }
)


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require_digest(value: object, label: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise SemanticQualityError("INVALID_EVIDENCE", f"{label} must be a lowercase SHA-256 digest")
    return value


def _freeze(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise SemanticQualityError("INVALID_EVIDENCE", f"{label} must be an object")
    return value  # type: ignore[return-value]


def _strict_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SemanticQualityError("DUPLICATE_FIELD", f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> object:
    raise SemanticQualityError("INVALID_JSON", f"non-finite JSON constant is not allowed: {value}")


@dataclass(frozen=True, slots=True)
class SemanticQualityEvidenceRecord:
    """Immutable canonical evidence exported from one C001 assessment."""

    trusted_artifact_digest: str
    final_logical_grid_digest: str
    target_width: int
    target_height: int
    final_used_palette_ids: tuple[str, ...]
    final_used_color_count: int
    diagnostic_policy_version: str
    diagnostics: Mapping[str, object]
    diagnostics_digest: str
    structural_assessment_identity_digest: str
    semantic_request_digest: str | None
    review_disposition: RecognizabilityDisposition
    reviewer: str
    review_reason: str
    review_notes: str
    review_identity_digest: str
    assessment_identity_digest: str
    schema: str = SEMANTIC_QUALITY_EVIDENCE_SCHEMA
    schema_version: int = SEMANTIC_QUALITY_EVIDENCE_SCHEMA_VERSION
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _EVIDENCE_TOKEN:
            raise SemanticQualityError("UNSEALED_EVIDENCE", "evidence requires canonical checked construction")
        self._validate_values()
        object.__setattr__(self, "_construction_fingerprint", self._fingerprint())

    def _validate_values(self) -> None:
        if self.schema != SEMANTIC_QUALITY_EVIDENCE_SCHEMA or self.schema_version != SEMANTIC_QUALITY_EVIDENCE_SCHEMA_VERSION:
            raise SemanticQualityError("UNSUPPORTED_SCHEMA", "unsupported semantic-quality evidence schema/version")
        _require_digest(self.trusted_artifact_digest, "trusted_artifact_digest")
        _require_digest(self.final_logical_grid_digest, "final_logical_grid_digest")
        _require_digest(self.diagnostics_digest, "diagnostics_digest")
        _require_digest(self.structural_assessment_identity_digest, "structural_assessment_identity_digest")
        _require_digest(self.review_identity_digest, "review_identity_digest")
        _require_digest(self.assessment_identity_digest, "assessment_identity_digest")
        if type(self.target_width) is not int or type(self.target_height) is not int or self.target_width < 1 or self.target_height < 1:
            raise SemanticQualityError("INVALID_EVIDENCE", "target dimensions must be positive integers")
        ids = tuple(self.final_used_palette_ids)
        if not ids or len(ids) != len(set(ids)) or ids != tuple(sorted(ids, key=lambda value: _palette_index(value))):
            raise SemanticQualityError("INVALID_EVIDENCE", "final used palette IDs are not unique canonical IDs")
        if type(self.final_used_color_count) is not int or self.final_used_color_count != len(ids):
            raise SemanticQualityError("INVALID_EVIDENCE", "final used color count is inconsistent")
        if self.diagnostic_policy_version != SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION:
            raise SemanticQualityError("UNSUPPORTED_POLICY", "unsupported diagnostic policy version")
        if not isinstance(self.diagnostics, Mapping):
            raise SemanticQualityError("INVALID_EVIDENCE", "diagnostics must be an immutable mapping")
        try:
            disposition = RecognizabilityDisposition(self.review_disposition)
        except Exception as exc:
            raise SemanticQualityError("INVALID_DISPOSITION", "unsupported review disposition") from exc
        if not all(isinstance(value, str) for value in (self.reviewer, self.review_reason, self.review_notes)):
            raise SemanticQualityError("INVALID_EVIDENCE", "review evidence fields must be strings")
        if disposition in (RecognizabilityDisposition.ACCEPT, RecognizabilityDisposition.REJECT) and (not self.reviewer.strip() or not self.review_reason.strip()):
            raise SemanticQualityError("REVIEW_EVIDENCE_REQUIRED", "ACCEPT and REJECT require non-empty reviewer and reason")
        if self.semantic_request_digest is not None:
            _require_digest(self.semantic_request_digest, "semantic_request_digest")
        object.__setattr__(self, "final_used_palette_ids", ids)
        object.__setattr__(self, "review_disposition", disposition)

    def _payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "trusted_artifact_digest": self.trusted_artifact_digest,
            "final_logical_grid_digest": self.final_logical_grid_digest,
            "target_dimensions": {"width": self.target_width, "height": self.target_height},
            "final_used_palette_ids": list(self.final_used_palette_ids),
            "final_used_color_count": self.final_used_color_count,
            "diagnostic_policy_version": self.diagnostic_policy_version,
            "diagnostics": _thaw(self.diagnostics),
            "diagnostics_digest": self.diagnostics_digest,
            "structural_assessment_identity_digest": self.structural_assessment_identity_digest,
            "semantic_request_digest": self.semantic_request_digest,
            "review_disposition": self.review_disposition.value,
            "reviewer": self.reviewer,
            "review_reason": self.review_reason,
            "review_notes": self.review_notes,
            "review_identity_digest": self.review_identity_digest,
            "assessment_identity_digest": self.assessment_identity_digest,
        }

    def _fingerprint(self) -> str:
        return _digest(self._payload())

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _EVIDENCE_TOKEN:
            raise SemanticQualityError("UNSEALED_EVIDENCE", "evidence construction seal is invalid")
        self._validate_values()
        if getattr(self, "_construction_fingerprint", None) != self._fingerprint():
            raise SemanticQualityError("TAMPERED_EVIDENCE", "evidence construction fingerprint is invalid")

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return self._payload()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())

    @classmethod
    def from_assessment(cls, assessment: SemanticQualityAssessment) -> "SemanticQualityEvidenceRecord":
        return export_semantic_quality_evidence(assessment)


def _palette_index(value: str) -> int:
    try:
        return CANONICAL_PALETTE.color(value).index
    except Exception as exc:
        raise SemanticQualityError("INVALID_EVIDENCE", f"unknown logical palette ID: {value!r}") from exc


def _build_record(assessment: SemanticQualityAssessment) -> SemanticQualityEvidenceRecord:
    instance = object.__new__(SemanticQualityEvidenceRecord)
    values: dict[str, Any] = {
        "trusted_artifact_digest": assessment.trusted_artifact_digest,
        "final_logical_grid_digest": assessment.final_logical_grid_digest,
        "target_width": assessment.target_width,
        "target_height": assessment.target_height,
        "final_used_palette_ids": tuple(assessment.final_used_palette_ids),
        "final_used_color_count": assessment.final_used_color_count,
        "diagnostic_policy_version": assessment.diagnostic_policy_version,
        "diagnostics": _freeze(assessment.diagnostics.canonical_dict()),
        "diagnostics_digest": assessment.diagnostic_digest,
        "structural_assessment_identity_digest": assessment.structural_identity_digest,
        "semantic_request_digest": assessment.semantic_request_digest,
        "review_disposition": assessment.review.disposition,
        "reviewer": assessment.review.reviewer,
        "review_reason": assessment.review.reason,
        "review_notes": assessment.review.notes,
        "review_identity_digest": assessment.review.digest(),
        "assessment_identity_digest": assessment.identity_digest,
        "schema": SEMANTIC_QUALITY_EVIDENCE_SCHEMA,
        "schema_version": SEMANTIC_QUALITY_EVIDENCE_SCHEMA_VERSION,
        "_construction_token": _EVIDENCE_TOKEN,
    }
    for key, value in values.items():
        object.__setattr__(instance, key, value)
    instance._validate_values()
    object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
    return instance


def export_semantic_quality_evidence(assessment: SemanticQualityAssessment) -> SemanticQualityEvidenceRecord:
    """Export only an intact assessment into deterministic durable evidence."""

    if not isinstance(assessment, SemanticQualityAssessment):
        raise SemanticQualityError("INVALID_ASSESSMENT", "evidence export requires a SemanticQualityAssessment")
    assessment._assert_integrity()
    return _build_record(assessment)


def _parse_json(value: bytes | str) -> dict[str, object]:
    raw = value if isinstance(value, bytes) else value.encode("utf-8")
    try:
        text = raw.decode("utf-8")
        parsed = json.loads(text, object_pairs_hook=_strict_pairs, parse_constant=_reject_constant)
    except SemanticQualityError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SemanticQualityError("INVALID_JSON", "evidence is not valid UTF-8 canonical JSON") from exc
    if type(parsed) is not dict:
        raise SemanticQualityError("INVALID_EVIDENCE", "evidence root must be a JSON object")
    if _canonical_bytes(parsed) != raw:
        raise SemanticQualityError("NON_CANONICAL_JSON", "evidence JSON is not the canonical byte representation")
    return parsed


def _validate_diagnostics_shape(value: object) -> dict[str, object]:
    diagnostics = _mapping(value, "diagnostics")
    if set(diagnostics) != _DIAGNOSTICS_KEYS:
        raise SemanticQualityError("INVALID_EVIDENCE", "diagnostics fields are missing or unknown")
    dimensions = _mapping(diagnostics.get("dimensions"), "diagnostics.dimensions")
    if set(dimensions) != {"width", "height"} or type(dimensions["width"]) is not int or type(dimensions["height"]) is not int:
        raise SemanticQualityError("INVALID_EVIDENCE", "diagnostic dimensions are malformed")
    ids = diagnostics.get("used_palette_ids")
    if type(ids) is not list or any(type(value) is not str for value in ids):
        raise SemanticQualityError("INVALID_EVIDENCE", "diagnostic palette IDs are malformed")
    for mapping_name in ("cell_counts", "component_counts", "largest_component_sizes", "largest_component_shares"):
        mapping = _mapping(diagnostics.get(mapping_name), f"diagnostics.{mapping_name}")
        if any(type(key) is not str for key in mapping):
            raise SemanticQualityError("INVALID_EVIDENCE", f"diagnostics.{mapping_name} keys are malformed")
    transition_density = _mapping(diagnostics.get("transition_density"), "diagnostics.transition_density")
    if set(transition_density) != {"numerator", "denominator"} or any(type(transition_density[key]) is not int for key in transition_density):
        raise SemanticQualityError("INVALID_EVIDENCE", "diagnostic transition density is malformed")
    for key in ("schema", "policy_version"):
        if type(diagnostics.get(key)) is not str:
            raise SemanticQualityError("INVALID_EVIDENCE", f"diagnostics.{key} is malformed")
    if type(diagnostics.get("schema_version")) is not int:
        raise SemanticQualityError("INVALID_EVIDENCE", "diagnostics.schema_version is malformed")
    for key in ("horizontal_transition_count", "vertical_transition_count", "total_adjacency_edge_count", "total_component_count", "singleton_component_count"):
        if type(diagnostics.get(key)) is not int:
            raise SemanticQualityError("INVALID_EVIDENCE", f"diagnostics.{key} is malformed")
    return dict(diagnostics)


def _parse_payload(evidence: SemanticQualityEvidenceRecord | bytes | str | Mapping[str, object]) -> dict[str, object]:
    if isinstance(evidence, SemanticQualityEvidenceRecord):
        evidence._assert_integrity()
        return evidence.canonical_dict()
    if isinstance(evidence, (bytes, str)):
        payload = _parse_json(evidence)
    elif type(evidence) is dict:
        payload = dict(evidence)
    else:
        raise SemanticQualityError("INVALID_EVIDENCE", "evidence must be a record, canonical JSON bytes/text, or plain dict")
    if set(payload) != _EVIDENCE_KEYS:
        raise SemanticQualityError("INVALID_EVIDENCE", "evidence fields are missing or unknown")
    if payload["schema"] != SEMANTIC_QUALITY_EVIDENCE_SCHEMA or payload["schema_version"] != SEMANTIC_QUALITY_EVIDENCE_SCHEMA_VERSION:
        raise SemanticQualityError("UNSUPPORTED_SCHEMA", "unsupported semantic-quality evidence schema/version")
    for key in ("schema", "diagnostic_policy_version", "review_disposition", "reviewer", "review_reason", "review_notes"):
        if type(payload[key]) is not str:
            raise SemanticQualityError("INVALID_EVIDENCE", f"{key} must be a string")
    if type(payload["schema_version"]) is not int or type(payload["final_used_color_count"]) is not int:
        raise SemanticQualityError("INVALID_EVIDENCE", "integer evidence fields are malformed")
    dimensions = _mapping(payload["target_dimensions"], "target_dimensions")
    if set(dimensions) != {"width", "height"} or type(dimensions["width"]) is not int or type(dimensions["height"]) is not int:
        raise SemanticQualityError("INVALID_EVIDENCE", "target dimensions are malformed")
    ids = payload["final_used_palette_ids"]
    if type(ids) is not list or any(type(value) is not str for value in ids):
        raise SemanticQualityError("INVALID_EVIDENCE", "final used palette IDs are malformed")
    for value in ids:
        _palette_index(value)
    if len(ids) != len(set(ids)) or payload["final_used_color_count"] != len(ids):
        raise SemanticQualityError("INVALID_EVIDENCE", "final used palette facts are inconsistent")
    for key in ("trusted_artifact_digest", "final_logical_grid_digest", "diagnostics_digest", "structural_assessment_identity_digest", "review_identity_digest", "assessment_identity_digest"):
        _require_digest(payload[key], key)
    if payload["semantic_request_digest"] is not None:
        _require_digest(payload["semantic_request_digest"], "semantic_request_digest")
    try:
        disposition = RecognizabilityDisposition(payload["review_disposition"])
    except Exception as exc:
        raise SemanticQualityError("INVALID_DISPOSITION", "unsupported review disposition") from exc
    if disposition in (RecognizabilityDisposition.ACCEPT, RecognizabilityDisposition.REJECT) and (not payload["reviewer"].strip() or not payload["review_reason"].strip()):
        raise SemanticQualityError("REVIEW_EVIDENCE_REQUIRED", "ACCEPT and REJECT require non-empty reviewer and reason")
    payload["diagnostics"] = _validate_diagnostics_shape(payload["diagnostics"])
    return payload


def load_semantic_quality_evidence(
    evidence: SemanticQualityEvidenceRecord | bytes | str | Mapping[str, object],
    artifact: SemanticLevelArtArtifact,
    expected_semantic_request: object | None = None,
) -> SemanticQualityAssessment:
    """Strictly reload evidence by recomputing and cross-binding a trusted artifact."""

    payload = _parse_payload(evidence)
    if not isinstance(artifact, SemanticLevelArtArtifact):
        raise SemanticQualityError("UNTRUSTED_ARTIFACT", "evidence reload requires a trusted LEVEL_ART artifact")
    stored_request_digest = payload["semantic_request_digest"]
    expected_request_digest = _request_digest(expected_semantic_request)
    if expected_request_digest != stored_request_digest and (expected_request_digest is not None or stored_request_digest is not None):
        raise SemanticQualityError("SEMANTIC_REQUEST_MISMATCH", "evidence semantic-request identity does not match the expected identity")
    fresh = assess_semantic_quality(artifact, stored_request_digest)
    expected_record = _build_record(fresh)
    expected_payload = expected_record.canonical_dict()
    expected_disposition = RecognizabilityDisposition(payload["review_disposition"])
    try:
        reconstructed = fresh.with_review(expected_disposition, payload["reviewer"], payload["review_reason"], payload["review_notes"])
    except SemanticQualityError:
        raise
    except Exception as exc:
        raise SemanticQualityError("INVALID_EVIDENCE", "stored review could not be reconstructed") from exc
    rebuilt_payload = _build_record(reconstructed).canonical_dict()
    # Compare all artifact, diagnostic and structural fields before returning a
    # trusted assessment. A record can be well-formed yet bound to another grid.
    if payload["diagnostics"] != expected_payload["diagnostics"]:
        raise SemanticQualityError("DIAGNOSTICS_MISMATCH", "stored diagnostics do not match recomputed artifact diagnostics")
    if any(payload[key] != expected_payload[key] for key in ("trusted_artifact_digest", "final_logical_grid_digest", "target_dimensions", "final_used_palette_ids", "final_used_color_count", "diagnostic_policy_version", "diagnostics_digest", "structural_assessment_identity_digest")):
        raise SemanticQualityError("ARTIFACT_BINDING_MISMATCH", "stored evidence is not bound to the supplied artifact")
    if any(payload[key] != rebuilt_payload[key] for key in ("review_disposition", "reviewer", "review_reason", "review_notes", "review_identity_digest", "assessment_identity_digest")):
        raise SemanticQualityError("REVIEW_BINDING_MISMATCH", "stored review or assessment identity is not canonical")
    return reconstructed


def require_semantic_recognizability_acceptance(
    evidence: SemanticQualityEvidenceRecord | bytes | str | Mapping[str, object],
    artifact: SemanticLevelArtArtifact,
    expected_semantic_request: object | None = None,
) -> SemanticQualityAssessment:
    """Return a verified assessment only when its explicit disposition is ACCEPT."""

    assessment = load_semantic_quality_evidence(evidence, artifact, expected_semantic_request)
    if not assessment.passes:
        raise SemanticQualityError("RECOGNIZABILITY_NOT_ACCEPTED", f"explicit review disposition is {assessment.disposition.value}")
    return assessment


__all__ = [
    "SEMANTIC_QUALITY_EVIDENCE_SCHEMA",
    "SEMANTIC_QUALITY_EVIDENCE_SCHEMA_VERSION",
    "SemanticQualityEvidenceRecord",
    "export_semantic_quality_evidence",
    "load_semantic_quality_evidence",
    "require_semantic_recognizability_acceptance",
]
