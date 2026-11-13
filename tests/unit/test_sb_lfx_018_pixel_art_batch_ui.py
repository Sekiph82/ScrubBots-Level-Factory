from pathlib import Path
import hashlib
import sys

import pytest

# Do not depend on another test having put the launcher folder on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts"))
import factory_core_launcher  # noqa: E402


def _function(source: str, name: str) -> str:
    marker = f"func {name}"
    start = source.index(marker)
    end = source.find("\nfunc ", start + len(marker))
    return source[start:] if end < 0 else source[start:end]


def test_csv_selection_is_retained_until_run_batch_and_batch_is_confirmed() -> None:
    root = Path(__file__).resolve().parents[2]
    source = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    selection = _function(source, "_on_file_selected")
    run_batch = _function(source, "_run_batch")
    prepare = _function(source, "_prepare_pixellab_csv_batch")
    worker = _function(source, "_start_next_pixellab_batch_row")

    assert '_file_selection_action == "PIXEL_ART_BATCH"' in selection
    assert "_batch_csv_path = path" in selection
    assert "_generate_batch_csv(path)" not in selection
    assert "_batch_csv_path.is_empty()" in run_batch
    assert "_generate_batch_csv(_batch_csv_path)" in run_batch
    assert "source_rows.size() >= 2000" in prepare
    assert '"width": 56' in worker and '"height": 56' in worker
    assert '"max_colors": 12' in worker
    assert '"pixellab-batch-inspect"' in prepare
    assert '"csv_path": path' in prepare and '"source_sha256": _pixel_batch_source_sha256' in prepare
    inspection = _function(source, "_confirm_pixellab_batch_after_inspection")
    assert "dialog.confirmed.connect" in inspection
    assert '"PixelLabBatchRequestCount"' in inspection
    assert "count * 10" in inspection
    assert "_pixel_batch_rows.resize(confirmed_count)" in inspection
    assert "ALREADY_ATTEMPTED" in inspection
    assert "200 - _pixel_batch_monthly_used" in inspection
    assert "_start_next_pixellab_batch_row()" in inspection
    assert "PixelLab Pro 4×4 CSV batch is disabled" not in source


def test_pixel_art_activity_log_is_bounded_and_provider_failures_stop_the_batch() -> None:
    root = Path(__file__).resolve().parents[2]
    source = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    recorder = _function(source, "_record_pixel_art_activity")
    poll = _function(source, "_poll_pixel_art_worker")

    assert '"PixelArtActivityTable"' in source
    table = _function(source, "_build_pixel_art_activity_table")
    refresh = _function(source, "_refresh_pixel_art_activity_table")
    assert '"PixelArtActivityTable"' in table
    assert '"TIME / STATUS"' in refresh and '"EVENT / DETAILS"' in refresh
    assert '"font_size", 16' in refresh
    # Column minimums follow the table width since 2026-11-13 (small-window overflow fix).
    assert "var time_width := clampf(grid_width * 0.34, 40.0, 155.0)" in refresh
    assert "var detail_width := maxf(50.0, grid_width - time_width - 8.0)" in refresh
    assert "detail.size_flags_horizontal = Control.SIZE_EXPAND_FILL" in refresh
    layout = _function(source, "_apply_responsive_layout")
    assert '_screen == "PIXEL ART" and _pixel_art_activity_table != null' in layout
    assert "_refresh_pixel_art_activity_table()" in layout
    geometry = _function(source, "responsive_geometry")
    assert "viewport_size.x * 0.23" in geometry
    assert "viewport_size.x * 0.204" in geometry
    assert "285.0, 354.0" not in geometry and "300.0, 420.0" not in geometry
    batch_row = _function(source, "_start_next_pixellab_batch_row")
    assert '"PREPARING"' in batch_row
    assert '"SUBMITTED"' not in batch_row
    assert "while _pixel_art_activity_events.size() > 200" in recorder
    assert "secret_pattern.sub" in recorder
    assert '"STOPPED_AFTER_FAILURE"' in poll
    assert "No retry or additional paid request was sent." in poll


def test_all_activity_tables_show_newest_first_and_leave_raw_event_order_intact() -> None:
    root = Path(__file__).resolve().parents[2]
    source = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    pixel_refresh = _function(source, "_refresh_pixel_art_activity_table")
    pipeline_append = _function(source, "_append_activity_row")
    batch_append = _function(source, "_append_batch_item_activity_row")
    release_refresh = _function(source, "_refresh_release_pool_activity")
    release_scroll = _function(source, "_scroll_release_pool_activity_to_latest")

    assert "range(_pixel_art_activity_events.size() - 1, -1, -1)" in pixel_refresh
    assert "_activity_rows.move_child(row, 0)" in pipeline_append
    assert "_activity_rows.move_child(row, 0)" in batch_append
    assert "_activity_rows.move_child(_activity_solver_row, 0)" in pipeline_append
    assert "range(_release_activity_events.size() - 1, -1, -1)" in release_refresh
    assert "_release_activity_scroll.scroll_vertical = 0" in release_scroll
    assert '"seq"' in source and '"previous_sha256"' in source


def test_owner_folder_preview_and_import_stream_per_file_progress_to_pipeline_activity() -> None:
    root = Path(__file__).resolve().parents[2]
    ui = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    launcher = (root / "level_factory/scripts/factory_core_launcher.py").read_text(encoding="utf-8")
    scanner = (root / "src/scrubbots_pixel_factory/owner_folder_batch.py").read_text(encoding="utf-8")
    importer = (root / "src/scrubbots_pixel_factory/studio_extensions.py").read_text(encoding="utf-8")

    assert "_begin_owner_folder_activity(folder" in _function(ui, "_on_owner_folder_selected")
    assert "request.merge(_owner_folder_activity_request(), true)" in _function(ui, "_on_owner_folder_selected")
    assert '"activity_run_id": _activity_run_id' in _function(ui, "_owner_folder_activity_request")
    assert '"activity_log_path": _activity_file_path' in _function(ui, "_owner_folder_activity_request")
    assert "request.merge(_owner_folder_activity_request(), true)" in _function(ui, "_on_owner_folder_selected")
    assert "request.merge(_owner_folder_activity_request(), true)" in _function(ui, "_confirm_owner_folder_import")
    assert "request.merge(_owner_folder_activity_request(), true)" in _function(ui, "_poll_studio_read_extension")
    assert "owner-folder-preview-" in _function(ui, "_begin_owner_folder_activity")
    assert "activity_source_id" in launcher and '"stage": "FILE CHECK"' in scanner
    assert '"stage": "FILE IMPORT"' in importer
    assert "writer.emit(\"PIPELINE\", \"COMPLETE\"" in launcher
    # Activity logs moved to the canonical data root (2026-11-08).
    assert '_factory_data_path("Level Factory/Activity")' in ui


def test_folder_activity_writer_is_bound_to_the_active_studio_project_output(monkeypatch) -> None:
    import scrubbots_pixel_factory.pipeline_activity as pipeline_activity

    captured: dict[str, object] = {}

    class FakeWriter:
        terminal_emitted = False

        def __init__(self, repository_root, run_id, source_id, source_sha256, *, output_directory):
            captured["output_directory"] = output_directory
            captured["identity"] = (run_id, source_id, source_sha256)

        def emit(self, stage, state, message):
            captured.setdefault("events", []).append((stage, state, message))

    monkeypatch.setattr(pipeline_activity, "PipelineActivityWriter", FakeWriter)
    folder = r"C:\approved\PixelLab\Final"
    folder_identity = Path(folder).resolve(strict=False).as_posix().lower()
    source_sha = hashlib.sha256(folder_identity.encode("utf-8")).hexdigest()
    run_id = "pipeline-ui-20261108T021000Z-0123456789ab"
    from scrubbots_pixel_factory.owner_art_storage import owner_art_paths

    # One shared Activity directory under the canonical data root (2026-11-08).
    project_output = owner_art_paths(factory_core_launcher._repository_root())["activity"]
    request = {
        "folder": folder,
        "activity_run_id": run_id,
        "activity_source_id": "owner-folder-preview-" + source_sha,
        "activity_source_sha256": source_sha,
        "activity_log_path": str(project_output / (run_id + ".jsonl")),
    }

    writer, emit, errors = factory_core_launcher._folder_activity_context(request)
    assert isinstance(writer, FakeWriter)
    assert captured["output_directory"] == project_output
    assert captured["identity"] == (run_id, request["activity_source_id"], source_sha)
    assert not errors
    emit({"stage": "DISCOVERY", "state": "RUNNING", "message": "Found 304 PNG files"})
    assert captured["events"][-1] == ("DISCOVERY", "RUNNING", "Found 304 PNG files")

    request["activity_log_path"] = str(project_output.parent / "outside.jsonl")
    with pytest.raises(ValueError, match="does not match this Studio project's output directory"):
        factory_core_launcher._folder_activity_context(request)


def test_pixel_art_left_controls_are_compact_and_prompt_refresh_is_removed() -> None:
    root = Path(__file__).resolve().parents[2]
    source = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    controls = _function(source, "_build_master_controls")
    table = _function(source, "_build_pixel_art_activity_table")

    assert '"RandomSeed"' not in source
    assert '"GenerationSize", Rect2(27, 312, 160, 42)' in controls
    assert '"GenerationProvider", Rect2(27, 366, 334, 42)' in controls
    assert '"GeneratePixelArt", Rect2(27, 424, 334, 49)' in controls
    assert '"BatchCsvPath", Rect2(27, 424, 334, 42)' in controls
    assert '"RunBatch", Rect2(27, 476, 334, 50)' in controls
    assert '"PixelArtActivityTable"' in table
    assert 'Vector2(27, 538)' in table


def test_pixellab_resume_inspection_is_read_only_and_reports_new_rows(tmp_path: Path, monkeypatch) -> None:
    # Isolated canonical input folder: the owner's real prompt CSV changes over time.
    repository = tmp_path / "repository"
    csv_path = repository / "data" / "input" / "prompts.csv"
    csv_path.parent.mkdir(parents=True)
    csv_path.write_text("id,prompt\n1,forest spirit\n2,desert golem\n3,sea serpent\n", encoding="utf-8")
    monkeypatch.setattr(factory_core_launcher, "_repository_root", lambda: repository)
    ledger_root = tmp_path / "unused-pixellab-ledger-test-root"

    class FakeExtensions:
        @staticmethod
        def extensions_root() -> Path:
            return ledger_root

        @staticmethod
        def _resolved_seed(seed: str | int) -> int:
            if isinstance(seed, int):
                return seed
            return int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:4], "big")

    request = {
        "csv_path": str(csv_path),
        "source_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "width": 56,
        "height": 56,
        "max_colors": 12,
    }

    result = factory_core_launcher._inspect_pixellab_batch(request, FakeExtensions)
    assert result["state"] == "READY", result
    assert result["monthly_request_limit"] == 200
    assert result["source_prompt_count"] == 3
    assert result["rows"][0] == {"row_index": 1, "disposition": "NEW"}
    assert result["rows"][-1] == {"row_index": 3, "disposition": "NEW"}
    assert not ledger_root.exists()


def test_solver_activity_uses_running_studio_project_and_emits_active_png_row(monkeypatch) -> None:
    from scrubbots_pixel_factory import studio_extensions
    from scrubbots_pixel_factory.owner_art_storage import owner_art_paths

    root = Path(__file__).resolve().parents[2]
    # Since 2026-11-08 source and installed Studio share one canonical Activity
    # directory under data/Level Factory; the project-root variable no longer moves it.
    expected = owner_art_paths(root)["activity"]
    ui = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    record_progress = _function(ui, "_record_verified_batch_item_progress")
    render_row = _function(ui, "_append_batch_item_activity_row")

    monkeypatch.delenv("SCRUBBOTS_STUDIO_PROJECT_ROOT", raising=False)
    assert studio_extensions._studio_activity_output_directory() == expected
    monkeypatch.setenv("SCRUBBOTS_STUDIO_PROJECT_ROOT", str(root / "Release" / "ScrubBots Factory Studio" / "level_factory"))
    assert studio_extensions._studio_activity_output_directory() == expected
    shutdown = _function(ui, "_finish_worker_cancel_marker")
    assert 'OS.set_environment("SCRUBBOTS_STUDIO_PROJECT_ROOT", _studio_project_root_previous_environment)' in shutdown
    assert 'state not in ["RUNNING", "READY", "FAILED", "REJECTED", "SKIPPED"]' in record_progress
    assert 'var run_reference := activity_id if state == "RUNNING" else run_id' in render_row
    assert "activity_run_id=%s" in render_row


def test_solver_activity_rejects_external_studio_project_root(monkeypatch) -> None:
    # An external project root can no longer redirect Activity: the directory
    # is always the canonical data/Level Factory/Activity of this checkout.
    from scrubbots_pixel_factory import studio_extensions
    from scrubbots_pixel_factory.owner_art_storage import owner_art_paths

    monkeypatch.setenv("SCRUBBOTS_STUDIO_PROJECT_ROOT", r"C:\outside\factory")
    directory = studio_extensions._studio_activity_output_directory()
    assert directory == owner_art_paths(Path(__file__).resolve().parents[2])["activity"]
    assert "outside" not in str(directory).lower()


def test_pixellab_resume_inspection_fails_closed_if_csv_changes_after_selection(tmp_path: Path, monkeypatch) -> None:
    repository = tmp_path / "repository"
    csv_path = repository / "data" / "input" / "prompts.csv"
    csv_path.parent.mkdir(parents=True)
    csv_path.write_text("id,prompt\n1,forest spirit\n", encoding="utf-8")
    monkeypatch.setattr(factory_core_launcher, "_repository_root", lambda: repository)
    result = factory_core_launcher._inspect_pixellab_batch({
        "csv_path": str(csv_path),
        "source_sha256": "0" * 64,
        "width": 56,
        "height": 56,
        "max_colors": 12,
    }, object())

    assert result == {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_CHANGED_DURING_PREFLIGHT"}
