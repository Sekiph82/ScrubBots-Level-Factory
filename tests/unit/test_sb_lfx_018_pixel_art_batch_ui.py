from pathlib import Path
import hashlib

import factory_core_launcher


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
    assert "var time_width := clampf(grid_width * 0.34, 105.0, 155.0)" in refresh
    assert "var detail_width := maxf(205.0, grid_width - time_width - 8.0)" in refresh
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


def test_pixellab_resume_inspection_is_read_only_and_reports_new_rows() -> None:
    project_root = Path(__file__).resolve().parents[2]
    csv_path = project_root / "data" / "input" / "scrubbots_2000_prompts.csv"
    ledger_root = project_root / "tests" / "fixtures" / "unused-pixellab-ledger-test-root"

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

    assert not ledger_root.exists()
    result = factory_core_launcher._inspect_pixellab_batch(request, FakeExtensions)
    assert result["state"] == "READY"
    assert result["monthly_request_limit"] == 200
    assert result["source_prompt_count"] == 1997
    assert len(result["rows"]) == 1997
    assert result["rows"][0] == {"row_index": 1, "disposition": "NEW"}
    assert result["rows"][-1] == {"row_index": 1997, "disposition": "NEW"}
    assert not ledger_root.exists()


def test_pixellab_resume_inspection_fails_closed_if_csv_changes_after_selection() -> None:
    csv_path = Path(__file__).resolve().parents[2] / "data" / "input" / "scrubbots_2000_prompts.csv"
    result = factory_core_launcher._inspect_pixellab_batch({
        "csv_path": str(csv_path),
        "source_sha256": "0" * 64,
        "width": 56,
        "height": 56,
        "max_colors": 12,
    }, object())

    assert result == {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_CHANGED_DURING_PREFLIGHT"}
