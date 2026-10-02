"""Transactional publication into a configured Scrubbots game project."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from collections.abc import Mapping

from .progression import ProgressionAuthorityError, describe_target, load_progression_authority


class PublicationError(ValueError):
    """Raised when a publication gate or transactional write fails."""


_STABLE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def discover_game_project(explicit: str | Path | None = None) -> Path:
    value = explicit if explicit is not None else os.environ.get("SCRUBBOTS_PROJECT", "")
    if not str(value).strip():
        raise PublicationError("SCRUBBOTS_PROJECT or an explicit game_project is required")
    root = Path(value).expanduser().resolve()
    required = (root / "project.godot", root / "data" / "config" / "level_progression_v1.json", root / "data" / "levels" / "catalog" / "production_catalog_v1.json")
    if any(not path.is_file() for path in required):
        raise PublicationError("configured Scrubbots project is missing project/progression/catalog authority")
    return root


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _load(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PublicationError(f"publication input is unreadable: {path}") from exc


def publish_level(*, game_project: str | Path | None, candidate: Mapping[str, object], pipeline: Mapping[str, object], source_bundle: str | Path, level_number: int | None = None) -> dict[str, object]:
    """Publish one validated batch member at its explicitly assigned catalog order."""

    if type(level_number) is not int or level_number < 1:
        raise PublicationError("CampaignBuilder must provide an explicit positive level_number")

    root = discover_game_project(game_project)
    candidate_id = str(candidate.get("candidate_id", ""))
    level_id = str(pipeline.get("primary", {}).get("level_id", candidate_id)) if isinstance(pipeline.get("primary"), Mapping) else candidate_id
    if not _STABLE_ID.fullmatch(level_id) or level_id != candidate_id:
        raise PublicationError("stable candidate/level identity is invalid or not immutable")
    if str(candidate.get("background_intent", "BACKGROUND")) == "TRANSPARENT":
        raise PublicationError("transparent artwork is valid input but is not publishable to current LevelData")
    primary = pipeline.get("primary")
    if not isinstance(primary, Mapping) or primary.get("state") != "READY" or pipeline.get("disposition") != "READY":
        raise PublicationError("only a READY canonical ZIP pipeline may be published")
    load_check = primary.get("load_check")
    if not isinstance(load_check, Mapping) or load_check.get("state") != "READY" or load_check.get("disposition") != "READY":
        raise PublicationError("shipping load-check is required before publication")
    files = primary.get("files")
    if not isinstance(files, Mapping) or not isinstance(files.get("level"), str) or not isinstance(files.get("supply_plan"), str):
        raise PublicationError("canonical ZIP export is missing the level or supply plan")
    bundle_root = Path(source_bundle).expanduser().resolve()
    artwork_source = bundle_root / "artwork.png"
    if not artwork_source.is_file():
        raise PublicationError("immutable candidate artwork.png is missing")
    level_source = Path(str(files["level"])).expanduser().resolve()
    plan_source = Path(str(files["supply_plan"])).expanduser().resolve()
    if not level_source.is_file() or not plan_source.is_file():
        raise PublicationError("canonical ZIP export files are missing")
    level = _load(level_source)
    plan = _load(plan_source)
    if not isinstance(level, dict) or not isinstance(plan, dict) or level.get("id") != level_id or plan.get("levelId") != level_id:
        raise PublicationError("level and supply identities do not match the immutable candidate")
    catalog_path = root / "data" / "levels" / "catalog" / "production_catalog_v1.json"
    catalog = _load(catalog_path)
    if not isinstance(catalog, dict) or catalog.get("schema") != "scrubbots.production_catalog.v1" or not isinstance(catalog.get("entries"), list):
        raise PublicationError("production catalog authority is malformed")
    if any(isinstance(entry, Mapping) and entry.get("id") == level_id for entry in catalog["entries"]):
        raise PublicationError("catalog collision: stable level ID already exists")
    authority = load_progression_authority(root)
    score = primary.get("difficulty", {}).get("score") if isinstance(primary.get("difficulty"), Mapping) else None
    if type(score) not in {int, float}:
        raise PublicationError("official Difficulty V1 score is missing")
    tolerance = float(authority.get("challengeTolerance", {}).get("neverForceLabelOutsidePlusMinus", 5.0))
    order = level_number
    try:
        progression = describe_target(order, authority)
    except ProgressionAuthorityError as exc:
        raise PublicationError(f"explicit campaign order is not valid under current progression authority: {exc}") from exc
    if abs(float(score) - float(progression["target_challenge"])) > tolerance:
        raise PublicationError("official Difficulty V1 score does not fit its explicit CampaignBuilder target")
    difficulty_class = primary.get("difficulty", {}).get("class") if isinstance(primary.get("difficulty"), Mapping) else None
    if difficulty_class != progression["class"]:
        raise PublicationError("official Difficulty V1 class does not match the explicit CampaignBuilder cadence class")
    metadata = {
        "schema": "scrubbots.level.metadata.v1", "version": 1, "builderVersion": "LevelFactory-ZIP-V02-R01/v1",
        "id": level_id, "width": level.get("width"), "height": level.get("height"), "cellCount": len(level.get("cells", [])),
        "difficulty": primary.get("difficulty", {}).get("class") if isinstance(primary.get("difficulty"), Mapping) else None,
        "challengeScore": score, "columnCount": plan.get("columnCount"), "visiblePreviewDepth": plan.get("visiblePreviewDepth"),
        "sourceCandidateId": candidate_id, "sourceArtworkSha256": candidate.get("artwork_sha256"), "sourceGridHash": candidate.get("grid_hash"),
        "sourceLineage": candidate.get("source_lineage"),
        "pipelineRunId": pipeline.get("run_id"), "loadCheck": load_check,
        "progression": progression, "fileDigests": {},
    }
    solver_metrics = primary.get("solver_metrics", {}) if isinstance(primary.get("solver_metrics", {}), Mapping) else {}
    official = solver_metrics.get("official_difficulty_v1", {}) if isinstance(solver_metrics.get("official_difficulty_v1", {}), Mapping) else {}
    official_profile = official.get("profile", {}) if isinstance(official.get("profile", {}), Mapping) else {}
    metadata.update({
        "challengeVector": official.get("vector", official.get("challengeVector")),
        "sessionLoad": official.get("sessionLoad"),
        "dominantProfile": official_profile.get("dominant"),
        "frustrationRisk": official.get("frustrationRisk"),
        "official_difficulty_v1": dict(official),
        "noveltySignature": {"dimensions": [level.get("width"), level.get("height")], "paletteSet": candidate.get("used_colors", []), "silhouetteHash": candidate.get("grid_hash")},
    })
    paths = {
        "level": root / "data" / "levels" / f"{level_id}.json",
        "supply_plan": root / "data" / "levels" / "supply" / f"{level_id}_supply_v1.json",
        "metadata": root / "data" / "levels" / "metadata" / f"{level_id}.metadata.json",
        "preview": root / "assets" / "art" / "levels" / "previews" / f"{level_id}.png",
        "catalog": catalog_path,
    }
    if any(path.exists() for path in paths.values() if path != catalog_path):
        raise PublicationError("publication path collision: one or more target files already exist")
    entry = {"id": level_id, "order": order, "level_path": f"res://data/levels/{level_id}.json", "metadata_path": f"res://data/levels/metadata/{level_id}.metadata.json", "preview_path": f"res://assets/art/levels/previews/{level_id}.png", "supply_plan_path": f"res://data/levels/supply/{level_id}_supply_v1.json"}
    catalog_out = {**catalog, "entries": [*catalog["entries"], entry]}
    with tempfile.TemporaryDirectory(prefix=".lfx-publish-", dir=root) as staging_name:
        staging = Path(staging_name)
        staged = {"level": staging / paths["level"].relative_to(root), "supply_plan": staging / paths["supply_plan"].relative_to(root), "preview": staging / paths["preview"].relative_to(root)}
        staged["level"].parent.mkdir(parents=True, exist_ok=True); staged["supply_plan"].parent.mkdir(parents=True, exist_ok=True); staged["preview"].parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(level_source, staged["level"]); shutil.copy2(plan_source, staged["supply_plan"]); shutil.copy2(artwork_source, staged["preview"])
        metadata["fileDigests"] = {name: _sha256(path) for name, path in staged.items()}
        staged_metadata = staging / paths["metadata"].relative_to(root); staged_metadata.parent.mkdir(parents=True, exist_ok=True); staged_metadata.write_bytes(_json_bytes(metadata))
        staged_catalog = staging / paths["catalog"].relative_to(root); staged_catalog.parent.mkdir(parents=True, exist_ok=True); staged_catalog.write_bytes(_json_bytes(catalog_out))
        ordered = [paths["level"], paths["supply_plan"], paths["metadata"], paths["preview"], paths["catalog"]]
        source_paths = [staged["level"], staged["supply_plan"], staged_metadata, staged["preview"], staged_catalog]
        written: list[Path] = []
        try:
            for target, source in zip(ordered, source_paths):
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(source, target)
                written.append(target)
        except OSError as exc:
            for target in written:
                target.unlink(missing_ok=True)
            raise PublicationError(f"transaction rolled back after write failure: {exc}") from exc
    return {"disposition": "PUBLISHED", "game_project": str(root), "level_id": level_id, "order": order, "paths": {name: str(path) for name, path in paths.items()}, "file_digests": {name: _sha256(path) for name, path in paths.items()}, "progression": progression}


def publish_batch(*, game_project: str | Path | None, items: list[Mapping[str, object]]) -> dict[str, object]:
    """Stage a contiguous campaign batch and expose it through one catalog commit."""
    root = discover_game_project(game_project)
    if not items:
        raise PublicationError("release batch must contain at least one level")
    numbers = [item.get("level_number") for item in items]
    if any(type(n) is not int for n in numbers) or numbers != list(range(int(numbers[0]), int(numbers[0]) + len(numbers))):
        raise PublicationError("release batch catalog orders must be a contiguous prefix")
    catalog_path = root / "data" / "levels" / "catalog" / "production_catalog_v1.json"
    original_catalog = catalog_path.read_bytes()
    with tempfile.TemporaryDirectory(prefix=".lfx-batch-", dir=root) as temporary:
        stage = Path(temporary) / "project"
        stage.mkdir()
        for relative in ("project.godot", "data/config/level_progression_v1.json", "data/levels/catalog/production_catalog_v1.json"):
            source = root / relative; target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)
        staged_results = []
        for item in items:
            staged_results.append(publish_level(game_project=stage, candidate=item["candidate"], pipeline=item["pipeline"], source_bundle=item["source_bundle"], level_number=int(item["level_number"])))
        base_catalog = _load(catalog_path)
        final_catalog = _load(stage / "data/levels/catalog/production_catalog_v1.json")
        base_ids = {entry.get("id") for entry in base_catalog["entries"] if isinstance(entry, Mapping)}
        added = [entry for entry in final_catalog["entries"] if entry.get("id") not in base_ids]
        if [entry.get("order") for entry in added] != numbers:
            raise PublicationError("staged catalog did not retain the requested contiguous batch order")
        relatives = []
        for entry in added:
            for key in ("level_path", "metadata_path", "preview_path", "supply_plan_path"):
                relatives.append(str(entry[key]).removeprefix("res://"))
        written: list[Path] = []
        try:
            for relative in relatives:
                source = stage / relative
                target = root / relative
                if target.exists(): raise PublicationError(f"batch publication path collision: {relative}")
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(source, target); written.append(target)
            # The catalog is the batch visibility/commit point.
            staged_catalog = stage / "data/levels/catalog/production_catalog_v1.json"
            os.replace(staged_catalog, catalog_path); written.append(catalog_path)
        except Exception as exc:
            for target in written:
                if target != catalog_path: target.unlink(missing_ok=True)
            if catalog_path.read_bytes() != original_catalog:
                restore = root / ".lfx-catalog-rollback.tmp"
                restore.write_bytes(original_catalog); os.replace(restore, catalog_path)
            if isinstance(exc, PublicationError): raise
            raise PublicationError(f"batch transaction rolled back: {exc}") from exc
    return {"disposition": "PUBLISHED", "game_project": str(root), "orders": numbers, "levels": staged_results, "catalog_sha256": _sha256(catalog_path)}


__all__ = ["PublicationError", "discover_game_project", "publish_level", "publish_batch"]
