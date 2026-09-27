from __future__ import annotations

from dataclasses import replace

import pytest

from scrubbots_pixel_factory import (
    AttemptRecord,
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
        "m03_digest": "a" * 64,
        "m04_digest": "b" * 64,
        "m04_lane_digest": "c" * 64,
        "m05_digest": "d" * 64,
        "level_data_digest": "e" * 64,
        "logical_art_digest": "f" * 64,
        "source_provenance_digest": "1" * 64,
        "generation_request_digest": "2" * 64,
        "generation_result_digest": "3" * 64,
        "generation_metadata_digest": "4" * 64,
        "bundle_digest": "5" * 64,
        "level_data_ref": "level-data/" + candidate + ".json",
        "logical_art_ref": "art/" + candidate + ".png",
        "bundle_ref": "bundles/" + candidate,
        "source_provenance_ref": "provenance/" + candidate + ".json",
        "m03_ref": "evidence/m03-" + candidate + ".json",
        "m04_ref": "evidence/m04-" + candidate + ".json",
        "m05_ref": "evidence/m05-" + candidate + ".json",
        "generation_ref": "generation/" + candidate + ".json",
    }
    return CandidateEvidence(candidate, lane, "ACCEPT", m04_disposition="ACCEPT", m05_disposition="ACCEPT", **values)


def test_deterministic_ordered_lane_cadence_counts_only_bound_evidence() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 1, 3), LaneRequest(LaneClass.HARD, 1, 2)), 11, "test")

    def produce(lane: LaneClass, ordinal: int, seed: int):
        if ordinal == 0:
            return {"disposition": "ACCEPT", "evidence": _evidence(lane.value.lower(), lane)}
        return {"disposition": "REJECT"}

    first = run_batch(plan, produce)
    second = run_batch(plan, produce)
    assert first.status == "COMPLETE"
    assert first.digest() == second.digest()
    assert first.statistics == {"accepted": 2, "duplicate": 0, "error": 0, "generated": 2, "inconclusive": 0, "rejected": 0, "unavailable": 0}
    assert list(first.attempted) == [LaneClass.EASY, LaneClass.HARD]


def test_wrong_lane_and_missing_m03_m05_evidence_fail_closed() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 1, 3),), 1, "x")
    calls = iter([
        {"disposition": "ACCEPT", "evidence": _evidence("wrong", LaneClass.HARD)},
        {"disposition": "UNAVAILABLE"},
        {"disposition": "INCONCLUSIVE"},
    ])
    result = run_batch(plan, lambda *_: next(calls))
    assert result.status == "EXHAUSTED"
    assert result.statistics["accepted"] == 0
    assert result.statistics["rejected"] == 1
    assert result.statistics["unavailable"] == 1 and result.statistics["inconclusive"] == 1
    with pytest.raises(M08ContractError):
        replace(_evidence("bad"), m05_disposition="UNAVAILABLE")


def test_duplicate_ids_and_exact_resume_do_not_redo_accepted_work() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 2, 4),), 2, "x")
    result = run_batch(plan, lambda _lane, ordinal, _seed: {"disposition": "ACCEPT", "evidence": _evidence("same" if ordinal < 2 else f"other-{ordinal}")})
    assert result.status == "COMPLETE"
    assert result.statistics["duplicate"] == 1
    calls: list[int] = []
    resumed = run_batch(plan, lambda _lane, ordinal, _seed: calls.append(ordinal) or {"disposition": "REJECT"}, history=result.attempts)
    assert calls == []
    assert resumed.digest() == result.digest()


def test_resume_plan_seed_budget_or_history_tamper_fails_closed() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 1, 2),), 2, "x")
    result = run_batch(plan, lambda *_: {"disposition": "ACCEPT", "evidence": _evidence("candidate")})
    other = BatchPlan((LaneRequest(LaneClass.EASY, 1, 2),), 3, "x")
    with pytest.raises(M08ContractError):
        run_batch(other, lambda *_: None, history=result.entries)
    with pytest.raises(M08ContractError):
        run_batch(plan, lambda *_: None, history=(AttemptRecord(LaneClass.EASY, 1, "REJECT"),))
    tampered = result.as_dict()
    tampered["plan"]["root_seed"] = 9
    with pytest.raises(M08ContractError):
        type(result).from_dict(tampered)


def test_artifact_contract_requires_safe_refs_and_optional_pairing() -> None:
    with pytest.raises(M08ContractError):
        replace(_evidence("unsafe"), bundle_ref="../escape")
    with pytest.raises(M08ContractError):
        replace(_evidence("unpaired"), preview_digest="a" * 64)


def test_manifest_round_trip_and_cross_candidate_tamper_fail_closed() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 1, 1),), 4, "x")
    result = run_batch(plan, lambda *_: {"disposition": "ACCEPT", "evidence": _evidence("candidate")})
    assert type(result).from_dict(result.as_dict()).digest() == result.digest()
    tampered = result.as_dict()
    tampered["accepted_entries"][0]["evidence"]["logical_art_digest"] = "9" * 64
    with pytest.raises(M08ContractError):
        type(result).from_dict(tampered)


def test_owner_review_summary_is_separate_and_handoff_requires_latest_accept() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 1, 1),), 4, "x")
    result = run_batch(plan, lambda *_: {"disposition": "ACCEPT", "evidence": _evidence("candidate")})
    pending = build_handoff(result, "candidate", [])
    assert pending["disposition"] == "NOT_OWNER_ACCEPTED"
    reject = {"candidate_id": "candidate", "artwork_sha256": "f" * 64, "disposition": "REJECT", "review_id": "review-1"}
    accept = {"candidate_id": "candidate", "artwork_sha256": "f" * 64, "disposition": "ACCEPT", "review_id": "review-2"}
    summary = review_summary(result, [reject, accept])
    assert summary["OWNER_ACCEPTED"] == 1 and result.statistics["accepted"] == 1
    ready = build_handoff(result, "candidate", [reject, accept])
    assert ready["disposition"] == "READY" and "handoff_digest" in ready
    assert build_handoff(result, "candidate", [{**accept, "artwork_sha256": "0" * 64}])["disposition"] == "NOT_OWNER_ACCEPTED"


def test_high_rejection_is_finite_one_lane_can_exhaust_while_another_completes() -> None:
    plan = BatchPlan(tuple(LaneRequest(lane, 1, 100) for lane in LaneClass), 9, "stress")

    def produce(lane: LaneClass, ordinal: int, _seed: int):
        if lane is LaneClass.HARD and ordinal == 99:
            return {"disposition": "ACCEPT", "evidence": _evidence("late-hard", lane)}
        return {"disposition": "REJECT"}

    result = run_batch(plan, produce)
    assert result.status == "EXHAUSTED"
    assert sum(result.attempted.values()) == 400
    assert result.statistics["accepted"] == 1
    assert result.statistics["generated"] == sum(result.statistics[key] for key in ("accepted", "rejected", "duplicate", "unavailable", "inconclusive", "error"))


def test_interruption_resume_after_rejection_is_bounded_and_deterministic() -> None:
    plan = BatchPlan((LaneRequest(LaneClass.EASY, 1, 10),), 10, "resume")

    def produce(_lane: LaneClass, ordinal: int, _seed: int):
        return {"disposition": "ACCEPT", "evidence": _evidence("late", LaneClass.EASY)} if ordinal == 9 else {"disposition": "REJECT"}

    partial = run_batch(plan, produce, max_total_attempts=5)
    assert partial.status == "PARTIAL" and len(partial.attempts) == 5
    complete = run_batch(plan, produce, history=partial.attempts)
    assert complete.status == "COMPLETE" and len(complete.attempts) == 10
    assert run_batch(plan, produce, history=complete.attempts).digest() == complete.digest()
