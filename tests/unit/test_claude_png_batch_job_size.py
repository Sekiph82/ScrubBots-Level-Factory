"""Regression 2026-11-13: the owner's 1256-PNG batch stopped at 211 READY.

Each READY item adds ~2 KB of proof refs to the job file. At 1,048,170 bytes the
next write crossed the old 1 MiB cap, _write_job raised, and the coordinator
stopped while six finished READY PNGs stayed RUNNING on disk.
"""
from scrubbots_pixel_factory import png_batch


def test_full_1256_png_batch_job_fits_the_state_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(png_batch, "_job_path", lambda job_id: tmp_path / "jobs" / f"{job_id}.json")
    ready_item = {"status": "READY", "source_id": "owner-upload-" + "a" * 64, "artifact_refs": {"level": "x" * 1200}, "release_pool": {"row": "y" * 1000}}
    job = {"schema": png_batch.JOB_SCHEMA, "version": png_batch.JOB_VERSION, "job_id": "png-batch-size",
           "items": [dict(ready_item, index=i) for i in range(1256)]}
    saved = png_batch._write_job(job)
    assert (tmp_path / "jobs" / "png-batch-size.json").stat().st_size > 1024 * 1024
    assert png_batch._read_job("png-batch-size")["state_digest"] == saved["state_digest"]
