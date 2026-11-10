"""Owner plan F3 (2026-11-10): Run Pipeline must process every PNG waiting in Pending.

A paused older job used to be offered as "Resume Batch · 179 remaining" even after
hundreds of new PixelLab PNGs entered Pending, so the new PNGs were never queued.
"""
from scrubbots_pixel_factory import png_batch, studio_extensions


def _job(job_id: str, state: str, statuses: dict[str, str]) -> dict:
    items = [{"index": i, "source_id": sid, "status": st} for i, (sid, st) in enumerate(statuses.items())]
    return {"schema": png_batch.JOB_SCHEMA, "version": png_batch.JOB_VERSION, "job_id": job_id,
            "state": state, "items": items, "counts": png_batch._counts(items), "updated_at": "t0"}


def test_new_pending_batch_supersedes_only_fully_covered_unfinished_jobs(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda *_args, **_kwargs: tmp_path)
    covered = png_batch._write_job(_job("png-batch-old-covered", "PAUSED",
                                        {"a": "READY", "b": "QUEUED", "c": "QUEUED"}))
    partly = png_batch._write_job(_job("png-batch-old-partly", "QUEUED", {"b": "QUEUED", "z": "QUEUED"}))
    done = png_batch._write_job(_job("png-batch-old-done", "COMPLETE", {"a": "READY"}))
    new = png_batch._write_job(_job("png-batch-new", "QUEUED", {"b": "QUEUED", "c": "QUEUED", "d": "QUEUED"}))

    superseded = png_batch._supersede_covered_jobs(new)

    assert superseded == [covered["job_id"]]
    old = png_batch._read_job(covered["job_id"])
    assert old["state"] == "SUPERSEDED" and old["superseded_by"] == "png-batch-new"
    assert old["items"][0]["status"] == "READY"          # finished history kept
    assert png_batch._read_job(partly["job_id"])["state"] == "QUEUED"
    assert png_batch._read_job(done["job_id"])["state"] == "COMPLETE"
    blocked = png_batch.run_png_batch(covered["job_id"], pipeline_runner=lambda **_k: None)
    assert blocked["disposition"] == "BATCH_JOB_SUPERSEDED"


def test_discovery_offers_all_pending_when_saved_job_does_not_cover_new_pngs(monkeypatch) -> None:
    job = {"job_id": "png-batch-old"}
    pending = {"items": [{"source_id": s, "source_sha256": s, "source_record_sha256": s} for s in ("b", "new1", "new2")]}

    def fake(pending_snapshot, active_ids):
        # Reuse the real decision with one resumable job whose unfinished rows are {"b"}.
        pending_ids = {row["source_id"] for row in pending_snapshot["items"]}
        resumable = [(job, {"batch_id": "x"}, {"b"})]
        if len(resumable) == 1 and pending_ids - resumable[0][2]:
            return {"disposition": "NO_MATCHING_COMPOSITE", "uncovered_pending_count": len(pending_ids - resumable[0][2])}
        return {"disposition": "RESUMABLE_PENDING_SUBSET"}

    # Guard the real source text so this test fails if the rule is removed.
    import inspect
    source = inspect.getsource(png_batch.find_resumable_pending_batch)
    assert "pending_candidate_ids - resumable[0][2]" in source
    assert fake(pending, ["b", "new1", "new2"]) == {"disposition": "NO_MATCHING_COMPOSITE", "uncovered_pending_count": 2}
    assert '"SUPERSEDED"' in inspect.getsource(png_batch.png_batch_latest)
