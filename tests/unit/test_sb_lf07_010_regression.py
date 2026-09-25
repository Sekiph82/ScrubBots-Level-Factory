from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory import (
    AttemptBudget,
    AttemptDisposition,
    AuthenticTargetCandidate,
    CANONICAL_PALETTE,
    GeneratorRouter,
    GenerationRequest,
    LineageRootRegistration,
    MutationContractError,
    MutationDisposition,
    ProvenanceLedger,
    SafetyConstraintEvidence,
    TypedChallengeTarget,
    TrustedAccountingEvidence,
    build_typed_target,
    revalidate_mutation_from_authentic_adapters,
    run_authentic_bounded_mutations,
)
from scrubbots_pixel_factory.mutation_evidence import adapt_m03_solver, provenance_from_authentic_validation
from scrubbots_pixel_factory.mutation_efficiency import MutationAttemptRouteEvidence, RegenerationRouteEvidence, compare_efficiency_from_authentic_routes
from scrubbots_pixel_factory.mutation_source import SourceLinkedMutationContext
from scrubbots_pixel_factory.mutation_targeting import select_authentic_target
from scrubbots_pixel_factory.qa import OwnerSourceRecord as M05OwnerSourceRecord
from sb_lf07_r01_support import engine as concrete_engine, m39_authority
from test_sb_lf07_004_revalidation import AUTHENTIC_SOURCE_PATH, _authentic_chain
from test_sb_lf07_007_attempts import _StaticEngine


ROOT = Path(__file__).parents[2]
CORPUS = ROOT / "tests" / "fixtures" / "sb_lf07_mutation_regression_v1.json"


def _fixture():
    raw = b"scrubbots-r03-regression-source"
    parent, request, mutation, solver, analysis, score, qa, solver_adapter, difficulty_adapter, qa_adapter = _authentic_chain(raw)
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver_adapter, difficulty_adapter, qa_adapter)
    candidate = AuthenticTargetCandidate(envelope, solver_adapter, difficulty_adapter, qa_adapter)
    unavailable_target = build_typed_target(0.0, 100.0, difficulty_adapter, qa_adapter)
    safety = SafetyConstraintEvidence("scrubbots-m07-regression-safety", "1", unavailable_target.policy_digest, True, True, True, qa_adapter.producer_digest)
    target = TypedChallengeTarget(0.0, 100.0, unavailable_target.policy_digest, safety)
    record = M05OwnerSourceRecord("r03-regression-source", str(AUTHENTIC_SOURCE_PATH), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    return parent, request, mutation, solver, difficulty_adapter, qa_adapter, solver_adapter, envelope, candidate, target, unavailable_target, record


def _run(fixture, target, *, budget=2, mutate_source=False):
    parent, request, mutation, _, _, _, _, _, candidate, _, _, record = fixture
    context = SourceLinkedMutationContext.establish(record)

    def validate(result):
        if mutate_source:
            AUTHENTIC_SOURCE_PATH.write_bytes(b"corrupted-after-mutation")
        return candidate

    return run_authentic_bounded_mutations(
        parent,
        base_seed=request.seed,
        budget=AttemptBudget(budget),
        request_factory=lambda current, ordinal, seed: request,
        engine=_StaticEngine(MutationDisposition.APPLIED, mutation),
        validator=validate,
        target=target,
        source_context=context,
    )


def test_checksummed_m07_regression_corpus_is_complete_and_versioned() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    expected = corpus["corpus_sha256"]
    payload = dict(corpus)
    payload.pop("corpus_sha256")
    assert corpus["schema"] == "scrubbots-m07-mutation-regression"
    assert corpus["version"] == 1
    assert hashlib.sha256(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected
    assert {case["contract"] for case in corpus["cases"]} == {f"SB-LF07-{index:03d}" for index in range(1, 11)}


def test_positive_regression_replays_complete_authentic_chain_and_typed_provenance() -> None:
    fixture = _fixture()
    first = _run(fixture, fixture[9], budget=2)
    second = _run(fixture, fixture[9], budget=2)
    assert first.disposition is second.disposition is AttemptDisposition.TARGET_MATCH
    assert first.attempts[0].provenance is not None
    assert [item.stage for item in first.attempts[0].provenance.evidence_references] == ["M03_SOLVER", "M04_DIFFICULTY", "M05_QA"]
    assert first.attempts[0].provenance.digest() == second.attempts[0].provenance.digest()  # type: ignore[union-attr]
    assert AUTHENTIC_SOURCE_PATH.read_bytes() == b"scrubbots-r03-regression-source"


def test_negative_regression_rejects_unrelated_authentic_evidence_and_preserves_root_cycle_guards() -> None:
    parent, request, mutation, solver, difficulty, qa, solver_adapter, envelope, candidate, target, _, _ = _fixture()
    with pytest.raises(MutationContractError):
        adapt_m03_solver(dataclasses.replace(solver_adapter.producer, level_id="unrelated-child"), mutation)
    with pytest.raises(MutationContractError):
        provenance_from_authentic_validation(request, mutation, envelope, difficulty, solver_adapter, qa)  # type: ignore[arg-type]
    provenance = _run(_fixture(), target, budget=1).attempts[0].provenance
    assert provenance is not None
    ledger = ProvenanceLedger()
    ledger.register_root(LineageRootRegistration(provenance.lineage_root, provenance.parent))
    assert ledger.record(provenance) == provenance.digest()
    with pytest.raises(MutationContractError):
        ledger.record(dataclasses.replace(provenance, attempt_ordinal=1))
    a_identity = provenance.child
    b_identity = dataclasses.replace(a_identity, candidate_id="cycle-b", parent_candidate_id=a_identity.candidate_id)
    a_to_b = dataclasses.replace(provenance, parent=a_identity, child=b_identity, pre_state_digest=a_identity.state_digest, post_state_digest=b_identity.state_digest)
    ledger.record(a_to_b)
    b_to_a = dataclasses.replace(provenance, parent=b_identity, child=dataclasses.replace(a_identity, parent_candidate_id=b_identity.candidate_id), pre_state_digest=b_identity.state_digest, post_state_digest=a_identity.state_digest)
    with pytest.raises(MutationContractError):
        ledger.record(b_to_a)


def test_truthful_unavailable_safety_and_all_authentic_runner_terminals() -> None:
    fixture = _fixture()
    unavailable = _run(fixture, fixture[10], budget=1)
    assert unavailable.disposition is AttemptDisposition.INCONCLUSIVE
    assert select_authentic_target(fixture[10], (fixture[8],)).disposition.value == "INCONCLUSIVE"
    score = fixture[7].challenge_score or 0.0
    impossible = TypedChallengeTarget(100.0 if score < 100.0 else 0.0, 100.0 if score < 100.0 else 0.0, fixture[9].policy_digest, fixture[9].safety)
    assert _run(fixture, impossible, budget=2).disposition is AttemptDisposition.EXHAUSTED
    parent, request, mutation, _, _, _, _, _, candidate, target, _, record = fixture
    for disposition, expected in ((MutationDisposition.ERROR, AttemptDisposition.ERROR), (MutationDisposition.UNAVAILABLE, AttemptDisposition.UNAVAILABLE), (MutationDisposition.INAPPLICABLE, AttemptDisposition.REJECTED)):
        report = run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(1), request_factory=lambda current, ordinal, seed: request, engine=_StaticEngine(disposition), validator=lambda result: candidate, target=target, source_context=SourceLinkedMutationContext.establish(record))
        assert report.disposition is expected


def test_actual_matched_regeneration_route_has_same_workload_and_no_accounting_authority() -> None:
    fixture = _fixture()
    report = _run(fixture, fixture[9], budget=1)
    mutation_route = MutationAttemptRouteEvidence.from_attempt_report(report)
    result = GeneratorRouter().generate(GenerationRequest("EASY", fixture[1].seed, "MASK", width=20, height=20))
    regeneration_route = RegenerationRouteEvidence.from_generation_result(result, target=fixture[9], budget=report.budget)
    comparison = compare_efficiency_from_authentic_routes(mutation_route, regeneration_route)
    assert comparison.workload == mutation_route.workload
    assert comparison.mutation_cost is None and comparison.regenerate_cost is None
    assert regeneration_route.route_id != "UNAVAILABLE" and regeneration_route.route_version != "UNAVAILABLE"
    with pytest.raises(MutationContractError):
        TrustedAccountingEvidence.from_cost_usage(__import__("scrubbots_pixel_factory.semantic.qualification.models", fromlist=["CostUsageRecord"]).CostUsageRecord(provider_attempt_count=1))


def test_real_m05_post_check_rejects_source_change_and_palette_no_proxy_invariants_remain() -> None:
    fixture = _fixture()
    failed = _run(fixture, fixture[9], budget=1, mutate_source=True)
    assert failed.disposition is AttemptDisposition.ERROR
    assert [color.id for color in CANONICAL_PALETTE.colors] == [f"C{i:02d}" for i in range(1, 17)]
    assert CANONICAL_PALETTE.background.id == "BG01"
    assert CANONICAL_PALETTE.used_color_envelope == (3, 12)
    assert CANONICAL_PALETTE.difficulty_class_derived_from_color_count is False
