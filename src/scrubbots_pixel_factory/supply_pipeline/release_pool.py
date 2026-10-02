"""Owner Release Pool, campaign plan, lock validation, and batch approval."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .campaign_builder import CampaignError, build_campaign_plan, write_campaign_plan
from .game_publisher import PublicationError, discover_game_project, publish_batch
from .progression import load_progression_authority


class ReleaseError(ValueError):
    pass


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"release authority is unavailable: {path}") from exc
    if not isinstance(value, dict): raise ReleaseError(f"release authority is malformed: {path}")
    return value


def _hash(raw: bytes) -> str: return hashlib.sha256(raw).hexdigest()


def _pool_root() -> Path:
    from .. import studio_extensions as studio
    return studio.extensions_root() / "release-pool"


def enter_release_pool(candidate: Mapping[str, Any], pipeline: Mapping[str, Any], review: Mapping[str, Any]) -> dict[str, Any]:
    if review.get("disposition") != "ACCEPT" or pipeline.get("disposition") != "READY" or pipeline.get("primary", {}).get("state") != "READY":
        return {"disposition": "NOT_ENTERED_NOT_READY", "reason": "Release Pool requires owner ACCEPT and a READY canonical ZIP/solver/replay/Difficulty pipeline."}
    primary = pipeline["primary"]
    difficulty = primary.get("difficulty", {})
    if not isinstance(difficulty, Mapping) or type(difficulty.get("score")) not in {int, float}:
        raise ReleaseError("official Difficulty V1 score is missing")
    metrics = primary.get("solver_metrics", {})
    official = metrics.get("official_difficulty_v1", {}) if isinstance(metrics, Mapping) else {}
    vector = official.get("challengeVector", official.get("challenge_vector", official.get("vector", []))) if isinstance(official, Mapping) else []
    if isinstance(vector, Mapping): vector = [vector.get(axis) for axis in ("W", "C", "A", "U", "B", "R", "S")]
    if not isinstance(vector, list) or len(vector) != 7 or any(type(value) not in {int, float} for value in vector):
        raise ReleaseError("official Difficulty V1 challenge vector [W,C,A,U,B,R,S] is missing or malformed")
    profile_defs = official.get("profiles", {}) if isinstance(official, Mapping) else {}
    dominant = official.get("dominantProfile", official.get("dominant_profile")) if isinstance(official, Mapping) else None
    if not dominant:
        w, c, a, u, b, r, s = [float(value) for value in vector]
        scores = {"FLOW": 1 - (a + u + b) / 3, "COLOR": (c + s) / 2, "FORTRESS": (u + b) / 2, "ROUTE": (r + a) / 2, "MARATHON": w - (b + u) / 2}
        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        dominant = "BALANCED" if ranked[0][1] - ranked[1][1] < 0.05 else ranked[0][0]
    from .. import studio_extensions as studio
    bundle_path = (studio._repository_root() / str(candidate["source_path"])).resolve()
    paths = {"artwork": bundle_path / "artwork.png", "level": Path(str(primary.get("files", {}).get("level", ""))).expanduser(), "supply_plan": Path(str(primary.get("files", {}).get("supply_plan", ""))).expanduser()}
    if any(not path.is_file() for path in paths.values()): raise ReleaseError("Release Pool requires existing canonical artwork, level, and supply files")
    file_digests = {name: {"path": str(path), "sha256": _hash(path.read_bytes())} for name, path in paths.items()}
    payload = {
        "schema": "scrubbots-release-pool-entry/v1", "candidate_id": candidate["candidate_id"],
        "width": candidate.get("width"), "height": candidate.get("height"), "used_colors": candidate.get("used_colors", []),
        "artwork_sha256": candidate["artwork_sha256"], "grid_hash": candidate["grid_hash"],
        "challenge_score": difficulty["score"], "difficulty_class": difficulty.get("class"),
        "challenge_vector": vector, "dominant_profile": dominant,
        "frustration_risk": official.get("frustrationRisk") if isinstance(official, Mapping) else None,
        "session_load": official.get("sessionLoad") if isinstance(official, Mapping) else None,
        "signature": {"dimensions": [candidate.get("width"), candidate.get("height")], "paletteSet": candidate.get("used_colors", []), "challengeVector": vector, "dominantProfile": dominant, "silhouetteHash": candidate.get("grid_hash")},
        "files": file_digests, "pipeline_run_id": pipeline["run_id"], "pipeline_sha256": _hash(studio._pipeline_path(str(pipeline["run_id"])).read_bytes()),
        "review_id": review["review_id"], "source_bundle": candidate["source_path"], "candidate": dict(candidate), "pipeline": dict(pipeline),
    }
    payload["entry_digest"] = _hash(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    path = _pool_root() / f"{candidate['candidate_id']}-{review['review_id']}.json"
    raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if path.exists() and path.read_bytes() != raw:
        raise ReleaseError("candidate already has different immutable Release Pool evidence")
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    return {"disposition": "ENTERED_RELEASE_POOL", "candidate_id": candidate["candidate_id"], "entry_digest": payload["entry_digest"], "pool_size": len(list(_pool_root().glob("*.json")))}


def release_entries() -> list[dict[str, Any]]:
    entries = []
    from .. import studio_extensions as studio
    for path in sorted(_pool_root().glob("*.json")) if _pool_root().exists() else ():
        value = _json(path)
        expected = value.pop("entry_digest", None)
        actual = _hash(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
        value["entry_digest"] = expected
        if expected != actual: raise ReleaseError(f"Release Pool entry digest mismatch: {path.name}")
        latest = studio._latest_review(str(value.get("candidate_id", "")))
        if latest and latest.get("disposition") == "ACCEPT" and latest.get("review_id") == value.get("review_id"):
            pipeline_path = studio._pipeline_path(str(value.get("pipeline_run_id", "")))
            if not pipeline_path.is_file() or _hash(pipeline_path.read_bytes()) != value.get("pipeline_sha256"):
                raise ReleaseError(f"Release Pool pipeline evidence changed or disappeared: {path.name}")
            current_candidate = next((item for item in studio.list_candidates() if item.get("candidate_id") == value.get("candidate_id")), None)
            if current_candidate is None or current_candidate.get("artwork_sha256") != value.get("artwork_sha256") or current_candidate.get("grid_hash") != value.get("grid_hash"):
                raise ReleaseError(f"Release Pool candidate identity changed or disappeared: {path.name}")
            for name, file_record in value.get("files", {}).items():
                evidence_file = Path(str(file_record.get("path", "")))
                if not evidence_file.is_file() or _hash(evidence_file.read_bytes()) != file_record.get("sha256"):
                    raise ReleaseError(f"Release Pool {name} artifact changed or disappeared: {path.name}")
            entries.append(value)
    return sorted(entries, key=lambda item: str(item["candidate_id"]))


def _game_authority(game: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    authority = load_progression_authority(game)
    analyzer_path = game / "data/config/level_difficulty_analysis_v1.json"
    analyzer = _json(analyzer_path)
    docs_path = game / "docs/10_LEVEL_FACTORY_GENERATION_SCORING_ARCHITECTURE.md"
    docs = docs_path.read_bytes()
    difficulty_rules_path = game / "scripts/data/difficulty_rules.gd"
    difficulty_rules = difficulty_rules_path.read_text(encoding="utf-8")
    minimum = re.search(r"const ENVELOPE_MIN\s*:=\s*(\d+)", difficulty_rules)
    maximum = re.search(r"const ENVELOPE_MAX\s*:=\s*(\d+)", difficulty_rules)
    palette_rules_path = game / "docs/08_PIXEL_ART_PALETTE_RULES.md"
    palette_rules = palette_rules_path.read_text(encoding="utf-8")
    color_range = re.search(r"global\s+(\d+)\.\.(\d+)\s+used-color envelope", palette_rules)
    if not minimum or not maximum or not color_range:
        raise ReleaseError("current game production dimension/color envelope cannot be derived from authoritative code/docs")
    authority["_production_envelope"] = {"min_dimension": int(minimum.group(1)), "max_dimension": int(maximum.group(1)), "min_colors": int(color_range.group(1)), "max_colors": int(color_range.group(2))}
    authority["_m10_rules"] = {"analysis_sha256": _hash(analyzer_path.read_bytes()), "architecture_sha256": _hash(docs), "difficulty_rules_sha256": _hash(difficulty_rules.encode()), "palette_rules_sha256": _hash(palette_rules.encode()), "similarity_definition": analyzer.get("operationalDefinitions", {}).get("similarity"), "profile_definition": analyzer.get("operationalDefinitions", {}).get("profiles")}
    catalog_path = game / "data/levels/catalog/production_catalog_v1.json"
    catalog = _json(catalog_path)
    last = max((entry for entry in catalog.get("entries", []) if isinstance(entry, Mapping) and type(entry.get("order")) is int), key=lambda item: int(item["order"]), default=None)
    if last is not None:
        metadata_path = str(last.get("metadata_path", "")).removeprefix("res://")
        if metadata_path:
            metadata_file = game / metadata_path
            if metadata_file.is_file():
                metadata = _json(metadata_file)
                progression = metadata.get("progression", {}) if isinstance(metadata.get("progression", {}), Mapping) else {}
                vector = metadata.get("challengeVector")
                authority["_catalog_tail"] = {"challenge_score": metadata.get("challengeScore"), "dominant_profile": metadata.get("dominantProfile", "BALANCED"), "challenge_vector": vector if isinstance(vector, list) else [], "frustration_risk": metadata.get("frustrationRisk"), "slot": progression.get("slot"), "width": metadata.get("width"), "height": metadata.get("height"), "palette": metadata.get("paletteSet", []), "signature": metadata.get("noveltySignature", {})}
    return catalog, authority


def build_release_plan(*, game_project: str | Path | None = None, k: int = 100, locks: Mapping[int, str] | None = None) -> dict[str, Any]:
    game = discover_game_project(game_project)
    catalog, authority = _game_authority(game)
    entries = release_entries()
    plan = build_campaign_plan(catalog=catalog, authority=authority, pool=entries, k=k, locks=locks)
    from .. import studio_extensions as studio
    plan_path = studio.extensions_root() / "release" / "campaign_plan.json"
    write_campaign_plan(plan_path, plan)
    plan["artifact_path"] = str(plan_path)
    plan["pool_size"] = len(entries)
    return plan


def approve_release_plan(*, plan_hash: str, game_project: str | Path | None = None) -> dict[str, Any]:
    game = discover_game_project(game_project)
    from .. import studio_extensions as studio
    plan_path = studio.extensions_root() / "release" / "campaign_plan.json"
    plan = _json(plan_path)
    if plan.get("plan_hash") != plan_hash: raise ReleaseError("APPROVE requires the current exact campaign plan hash")
    entries = {entry["candidate_id"]: entry for entry in release_entries()}
    rows = plan.get("slots", [])
    prefix = []
    for row in rows:
        if not row.get("chosen_id"): break
        prefix.append(row)
    if not prefix: raise ReleaseError("campaign plan has no publishable contiguous prefix")
    catalog, authority = _game_authority(game)
    locks = {int(row["n"]): str(row["chosen_id"]) for row in prefix}
    rebuilt = build_campaign_plan(catalog=catalog, authority=authority, pool=list(entries.values()), k=int(plan["K"]), locks=locks)
    if rebuilt.get("plan_hash") != plan_hash: raise ReleaseError("campaign inputs or locked sequence changed since plan review")
    items = []
    for row in prefix:
        entry = entries[str(row["chosen_id"])]
        bundle = (studio._repository_root() / str(entry["source_bundle"])).resolve()
        items.append({"candidate": entry["candidate"], "pipeline": entry["pipeline"], "source_bundle": bundle, "level_number": int(row["n"])})
    try:
        result = publish_batch(game_project=game, items=items)
    except (PublicationError, OSError, ValueError) as exc:
        raise ReleaseError(str(exc)) from exc
    return {**result, "plan_hash": plan_hash, "approved_orders": [row["n"] for row in prefix]}


__all__ = ["ReleaseError", "approve_release_plan", "build_release_plan", "enter_release_pool", "release_entries"]
