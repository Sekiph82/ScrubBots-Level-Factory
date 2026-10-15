from __future__ import annotations

import hashlib
import json
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import pytest

from scrubbots_pixel_factory import png_batch, studio_extensions as extensions


def _ready_pipeline(source_id: str, *, columns: int = 3) -> dict[str, object]:
    source_sha = source_id.removeprefix("owner-upload-")
    return {
        "schema": "scrubbots-studio-pipeline-run",
        "version": 2,
        "run_id": "pipeline-exact-attempt",
        "source_id": None,  # Real R02 producer shape; legacy top-level field was absent/null.
        "candidate_id": "candidate-owner-" + source_sha[:48],
        "disposition": "READY",
        "request": {
            "source_id": source_id,
            "activity_source_sha256": source_sha,
            "activity_run_id": "activity-exact",
            "png_batch_job_id": "png-batch-exact",
            "png_batch_item_index": 0,
            "png_batch_attempt_id": "attempt-exact",
            "column_count": columns,
        },
        "primary": {
            "state": "READY",
            "column_count": columns,
            "result": {
                "solver_status": "SOLVED",
                "solution_final": "WIN",
                "difficulty_basis": "ScrubBots Difficulty V1 test evidence",
                "solution_replay": {"ok": True, "solved": True, "finalActive": 0},
                "column_count": columns,
            },
            "files": {"level": "level.json", "supply_plan": "plan.json", "result": "result.json"},
            "load_check": {"state": "READY"},
        },
        "stages": [{"stage": "QA", "disposition": "PASS"}],
    }


def test_real_producer_shape_persists_owner_binding_before_immutable_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source_sha = hashlib.sha256(b"owner source png").hexdigest()
    source_id = "owner-upload-" + source_sha
    source_dir = tmp_path / "owner" / source_id
    source_dir.mkdir(parents=True)
    record_path = source_dir / "source.json"
    source_path = source_dir / "source.png"
    source_png_bytes = b"owner source png"
    source_path.write_bytes(source_png_bytes)
    record_path.write_text("immutable source record", encoding="utf-8")
    candidate_id = "candidate-owner-" + source_sha[:48]
    lineage = {
        "source_id": source_id,
        "source_sha256": source_sha,
        "source_record": f"level_factory/output/owner-uploads/{source_id}/source.json",
        "source_bytes_unchanged": True,
        "derivation": "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE",
    }
    bundle = SimpleNamespace(
        metadata={"generator_metadata": {"payload": {"data": {"source_lineage": lineage}}}},
        artwork=SimpleNamespace(width=20, height=20, cells=["C01"] * 400, sha256="a" * 64, grid_hash="b" * 64),
        artwork_png=source_png_bytes,
    )
    output_root = tmp_path / "factory-output"
    monkeypatch.setattr(extensions, "extensions_root", lambda: output_root)
    monkeypatch.setattr(extensions, "_source_record_paths", lambda *_args, **_kwargs: (record_path, source_path))
    monkeypatch.setattr(extensions, "validate_owner_source", lambda *_args, **_kwargs: {
        "source_sha256": source_sha, "record_path": str(record_path), "evidence_path": str(record_path),
        "exact_logical_source": True, "structural": {"disposition": "PASS"},
    })
    monkeypatch.setattr(extensions, "_derive_owner_candidate", lambda *_args, **_kwargs: (candidate_id, tmp_path / candidate_id))
    monkeypatch.setattr(extensions, "read_bundle", lambda _path: bundle)
    monkeypatch.setattr(extensions, "_canonical_cells_to_grid", lambda cells, width, height, _rules: (cells, [1]))

    class Rules:
        attestation = None
        authority = {"git_head": "pinned", "git_tree": "tree"}

        def __init__(self, _game_project: object, *, column_count: int) -> None:
            self.column_count = column_count

    class Optimizer:
        def __init__(self, rules: Rules) -> None:
            self.column_count = rules.column_count

        def run_grid(self, *_args: object, **kwargs: object) -> dict[str, object]:
            columns = self.column_count
            return {
                "solver_status": "SOLVED", "solution_final": "WIN", "difficulty": "FLOW",
                "difficulty_basis": "ScrubBots Difficulty V1 test evidence", "difficulty_score": 1,
                "solution_replay": {"ok": True, "solved": True, "finalActive": 0}, "column_count": columns,
            }

    class Exporter:
        def __init__(self, _rules: object) -> None:
            pass

        def export(self, result: dict[str, object], output: Path, level_id: str) -> dict[str, str]:
            output.mkdir(parents=True, exist_ok=True)
            level = output / f"{level_id}.json"
            plan = output / "plan.json"
            result_path = output / "result.json"
            level.write_text("{}", encoding="utf-8")
            plan.write_text(json.dumps({"columnCount": 3}), encoding="utf-8")
            result_path.write_text(json.dumps(result), encoding="utf-8")
            return {"level": str(level), "supply_plan": str(plan), "result": str(result_path)}

    from scrubbots_pixel_factory.supply_pipeline import game_rules, supply_exporter, supply_optimizer, solver_budget, verify

    monkeypatch.setattr(game_rules, "GameRules", Rules)
    monkeypatch.setattr(supply_optimizer, "SupplyOptimizer", Optimizer)
    monkeypatch.setattr(supply_exporter, "SupplyExporter", Exporter)
    monkeypatch.setattr(solver_budget, "normalize_solver_budget", lambda *_args: (25_000, 90.0))
    monkeypatch.setattr(verify, "verify_exported_supply", lambda *_args, **_kwargs: {"state": "READY"})
    monkeypatch.setattr(extensions, "list_candidates", lambda: [{"candidate_id": candidate_id}])
    monkeypatch.setattr(extensions, "_enter_candidate_release_pool", lambda *_args, **_kwargs: {"readback_verified": True, "entry_digest": "pool-proof"})
    monkeypatch.setattr("scrubbots_pixel_factory.supply_pipeline.scrubpack_identity.derive_solver_supply_identity", lambda *_args: {"identity": "bound"})

    request = {
        "column_count": 3,
        "game_project": None,
        "activity_run_id": "activity-exact",
        "activity_source_sha256": source_sha,
        "activity_source_record_sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
        "png_batch_job_id": "png-batch-exact",
        "png_batch_item_index": 0,
        "png_batch_attempt_id": "attempt-exact",
    }
    result = extensions._run_pipeline_impl(source_id=source_id, request=request)
    saved = extensions._read_json(extensions._pipeline_path(str(result["run_id"])))

    assert saved["source_id"] == source_id
    assert saved["candidate_id"] == candidate_id
    assert saved["request"]["png_batch_attempt_id"] == "attempt-exact"
    assert saved["owner_source_binding"] == {
        "source_id": source_id,
        "source_sha256": source_sha,
        "source_record_sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
        "candidate_id": candidate_id,
        "candidate_artwork_sha256": hashlib.sha256(source_png_bytes).hexdigest(),
        "candidate_grid_hash": "b" * 64,
    }
    assert png_batch._verify_column_artifacts(result, 3)
    assert {key: value for key, value in result.items() if key != "release_pool"} == saved


def test_legacy_null_source_recovers_only_exact_attempt_and_same_source(monkeypatch: pytest.MonkeyPatch) -> None:
    source_sha = "a" * 64
    source_id = "owner-upload-" + source_sha
    pipeline = _ready_pipeline(source_id)

    class PipelineRoot:
        def __truediv__(self, _name: str) -> "PipelineRoot":
            return self

        def exists(self) -> bool:
            return True

        def glob(self, _pattern: str) -> list[str]:
            return ["real-producer-shaped.json"]

    monkeypatch.setattr(extensions, "extensions_root", PipelineRoot)
    monkeypatch.setattr(extensions, "_read_json", lambda _path: pipeline)
    candidate = {"candidate_id": pipeline["candidate_id"]}
    monkeypatch.setattr(extensions, "list_candidates", lambda: [candidate])
    monkeypatch.setattr(extensions, "_enter_candidate_release_pool", lambda *_args, **_kwargs: {"readback_verified": True, "entry_digest": "exact"})
    monkeypatch.setattr(png_batch, "_candidate_has_source_lineage", lambda *_args: True)
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda *_args: True)
    monkeypatch.setattr(png_batch, "_pool_row_matches", lambda *_args: True)
    job = {"job_id": "png-batch-exact"}
    item = {
        "index": 0, "attempt_id": "attempt-exact", "activity_run_id": "activity-exact",
        "source_id": source_id, "source_sha256": source_sha, "source_record_sha256": "b" * 64, "column_count": 3,
    }

    recovered = png_batch._recover_attempt(job, item)

    assert recovered is not None
    assert recovered["pipeline"]["source_id"] is None
    assert recovered["pipeline"]["request"]["source_id"] == source_id
    assert recovered["pipeline"]["request"]["png_batch_attempt_id"] == item["attempt_id"]


def test_crash_recovery_orchestration_only_uses_isolated_evidence_gate_stubs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source_sha = "a" * 64
    source_id = "owner-upload-" + source_sha
    pipeline = _ready_pipeline(source_id)
    job_id = "png-batch-exact"
    item = {
        "index": 0, "status": "RUNNING", "attempt_id": "attempt-exact", "activity_run_id": "activity-exact",
        "source_id": source_id, "source_sha256": source_sha,
        "column_count": 3,
    }
    imported_batch = {"batch_id": "batch-exact", "items": [{"source_id": source_id}]}
    record = tmp_path / "source.json"
    record.write_text("immutable record", encoding="utf-8")
    item["source_record_sha256"] = hashlib.sha256(record.read_bytes()).hexdigest()
    png_batch_root = tmp_path / "png-batches"
    pipeline_root = tmp_path / "pipelines"
    pipeline_root.mkdir()
    (pipeline_root / "pipeline-exact.json").write_text(json.dumps(pipeline), encoding="utf-8")
    candidate = {"candidate_id": pipeline["candidate_id"]}
    monkeypatch.setattr(png_batch, "_root", lambda: png_batch_root)
    monkeypatch.setattr(png_batch, "_job_lock", lambda _job_id: nullcontext())
    monkeypatch.setattr(extensions, "extensions_root", lambda: tmp_path)
    monkeypatch.setattr(extensions, "batch_load", lambda _batch_id: {"batch": imported_batch})
    monkeypatch.setattr(extensions, "validate_owner_source", lambda *_args, **_kwargs: {
        "source_sha256": source_sha, "exact_logical_source": True, "structural": {"disposition": "PASS"},
    })
    monkeypatch.setattr(extensions, "_source_record_paths", lambda *_args, **_kwargs: (record, tmp_path / "source.png"))
    monkeypatch.setattr(extensions, "_read_json", lambda _path: pipeline)
    monkeypatch.setattr(extensions, "list_candidates", lambda: [candidate])
    monkeypatch.setattr(extensions, "_enter_candidate_release_pool", lambda *_args, **_kwargs: {"readback_verified": True, "entry_digest": "persisted-pool"})
    # This is strictly a restart/attempt/quota state test. It does not prove
    # the real artifact, candidate-lineage, or persisted Pool validators.
    monkeypatch.setattr(png_batch, "_candidate_has_source_lineage", lambda *_args: True)
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda *_args: True)
    monkeypatch.setattr(png_batch, "_pool_row_matches", lambda *_args: True)
    job = {
        "schema": png_batch.JOB_SCHEMA, "version": png_batch.JOB_VERSION, "job_id": job_id,
        "import_batch_id": "batch-exact", "batch_digest": extensions._digest(imported_batch),
        "plan_digest": "plan", "settings": {}, "state": "RUNNING", "created_at": "now", "updated_at": "now",
        "current_index": 0, "items": [item], "counts": {"total": 1, "ready": 0, "failed": 0, "rejected": 0, "skipped": 0, "remaining": 1},
        "planned_quotas": {"3": 1, "4": 0, "5": 0}, "ready_mix": {"3": 0, "4": 0, "5": 0},
    }
    png_batch._write_job(job)

    result = png_batch.run_png_batch(job_id, expected_batch_id="batch-exact", pipeline_runner=lambda **_: pytest.fail("crash recovery reran the canonical solver"))

    assert result["job"]["items"][0]["status"] == "READY"
    assert result["job"]["items"][0]["recovered_after_interruption"] is True
    assert result["job"]["ready_mix"] == {"3": 1, "4": 0, "5": 0}
    completed = png_batch.run_png_batch(job_id, expected_batch_id="batch-exact", pipeline_runner=lambda **_: pytest.fail("completed recovery reran"))
    assert completed.get("mutated") is False
    assert completed["job"]["ready_mix"] == {"3": 1, "4": 0, "5": 0}


@pytest.mark.parametrize("mismatch", ["attempt", "activity_sha", "item_index", "columns"])
def test_legacy_run_with_wrong_attempt_binding_is_not_recovered(monkeypatch: pytest.MonkeyPatch, mismatch: str) -> None:
    source_id = "owner-upload-" + "a" * 64
    pipeline = _ready_pipeline(source_id)
    request = pipeline["request"]
    if mismatch == "attempt":
        request["png_batch_attempt_id"] = "other-attempt"
    elif mismatch == "activity_sha":
        request["activity_source_sha256"] = "f" * 64
    elif mismatch == "item_index":
        request["png_batch_item_index"] = 1
    else:
        request["column_count"] = 4

    class PipelineRoot:
        def __truediv__(self, _name: str) -> "PipelineRoot":
            return self

        def exists(self) -> bool:
            return True

        def glob(self, _pattern: str) -> list[str]:
            return ["wrong-attempt.json"]

    monkeypatch.setattr(extensions, "extensions_root", PipelineRoot)
    monkeypatch.setattr(extensions, "_read_json", lambda _path: pipeline)
    item = {
        "index": 0, "attempt_id": "attempt-exact", "activity_run_id": "activity-exact",
        "source_id": source_id, "source_sha256": "a" * 64, "source_record_sha256": "b" * 64, "column_count": 3,
    }

    assert png_batch._recover_attempt({"job_id": "png-batch-exact"}, item) is None


def test_existing_four_column_ready_is_not_reused_for_three_column_quota(monkeypatch: pytest.MonkeyPatch) -> None:
    source_id = "owner-upload-" + "a" * 64
    pipeline = _ready_pipeline(source_id, columns=4)
    monkeypatch.setattr(extensions, "restore_source_run", lambda *_args, **_kwargs: {
        "state": "READY", "source_sha256": "a" * 64, "candidate_id": pipeline["candidate_id"], "pipeline": pipeline,
    })
    monkeypatch.setattr(extensions, "list_candidates", lambda: pytest.fail("wrong quota must refuse before Pool reuse"))
    item = {"source_id": source_id, "source_sha256": "a" * 64, "source_record_sha256": "b" * 64, "column_count": 3}

    assert png_batch._reuse_existing_ready({"settings": {}}, item) is None


def test_each_imported_source_gets_independent_canonical_validation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from scrubbots_pixel_factory import studio_extensions as studio

    good_sha = "a" * 64
    bad_sha = "b" * 64
    records = {"owner-upload-" + good_sha: tmp_path / "good.json", "owner-upload-" + bad_sha: tmp_path / "bad.json"}
    for path in records.values():
        path.write_text("source record", encoding="utf-8")
    monkeypatch.setattr(studio, "_source_record_paths", lambda source_id, *_args, **_kwargs: (records[source_id], tmp_path / "source.png"))
    calls: list[tuple[str, str]] = []

    def validate(source_id: str, **kwargs: object) -> dict[str, object]:
        calls.append((source_id, str(kwargs.get("game_project"))))
        good = source_id.endswith(good_sha)
        return {
            "source_sha256": good_sha if good else bad_sha,
            "exact_logical_source": good,
            "structural": {"disposition": "PASS" if good else "BLOCKED", "reason": "BAD_PALETTE"},
            "void_capability": {"state": "OPEN"},
        }

    monkeypatch.setattr(studio, "validate_owner_source", validate)
    monkeypatch.setattr(studio, "verify_owner_source", lambda source_id, **_kwargs: {
        "source_sha256": source_id.removeprefix("owner-upload-"), "original_filename": "source.png",
    })
    items = [
        {"source_id": "owner-upload-" + good_sha, "disposition": "IMPORTED", "display_path": "good.png"},
        {"source_id": "owner-upload-" + bad_sha, "disposition": "IMPORTED", "display_path": "bad.png"},
    ]

    verified = png_batch._verify_sources(items, {"game_project": "attested-runtime"})

    assert [item["status"] for item in verified] == ["QUEUED", "REJECTED"]
    assert verified[1]["reason"].startswith("BAD_PALETTE")
    assert calls == [(items[0]["source_id"], "attested-runtime"), (items[1]["source_id"], "attested-runtime")]


def test_run_rejects_job_for_different_displayed_batch_without_mutation(monkeypatch: pytest.MonkeyPatch) -> None:
    job = {"job_id": "png-batch-A", "import_batch_id": "batch-A", "state": "PAUSED", "items": []}
    monkeypatch.setattr(png_batch, "_job_lock", lambda _job_id: nullcontext())
    monkeypatch.setattr(png_batch, "_read_job", lambda _job_id: job)

    result = png_batch.run_png_batch("png-batch-A", expected_batch_id="batch-B", pipeline_runner=lambda **_: pytest.fail("must not run"))

    assert result["disposition"] == "BATCH_JOB_SOURCE_MISMATCH"
    assert result.get("job") is None


def test_restart_lookup_selects_only_job_bound_to_displayed_batch_digest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(png_batch, "_root", lambda: tmp_path / "png-batches")
    batches = {
        batch_id: {
            "schema": "scrubbots-owner-upload-batch",
            "version": 2,
            "kind": "COMPOSITE_LOADED_SOURCE_SNAPSHOT",
            "batch_id": batch_id,
            "items": [{
                "source_id": source_id,
                "source_sha256": source_id.removeprefix("owner-upload-"),
                "source_record_sha256": hashlib.sha256((batch_id + "-record").encode()).hexdigest(),
            }],
        }
        for batch_id, source_id in (("batch-A", "owner-upload-" + "a" * 64), ("batch-B", "owner-upload-" + "b" * 64))
    }
    monkeypatch.setattr(extensions, "batch_load", lambda batch_id: {"batch": batches[batch_id]})
    for job_id, batch_id in (("png-batch-a", "batch-A"), ("png-batch-b", "batch-B")):
        imported = batches[batch_id]
        png_batch._write_job({
            "schema": png_batch.JOB_SCHEMA, "version": png_batch.JOB_VERSION, "job_id": job_id,
            "import_batch_id": batch_id, "batch_digest": extensions._digest(imported), "plan_digest": job_id,
            "settings": {}, "state": "PAUSED", "created_at": "now", "updated_at": "now",
            "current_index": None, "items": [], "counts": {}, "planned_quotas": {}, "ready_mix": {},
        })

    association = png_batch.png_batch_latest("batch-B")

    assert association["disposition"] == "MATCHED"
    assert association["job"]["job_id"] == "png-batch-b"
    assert association["job"]["batch_digest"] == extensions._digest(batches["batch-B"])


def test_pool_readback_is_bound_to_pipeline_hash_and_requested_column(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source_id = "owner-upload-" + "a" * 64
    run_id = "pipeline-exact"
    root = tmp_path / "extensions"
    (root / "pipelines").mkdir(parents=True)
    pool_root = root / "release-pool"
    pool_root.mkdir()
    level = tmp_path / "level.json"
    plan = tmp_path / "plan.json"
    result = tmp_path / "result.json"
    level.write_text("{}", encoding="utf-8")
    plan.write_text(json.dumps({"columnCount": 3}), encoding="utf-8")
    result.write_text("{}", encoding="utf-8")
    pipeline = {"run_id": run_id, "candidate_id": "candidate-exact", "primary": {"files": {"level": str(level), "supply_plan": str(plan), "result": str(result)}}}
    pipeline_path = root / "pipelines" / f"{run_id}.json"
    pipeline_path.write_text(json.dumps(pipeline), encoding="utf-8")
    pipeline_sha = hashlib.sha256(pipeline_path.read_bytes()).hexdigest()
    pool_row = {
        "candidate_id": "candidate-exact", "pipeline_run_id": run_id, "pipeline_sha256": pipeline_sha,
        "source_id": source_id, "column_count": 3,
        "files": {
            "level": {"sha256": hashlib.sha256(level.read_bytes()).hexdigest()},
            "supply_plan": {"sha256": hashlib.sha256(plan.read_bytes()).hexdigest()},
        },
    }
    pool_row["entry_digest"] = hashlib.sha256(json.dumps(
        pool_row, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    (pool_root / "entry.json").write_text(json.dumps(pool_row), encoding="utf-8")
    monkeypatch.setattr(extensions, "extensions_root", lambda: root)
    monkeypatch.setattr(extensions, "_read_json", lambda path: json.loads(Path(path).read_text(encoding="utf-8")))
    from scrubbots_pixel_factory.supply_pipeline import release_pool

    monkeypatch.setattr(release_pool, "release_entries", lambda: [pool_row])
    candidate = {"candidate_id": "candidate-exact"}

    assert png_batch._pool_row_matches(pipeline, candidate, source_id, 3)
    assert not png_batch._pool_row_matches(pipeline, candidate, source_id, 4)

    # Isolate pipeline-byte drift from the missing-entry case.
    pipeline_path.write_text(json.dumps({**pipeline, "changed": True}), encoding="utf-8")
    assert not png_batch._pool_row_matches(pipeline, candidate, source_id, 3)

    # Restore the exact valid pipeline/Pool binding and prove the control again
    # immediately before changing only release_entries() to represent an empty Pool.
    pipeline_path.write_text(json.dumps(pipeline), encoding="utf-8")
    pool_row["pipeline_sha256"] = hashlib.sha256(pipeline_path.read_bytes()).hexdigest()
    pool_row["files"]["level"]["sha256"] = hashlib.sha256(level.read_bytes()).hexdigest()
    pool_row["files"]["supply_plan"]["sha256"] = hashlib.sha256(plan.read_bytes()).hexdigest()
    pool_row.pop("entry_digest")
    pool_row["entry_digest"] = hashlib.sha256(json.dumps(
        pool_row, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    (pool_root / "entry.json").write_text(json.dumps(pool_row), encoding="utf-8")
    monkeypatch.setattr(release_pool, "release_entries", lambda: [pool_row])
    assert png_batch._pool_row_matches(pipeline, candidate, source_id, 3)
    monkeypatch.setattr(release_pool, "release_entries", lambda: [])
    assert not png_batch._pool_row_matches(pipeline, candidate, source_id, 3)


def test_column_artifact_gate_rejects_wrong_columns_missing_files_and_digest_drift(tmp_path: Path) -> None:
    from scrubbots_pixel_factory.supply_pipeline.scrubpack_identity import derive_solver_supply_identity

    level = tmp_path / "level.json"
    plan = tmp_path / "plan.json"
    result_path = tmp_path / "result.json"
    level_bytes = json.dumps({"id": "synthetic-level", "version": 1, "cells": [0, 1]}, sort_keys=True).encode("utf-8")
    plan_bytes = json.dumps({
        "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": "synthetic-level",
        "columnCount": 3, "visiblePreviewDepth": 1, "maxRobotsPerBatch": 1,
        "columns": [[{"batchId": f"batch-{index}", "cid": f"C{index:02d}", "robots": 1}]
                    for index in range(1, 4)],
    }, sort_keys=True).encode("utf-8")
    authority = {"repository": "Sekiph82/Scrubbots", "branch": "main", "git_head": "a" * 40}
    result = {
        "solver_status": "SOLVED", "solution_final": "WIN", "column_count": 3,
        "solution_replay": {"ok": True, "solved": True, "finalActive": 0},
        "color_conservation_verification": {"all_ok": True},
        "solver_metrics": {"official_difficulty_v1": {"ok": True}},
    }
    result_bytes = json.dumps(result, sort_keys=True).encode("utf-8")
    level.write_bytes(level_bytes)
    plan.write_bytes(plan_bytes)
    result_path.write_bytes(result_bytes)
    artifacts = {
        "level": hashlib.sha256(level_bytes).hexdigest(),
        "supply_plan": hashlib.sha256(plan_bytes).hexdigest(),
        "result": hashlib.sha256(result_bytes).hexdigest(),
    }
    pipeline = {"primary": {
        "column_count": 3, "result": result, "authority": authority,
        "solver_supply_identity": derive_solver_supply_identity(level_bytes, plan_bytes, result, authority),
        "artifact_sha256": artifacts,
        "files": {"level": str(level), "supply_plan": str(plan), "result": str(result_path)},
    }}

    # This pure synthetic control exercises the real identity derivation
    # contract; it is not evidence of a pinned runtime or an authentic solve.
    assert png_batch._verify_column_artifacts(pipeline, 3) is True
    assert png_batch._verify_column_artifacts(pipeline, 4) is False
    assert png_batch._verify_column_artifacts({"primary": {**pipeline["primary"], "files": {
        **pipeline["primary"]["files"], "result": str(tmp_path / "missing.json"),
    }}}, 3) is False
    assert png_batch._verify_column_artifacts({"primary": {
        **pipeline["primary"], "artifact_sha256": {**artifacts, "result": "0" * 64},
    }}, 3) is False
    assert png_batch._verify_column_artifacts({"primary": {
        **pipeline["primary"], "solver_supply_identity": {"schema": "mismatched"},
    }}, 3) is False


def test_candidate_source_lineage_gate_fails_closed_on_bad_bundle_and_identity_claims(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    import hashlib
    from types import SimpleNamespace

    source_sha = "a" * 64
    source_id = "owner-upload-" + source_sha
    root = tmp_path / "repo"
    (root / "bundle").mkdir(parents=True)
    monkeypatch.setattr(extensions, "_repository_root", lambda: root)
    candidate = {
        "candidate_id": "candidate-lineage",
        "source_path": "bundle",
        "artwork_sha256": hashlib.sha256(b"canonical artwork").hexdigest(),
        "grid_hash": "grid-exact",
    }

    # Exercise the actual bundle parser's corrupt/incomplete bundle rejection.
    assert not png_batch._candidate_has_source_lineage(candidate, source_id, source_sha)

    from scrubbots_pixel_factory.output import bundle as bundle_module

    good_lineage = {
        "source_id": source_id,
        "source_sha256": source_sha,
        "derivation": "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE",
    }
    parsed = SimpleNamespace(
        metadata={"generator_metadata": {"payload": {"data": {"source_lineage": good_lineage}}}},
        artwork_png=b"canonical artwork",
        artwork=SimpleNamespace(grid_hash="grid-exact"),
    )
    monkeypatch.setattr(bundle_module, "read_bundle", lambda _path: parsed)
    assert png_batch._candidate_has_source_lineage(candidate, source_id, source_sha)

    for field, wrong in (
        ("source_id", "owner-upload-" + "b" * 64),
        ("source_sha256", "b" * 64),
        ("derivation", "RESAMPLED_OR_UNATTESTED"),
    ):
        lineage = {**good_lineage, field: wrong}
        parsed.metadata["generator_metadata"]["payload"]["data"]["source_lineage"] = lineage
        assert not png_batch._candidate_has_source_lineage(candidate, source_id, source_sha)

    parsed.metadata["generator_metadata"]["payload"]["data"]["source_lineage"] = good_lineage
    assert not png_batch._candidate_has_source_lineage(
        {**candidate, "artwork_sha256": "0" * 64}, source_id, source_sha,
    )
    assert not png_batch._candidate_has_source_lineage(
        {**candidate, "grid_hash": "wrong-grid"}, source_id, source_sha,
    )


def test_batch_ui_does_not_gate_on_selected_thumbnail_preflight() -> None:
    source = Path("level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    run_batch = source.split("func _run_png_batch() -> void:", 1)[1].split("func _pipeline_worker", 1)[0]
    dispatch = source.split("func _dispatch_png_batch_job(job_id: String, batch_id: String) -> void:", 1)[1].split("func _request_batch_pause", 1)[0]

    assert "_pinned_source_preflight_ok" not in run_batch
    assert "_dispatch_png_batch_job(_batch_job_id, _batch_import_id)" in run_batch
    assert '"expected_batch_id": batch_id' in dispatch
    assert "BATCH_JOB_SOURCE_MISMATCH" in run_batch

