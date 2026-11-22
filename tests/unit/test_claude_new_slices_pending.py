"""New PixelLab slices enter Pending when their atlas is sliced, not at the next startup (owner 2026-11-22)."""
import importlib.util
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("factory_core_launcher_t", ROOT / "level_factory/scripts/factory_core_launcher.py")
launcher = importlib.util.module_from_spec(spec)
sys.modules["factory_core_launcher_t"] = launcher
spec.loader.exec_module(launcher)


def test_each_new_slice_is_registered_pending_once(monkeypatch, tmp_path):
    from scrubbots_pixel_factory import owner_release_library as lib
    known = {"owner-upload-" + "b" * 64}
    calls = []
    monkeypatch.setattr(lib, "list_records", lambda status=None, source_id=None, **_k: {"records": [1] if source_id in known else []})
    monkeypatch.setattr(lib, "transition", lambda sid, status, **kw: calls.append((sid, status, kw["provider"], Path(kw["original_source_path"]).name)))
    monkeypatch.setattr(launcher, "_pixellab_final_slice_path", lambda catalog, frame: tmp_path / f"LF-{frame['index']:06d}.png")
    items = [{"index": 1, "source_id": "owner-upload-" + "a" * 64},
             {"index": 2, "source_id": "owner-upload-" + "b" * 64},   # already has a status
             {"index": 3, "source_id": None}]                          # not imported
    launcher._register_new_final_sources_pending({}, {"frames": [{"index": i} for i in (1, 2, 3)]}, items, "job-1")
    assert calls == [("owner-upload-" + "a" * 64, "PENDING", "PIXELLAB", "LF-000001.png")]
    assert items[0]["release_pool_status"] == "PENDING" and "release_pool_status" not in items[1]


def test_atlas_finish_registers_slices_and_ui_rereads_statuses():
    assert "_register_new_final_sources_pending(" in inspect.getsource(launcher._finish_pixellab_atlas_job)
    ui = (ROOT / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    assert "if atlas_generated:\n\t\t_refresh_owner_release_archive()" in ui
