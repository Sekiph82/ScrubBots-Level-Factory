"""P0-P S2: startup reads factory.db and validates only new/changed Final files; writes are mirrored."""
from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory import factory_db, owner_release_library, owner_upload, studio_extensions
from scrubbots_pixel_factory.output.png import encode_logical_png


def _png(path: Path, first: str, second: str) -> None:
    colors = [first, second, "C05"]
    path.write_bytes(encode_logical_png(52, 52, [colors[min(x // 18, 2)] for _y in range(52) for x in range(52)]))


def _repository(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    repository = tmp_path / "repository"
    final = repository / "data/output/Pixellab/Final"
    final.mkdir(parents=True)
    extensions = repository / "level_factory/output/studio-extensions"
    extensions.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda *_a, **_k: repository)
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda *_a, **_k: repository)
    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: extensions)
    return repository, final


def test_db_startup_validates_only_new_files_and_mirrors_new_pending(tmp_path, monkeypatch):
    # Arrange: two Final PNGs registered by the old file-based startup, then the one-shot import.
    repository, final = _repository(tmp_path, monkeypatch)
    _png(final / "LF-000001.png", "C01", "C02")
    _png(final / "LF-000002.png", "C03", "C04")
    legacy = studio_extensions.library_refresh(repository_root=repository)
    assert len(legacy["sources"]) == 2, legacy["invalid_sources"]
    factory_db.import_from_files(factory_db.db_path(repository), repository, candidate_rows=[], progress=lambda *_: None)

    # Act 1: unchanged folder, DB startup.
    events: list[dict] = []
    view = studio_extensions.library_refresh(repository_root=repository, progress_callback=events.append)

    # Assert 1: same sources, nothing re-validated, no reconcile pass.
    assert [s["source_id"] for s in view["sources"]] == [s["source_id"] for s in legacy["sources"]]
    discovery = next(e for e in events if e["stage"] == "DISCOVERY")
    assert discovery["total"] == 0
    assert not any(e["stage"] == "FILE CHECK" for e in events)
    assert view["release_pool_reconciliation"]["state"] == "SKIPPED"

    # Act 2: one new PixelLab Final PNG.
    _png(final / "LF-000003.png", "C06", "C07")
    events.clear()
    view = studio_extensions.library_refresh(repository_root=repository, progress_callback=events.append)

    # Assert 2: only the new file was checked; it is active and PENDING in the DB-backed view.
    assert next(e for e in events if e["stage"] == "DISCOVERY")["total"] == 1
    assert [e["filename"] for e in events if e["stage"] == "FILE CHECK"] == ["LF-000003.png"]
    assert len(view["sources"]) == 3
    assert owner_release_library.list_records(repository_root=repository)["counts"]["PENDING"] == 3
    conn = factory_db.connect(factory_db.db_path(repository))
    try:
        assert conn.execute("SELECT COUNT(*) FROM images").fetchone()[0] == 3
        report = factory_db.parity_report(conn, repository)
        assert report["ok"], report["differences"]
    finally:
        conn.close()


def test_db_startup_heals_an_event_the_db_missed(tmp_path, monkeypatch):
    # Arrange: DB imported, then a status event written to the files only (as after a crash).
    repository, final = _repository(tmp_path, monkeypatch)
    _png(final / "LF-000001.png", "C01", "C02")
    studio_extensions.library_refresh(repository_root=repository)
    factory_db.import_from_files(factory_db.db_path(repository), repository, candidate_rows=[], progress=lambda *_: None)
    row = owner_release_library.list_records(repository_root=repository)["records"][0]
    monkeypatch.setattr(owner_release_library, "_mirror_to_db", lambda *_a, **_k: None)
    owner_release_library.transition(row["source_id"], "FAILED", source_sha256=row["source_sha256"], provider="PIXELLAB",
                                     original_source_path=row["original_source_path"], reason="test",
                                     repository_root=repository)
    assert owner_release_library.list_records(repository_root=repository)["counts"]["FAILED"] == 0  # DB is behind

    # Act
    view = studio_extensions.library_refresh(repository_root=repository)

    # Assert
    assert view["release_pool_status_reconciliation"]["events_healed"] == 1
    assert owner_release_library.list_records(repository_root=repository)["counts"]["FAILED"] == 1


def test_transition_mirrors_into_the_db(tmp_path, monkeypatch):
    repository, final = _repository(tmp_path, monkeypatch)
    _png(final / "LF-000001.png", "C01", "C02")
    studio_extensions.library_refresh(repository_root=repository)
    factory_db.import_from_files(factory_db.db_path(repository), repository, candidate_rows=[], progress=lambda *_: None)
    row = owner_release_library.list_records(repository_root=repository)["records"][0]

    owner_release_library.transition(row["source_id"], "REJECTED", source_sha256=row["source_sha256"], provider="PIXELLAB",
                                     original_source_path=row["original_source_path"], reason="test",
                                     repository_root=repository)
    assert owner_release_library.list_records(repository_root=repository)["counts"]["REJECTED"] == 1
    owner_release_library.purge_rejected_source(row["source_id"], repository_root=repository)

    assert owner_release_library.list_records(repository_root=repository)["records"] == []
    conn = factory_db.connect(factory_db.db_path(repository))
    try:
        assert conn.execute("SELECT COUNT(*) FROM status_events").fetchone()[0] == 0
    finally:
        conn.close()


def _entry(ready: Path, candidate_id: str, run_id: str) -> Path:
    import hashlib, json
    payload = {"schema": "scrubbots-release-pool-entry/v1", "candidate_id": candidate_id, "pipeline_run_id": run_id,
               "eligibility_source": "READY_AUTO", "real_play": {"gameCommit": "abc", "verdict": "WON_CANONICAL"}}
    payload["entry_digest"] = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    path = ready / f"{candidate_id}-{run_id}-ready.json"
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return path


def test_release_pool_listing_reads_the_db_and_new_entries_are_mirrored(tmp_path, monkeypatch):
    # Arrange: one READY entry on disk, imported into the DB.
    from scrubbots_pixel_factory import owner_art_storage
    from scrubbots_pixel_factory.supply_pipeline import release_pool
    repository, _final = _repository(tmp_path, monkeypatch)
    ready = owner_art_storage.ensure_owner_art_layout(repository)["ready"]
    _entry(ready, "candidate-owner-aaa", "pipeline-1")
    factory_db.import_from_files(factory_db.db_path(repository), repository, candidate_rows=[], progress=lambda *_: None)
    monkeypatch.setattr(release_pool, "_release_entries", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("full re-verification ran")))

    # Act / Assert: the listing is a DB query; a second entry appears once mirrored.
    assert [e["candidate_id"] for e in release_pool.release_entries()] == ["candidate-owner-aaa"]
    conn = factory_db.connect(factory_db.db_path(repository))
    try:
        factory_db.insert_release_entry(conn, _entry(ready, "candidate-owner-bbb", "pipeline-2"))
    finally:
        conn.close()
    assert [e["candidate_id"] for e in release_pool.release_entries()] == ["candidate-owner-aaa", "candidate-owner-bbb"]
    assert [e["pipeline_run_id"] for e in release_pool.release_entries("candidate-owner-bbb")] == ["pipeline-2"]


def test_source_record_written_under_another_root_never_reaches_this_db(tmp_path, monkeypatch):
    # Arrange: root A has a factory.db; an import writes its record under root B with no explicit root.
    from scrubbots_pixel_factory import owner_art_storage
    root_a, final_a = _repository(tmp_path / "a", monkeypatch)
    owner_art_storage.ensure_owner_art_layout(root_a)
    factory_db.import_from_files(factory_db.db_path(root_a), root_a, candidate_rows=[], progress=lambda *_: None)
    imported_b = tmp_path / "b" / "data" / "Level Factory" / "Imported"
    imported_b.mkdir(parents=True)
    monkeypatch.setattr(owner_art_storage, "factory_repository_root", lambda *_a, **_k: root_a)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda _root=None: imported_b)
    png = tmp_path / "x.png"
    _png(png, "C01", "C02")

    # Act
    assert owner_upload.import_owner_upload(png)["state"] == "IMPORTED"

    # Assert: A's DB still has no source rows.
    conn = factory_db.connect(factory_db.db_path(root_a))
    try:
        assert conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0] == 0
    finally:
        conn.close()


def test_studio_release_list_is_slim_and_matches_the_python_projection(tmp_path, monkeypatch):
    from scrubbots_pixel_factory import owner_art_storage
    from scrubbots_pixel_factory.supply_pipeline import release_pool
    repository, _final = _repository(tmp_path, monkeypatch)
    ready = owner_art_storage.ensure_owner_art_layout(repository)["ready"]
    _entry(ready, "candidate-owner-aaa", "pipeline-1")
    factory_db.import_from_files(factory_db.db_path(repository), repository, candidate_rows=[], progress=lambda *_: None)

    slim = release_pool.slim_release_entries()

    assert slim == [release_pool.slim_release_entry(e) for e in release_pool.release_entries()]
    assert slim[0]["slim"] is True and "candidate_classification" not in slim[0]
