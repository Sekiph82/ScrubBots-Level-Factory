"""PixelLab official-API adapter with deterministic local contracts.

The optional ``pixellab`` package is imported only inside explicit execution.
Job construction, identity, binding validation, manifests, and all tests work
without the package, a secret, or network access.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from io import BytesIO
import base64
import hashlib
import os
from pathlib import Path
from typing import Any

from ...contracts import (
    CandidateStatus,
    ImageInputDescriptor,
    ImageInputRole,
    ProviderUnavailableError,
    SemanticCapabilities,
    SemanticGenerationRequest,
    SemanticImageCandidate,
    SemanticProviderError,
    SemanticRequestError,
    UnsupportedCapabilityError,
)
from ...provider import SemanticGeneratorProvider
from ..common import bytes_sha256, canonical_bytes, canonical_digest, image_identity, require_bytes_hash, typed_seed


PIXELLAB_PROVIDER_ID = "PIXELLAB"
PIXELLAB_ADAPTER_VERSION = "pixellab-adapter-v1"
PIXELLAB_CONFIG_VERSION = "1"
PIXELLAB_JOB_SCHEMA = "scrubbots-pixellab-job"
PIXELLAB_JOB_SCHEMA_VERSION = 1
PIXELLAB_RESULT_SCHEMA = "scrubbots-pixellab-result"
PIXELLAB_RESULT_SCHEMA_VERSION = 1
PIXELLAB_DEFAULT_BASE_URL = "https://api.pixellab.ai/v1"


PIXELLAB_CONTROL_MAP = {
    "outline": {"NONE": "lineless", "SINGLE": "single color outline", "DARK": "single color black outline", "AUTO": None},
    "shading": {"FLAT": "flat shading", "BASIC": "basic shading", "AUTO": None},
    "detail": {"LOW": "low detail", "MEDIUM": "medium detail", "HIGH": "highly detailed", "AUTO": None},
    "view": {"FRONT": None, "SIDE": "side", "TOP_DOWN": "low top-down", "AUTO": None},
    "direction": {"N": "north", "NE": "north-east", "E": "east", "SE": "south-east", "S": "south", "SW": "south-west", "W": "west", "NW": "north-west", "AUTO": None},
}
_ROLE_ORDER = (ImageInputRole.INIT, ImageInputRole.COLOR_REFERENCE, ImageInputRole.STYLE)


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise SemanticProviderError(f"{label} must be a non-empty string")
    return value.strip()


def _provider_seed(seed: int | str, request_digest: str) -> int:
    encoded = canonical_bytes({"domain": "scrubbots-pixellab-provider-seed-v1", "request_digest": request_digest, "seed": typed_seed(seed)})
    # Keep the result in the non-negative signed range accepted by the SDK.
    return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "big") % 2_147_483_647


@dataclass(frozen=True, slots=True, repr=False)
class PixelLabRuntimeConfig:
    """Runtime-only configuration; credentials never enter identity or repr."""

    secret: str | None = field(default=None, repr=False, compare=False)
    base_url: str = PIXELLAB_DEFAULT_BASE_URL

    @classmethod
    def from_env(cls) -> "PixelLabRuntimeConfig":
        return cls(os.environ.get("PIXELLAB_SECRET"), os.environ.get("PIXELLAB_BASE_URL", PIXELLAB_DEFAULT_BASE_URL))

    def __repr__(self) -> str:
        return f"PixelLabRuntimeConfig(base_url={self.base_url!r}, secret={'configured' if self.secret else 'absent'})"

    def identity_dict(self) -> dict[str, str]:
        # The network endpoint is operational configuration, never job identity.
        return {"config_version": PIXELLAB_CONFIG_VERSION}


@dataclass(frozen=True, slots=True)
class PixelLabExecutionBinding:
    role: ImageInputRole | str
    content_sha256: str
    image_bytes: bytes = field(repr=False, compare=False)
    local_path: str | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        role = ImageInputRole.parse(self.role)
        if role not in _ROLE_ORDER:
            raise SemanticProviderError("PixelLab bindings must use INIT, COLOR_REFERENCE, or STYLE")
        if type(self.content_sha256) is not str or len(self.content_sha256) != 64 or any(char not in "0123456789abcdef" for char in self.content_sha256):
            raise SemanticProviderError("PixelLab binding content_sha256 is invalid")
        if not isinstance(self.image_bytes, bytes) or not self.image_bytes:
            raise SemanticProviderError("PixelLab binding requires non-empty immutable bytes")
        try:
            require_bytes_hash(self.image_bytes, self.content_sha256)
        except Exception as exc:
            raise SemanticProviderError("PixelLab binding bytes do not match content_sha256") from exc
        object.__setattr__(self, "role", role)

    @classmethod
    def from_file(cls, role: ImageInputRole | str, path: str | Path) -> "PixelLabExecutionBinding":
        resolved = Path(path)
        raw = resolved.read_bytes()
        return cls(role, bytes_sha256(raw), raw, str(resolved))

    def identity_dict(self) -> dict[str, str]:
        return {"role": self.role.value, "content_sha256": self.content_sha256}


def _expected_bindings(request: SemanticGenerationRequest, engine: str) -> list[tuple[ImageInputRole, ImageInputDescriptor]]:
    if request.reference_images:
        raise UnsupportedCapabilityError("PixelLab does not accept generic REFERENCE inputs in this bridge")
    expected: list[tuple[ImageInputRole, ImageInputDescriptor]] = []
    if request.init_image is not None:
        expected.append((ImageInputRole.INIT, request.init_image))
    if request.color_reference is not None:
        expected.append((ImageInputRole.COLOR_REFERENCE, request.color_reference))
    if request.style_image is not None:
        if engine != "BITFORGE":
            raise UnsupportedCapabilityError("PIXFLUX has no STYLE input mapping")
        expected.append((ImageInputRole.STYLE, request.style_image))
    return expected


def _normalize_bindings(request: SemanticGenerationRequest, engine: str, bindings: Iterable[PixelLabExecutionBinding] | Mapping[object, object] | None) -> tuple[PixelLabExecutionBinding, ...]:
    expected = _expected_bindings(request, engine)
    if bindings is None:
        if expected:
            raise SemanticProviderError("PixelLab image inputs require explicit local role/hash bindings")
        return ()
    if isinstance(bindings, Mapping):
        values = []
        for key, raw in bindings.items():
            if not isinstance(key, tuple) or len(key) != 2 or not isinstance(raw, bytes):
                raise SemanticProviderError("PixelLab binding map keys/values are invalid")
            values.append(PixelLabExecutionBinding(key[0], key[1], raw))
    else:
        values = list(bindings)
    if any(not isinstance(item, PixelLabExecutionBinding) for item in values):
        raise SemanticProviderError("PixelLab bindings must be PixelLabExecutionBinding values")
    keys = [(item.role.value, item.content_sha256) for item in values]
    if len(keys) != len(set(keys)):
        raise SemanticProviderError("duplicate PixelLab role/hash binding")
    expected_keys = [(role.value, image.content_sha256) for role, image in expected]
    if len(values) != len(expected_keys) or set(keys) != set(expected_keys):
        raise SemanticProviderError("PixelLab bindings are missing, extra, or role/hash mismatched")
    by_key = {key: item for key, item in zip(keys, values)}
    return tuple(by_key[(role.value, image.content_sha256)] for role, image in expected)


def _map_control(group: str, value: str) -> str | None:
    mapped = PIXELLAB_CONTROL_MAP[group].get(value)
    if value not in PIXELLAB_CONTROL_MAP[group]:
        raise UnsupportedCapabilityError(f"PIXFLUX has no truthful {group} mapping for {value}")
    return mapped


@dataclass(frozen=True, slots=True)
class PixelLabJobSpec:
    request_digest: str
    provider_id: str
    provider_version: str
    provider_config_version: str
    engine: str
    workflow_version: str
    width: int
    height: int
    original_seed: int | str
    provider_seed: int
    description: str
    negative_description: str | None
    outline: str | None
    shading: str | None
    detail: str | None
    view: str | None
    direction: str | None
    isometric: bool
    no_background: bool
    coverage_percentage: float
    init_image_sha256: str | None
    style_image_sha256: str | None
    color_image_sha256: str | None
    init_strength: int | None
    schema: str = PIXELLAB_JOB_SCHEMA
    schema_version: int = PIXELLAB_JOB_SCHEMA_VERSION

    @classmethod
    def from_request(cls, request: SemanticGenerationRequest, *, engine: str | None = None, bindings: Iterable[PixelLabExecutionBinding] | Mapping[object, object] | None = None) -> "PixelLabJobSpec":
        if not isinstance(request, SemanticGenerationRequest):
            raise TypeError("PixelLab job requires SemanticGenerationRequest")
        if request.provider_id != PIXELLAB_PROVIDER_ID:
            raise SemanticProviderError("PixelLab job requires explicit provider_id PIXELLAB")
        selected = (engine or request.provider_model or "").upper()
        if selected not in ("PIXFLUX", "BITFORGE"):
            raise SemanticProviderError("PixelLab requires explicit engine PIXFLUX or BITFORGE")
        if request.provider_model is None or request.provider_model.upper() != selected:
            raise SemanticProviderError("request provider_model must explicitly match the PixelLab engine")
        if request.provider_config_version != PIXELLAB_CONFIG_VERSION:
            raise SemanticProviderError("unsupported PixelLab provider config version")
        if request.desired_candidate_count != 1:
            raise SemanticRequestError("direct PixelLab execution supports exactly one candidate")
        expected_bindings = _normalize_bindings(request, selected, bindings)
        by_role = {item.role: item.content_sha256 for item in expected_bindings}
        width, height = request.resolved_dimensions()
        return cls(
            request.digest(), PIXELLAB_PROVIDER_ID, PIXELLAB_ADAPTER_VERSION, request.provider_config_version,
            selected, request.provider_workflow_version, width, height, request.seed, _provider_seed(request.seed, request.digest()),
            request.description, request.negative_description, _map_control("outline", request.outline), _map_control("shading", request.shading), _map_control("detail", request.detail), _map_control("view", request.view), _map_control("direction", request.direction), request.isometric, request.no_background, request.coverage_percentage,
            by_role.get(ImageInputRole.INIT), by_role.get(ImageInputRole.STYLE), by_role.get(ImageInputRole.COLOR_REFERENCE),
            None if request.init_strength is None else round(request.init_strength * 1000),
        )

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema, "schema_version": self.schema_version, "request_digest": self.request_digest,
            "provider": {"id": self.provider_id, "version": self.provider_version, "config_version": self.provider_config_version},
            "engine": self.engine, "workflow_version": self.workflow_version,
            "image_size": {"width": self.width, "height": self.height},
            "original_seed": typed_seed(self.original_seed), "provider_seed": self.provider_seed,
            "description": self.description, "negative_description": self.negative_description,
            "controls": {"outline": self.outline, "shading": self.shading, "detail": self.detail, "view": self.view, "direction": self.direction, "isometric": self.isometric},
            "no_background": self.no_background, "coverage_percentage": self.coverage_percentage,
            "image_bindings": {"INIT": self.init_image_sha256, "STYLE": self.style_image_sha256, "COLOR_REFERENCE": self.color_image_sha256},
            "init_strength": self.init_strength,
        }

    def canonical_bytes(self) -> bytes:
        return canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return canonical_digest(self.canonical_dict())

    @property
    def job_digest(self) -> str:
        return self.digest()

    def sdk_kwargs(self, bindings: tuple[PixelLabExecutionBinding, ...] = ()) -> dict[str, object]:
        by_role = {item.role: item for item in bindings}
        kwargs: dict[str, object] = {"description": self.description, "image_size": {"width": self.width, "height": self.height}, "negative_description": self.negative_description or "", "seed": self.provider_seed, "no_background": self.no_background, "isometric": self.isometric}
        for label, value in (("outline", self.outline), ("shading", self.shading), ("detail", self.detail), ("view", self.view), ("direction", self.direction), ("coverage_percentage", self.coverage_percentage)):
            if value is not None:
                kwargs[label] = value
        if self.init_image_sha256 is not None:
            binding = by_role.get(ImageInputRole.INIT)
            if binding is None:
                raise SemanticProviderError("INIT bytes are missing for PixelLab execution")
            kwargs["init_image"] = _decode_pil(binding.image_bytes)
            kwargs["init_image_strength"] = self.init_strength if self.init_strength is not None else 1000
        if self.color_image_sha256 is not None:
            binding = by_role.get(ImageInputRole.COLOR_REFERENCE)
            if binding is None:
                raise SemanticProviderError("COLOR_REFERENCE bytes are missing for PixelLab execution")
            kwargs["color_image"] = _decode_pil(binding.image_bytes)
        if self.style_image_sha256 is not None:
            binding = by_role.get(ImageInputRole.STYLE)
            if binding is None:
                raise SemanticProviderError("STYLE bytes are missing for PixelLab execution")
            kwargs["style_image"] = _decode_pil(binding.image_bytes)
        return kwargs


def _decode_pil(raw: bytes) -> object:
    try:
        from PIL import Image

        with Image.open(BytesIO(raw)) as image:
            return image.convert("RGBA")
    except ImportError as exc:
        raise ProviderUnavailableError("PixelLab image execution requires the optional PIL dependency") from exc
    except Exception as exc:
        raise SemanticProviderError("PixelLab input bytes are not a decodable image") from exc


def _response_image_bytes(response: object) -> tuple[bytes, tuple[int, int]]:
    image = getattr(response, "image", response)
    raw = getattr(image, "raw_bytes", None)
    dimensions = getattr(image, "size", None)
    if isinstance(raw, bytes):
        if not isinstance(dimensions, tuple) or len(dimensions) != 2:
            raise SemanticProviderError("PixelLab response image dimensions are missing")
        return bytes(raw), (int(dimensions[0]), int(dimensions[1]))
    pil_method = getattr(image, "pil_image", None)
    if not callable(pil_method):
        raise SemanticProviderError("PixelLab response does not expose an image")
    pil_image = pil_method()
    size = getattr(pil_image, "size", None)
    if not isinstance(size, tuple) or len(size) != 2:
        raise SemanticProviderError("PixelLab response image dimensions are missing")
    stream = BytesIO()
    pil_image.save(stream, format="PNG", optimize=False)
    return stream.getvalue(), (int(size[0]), int(size[1]))


@dataclass(frozen=True, slots=True)
class PixelLabResultManifest:
    request_digest: str
    job_digest: str
    provider_id: str
    provider_version: str
    provider_config_version: str
    engine: str
    workflow_version: str
    original_seed: int | str
    provider_seed: int
    returned_width: int | None
    returned_height: int | None
    raw_image_sha256: str | None
    media_type: str | None
    status: CandidateStatus | str
    usage_usd: float | None = None
    failure_reason: str | None = None
    audit_metadata: Mapping[str, object] = field(default_factory=dict)
    schema: str = PIXELLAB_RESULT_SCHEMA
    schema_version: int = PIXELLAB_RESULT_SCHEMA_VERSION

    @classmethod
    def from_candidate(cls, candidate: SemanticImageCandidate, job: PixelLabJobSpec, *, usage_usd: float | None = None) -> "PixelLabResultManifest":
        return cls(candidate.request_digest, job.digest(), candidate.provider_id, candidate.provider_version, job.provider_config_version, job.engine, candidate.workflow_version, job.original_seed, job.provider_seed, candidate.returned_width, candidate.returned_height, candidate.raw_image_sha256, "image/png" if candidate.is_success else None, candidate.status, usage_usd, candidate.failure_reason, {})

    @classmethod
    def success(cls, job: PixelLabJobSpec, *, raw_image_sha256: str, returned_width: int, returned_height: int, workflow_version: str | None = None, media_type: str = "image/png", usage_usd: float | None = None, audit_metadata: Mapping[str, object] | None = None) -> "PixelLabResultManifest":
        return cls(job.request_digest, job.digest(), job.provider_id, job.provider_version, job.provider_config_version, job.engine, workflow_version or job.workflow_version, job.original_seed, job.provider_seed, returned_width, returned_height, raw_image_sha256, _text(media_type, "media_type"), CandidateStatus.SUCCESS, usage_usd, None, audit_metadata or {})

    @classmethod
    def failure(cls, job: PixelLabJobSpec, *, reason: str, workflow_version: str | None = None, audit_metadata: Mapping[str, object] | None = None) -> "PixelLabResultManifest":
        return cls(job.request_digest, job.digest(), job.provider_id, job.provider_version, job.provider_config_version, job.engine, workflow_version or job.workflow_version, job.original_seed, job.provider_seed, None, None, None, None, CandidateStatus.FAILURE, None, _text(reason, "failure_reason"), audit_metadata or {})

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "schema_version": self.schema_version, "request_digest": self.request_digest, "job_digest": self.job_digest, "provider": {"id": self.provider_id, "version": self.provider_version, "config_version": self.provider_config_version}, "engine": self.engine, "workflow_version": self.workflow_version, "original_seed": typed_seed(self.original_seed), "provider_seed": self.provider_seed, "returned_dimensions": {"width": self.returned_width, "height": self.returned_height} if self.returned_width is not None else None, "raw_image_sha256": self.raw_image_sha256, "media_type": self.media_type, "status": self.status.value if isinstance(self.status, CandidateStatus) else self.status, "usage": {"usd": self.usage_usd} if self.usage_usd is not None else None, "failure_reason": self.failure_reason, "audit_metadata": dict(self.audit_metadata)}

    def canonical_bytes(self) -> bytes:
        return canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return canonical_digest(self.canonical_dict())


class PixelLabProvider(SemanticGeneratorProvider):
    """Explicit official PixelLab adapter; default operation remains offline."""

    def __init__(self, *, engine: str = "PIXFLUX", runtime_config: PixelLabRuntimeConfig | None = None, client: object | None = None, bindings: Iterable[PixelLabExecutionBinding] | Mapping[object, object] | None = None) -> None:
        selected = engine.upper()
        if selected not in ("PIXFLUX", "BITFORGE"):
            raise SemanticProviderError("PixelLab engine must be PIXFLUX or BITFORGE")
        self.engine = selected
        self.runtime_config = runtime_config or PixelLabRuntimeConfig.from_env()
        self._client = client
        self._bindings = bindings

    @property
    def provider_id(self) -> str:
        return PIXELLAB_PROVIDER_ID

    @property
    def provider_version(self) -> str:
        return PIXELLAB_ADAPTER_VERSION

    @property
    def capabilities(self) -> SemanticCapabilities:
        return SemanticCapabilities(text_to_image=True, negative_prompt=True, transparent_background=True, init_image=True, palette_color_reference=True, view_direction_controls=True, isometric=True, style_image=self.engine == "BITFORGE")

    @property
    def capability_metadata(self) -> dict[str, object]:
        """Provider-specific truthful capabilities beyond the SP01 flags."""
        return {
            "provider_id": PIXELLAB_PROVIDER_ID,
            "engine": self.engine,
            "exact_dimensions": True,
            "deterministic_provider_seed": True,
            "mapped_controls": {key: dict(value) for key, value in PIXELLAB_CONTROL_MAP.items()},
            "supports_generic_reference": False,
            "supports_style": self.engine == "BITFORGE",
            "supports_init": True,
            "supports_color_reference": True,
            "supports_usage_audit": True,
        }

    def validate_request(self, request: SemanticGenerationRequest) -> None:
        super().validate_request(request)
        if request.provider_id != PIXELLAB_PROVIDER_ID:
            raise SemanticProviderError("PixelLab requires explicit provider_id PIXELLAB")
        if request.provider_model is None or request.provider_model.upper() != self.engine:
            raise SemanticProviderError("request provider_model does not match the selected PixelLab engine")
        PixelLabJobSpec.from_request(request, engine=self.engine, bindings=self._bindings)

    def prepare_job(self, request: SemanticGenerationRequest, *, bindings: Iterable[PixelLabExecutionBinding] | Mapping[object, object] | None = None) -> PixelLabJobSpec:
        selected_bindings = self._bindings if bindings is None else bindings
        return PixelLabJobSpec.from_request(request, engine=self.engine, bindings=selected_bindings)

    def _default_client(self) -> object:
        if not self.runtime_config.secret:
            raise ProviderUnavailableError("PixelLab requires local PIXELLAB_SECRET for explicit execution")
        try:
            import pixellab
        except ImportError as exc:
            raise ProviderUnavailableError("optional PixelLab package is unavailable") from exc
        client_type = getattr(pixellab, "Client", None)
        if client_type is None:
            raise ProviderUnavailableError("optional PixelLab package does not expose Client")
        return client_type(secret=self.runtime_config.secret, base_url=self.runtime_config.base_url)

    def generate(self, request: SemanticGenerationRequest) -> SemanticImageCandidate:
        job = self.prepare_job(request)
        try:
            client = self._client or self._default_client()
            kwargs = job.sdk_kwargs(tuple(_normalize_bindings(request, self.engine, self._bindings)))
            method_name = "generate_image_pixflux" if self.engine == "PIXFLUX" else "generate_image_bitforge"
            method = getattr(client, method_name, None)
            if not callable(method):
                raise ProviderUnavailableError(f"PixelLab client lacks {method_name}")
            response = method(**kwargs)
            raw, dimensions = _response_image_bytes(response)
            if dimensions != (job.width, job.height):
                return SemanticImageCandidate.failure(request, candidate_id=f"pixellab-{job.digest()[:24]}", provider_id=PIXELLAB_PROVIDER_ID, provider_version=PIXELLAB_ADAPTER_VERSION, workflow_version=request.provider_workflow_version, reason="PixelLab returned dimensions do not match the requested dimensions")
            usage = getattr(response, "usage", None)
            usage_usd = getattr(usage, "usd", None)
            metadata = {"job_digest": job.digest(), "engine": job.engine, "provider_seed": job.provider_seed, "usage": {"usd": usage_usd} if usage_usd is not None else None}
            return SemanticImageCandidate.success(request, candidate_id=f"pixellab-{job.digest()[:24]}", provider_id=PIXELLAB_PROVIDER_ID, provider_version=PIXELLAB_ADAPTER_VERSION, workflow_version=request.provider_workflow_version, image_bytes=raw, returned_width=dimensions[0], returned_height=dimensions[1], model_id=request.provider_model, generation_metadata=metadata)
        except ProviderUnavailableError as exc:
            return SemanticImageCandidate.failure(request, candidate_id=f"pixellab-{job.digest()[:24]}", provider_id=PIXELLAB_PROVIDER_ID, provider_version=PIXELLAB_ADAPTER_VERSION, workflow_version=request.provider_workflow_version, reason=str(exc), status=CandidateStatus.UNAVAILABLE)
        except Exception:
            # Never echo SDK errors: they may contain credentials or URLs.
            return SemanticImageCandidate.failure(request, candidate_id=f"pixellab-{job.digest()[:24]}", provider_id=PIXELLAB_PROVIDER_ID, provider_version=PIXELLAB_ADAPTER_VERSION, workflow_version=request.provider_workflow_version, reason="PixelLab execution failed", status=CandidateStatus.FAILURE)

    def manifest_for(self, candidate: SemanticImageCandidate, request: SemanticGenerationRequest, *, usage_usd: float | None = None) -> PixelLabResultManifest:
        return PixelLabResultManifest.from_candidate(candidate, self.prepare_job(request), usage_usd=usage_usd)


PixelLabDirectProvider = PixelLabProvider


__all__ = [
    "PIXELLAB_ADAPTER_VERSION", "PIXELLAB_CONFIG_VERSION", "PIXELLAB_CONTROL_MAP", "PIXELLAB_DEFAULT_BASE_URL", "PIXELLAB_PROVIDER_ID", "PIXELLAB_RESULT_SCHEMA", "PixelLabDirectProvider", "PixelLabExecutionBinding", "PixelLabJobSpec", "PixelLabProvider", "PixelLabResultManifest", "PixelLabRuntimeConfig",
]
