"""A source skipped by batch planning as already READY must stop counting as Pending (owner 2026-11-18)."""
import inspect

from scrubbots_pixel_factory import owner_release_library, png_batch, studio_extensions


def test_verified_ready_but_pending_source_is_recorded_ready(monkeypatch):
    pending = {"owner-upload-a"}
    calls = []
    monkeypatch.setattr(owner_release_library, "list_records",
                        lambda status=None, source_id=None, **_k: {"records": [{"source_id": source_id}] if source_id in pending else []})
    monkeypatch.setattr(owner_release_library, "transition_pipeline", lambda sid, pipeline, **_k: calls.append((sid, pipeline["run_id"])))
    monkeypatch.setattr(studio_extensions, "_pipeline_path", lambda run_id: run_id)
    monkeypatch.setattr(studio_extensions, "_read_json", lambda path: {"run_id": path, "disposition": "READY"})

    png_batch._record_verified_ready([
        {"source_id": "owner-upload-a", "pipeline_run_id": "pipeline-1"},
        {"source_id": "owner-upload-b", "pipeline_run_id": "pipeline-2"},  # already READY: untouched
    ])

    assert calls == [("owner-upload-a", "pipeline-1")]


def test_batch_planning_records_the_ready_sources_it_excludes():
    assert "_record_verified_ready(excluded_ready)" in inspect.getsource(png_batch.create_png_batch)
