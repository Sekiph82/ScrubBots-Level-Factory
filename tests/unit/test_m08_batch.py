from __future__ import annotations

import pytest

from scrubbots_pixel_factory import (
    BatchPlan,
    CandidateEvidence,
    LaneRequest,
    M08ContractError,
    build_handoff,
    review_summary,
    run_batch,
)
from scrubbots_pixel_factory.difficulty_analysis import LaneClass


def _evidence(candidate: str, lane: LaneClass = LaneClass.EASY) -> CandidateEvidence:
    values = {
        "m03_digest": "a" * 64, "m04_digest": "b" * 64, "m04_lane_digest": "c" * 64,
        "m05_digest": "d" * 64, "level_data_digest": "e" * 64, "logical_art_digest": "f" * 64,
        "source_provenance_digest": "1" * 64, "generation_request_digest": "2" * 64,
        "generation_result_digest": "3" * 64, "bundle_digest": "4" * 64,
    }
    return CandidateEvidence(candidate, lane, "ACCEPT", m04_disposition="ACCEPT", m05_disposition="ACCEPT", **values)


def test_deterministic_lane_cadence_counts_only_bound_evidence() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 1, 3), LaneRequest(LaneClass.HARD, 1, 2)), 11, "test")

    def produce(lane, ordinal, seed):
        if lane is LaneClass.EASY and ordinal == 0:
            return {"disposition": "ACCEPT", "evidence": _evidence("easy", lane)}
        if lane is LaneClass.HARD and ordinal == 0:
            return {"disposition": "ACCEPT", "evidence": _evidence("hard", lane)}
        return {"disposition": "REJECT"}

    first = run_batch(plan, produce)
    second = run_batch(plan, produce)
    assert first.status == "COMPLETE" and first.digest() == second.digest()
    assert first.statistics["accepted"] == 2


def test_wrong_lane_and_unavailable_never_increment_acceptance() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 1, 3),), 1, "x")
    calls = iter([
        {"disposition": "ACCEPT", "evidence": _evidence("wrong", LaneClass.HARD)},
        {"disposition": "UNAVAILABLE"},
        {"disposition": "INCONCLUSIVE"},
    ])
    result = run_batch(plan, lambda *_: next(calls))
    assert result.status == "EXHAUSTED"
    assert result.statistics["accepted"] == 0
    assert result.statistics["unavailable"] == 1 and result.statistics["inconclusive"] == 1


def test_duplicate_and_resume_plan_tamper_fail_closed() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 1, 2),), 2, "x")
    result = run_batch(plan, lambda *_: {"disposition": "ACCEPT", "evidence": _evidence("same")})
    assert result.statistics["accepted"] == 1
    resumed = run_batch(plan, lambda *_: {"disposition": "ACCEPT", "evidence": _evidence("other")}, history=result.entries)
    assert resumed.digest() == result.digest()
    other = BatchPlan((LaneRequest(LaneClass.EASY, 1, 2),), 3, "x")
    with pytest.raises(M08ContractError):
        run_batch(other, lambda *_: None, history=result.entries)


def test_owner_review_is_separate_and_handoff_requires_owner_accept() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 1, 1),), 4, "x")
    result = run_batch(plan, lambda *_: {"disposition": "ACCEPT", "evidence": _evidence("candidate")})
    pending = build_handoff(result, "candidate", [])
    assert pending["disposition"] == "NOT_OWNER_ACCEPTED"
    summary = review_summary(result, [{"candidate_id": "candidate", "disposition": "REJECT"}])
    assert summary["OWNER_REJECTED"] == 1 and result.statistics["accepted"] == 1
    ready = build_handoff(result, "candidate", [{"candidate_id": "candidate", "disposition": "ACCEPT", "review_id": "r1"}])
    assert ready["disposition"] == "READY" and "handoff_digest" in ready


def test_high_rejection_is_finite_and_terminal() -> None:
    plan = BatchPlan(tuple(LaneRequest(lane, 1, 100) for lane in LaneClass), 9, "stress")
    result = run_batch(plan, lambda *_: {"disposition": "REJECT"})
    assert result.status == "EXHAUSTED"
    assert sum(result.attempted.values()) == 400
    assert result.statistics["accepted"] == 0
