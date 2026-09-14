from __future__ import annotations

from dataclasses import replace
import hashlib

import pytest

from scrubbots_pixel_factory import (
    DeterministicRNG,
    Difficulty,
    ImageInputDescriptor,
    ImageInputRole,
    OutputClass,
    SemanticGenerationPlanError,
    SemanticGenerationRequest,
    SemanticGenerationVariant,
    SemanticInputBinding,
    SemanticReferenceStylePlan,
    plan_reference_style_generation,
)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _request(count: int = 3, seed: int | str = "sp07-seed") -> SemanticGenerationRequest:
    refs = (
        ImageInputDescriptor(ImageInputRole.REFERENCE, _sha("reference-b"), media_type="image/png", width=24, height=24, source_label="reference-b"),
        ImageInputDescriptor(ImageInputRole.REFERENCE, _sha("reference-a"), media_type="image/png", width=24, height=24, source_label="reference-a"),
    )
    style = ImageInputDescriptor(ImageInputRole.STYLE, _sha("style"), media_type="image/png", width=24, height=24, local_path="C:\\private\\style.png")
    init = ImageInputDescriptor(ImageInputRole.INIT, _sha("init"), media_type="image/png", width=24, height=24)
    color = ImageInputDescriptor(ImageInputRole.COLOR_REFERENCE, _sha("palette"), media_type="image/png", width=16, height=16)
    return SemanticGenerationRequest(
        OutputClass.ASSET_ART,
        "a semantic asset",
        semantic_category="creature",
        width=24,
        height=24,
        seed=seed,
        negative_description="photorealistic",
        reference_images=refs,
        style_image=style,
        style_strength=0.35,
        init_image=init,
        init_strength=0.65,
        color_reference=color,
        no_background=True,
        outline="SINGLE",
        shading="BASIC",
        detail="HIGH",
        view="THREE_QUARTER",
        direction="NE",
        isometric=False,
        coverage_percentage=72,
        provider_id="MAGNIFIC",
        provider_workflow_version="magnific-workflow-v1",
        provider_model="model-snapshot",
        provider_config_version="cfg-v1",
        desired_candidate_count=count,
    )


def test_same_canonical_request_has_identical_plan_bytes_and_digest():
    request = _request()
    first = plan_reference_style_generation(request)
    second = plan_reference_style_generation(request)
    assert first.request_digest == request.digest()
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.digest() == second.digest()
    assert first.verify_against_request(request) is True


def test_input_roles_order_and_exact_content_identities_are_preserved():
    plan = plan_reference_style_generation(_request())
    assert tuple(binding.role for binding in plan.input_bindings) == (
        ImageInputRole.REFERENCE,
        ImageInputRole.REFERENCE,
        ImageInputRole.STYLE,
        ImageInputRole.INIT,
        ImageInputRole.COLOR_REFERENCE,
    )
    assert tuple(binding.ordinal for binding in plan.input_bindings) == tuple(range(5))
    assert tuple(binding.content_sha256 for binding in plan.input_bindings) == (
        _sha("reference-b"), _sha("reference-a"), _sha("style"), _sha("init"), _sha("palette")
    )
    assert plan.style_strength == 0.35
    assert plan.init_strength == 0.65
    assert plan.input_bindings[2].canonical_identity["source_label"] is None


def test_paths_are_not_identity_but_content_changes_are_identity_changes():
    first_request = _request()
    first = plan_reference_style_generation(first_request)
    changed_path = ImageInputDescriptor(ImageInputRole.STYLE, _sha("style"), media_type="image/png", width=24, height=24, local_path="D:\\other\\style.png")
    same_identity_request = replace(first_request, style_image=changed_path)
    assert same_identity_request.digest() == first_request.digest()
    assert plan_reference_style_generation(same_identity_request).digest() == first.digest()
    altered_style = ImageInputDescriptor(ImageInputRole.STYLE, _sha("different-style"), media_type="image/png", width=24, height=24)
    changed_style_request = replace(same_identity_request, style_image=altered_style)
    assert changed_style_request.digest() != first_request.digest()
    assert plan_reference_style_generation(changed_style_request).digest() != first.digest()


def test_strengths_and_request_seed_change_plan_and_variant_identity():
    base = _request()
    changed_strength = replace(base, style_strength=0.36)
    changed_seed = _request(seed="different-seed")
    assert plan_reference_style_generation(changed_strength).digest() != plan_reference_style_generation(base).digest()
    assert plan_reference_style_generation(changed_seed).digest() != plan_reference_style_generation(base).digest()
    assert tuple(item.seed for item in plan_reference_style_generation(changed_seed).variants) != tuple(item.seed for item in plan_reference_style_generation(base).variants)


def test_variant_count_order_ids_and_project_rng_seed_derivation_are_deterministic():
    request = _request(4)
    plan = plan_reference_style_generation(request)
    assert len(plan.variants) == 4
    assert tuple(item.ordinal for item in plan.variants) == (0, 1, 2, 3)
    assert len({item.candidate_id for item in plan.variants}) == 4
    rng = DeterministicRNG(request.seed).child("semantic-generation")
    assert tuple(item.seed for item in plan.variants) == tuple(rng.retry_seed(index) for index in range(4))
    assert all(item.request_digest == request.digest() for item in plan.variants)
    assert plan_reference_style_generation(_request(5)).digest() != plan.digest()


def test_provider_selection_and_execution_intent_are_bound_without_fallback():
    request = _request()
    plan = plan_reference_style_generation(request)
    assert (plan.provider_id, plan.provider_model, plan.workflow_version, plan.config_version) == (
        "MAGNIFIC", "model-snapshot", "magnific-workflow-v1", "cfg-v1"
    )
    assert plan.output_class is OutputClass.ASSET_ART
    assert (plan.resolved_width, plan.resolved_height) == (24, 24)
    assert plan.canonical_dict()["provider"]["id"] == "MAGNIFIC"


def test_level_and_asset_requests_remain_separate_and_legal():
    asset_plan = plan_reference_style_generation(_request(1))
    level_request = SemanticGenerationRequest(OutputClass.LEVEL_ART, "a level subject", difficulty=Difficulty.EASY, width=20, height=20, seed="level-seed", desired_candidate_count=1)
    level_plan = plan_reference_style_generation(level_request)
    assert asset_plan.output_class is OutputClass.ASSET_ART
    assert level_plan.output_class is OutputClass.LEVEL_ART
    assert (level_plan.resolved_width, level_plan.resolved_height) == (20, 20)
    assert level_plan.input_bindings == ()


def test_duplicate_reference_content_role_is_explicitly_rejected():
    descriptor = ImageInputDescriptor(ImageInputRole.REFERENCE, _sha("duplicate"))
    same_content = ImageInputDescriptor(ImageInputRole.REFERENCE, _sha("duplicate"), source_label="different-label")
    request = SemanticGenerationRequest(OutputClass.ASSET_ART, "duplicate reference test", width=24, height=24, reference_images=(descriptor, same_content))
    with pytest.raises(SemanticGenerationPlanError) as error:
        plan_reference_style_generation(request)
    assert error.value.code == "DUPLICATE_INPUT"


def test_untrusted_request_and_public_plan_construction_cannot_mint_derived_facts():
    with pytest.raises(SemanticGenerationPlanError) as error:
        plan_reference_style_generation({"description": "not a request"})  # type: ignore[arg-type]
    assert error.value.code == "UNTRUSTED_REQUEST"
    plan = plan_reference_style_generation(_request())
    with pytest.raises(SemanticGenerationPlanError) as error:
        replace(plan, request_digest="0" * 64)
    assert error.value.code == "UNSEALED_PLAN"
    with pytest.raises(SemanticGenerationPlanError):
        replace(plan.variants[0], seed="0" * 64)
    with pytest.raises(SemanticGenerationPlanError):
        replace(plan.input_bindings[0], content_sha256=_sha("forged"))
