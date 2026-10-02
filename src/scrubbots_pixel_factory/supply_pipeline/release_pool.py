"""Owner Release Pool, campaign plan, lock validation, and batch approval."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .campaign_builder import CampaignError, build_campaign_plan, write_campaign_plan
from .game_publisher import PublicationError, discover_game_project, publish_batch
from .progression import load_progression_authority


class ReleaseError(ValueError):
    pass


_DIFFICULTY_PROFILES = {"FLOW", "COLOR", "FORTRESS", "ROUTE", "MARATHON", "BALANCED"}


def _official_challenge_vector(official: Mapping[str, Any]) -> list[float]:
    vector = official.get("challengeVector", official.get("challenge_vector", official.get("vector")))
    if isinstance(vector, Mapping):
        vector = [vector.get(axis) for axis in ("W", "C", "A", "U", "B", "R", "S")]
    if not isinstance(vector, (list, tuple)) or len(vector) != 7 or any(type(value) not in {int, float} or not math.isfinite(float(value)) for value in vector):
        raise ReleaseError("official Difficulty V1 challenge vector [W,C,A,U,B,R,S] is missing or malformed")
    return [float(value) for value in vector]


def _official_profile(official: Mapping[str, Any]) -> dict[str, Any]:
    profile = official.get("profile")
    if not isinstance(profile, Mapping) or profile.get("dominant") not in _DIFFICULTY_PROFILES:
        raise ReleaseError("official Difficulty V1 profile.dominant is missing or malformed")
    return dict(profile)


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"release authority is unavailable: {path}") from exc
    if not isinstance(value, dict): raise ReleaseError(f"release authority is malformed: {path}")
    return value


def _hash(raw: bytes) -> str: return hashlib.sha256(raw).hexdigest()


def _level_content_hash(path: Path) -> str:
    # Git's text checkout may convert JSON line endings on Windows. Official
    # game evidence binds the canonical LF file content, so ignore CRLF-only
    # checkout conversion while still rejecting any content change.
    return _hash(path.read_bytes().replace(b"\r\n", b"\n"))


def _pool_root() -> Path:
    from .. import studio_extensions as studio
    return studio.extensions_root() / "release-pool"


def enter_release_pool(candidate: Mapping[str, Any], pipeline: Mapping[str, Any], review: Mapping[str, Any]) -> dict[str, Any]:
    if review.get("disposition") != "ACCEPT" or pipeline.get("disposition") != "READY" or pipeline.get("primary", {}).get("state") != "READY":
        return {"disposition": "NOT_ENTERED_NOT_READY", "reason": "Release Pool requires owner ACCEPT and a READY canonical ZIP/solver/replay/Difficulty pipeline."}
    primary = pipeline["primary"]
    difficulty = primary.get("difficulty", {})
    if not isinstance(difficulty, Mapping) or type(difficulty.get("score")) not in {int, float} or not math.isfinite(float(difficulty["score"])):
        raise ReleaseError("official Difficulty V1 score is missing")
    metrics = primary.get("solver_metrics", {})
    official = metrics.get("official_difficulty_v1", {}) if isinstance(metrics, Mapping) else {}
    if not isinstance(official, Mapping):
        raise ReleaseError("official Difficulty V1 evidence is missing or malformed")
    vector = _official_challenge_vector(official)
    profile = _official_profile(official)
    official_score = official.get("challengeScore")
    if type(official_score) not in {int, float} or not math.isfinite(float(official_score)) or float(official_score) != float(difficulty["score"]):
        raise ReleaseError("official Difficulty V1 challengeScore is missing or does not match the pipeline score")
    dominant = profile["dominant"]
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
        "challenge_vector": vector, "dominant_profile": dominant, "official_profile": profile,
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
    entries = [entry for entry in catalog.get("entries", []) if isinstance(entry, Mapping) and type(entry.get("order")) is int]
    ordered = sorted(entries, key=lambda item: int(item["order"]))
    required_tail = ordered[-2:]
    evidence_path = game / "coordination/sessions/M53-C001/evidence/first10_difficulty_v1.json"
    evidence: dict[str, Any] = {}
    if evidence_path.is_file():
        evidence = _json(evidence_path)
        provenance = evidence.get("provenance", {})
        if (evidence.get("schema") != "scrubbots.m53.first10_difficulty.v1"
            or not isinstance(provenance, Mapping)
            or provenance.get("analyzerVersion") != analyzer.get("analyzerVersion")
            or evidence.get("analysisConfig") != analyzer):
            evidence = {}
    evidence_by_identity = {
        (record.get("order"), record.get("id")): record
        for record in evidence.get("levels", [])
        if isinstance(record, Mapping)
    }

    def canonical_tail(entry: Mapping[str, Any], metadata: Mapping[str, Any], official: Mapping[str, Any], *, evidence_source: str) -> dict[str, Any] | None:
        level_path = game / str(entry.get("level_path", "")).removeprefix("res://")
        if not level_path.is_file():
            return None
        level_sha = _level_content_hash(level_path)
        file_digests = metadata.get("fileDigests", {})
        official_level_sha = official.get("levelSha256") if isinstance(official, Mapping) else None
        bound_level_sha = file_digests.get("level") if isinstance(file_digests, Mapping) else None
        if bound_level_sha != level_sha and official_level_sha != level_sha:
            return None
        try:
            profile = _official_profile(official)
            vector = _official_challenge_vector(official)
        except ReleaseError:
            return None
        score = official.get("challengeScore", metadata.get("challengeScore"))
        if type(score) not in {int, float} or not math.isfinite(float(score)):
            return None
        dimensions = [metadata.get("width"), metadata.get("height")]
        if any(type(value) is not int or value < 1 for value in dimensions):
            return None
        progression = metadata.get("progression", {})
        progression = progression if isinstance(progression, Mapping) else {}
        signature = metadata.get("noveltySignature", official.get("signature"))
        if not isinstance(signature, Mapping):
            return None
        palette = signature.get("paletteSet", metadata.get("paletteSet", metadata.get("palette", [])))
        signature_dimensions = signature.get("dimensions", dimensions)
        signature_vector = signature.get("challengeVector", vector)
        if (not isinstance(palette, list) or not palette
            or signature_dimensions != dimensions
            or not isinstance(signature_vector, (list, tuple)) or len(signature_vector) != 7
            or any(type(value) not in {int, float} or not math.isfinite(float(value)) for value in signature_vector)):
            return None
        bound_signature = {
            **dict(signature),
            "dimensions": dimensions,
            "paletteSet": list(palette),
            "challengeVector": [float(value) for value in signature_vector],
            "dominantProfile": profile["dominant"],
        }
        return {
            "order": int(entry["order"]), "candidate_id": str(entry.get("id", "")),
            "challenge_score": float(score), "dominant_profile": profile["dominant"],
            "official_profile": profile, "challenge_vector": vector,
            "frustration_risk": official.get("frustrationRisk", metadata.get("frustrationRisk")),
            "slot": progression.get("slot", metadata.get("slot")),
            "width": dimensions[0], "height": dimensions[1], "palette": list(palette),
            "signature": bound_signature, "level_sha256": level_sha, "evidence_source": evidence_source,
        }

    catalog_tail: list[dict[str, Any]] = []
    for entry in required_tail:
        metadata_path = str(entry.get("metadata_path", "")).removeprefix("res://")
        metadata_file = game / metadata_path if metadata_path else None
        metadata = _json(metadata_file) if metadata_file is not None and metadata_file.is_file() else {}
        official = metadata.get("official_difficulty_v1", metadata.get("officialDifficultyV1", {}))
        resolved = canonical_tail(entry, metadata, official, evidence_source="catalog metadata") if isinstance(official, Mapping) else None
        if resolved is None:
            record = evidence_by_identity.get((entry.get("order"), entry.get("id")))
            level_path = game / str(entry.get("level_path", "")).removeprefix("res://")
            if isinstance(record, Mapping) and level_path.is_file() and record.get("levelSha256") == _level_content_hash(level_path):
                evidence_vector = record.get("vector")
                signature_vector = [evidence_vector.get(axis) for axis in ("W", "C", "A", "U", "B", "R", "S")] if isinstance(evidence_vector, Mapping) else evidence_vector
                record_metadata = {"width": record.get("width"), "height": record.get("height"), "palette": record.get("palette"), "slot": record.get("slot"), "challengeScore": record.get("challengeScore"), "noveltySignature": {"dimensions": [record.get("width"), record.get("height")], "paletteSet": record.get("palette"), "challengeVector": signature_vector}}
                record_official = {"levelSha256": record.get("levelSha256"), "challengeScore": record.get("challengeScore"), "vector": record.get("vector"), "profile": record.get("profile"), "frustrationRisk": record.get("frustrationRisk")}
                resolved = canonical_tail(entry, record_metadata, record_official, evidence_source="current-game M53 Difficulty V1 evidence")
        if resolved is None:
            raise ReleaseError(f"CATALOG_TAIL_DIFFICULTY_EVIDENCE_UNAVAILABLE: order {entry.get('order')} ({entry.get('id')}) has no hash-bound official Difficulty V1 profile/vector/signature")
        catalog_tail.append(resolved)
    if catalog_tail:
        authority["_catalog_tail"] = catalog_tail
        authority["_m10_rules"]["catalog_tail_difficulty_evidence_sha256"] = _hash(evidence_path.read_bytes()) if evidence_path.is_file() and any(item["evidence_source"].startswith("current-game M53") for item in catalog_tail) else None
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
