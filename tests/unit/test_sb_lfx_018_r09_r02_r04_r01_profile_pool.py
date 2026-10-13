from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scrubbots_pixel_factory import studio_extensions
from scrubbots_pixel_factory.supply_pipeline import release_pool


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _ready_fixture(root: Path):
    output = root / "studio-extensions"
    pipelines = output / "pipelines"
    pipelines.mkdir(parents=True)
    bundle = root / "candidate"
    bundle.mkdir()
    artwork = bundle / "artwork.png"
    artwork.write_bytes(b"PNG-fixture")
    level = root / "level.json"
    plan = root / "plan.json"
    level.write_text("{}", encoding="utf-8")
    plan.write_text("{}", encoding="utf-8")
    official = {
        "ok": True, "vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
        "challengeScore": 50.0,
        "profile": {"dominant": "FLOW", "scores": {"FLOW": 0.8}, "runnerUp": "COLOR"},
    }
    run = {
        "schema": "scrubbots-pipeline/v2", "version": 2, "run_id": "pipeline-fixture-one",
        "candidate_id": "candidate-fixture", "request": {"activity_run_id": "run-a"},
        "disposition": "READY", "created_at": "2026-10-13T00:00:00Z",
        "primary": {
            "state": "READY", "column_count": 4,
            "difficulty": {"score": 50.0, "class": "MEDIUM"},
            "files": {"level": str(level), "supply_plan": str(plan)},
            "solver_metrics": {"official_difficulty_v1": official},
        },
    }
    pipeline_path = pipelines / f"{run['run_id']}.json"
    pipeline_path.write_text(json.dumps(run, sort_keys=True), encoding="utf-8")
    candidate = {
        "candidate_id": run["candidate_id"], "source_path": "candidate",
        "artwork_sha256": _sha(artwork.read_bytes()), "grid_hash": "grid-fixture",
        "width": 1, "height": 1, "used_colors": ["C01"],
    }
    def candidate_list(): return [candidate]
    def latest_run(_candidate_id): return run
    def latest_review(_candidate_id): return None
    def pipeline_file(_run_id): return pipeline_path
    return output, run, candidate, pipeline_path, candidate_list, latest_run, latest_review, pipeline_file


def _pool_patches(root, output, candidate_list, latest_run, latest_review, pipeline_file):
    return (
        patch.object(studio_extensions, "extensions_root", return_value=output),
        patch.object(studio_extensions, "_repository_root", return_value=root),
        patch.object(studio_extensions, "list_candidates", side_effect=candidate_list),
        patch.object(studio_extensions, "_latest_ready_pipeline", side_effect=latest_run),
        patch.object(studio_extensions, "_latest_review", side_effect=latest_review),
        patch.object(studio_extensions, "_pipeline_path", side_effect=pipeline_file),
        patch.object(release_pool, "GameRules", create=True),
    )


def test_ready_auto_release_pool_entry_reads_back_exactly_once(tmp_path):
    output, run, candidate, _path, candidates, latest, review, pipeline_file = _ready_fixture(tmp_path)
    context = _pool_patches(tmp_path, output, candidates, latest, review, pipeline_file)
    with context[0], context[1], context[2], context[3], context[4], context[5], patch(
        "scrubbots_pixel_factory.supply_pipeline.game_rules.GameRules"
    ) as rules:
        rules.return_value.classify.return_value = "MEDIUM"
        first = release_pool.enter_release_pool(candidate, run)
        assert first["disposition"] == "ENTERED_RELEASE_POOL"
        entries = release_pool.release_entries()
        assert len(entries) == 1
        assert entries[0]["eligibility_source"] == "READY_AUTO"
        assert entries[0]["official_profile_provenance"]["kind"] == "DIRECT"
        assert release_pool.enter_release_pool(candidate, run)["entry_digest"] == first["entry_digest"]
        assert len(release_pool.release_entries()) == 1


def test_score_and_class_gates_reject_mismatch_and_only_allow_documented_derived_rounding():
    primary = {"difficulty": {"score": 48.82, "class": "MEDIUM"}, "column_count": 4}
    official = {"challengeScore": 48.8166775742989}
    derived = {"kind": "DERIVED"}
    with patch("scrubbots_pixel_factory.supply_pipeline.game_rules.GameRules") as rules:
        rules.return_value.classify.return_value = "MEDIUM"
        release_pool._validate_score_and_class(primary, official, derived)
        with pytest.raises(release_pool.ReleaseError, match="exactly equal"):
            release_pool._validate_score_and_class(primary, official, {"kind": "DIRECT"})
        primary["difficulty"]["class"] = "HARD"
        with pytest.raises(release_pool.ReleaseError, match="class authority"):
            release_pool._validate_score_and_class(primary, official, derived)
        primary["difficulty"].update(score=48.83, **{"class": "MEDIUM"})
        with pytest.raises(release_pool.ReleaseError, match="two-decimal"):
            release_pool._validate_score_and_class(primary, official, derived)


def test_official_vector_and_profile_shape_reject_tampered_values():
    with pytest.raises(release_pool.ReleaseError, match="vector"):
        release_pool._official_challenge_vector({"vector": [0.1] * 6})
    with pytest.raises(release_pool.ReleaseError, match="profile.dominant"):
        release_pool._official_profile({"profile": {"dominant": "MADE_UP"}})


def test_canonical_output_is_per_activity_run_and_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: tmp_path)
    first = studio_extensions._canonical_run_output_dir("candidate-abc", "activity-one")
    second = studio_extensions._canonical_run_output_dir("candidate-abc", "activity-two")
    assert first.parent == second.parent
    assert first != second
    assert first.parent.name == "candidate-abc"
    with pytest.raises(studio_extensions.StudioExtensionError, match="unsafe path"):
        studio_extensions._canonical_run_output_dir("../escape", "activity-three")
