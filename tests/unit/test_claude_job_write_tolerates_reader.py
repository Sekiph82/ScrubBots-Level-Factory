"""Regression 2026-11-13 18:36: the 1013-PNG batch coordinator died while six PNGs were
finishing READY. On Windows os.replace onto a file another process has open fails with
PermissionError (WinError 5); the Studio reads the job file every 2.5 s."""
import threading

from scrubbots_pixel_factory import png_batch


def test_job_write_waits_for_a_brief_reader_instead_of_failing(tmp_path, monkeypatch):
    monkeypatch.setattr(png_batch, "_job_path", lambda job_id: tmp_path / f"{job_id}.json")
    job = {"schema": png_batch.JOB_SCHEMA, "version": png_batch.JOB_VERSION, "job_id": "png-batch-reader", "items": []}
    png_batch._write_job(job)
    reader = open(tmp_path / "png-batch-reader.json", encoding="utf-8")
    threading.Timer(0.4, reader.close).start()

    saved = png_batch._write_job(dict(job, state="RUNNING"))

    assert png_batch._read_job("png-batch-reader")["state_digest"] == saved["state_digest"]
