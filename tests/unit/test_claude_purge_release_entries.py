"""A purged (owner-rejected) READY level must leave the Release Pool list: entry files and DB rows go."""
from __future__ import annotations

import sqlite3

from scrubbots_pixel_factory import factory_db
from scrubbots_pixel_factory.supply_pipeline import release_pool

GONE = "candidate-owner-" + "a" * 48
KEPT = "candidate-owner-" + "b" * 48


def test_purge_candidate_entries_removes_only_that_candidate(tmp_path, monkeypatch):
    # Arrange: two Ready entries on disk and in a release_entries table.
    pool = tmp_path / "Ready"
    pool.mkdir()
    for cid in (GONE, KEPT):
        (pool / f"{cid}-pipeline-1-ready.json").write_text("{}")
    db = tmp_path / "factory.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE release_entries (entry_name TEXT PRIMARY KEY, folder TEXT, candidate_id TEXT,"
                 " pipeline_run_id TEXT, entry_digest TEXT, game_commit TEXT, real_play_verdict TEXT,"
                 " file_sha256 TEXT, entry_json TEXT)")
    for cid in (GONE, KEPT):
        conn.execute("INSERT INTO release_entries (entry_name, folder, candidate_id, pipeline_run_id, entry_digest,"
                     " file_sha256, entry_json) VALUES (?, 'Ready', ?, 'r', 'd', 's', '{}')", (f"{cid}.json", cid))
    conn.commit()
    conn.close()
    monkeypatch.setattr(release_pool, "_pool_root", lambda: pool)
    monkeypatch.setattr(release_pool, "_factory_db", lambda: (factory_db, sqlite3.connect(db)))

    # Act
    deleted = release_pool.purge_candidate_entries(GONE)

    # Assert
    assert len(deleted) == 1 and deleted[0].endswith(f"{GONE}-pipeline-1-ready.json")
    assert sorted(p.name for p in pool.iterdir()) == [f"{KEPT}-pipeline-1-ready.json"]
    rows = sqlite3.connect(db).execute("SELECT candidate_id FROM release_entries").fetchall()
    assert rows == [(KEPT,)]
