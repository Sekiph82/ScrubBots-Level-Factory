from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scrubbots_pixel_factory import studio_extensions
from scrubbots_pixel_factory.supply_pipeline import pinned_game_source, release_pool


PROFILE = {
    "dominant": "COLOR", "runnerUp": "ROUTE",
    "scores": {
        "COLOR": 0.595974592170614, "FLOW": 0.491442744140379,
        "FORTRESS": 0.406108251021549, "MARATHON": -0.160183091219728,
        "ROUTE": 0.524585427301204,
    },
}


def test_historical_profile_supplement_binds_real_source_run_analyzer_and_is_tamper_evident(tmp_path):
    source_id = "owner-upload-test-source"
    candidate_id = "candidate-test-source"
    run_id = "pipeline-test-profile-run"
    repository = tmp_path / "repo"
    runtime = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio\level_factory\output\current-game-runtime\aef60a616d4ac401e9dfac15df6fe56e671c0053")
    source_record = repository / "level_factory" / "output" / "owner-uploads" / source_id / "source.json"
    source_record.parent.mkdir(parents=True)
    source_record.write_text('{"source_id":"owner-upload-test-source"}', encoding="utf-8")
    candidate_bundle = repository / "level_factory" / "output" / "studio-derived-candidates" / candidate_id
    candidate_bundle.mkdir(parents=True)
    metadata = {"generator_metadata": {"payload": {"data": {"source_lineage": {
        "derivation": "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE",
        "source_id": source_id,
        "source_sha256": source_id.removeprefix("owner-upload-"),
        "source_record": f"level_factory/output/owner-uploads/{source_id}/source.json",
    }}}}}
    (candidate_bundle / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    extensions = repository / "level_factory" / "output" / "studio-extensions"
    pipeline_path = extensions / "pipelines" / f"{run_id}.json"
    pipeline_path.parent.mkdir(parents=True)
    pipeline = {
        "run_id": run_id, "candidate_id": candidate_id,
        "request": {"source_id": source_id}, "disposition": "READY",
        "primary": {
            "state": "READY",
            "authority": {"git_head": pinned_game_source.PINNED_MAIN_SHA, "git_tree": pinned_game_source.PINNED_TREE_SHA},
            "solver_supply_identity": {"identity_sha256": "solver-fixture"},
            "result": {"solver_metrics": {"official_difficulty_v1": {
                "ok": True, "vector": [0.245925159801821, 0.611507793811217, 0.713455265535767,
                    0.314177286356822, 0.498039215686275, 0.33571558906664, 0.580441390530011],
                "challengeScore": 48.8166775742989,
            }}},
        },
    }
    pipeline_path.write_text(json.dumps(pipeline, sort_keys=True), encoding="utf-8")
    candidate = {"candidate_id": candidate_id, "source_path": f"level_factory/output/studio-derived-candidates/{candidate_id}"}
    with patch.object(studio_extensions, "_repository_root", return_value=repository), \
         patch.object(studio_extensions, "extensions_root", return_value=extensions), \
         patch.object(studio_extensions, "_pipeline_path", return_value=pipeline_path), \
         patch.object(pinned_game_source, "expected_runtime_root", return_value=runtime):
        written = release_pool.write_historical_profile_supplement(candidate, pipeline)
        profile, proof = release_pool._resolve_official_profile(
            candidate, pipeline, pipeline["primary"]["result"]["solver_metrics"]["official_difficulty_v1"]
        )
        assert profile == PROFILE
        assert proof["kind"] == "DERIVED"
        assert proof["supplement_sha256"] == written["sha256"]
        supplement_path = Path(written["path"])
        payload = json.loads(supplement_path.read_text(encoding="utf-8"))
        payload["profile"]["dominant"] = "MARATHON"
        supplement_path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(release_pool.ReleaseError, match="chain, analyzer authority, or digest"):
            release_pool._resolve_official_profile(
                candidate, pipeline, pipeline["primary"]["result"]["solver_metrics"]["official_difficulty_v1"]
            )
