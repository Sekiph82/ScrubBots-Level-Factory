from __future__ import annotations

from scrubbots_pixel_factory import (
    CANONICAL_M23_PREVIEW_AUTHORITY,
    ChallengeTarget,
    EvidenceDisposition,
    MutationCandidate,
    MutationEngine,
    MutationIntent,
    MutationRequest,
    TargetDisposition,
    evidence,
    revalidate_mutation,
    select_target,
)


def _envelope(candidate_id: str, score: float, *, policy: str = "DIFFICULTY_V1", safe: bool = True, risk: object = True, include_proxies: bool = False):
    payload = {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 5}}
    if include_proxies:
        payload.update({"width": 20, "height": 20, "color_count": 3, "difficulty_label": "EASY"})
    parent = MutationCandidate.root(candidate_id, payload)
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PREVIEW_DEPTH_HARDEN_V1", operator_version="1", seed=61, intent=MutationIntent.HARDEN, authority=CANONICAL_M23_PREVIEW_AUTHORITY)
    mutation = MutationEngine().apply(request, parent)
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
