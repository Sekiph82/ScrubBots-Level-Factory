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
    SEMANTIC_RAW_RASTER_MAX_DIMENSION,
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

from .normalization import (
    SemanticDecodeError,
    SemanticNormalizedArtifact,
    SemanticNormalizationError,
    SemanticNormalizationReport,
    SemanticNormalizationRequest,
    SemanticNormalizer,
    SemanticRawArtifact,
    SemanticSourceProvenance,
    normalize_semantic_artifact,
)
from .qualification import *


def __getattr__(name: str) -> object:
    """Lazily expose SP02 bridges without importing optional SDKs."""
    if name in {"MagnificJobSpec", "MagnificModelCapabilitySnapshot", "MagnificProvider", "MagnificReferenceBinding", "MagnificResultManifest", "get_magnific_model_snapshot"}:
        from .providers.magnific import MagnificJobSpec, MagnificModelCapabilitySnapshot, MagnificProvider, MagnificReferenceBinding, MagnificResultManifest, get_magnific_model_snapshot

        return {"MagnificJobSpec": MagnificJobSpec, "MagnificModelCapabilitySnapshot": MagnificModelCapabilitySnapshot, "MagnificProvider": MagnificProvider, "MagnificReferenceBinding": MagnificReferenceBinding, "MagnificResultManifest": MagnificResultManifest, "get_magnific_model_snapshot": get_magnific_model_snapshot}[name]
    if name in {"PixelLabExecutionBinding", "PixelLabJobSpec", "PixelLabProvider", "PixelLabResultManifest", "PixelLabRuntimeConfig"}:
        from .providers.pixellab import PixelLabExecutionBinding, PixelLabJobSpec, PixelLabProvider, PixelLabResultManifest, PixelLabRuntimeConfig

        return {"PixelLabExecutionBinding": PixelLabExecutionBinding, "PixelLabJobSpec": PixelLabJobSpec, "PixelLabProvider": PixelLabProvider, "PixelLabResultManifest": PixelLabResultManifest, "PixelLabRuntimeConfig": PixelLabRuntimeConfig}[name]
    raise AttributeError(name)

__all__ = [
    "CandidateStatus", "DETAIL_VALUES", "DIRECTION_VALUES", "ImageDescriptor", "ImageInputDescriptor", "ImageInputRole", "OUTLINE_VALUES", "OutputClass", "ProviderResult", "ProviderUnavailableError", "SEMANTIC_CANDIDATE_SCHEMA", "SEMANTIC_CANDIDATE_SCHEMA_VERSION", "SEMANTIC_CAPABILITIES_SCHEMA", "SEMANTIC_CAPABILITIES_SCHEMA_VERSION", "SEMANTIC_RAW_RASTER_MAX_DIMENSION", "SEMANTIC_REQUEST_SCHEMA", "SEMANTIC_REQUEST_SCHEMA_VERSION", "SemanticCandidateError", "SemanticContractError", "SemanticGenerationRequest", "SemanticGeneratorProvider", "SemanticImageCandidate", "SemanticImageInputDescriptor", "SemanticNormalizationRequiredError", "SemanticOutputClass", "SemanticProviderCapabilities", "SemanticProviderError", "SemanticProvenanceError", "SemanticProviderResult", "SemanticRequestError", "SemanticResult", "SemanticCapabilities", "SHADING_VALUES", "UnsupportedCapabilityError", "VIEW_VALUES",
    "MagnificJobSpec", "MagnificModelCapabilitySnapshot", "MagnificProvider", "MagnificReferenceBinding", "MagnificResultManifest", "get_magnific_model_snapshot", "PixelLabExecutionBinding", "PixelLabJobSpec", "PixelLabProvider", "PixelLabResultManifest", "PixelLabRuntimeConfig", "SemanticDecodeError", "SemanticNormalizedArtifact", "SemanticNormalizationError", "SemanticNormalizationReport", "SemanticNormalizationRequest", "SemanticNormalizer", "SemanticRawArtifact", "SemanticSourceProvenance", "normalize_semantic_artifact",
    *(__import__("scrubbots_pixel_factory.semantic.qualification", fromlist=["__all__"]).__all__),
]
