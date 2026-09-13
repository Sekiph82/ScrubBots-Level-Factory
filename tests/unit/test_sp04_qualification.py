import json
from dataclasses import replace

import pytest

from scrubbots_pixel_factory.semantic import (
    BenchmarkCase, CostUsageRecord, MetadataBlindReviewPack,
    NormalizationCompatibility, NormalizationEvidence, OutputClass,
    OwnerReviewDisposition, ProviderWorkflowSpec, QualificationAttemptRecord,
    QualificationLifecycle, RawImportEvidence, SemanticContractError,
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


def _ready_attempt():
    raw_sha = "a" * 64
    raw = RawImportEvidence(raw_sha, "image/png", 2048, 2048, "MAGNIFIC", "magnific-adapter-v1", "semantic-magnific-workflow-v1", "provider-result-1", "b" * 64, NormalizationCompatibility.PASS)
    normalized = NormalizationEvidence("c" * 64, "d" * 64, 24, 24, "semantic-normalization-v1", "nearest-neighbor", False, NormalizationCompatibility.PASS, raw_sha)
    return QualificationAttemptRecord("attempt-1", "entry-1", "SP04-BENCH-001", "MAGNIFIC", "recraft-v4-1", "semantic-magnific-workflow-v1", QualificationLifecycle.READY_FOR_BLIND_REVIEW, raw, normalized, OwnerReviewDisposition.PENDING_OWNER_REVIEW, CostUsageRecord(), provider_version="magnific-adapter-v1")


def test_raw_import_and_normalized_evidence_are_required_and_bound():
    record = _ready_attempt()
    assert record.lifecycle is QualificationLifecycle.READY_FOR_BLIND_REVIEW
    with pytest.raises(SemanticContractError):
        replace(record, raw_import=replace(record.raw_import, compatibility=NormalizationCompatibility.NOT_ATTEMPTED))
    with pytest.raises(SemanticContractError):
        replace(record, normalization=replace(record.normalization, raw_import_sha256="e" * 64))
    with pytest.raises(SemanticContractError):
        QualificationAttemptRecord("attempt-1", "entry-1", "case", "MAGNIFIC", "recraft-v4-1", "workflow", QualificationLifecycle.READY_FOR_BLIND_REVIEW)


def test_blind_review_is_metadata_blind_stable_and_hidden_bound():
    first = _ready_attempt()
    second = replace(first, attempt_id="attempt-2", plan_entry_id="entry-2", case_id="SP04-BENCH-002")
    pack = build_metadata_blind_review_pack([first, second], review_seed=123)
    assert isinstance(pack, MetadataBlindReviewPack)
    visible = json.dumps(pack.visible_dict(), sort_keys=True)
    assert "MAGNIFIC" not in visible and "recraft" not in visible and "seed" not in visible and "cost" not in visible
    assert {item.hidden_attempt_id for item in pack.items} == {"attempt-1", "attempt-2"}
    assert {item.review_id for item in pack.items} == {item.review_item_id for item in pack.hidden_attempts}
    assert "MAGNIFIC" in json.dumps(pack.hidden_manifest())
    assert pack.visible_dict() == build_metadata_blind_review_pack([first, second], review_seed=123).visible_dict()


def test_review_requires_ready_pending_and_owner_state_is_separate():
    with pytest.raises(SemanticContractError):
        build_metadata_blind_review_pack([replace(_ready_attempt(), lifecycle=QualificationLifecycle.NORMALIZED)], review_seed=1)
    with pytest.raises(SemanticContractError):
        replace(_ready_attempt(), owner_disposition=OwnerReviewDisposition.OWNER_ACCEPTED)
    assert replace(_ready_attempt(), lifecycle=QualificationLifecycle.OWNER_ACCEPTED, owner_disposition=OwnerReviewDisposition.OWNER_ACCEPTED)


def test_cost_usage_is_unknown_and_separate_from_identity():
    record = _ready_attempt()
    expensive = replace(record, cost_usage=CostUsageRecord(provider_attempt_count=4, provider_credits=2.5, currency_cost=9.0, elapsed_seconds=1.5, observed_at="2026-09-13T00:00:00Z"))
    assert record.cost_usage.currency_cost is None and record.digest() == expensive.digest() and record.canonical_dict() != expensive.canonical_dict()


def test_summary_is_technical_and_does_not_promote_owner_state():
    summary = summarize_qualification(build_qualification_plan(), [_ready_attempt()])
    assert summary.technical_ready_count == 1 and summary.gate_status == "PENDING_OWNER_REVIEW" and summary.owner_accepted_count == 0


def test_evidence_references_have_no_private_material():
    references = default_evidence_references()
    assert {item.evidence_id for item in references} == {"SP02-MAGNIFIC-WIZARD-DIRECTION", "M10-NEGATIVE-OWNER-PACK"}
    encoded = json.dumps([item.canonical_dict() for item in references])
    assert "https://" not in encoded and "signed" not in encoded.lower() and all(not item.private_source_embedded for item in references)
