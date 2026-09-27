from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import pytest

from scrubbots_pixel_factory import AttemptBudget, AttemptDisposition, CANONICAL_PALETTE, MutationContractError, MutationDisposition, SafetyConstraintEvidence, run_authentic_bounded_mutations, build_typed_target, revalidate_mutation_from_authentic_adapters, AuthenticTargetCandidate
from scrubbots_pixel_factory.mutation_efficiency import MutationAttemptRouteEvidence, RegenerationRouteEvidence, compare_efficiency_from_authentic_routes
from scrubbots_pixel_factory.mutation_targeting import select_authentic_target
from test_sb_lf07_004_revalidation import _authentic_chain
from test_sb_lf07_007_attempts import _StaticEngine

CORPUS = Path(__file__).parents[1] / "fixtures" / "sb_lf07_mutation_regression_v1.json"


def test_regression_corpus_remains_versioned_and_complete() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    expected = corpus["corpus_sha256"]
    payload = dict(corpus)
    payload.pop("corpus_sha256")
    actual = hashlib.sha256(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert corpus["schema"] == "scrubbots-m07-mutation-regression"
    assert corpus["version"] == 1
    assert actual == expected
    assert {case["contract"] for case in corpus["cases"]} == {f"SB-LF07-{index:03d}" for index in range(1, 11)}


def test_r04_positive_closure_uses_only_sealed_authentic_apis() -> None:
    parent, request, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    candidate = AuthenticTargetCandidate(envelope, solver, difficulty, qa)
    target = build_typed_target(0.0, 100.0, difficulty, qa, required_constraints=())
    report = run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(1), request_factory=lambda *_: request, engine=_StaticEngine(MutationDisposition.APPLIED, mutation), validator=lambda _: candidate, target=target)
    assert report.disposition is AttemptDisposition.TARGET_MATCH
    assert report.attempts[0].provenance is not None and report.attempts[0].provenance.is_authentic_sealed
    assert target.is_authentic_sealed


def test_r04_negative_closure_rejects_forged_safety_and_provenance_replacement() -> None:
    parent, request, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    candidate = AuthenticTargetCandidate(envelope, solver, difficulty, qa)
    target = build_typed_target(0.0, 100.0, difficulty, qa, required_constraints=())
    report = run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(1), request_factory=lambda *_: request, engine=_StaticEngine(MutationDisposition.APPLIED, mutation), validator=lambda _: candidate, target=target)
    provenance = report.attempts[0].provenance
    assert provenance is not None
    with pytest.raises(MutationContractError):
        replace(provenance, evidence_references=tuple(replace(ref, producer_digest="f" * 64) for ref in provenance.evidence_references))
    with pytest.raises(MutationContractError):
        SafetyConstraintEvidence("forged", "1", target.policy_digest, True, True, True, "f" * 64)
    unavailable = build_typed_target(0.0, 100.0, difficulty, qa)
    assert select_authentic_target(unavailable, (candidate,)).disposition.value == "UNAVAILABLE"


def test_r04_efficiency_and_palette_regressions_remain_truthful() -> None:
    parent, request, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    candidate = AuthenticTargetCandidate(envelope, solver, difficulty, qa)
    target = build_typed_target(0.0, 100.0, difficulty, qa, required_constraints=())
    report = run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(1), request_factory=lambda *_: request, engine=_StaticEngine(MutationDisposition.APPLIED, mutation), validator=lambda _: candidate, target=target)
    route = MutationAttemptRouteEvidence.from_attempt_report(report)
    assert route.counters.accepted == 1
    assert route.counters.solver_workload_available is False
    assert [color.id for color in CANONICAL_PALETTE.colors] == [f"C{i:02d}" for i in range(1, 17)]
    assert CANONICAL_PALETTE.difficulty_class_derived_from_color_count is False
