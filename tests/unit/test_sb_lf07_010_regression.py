from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory import (
    AttemptBudget,
    AttemptDisposition,
    CANONICAL_M23_PREVIEW_AUTHORITY,
    CANONICAL_M39_SLOT_AUTHORITY,
    CANONICAL_PALETTE,
    ChallengeTarget,
    EfficiencyCounters,
    EfficiencyWorkload,
    GeneratorRouteEvidence,
    EvidenceDisposition,
    MutationCandidate,
    MutationContractError,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationProvenance,
    MutationRequest,
    OwnerSourceRecord,
    SafetyConstraintEvidence,
    TypedChallengeTarget,
    compare_efficiency,
    compare_efficiency_from_routes,
    evidence,
    revalidate_mutation,
    run_bounded_mutations,
    select_target,
    verify_owner_source_immutable,
    MutationAttemptRouteEvidence,
    RegenerationRouteEvidence,
    TrustedAccountingEvidence,
    GenerationRequest,
    GeneratorRouter,
    revalidate_mutation_from_authentic_adapters,
    SourceLinkedMutationContext,
)
from scrubbots_pixel_factory.mutation_base import MutationCandidate as BaseMutationCandidate
from scrubbots_pixel_factory.mutation_hardening import build_hardening_registry
from scrubbots_pixel_factory.mutation_easing import build_easing_registry
from scrubbots_pixel_factory.qa import OwnerSourceRecord as M05OwnerSourceRecord
from scrubbots_pixel_factory.semantic.qualification.models import CostUsageRecord
from sb_lf07_r02_support import fresh_m39_authority
from sb_lf07_r01_support import engine as concrete_engine, m39_authority


ROOT = Path(__file__).parents[2]
CORPUS = ROOT / "tests" / "fixtures" / "sb_lf07_mutation_regression_v1.json"


def _parent(candidate_id: str = "regression-parent") -> MutationCandidate:
    return MutationCandidate.root(
        candidate_id,
        {"width": 20, "height": 20, "color_count": 3, "difficulty_label": "EASY", "gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 6, "booster": "+1_SLOT", "sixth_slot_state": "EMPTY", "live_work_on_sixth": 0}},
        level_data_sha256="1" * 64,
        source_art_sha256="2" * 64,
    )


def _evidence_chain(mutation):
    solver = evidence("M03_SOLVER", EvidenceDisposition.SOLVED, mutation, {"status": "SOLVED"})
    difficulty = evidence("M04_DIFFICULTY", EvidenceDisposition.AVAILABLE, mutation, {"policy_version": "DIFFICULTY_V1", "challenge_score": 60.0, "load": True, "risk": True, "retention": True})
    qa = evidence("M05_QA", EvidenceDisposition.PASS, mutation, {"structural": True, "production": True})
    return solver, difficulty, qa


def test_checksummed_m07_regression_corpus_is_complete_and_versioned() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    expected = corpus["corpus_sha256"]
    payload = dict(corpus)
    payload.pop("corpus_sha256")
    assert corpus["schema"] == "scrubbots-m07-mutation-regression"
    assert corpus["version"] == 1
    assert hashlib.sha256(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected
    assert {case["contract"] for case in corpus["cases"]} == {f"SB-LF07-{index:03d}" for index in range(1, 11)}


def test_repeated_clean_regression_run_has_identical_canonical_digests_and_attempts() -> None:
    parent = _parent()
    engine = concrete_engine()
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1", operator_version="1", seed=101, intent=MutationIntent.HARDEN, authority=m39_authority())
    first = engine.apply(request, parent)
    second = engine.apply(request, parent)
    assert first.digest() == second.digest()
    assert first.child is not None and first.child.payload["width"] == 20  # type: ignore[index]
    assert first.child.payload["color_count"] == 3  # type: ignore[index]
    assert MutationProvenance.from_result(request, first, attempt_ordinal=0).digest() == MutationProvenance.from_result(request, second, attempt_ordinal=0).digest()

    def factory(candidate, ordinal, seed):
        return MutationRequest.for_candidate(candidate, operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1", operator_version="1", seed=seed, intent=MutationIntent.HARDEN, authority=m39_authority())

    def validate(result):
        return revalidate_mutation(result, *_evidence_chain(result))

    target = ChallengeTarget(50, 70, "DIFFICULTY_V1", ("load", "risk", "retention"))
    report_a = run_bounded_mutations(parent, base_seed=101, budget=AttemptBudget(2), request_factory=factory, engine=engine, validator=validate, target=target)
    report_b = run_bounded_mutations(parent, base_seed=101, budget=AttemptBudget(2), request_factory=factory, engine=engine, validator=validate, target=target)
    assert report_a.disposition is report_b.disposition is AttemptDisposition.TARGET_MATCH
    assert [(r.ordinal, r.effective_seed, r.mutation.digest()) for r in report_a.attempts] == [(r.ordinal, r.effective_seed, r.mutation.digest()) for r in report_b.attempts]


def test_regression_corpus_exercises_real_easing_truth_chain_and_negative_tamper() -> None:
    parent = MutationCandidate.root("regression-easing-parent", {"width": 20, "height": 20, "color_count": 3, "difficulty_label": "EASY", "gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 5, "booster": "+1_SLOT"}})
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=102, intent=MutationIntent.EASE, authority=m39_authority())
    mutation = concrete_engine().apply(request, parent)
    assert mutation.disposition is MutationDisposition.APPLIED
    assert mutation.child is not None and mutation.child.payload["gameplay"]["slot_capacity"] == 6  # type: ignore[index]
    solver, difficulty, qa = _evidence_chain(mutation)
    envelope = revalidate_mutation(mutation, solver, difficulty, qa)
    assert envelope.disposition.value == "ELIGIBLE"
    assert select_target(ChallengeTarget(50, 70, "DIFFICULTY_V1"), (envelope,)).candidate is envelope
    bad = dataclasses.replace(difficulty, request_digest="0" * 64, evidence_digest=None)
    with pytest.raises(MutationContractError):
        revalidate_mutation(mutation, solver, bad, qa)


def test_regression_corpus_covers_efficiency_owner_source_and_palette_v3() -> None:
    workload = EfficiencyWorkload("a" * 64, "b" * 64, "c" * 64, "d" * 64)
    comparison = compare_efficiency(workload, workload, EfficiencyCounters(1, 1, 1, 0, 0, 3), EfficiencyCounters(1, 1, 0, 1, 0, 4), telemetry={"wall_clock_ms": 1})
    assert "wall_clock_ms" not in str(comparison.canonical_dict())
    raw = b"regression-owner-source"
    source = OwnerSourceRecord("regression-source", hashlib.sha256(raw).hexdigest(), len(raw), 20, 20, "owner-uploads/regression/source.png")
    assert verify_owner_source_immutable(source, raw, raw, before_dimensions=(20, 20), after_dimensions=(20, 20)).disposition == "PASS"
    assert [color.id for color in CANONICAL_PALETTE.colors] == [f"C{i:02d}" for i in range(1, 17)]
    assert CANONICAL_PALETTE.background.id == "BG01"
    assert CANONICAL_PALETTE.used_color_envelope == (3, 12)
    assert CANONICAL_PALETTE.difficulty_class_derived_from_color_count is False


def test_r01_corpus_binds_typed_target_route_and_owner_identity() -> None:
    policy = "a" * 64
    safety = SafetyConstraintEvidence("m04-safety", "1", policy, True, True, True, "b" * 64)
    target = TypedChallengeTarget(50, 70, policy, safety)
    assert target.digest()
    route_a = GeneratorRouteEvidence("mutation", "c" * 64, 2, 1, 0, 4, "d" * 64)
    route_b = GeneratorRouteEvidence("regenerate", "c" * 64, 2, 0, 1, 8, "e" * 64)
    assert compare_efficiency_from_routes(route_a, route_b).digest()
    upload = "owner-upload-" + "f" * 64
    owner = OwnerSourceRecord.from_m05_owner_upload({"source_id": upload, "origin": "OWNER_UPLOAD", "status": "SOURCE_ONLY", "validation_state": "UNVALIDATED", "source_sha256": "1" * 64, "byte_length": 1, "original_width": 1, "original_height": 1, "immutable_relative_path": f"owner-uploads/{upload}/source.png"})
    assert owner.source_id == upload


def test_r02_regression_exercises_separated_services_fresh_authority_and_real_route() -> None:
    authority = fresh_m39_authority()
    assert authority.commit_sha != "281ea38218aaf24ab88c70e998f59b14df9d1c97"
    assert not hasattr(__import__("scrubbots_pixel_factory.mutation_base", fromlist=["x"]), "evidence")
    assert build_hardening_registry(authority).snapshot()[0].operator_id.endswith("HARDEN_V1")
    assert build_easing_registry(authority).snapshot()[0].operator_id.endswith("EASE_V1")
    parent = _parent("r02-dynamic-authority")
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1", operator_version="1", seed=303, intent=MutationIntent.HARDEN, authority=authority)
    result = MutationEngine(build_hardening_registry(authority)).apply(request, parent)
    assert result.disposition is MutationDisposition.APPLIED
    solver, difficulty, qa = _evidence_chain(result)
    with pytest.raises(MutationContractError):
        revalidate_mutation_from_authentic_adapters(result, solver, difficulty, qa)  # type: ignore[arg-type]
    generation = GeneratorRouter().generate(GenerationRequest("EASY", 303, "MASK", width=20, height=20))
    workload = EfficiencyWorkload("a" * 64, "b" * 64, "c" * 64, "d" * 64)
    regen = RegenerationRouteEvidence.from_generation_result(generation, workload, config_digest="e" * 64, accounting=TrustedAccountingEvidence.from_cost_usage(CostUsageRecord(provider_attempt_count=1)))
    assert regen.counters.produced == 1
