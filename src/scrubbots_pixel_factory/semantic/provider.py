"""Provider-neutral SP01 interface and fail-closed capability validation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .contracts import (
    SemanticProvenanceError,
    SemanticCapabilities,
    SemanticGenerationRequest,
    SemanticImageCandidate,
    UnsupportedCapabilityError,
)


class SemanticGeneratorProvider(ABC):
    """Interface for future local/imported semantic providers.

    This contract contains no Magnific, ComfyUI, browser, HTTP or SDK import.
    Concrete adapters must return a typed candidate, including explicit
    failure/unavailable/unsupported states, rather than partial success.
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Stable provider identity, such as an imported external source."""

    @property
    @abstractmethod
    def provider_version(self) -> str:
        """Provider adapter contract version."""

    @property
    def provider_config_version(self) -> str:
        """Provider configuration contract version used for request binding."""
        return "1"

    @property
    @abstractmethod
    def capabilities(self) -> SemanticCapabilities:
        """Truthful versioned feature declaration."""

    def validate_request(self, request: SemanticGenerationRequest) -> None:
        if not isinstance(request, SemanticGenerationRequest):
            raise TypeError("semantic provider requires SemanticGenerationRequest")
        if request.provider_id != "UNSPECIFIED" and request.provider_id != self.provider_id:
            raise SemanticProvenanceError(f"request provider_id {request.provider_id!r} does not match executing provider {self.provider_id!r}")
        if request.provider_config_version != self.provider_config_version:
            raise SemanticProvenanceError("request provider_config_version does not match executing provider")
        unsupported = self.capabilities.unsupported_for(request)
        if unsupported:
            raise UnsupportedCapabilityError("provider does not support: " + ", ".join(unsupported))

    @abstractmethod
    def generate(self, request: SemanticGenerationRequest) -> SemanticImageCandidate:
        """Return a complete typed result or an explicit non-success result."""

    def generate_checked(self, request: SemanticGenerationRequest) -> SemanticImageCandidate:
        self.validate_request(request)
        result = self.generate(request)
        if not isinstance(result, SemanticImageCandidate):
            raise TypeError("semantic provider must return SemanticImageCandidate")
        expected_width, expected_height = request.resolved_dimensions()
        bindings = (
            ("request_digest", result.request_digest, request.digest()),
            ("provider_id", result.provider_id, self.provider_id),
            ("provider_version", result.provider_version, self.provider_version),
            ("workflow_version", result.workflow_version, request.provider_workflow_version),
            ("seed", result.seed, request.seed),
            ("requested_width", result.requested_width, expected_width),
            ("requested_height", result.requested_height, expected_height),
            ("reference_images", result.reference_images, request.reference_images),
            ("style_image", result.style_image, request.style_image),
            ("init_image", result.init_image, request.init_image),
            ("color_reference", result.color_reference, request.color_reference),
        )
        for label, actual, expected in bindings:
            if actual != expected:
                raise SemanticProvenanceError(f"result {label} is not bound to the checked request/provider")
        if request.provider_model is not None and result.model_id != request.provider_model:
            raise SemanticProvenanceError("result model_id is not bound to the requested provider model")
        return result

    def identity(self) -> dict[str, str]:
        return {"provider_id": self.provider_id, "provider_version": self.provider_version, "provider_config_version": self.provider_config_version}


__all__ = ["SemanticGeneratorProvider"]
