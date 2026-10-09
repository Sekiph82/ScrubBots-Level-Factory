from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UI_PATH = ROOT / "level_factory/scripts/factory_studio_exact_ui.gd"
UI = UI_PATH.read_text(encoding="utf-8")
sys.path.insert(0, str(ROOT / "level_factory/scripts"))


def test_every_declared_master_hotspot_has_one_unique_explicit_action() -> None:
    declared = re.findall(r'_hotspot\("([A-Za-z0-9]+)",\s*Rect2\([^\n]+?,\s*([A-Za-z_][A-Za-z0-9_.]*(?:\.bind\([^\n]*?\))?)\)', UI)
    names = [name for name, _ in declared]
    assert len(names) >= 65
    assert len(names) == len(set(names))
    assert all(action not in {"Callable()", "TODO", "pass"} for _, action in declared)
    assert "button.pressed.connect(action)" in UI
    assert "button.visible = button.name in shared" in UI
    assert '"PIXEL ART"' in UI and '"LEVEL FACTORY"' in UI and '"RELEASE POOL"' in UI


def test_generation_values_and_csv_use_the_same_real_generation_entrypoint() -> None:
    assert '"semantic-generate"' in UI
    assert '"prompt": request.get("prompt", "")' in UI
    assert '"style": request.get("style", "")' in UI
    assert '"provider_model": model' in UI
    assert '"width": request.get("width", 32)' in UI
    assert '"height": request.get("height", 32)' in UI
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
    assert '_extension("pipeline", pipeline_request)' in UI
    assert '_extension("owner-review", {"candidate_id": _last_candidate_id, "disposition": disposition})' in UI
    assert 'str(_last_pipeline.get("disposition", "")) != "READY"' in UI
    assert '_last_pipeline.get("primary", {})' in UI
    assert 'primary.get("replay", primary.get("replay_verification", {}))' in UI
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
    assert 'PRODUCTION is unavailable: exact verified STAGING manifest and trusted owner-approval promotion handoff are not connected.' in UI


def test_canvas_presentation_is_separate_from_source_art_and_selection() -> None:
    for control in ("ZoomOut", "ZoomSlider", "ZoomIn", "ZoomOneToOne", "ZoomFit", "ToggleGrid"):
        assert f'"{control}"' in UI
    assert "func _set_zoom" in UI
    assert "func _toggle_grid" in UI
    assert "_preview_rect.scale" in UI
    assert "line.visible = _grid_enabled" in UI


def test_provider_picker_exposes_owner_provider_choices_with_truthful_availability(monkeypatch) -> None:
    import importlib.util
    import factory_core_launcher
    from scrubbots_pixel_factory import alpix_batch

    monkeypatch.delenv("PIXELLAB_SECRET", raising=False)
    monkeypatch.setattr(alpix_batch, "discover_alpix", lambda: {"available": False, "reason": "not installed"})
    options = factory_core_launcher._provider_options()
    assert options["state"] == "READY"
    assert [item["id"] for item in options["providers"]] == ["ALPIX (Claude)", "MAGNIFIC", "PIXELLAB"]
    assert options["providers"][0]["available"] is False
    assert options["providers"][1]["execution_mode"] == "PREPARE_AND_IMPORT"
    monkeypatch.setenv("PIXELLAB_SECRET", "redacted-test-secret")
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object() if name == "pixellab" else None)
    configured = factory_core_launcher._provider_options()
    assert configured["providers"][2]["available"] is True
    assert "redacted-test-secret" not in str(configured)
