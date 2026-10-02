from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory.supply_pipeline.release_pool import ReleaseError, _game_authority


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def _authority_fixture(root: Path) -> tuple[dict, dict]:
    progression = {
        "schema": "scrubbots-level-progression/v1", "version": 1, "cadenceLength": 1,
        "cadence": [{"slot": 1, "class": "EASY", "role": "release", "modifier": 0, "noveltyTarget": 0}],
        "lanes": {"EASY": {"base": 50, "growth": 0}}, "progression": {"tauCycles": 20},
        "challengeTolerance": {"preferredWhenPoolIsLarge": 2, "defaultPlusMinus": 3.5, "neverForceLabelOutsidePlusMinus": 5},
        "recoveryGuards": [],
    }
    analyzer = {"schema": "scrubbots-level-difficulty-analysis/v1", "version": 1, "analyzerVersion": "m53-level-difficulty-analyzer/v1", "operationalDefinitions": {"similarity": {"fields": ["challengeVector", "paletteSet", "dimensions"]}, "profiles": {"source": "official"}}}
    _write_json(root / "data/config/level_progression_v1.json", progression)
    _write_json(root / "data/config/level_difficulty_analysis_v1.json", analyzer)
    _write_json(root / "data/levels/catalog/production_catalog_v1.json", {"schema": "scrubbots.production_catalog.v1", "entries": [{"id": "old-nine", "order": 9, "level_path": "res://data/levels/old-nine.json", "metadata_path": "res://data/levels/metadata/old-nine.json"}, {"id": "old-ten", "order": 10, "level_path": "res://data/levels/old-ten.json", "metadata_path": "res://data/levels/metadata/old-ten.json"}]})
    rules = root / "scripts/data/difficulty_rules.gd"
    rules.parent.mkdir(parents=True, exist_ok=True)
    rules.write_text("const ENVELOPE_MIN := 20\nconst ENVELOPE_MAX := 59\n", encoding="utf-8")
    docs = root / "docs/10_LEVEL_FACTORY_GENERATION_SCORING_ARCHITECTURE.md"
    docs.parent.mkdir(parents=True, exist_ok=True)
    docs.write_text("Campaign Builder\n", encoding="utf-8")
    (root / "docs/08_PIXEL_ART_PALETTE_RULES.md").write_text("global 3..12 used-color envelope\n", encoding="utf-8")
    levels = []
    for order, identity, profile in ((9, "old-nine", "FLOW"), (10, "old-ten", "COLOR")):
        level_path = root / f"data/levels/{identity}.json"
        level_path.write_text(f'{{"id":"{identity}"}}', encoding="utf-8")
        levels.append({
            "order": order, "id": identity, "levelSha256": hashlib.sha256(level_path.read_bytes()).hexdigest(),
            "profile": {"dominant": profile, "scores": {profile: 0.8}, "runnerUp": "ROUTE"},
            "vector": {"W": 0.1, "C": 0.2, "A": 0.3, "U": 0.4, "B": 0.5, "R": 0.6, "S": 0.7},
            "challengeScore": 50.0, "slot": order, "width": 20, "height": 20, "palette": ["C01", "C02", "C03"],
            "frustrationRisk": {"scalar": None},
        })
        _write_json(root / f"data/levels/metadata/{identity}.json", {"id": identity})
    _write_json(root / "coordination/sessions/M53-C001/evidence/first10_difficulty_v1.json", {
        "schema": "scrubbots.m53.first10_difficulty.v1", "provenance": {"analyzerVersion": analyzer["analyzerVersion"]},
        "analysisConfig": analyzer, "levels": levels,
    })
    return progression, analyzer


def test_game_authority_resolves_two_hash_bound_profiles_from_current_difficulty_evidence(tmp_path: Path) -> None:
    _authority_fixture(tmp_path)
    catalog, authority = _game_authority(tmp_path)
    assert [record["order"] for record in authority["_catalog_tail"]] == [9, 10]
    assert [record["dominant_profile"] for record in authority["_catalog_tail"]] == ["FLOW", "COLOR"]
    assert all(record["evidence_source"] == "current-game M53 Difficulty V1 evidence" for record in authority["_catalog_tail"])
    assert all(len(record["challenge_vector"]) == 7 and record["signature"]["dimensions"] == [20, 20] for record in authority["_catalog_tail"])


def test_game_authority_fails_closed_when_tail_level_no_longer_matches_official_evidence(tmp_path: Path) -> None:
    _authority_fixture(tmp_path)
    (tmp_path / "data/levels/old-ten.json").write_text('{"id":"tampered"}', encoding="utf-8")
    with pytest.raises(ReleaseError, match="CATALOG_TAIL_DIFFICULTY_EVIDENCE_UNAVAILABLE"):
        _game_authority(tmp_path)
