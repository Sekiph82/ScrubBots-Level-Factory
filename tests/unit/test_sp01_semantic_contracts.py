import hashlib

import pytest

from scrubbots_pixel_factory import (
    CandidateStatus,
    ImageInputDescriptor,
    OutputClass,
    SemanticCapabilities,
    SemanticGenerationRequest,
    SemanticGeneratorProvider,
    SemanticImageCandidate,
    SemanticNormalizationRequiredError,
    SemanticRequestError,
    UnsupportedCapabilityError,
)


IMAGE_HASH = hashlib.sha256(b"owner-reference").hexdigest()


def level_request(**changes: object) -> SemanticGenerationRequest:
    values: dict[str, object] = {
        "output_class": "LEVEL_ART",
        "description": "a readable wizard in a cave",
        "difficulty": "EASY",
        "width": 20,
        "height": 21,
        "seed": "sp01-seed",
        "provider_id": "test-provider",
        "provider_model": "model-a",
    }
    values.update(changes)
    return SemanticGenerationRequest(**values)


def test_level_art_is_bound_to_existing_difficulty_dimensions() -> None:
    request = level_request()
    assert request.output_class is OutputClass.LEVEL_ART
    assert request.resolved_dimensions() == (20, 21)
    assert request.canonical_dict()["difficulty"] == "EASY"

    with pytest.raises(SemanticRequestError):
        level_request(width=16, height=16)
    with pytest.raises(SemanticRequestError):
        level_request(difficulty=None)


def test_asset_art_supports_explicit_sizes_without_fake_difficulty() -> None:
    request = SemanticGenerationRequest(output_class="ASSET_ART", description="a tiny robot", width=16, height=16)
    rectangular = SemanticGenerationRequest(output_class=OutputClass.ASSET_ART, description="a banner object", width=24, height=32)
    assert request.output_class is OutputClass.ASSET_ART
    assert request.resolved_dimensions() == (16, 16)
    assert rectangular.resolved_dimensions() == (24, 32)
    assert request.difficulty is None


@pytest.mark.parametrize(
    "field,value",
    [("description", ""), ("outline", "bad-outline"), ("shading", "bad-shading"), ("detail", "bad-detail"), ("view", "bad-view"), ("direction", "bad-direction"), ("coverage_percentage", 101), ("style_strength", 2.0)],
)
def test_invalid_semantic_controls_fail_closed(field: str, value: object) -> None:
    changes = {field: value}
    if field == "style_strength":
        changes["style_image"] = ImageInputDescriptor("STYLE", IMAGE_HASH)
    with pytest.raises(SemanticRequestError):
        level_request(**changes)


def test_request_identity_is_canonical_and_path_independent() -> None:
    reference_a = ImageInputDescriptor("REFERENCE", IMAGE_HASH, media_type="image/png", width=16, height=16, local_path="C:/one/reference.png")
    reference_b = ImageInputDescriptor("REFERENCE", IMAGE_HASH, media_type="image/png", width=16, height=16, local_path="D:/other/reference.png")
    first = level_request(reference_images=(reference_a,), audit_metadata={"timestamp": "2026-01-01", "run": 1})
    second = level_request(reference_images=(reference_b,), audit_metadata={"run": 2, "timestamp": "2030-01-01"})
    assert first.digest() == second.digest()
    assert first.canonical_bytes() == second.canonical_bytes()
    changed = level_request(reference_images=(ImageInputDescriptor("REFERENCE", "0" * 64),))
    assert changed.digest() != first.digest()
    assert level_request(provider_model="model-b").digest() != first.digest()


class TextOnlyProvider(SemanticGeneratorProvider):
    @property
    def provider_id(self) -> str:
        return "text-only-test"

    @property
    def provider_version(self) -> str:
        return "test-v1"

    @property
    def capabilities(self) -> SemanticCapabilities:
        return SemanticCapabilities(text_to_image=True)

    def generate(self, request: SemanticGenerationRequest) -> SemanticImageCandidate:
        return SemanticImageCandidate.failure(request, candidate_id="failed-1", provider_id=self.provider_id, provider_version=self.provider_version, workflow_version="workflow-v1", reason="provider unavailable", status=CandidateStatus.UNAVAILABLE)


def test_provider_capabilities_and_typed_failure_boundary() -> None:
    provider = TextOnlyProvider()
    provider.validate_request(level_request())
    with pytest.raises(UnsupportedCapabilityError):
        provider.validate_request(level_request(negative_description="no blur"))
    result = provider.generate_checked(level_request())
    assert result.status is CandidateStatus.UNAVAILABLE
    assert result.is_success is False
    with pytest.raises(SemanticNormalizationRequiredError):
        result.as_m08_artwork()


def test_successful_semantic_candidate_preserves_raw_provenance_without_m08_masquerade() -> None:
    request = level_request(reference_images=(ImageInputDescriptor("REFERENCE", IMAGE_HASH),))
    candidate = SemanticImageCandidate.success(request, candidate_id="candidate-1", provider_id="test-provider", provider_version="v1", workflow_version="workflow-v1", model_id="model-a", image_bytes=b"raw-image", returned_width=20, returned_height=21, generation_metadata={"audit_timestamp": "not-an-identity-field"})
    assert candidate.is_success
    assert candidate.raw_image_sha256 == hashlib.sha256(b"raw-image").hexdigest()
    assert candidate.reference_images == request.reference_images
    assert candidate.digest() == SemanticImageCandidate.success(request, candidate_id="candidate-1", provider_id="test-provider", provider_version="v1", workflow_version="workflow-v1", model_id="model-a", image_bytes=b"raw-image", returned_width=20, returned_height=21, generation_metadata={"audit_timestamp": "different"}).digest()
    assert "logical_grid" not in candidate.canonical_dict()
    with pytest.raises(SemanticNormalizationRequiredError):
        candidate.as_m08_artwork()
