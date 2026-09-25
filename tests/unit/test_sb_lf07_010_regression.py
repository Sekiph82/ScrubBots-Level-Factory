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
    EvidenceDisposition,
    MutationCandidate,
    MutationContractError,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationProvenance,
    MutationRequest,
    OwnerSourceRecord,
    compare_efficiency,
    evidence,
    revalidate_mutation,
    run_bounded_mutations,
    select_target,
    verify_owner_source_immutable,
)
from sb_lf07_r01_support import engine as concrete_engine, m23_authority, m39_authority


ROOT = Path(__file__).parents[2]
CORPUS = ROOT / "tests" / "fixtures" / "sb_lf07_mutation_regression_v1.json"


def _parent(candidate_id: str = "regression-parent") -> MutationCandidate:
    return MutationCandidate.root(
        candidate_id,
        {"width": 20, "height": 20, "color_count": 3, "difficulty_label": "EASY", "gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 5, "booster": "+1_SLOT"}},
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
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PREVIEW_DEPTH_HARDEN_V1", operator_version="1", seed=101, intent=MutationIntent.HARDEN, authority=m23_authority())
    first = engine.apply(request, parent)
    second = engine.apply(request, parent)
    assert first.digest() == second.digest()
    assert first.child is not None and first.child.payload["width"] == 20  # type: ignore[index]
    assert first.child.payload["color_count"] == 3  # type: ignore[index]
    assert MutationProvenance.from_result(request, first, attempt_ordinal=0).digest() == MutationProvenance.from_result(request, second, attempt_ordinal=0).digest()

    def factory(candidate, ordinal, seed):
        return MutationRequest.for_candidate(candidate, operator_id="CANONICAL_PREVIEW_DEPTH_HARDEN_V1", operator_version="1", seed=seed, intent=MutationIntent.HARDEN, authority=m23_authority())

    def validate(result):
        return revalidate_mutation(result, *_evidence_chain(result))

    target = ChallengeTarget(50, 70, "DIFFICULTY_V1", ("load", "risk", "retention"))
    report_a = run_bounded_mutations(parent, base_seed=101, budget=AttemptBudget(2), request_factory=factory, engine=engine, validator=validate, target=target)
    report_b = run_bounded_mutations(parent, base_seed=101, budget=AttemptBudget(2), request_factory=factory, engine=engine, validator=validate, target=target)
    assert report_a.disposition is report_b.disposition is AttemptDisposition.TARGET_MATCH
    assert [(r.ordinal, r.effective_seed, r.mutation.digest()) for r in report_a.attempts] == [(r.ordinal, r.effective_seed, r.mutation.digest()) for r in report_b.attempts]


def test_regression_corpus_exercises_real_easing_truth_chain_and_negative_tamper() -> None:
    parent = _parent()
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
