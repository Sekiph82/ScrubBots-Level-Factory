from __future__ import annotations

import pytest

from scrubbots_pixel_factory.studio_extensions import StudioExtensionError, extensions_root, restore_session, save_session


@pytest.fixture(autouse=True)
def _isolated_extensions_root(tmp_path, monkeypatch):
    # Never write sessions/presets into the owner's real Studio Extensions.
    from scrubbots_pixel_factory import studio_extensions

    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: tmp_path / "Studio Extensions")


def test_session_allowlist_rejects_unknown_nested_secret_and_preserves_typed_state() -> None:
    with pytest.raises(StudioExtensionError):
        save_session("lfx015-test", {"surface": "Batch Import", "nested": {"safe": "secret"}})
    saved = save_session("lfx015-test", {"surface": "Batch Import", "autosave_generation": 2})
    try:
        assert "nested" not in str(saved)
        restored = restore_session("lfx015-test")
        assert restored["recovery"] == "NEW"
    finally:
        path = extensions_root() / "sessions" / "lfx015-test.json"
        if path.exists(): path.unlink()
