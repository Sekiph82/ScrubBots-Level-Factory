"""Deterministic structural quality facts and explicit recognizability review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import re
from typing import Any, Sequence

from ...contracts import CANONICAL_PALETTE
from ..normalization.core import _canonical_bytes
from ..normalization.level_art import SemanticLevelArtArtifact


SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA = "scrubbots-semantic-quality-diagnostics"
SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA_VERSION = 1
SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION = "SEMANTIC_STRUCTURAL_DIAGNOSTICS_V1"
SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA = "scrubbots-semantic-recognizability-review"
SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA_VERSION = 1
SEMANTIC_QUALITY_ASSESSMENT_SCHEMA = "scrubbots-semantic-quality-assessment"
SEMANTIC_QUALITY_ASSESSMENT_SCHEMA_VERSION = 1
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DIAGNOSTICS_TOKEN = object()
_REVIEW_TOKEN = object()
_ASSESSMENT_TOKEN = object()


class SemanticQualityError(ValueError):
    """Raised when a quality fact, review, or assessment is not trustworthy."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


class RecognizabilityDisposition(str, Enum):
    """A human review state; structural metrics never select this state."""

    UNREVIEWED = "UNREVIEWED"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require_digest(value: object, label: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise SemanticQualityError("INVALID_DIGEST", f"{label} must be a lowercase SHA-256 digest")
    return value


def _palette_key(value: str) -> int:
    try:
        return CANONICAL_PALETTE.color(value).index
    except Exception as exc:
        raise SemanticQualityError("INVALID_LOGICAL_GRID", f"unknown logical palette ID: {value!r}") from exc


def _validate_cells(cells: Sequence[str], width: int, height: int) -> tuple[str, ...]:
    if type(width) is not int or type(height) is not int or width < 1 or height < 1:
        raise SemanticQualityError("INVALID_DIMENSIONS", "diagnostic dimensions must be positive integers")
    try:
        frozen = tuple(cells)
    except TypeError as exc:
        raise SemanticQualityError("INVALID_LOGICAL_GRID", "diagnostics require row-major logical cells") from exc
    if len(frozen) != width * height:
        raise SemanticQualityError("INVALID_LOGICAL_GRID", "cell count does not match dimensions")
    for value in frozen:
        _palette_key(value)
    return frozen


def _component_sizes(cells: tuple[str, ...], width: int, height: int, palette_id: str) -> tuple[int, ...]:
    visited: set[int] = set()
    sizes: list[int] = []
    for start, value in enumerate(cells):
        if value != palette_id or start in visited:
            continue
        visited.add(start)
        pending = [start]
        size = 0
        while pending:
            index = pending.pop()
            size += 1
            x, y = index % width, index // width
            for neighbor in (
                index - 1 if x else -1,
                index + 1 if x + 1 < width else -1,
                index - width if y else -1,
                index + width if y + 1 < height else -1,
            ):
                if neighbor >= 0 and neighbor not in visited and cells[neighbor] == palette_id:
                    visited.add(neighbor)
                    pending.append(neighbor)
        sizes.append(size)
    return tuple(sizes)


@dataclass(frozen=True, slots=True)
class SemanticQualityDiagnostics:
    """Sealed, deterministic structural facts derived from logical cells."""

    width: int
    height: int
    used_palette_ids: tuple[str, ...]
    cell_counts: tuple[tuple[str, int], ...]
    horizontal_transition_count: int
    vertical_transition_count: int
    total_adjacency_edge_count: int
    transition_density_numerator: int
    transition_density_denominator: int
    component_counts: tuple[tuple[str, int], ...]
    total_component_count: int
    singleton_component_count: int
    largest_component_sizes: tuple[tuple[str, int], ...]
    largest_component_shares: tuple[tuple[str, int, int], ...]
    schema: str = SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA
    schema_version: int = SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA_VERSION
    policy_version: str = SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _DIAGNOSTICS_TOKEN:
            raise SemanticQualityError("UNSEALED_DIAGNOSTICS", "diagnostics require canonical checked construction")
        self._validate_values()
        object.__setattr__(self, "_construction_fingerprint", self._fingerprint())

    def _validate_values(self) -> None:
        if self.schema != SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA or self.schema_version != SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA_VERSION:
            raise SemanticQualityError("UNSUPPORTED_SCHEMA", "unsupported diagnostics schema/version")
        if self.policy_version != SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION:
            raise SemanticQualityError("UNSUPPORTED_POLICY", "unsupported diagnostics policy version")
        if type(self.width) is not int or type(self.height) is not int or self.width < 1 or self.height < 1:
            raise SemanticQualityError("INVALID_DIMENSIONS", "diagnostics dimensions must be positive integers")
        ids = tuple(self.used_palette_ids)
        if not ids or ids != tuple(sorted(ids, key=_palette_key)) or len(set(ids)) != len(ids):
            raise SemanticQualityError("INVALID_DIAGNOSTICS", "used palette IDs must be unique canonical IDs")
        for value in ids:
            _palette_key(value)
        for name, pairs in (("cell_counts", self.cell_counts), ("component_counts", self.component_counts), ("largest_component_sizes", self.largest_component_sizes)):
            if tuple(pair[0] for pair in pairs) != ids or any(type(pair[1]) is not int or pair[1] < 0 for pair in pairs):
                raise SemanticQualityError("INVALID_DIAGNOSTICS", f"{name} are not canonical per-ID facts")
        if tuple(item[0] for item in self.largest_component_shares) != ids or any(
            type(item[1]) is not int or type(item[2]) is not int or item[1] < 0 or item[2] <= 0 or item[1] > item[2]
            for item in self.largest_component_shares
        ):
            raise SemanticQualityError("INVALID_DIAGNOSTICS", "largest component shares are not canonical ratios")
        numeric = (
            self.horizontal_transition_count,
            self.vertical_transition_count,
            self.total_adjacency_edge_count,
            self.transition_density_numerator,
            self.transition_density_denominator,
            self.total_component_count,
            self.singleton_component_count,
        )
        if any(type(value) is not int or value < 0 for value in numeric):
            raise SemanticQualityError("INVALID_DIAGNOSTICS", "diagnostic counts must be non-negative integers")
        if self.total_adjacency_edge_count != self.width * max(self.height - 1, 0) + self.height * max(self.width - 1, 0):
            raise SemanticQualityError("INVALID_DIAGNOSTICS", "adjacency edge denominator is inconsistent")
        if self.transition_density_denominator != self.total_adjacency_edge_count or self.transition_density_numerator > self.transition_density_denominator:
            raise SemanticQualityError("INVALID_DIAGNOSTICS", "transition density ratio is inconsistent")
        if sum(value for _, value in self.cell_counts) != self.width * self.height:
            raise SemanticQualityError("INVALID_DIAGNOSTICS", "per-ID cell counts do not sum to total cells")
        if sum(value for _, value in self.component_counts) != self.total_component_count:
            raise SemanticQualityError("INVALID_DIAGNOSTICS", "component counts do not sum to total")
        if self.singleton_component_count > self.total_component_count:
            raise SemanticQualityError("INVALID_DIAGNOSTICS", "singleton count exceeds component count")

    def _payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "policy_version": self.policy_version,
            "dimensions": {"width": self.width, "height": self.height},
            "used_palette_ids": list(self.used_palette_ids),
            "cell_counts": {key: value for key, value in self.cell_counts},
            "horizontal_transition_count": self.horizontal_transition_count,
            "vertical_transition_count": self.vertical_transition_count,
            "total_adjacency_edge_count": self.total_adjacency_edge_count,
            "transition_density": {"numerator": self.transition_density_numerator, "denominator": self.transition_density_denominator},
            "component_counts": {key: value for key, value in self.component_counts},
            "total_component_count": self.total_component_count,
            "singleton_component_count": self.singleton_component_count,
            "largest_component_sizes": {key: value for key, value in self.largest_component_sizes},
            "largest_component_shares": {key: {"numerator": numerator, "denominator": denominator} for key, numerator, denominator in self.largest_component_shares},
        }

    def _fingerprint(self) -> str:
        return _digest(self._payload())

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _DIAGNOSTICS_TOKEN:
            raise SemanticQualityError("UNSEALED_DIAGNOSTICS", "diagnostics construction seal is invalid")
        self._validate_values()
        if getattr(self, "_construction_fingerprint", None) != self._fingerprint():
            raise SemanticQualityError("TAMPERED_DIAGNOSTICS", "diagnostic construction fingerprint is invalid")

    @property
    def total_cell_count(self) -> int:
        return self.width * self.height

    @property
    def transition_density(self) -> tuple[int, int]:
        return self.transition_density_numerator, self.transition_density_denominator

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return self._payload()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())


def _compute_diagnostics(cells: Sequence[str], width: int, height: int) -> SemanticQualityDiagnostics:
    """Compute diagnostics from cells; this private helper also supports small hand fixtures."""

    frozen = _validate_cells(cells, width, height)
    ids = tuple(sorted(set(frozen), key=_palette_key))
    cell_counts = tuple((palette_id, frozen.count(palette_id)) for palette_id in ids)
    horizontal = sum(frozen[index] != frozen[index + 1] for y in range(height) for index in range(y * width, (y + 1) * width - 1))
    vertical = sum(frozen[index] != frozen[index + width] for y in range(height - 1) for index in range(y * width, (y + 1) * width))
    edge_count = width * max(height - 1, 0) + height * max(width - 1, 0)
    component_data = {palette_id: _component_sizes(frozen, width, height, palette_id) for palette_id in ids}
    component_counts = tuple((palette_id, len(component_data[palette_id])) for palette_id in ids)
    largest_sizes = tuple((palette_id, max(component_data[palette_id], default=0)) for palette_id in ids)
    largest_shares = tuple((palette_id, largest, dict(cell_counts)[palette_id]) for palette_id, largest in largest_sizes)
    total_components = sum(value for _, value in component_counts)
    singleton_components = sum(sum(size == 1 for size in sizes) for sizes in component_data.values())
    instance = object.__new__(SemanticQualityDiagnostics)
    values: dict[str, Any] = {
        "width": width,
        "height": height,
        "used_palette_ids": ids,
        "cell_counts": cell_counts,
        "horizontal_transition_count": horizontal,
        "vertical_transition_count": vertical,
        "total_adjacency_edge_count": edge_count,
        "transition_density_numerator": horizontal + vertical,
        "transition_density_denominator": edge_count,
        "component_counts": component_counts,
        "total_component_count": total_components,
        "singleton_component_count": singleton_components,
        "largest_component_sizes": largest_sizes,
        "largest_component_shares": largest_shares,
        "schema": SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA,
        "schema_version": SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA_VERSION,
        "policy_version": SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION,
        "_construction_token": _DIAGNOSTICS_TOKEN,
    }
    for key, value in values.items():
        object.__setattr__(instance, key, value)
    instance._validate_values()
    object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
    return instance


@dataclass(frozen=True, slots=True)
class SemanticRecognizabilityReview:
    """Explicit, evidence-bearing review separate from structural diagnostics."""

    assessment_identity_digest: str
    disposition: RecognizabilityDisposition
    reviewer: str = ""
    reason: str = ""
    notes: str = ""
    schema: str = SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA
    schema_version: int = SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA_VERSION
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _REVIEW_TOKEN:
            raise SemanticQualityError("UNSEALED_REVIEW", "reviews require canonical checked construction")
        self._validate_values()
        object.__setattr__(self, "_construction_fingerprint", self._fingerprint())

    def _validate_values(self) -> None:
        if self.schema != SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA or self.schema_version != SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA_VERSION:
            raise SemanticQualityError("UNSUPPORTED_SCHEMA", "unsupported review schema/version")
        _require_digest(self.assessment_identity_digest, "assessment_identity_digest")
        try:
            disposition = RecognizabilityDisposition(self.disposition)
        except Exception as exc:
            raise SemanticQualityError("INVALID_DISPOSITION", "review disposition is not supported") from exc
        if not all(isinstance(value, str) for value in (self.reviewer, self.reason, self.notes)):
            raise SemanticQualityError("INVALID_REVIEW", "review evidence and notes must be strings")
        if disposition in (RecognizabilityDisposition.ACCEPT, RecognizabilityDisposition.REJECT) and (not self.reviewer.strip() or not self.reason.strip()):
            raise SemanticQualityError("REVIEW_EVIDENCE_REQUIRED", "ACCEPT and REJECT require non-empty reviewer and reason")
        object.__setattr__(self, "disposition", disposition)

    def _payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "assessment_identity_digest": self.assessment_identity_digest,
            "disposition": self.disposition.value,
            "reviewer": self.reviewer,
            "reason": self.reason,
            "notes": self.notes,
        }

    def _fingerprint(self) -> str:
        return _digest(self._payload())

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _REVIEW_TOKEN:
            raise SemanticQualityError("UNSEALED_REVIEW", "review construction seal is invalid")
        self._validate_values()
        if getattr(self, "_construction_fingerprint", None) != self._fingerprint():
            raise SemanticQualityError("TAMPERED_REVIEW", "review construction fingerprint is invalid")

    @property
    def identity_digest(self) -> str:
        self._assert_integrity()
        return self._fingerprint()

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return self._payload()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())


def _make_review(identity: str, disposition: RecognizabilityDisposition | str, reviewer: str = "", reason: str = "", notes: str = "") -> SemanticRecognizabilityReview:
    instance = object.__new__(SemanticRecognizabilityReview)
    values = {
        "assessment_identity_digest": identity,
        "disposition": RecognizabilityDisposition(disposition),
        "reviewer": reviewer,
        "reason": reason,
        "notes": notes,
        "schema": SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA,
        "schema_version": SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA_VERSION,
        "_construction_token": _REVIEW_TOKEN,
    }
    for key, value in values.items():
        object.__setattr__(instance, key, value)
    instance._validate_values()
    object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
    return instance


@dataclass(frozen=True, slots=True)
class SemanticQualityAssessment:
    """Immutable structural assessment plus an independently explicit review."""

    trusted_artifact_digest: str
    final_logical_grid_digest: str
    target_width: int
    target_height: int
    final_used_palette_ids: tuple[str, ...]
    final_used_color_count: int
    diagnostic_policy_version: str
    diagnostics: SemanticQualityDiagnostics
    review: SemanticRecognizabilityReview
    semantic_request_digest: str | None = None
    schema: str = SEMANTIC_QUALITY_ASSESSMENT_SCHEMA
    schema_version: int = SEMANTIC_QUALITY_ASSESSMENT_SCHEMA_VERSION
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _ASSESSMENT_TOKEN:
            raise SemanticQualityError("UNSEALED_ASSESSMENT", "assessments require canonical checked construction")
        self._validate_values()
        object.__setattr__(self, "_construction_fingerprint", self._fingerprint())

    def _base_payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "trusted_artifact_digest": self.trusted_artifact_digest,
            "final_logical_grid_digest": self.final_logical_grid_digest,
            "target_dimensions": {"width": self.target_width, "height": self.target_height},
            "final_used_palette_ids": list(self.final_used_palette_ids),
            "final_used_color_count": self.final_used_color_count,
            "diagnostic_policy_version": self.diagnostic_policy_version,
            "diagnostics_digest": self.diagnostics.digest(),
            "semantic_request_digest": self.semantic_request_digest,
        }

    def _payload(self) -> dict[str, object]:
        return {**self._base_payload(), "review": self.review.canonical_dict()}

    def _base_digest(self) -> str:
        return _digest(self._base_payload())

    def _fingerprint(self) -> str:
        return _digest(self._payload())

    def _validate_values(self) -> None:
        if self.schema != SEMANTIC_QUALITY_ASSESSMENT_SCHEMA or self.schema_version != SEMANTIC_QUALITY_ASSESSMENT_SCHEMA_VERSION:
            raise SemanticQualityError("UNSUPPORTED_SCHEMA", "unsupported assessment schema/version")
        _require_digest(self.trusted_artifact_digest, "trusted_artifact_digest")
        _require_digest(self.final_logical_grid_digest, "final_logical_grid_digest")
        if type(self.target_width) is not int or type(self.target_height) is not int or self.target_width < 1 or self.target_height < 1:
            raise SemanticQualityError("INVALID_DIMENSIONS", "assessment dimensions must be positive integers")
        ids = tuple(self.final_used_palette_ids)
        if ids != tuple(sorted(ids, key=_palette_key)) or len(set(ids)) != len(ids) or self.final_used_color_count != len(ids):
            raise SemanticQualityError("INVALID_ASSESSMENT", "assessment palette facts are not canonical")
        if self.diagnostic_policy_version != SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION:
            raise SemanticQualityError("UNSUPPORTED_POLICY", "assessment diagnostic policy is unsupported")
        if not isinstance(self.diagnostics, SemanticQualityDiagnostics) or not isinstance(self.review, SemanticRecognizabilityReview):
            raise SemanticQualityError("INVALID_ASSESSMENT", "assessment diagnostics/review types are invalid")
        self.diagnostics._assert_integrity()
        self.review._assert_integrity()
        if (
            (self.target_width, self.target_height) != (self.diagnostics.width, self.diagnostics.height)
            or ids != self.diagnostics.used_palette_ids
            or self.diagnostics.total_cell_count != self.target_width * self.target_height
            or self.review.assessment_identity_digest != self._base_digest()
        ):
            raise SemanticQualityError("INVALID_ASSESSMENT", "assessment facts are not bound to the same diagnostics/review identity")
        if self.semantic_request_digest is not None:
            _require_digest(self.semantic_request_digest, "semantic_request_digest")

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _ASSESSMENT_TOKEN:
            raise SemanticQualityError("UNSEALED_ASSESSMENT", "assessment construction seal is invalid")
        self._validate_values()
        if getattr(self, "_construction_fingerprint", None) != self._fingerprint():
            raise SemanticQualityError("TAMPERED_ASSESSMENT", "assessment construction fingerprint is invalid")

    @property
    def artifact_digest(self) -> str:
        return self.trusted_artifact_digest

    @property
    def diagnostic_digest(self) -> str:
        self._assert_integrity()
        return self.diagnostics.digest()

    @property
    def disposition(self) -> RecognizabilityDisposition:
        self._assert_integrity()
        return self.review.disposition

    @property
    def identity_digest(self) -> str:
        self._assert_integrity()
        return self.digest()

    @property
    def structural_identity_digest(self) -> str:
        """Stable artifact/diagnostics identity shared by review dispositions."""
        self._assert_integrity()
        return self._base_digest()

    @property
    def passes(self) -> bool:
        self._assert_integrity()
        return self.review.disposition is RecognizabilityDisposition.ACCEPT and self.review.assessment_identity_digest == self._base_digest()

    @property
    def accepted(self) -> bool:
        return self.passes

    @classmethod
    def from_artifact(cls, artifact: SemanticLevelArtArtifact, semantic_request: object | None = None) -> "SemanticQualityAssessment":
        return assess_semantic_quality(artifact, semantic_request)

    def with_review(self, disposition: RecognizabilityDisposition | str, reviewer: str, reason: str, notes: str = "") -> "SemanticQualityAssessment":
        self._assert_integrity()
        review = _make_review(self._base_digest(), disposition, reviewer, reason, notes)
        return _build_assessment(
            self.trusted_artifact_digest,
            self.final_logical_grid_digest,
            self.target_width,
            self.target_height,
            self.final_used_palette_ids,
            self.diagnostics,
            review,
            self.semantic_request_digest,
        )

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return self._payload()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())


def _request_digest(value: object | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return _require_digest(value, "semantic_request_digest")
    digest_method = getattr(value, "digest", None)
    if not callable(digest_method):
        raise SemanticQualityError("INVALID_REQUEST_IDENTITY", "semantic intent must provide a canonical digest")
    return _require_digest(digest_method(), "semantic_request_digest")


def _build_assessment(
    artifact_digest: str,
    grid_digest: str,
    width: int,
    height: int,
    used_ids: tuple[str, ...],
    diagnostics: SemanticQualityDiagnostics,
    review: SemanticRecognizabilityReview,
    request_digest: str | None,
) -> SemanticQualityAssessment:
    instance = object.__new__(SemanticQualityAssessment)
    values = {
        "trusted_artifact_digest": artifact_digest,
        "final_logical_grid_digest": grid_digest,
        "target_width": width,
        "target_height": height,
        "final_used_palette_ids": tuple(used_ids),
        "final_used_color_count": len(used_ids),
        "diagnostic_policy_version": SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION,
        "diagnostics": diagnostics,
        "review": review,
        "semantic_request_digest": request_digest,
        "schema": SEMANTIC_QUALITY_ASSESSMENT_SCHEMA,
        "schema_version": SEMANTIC_QUALITY_ASSESSMENT_SCHEMA_VERSION,
        "_construction_token": _ASSESSMENT_TOKEN,
    }
    for key, value in values.items():
        object.__setattr__(instance, key, value)
    instance._validate_values()
    object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
    return instance


def _assessment_base_digest(
    artifact_digest: str,
    grid_digest: str,
    width: int,
    height: int,
    used_ids: tuple[str, ...],
    diagnostics: SemanticQualityDiagnostics,
    request_digest: str | None,
) -> str:
    return _digest(
        {
            "schema": SEMANTIC_QUALITY_ASSESSMENT_SCHEMA,
            "schema_version": SEMANTIC_QUALITY_ASSESSMENT_SCHEMA_VERSION,
            "trusted_artifact_digest": artifact_digest,
            "final_logical_grid_digest": grid_digest,
            "target_dimensions": {"width": width, "height": height},
            "final_used_palette_ids": list(used_ids),
            "final_used_color_count": len(used_ids),
            "diagnostic_policy_version": SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION,
            "diagnostics_digest": diagnostics.digest(),
            "semantic_request_digest": request_digest,
        }
    )


def assess_semantic_quality(artifact: SemanticLevelArtArtifact, semantic_request: object | None = None) -> SemanticQualityAssessment:
    """Compute a sealed assessment from one trusted LEVEL_ART artifact."""

    if not isinstance(artifact, SemanticLevelArtArtifact):
        raise SemanticQualityError("UNTRUSTED_ARTIFACT", "semantic quality requires a trusted LEVEL_ART artifact")
    try:
        artifact._assert_integrity()
        diagnostics = _compute_diagnostics(artifact.logical_cells, artifact.target_width, artifact.target_height)
        request_digest = _request_digest(semantic_request)
        artifact_digest = artifact.digest()
        grid_digest = artifact.logical_grid_digest
        used_ids = tuple(artifact.final_used_palette_ids)
    except SemanticQualityError:
        raise
    except Exception as exc:
        raise SemanticQualityError("INVALID_ARTIFACT", "trusted LEVEL_ART artifact failed integrity validation") from exc
    base_digest = _assessment_base_digest(artifact_digest, grid_digest, artifact.target_width, artifact.target_height, used_ids, diagnostics, request_digest)
    return _build_assessment(artifact_digest, grid_digest, artifact.target_width, artifact.target_height, used_ids, diagnostics, _make_review(base_digest, RecognizabilityDisposition.UNREVIEWED), request_digest)


__all__ = [
    "SEMANTIC_QUALITY_ASSESSMENT_SCHEMA",
    "SEMANTIC_QUALITY_ASSESSMENT_SCHEMA_VERSION",
    "SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION",
    "SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA",
    "SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA_VERSION",
    "SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA",
    "SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA_VERSION",
    "RecognizabilityDisposition",
    "SemanticQualityAssessment",
    "SemanticQualityDiagnostics",
    "SemanticQualityError",
    "SemanticRecognizabilityReview",
    "assess_semantic_quality",
]
