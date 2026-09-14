from __future__ import annotations

from dataclasses import replace
import struct
import zlib

import pytest

from scrubbots_pixel_factory import (
    CANONICAL_PALETTE,
    Difficulty,
    OutputClass,
    RecognizabilityDisposition,
    SemanticGenerationRequest,
    SemanticImageCandidate,
    SemanticLevelArtRequest,
    SemanticQualityError,
    SemanticRawArtifact,
    assess_semantic_quality,
    export_semantic_quality_evidence,
    load_semantic_quality_evidence,
    require_semantic_recognizability_acceptance,
)
from scrubbots_pixel_factory.semantic.normalization.level_art import compile_semantic_level_art


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def _png(width: int, height: int, pixels: bytes) -> bytes:
    rows = b"".join(b"\x00" + pixels[row * width * 4 : (row + 1) * width * 4] for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) + _chunk(b"IDAT", zlib.compress(rows, 9)) + _chunk(b"IEND", b"")


def _artifact(tmp_path, variant: int = 0):
    width = height = 20
    cells = ["C01"] * (width * height)
    for row in range(height):
        cells[row * width + 8] = "C02"
    cells[(2 + variant) * width + 2] = "C03"
    cells[(17 - variant) * width + 17] = "C03"
    pixels = b"".join(bytes(CANONICAL_PALETTE.rgb_for(value) + (255,)) for value in cells)
    request = SemanticGenerationRequest(OutputClass.LEVEL_ART, "SP06 evidence fixture", difficulty=Difficulty.EASY, width=width, height=height, seed=f"sp06-evidence-{variant}")
    candidate = SemanticImageCandidate.success(
        request,
        candidate_id=f"sp06-evidence-{variant}",
        provider_id="test-fixture",
        provider_version="1",
        workflow_version="sp06-test",
        model_id="fixture",
        image_bytes=_png(width, height, pixels),
        returned_width=width,
        returned_height=height,
    )
    raw = SemanticRawArtifact.from_candidate(candidate)
    artifact = compile_semantic_level_art(raw, SemanticLevelArtRequest(raw.digest(), Difficulty.EASY, width, height))
    return artifact, request


def _accepted(tmp_path, variant: int = 0):
    artifact, request = _artifact(tmp_path, variant)
    assessment = assess_semantic_quality(artifact, request).with_review(RecognizabilityDisposition.ACCEPT, "owner-review", "explicit offline review evidence")
    return artifact, request, assessment


def test_accept_evidence_exports_and_reloads_with_same_trusted_identity(tmp_path):
    artifact, request, assessment = _accepted(tmp_path)
    evidence = export_semantic_quality_evidence(assessment)
    reloaded = load_semantic_quality_evidence(evidence.canonical_bytes(), artifact, request)
    assert reloaded.passes is True
    assert reloaded.identity_digest == assessment.identity_digest
    assert reloaded.canonical_bytes() == assessment.canonical_bytes()
    assert require_semantic_recognizability_acceptance(evidence.canonical_dict(), artifact, request).identity_digest == assessment.identity_digest


@pytest.mark.parametrize("disposition", [RecognizabilityDisposition.UNREVIEWED, RecognizabilityDisposition.REJECT])
def test_non_accept_evidence_reloads_but_acceptance_gate_rejects(tmp_path, disposition):
    artifact, request = _artifact(tmp_path)
    assessment = assess_semantic_quality(artifact, request)
    if disposition is RecognizabilityDisposition.REJECT:
        assessment = assessment.with_review(disposition, "owner-review", "explicit rejection evidence")
    evidence = export_semantic_quality_evidence(assessment)
    assert load_semantic_quality_evidence(evidence, artifact, request).disposition is disposition
    with pytest.raises(SemanticQualityError) as error:
        require_semantic_recognizability_acceptance(evidence, artifact, request)
    assert error.value.code == "RECOGNIZABILITY_NOT_ACCEPTED"


def test_repeated_export_is_byte_and_digest_identical(tmp_path):
    _, _, assessment = _accepted(tmp_path)
    first = export_semantic_quality_evidence(assessment)
    second = export_semantic_quality_evidence(assessment)
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.digest() == second.digest()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("trusted_artifact_digest", "0" * 64),
        ("final_logical_grid_digest", "1" * 64),
        ("target_dimensions", {"width": 21, "height": 20}),
        ("final_used_palette_ids", ["C01", "C02", "C03", "C03"]),
        ("final_used_color_count", 4),
        ("diagnostic_policy_version", "WRONG_POLICY"),
        ("structural_assessment_identity_digest", "2" * 64),
        ("review_identity_digest", "3" * 64),
        ("assessment_identity_digest", "4" * 64),
    ],
)
def test_evidence_binding_fields_cannot_be_tampered(tmp_path, field, value):
    artifact, request, assessment = _accepted(tmp_path)
    payload = export_semantic_quality_evidence(assessment).canonical_dict()
    payload[field] = value
    with pytest.raises(SemanticQualityError):
        load_semantic_quality_evidence(payload, artifact, request)


def test_diagnostic_digest_and_fact_tampering_are_recomputed_and_rejected(tmp_path):
    artifact, request, assessment = _accepted(tmp_path)
    payload = export_semantic_quality_evidence(assessment).canonical_dict()
    payload["diagnostics"]["horizontal_transition_count"] += 1
    with pytest.raises(SemanticQualityError) as error:
        load_semantic_quality_evidence(payload, artifact, request)
    assert error.value.code == "DIAGNOSTICS_MISMATCH"
    payload = export_semantic_quality_evidence(assessment).canonical_dict()
    payload["diagnostics_digest"] = "5" * 64
    with pytest.raises(SemanticQualityError):
        load_semantic_quality_evidence(payload, artifact, request)


def test_review_and_full_assessment_identity_tampering_is_rejected(tmp_path):
    artifact, request, assessment = _accepted(tmp_path)
    original = export_semantic_quality_evidence(assessment).canonical_dict()
    for field, value in (("reviewer", "different-reviewer"), ("review_reason", "different-reason"), ("review_notes", "different-notes")):
        payload = dict(original)
        payload[field] = value
        with pytest.raises(SemanticQualityError):
            load_semantic_quality_evidence(payload, artifact, request)
    payload = dict(original)
    payload["review_disposition"] = "REJECT"
    with pytest.raises(SemanticQualityError):
        load_semantic_quality_evidence(payload, artifact, request)


def test_legitimate_reject_reconstructs_but_gate_semantics_remain_reject(tmp_path):
    artifact, request = _artifact(tmp_path)
    rejected = assess_semantic_quality(artifact, request).with_review(RecognizabilityDisposition.REJECT, "owner-review", "explicit rejection evidence")
    evidence = export_semantic_quality_evidence(rejected)
    reloaded = load_semantic_quality_evidence(evidence, artifact, request)
    assert reloaded.disposition is RecognizabilityDisposition.REJECT
    with pytest.raises(SemanticQualityError, match="RECOGNIZABILITY_NOT_ACCEPTED"):
        require_semantic_recognizability_acceptance(evidence, artifact, request)


def test_artifact_a_evidence_cannot_validate_against_artifact_b(tmp_path):
    artifact_a, request_a, assessment = _accepted(tmp_path, 0)
    artifact_b, request_b = _artifact(tmp_path, 1)
    evidence = export_semantic_quality_evidence(assessment)
    with pytest.raises(SemanticQualityError):
        load_semantic_quality_evidence(evidence, artifact_b, request_b)
    with pytest.raises(SemanticQualityError):
        load_semantic_quality_evidence(evidence, artifact_a, request_b)


def test_expected_semantic_request_identity_is_checked_when_present(tmp_path):
    artifact, request, assessment = _accepted(tmp_path)
    evidence = export_semantic_quality_evidence(assessment)
    other = SemanticGenerationRequest(OutputClass.LEVEL_ART, "SP06 evidence fixture", difficulty=Difficulty.EASY, width=20, height=20, seed="other")
    with pytest.raises(SemanticQualityError) as error:
        load_semantic_quality_evidence(evidence, artifact, other)
    assert error.value.code == "SEMANTIC_REQUEST_MISMATCH"


def test_strict_parser_rejects_malformed_schema_unknown_fields_and_noncanonical_json(tmp_path):
    artifact, request, assessment = _accepted(tmp_path)
    payload = export_semantic_quality_evidence(assessment).canonical_dict()
    payload["schema_version"] = 99
    with pytest.raises(SemanticQualityError) as error:
        load_semantic_quality_evidence(payload, artifact, request)
    assert error.value.code == "UNSUPPORTED_SCHEMA"
    payload = export_semantic_quality_evidence(assessment).canonical_dict()
    payload["unknown_critical_field"] = True
    with pytest.raises(SemanticQualityError):
        load_semantic_quality_evidence(payload, artifact, request)
    payload = export_semantic_quality_evidence(assessment).canonical_dict()
    with pytest.raises(SemanticQualityError) as error:
        load_semantic_quality_evidence((b" {" + export_semantic_quality_evidence(assessment).canonical_bytes()[1:]), artifact, request)
    assert error.value.code in {"INVALID_JSON", "NON_CANONICAL_JSON"}


def test_public_evidence_construction_and_replace_cannot_mint_trusted_record(tmp_path):
    _, _, assessment = _accepted(tmp_path)
    evidence = export_semantic_quality_evidence(assessment)
    with pytest.raises(SemanticQualityError) as error:
        replace(evidence, assessment_identity_digest="6" * 64)
    assert error.value.code == "UNSEALED_EVIDENCE"
