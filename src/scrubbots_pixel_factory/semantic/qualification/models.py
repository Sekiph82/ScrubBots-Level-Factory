"""Offline, deterministic semantic-provider qualification contracts for SP04."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, replace
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
    case_digest: str | None = None
    provider_version: str | None = None

    def canonical_dict(self) -> dict[str, object]:
        return {"entry_id": self.entry_id, "case_id": self.case_id, "case_digest": self.case_digest, "provider_matrix_id": self.provider_matrix_id, "provider_id": self.provider_id, "provider_version": self.provider_version, "model_or_engine": self.model_or_engine, "workflow_version": self.workflow_version, "attempt_index": self.attempt_index, "target_dimensions": {"width": self.target_width, "height": self.target_height}}


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
        cases = {case.case_id: case for case in self.cases}
        specs = {spec.matrix_id: spec for spec in self.provider_matrix}
        seen: set[tuple[str, str, int]] = set()
        for entry in self.entries:
            if entry.case_id not in cases or entry.provider_matrix_id not in specs:
                raise SemanticContractError("plan entry references an unknown case or provider matrix cell")
            case = cases[entry.case_id]
            spec = specs[entry.provider_matrix_id]
            if case.requires_reference and not spec.supports_reference:
                raise SemanticContractError("plan contains a case/provider cell that cannot satisfy REFERENCE")
            if case.requires_style and not spec.supports_style:
                raise SemanticContractError("plan contains a case/provider cell that cannot satisfy STYLE")
            key = (entry.case_id, entry.provider_matrix_id, entry.attempt_index)
            expected_entry_id = f"entry-{canonical_digest({'case': case.digest(), 'provider': spec.matrix_id, 'attempt_index': entry.attempt_index, 'target': [self.target_width, self.target_height]})[:24]}"
            if key in seen or not 0 <= entry.attempt_index < self.attempts_per_cell:
                raise SemanticContractError("plan has duplicate or out-of-domain matrix attempts")
            if entry.entry_id != expected_entry_id or entry.case_digest != case.digest() or entry.provider_id != spec.provider_id or entry.provider_version != spec.provider_version or entry.model_or_engine != spec.model_or_engine or entry.workflow_version != spec.workflow_version or (entry.target_width, entry.target_height) != (self.target_width, self.target_height):
                raise SemanticContractError("plan entry is not exactly bound to its case, provider cell, or target")
            seen.add(key)
        expected_keys = {(case.case_id, spec.matrix_id, index) for case in self.cases for spec in self.provider_matrix for index in range(self.attempts_per_cell)}
        if seen != expected_keys:
            raise SemanticContractError("plan is missing a Cartesian case/provider/attempt cell")

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
            if case.requires_reference and not spec.supports_reference:
                raise SemanticContractError(f"provider cell {spec.provider_id}/{spec.model_or_engine} cannot satisfy required REFERENCE capability")
            if case.requires_style and not spec.supports_style:
                raise SemanticContractError(f"provider cell {spec.provider_id}/{spec.model_or_engine} cannot satisfy required STYLE capability")
            for attempt_index in range(attempts_per_cell):
                entry_digest = canonical_digest({"case": case.digest(), "provider": spec.matrix_id, "attempt_index": attempt_index, "target": [target_width, target_height]})
                entries.append(QualificationPlanEntry(f"entry-{entry_digest[:24]}", case.case_id, spec.matrix_id, spec.provider_id, spec.model_or_engine, spec.workflow_version, attempt_index, target_width, target_height, case.digest(), spec.provider_version))
    bounded_max = total if max_attempts is None else max_attempts
    return QualificationPlan(next(iter(versions)), cases, matrix, tuple(entries), target_width, target_height, attempts_per_cell, review_seed, bounded_max, _number(credit_budget, "credit_budget"))


_RAW_EVIDENCE_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class RawImportEvidence:
    """Sealed evidence derived from one checked SP03 raw artifact."""

    raw_artifact: object
    raw_artifact_digest: str
    raw_sha256: str
    raw_media_type: str
    returned_width: int
    returned_height: int
    provider_id: str
    provider_version: str
    workflow_version: str
    model_id: str | None
    provider_result_identity: str
    local_raw_artifact_digest: str
    request_digest: str
    compatibility: NormalizationCompatibility
    _construction_token: object
    _construction_fingerprint: str

    @classmethod
    def from_sp03(cls, raw_artifact: object) -> "RawImportEvidence":
        from ..normalization.core import SemanticRawArtifact
        if not isinstance(raw_artifact, SemanticRawArtifact):
            raise SemanticContractError("raw qualification evidence requires a typed SP03 SemanticRawArtifact")
        instance = object.__new__(cls)
        values = {"raw_artifact": raw_artifact, "raw_artifact_digest": raw_artifact.digest(), "raw_sha256": raw_artifact.raw_sha256, "raw_media_type": raw_artifact.media_type, "returned_width": raw_artifact.returned_width, "returned_height": raw_artifact.returned_height, "provider_id": raw_artifact.provider_id, "provider_version": raw_artifact.provider_version, "workflow_version": raw_artifact.workflow_version, "model_id": raw_artifact.model_id, "provider_result_identity": raw_artifact.provider_candidate_digest, "local_raw_artifact_digest": raw_artifact.digest(), "request_digest": raw_artifact.request_digest, "compatibility": NormalizationCompatibility.PASS, "_construction_token": _RAW_EVIDENCE_TOKEN}
        for name, value in values.items():
            object.__setattr__(instance, name, value)
        instance._validate()
        object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
        instance._assert_integrity()
        return instance

    def __post_init__(self) -> None:
        raise SemanticContractError("RawImportEvidence must be constructed from a typed SP03 raw artifact")

    def _validate(self) -> None:
        from ..normalization.core import SemanticRawArtifact
        if self._construction_token is not _RAW_EVIDENCE_TOKEN or not isinstance(self.raw_artifact, SemanticRawArtifact):
            raise SemanticContractError("raw evidence construction seal is invalid")
        if self.raw_artifact.digest() != self.raw_artifact_digest or self.local_raw_artifact_digest != self.raw_artifact_digest or self.raw_artifact.raw_sha256 != self.raw_sha256 or self.raw_artifact.media_type != self.raw_media_type or self.raw_artifact.provider_id != self.provider_id or self.raw_artifact.provider_version != self.provider_version or self.raw_artifact.workflow_version != self.workflow_version or self.raw_artifact.model_id != self.model_id or self.raw_artifact.provider_candidate_digest != self.provider_result_identity or self.raw_artifact.request_digest != self.request_digest:
            raise SemanticContractError("raw evidence is not bound to the exact SP03 artifact")
        _digest(self.raw_artifact_digest, "raw_artifact_digest")
        _digest(self.raw_sha256, "raw_sha256")
        _digest(self.local_raw_artifact_digest, "local_raw_artifact_digest")
        for name in ("raw_media_type", "provider_id", "provider_version", "workflow_version", "provider_result_identity", "request_digest"):
            _text(getattr(self, name), name)
        _dimensions(self.returned_width, self.returned_height, "raw returned dimensions", MAX_RAW_DIMENSION)
        if (self.returned_width, self.returned_height) != (self.raw_artifact.returned_width, self.raw_artifact.returned_height):
            raise SemanticContractError("raw evidence dimensions are not bound")
        if self.compatibility is not NormalizationCompatibility.PASS:
            raise SemanticContractError("only checked PASS raw evidence is representable")

    def _fingerprint(self) -> str:
        return canonical_digest({"raw_artifact_digest": self.raw_artifact_digest, "raw_sha256": self.raw_sha256, "provider": [self.provider_id, self.provider_version, self.workflow_version, self.model_id, self.provider_result_identity], "request_digest": self.request_digest, "dimensions": [self.returned_width, self.returned_height]})

    def _assert_integrity(self) -> None:
        self._validate()
        if self._construction_fingerprint != self._fingerprint():
            raise SemanticContractError("raw evidence construction fingerprint is invalid")

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return {"raw_artifact_digest": self.raw_artifact_digest, "raw_sha256": self.raw_sha256, "raw_media_type": self.raw_media_type, "returned_dimensions": {"width": self.returned_width, "height": self.returned_height}, "provider": {"id": self.provider_id, "version": self.provider_version, "workflow_version": self.workflow_version, "model_id": self.model_id, "result_identity": self.provider_result_identity}, "request_digest": self.request_digest, "local_raw_artifact_digest": self.local_raw_artifact_digest, "compatibility": self.compatibility.value}


_NORMALIZATION_EVIDENCE_TOKEN = object()
_ATTEMPT_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class NormalizationEvidence:
    """Sealed evidence derived from one checked SP03 normalized artifact."""

    normalized_artifact: object
    source_raw_artifact_digest: str
    raw_import_sha256: str
    normalization_request_digest: str
    normalized_artifact_digest: str
    normalized_rgba_sha256: str
    target_width: int
    target_height: int
    policy_version: str
    resampler: str
    exact_size_fast_path: bool
    compatibility: NormalizationCompatibility
    _construction_token: object
    _construction_fingerprint: str

    @classmethod
    def from_sp03(cls, normalized_artifact: object) -> "NormalizationEvidence":
        from ..normalization.core import SemanticNormalizedArtifact
        if not isinstance(normalized_artifact, SemanticNormalizedArtifact):
            raise SemanticContractError("normalization qualification evidence requires a typed SP03 SemanticNormalizedArtifact")
        normalized_artifact._assert_integrity()
        report = normalized_artifact.report
        instance = object.__new__(cls)
        values = {"normalized_artifact": normalized_artifact, "source_raw_artifact_digest": normalized_artifact.source_raw_artifact_digest, "raw_import_sha256": report.input_raw_sha256, "normalization_request_digest": normalized_artifact.normalization_request_digest, "normalized_artifact_digest": normalized_artifact.digest(), "normalized_rgba_sha256": normalized_artifact.normalized_rgba_sha256, "target_width": normalized_artifact.target_width, "target_height": normalized_artifact.target_height, "policy_version": normalized_artifact.normalization_request.policy_version, "resampler": report.resampler, "exact_size_fast_path": report.exact_size_fast_path, "compatibility": NormalizationCompatibility.PASS, "_construction_token": _NORMALIZATION_EVIDENCE_TOKEN}
        for name, value in values.items():
            object.__setattr__(instance, name, value)
        instance._validate()
        object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
        instance._assert_integrity()
        return instance

    def __post_init__(self) -> None:
        raise SemanticContractError("NormalizationEvidence must be constructed from a typed SP03 normalized artifact")

    def _validate(self) -> None:
        from ..normalization.core import SemanticNormalizedArtifact
        if self._construction_token is not _NORMALIZATION_EVIDENCE_TOKEN or not isinstance(self.normalized_artifact, SemanticNormalizedArtifact):
            raise SemanticContractError("normalization evidence construction seal is invalid")
        self.normalized_artifact._assert_integrity()
        report = self.normalized_artifact.report
        if self.source_raw_artifact_digest != self.normalized_artifact.source_raw_artifact_digest or self.normalization_request_digest != self.normalized_artifact.normalization_request_digest or self.normalized_artifact.digest() != self.normalized_artifact_digest or self.normalized_rgba_sha256 != self.normalized_artifact.normalized_rgba_sha256 or self.raw_import_sha256 != report.input_raw_sha256 or self.policy_version != self.normalized_artifact.normalization_request.policy_version or self.resampler != report.resampler or self.exact_size_fast_path != report.exact_size_fast_path or (self.target_width, self.target_height) != (self.normalized_artifact.target_width, self.normalized_artifact.target_height):
            raise SemanticContractError("normalization evidence is not bound to the exact SP03 artifact")
        for name in ("source_raw_artifact_digest", "raw_import_sha256", "normalization_request_digest", "normalized_artifact_digest", "normalized_rgba_sha256"):
            _digest(getattr(self, name), name)
        _dimensions(self.target_width, self.target_height, "normalized target dimensions")
        _text(self.policy_version, "policy_version")
        _text(self.resampler, "resampler")
        if type(self.exact_size_fast_path) is not bool or self.compatibility is not NormalizationCompatibility.PASS:
            raise SemanticContractError("normalization evidence must be checked PASS")

    def _fingerprint(self) -> str:
        return canonical_digest({"source_raw_artifact_digest": self.source_raw_artifact_digest, "raw_import_sha256": self.raw_import_sha256, "request": self.normalization_request_digest, "artifact": self.normalized_artifact_digest, "rgba": self.normalized_rgba_sha256, "target": [self.target_width, self.target_height], "policy": [self.policy_version, self.resampler, self.exact_size_fast_path]})

    def _assert_integrity(self) -> None:
        self._validate()
        if self._construction_fingerprint != self._fingerprint():
            raise SemanticContractError("normalization evidence construction fingerprint is invalid")

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return {"source_raw_artifact_digest": self.source_raw_artifact_digest, "raw_import_sha256": self.raw_import_sha256, "normalization_request_digest": self.normalization_request_digest, "normalized_artifact_digest": self.normalized_artifact_digest, "normalized_rgba_sha256": self.normalized_rgba_sha256, "target_dimensions": {"width": self.target_width, "height": self.target_height}, "policy_version": self.policy_version, "resampler": self.resampler, "exact_size_fast_path": self.exact_size_fast_path, "compatibility": self.compatibility.value}


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
    provider_matrix_id: str | None = None
    case_digest: str | None = None
    plan_digest: str | None = None
    request_digest: str | None = None
    target_width: int | None = None
    target_height: int | None = None
    _construction_token: object = field(init=False, repr=False, compare=False, default=None)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False, default="")

    @classmethod
    def from_plan_entry(cls, plan: QualificationPlan, entry: QualificationPlanEntry, *, lifecycle: QualificationLifecycle = QualificationLifecycle.PLANNED, raw_import: RawImportEvidence | None = None, normalization: NormalizationEvidence | None = None, owner_disposition: OwnerReviewDisposition = OwnerReviewDisposition.PENDING_OWNER_REVIEW, cost_usage: CostUsageRecord | None = None, attempt_id: str | None = None) -> "QualificationAttemptRecord":
        if not isinstance(plan, QualificationPlan) or not isinstance(entry, QualificationPlanEntry):
            raise SemanticContractError("attempt construction requires a typed qualification plan and entry")
        selected = next((candidate for candidate in plan.entries if candidate.entry_id == entry.entry_id), None)
        if selected is None or selected.canonical_dict() != entry.canonical_dict():
            raise SemanticContractError("attempt entry is not an exact member of the validated plan")
        case = next(case for case in plan.cases if case.case_id == entry.case_id)
        spec = next(spec for spec in plan.provider_matrix if spec.matrix_id == entry.provider_matrix_id)
        instance = object.__new__(cls)
        values = {"attempt_id": attempt_id or f"attempt-{entry.entry_id[6:]}", "plan_entry_id": entry.entry_id, "case_id": case.case_id, "provider_id": spec.provider_id, "model_or_engine": spec.model_or_engine, "workflow_version": spec.workflow_version, "lifecycle": lifecycle, "raw_import": raw_import, "normalization": normalization, "owner_disposition": owner_disposition, "cost_usage": cost_usage or CostUsageRecord(), "review_item_id": None, "provider_version": spec.provider_version, "provider_matrix_id": spec.matrix_id, "case_digest": case.digest(), "plan_digest": plan.digest(), "request_digest": None if raw_import is None else raw_import.request_digest, "target_width": plan.target_width, "target_height": plan.target_height, "_construction_token": _ATTEMPT_TOKEN}
        for name, value in values.items():
            object.__setattr__(instance, name, value)
        instance.__post_init__()
        object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
        instance._assert_integrity()
        return instance

    def __post_init__(self) -> None:
        for name in ("attempt_id", "plan_entry_id", "case_id", "provider_id", "model_or_engine", "workflow_version"):
            _text(getattr(self, name), name)
        lifecycle = self.lifecycle if isinstance(self.lifecycle, QualificationLifecycle) else QualificationLifecycle(self.lifecycle)
        disposition = self.owner_disposition if isinstance(self.owner_disposition, OwnerReviewDisposition) else OwnerReviewDisposition(self.owner_disposition)
        advanced = lifecycle is not QualificationLifecycle.PLANNED
        if advanced and self._construction_token is not _ATTEMPT_TOKEN:
            raise SemanticContractError("advanced attempts require checked construction from a validated plan entry")
        if advanced and any(value is None for value in (self.provider_matrix_id, self.case_digest, self.plan_digest, self.target_width, self.target_height)):
            raise SemanticContractError("advanced attempts require complete plan binding")
        if advanced:
            _digest(self.case_digest, "case_digest")
            _digest(self.plan_digest, "plan_digest")
            _dimensions(self.target_width, self.target_height, "attempt target dimensions")
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
        if self.raw_import is not None and not isinstance(self.raw_import, RawImportEvidence):
            raise SemanticContractError("attempt raw evidence must be sealed SP03-derived evidence")
        if self.normalization is not None and not isinstance(self.normalization, NormalizationEvidence):
            raise SemanticContractError("attempt normalization evidence must be sealed SP03-derived evidence")
        if self.raw_import is not None and self.raw_import.provider_id != self.provider_id:
            raise SemanticContractError("raw-import provider is not bound to attempt")
        if self.normalization is not None and self.normalization.compatibility is not NormalizationCompatibility.PASS:
            raise SemanticContractError("normalization is not compatible")
        if self.provider_version is not None:
            _text(self.provider_version, "provider_version")
        if self.raw_import is not None and self.provider_version is not None and self.raw_import.provider_version != self.provider_version:
            raise SemanticContractError("raw-import provider version is not bound to attempt")
        if self.raw_import is not None and self.raw_import.workflow_version != self.workflow_version:
            raise SemanticContractError("raw-import workflow is not bound to attempt")
        if self.raw_import is not None and self.raw_import.model_id is not None and self.raw_import.model_id != self.model_or_engine:
            raise SemanticContractError("raw-import model is not bound to attempt")
        if self.normalization is not None and self.raw_import is not None and (self.normalization.raw_import_sha256 != self.raw_import.raw_sha256 or self.normalization.source_raw_artifact_digest != self.raw_import.local_raw_artifact_digest):
            raise SemanticContractError("normalization is not bound to exact raw import")
        if self.request_digest is not None:
            _digest(self.request_digest, "request_digest")
        if self.raw_import is not None and self.request_digest is not None and self.request_digest != self.raw_import.request_digest:
            raise SemanticContractError("raw request digest is not bound to attempt")
        if self.normalization is not None and self.target_width is not None and (self.normalization.target_width, self.normalization.target_height) != (self.target_width, self.target_height):
            raise SemanticContractError("normalization dimensions are not bound to attempt")
        if self.review_item_id is not None:
            _text(self.review_item_id, "review_item_id")
        object.__setattr__(self, "lifecycle", lifecycle)
        object.__setattr__(self, "owner_disposition", disposition)

    def identity_dict(self) -> dict[str, object]:
        return {"attempt_id": self.attempt_id, "plan_entry_id": self.plan_entry_id, "case_id": self.case_id, "case_digest": self.case_digest, "plan_digest": self.plan_digest, "provider_matrix_id": self.provider_matrix_id, "provider_id": self.provider_id, "provider_version": self.provider_version, "model_or_engine": self.model_or_engine, "workflow_version": self.workflow_version, "request_digest": self.request_digest, "target_dimensions": None if self.target_width is None else {"width": self.target_width, "height": self.target_height}, "raw_import": None if self.raw_import is None else self.raw_import.canonical_dict(), "normalization": None if self.normalization is None else self.normalization.canonical_dict()}

    def canonical_dict(self) -> dict[str, object]:
        return {**self.identity_dict(), "lifecycle": self.lifecycle.value, "owner_disposition": self.owner_disposition.value, "cost_usage": self.cost_usage.canonical_dict()}

    def digest(self) -> str:
        return canonical_digest(self.identity_dict())

    def review_binding_digest(self) -> str:
        """Stable identity excluding review binding, cost, owner and audit data."""
        return self.digest()

    def _fingerprint(self) -> str:
        return self.digest()

    def _assert_integrity(self) -> None:
        if self._construction_token is _ATTEMPT_TOKEN and self._construction_fingerprint != self._fingerprint():
            raise SemanticContractError("attempt construction fingerprint is invalid")

    def with_cost_usage(self, cost_usage: CostUsageRecord) -> "QualificationAttemptRecord":
        self._assert_integrity()
        return self._copy_bound(cost_usage=cost_usage)

    def with_review_binding(self, review_item_id: str) -> "QualificationAttemptRecord":
        self._assert_integrity()
        _text(review_item_id, "review_item_id")
        return self._copy_bound(review_item_id=review_item_id)

    def with_lifecycle(self, lifecycle: QualificationLifecycle, *, owner_disposition: OwnerReviewDisposition | None = None) -> "QualificationAttemptRecord":
        self._assert_integrity()
        return self._copy_bound(lifecycle=lifecycle, owner_disposition=owner_disposition or self.owner_disposition)

    def _copy_bound(self, **changes: object) -> "QualificationAttemptRecord":
        instance = object.__new__(type(self))
        for name in ("attempt_id", "plan_entry_id", "case_id", "provider_id", "model_or_engine", "workflow_version", "lifecycle", "raw_import", "normalization", "owner_disposition", "cost_usage", "review_item_id", "provider_version", "provider_matrix_id", "case_digest", "plan_digest", "request_digest", "target_width", "target_height"):
            object.__setattr__(instance, name, changes.get(name, getattr(self, name)))
        object.__setattr__(instance, "_construction_token", _ATTEMPT_TOKEN)
        instance.__post_init__()
        object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
        instance._assert_integrity()
        return instance


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
        hidden = {attempt.attempt_id: attempt for attempt in self.hidden_attempts}
        if len(hidden) != len(self.hidden_attempts):
            raise SemanticContractError("hidden review attempts must have unique IDs")
        for attempt in self.hidden_attempts:
            attempt._assert_integrity()
        for item in self.items:
            attempt = hidden.get(item.hidden_attempt_id)
            if attempt is None:
                raise SemanticContractError("visible review item references an orphan hidden attempt")
            if attempt.review_item_id != item.review_id:
                raise SemanticContractError("visible review ID is not bound to its hidden attempt")

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
        review_id = f"review-{canonical_digest({"seed": typed_seed(review_seed), "attempt": record.review_binding_digest()})[:24]}"
        items.append(MetadataBlindReviewItem(review_id, sequence, record.case_id, record.normalization.target_width, record.normalization.target_height, record.attempt_id))
    item_tuple = tuple(items)
    return MetadataBlindReviewPack(review_seed, item_tuple, tuple(record.with_review_binding(item.review_id) for record, item in zip(ordered, item_tuple)))


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
        for label, value in (("technical_ready_count", self.technical_ready_count), ("owner_accepted_count", self.owner_accepted_count), ("owner_rejected_count", self.owner_rejected_count)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise SemanticContractError(f"summary {label} is invalid")
        lifecycle = dict(self.lifecycle_counts)
        dispositions = dict(self.owner_disposition_counts)
        if len(lifecycle) != len(self.lifecycle_counts) or len(dispositions) != len(self.owner_disposition_counts) or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in (*lifecycle.values(), *dispositions.values())):
            raise SemanticContractError("summary count maps are invalid")
        if sum(lifecycle.values()) != self.total_attempts or dispositions.get(OwnerReviewDisposition.OWNER_ACCEPTED.value, 0) != self.owner_accepted_count or dispositions.get(OwnerReviewDisposition.OWNER_REJECTED.value, 0) != self.owner_rejected_count:
            raise SemanticContractError("summary counts are internally inconsistent")
        if self.gate_status not in {"NO_READY_CANDIDATES", "PENDING_OWNER_REVIEW", "OWNER_ACCEPTED", "OWNER_REJECTED", "MIXED"}:
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
    status = "MIXED" if (accepted and rejected) or (accepted and ready) or (rejected and ready) else ("OWNER_ACCEPTED" if accepted else ("OWNER_REJECTED" if rejected else ("PENDING_OWNER_REVIEW" if ready else "NO_READY_CANDIDATES")))
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
