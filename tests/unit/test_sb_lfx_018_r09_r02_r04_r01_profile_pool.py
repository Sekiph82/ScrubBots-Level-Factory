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


def test_release_pool_index_distinguishes_owner_status_events_from_candidate_entries():
    status_event = {
        "schema": "scrubbots-owner-release-library-event/v1",
        "event_sha256": "a" * 64,
        "status": "READY",
    }
    candidate_entry = {
        "schema": "scrubbots-release-pool-entry/v1",
        "entry_digest": "b" * 64,
    }
    assert release_pool._is_owner_release_library_event(status_event)
    assert not release_pool._is_owner_release_library_event(candidate_entry)
    assert not release_pool._is_owner_release_library_event({"schema": "unknown"})


def test_release_pool_ready_index_ignores_owner_status_projection_without_digest():
    """An owner READY status projection must not poison candidate receipt discovery."""
    from scrubbots_pixel_factory import owner_art_storage

    ready = Path("repo/data/Release Pool/Ready")
    owner_event_path = ready / ("owner-upload-" + "a" * 64 + ".json")
    candidate_path = ready / "candidate-fixture-pipeline-fixture-ready.json"
    owner_event = {"schema": "scrubbots-owner-release-library-event/v1", "source_id": owner_event_path.stem,
                   "status": "READY", "event_sha256": "b" * 64}
    candidate_entry = {"schema": "scrubbots-release-pool-entry/v1", "candidate_id": "candidate-fixture",
                       "pipeline_run_id": "pipeline-fixture", "entry_digest": "c" * 64}
    entries = {owner_event_path.name: owner_event, candidate_path.name: candidate_entry}

    with patch.object(release_pool, "_pool_root", return_value=ready), \
         patch.object(release_pool, "_pool_roots", return_value=(ready,)), \
         patch.object(studio_extensions, "_repository_root", return_value=Path("repo")), \
         patch.object(owner_art_storage, "_verify_path_under_root"), \
         patch.object(owner_art_storage, "_is_reparse_point", return_value=False), \
         patch.object(Path, "resolve", lambda self: self), \
         patch.object(Path, "is_dir", lambda self: self == ready), \
         patch.object(Path, "is_file", lambda self: True), \
         patch.object(Path, "glob", lambda self, _pattern: [owner_event_path, candidate_path] if self == ready else []), \
         patch.object(release_pool, "_json", side_effect=lambda path: entries[path.name]):
        assert release_pool.entry_paths() == [candidate_path]


def _ready_fixture(root: Path):
    output = root / "studio-extensions"
    pipelines = root / "data" / "Release Pool" / "Ready" / "Pipelines"
    pipelines.mkdir(parents=True)
    candidate_id = "candidate-fixture"
    bundle = root / candidate_id
    bundle.mkdir()
    artwork = bundle / "artwork.png"
    artwork.write_bytes(b"PNG-fixture")
    (bundle / "metadata.json").write_text(json.dumps({
        "generator_metadata": {"payload": {"data": {"source_lineage": {
            "derivation": "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE",
            "source_id": "owner-upload-fixture",
        }}}},
    }), encoding="utf-8")
    work = root / "data" / "Release Pool" / "Pending" / "Pipelines" / "Work" / "fixture-run"
    work.mkdir(parents=True)
    level = work / "level.json"
    plan = work / "plan.json"
    level.write_text(json.dumps({"id": "level-fixture"}), encoding="utf-8")
    plan.write_text(json.dumps({"levelId": "level-fixture", "intendedColumnClicks": [1]}), encoding="utf-8")
    real_play_path = work / "real_play_result_v2.json"
    real_play = {
        "schema": "scrubbots.real_play_file_result.v2", "model": "real_play_v1",
        "mode": "canonical_60hz", "canonicalDt": "1/60", "verdict": "WON_CANONICAL", "exitCode": 0,
        "levelFile": str(level.resolve()), "planFile": str(plan.resolve()), "levelId": "level-fixture",
        "levelSha256": hashlib.sha256(level.read_bytes()).hexdigest(),
        "planSha256": hashlib.sha256(plan.read_bytes()).hexdigest(), "planClicks": [1],
        "sourceSha256": "a" * 64, "gameCommit": "a" * 40, "runId": "fixture-run", "timestamp": "2026-11-07T12:00:00Z",
        "searched": False,
        "perDt": {"1/60": {"won": True, "final": {"supplyExhausted": True, "targetsCleared": True,
            "slotsEmpty": True, "activeRobots": 0, "boardResidue": 0}}},
    }
    real_play_path.write_text(json.dumps(real_play), encoding="utf-8")
    official = {
        "ok": True, "vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
        "challengeScore": 50.0,
        "profile": {"dominant": "FLOW", "scores": {"FLOW": 0.8}, "runnerUp": "COLOR"},
    }
    run = {
        "schema": "scrubbots-pipeline/v2", "version": 2, "run_id": "pipeline-fixture-one",
        "candidate_id": candidate_id, "request": {"activity_run_id": "run-a"},
        "disposition": "READY", "created_at": "2026-10-13T00:00:00Z",
        "primary": {
            "state": "READY", "column_count": 4,
            "acceptance": {"solver_status": "SOLVED", "replay": "WIN"},
            "difficulty": {"score": 50.0, "class": "MEDIUM"},
            "files": {"level": str(level), "supply_plan": str(plan), "real_play_result": str(real_play_path)},
            "solver_metrics": {"official_difficulty_v1": official},
        },
    }
    pipeline_path = pipelines / f"{run['run_id']}.json"
    pipeline_path.write_text(json.dumps(run, sort_keys=True), encoding="utf-8")
    candidate = {
        "candidate_id": run["candidate_id"], "source_path": candidate_id,
        "artwork_sha256": _sha(artwork.read_bytes()), "grid_hash": "grid-fixture",
        "width": 1, "height": 1, "used_colors": ["C01"],
    }
    def candidate_list(): return [candidate]
    def latest_run(_candidate_id): return run
    def latest_review(_candidate_id): return None
    def pipeline_file(_run_id, *, status=None): return pipeline_path
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
    ) as rules, patch.object(
        release_pool,
        "validate_pool_candidate_provenance",
        return_value={"candidate_class": "PRODUCTION_CANDIDATE", "source_sha256": "a" * 64},
    ), patch.object(
        studio_extensions,
        "verify_owner_source",
        return_value={"source_sha256": "a" * 64, "source_bytes_sha256": "a" * 64},
    ):
        rules.return_value.classify.return_value = "MEDIUM"
        first = release_pool.enter_release_pool(candidate, run)
        assert first["disposition"] == "ENTERED_RELEASE_POOL"
        canonical_ready = tmp_path / "data" / "Release Pool" / "Ready"
        assert release_pool._pool_root() == canonical_ready
        assert any(path.parent == canonical_ready for path in release_pool.entry_paths(candidate["candidate_id"]))
        entries = release_pool.release_entries()
        assert len(entries) == 1
        assert entries[0]["eligibility_source"] == "READY_AUTO"
        assert entries[0]["official_profile_provenance"]["kind"] == "DIRECT"
        assert release_pool.enter_release_pool(candidate, run)["entry_digest"] == first["entry_digest"]
        assert len(release_pool.release_entries()) == 1


def test_release_pool_lists_only_canonical_ready_receipt_paths(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    extension_root = repository / "level_factory" / "output" / "studio-extensions"
    legacy = extension_root / "release-pool"
    legacy.mkdir(parents=True)
    legacy_receipt = legacy / "candidate-legacy-pipeline-legacy-ready.json"
    legacy_receipt.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: extension_root)

    assert release_pool._pool_root() == repository / "data" / "Release Pool" / "Ready"
    assert release_pool.entry_paths("candidate-legacy") == []
    assert legacy_receipt.is_file()  # Historical bytes are untouched but are no longer active.
    assert not (repository / "data" / "Release Pool" / "Ready").exists()


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
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda: tmp_path)
    first = studio_extensions._canonical_run_output_dir("candidate-abc", "activity-one")
    second = studio_extensions._canonical_run_output_dir("candidate-abc", "activity-two")
    assert first.parent == second.parent
    assert first != second
    assert first.parent.name == "candidate-abc"
    assert first.is_relative_to(tmp_path / "data" / "Release Pool" / "Pending" / "Pipelines" / "Work")
    with pytest.raises(studio_extensions.StudioExtensionError, match="unsafe path"):
        studio_extensions._canonical_run_output_dir("../escape", "activity-three")


def test_primary_image_path_cannot_bypass_canonical_factory_acceptance(tmp_path, monkeypatch):
    from scrubbots_pixel_factory.supply_pipeline import primary

    repository = tmp_path / "repository"
    repository.mkdir()
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: repository / "level_factory" / "output" / "studio-extensions")
    image = tmp_path / "input.png"
    image.write_bytes(b"fixture image path; primary runner is isolated")
    calls = []

    def unavailable_primary(_image_path, *, output, **_kwargs):
        calls.append((str(_image_path), str(output)))
        return {"state": "UNAVAILABLE", "reason": "isolated fixture"}

    monkeypatch.setattr(primary, "run_primary_supply_pipeline", unavailable_primary)
    result = studio_extensions.run_pipeline(request={"image_path": str(image)})

    assert result["disposition"] == "BLOCKED", result
    assert result["route"] == "DIRECT_IMAGE_PATH_RETIRED"
    assert "Pixellab/Final" in result["reason"]
    assert calls == []
    assert not (repository / "data" / "Release Pool" / "Pending" / "Pipelines" / "Work").exists()
    assert not (repository / "level_factory" / "output" / "studio-extensions" / "primary-supply").exists()


def test_explicit_primary_workdir_rejects_external_output_path(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    repository.mkdir()
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda: repository)
    outside = tmp_path / "outside-work"

    with pytest.raises(studio_extensions.StudioExtensionError, match="must stay under data/Release Pool"):
        studio_extensions._primary_work_output_dir(
            str(outside), identity="primary-image", activity_run_id="activity-external-fixture",
        )
    assert not outside.exists()
