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

__all__ = [
    "CandidateStatus", "DETAIL_VALUES", "DIRECTION_VALUES", "ImageDescriptor", "ImageInputDescriptor", "ImageInputRole", "OUTLINE_VALUES", "OutputClass", "ProviderResult", "ProviderUnavailableError", "SEMANTIC_CANDIDATE_SCHEMA", "SEMANTIC_CANDIDATE_SCHEMA_VERSION", "SEMANTIC_CAPABILITIES_SCHEMA", "SEMANTIC_CAPABILITIES_SCHEMA_VERSION", "SEMANTIC_REQUEST_SCHEMA", "SEMANTIC_REQUEST_SCHEMA_VERSION", "SemanticCandidateError", "SemanticContractError", "SemanticGenerationRequest", "SemanticGeneratorProvider", "SemanticImageCandidate", "SemanticImageInputDescriptor", "SemanticNormalizationRequiredError", "SemanticOutputClass", "SemanticProviderCapabilities", "SemanticProviderError", "SemanticProvenanceError", "SemanticProviderResult", "SemanticRequestError", "SemanticResult", "SemanticCapabilities", "SHADING_VALUES", "UnsupportedCapabilityError", "VIEW_VALUES",
]
