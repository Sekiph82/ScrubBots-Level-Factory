from __future__ import annotations

from scrubbots_pixel_factory.studio_extensions import extensions_root, restore_session, save_session


def test_session_autosave_scrubs_secrets_and_restores_resumed_reference_state() -> None:
    saved = save_session("lfx015-test", {"surface": "Batch Import", "active_batch_id": "batch-1", "autosave_generation": 2, "api_key": "must-not-persist", "token": "must-not-persist"})
    try:
        assert "api_key" not in str(saved) and "token" not in str(saved)
        restored = restore_session("lfx015-test")
        assert restored["recovery"] == "RESUMED"
        assert restored["state"]["active_batch_id"] == "batch-1"
        assert "api_key" not in restored["state"] and "token" not in restored["state"]
    finally:
        path = extensions_root() / "sessions" / "lfx015-test.json"
        if path.exists(): path.unlink()
