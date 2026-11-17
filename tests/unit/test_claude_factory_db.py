"""P0-P S1: factory.db schema, append-only history and one-shot import parity (temp roots only)."""
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from PIL import Image

from scrubbots_pixel_factory import factory_db
from scrubbots_pixel_factory import owner_art_storage
from scrubbots_pixel_factory import owner_release_library as lib


def _tree(root: Path) -> list[str]:
    paths = owner_art_storage.ensure_owner_art_layout(root)
    final = paths["pixellab_final"]; final.mkdir(parents=True, exist_ok=True)
    ids = []
    for i in range(3):
        png = final / f"LF-{i:06d}.png"
        image = Image.new("RGBA", (56, 56), (0, 0, 0, 0)); image.putpixel((i, i), (255, 69, 0, 255)); image.save(png)
        sha = hashlib.sha256(png.read_bytes()).hexdigest(); sid = "owner-upload-" + sha
        folder = paths["imported"] / sid; folder.mkdir(parents=True)
        (folder / "source.json").write_text(json.dumps({"source_id": sid, "source_sha256": sha,
                                                        "original_filename": png.name}), encoding="utf-8")
        lib.transition(sid, "PENDING", source_sha256=sha, provider="PIXELLAB", original_source_path=str(png), repository_root=root)
        ids.append(sid)
    first = lib.list_records(source_id=ids[0], repository_root=root)["records"][0]
    lib.transition(ids[0], "FAILED", source_sha256=first["source_sha256"], provider="PIXELLAB",
                   original_source_path=first["original_source_path"], reason="test", repository_root=root)
    jobs = paths["batch_jobs"] / "jobs"; jobs.mkdir(parents=True, exist_ok=True)
    (jobs / "png-batch-test.json").write_text('{"job_id":"png-batch-test"}', encoding="utf-8")
    return ids


def _build(tmp_path: Path) -> sqlite3.Connection:
    target = tmp_path / "factory.db"
    factory_db.import_from_files(target, tmp_path, candidate_rows=[], progress=lambda *_: None)
    return factory_db.connect(target)


def test_import_matches_files_exactly(tmp_path):
    ids = _tree(tmp_path)
    conn = _build(tmp_path)
    assert factory_db.status_counts(conn) == {"FAILED": 1, "PENDING": 2, "READY": 0, "REJECTED": 0}
    assert conn.execute("SELECT COUNT(*) FROM status_events").fetchone()[0] == 4
    assert conn.execute("SELECT status FROM status WHERE source_id = ?", (ids[0],)).fetchone()[0] == "FAILED"
    report = factory_db.parity_report(conn, tmp_path, candidate_folders=set())
    assert report["ok"], report["differences"]
    assert report["final_images"]["db"] == 3 and report["batch_records"]["db"] == 1


def test_parity_reports_a_changed_file(tmp_path):
    _tree(tmp_path)
    conn = _build(tmp_path)
    final = owner_art_storage.owner_art_paths(tmp_path)["pixellab_final"] / "LF-000001.png"
    final.write_bytes(final.read_bytes() + b"x")
    report = factory_db.parity_report(conn, tmp_path)
    assert not report["ok"] and report["final_images"]["different"] == 1


def test_history_is_append_only_and_status_follows_events(tmp_path):
    ids = _tree(tmp_path)
    conn = _build(tmp_path)
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        conn.execute("UPDATE status_events SET status = 'READY' WHERE source_id = ?", (ids[1],))
    with pytest.raises(sqlite3.IntegrityError, match="REJECTED"):
        conn.execute("DELETE FROM status_events WHERE source_id = ?", (ids[1],))
    with pytest.raises(sqlite3.IntegrityError, match="history event"):
        conn.execute("UPDATE status SET status = 'READY', event_sha256 = 'x' WHERE source_id = ?", (ids[1],))
    # A forged next event that does not link to the last one is refused.
    last = json.loads(conn.execute("SELECT event_json FROM status_events WHERE source_id = ? ORDER BY sequence DESC",
                                   (ids[1],)).fetchone()[0])
    forged = {**last, "sequence": last["sequence"] + 1, "status": "READY", "previous_event_sha256": "0" * 64}
    with pytest.raises(sqlite3.IntegrityError, match="chain"):
        factory_db.append_status_event(conn, lib._json_bytes(forged).decode("utf-8"))
    # A correctly linked event moves the current status in the same statement.
    linked = {**last, "sequence": last["sequence"] + 1, "status": "REJECTED",
              "previous_event_sha256": hashlib.sha256(lib._json_bytes(last)).hexdigest()}
    factory_db.append_status_event(conn, lib._json_bytes(linked).decode("utf-8"))
    assert conn.execute("SELECT status FROM status WHERE source_id = ?", (ids[1],)).fetchone()[0] == "REJECTED"
    conn.execute("DELETE FROM status_events WHERE source_id = ?", (ids[1],))  # purge of rejected art is allowed
    assert factory_db.verify_chains(conn) == []


def test_import_refuses_to_overwrite(tmp_path):
    _tree(tmp_path)
    _build(tmp_path).close()
    with pytest.raises(factory_db.FactoryDbError, match="overwrite"):
        factory_db.import_from_files(tmp_path / "factory.db", tmp_path, candidate_rows=[], progress=lambda *_: None)
