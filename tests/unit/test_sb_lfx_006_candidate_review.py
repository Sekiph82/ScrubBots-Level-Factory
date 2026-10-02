from __future__ import annotations

import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory import GenerationRequest, GeneratorRouter, export_candidate
from scrubbots_pixel_factory.studio_extensions import candidate_inbox, extensions_root, record_owner_review


def test_candidate_inbox_uses_real_bundle_and_review_history_is_append_only(tmp_path: Path) -> None:
    destination = Path("level_factory/output/.lfx-006-test/candidates")
    destination.mkdir(parents=True, exist_ok=True)
    candidate = GeneratorRouter().generate_candidate(GenerationRequest("EASY", 123, "MASK", width=20, height=20))
    candidate_id = "lfx006-review-candidate"
    path = export_candidate(candidate, candidate_id, destination)
    before = {item.name: item.read_bytes() for item in path.iterdir()}
    try:
        inbox = candidate_inbox()
        assert any(item["candidate_id"] == candidate_id for item in inbox["candidates"])
        accepted = record_owner_review(candidate_id, "ACCEPT", "owner accepted", "keep")
        assert accepted["publication"]["disposition"] == "NOT_ENTERED_NOT_READY"
        rejected = record_owner_review(candidate_id, "REJECT", "second review", "revisit")
        assert rejected["previous_review_id"] == accepted["review_id"]
        assert len(list((extensions_root() / "owner-review").glob(f"review-{candidate_id}-*.json"))) == 2
        after = {item.name: item.read_bytes() for item in path.iterdir()}
        assert after == before
    finally:
        if path.exists():
            for item in path.iterdir(): item.unlink()
            path.rmdir()
        if destination.exists(): destination.rmdir()
        if destination.parent.exists(): destination.parent.rmdir()
        for item in (extensions_root() / "owner-review").glob(f"review-{candidate_id}-*.json"):
            item.unlink()


def test_ready_owner_accept_enters_release_pool_without_publication(tmp_path: Path, monkeypatch) -> None:
    from scrubbots_pixel_factory import studio_extensions as studio
    from scrubbots_pixel_factory.supply_pipeline import game_publisher
    from scrubbots_pixel_factory.supply_pipeline.release_pool import release_entries

    evidence_root = tmp_path / "extensions"
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence_root)
    monkeypatch.setattr(studio, "_repository_root", lambda: tmp_path)
    candidate = {"candidate_id": "accepted-candidate", "artwork_sha256": "a" * 64, "grid_hash": "b" * 64, "width": 20, "height": 20, "used_colors": ["C01", "C02", "C03"], "source_path": "bundle", "source_lineage": {"source_sha256": "c" * 64}, "background_intent": "BACKGROUND"}
    bundle = tmp_path / "bundle"; bundle.mkdir(); (bundle / "artwork.png").write_bytes(b"pixels")
    level_file = tmp_path / "level.json"; level_file.write_text("{}", encoding="utf-8")
    supply_file = tmp_path / "supply.json"; supply_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(studio, "list_candidates", lambda: [candidate])
    pipeline = {"schema": studio.PIPELINE_SCHEMA, "version": 2, "run_id": "pipeline-ready", "candidate_id": candidate["candidate_id"], "request": {}, "disposition": "READY", "primary": {"state": "READY", "difficulty": {"score": 50.0, "class": "EASY"}, "files": {"level": str(level_file), "supply_plan": str(supply_file)}, "solver_metrics": {"official_difficulty_v1": {"ok": True, "vector": [0.1] * 7, "sessionLoad": 20}}}}
    pipeline_path = studio._pipeline_path(pipeline["run_id"])
    pipeline_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_path.write_text(json.dumps(pipeline), encoding="utf-8")
    monkeypatch.setattr(game_publisher, "publish_level", lambda **_kwargs: pytest.fail("ACCEPT must not publish"))

    accepted = studio.record_owner_review(candidate["candidate_id"], "ACCEPT", "approved", "")
    assert accepted["publication"]["publication"] == "OWNER_ACCEPT_RELEASE_POOL_ONLY"
    assert accepted["publication"]["disposition"] == "ENTERED_RELEASE_POOL"
    pool = release_entries()
    assert len(pool) == 1
    assert pool[0]["candidate_id"] == candidate["candidate_id"]
    assert pool[0]["challenge_vector"] == [0.1] * 7
