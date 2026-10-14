from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
import hashlib

import pytest

from scrubbots_pixel_factory import png_batch, studio_extensions


class MemoryPath:
    def __init__(self, name: str, *, entries=(), files=None):
        self.name = name
        self.stem = name.rsplit("/", 1)[-1].removesuffix(".json")
        self.entries = list(entries)
        self.files = files if files is not None else {}
        self.parent = self

    def __truediv__(self, child):
        return MemoryPath(f"{self.name}/{child}", entries=self.entries, files=self.files)

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return isinstance(other, MemoryPath) and self.name == other.name

    def glob(self, _pattern):
        return self.entries

    def exists(self):
        if self.name.endswith(".json"):
            return self.name in self.files
        return bool(self.entries) or self.name.rsplit("/", 1)[-1] in self.files

    def mkdir(self, **_kwargs):
        return None


class MemoryRecord:
    def __init__(self, raw: bytes):
        self.raw = raw

    def read_bytes(self):
        return self.raw


def _source_ids(count: int) -> list[str]:
    return ["owner-upload-" + format(index + 1, "064x") for index in range(count)]


def _record(source_id: str) -> dict:
    digest = source_id.removeprefix("owner-upload-")
    return {
        "source_id": source_id,
        "source_sha256": digest,
        "source_record_sha256": hashlib.sha256((source_id + ":record").encode()).hexdigest(),
        "original_filename": f"{int(digest, 16):03d}_32x32px.png",
    }


def _validated_items(source_ids: list[str]) -> list[dict]:
    return [
        {"index": index, "source_id": source_id, "display_path": _record(source_id)["original_filename"],
         "disposition": "ALREADY_IMPORTED", "source_sha256": _record(source_id)["source_sha256"],
         "source_record_sha256": _record(source_id)["source_record_sha256"]}
        for index, source_id in enumerate(source_ids)
    ]


def test_exact_campaign_quotas_and_legacy_collision_is_versioned(monkeypatch):
    expected = {
        9: {3: 4, 4: 4, 5: 1},
        40: {3: 18, 4: 16, 5: 6},
        100: {3: 45, 4: 40, 5: 15},
        150: {3: 68, 4: 60, 5: 22},
    }
    for count, quotas in expected.items():
        assert png_batch.largest_remainder_quotas(count) == quotas

    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: MemoryPath("root"))
    source_id = _source_ids(1)[0]
    source_sha = source_id.removeprefix("owner-upload-")
    legacy = {
        "version": 1, "analysis_policy": "SB-LFX-004-C001_CANONICAL_IMPORT_ANALYSIS_V1",
        "alpha": {"transparent_count": 12}, "void_capability": {"state": "OPEN", "git_head": "aef60a616d4ac401e9dfac15df6fe56e671c0053", "void_contract": "PINNED_RUNTIME_V2"},
    }
    upgraded = {
        **legacy, "version": 2, "analysis_policy": "SB-LFX-004-C001_CANONICAL_IMPORT_ANALYSIS_V2",
        "source_authority": {"source_record_sha256": "a" * 64},
        "game_authority": {"repository": "Sekiph82/Scrubbots", "commit": "aef60a616d4ac401e9dfac15df6fe56e671c0053", "state": "OPEN", "void_contract": "PINNED_RUNTIME_V2"},
    }
    legacy_path = studio_extensions._validation_evidence_path(source_id, source_sha, legacy)
    upgraded_path = studio_extensions._validation_evidence_path(source_id, source_sha, upgraded)
    assert legacy_path.name != upgraded_path.name
    assert upgraded_path == studio_extensions._validation_evidence_path(source_id, source_sha, upgraded)


def test_loaded_snapshot_unions_import_events_and_binds_both_hashes(monkeypatch):
    ids = _source_ids(9)
    old_event = MemoryPath("batches/old-event.json")
    new_event = MemoryPath("batches/new-event.json")
    root = MemoryPath("extensions", entries=[old_event, new_event])
    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: root)
    monkeypatch.setattr(studio_extensions, "batch_load", lambda batch_id: {"batch": {
        "schema": studio_extensions.BATCH_SCHEMA,
        "version": 1,
        "batch_id": batch_id,
        "items": ([{"index": i, "source_id": source_id, "disposition": "IMPORTED"} for i, source_id in enumerate(ids[:4])]
                  if batch_id == "old-event" else
                  [{"index": i, "source_id": source_id, "disposition": "ALREADY_IMPORTED"} for i, source_id in enumerate(ids[3:])]),
    }})
    monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda source_id: _record(source_id))
    monkeypatch.setattr(studio_extensions, "_source_record_paths", lambda source_id, *_args: (MemoryRecord((source_id + ":record").encode()), None))
    writes = []
    monkeypatch.setattr(studio_extensions, "_write_json", lambda path, value, **_kwargs: writes.append((path, deepcopy(value))))

    snapshot = studio_extensions.create_loaded_png_batch(ids)

    assert len(snapshot["items"]) == 9
    assert snapshot["counts"] == {"success": 9, "failed": 0}
    assert [item["source_id"] for item in snapshot["items"]] == ids
    assert all(len(item["source_sha256"]) == 64 and len(item["source_record_sha256"]) == 64 for item in snapshot["items"])
    assert snapshot["items"][0]["import_provenance"][0]["batch_id"] == "old-event"
    assert snapshot["items"][8]["import_provenance"][0]["batch_id"] == "new-event"
    assert snapshot["batch_id"].startswith("batch-loaded-")
    assert writes and writes[0][1] == snapshot


def test_one_explicit_fake_run_visits_all_nine_sequentially_and_retry_is_separate(monkeypatch):
    ids = _source_ids(9)
    records = {source_id: _record(source_id) for source_id in ids}
    manifest = {"batch_id": "batch-loaded-test", "items": _validated_items(ids)}
    manifest["snapshot_source_count"] = 9
    jobs: dict[str, dict] = {}
    root = MemoryPath("png-batches")
    monkeypatch.setattr(png_batch, "_root", lambda: root)
    monkeypatch.setattr(png_batch, "_job_path", lambda job_id: MemoryPath(f"jobs/{job_id}.json", files=jobs))
    monkeypatch.setattr(png_batch, "_read_job", lambda job_id: deepcopy(jobs[job_id]))

    def write_job(job):
        sealed = png_batch._seal(job)
        jobs[sealed["job_id"]] = deepcopy(sealed)
        return sealed

    monkeypatch.setattr(png_batch, "_write_job", write_job)
    monkeypatch.setattr(png_batch, "_job_lock", lambda _job_id: _unlocked())
    monkeypatch.setattr(png_batch, "_clear_control", lambda _job_id: None)
    monkeypatch.setattr(png_batch, "_control_action", lambda _job_id: "")
    monkeypatch.setattr(png_batch, "_recover_attempt", lambda *_args: None)
    monkeypatch.setattr(png_batch, "_reuse_existing_ready", lambda *_args: None)
    monkeypatch.setattr(studio_extensions, "batch_load", lambda _batch_id: {"batch": manifest})
    monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda source_id, **_kwargs: records[source_id])
    monkeypatch.setattr(studio_extensions, "validate_owner_source", lambda *_args, **_kwargs: {"source_sha256": ""})
    monkeypatch.setattr(studio_extensions, "_source_record_paths", lambda source_id, *_args: (MemoryRecord((source_id + ":record").encode()), None))
    monkeypatch.setattr(png_batch, "_source_record_paths", lambda source_id, *_args: (MemoryRecord((source_id + ":record").encode()), None), raising=False)

    # Install the exact fake validation API on the module imported by _verify_sources.
    def validate(source_id, **_kwargs):
        return {"source_sha256": records[source_id]["source_sha256"], "exact_logical_source": True,
                "structural": {"disposition": "PASS"}, "void_capability": {"state": "OPEN"}}

    monkeypatch.setattr(studio_extensions, "validate_owner_source", validate)
    created = png_batch.create_png_batch("batch-loaded-test", {"background_intent": "TRANSPARENT"})
    job = created["job"]
    assert len(job["items"]) == 9
    assert Counter(item["column_count"] for item in job["items"]) == Counter({3: 4, 4: 4, 5: 1})

    calls = []

    def fake_pipeline_runner(*, source_id, request):
        calls.append((source_id, request["column_count"], request["png_batch_item_index"]))
        if len(calls) == 1:
            raise RuntimeError("fixture failure; continue the batch")
        return {"disposition": "ERROR", "error": "fake non-READY result"}

    result = png_batch.run_png_batch(job["job_id"], expected_batch_id="batch-loaded-test", pipeline_runner=fake_pipeline_runner)
    failed_job = result["job"]
    assert [row[0] for row in calls] == ids
    assert [row[2] for row in calls] == list(range(9))
    assert result["disposition"] == "FINISHED_WITH_FAILURES", (result["disposition"], result["job"].get("state"), result["job"].get("counts"), [(item["status"], item.get("reason")) for item in result["job"].get("items", [])])
    assert failed_job["counts"] == {"total": 9, "ready": 0, "failed": 9, "rejected": 0, "skipped": 0, "remaining": 0}
    assert "FINISHED WITH FAILURES" in png_batch.batch_terminal_message(failed_job, loaded_count=9)

    retry = png_batch.retry_failed_png_batch(job["job_id"])
    retry_job = retry["job"]
    assert retry["disposition"] == "RETRY_CREATED"
    assert retry_job["job_id"] != job["job_id"]
    assert retry_job["parent_job_id"] == job["job_id"]
    assert len(retry_job["items"]) == 9
    assert [item["column_count"] for item in retry_job["items"]] == [item["column_count"] for item in failed_job["items"]]
    assert all(item["prior_attempt"]["status"] == "FAILED" for item in retry_job["items"])
    assert jobs[job["job_id"]]["state"] == "COMPLETE"


@contextmanager
def _unlocked():
    yield


def test_immutable_writer_still_fails_closed_without_changing_existing_bytes():
    class ExistingEvidence:
        name = "validation.json"
        parent = type("Parent", (), {"mkdir": staticmethod(lambda **_kwargs: None)})()

        def __init__(self, raw):
            self.raw = raw

        def exists(self):
            return True

        def read_bytes(self):
            return self.raw

    raw = studio_extensions._canonical_bytes({"schema": "old", "source_sha256": "a" * 64})
    path = ExistingEvidence(raw)
    with pytest.raises(studio_extensions.StudioExtensionError, match="immutable evidence already exists"):
        studio_extensions._write_json(path, {"schema": "new", "source_sha256": "a" * 64}, immutable=True)
    assert path.read_bytes() == raw
