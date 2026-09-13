from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import zlib

import pytest

from scrubbots_pixel_factory import (
    CandidateStatus,
    ImageInputDescriptor,
    OutputClass,
    SemanticCandidateError,
    SemanticGenerationRequest,
    SemanticImageCandidate,
    SemanticNormalizationError,
    SemanticNormalizationRequiredError,
    SemanticRawArtifact,
    SemanticDecodeError,
    SemanticNormalizationRequest,
    normalize_semantic_artifact,
)
from scrubbots_pixel_factory.cli.main import main


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def rgba_png(width: int, height: int, pixels: bytes) -> bytes:
    assert len(pixels) == width * height * 4
    rows = b"".join(b"\x00" + pixels[row * width * 4 : (row + 1) * width * 4] for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) + _chunk(b"IDAT", zlib.compress(rows, 9)) + _chunk(b"IEND", b"")


def asset_request(**changes: object) -> SemanticGenerationRequest:
    values: dict[str, object] = {"output_class": OutputClass.ASSET_ART, "description": "24x24 semantic test asset", "width": 24, "height": 24, "seed": "sp03-seed"}
    values.update(changes)
    return SemanticGenerationRequest(**values)


def candidate_for_png(raw: bytes, width: int, height: int, **request_changes: object) -> SemanticImageCandidate:
    request = asset_request(**request_changes)
    return SemanticImageCandidate.success(request, candidate_id="sp03-candidate", provider_id="fixture-provider", provider_version="fixture-v1", workflow_version="sp03-fixture-workflow", model_id="fixture-model", image_bytes=raw, returned_width=width, returned_height=height, generation_metadata={"private_url": "https://signed.invalid/x", "secret": "should-not-cross"})


def test_successful_candidate_becomes_immutable_raw_artifact_and_paths_are_not_identity() -> None:
    pixels = bytes((index * 17 % 256 for index in range(24 * 24 * 4)))
    raw_bytes = rgba_png(24, 24, pixels)
    descriptor = ImageInputDescriptor("STYLE", hashlib.sha256(b"style").hexdigest(), local_path="C:\\private\\style.png")
    candidate = candidate_for_png(raw_bytes, 24, 24, style_image=descriptor)
    artifact = SemanticRawArtifact.from_candidate(candidate)
    assert artifact.raw_bytes == raw_bytes
    assert artifact.raw_sha256 == hashlib.sha256(raw_bytes).hexdigest()
    assert artifact.returned_width == artifact.returned_height == 24
    assert "private" not in json.dumps(artifact.canonical_dict()).lower()
    assert "secret" not in json.dumps(artifact.canonical_dict()).lower()
    assert candidate.digest() == artifact.provider_candidate_digest
    normalized = normalize_semantic_artifact(artifact, SemanticNormalizationRequest(artifact.digest(), "ASSET_ART", 24, 24))
    assert artifact.raw_bytes == raw_bytes
    assert normalized.report.exact_size_fast_path is True
    assert normalized.report.resize_applied is False
    assert normalized.rgba8 == pixels


def test_exact_24x24_rgba_path_preserves_pixels_and_is_repeatable() -> None:
    pixels = bytes((index * 29 + 3) % 256 for index in range(24 * 24 * 4))
    raw = SemanticRawArtifact.from_candidate(candidate_for_png(rgba_png(24, 24, pixels), 24, 24))
    request = SemanticNormalizationRequest(raw.digest(), OutputClass.ASSET_ART, 24, 24)
    first = normalize_semantic_artifact(raw, request)
    second = normalize_semantic_artifact(raw, request)
    assert first.rgba8 == pixels == second.rgba8
    assert first.report.canonical_bytes() == second.report.canonical_bytes()
    assert first.digest() == second.digest()


def test_2048_square_source_uses_deterministic_24x24_area_baseline() -> None:
    pixels = bytes((40, 80, 120, 255)) * (2048 * 2048)
    raw = SemanticRawArtifact.from_candidate(candidate_for_png(rgba_png(2048, 2048, pixels), 2048, 2048))
    request = SemanticNormalizationRequest(raw.digest(), "ASSET_ART", 24, 24)
    normalized = normalize_semantic_artifact(raw, request)
    assert (normalized.target_width, normalized.target_height) == (24, 24)
    assert normalized.report.resampler == "AREA_AVERAGE_V1"
    assert normalized.report.crop_pad["operation"] == "FIT_CENTER_LETTERBOX"
    assert normalized.rgba8 == bytes((40, 80, 120, 255)) * (24 * 24)


def test_aspect_mismatch_is_centered_letterbox_not_crop() -> None:
    pixels = bytes((200, 30, 50, 255)) * (8 * 4)
    raw = SemanticRawArtifact.from_candidate(candidate_for_png(rgba_png(8, 4, pixels), 8, 4))
    normalized = normalize_semantic_artifact(raw, SemanticNormalizationRequest(raw.digest(), "ASSET_ART", 8, 8))
    assert normalized.report.crop_pad == {"operation": "FIT_CENTER_LETTERBOX", "scaled_width": 8, "scaled_height": 4, "offset_x": 0, "offset_y": 2}
    assert all(normalized.rgba8[(row * 8 + column) * 4 + 3] == 0 for row in (0, 1, 6, 7) for column in range(8))
    assert normalized.rgba8[(2 * 8) * 4 : (3 * 8) * 4] == pixels[: 8 * 4]


def test_alpha_policy_is_explicit_and_deterministic() -> None:
    pixels = bytes((10, 20, 30, 0)) * (24 * 24)
    raw = SemanticRawArtifact.from_candidate(candidate_for_png(rgba_png(24, 24, pixels), 24, 24))
    opaque = normalize_semantic_artifact(raw, SemanticNormalizationRequest(raw.digest(), "ASSET_ART", 24, 24, alpha_policy="OPAQUE_AS_IS"))
    preserved = normalize_semantic_artifact(raw, SemanticNormalizationRequest(raw.digest(), "ASSET_ART", 24, 24, alpha_policy="PRESERVE_ALPHA"))
    assert opaque.rgba8 == bytes((10, 20, 30, 255)) * (24 * 24)
    assert preserved.rgba8 == pixels


def test_corrupt_and_unsupported_images_fail_closed() -> None:
    raw = SemanticRawArtifact.from_candidate(candidate_for_png(rgba_png(24, 24, bytes((1, 2, 3, 255)) * (24 * 24)), 24, 24))
    request = SemanticNormalizationRequest(raw.digest(), "ASSET_ART", 24, 24)
    corrupt = SemanticRawArtifact.from_candidate(candidate_for_png(b"not-a-png", 24, 24))
    with pytest.raises(SemanticDecodeError):
        normalize_semantic_artifact(corrupt, SemanticNormalizationRequest(corrupt.digest(), "ASSET_ART", 24, 24))
    jpeg_marked = SemanticRawArtifact.from_candidate(candidate_for_png(raw.raw_bytes, 24, 24), media_type="image/jpeg")
    with pytest.raises(SemanticDecodeError):
        normalize_semantic_artifact(jpeg_marked, SemanticNormalizationRequest(jpeg_marked.digest(), "ASSET_ART", 24, 24))
    assert request.target_width == 24


def test_decoded_dimensions_must_match_candidate_returned_dimensions() -> None:
    candidate = candidate_for_png(rgba_png(2, 2, bytes((1, 2, 3, 255)) * 4), 24, 24)
    raw = SemanticRawArtifact.from_candidate(candidate)
    with pytest.raises(SemanticNormalizationError, match="dimensions"):
        normalize_semantic_artifact(raw, SemanticNormalizationRequest(raw.digest(), "ASSET_ART", 24, 24))


def test_raw_source_status_and_hash_contracts_are_required() -> None:
    request = asset_request()
    failed = SemanticImageCandidate.failure(request, candidate_id="failed", provider_id="fixture-provider", provider_version="fixture-v1", workflow_version="sp03-fixture-workflow", reason="not available", status=CandidateStatus.FAILURE)
    with pytest.raises(SemanticNormalizationError):
        SemanticRawArtifact.from_candidate(failed)
    with pytest.raises(SemanticCandidateError):
        SemanticImageCandidate.success(request, candidate_id="too-large", provider_id="fixture-provider", provider_version="fixture-v1", workflow_version="sp03-fixture-workflow", image_bytes=b"raw", returned_width=8193, returned_height=8193)


def test_level_art_requires_future_palette_policy_and_never_masquerades_as_m08() -> None:
    raw = SemanticRawArtifact.from_candidate(candidate_for_png(rgba_png(24, 24, bytes((220, 30, 40, 255)) * (24 * 24)), 24, 24))
    with pytest.raises(SemanticNormalizationError):
        SemanticNormalizationRequest(raw.digest(), "LEVEL_ART", 20, 20)
    request = SemanticNormalizationRequest(raw.digest(), "LEVEL_ART", 20, 20, palette_policy="SCRUBBOTS_C01_C16")
    with pytest.raises(SemanticNormalizationError):
        normalize_semantic_artifact(raw, request)
    normalized = normalize_semantic_artifact(raw, SemanticNormalizationRequest(raw.digest(), "ASSET_ART", 24, 24))
    with pytest.raises(SemanticNormalizationRequiredError):
        normalized.as_m08_artwork()


def test_local_normalization_cli_writes_manifest_without_overwriting_source(tmp_path: Path) -> None:
    source = tmp_path / "input.png"
    output = tmp_path / "normalized.json"
    source_bytes = rgba_png(24, 24, bytes((9, 8, 7, 255)) * (24 * 24))
    source.write_bytes(source_bytes)
    assert main(["semantic-normalize", str(source), "--output-class", "ASSET_ART", "--width", "24", "--height", "24", "--output", str(output)]) == 0
    assert source.read_bytes() == source_bytes
    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["normalization_request"]["target_dimensions"] == {"width": 24, "height": 24}
    assert manifest["normalized_artifact"]["target_dimensions"] == {"width": 24, "height": 24}
    assert main(["semantic-normalize", str(source), "--output-class", "ASSET_ART", "--width", "24", "--height", "24", "--output", str(source)]) == 3
