from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory import png_batch
from scrubbots_pixel_factory import studio_extensions


def _pending_status(monkeypatch: pytest.MonkeyPatch, items, repository: Path | None = None) -> None:
    """New solver jobs start only from current Release Pool PENDING rows (2026-11).

    Serve those rows for the synthetic items; with a repository, every Release
    Pool write of the run also lands in that isolated root, never owner data.
    """
    from scrubbots_pixel_factory import owner_art_storage, owner_release_library

    rows = [{"source_id": str(item["source_id"]), "source_sha256": str(item.get("source_sha256", "")),
             "provider": "PIXELLAB", "status": "PENDING"} for item in items]
    monkeypatch.setattr(owner_release_library, "list_records", lambda *_args, **_kwargs: {"records": [dict(row) for row in rows]})
    if repository is not None:
        repository.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(owner_art_storage, "factory_repository_root", lambda *_args, **_kwargs: repository)
        from scrubbots_pixel_factory import studio_extensions as extensions

        monkeypatch.setattr(extensions, "_repository_root", lambda *_args, **_kwargs: repository)


@pytest.mark.parametrize(
    ("count", "expected"),
    [
        (9, {3: 4, 4: 4, 5: 1}),
        (40, {3: 18, 4: 16, 5: 6}),
        (100, {3: 45, 4: 40, 5: 15}),
        (150, {3: 68, 4: 60, 5: 22}),
        (304, {3: 137, 4: 122, 5: 45}),
    ],
)
def test_largest_remainder_quotas_match_locked_mix(count: int, expected: dict[int, int]) -> None:
    assert png_batch.largest_remainder_quotas(count) == expected


def test_assignments_are_deterministic_interleaved_and_exact() -> None:
    ids = [f"owner-upload-{index:064x}" for index in range(304)]
    assignment = png_batch.assign_columns(ids)
    assert assignment == png_batch.assign_columns(ids)
    assert {column: assignment.count(column) for column in (3, 4, 5)} == {3: 137, 4: 122, 5: 45}
    assert max((len(list(group)) for _key, group in __import__("itertools").groupby(assignment))) <= 3


def test_batch_planner_accepts_304_sources_without_touching_disk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source_ids = [f"owner-upload-{index:064x}" for index in range(304)]
    imported = {"batch_id": "batch-304-in-memory", "items": [
        {"index": index, "source_id": source_id, "disposition": "IMPORTED"}
        for index, source_id in enumerate(source_ids)
    ]}
    monkeypatch.setattr(studio_extensions, "batch_load", lambda _batch_id: {"batch": imported})
    _pending_status(monkeypatch, imported["items"])
    monkeypatch.setattr(
        png_batch, "_verify_sources",
        lambda items, _settings: [
            {"index": item["index"], "source_id": item["source_id"], "status": "QUEUED"}
            for item in items
        ],
    )
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda _pipeline, _columns: True)
    # Paths that are never created: _write_job is captured and the job lock is a no-op.
    monkeypatch.setattr(png_batch, "_job_path", lambda job_id: tmp_path / "never-written" / "jobs" / f"{job_id}.json")
    monkeypatch.setattr(png_batch, "_job_lock", lambda _job_id: __import__("contextlib").nullcontext())
    monkeypatch.setattr(png_batch, "_configured_game_project", lambda _settings: "pinned-runtime")
    captured: dict[str, object] = {}
    monkeypatch.setattr(png_batch, "_write_job", lambda job: captured.update(job) or job)

    result = png_batch.create_png_batch("batch-304-in-memory")
    assert not (tmp_path / "never-written").exists()

    assert result["state"] == "SUCCESS"
    assert result["disposition"] == "CREATED"
    assert len(captured["items"]) == 304
    assert captured["planned_quotas"] == {"3": 137, "4": 122, "5": 45}


def test_batch_planner_excludes_only_44_verified_ready_sources_and_queues_260(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source_ids = [f"owner-upload-{index:064x}" for index in range(304)]
    full = {"batch_id": "batch-loaded-304", "items": [
        {"index": index, "source_id": source_id, "source_sha256": source_id.removeprefix("owner-upload-"), "disposition": "ALREADY_IMPORTED"}
        for index, source_id in enumerate(source_ids)
    ]}
    remaining_ids = source_ids[44:]
    subset = {"batch_id": "batch-loaded-260", "items": [
        {"index": index, "source_id": source_id, "source_sha256": source_id.removeprefix("owner-upload-"), "disposition": "ALREADY_IMPORTED"}
        for index, source_id in enumerate(remaining_ids)
    ]}
    ready = {
        source_id.removeprefix("owner-upload-"): {
            "source_id": source_id, "candidate_id": f"candidate-{index}",
            "pipeline_run_id": f"pipeline-{index}", "ready_job_id": "prior-ready-job",
        }
        for index, source_id in enumerate(source_ids[:44])
    }
    captured: dict[str, object] = {}
    monkeypatch.setattr(studio_extensions, "batch_load", lambda batch_id: {"batch": full if batch_id == full["batch_id"] else subset})
    _pending_status(monkeypatch, full["items"])
    monkeypatch.setattr(studio_extensions, "create_loaded_png_batch", lambda ids: subset if list(ids) == remaining_ids else {})
    monkeypatch.setattr(png_batch, "_verified_ready_sources", lambda _items: ready)
    monkeypatch.setattr(png_batch, "_configured_game_project", lambda _settings: "pinned-runtime")
    monkeypatch.setattr(png_batch, "_verify_sources", lambda items, _settings: [
        {"index": index, "source_id": item["source_id"], "source_sha256": item["source_sha256"],
         "source_record_sha256": "a" * 64, "status": "QUEUED"}
        for index, item in enumerate(items)
    ])
    monkeypatch.setattr(png_batch, "_root", lambda: tmp_path / "never-written")
    monkeypatch.setattr(png_batch, "_job_path", lambda job_id: tmp_path / "never-written" / "jobs" / f"{job_id}.json")
    monkeypatch.setattr(png_batch, "_job_lock", lambda _job_id: __import__("contextlib").nullcontext())
    monkeypatch.setattr(png_batch, "_write_job", lambda job: captured.update(job) or job)

    result = png_batch.create_png_batch(full["batch_id"], {"game_project": "pinned-runtime"})

    assert result["disposition"] == "CREATED"
    assert len(captured["items"]) == 260
    assert captured["inventory_source_count"] == 304
    assert captured["snapshot_source_count"] == 260
    assert captured["import_batch_id"] == subset["batch_id"]
    assert len(captured["excluded_ready_sources"]) == 44
    assert {item["source_id"] for item in captured["items"]}.isdisjoint(source_ids[:44])
    assert captured["planned_quotas"] == {"3": 117, "4": 104, "5": 39}


def test_missing_pinned_project_blocks_without_persisting_a_rejected_job(monkeypatch: pytest.MonkeyPatch) -> None:
    imported = {"batch_id": "batch-missing-runtime", "items": [{"source_id": "owner-upload-" + "1" * 64}]}
    monkeypatch.setattr(studio_extensions, "batch_load", lambda _batch_id: {"batch": imported})
    _pending_status(monkeypatch, imported["items"])
    monkeypatch.setattr(png_batch, "_configured_game_project", lambda _settings: None)
    monkeypatch.setattr(png_batch, "_write_job", lambda _job: pytest.fail("must not persist a missing-runtime job"))

    result = png_batch.create_png_batch(imported["batch_id"], {"game_project": "missing-runtime"})

    assert result["state"] == "BLOCKED"
    assert result["disposition"] == "PINNED_GAME_PROJECT_MISSING"
    assert result["job"] == {}


def test_new_png_batch_jobs_use_canonical_batches_jobs_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # The legacy studio-extensions/png-batches resume path was removed with the
    # canonical data rebuild (c0d940f5, 2026-11-08); jobs live only here now.
    repository = tmp_path / "repository"
    repository.mkdir()
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda *_args, **_kwargs: repository)

    new_path = png_batch._job_path("png-batch-new-fixture")
    assert new_path == repository / "data/Level Factory/Batches/Jobs/jobs/png-batch-new-fixture.json"
    with pytest.raises(ValueError, match="malformed"):
        png_batch._job_path("../escape")


def _make_batch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, source_count: int = 4) -> tuple[str, list[dict[str, object]]]:
    """Build synthetic inputs for batch-orchestration contracts only.

    Source-record validation is stubbed here, so tests using this helper do not
    prove real owner-source eligibility or canonical READY evidence.
    """
    root = tmp_path / "repository" / "data" / "Level Factory" / "Batches" / "Jobs"
    monkeypatch.setattr(png_batch, "_root", lambda: root)
    records = tmp_path / "owner-uploads"
    records.mkdir()
    items: list[dict[str, object]] = []
    by_id: dict[str, dict[str, str]] = {}
    for index in range(source_count):
        digest = hashlib.sha256(f"source-{index}".encode()).hexdigest()
        source_id = "owner-upload-" + digest
        record = records / f"{index}.json"
        record.write_text(json.dumps({"index": index}), encoding="utf-8")
        by_id[source_id] = {"sha": digest, "record": str(record)}
        items.append({"index": index, "display_path": f"source-{index}.png", "source_id": source_id,
                      "source_sha256": digest, "disposition": "IMPORTED"})

    from scrubbots_pixel_factory import studio_extensions as extensions

    batch = {"schema": "scrubbots-owner-upload-batch", "version": 1, "batch_id": "batch-test", "items": items}
    monkeypatch.setattr(extensions, "batch_load", lambda _batch_id: {"batch": batch})
    monkeypatch.setattr(extensions, "_digest", lambda value: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest())
    monkeypatch.setattr(
        extensions,
        "verify_owner_source",
        lambda source_id, **_kwargs: {"source_sha256": by_id[source_id]["sha"], "original_filename": f"{source_id[-4:]}.png",
                                      "source_path": str(Path(by_id[source_id]["record"]).with_suffix(".png"))},
    )
    monkeypatch.setattr(extensions, "validate_owner_source", lambda source_id, **_kwargs: {
        "source_sha256": by_id[source_id]["sha"],
        "exact_logical_source": True,
        "structural": {"disposition": "PASS"},
    })
    monkeypatch.setattr(extensions, "_source_record_paths", lambda source_id, *_args, **_kwargs: (Path(by_id[source_id]["record"]), Path("unused.png")))
    monkeypatch.setattr(extensions, "restore_source_run", lambda *args, **kwargs: {"state": "SOURCE_ONLY"})
    _pending_status(monkeypatch, items, tmp_path / "repository")
    # Jobs are bound to a pinned game project; orchestration tests use a fixed pin.
    monkeypatch.setattr(png_batch, "_configured_game_project", lambda _settings: "pinned-runtime")
    return "batch-test", items


def _ready_result(source_id: str, run_id: str, request: dict[str, object] | None = None) -> dict[str, object]:
    bound_request = dict(request or {})
    bound_request.update({
        "source_id": source_id,
        "activity_source_sha256": source_id.removeprefix("owner-upload-"),
    })
    bound_request.setdefault("activity_run_id", f"activity-{run_id}")
    columns = int(bound_request.get("column_count", 3))
    return {
        "disposition": "READY",
        "source_id": source_id,
        "candidate_id": "candidate-" + source_id[-8:],
        "run_id": run_id,
        "request": bound_request,
        "primary": {
            "state": "READY",
            "column_count": columns,
            "result": {
                "solver_status": "SOLVED", "solution_final": "WIN", "difficulty_basis": "ScrubBots Difficulty V1",
                "solution_replay": {"ok": True, "solved": True, "finalActive": 0}, "column_count": columns,
            },
            "load_check": {"state": "READY"},
            "files": {"result": f"{run_id}.json"},
        },
        "stages": [{"stage": "QA", "disposition": "PASS"}],
        "release_pool": {"readback_verified": True, "entry_digest": "verified"},
    }


def test_sequential_runner_orchestration_only_passes_columns_and_continues_failures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    batch_id, items = _make_batch(tmp_path, monkeypatch, 9)
    from scrubbots_pixel_factory import studio_extensions as extensions

    # Fake runner outputs exercise batch ordering/checkpoint bookkeeping only.
    # Real source, artifact, lineage, and Pool gates are tested independently.
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda _pipeline, _columns: True)
    job = png_batch.create_png_batch(batch_id)["job"]
    calls: list[tuple[str, int]] = []

    def fake_runner(*, source_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append((source_id, int(request["column_count"])))
        if source_id == str(items[1]["source_id"]):
            return {"disposition": "UNAVAILABLE", "source_id": source_id, "reason": "bounded fake failure"}
        return _ready_result(source_id, f"run-{len(calls)}", request)

    monkeypatch.setattr(png_batch, "_recover_attempt", lambda _job, _item: None)
    result = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=fake_runner)
    stored = result["job"]
    assert result["disposition"] == "FINISHED_WITH_FAILURES"
    assert len(calls) == 9
    assert [item["status"] for item in stored["items"]].count("READY") == 8
    assert [item["status"] for item in stored["items"]].count("FAILED") == 1
    for source_id, column_count in calls:
        item = next(row for row in stored["items"] if row["source_id"] == source_id)
        assert item["column_count"] == column_count
    repeat = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=lambda **_args: pytest.fail("completed items must never rerun"))
    assert repeat["disposition"] == "FINISHED_WITH_FAILURES" and repeat.get("mutated") is False
    assert extensions._digest(extensions.batch_load(batch_id)["batch"]) == stored["batch_digest"]


def test_duplicate_source_scheduling_orchestration_only_deduplicates_identity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    batch_id, items = _make_batch(tmp_path, monkeypatch, 3)
    from scrubbots_pixel_factory import studio_extensions as extensions

    imported = extensions.batch_load(batch_id)["batch"]
    imported["items"].append(dict(items[0]))
    monkeypatch.setattr(extensions, "batch_load", lambda _batch_id: {"batch": imported})
    job = png_batch.create_png_batch(batch_id)["job"]
    scheduled = [item for item in job["items"] if item["status"] == "QUEUED"]
    assert len(scheduled) == 3
    assert job["items"][-1]["status"] == "SKIPPED_DUPLICATE"
    assert job["items"][-1]["duplicate_of"] == items[0]["source_id"]


def test_resume_orchestration_only_retries_the_interrupted_item(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    batch_id, _items = _make_batch(tmp_path, monkeypatch, 3)
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda _pipeline, _columns: True)
    job = png_batch.create_png_batch(batch_id)["job"]
    calls: list[str] = []

    def interrupted_runner(*, source_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append(source_id)
        if len(calls) == 2:
            raise KeyboardInterrupt("simulated process loss after durable RUNNING checkpoint")
        return _ready_result(source_id, f"run-{len(calls)}", request)

    monkeypatch.setattr(png_batch, "_recover_attempt", lambda _job, _item: None)
    with pytest.raises(KeyboardInterrupt):
        png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=interrupted_runner)
    interrupted = png_batch.png_batch_status(str(job["job_id"]))["job"]
    assert interrupted["items"][0]["status"] == "READY"
    assert interrupted["items"][1]["status"] == "RUNNING"
    resumed = png_batch.run_png_batch(
        str(job["job_id"]),
        pipeline_runner=lambda **args: (calls.append(str(args["source_id"])) or _ready_result(str(args["source_id"]), f"resume-{len(calls)}", args["request"])),
    )
    assert resumed["disposition"] == "COMPLETE"
    assert calls.count(str(interrupted["items"][0]["source_id"])) == 1
    assert [item["status"] for item in resumed["job"]["items"]] == ["READY", "READY", "READY"]


def test_pause_orchestration_only_does_not_start_the_next_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    batch_id, _items = _make_batch(tmp_path, monkeypatch, 3)
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda _pipeline, _columns: True)
    job = png_batch.create_png_batch(batch_id)["job"]
    calls: list[str] = []

    def pausing_runner(*, source_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append(source_id)
        png_batch.png_batch_control(str(job["job_id"]), "PAUSE_AFTER_CURRENT")
        return _ready_result(source_id, "run-one", request)

    monkeypatch.setattr(png_batch, "_recover_attempt", lambda _job, _item: None)
    paused = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=pausing_runner)
    assert paused["disposition"] == "PAUSED"
    assert len(calls) == 1
    assert paused["job"]["counts"]["remaining"] == 2


def test_close_cancellation_marks_current_batch_item_interrupted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import copy
    import hashlib

    from scrubbots_pixel_factory import studio_extensions as extensions

    source_sha = "a" * 64
    source_id = "owner-upload-" + source_sha
    record_bytes = b"immutable owner source record"
    record_sha = hashlib.sha256(record_bytes).hexdigest()
    item = {
        "index": 0, "source_id": source_id, "source_sha256": source_sha,
        "source_record_sha256": record_sha, "column_count": 3, "status": "QUEUED",
    }
    job = {
        "job_id": "png-batch-close-test", "import_batch_id": "batch-close-test",
        "batch_digest": "close-test-digest", "items": [item], "settings": {},
        "counts": {}, "ready_mix": {}, "state": "QUEUED", "current_index": None,
    }
    stored = {"job": copy.deepcopy(job)}
    control = {"action": ""}

    class ReadOnlyRecord:
        def read_bytes(self) -> bytes:
            return record_bytes

    monkeypatch.setattr(png_batch, "_read_job", lambda _job_id: copy.deepcopy(stored["job"]))
    monkeypatch.setattr(png_batch, "_write_job", lambda value: (stored.update(job=copy.deepcopy(value)), dict(value))[1])
    monkeypatch.setattr(png_batch, "_job_lock", lambda _job_id: __import__("contextlib").nullcontext())  # no lock file in owner data
    monkeypatch.setattr(png_batch, "_control_path", lambda _job_id: Path("unused-control.json"))
    monkeypatch.setattr(png_batch, "_control_action", lambda _job_id: control["action"])
    monkeypatch.setattr(png_batch, "_clear_control", lambda _job_id: control.update(action=""))
    monkeypatch.setattr(png_batch, "_record_legacy_resume_choice", lambda *_args: None)
    monkeypatch.setattr(png_batch, "_recover_attempt", lambda *_args: None)
    monkeypatch.setattr(extensions, "batch_load", lambda _batch_id: {"batch": {"version": 1, "batch_id": "batch-close-test"}})
    monkeypatch.setattr(extensions, "_digest", lambda _value: "close-test-digest")
    monkeypatch.setattr(extensions, "validate_owner_source", lambda *_args, **_kwargs: {
        "source_sha256": source_sha, "structural": {"disposition": "PASS"}, "exact_logical_source": True,
    })
    monkeypatch.setattr(extensions, "_source_record_paths", lambda *_args, **_kwargs: (ReadOnlyRecord(), None))
    monkeypatch.setattr(extensions, "restore_source_run", lambda *_args, **_kwargs: {"state": "SOURCE_ONLY"})
    source_png = tmp_path / "close-test.png"
    monkeypatch.setattr(extensions, "verify_owner_source", lambda *_args, **_kwargs: {
        "source_sha256": source_sha, "source_path": str(source_png)})
    _pending_status(monkeypatch, [item], tmp_path / "repository")
    monkeypatch.setattr(png_batch, "_job_lock", lambda _job_id: __import__("contextlib").nullcontext())

    def cancelled_runner(**_args: object) -> dict[str, object]:
        control["action"] = "CANCEL_NOW"
        raise RuntimeError("canonical solver cancelled by Studio close")

    result = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=cancelled_runner)

    assert result["disposition"] == "INTERRUPTED"
    assert result["job"]["state"] == "INTERRUPTED"
    assert result["job"]["current_index"] == 0
    assert result["job"]["items"][0]["status"] == "RUNNING"
    assert result["job"]["counts"]["remaining"] == 1


def test_ready_pool_readback_failure_does_not_start_another_solver(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    batch_id, _items = _make_batch(tmp_path, monkeypatch, 1)
    job = png_batch.create_png_batch(batch_id)["job"]
    ready = _ready_result(str(job["items"][0]["source_id"]), "original-ready-run", {
        "column_count": int(job["items"][0]["column_count"]),
    })
    monkeypatch.setattr(png_batch, "_reuse_existing_ready", lambda *_args: {
        "pipeline": ready,
        "release_pool": {"disposition": "NOT_ENTERED", "readback_verified": False},
        "pool_retryable_error": "candidate already has immutable READY evidence",
    })

    result = png_batch.run_png_batch(
        str(job["job_id"]),
        pipeline_runner=lambda **_args: pytest.fail("an existing READY source must not be solved again"),
    )

    item = result["job"]["items"][0]
    assert item["status"] == "FAILED"
    assert item["run_id"] == "original-ready-run"
    assert item["reason"].startswith("READY_POOL_ENTRY_FAILED:")


def test_interrupted_ready_recovery_orchestration_only_uses_isolated_gate_stubs(monkeypatch: pytest.MonkeyPatch) -> None:
    from scrubbots_pixel_factory import studio_extensions as extensions

    source_id = "owner-upload-" + "a" * 64
    pipeline = _ready_result(source_id, "run-exact", {
        "source_id": source_id, "activity_source_sha256": "a" * 64,
        "activity_run_id": "activity-exact", "column_count": 3,
    })
    pipeline["request"] = {
        "source_id": source_id,
        "activity_source_sha256": "a" * 64,
        "activity_source_record_sha256": "b" * 64,
        "activity_run_id": "activity-exact",
        "png_batch_job_id": "png-batch-exact",
        "png_batch_item_index": 0,
        "png_batch_attempt_id": "attempt-exact",
        "column_count": 3,
    }

    class PipelineRoot:
        def __truediv__(self, _name: str) -> "PipelineRoot":
            return self

        def exists(self) -> bool:
            return True

        def glob(self, _pattern: str) -> list[str]:
            return ["exact-run.json"]

    monkeypatch.setattr(extensions, "_pipeline_paths", lambda: [Path("exact-run.json")])
    monkeypatch.setattr(extensions, "_read_json", lambda _path: pipeline)
    monkeypatch.setattr(extensions, "list_candidates", lambda: [{"candidate_id": pipeline["candidate_id"]}])
    monkeypatch.setattr(extensions, "_enter_candidate_release_pool", lambda candidate, *, pipeline: {"readback_verified": True, "entry_digest": "exact"})
    # This test proves attempt lookup and no-retry bookkeeping only. These
    # stubs do not prove artifact, candidate-lineage, or Pool authority.
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda _pipeline, _columns: True)
    monkeypatch.setattr(png_batch, "_candidate_has_source_lineage", lambda *_args: True)
    monkeypatch.setattr(png_batch, "_pool_row_matches", lambda *_args: True)

    recovered = png_batch._recover_attempt(
        {"job_id": "png-batch-exact"},
        {"index": 0, "attempt_id": "attempt-exact", "activity_run_id": "activity-exact",
         "source_id": source_id, "source_sha256": "a" * 64, "source_record_sha256": "b" * 64,
         "column_count": 3},
    )

    assert recovered is not None
    assert recovered["pipeline"]["run_id"] == "run-exact"
    assert recovered["recovered_after_interruption"] is True
    assert recovered["release_pool"]["readback_verified"] is True


def test_interrupted_run_missing_qa_proof_is_not_recovered_as_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    from scrubbots_pixel_factory import studio_extensions as extensions

    source_id = "owner-upload-" + "c" * 64
    pipeline = _ready_result(source_id, "run-without-qa", {
        "source_id": source_id, "activity_source_sha256": "c" * 64,
        "activity_run_id": "activity-proof-gap", "column_count": 3,
    })
    pipeline["stages"] = [{"stage": "REPLAY", "disposition": "PASS"}]
    pipeline["request"] = {
        "source_id": source_id,
        "activity_source_sha256": "c" * 64,
        "activity_run_id": "activity-proof-gap",
        "column_count": 3,
        "png_batch_job_id": "png-batch-proof-gap",
        "png_batch_item_index": 0,
        "png_batch_attempt_id": "attempt-proof-gap",
    }

    class PipelineRoot:
        def __truediv__(self, _name: str) -> "PipelineRoot":
            return self

        def exists(self) -> bool:
            return True

        def glob(self, _pattern: str) -> list[str]:
            return ["proof-gap.json"]

    monkeypatch.setattr(extensions, "_pipeline_paths", lambda: [Path("proof-gap.json")])
    monkeypatch.setattr(extensions, "_read_json", lambda _path: pipeline)
    monkeypatch.setattr(extensions, "list_candidates", lambda: pytest.fail("candidate lookup must follow full proof validation"))

    recovered = png_batch._recover_attempt(
        {"job_id": "png-batch-proof-gap"},
        {"index": 0, "attempt_id": "attempt-proof-gap", "activity_run_id": "activity-proof-gap",
         "source_id": source_id, "source_sha256": "c" * 64,
         "source_record_sha256": "d" * 64, "column_count": 3},
    )

    assert recovered is None


def test_existing_ready_reuse_orchestration_only_uses_isolated_gate_stubs(monkeypatch: pytest.MonkeyPatch) -> None:
    from scrubbots_pixel_factory import studio_extensions as extensions

    source_id = "owner-upload-" + "b" * 64
    pipeline = _ready_result(source_id, "already-ready", {
        "source_id": source_id, "activity_source_sha256": "b" * 64,
        "activity_run_id": "activity-existing-ready", "column_count": 3,
    })
    restored = {
        "state": "READY",
        "source_sha256": "b" * 64,
        "candidate_id": pipeline["candidate_id"],
        "owner_review_status": {},
        "pipeline": pipeline,
    }
    monkeypatch.setattr(extensions, "restore_source_run", lambda *_args, **_kwargs: restored)
    monkeypatch.setattr(extensions, "list_candidates", lambda: [{"candidate_id": pipeline["candidate_id"]}])
    monkeypatch.setattr(extensions, "_enter_candidate_release_pool", lambda candidate, *, pipeline: {"readback_verified": True, "entry_digest": "exact"})
    # This test exercises reuse orchestration only; real proof gates have
    # separate fail-closed contract coverage.
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda _pipeline, _columns: True)
    monkeypatch.setattr(png_batch, "_candidate_has_source_lineage", lambda *_args: True)
    monkeypatch.setattr(png_batch, "_pool_row_matches", lambda *_args: True)

    reused = png_batch._reuse_existing_ready(
        {"settings": {}},
        {"source_id": source_id, "source_sha256": "b" * 64, "column_count": 3, "source_record_sha256": "c" * 64},
    )

    assert reused is not None
    assert reused["pipeline"]["run_id"] == "already-ready"
    assert reused["release_pool"]["readback_verified"] is True


def test_existing_batch_run_uses_exact_proof_fast_path_without_history_scan(monkeypatch: pytest.MonkeyPatch) -> None:
    import hashlib
    from scrubbots_pixel_factory import studio_extensions as extensions

    source_id = "owner-upload-" + "b" * 64
    source_bytes = b"unchanged owner source bytes"
    record_bytes = b"unchanged owner source record"
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    record_sha = hashlib.sha256(record_bytes).hexdigest()
    columns = 3
    pipeline = _ready_result(source_id, "pipeline-existing-exact", {
        "source_id": source_id, "activity_source_sha256": source_sha,
        "activity_source_record_sha256": record_sha,
        "activity_run_id": "activity-existing-exact", "column_count": columns,
        "png_batch_job_id": "png-batch-existing-exact", "png_batch_item_index": 7,
        "png_batch_attempt_id": "attempt-existing-exact",
    })
    candidate_id = pipeline["candidate_id"]

    class ReadBytes:
        def __init__(self, payload: bytes) -> None:
            self.payload = payload

        def read_bytes(self) -> bytes:
            return self.payload

    job = {"job_id": "png-batch-existing-exact", "settings": {}}
    item = {
        "index": 7, "attempt_id": "attempt-existing-exact",
        "activity_run_id": "activity-existing-exact", "source_id": source_id,
        "source_sha256": source_sha, "source_record_sha256": record_sha,
        "column_count": columns, "run_id": pipeline["run_id"],
    }
    monkeypatch.setattr(extensions, "_read_json", lambda _path: pipeline)
    monkeypatch.setattr(extensions, "_pipeline_path", lambda _run_id: object())
    monkeypatch.setattr(extensions, "_source_record_paths", lambda *_args: (ReadBytes(record_bytes), ReadBytes(source_bytes)))
    monkeypatch.setattr(extensions, "_latest_ready_pipeline", lambda _candidate_id: pipeline)
    monkeypatch.setattr(extensions, "restore_source_run", lambda *_args, **_kwargs: pytest.fail("exact READY item must not scan history"))
    monkeypatch.setattr(extensions, "list_candidates", lambda: [{"candidate_id": candidate_id}])
    monkeypatch.setattr(extensions, "_enter_candidate_release_pool", lambda *_args, **_kwargs: {"readback_verified": True})
    monkeypatch.setattr(png_batch, "_has_ready_pipeline_proof", lambda run, source, **kwargs: run is pipeline and source == source_id and kwargs.get("job") is job and kwargs.get("item") is item)
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda run, count: run is pipeline and count == columns)
    monkeypatch.setattr(png_batch, "_candidate_has_source_lineage", lambda *_args: True)
    monkeypatch.setattr(png_batch, "_pool_row_matches", lambda *_args: True)

    reused = png_batch._reuse_existing_ready(job, item)

    assert reused is not None
    assert reused["pipeline"] is pipeline


def test_existing_ready_pool_reentry_failure_is_returned_without_solver_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    from scrubbots_pixel_factory import studio_extensions as extensions

    source_id = "owner-upload-" + "d" * 64
    pipeline = _ready_result(source_id, "already-ready-no-pool", {
        "source_id": source_id, "activity_source_sha256": "d" * 64,
        "activity_run_id": "activity-existing-ready-no-pool", "column_count": 4,
    })
    restored = {
        "state": "READY", "source_sha256": "d" * 64,
        "candidate_id": pipeline["candidate_id"], "owner_review_status": {}, "pipeline": pipeline,
    }
    monkeypatch.setattr(extensions, "restore_source_run", lambda *_args, **_kwargs: restored)
    monkeypatch.setattr(extensions, "list_candidates", lambda: [{"candidate_id": pipeline["candidate_id"]}])
    monkeypatch.setattr(extensions, "_enter_candidate_release_pool", lambda *_args, **_kwargs: {
        "disposition": "NOT_ENTERED", "readback_verified": False, "reason": "immutable exact read-back failed",
    })
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda *_args: True)
    monkeypatch.setattr(png_batch, "_candidate_has_source_lineage", lambda *_args: True)
    monkeypatch.setattr(png_batch, "_pool_row_matches", lambda *_args: pytest.fail("failed pool proof must not be treated as a reuse miss"))

    outcome = png_batch._reuse_existing_ready(
        {"settings": {}},
        {"source_id": source_id, "source_sha256": "d" * 64, "source_record_sha256": "e" * 64, "column_count": 4},
    )

    assert outcome is not None
    assert outcome["pipeline"]["run_id"] == "already-ready-no-pool"
    assert outcome["pool_retryable_error"] == "immutable exact read-back failed"
    assert outcome["release_pool"]["readback_verified"] is False


def test_pool_reentry_returns_existing_exact_row_without_rewriting_immutable_file(monkeypatch: pytest.MonkeyPatch) -> None:
    from scrubbots_pixel_factory import studio_extensions as extensions
    from scrubbots_pixel_factory.supply_pipeline import release_pool

    candidate_id = "candidate-idempotent-pool"
    pipeline = {"run_id": "pipeline-idempotent", "candidate_id": candidate_id,
                "disposition": "READY", "primary": {"state": "READY"}}
    existing_entry = {"candidate_id": candidate_id, "pipeline_run_id": pipeline["run_id"],
                      "entry_digest": "verified-digest", "eligibility_source": "READY_AUTO"}

    monkeypatch.setattr(extensions, "_pipeline_paths", lambda: [Path("pipeline-idempotent.json")])
    monkeypatch.setattr(extensions, "_read_json", lambda _path: pipeline)
    monkeypatch.setattr(release_pool, "release_entries", lambda *_args: [existing_entry])
    monkeypatch.setattr(release_pool, "enter_release_pool", lambda *_args, **_kwargs: pytest.fail("immutable existing row must not be rewritten"))

    result = extensions._enter_candidate_release_pool(
        {"candidate_id": candidate_id, "artwork_sha256": "a" * 64}, pipeline=pipeline,
    )

    assert result["readback_verified"] is True
    assert result["entry_digest"] == "verified-digest"
    assert result["disposition"] == "ALREADY_IN_RELEASE_POOL"


def test_candidate_filtered_release_pool_read_scans_only_that_candidate(monkeypatch: pytest.MonkeyPatch) -> None:
    from scrubbots_pixel_factory.supply_pipeline import release_pool

    observed: list[str] = []

    class PoolRoot:
        def is_dir(self) -> bool:
            return True

        def glob(self, pattern: str) -> list[Path]:
            observed.append(pattern)
            return []

    monkeypatch.setattr(release_pool, "_pool_roots", lambda: (PoolRoot(),))
    monkeypatch.setattr("scrubbots_pixel_factory.owner_art_storage._is_reparse_point", lambda _path: False)
    candidate_id = "candidate-owner-" + "a" * 48

    assert release_pool.release_entries(candidate_id) == []
    assert observed == [f"{candidate_id}-*.json"]


def test_304_item_fake_campaign_orchestration_only_is_sequential_and_bounded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    batch_id, _items = _make_batch(tmp_path, monkeypatch, 304)
    monkeypatch.setattr(png_batch, "_verify_column_artifacts", lambda _pipeline, _columns: True)
    job = png_batch.create_png_batch(batch_id)["job"]
    active = 0
    peak = 0
    calls = 0

    def fake_runner(*, source_id: str, request: dict[str, object]) -> dict[str, object]:
        nonlocal active, peak, calls
        active += 1
        peak = max(peak, active)
        calls += 1
        assert int(request["column_count"]) in (3, 4, 5)
        active -= 1
        return _ready_result(source_id, f"run-{calls}", request)

    monkeypatch.setattr(png_batch, "_recover_attempt", lambda _job, _item: None)
    result = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=fake_runner)
    assert result["disposition"] == "COMPLETE"
    assert calls == 304 and peak == 1
    assert result["job"]["counts"] == {"total": 304, "ready": 304, "failed": 0, "rejected": 0, "skipped": 0, "remaining": 0}
    assert result["job"]["ready_mix"] == {"3": 137, "4": 122, "5": 45}
    saved = json.loads(png_batch._job_path(str(job["job_id"])).read_text(encoding="utf-8"))
    assert saved["state_digest"] == result["job"]["state_digest"]
    assert png_batch.MAX_JOB_BYTES == 1024 * 1024
