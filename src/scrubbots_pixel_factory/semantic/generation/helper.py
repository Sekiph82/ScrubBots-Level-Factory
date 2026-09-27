"""Deterministic, offline semantic/procedural art-helper intents.

This boundary consumes the accepted semantic request and SP07 plan.  It only
creates bounded, auditable planning intents; it never creates image bytes,
logical art, gameplay data, or an acceptance/promotion decision.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import math
import re
from types import MappingProxyType
from typing import Any

from ..contracts import OutputClass, SemanticGenerationRequest
from ..normalization.core import _canonical_bytes
from .plan import (
    SemanticGenerationPlanError,
    SemanticGenerationVariant,
    SemanticInputBinding,
    SemanticReferenceStylePlan,
    plan_reference_style_generation,
)


SEMANTIC_ART_HELPER_SCHEMA = "scrubbots-semantic-art-helper-result"
SEMANTIC_ART_HELPER_SCHEMA_VERSION = 1
SEMANTIC_ART_HELPER_POLICY_VERSION = "SEMANTIC_ART_HELPER_V1"
SEMANTIC_ART_HELPER_INTENT_SCHEMA = "scrubbots-semantic-art-helper-intent"
SEMANTIC_ART_HELPER_VERSION = "semantic-art-helper-v1"
SEMANTIC_ART_HELPER_MAX_CANDIDATE_COUNT = 32
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_CANDIDATE_ID = re.compile(r"^sp07-[0-9a-f]{64}$")
_HELPER_TOKEN = object()
_INTENT_TOKEN = object()
_RECIPE_KEYS = frozenset(
    {
        "mode",
        "output_class",
        "resolved_dimensions",
        "semantic_category",
        "coverage_percentage",
        "no_background",
        "outline",
        "shading",
        "detail",
        "view",
        "direction",
        "isometric",
        "style_strength",
        "init_strength",
        "input_binding_digests",
    }
)


class SemanticArtHelperError(ValueError):
    """Raised when helper input, output, or restoration is not trustworthy."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


class SemanticArtHelperStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class SemanticArtHelperDisposition(str, Enum):
    PROCEDURAL_INTENTS = "PROCEDURAL_INTENTS"
    UNAVAILABLE_CAPABILITY = "UNAVAILABLE_CAPABILITY"


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require_digest(value: object, label: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise SemanticArtHelperError("INVALID_DIGEST", f"{label} must be a lowercase SHA-256 digest")
    return value


def _freeze(value: object, path: str = "value") -> object:
    if value is None or type(value) is bool or type(value) is str:
        return value
    if type(value) is int:
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise SemanticArtHelperError("INVALID_RECIPE", f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise SemanticArtHelperError("INVALID_RECIPE", f"{path} mapping keys must be strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[{index}]") for index, item in enumerate(value))
    raise SemanticArtHelperError("INVALID_RECIPE", f"{path} must contain JSON-compatible values")


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _nonblank(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise SemanticArtHelperError("INVALID_RESULT", f"{label} must be non-empty")
    return value


@dataclass(frozen=True, slots=True)
class SemanticHelperSeedIdentity:
    """The request seed with its type retained as part of helper identity."""

    seed_type: str
    value: int | str

    def __post_init__(self) -> None:
        if self.seed_type not in {"int", "string"}:
            raise SemanticArtHelperError("INVALID_SEED", "seed type must be int or string")
        if self.seed_type == "int" and (type(self.value) is not int or isinstance(self.value, bool)):
            raise SemanticArtHelperError("INVALID_SEED", "int seed identity must contain an integer")
        if self.seed_type == "string" and (type(self.value) is not str or not self.value):
            raise SemanticArtHelperError("INVALID_SEED", "string seed identity must contain a non-empty string")

    @classmethod
    def from_request(cls, request: SemanticGenerationRequest) -> "SemanticHelperSeedIdentity":
        return cls("int" if type(request.seed) is int else "string", request.seed)

    def canonical_dict(self) -> dict[str, object]:
        return {"type": self.seed_type, "value": self.value}


@dataclass(frozen=True, slots=True)
class SemanticArtHelperIntent:
    """One bounded procedural recipe, with no generated-art payload."""

    ordinal: int
    candidate_id: str
    request_digest: str
    plan_digest: str
    variant_seed: str
    input_binding_digests: tuple[str, ...]
    recipe: Mapping[str, object]
    schema: str = SEMANTIC_ART_HELPER_INTENT_SCHEMA
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _INTENT_TOKEN:
            raise SemanticArtHelperError("UNSEALED_INTENT", "helper intents require checked construction")
        self._validate_values()
        object.__setattr__(self, "_construction_fingerprint", self._fingerprint())

    def _validate_values(self) -> None:
        if self.schema != SEMANTIC_ART_HELPER_INTENT_SCHEMA:
            raise SemanticArtHelperError("UNSUPPORTED_SCHEMA", "unsupported helper-intent schema")
        if type(self.ordinal) is not int or self.ordinal < 0:
            raise SemanticArtHelperError("INVALID_INTENT", "intent ordinal must be non-negative")
        if type(self.candidate_id) is not str or _CANDIDATE_ID.fullmatch(self.candidate_id) is None:
            raise SemanticArtHelperError("INVALID_INTENT", "intent candidate identity is not canonical")
        _require_digest(self.request_digest, "intent request_digest")
        _require_digest(self.plan_digest, "intent plan_digest")
        _require_digest(self.variant_seed, "intent variant_seed")
        if not isinstance(self.input_binding_digests, tuple) or any(
            type(value) is not str or _SHA256.fullmatch(value) is None for value in self.input_binding_digests
        ):
            raise SemanticArtHelperError("INVALID_INTENT", "intent input identities are invalid")
        if not isinstance(self.recipe, Mapping):
            raise SemanticArtHelperError("INVALID_INTENT", "intent recipe must be immutable mapping data")
        recipe = dict(_thaw(self.recipe))
        if set(recipe) != _RECIPE_KEYS:
            raise SemanticArtHelperError("INVALID_RECIPE", "intent recipe fields are not exact")
        if recipe["mode"] != "BOUNDED_PROCEDURAL_INTENT":
            raise SemanticArtHelperError("INVALID_RECIPE", "intent mode is unsupported")
        if recipe["input_binding_digests"] != list(self.input_binding_digests):
            raise SemanticArtHelperError("INVALID_RECIPE", "intent input identities are inconsistent")
        dimensions = recipe["resolved_dimensions"]
        if not isinstance(dimensions, Mapping) or set(dimensions) != {"width", "height"}:
            raise SemanticArtHelperError("INVALID_RECIPE", "intent dimensions are malformed")
        if any(type(dimensions[key]) is not int or dimensions[key] < 1 for key in ("width", "height")):
            raise SemanticArtHelperError("INVALID_RECIPE", "intent dimensions are invalid")
        for key in ("output_class", "outline", "shading", "detail", "view", "direction"):
            _nonblank(recipe[key], f"recipe {key}")
        if type(recipe["no_background"]) is not bool or type(recipe["isometric"]) is not bool:
            raise SemanticArtHelperError("INVALID_RECIPE", "intent boolean controls are invalid")
        if type(recipe["coverage_percentage"]) is not float or not 0.0 <= recipe["coverage_percentage"] <= 100.0:
            raise SemanticArtHelperError("INVALID_RECIPE", "intent coverage is invalid")
        for key in ("style_strength", "init_strength"):
            value = recipe[key]
            if value is not None and (type(value) is not float or not 0.0 <= value <= 1.0):
                raise SemanticArtHelperError("INVALID_RECIPE", f"intent {key} is invalid")
        if recipe["semantic_category"] is not None:
            _nonblank(recipe["semantic_category"], "recipe semantic_category")
        object.__setattr__(self, "recipe", _freeze(recipe, "recipe"))

    def _payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "ordinal": self.ordinal,
            "candidate_id": self.candidate_id,
            "request_digest": self.request_digest,
            "plan_digest": self.plan_digest,
            "variant_seed": self.variant_seed,
            "input_binding_digests": list(self.input_binding_digests),
            "recipe": _thaw(self.recipe),
        }

    def _fingerprint(self) -> str:
        return _digest(self._payload())

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _INTENT_TOKEN:
            raise SemanticArtHelperError("UNSEALED_INTENT", "helper-intent construction seal is invalid")
        self._validate_values()
        if getattr(self, "_construction_fingerprint", None) != self._fingerprint():
            raise SemanticArtHelperError("TAMPERED_INTENT", "helper-intent construction fingerprint is invalid")

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return self._payload()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class SemanticArtHelperResult:
    """Immutable helper-only result, replayable from request and plan."""

    status: SemanticArtHelperStatus
    disposition: SemanticArtHelperDisposition
    request_digest: str
    plan_digest: str
    seed_identity: SemanticHelperSeedIdentity
    helper_version: str
    output_class: OutputClass
    resolved_width: int
    resolved_height: int
    requested_candidate_count: int
    input_bindings: tuple[SemanticInputBinding, ...]
    intents: tuple[SemanticArtHelperIntent, ...]
    reason: str | None
    output_kind: str = "SEMANTIC_HELPER_INTENT"
    recognizability_disposition: str = "NOT_EVALUATED"
    owner_acceptance_disposition: str = "NOT_EVALUATED"
    promotion_disposition: str = "NOT_ELIGIBLE"
    schema: str = SEMANTIC_ART_HELPER_SCHEMA
    schema_version: int = SEMANTIC_ART_HELPER_SCHEMA_VERSION
    policy_version: str = SEMANTIC_ART_HELPER_POLICY_VERSION
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _HELPER_TOKEN:
            raise SemanticArtHelperError("UNSEALED_RESULT", "helper results require checked construction")
        self._validate_values()
        object.__setattr__(self, "_construction_fingerprint", self._fingerprint())

    def _validate_values(self) -> None:
        try:
            status = self.status if isinstance(self.status, SemanticArtHelperStatus) else SemanticArtHelperStatus(self.status)
            disposition = self.disposition if isinstance(self.disposition, SemanticArtHelperDisposition) else SemanticArtHelperDisposition(self.disposition)
            output_class = self.output_class if isinstance(self.output_class, OutputClass) else OutputClass.parse(self.output_class)
        except (TypeError, ValueError) as exc:
            raise SemanticArtHelperError("INVALID_RESULT", "helper status, disposition, or output class is invalid") from exc
        if self.schema != SEMANTIC_ART_HELPER_SCHEMA or self.schema_version != SEMANTIC_ART_HELPER_SCHEMA_VERSION or self.policy_version != SEMANTIC_ART_HELPER_POLICY_VERSION:
            raise SemanticArtHelperError("UNSUPPORTED_SCHEMA", "unsupported helper result schema/policy")
        _require_digest(self.request_digest, "request_digest")
        _require_digest(self.plan_digest, "plan_digest")
        if not isinstance(self.seed_identity, SemanticHelperSeedIdentity):
            raise SemanticArtHelperError("INVALID_RESULT", "seed identity is not typed")
        if self.helper_version != SEMANTIC_ART_HELPER_VERSION:
            raise SemanticArtHelperError("UNSUPPORTED_VERSION", "unsupported helper version")
        if any(type(value) is not int or value < 1 for value in (self.resolved_width, self.resolved_height)):
            raise SemanticArtHelperError("INVALID_RESULT", "resolved dimensions are invalid")
        if type(self.requested_candidate_count) is not int or self.requested_candidate_count < 1:
            raise SemanticArtHelperError("INVALID_RESULT", "requested candidate count is invalid")
        bindings = tuple(self.input_bindings)
        if any(not isinstance(binding, SemanticInputBinding) for binding in bindings) or tuple(binding.ordinal for binding in bindings) != tuple(range(len(bindings))):
            raise SemanticArtHelperError("INVALID_RESULT", "input bindings are not ordered")
        for binding in bindings:
            binding._assert_integrity()
        intents = tuple(self.intents)
        if any(not isinstance(intent, SemanticArtHelperIntent) for intent in intents) or tuple(intent.ordinal for intent in intents) != tuple(range(len(intents))):
            raise SemanticArtHelperError("INVALID_RESULT", "helper intents are not ordered")
        binding_digests = tuple(binding.digest() for binding in bindings)
        for intent in intents:
            intent._assert_integrity()
            if intent.request_digest != self.request_digest or intent.plan_digest != self.plan_digest or tuple(intent.input_binding_digests) != binding_digests:
                raise SemanticArtHelperError("INVALID_RESULT", "helper intent is not bound to the result")
            recipe = dict(_thaw(intent.recipe))
            if recipe["output_class"] != output_class.value or recipe["resolved_dimensions"] != {"width": self.resolved_width, "height": self.resolved_height}:
                raise SemanticArtHelperError("INVALID_RESULT", "helper intent does not match result dimensions/class")
        if status is SemanticArtHelperStatus.AVAILABLE:
            if disposition is not SemanticArtHelperDisposition.PROCEDURAL_INTENTS or len(intents) != self.requested_candidate_count or self.requested_candidate_count > SEMANTIC_ART_HELPER_MAX_CANDIDATE_COUNT or self.reason is not None:
                raise SemanticArtHelperError("INVALID_RESULT", "available helper result is inconsistent")
        elif disposition is not SemanticArtHelperDisposition.UNAVAILABLE_CAPABILITY or intents or self.requested_candidate_count <= SEMANTIC_ART_HELPER_MAX_CANDIDATE_COUNT or not isinstance(self.reason, str) or not self.reason.strip():
            raise SemanticArtHelperError("INVALID_RESULT", "unavailable helper result is inconsistent")
        if self.output_kind != "SEMANTIC_HELPER_INTENT" or self.recognizability_disposition != "NOT_EVALUATED" or self.owner_acceptance_disposition != "NOT_EVALUATED" or self.promotion_disposition != "NOT_ELIGIBLE":
            raise SemanticArtHelperError("INVALID_RESULT", "helper output boundary is not fail-closed")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "disposition", disposition)
        object.__setattr__(self, "output_class", output_class)

    def _payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "policy_version": self.policy_version,
            "helper_version": self.helper_version,
            "status": self.status.value,
            "disposition": self.disposition.value,
            "request_digest": self.request_digest,
            "plan_digest": self.plan_digest,
            "seed": self.seed_identity.canonical_dict(),
            "output_class": self.output_class.value,
            "resolved_dimensions": {"width": self.resolved_width, "height": self.resolved_height},
            "requested_candidate_count": self.requested_candidate_count,
            "input_bindings": [binding.canonical_dict() for binding in self.input_bindings],
            "intents": [intent.canonical_dict() for intent in self.intents],
            "reason": self.reason,
            "boundary": {
                "output_kind": self.output_kind,
                "recognizability": self.recognizability_disposition,
                "owner_acceptance": self.owner_acceptance_disposition,
                "promotion": self.promotion_disposition,
            },
        }

    def _fingerprint(self) -> str:
        return _digest(self._payload())

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _HELPER_TOKEN:
            raise SemanticArtHelperError("UNSEALED_RESULT", "helper-result construction seal is invalid")
        self._validate_values()
        if getattr(self, "_construction_fingerprint", None) != self._fingerprint():
            raise SemanticArtHelperError("TAMPERED_RESULT", "helper-result construction fingerprint is invalid")

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return self._payload()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())

    def verify_against(self, request: SemanticGenerationRequest, plan: SemanticReferenceStylePlan) -> bool:
        expected = build_semantic_art_helper(request, plan)
        return expected.canonical_bytes() == self.canonical_bytes()

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], *, request: SemanticGenerationRequest, plan: SemanticReferenceStylePlan) -> "SemanticArtHelperResult":
        if not isinstance(value, Mapping):
            raise SemanticArtHelperError("MALFORMED_RESULT", "helper result must be a mapping")
        expected = build_semantic_art_helper(request, plan)
        try:
            actual_bytes = _canonical_bytes(value)
        except (TypeError, ValueError) as exc:
            raise SemanticArtHelperError("MALFORMED_RESULT", "helper result is not canonical JSON data") from exc
        if actual_bytes != expected.canonical_bytes():
            try:
                if not plan.verify_against_request(request):
                    raise SemanticArtHelperError("STALE_PLAN", "helper result was restored against a stale plan")
            except SemanticGenerationPlanError as exc:
                raise SemanticArtHelperError("STALE_PLAN", "helper result was restored against an invalid plan") from exc
            raise SemanticArtHelperError("TAMPERED_RESULT", "helper result does not match deterministic replay")
        return expected


def _build_intent(variant: SemanticGenerationVariant, plan: SemanticReferenceStylePlan) -> SemanticArtHelperIntent:
    binding_digests = tuple(binding.digest() for binding in plan.input_bindings)
    recipe = {
        "mode": "BOUNDED_PROCEDURAL_INTENT",
        "output_class": variant.output_class.value,
        "resolved_dimensions": {"width": variant.resolved_width, "height": variant.resolved_height},
        "semantic_category": plan.semantic_category,
        "coverage_percentage": plan.coverage_percentage,
        "no_background": plan.no_background,
        "outline": plan.outline,
        "shading": plan.shading,
        "detail": plan.detail,
        "view": plan.view,
        "direction": plan.direction,
        "isometric": plan.isometric,
        "style_strength": plan.style_strength,
        "init_strength": plan.init_strength,
        "input_binding_digests": list(binding_digests),
    }
    instance = object.__new__(SemanticArtHelperIntent)
    values = {
        "ordinal": variant.ordinal,
        "candidate_id": variant.candidate_id,
        "request_digest": plan.request_digest,
        "plan_digest": plan.digest(),
        "variant_seed": variant.seed,
        "input_binding_digests": binding_digests,
        "recipe": _freeze(recipe, "recipe"),
        "schema": SEMANTIC_ART_HELPER_INTENT_SCHEMA,
        "_construction_token": _INTENT_TOKEN,
    }
    for key, value in values.items():
        object.__setattr__(instance, key, value)
    instance._validate_values()
    object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
    return instance


def _build_result(request: SemanticGenerationRequest, plan: SemanticReferenceStylePlan) -> SemanticArtHelperResult:
    seed_identity = SemanticHelperSeedIdentity.from_request(request)
    status = SemanticArtHelperStatus.AVAILABLE
    disposition = SemanticArtHelperDisposition.PROCEDURAL_INTENTS
    reason = None
    intents: tuple[SemanticArtHelperIntent, ...] = ()
    if plan.desired_candidate_count > SEMANTIC_ART_HELPER_MAX_CANDIDATE_COUNT:
        status = SemanticArtHelperStatus.UNAVAILABLE
        disposition = SemanticArtHelperDisposition.UNAVAILABLE_CAPABILITY
        reason = f"requested candidate count exceeds helper bound of {SEMANTIC_ART_HELPER_MAX_CANDIDATE_COUNT}"
    else:
        intents = tuple(_build_intent(variant, plan) for variant in plan.candidate_variants)
    instance = object.__new__(SemanticArtHelperResult)
    values = {
        "status": status,
        "disposition": disposition,
        "request_digest": request.digest(),
        "plan_digest": plan.digest(),
        "seed_identity": seed_identity,
        "helper_version": SEMANTIC_ART_HELPER_VERSION,
        "output_class": plan.output_class,
        "resolved_width": plan.resolved_width,
        "resolved_height": plan.resolved_height,
        "requested_candidate_count": plan.desired_candidate_count,
        "input_bindings": plan.input_bindings,
        "intents": intents,
        "reason": reason,
        "output_kind": "SEMANTIC_HELPER_INTENT",
        "recognizability_disposition": "NOT_EVALUATED",
        "owner_acceptance_disposition": "NOT_EVALUATED",
        "promotion_disposition": "NOT_ELIGIBLE",
        "schema": SEMANTIC_ART_HELPER_SCHEMA,
        "schema_version": SEMANTIC_ART_HELPER_SCHEMA_VERSION,
        "policy_version": SEMANTIC_ART_HELPER_POLICY_VERSION,
        "_construction_token": _HELPER_TOKEN,
    }
    for key, value in values.items():
        object.__setattr__(instance, key, value)
    instance._validate_values()
    object.__setattr__(instance, "_construction_fingerprint", instance._fingerprint())
    return instance


def build_semantic_art_helper(request: SemanticGenerationRequest, plan: SemanticReferenceStylePlan | None = None) -> SemanticArtHelperResult:
    """Build a deterministic helper-only result from the accepted contracts."""

    if not isinstance(request, SemanticGenerationRequest):
        raise SemanticArtHelperError("UNTRUSTED_REQUEST", "helper requires a canonical SemanticGenerationRequest")
    if plan is None:
        plan = plan_reference_style_generation(request)
    if not isinstance(plan, SemanticReferenceStylePlan):
        raise SemanticArtHelperError("UNTRUSTED_PLAN", "helper requires a canonical SemanticReferenceStylePlan")
    try:
        if not plan.verify_against_request(request):
            raise SemanticArtHelperError("STALE_PLAN", "helper plan does not match the canonical request")
    except SemanticGenerationPlanError as exc:
        raise SemanticArtHelperError("STALE_PLAN", "helper plan is invalid or tampered") from exc
    return _build_result(request, plan)


def restore_semantic_art_helper(value: Mapping[str, Any], *, request: SemanticGenerationRequest, plan: SemanticReferenceStylePlan) -> SemanticArtHelperResult:
    """Restore only an exact deterministic replay bound to current contracts."""

    return SemanticArtHelperResult.from_dict(value, request=request, plan=plan)


__all__ = [
    "SEMANTIC_ART_HELPER_SCHEMA",
    "SEMANTIC_ART_HELPER_SCHEMA_VERSION",
    "SEMANTIC_ART_HELPER_POLICY_VERSION",
    "SEMANTIC_ART_HELPER_INTENT_SCHEMA",
    "SEMANTIC_ART_HELPER_VERSION",
    "SEMANTIC_ART_HELPER_MAX_CANDIDATE_COUNT",
    "SemanticArtHelperError",
    "SemanticArtHelperStatus",
    "SemanticArtHelperDisposition",
    "SemanticHelperSeedIdentity",
    "SemanticArtHelperIntent",
    "SemanticArtHelperResult",
    "build_semantic_art_helper",
    "restore_semantic_art_helper",
]
