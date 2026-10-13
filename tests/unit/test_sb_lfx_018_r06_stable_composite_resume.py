from __future__ import annotations

from collections import Counter
import hashlib
import importlib
import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory import png_batch, studio_extensions as ext


def _install_disk_sources(monkeypatch, tmp_path: Path, count: int = 9):
    root = tmp_path / "extensions"
    batches = root / "batches"
    source_root = tmp_path / "owner-uploads"
    batches.mkdir(parents=True)
    source_root.mkdir()
    ids: list[str] = []
    for index in range(count):
        raw = b"PNG-fixture-" + index.to_bytes(4, "big")
        source_sha = hashlib.sha256(raw).hexdigest()
        source_id = "owner-upload-" + source_sha
        ids.append(source_id)
        folder = source_root / source_id
        folder.mkdir()
        record = {
            "schema": "scrubbots-owner-upload", "version": 1, "source_id": source_id,
            "origin": ext.OWNER_UPLOAD_ORIGIN, "source_sha256": source_sha,
            "byte_length": len(raw), "media_type": "image/png",
            "original_filename": f"{index + 1:03d}_32x32px.png",
            "original_width": 32, "original_height": 32,
            "immutable_relative_path": f"owner-uploads/{source_id}/source.png",
            "source_record_relative_path": f"owner-uploads/{source_id}/source.json",
            "status": ext.OWNER_UPLOAD_STATUS,
            "validation_state": ext.OWNER_UPLOAD_VALIDATION_STATE,
        }
        (folder / "source.png").write_bytes(raw)
        (folder / "source.json").write_bytes(ext._canonical_bytes(record))

    monkeypatch.setattr(ext, "extensions_root", lambda: root)
    monkeypatch.setattr(ext, "_source_record_paths", lambda source_id, *_args: (
        source_root / source_id / "source.json", source_root / source_id / "source.png"))
    monkeypatch.setattr(png_batch, "_root", lambda: root / "png-batches")
    monkeypatch.setattr(ext, "validate_owner_source", lambda source_id, **_kwargs: {
        "source_sha256": source_id.removeprefix("owner-upload-"),
        "exact_logical_source": True, "structural": {"disposition": "PASS"},
        "void_capability": {"state": "OPEN"},
    })
    return root, batches, source_root, ids


def _write_v1_event(batch_root: Path, batch_id: str, ids: list[str]) -> None:
    payload = {
        "schema": ext.BATCH_SCHEMA, "version": 1, "batch_id": batch_id,
        "items": [{"index": index, "source_id": source_id, "disposition": "IMPORTED"} for index, source_id in enumerate(ids)],
        "counts": {"success": len(ids), "failed": 0}, "created_at": "2026-10-13T00:00:00+00:00",
    }
    ext._write_json(batch_root / f"{batch_id}.json", payload, immutable=True)


def _legacy_composite(ids: list[str]) -> dict:
    """Faithful pre-R06 identity rule used to demonstrate the original red case."""
    history: dict[str, list[dict]] = {}
    batch_root = ext.extensions_root() / "batches"
    for path in sorted(batch_root.glob("*.json")):
        try:
            prior = ext.batch_load(path.stem)["batch"]
        except (ext.StudioExtensionError, OSError, ValueError):
            continue
        for item in prior.get("items", []):
            if isinstance(item, dict) and item.get("source_id"):
                history.setdefault(item["source_id"], []).append({
                    "batch_id": prior.get("batch_id", path.stem),
                    "index": int(item.get("index", -1)),
                    "disposition": str(item.get("disposition", "")),
                })
    items = []
    for index, source_id in enumerate(ids):
        source = ext.verify_owner_source(source_id)
        record_path, _png_path = ext._source_record_paths(source_id)
        items.append({
            "index": index, "source_id": source_id, "display_path": source["original_filename"],
            "disposition": "ALREADY_IMPORTED", "error": None,
            "source_sha256": source["source_sha256"],
            "source_record_sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
            "import_provenance": history.get(source_id, []),
        })
    snapshot = {
        "schema": ext.BATCH_SCHEMA, "version": 2,
        "kind": "COMPOSITE_LOADED_SOURCE_SNAPSHOT", "items": items,
        "counts": {"success": len(items), "failed": 0},
    }
    digest = ext._digest(snapshot)
    payload = {**snapshot, "batch_id": f"batch-loaded-{digest[:36]}", "snapshot_digest": digest}
    ext._write_json(batch_root / f"{payload['batch_id']}.json", payload, immutable=True)
    return payload


def test_real_disk_legacy_snapshot_red_then_stable_composite_and_job_reuse(monkeypatch, tmp_path):
    root, batch_root, _source_root, ids = _install_disk_sources(monkeypatch, tmp_path)
    original_pngs = {source_id: (root.parent / "owner-uploads" / source_id / "source.png").read_bytes() for source_id in ids}
    _write_v1_event(batch_root, "batch-import-original-002-005", ids[:4])
    _write_v1_event(batch_root, "batch-import-original-003-010", ids[3:])

    # RED reproduction: real v1→v2→v2 disk history makes the pre-fix identity drift.
    old_first = _legacy_composite(ids)
    assert ext.find_loaded_png_batch(ids)["disposition"] == "LEGACY_EXACT_MATCH"
    old_second = _legacy_composite(ids)
    assert old_first["batch_id"] != old_second["batch_id"]
    assert ext.find_loaded_png_batch(ids)["disposition"] == "LEGACY_COMPOSITE_AMBIGUOUS"
    assert any(item.get("version") == 2 for item in (ext.batch_load(path.stem)["batch"] for path in batch_root.glob("*.json")))

    # A unique legacy match is only durably reconciled by the explicit run call.
    legacy_job = png_batch.create_png_batch(old_second["batch_id"], {})["job"]
    reconciliation_root = png_batch._root() / "reconciliations"
    assert not reconciliation_root.exists()
    monkeypatch.setattr(png_batch, "_reuse_existing_ready", lambda *_args: {
        "pipeline": {"primary": {}}, "release_pool": {"readback_verified": True}})
    monkeypatch.setattr(png_batch, "_recover_attempt", lambda *_args: None)
    explicit_legacy_resume = png_batch.run_png_batch(legacy_job["job_id"], expected_batch_id=old_second["batch_id"], pipeline_runner=lambda **_kwargs: pytest.fail("fake existing proof should avoid executor"))
    assert explicit_legacy_resume["job"]["counts"]["ready"] == 9
    choices = list(reconciliation_root.glob("legacy-resume-*.json"))
    assert len(choices) == 1
    assert json.loads(choices[0].read_text(encoding="utf-8"))["owner_action"] == "EXPLICIT_RESUME"

    # GREEN: v2 self-history is ignored; original import memberships remain readable.
    first = ext.create_loaded_png_batch(ids)
    first_bytes = (batch_root / f"{first['batch_id']}.json").read_bytes()
    second = ext.create_loaded_png_batch(ids)
    assert second["batch_id"] == first["batch_id"]
    assert (batch_root / f"{second['batch_id']}.json").read_bytes() == first_bytes
    assert [len(item["import_provenance"]) for item in second["items"]] == [1, 1, 1, 2, 1, 1, 1, 1, 1]
    snapshot_path = batch_root / f"{first['batch_id']}.json"
    tampered = json.loads(first_bytes.decode("utf-8"))
    tampered["items"][0]["import_provenance"].append({"batch_id": "forged", "index": 99, "disposition": "IMPORTED"})
    snapshot_path.write_bytes(ext._canonical_bytes(tampered))
    with pytest.raises(ext.StudioExtensionError, match="provenance digest"):
        ext.batch_load(first["batch_id"])
    snapshot_path.write_bytes(first_bytes)

    # A later duplicate original import does not change the identity or mutate the snapshot.
    _write_v1_event(batch_root, "batch-import-duplicate-one", [ids[0]])
    duplicate = ext.create_loaded_png_batch(ids)
    assert duplicate["batch_id"] == first["batch_id"]
    assert (batch_root / f"{first['batch_id']}.json").read_bytes() == first_bytes

    # Simulated process restart: reload the backend module and recover only from disk.
    importlib.reload(ext)
    monkeypatch.setattr(ext, "extensions_root", lambda: root)
    monkeypatch.setattr(ext, "_source_record_paths", lambda source_id, *_args: (
        root.parent / "owner-uploads" / source_id / "source.json",
        root.parent / "owner-uploads" / source_id / "source.png"))
    monkeypatch.setattr(ext, "validate_owner_source", lambda source_id, **_kwargs: {
        "source_sha256": source_id.removeprefix("owner-upload-"),
        "exact_logical_source": True, "structural": {"disposition": "PASS"},
        "void_capability": {"state": "OPEN"},
    })
    resolved = ext.find_loaded_png_batch(ids)
    assert resolved["disposition"] == "MATCHED"
    assert resolved["batch"] == first
    created = png_batch.create_png_batch(first["batch_id"], {"background_intent": "TRANSPARENT"})
    reused = png_batch.create_png_batch(first["batch_id"], {"background_intent": "TRANSPARENT"})
    assert created["job"]["job_id"] == reused["job"]["job_id"]
    assert created["job"]["plan_digest"] == reused["job"]["plan_digest"]
    assert Counter(item["column_count"] for item in created["job"]["items"]) == Counter({3: 4, 4: 4, 5: 1})
    for source_id, raw in original_pngs.items():
        assert (root.parent / "owner-uploads" / source_id / "source.png").read_bytes() == raw


def test_three_level_failed_subset_retry_chain_and_fail_closed_authority(monkeypatch, tmp_path):
    _root, _batch_root, source_root, ids = _install_disk_sources(monkeypatch, tmp_path)
    batch = ext.create_loaded_png_batch(ids)
    plan = png_batch.create_png_batch(batch["batch_id"], {"source_directory": str(source_root)})["job"]
    call_sources: list[str] = []
    ready_ids = set(ids[4:])

    def verified_existing(_job, item):
        if item["source_id"] in ready_ids:
            return {"pipeline": {"primary": {}}, "release_pool": {"readback_verified": True}}
        return None

    monkeypatch.setattr(png_batch, "_reuse_existing_ready", verified_existing)
    monkeypatch.setattr(png_batch, "_recover_attempt", lambda *_args: None)
    monkeypatch.setattr(png_batch, "_job_lock", lambda _job_id: _unlocked())

    def fake_runner(*, source_id, request):
        call_sources.append(source_id)
        return {"disposition": "ERROR", "reason": "fixture intentionally fails this source", "request": request}

    first_run = png_batch.run_png_batch(plan["job_id"], expected_batch_id=batch["batch_id"], pipeline_runner=fake_runner)
    first_job = first_run["job"]
    assert first_job["counts"]["ready"] == 5 and first_job["counts"]["failed"] == 4
    assert Counter(item["column_count"] for item in first_job["items"]) == Counter({3: 4, 4: 4, 5: 1})
    assert len(call_sources) == 4

    retry_one = png_batch.retry_failed_png_batch(first_job["job_id"])["job"]
    assert len(retry_one["items"]) == 4
    ready_ids = set(ids[:2])
    second_run = png_batch.run_png_batch(retry_one["job_id"], expected_batch_id=batch["batch_id"], pipeline_runner=fake_runner)
    retry_one_done = second_run["job"]
    assert retry_one_done["counts"]["ready"] == 2 and retry_one_done["counts"]["failed"] == 2
    assert [item["column_count"] for item in retry_one_done["items"]] == [item["column_count"] for item in first_job["items"] if item["status"] == "FAILED"]
    assert png_batch._job_lineage_matches_snapshot(retry_one_done, batch)

    retry_two = png_batch.retry_failed_png_batch(retry_one_done["job_id"])["job"]
    assert len(retry_two["items"]) == 2
    assert retry_two["job_id"] not in {retry_one["job_id"], first_job["job_id"]}
    assert [item["column_count"] for item in retry_two["items"]] == [item["column_count"] for item in retry_one_done["items"] if item["status"] == "FAILED"]
    ready_ids = set(ids[2:4])
    third_run = png_batch.run_png_batch(retry_two["job_id"], expected_batch_id=batch["batch_id"], pipeline_runner=fake_runner)
    retry_two_done = third_run["job"]
    assert retry_two_done["counts"]["ready"] == 2 and retry_two_done["counts"]["failed"] == 0
    assert png_batch.png_batch_latest(batch["batch_id"])["job"]["job_id"] == retry_two["job_id"]
    assert call_sources == ids[:4] + ids[2:4]

    wrong_batch = png_batch.png_batch_latest("batch-import-wrong-source")
    assert wrong_batch["disposition"] == "BATCH_JOB_SOURCE_MISMATCH"

    # Changed owner record cannot be retried even though old job bytes remain valid.
    record_path = source_root / ids[3] / "source.json"
    before = record_path.read_bytes()
    record_path.write_bytes(before + b" ")
    assert png_batch.retry_failed_png_batch(retry_one_done["job_id"])["disposition"] == "RETRY_SOURCE_CHANGED"
    record_path.write_bytes(before)

    # Parent alteration is rejected by its seal/ancestry checks; no child is created.
    parent_path = png_batch._job_path(retry_one_done["job_id"])
    parent_value = json.loads(parent_path.read_text(encoding="utf-8"))
    parent_value["state"] = "RUNNING"
    parent_path.write_bytes(ext._canonical_bytes(parent_value))
    assert png_batch.png_batch_latest(batch["batch_id"])["disposition"] == "BATCH_JOB_SOURCE_MISMATCH"


def test_bounded_fake_150_source_plan_is_stable_and_no_executor_runs(monkeypatch, tmp_path):
    _root, _batch_root, _source_root, ids = _install_disk_sources(monkeypatch, tmp_path, count=150)
    batch = ext.create_loaded_png_batch(ids)
    created = png_batch.create_png_batch(batch["batch_id"], {})
    assert created["job"]["snapshot_source_count"] == 150
    assert created["job"]["counts"]["total"] == 150
    assert created["job"]["planned_quotas"] == {"3": 68, "4": 60, "5": 22}
    reused = png_batch.create_png_batch(batch["batch_id"], {})
    assert reused["disposition"] == "EXISTING"
    assert reused["job"]["job_id"] == created["job"]["job_id"]


from contextlib import contextmanager


@contextmanager
def _unlocked():
    yield
