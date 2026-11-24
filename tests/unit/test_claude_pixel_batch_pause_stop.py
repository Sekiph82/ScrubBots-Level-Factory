"""Owner request 2026-11-24: PIXEL ART CSV batches get Pause / Stop after current.

The running paid row always finishes and is saved; the request is applied before the
next row is sent. Pause keeps the remaining rows for Resume (Run Batch), Stop drops them.
"""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[2] / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")


def _function(name: str) -> str:
    start = SOURCE.index(f"func {name}")
    end = SOURCE.find("\nfunc ", start + 5)
    return SOURCE[start:] if end < 0 else SOURCE[start:end]


def test_pause_and_stop_buttons_replace_csv_and_run_batch_while_a_batch_runs() -> None:
    assert '_place_control("PausePixelBatch", Rect2(27, 261, 160, 45), _request_pixel_batch_control.bind("PAUSE"))' in SOURCE
    assert '_place_control("StopPixelBatch", Rect2(198, 261, 162, 45), _request_pixel_batch_control.bind("STOP"))' in SOURCE
    visibility = _function("_update_master_control_visibility")
    assert 'batch_path.visible = _generation_mode == "BATCH" and not batch_running' in visibility
    assert 'control.visible = _generation_mode == "BATCH" and batch_running' in visibility


def test_request_is_applied_only_after_the_running_row_finished() -> None:
    request = _function("_request_pixel_batch_control")
    assert "_start_pixel_art_worker" not in request and "_start_next_pixellab_batch_row" not in request
    result = SOURCE[SOURCE.index("_pixel_batch_succeeded += 1\n\t\t_pixel_batch_index += 1"):]
    result = result[:result.index("return")]
    assert result.index("_apply_pixel_batch_control()") > result.index("_pixel_batch_index += 1")
    assert "_start_next_pixellab_batch_row()" not in result[:result.index("_apply_pixel_batch_control()")]


def test_pause_keeps_rows_for_resume_and_stop_drops_them() -> None:
    apply = _function("_apply_pixel_batch_control")
    pause_branch, stop_branch = apply.split("\telse:", 1)
    assert "_pixel_batch_paused = true" in pause_branch and "_set_batch_action_label(true)" in pause_branch
    assert "_pixel_batch_rows.clear()" not in pause_branch
    assert "_pixel_batch_rows.clear()" in stop_branch
    run_batch = _function("_run_batch")
    assert run_batch.index("_pixel_batch_paused and not _pixel_batch_active") < run_batch.index("_generate_batch_csv")
    resume = run_batch[:run_batch.index("_generate_batch_csv")]
    assert "_start_next_pixellab_batch_row()" in resume and "_pixel_batch_active = true" in resume
