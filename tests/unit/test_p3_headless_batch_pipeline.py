from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scrubbots_pixel_factory import owner_upload, studio_extensions as studio
from scrubbots_pixel_factory.cli.main import main
from scrubbots_pixel_factory.headless_pipeline import (
    EVENT_SCHEMA,
    JOB_SCHEMA,
    PipelineInterruption,
    load_job,
    run_job,
    status_job,
)
from scrubbots_pixel_factory.output.png import encode_logical_png


def _install_fake_canonical_route(monkeypatch, tmp_path: Path) -> dict[str, object]:
    repository = tmp_path / "repository"
    source_root = repository / "level_factory" / "output" / "owner-uploads"
    evidence_root = repository / "level_factory" / "output" / "studio-extensions"
    source_root.mkdir(parents=True)
    evidence_root.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence_root)

    source_png = tmp_path / "source.png"
    cells = ["C01", "C02", "C03", "C04"] * 100
    source_png.write_bytes(encode_logical_png(20, 20, cells))
    imported = owner_upload.import_owner_upload(source_png)
    assert imported["state"] == "IMPORTED"
    source_id = str(imported["source_id"])
    source_sha = str(imported["source_sha256"])
    source_bytes = (source_root / source_id / "source.png").read_bytes()

    manifest = {
        "schema": JOB_SCHEMA,
        "schema_version": 1,
        "job_id": "p3-test-job",
        "sources": [{
            "source_id": source_id,
            "source_sha256": source_sha,
            "requested_size": {"width": 20, "height": 20},
            "background_intent": "FULL",
            "csv_row_id": "row-0001",
        }],
    }
    job_path = tmp_path / "producer_job.json"
    job_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")
    job_path.write_bytes(job_bytes)
    candidate_id = f"candidate-owner-{source_sha[:48]}"
    bundle_path = repository / "level_factory" / "output" / "studio-derived-candidates" / candidate_id
    bundle_path.mkdir(parents=True)
    artwork_png = b"immutable canonical test artwork"
    bundle = SimpleNamespace(
        artwork_png=artwork_png,
        artwork=SimpleNamespace(grid_hash="a" * 64),
        metadata={"generator_metadata": {"data": {"source_lineage": {"source_id": source_id, "source_sha256": source_sha}}}},
    )
    monkeypatch.setattr(studio, "_derive_owner_candidate", lambda *_args: (candidate_id, bundle_path))
    monkeypatch.setattr(studio, "read_bundle", lambda *_args: bundle)
    canonical_candidate = {
        "candidate_id": candidate_id,
        "source_path": bundle_path.relative_to(repository).as_posix(),
        "source_lineage": {"source_sha256": source_sha},
        "artwork_sha256": hashlib.sha256(artwork_png).hexdigest(),
        "grid_hash": "a" * 64,
    }
    monkeypatch.setattr(studio, "list_candidates", lambda: [canonical_candidate])
    monkeypatch.setattr(studio, "candidate_inbox", lambda: {"candidates": [{**canonical_candidate, "owner_review": {"disposition": "NEEDS_REVIEW"}}]})

    route_calls: list[dict[str, object]] = []

    def run_canonical(*, source_id=None, candidate_id=None, request=None):
        route_calls.append({"source_id": source_id, "candidate_id": candidate_id, "request": dict(request or {})})
        run_id = f"pipeline-test-{len(route_calls)}"
        stages = [
            {"stage": "SOLVE", "disposition": "PASS", "reason": "game solve pass"},
            {"stage": "REPLAY", "disposition": "PASS", "reason": "fresh replay pass"},
            {"stage": "DIFFICULTY", "disposition": "PASS", "reason": "Difficulty V1 pass"},
            {"stage": "QA", "disposition": "PASS", "reason": "canonical QA pass", "evidence_reference": "level_factory/output/qa/result.json"},
            {"stage": "REVIEW", "disposition": "NOT_AVAILABLE", "reason": "owner review remains independent"},
        ]
        pipeline = {
            "schema": studio.PIPELINE_SCHEMA,
            "version": 2,
            "run_id": run_id,
            "candidate_id": candidate_id,
            "source_id": None,
            "request": dict(request or {}),
            "stages": stages,
            "disposition": "READY",
            "created_at": f"2026-10-02T00:00:0{len(route_calls)}+00:00",
        }
        path = studio._pipeline_path(run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(pipeline, sort_keys=True), encoding="utf-8")
        return pipeline

    monkeypatch.setattr(studio, "run_pipeline", run_canonical)
    return {
        "job_path": job_path,
        "job_bytes": job_bytes,
        "source_id": source_id,
        "source_sha256": source_sha,
        "source_root": source_root,
        "source_bytes": source_bytes,
        "route_calls": route_calls,
        "candidate_id": candidate_id,
        "bundle": bundle,
    }


def _interrupt_after(target: str):
    occurrences = 0

    def callback(_row_id: str, stage: str) -> None:
        nonlocal occurrences
        if stage == target:
            occurrences += 1
            completed_checkpoint = 1 if target in {"QA", "REVIEW"} else 2
            if occurrences == completed_checkpoint:
                raise PipelineInterruption(target)

    return callback


def test_pipeline_manifest_is_strict_and_read_only(monkeypatch, tmp_path: Path) -> None:
    fixture = _install_fake_canonical_route(monkeypatch, tmp_path)
    job = load_job(fixture["job_path"])
    assert job["sources"][0]["background_intent"] == "FULL"
    assert job["sources"][0]["requested_width"] == 20
    assert fixture["job_path"].read_bytes() == fixture["job_bytes"]

    summary = status_job(fixture["job_path"])
    assert summary["state"] == "IN_PROGRESS"
    assert summary["PENDING"] == 1
    assert fixture["route_calls"] == []
    assert fixture["job_path"].read_bytes() == fixture["job_bytes"]

    malformed = json.loads(fixture["job_bytes"])
    malformed["sources"][0]["requested_width"] = 20
    with pytest.raises(ValueError, match="requested_size or requested_width"):
        from scrubbots_pixel_factory.headless_pipeline import _normalize_source

        _normalize_source(malformed["sources"][0], 0)


@pytest.mark.parametrize("interrupt_stage", ["IMPORT", "NORMALIZE", "VALIDATE", "CANDIDATE", "ZIP_SUPPLY_SOLVE_DIFFICULTY", "QA", "REVIEW"])
def test_pipeline_resume_reuses_every_completed_stage_and_is_idempotent(monkeypatch, tmp_path: Path, interrupt_stage: str) -> None:
    fixture = _install_fake_canonical_route(monkeypatch, tmp_path)
    source_png = fixture["source_root"] / fixture["source_id"] / "source.png"
    with pytest.raises(PipelineInterruption):
        run_job(fixture["job_path"], after_checkpoint=_interrupt_after(interrupt_stage))
    interrupted_events = sorted((studio.extensions_root() / "pipelines" / "jobs").rglob("*.json"))
    assert interrupted_events, "the interrupted stage should already have durable event evidence"

    resumed = run_job(fixture["job_path"])
    assert resumed["state"] == "COMPLETE"
    assert resumed["READY"] == 1
    assert resumed["REJECTED"] == resumed["FAILED"] == 0
    assert resumed["sources"][0]["completed_stages"] == ["IMPORT", "NORMALIZE", "VALIDATE", "CANDIDATE", "ZIP_SUPPLY_SOLVE_DIFFICULTY", "QA", "REVIEW"]
    assert len(fixture["route_calls"]) == 1

    # A completed rerun only reads immutable job/pipeline evidence.
    completed_events = sorted((studio.extensions_root() / "pipelines" / "jobs").rglob("*.json"))
    repeated = run_job(fixture["job_path"])
    assert repeated == resumed
    assert sorted((studio.extensions_root() / "pipelines" / "jobs").rglob("*.json")) == completed_events
    assert len(fixture["route_calls"]) == 1
    assert source_png.read_bytes() == fixture["source_bytes"]
    assert fixture["job_path"].read_bytes() == fixture["job_bytes"]
    assert all(json.loads(path.read_text(encoding="utf-8"))["schema"] == EVENT_SCHEMA for path in completed_events)


def test_pipeline_cli_exposes_run_and_read_only_status(monkeypatch, tmp_path: Path, capsys) -> None:
    fixture = _install_fake_canonical_route(monkeypatch, tmp_path)
    result = main(["pipeline", "run", "--job", str(fixture["job_path"])])
    assert result == 0
    output = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert output[-1]["event"] == "summary"
    assert output[-1]["READY"] == 1

    result = main(["pipeline", "status", "--job", str(fixture["job_path"])])
    assert result == 0
    status = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert status["event"] == "status"
    assert status["sources"][0]["disposition"] == "READY"
    assert len(fixture["route_calls"]) == 1


def test_pipeline_rejects_dimension_mismatch_without_resampling(monkeypatch, tmp_path: Path) -> None:
    fixture = _install_fake_canonical_route(monkeypatch, tmp_path)
    manifest = json.loads(fixture["job_path"].read_text(encoding="utf-8"))
    manifest["sources"][0]["requested_size"] = {"width": 21, "height": 20}
    fixture["job_path"].write_text(json.dumps(manifest), encoding="utf-8")
    summary = run_job(fixture["job_path"])
    assert summary["REJECTED"] == 1
    assert "never resized" in summary["sources"][0]["reason"]
    assert fixture["route_calls"] == []
    assert (fixture["source_root"] / fixture["source_id"] / "source.png").read_bytes() == fixture["source_bytes"]


def test_pipeline_job_failure_does_not_corrupt_other_source_records(monkeypatch, tmp_path: Path) -> None:
    fixture = _install_fake_canonical_route(monkeypatch, tmp_path)
    manifest = json.loads(fixture["job_path"].read_text(encoding="utf-8"))
    manifest["sources"].append({
        "source_id": "owner-upload-" + "f" * 64,
        "source_sha256": "f" * 64,
        "requested_size": {"width": 20, "height": 20},
        "background_intent": "FULL",
        "csv_row_id": "row-0002",
    })
    fixture["job_path"].write_text(json.dumps(manifest), encoding="utf-8")
    summary = run_job(fixture["job_path"])
    assert summary["READY"] == 1
    assert summary["FAILED"] == 1
    assert summary["sources"][0]["disposition"] == "READY"
    assert summary["sources"][1]["disposition"] == "FAILED"
    assert "IMPORT:" in summary["sources"][1]["reason"]
    assert len(fixture["route_calls"]) == 1


def test_headless_pipeline_keeps_an_offline_core_and_review_boundary() -> None:
    source = (Path(__file__).resolve().parents[2] / "src" / "scrubbots_pixel_factory" / "headless_pipeline.py").read_text(encoding="utf-8").lower()
    forbidden = ("import requests", "import urllib", "import http", "httprequest", "api_key", "telemetry")
    assert not any(token in source for token in forbidden)
