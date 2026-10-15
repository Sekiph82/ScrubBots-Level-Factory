from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scrubbots_pixel_factory import studio_extensions
from scrubbots_pixel_factory.supply_pipeline import pinned_game_source
from scrubbots_pixel_factory.supply_pipeline.release_pool import (
    ReleaseError,
    _canonical_official_difficulty,
    enter_release_pool,
)


RELEASE_ROOT = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio")
SOURCE_ID_002 = "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
SOURCE_ID_003 = "owner-upload-e26b81cc6cc364364e3bb1b5eefbb79b88556c49aabbb5d8ca8cdc6fabda8fe1"


def test_release_adapter_reads_real_002_nested_official_difficulty_and_fails_closed_without_profile():
    pipeline_root = RELEASE_ROOT / "level_factory" / "output" / "studio-extensions" / "pipelines"
    runs = []
    for path in pipeline_root.glob("pipeline-*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        request = payload.get("request", {})
        if request.get("source_id") == SOURCE_ID_002 and payload.get("disposition") == "READY":
            runs.append(payload)
    assert runs, "the immutable saved 002 READY records are the read-only producer fixture"
    run = max(runs, key=lambda value: str(value.get("created_at", "")))
    primary = run["primary"]
    official = primary["result"]["solver_metrics"]["official_difficulty_v1"]
    assert _canonical_official_difficulty(primary) == official
    assert "challengeScore" in official and "vector" in official
    if "profile" not in official:
        with patch.object(studio_extensions, "_repository_root", return_value=RELEASE_ROOT), patch.object(
            studio_extensions, "extensions_root", return_value=RELEASE_ROOT / "level_factory" / "output" / "studio-extensions"
        ):
            candidate = next(item for item in studio_extensions.list_candidates() if item["candidate_id"] == run["candidate_id"])
            try:
                enter_release_pool(candidate, run)
            except ReleaseError as exc:
                assert "profile.dominant" in str(exc)
            else:
                raise AssertionError("the historical saved run must not receive a synthesized official profile")


def test_pinned_analyzer_profile_is_preserved_by_the_solver_bridge():
    bridge = (
        Path(__file__).resolve().parents[2]
        / "src/scrubbots_pixel_factory/supply_pipeline/godot/solver_bridge.gd"
    ).read_text(encoding="utf-8")
    assert '"profile": sc.get("profile", {})' in bridge


def test_source_003_uses_independent_identity_and_attested_void_authority_without_persisting():
    game = RELEASE_ROOT / "level_factory" / "output" / "current-game-runtime" / pinned_game_source.PINNED_MAIN_SHA
    source_dir = RELEASE_ROOT / "level_factory" / "output" / "owner-uploads" / SOURCE_ID_003
    assert game.is_dir() and source_dir.is_dir()
    with patch.object(pinned_game_source, "expected_runtime_root", return_value=game):
        report = studio_extensions.validate_owner_source(
            SOURCE_ID_003, persist=False, game_project=game, source_directory=source_dir
        )
    assert report["source_authority"]["source_id"] == SOURCE_ID_003
    assert report["source_authority"]["source_sha256"] == SOURCE_ID_003.removeprefix("owner-upload-")
    assert report["game_authority"]["repository"] == "Sekiph82/Scrubbots"
    assert report["game_authority"]["commit"] == pinned_game_source.PINNED_MAIN_SHA
    assert report["game_authority"]["tree"] == pinned_game_source.PINNED_TREE_SHA
    assert report["void_capability"]["state"] == "OPEN"
    assert report["exact_logical_source"] is True
    assert report["structural"]["disposition"] == "PASS"
    assert report["original_dimensions"] == {"width": 32, "height": 32}
    assert report["alpha"]["transparent_count"] == 612


def test_latest_002_ready_run_restores_only_when_all_saved_identity_hashes_match():
    output_root = RELEASE_ROOT / "level_factory" / "output"
    source_dir = output_root / "owner-uploads" / SOURCE_ID_002
    game = output_root / "current-game-runtime" / pinned_game_source.PINNED_MAIN_SHA
    assert source_dir.is_dir() and game.is_dir()
    with patch.object(studio_extensions, "_repository_root", return_value=RELEASE_ROOT), patch.object(
        studio_extensions, "extensions_root", return_value=output_root / "studio-extensions"
    ), patch.object(pinned_game_source, "expected_runtime_root", return_value=game):
        restored = studio_extensions.restore_source_run(
            SOURCE_ID_002, game_project=game, source_directory=source_dir
        )
    assert restored["state"] == "READY"
    assert restored["source_id"] == SOURCE_ID_002
    assert restored["source_sha256"] == SOURCE_ID_002.removeprefix("owner-upload-")
    assert restored["pipeline"]["disposition"] == "READY"
    assert restored["activity_run_id"] == restored["pipeline"]["request"]["activity_run_id"]
    assert set(restored["artifact_sha256"]) == {"level", "supply_plan", "result"}
    from scrubbots_pixel_factory.supply_pipeline.release_pool import release_entries

    matching = [
        entry for entry in release_entries()
        if entry.get("candidate_id") == restored.get("candidate_id")
        and entry.get("pipeline_run_id") == restored["pipeline"].get("run_id")
    ]
    if matching:
        assert restored["owner_review_status"]["pool_state"] == "IN_RELEASE_POOL"
        assert restored["owner_review_status"]["entry_digest"] == matching[0]["entry_digest"]
    else:
        assert restored["owner_review_status"]["pool_state"] == "ACCEPT_RECORDED_BUT_POOL_DENIED"
        assert "profile.dominant" in restored["owner_review_status"]["reason"]


def test_existing_002_accept_is_idempotent_and_does_not_create_duplicate_receipt():
    output_root = RELEASE_ROOT / "level_factory" / "output"
    with patch.object(studio_extensions, "_repository_root", return_value=RELEASE_ROOT), patch.object(
        studio_extensions, "extensions_root", return_value=output_root / "studio-extensions"
    ):
        candidate_id = next(
            run["candidate_id"]
            for path in (output_root / "studio-extensions" / "pipelines").glob("pipeline-*.json")
            for run in [json.loads(path.read_text(encoding="utf-8"))]
            if run.get("request", {}).get("source_id") == SOURCE_ID_002 and run.get("disposition") == "READY"
        )
        previous = studio_extensions._latest_review(candidate_id)
        assert previous and previous["disposition"] == "ACCEPT"
        from scrubbots_pixel_factory.supply_pipeline.release_pool import release_entries

        pool_before = release_entries()
        existing_entry = next((entry for entry in pool_before if entry.get("candidate_id") == candidate_id), None)
        # This test is read-only against the owner Release installation. Reuse
        # its existing pool read-back, if present; never create a missing entry.
        def read_only_pool_projection(candidate, *, pipeline=None):
            if existing_entry is None:
                return {"disposition": "NOT_ENTERED", "reason": "No pre-existing Pool read-back."}
            return {
                "disposition": "ENTERED_RELEASE_POOL",
                "entry_digest": existing_entry.get("entry_digest"),
                "readback_verified": True,
            }

        with patch.object(studio_extensions, "_write_json") as write:
            with patch.object(studio_extensions, "_enter_candidate_release_pool", side_effect=read_only_pool_projection):
                outcome = studio_extensions.record_owner_review(candidate_id, "ACCEPT")
        assert outcome["idempotent"] is True
        assert outcome["review_id"] == previous["review_id"]
        assert outcome["publication"]["disposition"] == (
            "ENTERED_RELEASE_POOL" if existing_entry is not None else "NOT_ENTERED"
        )
        assert release_entries() == pool_before
        write.assert_not_called()
