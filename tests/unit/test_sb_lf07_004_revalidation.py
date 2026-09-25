from __future__ import annotations

import pytest

from scrubbots_pixel_factory import (
    CANONICAL_M23_PREVIEW_AUTHORITY,
    EvidenceDisposition,
    MutationCandidate,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationRequest,
    MutationContractError,
    M03SolverEvidenceReceipt,
    M04DifficultyEvidenceReceipt,
    M05QAEvidenceReceipt,
    ValidationDisposition,
    evidence,
    revalidate_mutation,
    revalidate_mutation_from_typed_receipts,
)
from sb_lf07_r01_support import engine, m39_authority


def _mutation():
    parent = MutationCandidate.root("revalidate-parent", {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 6, "booster": "+1_SLOT", "sixth_slot_state": "EMPTY", "live_work_on_sixth": 0}})
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1", operator_version="1", seed=31, intent=MutationIntent.HARDEN, authority=m39_authority())
    result = engine().apply(request, parent)
    assert result.disposition is MutationDisposition.APPLIED
    return result


def _records(mutation, *, solver=EvidenceDisposition.SOLVED, difficulty=EvidenceDisposition.AVAILABLE, qa=EvidenceDisposition.PASS):
    return (
        evidence("M03_SOLVER", solver, mutation, {"status": solver.value}),
        evidence("M04_DIFFICULTY", difficulty, mutation, {"policy_version": "DIFFICULTY_V1", "challenge_score": 62.5, "lane": "HARD"}),
        evidence("M05_QA", qa, mutation, {"structural": True, "production": True}),
    )


def test_applied_mutation_requires_complete_child_evidence_chain() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    envelope = revalidate_mutation(mutation, solver, difficulty, qa)
    assert envelope.disposition is ValidationDisposition.ELIGIBLE
    assert envelope.child.state_digest == mutation.child.state_digest  # type: ignore[union-attr]
    assert envelope.challenge_score == 62.5


def test_unsolvable_inconclusive_and_unavailable_never_become_eligible() -> None:
    mutation = _mutation()
    for solver_status, expected in ((EvidenceDisposition.PROVEN_UNSOLVABLE, ValidationDisposition.REJECTED), (EvidenceDisposition.UNKNOWN_BOUND, ValidationDisposition.INCONCLUSIVE), (EvidenceDisposition.UNAVAILABLE, ValidationDisposition.UNAVAILABLE)):
        solver, difficulty, qa = _records(mutation, solver=solver_status)
        assert revalidate_mutation(mutation, solver, difficulty, qa).disposition is expected


def test_parent_acceptance_cannot_float_to_child_and_stale_evidence_fails_closed() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    stale_parent = type(solver)(solver.stage, solver.disposition, mutation.parent.state_digest, solver.request_digest, solver.parent_state_digest, solver.operator_id, solver.authority_digest, solver.payload)
    with pytest.raises(MutationContractError):
        revalidate_mutation(mutation, stale_parent, difficulty, qa)
    with pytest.raises(MutationContractError):
        revalidate_mutation(mutation, solver, type(difficulty)(difficulty.stage, difficulty.disposition, difficulty.child_state_digest, "0" * 64, difficulty.parent_state_digest, difficulty.operator_id, difficulty.authority_digest, difficulty.payload), qa)


def test_child_hash_and_stage_order_are_bound_not_caller_claims() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    with pytest.raises(MutationContractError):
        revalidate_mutation(mutation, difficulty, solver, qa)
    bad_solver = type(solver)(solver.stage, solver.disposition, "0" * 64, solver.request_digest, solver.parent_state_digest, solver.operator_id, solver.authority_digest, solver.payload)
    with pytest.raises(MutationContractError):
        revalidate_mutation(mutation, bad_solver, difficulty, qa)


def test_production_entry_point_requires_typed_m03_m04_m05_receipts() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    with pytest.raises(MutationContractError):
        revalidate_mutation_from_typed_receipts(mutation, solver, difficulty, qa)  # type: ignore[arg-type]
    typed_solver = M03SolverEvidenceReceipt("M03_SOLVER", "solver-evidence", "1", "1" * 64, solver)
    typed_difficulty = M04DifficultyEvidenceReceipt("M04_DIFFICULTY", "difficulty-evidence", "1", "2" * 64, difficulty)
    typed_qa = M05QAEvidenceReceipt("M05_QA", "qa-evidence", "1", "3" * 64, qa)
    envelope = revalidate_mutation_from_typed_receipts(mutation, typed_solver, typed_difficulty, typed_qa)
    assert envelope.disposition is ValidationDisposition.ELIGIBLE


def test_typed_receipt_rejects_forged_producer_stage_or_missing_score() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    with pytest.raises(MutationContractError):
        M03SolverEvidenceReceipt("M04_DIFFICULTY", "solver-evidence", "1", "1" * 64, solver)
    bad = type(difficulty)(difficulty.stage, difficulty.disposition, difficulty.child_state_digest, difficulty.request_digest, difficulty.parent_state_digest, difficulty.operator_id, difficulty.authority_digest, {"policy_version": "DIFFICULTY_V1"})
    with pytest.raises(MutationContractError):
        M04DifficultyEvidenceReceipt("M04_DIFFICULTY", "difficulty-evidence", "1", "2" * 64, bad)
