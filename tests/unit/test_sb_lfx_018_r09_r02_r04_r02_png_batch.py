from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory import png_batch


@pytest.mark.parametrize(
    ("count", "expected"),
    [
        (9, {3: 4, 4: 4, 5: 1}),
        (40, {3: 18, 4: 16, 5: 6}),
        (100, {3: 45, 4: 40, 5: 15}),
        (150, {3: 68, 4: 60, 5: 22}),
    ],
)
def test_largest_remainder_quotas_match_locked_mix(count: int, expected: dict[int, int]) -> None:
    assert png_batch.largest_remainder_quotas(count) == expected


def test_assignments_are_deterministic_interleaved_and_exact() -> None:
    ids = [f"owner-upload-{index:064x}" for index in range(150)]
    assignment = png_batch.assign_columns(ids)
    assert assignment == png_batch.assign_columns(ids)
    assert {column: assignment.count(column) for column in (3, 4, 5)} == {3: 68, 4: 60, 5: 22}
    assert max((len(list(group)) for _key, group in __import__("itertools").groupby(assignment))) <= 3


def _make_batch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, source_count: int = 4) -> tuple[str, list[dict[str, object]]]:
    """Build synthetic inputs for batch-orchestration contracts only.

    Source-record validation is stubbed here, so tests using this helper do not
    prove real owner-source eligibility or canonical READY evidence.
    """
    root = tmp_path / "png-batches"
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
        items.append({"index": index, "display_path": f"source-{index}.png", "source_id": source_id, "disposition": "IMPORTED"})

    from scrubbots_pixel_factory import studio_extensions as extensions

    batch = {"schema": "scrubbots-owner-upload-batch", "version": 1, "batch_id": "batch-test", "items": items}
    monkeypatch.setattr(extensions, "batch_load", lambda _batch_id: {"batch": batch})
    monkeypatch.setattr(extensions, "_digest", lambda value: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest())
    monkeypatch.setattr(
        extensions,
        "verify_owner_source",
        lambda source_id: {"source_sha256": by_id[source_id]["sha"], "original_filename": f"{source_id[-4:]}.png"},
    )
    monkeypatch.setattr(extensions, "validate_owner_source", lambda source_id, **_kwargs: {
        "source_sha256": by_id[source_id]["sha"],
        "exact_logical_source": True,
        "structural": {"disposition": "PASS"},
    })
    monkeypatch.setattr(extensions, "_source_record_paths", lambda source_id, *_args, **_kwargs: (Path(by_id[source_id]["record"]), Path("unused.png")))
    monkeypatch.setattr(extensions, "restore_source_run", lambda *args, **kwargs: {"state": "SOURCE_ONLY"})
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
    assert result["disposition"] == "COMPLETE"
    assert len(calls) == 9
    assert [item["status"] for item in stored["items"]].count("READY") == 8
    assert [item["status"] for item in stored["items"]].count("FAILED") == 1
    for source_id, column_count in calls:
        item = next(row for row in stored["items"] if row["source_id"] == source_id)
        assert item["column_count"] == column_count
    repeat = png_batch.run_png_batch(str(job["job_id"]), pipeline_runner=lambda **_args: pytest.fail("completed items must never rerun"))
    assert repeat["disposition"] == "COMPLETE" and repeat.get("mutated") is False
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

    monkeypatch.setattr(extensions, "extensions_root", PipelineRoot)
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

    monkeypatch.setattr(extensions, "extensions_root", PipelineRoot)
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
        {"source_id": source_id, "source_sha256": "b" * 64},
    )

    assert reused is not None
    assert reused["pipeline"]["run_id"] == "already-ready"
    assert reused["release_pool"]["readback_verified"] is True


def test_150_item_fake_campaign_orchestration_only_is_sequential_and_bounded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    batch_id, _items = _make_batch(tmp_path, monkeypatch, 150)
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
    assert calls == 150 and peak == 1
    assert result["job"]["counts"] == {"total": 150, "ready": 150, "failed": 0, "rejected": 0, "skipped": 0, "remaining": 0}
    assert result["job"]["ready_mix"] == {"3": 68, "4": 60, "5": 22}
    saved = json.loads(png_batch._job_path(str(job["job_id"])).read_text(encoding="utf-8"))
    assert saved["state_digest"] == result["job"]["state_digest"]
    assert png_batch.MAX_JOB_BYTES == 1024 * 1024
