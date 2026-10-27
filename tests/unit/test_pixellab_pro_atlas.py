"""Offline, no-credit exact PixelLab Pro 4x4 source-atlas regression tests."""

from io import BytesIO

import pytest
from PIL import Image, ImageDraw

from scrubbots_pixel_factory.pixellab_pro_atlas import inspect_atlas


def _synthetic_atlas(*, foreign=False, semi=False, width=224, height=224) -> bytes:
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    painter = ImageDraw.Draw(canvas)
    for row in range(4):
        for col in range(4):
            x, y = col * 56 + 8, row * 56 + 8
            painter.rectangle((x, y, x + 35, y + 35), fill=(255, 168, 0, 255))  # C02
            painter.rectangle((x + 5, y + 5, x + 20, y + 20), fill=(255, 214, 53, 255))  # C03
            painter.rectangle((x + 21, y + 21, x + 30, y + 30), fill=(0, 0, 0, 255))  # C16
    if foreign:
        canvas.putpixel((10, 10), (3, 2, 1, 255))
    if semi:
        canvas.putpixel((11, 10), (255, 168, 0, 128))
    data = BytesIO()
    canvas.save(data, "PNG")
    return data.getvalue()


def test_pro_atlas_yields_16_exact_56x56_source_pngs_without_interpolation() -> None:
    raw = _synthetic_atlas()
    with Image.open(BytesIO(raw)) as atlas:
        original = atlas.convert("RGBA")
    frames, rows = inspect_atlas(raw)
    assert len(frames) == len(rows) == 16
    assert {r["intake_status"] for r in rows} == {"PASS"}
    assert all(frame.size == (56, 56) for frame in frames)
    assert [r["index"] for r in rows] == list(range(1, 17))
    assert rows[0]["bounds"] == [0, 0, 56, 56]
    assert rows[15]["bounds"] == [168, 168, 224, 224]
    assert all(r["used_color_ids"] == ["C02", "C03", "C16"] for r in rows)
    for record, frame in zip(rows, frames):
        assert frame.tobytes() == original.crop(tuple(record["bounds"])).tobytes()


def test_pro_atlas_rejects_non_224_canvas() -> None:
    with pytest.raises(ValueError, match="Expected 224x224"):
        inspect_atlas(_synthetic_atlas(width=223))


def test_pro_atlas_flags_off_palette_without_changing_other_sprites() -> None:
    frames, rows = inspect_atlas(_synthetic_atlas(foreign=True))
    assert len(frames) == 16
    assert rows[0]["reasons"] == ["FOREIGN_COLORS"]
    assert all(r["intake_status"] == "PASS" for r in rows[1:])


def test_pro_atlas_flags_semialpha_without_silent_quantization() -> None:
    frames, rows = inspect_atlas(_synthetic_atlas(semi=True))
    assert rows[0]["reasons"] == ["ALPHA_CONTRACT"]
    assert frames[0].getpixel((11, 10)) == (255, 168, 0, 128)
    assert all(r["intake_status"] == "PASS" for r in rows[1:])


def test_pro_atlas_rejects_untrusted_non_png_bytes() -> None:
    with pytest.raises(ValueError, match="eight-byte PNG signature"):
        inspect_atlas(b"not PNG")
