"""Pure local Magnific job construction and result import.

Magnific is intentionally not an HTTP client in SP02.  This module produces a
versioned external job description and verifies an owner-supplied result
manifest and immutable bytes without scraping, browser automation, or secret
handling.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
import hashlib
import math
from typing import Any

from ...contracts import (
    CandidateStatus,
    ImageInputDescriptor,
    ImageInputRole,
    ProviderUnavailableError,
    SemanticGenerationRequest,
    SemanticImageCandidate,
    SemanticProviderError,
    SemanticRequestError,
    SemanticCapabilities,
)
from ...provider import SemanticGeneratorProvider
from ..common import canonical_bytes, canonical_digest, image_identity, typed_seed


MAGNIFIC_PROVIDER_ID = "MAGNIFIC"
MAGNIFIC_ADAPTER_VERSION = "magnific-adapter-v1"
MAGNIFIC_CONFIG_VERSION = "1"
MAGNIFIC_JOB_SCHEMA = "scrubbots-magnific-job"
MAGNIFIC_JOB_SCHEMA_VERSION = 1
MAGNIFIC_RESULT_SCHEMA = "scrubbots-magnific-result"
MAGNIFIC_RESULT_SCHEMA_VERSION = 1
MAGNIFIC_EXECUTION_SURFACE = "external-manual-orchestrator"


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise SemanticProviderError(f"{label} must be a non-empty string")
    return value.strip()


def _aspect_ratio(width: int, height: int) -> str:
    divisor = math.gcd(width, height)
    return f"{width // divisor}:{height // divisor}"


@dataclass(frozen=True, slots=True)
class MagnificReferenceBinding:
    """One owner-authorized provider creation binding, identified by role/hash."""

    role: ImageInputRole | str
    content_sha256: str
    creation_id: str

    def __post_init__(self) -> None:
        role = ImageInputRole.parse(self.role)
        if role not in (ImageInputRole.REFERENCE, ImageInputRole.STYLE):
            raise SemanticProviderError("Magnific bindings may only be REFERENCE or STYLE")
        if type(self.content_sha256) is not str or len(self.content_sha256) != 64 or any(char not in "0123456789abcdef" for char in self.content_sha256):
            raise SemanticProviderError("Magnific binding content_sha256 is invalid")
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "creation_id", _text(self.creation_id, "creation_id"))

    def canonical_dict(self) -> dict[str, str]:
        return {"role": self.role.value, "content_sha256": self.content_sha256, "creation_id": self.creation_id}


MagnificExecutionBinding = MagnificReferenceBinding


def _expected_images(request: SemanticGenerationRequest) -> list[tuple[ImageInputRole, ImageInputDescriptor]]:
    result = [(ImageInputRole.REFERENCE, item) for item in request.reference_images]
    if request.style_image is not None:
        result.append((ImageInputRole.STYLE, request.style_image))
    return result


def _normalize_bindings(request: SemanticGenerationRequest, bindings: Iterable[MagnificReferenceBinding] | Mapping[object, object] | None) -> tuple[MagnificReferenceBinding, ...]:
    expected = _expected_images(request)
    if bindings is None:
        if expected:
            raise SemanticProviderError("Magnific image inputs require explicit creation bindings")
        return ()
    if isinstance(bindings, Mapping):
        values: list[MagnificReferenceBinding] = []
        for key, creation_id in bindings.items():
            if not isinstance(key, tuple) or len(key) != 2:
                raise SemanticProviderError("Magnific binding map keys must be (role, content_sha256)")
            values.append(MagnificReferenceBinding(key[0], key[1], creation_id))
    else:
        values = list(bindings)
    if any(not isinstance(item, MagnificReferenceBinding) for item in values):
        raise SemanticProviderError("Magnific bindings must be MagnificReferenceBinding values")
    keys = [(item.role.value, item.content_sha256) for item in values]
    if len(keys) != len(set(keys)):
        raise SemanticProviderError("duplicate Magnific role/hash binding")
    expected_keys = [(role.value, image.content_sha256) for role, image in expected]
    if set(keys) != set(expected_keys) or len(keys) != len(expected_keys):
        raise SemanticProviderError("Magnific bindings are missing, extra, or role/hash mismatched")
    by_key = {key: item for key, item in zip(keys, values)}
    return tuple(by_key[key] for key in expected_keys)


def _render_prompt(request: SemanticGenerationRequest) -> str:
    parts = [request.description]
    if request.negative_description:
        parts.append(f"Avoid: {request.negative_description}")
    controls = {
        "semantic_category": request.semantic_category,
        "outline": request.outline,
        "shading": request.shading,
        "detail": request.detail,
        "view": request.view,
        "direction": request.direction,
        "isometric": request.isometric,
        "transparent_background": request.no_background,
        "coverage_percentage": request.coverage_percentage,
    }
    parts.extend(f"{key}={value}" for key, value in controls.items() if value is not None)
    # This is guidance, not a claim that Magnific can emit a logical grid.
    parts.append("Return raw provider artwork; logical dimensions are provenance only.")
    return "; ".join(parts)


@dataclass(frozen=True, slots=True)
class MagnificJobSpec:
    request_digest: str
    provider_id: str
    provider_version: str
    provider_config_version: str
    execution_surface: str
    model_slug: str
    rendered_prompt: str
    aspect_ratio: str
    candidate_count: int
    provider_quality: str | None
    provider_resolution: str | None
    reference_bindings: tuple[MagnificReferenceBinding, ...] = ()
    logical_width: int = 0
    logical_height: int = 0
    original_seed: int | str = ""
    provider_seed_supported: bool = False
    schema: str = MAGNIFIC_JOB_SCHEMA
    schema_version: int = MAGNIFIC_JOB_SCHEMA_VERSION

    @classmethod
    def from_request(
        cls,
        request: SemanticGenerationRequest,
        *,
        bindings: Iterable[MagnificReferenceBinding] | Mapping[object, object] | None = None,
        model_slug: str | None = None,
        quality: str | None = None,
        resolution: str | None = None,
        candidate_count: int | None = None,
    ) -> "MagnificJobSpec":
        if not isinstance(request, SemanticGenerationRequest):
            raise TypeError("Magnific job requires SemanticGenerationRequest")
        if request.provider_id != MAGNIFIC_PROVIDER_ID:
            raise SemanticProviderError("Magnific job requires explicit provider_id MAGNIFIC")
        if request.provider_config_version != MAGNIFIC_CONFIG_VERSION:
            raise SemanticProviderError("unsupported Magnific provider config version")
        model = model_slug if model_slug is not None else request.provider_model
        if model is None or model.upper() == "AUTO":
            raise SemanticProviderError("Magnific requires an explicit model slug")
        width, height = request.resolved_dimensions()
        count = request.desired_candidate_count if candidate_count is None else candidate_count
        if type(count) is not int or isinstance(count, bool) or count < 1:
            raise SemanticRequestError("Magnific candidate_count must be a positive integer")
        ref_bindings = _normalize_bindings(request, bindings)
        return cls(
            request_digest=request.digest(),
            provider_id=MAGNIFIC_PROVIDER_ID,
            provider_version=MAGNIFIC_ADAPTER_VERSION,
            provider_config_version=request.provider_config_version,
            execution_surface=MAGNIFIC_EXECUTION_SURFACE,
            model_slug=_text(model, "model_slug"),
            rendered_prompt=_render_prompt(request),
            aspect_ratio=_aspect_ratio(width, height),
            candidate_count=count,
            provider_quality=None if quality is None else _text(quality, "quality"),
            provider_resolution=None if resolution is None else _text(resolution, "resolution"),
            reference_bindings=ref_bindings,
            logical_width=width,
            logical_height=height,
            original_seed=request.seed,
        )

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "request_digest": self.request_digest,
            "provider": {"id": self.provider_id, "version": self.provider_version, "config_version": self.provider_config_version},
            "execution_surface": self.execution_surface,
            "model_slug": self.model_slug,
            "rendered_prompt": self.rendered_prompt,
            "aspect_ratio": self.aspect_ratio,
            "candidate_count": self.candidate_count,
            "quality": self.provider_quality,
            "resolution": self.provider_resolution,
            "reference_bindings": [item.canonical_dict() for item in self.reference_bindings],
            "logical_dimensions": {"width": self.logical_width, "height": self.logical_height},
            "original_seed": typed_seed(self.original_seed),
            "provider_seed_supported": self.provider_seed_supported,
        }

    def canonical_bytes(self) -> bytes:
        return canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @property
    def job_digest(self) -> str:
        return self.digest()


@dataclass(frozen=True, slots=True)
class MagnificResultManifest:
    request_digest: str
    job_digest: str
    provider_id: str
    provider_version: str
    provider_config_version: str
    execution_surface: str
    model_slug: str
    actual_model_slug: str
    creation_id: str
    returned_width: int | None
    returned_height: int | None
    raw_image_sha256: str | None
    media_type: str | None
    status: CandidateStatus | str
    audit_metadata: Mapping[str, object] = field(default_factory=dict)
    failure_reason: str | None = None
    schema: str = MAGNIFIC_RESULT_SCHEMA
    schema_version: int = MAGNIFIC_RESULT_SCHEMA_VERSION

    @classmethod
    def success(cls, job: MagnificJobSpec, *, raw_image_sha256: str, returned_width: int, returned_height: int, creation_id: str, media_type: str = "image/png", actual_model_slug: str | None = None, audit_metadata: Mapping[str, object] | None = None) -> "MagnificResultManifest":
        return cls(job.request_digest, job.digest(), job.provider_id, job.provider_version, job.provider_config_version, job.execution_surface, job.model_slug, actual_model_slug or job.model_slug, _text(creation_id, "creation_id"), returned_width, returned_height, raw_image_sha256, _text(media_type, "media_type"), CandidateStatus.SUCCESS, audit_metadata or {})

    @classmethod
    def failure(cls, job: MagnificJobSpec, *, reason: str, audit_metadata: Mapping[str, object] | None = None) -> "MagnificResultManifest":
        return cls(job.request_digest, job.digest(), job.provider_id, job.provider_version, job.provider_config_version, job.execution_surface, job.model_slug, job.model_slug, "external-failure", None, None, None, None, CandidateStatus.FAILURE, audit_metadata or {}, _text(reason, "failure_reason"))

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "request_digest": self.request_digest,
            "job_digest": self.job_digest,
            "provider": {"id": self.provider_id, "version": self.provider_version, "config_version": self.provider_config_version},
            "execution_surface": self.execution_surface,
            "model_slug": self.model_slug,
            "actual_model_slug": self.actual_model_slug,
            "creation_id": self.creation_id,
            "returned_dimensions": {"width": self.returned_width, "height": self.returned_height} if self.returned_width is not None else None,
            "raw_image_sha256": self.raw_image_sha256,
            "media_type": self.media_type,
            "status": self.status.value if isinstance(self.status, CandidateStatus) else self.status,
            "audit_metadata": dict(self.audit_metadata),
            "failure_reason": self.failure_reason,
        }

    def canonical_bytes(self) -> bytes:
        return canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return canonical_digest(self.canonical_dict())

    def import_result(self, request: SemanticGenerationRequest, job: MagnificJobSpec, raw_bytes: bytes | None) -> SemanticImageCandidate:
        if self.request_digest != request.digest() or self.job_digest != job.digest() or self.provider_id != MAGNIFIC_PROVIDER_ID or self.provider_version != MAGNIFIC_ADAPTER_VERSION or self.provider_config_version != request.provider_config_version or self.execution_surface != job.execution_surface or self.model_slug != job.model_slug:
            raise SemanticProviderError("Magnific result manifest is not bound to the request/job")
        try:
            status = self.status if isinstance(self.status, CandidateStatus) else CandidateStatus(self.status)
        except ValueError as exc:
            raise SemanticProviderError("Magnific result status is invalid") from exc
        candidate_id = f"magnific-{self.job_digest[:24]}"
        if status is not CandidateStatus.SUCCESS:
            return SemanticImageCandidate.failure(request, candidate_id=candidate_id, provider_id=MAGNIFIC_PROVIDER_ID, provider_version=MAGNIFIC_ADAPTER_VERSION, workflow_version=request.provider_workflow_version, reason=self.failure_reason or "Magnific external execution failed", status=status)
        if not isinstance(raw_bytes, bytes) or not raw_bytes:
            raise SemanticProviderError("successful Magnific result requires non-empty raw bytes")
        if self.raw_image_sha256 != hashlib.sha256(raw_bytes).hexdigest():
            raise SemanticProviderError("Magnific raw bytes hash does not match result manifest")
        width, height = request.resolved_dimensions()
        if (self.returned_width, self.returned_height) != (width, height):
            raise SemanticProviderError("Magnific result dimensions do not match the requested dimensions")
        if self.returned_width is None or self.returned_height is None or self.media_type is None or not self.creation_id:
            raise SemanticProviderError("successful Magnific result is incomplete")
        return SemanticImageCandidate.success(request, candidate_id=candidate_id, provider_id=MAGNIFIC_PROVIDER_ID, provider_version=MAGNIFIC_ADAPTER_VERSION, workflow_version=request.provider_workflow_version, image_bytes=raw_bytes, returned_width=self.returned_width, returned_height=self.returned_height, model_id=request.provider_model, generation_metadata={"job_digest": job.digest(), "execution_surface": self.execution_surface, "actual_model_slug": self.actual_model_slug, "creation_id": self.creation_id, "media_type": self.media_type, "audit_metadata": dict(self.audit_metadata)})


class MagnificProvider(SemanticGeneratorProvider):
    """Offline bridge: prepare/import only; no provider API is implemented."""

    @property
    def provider_id(self) -> str:
        return MAGNIFIC_PROVIDER_ID

    @property
    def provider_version(self) -> str:
        return MAGNIFIC_ADAPTER_VERSION

    @property
    def capabilities(self) -> SemanticCapabilities:
        return SemanticCapabilities(text_to_image=True, negative_prompt=True, transparent_background=True, reference_images=True, style_image=True, view_direction_controls=True, isometric=True)

    @property
    def capability_metadata(self) -> dict[str, object]:
        return {
            "provider_id": MAGNIFIC_PROVIDER_ID,
            "execution_surface": MAGNIFIC_EXECUTION_SURFACE,
            "text_to_image": True,
            "generic_reference_bindings": True,
            "style_bindings": True,
            "provider_seed_control": False,
            "exact_logical_dimensions": False,
            "supported_output": "raw provider artwork imported without normalization",
        }

    def validate_request(self, request: SemanticGenerationRequest) -> None:
        super().validate_request(request)
        if request.provider_id != MAGNIFIC_PROVIDER_ID:
            raise SemanticProviderError("Magnific requires explicit provider_id MAGNIFIC")
        if request.provider_model is None or request.provider_model.upper() == "AUTO":
            raise SemanticProviderError("Magnific requires an explicit model slug")

    def prepare_job(self, request: SemanticGenerationRequest, *, bindings: Iterable[MagnificReferenceBinding] | Mapping[object, object] | None = None, **kwargs: Any) -> MagnificJobSpec:
        self.validate_request(request)
        return MagnificJobSpec.from_request(request, bindings=bindings, **kwargs)

    def import_result(self, request: SemanticGenerationRequest, manifest: MagnificResultManifest, raw_bytes: bytes | None, *, job: MagnificJobSpec | None = None) -> SemanticImageCandidate:
        actual_job = self.prepare_job(request) if job is None else job
        return manifest.import_result(request, actual_job, raw_bytes)

    def generate(self, request: SemanticGenerationRequest) -> SemanticImageCandidate:
        # An explicit typed result keeps the provider boundary usable by router
        # tests while making the no-network execution surface unambiguous.
        return SemanticImageCandidate.failure(request, candidate_id=f"magnific-external-{request.digest()[:16]}", provider_id=MAGNIFIC_PROVIDER_ID, provider_version=MAGNIFIC_ADAPTER_VERSION, workflow_version=request.provider_workflow_version, reason="Magnific requires external job execution and local result import", status=CandidateStatus.UNAVAILABLE)


__all__ = [
    "MAGNIFIC_ADAPTER_VERSION", "MAGNIFIC_CONFIG_VERSION", "MAGNIFIC_EXECUTION_SURFACE", "MAGNIFIC_JOB_SCHEMA", "MAGNIFIC_PROVIDER_ID", "MAGNIFIC_RESULT_SCHEMA", "MagnificExecutionBinding", "MagnificJobSpec", "MagnificProvider", "MagnificReferenceBinding", "MagnificResultManifest",
]
