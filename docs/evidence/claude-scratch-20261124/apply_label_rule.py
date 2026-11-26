from pathlib import Path

ROOT = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert s.count(old) == 1, (rel, old[:80])
        s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")


edit("src/scrubbots_pixel_factory/supply_pipeline/campaign_builder.py", [
    ('''def _eligible(item: Mapping[str, Any], target: Mapping[str, Any], tolerance: float, envelope: Mapping[str, int]) -> bool:
    score = item.get("challenge_score")
    label = item.get("difficulty_class")
    width, height = item.get("width"), item.get("height")''',
     '''def _eligible(item: Mapping[str, Any], target: Mapping[str, Any], tolerance: float, envelope: Mapping[str, int]) -> bool:
    # Owner decision 2026-11-24: a slot is filled by official challenge score within the hard
    # tolerance of its own target; the stored label (nearest fixed lane base) no longer has to
    # match. Targets grow with the cycle, so a level-300 EASY slot wants ~32, which the fixed
    # bases label MEDIUM; the published class is the slot's cadence class.
    score = item.get("challenge_score")
    width, height = item.get("width"), item.get("height")'''),
    ('''abs(float(score) - float(target["target_challenge"])) <= tolerance and label == target["class"]
        and type(width)''',
     '''abs(float(score) - float(target["target_challenge"])) <= tolerance
        and type(width)'''),
    ('''                if candidate.get("difficulty_class") != slot["class"]: reasons.append("class mismatch")
''', ""),
])

edit("src/scrubbots_pixel_factory/supply_pipeline/game_publisher.py", [
    ('''    difficulty_class = primary.get("difficulty", {}).get("class") if isinstance(primary.get("difficulty"), Mapping) else None
    if difficulty_class != progression["class"]:
        raise PublicationError("official Difficulty V1 class does not match the explicit CampaignBuilder cadence class")
''', '''    # Owner decision 2026-11-24: the published class is the slot's cadence class; the official
    # score must fit that slot's target (checked above), the fixed-base label is not required.
'''),
    ('''        "difficulty": primary.get("difficulty", {}).get("class") if isinstance(primary.get("difficulty"), Mapping) else None,
        "challengeScore": score,''',
     '''        "difficulty": progression["class"],
        "challengeScore": score,'''),
])

edit("tests/unit/test_campaign_builder.py", [
    ('''def test_class_mismatch_and_invalid_owner_lock_fail_closed():
    pool = _pool([50]); pool[0]["difficulty_class"] = "MEDIUM"
    plan = build_campaign_plan(catalog={"entries": []}, authority=_authority(), pool=pool, k=1)
    assert plan["slots"][0]["chosen_id"] is None
    assert plan["unassigned_ready_candidates"] == ["level-000"]
    assert pool[0]["difficulty_class"] == "MEDIUM"
    assert any("class mismatch" in reason for candidate in plan["shortages"][0]["nearest_unused_candidates"] for reason in candidate["reasons"])
''', '''def test_slot_is_filled_by_score_within_tolerance_not_by_stored_label_and_invalid_lock_fails_closed():
    # Owner decision 2026-11-24: the stored label is the nearest fixed lane base; growing slot
    # targets make it disagree with the cadence class, so only the score window decides.
    pool = _pool([50, 60]); pool[0]["difficulty_class"] = "MEDIUM"; pool[1]["difficulty_class"] = "EASY"
    plan = build_campaign_plan(catalog={"entries": []}, authority=_authority(), pool=pool, k=1)
    assert plan["slots"][0]["chosen_id"] == "level-000"  # MEDIUM label, score on the EASY target
    assert pool[0]["difficulty_class"] == "MEDIUM"
'''),
])
print("applied")
