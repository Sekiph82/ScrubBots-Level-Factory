"""One SQLite store for the Factory's image, status, candidate, READY and batch records (P0-P).

S1 scope: schema, append-only status history enforced by the database, and a one-shot
read-only import of today's file stores with an independent parity report. Nothing in the
app reads or writes this database yet; the old files stay the authority until S2.

    python -B -m scrubbots_pixel_factory.factory_db import   # builds data/Level Factory/factory.db
    python -B -m scrubbots_pixel_factory.factory_db parity   # re-checks an existing DB against the files
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from typing import Any, Iterable

from . import owner_art_storage
from . import owner_release_library as library

SCHEMA_VERSION = 1
STATUSES = tuple(sorted(library.STATUSES))

_DDL = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);

-- PixelLab Final PNGs (the only intake folder), keyed by file name.
CREATE TABLE images (
    final_name TEXT PRIMARY KEY,
    source_sha256 TEXT NOT NULL,
    bytes INTEGER NOT NULL,
    mtime_ns INTEGER NOT NULL
);
CREATE INDEX images_sha ON images(source_sha256);

-- Imported source records (data/Level Factory/Imported/<source_id>/source.json).
CREATE TABLE sources (
    source_id TEXT PRIMARY KEY,
    source_sha256 TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    record_sha256 TEXT NOT NULL,
    record_json TEXT NOT NULL
);
CREATE INDEX sources_sha ON sources(source_sha256);

-- Immutable status history: the exact event bytes of the owner release library chain.
CREATE TABLE status_events (
    source_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'READY', 'FAILED', 'REJECTED')),
    created_at TEXT NOT NULL,
    previous_event_sha256 TEXT,
    event_sha256 TEXT NOT NULL UNIQUE,
    event_json TEXT NOT NULL,
    PRIMARY KEY (source_id, sequence)
);

-- Current status, maintained only by the trigger below (same transaction as its event).
CREATE TABLE status (
    source_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    event_sha256 TEXT NOT NULL
);
CREATE INDEX status_by_status ON status(status);

CREATE TRIGGER status_events_chain BEFORE INSERT ON status_events
WHEN NEW.sequence != COALESCE((SELECT MAX(sequence) FROM status_events WHERE source_id = NEW.source_id), 0) + 1
  OR NEW.previous_event_sha256 IS NOT (SELECT event_sha256 FROM status_events
                                       WHERE source_id = NEW.source_id ORDER BY sequence DESC LIMIT 1)
BEGIN SELECT RAISE(ABORT, 'status event breaks the source history chain'); END;

CREATE TRIGGER status_events_project AFTER INSERT ON status_events
BEGIN
    INSERT INTO status (source_id, status, sequence, event_sha256)
    VALUES (NEW.source_id, NEW.status, NEW.sequence, NEW.event_sha256)
    ON CONFLICT(source_id) DO UPDATE SET status = excluded.status, sequence = excluded.sequence,
                                         event_sha256 = excluded.event_sha256;
END;

CREATE TRIGGER status_events_no_update BEFORE UPDATE ON status_events
BEGIN SELECT RAISE(ABORT, 'status history is append-only'); END;

-- The owner purges rejected art completely (2026-11-15): only a REJECTED source's history may go.
CREATE TRIGGER status_events_delete_rejected_only BEFORE DELETE ON status_events
WHEN (SELECT status FROM status WHERE source_id = OLD.source_id) IS NOT 'REJECTED'
BEGIN SELECT RAISE(ABORT, 'only a REJECTED source history can be purged'); END;

CREATE TRIGGER status_no_direct_update BEFORE UPDATE ON status
WHEN NEW.event_sha256 IS NOT (SELECT event_sha256 FROM status_events
                              WHERE source_id = NEW.source_id ORDER BY sequence DESC LIMIT 1)
BEGIN SELECT RAISE(ABORT, 'status changes only through a history event'); END;

-- Validated candidate rows (one per candidate bundle).
CREATE TABLE candidates (
    candidate_id TEXT PRIMARY KEY,
    source_id TEXT,
    row_json TEXT NOT NULL
);
CREATE INDEX candidates_source ON candidates(source_id);

-- Release Pool candidate entries (Ready/<candidate>-<run>-ready.json).
CREATE TABLE release_entries (
    entry_name TEXT PRIMARY KEY,
    folder TEXT NOT NULL,
    candidate_id TEXT NOT NULL,
    pipeline_run_id TEXT NOT NULL,
    entry_digest TEXT NOT NULL,
    game_commit TEXT,
    real_play_verdict TEXT,
    file_sha256 TEXT NOT NULL,
    entry_json TEXT NOT NULL
);
CREATE INDEX release_entries_candidate ON release_entries(candidate_id);

-- PNG batch jobs and folder-import batches, stored as their exact JSON.
CREATE TABLE batch_records (
    kind TEXT NOT NULL CHECK (kind IN ('JOB', 'IMPORT')),
    name TEXT NOT NULL,
    file_sha256 TEXT NOT NULL,
    record_json TEXT NOT NULL,
    PRIMARY KEY (kind, name)
);
"""


class FactoryDbError(RuntimeError):
    """The factory database is missing, unsafe, or disagrees with its source files."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def db_path(repository_root: str | Path | None = None) -> Path:
    return owner_art_storage.owner_art_paths(repository_root)["level_factory"] / "factory.db"


def connect(path: str | Path, *, create: bool = False) -> sqlite3.Connection:
    path = Path(path)
    if not create and not path.is_file():
        raise FactoryDbError(f"factory database is missing: {path}")
    conn = sqlite3.connect(path, timeout=30, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    if create:
        conn.execute("PRAGMA journal_mode = WAL")
        if conn.execute("PRAGMA user_version").fetchone()[0] == 0:
            conn.executescript(_DDL)
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version != SCHEMA_VERSION:
        conn.close()
        raise FactoryDbError(f"factory database schema {version} is not {SCHEMA_VERSION}")
    return conn


def append_status_event(conn: sqlite3.Connection, event_json: str) -> str:
    """Append one owner release library event (its exact canonical bytes); returns its SHA-256."""
    raw = event_json.encode("utf-8")
    event = json.loads(event_json)
    if library._json_bytes(event) != raw or event.get("schema") != library.SCHEMA:
        raise FactoryDbError("status event is not in canonical owner release library form")
    digest = _sha(raw)
    conn.execute(
        "INSERT INTO status_events (source_id, sequence, status, created_at, previous_event_sha256, event_sha256, event_json)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (event["source_id"], event["sequence"], event["status"], event["created_at"],
         event.get("previous_event_sha256"), digest, event_json))
    return digest


def status_counts(conn: sqlite3.Connection) -> dict[str, int]:
    counts = dict.fromkeys(STATUSES, 0)
    counts.update(dict(conn.execute("SELECT status, COUNT(*) FROM status GROUP BY status")))
    return counts


def verify_chains(conn: sqlite3.Connection) -> list[str]:
    """Full re-verification of every stored history (the on-demand integrity check, never at startup)."""
    errors: list[str] = []
    previous: dict[str, str | None] = {}
    for source_id, sequence, sha, prev, text in conn.execute(
            "SELECT source_id, sequence, event_sha256, previous_event_sha256, event_json"
            " FROM status_events ORDER BY source_id, sequence"):
        if _sha(text.encode("utf-8")) != sha:
            errors.append(f"{source_id}#{sequence}: stored event bytes do not match their SHA-256")
        if prev != previous.get(source_id) or (sequence == 1) != (source_id not in previous):
            errors.append(f"{source_id}#{sequence}: chain link is broken")
        previous[source_id] = sha
    return errors


# --- S2: the DB is the read authority; status writes still land in the files first -----------

def open_existing(repository_root: str | Path | None = None) -> sqlite3.Connection | None:
    """The installed database, or None when this data root has none (tests, old layouts)."""
    path = db_path(repository_root)
    return connect(path) if path.is_file() else None


def _file_history_names(pool: Path, source_id: str) -> list[str]:
    folder = pool / ".history" / source_id
    return sorted(p.name for p in folder.glob("*.json")) if folder.is_dir() else []


def sync_source_history(conn: sqlite3.Connection, pool: Path, source_id: str) -> int:
    """Bring one source's DB history level with its file chain; returns events appended (-n when purged).

    Appends only events the DB lacks; a DB event that differs from the file at the same
    sequence is a conflict, never overwritten. A history the owner purged (rejected art)
    is removed from the DB only when the DB also says REJECTED.
    """
    names = _file_history_names(pool, source_id)
    stored = [row[0] for row in conn.execute(
        "SELECT event_sha256 FROM status_events WHERE source_id = ? ORDER BY sequence", (source_id,))]
    if not names and stored:
        conn.execute("BEGIN IMMEDIATE")
        try:
            conn.execute("DELETE FROM status_events WHERE source_id = ?", (source_id,))
            conn.execute("DELETE FROM status WHERE source_id = ?", (source_id,))
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK"); raise
        return -len(stored)
    for name, sha in zip(names, stored):
        if not name.endswith(f"-{sha}.json"):
            raise FactoryDbError(f"{source_id}: DB history differs from the file chain at {name}")
    if len(stored) > len(names):
        raise FactoryDbError(f"{source_id}: DB holds events the file chain does not")
    if len(stored) == len(names):
        return 0
    events = library._history(pool, source_id)  # verifies the whole file chain before copying
    conn.execute("BEGIN IMMEDIATE")
    try:
        for event in events[len(stored):]:
            append_status_event(conn, library._json_bytes(event).decode("utf-8"))
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK"); raise
    return len(events) - len(stored)


def heal_from_files(conn: sqlite3.Connection, pool: Path) -> dict[str, Any]:
    """Cheap startup drift check (~0.3 s): per-source event counts in the files versus the DB."""
    files: dict[str, int] = {}
    history = pool / ".history"
    if history.is_dir():
        with os.scandir(history) as entries:
            for entry in entries:
                if entry.is_dir():
                    files[entry.name] = sum(1 for name in os.listdir(entry.path) if name.endswith(".json"))
    stored = dict(conn.execute("SELECT source_id, MAX(sequence) FROM status_events GROUP BY source_id"))
    drift = sorted(sid for sid in set(files) | set(stored) if files.get(sid, 0) != stored.get(sid, 0))
    healed, errors = 0, []
    for source_id in drift:
        try:
            healed += abs(sync_source_history(conn, pool, source_id))
        except (FactoryDbError, library.OwnerReleaseLibraryError, sqlite3.Error) as exc:
            errors.append(f"{source_id}: {exc}"[:300])
    return {"sources": len(files), "drifted": len(drift), "events_healed": healed, "errors": errors}


def status_rows(conn: sqlite3.Connection, status: str | None = None, source_id: str | None = None) -> list[dict[str, Any]]:
    """The owner release library view (current event of each source + its SHA), newest first."""
    sql = ("SELECT e.event_json, e.event_sha256 FROM status s JOIN status_events e"
           " ON e.source_id = s.source_id AND e.sequence = s.sequence")
    clauses, args = [], []
    if status is not None:
        clauses.append("s.status = ?"); args.append(status)
    if source_id is not None:
        clauses.append("s.source_id = ?"); args.append(source_id)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    rows = []
    for text, sha in conn.execute(sql, args):
        row = json.loads(text); row["event_sha256"] = sha; rows.append(row)
    rows.sort(key=lambda row: (str(row.get("created_at", "")), str(row.get("source_id", ""))), reverse=True)
    return rows


def insert_release_entry(conn: sqlite3.Connection, path: Path) -> None:
    """Mirror one immutable Release Pool entry file (validated by name and entry digest)."""
    status = next(s for s in STATUSES if s.title() == path.parent.name)
    conn.execute("INSERT OR IGNORE INTO release_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", _release_entry_row(path, status))


def release_entry_rows(conn: sqlite3.Connection, candidate_id: str | None = None) -> list[dict[str, Any]]:
    """Current Release Pool entries, one per candidate (owner-accepted first, then newest run)."""
    sql = "SELECT entry_json FROM release_entries WHERE folder = 'Ready'"
    args: tuple = ()
    if candidate_id is not None:
        sql += " AND candidate_id = ?"; args = (candidate_id,)
    best: dict[str, dict[str, Any]] = {}
    for (text,) in conn.execute(sql + " ORDER BY candidate_id, pipeline_run_id", args):
        entry = json.loads(text)
        current = best.get(entry["candidate_id"])
        if current is None or (entry.get("eligibility_source") == "OWNER_ACCEPT") >= (current.get("eligibility_source") == "OWNER_ACCEPT"):
            best[entry["candidate_id"]] = entry
    return [best[key] for key in sorted(best)]


def upsert_source_record(conn: sqlite3.Connection, record_path: Path) -> None:
    text, digest = _read_text(record_path)
    value = json.loads(text)
    conn.execute("INSERT INTO sources VALUES (?, ?, ?, ?, ?) ON CONFLICT(source_id) DO UPDATE SET"
                 " source_sha256 = excluded.source_sha256, original_filename = excluded.original_filename,"
                 " record_sha256 = excluded.record_sha256, record_json = excluded.record_json",
                 (value["source_id"], value["source_sha256"], str(value.get("original_filename", "")), digest, text))


# --- one-shot import from today's files (S1) -------------------------------------------------

def _files(folder: Path, pattern: str) -> list[Path]:
    return sorted(folder.glob(pattern), key=lambda p: p.name) if folder.is_dir() else []


def _read_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    return raw.decode("utf-8"), _sha(raw)


def _final_images(paths: dict[str, Path]) -> Iterable[tuple[str, str, int, int]]:
    for path in _files(paths["pixellab_final"], "*.png"):
        info = path.stat()
        yield path.name, _sha(path.read_bytes()), info.st_size, info.st_mtime_ns


def _sources(paths: dict[str, Path]) -> Iterable[tuple[str, str, str, str, str]]:
    for record in _files(paths["imported"], "*/source.json"):
        text, digest = _read_text(record)
        value = json.loads(text)
        if value.get("source_id") != record.parent.name:
            raise FactoryDbError(f"source record identity does not match its folder: {record}")
        yield value["source_id"], value["source_sha256"], str(value.get("original_filename", "")), digest, text


def _release_entry_row(path: Path, status: str) -> tuple:
    text, digest = _read_text(path)
    value = json.loads(text)
    # Validates name, schema and entry digest exactly as the status library does.
    library._is_release_pool_entry_projection(path, status, value)
    play = value.get("real_play") if isinstance(value.get("real_play"), dict) else {}
    return (path.name, status.title(), value["candidate_id"], value["pipeline_run_id"], value["entry_digest"],
            play.get("gameCommit"), play.get("verdict"), digest, text)


def _release_entries(pool: Path) -> Iterable[tuple]:
    for status in STATUSES:
        for path in _files(pool / status.title(), "candidate-owner-*.json"):
            yield _release_entry_row(path, status)


def _batch_records(paths: dict[str, Path]) -> Iterable[tuple[str, str, str, str]]:
    for kind, folder in (("JOB", paths["batch_jobs"] / "jobs"), ("IMPORT", paths["batch_imports"])):
        for path in _files(folder, "*.json"):
            text, digest = _read_text(path)
            yield kind, path.name, digest, text


def _candidate_rows() -> Iterable[tuple[str, str | None, str]]:
    from . import studio_extensions
    for row in studio_extensions.list_candidates():
        lineage = row.get("source_lineage") if isinstance(row.get("source_lineage"), dict) else {}
        yield (str(row["candidate_id"]), lineage.get("source_id"),
               json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def import_from_files(target: Path, repository_root: str | Path | None = None, *,
                      candidate_rows: Iterable[tuple[str, str | None, str]] | None = None,
                      progress=print) -> dict[str, Any]:
    """Copy today's file stores into a new database at ``target`` (read-only on the files)."""
    paths = owner_art_storage.owner_art_paths(repository_root)
    pool = paths["release_pool"]
    if target.exists():
        raise FactoryDbError(f"refusing to overwrite {target}")
    conn = connect(target, create=True)
    started = time.monotonic()
    try:
        conn.execute("BEGIN")
        conn.executemany("INSERT INTO images VALUES (?, ?, ?, ?)", _final_images(paths))
        progress(f"images {conn.execute('SELECT COUNT(*) FROM images').fetchone()[0]}")
        conn.executemany("INSERT INTO sources VALUES (?, ?, ?, ?, ?)", _sources(paths))
        progress(f"sources {conn.execute('SELECT COUNT(*) FROM sources').fetchone()[0]}")
        histories = sorted(p for p in (pool / ".history").iterdir() if p.is_dir()) if (pool / ".history").is_dir() else []
        for folder in histories:
            for event in library._history(pool, folder.name):  # verifies the chain once, here
                append_status_event(conn, library._json_bytes(event).decode("utf-8"))
        progress(f"status histories {len(histories)}")
        conn.executemany("INSERT INTO release_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", _release_entries(pool))
        conn.executemany("INSERT INTO batch_records VALUES (?, ?, ?, ?)", _batch_records(paths))
        conn.executemany("INSERT INTO candidates VALUES (?, ?, ?)",
                         _candidate_rows() if candidate_rows is None else candidate_rows)
        progress(f"candidates {conn.execute('SELECT COUNT(*) FROM candidates').fetchone()[0]}")
        conn.executemany("INSERT INTO meta VALUES (?, ?)", [
            ("imported_at", datetime.now(timezone.utc).isoformat()),
            ("imported_from", str(Path(paths["level_factory"]).parent)),
            ("import_seconds", f"{time.monotonic() - started:.1f}")])
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK") if conn.in_transaction else None
        conn.close()
        target.unlink(missing_ok=True)
        raise
    return {"seconds": round(time.monotonic() - started, 1)}


def parity_report(conn: sqlite3.Connection, repository_root: str | Path | None = None, *,
                  candidate_folders: set[str] | None = None) -> dict[str, Any]:
    """Re-read the files independently and list every difference from the database."""
    paths = owner_art_storage.owner_art_paths(repository_root)
    pool = paths["release_pool"]
    diffs: dict[str, list] = {}

    def compare(name: str, files: dict, db: dict) -> dict[str, int]:
        missing = sorted(set(files) - set(db)); extra = sorted(set(db) - set(files))
        changed = sorted(k for k in set(files) & set(db) if files[k] != db[k])
        if missing or extra or changed:
            diffs[name] = [{"missing_in_db": missing[:50], "extra_in_db": extra[:50], "different": changed[:50]}]
        return {"files": len(files), "db": len(db), "missing": len(missing), "extra": len(extra), "different": len(changed)}

    report: dict[str, Any] = {}
    report["final_images"] = compare("final_images",
        {p.name: _sha(p.read_bytes()) for p in _files(paths["pixellab_final"], "*.png")},
        dict(conn.execute("SELECT final_name, source_sha256 FROM images")))
    report["sources"] = compare("sources",
        {p.parent.name: _sha(p.read_bytes()) for p in _files(paths["imported"], "*/source.json")},
        dict(conn.execute("SELECT source_id, record_sha256 FROM sources")))
    # Current status: the library's own full verified view versus the trigger-maintained table.
    view = library.list_records(repository_root=repository_root, from_files=True)
    report["status"] = compare("status",
        {r["source_id"]: (r["status"], r["event_sha256"]) for r in view["records"]},
        {sid: (st, sha) for sid, st, sha in conn.execute("SELECT source_id, status, event_sha256 FROM status")})
    report["status_counts"] = {"files": view["counts"], "db": status_counts(conn)}
    if view["counts"] != report["status_counts"]["db"]:
        diffs["status_counts"] = [report["status_counts"]]
    report["history_events"] = compare("history_events",
        {f"{p.parent.name}/{p.name}": _sha(p.read_bytes()) for p in _files(pool / ".history", "*/*.json")},
        {f"{sid}/{seq:06d}-{sha}.json": sha for sid, seq, sha in
         conn.execute("SELECT source_id, sequence, event_sha256 FROM status_events")})
    report["release_entries"] = compare("release_entries",
        {f"{s.title()}/{p.name}": _sha(p.read_bytes()) for s in STATUSES for p in _files(pool / s.title(), "candidate-owner-*.json")},
        {f"{folder}/{name}": sha for name, folder, sha in conn.execute("SELECT entry_name, folder, file_sha256 FROM release_entries")})
    report["batch_records"] = compare("batch_records",
        {f"{kind}/{p.name}": _sha(p.read_bytes()) for kind, folder in (("JOB", paths["batch_jobs"] / "jobs"), ("IMPORT", paths["batch_imports"]))
         for p in _files(folder, "*.json")},
        {f"{kind}/{name}": sha for kind, name, sha in conn.execute("SELECT kind, name, file_sha256 FROM batch_records")})
    if candidate_folders is not None:
        # A bundle that fails validation has no row by design: listed, not a difference.
        stored = {c for (c,) in conn.execute("SELECT candidate_id FROM candidates")}
        report["candidates"] = {"folders": len(candidate_folders), "db": len(stored),
                                "folders_without_valid_row": sorted(candidate_folders - stored)[:200],
                                "rows_without_folder": sorted(stored - candidate_folders)}
        if stored - candidate_folders:
            diffs["candidates"] = report["candidates"]["rows_without_folder"][:50]
    chain_errors = verify_chains(conn)
    if chain_errors:
        diffs["chains"] = chain_errors[:50]
    report["chain_errors"] = len(chain_errors)
    report["differences"] = diffs
    report["ok"] = not diffs
    return report


def _main(argv: list[str]) -> int:
    command = argv[0] if argv else ""
    target = db_path()
    if command == "import":
        if target.exists():
            print(f"refusing: {target} exists"); return 2
        partial = target.with_name(target.name + ".partial")
        for leftover in (partial, Path(f"{partial}-wal"), Path(f"{partial}-shm")):
            leftover.unlink(missing_ok=True)
        print(import_from_files(partial))
    elif command == "parity":
        partial = target
    else:
        print(__doc__); return 2
    conn = connect(partial)
    from . import studio_extensions
    report = parity_report(conn, candidate_folders={p.name for p in studio_extensions._candidate_roots()})
    conn.close()
    out = Path(owner_art_storage.factory_repository_root()) / "docs" / "evidence" / "claude-factory-db-20261117" / "parity.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "differences"}, indent=1))
    print("parity", "PASS" if report["ok"] else "FAIL", "->", out)
    if command == "import" and report["ok"]:
        os.replace(partial, target)
        print("installed", target)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
