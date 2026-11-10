"""Owner 2026-11-10: "Run Pending Batch (499)" did nothing. create_pending_png_batch
rejected all 499 because 31 Pending records' display filename (staging sprite-NN.png
vs Final LF-xxxxxx.png) differed from the Imported record, although SHA identity matched."""
import pytest

from scrubbots_pixel_factory import owner_release_library, studio_extensions

SHA = "a" * 64
SID = "owner-upload-" + SHA


def _setup(monkeypatch, imported_name, pending_path, imported_sha=SHA):
    monkeypatch.setattr(owner_release_library, "list_records", lambda *_a, **_k: {"records": [
        {"source_id": SID, "source_sha256": SHA, "provider": "PIXELLAB", "original_source_path": pending_path}]})
    monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda _sid: {
        "source_id": SID, "source_sha256": imported_sha, "original_filename": imported_name})
    monkeypatch.setattr(studio_extensions, "create_loaded_png_batch", lambda ids: {"batch_id": "b", "items": list(ids)})


def test_display_name_difference_does_not_block_pending_batch(monkeypatch) -> None:
    _setup(monkeypatch, "sprite-01.png", r"C:\x\data\output\Pixellab\Final\LF-000401.png")
    result = studio_extensions.create_pending_png_batch([SID])
    assert result["pending_verified_count"] == 1


def test_sha_difference_still_blocks(monkeypatch) -> None:
    _setup(monkeypatch, "LF-000401.png", r"C:\x\Final\LF-000401.png", imported_sha="b" * 64)
    with pytest.raises(studio_extensions.StudioExtensionError, match="identity changed"):
        studio_extensions.create_pending_png_batch([SID])
