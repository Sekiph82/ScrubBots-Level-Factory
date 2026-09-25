from __future__ import annotations

import pytest
from dataclasses import replace
import hashlib
import json

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
    MutationRegistry,
    derive_attempt_seed,
    evidence,
    revalidate_mutation,
    run_bounded_mutations,
    AuthenticTargetCandidate,
    AttemptReport,
    SafetyConstraintEvidence,
    TypedChallengeTarget,
    revalidate_mutation_from_authentic_adapters,
    build_typed_target,
    run_authentic_bounded_mutations,
)
from scrubbots_pixel_factory.mutation_base import MutationResult
from test_sb_lf07_004_revalidation import _authentic_chain
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
    assert report.disposition is AttemptDisposition.REJECTED
    assert len(report.attempts) == 2
    assert report.selected is None
    assert all(record.attempt_provenance is not None for record in report.attempts)
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


def test_runner_records_non_applied_provenance_and_returns_error() -> None:
    parent = _parent()
    request_factory = lambda candidate, ordinal, seed: _request(candidate, ordinal, seed)
    report = run_bounded_mutations(parent, base_seed=90, budget=AttemptBudget(1), request_factory=request_factory, engine=MutationEngine(MutationRegistry()), validator=_validate, target=ChallengeTarget(50, 70, "DIFFICULTY_V1"))
    assert report.disposition is AttemptDisposition.REJECTED
    assert report.attempts[0].attempt_provenance is not None
    assert report.attempts[0].mutation.disposition is MutationDisposition.INAPPLICABLE


def _authentic_runner_fixture():
    parent, request, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    candidate = AuthenticTargetCandidate(envelope, solver, difficulty, qa)
    base_target = build_typed_target(0.0, 100.0, difficulty, qa)
    safety = SafetyConstraintEvidence("scrubbots-m07-safety-availability", "1", base_target.policy_digest, True, True, True, qa.producer_digest)
    return parent, request, mutation, candidate, TypedChallengeTarget(0.0, 100.0, base_target.policy_digest, safety), base_target


class _StaticEngine:
    def __init__(self, disposition: MutationDisposition, applied=None):
        self.disposition = disposition
        self.applied = applied

    def apply(self, request, parent):
        if self.disposition is MutationDisposition.APPLIED:
            return self.applied
        return MutationResult(self.disposition, request.digest(), parent.identity, None, parent.state_digest, None, None, f"terminal {self.disposition.value}", request.operator_id, request.operator_version, request.authority)


def _run_authentic(parent, request, mutation, candidate, target, *, budget=2, engine=None, calls=None):
    def factory(current, ordinal, seed):
        if calls is not None:
            calls.append(("request", ordinal))
        return request

    def validator(result):
        if calls is not None:
            calls.append(("validator", len(calls)))
        return candidate

    return run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(budget), request_factory=factory, engine=engine or _StaticEngine(MutationDisposition.APPLIED, mutation), validator=validator, target=target, source_context=type("SourcePass", (), {"passed": True})())


def test_authentic_runner_covers_all_terminal_dispositions_and_precedence() -> None:
    parent, request, mutation, candidate, matching_target, unavailable_target = _authentic_runner_fixture()
    assert _run_authentic(parent, request, mutation, candidate, matching_target, budget=3).disposition is AttemptDisposition.TARGET_MATCH
    assert _run_authentic(parent, request, mutation, candidate, unavailable_target, budget=1).disposition is AttemptDisposition.INCONCLUSIVE
    score = candidate.envelope.challenge_score or 0.0
    lower = 100.0 if score < 100.0 else 0.0
    exhausted_target = TypedChallengeTarget(lower, 100.0 if lower == 100.0 else 0.0, matching_target.policy_digest, matching_target.safety)
    assert _run_authentic(parent, request, mutation, candidate, exhausted_target, budget=2).disposition is AttemptDisposition.EXHAUSTED
    assert _run_authentic(parent, request, mutation, candidate, matching_target, budget=1, engine=_StaticEngine(MutationDisposition.ERROR)).disposition is AttemptDisposition.ERROR
    assert _run_authentic(parent, request, mutation, candidate, matching_target, budget=1, engine=_StaticEngine(MutationDisposition.UNAVAILABLE)).disposition is AttemptDisposition.UNAVAILABLE
    assert _run_authentic(parent, request, mutation, candidate, matching_target, budget=1, engine=_StaticEngine(MutationDisposition.INAPPLICABLE)).disposition is AttemptDisposition.REJECTED


def test_authentic_runner_stops_at_exact_limit_and_replays_deterministically() -> None:
    parent, request, mutation, candidate, matching_target, _ = _authentic_runner_fixture()
    calls: list[tuple[str, int]] = []
    first = _run_authentic(parent, request, mutation, candidate, matching_target, budget=1, calls=calls)
    second = _run_authentic(parent, request, mutation, candidate, matching_target, budget=1)
    assert len(first.attempts) == 1
    assert [kind for kind, _ in calls] == ["request", "validator"]
    assert first.attempts[0].provenance is not None
    assert first.attempts[0].provenance.digest() == second.attempts[0].provenance.digest()  # type: ignore[union-attr]
