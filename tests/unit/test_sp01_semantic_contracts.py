import hashlib
from dataclasses import replace

import pytest

from scrubbots_pixel_factory import (
    CandidateStatus,
    ImageInputDescriptor,
    OutputClass,
    SemanticCapabilities,
    SemanticGenerationRequest,
    SemanticGeneratorProvider,
    SemanticImageCandidate,
    SemanticCandidateError,
    SemanticNormalizationRequiredError,
    SemanticProvenanceError,
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


def test_request_identity_changes_for_every_material_generation_field() -> None:
    base = level_request()
    variants = (
        level_request(description="a different subject").digest(),
        level_request(seed="different-seed").digest(),
        level_request(provider_id="different-provider").digest(),
        level_request(provider_workflow_version="workflow-v2").digest(),
        level_request(provider_model="model-b").digest(),
        level_request(provider_config_version="2").digest(),
        level_request(reference_images=(ImageInputDescriptor("REFERENCE", "0" * 64),)).digest(),
    )
    assert all(digest != base.digest() for digest in variants)
    asset_a = SemanticGenerationRequest(output_class="ASSET_ART", description="asset", width=16, height=16, seed=7)
    asset_b = SemanticGenerationRequest(output_class="ASSET_ART", description="asset", width=24, height=16, seed=7)
    assert asset_a.digest() != asset_b.digest()


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
        return SemanticImageCandidate.failure(request, candidate_id="failed-1", provider_id=self.provider_id, provider_version=self.provider_version, workflow_version=request.provider_workflow_version, reason="provider unavailable", status=CandidateStatus.UNAVAILABLE)


def test_provider_capabilities_and_typed_failure_boundary() -> None:
    provider = TextOnlyProvider()
    provider.validate_request(level_request(provider_id="UNSPECIFIED", provider_model=None))
    with pytest.raises(UnsupportedCapabilityError):
        provider.validate_request(level_request(provider_id="UNSPECIFIED", provider_model=None, negative_description="no blur"))
    result = provider.generate_checked(level_request(provider_id="UNSPECIFIED", provider_model=None))
    assert result.status is CandidateStatus.UNAVAILABLE
    assert result.is_success is False
    with pytest.raises(SemanticNormalizationRequiredError):
        result.as_m08_artwork()


def test_concrete_request_provider_mismatch_is_rejected_but_neutral_is_explicit() -> None:
    provider = TextOnlyProvider()
    with pytest.raises(SemanticProvenanceError):
        provider.generate_checked(level_request(provider_id="provider-A", provider_model=None))
    assert provider.generate_checked(level_request(provider_id="UNSPECIFIED", provider_model=None)).provider_id == provider.provider_id


class BindingProvider(SemanticGeneratorProvider):
    @property
    def provider_id(self) -> str:
        return "binding-provider"

    @property
    def provider_version(self) -> str:
        return "adapter-v1"

    @property
    def capabilities(self) -> SemanticCapabilities:
        return SemanticCapabilities(text_to_image=True, negative_prompt=True, transparent_background=True, reference_images=True, style_image=True, init_image=True, palette_color_reference=True, view_direction_controls=True, isometric=True)

    def __init__(self, mutate=None) -> None:
        self._mutate = mutate

    def generate(self, request: SemanticGenerationRequest) -> SemanticImageCandidate:
        result = SemanticImageCandidate.failure(request, candidate_id="bound-failure", provider_id=self.provider_id, provider_version=self.provider_version, workflow_version=request.provider_workflow_version, reason="provider unavailable", status=CandidateStatus.UNAVAILABLE)
        return self._mutate(result) if self._mutate is not None else result


def bound_request() -> SemanticGenerationRequest:
    return level_request(
        provider_id="binding-provider",
        reference_images=(ImageInputDescriptor("REFERENCE", IMAGE_HASH),),
        style_image=ImageInputDescriptor("STYLE", IMAGE_HASH),
        init_image=ImageInputDescriptor("INIT", "0" * 64),
        color_reference=ImageInputDescriptor("COLOR_REFERENCE", "1" * 64),
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("request_digest", "0" * 64),
        ("provider_id", "other-provider"),
        ("provider_version", "other-version"),
        ("workflow_version", "other-workflow"),
        ("model_id", "other-model"),
        ("seed", "other-seed"),
        ("requested_width", 21),
        ("reference_images", (ImageInputDescriptor("REFERENCE", "2" * 64),)),
        ("style_image", ImageInputDescriptor("STYLE", "2" * 64)),
        ("init_image", ImageInputDescriptor("INIT", "2" * 64)),
        ("color_reference", ImageInputDescriptor("COLOR_REFERENCE", "2" * 64)),
    ],
)
def test_generate_checked_rejects_each_corrupted_provenance_binding(field: str, value: object) -> None:
    request = bound_request()
    with pytest.raises(SemanticProvenanceError):
        BindingProvider(lambda result: replace(result, **{field: value})).generate_checked(request)


def test_generate_checked_rejects_coordinated_self_consistent_but_foreign_result() -> None:
    request = bound_request()
    foreign_request = level_request(provider_id="binding-provider", provider_model="model-a", seed="foreign-seed")
    foreign = SemanticImageCandidate.failure(foreign_request, candidate_id="foreign", provider_id="binding-provider", provider_version="adapter-v1", workflow_version=foreign_request.provider_workflow_version, reason="provider unavailable", status=CandidateStatus.UNAVAILABLE)
    with pytest.raises(SemanticProvenanceError):
        BindingProvider(lambda _: foreign).generate_checked(request)


@pytest.mark.parametrize(
    "slot,descriptor",
    [
        ("reference_images", (ImageInputDescriptor("STYLE", IMAGE_HASH),)),
        ("style_image", ImageInputDescriptor("REFERENCE", IMAGE_HASH)),
        ("init_image", ImageInputDescriptor("REFERENCE", IMAGE_HASH)),
        ("color_reference", ImageInputDescriptor("REFERENCE", IMAGE_HASH)),
    ],
)
def test_request_rejects_contradictory_image_slot_roles(slot: str, descriptor: object) -> None:
    with pytest.raises(SemanticRequestError):
        level_request(**{slot: descriptor})


@pytest.mark.parametrize(
    "slot,descriptor",
    [
        ("reference_images", ({"role": "STYLE", "content_sha256": IMAGE_HASH},)),
        ("style_image", {"role": "REFERENCE", "content_sha256": IMAGE_HASH}),
        ("init_image", {"role": "REFERENCE", "content_sha256": IMAGE_HASH}),
        ("color_reference", {"role": "REFERENCE", "content_sha256": IMAGE_HASH}),
    ],
)
def test_direct_candidate_rejects_contradictory_image_slot_roles(slot: str, descriptor: object) -> None:
    base = SemanticImageCandidate.failure(bound_request(), candidate_id="direct", provider_id="binding-provider", provider_version="adapter-v1", workflow_version="semantic-workflow-v1", reason="provider unavailable", status=CandidateStatus.UNAVAILABLE)
    with pytest.raises(SemanticCandidateError):
        replace(base, **{slot: descriptor})


def test_direct_candidate_converts_valid_mappings_and_rejects_malformed_fields() -> None:
    request = level_request(provider_id="binding-provider", provider_model=None)
    base = SemanticImageCandidate.failure(request, candidate_id="direct", provider_id="binding-provider", provider_version="adapter-v1", workflow_version=request.provider_workflow_version, reason="provider unavailable", status=CandidateStatus.UNAVAILABLE)
    converted = replace(base, reference_images=({"role": "REFERENCE", "content_sha256": IMAGE_HASH},))
    assert converted.reference_images[0].role.value == "REFERENCE"
    with pytest.raises(SemanticCandidateError):
        replace(base, status="not-a-status")
    with pytest.raises(SemanticCandidateError):
        replace(base, model_id=" ")


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
