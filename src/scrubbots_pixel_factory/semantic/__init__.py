"""Provider-neutral semantic generation boundary introduced by SP01."""

from .contracts import (
    CandidateStatus,
    DETAIL_VALUES,
    DIRECTION_VALUES,
    ImageDescriptor,
    ImageInputDescriptor,
    ImageInputRole,
    OUTLINE_VALUES,
    OutputClass,
    ProviderResult,
    ProviderUnavailableError,
    SEMANTIC_CANDIDATE_SCHEMA,
    SEMANTIC_CANDIDATE_SCHEMA_VERSION,
    SEMANTIC_CAPABILITIES_SCHEMA,
    SEMANTIC_CAPABILITIES_SCHEMA_VERSION,
    SEMANTIC_REQUEST_SCHEMA,
    SEMANTIC_REQUEST_SCHEMA_VERSION,
    SemanticCandidateError,
    SemanticContractError,
    SemanticGenerationRequest,
    SemanticImageCandidate,
    SemanticImageInputDescriptor,
    SemanticNormalizationRequiredError,
    SemanticProviderError,
    SemanticProvenanceError,
    SemanticProviderResult,
    SemanticRequestError,
    SemanticOutputClass,
    SemanticProviderCapabilities,
    SemanticResult,
    SemanticCapabilities,
    SHADING_VALUES,
    UnsupportedCapabilityError,
    VIEW_VALUES,
)
from .provider import SemanticGeneratorProvider


def __getattr__(name: str) -> object:
    """Lazily expose SP02 bridges without importing optional SDKs."""
    if name in {"MagnificJobSpec", "MagnificProvider", "MagnificReferenceBinding", "MagnificResultManifest"}:
        from .providers.magnific import MagnificJobSpec, MagnificProvider, MagnificReferenceBinding, MagnificResultManifest

        return {"MagnificJobSpec": MagnificJobSpec, "MagnificProvider": MagnificProvider, "MagnificReferenceBinding": MagnificReferenceBinding, "MagnificResultManifest": MagnificResultManifest}[name]
    if name in {"PixelLabExecutionBinding", "PixelLabJobSpec", "PixelLabProvider", "PixelLabResultManifest", "PixelLabRuntimeConfig"}:
        from .providers.pixellab import PixelLabExecutionBinding, PixelLabJobSpec, PixelLabProvider, PixelLabResultManifest, PixelLabRuntimeConfig

        return {"PixelLabExecutionBinding": PixelLabExecutionBinding, "PixelLabJobSpec": PixelLabJobSpec, "PixelLabProvider": PixelLabProvider, "PixelLabResultManifest": PixelLabResultManifest, "PixelLabRuntimeConfig": PixelLabRuntimeConfig}[name]
    raise AttributeError(name)

__all__ = [
    "CandidateStatus", "DETAIL_VALUES", "DIRECTION_VALUES", "ImageDescriptor", "ImageInputDescriptor", "ImageInputRole", "OUTLINE_VALUES", "OutputClass", "ProviderResult", "ProviderUnavailableError", "SEMANTIC_CANDIDATE_SCHEMA", "SEMANTIC_CANDIDATE_SCHEMA_VERSION", "SEMANTIC_CAPABILITIES_SCHEMA", "SEMANTIC_CAPABILITIES_SCHEMA_VERSION", "SEMANTIC_REQUEST_SCHEMA", "SEMANTIC_REQUEST_SCHEMA_VERSION", "SemanticCandidateError", "SemanticContractError", "SemanticGenerationRequest", "SemanticGeneratorProvider", "SemanticImageCandidate", "SemanticImageInputDescriptor", "SemanticNormalizationRequiredError", "SemanticOutputClass", "SemanticProviderCapabilities", "SemanticProviderError", "SemanticProvenanceError", "SemanticProviderResult", "SemanticRequestError", "SemanticResult", "SemanticCapabilities", "SHADING_VALUES", "UnsupportedCapabilityError", "VIEW_VALUES",
    "MagnificJobSpec", "MagnificProvider", "MagnificReferenceBinding", "MagnificResultManifest", "PixelLabExecutionBinding", "PixelLabJobSpec", "PixelLabProvider", "PixelLabResultManifest", "PixelLabRuntimeConfig",
]
