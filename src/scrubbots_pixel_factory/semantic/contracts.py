"""Provider-neutral semantic generation contracts for SP01.

This module deliberately stops at the raw semantic-image boundary.  It does
not normalize images into logical grids and therefore cannot create an M08
artwork bundle by accident; that boundary belongs to SP03.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
import base64
import hashlib
import json
import math
import re
from types import MappingProxyType
from typing import Any

from ..contracts import Difficulty, parse_difficulty, resolve_dimensions, validate_dimensions
from ..core.rng import DeterministicRNG


SEMANTIC_REQUEST_SCHEMA = "scrubbots-semantic-generation-request"
SEMANTIC_REQUEST_SCHEMA_VERSION = 1
SEMANTIC_CANDIDATE_SCHEMA = "scrubbots-semantic-image-candidate"
SEMANTIC_CANDIDATE_SCHEMA_VERSION = 1
SEMANTIC_CAPABILITIES_SCHEMA = "scrubbots-semantic-provider-capabilities"
SEMANTIC_CAPABILITIES_SCHEMA_VERSION = 1
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class SemanticContractError(ValueError):
    """Base error for malformed semantic requests, descriptors or results."""


class SemanticRequestError(SemanticContractError):
    """Raised when a semantic request violates its output-class contract."""


class SemanticCandidateError(SemanticContractError):
    """Raised when a provider result is not a complete typed boundary value."""


class SemanticProviderError(SemanticContractError):
    """Base provider-boundary error."""


class SemanticProvenanceError(SemanticProviderError):
    """Raised when a typed result is not bound to its executing request/provider."""


class UnsupportedCapabilityError(SemanticProviderError):
    """Raised when a provider cannot truthfully satisfy a request feature."""


class ProviderUnavailableError(SemanticProviderError):
    """Raised when a provider is configured but unavailable."""


class SemanticNormalizationRequiredError(SemanticCandidateError):
    """Raised when raw semantic art is used as if SP03 had normalized it."""


class OutputClass(str, Enum):
    """The two intentionally separate semantic output contracts."""

    LEVEL_ART = "LEVEL_ART"
    ASSET_ART = "ASSET_ART"

    @classmethod
    def parse(cls, value: object) -> "OutputClass":
        if isinstance(value, cls):
            return value
        if type(value) is not str:
            raise SemanticRequestError("output_class must be LEVEL_ART or ASSET_ART")
        try:
            return cls(value.upper())
        except ValueError as exc:
            raise SemanticRequestError("output_class must be LEVEL_ART or ASSET_ART") from exc


class ImageInputRole(str, Enum):
    REFERENCE = "REFERENCE"
    STYLE = "STYLE"
    INIT = "INIT"
    COLOR_REFERENCE = "COLOR_REFERENCE"
    INPAINT = "INPAINT"

    @classmethod
    def parse(cls, value: object) -> "ImageInputRole":
        if isinstance(value, cls):
            return value
        if type(value) is not str:
            raise SemanticContractError("image descriptor role is invalid")
        aliases = {"COLOR": cls.COLOR_REFERENCE, "PALETTE": cls.COLOR_REFERENCE}
        try:
            normalized = value.upper()
            return aliases[normalized] if normalized in aliases else cls(normalized)
        except ValueError as exc:
            raise SemanticContractError("image descriptor role is invalid") from exc


class CandidateStatus(str, Enum):
    SUCCESS = "SUCCESS"
    UNAVAILABLE = "UNAVAILABLE"
    UNSUPPORTED = "UNSUPPORTED"
    FAILURE = "FAILURE"


def _freeze(value: object, path: str = "value") -> object:
    if value is None or type(value) is bool or type(value) is str:
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise SemanticContractError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise SemanticContractError(f"{path} mapping keys must be strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[{index}]") for index, item in enumerate(value))
    raise SemanticContractError(f"{path} must contain JSON-compatible values")


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _nonblank(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise SemanticContractError(f"{label} must be a non-empty string")
    return value.strip()


def _request_nonblank(value: object, label: str) -> str:
    try:
        return _nonblank(value, label)
    except SemanticContractError as exc:
        raise SemanticRequestError(str(exc)) from exc


def _candidate_nonblank(value: object, label: str) -> str:
    try:
        return _nonblank(value, label)
    except SemanticContractError as exc:
        raise SemanticCandidateError(str(exc)) from exc


def _seed(value: object) -> int | str:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise SemanticRequestError("seed must be an integer or string, excluding bool")
    if isinstance(value, str) and not value:
        raise SemanticRequestError("seed must not be empty")
    return value


def _optional_strength(value: object, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
        raise SemanticRequestError(f"{label} must be a finite number from 0 through 1")
    return float(value)


def _optional_dimension(value: object, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > 1024:
        raise SemanticRequestError(f"{label} must be an integer from 1 through 1024")
    return value


@dataclass(frozen=True, slots=True)
class ImageInputDescriptor:
    """Content-identified image input; local filesystem paths are non-identity."""

    role: ImageInputRole | str
    content_sha256: str
    media_type: str | None = None
    width: int | None = None
    height: int | None = None
    source_label: str | None = None
    # Accepted for import ergonomics but intentionally excluded from identity.
    local_path: str | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        role = ImageInputRole.parse(self.role)
        if type(self.content_sha256) is not str or _SHA256.fullmatch(self.content_sha256) is None:
            raise SemanticContractError("content_sha256 must be a lowercase SHA-256 hex digest")
        media_type = None if self.media_type is None else _nonblank(self.media_type, "media_type")
        width, height = _optional_dimension(self.width, "image width"), _optional_dimension(self.height, "image height")
        if (width is None) != (height is None):
            raise SemanticContractError("image width and height must be supplied together")
        label = None if self.source_label is None else _nonblank(self.source_label, "source_label")
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "media_type", media_type)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)
        object.__setattr__(self, "source_label", label)

    @property
    def identity_dict(self) -> dict[str, object]:
        # A path-like source label is treated as a non-portable local hint.
        label = self.source_label
        if label is not None and ("/" in label or "\\" in label or ":" in label):
            label = None
        return {"role": self.role.value, "content_sha256": self.content_sha256, "media_type": self.media_type, "width": self.width, "height": self.height, "source_label": label}

    def canonical_dict(self) -> dict[str, object]:
        return dict(self.identity_dict)

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


OUTLINE_VALUES = frozenset({"NONE", "SINGLE", "DOUBLE", "DARK", "COLORED", "AUTO"})
SHADING_VALUES = frozenset({"NONE", "FLAT", "BASIC", "SOFT", "DITHERED", "AUTO"})
DETAIL_VALUES = frozenset({"LOW", "MEDIUM", "HIGH", "AUTO"})
VIEW_VALUES = frozenset({"FRONT", "SIDE", "TOP_DOWN", "THREE_QUARTER", "ISOMETRIC", "AUTO"})
DIRECTION_VALUES = frozenset({"N", "NE", "E", "SE", "S", "SW", "W", "NW", "AUTO"})


def _choice(value: object, allowed: frozenset[str], label: str) -> str:
    if type(value) is not str or value.upper() not in allowed:
        raise SemanticRequestError(f"{label} is unsupported")
    return value.upper()


@dataclass(frozen=True, slots=True)
class SemanticGenerationRequest:
    """Immutable, canonical semantic intent before provider execution."""

    output_class: OutputClass | str
    description: str
    schema_version: int = SEMANTIC_REQUEST_SCHEMA_VERSION
    negative_description: str | None = None
    semantic_category: str | None = None
    difficulty: Difficulty | str | None = None
    width: int | None = None
    height: int | None = None
    seed: int | str = "semantic-default-seed"
    no_background: bool = False
    outline: str = "NONE"
    shading: str = "FLAT"
    detail: str = "MEDIUM"
    view: str = "FRONT"
    direction: str = "S"
    isometric: bool = False
    coverage_percentage: float = 80.0
    reference_images: tuple[ImageInputDescriptor, ...] | Sequence[ImageInputDescriptor] = ()
    style_image: ImageInputDescriptor | None = None
    style_strength: float | None = None
    init_image: ImageInputDescriptor | None = None
    init_strength: float | None = None
    color_reference: ImageInputDescriptor | None = None
    provider_id: str = "UNSPECIFIED"
    provider_workflow_version: str = "semantic-workflow-v1"
    provider_model: str | None = None
    provider_config_version: str = "1"
    desired_candidate_count: int = 1
    audit_metadata: Mapping[str, object] | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        output_class = OutputClass.parse(self.output_class)
        description = _request_nonblank(self.description, "description")
        if isinstance(self.schema_version, bool) or self.schema_version != SEMANTIC_REQUEST_SCHEMA_VERSION:
            raise SemanticRequestError("unsupported semantic request schema version")
        negative = None if self.negative_description is None else _request_nonblank(self.negative_description, "negative_description")
        category = None if self.semantic_category is None else _request_nonblank(self.semantic_category, "semantic_category")
        difficulty = None if self.difficulty is None else parse_difficulty(self.difficulty)
        width, height = _optional_dimension(self.width, "width"), _optional_dimension(self.height, "height")
        seed = _seed(self.seed)
        if type(self.no_background) is not bool or type(self.isometric) is not bool:
            raise SemanticRequestError("no_background and isometric must be booleans")
        outline = _choice(self.outline, OUTLINE_VALUES, "outline")
        shading = _choice(self.shading, SHADING_VALUES, "shading")
        detail = _choice(self.detail, DETAIL_VALUES, "detail")
        view = _choice(self.view, VIEW_VALUES, "view")
        direction = _choice(self.direction, DIRECTION_VALUES, "direction")
        if isinstance(self.coverage_percentage, bool) or not isinstance(self.coverage_percentage, (int, float)) or not math.isfinite(float(self.coverage_percentage)) or not 0.0 <= float(self.coverage_percentage) <= 100.0:
            raise SemanticRequestError("coverage_percentage must be a finite number from 0 through 100")
        if isinstance(self.desired_candidate_count, bool) or not isinstance(self.desired_candidate_count, int) or not 1 <= self.desired_candidate_count <= 10000:
            raise SemanticRequestError("desired_candidate_count must be an integer from 1 through 10000")
        try:
            references = tuple(item if isinstance(item, ImageInputDescriptor) else ImageInputDescriptor(**item) for item in self.reference_images)  # type: ignore[arg-type]
        except (TypeError, SemanticContractError) as exc:
            raise SemanticRequestError("reference_images must contain image descriptors") from exc
        if any(image.role is not ImageInputRole.REFERENCE for image in references):
            raise SemanticRequestError("reference_images entries must use the REFERENCE role")
        for label, image in (("style_image", self.style_image), ("init_image", self.init_image), ("color_reference", self.color_reference)):
            if image is not None and not isinstance(image, ImageInputDescriptor):
                raise SemanticRequestError(f"{label} must be an ImageInputDescriptor")
        if self.style_image is not None and self.style_image.role is not ImageInputRole.STYLE:
            raise SemanticRequestError("style_image must use the STYLE role")
        if self.init_image is not None and self.init_image.role is not ImageInputRole.INIT:
            raise SemanticRequestError("init_image must use the INIT role")
        if self.color_reference is not None and self.color_reference.role is not ImageInputRole.COLOR_REFERENCE:
            raise SemanticRequestError("color_reference must use the COLOR_REFERENCE role")
        style_strength = _optional_strength(self.style_strength, "style_strength")
        init_strength = _optional_strength(self.init_strength, "init_strength")
        if self.style_image is None and style_strength is not None:
            raise SemanticRequestError("style_strength requires style_image")
        if self.init_image is None and init_strength is not None:
            raise SemanticRequestError("init_strength requires init_image")
        if self.style_image is not None and style_strength is None:
            style_strength = 1.0
        if self.init_image is not None and init_strength is None:
            init_strength = 1.0
        provider_id = _request_nonblank(self.provider_id, "provider_id")
        workflow = _request_nonblank(self.provider_workflow_version, "provider_workflow_version")
        model = None if self.provider_model is None else _request_nonblank(self.provider_model, "provider_model")
        config = _request_nonblank(self.provider_config_version, "provider_config_version")
        if output_class is OutputClass.LEVEL_ART:
            if difficulty is None:
                raise SemanticRequestError("LEVEL_ART requires a ScrubBots difficulty")
            try:
                resolve_dimensions(difficulty, width, height, seed=DeterministicRNG(seed).stage_seed("dimension"))
            except (TypeError, ValueError) as exc:
                raise SemanticRequestError(str(exc)) from exc
        else:
            if difficulty is not None:
                raise SemanticRequestError("ASSET_ART must not carry a ScrubBots difficulty")
            if width is None or height is None:
                raise SemanticRequestError("ASSET_ART requires explicit width and height")
        frozen_audit = None if self.audit_metadata is None else _freeze(self.audit_metadata, "audit_metadata")
        if frozen_audit is not None and not isinstance(frozen_audit, Mapping):
            raise SemanticRequestError("audit_metadata must be a mapping")
        object.__setattr__(self, "output_class", output_class)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "negative_description", negative)
        object.__setattr__(self, "semantic_category", category)
        object.__setattr__(self, "difficulty", difficulty)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)
        object.__setattr__(self, "seed", seed)
        object.__setattr__(self, "outline", outline)
        object.__setattr__(self, "shading", shading)
        object.__setattr__(self, "detail", detail)
        object.__setattr__(self, "view", view)
        object.__setattr__(self, "direction", direction)
        object.__setattr__(self, "coverage_percentage", float(self.coverage_percentage))
        object.__setattr__(self, "reference_images", references)
        object.__setattr__(self, "style_strength", style_strength)
        object.__setattr__(self, "init_strength", init_strength)
        object.__setattr__(self, "provider_id", provider_id)
        object.__setattr__(self, "provider_workflow_version", workflow)
        object.__setattr__(self, "provider_model", model)
        object.__setattr__(self, "provider_config_version", config)
        object.__setattr__(self, "audit_metadata", frozen_audit)

    def resolved_dimensions(self) -> tuple[int, int]:
        if self.output_class is OutputClass.ASSET_ART:
            return self.width, self.height  # type: ignore[return-value]
        return resolve_dimensions(self.difficulty, self.width, self.height, seed=DeterministicRNG(self.seed).stage_seed("dimension"))  # type: ignore[arg-type]

    @property
    def requested_dimensions(self) -> tuple[int, int]:
        return self.resolved_dimensions()

    @property
    def reference_image_descriptors(self) -> tuple[ImageInputDescriptor, ...]:
        return self.reference_images

    @property
    def color_reference_image(self) -> ImageInputDescriptor | None:
        return self.color_reference

    def required_capabilities(self) -> tuple[str, ...]:
        required: list[str] = ["text_to_image"]
        if self.negative_description is not None:
            required.append("negative_prompt")
        if self.no_background:
            required.append("transparent_background")
        if self.reference_images:
            required.append("reference_images")
        if self.style_image is not None:
            required.append("style_image")
        if self.init_image is not None:
            required.append("init_image")
        if self.color_reference is not None:
            required.append("palette_color_reference")
        if self.view != "FRONT" or self.direction != "S" or self.isometric:
            required.append("view_direction_controls")
        if self.isometric:
            required.append("isometric")
        return tuple(dict.fromkeys(required))

    def canonical_dict(self) -> dict[str, object]:
        width, height = self.resolved_dimensions()
        return {"schema": SEMANTIC_REQUEST_SCHEMA, "schema_version": self.schema_version, "output_class": self.output_class.value, "description": self.description, "negative_description": self.negative_description, "semantic_category": self.semantic_category, "difficulty": self.difficulty.value if self.difficulty is not None else None, "width": self.width, "height": self.height, "resolved_dimensions": {"width": width, "height": height}, "seed": {"type": "int" if isinstance(self.seed, int) else "string", "value": self.seed}, "no_background": self.no_background, "outline": self.outline, "shading": self.shading, "detail": self.detail, "view": self.view, "direction": self.direction, "isometric": self.isometric, "coverage_percentage": self.coverage_percentage, "reference_images": [image.canonical_dict() for image in self.reference_images], "style_image": self.style_image.canonical_dict() if self.style_image is not None else None, "style_strength": self.style_strength, "init_image": self.init_image.canonical_dict() if self.init_image is not None else None, "init_strength": self.init_strength, "color_reference": self.color_reference.canonical_dict() if self.color_reference is not None else None, "provider_id": self.provider_id, "provider_workflow_version": self.provider_workflow_version, "provider_model": self.provider_model, "provider_config_version": self.provider_config_version, "desired_candidate_count": self.desired_candidate_count}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def canonical_json(self) -> str:
        return self.canonical_bytes().decode("utf-8")

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class SemanticCapabilities:
    """Versioned truthful provider feature declaration."""

    version: int = SEMANTIC_CAPABILITIES_SCHEMA_VERSION
    text_to_image: bool = False
    negative_prompt: bool = False
    transparent_background: bool = False
    reference_images: bool = False
    style_image: bool = False
    init_image: bool = False
    palette_color_reference: bool = False
    inpaint: bool = False
    view_direction_controls: bool = False
    isometric: bool = False
    rotation_variants: bool = False
    animation: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.version, bool) or self.version != SEMANTIC_CAPABILITIES_SCHEMA_VERSION:
            raise SemanticProviderError("unsupported semantic capability schema version")
        for name in self.__dataclass_fields__:
            if name != "version" and type(getattr(self, name)) is not bool:
                raise SemanticProviderError(f"capability {name} must be boolean")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": SEMANTIC_CAPABILITIES_SCHEMA, "version": self.version, **{name: getattr(self, name) for name in self.__dataclass_fields__ if name != "version"}}

    def unsupported_for(self, request: SemanticGenerationRequest) -> tuple[str, ...]:
        return tuple(name for name in request.required_capabilities() if not getattr(self, name))


# Descriptive aliases make the public boundary discoverable without creating
# alternate value types or changing canonical identity.
SemanticOutputClass = OutputClass
SemanticImageInputDescriptor = ImageInputDescriptor
ImageDescriptor = ImageInputDescriptor
SemanticProviderCapabilities = SemanticCapabilities


@dataclass(frozen=True, slots=True)
class SemanticImageCandidate:
    """Raw provider image boundary; this type has no logical-grid fields."""

    candidate_id: str
    request_digest: str
    provider_id: str
    provider_version: str
    workflow_version: str
    model_id: str | None
    seed: int | str | None
    requested_width: int
    requested_height: int
    returned_width: int | None
    returned_height: int | None
    raw_image_sha256: str | None
    image_bytes: bytes | None
    status: CandidateStatus | str
    failure_reason: str | None = None
    retry_reason: str | None = None
    reference_images: tuple[ImageInputDescriptor, ...] = ()
    style_image: ImageInputDescriptor | None = None
    init_image: ImageInputDescriptor | None = None
    color_reference: ImageInputDescriptor | None = None
    generation_metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        candidate_id = _candidate_nonblank(self.candidate_id, "candidate_id")
        if type(self.request_digest) is not str or _SHA256.fullmatch(self.request_digest) is None:
            raise SemanticCandidateError("request_digest must be a SHA-256 hex digest")
        provider_id, provider_version, workflow = (_candidate_nonblank(self.provider_id, "provider_id"), _candidate_nonblank(self.provider_version, "provider_version"), _candidate_nonblank(self.workflow_version, "workflow_version"))
        model_id = None if self.model_id is None else _candidate_nonblank(self.model_id, "model_id")
        try:
            status = self.status if isinstance(self.status, CandidateStatus) else CandidateStatus(self.status)
        except (TypeError, ValueError) as exc:
            raise SemanticCandidateError("candidate status is invalid") from exc
        for label, value in (("requested_width", self.requested_width), ("requested_height", self.requested_height), ("returned_width", self.returned_width), ("returned_height", self.returned_height)):
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > 1024):
                raise SemanticCandidateError(f"{label} is invalid")
        if isinstance(self.seed, bool) or self.seed is not None and not isinstance(self.seed, (int, str)) or isinstance(self.seed, str) and not self.seed:
            raise SemanticCandidateError("candidate seed is invalid")
        raw = self.image_bytes
        if raw is not None and not isinstance(raw, bytes):
            raise SemanticCandidateError("image_bytes must be immutable bytes")
        if status is CandidateStatus.SUCCESS:
            if raw is None or not raw:
                raise SemanticCandidateError("successful candidate requires non-empty image_bytes")
            if self.returned_width is None or self.returned_height is None:
                raise SemanticCandidateError("successful candidate requires returned dimensions")
            actual_hash = hashlib.sha256(raw).hexdigest()
            if self.raw_image_sha256 != actual_hash:
                raise SemanticCandidateError("raw_image_sha256 does not match image_bytes")
            if self.failure_reason is not None or self.retry_reason is not None:
                raise SemanticCandidateError("successful candidate cannot carry failure reasons")
        else:
            if raw is not None or self.raw_image_sha256 is not None or self.returned_width is not None or self.returned_height is not None:
                raise SemanticCandidateError("non-success candidate cannot carry image output")
            if type(self.failure_reason) is not str or not self.failure_reason.strip():
                raise SemanticCandidateError("non-success candidate requires failure_reason")
        if self.retry_reason is not None and (type(self.retry_reason) is not str or not self.retry_reason.strip()):
            raise SemanticCandidateError("retry_reason must be a non-empty string when supplied")
        frozen = _freeze(self.generation_metadata, "generation_metadata")
        if not isinstance(frozen, Mapping):
            raise SemanticCandidateError("generation_metadata must be a mapping")
        try:
            references = tuple(image if isinstance(image, ImageInputDescriptor) else ImageInputDescriptor(**image) for image in self.reference_images)  # type: ignore[arg-type]
        except (TypeError, SemanticContractError) as exc:
            raise SemanticCandidateError("reference_images must contain image descriptors") from exc
        if any(image.role is not ImageInputRole.REFERENCE for image in references):
            raise SemanticCandidateError("reference_images entries must use the REFERENCE role")
        images: dict[str, ImageInputDescriptor | None] = {}
        for label, image, role in (("style_image", self.style_image, ImageInputRole.STYLE), ("init_image", self.init_image, ImageInputRole.INIT), ("color_reference", self.color_reference, ImageInputRole.COLOR_REFERENCE)):
            if image is None:
                images[label] = None
                continue
            try:
                descriptor = image if isinstance(image, ImageInputDescriptor) else ImageInputDescriptor(**image)  # type: ignore[arg-type]
            except (TypeError, SemanticContractError) as exc:
                raise SemanticCandidateError(f"{label} must be an image descriptor") from exc
            if descriptor.role is not role:
                raise SemanticCandidateError(f"{label} must use the {role.value} role")
            images[label] = descriptor
        object.__setattr__(self, "candidate_id", candidate_id)
        object.__setattr__(self, "provider_id", provider_id)
        object.__setattr__(self, "provider_version", provider_version)
        object.__setattr__(self, "workflow_version", workflow)
        object.__setattr__(self, "model_id", model_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "generation_metadata", frozen)
        object.__setattr__(self, "reference_images", references)
        object.__setattr__(self, "style_image", images["style_image"])
        object.__setattr__(self, "init_image", images["init_image"])
        object.__setattr__(self, "color_reference", images["color_reference"])

    @classmethod
    def success(cls, request: SemanticGenerationRequest, *, candidate_id: str, provider_id: str, provider_version: str, workflow_version: str, image_bytes: bytes, returned_width: int, returned_height: int, model_id: str | None = None, generation_metadata: Mapping[str, object] | None = None) -> "SemanticImageCandidate":
        width, height = request.resolved_dimensions()
        return cls(candidate_id, request.digest(), provider_id, provider_version, workflow_version, model_id, request.seed, width, height, returned_width, returned_height, hashlib.sha256(image_bytes).hexdigest(), bytes(image_bytes), CandidateStatus.SUCCESS, reference_images=request.reference_images, style_image=request.style_image, init_image=request.init_image, color_reference=request.color_reference, generation_metadata=generation_metadata or {})

    @classmethod
    def failure(cls, request: SemanticGenerationRequest, *, candidate_id: str, provider_id: str, provider_version: str, workflow_version: str, reason: str, status: CandidateStatus | str = CandidateStatus.FAILURE, retry_reason: str | None = None) -> "SemanticImageCandidate":
        width, height = request.resolved_dimensions()
        return cls(candidate_id, request.digest(), provider_id, provider_version, workflow_version, request.provider_model, request.seed, width, height, None, None, None, None, status, reason, retry_reason, reference_images=request.reference_images, style_image=request.style_image, init_image=request.init_image, color_reference=request.color_reference)

    @property
    def is_success(self) -> bool:
        return self.status is CandidateStatus.SUCCESS

    @property
    def ok(self) -> bool:
        return self.is_success

    def identity_dict(self) -> dict[str, object]:
        """Return deterministic candidate identity without audit metadata."""
        return {"schema": SEMANTIC_CANDIDATE_SCHEMA, "schema_version": SEMANTIC_CANDIDATE_SCHEMA_VERSION, "candidate_id": self.candidate_id, "request_digest": self.request_digest, "provider": {"id": self.provider_id, "version": self.provider_version, "workflow_version": self.workflow_version, "model_id": self.model_id}, "seed": {"type": "int" if isinstance(self.seed, int) else "string", "value": self.seed} if self.seed is not None else None, "requested_dimensions": {"width": self.requested_width, "height": self.requested_height}, "returned_dimensions": {"width": self.returned_width, "height": self.returned_height} if self.returned_width is not None else None, "raw_image_sha256": self.raw_image_sha256, "reference_images": [image.canonical_dict() for image in self.reference_images], "style_image": self.style_image.canonical_dict() if self.style_image is not None else None, "init_image": self.init_image.canonical_dict() if self.init_image is not None else None, "color_reference": self.color_reference.canonical_dict() if self.color_reference is not None else None, "status": self.status.value, "failure_reason": self.failure_reason, "retry_reason": self.retry_reason}

    def canonical_dict(self) -> dict[str, object]:
        return {**self.identity_dict(), "image_bytes_base64": base64.b64encode(self.image_bytes).decode("ascii") if self.image_bytes is not None else None, "generation_metadata": _thaw(self.generation_metadata)}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(_canonical_bytes(self.identity_dict())).hexdigest()

    def as_m08_artwork(self) -> object:
        raise SemanticNormalizationRequiredError("semantic raw image requires future SP03 normalization before M08 artwork export")


SemanticProviderResult = SemanticImageCandidate
ProviderResult = SemanticImageCandidate
SemanticResult = SemanticImageCandidate


__all__ = [
    "CandidateStatus", "DETAIL_VALUES", "DIRECTION_VALUES", "ImageDescriptor", "ImageInputDescriptor", "ImageInputRole", "OUTLINE_VALUES", "OutputClass", "ProviderResult", "ProviderUnavailableError", "SEMANTIC_CANDIDATE_SCHEMA", "SEMANTIC_CANDIDATE_SCHEMA_VERSION", "SEMANTIC_CAPABILITIES_SCHEMA", "SEMANTIC_CAPABILITIES_SCHEMA_VERSION", "SEMANTIC_REQUEST_SCHEMA", "SEMANTIC_REQUEST_SCHEMA_VERSION", "SemanticCandidateError", "SemanticContractError", "SemanticGenerationRequest", "SemanticImageCandidate", "SemanticImageInputDescriptor", "SemanticNormalizationRequiredError", "SemanticOutputClass", "SemanticProviderCapabilities", "SemanticProviderError", "SemanticProvenanceError", "SemanticProviderResult", "SemanticRequestError", "SemanticResult", "SemanticCapabilities", "SHADING_VALUES", "UnsupportedCapabilityError", "VIEW_VALUES",
]
