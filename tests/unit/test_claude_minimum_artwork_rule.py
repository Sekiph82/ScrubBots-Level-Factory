"""Owner decision 2026-11-12: drop the 25%-of-canvas artwork ratio, keep >= 200 cells.

In the 2026-11-12 run, 22 PixelLab Final PNGs (56x56, 462..778 artwork
cells) were rejected with MINIMUM_ARTWORK only because 778 < 25% of 3136.
A full 20x20 level has 400 cells and is accepted, so the ratio rejected
artwork larger than accepted levels. The absolute 200-cell floor stays.
"""
from io import BytesIO

from PIL import Image, ImageDraw

from scrubbots_pixel_factory.pixellab_pro_atlas import inspect_atlas


def _thin_frame(index: int, opaque_rows: int) -> Image.Image:
    """56x56 sprite with 3 canonical colours and opaque_rows x 14 cells of artwork."""
    image = Image.new("RGBA", (56, 56), (0, 0, 0, 0))
    painter = ImageDraw.Draw(image)
    colours = [(255, 69, 0, 255), (255, 168, 0, 255), (255, 214, 53, 255)]
    top = 4 + index % 3
    for row in range(opaque_rows):
        painter.line((20, top + row, 33, top + row), fill=colours[row % 3])
    image.putpixel((40, 40 + index // 4), colours[index % 3])  # unique per frame
    return image


def _atlas(opaque_rows: int) -> bytes:
    canvas = Image.new("RGBA", (224, 224), (0, 0, 0, 0))
    for index in range(16):
        canvas.paste(_thin_frame(index, opaque_rows), ((index % 4) * 56, (index // 4) * 56))
    buffer = BytesIO()
    canvas.save(buffer, format="PNG")
    return buffer.getvalue()


def test_pixellab_intake_accepts_artwork_above_200_cells_below_quarter_canvas() -> None:
    # 48 rows x 14 = 672 (+1) cells: above 200, below 25% of 3136 (784).
    _frames, records = inspect_atlas(_atlas(48))
    for record in records:
        assert 200 <= record["opaque_pixels"] < 784
        assert "MINIMUM_ARTWORK" not in record["reasons"], record


def test_pixellab_intake_still_rejects_artwork_below_200_cells() -> None:
    # 13 rows x 14 = 182 (+1) cells.
    _frames, records = inspect_atlas(_atlas(13))
    assert all("MINIMUM_ARTWORK" in record["reasons"] for record in records)
