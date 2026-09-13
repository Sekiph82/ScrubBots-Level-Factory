import json
from dataclasses import replace
import struct
import zlib

import pytest

from scrubbots_pixel_factory.semantic import (
    BenchmarkCase, CostUsageRecord, MetadataBlindReviewPack,
    NormalizationCompatibility, NormalizationEvidence, OutputClass,
    OwnerReviewDisposition, ProviderWorkflowSpec, QualificationAttemptRecord,
    QualificationLifecycle, RawImportEvidence, SemanticContractError,
    SemanticGenerationRequest, SemanticImageCandidate, SemanticRawArtifact,
    SemanticNormalizationRequest, normalize_semantic_artifact,
    build_metadata_blind_review_pack, build_qualification_plan,
    default_benchmark_corpus, default_evidence_references,
    default_provider_workflow_matrix, summarize_qualification,
)


def test_default_corpus_is_versioned_complete_and_canonical():
    corpus = default_benchmark_corpus()
    subjects = {case.subject for case in corpus}
    assert len(corpus) >= 15
    assert {"wizard", "warrior", "elf", "robot", "fish", "sea-creature", "mushroom", "ghost", "rocket", "tree", "skull", "potion", "crab", "alien", "building"} <= subjects
    assert len({case.case_id for case in corpus}) == len(corpus)
    assert all(case.output_class is OutputClass.ASSET_ART for case in corpus)
    assert all((case.target_width, case.target_height) == (24, 24) for case in corpus)
    assert all("C01" not in json.dumps(case.canonical_dict()) for case in corpus)
    assert [case.digest() for case in corpus] == [case.digest() for case in default_benchmark_corpus()]


def test_corpus_rejects_level_art_and_invalid_dimensions():
    with pytest.raises(SemanticContractError):
        BenchmarkCase("x", "wizard", "character", "wizard", output_class=OutputClass.LEVEL_ART)
    with pytest.raises(SemanticContractError):
        BenchmarkCase("x", "wizard", "character", "wizard", target_width=0)


def test_provider_matrix_is_explicit_and_truthful():
    matrix = default_provider_workflow_matrix()
    assert {(item.provider_id, item.model_or_engine) for item in matrix} == {("MAGNIFIC", "recraft-v4-1"), ("PIXELLAB", "PIXFLUX"), ("PIXELLAB", "BITFORGE")}
    assert matrix[0].requires_sp03_normalization and not matrix[0].exact_size_expected
    assert matrix[1].exact_size_expected and matrix[1].deterministic_seed_supported
    assert matrix[2].supports_style and "style_image" in matrix[2].native_controls
    with pytest.raises(SemanticContractError):
        ProviderWorkflowSpec("UNKNOWN", "model", "v", "1", "workflow", execution_surface="official-sdk")
    with pytest.raises(SemanticContractError):
        ProviderWorkflowSpec("MAGNIFIC", "not-pinned", "v", "1", "workflow", "magnific-model-snapshot-v1", "1:1", None, False, True, True, False, False, "external-manual-orchestrator", ("style_image",))
    with pytest.raises(SemanticContractError):
        ProviderWorkflowSpec("PIXELLAB", "PIXFLUX", "v", "1", "workflow", None, None, None, True, False, False, True, True, "official-sdk", ("image_size",))


def test_plan_is_finite_explicit_and_corpus_version_bound():
    plan = build_qualification_plan(review_seed="review-seed", attempts_per_cell=2, max_attempts=90)
    assert plan.attempt_count == 90 and plan.max_attempts == 90 and plan.credit_budget is None
    assert len({entry.entry_id for entry in plan.entries}) == plan.attempt_count
    assert plan.digest() == build_qualification_plan(review_seed="review-seed", attempts_per_cell=2, max_attempts=90).digest()
    with pytest.raises(SemanticContractError):
        build_qualification_plan(corpus_version="wrong")
    with pytest.raises(SemanticContractError):
        build_qualification_plan(attempts_per_cell=10_001)


def test_plan_construction_does_not_invoke_provider(monkeypatch):
    import scrubbots_pixel_factory.semantic.providers.magnific.bridge as bridge
    monkeypatch.setattr(bridge.MagnificProvider, "generate", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("provider execution")))
    assert build_qualification_plan().attempt_count == 45


def _ready_attempt(entry_index=0):
    pixels = bytes((12, 34, 56, 255)) * (24 * 24)
    rows = b"".join(b"\x00" + pixels[row * 24 * 4 : (row + 1) * 24 * 4] for row in range(24))
    header = struct.pack(">IIBBBBB", 24, 24, 8, 6, 0, 0, 0)
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
    request = SemanticGenerationRequest(output_class=OutputClass.ASSET_ART, description="wizard qualification fixture", width=24, height=24, seed="sp04-fixture")
    candidate = SemanticImageCandidate.success(request, candidate_id="sp04-candidate", provider_id="MAGNIFIC", provider_version="magnific-adapter-v1", workflow_version="semantic-magnific-workflow-v1", model_id="recraft-v4-1", image_bytes=png, returned_width=24, returned_height=24)
    typed_raw = SemanticRawArtifact.from_candidate(candidate)
    typed_normalized = normalize_semantic_artifact(typed_raw, SemanticNormalizationRequest(typed_raw.digest(), OutputClass.ASSET_ART, 24, 24))
    raw = RawImportEvidence.from_sp03(typed_raw)
    normalized = NormalizationEvidence.from_sp03(typed_normalized)
    plan = build_qualification_plan()
    return QualificationAttemptRecord.from_plan_entry(plan, plan.entries[entry_index], lifecycle=QualificationLifecycle.READY_FOR_BLIND_REVIEW, raw_import=raw, normalization=normalized)


def test_raw_import_and_normalized_evidence_are_required_and_bound():
    record = _ready_attempt()
    assert record.lifecycle is QualificationLifecycle.READY_FOR_BLIND_REVIEW
    object.__setattr__(record.raw_import, "compatibility", NormalizationCompatibility.NOT_ATTEMPTED)
    with pytest.raises(SemanticContractError):
        record.raw_import._assert_integrity()
    record = _ready_attempt()
    object.__setattr__(record.normalization, "raw_import_sha256", "e" * 64)
    with pytest.raises(SemanticContractError):
        record.normalization._assert_integrity()
    with pytest.raises(SemanticContractError):
        QualificationAttemptRecord("attempt-1", "entry-1", "case", "MAGNIFIC", "recraft-v4-1", "workflow", QualificationLifecycle.READY_FOR_BLIND_REVIEW)


def test_blind_review_is_metadata_blind_stable_and_hidden_bound():
    first = _ready_attempt()
    second = _ready_attempt(3)
    pack = build_metadata_blind_review_pack([first, second], review_seed=123)
    assert isinstance(pack, MetadataBlindReviewPack)
    visible = json.dumps(pack.visible_dict(), sort_keys=True)
    assert "MAGNIFIC" not in visible and "recraft" not in visible and "seed" not in visible and "cost" not in visible
    assert {item.hidden_attempt_id for item in pack.items} == {first.attempt_id, second.attempt_id}
    assert {item.review_id for item in pack.items} == {item.review_item_id for item in pack.hidden_attempts}
    assert "MAGNIFIC" in json.dumps(pack.hidden_manifest())
    assert pack.visible_dict() == build_metadata_blind_review_pack([first, second], review_seed=123).visible_dict()


def test_review_requires_ready_pending_and_owner_state_is_separate():
    with pytest.raises(SemanticContractError):
        build_metadata_blind_review_pack([replace(_ready_attempt(), lifecycle=QualificationLifecycle.NORMALIZED)], review_seed=1)
    with pytest.raises(SemanticContractError):
        replace(_ready_attempt(), owner_disposition=OwnerReviewDisposition.OWNER_ACCEPTED)
    assert _ready_attempt().with_lifecycle(QualificationLifecycle.OWNER_ACCEPTED, owner_disposition=OwnerReviewDisposition.OWNER_ACCEPTED)


def test_cost_usage_is_unknown_and_separate_from_identity():
    record = _ready_attempt()
    expensive = record.with_cost_usage(CostUsageRecord(provider_attempt_count=4, provider_credits=2.5, currency_cost=9.0, elapsed_seconds=1.5, observed_at="2026-09-13T00:00:00Z"))
    assert record.cost_usage.currency_cost is None and record.digest() == expensive.digest() and record.canonical_dict() != expensive.canonical_dict()


def test_summary_is_technical_and_does_not_promote_owner_state():
    summary = summarize_qualification(build_qualification_plan(), [_ready_attempt()])
    assert summary.technical_ready_count == 1 and summary.gate_status == "PENDING_OWNER_REVIEW" and summary.owner_accepted_count == 0


def test_evidence_references_have_no_private_material():
    references = default_evidence_references()
    assert {item.evidence_id for item in references} == {"SP02-MAGNIFIC-WIZARD-DIRECTION", "M10-NEGATIVE-OWNER-PACK"}
    encoded = json.dumps([item.canonical_dict() for item in references])
    assert "https://" not in encoded and "signed" not in encoded.lower() and all(not item.private_source_embedded for item in references)


def test_plan_capabilities_fail_closed_and_style_requirement_is_identity_bound():
    case = replace(default_benchmark_corpus()[0], requires_style=True)
    matrix = default_provider_workflow_matrix()
    with pytest.raises(SemanticContractError):
        build_qualification_plan(corpus=(case,), provider_matrix=(matrix[1],))
    bitforge_plan = build_qualification_plan(corpus=(case,), provider_matrix=(matrix[2],))
    assert bitforge_plan.attempt_count == 1
    assert bitforge_plan.cases[0].requires_style is True
    reference_case = replace(default_benchmark_corpus()[0], requires_reference=True)
    with pytest.raises(SemanticContractError):
        build_qualification_plan(corpus=(reference_case,), provider_matrix=(matrix[1],))


def test_plan_entry_integrity_rejects_wrong_or_duplicate_cartesian_cells():
    plan = build_qualification_plan()
    bad_entry = replace(plan.entries[0], provider_id="PIXELLAB")
    with pytest.raises(SemanticContractError):
        replace(plan, entries=(bad_entry,) + plan.entries[1:])
    duplicate = plan.entries[:-1] + (plan.entries[0],)
    with pytest.raises(SemanticContractError):
        replace(plan, entries=duplicate)
    missing = plan.entries[:-1]
    with pytest.raises(SemanticContractError):
        replace(plan, entries=missing)


def test_only_typed_sp03_artifacts_can_mint_verified_evidence():
    record = _ready_attempt()
    with pytest.raises(TypeError):
        RawImportEvidence("a" * 64, "image/png", 24, 24, "MAGNIFIC", "v", "w", "id", "b" * 64, NormalizationCompatibility.PASS)
    with pytest.raises(TypeError):
        NormalizationEvidence("a" * 64, "b" * 64, 24, 24, "policy", "nearest", True, NormalizationCompatibility.PASS)
    raw = record.raw_import
    object.__setattr__(raw, "raw_sha256", "e" * 64)
    with pytest.raises(SemanticContractError):
        raw._assert_integrity()


def test_evidence_seals_detect_coordinated_provenance_tampering():
    record = _ready_attempt()
    raw = record.raw_import
    object.__setattr__(raw, "raw_artifact_digest", "e" * 64)
    with pytest.raises(SemanticContractError):
        raw._assert_integrity()
    record = _ready_attempt()
    raw = record.raw_import
    object.__setattr__(raw, "provider_id", "PIXELLAB")
    with pytest.raises(SemanticContractError):
        raw._assert_integrity()
    record = _ready_attempt()
    normalized = record.normalization
    object.__setattr__(normalized, "normalization_request_digest", "e" * 64)
    with pytest.raises(SemanticContractError):
        normalized._assert_integrity()
    record = _ready_attempt()
    object.__setattr__(record, "provider_matrix_id", "f" * 64)
    with pytest.raises(SemanticContractError):
        record._assert_integrity()


def test_lifecycle_transitions_require_sealed_chain_and_owner_terminal_prerequisites():
    record = _ready_attempt()
    assert record.with_lifecycle(QualificationLifecycle.OWNER_ACCEPTED, owner_disposition=OwnerReviewDisposition.OWNER_ACCEPTED).lifecycle is QualificationLifecycle.OWNER_ACCEPTED
    assert record.with_lifecycle(QualificationLifecycle.OWNER_REJECTED, owner_disposition=OwnerReviewDisposition.OWNER_REJECTED).lifecycle is QualificationLifecycle.OWNER_REJECTED
    with pytest.raises(SemanticContractError):
        record.with_lifecycle(QualificationLifecycle.OWNER_ACCEPTED)
    object.__setattr__(record.raw_import, "compatibility", NormalizationCompatibility.FAIL)
    with pytest.raises(SemanticContractError):
        record._assert_integrity()


def test_blind_review_direct_mapping_is_id_based_and_rejects_orphans_duplicates_and_mismatch():
    first = _ready_attempt()
    second = _ready_attempt(3)
    pack = build_metadata_blind_review_pack([first, second], review_seed=7)
    with pytest.raises(SemanticContractError):
        MetadataBlindReviewPack(pack.review_seed, (replace(pack.items[0], hidden_attempt_id="missing"), pack.items[1]), pack.hidden_attempts)
    with pytest.raises(SemanticContractError):
        MetadataBlindReviewPack(pack.review_seed, (replace(pack.items[0], review_id="wrong"), pack.items[1]), pack.hidden_attempts)
    with pytest.raises(SemanticContractError):
        MetadataBlindReviewPack(pack.review_seed, (pack.items[0], pack.items[0]), pack.hidden_attempts)
    reordered = MetadataBlindReviewPack(pack.review_seed, pack.items, tuple(reversed(pack.hidden_attempts)))
    assert {item.hidden_attempt_id: item.review_id for item in reordered.items} == {attempt.attempt_id: attempt.review_item_id for attempt in pack.hidden_attempts}


def test_review_binding_is_idempotent_and_ignores_cost_but_tracks_artifact_identity():
    record = _ready_attempt()
    bound = record.with_review_binding("review-fixed")
    assert bound.review_binding_digest() == record.review_binding_digest()
    assert bound.with_review_binding("review-fixed").review_binding_digest() == bound.review_binding_digest()
    assert bound.with_cost_usage(CostUsageRecord(provider_credits=4.0)).review_binding_digest() == bound.review_binding_digest()


def test_summary_terminal_states_are_not_reported_as_no_ready():
    plan = build_qualification_plan()
    accepted = _ready_attempt().with_lifecycle(QualificationLifecycle.OWNER_ACCEPTED, owner_disposition=OwnerReviewDisposition.OWNER_ACCEPTED)
    rejected = _ready_attempt(3).with_lifecycle(QualificationLifecycle.OWNER_REJECTED, owner_disposition=OwnerReviewDisposition.OWNER_REJECTED)
    assert summarize_qualification(plan, [accepted]).gate_status == "OWNER_ACCEPTED"
    assert summarize_qualification(plan, [rejected]).gate_status == "OWNER_REJECTED"
    assert summarize_qualification(plan, [accepted, rejected]).gate_status == "MIXED"
