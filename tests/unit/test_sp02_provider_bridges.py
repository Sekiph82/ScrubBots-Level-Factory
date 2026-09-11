"""Offline SP02 provider bridge contract tests; no credentials or network."""

from __future__ import annotations

import hashlib
import json
import os
from types import SimpleNamespace
from pathlib import Path

import pytest

from scrubbots_pixel_factory.semantic import (
    CandidateStatus,
    ImageInputDescriptor,
    ImageInputRole,
    OutputClass,
    SemanticGenerationRequest,
    SemanticProviderError,
)
from scrubbots_pixel_factory.semantic.providers import (
    available_provider_ids,
    create_provider,
    get_provider_descriptor,
)
from scrubbots_pixel_factory.semantic.providers.magnific import (
    MagnificJobSpec,
    MagnificProvider,
    MagnificReferenceBinding,
    MagnificResultManifest,
)
from scrubbots_pixel_factory.semantic.providers.pixellab import (
    PixelLabExecutionBinding,
    PixelLabJobSpec,
    PixelLabProvider,
    PixelLabRuntimeConfig,
)


def asset_request(**changes: object) -> SemanticGenerationRequest:
    values: dict[str, object] = {
        "output_class": OutputClass.ASSET_ART,
        "description": "16 by 16 pixel wizard",
        "width": 16,
        "height": 16,
        "seed": "sp02-fixed-seed",
        "provider_id": "PIXELLAB",
        "provider_workflow_version": "sp02-test-workflow",
        "provider_model": "PIXFLUX",
    }
    values.update(changes)
    return SemanticGenerationRequest(**values)


def image(role: ImageInputRole, payload: bytes) -> ImageInputDescriptor:
    return ImageInputDescriptor(role, hashlib.sha256(payload).hexdigest(), "image/png", 16, 16, "fixture")


def test_registry_is_explicit_stable_and_lazy() -> None:
    assert available_provider_ids() == ("MAGNIFIC", "PIXELLAB")
    assert get_provider_descriptor("MAGNIFIC").adapter_version == "magnific-adapter-v1"
    assert get_provider_descriptor("PIXELLAB").adapter_version == "pixellab-adapter-v1"
    assert isinstance(create_provider("MAGNIFIC"), MagnificProvider)
    assert isinstance(create_provider("PIXELLAB"), PixelLabProvider)
    with pytest.raises(SemanticProviderError):
        create_provider("OTHER")


def test_magnific_job_is_deterministic_and_preserves_seed_without_claiming_seed_control() -> None:
    request = asset_request(provider_id="MAGNIFIC", provider_model="magnific-sd3")
    first = MagnificJobSpec.from_request(request)
    second = MagnificJobSpec.from_request(request)
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.digest() == second.digest()
    assert first.provider_seed_supported is False
    assert first.original_seed == request.seed
    assert first.aspect_ratio == "1:1"
    assert first.logical_width == first.logical_height == 16
    assert "logical dimensions are provenance only" in first.rendered_prompt


def test_committed_provider_job_fixtures_are_executable_canonical_examples() -> None:
    fixture_root = Path(__file__).parents[1] / "fixtures" / "sp02"
    magnific = json.loads((fixture_root / "magnific_smoke_job.json").read_text(encoding="utf-8"))
    pixellab = json.loads((fixture_root / "pixellab_pixflux_job.json").read_text(encoding="utf-8"))
    magnific_request = asset_request(provider_id="MAGNIFIC", provider_model="magnific-sd3", seed="sp02-magnific-fixture", provider_workflow_version="sp02-workflow-v1")
    pixellab_request = asset_request(provider_id="PIXELLAB", provider_model="PIXFLUX", seed="sp02-pixellab-fixture", provider_workflow_version="sp02-workflow-v1")
    assert MagnificJobSpec.from_request(magnific_request).canonical_dict() == magnific
    assert PixelLabJobSpec.from_request(pixellab_request).canonical_dict() == pixellab


def test_magnific_reference_and_style_bindings_are_role_hash_exact() -> None:
    ref_payload, style_payload = b"reference", b"style"
    request = asset_request(provider_id="MAGNIFIC", provider_model="magnific-low-cost", reference_images=(image(ImageInputRole.REFERENCE, ref_payload),), style_image=image(ImageInputRole.STYLE, style_payload))
    bindings = (
        MagnificReferenceBinding("REFERENCE", hashlib.sha256(ref_payload).hexdigest(), "creation-ref"),
        MagnificReferenceBinding("STYLE", hashlib.sha256(style_payload).hexdigest(), "creation-style"),
    )
    job = MagnificJobSpec.from_request(request, bindings=bindings)
    assert [item.creation_id for item in job.reference_bindings] == ["creation-ref", "creation-style"]
    with pytest.raises(SemanticProviderError):
        MagnificJobSpec.from_request(request, bindings=bindings[:1])
    with pytest.raises(SemanticProviderError):
        MagnificJobSpec.from_request(request, bindings=bindings + (MagnificReferenceBinding("REFERENCE", hashlib.sha256(b"extra").hexdigest(), "extra"),))


def test_magnific_result_import_verifies_manifest_bytes_dimensions_and_request() -> None:
    request = asset_request(provider_id="MAGNIFIC", provider_model="magnific-low-cost")
    job = MagnificJobSpec.from_request(request)
    raw = b"verified-external-png-bytes"
    manifest = MagnificResultManifest.success(job, raw_image_sha256=hashlib.sha256(raw).hexdigest(), returned_width=16, returned_height=16, creation_id="creation-1")
    candidate = manifest.import_result(request, job, raw)
    assert candidate.status is CandidateStatus.SUCCESS
    assert candidate.provider_id == "MAGNIFIC"
    assert candidate.model_id == "magnific-low-cost"
    with pytest.raises(SemanticProviderError):
        manifest.import_result(request, job, b"tampered")
    wrong = asset_request(provider_id="MAGNIFIC", provider_model="magnific-low-cost", seed="other")
    with pytest.raises(SemanticProviderError):
        manifest.import_result(wrong, job, raw)


def test_pixellab_job_maps_controls_exactly_and_excludes_runtime_secret() -> None:
    request = asset_request(outline="DARK", shading="BASIC", detail="HIGH", view="SIDE", direction="NE", isometric=True, no_background=True, negative_description="blur")
    job = PixelLabJobSpec.from_request(request)
    assert job.width == job.height == 16
    assert job.provider_seed >= 0
    assert job.original_seed == request.seed
    controls = job.canonical_dict()["controls"]
    assert controls == {"outline": "single color black outline", "shading": "basic shading", "detail": "highly detailed", "view": "side", "direction": "north-east", "isometric": True}
    assert "secret" not in json.dumps(job.canonical_dict()).lower()
    config = PixelLabRuntimeConfig("sentinel-secret", "https://secret.example.invalid")
    assert "sentinel-secret" not in repr(config)
    assert "sentinel-secret" not in json.dumps(config.identity_dict())
    assert PixelLabJobSpec.from_request(asset_request(seed="different")).provider_seed != job.provider_seed


def test_pixellab_rejects_unmapped_controls_and_generic_reference_inputs() -> None:
    with pytest.raises(Exception, match="truthful shading mapping"):
        PixelLabJobSpec.from_request(asset_request(shading="SOFT"))
    payload = b"generic-reference"
    request = asset_request(reference_images=(image(ImageInputRole.REFERENCE, payload),))
    with pytest.raises(Exception, match="generic REFERENCE"):
        PixelLabJobSpec.from_request(request)
    with pytest.raises(Exception, match="exactly one"):
        PixelLabJobSpec.from_request(asset_request(desired_candidate_count=2))


def test_pixellab_role_hash_bindings_and_immutable_bytes() -> None:
    payload = b"init-input"
    descriptor = image(ImageInputRole.INIT, payload)
    request = asset_request(init_image=descriptor, init_strength=0.5)
    binding = PixelLabExecutionBinding("INIT", descriptor.content_sha256, payload, "C:\\local\\input.png")
    job = PixelLabJobSpec.from_request(request, bindings=(binding,))
    assert job.init_image_sha256 == descriptor.content_sha256
    with pytest.raises(SemanticProviderError):
        PixelLabExecutionBinding("INIT", hashlib.sha256(b"other").hexdigest(), payload)
    with pytest.raises(SemanticProviderError):
        PixelLabJobSpec.from_request(request, bindings=())


class FakeImage:
    def __init__(self, raw: bytes, size: tuple[int, int]) -> None:
        self.raw_bytes = raw
        self.size = size


class FakeClient:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def generate_image_pixflux(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return self.response


def test_pixellab_injected_client_calls_only_selected_method_and_verifies_dimensions() -> None:
    raw = b"fake-lossless-result"
    response = SimpleNamespace(image=FakeImage(raw, (16, 16)), usage=SimpleNamespace(usd=0.0))
    client = FakeClient(response)
    provider = PixelLabProvider(client=client, runtime_config=PixelLabRuntimeConfig())
    candidate = provider.generate_checked(asset_request())
    assert candidate.status is CandidateStatus.SUCCESS
    assert client.calls and client.calls[0]["image_size"] == {"width": 16, "height": 16}
    assert client.calls[0]["seed"] == PixelLabJobSpec.from_request(asset_request()).provider_seed
    assert "PIXELLAB_SECRET" not in repr(candidate)

    bad = PixelLabProvider(client=FakeClient(SimpleNamespace(image=FakeImage(raw, (15, 16)))))
    rejected = bad.generate_checked(asset_request())
    assert rejected.status is CandidateStatus.FAILURE
    assert "dimensions" in (rejected.failure_reason or "")
    manifest = provider.manifest_for(candidate, asset_request())
    assert manifest.workflow_version == "sp02-test-workflow"
    assert manifest.canonical_dict()["engine"] == "PIXFLUX"


def test_pixellab_without_secret_is_typed_unavailable_and_does_not_import_or_call_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PIXELLAB_SECRET", raising=False)
    provider = PixelLabProvider(runtime_config=PixelLabRuntimeConfig())
    result = provider.generate_checked(asset_request())
    assert result.status is CandidateStatus.UNAVAILABLE
    assert result.failure_reason == "PixelLab requires local PIXELLAB_SECRET for explicit execution"


def test_bitforge_is_separately_selected_and_style_binding_is_not_pixflux() -> None:
    payload = b"style-input"
    descriptor = image(ImageInputRole.STYLE, payload)
    request = asset_request(provider_model="BITFORGE", style_image=descriptor)
    binding = PixelLabExecutionBinding("STYLE", descriptor.content_sha256, payload)
    job = PixelLabJobSpec.from_request(request, engine="BITFORGE", bindings=(binding,))
    assert job.engine == "BITFORGE"
    with pytest.raises(Exception, match="STYLE"):
        PixelLabJobSpec.from_request(asset_request(style_image=descriptor))
    assert PixelLabProvider(engine="BITFORGE").capability_metadata["supports_style"] is True
    assert MagnificProvider().capability_metadata["provider_seed_control"] is False
