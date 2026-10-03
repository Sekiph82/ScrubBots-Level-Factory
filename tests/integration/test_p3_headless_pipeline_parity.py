from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from scrubbots_pixel_factory import owner_upload, studio_extensions as studio
from scrubbots_pixel_factory.headless_pipeline import JOB_SCHEMA, run_job, _read_events, load_job
from scrubbots_pixel_factory.output.png import encode_logical_png
from scrubbots_pixel_factory.supply_pipeline.game_rules import DEFAULT_PROJECT, find_godot


def test_headless_job_uses_the_same_canonical_route_and_review_queue(tmp_path: Path, monkeypatch) -> None:
    configured_project = Path(os.environ.get("SCRUBBOTS_PROJECT") or DEFAULT_PROJECT)
    if find_godot() is None or not (configured_project / "project.godot").is_file():
        pytest.skip("local Godot or configured read-only ScrubBots authority is unavailable")

    repository = tmp_path / "level-factory"
    source_root = repository / "level_factory" / "output" / "owner-uploads"
    evidence_root = repository / "level_factory" / "output" / "studio-extensions"
    source_root.mkdir(parents=True)
    evidence_root.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence_root)

    source_path = tmp_path / "producer-source.png"
    source_path.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    imported = owner_upload.import_owner_upload(source_path)
    assert imported["state"] == "IMPORTED"
    source_id = str(imported["source_id"])
    source_bytes_before = (source_root / source_id / "source.png").read_bytes()
    validation = studio.validate_owner_source(source_id)
    candidate_id, bundle_path = studio._derive_owner_candidate(source_id, validation, source_root / source_id / "source.png")
    bundle = studio.read_bundle(bundle_path)
    source_lineage = bundle.metadata.get("generator_metadata", {})

    manifest = {
        "schema": JOB_SCHEMA,
        "schema_version": 1,
        "job_id": "p3-live-parity",
        "sources": [{
            "source_id": source_id,
            "source_sha256": imported["source_sha256"],
            "requested_size": {"width": 20, "height": 20},
            "background_intent": "FULL",
            "csv_row_id": "csv-row-001",
        }],
    }
    job_path = tmp_path / "producer_job.json"
    job_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")
    job_path.write_bytes(job_bytes)
    job = load_job(job_path)
    source = job["sources"][0]
    studio_request = {
        "source_id": source_id,
        "source_lineage": source_lineage,
        "headless_job_id": job["job_id"],
        "headless_manifest_digest": job["manifest_digest"],
        "headless_csv_row_id": source["csv_row_id"],
        "producer_request": {
            "csv_row_id": source["csv_row_id"],
            "requested_size": {"width": 20, "height": 20},
            "background_intent": "FULL",
        },
    }
    # The existing Studio source action and the CLI both use the same canonical route and inputs.
    studio_run = studio.run_pipeline(source_id=source_id, request=studio_request)
    studio_pipeline_path = studio._pipeline_path(str(studio_run["run_id"]))
    studio_pipeline = studio._read_json(studio_pipeline_path)

    summary = run_job(job_path)
    assert summary["READY"] == 1
    assert summary["sources"][0]["source_id"] == source_id
    cli_events = _read_events(job)
    zip_event = next(event for event in cli_events if event.get("source_id") == source_id and event.get("stage") == "ZIP_SUPPLY_SOLVE_DIFFICULTY" and event.get("disposition") == "PASS")
    cli_pipeline = studio._read_json(repository / zip_event["canonical_references"][0])

    assert cli_pipeline["candidate_id"] == studio_pipeline["candidate_id"] == candidate_id
    assert cli_pipeline["request"] == studio_pipeline["request"]
    assert cli_pipeline["stages"] == studio_pipeline["stages"]
    assert cli_pipeline["primary"]["acceptance"] == studio_pipeline["primary"]["acceptance"]
    assert cli_pipeline["primary"]["difficulty"] == studio_pipeline["primary"]["difficulty"]
    assert cli_pipeline["primary"]["result"]["supply_columns"] == studio_pipeline["primary"]["result"]["supply_columns"]
    assert (source_root / source_id / "source.png").read_bytes() == source_bytes_before
    assert job_path.read_bytes() == job_bytes
    inbox = studio.candidate_inbox()
    queued = next(item for item in inbox["candidates"] if item["candidate_id"] == candidate_id)
    assert queued["owner_review"]["disposition"] == "NEEDS_REVIEW"
