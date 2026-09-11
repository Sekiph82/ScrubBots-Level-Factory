"""Provider-neutral SP01 interface and fail-closed capability validation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .contracts import (
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
    @abstractmethod
    def capabilities(self) -> SemanticCapabilities:
        """Truthful versioned feature declaration."""

    def validate_request(self, request: SemanticGenerationRequest) -> None:
        if not isinstance(request, SemanticGenerationRequest):
            raise TypeError("semantic provider requires SemanticGenerationRequest")
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
        return result

    def identity(self) -> dict[str, str]:
        return {"provider_id": self.provider_id, "provider_version": self.provider_version}


__all__ = ["SemanticGeneratorProvider"]
