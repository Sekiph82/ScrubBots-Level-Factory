"""Versioned, provider-neutral contracts; this module contains no adapter implementation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from .config import Environment
from .validation import DryRunReport

PROVIDER_CONTRACT_VERSION = "1.0"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class ProviderFeature(StrEnum):
    STAGING_PUBLISH = "STAGING_PUBLISH"
    PRODUCTION_PROMOTION = "PRODUCTION_PROMOTION"
    OBJECT_WRITE = "OBJECT_WRITE"
    OBJECT_DELETE = "OBJECT_DELETE"
    INTEGRITY_VERIFY = "INTEGRITY_VERIFY"
    ATOMIC_MANIFEST_PUBLISH = "ATOMIC_MANIFEST_PUBLISH"
    CONDITIONAL_WRITE = "CONDITIONAL_WRITE"
    ROLLBACK = "ROLLBACK"


class ProviderResultCategory(StrEnum):
    SUCCESS = "SUCCESS"
    UNAVAILABLE = "UNAVAILABLE"
    UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"
    CONFLICT_STALE_PRECONDITION = "CONFLICT_STALE_PRECONDITION"
    INTEGRITY_MISMATCH = "INTEGRITY_MISMATCH"
    UNAUTHORIZED_REFERENCE = "UNAUTHORIZED_REFERENCE"
    TRANSIENT_FAILURE = "TRANSIENT_FAILURE"
    INVALID_REQUEST = "INVALID_REQUEST"


@dataclass(frozen=True, slots=True)
class ProviderIdentity:
    provider_id: str
    provider_version: str
    contract_version: str = PROVIDER_CONTRACT_VERSION

    def to_dict(self) -> dict[str, str]:
        return {
            "contract_version": self.contract_version if self.contract_version == PROVIDER_CONTRACT_VERSION else "[INVALID]",
            "provider_id": self.provider_id if _safe_identifier(self.provider_id) else "[INVALID]",
            "provider_version": self.provider_version if _safe_identifier(self.provider_version) else "[INVALID]",
        }


@dataclass(frozen=True, slots=True)
class ProviderCapability:
    """Secret-free declaration of environment and feature support."""

    capability_id: str
    capability_version: str
    environments: tuple[Environment, ...]
    features: tuple[ProviderFeature, ...]
    contract_version: str = PROVIDER_CONTRACT_VERSION

    @property
    def supports_staging_publish(self) -> bool:
        return ProviderFeature.STAGING_PUBLISH in self.features

    @property
    def supports_production_promotion(self) -> bool:
        return ProviderFeature.PRODUCTION_PROMOTION in self.features

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version if self.contract_version == PROVIDER_CONTRACT_VERSION else "[INVALID]",
            "capability_id": self.capability_id if _safe_identifier(self.capability_id) else "[INVALID]",
            "capability_version": self.capability_version if _safe_identifier(self.capability_version) else "[INVALID]",
            "environments": [item.value for item in self.environments if isinstance(item, Environment)],
            "features": [item.value for item in self.features if isinstance(item, ProviderFeature)],
        }


@dataclass(frozen=True, slots=True)
class ProviderResult:
    """Stable result without free-form messages where a secret could be echoed."""

    result_version: str
    category: ProviderResultCategory
    provider_id: str
    environment: Environment
    content_digest: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "result_version": self.result_version if self.result_version == PROVIDER_CONTRACT_VERSION else "[INVALID]",
            "category": self.category.value if isinstance(self.category, ProviderResultCategory) else ProviderResultCategory.INVALID_REQUEST.value,
            "provider_id": self.provider_id if _safe_identifier(self.provider_id) else "[INVALID]",
            "environment": self.environment.value if isinstance(self.environment, Environment) else "unknown",
            "content_digest": self.content_digest if isinstance(self.content_digest, str) and re.fullmatch(r"[a-f0-9]{64}", self.content_digest) else None,
        }


@dataclass(frozen=True, slots=True)
class ProviderObjectBytesResult:
    """Read-only exact object bytes with explicit key and provider result identity."""

    result_version: str
    category: ProviderResultCategory
    provider_id: str
    environment: Environment
    object_key: str
    content_bytes: bytes | None


@dataclass(frozen=True, slots=True)
class CapabilityNegotiationResult:
    negotiation_version: str
    accepted: bool
    environment: str
    required_features: tuple[str, ...]
    missing_features: tuple[str, ...]
    result_category: ProviderResultCategory

    def to_dict(self) -> dict[str, object]:
        return {
            "negotiation_version": self.negotiation_version if self.negotiation_version == PROVIDER_CONTRACT_VERSION else "[INVALID]",
            "accepted": self.accepted is True,
            "environment": self.environment if self.environment in {item.value for item in Environment} else "unknown",
            "required_features": [value for value in self.required_features if value in {item.value for item in ProviderFeature}],
            "missing_features": [value for value in self.missing_features if value in {item.value for item in ProviderFeature}],
            "result_category": self.result_category.value if isinstance(self.result_category, ProviderResultCategory) else ProviderResultCategory.INVALID_REQUEST.value,
        }


def _safe_identifier(value: object) -> bool:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        return False
    from .secret_refs import _contains_obvious_secret

    return not _contains_obvious_secret(value)


def validate_provider_identity(identity: object) -> bool:
    return (
        isinstance(identity, ProviderIdentity)
        and identity.contract_version == PROVIDER_CONTRACT_VERSION
        and _safe_identifier(identity.provider_id)
        and _safe_identifier(identity.provider_version)
    )


def validate_provider_capability(capability: object) -> bool:
    return (
        isinstance(capability, ProviderCapability)
        and capability.contract_version == PROVIDER_CONTRACT_VERSION
        and _safe_identifier(capability.capability_id)
        and _safe_identifier(capability.capability_version)
        and isinstance(capability.environments, tuple)
        and bool(capability.environments)
        and all(isinstance(item, Environment) for item in capability.environments)
        and tuple(sorted(set(capability.environments), key=lambda item: item.value)) == capability.environments
        and isinstance(capability.features, tuple)
        and all(isinstance(item, ProviderFeature) for item in capability.features)
        and tuple(sorted(set(capability.features), key=lambda item: item.value)) == capability.features
    )


def serialize_provider_capability(capability: ProviderCapability) -> str:
    value = capability.to_dict() if validate_provider_capability(capability) else {
        "contract_version": PROVIDER_CONTRACT_VERSION,
        "capability_id": "[INVALID]",
        "capability_version": "[INVALID]",
        "environments": [],
        "features": [],
    }
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def serialize_provider_identity(identity: ProviderIdentity) -> str:
    value = identity.to_dict() if validate_provider_identity(identity) else {
        "contract_version": PROVIDER_CONTRACT_VERSION,
        "provider_id": "[INVALID]",
        "provider_version": "[INVALID]",
    }
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def serialize_provider_result(result: ProviderResult) -> str:
    value = result.to_dict() if isinstance(result, ProviderResult) else {
        "result_version": PROVIDER_CONTRACT_VERSION,
        "category": ProviderResultCategory.INVALID_REQUEST.value,
        "provider_id": "[INVALID]",
        "environment": "unknown",
        "content_digest": None,
    }
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def negotiate_capabilities(
    capability: ProviderCapability,
    environment: Environment,
    required_features: tuple[ProviderFeature, ...],
) -> CapabilityNegotiationResult:
    """Return deterministic fail-closed feature negotiation with no provider calls."""
    valid = (
        validate_provider_capability(capability)
        and isinstance(environment, Environment)
        and isinstance(required_features, tuple)
        and all(isinstance(feature, ProviderFeature) for feature in required_features)
        and len(set(required_features)) == len(required_features)
    )
    ordered = tuple(sorted(required_features, key=lambda item: item.value)) if valid else ()
    missing = tuple(feature.value for feature in ordered if feature not in capability.features) if valid else ()
    env_supported = valid and environment in capability.environments
    accepted = bool(valid and env_supported and not missing)
    if not valid:
        category = ProviderResultCategory.INVALID_REQUEST
    elif not env_supported:
        category = ProviderResultCategory.UNSUPPORTED_CAPABILITY
    elif missing:
        category = ProviderResultCategory.UNSUPPORTED_CAPABILITY
    else:
        category = ProviderResultCategory.SUCCESS
    return CapabilityNegotiationResult(
        PROVIDER_CONTRACT_VERSION, accepted,
        environment.value if isinstance(environment, Environment) else "unknown",
        tuple(feature.value for feature in ordered), missing, category,
    )


class ReadOnlyProvider(Protocol):
    """Inspection and validation surface; it exposes no mutation method."""

    @property
    def identity(self) -> ProviderIdentity: ...

    @property
    def capabilities(self) -> ProviderCapability: ...

    def inspect(self, environment: Environment, logical_object_id: str, expected_digest: str) -> ProviderResult:
        """Inspect provider-neutral object identity and integrity without writes."""
        ...

    def read_object_bytes(
        self, environment: Environment, logical_object_id: str
    ) -> ProviderObjectBytesResult:
        """Read exact stored bytes without changing provider state."""
        ...

    def validate_content(self, environment: Environment, logical_object_id: str, content_digest: str) -> ProviderResult:
        """Validate a future publication precondition without changing state."""
        ...


class MutatingProvider(Protocol):
    """Future object operation surface; no implementation is shipped."""

    @property
    def identity(self) -> ProviderIdentity: ...

    @property
    def capabilities(self) -> ProviderCapability: ...

    def write_object(self, environment: Environment, logical_object_id: str, content_digest: str) -> ProviderResult:
        """Interface only: write an object after an authorized plan gate."""
        ...

    def delete_object(self, environment: Environment, logical_object_id: str, expected_digest: str) -> ProviderResult:
        """Interface only: delete an object using an exact digest precondition."""
        ...

    def verify_object(self, environment: Environment, logical_object_id: str, expected_digest: str) -> ProviderResult:
        """Interface only: verify object integrity without disclosing provider details."""
        ...


class ProductionPromotionProvider(Protocol):
    """Narrow source-bound copy/read/CAS surface for STAGING to PRODUCTION promotion."""

    @property
    def identity(self) -> ProviderIdentity: ...

    @property
    def capabilities(self) -> ProviderCapability: ...

    def promote_object(
        self,
        source_environment: Environment,
        source_object_key: str,
        target_environment: Environment,
        target_object_key: str,
        expected_sha256: str,
    ) -> ProviderResult:
        """Copy one exact existing object between environments without deleting source."""
        ...

    def read_object_bytes(
        self, environment: Environment, object_key: str
    ) -> ProviderObjectBytesResult:
        """Read exact bytes in either environment for local verification."""
        ...

    def append_release_event(self, event: object) -> ProviderResult:
        """Durably append a hash-chained M11 release event."""
        ...

    def write_manifest_conditionally(
        self,
        environment: Environment,
        target_id: str,
        object_key: str,
        content_digest: str,
        content_bytes: bytes,
        *,
        expected_prior_sha256: str | None,
        promotion_pending_event_digest: str,
    ) -> ProviderResult:
        """Atomically activate a manifest under CAS after durable pending evidence."""
        ...


class ProviderAdapter(Protocol):
    """Deprecated combined placeholder retained for the CP001 boundary contract.

    New code must type read-only work as `ReadOnlyProvider` and future mutation
    as `MutatingProvider`; this compatibility surface is not used by planning.
    """

    def validate(self, environment: Environment) -> DryRunReport:
        """Describe provider-side validation without changing remote state."""
        ...

    def publish(self, report: DryRunReport) -> None:
        """Reserved interface; no implementation is available in this milestone."""
        ...

    def promote(self, report: DryRunReport) -> None:
        """Reserved interface; no implementation is available in this milestone."""
        ...

    def rollback(self, report: DryRunReport) -> None:
        """Reserved interface; no implementation is available in this milestone."""
        ...


__all__ = [
    "PROVIDER_CONTRACT_VERSION", "CapabilityNegotiationResult", "ProviderAdapter",
    "ProviderCapability", "ProviderFeature", "ProviderIdentity", "ProviderObjectBytesResult", "ProviderResult",
    "ProviderResultCategory", "ReadOnlyProvider", "MutatingProvider", "ProductionPromotionProvider",
    "negotiate_capabilities", "serialize_provider_capability", "serialize_provider_identity", "serialize_provider_result",
    "validate_provider_capability", "validate_provider_identity",
]
