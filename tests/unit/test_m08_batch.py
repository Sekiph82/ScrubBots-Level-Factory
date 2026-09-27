from __future__ import annotations

from dataclasses import replace
import hashlib

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
    verify_artifact_set,
)
from scrubbots_pixel_factory.difficulty_analysis import LaneClass


def _evidence(candidate: str, lane: LaneClass = LaneClass.EASY) -> CandidateEvidence:
    raw = {
        "m03_digest": f"m03:{candidate}".encode(),
        "m04_digest": f"m04:{candidate}".encode(),
        "m04_lane_digest": f"lane:{candidate}".encode(),
        "m05_digest": f"m05:{candidate}".encode(),
        "level_data_digest": f"level:{candidate}".encode(),
        "logical_art_digest": f"art:{candidate}".encode(),
        "source_provenance_digest": f"source:{candidate}".encode(),
        "generation_request_digest": f"request:{candidate}".encode(),
        "generation_result_digest": f"result:{candidate}".encode(),
        "generation_metadata_digest": f"generation:{candidate}".encode(),
        "bundle_digest": f"bundle:{candidate}".encode(),
    }
    values = {
        **{key: hashlib.sha256(value).hexdigest() for key, value in raw.items()},
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


def _artifact_map(evidence: CandidateEvidence) -> dict[str, bytes]:
    candidate = evidence.candidate_id
    return {
        evidence.level_data_ref: f"level:{candidate}".encode(),
        evidence.logical_art_ref: f"art:{candidate}".encode(),
        evidence.bundle_ref: f"bundle:{candidate}".encode(),
        evidence.source_provenance_ref: f"source:{candidate}".encode(),
        evidence.m03_ref: f"m03:{candidate}".encode(),
        evidence.m04_ref: f"m04:{candidate}".encode(),
        evidence.m05_ref: f"m05:{candidate}".encode(),
        evidence.generation_ref: f"generation:{candidate}".encode(),
    }


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


def test_artifact_set_verifies_exact_canonical_bytes_without_reencoding() -> None:
    evidence = _evidence("bytes")
    artifacts = {
        evidence.level_data_ref: b"level",
        evidence.logical_art_ref: b"art",
        evidence.bundle_ref: b"bundle",
        evidence.source_provenance_ref: b"source",
        evidence.m03_ref: b"m03",
        evidence.m04_ref: b"m04",
        evidence.m05_ref: b"m05",
        evidence.generation_ref: b"generation",
    }
    evidence = replace(evidence, level_data_digest=__import__("hashlib").sha256(b"level").hexdigest(), logical_art_digest=__import__("hashlib").sha256(b"art").hexdigest(), bundle_digest=__import__("hashlib").sha256(b"bundle").hexdigest(), source_provenance_digest=__import__("hashlib").sha256(b"source").hexdigest(), m03_digest=__import__("hashlib").sha256(b"m03").hexdigest(), m04_digest=__import__("hashlib").sha256(b"m04").hexdigest(), m05_digest=__import__("hashlib").sha256(b"m05").hexdigest(), generation_metadata_digest=__import__("hashlib").sha256(b"generation").hexdigest())
    checked = verify_artifact_set(evidence, artifacts)
    assert checked["disposition"] == "ACCEPT" and len(checked["verified_references"]) == 8
    with pytest.raises(M08ContractError):
        verify_artifact_set(evidence, {**artifacts, evidence.m05_ref: b"tampered"})


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
    artwork_digest = result.entries[0].evidence.logical_art_digest
    reject = {"candidate_id": "candidate", "artwork_sha256": artwork_digest, "disposition": "REJECT", "review_id": "review-1"}
    accept = {"candidate_id": "candidate", "artwork_sha256": artwork_digest, "disposition": "ACCEPT", "review_id": "review-2"}
    summary = review_summary(result, [reject, accept])
    assert summary["OWNER_ACCEPTED"] == 1 and result.statistics["accepted"] == 1
    ready = build_handoff(result, "candidate", [reject, accept], artifacts=_artifact_map(result.entries[0].evidence))
    assert ready["disposition"] == "READY" and "handoff_digest" in ready
    assert build_handoff(result, "candidate", [reject, accept])["disposition"] == "UNAVAILABLE"
    assert build_handoff(result, "candidate", [{**accept, "artwork_sha256": "0" * 64}], artifacts=_artifact_map(result.entries[0].evidence))["disposition"] == "NOT_OWNER_ACCEPTED"
    assert review_summary(result, [accept, reject]) == review_summary(result, [reject, accept])
    assert review_summary(result, [accept, dict(accept)])["INVALID_REVIEW_EVIDENCE"] == 1


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
