from pathlib import Path

ROOT = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert s.count(old) == 1, (rel, old[:80])
        s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")


edit("src/scrubbots_pixel_factory/supply_pipeline/progression.py", [
    ('''    if type(value["progression"].get("tauCycles")) not in {int, float} or float(value["progression"]["tauCycles"]) <= 0:
        raise ProgressionAuthorityError("progression tauCycles is invalid")
    return value
''', '''    if type(value["progression"].get("tauCycles")) not in {int, float} or float(value["progression"]["tauCycles"]) <= 0:
        raise ProgressionAuthorityError("progression tauCycles is invalid")
    value["campaignScoreBands"] = load_campaign_score_bands()
    return value


CAMPAIGN_SCORE_BANDS_PATH = Path(__file__).with_name("campaign_score_bands_v1.json")


def load_campaign_score_bands(path: str | Path | None = None) -> dict[str, object]:
    """Owner decision 2026-11-24: contiguous score bands for one campaign range.

    Inside ``fromLevel..toLevel`` a slot takes a level whose official challenge score lies in
    its cadence class band, the target rises through the band over the range, and the band's
    own recovery guards replace the game's (whose drops the pool cannot meet).
    """
    source = Path(path) if path is not None else CAMPAIGN_SCORE_BANDS_PATH
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProgressionAuthorityError(f"campaign score bands are unreadable: {source}") from exc
    bands = value.get("bands") if isinstance(value, dict) else None
    if (not isinstance(value, dict) or value.get("schema") != "scrubbots-campaign-score-bands/v1"
            or type(value.get("fromLevel")) is not int or type(value.get("toLevel")) is not int
            or not 1 <= value["fromLevel"] < value["toLevel"] or not isinstance(bands, dict)
            or set(bands) != {"EASY", "MEDIUM", "HARD", "VERY_HARD"} or not isinstance(value.get("recoveryGuards"), list)):
        raise ProgressionAuthorityError("campaign score bands are malformed")
    for name, band in bands.items():
        keys = ("min", "max", "targetFrom", "targetTo")
        if (not isinstance(band, dict) or any(type(band.get(key)) not in {int, float} or not math.isfinite(float(band[key])) for key in keys)
                or not band["min"] <= band["targetFrom"] <= band["targetTo"] <= band["max"] or band["min"] >= band["max"]):
            raise ProgressionAuthorityError(f"campaign score band {name} is malformed")
    return value


def campaign_band(level_number: int, class_name: str, authority: Mapping[str, object]) -> dict[str, float] | None:
    policy = authority.get("campaignScoreBands")
    if not isinstance(policy, Mapping) or not int(policy["fromLevel"]) <= level_number <= int(policy["toLevel"]):
        return None
    band = policy["bands"].get(class_name) if isinstance(policy.get("bands"), Mapping) else None
    return dict(band) if isinstance(band, Mapping) else None


def score_in_band(score: float, band: Mapping[str, object]) -> bool:
    return float(band["min"]) <= float(score) < float(band["max"]) or float(score) == float(band["max"]) == 100.0
'''),
    ('''    p = 1.0 - math.exp(-float(cycle) / float(progression["tauCycles"]))
    target = max(0.0, min(100.0, float(lane.get("base", 0.0)) + float(lane.get("growth", 0.0)) * p + float(cadence_entry.get("modifier", 0.0))))
    return {"level": level_number, "slot": slot, "cycle": cycle, "class": class_name, "role": str(cadence_entry.get("role", "")), "modifier": float(cadence_entry.get("modifier", 0.0)), "p": p, "target_challenge": target, "novelty_target": float(cadence_entry.get("noveltyTarget", 0.0))}
''', '''    p = 1.0 - math.exp(-float(cycle) / float(progression["tauCycles"]))
    target = max(0.0, min(100.0, float(lane.get("base", 0.0)) + float(lane.get("growth", 0.0)) * p + float(cadence_entry.get("modifier", 0.0))))
    described = {"level": level_number, "slot": slot, "cycle": cycle, "class": class_name, "role": str(cadence_entry.get("role", "")), "modifier": float(cadence_entry.get("modifier", 0.0)), "p": p, "target_challenge": target, "novelty_target": float(cadence_entry.get("noveltyTarget", 0.0))}
    band = campaign_band(level_number, class_name, authority)
    if band is not None:
        policy = authority["campaignScoreBands"]
        span = max(1, int(policy["toLevel"]) - int(policy["fromLevel"]))
        fraction = (level_number - int(policy["fromLevel"])) / span
        described["target_challenge"] = float(band["targetFrom"]) + (float(band["targetTo"]) - float(band["targetFrom"])) * fraction
        described["band"] = [float(band["min"]), float(band["max"])]
    return described
'''),
])

edit("src/scrubbots_pixel_factory/supply_pipeline/campaign_builder.py", [
    ("from .progression import describe_target\n", "from .progression import describe_target, score_in_band\n"),
    ('''    score = item.get("challenge_score")
    width, height = item.get("width"), item.get("height")
    colors = item.get("used_colors", item.get("palette", []))
    return (type(score) in {int, float} and math.isfinite(float(score)) and abs(float(score) - float(target["target_challenge"])) <= tolerance
''', '''    score = item.get("challenge_score")
    width, height = item.get("width"), item.get("height")
    colors = item.get("used_colors", item.get("palette", []))
    band = target.get("band")
    return (type(score) in {int, float} and math.isfinite(float(score))
        and (score_in_band(float(score), {"min": band[0], "max": band[1]}) if band else abs(float(score) - float(target["target_challenge"])) <= tolerance)
'''),
    ('''            guards = authority.get("recoveryGuards", [])
''', '''            band_policy = authority.get("campaignScoreBands")
            guards = band_policy["recoveryGuards"] if slot.get("band") and isinstance(band_policy, Mapping) else authority.get("recoveryGuards", [])
'''),
    ('''                if abs(score - float(slot["target_challenge"])) > hard: reasons.append("outside hard tolerance")
''', '''                if slot.get("band") and not score_in_band(score, {"min": slot["band"][0], "max": slot["band"][1]}): reasons.append("outside class score band")
                elif not slot.get("band") and abs(score - float(slot["target_challenge"])) > hard: reasons.append("outside hard tolerance")
'''),
    ('''"allowed_range": [float(slot["target_challenge"])-hard, float(slot["target_challenge"])+hard],''',
     '''"allowed_range": list(slot["band"]) if slot.get("band") else [float(slot["target_challenge"])-hard, float(slot["target_challenge"])+hard],'''),
])

edit("src/scrubbots_pixel_factory/supply_pipeline/game_publisher.py", [
    ("from .progression import ProgressionAuthorityError, challenge_tolerance, describe_target, load_progression_authority\n",
     "from .progression import ProgressionAuthorityError, challenge_tolerance, describe_target, load_progression_authority, score_in_band\n"),
    ('''    if abs(float(score) - float(progression["target_challenge"])) > tolerance:
        raise PublicationError("official Difficulty V1 score does not fit its explicit CampaignBuilder target")
''', '''    band = progression.get("band")
    if band is not None and not score_in_band(float(score), {"min": band[0], "max": band[1]}):
        raise PublicationError("official Difficulty V1 score is outside its CampaignBuilder class score band")
    if band is None and abs(float(score) - float(progression["target_challenge"])) > tolerance:
        raise PublicationError("official Difficulty V1 score does not fit its explicit CampaignBuilder target")
'''),
])
print("applied")
