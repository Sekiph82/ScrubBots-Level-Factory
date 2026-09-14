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
    CELL_MAJORITY_POLICY_VERSION,
    DIFFICULTY_BUDGET_POLICY_VERSION,
    LEVEL_ART_REPORT_SCHEMA,
    LEVEL_ART_REPORT_VERSION,
    LEVEL_ART_SCHEMA,
    LEVEL_ART_SCHEMA_VERSION,
    PALETTE_SNAP_POLICY_VERSION,
    PRODUCTION_COLOR_ENVELOPE_POLICY_VERSION,
    LevelArtStatus,
    SemanticDecodeError,
    SemanticLevelArtArtifact,
    SemanticLevelArtCompiler,
    SemanticLevelArtError,
    SemanticLevelArtReport,
    SemanticLevelArtRequest,
    SemanticNormalizedArtifact,
    SemanticNormalizationError,
    SemanticNormalizationReport,
    SemanticNormalizationRequest,
    SemanticNormalizer,
    SemanticRawArtifact,
    SemanticSourceProvenance,
    cell_majority_rgba_grid,
    compile_level_art,
    compile_semantic_level_art,
    enforce_difficulty_color_budget,
    normalize_semantic_artifact,
    palette_snap_grid,
)
from .qualification import *
from .quality import (
    SEMANTIC_QUALITY_ASSESSMENT_SCHEMA,
    SEMANTIC_QUALITY_ASSESSMENT_SCHEMA_VERSION,
    SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION,
    SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA,
    SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA_VERSION,
    SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA,
    SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA_VERSION,
    RecognizabilityDisposition,
    SemanticQualityAssessment,
    SemanticQualityDiagnostics,
    SemanticQualityError,
    SemanticRecognizabilityReview,
    assess_semantic_quality,
)


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
    "MagnificJobSpec", "MagnificModelCapabilitySnapshot", "MagnificProvider", "MagnificReferenceBinding", "MagnificResultManifest", "get_magnific_model_snapshot", "PixelLabExecutionBinding", "PixelLabJobSpec", "PixelLabProvider", "PixelLabResultManifest", "PixelLabRuntimeConfig", "CELL_MAJORITY_POLICY_VERSION", "DIFFICULTY_BUDGET_POLICY_VERSION", "LEVEL_ART_REPORT_SCHEMA", "LEVEL_ART_REPORT_VERSION", "LEVEL_ART_SCHEMA", "LEVEL_ART_SCHEMA_VERSION", "PALETTE_SNAP_POLICY_VERSION", "PRODUCTION_COLOR_ENVELOPE_POLICY_VERSION", "LevelArtStatus", "SemanticDecodeError", "SemanticLevelArtArtifact", "SemanticLevelArtCompiler", "SemanticLevelArtError", "SemanticLevelArtReport", "SemanticLevelArtRequest", "SemanticNormalizedArtifact", "SemanticNormalizationError", "SemanticNormalizationReport", "SemanticNormalizationRequest", "SemanticNormalizer", "SemanticRawArtifact", "SemanticSourceProvenance", "cell_majority_rgba_grid", "compile_level_art", "compile_semantic_level_art", "enforce_difficulty_color_budget", "normalize_semantic_artifact", "palette_snap_grid",
    *(__import__("scrubbots_pixel_factory.semantic.qualification", fromlist=["__all__"]).__all__),
    "SEMANTIC_QUALITY_ASSESSMENT_SCHEMA", "SEMANTIC_QUALITY_ASSESSMENT_SCHEMA_VERSION",
    "SEMANTIC_QUALITY_DIAGNOSTICS_POLICY_VERSION", "SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA",
    "SEMANTIC_QUALITY_DIAGNOSTICS_SCHEMA_VERSION", "SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA",
    "SEMANTIC_RECOGNIZABILITY_REVIEW_SCHEMA_VERSION", "RecognizabilityDisposition",
    "SemanticQualityAssessment", "SemanticQualityDiagnostics", "SemanticQualityError",
    "SemanticRecognizabilityReview", "assess_semantic_quality",
]
