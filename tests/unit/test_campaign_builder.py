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


def test_profile_limit_and_manual_lock_revalidation():
    authority = _authority()
    profiles = ["FLOW", "FLOW", "FLOW"]
    pool = _pool([50, 50, 50], profiles=profiles)
    plan = build_campaign_plan(catalog={"entries": []}, authority=authority, pool=pool, k=3)
    assert plan["slots"][2]["chosen_id"] is None
    with pytest.raises(CampaignError, match="sequence constraint"):
        build_campaign_plan(catalog={"entries": []}, authority=authority, pool=pool, k=3, locks={3: "level-002"})


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
