"""Current Scrubbots DifficultyProgressionV1 placement authority."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Mapping
from pathlib import Path


class ProgressionAuthorityError(ValueError):
    """Raised when current game progression authority cannot be trusted."""


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
    return value


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
    return {"level": level_number, "slot": slot, "cycle": cycle, "class": class_name, "role": str(cadence_entry.get("role", "")), "modifier": float(cadence_entry.get("modifier", 0.0)), "p": p, "target_challenge": target, "novelty_target": float(cadence_entry.get("noveltyTarget", 0.0))}


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
            tolerance = authority.get("challengeTolerance", {})
            allowed = float(tolerance.get("neverForceLabelOutsidePlusMinus", 5.0)) if isinstance(tolerance, Mapping) else 5.0
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


__all__ = ["ProgressionAuthorityError", "build_progression", "describe_target", "load_progression_authority"]
