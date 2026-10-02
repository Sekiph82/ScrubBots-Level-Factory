from __future__ import annotations

from pathlib import Path

import pytest

from scrubbots_pixel_factory import studio_extensions as studio
from scrubbots_pixel_factory.supply_pipeline import release_pool
from scrubbots_pixel_factory.supply_pipeline.campaign_builder import CampaignError


def _authority():
    return {"schema": "scrubbots-level-progression/v1", "version": 1, "cadenceLength": 1, "cadence": [{"slot": 1, "class": "EASY", "role": "release", "modifier": 0, "noveltyTarget": 0}], "lanes": {"EASY": {"base": 50, "growth": 0}}, "progression": {"tauCycles": 20}, "challengeTolerance": {"preferredWhenPoolIsLarge": 2, "defaultPlusMinus": 3.5, "neverForceLabelOutsidePlusMinus": 5}, "recoveryGuards": [], "_production_envelope": {"min_dimension": 20, "max_dimension": 59, "min_colors": 3, "max_colors": 12}}


def _pool():
    return [{"candidate_id": f"release-{i}", "challenge_score": 50.0, "difficulty_class": "EASY", "dominant_profile": ("FLOW", "COLOR")[i], "challenge_vector": [float(i % 2)] * 7, "width": 20 if i == 0 else 59, "height": 20 if i == 0 else 59, "used_colors": [f"C{n:02d}" for n in range(1, 4)] if i == 0 else [f"C{n:02d}" for n in range(4, 7)], "signature": {"dimensions": [20 if i == 0 else 59, 20 if i == 0 else 59], "paletteSet": [f"C{n:02d}" for n in range(1, 4)] if i == 0 else [f"C{n:02d}" for n in range(4, 7)], "challengeVector": [float(i % 2)] * 7}, "pipeline": {"run_id": f"run-{i}"}, "source_bundle": f"bundle-{i}", "candidate": {"candidate_id": f"release-{i}"}} for i in range(2)]


def test_approve_revalidates_current_plan_and_submits_only_contiguous_prefix(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(studio, "extensions_root", lambda: tmp_path / "extensions")
    monkeypatch.setattr(studio, "_repository_root", lambda: tmp_path)
    monkeypatch.setattr(release_pool, "discover_game_project", lambda _path=None: tmp_path / "game")
    monkeypatch.setattr(release_pool, "_game_authority", lambda _game: ({"schema": "scrubbots.production_catalog.v1", "entries": []}, _authority()))
    entries = _pool()
    monkeypatch.setattr(release_pool, "release_entries", lambda: entries)
    published = []
    monkeypatch.setattr(release_pool, "publish_batch", lambda **kwargs: published.append(kwargs["items"]) or {"disposition": "PUBLISHED", "orders": [1, 2]})

    plan = release_pool.build_release_plan(k=2)
    result = release_pool.approve_release_plan(plan_hash=plan["plan_hash"])
    assert result["disposition"] == "PUBLISHED"
    assert result["approved_orders"] == [1, 2]
    assert [item["level_number"] for item in published[0]] == [1, 2]
    with pytest.raises(release_pool.ReleaseError, match="exact campaign plan hash"):
        release_pool.approve_release_plan(plan_hash="0" * 64)


def test_approval_fails_when_release_pool_changes_since_plan(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(studio, "extensions_root", lambda: tmp_path / "extensions")
    monkeypatch.setattr(studio, "_repository_root", lambda: tmp_path)
    monkeypatch.setattr(release_pool, "discover_game_project", lambda _path=None: tmp_path / "game")
    authority = _authority(); catalog = {"schema": "scrubbots.production_catalog.v1", "entries": []}
    monkeypatch.setattr(release_pool, "_game_authority", lambda _game: (catalog, authority))
    entries = _pool()
    monkeypatch.setattr(release_pool, "release_entries", lambda: entries)
    plan = release_pool.build_release_plan(k=2)
    changed = _pool(); changed[0]["challenge_score"] = 52.0
    monkeypatch.setattr(release_pool, "release_entries", lambda: changed)
    with pytest.raises(release_pool.ReleaseError, match="inputs or locked sequence changed"):
        release_pool.approve_release_plan(plan_hash=plan["plan_hash"])
