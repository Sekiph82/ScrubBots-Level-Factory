from __future__ import annotations

import itertools
import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory.supply_pipeline.campaign_builder import CampaignError, _assignment, build_campaign_plan


def _authority():
    return {
        "schema": "scrubbots-level-progression/v1", "version": 1, "cadenceLength": 1,
        "cadence": [{"slot": 1, "class": "EASY", "role": "recovery", "modifier": 0, "noveltyTarget": 0}],
        "lanes": {"EASY": {"base": 50, "growth": 0}}, "progression": {"tauCycles": 20},
        "challengeTolerance": {"preferredWhenPoolIsLarge": 2, "defaultPlusMinus": 3.5, "neverForceLabelOutsidePlusMinus": 5},
        "recoveryGuards": [],
        "_production_envelope": {"min_dimension": 20, "max_dimension": 59, "min_colors": 3, "max_colors": 12},
    }


def _pool(scores, *, profiles=None):
    profiles = profiles or ["BALANCED"] * len(scores)
    return [{"candidate_id": f"level-{i:03d}", "challenge_score": score, "difficulty_class": "EASY", "dominant_profile": profiles[i], "challenge_vector": [0.1] * 7, "width": 20 + i % 40, "height": 20, "used_colors": ["C01", "C02", "C03"], "palette": ["C01", "C02", "C03"], "signature": {"paletteSet": ["C01", "C02", "C03"], "dimensions": [20 + i % 40, 20], "challengeVector": [0.1] * 7}} for i, score in enumerate(scores)]


def _tail(order, profile, vector=None, *, slot=1, score=50):
    vector = vector or [0.1] * 7
    return {"order": order, "candidate_id": f"existing-{order}", "challenge_score": score, "dominant_profile": profile, "official_profile": {"dominant": profile}, "challenge_vector": vector, "slot": slot, "width": 20, "height": 20, "palette": ["C01", "C02", "C03"], "signature": {"dimensions": [20, 20], "paletteSet": ["C01", "C02", "C03"], "challengeVector": vector, "dominantProfile": profile}}


def _set_vector(candidate, vector):
    candidate["challenge_vector"] = vector
    candidate["signature"]["challengeVector"] = vector


def test_hungarian_global_assignment_matches_bruteforce_small_pool():
    costs = [[4, 1, 3, 99], [2, 0, 5, 99], [3, 2, 2, 99]]
    assignment = _assignment(costs)
    actual = sum(costs[i][j] for i, j in enumerate(assignment))
    expected = min(sum(costs[i][j] for i, j in enumerate(cols)) for cols in itertools.permutations(range(4), 3))
    assert actual == expected


def test_plan_is_deterministic_hard_tolerance_tier_and_shortage_is_reported():
    catalog = {"schema": "scrubbots.production_catalog.v1", "entries": []}
    pool = _pool([51, 54, 60])
    one = build_campaign_plan(catalog=catalog, authority=_authority(), pool=pool, k=3)
    two = build_campaign_plan(catalog=catalog, authority=_authority(), pool=pool, k=3)
    assert one == two
    assert one["plan_hash"] == two["plan_hash"]
    assert one["publishable_prefix"] == [1, 2]
    assert [row["chosen_id"] for row in one["slots"]] == ["level-000", "level-001", None]
    assert [row["tier"] for row in one["slots"][:2]] == [0, 2]
    assert one["shortages"][0]["n"] == 3
    assert one["shortages"][0]["allowed_range"] == [45.0, 55.0]
    assert all(abs(float(row["D"]) - float(row["target"])) <= 5 for row in one["slots"] if row["D"] is not None)


def test_class_mismatch_and_invalid_owner_lock_fail_closed():
    pool = _pool([50]); pool[0]["difficulty_class"] = "MEDIUM"
    plan = build_campaign_plan(catalog={"entries": []}, authority=_authority(), pool=pool, k=1)
    assert plan["slots"][0]["chosen_id"] is None
    with pytest.raises(CampaignError, match="hard-tolerance eligibility"):
        build_campaign_plan(catalog={"entries": []}, authority=_authority(), pool=_pool([60]), k=1, locks={1: "level-000"})


def test_default_tolerance_tier_is_reported():
    plan = build_campaign_plan(catalog={"entries": []}, authority=_authority(), pool=_pool([53]), k=1)
    assert plan["slots"][0]["delta"] == 3
    assert plan["slots"][0]["tier"] == 1


@pytest.mark.parametrize("field,value", [
    ("preferredWhenPoolIsLarge", None), ("preferredWhenPoolIsLarge", True),
    ("defaultPlusMinus", "3.5"), ("neverForceLabelOutsidePlusMinus", float("nan")),
    ("neverForceLabelOutsidePlusMinus", -1),
])
def test_missing_or_malformed_runtime_tolerance_fails_closed(field, value):
    authority = _authority()
    if value is None:
        authority["challengeTolerance"].pop(field)
    else:
        authority["challengeTolerance"][field] = value
    with pytest.raises(CampaignError, match="challengeTolerance"):
        build_campaign_plan(catalog={"entries": []}, authority=authority, pool=_pool([50]), k=1)


def test_runtime_tolerance_order_must_be_preferred_default_hard():
    authority = _authority()
    authority["challengeTolerance"] = {"preferredWhenPoolIsLarge": 4, "defaultPlusMinus": 3.5, "neverForceLabelOutsidePlusMinus": 5}
    with pytest.raises(CampaignError, match="preferred <= default <= hard"):
        build_campaign_plan(catalog={"entries": []}, authority=authority, pool=_pool([50]), k=1)


@pytest.mark.parametrize("guard,order,history", [
    ({"fromSlot": 1, "toSlot": 2, "minimumChallengeDrop": 10}, 1, [_tail(1, "COLOR", slot=1, score=80)]),
    ({"fromSlot": 2, "toNextCycleSlot": 1, "minimumChallengeDrop": 10}, 2, [_tail(1, "COLOR", slot=1, score=50), _tail(2, "ROUTE", slot=2, score=100)]),
])
def test_recovery_profile_targets_are_derived_from_runtime_guard_fields(guard, order, history):
    authority = _authority()
    authority["cadenceLength"] = 2
    authority["cadence"] = [{"slot": 1, "class": "EASY", "role": "regular", "modifier": 30, "noveltyTarget": 0}, {"slot": 2, "class": "EASY", "role": "recovery", "modifier": -30, "noveltyTarget": 0}]
    authority["recoveryGuards"] = [guard]
    catalog = {"entries": [{"order": n, "id": f"existing-{n}"} for n in range(1, order + 1)]}
    candidate = _pool([20 if order == 1 else 80])[0]
    plan = build_campaign_plan(catalog=catalog, authority={**authority, "_catalog_tail": history}, pool=[candidate], k=1)
    assert plan["slots"][0]["slot"] == (2 if order == 1 else 1)
    assert plan["slots"][0]["checks"]["recovery_profile_target_slot"] is True


def test_profile_limit_and_manual_lock_revalidation():
    authority = _authority()
    profiles = ["FLOW", "FLOW", "FLOW"]
    pool = _pool([50, 50, 50], profiles=profiles)
    plan = build_campaign_plan(catalog={"entries": []}, authority=authority, pool=pool, k=3)
    assert plan["slots"][2]["chosen_id"] is None
    with pytest.raises(CampaignError, match="sequence constraint"):
        build_campaign_plan(catalog={"entries": []}, authority=authority, pool=pool, k=3, locks={3: "level-002"})


def test_existing_two_level_profile_run_forces_first_new_level_to_reassign():
    authority = _authority()
    authority["_catalog_tail"] = [_tail(9, "FLOW"), _tail(10, "FLOW")]
    catalog = {"entries": [{"order": 9, "id": "existing-9"}, {"order": 10, "id": "existing-10"}]}
    pool = _pool([50, 50], profiles=["FLOW", "COLOR"])
    plan = build_campaign_plan(catalog=catalog, authority=authority, pool=pool, k=1)
    assert plan["slots"][0]["chosen_id"] == "level-001"
    assert plan["slots"][0]["checks"]["profile_run_ok"] is True


def test_profile_two_positions_back_does_not_break_a_nonconsecutive_flow_history():
    authority = _authority()
    authority["_catalog_tail"] = [_tail(9, "FLOW"), _tail(10, "COLOR")]
    catalog = {"entries": [{"order": 9, "id": "existing-9"}, {"order": 10, "id": "existing-10"}]}
    plan = build_campaign_plan(catalog=catalog, authority=authority, pool=_pool([50], profiles=["FLOW"]), k=1)
    assert plan["slots"][0]["chosen_id"] == "level-000"


def test_nonempty_catalog_without_two_level_official_history_fails_closed():
    with pytest.raises(CampaignError, match="CATALOG_TAIL_DIFFICULTY_EVIDENCE_UNAVAILABLE"):
        build_campaign_plan(catalog={"entries": [{"order": 1, "id": "existing-1"}]}, authority=_authority(), pool=_pool([50]), k=1)


def test_each_profile_rule_compares_its_own_axis_median():
    # W, U, and B distributions have different medians. A candidate that is high
    # on exactly one axis must be rejected by that axis's rule.
    catalog = {"entries": [{"order": 1, "id": "existing-1"}]}
    cases = [
        ("high_w_adjacency_ok", [0.1, 0.2, 0.3, 0.8, 0.9], [0.1] * 5, [0.95, 0.95, 0.95, 0.1, 0.1], _tail(1, "COLOR", [0.85, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]), False),
        ("low_u_recovery_ok", [0.1] * 5, [0.1, 0.2, 0.3, 0.8, 0.9], [0.9, 0.9, 0.9, 0.1, 0.1], _tail(1, "COLOR", [0.1] * 7, slot=1, score=80), True),
        ("low_b_recovery_ok", [0.1] * 5, [0.9, 0.9, 0.9, 0.1, 0.1], [0.1, 0.2, 0.3, 0.8, 0.9], _tail(1, "COLOR", [0.1] * 7, slot=1, score=80), True),
        ("high_b_adjacency_ok", [0.1, 0.2, 0.25, 0.8, 0.9], [0.6] * 5, [0.1, 0.2, 0.3, 0.8, 0.9], _tail(1, "COLOR", [0.1, 0.1, 0.1, 0.1, 0.8, 0.1, 0.1]), False),
    ]
    for rule, w_values, u_values, b_values, tail, recovery in cases:
        authority = _authority()
        authority["_catalog_tail"] = [tail]
        if recovery:
            authority["cadenceLength"] = 2
            authority["cadence"] = [{"slot": 1, "class": "EASY", "role": "regular", "modifier": 30, "noveltyTarget": 0}, {"slot": 2, "class": "EASY", "role": "recovery", "modifier": -30, "noveltyTarget": 0}]
            authority["recoveryGuards"] = [{"fromSlot": 1, "toSlot": 2, "minimumChallengeDrop": 10}]
        catalog = {"entries": [{"order": 1, "id": "existing-1"}]}
        pool = _pool([50] * 5, profiles=["FLOW", "COLOR", "ROUTE", "FORTRESS", "MARATHON"])
        if recovery:
            for candidate in pool:
                candidate["challenge_score"] = 20
        for index, candidate in enumerate(pool):
            vector = [0.1] * 7
            vector[0], vector[3], vector[4] = w_values[index], u_values[index], b_values[index]
            _set_vector(candidate, vector)
        medians = (sorted(w_values)[len(w_values)//2], sorted(u_values)[len(u_values)//2], sorted(b_values)[len(b_values)//2])
        target_vector = pool[3]["challenge_vector"]
        previous_vector = tail["challenge_vector"]
        assert len(set(medians)) == 3
        if rule == "high_w_adjacency_ok":
            assert target_vector[0] > medians[0] and previous_vector[0] > medians[0]
            assert target_vector[4] <= medians[2] and previous_vector[4] <= medians[2]
        elif rule == "low_u_recovery_ok":
            assert target_vector[3] > medians[1] and target_vector[4] <= medians[2]
        elif rule == "low_b_recovery_ok":
            assert target_vector[4] > medians[2] and target_vector[3] <= medians[1]
        else:
            assert target_vector[4] > medians[2] and previous_vector[4] > medians[2]
            assert target_vector[0] > medians[0] and previous_vector[0] <= medians[0]
        authority["_catalog_tail"][-1]["slot"] = 1
        # Lock level-003, whose relevant axis is above its own median while the
        # other axis used by the former shared-median bug is below that median.
        with pytest.raises(CampaignError, match="sequence constraint"):
            build_campaign_plan(catalog=catalog, authority=authority, pool=pool, k=1, locks={2: "level-003"})


def test_each_current_recovery_guard_uses_actual_adjacent_challenge_scores():
    authority = _authority()
    authority.update({"cadenceLength": 10, "cadence": [{"slot": slot, "class": "EASY", "role": "test", "modifier": (30 if slot in {3, 5, 8, 10} else -30 if slot in {1, 4, 6, 9} else 0), "noveltyTarget": 0} for slot in range(1, 11)], "recoveryGuards": [
        {"fromSlot": 3, "toSlot": 4, "minimumChallengeDrop": 15},
        {"fromSlot": 5, "toSlot": 6, "minimumChallengeDrop": 20},
        {"fromSlot": 8, "toSlot": 9, "minimumChallengeDrop": 15},
        {"fromSlot": 10, "toNextCycleSlot": 1, "minimumChallengeDrop": 35},
    ]})
    authority["lanes"] = {"EASY": {"base": 50, "growth": 0}}
    # Slot 1 is 20; guard source slots are 80 and recovery slots are 20.
    scores = [20 if slot in {1, 4, 6, 9} else 80 if slot in {3, 5, 8, 10} else 50 for slot in range(1, 11)]
    pool = _pool(scores + [20], profiles=[("FLOW", "COLOR", "ROUTE")[i % 3] for i in range(11)])
    plan = build_campaign_plan(catalog={"entries": []}, authority=authority, pool=pool, k=11)
    assert [plan["slots"][i]["checks"]["recovery_guard"] for i in (3, 5, 8, 10)] == [True] * 4


def test_configured_similarity_limit_blocks_consecutive_near_duplicates():
    authority = _authority(); authority["campaignBuilder"] = {"maxConsecutiveSimilarity": 0.9}
    pool = _pool([50, 50])
    pool[0]["signature"] = pool[1]["signature"] = {"paletteSet": ["C01"], "dimensions": [20, 20], "challengeVector": [0.1] * 7}
    plan = build_campaign_plan(catalog={"entries": []}, authority=authority, pool=pool, k=2)
    assert plan["slots"][1]["chosen_id"] is None
    assert plan["shortages"][0]["n"] == 2


def test_slot_novelty_target_is_applied_against_prior_signature():
    authority = _authority()
    pool = _pool([50, 50])
    pool[0]["signature"] = pool[1]["signature"] = {"paletteSet": ["C01"], "dimensions": [20, 20], "challengeVector": [0.1] * 7}
    authority["cadence"][0]["noveltyTarget"] = 0.5
    plan = build_campaign_plan(catalog={"entries": []}, authority=authority, pool=pool, k=2)
    assert plan["slots"][0]["checks"]["novelty_ok"]
    assert plan["slots"][1]["chosen_id"] is None
    assert any("below slot novelty target" in reason for item in plan["shortages"][0]["nearest_unused_candidates"] for reason in item["reasons"])


def test_k100_synthetic_example_is_deterministic_and_complete():
    root = Path(__file__).resolve().parents[2]
    pool = _pool([50] * 100, profiles=[("FLOW", "COLOR", "ROUTE")[i % 3] for i in range(100)])
    for i, candidate in enumerate(pool):
        vector = [0.0] * 7 if i % 2 == 0 else [1.0] * 7
        palette = [f"C{n:02d}" for n in range((i % 4) * 3 + 1, (i % 4) * 3 + 4)]
        dimensions = [20, 20] if i % 2 == 0 else [59, 59]
        candidate.update({"width": dimensions[0], "height": dimensions[1], "challenge_vector": vector, "used_colors": palette, "palette": palette, "signature": {"paletteSet": palette, "dimensions": dimensions, "challengeVector": vector}})
    authority = _authority()
    authority["cadence"][0]["noveltyTarget"] = 0.75
    plan = build_campaign_plan(catalog={"schema": "scrubbots.production_catalog.v1", "entries": []}, authority=authority, pool=pool, k=100)
    assert len(plan["slots"]) == 100
    assert len(plan["publishable_prefix"]) == 100
    assert not plan["shortages"]
    example = root / "docs/examples/campaign_plan_k100_synthetic.json"
    example.parent.mkdir(parents=True, exist_ok=True)
    example.write_text(json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
