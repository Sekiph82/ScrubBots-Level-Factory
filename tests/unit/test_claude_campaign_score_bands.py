"""Owner decision 2026-11-24: contiguous campaign score bands for levels 201-1200.

The game's fixed lane bases with +/-5 tolerance leave gaps and need scores the Release
Pool does not have; bands cut from the pool's own distribution replace them in range.
"""
from __future__ import annotations

from scrubbots_pixel_factory.supply_pipeline import progression
from scrubbots_pixel_factory.supply_pipeline.campaign_builder import build_campaign_plan

POLICY = progression.load_campaign_score_bands()


def _authority():
    return {
        "schema": "scrubbots-level-progression/v1", "version": 1, "cadenceLength": 1,
        "cadence": [{"slot": 1, "class": "EASY", "role": "recovery", "modifier": 0, "noveltyTarget": 0}],
        "lanes": {"EASY": {"base": 20, "growth": 14}}, "progression": {"tauCycles": 20},
        "challengeTolerance": {"preferredWhenPoolIsLarge": 2, "defaultPlusMinus": 3.5, "neverForceLabelOutsidePlusMinus": 5},
        "recoveryGuards": [],
        "_production_envelope": {"min_dimension": 20, "max_dimension": 59, "min_colors": 3, "max_colors": 12},
        "campaignScoreBands": POLICY,
    }


def _item(i, score):
    return {"candidate_id": f"level-{i:03d}", "challenge_score": score, "difficulty_class": "MEDIUM", "dominant_profile": "BALANCED",
            "challenge_vector": [0.1 * (i + 1)] * 7, "width": 56, "height": 56, "used_colors": ["C01", "C02", "C03"],
            "palette": ["C01", "C02", "C03"], "signature": {"paletteSet": ["C01", "C02", "C03"], "dimensions": [56, 56], "challengeVector": [0.1 * (i + 1)] * 7}}


def test_bands_are_contiguous_and_cover_the_owner_range() -> None:
    bands = POLICY["bands"]
    order = ["EASY", "MEDIUM", "HARD", "VERY_HARD"]
    assert [bands[a]["max"] for a in order[:-1]] == [bands[b]["min"] for b in order[1:]]  # no gaps
    assert (POLICY["fromLevel"], POLICY["toLevel"]) == (201, 6450)
    assert (bands["EASY"]["max"], bands["VERY_HARD"]["min"]) == (49.0, 55.3)


def test_target_rises_through_the_class_band_inside_the_range() -> None:
    authority = _authority()
    first = progression.describe_target(201, authority)
    last = progression.describe_target(6450, authority)
    outside = progression.describe_target(6451, authority)
    assert first["band"] == [0.0, 49.0] and first["target_challenge"] == 42.0
    assert abs(last["target_challenge"] - 48.9) < 1e-9
    assert "band" not in outside


def test_slot_in_range_takes_any_score_inside_its_band_and_rejects_outside() -> None:
    # Level 201 is an EASY slot (target 42): 40.0 is inside the EASY band; 49.5 is outside it.
    catalog = {"entries": [{"order": n, "id": f"x{n}"} for n in range(1, 201)]}
    authority = _authority()
    authority["_catalog_tail"] = [
        {"order": n, "candidate_id": f"x{n}", "challenge_score": 40.0, "dominant_profile": "FLOW", "challenge_vector": [0.9] * 7,
         "slot": 1, "width": 56, "height": 56, "palette": ["C04"],
         "signature": {"dimensions": [56, 56], "paletteSet": ["C04"], "challengeVector": [0.9] * 7, "dominantProfile": "FLOW"}}
        for n in (199, 200)]
    plan = build_campaign_plan(catalog=catalog, authority=authority, pool=[_item(0, 49.5), _item(1, 40.0)], k=1)
    assert plan["slots"][0]["n"] == 201
    assert plan["slots"][0]["chosen_id"] == "level-001"
