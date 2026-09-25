from __future__ import annotations

import pytest

from scrubbots_pixel_factory import (
    AttemptBudget,
    AttemptDisposition,
    AttemptProvenance,
    CANONICAL_M23_PREVIEW_AUTHORITY,
    ChallengeTarget,
    EvidenceDisposition,
    MutationCandidate,
    MutationContractError,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationRequest,
    derive_attempt_seed,
    evidence,
    revalidate_mutation,
    run_bounded_mutations,
)
from sb_lf07_r01_support import engine as concrete_engine, m39_authority


def _parent() -> MutationCandidate:
    return MutationCandidate.root("attempt-parent", {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 6, "booster": "+1_SLOT", "sixth_slot_state": "EMPTY", "live_work_on_sixth": 0}})


def _request(parent: MutationCandidate, ordinal: int, seed: int) -> MutationRequest:
    return MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1", operator_version="1", seed=seed, intent=MutationIntent.HARDEN, authority=m39_authority())


def _validate(mutation):
    solver = evidence("M03_SOLVER", EvidenceDisposition.SOLVED, mutation, {"status": "SOLVED"})
    difficulty = evidence("M04_DIFFICULTY", EvidenceDisposition.AVAILABLE, mutation, {"policy_version": "DIFFICULTY_V1", "challenge_score": 60.0})
    qa = evidence("M05_QA", EvidenceDisposition.PASS, mutation, {"structural": True})
    return revalidate_mutation(mutation, solver, difficulty, qa)


def test_success_before_limit_records_ordinal_seed_and_provenance() -> None:
    calls: list[int] = []
    engine = concrete_engine()
    report = run_bounded_mutations(_parent(), base_seed=70, budget=AttemptBudget(3), request_factory=lambda parent, ordinal, seed: (calls.append(ordinal) or _request(parent, ordinal, seed)), engine=engine, validator=_validate, target=ChallengeTarget(50, 70, "DIFFICULTY_V1"))
    assert report.disposition is AttemptDisposition.TARGET_MATCH
    assert len(report.attempts) == 1
    assert calls == [0]
    assert report.attempts[0].provenance is not None
    assert report.attempts[0].provenance.attempt_ordinal == 0
    assert report.attempts[0].effective_seed == derive_attempt_seed(70, 0)


def test_exact_limit_exhaustion_is_not_unsolvable_or_success() -> None:
    report = run_bounded_mutations(_parent(), base_seed=71, budget=AttemptBudget(2), request_factory=_request, engine=concrete_engine(), validator=_validate, target=ChallengeTarget(90, 100, "DIFFICULTY_V1"))
    assert report.disposition is AttemptDisposition.EXHAUSTED
    assert len(report.attempts) == 2
    assert report.selected is None
    assert all(record.mutation.disposition.value != "UNSOLVABLE" for record in report.attempts)


def test_invalid_budgets_fail_closed_and_seed_replay_is_stable() -> None:
    for value in (0, -1, 10001):
        with pytest.raises(MutationContractError):
            AttemptBudget(value)
    assert derive_attempt_seed(100, 3) == derive_attempt_seed(100, 3)
    with pytest.raises(MutationContractError):
        derive_attempt_seed(100, -1)


def test_signed64_overflow_is_rejected_and_non_applied_attempts_have_typed_provenance() -> None:
    with pytest.raises(MutationContractError):
        derive_attempt_seed(2**63 - 1, 1)
    record = AttemptProvenance(0, 17, "a" * 64, "candidate", MutationDisposition.ERROR, "canonical capability unavailable")
    assert record.mutation_disposition.value == "ERROR"
