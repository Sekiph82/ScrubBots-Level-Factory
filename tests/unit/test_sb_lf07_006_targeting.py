from __future__ import annotations

import pytest

from scrubbots_pixel_factory import (
    CANONICAL_M23_PREVIEW_AUTHORITY,
    ChallengeTarget,
    EvidenceDisposition,
    MutationCandidate,
    MutationEngine,
    MutationIntent,
    MutationRequest,
    TargetDisposition,
    SafetyConstraintEvidence,
    TypedChallengeTarget,
    evidence,
    revalidate_mutation,
    select_target,
)
from scrubbots_pixel_factory import build_typed_target
from scrubbots_pixel_factory import AuthenticTargetCandidate, revalidate_mutation_from_authentic_adapters
from scrubbots_pixel_factory.mutation_targeting import select_authentic_target
from test_sb_lf07_004_revalidation import _authentic_chain
from sb_lf07_r01_support import engine, m39_authority


def _envelope(candidate_id: str, score: float, *, policy: str = "DIFFICULTY_V1", safe: bool = True, risk: object = True, include_proxies: bool = False):
    payload = {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 6, "booster": "+1_SLOT", "sixth_slot_state": "EMPTY", "live_work_on_sixth": 0}}
    if include_proxies:
        payload.update({"width": 20, "height": 20, "color_count": 3, "difficulty_label": "EASY"})
    parent = MutationCandidate.root(candidate_id, payload)
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1", operator_version="1", seed=61, intent=MutationIntent.HARDEN, authority=m39_authority())
    mutation = engine().apply(request, parent)
    solver = evidence("M03_SOLVER", EvidenceDisposition.SOLVED, mutation, {"status": "SOLVED"})
    difficulty = evidence("M04_DIFFICULTY", EvidenceDisposition.AVAILABLE, mutation, {"policy_version": policy, "challenge_score": score, "lane": "HARD", "load": safe, "risk": risk, "retention": safe})
    qa = evidence("M05_QA", EvidenceDisposition.PASS, mutation, {"structural": True, "production": True})
    return revalidate_mutation(mutation, solver, difficulty, qa)


def test_score_target_selects_only_in_range_and_uses_deterministic_tie_break() -> None:
    target = ChallengeTarget(50.0, 70.0, "DIFFICULTY_V1", ("load", "risk", "retention"))
    below, inside, above = _envelope("below", 49.9), _envelope("inside", 60.0), _envelope("above", 70.1)
    selected = select_target(target, (below, inside, above))
    assert selected.disposition is TargetDisposition.MATCH
    assert selected.candidate is inside
    tie_a, tie_b = _envelope("tie-a", 55.0), _envelope("tie-b", 65.0)
    first = select_target(target, (tie_a, tie_b))
    second = select_target(target, (tie_b, tie_a))
    assert first.selection_digest == second.selection_digest
    assert first.candidate is second.candidate


def test_missing_required_constraint_and_policy_drift_are_not_match() -> None:
    target = ChallengeTarget(50.0, 70.0, "DIFFICULTY_V1", ("load", "risk", "retention"))
    missing = _envelope("missing", 60.0, risk=None)
    wrong_policy = _envelope("policy", 60.0, policy="DIFFICULTY_V0")
    assert select_target(target, (missing,)).disposition is TargetDisposition.INCONCLUSIVE
    assert select_target(target, (wrong_policy,)).disposition is TargetDisposition.INCONCLUSIVE


def test_forbidden_metadata_proxies_do_not_drive_selection() -> None:
    target = ChallengeTarget(50.0, 70.0, "DIFFICULTY_V1")
    candidate = _envelope("proxy", 60.0, include_proxies=True)
    assert select_target(target, (candidate,)).disposition is TargetDisposition.MATCH


def test_no_acceptable_candidate_is_truthful_no_match() -> None:
    target = ChallengeTarget(80.0, 90.0, "DIFFICULTY_V1")
    assert select_target(target, (_envelope("none", 60.0),)).disposition is TargetDisposition.NO_MATCH


def test_typed_target_binds_policy_digest_and_all_safety_dimensions() -> None:
    policy_digest = "a" * 64
    safety = SafetyConstraintEvidence("m04-safety", "1", policy_digest, True, True, True, "b" * 64)
    target = TypedChallengeTarget(50.0, 70.0, policy_digest, safety)
    assert target.digest() != policy_digest


def test_typed_target_rejects_policy_drift_and_untyped_safety_values() -> None:
    with pytest.raises(Exception):
        SafetyConstraintEvidence("m04-safety", "1", "a" * 64, True, "true", True, "b" * 64)  # type: ignore[arg-type]
    safety = SafetyConstraintEvidence("m04-safety", "1", "a" * 64, True, True, True, "b" * 64)
    with pytest.raises(Exception):
        TypedChallengeTarget(50.0, 70.0, "c" * 64, safety)


def test_production_typed_target_builder_rejects_legacy_generic_records() -> None:
    envelope = _envelope("typed-target", 60.0)
    with pytest.raises(Exception):
        build_typed_target(50.0, 70.0, envelope.difficulty, envelope.qa)  # type: ignore[arg-type]


def test_authentic_target_uses_stable_m04_policy_and_never_synthesizes_safety_truth() -> None:
    _, _, mutation, _, _, _, _, solver_adapter, difficulty_adapter, qa_adapter = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver_adapter, difficulty_adapter, qa_adapter)
    candidate = AuthenticTargetCandidate(envelope, solver_adapter, difficulty_adapter, qa_adapter)
    target = build_typed_target(0.0, 100.0, difficulty_adapter, qa_adapter)
    assert target.safety.load_ok is False
    assert target.safety.risk_ok is False
    assert target.safety.retention_ok is False
    assert target.safety.version == "UNAVAILABLE"
    assert target.policy_digest != difficulty_adapter.producer_digest
    selection = select_authentic_target(target, (candidate,))
    assert selection.disposition is TargetDisposition.INCONCLUSIVE
