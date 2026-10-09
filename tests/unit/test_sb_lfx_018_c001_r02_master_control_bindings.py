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
    assert '"style": family' in UI
    assert 'var result := _generate_request({' in UI
    assert 'var result := _generate_request({"prompt": str(row_values.get("prompt", ""))' in UI
    assert 'PackedStringArray(["prompt", "style", "width", "height", "provider", "seed", "background_intent"])' in UI
    assert '"size"' in UI and "_csv_dimensions" in UI
    assert '"PIXELLAB_SECRET: %s"' in UI
    assert 'OS.get_environment("PIXELLAB_SECRET")' in UI
    assert 'credentials.text = "PIXELLAB_SECRET: %s" % ("Configured"' in UI


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
    assert '"production-promotion"' in UI
    assert '"manifest_sha256"' in UI
    assert '"content_version"' in UI
    assert '"content_version": 2' not in UI
    assert "CloudflareR2Provider" not in UI and "write_object_bytes" not in UI
    assert '_release_confirmation.confirmed.connect(_confirm_production_promotion' in UI


def test_canvas_presentation_is_separate_from_source_art_and_selection() -> None:
    for control in ("ZoomOut", "ZoomSlider", "ZoomIn", "ZoomOneToOne", "ZoomFit", "ToggleGrid"):
        assert f'"{control}"' in UI
    assert "func _set_zoom" in UI
    assert "func _toggle_grid" in UI
    assert "_preview_rect.scale" in UI
    assert "line.visible = _grid_enabled" in UI


def test_provider_picker_exposes_only_registry_adapter_with_configured_execution(monkeypatch) -> None:
    import importlib.util
    import factory_core_launcher

    monkeypatch.delenv("PIXELLAB_SECRET", raising=False)
    options = factory_core_launcher._provider_options()
    assert options["state"] == "READY"
    assert options["providers"] == [{"id": "LOCAL_MASK", "available": True, "prompt_capable": False}]
    monkeypatch.setenv("PIXELLAB_SECRET", "redacted-test-secret")
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object() if name == "pixellab" else None)
    configured = factory_core_launcher._provider_options()
    assert [item["id"] for item in configured["providers"]] == ["LOCAL_MASK", "PIXELLAB/PIXFLUX", "PIXELLAB/BITFORGE"]
    assert "redacted-test-secret" not in str(configured)
