"""Owner 2026-11-25: Release Pool READY_AUTO levels can be sent to the game; REJECTed ones cannot."""
from scrubbots_pixel_factory import studio_extensions as studio
from scrubbots_pixel_factory.supply_pipeline import release_pool


def _entry(candidate_id, source="READY_AUTO", review_id=None):
    return {"candidate_id": candidate_id, "eligibility_source": source, "review_id": review_id,
            "candidate_classification": {"candidate_class": "PRODUCTION_CANDIDATE"},
            "candidate": {"candidate_id": candidate_id}}


def test_ready_auto_entries_are_releasable_unless_rejected(monkeypatch):
    entries = [_entry("candidate-a"), _entry("candidate-b"), _entry("candidate-c", "OWNER_ACCEPT", "r-c")]
    reviews = {"candidate-b": {"disposition": "REJECT", "review_id": "r-b"},
               "candidate-c": {"disposition": "ACCEPT", "review_id": "r-c"}}
    monkeypatch.setattr(release_pool, "release_entries", lambda *a, **k: entries)
    monkeypatch.setattr(studio, "_latest_review", lambda cid: reviews.get(cid, {}))
    ids = [e["candidate_id"] for e in release_pool._production_release_entries()]
    assert ids == ["candidate-a", "candidate-c"]
