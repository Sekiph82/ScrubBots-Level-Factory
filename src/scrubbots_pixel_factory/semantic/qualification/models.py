"""Offline, deterministic semantic-provider qualification contracts for SP04."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from enum import Enum
import math

from ..contracts import OutputClass, SemanticContractError
from ..providers.common import canonical_digest, typed_seed


QUALIFICATION_SCHEMA = "scrubbots-semantic-qualification"
QUALIFICATION_SCHEMA_VERSION = 1
CORPUS_VERSION = "semantic-benchmark-corpus-v1"
BENCHMARK_CORPUS_VERSION = CORPUS_VERSION
PLAN_VERSION = "semantic-qualification-plan-v1"
REVIEW_PACK_VERSION = "semantic-blind-review-pack-v1"
MAX_PLAN_ATTEMPTS = 10_000
MAX_RAW_DIMENSION = 8192


class QualificationLifecycle(str, Enum):
    PLANNED = "PLANNED"
    RAW_PROVIDER_CAPTURED = "RAW_PROVIDER_CAPTURED"
    RAW_IMPORT_VERIFIED = "RAW_IMPORT_VERIFIED"
    NORMALIZED = "NORMALIZED"
    READY_FOR_BLIND_REVIEW = "READY_FOR_BLIND_REVIEW"
    OWNER_ACCEPTED = "OWNER_ACCEPTED"
    OWNER_REJECTED = "OWNER_REJECTED"


class OwnerReviewDisposition(str, Enum):
    PENDING_OWNER_REVIEW = "PENDING_OWNER_REVIEW"
    OWNER_ACCEPTED = "OWNER_ACCEPTED"
    OWNER_REJECTED = "OWNER_REJECTED"


class NormalizationCompatibility(str, Enum):
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    PASS = "PASS"
    FAIL = "FAIL"


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise SemanticContractError(f"{label} must be a non-empty string")
    return value.strip()


def _digest(value: object, label: str) -> str:
    if type(value) is not str or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise SemanticContractError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _number(value: object, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or float(value) < 0:
        raise SemanticContractError(f"{label} must be finite and non-negative or null")
    return float(value)


def _dimensions(width: object, height: object, label: str, maximum: int = 1024) -> tuple[int, int]:
    if any(isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum for value in (width, height)):
        raise SemanticContractError(f"{label} must contain positive dimensions up to {maximum}")
    return width, height


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    case_id: str
    subject: str
    category: str
    description: str
    negative_description: str | None = None
    output_class: OutputClass | str = OutputClass.ASSET_ART
    target_width: int = 24
    target_height: int = 24
    transparency_intent: str = "OPAQUE_OR_TRANSPARENT_AS_REQUESTED"
    recognizability_objective: str = "recognizable semantic silhouette with clear subject identity"
    complexity_intent: str = "moderate pixel-art detail"
    requires_reference: bool = False
    requires_style: bool = False
    corpus_version: str = CORPUS_VERSION

    def __post_init__(self) -> None:
        for name in ("case_id", "subject", "category", "description", "transparency_intent", "recognizability_objective", "complexity_intent", "corpus_version"):
            _text(getattr(self, name), name)
        try:
            output_class = OutputClass.parse(self.output_class)
        except Exception as exc:
            raise SemanticContractError("benchmark output_class is invalid") from exc
        if output_class is not OutputClass.ASSET_ART:
            raise SemanticContractError("SP04 benchmark cases must use ASSET_ART")
        _dimensions(self.target_width, self.target_height, "benchmark target dimensions")
        if self.negative_description is not None:
            _text(self.negative_description, "negative_description")
        if type(self.requires_reference) is not bool or type(self.requires_style) is not bool:
            raise SemanticContractError("benchmark reference/style flags must be boolean")
        object.__setattr__(self, "output_class", output_class)

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": QUALIFICATION_SCHEMA, "schema_version": QUALIFICATION_SCHEMA_VERSION, "case_id": self.case_id, "subject": self.subject, "category": self.category, "description": self.description, "negative_description": self.negative_description, "output_class": self.output_class.value, "target_dimensions": {"width": self.target_width, "height": self.target_height}, "transparency_intent": self.transparency_intent, "recognizability_objective": self.recognizability_objective, "complexity_intent": self.complexity_intent, "requires_reference": self.requires_reference, "requires_style": self.requires_style, "corpus_version": self.corpus_version}

    def digest(self) -> str:
        return canonical_digest(self.canonical_dict())


_BENCHMARK_SUBJECTS = (
    ("wizard", "character", "a small pixel-art wizard with a readable hat, robe, and staff"),
    ("warrior", "character", "a small pixel-art dwarf or warrior with readable armor and a weapon"),
    ("elf", "character", "a small pixel-art elf with pointed ears and a clear forest-fantasy silhouette"),
    ("robot", "character", "a small pixel-art robot with a readable head, body, and mechanical limbs"),
    ("fish", "animal", "a small pixel-art fish with a readable body, eye, fins, and tail"),
    ("sea-creature", "animal", "a small pixel-art sea creature with a distinct underwater silhouette"),
    ("mushroom", "nature", "a small pixel-art mushroom with a readable cap and stem"),
    ("ghost", "character", "a small pixel-art ghost with a readable floating body and face"),
    ("rocket", "vehicle", "a small pixel-art rocket with a readable nose, body, fins, and exhaust"),
    ("tree", "nature", "a small pixel-art tree with a readable trunk and leafy crown"),
    ("skull", "symbol", "a small pixel-art skull with readable eye sockets and jaw"),
    ("potion", "object", "a small pixel-art potion bottle with a readable stopper and liquid"),
    ("crab", "animal", "a small pixel-art crab with readable claws, shell, and legs"),
    ("alien", "character", "a small pixel-art alien with a readable head, eyes, and body"),
    ("building", "object", "a small pixel-art building or simple object with a readable outline"),
)


def default_benchmark_corpus() -> tuple[BenchmarkCase, ...]:
    return tuple(BenchmarkCase(f"SP04-BENCH-{index:03d}", subject, category, description, "photorealism, text, watermark, noisy background") for index, (subject, category, description) in enumerate(_BENCHMARK_SUBJECTS, 1))


@dataclass(frozen=True, slots=True)
class ProviderWorkflowSpec:
    provider_id: str
    model_or_engine: str
    provider_version: str
    config_version: str
    workflow_version: str
    capability_snapshot_version: str | None = None
    aspect_ratio_intent: str | None = None
    raw_resolution_intent: str | None = None
    supports_reference: bool = False
    supports_style: bool = False
    requires_sp03_normalization: bool = False
    exact_size_expected: bool = False
    deterministic_seed_supported: bool = False
    execution_surface: str = ""
    native_controls: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("provider_id", "model_or_engine", "provider_version", "config_version", "workflow_version", "execution_surface"):
            _text(getattr(self, name), name)
        provider = self.provider_id.upper()
        if provider not in {"MAGNIFIC", "PIXELLAB"}:
            raise SemanticContractError("provider must be explicitly MAGNIFIC or PIXELLAB")
        if any(type(getattr(self, name)) is not bool for name in ("supports_reference", "supports_style", "requires_sp03_normalization", "exact_size_expected", "deterministic_seed_supported")):
            raise SemanticContractError("provider capability flags must be boolean")
        if type(self.native_controls) is not tuple or not self.native_controls or any(type(item) is not str or not item for item in self.native_controls) or len(set(self.native_controls)) != len(self.native_controls):
            raise SemanticContractError("provider native controls must be a stable unique tuple")
        if provider == "MAGNIFIC":
            from ..providers.magnific import get_magnific_model_snapshot
            try:
                snapshot = get_magnific_model_snapshot(self.model_or_engine)
            except Exception as exc:
                raise SemanticContractError("Magnific model must be pinned in the accepted capability snapshot") from exc
            if self.capability_snapshot_version != snapshot.snapshot_version or self.aspect_ratio_intent not in snapshot.supported_aspect_ratios:
                raise SemanticContractError("Magnific capability snapshot/aspect ratio is not pinned")
            if self.raw_resolution_intent is not None and self.raw_resolution_intent not in snapshot.supported_resolutions:
                raise SemanticContractError("Magnific raw resolution is unsupported by the pinned snapshot")
            if self.execution_surface != "external-manual-orchestrator" or not self.requires_sp03_normalization or self.exact_size_expected:
                raise SemanticContractError("Magnific must use the external raw-raster SP03 path")
            if self.supports_reference and not any(role.value == "REFERENCE" for role in snapshot.supported_reference_roles):
                raise SemanticContractError("Magnific REFERENCE capability is not truthful")
            if self.supports_style and not any(role.value == "STYLE" for role in snapshot.supported_reference_roles):
                raise SemanticContractError("Magnific STYLE capability is not truthful")
        else:
            if self.model_or_engine not in {"PIXFLUX", "BITFORGE"}:
                raise SemanticContractError("PixelLab engine must be explicit PIXFLUX or BITFORGE")
            if self.supports_reference:
                raise SemanticContractError("PixelLab has no generic REFERENCE input mapping")
            if any(value is not None for value in (self.capability_snapshot_version, self.aspect_ratio_intent, self.raw_resolution_intent)):
                raise SemanticContractError("PixelLab cannot carry Magnific capability fields")
            if self.execution_surface != "official-sdk" or not self.exact_size_expected or self.requires_sp03_normalization:
                raise SemanticContractError("PixelLab must use exact-size/no-resize semantics")
            if self.model_or_engine == "PIXFLUX" and self.supports_style:
                raise SemanticContractError("PIXFLUX has no STYLE mapping")
            if self.model_or_engine == "BITFORGE" and not self.supports_style:
                raise SemanticContractError("BITFORGE STYLE capability must be explicit")
        object.__setattr__(self, "provider_id", provider)

    def canonical_dict(self) -> dict[str, object]:
        return {"provider_id": self.provider_id, "model_or_engine": self.model_or_engine, "provider_version": self.provider_version, "config_version": self.config_version, "workflow_version": self.workflow_version, "capability_snapshot_version": self.capability_snapshot_version, "aspect_ratio_intent": self.aspect_ratio_intent, "raw_resolution_intent": self.raw_resolution_intent, "supports_reference": self.supports_reference, "supports_style": self.supports_style, "requires_sp03_normalization": self.requires_sp03_normalization, "exact_size_expected": self.exact_size_expected, "deterministic_seed_supported": self.deterministic_seed_supported, "execution_surface": self.execution_surface, "native_controls": list(self.native_controls)}

    @property
    def matrix_id(self) -> str:
        return canonical_digest(self.canonical_dict())


def default_provider_workflow_matrix() -> tuple[ProviderWorkflowSpec, ...]:
    return (
        ProviderWorkflowSpec("MAGNIFIC", "recraft-v4-1", "magnific-adapter-v1", "1", "semantic-magnific-workflow-v1", "magnific-model-snapshot-v1", "1:1", None, False, True, True, False, False, "external-manual-orchestrator", ("aspect_ratio", "raw_resolution", "style_image")),
        ProviderWorkflowSpec("PIXELLAB", "PIXFLUX", "pixellab-adapter-v1", "1", "semantic-pixellab-workflow-v1", None, None, None, False, False, False, True, True, "official-sdk", ("image_size", "seed", "outline", "shading", "detail", "view", "direction")),
        ProviderWorkflowSpec("PIXELLAB", "BITFORGE", "pixellab-adapter-v1", "1", "semantic-pixellab-workflow-v1", None, None, None, False, True, False, True, True, "official-sdk", ("image_size", "seed", "style_image", "outline", "shading", "detail", "view", "direction")),
    )


@dataclass(frozen=True, slots=True)
class QualificationPlanEntry:
    entry_id: str
    case_id: str
    provider_matrix_id: str
    provider_id: str
    model_or_engine: str
    workflow_version: str
    attempt_index: int
    target_width: int
    target_height: int

    def canonical_dict(self) -> dict[str, object]:
        return {"entry_id": self.entry_id, "case_id": self.case_id, "provider_matrix_id": self.provider_matrix_id, "provider_id": self.provider_id, "model_or_engine": self.model_or_engine, "workflow_version": self.workflow_version, "attempt_index": self.attempt_index, "target_dimensions": {"width": self.target_width, "height": self.target_height}}


@dataclass(frozen=True, slots=True)
class QualificationPlan:
    corpus_version: str
    cases: tuple[BenchmarkCase, ...]
    provider_matrix: tuple[ProviderWorkflowSpec, ...]
    entries: tuple[QualificationPlanEntry, ...]
    target_width: int
    target_height: int
    attempts_per_cell: int
    review_seed: int | str | None
    max_attempts: int
    credit_budget: float | None = None
    plan_version: str = PLAN_VERSION

    def __post_init__(self) -> None:
        _text(self.corpus_version, "corpus_version")
        _dimensions(self.target_width, self.target_height, "plan target dimensions")
        if type(self.cases) is not tuple or not self.cases or any(not isinstance(item, BenchmarkCase) for item in self.cases):
            raise SemanticContractError("plan cases must be a non-empty tuple")
        if len({item.case_id for item in self.cases}) != len(self.cases):
            raise SemanticContractError("plan case IDs must be unique")
        if type(self.provider_matrix) is not tuple or not self.provider_matrix or any(not isinstance(item, ProviderWorkflowSpec) for item in self.provider_matrix):
            raise SemanticContractError("plan provider matrix must be a non-empty tuple")
        if len({item.matrix_id for item in self.provider_matrix}) != len(self.provider_matrix):
            raise SemanticContractError("plan provider matrix entries must be unique")
        if isinstance(self.attempts_per_cell, bool) or not isinstance(self.attempts_per_cell, int) or not 1 <= self.attempts_per_cell <= MAX_PLAN_ATTEMPTS:
            raise SemanticContractError("attempts_per_cell must be finite and positive")
        if isinstance(self.max_attempts, bool) or not isinstance(self.max_attempts, int) or not 1 <= self.max_attempts <= MAX_PLAN_ATTEMPTS or self.max_attempts < len(self.entries):
            raise SemanticContractError("max_attempts is invalid for the finite plan")
        _number(self.credit_budget, "credit_budget")
        if len(self.entries) != len(self.cases) * len(self.provider_matrix) * self.attempts_per_cell:
            raise SemanticContractError("plan entry count does not match matrix size")

    @property
    def attempt_count(self) -> int:
        return len(self.entries)

    def identity_dict(self) -> dict[str, object]:
        return {"schema": QUALIFICATION_SCHEMA, "schema_version": QUALIFICATION_SCHEMA_VERSION, "plan_version": self.plan_version, "corpus_version": self.corpus_version, "cases": [case.canonical_dict() for case in self.cases], "provider_matrix": [spec.canonical_dict() for spec in self.provider_matrix], "entries": [entry.canonical_dict() for entry in self.entries], "target_dimensions": {"width": self.target_width, "height": self.target_height}, "attempts_per_cell": self.attempts_per_cell, "review_seed": None if self.review_seed is None else typed_seed(self.review_seed), "max_attempts": self.max_attempts}

    def canonical_dict(self) -> dict[str, object]:
        return {**self.identity_dict(), "credit_budget": self.credit_budget}

    def digest(self) -> str:
        return canonical_digest(self.identity_dict())


def build_qualification_plan(*, corpus_version: str | None = None, corpus: Sequence[BenchmarkCase] | None = None, provider_matrix: Sequence[ProviderWorkflowSpec] | None = None, target_width: int = 24, target_height: int = 24, attempts_per_cell: int = 1, review_seed: int | str | None = None, max_attempts: int | None = None, credit_budget: float | None = None) -> QualificationPlan:
    cases = tuple(default_benchmark_corpus() if corpus is None else corpus)
    matrix = tuple(default_provider_workflow_matrix() if provider_matrix is None else provider_matrix)
    _dimensions(target_width, target_height, "plan target dimensions")
    if isinstance(attempts_per_cell, bool) or not isinstance(attempts_per_cell, int) or not 1 <= attempts_per_cell <= MAX_PLAN_ATTEMPTS:
        raise SemanticContractError("attempts_per_cell must be finite and positive")
    total = len(cases) * len(matrix) * attempts_per_cell
    if not 1 <= total <= MAX_PLAN_ATTEMPTS:
        raise SemanticContractError("qualification plan size exceeds the bounded finite limit")
    versions = {case.corpus_version for case in cases}
    if len(versions) != 1 or (corpus_version is not None and corpus_version not in versions):
        raise SemanticContractError("selected benchmark cases must use the requested single corpus version")
    entries: list[QualificationPlanEntry] = []
    for case in cases:
        if (case.target_width, case.target_height) != (target_width, target_height):
            raise SemanticContractError("plan target dimensions must match every benchmark case")
        for spec in matrix:
            for attempt_index in range(attempts_per_cell):
                entry_digest = canonical_digest({"case": case.digest(), "provider": spec.matrix_id, "attempt_index": attempt_index, "target": [target_width, target_height]})
                entries.append(QualificationPlanEntry(f"entry-{entry_digest[:24]}", case.case_id, spec.matrix_id, spec.provider_id, spec.model_or_engine, spec.workflow_version, attempt_index, target_width, target_height))
    bounded_max = total if max_attempts is None else max_attempts
    return QualificationPlan(next(iter(versions)), cases, matrix, tuple(entries), target_width, target_height, attempts_per_cell, review_seed, bounded_max, _number(credit_budget, "credit_budget"))


@dataclass(frozen=True, slots=True)
class RawImportEvidence:
    raw_sha256: str
    raw_media_type: str
    returned_width: int
    returned_height: int
    provider_id: str
    provider_version: str
    workflow_version: str
    provider_result_identity: str
    local_raw_artifact_digest: str
    compatibility: NormalizationCompatibility = NormalizationCompatibility.NOT_ATTEMPTED

    def __post_init__(self) -> None:
        _digest(self.raw_sha256, "raw_sha256")
        _digest(self.local_raw_artifact_digest, "local_raw_artifact_digest")
        for name in ("raw_media_type", "provider_id", "provider_version", "workflow_version", "provider_result_identity"):
            _text(getattr(self, name), name)
        _dimensions(self.returned_width, self.returned_height, "raw returned dimensions", MAX_RAW_DIMENSION)
        object.__setattr__(self, "compatibility", self.compatibility if isinstance(self.compatibility, NormalizationCompatibility) else NormalizationCompatibility(self.compatibility))

    def canonical_dict(self) -> dict[str, object]:
        return {"raw_sha256": self.raw_sha256, "raw_media_type": self.raw_media_type, "returned_dimensions": {"width": self.returned_width, "height": self.returned_height}, "provider": {"id": self.provider_id, "version": self.provider_version, "workflow_version": self.workflow_version}, "provider_result_identity": self.provider_result_identity, "local_raw_artifact_digest": self.local_raw_artifact_digest, "compatibility": self.compatibility.value}


@dataclass(frozen=True, slots=True)
class NormalizationEvidence:
    normalization_request_digest: str
    normalized_artifact_digest: str
    target_width: int
    target_height: int
    policy_version: str
    resampler: str
    exact_size_fast_path: bool
    compatibility: NormalizationCompatibility
    raw_import_sha256: str | None = None

    def __post_init__(self) -> None:
        _digest(self.normalization_request_digest, "normalization_request_digest")
        _digest(self.normalized_artifact_digest, "normalized_artifact_digest")
        if self.raw_import_sha256 is not None:
            _digest(self.raw_import_sha256, "raw_import_sha256")
        _dimensions(self.target_width, self.target_height, "normalized target dimensions")
        _text(self.policy_version, "policy_version")
        _text(self.resampler, "resampler")
        if type(self.exact_size_fast_path) is not bool:
            raise SemanticContractError("exact_size_fast_path must be boolean")
        compatibility = self.compatibility if isinstance(self.compatibility, NormalizationCompatibility) else NormalizationCompatibility(self.compatibility)
        if compatibility is not NormalizationCompatibility.PASS:
            raise SemanticContractError("normalization evidence must be PASS")
        object.__setattr__(self, "compatibility", compatibility)

    def canonical_dict(self) -> dict[str, object]:
        return {"normalization_request_digest": self.normalization_request_digest, "normalized_artifact_digest": self.normalized_artifact_digest, "target_dimensions": {"width": self.target_width, "height": self.target_height}, "policy_version": self.policy_version, "resampler": self.resampler, "exact_size_fast_path": self.exact_size_fast_path, "compatibility": self.compatibility.value, "raw_import_sha256": self.raw_import_sha256}


@dataclass(frozen=True, slots=True)
class CostUsageRecord:
    provider_attempt_count: int = 0
    provider_credits: float | None = None
    currency_cost: float | None = None
    failed_generation_cost: float | None = None
    accepted_candidate_cost: float | None = None
    rejected_candidate_cost: float | None = None
    normalization_reject_count: int = 0
    owner_accept_count: int = 0
    owner_reject_count: int = 0
    elapsed_seconds: float | None = None
    observed_at: str | None = None

    def __post_init__(self) -> None:
        for name in ("provider_attempt_count", "normalization_reject_count", "owner_accept_count", "owner_reject_count"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise SemanticContractError(f"{name} must be a non-negative integer")
        for name in ("provider_credits", "currency_cost", "failed_generation_cost", "accepted_candidate_cost", "rejected_candidate_cost", "elapsed_seconds"):
            _number(getattr(self, name), name)
        if self.observed_at is not None:
            _text(self.observed_at, "observed_at")

    def canonical_dict(self) -> dict[str, object]:
        return {"provider_attempt_count": self.provider_attempt_count, "provider_credits": self.provider_credits, "currency_cost": self.currency_cost, "failed_generation_cost": self.failed_generation_cost, "accepted_candidate_cost": self.accepted_candidate_cost, "rejected_candidate_cost": self.rejected_candidate_cost, "normalization_reject_count": self.normalization_reject_count, "owner_accept_count": self.owner_accept_count, "owner_reject_count": self.owner_reject_count, "elapsed_seconds": self.elapsed_seconds, "observed_at": self.observed_at}


@dataclass(frozen=True, slots=True)
class QualificationAttemptRecord:
    attempt_id: str
    plan_entry_id: str
    case_id: str
    provider_id: str
    model_or_engine: str
    workflow_version: str
    lifecycle: QualificationLifecycle = QualificationLifecycle.PLANNED
    raw_import: RawImportEvidence | None = None
    normalization: NormalizationEvidence | None = None
    owner_disposition: OwnerReviewDisposition = OwnerReviewDisposition.PENDING_OWNER_REVIEW
    cost_usage: CostUsageRecord = CostUsageRecord()
    review_item_id: str | None = None
    provider_version: str | None = None

    def __post_init__(self) -> None:
        for name in ("attempt_id", "plan_entry_id", "case_id", "provider_id", "model_or_engine", "workflow_version"):
            _text(getattr(self, name), name)
        lifecycle = self.lifecycle if isinstance(self.lifecycle, QualificationLifecycle) else QualificationLifecycle(self.lifecycle)
        disposition = self.owner_disposition if isinstance(self.owner_disposition, OwnerReviewDisposition) else OwnerReviewDisposition(self.owner_disposition)
        if lifecycle in {QualificationLifecycle.RAW_IMPORT_VERIFIED, QualificationLifecycle.NORMALIZED, QualificationLifecycle.READY_FOR_BLIND_REVIEW, QualificationLifecycle.OWNER_ACCEPTED, QualificationLifecycle.OWNER_REJECTED} and self.raw_import is None:
            raise SemanticContractError("lifecycle requires raw-import evidence")
        if lifecycle in {QualificationLifecycle.NORMALIZED, QualificationLifecycle.READY_FOR_BLIND_REVIEW, QualificationLifecycle.OWNER_ACCEPTED, QualificationLifecycle.OWNER_REJECTED} and self.normalization is None:
            raise SemanticContractError("lifecycle requires normalization evidence")
        if lifecycle is QualificationLifecycle.READY_FOR_BLIND_REVIEW and self.raw_import.compatibility is not NormalizationCompatibility.PASS:
            raise SemanticContractError("review-ready lifecycle requires raw-import compatibility PASS")
        if lifecycle is QualificationLifecycle.READY_FOR_BLIND_REVIEW and disposition is not OwnerReviewDisposition.PENDING_OWNER_REVIEW:
            raise SemanticContractError("review-ready attempts must be pending owner review")
        if lifecycle is QualificationLifecycle.OWNER_ACCEPTED and disposition is not OwnerReviewDisposition.OWNER_ACCEPTED:
            raise SemanticContractError("owner-accepted lifecycle requires owner disposition")
        if lifecycle is QualificationLifecycle.OWNER_REJECTED and disposition is not OwnerReviewDisposition.OWNER_REJECTED:
            raise SemanticContractError("owner-rejected lifecycle requires owner disposition")
        if self.raw_import is not None and self.raw_import.provider_id != self.provider_id:
            raise SemanticContractError("raw-import provider is not bound to attempt")
        if self.normalization is not None and self.normalization.compatibility is not NormalizationCompatibility.PASS:
            raise SemanticContractError("normalization is not compatible")
        if self.provider_version is not None:
            _text(self.provider_version, "provider_version")
        if self.raw_import is not None and self.provider_version is not None and self.raw_import.provider_version != self.provider_version:
            raise SemanticContractError("raw-import provider version is not bound to attempt")
        if self.normalization is not None and self.raw_import is not None and self.normalization.raw_import_sha256 != self.raw_import.raw_sha256:
            raise SemanticContractError("normalization is not bound to exact raw import")
        if self.review_item_id is not None:
            _text(self.review_item_id, "review_item_id")
        object.__setattr__(self, "lifecycle", lifecycle)
        object.__setattr__(self, "owner_disposition", disposition)

    def identity_dict(self) -> dict[str, object]:
        return {"attempt_id": self.attempt_id, "plan_entry_id": self.plan_entry_id, "case_id": self.case_id, "provider_id": self.provider_id, "provider_version": self.provider_version, "model_or_engine": self.model_or_engine, "workflow_version": self.workflow_version, "raw_import": None if self.raw_import is None else self.raw_import.canonical_dict(), "normalization": None if self.normalization is None else self.normalization.canonical_dict(), "review_item_id": self.review_item_id}

    def canonical_dict(self) -> dict[str, object]:
        return {**self.identity_dict(), "lifecycle": self.lifecycle.value, "owner_disposition": self.owner_disposition.value, "cost_usage": self.cost_usage.canonical_dict()}

    def digest(self) -> str:
        return canonical_digest(self.identity_dict())


@dataclass(frozen=True, slots=True)
class MetadataBlindReviewItem:
    review_id: str
    sequence: int
    subject_label: str
    target_width: int
    target_height: int
    hidden_attempt_id: str

    def visible_dict(self) -> dict[str, object]:
        return {"review_id": self.review_id, "sequence": self.sequence, "subject_label": self.subject_label, "target_dimensions": {"width": self.target_width, "height": self.target_height}}

    def hidden_dict(self) -> dict[str, object]:
        return {**self.visible_dict(), "hidden_attempt_id": self.hidden_attempt_id}


@dataclass(frozen=True, slots=True)
class MetadataBlindReviewPack:
    review_seed: int | str
    items: tuple[MetadataBlindReviewItem, ...]
    hidden_attempts: tuple[QualificationAttemptRecord, ...]
    pack_version: str = REVIEW_PACK_VERSION

    def __post_init__(self) -> None:
        if type(self.items) is not tuple or type(self.hidden_attempts) is not tuple or len(self.items) != len(self.hidden_attempts):
            raise SemanticContractError("visible and hidden review records must be one-to-one")
        if len({item.review_id for item in self.items}) != len(self.items) or len({item.hidden_attempt_id for item in self.items}) != len(self.items):
            raise SemanticContractError("review IDs must be stable and unique")

    def visible_dict(self) -> dict[str, object]:
        return {"schema": self.pack_version, "items": [item.visible_dict() for item in self.items]}

    def hidden_manifest(self) -> dict[str, object]:
        return {"schema": self.pack_version, "review_seed": typed_seed(self.review_seed), "items": [item.hidden_dict() for item in self.items], "attempts": [attempt.canonical_dict() for attempt in self.hidden_attempts]}

    def digest(self) -> str:
        return canonical_digest(self.hidden_manifest())


def build_metadata_blind_review_pack(attempts: Iterable[QualificationAttemptRecord], *, review_seed: int | str) -> MetadataBlindReviewPack:
    records = tuple(attempts)
    if any(record.lifecycle is not QualificationLifecycle.READY_FOR_BLIND_REVIEW or record.owner_disposition is not OwnerReviewDisposition.PENDING_OWNER_REVIEW for record in records):
        raise SemanticContractError("only technically ready, pending attempts may enter blind review")
    ordered = sorted(records, key=lambda record: canonical_digest({"review_seed": typed_seed(review_seed), "attempt": record.digest()}))
    items: list[MetadataBlindReviewItem] = []
    for sequence, record in enumerate(ordered, 1):
        if record.normalization is None:
            raise SemanticContractError("review-ready attempt lacks normalization evidence")
        review_id = f"review-{canonical_digest({"seed": typed_seed(review_seed), "attempt": record.digest()})[:24]}"
        items.append(MetadataBlindReviewItem(review_id, sequence, record.case_id, record.normalization.target_width, record.normalization.target_height, record.attempt_id))
    item_tuple = tuple(items)
    return MetadataBlindReviewPack(review_seed, item_tuple, tuple(replace(record, review_item_id=item.review_id) for record, item in zip(ordered, item_tuple)))


@dataclass(frozen=True, slots=True)
class QualificationSummary:
    plan_digest: str
    total_attempts: int
    lifecycle_counts: tuple[tuple[str, int], ...]
    owner_disposition_counts: tuple[tuple[str, int], ...]
    technical_ready_count: int
    owner_accepted_count: int
    owner_rejected_count: int
    gate_status: str

    def __post_init__(self) -> None:
        _digest(self.plan_digest, "plan_digest")
        if isinstance(self.total_attempts, bool) or not isinstance(self.total_attempts, int) or self.total_attempts < 0:
            raise SemanticContractError("summary total_attempts is invalid")
        if self.gate_status not in {"NO_READY_CANDIDATES", "PENDING_OWNER_REVIEW", "OWNER_ACCEPTED", "OWNER_REJECTED"}:
            raise SemanticContractError("summary gate_status is invalid")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": QUALIFICATION_SCHEMA, "schema_version": QUALIFICATION_SCHEMA_VERSION, "plan_digest": self.plan_digest, "total_attempts": self.total_attempts, "lifecycle_counts": dict(self.lifecycle_counts), "owner_disposition_counts": dict(self.owner_disposition_counts), "technical_ready_count": self.technical_ready_count, "owner_accepted_count": self.owner_accepted_count, "owner_rejected_count": self.owner_rejected_count, "gate_status": self.gate_status}


def summarize_qualification(plan: QualificationPlan, attempts: Iterable[QualificationAttemptRecord]) -> QualificationSummary:
    records = tuple(attempts)
    lifecycle_counts = tuple((state.value, sum(record.lifecycle is state for record in records)) for state in QualificationLifecycle if any(record.lifecycle is state for record in records))
    disposition_counts = tuple((state.value, sum(record.owner_disposition is state for record in records)) for state in OwnerReviewDisposition if any(record.owner_disposition is state for record in records))
    ready = sum(record.lifecycle is QualificationLifecycle.READY_FOR_BLIND_REVIEW for record in records)
    accepted = sum(record.owner_disposition is OwnerReviewDisposition.OWNER_ACCEPTED for record in records)
    rejected = sum(record.owner_disposition is OwnerReviewDisposition.OWNER_REJECTED for record in records)
    status = "NO_READY_CANDIDATES" if ready == 0 else ("PENDING_OWNER_REVIEW" if accepted == 0 and rejected == 0 else ("OWNER_ACCEPTED" if accepted else "OWNER_REJECTED"))
    return QualificationSummary(plan.digest(), len(records), lifecycle_counts, disposition_counts, ready, accepted, rejected, status)


@dataclass(frozen=True, slots=True)
class QualificationEvidenceReference:
    evidence_id: str
    label: str
    repository_path: str
    private_source_embedded: bool = False

    def __post_init__(self) -> None:
        _text(self.evidence_id, "evidence_id")
        _text(self.label, "label")
        _text(self.repository_path, "repository_path")
        if type(self.private_source_embedded) is not bool:
            raise SemanticContractError("private_source_embedded must be boolean")

    def canonical_dict(self) -> dict[str, object]:
        return {"evidence_id": self.evidence_id, "label": self.label, "repository_path": self.repository_path, "private_source_embedded": self.private_source_embedded}


def default_evidence_references() -> tuple[QualificationEvidenceReference, ...]:
    return (QualificationEvidenceReference("SP02-MAGNIFIC-WIZARD-DIRECTION", "owner-approved Magnific wizard direction; private raster not embedded", "review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md"), QualificationEvidenceReference("M10-NEGATIVE-OWNER-PACK", "retained M10 semantic review negative evidence: 100/100 rejected", "review/m10/M10_OWNER_REVIEW_DECISION.md"))
