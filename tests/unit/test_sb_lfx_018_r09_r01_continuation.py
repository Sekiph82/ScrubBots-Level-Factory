from __future__ import annotations

import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory.supply_pipeline import r09_campaign
from scrubbots_pixel_factory.supply_pipeline import r09_solver_attempts as r09


ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = r09_campaign.SOURCE_SHA256
GAME_SHA = r09_campaign.PINNED_MAIN_SHA
PREDECESSOR = ROOT / "level_factory" / "output" / "r09-capped-solver" / f"{SOURCE_SHA}-{GAME_SHA}"


def test_original_blocked_receipts_are_sha_bound_and_leave_all_six_native_calls():
    proof = r09_campaign._historical_r09_predecessor_proof(ROOT)
    assert proof["predecessor_summary_sha256"] == "211a5abe7b9b95effce6fcdb6f7a6dc914eadade3f07bcc4f9cf0517a5f78b43"
    assert proof["predecessor_attempt_sha256"] == "e0a833dee3beaec3dc5486adde6326b7bdd8fd7f3c9a6f6616597e57cbc025a4"
    assert proof["logical_attempts_run"] == 1
    assert proof["native_primary_calls_consumed"] == 0
    assert proof["native_load_check_calls_consumed"] == 0
    assert proof["remaining_authorized_primary_calls"] == 6
    assert min(r09_campaign.MAX_PRIMARY_ATTEMPTS, proof["remaining_authorized_primary_calls"]) == 6
    assert proof["predecessor_job_entry_count"] == 0


def test_missing_or_ambiguous_predecessor_fails_closed():
    with pytest.raises(r09.R09Blocked, match="historical predecessor is unreadable"):
        r09_campaign._historical_r09_predecessor_proof(ROOT / "missing-r09-predecessor")

    summary = json.loads((PREDECESSOR / "summary.json").read_text(encoding="utf-8"))
    attempt = json.loads((PREDECESSOR / "attempt-01.json").read_text(encoding="utf-8"))
    attempt["process"] = {"native_solve_started": False}
    with pytest.raises(r09.R09Blocked, match="zero native starts"):
        r09_campaign._validate_predecessor_records(summary, attempt, PREDECESSOR, 0)
    attempt["process"] = None
    summary["primary_invocations"] = 1
    with pytest.raises(r09.R09Blocked, match="zero native starts"):
        r09_campaign._validate_predecessor_records(summary, attempt, PREDECESSOR, 0)


def test_original_six_candidate_order_scores_and_plan_hashes_are_required():
    expected = r09_campaign.EXPECTED_R09_RANKED_PLANS
    ranked = [
        {"id": candidate_id, "score": score, "plan_sha256": plan_sha}
        for candidate_id, score, plan_sha in expected
    ]
    assert r09_campaign._assert_original_queue_identity(ranked) is ranked
    with pytest.raises(r09.R09Blocked, match="R09_QUEUE_IDENTITY_UNVERIFIED"):
        r09_campaign._assert_original_queue_identity(list(reversed(ranked)))


def test_continuation_has_exact_separate_path_and_rejects_existing_output():
    continuation_path = ROOT / "level_factory" / "output" / f"r09-r01-continuation-{SOURCE_SHA}-{GAME_SHA}"
    assert continuation_path != PREDECESSOR
    with pytest.raises(r09.R09Blocked, match="already exists"):
        r09_campaign._assert_continuation_output_available(PREDECESSOR)


def test_tuple_plan_is_validated_and_marshaled_as_native_batch_objects():
    candidate = {"id": "one", "columns": [[(1, 2)], [(0, 3)], [(1, 4)]]}
    assert r09.serialize_bridge_candidate(candidate) == {
        "id": "one",
        "columns": [[{"color": 1, "count": 2}], [{"color": 0, "count": 3}], [{"color": 1, "count": 4}]],
    }
    with pytest.raises(r09.R09Blocked, match="exactly three"):
        r09.serialize_bridge_candidate({"id": "bad", "columns": [[(0, 1)]]})
    with pytest.raises(r09.R09Blocked, match="color/count"):
        r09.serialize_bridge_candidate({"id": "bad", "columns": [[(-1, 1)], [(0, 1)], [(0, 1)]]})


def test_local_ready_requires_full_independent_native_load_check_evidence():
    ready = {
        "state": "READY", "solver_status": "SOLVED", "solver_invocations": 1,
        "solver_runner": {"invocation_count": 1, "process_invocation_count": 1,
                          "native_solve_started": True, "native_solve_completed": True,
                          "elapsed_seconds": 12.5},
        "solver": {"status": "SOLVED", "replay": {"ok": True, "solved": True, "finalActive": 0}},
        "difficulty_v1": {"ok": True}, "verification": {"all_ok": True},
        "levelLoaderPass": True, "productionValidatorPass": True, "supplyPlanLoaderPass": True,
    }
    assert r09._load_check_proves_ready(ready)
    for key, value in (("state", "UNAVAILABLE"), ("solver", {"status": "SOLVED", "replay": {"ok": False}}),
                       ("difficulty_v1", None), ("verification", {"all_ok": False}),
                       ("supplyPlanLoaderPass", False)):
        failed = dict(ready)
        failed[key] = value
        assert not r09._load_check_proves_ready(failed)


def test_primary_call_budget_stays_six_and_each_call_is_hard_capped():
    assert r09.MAX_PRIMARY_ATTEMPTS == 6
    assert r09.MAX_NATIVE_TIMEOUT_SECONDS == 90.0
    assert r09.MAX_NATIVE_VISITED == 25_000
    assert len({item[2] for item in r09_campaign.EXPECTED_R09_RANKED_PLANS}) == 6
