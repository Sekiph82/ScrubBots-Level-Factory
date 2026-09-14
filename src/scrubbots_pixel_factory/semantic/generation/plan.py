"""Provider-neutral, deterministic reference/style generation planning."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re
from types import MappingProxyType
from typing import Any, Mapping

from ...core.rng import DeterministicRNG
from ..contracts import ImageInputDescriptor, ImageInputRole, OutputClass, SemanticGenerationRequest
from ..normalization.core import _canonical_bytes


SEMANTIC_GENERATION_PLAN_SCHEMA = "scrubbots-semantic-generation-plan"
SEMANTIC_GENERATION_PLAN_SCHEMA_VERSION = 1
SEMANTIC_GENERATION_INPUT_SCHEMA = "scrubbots-semantic-generation-input-binding"
SEMANTIC_GENERATION_VARIANT_SCHEMA = "scrubbots-semantic-generation-variant"
SEMANTIC_GENERATION_POLICY_VERSION = "SEMANTIC_GENERATION_PLAN_V1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_PLAN_TOKEN = object()
_BINDING_TOKEN = object()
_VARIANT_TOKEN = object()


class SemanticGenerationPlanError(ValueError):
    """Raised when a deterministic SP07 plan cannot be built or verified."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require_digest(value: object, label: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise SemanticGenerationPlanError("INVALID_DIGEST", f"{label} must be a lowercase SHA-256 digest")
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


def _nonblank(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise SemanticGenerationPlanError("INVALID_PLAN", f"{label} must be non-empty")
    return value


@dataclass(frozen=True, slots=True)
class SemanticInputBinding:
    """One role-correct, content-addressed input retained by a plan."""

    ordinal: int
    role: ImageInputRole
    descriptor_digest: str
    content_sha256: str
    canonical_identity: Mapping[str, object]
    schema: str = SEMANTIC_GENERATION_INPUT_SCHEMA
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _BINDING_TOKEN:
            raise SemanticGenerationPlanError("UNSEALED_INPUT", "input bindings require checked construction")
        self._validate_values()
        object.__setattr__(self, "_construction_fingerprint", self._fingerprint())

    def _validate_values(self) -> None:
        if self.schema != SEMANTIC_GENERATION_INPUT_SCHEMA:
            raise SemanticGenerationPlanError("UNSUPPORTED_SCHEMA", "unsupported input-binding schema")
        if type(self.ordinal) is not int or self.ordinal < 0:
            raise SemanticGenerationPlanError("INVALID_INPUT", "input ordinal must be non-negative")
        try:
            role = ImageInputRole.parse(self.role)
        except Exception as exc:
            raise SemanticGenerationPlanError("INVALID_INPUT_ROLE", "input role is unsupported") from exc
        _require_digest(self.descriptor_digest, "descriptor_digest")
        _require_digest(self.content_sha256, "content_sha256")
        if not isinstance(self.canonical_identity, Mapping):
            raise SemanticGenerationPlanError("INVALID_INPUT", "canonical input identity must be immutable mapping data")
        identity = dict(_thaw(self.canonical_identity))
        expected = {"role", "content_sha256", "media_type", "width", "height", "source_label"}
        if set(identity) != expected:
            raise SemanticGenerationPlanError("INVALID_INPUT", "canonical input identity fields are not exact")
        if identity["role"] != role.value or identity["content_sha256"] != self.content_sha256 or _digest(identity) != self.descriptor_digest:
            raise SemanticGenerationPlanError("INPUT_IDENTITY_MISMATCH", "input binding is not bound to its canonical descriptor identity")
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "canonical_identity", _freeze(identity))

    def _payload(self) -> dict[str, object]:
        return {"schema": self.schema, "ordinal": self.ordinal, "role": self.role.value, "descriptor_digest": self.descriptor_digest, "content_sha256": self.content_sha256, "canonical_identity": _thaw(self.canonical_identity)}

    def _fingerprint(self) -> str:
        return _digest(self._payload())

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _BINDING_TOKEN:
            raise SemanticGenerationPlanError("UNSEALED_INPUT", "input-binding construction seal is invalid")
        self._validate_values()
        if getattr(self, "_construction_fingerprint", None) != self._fingerprint():
            raise SemanticGenerationPlanError("TAMPERED_INPUT", "input-binding construction fingerprint is invalid")

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return self._payload()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class SemanticGenerationVariant:
    """One deterministic provider-execution intent, without executing it."""

    ordinal: int
    candidate_id: str
    request_digest: str
    seed: str
    provider_id: str
    provider_model: str | None
    workflow_version: str
    config_version: str
    output_class: OutputClass
    resolved_width: int
    resolved_height: int
    input_binding_digests: tuple[str, ...]
    schema: str = SEMANTIC_GENERATION_VARIANT_SCHEMA
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _VARIANT_TOKEN:
            raise SemanticGenerationPlanError("UNSEALED_VARIANT", "variants require checked construction")
        self._validate_values()
        object.__setattr__(self, "_construction_fingerprint", self._fingerprint())

    def _validate_values(self) -> None:
        if self.schema != SEMANTIC_GENERATION_VARIANT_SCHEMA:
            raise SemanticGenerationPlanError("UNSUPPORTED_SCHEMA", "unsupported generation-variant schema")
        if type(self.ordinal) is not int or self.ordinal < 0 or type(self.candidate_id) is not str or not self.candidate_id.startswith("sp07-"):
            raise SemanticGenerationPlanError("INVALID_VARIANT", "variant ordinal or candidate ID is not canonical")
        _require_digest(self.request_digest, "request_digest")
        _require_digest(self.seed, "variant seed")
        for label, value in (("provider_id", self.provider_id), ("workflow_version", self.workflow_version), ("config_version", self.config_version)):
            _nonblank(value, label)
        if self.provider_model is not None:
            _nonblank(self.provider_model, "provider_model")
        try:
            output_class = OutputClass.parse(self.output_class)
        except Exception as exc:
            raise SemanticGenerationPlanError("INVALID_VARIANT", "variant output class is unsupported") from exc
        if type(self.resolved_width) is not int or type(self.resolved_height) is not int or self.resolved_width < 1 or self.resolved_height < 1:
            raise SemanticGenerationPlanError("INVALID_VARIANT", "variant resolved dimensions are invalid")
        if not isinstance(self.input_binding_digests, tuple) or any(type(value) is not str or _SHA256.fullmatch(value) is None for value in self.input_binding_digests):
            raise SemanticGenerationPlanError("INVALID_VARIANT", "variant input binding identities are invalid")
        object.__setattr__(self, "output_class", output_class)

    def _payload(self) -> dict[str, object]:
        return {"schema": self.schema, "ordinal": self.ordinal, "candidate_id": self.candidate_id, "request_digest": self.request_digest, "seed": self.seed, "provider": {"id": self.provider_id, "model": self.provider_model, "workflow_version": self.workflow_version, "config_version": self.config_version}, "output_class": self.output_class.value, "resolved_dimensions": {"width": self.resolved_width, "height": self.resolved_height}, "input_binding_digests": list(self.input_binding_digests)}

    def _fingerprint(self) -> str:
        return _digest(self._payload())

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _VARIANT_TOKEN:
            raise SemanticGenerationPlanError("UNSEALED_VARIANT", "variant construction seal is invalid")
        self._validate_values()
        if getattr(self, "_construction_fingerprint", None) != self._fingerprint():
            raise SemanticGenerationPlanError("TAMPERED_VARIANT", "variant construction fingerprint is invalid")

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return self._payload()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class SemanticReferenceStylePlan:
    """Sealed deterministic plan bound to one canonical semantic request."""

    request_digest: str
    output_class: OutputClass
    requested_width: int | None
    requested_height: int | None
    resolved_width: int
    resolved_height: int
    seed_type: str
    seed_value: int | str
    desired_candidate_count: int
    provider_id: str
    provider_model: str | None
    workflow_version: str
    config_version: str
    semantic_category: str | None
    no_background: bool
    outline: str
    shading: str
    detail: str
    view: str
    direction: str
    isometric: bool
    coverage_percentage: float
    input_bindings: tuple[SemanticInputBinding, ...]
    style_strength: float | None
    init_strength: float | None
    variants: tuple[SemanticGenerationVariant, ...]
    schema: str = SEMANTIC_GENERATION_PLAN_SCHEMA
    schema_version: int = SEMANTIC_GENERATION_PLAN_SCHEMA_VERSION
    policy_version: str = SEMANTIC_GENERATION_POLICY_VERSION
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _PLAN_TOKEN:
            raise SemanticGenerationPlanError("UNSEALED_PLAN", "generation plans require checked construction")
        self._validate_values()
        object.__setattr__(self, "_construction_fingerprint", self._fingerprint())

    def _validate_values(self) -> None:
        if self.schema != SEMANTIC_GENERATION_PLAN_SCHEMA or self.schema_version != SEMANTIC_GENERATION_PLAN_SCHEMA_VERSION or self.policy_version != SEMANTIC_GENERATION_POLICY_VERSION:
            raise SemanticGenerationPlanError("UNSUPPORTED_SCHEMA", "unsupported generation-plan schema/policy")
        _require_digest(self.request_digest, "request_digest")
        try:
            output_class = OutputClass.parse(self.output_class)
        except Exception as exc:
            raise SemanticGenerationPlanError("INVALID_PLAN", "output class is unsupported") from exc
        if any(type(value) is not int or value < 1 for value in (self.resolved_width, self.resolved_height)):
            raise SemanticGenerationPlanError("INVALID_PLAN", "resolved dimensions are invalid")
        if self.requested_width is not None and (type(self.requested_width) is not int or self.requested_width < 1):
            raise SemanticGenerationPlanError("INVALID_PLAN", "requested width is invalid")
        if self.requested_height is not None and (type(self.requested_height) is not int or self.requested_height < 1):
            raise SemanticGenerationPlanError("INVALID_PLAN", "requested height is invalid")
        if self.seed_type not in {"int", "string"} or (self.seed_type == "int" and (type(self.seed_value) is not int or isinstance(self.seed_value, bool))) or (self.seed_type == "string" and type(self.seed_value) is not str):
            raise SemanticGenerationPlanError("INVALID_PLAN", "typed seed identity is invalid")
        if type(self.desired_candidate_count) is not int or self.desired_candidate_count < 1 or len(self.variants) != self.desired_candidate_count:
            raise SemanticGenerationPlanError("INVALID_PLAN", "candidate count does not match variants")
        for label, value in (("provider_id", self.provider_id), ("workflow_version", self.workflow_version), ("config_version", self.config_version), ("outline", self.outline), ("shading", self.shading), ("detail", self.detail), ("view", self.view), ("direction", self.direction)):
            _nonblank(value, label)
        if self.provider_model is not None:
            _nonblank(self.provider_model, "provider_model")
        if type(self.no_background) is not bool or type(self.isometric) is not bool or type(self.coverage_percentage) is not float or not 0.0 <= self.coverage_percentage <= 100.0:
            raise SemanticGenerationPlanError("INVALID_PLAN", "request intent types are invalid")
        bindings = tuple(self.input_bindings)
        if any(not isinstance(binding, SemanticInputBinding) for binding in bindings) or tuple(binding.ordinal for binding in bindings) != tuple(range(len(bindings))):
            raise SemanticGenerationPlanError("INVALID_PLAN", "input bindings are not ordered")
        seen_references: set[tuple[str, str]] = set()
        for binding in bindings:
            binding._assert_integrity()
            if binding.role is ImageInputRole.REFERENCE:
                key = (binding.role.value, binding.content_sha256)
                if key in seen_references:
                    raise SemanticGenerationPlanError("DUPLICATE_INPUT", "duplicate reference content/role is ambiguous")
                seen_references.add(key)
        variants = tuple(self.variants)
        if tuple(variant.ordinal for variant in variants) != tuple(range(self.desired_candidate_count)) or len({variant.candidate_id for variant in variants}) != len(variants):
            raise SemanticGenerationPlanError("INVALID_PLAN", "variants are not in canonical ordinal order")
        binding_digests = tuple(binding.digest() for binding in bindings)
        for variant in variants:
            variant._assert_integrity()
            if variant.request_digest != self.request_digest or variant.output_class is not output_class or variant.resolved_width != self.resolved_width or variant.resolved_height != self.resolved_height or variant.input_binding_digests != binding_digests:
                raise SemanticGenerationPlanError("INVALID_PLAN", "variant is not bound to the plan")
        if self.style_strength is not None and (type(self.style_strength) is not float or not 0.0 <= self.style_strength <= 1.0):
            raise SemanticGenerationPlanError("INVALID_PLAN", "style strength is invalid")
        if self.init_strength is not None and (type(self.init_strength) is not float or not 0.0 <= self.init_strength <= 1.0):
            raise SemanticGenerationPlanError("INVALID_PLAN", "init strength is invalid")
        object.__setattr__(self, "output_class", output_class)

    def _payload(self) -> dict[str, object]:
        return {"schema": self.schema, "schema_version": self.schema_version, "policy_version": self.policy_version, "request_digest": self.request_digest, "output_class": self.output_class.value, "requested_dimensions": {"width": self.requested_width, "height": self.requested_height}, "resolved_dimensions": {"width": self.resolved_width, "height": self.resolved_height}, "seed": {"type": self.seed_type, "value": self.seed_value}, "desired_candidate_count": self.desired_candidate_count, "provider": {"id": self.provider_id, "model": self.provider_model, "workflow_version": self.workflow_version, "config_version": self.config_version}, "intent": {"semantic_category": self.semantic_category, "no_background": self.no_background, "outline": self.outline, "shading": self.shading, "detail": self.detail, "view": self.view, "direction": self.direction, "isometric": self.isometric, "coverage_percentage": self.coverage_percentage}, "input_bindings": [binding.canonical_dict() for binding in self.input_bindings], "style_strength": self.style_strength, "init_strength": self.init_strength, "variants": [variant.canonical_dict() for variant in self.variants]}

    def _fingerprint(self) -> str:
        return _digest(self._payload())

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _PLAN_TOKEN:
            raise SemanticGenerationPlanError("UNSEALED_PLAN", "generation-plan construction seal is invalid")
        self._validate_values()
        if getattr(self, "_construction_fingerprint", None) != self._fingerprint():
            raise SemanticGenerationPlanError("TAMPERED_PLAN", "generation-plan construction fingerprint is invalid")

    @property
    def candidate_variants(self) -> tuple[SemanticGenerationVariant, ...]:
        self._assert_integrity()
        return self.variants

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return self._payload()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())

    def verify_against_request(self, request: SemanticGenerationRequest) -> bool:
        self._assert_integrity()
        rebuilt = plan_reference_style_generation(request)
        return rebuilt.canonical_bytes() == self.canonical_bytes()


def _build_binding(ordinal: int, descriptor: ImageInputDescriptor) -> SemanticInputBinding:
    instance = object.__new__(SemanticInputBinding)
    values = {"ordinal": ordinal, "role": descriptor.role, "descriptor_digest": descriptor.digest(), "content_sha256": descriptor.content_sha256, "canonical_identity": _freeze(descriptor.canonical_dict()), "schema": SEMANTIC_GENERATION_INPUT_SCHEMA, "_construction_token": _BINDING_TOKEN}
    for key, value in values.items():
        object.__setattr__(instance, key, value)
    instance._validate_values()
    object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
    return instance


def _build_variant(ordinal: int, request: SemanticGenerationRequest, request_digest: str, seed: str, bindings: tuple[SemanticInputBinding, ...]) -> SemanticGenerationVariant:
    candidate_id = "sp07-" + _digest({"schema": SEMANTIC_GENERATION_VARIANT_SCHEMA, "request_digest": request_digest, "ordinal": ordinal, "seed": seed})
    instance = object.__new__(SemanticGenerationVariant)
    values = {"ordinal": ordinal, "candidate_id": candidate_id, "request_digest": request_digest, "seed": seed, "provider_id": request.provider_id, "provider_model": request.provider_model, "workflow_version": request.provider_workflow_version, "config_version": request.provider_config_version, "output_class": request.output_class, "resolved_width": request.resolved_dimensions()[0], "resolved_height": request.resolved_dimensions()[1], "input_binding_digests": tuple(binding.digest() for binding in bindings), "schema": SEMANTIC_GENERATION_VARIANT_SCHEMA, "_construction_token": _VARIANT_TOKEN}
    for key, value in values.items():
        object.__setattr__(instance, key, value)
    instance._validate_values()
    object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
    return instance


def _build_plan(request: SemanticGenerationRequest) -> SemanticReferenceStylePlan:
    request_digest = request.digest()
    descriptors = list(request.reference_images)
    for descriptor in (request.style_image, request.init_image, request.color_reference):
        if descriptor is not None:
            descriptors.append(descriptor)
    bindings = tuple(_build_binding(index, descriptor) for index, descriptor in enumerate(descriptors))
    planner_rng = DeterministicRNG(request.seed).child("semantic-generation")
    variants = tuple(_build_variant(index, request, request_digest, planner_rng.retry_seed(index), bindings) for index in range(request.desired_candidate_count))
    resolved_width, resolved_height = request.resolved_dimensions()
    instance = object.__new__(SemanticReferenceStylePlan)
    values: dict[str, Any] = {"request_digest": request_digest, "output_class": request.output_class, "requested_width": request.width, "requested_height": request.height, "resolved_width": resolved_width, "resolved_height": resolved_height, "seed_type": "int" if isinstance(request.seed, int) else "string", "seed_value": request.seed, "desired_candidate_count": request.desired_candidate_count, "provider_id": request.provider_id, "provider_model": request.provider_model, "workflow_version": request.provider_workflow_version, "config_version": request.provider_config_version, "semantic_category": request.semantic_category, "no_background": request.no_background, "outline": request.outline, "shading": request.shading, "detail": request.detail, "view": request.view, "direction": request.direction, "isometric": request.isometric, "coverage_percentage": float(request.coverage_percentage), "input_bindings": bindings, "style_strength": request.style_strength, "init_strength": request.init_strength, "variants": variants, "schema": SEMANTIC_GENERATION_PLAN_SCHEMA, "schema_version": SEMANTIC_GENERATION_PLAN_SCHEMA_VERSION, "policy_version": SEMANTIC_GENERATION_POLICY_VERSION, "_construction_token": _PLAN_TOKEN}
    for key, value in values.items():
        object.__setattr__(instance, key, value)
    instance._validate_values()
    object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
    return instance


def plan_reference_style_generation(request: SemanticGenerationRequest) -> SemanticReferenceStylePlan:
    """Create a deterministic offline plan from one canonical request."""

    if not isinstance(request, SemanticGenerationRequest):
        raise SemanticGenerationPlanError("UNTRUSTED_REQUEST", "planning requires a canonical SemanticGenerationRequest")
    seen_reference_descriptors: set[tuple[str, str]] = set()
    for descriptor in request.reference_images:
        key = (descriptor.role.value, descriptor.content_sha256)
        if key in seen_reference_descriptors:
            raise SemanticGenerationPlanError("DUPLICATE_INPUT", "duplicate REFERENCE descriptor content/role is ambiguous")
        seen_reference_descriptors.add(key)
    try:
        return _build_plan(request)
    except SemanticGenerationPlanError:
        raise
    except Exception as exc:
        raise SemanticGenerationPlanError("INVALID_REQUEST", "canonical request could not be planned") from exc


__all__ = [
    "SEMANTIC_GENERATION_INPUT_SCHEMA", "SEMANTIC_GENERATION_PLAN_SCHEMA", "SEMANTIC_GENERATION_PLAN_SCHEMA_VERSION", "SEMANTIC_GENERATION_POLICY_VERSION", "SEMANTIC_GENERATION_VARIANT_SCHEMA", "SemanticGenerationPlanError", "SemanticGenerationVariant", "SemanticInputBinding", "SemanticReferenceStylePlan", "plan_reference_style_generation",
]
