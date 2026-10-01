from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import hashlib
from pathlib import Path

import pytest

from scrubbots_pixel_factory import (
    ImageInputDescriptor,
    ImageInputRole,
    OutputClass,
    SEMANTIC_ART_HELPER_MAX_CANDIDATE_COUNT,
    SemanticArtHelperError,
    SemanticArtHelperStatus,
    SemanticGenerationPlanError,
    SemanticGenerationRequest,
    build_semantic_art_helper,
    plan_reference_style_generation,
    restore_semantic_art_helper,
)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _request(count: int = 3, seed: int | str = "lf09-003-seed") -> SemanticGenerationRequest:
    return SemanticGenerationRequest(
        OutputClass.ASSET_ART,
        "a semantic creature asset",
        semantic_category="creature",
        width=24,
        height=24,
        seed=seed,
        negative_description="photorealistic",
        reference_images=(
            ImageInputDescriptor(ImageInputRole.REFERENCE, _sha("reference-a"), media_type="image/png", width=24, height=24),
            ImageInputDescriptor(ImageInputRole.REFERENCE, _sha("reference-b"), media_type="image/png", width=24, height=24),
        ),
        style_image=ImageInputDescriptor(ImageInputRole.STYLE, _sha("style"), media_type="image/png", width=24, height=24, local_path="C:\\private\\style.png"),
        style_strength=0.35,
        init_image=ImageInputDescriptor(ImageInputRole.INIT, _sha("init"), media_type="image/png", width=24, height=24),
        init_strength=0.65,
        color_reference=ImageInputDescriptor(ImageInputRole.COLOR_REFERENCE, _sha("palette"), media_type="image/png", width=16, height=16),
        no_background=True,
        outline="SINGLE",
        shading="BASIC",
        detail="HIGH",
        view="THREE_QUARTER",
        direction="NE",
        coverage_percentage=72,
        provider_id="MAGNIFIC",
        provider_workflow_version="magnific-workflow-v1",
        provider_model="model-snapshot",
        provider_config_version="cfg-v1",
        desired_candidate_count=count,
    )


def test_helper_binds_canonical_request_plan_and_all_typed_input_roles() -> None:
    request = _request()
    plan = plan_reference_style_generation(request)
    result = build_semantic_art_helper(request, plan)

    assert result.status is SemanticArtHelperStatus.AVAILABLE
    assert result.request_digest == request.digest()
    assert result.plan_digest == plan.digest()
    assert result.seed_identity.seed_type == "string"
    assert result.seed_identity.value == "lf09-003-seed"
    assert tuple(binding.role for binding in result.input_bindings) == (
        ImageInputRole.REFERENCE,
        ImageInputRole.REFERENCE,
        ImageInputRole.STYLE,
        ImageInputRole.INIT,
        ImageInputRole.COLOR_REFERENCE,
    )
    assert tuple(binding.content_sha256 for binding in result.input_bindings) == (
        _sha("reference-a"),
        _sha("reference-b"),
        _sha("style"),
        _sha("init"),
        _sha("palette"),
    )
    assert result.canonical_dict()["boundary"] == {
        "output_kind": "SEMANTIC_HELPER_INTENT",
        "recognizability": "NOT_EVALUATED",
        "owner_acceptance": "NOT_EVALUATED",
        "promotion": "NOT_ELIGIBLE",
    }


def test_equivalent_canonical_requests_replay_byte_identical_helpers_and_ordered_seeds() -> None:
    first_request = _request(4, seed=42)
    second_request = replace(first_request, style_image=replace(first_request.style_image, local_path="D:\\other\\style.png"))
    first = build_semantic_art_helper(first_request)
    second = build_semantic_art_helper(second_request)
    plan = plan_reference_style_generation(first_request)

    assert first_request.digest() == second_request.digest()
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.digest() == second.digest()
    assert first.seed_identity.seed_type == "int"
    assert tuple(intent.ordinal for intent in first.intents) == (0, 1, 2, 3)
    assert tuple(intent.candidate_id for intent in first.intents) == tuple(variant.candidate_id for variant in plan.variants)
    assert tuple(intent.variant_seed for intent in first.intents) == tuple(variant.seed for variant in plan.variants)


def test_reference_duplicate_is_rejected_but_cross_role_same_content_remains_explicit() -> None:
    descriptor = ImageInputDescriptor(ImageInputRole.REFERENCE, _sha("duplicate"))
    duplicate = replace(descriptor, source_label="different-label")
    with pytest.raises(SemanticGenerationPlanError, match="DUPLICATE_INPUT"):
        build_semantic_art_helper(
            SemanticGenerationRequest(OutputClass.ASSET_ART, "duplicate", width=24, height=24, reference_images=(descriptor, duplicate))
        )

    request = replace(_request(1), init_image=ImageInputDescriptor(ImageInputRole.INIT, _sha("style"), width=24, height=24))
    result = build_semantic_art_helper(request)
    assert tuple((binding.role.value, binding.content_sha256) for binding in result.input_bindings)[2:4] == (
        ("STYLE", _sha("style")),
        ("INIT", _sha("style")),
    )


def test_tampered_malformed_and_stale_helpers_fail_closed_on_restore() -> None:
    request = _request()
    plan = plan_reference_style_generation(request)
    result = build_semantic_art_helper(request, plan)

    tampered = deepcopy(result.canonical_dict())
    tampered["intents"][0]["recipe"]["coverage_percentage"] = 1.0
    with pytest.raises(SemanticArtHelperError) as error:
        restore_semantic_art_helper(tampered, request=request, plan=plan)
    assert error.value.code == "TAMPERED_RESULT"

    malformed = deepcopy(result.canonical_dict())
    malformed["boundary"]["promotion"] = "ELIGIBLE"
    with pytest.raises(SemanticArtHelperError) as error:
        restore_semantic_art_helper(malformed, request=request, plan=plan)
    assert error.value.code == "TAMPERED_RESULT"

    changed_request = replace(request, semantic_category="different-category")
    with pytest.raises(SemanticArtHelperError) as error:
        restore_semantic_art_helper(result.canonical_dict(), request=changed_request, plan=plan)
    assert error.value.code == "STALE_PLAN"

    with pytest.raises(SemanticArtHelperError) as error:
        replace(result, request_digest="0" * 64)
    assert error.value.code == "UNSEALED_RESULT"


def test_candidate_bound_returns_explicit_unavailable_without_intents() -> None:
    request = _request(SEMANTIC_ART_HELPER_MAX_CANDIDATE_COUNT + 1)
    plan = plan_reference_style_generation(request)
    result = build_semantic_art_helper(request, plan)

    assert result.status is SemanticArtHelperStatus.UNAVAILABLE
    assert result.disposition.value == "UNAVAILABLE_CAPABILITY"
    assert result.intents == ()
    assert "exceeds helper bound" in (result.reason or "")
    assert restore_semantic_art_helper(result.canonical_dict(), request=request, plan=plan).canonical_bytes() == result.canonical_bytes()


def test_helper_is_offline_and_not_a_production_or_recognizability_path() -> None:
    source = Path(__file__).parents[2] / "src" / "scrubbots_pixel_factory" / "semantic" / "generation" / "helper.py"
    text = source.read_text(encoding="utf-8").lower()
    assert not any(marker in text for marker in ("urllib", "requests", "httpx", "aiohttp", "magnific", "pixellab", "api_key", "credential"))
    result = build_semantic_art_helper(_request(1))
    assert result.output_kind == "SEMANTIC_HELPER_INTENT"
    assert result.promotion_disposition == "NOT_ELIGIBLE"
    assert result.recognizability_disposition == "NOT_EVALUATED"
    assert not hasattr(result, "as_m08_artwork")
