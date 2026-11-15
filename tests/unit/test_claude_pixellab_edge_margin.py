"""Owner 2026-11-15: PixelLab frames are requested at 52x52 and padded to 56x56 so no
sprite touches the frame edge (EDGE_CLIPPED)."""
from __future__ import annotations

import json
from io import BytesIO

from PIL import Image

from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE
from scrubbots_pixel_factory.pixellab_pro_atlas import export_atlas, pad_atlas_frames, provider_frame_size


def _full_bleed_atlas(frame: int) -> bytes:
    """Every cell is filled edge to edge: unpadded, all 16 frames are EDGE_CLIPPED."""
    colors = [color.rgb for color in CANONICAL_PALETTE.colors]
    atlas = Image.new("RGBA", (4 * frame, 4 * frame), (0, 0, 0, 0))
    for index in range(16):
        row, column = divmod(index, 4)
        cell = Image.new("RGBA", (frame, frame), (*colors[index % len(colors)], 255))
        cell.putpixel((index, index), (*colors[(index + 1) % len(colors)], 255))  # unique frames
        atlas.paste(cell, (column * frame, row * frame))
    buffer = BytesIO()
    atlas.save(buffer, format="PNG")
    return buffer.getvalue()


def test_provider_size_leaves_two_pixel_ring() -> None:
    assert provider_frame_size(56, 56) == (52, 52)
    assert provider_frame_size(52, 52) == (52, 52)  # 48 would be below PixelLab's 51 minimum


def test_52px_sheet_is_padded_to_56_and_never_edge_clipped(tmp_path) -> None:
    raw = _full_bleed_atlas(52)
    assert pad_atlas_frames(raw) == pad_atlas_frames(raw)  # deterministic for gallery re-sync
    manifest = export_atlas(raw, tmp_path / "out")
    assert manifest["frame_dimensions"] == [56, 56]
    assert manifest["provider_frame_padding"] == 2
    assert all("EDGE_CLIPPED" not in frame["reasons"] for frame in manifest["frames"])
    with Image.open(tmp_path / "out" / "sprite-01.png") as sprite:
        assert sprite.size == (56, 56)
        assert sprite.getpixel((1, 1))[3] == 0 and sprite.getpixel((2, 2))[3] == 255
    assert json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))["provider_atlas_sha256"]


def test_56px_sheet_is_unchanged(tmp_path) -> None:
    raw = _full_bleed_atlas(56)
    assert pad_atlas_frames(raw) == raw
    manifest = export_atlas(raw, tmp_path / "out")
    assert "provider_frame_padding" not in manifest
    assert all("EDGE_CLIPPED" in frame["reasons"] for frame in manifest["frames"])
