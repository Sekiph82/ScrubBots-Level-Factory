from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UI_PATH = ROOT / "level_factory/scripts/factory_studio_exact_ui.gd"
UI = UI_PATH.read_text(encoding="utf-8")
sys.path.insert(0, str(ROOT / "level_factory/scripts"))


def test_every_declared_master_control_has_one_unique_explicit_action() -> None:
    declared = re.findall(r'_place_control\("([A-Za-z0-9]+)",\s*Rect2\([^\n]+?,\s*([A-Za-z_][A-Za-z0-9_.]*(?:\.bind\([^\n]*?\))?)\)', UI)
    names = [name for name, _ in declared]
    assert len(names) >= 65
    assert len(names) == len(set(names))
    assert all(action not in {"Callable()", "TODO", "pass"} for _, action in declared)
    assert "button.pressed.connect(action)" in UI
    assert "button.visible = button.name in shared" in UI
    assert '"PIXEL ART"' in UI and '"LEVEL FACTORY"' in UI and '"RELEASE POOL"' in UI


def test_generation_values_and_csv_use_the_same_real_generation_entrypoint() -> None:
    assert '"semantic-generate"' in UI
    assert '"provider_model": "PRO_FLASH"' in UI
    assert '"width": request.get("width", 32)' in UI
    assert '"height": request.get("height", 32)' in UI
    assert "_confirm_pro_flash_generation()" in UI
    assert "_start_pixel_art_worker" in UI
    assert '"state": "PAID_CONFIRMATION_REQUIRED"' in UI
    assert 'selected_provider == "ALPIX (Claude)"' in UI
    assert 'selected_provider == "MAGNIFIC"' in UI
    assert 'var result := _generate_request({' in UI
    assert 'var result := _generate_request({"prompt": str(row_values.get("prompt", ""))' in UI
    assert 'PackedStringArray(["prompt", "style", "width", "height", "provider", "seed", "background_intent"])' in UI
    assert '"size"' in UI and "_csv_dimensions" in UI
    assert 'OS.get_environment("PIXELLAB_SECRET")' not in UI
    assert '"provider-options"' in UI


def test_pipeline_review_and_replay_bind_to_canonical_studio_operations() -> None:
    assert '"column_count": _column_count' in UI
    assert '"level_number": _level_number' in UI
    assert 'prepare_studio_extension_call", "pipeline", pipeline_request' in UI
    assert '_extension("owner-review", {"candidate_id": _last_candidate_id, "disposition": disposition})' in UI
    assert 'str(_last_pipeline.get("disposition", "")) != "READY"' in UI
    assert '_last_pipeline.get("primary", {})' in UI
    assert 'result.get("solution_replay", {})' in UI
    assert 'func _solve_again()' in UI and '_run_level_pipeline()' in UI


def test_release_projection_and_publish_stay_within_canonical_boundaries() -> None:
    assert '_extension("release-pool", {})' in UI
    assert 'func _apply_release_projection()' in UI
    assert 'func _select_all_release()' in UI
    assert 'func _clear_release_selection()' in UI
    assert 'func _remove_release_selection(index: int)' in UI
    assert '"action": "publish-staging"' in UI
    assert '"production-promotion"' not in UI
    assert '"reviewed_identity": reviewed' in UI
    assert '"content_version"' in UI
    assert '"content_version": 2' not in UI
    assert "CloudflareR2Provider" not in UI and "write_object_bytes" not in UI
    assert '"action": "publish-production"' in UI
    assert '"manifest_sha256": _pending_production_confirmation.get' in UI
    assert '_release_confirmation.confirmed.connect(_publish_production_confirmed)' in UI


def test_canvas_presentation_is_separate_from_source_art_and_selection() -> None:
    for control in ("ZoomOut", "ZoomSlider", "ZoomIn", "ZoomOneToOne", "ZoomFit", "ToggleGrid"):
        assert f'"{control}"' in UI
    assert "func _set_zoom" in UI
    assert "func _toggle_grid" in UI
    assert "_preview_content.scale" in UI
    assert "line.visible = _grid_enabled" in UI


def test_provider_picker_exposes_owner_provider_choices_with_truthful_availability(monkeypatch) -> None:
    import factory_core_launcher
    from scrubbots_pixel_factory import alpix_batch

    monkeypatch.delenv("PIXELLAB_SECRET", raising=False)
    monkeypatch.delenv("PIXELLAB_API_TOKEN", raising=False)
    monkeypatch.setattr(alpix_batch, "discover_alpix", lambda: {"available": False, "reason": "not installed"})
    options = factory_core_launcher._provider_options()
    assert options["state"] == "READY"
    assert [item["id"] for item in options["providers"]] == ["ALPIX (Claude)", "PIXELLAB"]
    assert options["providers"][0]["available"] is False
    assert options["providers"][1]["execution_mode"] == "PRO_FLASH"
    monkeypatch.setenv("PIXELLAB_API_TOKEN", "redacted-test-secret")
    configured = factory_core_launcher._provider_options()
    assert configured["providers"][1]["available"] is True
    assert "redacted-test-secret" not in str(configured)


def test_production_screens_are_native_controls_and_master_textures_are_not_live_underlays() -> None:
    assert "_canvas.texture = null" in UI
    assert "_canvas.visible = false" in UI
    assert "func _build_live_chrome()" in UI
    assert "Panel.new()" in UI and "Label.new()" in UI
    assert "button.flat = false" in UI
    assert "func _refresh_live_data()" in UI
    assert "candidate_manifest_sha256" in UI or "manifest_sha256" in UI


def test_external_png_single_multi_and_csv_use_the_same_canonical_pipeline_in_source_order() -> None:
    single = UI.split("func _on_file_selected", 1)[1].split("func _on_files_selected", 1)[0]
    multiple = UI.split("func _on_files_selected", 1)[1].split("func _set_generation_mode", 1)[0]
    imported = UI.split("func _import_pngs", 1)[1].split("func _show_import_results", 1)[0]
    csv = UI.split("func _process_level_csv", 1)[1].split("func _on_file_selected", 1)[0]
    assert "_import_pngs([path])" in single
    assert "_import_pngs(Array(paths))" in multiple
    assert '"batch-import", {"paths": paths}' in imported
    assert '"solver_calls": 0' in imported
    assert '"pipeline"' not in imported
    assert '"batch-import", {"paths": [artwork_path]}' in csv
    assert 'while not file.eof_reached():' in csv and '"pipeline", {"source_id": source_id' in csv
    assert '"column_count": _column_count' in UI
    assert '"column_count": int(row[col_index])' in csv
    assert '"background_intent": _background_intent' in multiple
    assert '"background_intent": row[bg_index]' in csv
