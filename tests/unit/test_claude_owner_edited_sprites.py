"""Owner 2026-11-15: edited versions of EDGE_CLIPPED PixelLab frames are cleaned and
added to Final; intake-rejected slices never become Pending."""
from __future__ import annotations

import json
import sys
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from scrubbots_pixel_factory import owner_art_storage
from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE
from scrubbots_pixel_factory.pixellab_pro_atlas import clean_owner_edited_frame

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts"))
import factory_core_launcher as launcher  # noqa: E402

BLACK = CANONICAL_PALETTE.colors[0].rgb


def _png(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _edited_sprite() -> Image.Image:
    """59x59, artwork touching the left and right edges, with editor leftovers."""
    image = Image.new("RGBA", (59, 59), (0, 0, 0, 0))
    for x in range(59):
        for y in range(20, 40):
            image.putpixel((x, y), (*BLACK, 255))
    image.putpixel((10, 10), (*BLACK, 254))            # nearly opaque -> opaque
    image.putpixel((11, 10), (*BLACK, 20))             # faint -> transparent
    image.putpixel((30, 30), (BLACK[0] + 2, BLACK[1] + 2, BLACK[2] + 2, 255))  # near-palette tone
    return image


def test_clean_owner_edit_meets_intake_rules() -> None:
    cleaned = clean_owner_edited_frame(_edited_sprite())
    palette = {color.rgb for color in CANONICAL_PALETTE.colors}
    pixels = [cleaned.getpixel((x, y)) for y in range(cleaned.height) for x in range(cleaned.width)]
    assert cleaned.size == (59, 59)
    assert all(alpha in (0, 255) for *_, alpha in pixels)
    assert all(rgb in palette for *rgb, alpha in [tuple(p) for p in pixels] if alpha for rgb in [tuple(rgb)])
    width, height = cleaned.size
    assert not any(cleaned.getpixel((x, y))[3] for x in range(width) for y in (0, height - 1))
    assert not any(cleaned.getpixel((x, y))[3] for y in range(height) for x in (0, width - 1))
    assert sum(alpha == 255 for *_, alpha in pixels) == 57 * 20 + 1   # two edge columns cleared, 254-alpha kept


def test_archive_owner_edit_names_it_and_refuses_dirty_sprites(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(owner_art_storage, "factory_repository_root", lambda anchor=None: tmp_path)
    raw = _png(clean_owner_edited_frame(_edited_sprite()))
    first = owner_art_storage.archive_owner_edited_sprite(raw, replaces="LF-000123.png", original_filename="14.png")
    again = owner_art_storage.archive_owner_edited_sprite(raw, replaces="LF-000123.png", original_filename="14.png")
    assert first == again and first["filename"] == "LF-000001.png"
    assert (tmp_path / "data/output/Pixellab/Final/LF-000001.png").read_bytes() == raw
    names = json.loads((tmp_path / "data/output/Pixellab/asset-name-manifest.json").read_text(encoding="utf-8"))
    assert names["sprites"]["owner-edit:" + first["sha256"]]["replaces"] == "LF-000123.png"
    with pytest.raises(owner_art_storage.OwnerArtStorageError):
        owner_art_storage.archive_owner_edited_sprite(_png(_edited_sprite()), replaces="LF-000123.png", original_filename="14.png")


def test_edge_clipped_slices_get_a_rejected_status(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []
    import scrubbots_pixel_factory.owner_release_library as library
    monkeypatch.setattr(library, "list_records", lambda: {"records": []})
    monkeypatch.setattr(library, "transition", lambda source_id, status, **kwargs: calls.append((source_id, status, kwargs["reason"])))
    monkeypatch.setattr(launcher, "_pixellab_final_slice_path", lambda catalog, frame: Path("Final") / f"LF-{frame['index']:06d}.png")
    monkeypatch.setattr(launcher, "_purge_rejected_sources", lambda ids: {"purged": len(ids)})
    manifest = {"frames": [{"index": 1, "sha256": "a" * 64, "intake_status": "REJECTED", "reasons": ["EDGE_CLIPPED"]},
                           {"index": 2, "sha256": "b" * 64, "intake_status": "PASS", "reasons": []}]}

    assert launcher._reject_background_atlas_frames({"atlas_path": "PX-ATLAS-000124.png"}, manifest) == 1
    assert calls[0][:2] == ("owner-upload-" + "a" * 64, "REJECTED") and "EDGE_CLIPPED" in calls[0][2]
