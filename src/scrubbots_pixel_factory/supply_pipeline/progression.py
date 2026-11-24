"""Current Scrubbots DifficultyProgressionV1 placement authority."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Mapping
from pathlib import Path


class ProgressionAuthorityError(ValueError):
    """Raised when current game progression authority cannot be trusted."""


def challenge_tolerance(authority: Mapping[str, object]) -> float:
    tolerance = authority.get("challengeTolerance")
    value = tolerance.get("neverForceLabelOutsidePlusMinus") if isinstance(tolerance, Mapping) else None
    if type(value) not in {int, float} or not math.isfinite(float(value)) or float(value) < 0:
        raise ProgressionAuthorityError("current challengeTolerance.neverForceLabelOutsidePlusMinus is missing or malformed")
    return float(value)


def load_progression_authority(game_project: str | Path) -> dict[str, object]:
    path = Path(game_project).expanduser().resolve() / "data" / "config" / "level_progression_v1.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProgressionAuthorityError(f"progression authority is unreadable: {path}") from exc
    if not isinstance(value, dict) or value.get("schema") != "scrubbots-level-progression/v1" or value.get("version") != 1:
        raise ProgressionAuthorityError("unsupported DifficultyProgressionV1 authority")
    cadence = value.get("cadence")
    if type(value.get("cadenceLength")) is not int or value["cadenceLength"] < 1 or not isinstance(cadence, list) or len(cadence) != value["cadenceLength"] or not isinstance(value.get("lanes"), dict) or not isinstance(value.get("progression"), dict):
        raise ProgressionAuthorityError("progression cadence/lanes are malformed")
    if type(value["progression"].get("tauCycles")) not in {int, float} or float(value["progression"]["tauCycles"]) <= 0:
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


def describe_target(level_number: int, authority: Mapping[str, object]) -> dict[str, object]:
    if type(level_number) is not int or level_number < 1:
        raise ProgressionAuthorityError("level number must be a positive integer")
    cadence_length = int(authority["cadenceLength"])
    cadence = authority["cadence"]
    lanes = authority["lanes"]
    progression = authority["progression"]
    slot = ((level_number - 1) % cadence_length) + 1
    cycle = (level_number - 1) // cadence_length
    cadence_entry = next((entry for entry in cadence if isinstance(entry, Mapping) and entry.get("slot") == slot), None)
    if not isinstance(cadence_entry, Mapping):
        raise ProgressionAuthorityError(f"cadence slot {slot} is missing")
    class_name = str(cadence_entry.get("class", ""))
    lane = lanes.get(class_name) if isinstance(lanes, Mapping) else None
    if not isinstance(lane, Mapping):
        raise ProgressionAuthorityError(f"lane is missing for cadence class {class_name}")
    p = 1.0 - math.exp(-float(cycle) / float(progression["tauCycles"]))
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


def build_progression(entries: Iterable[Mapping[str, object]], *, authority: Mapping[str, object] | None = None) -> dict[str, object]:
    """Build campaign order from catalog positions and current cadence targets."""

    normalized = [dict(entry) for entry in entries]
    for entry in normalized:
        entry.setdefault("order", len(normalized))
    if authority is not None:
        for entry in normalized:
            if type(entry.get("order")) is not int or entry["order"] < 1:
                raise ProgressionAuthorityError("published entry requires a positive catalog order")
            target = describe_target(int(entry["order"]), authority)
            score = entry.get("difficulty_score")
            if type(score) not in {int, float} or not math.isfinite(float(score)):
                raise ProgressionAuthorityError("published entry requires an official finite difficulty score")
            allowed = challenge_tolerance(authority)
            if abs(float(score) - float(target["target_challenge"])) > allowed:
                raise ProgressionAuthorityError(f"difficulty score is outside the current cadence target for order {entry['order']}")
            entry["progression"] = target
        ordering = "current_catalog_order_with_difficulty_progression_v1_targets"
        authority_name = "ScrubBots DifficultyProgressionV1 / data/config/level_progression_v1.json"
    else:
        ordering = "catalog_order_then_level_id"
        authority_name = "historical-compatibility-view"
    normalized.sort(key=lambda item: (int(item.get("order", 0)), str(item.get("level_id", item.get("candidate_id", "")))))
    return {"schema": "scrubbots-level-progression-v1", "version": 1, "authority": authority_name, "ordering": ordering, "levels": normalized}


__all__ = ["ProgressionAuthorityError", "build_progression", "challenge_tolerance", "describe_target", "load_progression_authority"]
