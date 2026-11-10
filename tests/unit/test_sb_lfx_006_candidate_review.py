from __future__ import annotations

from scrubbots_pixel_factory.core.request import LegacyGenerationRequest as _LegacyGenerationRequest  # explicit legacy/research fixture

import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory import GenerationRequest, GeneratorRouter, export_candidate
from scrubbots_pixel_factory.studio_extensions import candidate_inbox, extensions_root, record_owner_review


def test_candidate_inbox_uses_real_bundle_and_review_history_is_append_only(tmp_path: Path, monkeypatch) -> None:
    # Isolated repository: never write test candidates or reviews into owner data.
    from scrubbots_pixel_factory import studio_extensions as studio

    monkeypatch.setattr(studio, "_repository_root", lambda *_args, **_kwargs: tmp_path)
    destination = tmp_path / "data" / "Level Factory" / "Workspace" / "Candidates"
    destination.mkdir(parents=True)
    candidate = GeneratorRouter().generate_candidate(GenerationRequest("EASY", 123, "MASK", width=20, height=20))
    candidate_id = "lfx006-review-candidate"
    path = export_candidate(candidate, candidate_id, destination)
    before = {item.name: item.read_bytes() for item in path.iterdir()}
    inbox = candidate_inbox()
    assert any(item["candidate_id"] == candidate_id for item in inbox["candidates"])
    accepted = record_owner_review(candidate_id, "ACCEPT", "owner accepted", "keep")
    assert accepted["publication"]["disposition"] == "NOT_ENTERED_NOT_READY"
    rejected = record_owner_review(candidate_id, "REJECT", "second review", "revisit")
    assert rejected["previous_review_id"] == accepted["review_id"]
    assert len(list((studio.extensions_root() / "owner-review").glob(f"review-{candidate_id}-*.json"))) == 2
    assert str(studio.extensions_root()).startswith(str(tmp_path.resolve()))
    after = {item.name: item.read_bytes() for item in path.iterdir()}
    assert after == before


def test_incomplete_run_cannot_enter_release_pool_on_owner_accept(tmp_path: Path, monkeypatch) -> None:
    from scrubbots_pixel_factory import studio_extensions as studio
    from scrubbots_pixel_factory.supply_pipeline import game_publisher
    from scrubbots_pixel_factory.supply_pipeline.release_pool import release_entries

    evidence_root = tmp_path / "extensions"
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence_root)
    monkeypatch.setattr(studio, "_repository_root", lambda *_args, **_kwargs: tmp_path)
    candidate = {"candidate_id": "accepted-candidate", "artwork_sha256": "a" * 64, "grid_hash": "b" * 64, "width": 20, "height": 20, "used_colors": ["C01", "C02", "C03"], "source_path": "bundle", "source_lineage": {"source_sha256": "c" * 64}, "background_intent": "BACKGROUND"}
    bundle = tmp_path / "bundle"; bundle.mkdir(); (bundle / "artwork.png").write_bytes(b"pixels")
    level_file = tmp_path / "level.json"; level_file.write_text("{}", encoding="utf-8")
    supply_file = tmp_path / "supply.json"; supply_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(studio, "list_candidates", lambda: [candidate])
    pipeline = {"schema": studio.PIPELINE_SCHEMA, "version": 2, "run_id": "pipeline-incomplete", "candidate_id": candidate["candidate_id"], "request": {}, "disposition": "UNAVAILABLE", "primary": {"state": "UNAVAILABLE", "difficulty": {"score": 50.0, "class": "EASY"}, "files": {"level": str(level_file), "supply_plan": str(supply_file)}}}
    pipeline_path = studio._pipeline_path(pipeline["run_id"])
    pipeline_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_path.write_text(json.dumps(pipeline), encoding="utf-8")
    monkeypatch.setattr(game_publisher, "publish_level", lambda **_kwargs: pytest.fail("ACCEPT must not publish"))

    accepted = studio.record_owner_review(candidate["candidate_id"], "ACCEPT", "approved", "")
    assert accepted["publication"]["disposition"] == "NOT_ENTERED_NOT_READY"
    pool = release_entries()
    assert not any(entry.get("candidate_id") == candidate["candidate_id"] for entry in pool)


def test_ready_owner_accept_without_official_nested_profile_fails_closed(tmp_path: Path, monkeypatch) -> None:
    from scrubbots_pixel_factory import studio_extensions as studio

    evidence_root = tmp_path / "extensions"
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence_root)
    monkeypatch.setattr(studio, "_repository_root", lambda *_args, **_kwargs: tmp_path)
    candidate = {"candidate_id": "accepted-candidate", "artwork_sha256": "a" * 64, "grid_hash": "b" * 64, "width": 20, "height": 20, "used_colors": ["C01", "C02", "C03"], "source_path": "bundle", "source_lineage": {"source_sha256": "c" * 64}, "background_intent": "BACKGROUND"}
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "artwork.png").write_bytes(b"pixels")
    level_file = tmp_path / "level.json"
    level_file.write_text("{}", encoding="utf-8")
    supply_file = tmp_path / "supply.json"
    supply_file.write_text("{}", encoding="utf-8")
    pipeline = {"schema": studio.PIPELINE_SCHEMA, "version": 2, "run_id": "pipeline-ready", "candidate_id": candidate["candidate_id"], "request": {}, "disposition": "READY", "primary": {"state": "READY", "difficulty": {"score": 50.0, "class": "EASY"}, "files": {"level": str(level_file), "supply_plan": str(supply_file)}, "solver_metrics": {"official_difficulty_v1": {"ok": True, "vector": [0.1] * 7, "challengeScore": 50.0}}}}
    pipeline_path = studio._pipeline_path(pipeline["run_id"])
    pipeline_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_path.write_text(json.dumps(pipeline), encoding="utf-8")
    monkeypatch.setattr(studio, "list_candidates", lambda: [candidate])
    accepted = studio.record_owner_review(candidate["candidate_id"], "ACCEPT", "approved", "")
    assert accepted["publication"]["disposition"] == "NOT_ENTERED"
    # Since the 2026-11 provenance gate this bundle-less candidate is stopped
    # before the profile check; the profile.dominant gate itself is covered by
    # test_sb_lfx_018_r09_r02_r04_r01_profile_pool.
    assert "production classification is unavailable" in accepted["publication"]["reason"]

# These tests exercise explicit historical/research behavior, not the current production request.
GenerationRequest = _LegacyGenerationRequest
