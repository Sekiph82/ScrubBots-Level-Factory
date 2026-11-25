"""Owner 2026-11-25: Release Pool READY_AUTO levels can be sent to the game; REJECTed ones cannot."""
from scrubbots_pixel_factory import studio_extensions as studio
from scrubbots_pixel_factory.supply_pipeline import release_pool


def _entry(candidate_id, source="READY_AUTO", review_id=None):
    return {"candidate_id": candidate_id, "eligibility_source": source, "review_id": review_id,
            "candidate_classification": {"candidate_class": "PRODUCTION_CANDIDATE"},
            "candidate": {"candidate_id": candidate_id}}


def test_ready_auto_entries_are_releasable_unless_rejected(monkeypatch, tmp_path):
    entries = [_entry("candidate-a"), _entry("candidate-b"), _entry("candidate-c", "OWNER_ACCEPT", "r-c")]
    reviews = {"candidate-b": {"disposition": "REJECT", "review_id": "r-b"},
               "candidate-c": {"disposition": "ACCEPT", "review_id": "r-c"}}
    monkeypatch.setattr(release_pool, "release_entries", lambda *a, **k: entries)
    monkeypatch.setattr(studio, "_latest_review", lambda cid: reviews.get(cid, {}))
    for name in ("candidate-b", "candidate-c"):
        (tmp_path / f"{name}.json").write_text('{"candidate_id": "%s"}' % name, encoding="utf-8")
    monkeypatch.setattr(studio, "_review_root", lambda: tmp_path)
    ids = [e["candidate_id"] for e in release_pool._production_release_entries()]
    assert ids == ["candidate-a", "candidate-c"]


def test_review_lookup_runs_only_for_candidates_with_review_records(monkeypatch, tmp_path):
    (tmp_path / "r1.json").write_text('{"candidate_id": "candidate-b"}', encoding="utf-8")
    entries = [_entry("candidate-a"), _entry("candidate-b")]
    looked_up = []
    monkeypatch.setattr(release_pool, "release_entries", lambda *a, **k: entries)
    monkeypatch.setattr(studio, "_review_root", lambda: tmp_path)
    monkeypatch.setattr(studio, "_latest_review", lambda cid: looked_up.append(cid) or {"disposition": "REJECT", "review_id": "r1"})
    ids = [e["candidate_id"] for e in release_pool._production_release_entries()]
    assert looked_up == ["candidate-b"]
    assert ids == ["candidate-a"]
