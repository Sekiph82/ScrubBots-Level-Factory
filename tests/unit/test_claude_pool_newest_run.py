"""A level with two READY runs (e.g. an EASY difficulty variant) is listed by its newest run.

The verified read already keeps only the newest READY run per candidate; the DB fast path
ordered by the random pipeline run id instead, so the chosen run was arbitrary.
"""
import json
import sqlite3

from scrubbots_pixel_factory import factory_db

CID = "candidate-owner-" + "f" * 48


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE release_entries (entry_name TEXT PRIMARY KEY, folder TEXT, candidate_id TEXT, pipeline_run_id TEXT,"
                 " entry_digest TEXT, game_commit TEXT, real_play_verdict TEXT, file_sha256 TEXT, entry_json TEXT)")
    # run id order (a < z) is the opposite of creation order
    for run_id, created, score in (("pipeline-zzz", "2026-11-01T00:00:00+00:00", 50.0), ("pipeline-aaa", "2026-11-24T00:00:00+00:00", 40.0)):
        entry = {"candidate_id": CID, "pipeline_run_id": run_id, "challenge_score": score, "difficulty_class": "EASY",
                 "pipeline": {"run_id": run_id, "created_at": created, "primary": {"state": "READY"}}, "candidate": {}}
        conn.execute("INSERT INTO release_entries VALUES (?, 'Ready', ?, ?, 'd', NULL, NULL, 's', ?)",
                     (f"{run_id}.json", CID, run_id, json.dumps(entry)))
    return conn


def test_full_and_slim_rows_pick_the_newest_ready_run() -> None:
    conn = _db()
    assert [row["challenge_score"] for row in factory_db.release_entry_rows(conn)] == [40.0]
    assert [row["challenge_score"] for row in factory_db.slim_release_entry_rows(conn)] == [40.0]
