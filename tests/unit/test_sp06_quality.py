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
    SemanticQualityDiagnostics,
    SemanticQualityError,
    SemanticRawArtifact,
    assess_semantic_quality,
)
from scrubbots_pixel_factory.semantic.quality.core import _compute_diagnostics
from scrubbots_pixel_factory.semantic.normalization.level_art import compile_semantic_level_art


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def _rgba_png(width: int, height: int, pixels: bytes) -> bytes:
    rows = b"".join(b"\x00" + pixels[row * width * 4 : (row + 1) * width * 4] for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) + _chunk(b"IDAT", zlib.compress(rows, 9)) + _chunk(b"IEND", b"")


def _rgb(color_id: str) -> bytes:
    return bytes(CANONICAL_PALETTE.rgb_for(color_id) + (255,))


def _artifact(tmp_path):
    width = height = 20
    cells = ["C01"] * (width * height)
    for row in range(height):
        cells[row * width + 8] = "C02"
    cells[2 * width + 2] = "C03"
    cells[17 * width + 17] = "C03"
    pixels = b"".join(_rgb(value) for value in cells)
    candidate_request = SemanticGenerationRequest(OutputClass.LEVEL_ART, "SP06 legal fixture", difficulty=Difficulty.EASY, width=width, height=height, seed="sp06-fixture")
    candidate = SemanticImageCandidate.success(
        candidate_request,
        candidate_id="sp06-fixture",
        provider_id="test-fixture",
        provider_version="1",
        workflow_version="sp06-test",
        model_id="fixture",
        image_bytes=_rgba_png(width, height, pixels),
        returned_width=width,
        returned_height=height,
    )
    raw = SemanticRawArtifact.from_candidate(candidate)
    return compile_semantic_level_art(raw, SemanticLevelArtRequest(raw.digest(), Difficulty.EASY, width, height))


def test_same_trusted_artifact_has_identical_diagnostics_bytes_and_digest(tmp_path):
    artifact = _artifact(tmp_path)
    first = assess_semantic_quality(artifact)
    second = assess_semantic_quality(artifact)
    assert first.diagnostics.canonical_bytes() == second.diagnostics.canonical_bytes()
    assert first.diagnostics.digest() == second.diagnostics.digest()
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.digest() == second.digest()


def test_transition_counts_and_density_are_exact_on_small_fixture():
    diagnostics = _compute_diagnostics(("C01", "C01", "C02", "C01"), 2, 2)
    assert diagnostics.horizontal_transition_count == 1
    assert diagnostics.vertical_transition_count == 1
    assert diagnostics.total_adjacency_edge_count == 4
    assert diagnostics.transition_density == (2, 4)


def test_components_singletons_largest_sizes_and_shares_are_four_neighbour_facts():
    # C01 has two disconnected components (sizes 3 and 2); C03 is one singleton.
    cells = ("C01", "C01", "C02", "C01", "C02", "C02", "C03", "C01", "C01")
    diagnostics = _compute_diagnostics(cells, 3, 3)
    assert diagnostics.component_counts == (("C01", 2), ("C02", 1), ("C03", 1))
    assert diagnostics.total_component_count == 4
    assert diagnostics.singleton_component_count == 1
    assert diagnostics.largest_component_sizes == (("C01", 3), ("C02", 3), ("C03", 1))
    assert diagnostics.largest_component_shares == (("C01", 3, 5), ("C02", 3, 3), ("C03", 1, 1))


def test_public_assessment_reports_derived_ids_and_counts(tmp_path):
    assessment = assess_semantic_quality(_artifact(tmp_path))
    diagnostics = assessment.diagnostics
    assert diagnostics.used_palette_ids == ("C01", "C02", "C03")
    assert sum(value for _, value in diagnostics.cell_counts) == diagnostics.total_cell_count == 400
    assert tuple(key for key, _ in diagnostics.cell_counts) == tuple(assessment.final_used_palette_ids)
    assert assessment.final_used_color_count == 3


def test_false_diagnostic_counts_cannot_be_minted_by_public_construction(tmp_path):
    diagnostics = assess_semantic_quality(_artifact(tmp_path)).diagnostics
    with pytest.raises(SemanticQualityError) as error:
        replace(diagnostics, horizontal_transition_count=0)
    assert error.value.code == "UNSEALED_DIAGNOSTICS"
    with pytest.raises(SemanticQualityError):
        SemanticQualityDiagnostics(
            diagnostics.width,
            diagnostics.height,
            diagnostics.used_palette_ids,
            diagnostics.cell_counts,
            0,
            diagnostics.vertical_transition_count,
            diagnostics.total_adjacency_edge_count,
            diagnostics.transition_density_numerator,
            diagnostics.transition_density_denominator,
            diagnostics.component_counts,
            diagnostics.total_component_count,
            diagnostics.singleton_component_count,
            diagnostics.largest_component_sizes,
            diagnostics.largest_component_shares,
        )


def test_assessment_requires_intact_artifact_and_grid_binding(tmp_path):
    artifact = _artifact(tmp_path)
    original = artifact.logical_cells
    try:
        object.__setattr__(artifact, "logical_cells", original[:-1] + ("C02",))
        with pytest.raises(SemanticQualityError):
            assess_semantic_quality(artifact)
    finally:
        object.__setattr__(artifact, "logical_cells", original)


def test_unreviewed_never_passes_and_explicit_review_states_are_bound(tmp_path):
    assessment = assess_semantic_quality(_artifact(tmp_path))
    assert assessment.disposition is RecognizabilityDisposition.UNREVIEWED
    assert assessment.passes is False
    accepted = assessment.with_review(RecognizabilityDisposition.ACCEPT, "owner-review", "subject recognizable in review")
    rejected = assessment.with_review(RecognizabilityDisposition.REJECT, "owner-review", "subject not recognizable")
    assert accepted.passes is True
    assert accepted.accepted is True
    assert rejected.passes is False
    assert assessment.diagnostic_digest == accepted.diagnostic_digest == rejected.diagnostic_digest
    assert len({assessment.identity_digest, accepted.identity_digest, rejected.identity_digest}) == 3
    assert assessment.structural_identity_digest == accepted.structural_identity_digest == rejected.structural_identity_digest


@pytest.mark.parametrize("disposition", [RecognizabilityDisposition.ACCEPT, RecognizabilityDisposition.REJECT])
def test_terminal_review_requires_auditable_evidence(tmp_path, disposition):
    with pytest.raises(SemanticQualityError) as error:
        assess_semantic_quality(_artifact(tmp_path)).with_review(disposition, "", "")
    assert error.value.code == "REVIEW_EVIDENCE_REQUIRED"


def test_sp05_artifact_contract_remains_legal(tmp_path):
    artifact = _artifact(tmp_path)
    assert 20 <= artifact.target_width <= 59
    assert 20 <= artifact.target_height <= 59
    assert 3 <= len(artifact.final_used_palette_ids) <= 12
    assert all(value in CANONICAL_PALETTE.ids for value in artifact.logical_cells)
