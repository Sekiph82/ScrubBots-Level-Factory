"""Regression 2026-11-13: after Stop, the batch launcher spent minutes in
record_batch_outcomes re-projecting all 237 terminal items, although each one
was already recorded when it finished; the Studio stayed "Running" meanwhile."""
from scrubbots_pixel_factory import owner_release_library


def test_record_batch_outcomes_skips_items_already_recorded_with_same_status(monkeypatch):
    calls = []
    monkeypatch.setattr(owner_release_library, "transition_pipeline", lambda source_id, pipeline, repository_root=None: calls.append(source_id) or {"source_id": source_id})
    job = {"items": [
        {"source_id": "a", "status": "READY", "owner_release_projection": {"state": "RECORDED", "status": "READY"}},
        {"source_id": "b", "status": "FAILED", "owner_release_projection": {"state": "RECORDED", "status": "PENDING"}},
        {"source_id": "c", "status": "READY"},
        {"source_id": "d", "status": "QUEUED"},
    ]}

    owner_release_library.record_batch_outcomes(job)

    assert calls == ["b", "c"]
