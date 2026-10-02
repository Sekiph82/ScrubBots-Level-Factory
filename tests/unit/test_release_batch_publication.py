from __future__ import annotations

import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory.supply_pipeline import game_publisher
from scrubbots_pixel_factory.supply_pipeline.game_publisher import PublicationError, publish_batch


def _project(tmp_path: Path):
    root = tmp_path / "game"
    (root / "data/config").mkdir(parents=True)
    (root / "data/levels/catalog").mkdir(parents=True)
    (root / "scripts").mkdir(parents=True)
    (root / "data/palettes").mkdir(parents=True)
    (root / "data/palettes/scrubbots_palette_v3.json").write_text("{}", encoding="utf-8")
    (root / "project.godot").write_text("config_version=5\n", encoding="utf-8")
    (root / "data/config/level_progression_v1.json").write_text(json.dumps({
        "schema": "scrubbots-level-progression/v1", "version": 1, "cadenceLength": 1,
        "cadence": [{"slot": 1, "class": "EASY", "role": "recovery", "modifier": 0, "noveltyTarget": 0}],
        "lanes": {"EASY": {"base": 50, "growth": 0}}, "progression": {"tauCycles": 20},
        "challengeTolerance": {"neverForceLabelOutsidePlusMinus": 5}, "recoveryGuards": [],
    }), encoding="utf-8")
    catalog = {"schema": "scrubbots.production_catalog.v1", "entries": [{"id": "prior", "order": 7, "level_path": "res://data/levels/prior.json", "metadata_path": "res://data/levels/metadata/prior.metadata.json", "preview_path": None, "supply_plan_path": ""}]}
    catalog_path = root / "data/levels/catalog/production_catalog_v1.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    items = []
    for i, number in enumerate((8, 9)):
        identity = f"batch-level-{i}"
        bundle = tmp_path / f"bundle-{i}"; bundle.mkdir(); (bundle / "artwork.png").write_bytes(b"pixels" + bytes([i]))
        level = tmp_path / f"level-{i}.json"; level.write_text(json.dumps({"id": identity, "width": 20, "height": 20, "cells": ["C01"] * 400}), encoding="utf-8")
        supply = tmp_path / f"supply-{i}.json"; supply.write_text(json.dumps({"levelId": identity, "columnCount": 4, "visiblePreviewDepth": 3}), encoding="utf-8")
        items.append({"level_number": number, "candidate": {"candidate_id": identity, "artwork_sha256": "a" * 64, "grid_hash": "b" * 64, "source_lineage": {"source_sha256": "c" * 64}, "background_intent": "BACKGROUND"}, "pipeline": {"run_id": f"run-{i}", "disposition": "READY", "primary": {"state": "READY", "load_check": {"state": "READY", "disposition": "READY"}, "files": {"level": str(level), "supply_plan": str(supply)}, "difficulty": {"score": 50, "class": "EASY"}}}, "source_bundle": bundle})
    return root, catalog_path, catalog, items


def test_batch_publishes_one_contiguous_catalog_update_and_preserves_existing_entries(tmp_path: Path, monkeypatch):
    root, catalog_path, original, items = _project(tmp_path)
    monkeypatch.setattr(game_publisher, "_validate_proposed_catalog", lambda _project: None)
    result = publish_batch(game_project=root, items=items)
    current = json.loads(catalog_path.read_text(encoding="utf-8"))
    assert result["orders"] == [8, 9]
    assert current["entries"][0] == original["entries"][0]
    assert [entry["order"] for entry in current["entries"][-2:]] == [8, 9]
    assert all((root / "data/levels" / f"batch-level-{i}.json").is_file() for i in range(2))
    assert all((root / "data/levels/supply" / f"batch-level-{i}_supply_v1.json").is_file() for i in range(2))


def test_batch_failure_rolls_back_every_new_file_and_catalog(tmp_path: Path, monkeypatch):
    root, catalog_path, _original, items = _project(tmp_path)
    monkeypatch.setattr(game_publisher, "_validate_proposed_catalog", lambda _project: None)
    catalog_bytes = catalog_path.read_bytes()
    original_replace = game_publisher.os.replace
    failed = False

    def fail_during_commit(source, target):
        nonlocal failed
        target_path = Path(target)
        if not failed and target_path.parent == root / "data/levels" and target_path.name == "batch-level-1.json":
            failed = True
            raise OSError("injected commit interruption")
        return original_replace(source, target)

    monkeypatch.setattr(game_publisher.os, "replace", fail_during_commit)
    with pytest.raises(PublicationError, match="rolled back"):
        publish_batch(game_project=root, items=items)
    assert failed
    assert catalog_path.read_bytes() == catalog_bytes
    assert not list((root / "data/levels").glob("batch-level-*.json"))
    assert not list((root / "data/levels/supply").glob("batch-level-*_supply_v1.json"))


def test_batch_rejects_later_compatible_order_across_catalog_gap_before_writes(tmp_path: Path, monkeypatch):
    root, catalog_path, _original, items = _project(tmp_path)
    monkeypatch.setattr(game_publisher, "_validate_proposed_catalog", lambda _project: None)
    items[0]["level_number"] = 9
    items[1]["level_number"] = 10
    original = catalog_path.read_bytes()
    with pytest.raises(PublicationError, match="exact next catalog order 8"):
        publish_batch(game_project=root, items=items)
    assert catalog_path.read_bytes() == original
    assert not (root / "data/levels/batch-level-0.json").exists()


def test_batch_fails_closed_when_current_challenge_tolerance_is_missing(tmp_path: Path, monkeypatch):
    root, catalog_path, _original, items = _project(tmp_path)
    monkeypatch.setattr(game_publisher, "_validate_proposed_catalog", lambda _project: None)
    progression_path = root / "data/config/level_progression_v1.json"
    progression = json.loads(progression_path.read_text(encoding="utf-8"))
    progression["challengeTolerance"] = {}
    progression_path.write_text(json.dumps(progression), encoding="utf-8")
    original = catalog_path.read_bytes()
    with pytest.raises(PublicationError, match="challengeTolerance.neverForceLabelOutsidePlusMinus"):
        publish_batch(game_project=root, items=items)
    assert catalog_path.read_bytes() == original
    assert not (root / "data/levels/batch-level-0.json").exists()


def test_proposed_catalog_validation_failure_has_zero_production_writes(tmp_path: Path, monkeypatch):
    root, catalog_path, _original, items = _project(tmp_path)
    catalog_bytes = catalog_path.read_bytes()
    def reject_staged_catalog(_project):
        raise PublicationError("staged LevelCatalog/DifficultyV1CatalogCheck rejected proposed content")
    monkeypatch.setattr(game_publisher, "_validate_proposed_catalog", reject_staged_catalog)
    with pytest.raises(PublicationError, match="staged LevelCatalog"):
        publish_batch(game_project=root, items=items)
    assert catalog_path.read_bytes() == catalog_bytes
    assert not list((root / "data/levels").glob("batch-level-*.json"))
    assert not list((root / "data/levels/supply").glob("batch-level-*_supply_v1.json"))
    assert not list((root / "data/levels/metadata").glob("batch-level-*.metadata.json"))
    assert not list((root / "assets").rglob("batch-level-*.png")) if (root / "assets").exists() else True
