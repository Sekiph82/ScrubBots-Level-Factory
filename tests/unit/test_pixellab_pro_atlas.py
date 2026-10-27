"""Offline, no-credit PixelLab Pro 4x4 normalization and mandatory slicing tests."""

from contextlib import contextmanager
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import shutil
from zipfile import ZipFile

import pytest
from PIL import Image, ImageDraw

from scrubbots_pixel_factory.pixellab_pro_atlas import (
    DEFAULT_FRAME_SIZE,
    export_atlas,
    export_frames,
    export_photopea_zip,
    inspect_atlas,
    normalize_frames,
    validate_frame_size,
)


def _colors(extra: int = 0):
    values = [
        (255, 69, 0, 255), (255, 168, 0, 255), (255, 214, 53, 255),
        (0, 204, 120, 255), (0, 204, 192, 255), (81, 233, 244, 255),
        (54, 144, 234, 255), (36, 80, 164, 255), (106, 92, 255, 255),
        (255, 56, 129, 255), (156, 105, 38, 255), (255, 248, 184, 255),
    ]
    return values[: 3 + extra]


def _frame(width: int, height: int, index: int, *, color_count: int = 3, hidden_rgb: bool = False) -> bytes:
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    painter = ImageDraw.Draw(image)
    palette = _colors(color_count - 3)
    # Unique geometry per cell catches row/column swaps and duplicate frames.
    margin = 4 + index % 3
    painter.rectangle((margin, margin, width - 5, height - 5), fill=palette[0])
    painter.rectangle((margin + 3, margin + 3, width // 2 + index % 5, height // 2), fill=palette[1])
    painter.rectangle((width // 2 + 2, height // 2 + 2, width - 8, height - 8), fill=palette[2])
    for extra in range(color_count - 3):
        x = width - 9 - (extra % 3) * 2
        y = margin + 1 + (extra // 3) * 2
        image.putpixel((x, y), palette[3 + extra])
    image.putpixel((1 + index % 4, 1 + index // 4), palette[2])
    if hidden_rgb:
        image.putpixel((0, 0), (12 + index, 34, 56, 0))
    buf = BytesIO()
    image.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def _atlas(width: int = 56, height: int = 56, *, color_count: int = 3, repeat: bool = False, hidden_rgb: bool = False) -> bytes:
    canvas = Image.new("RGBA", (4 * width, 4 * height), (0, 0, 0, 0))
    for index in range(16):
        frame_index = 0 if repeat else index
        frame = Image.open(BytesIO(_frame(width, height, frame_index, color_count=color_count, hidden_rgb=hidden_rgb))).convert("RGBA")
        canvas.paste(frame, ((index % 4) * width, (index // 4) * height))
    buf = BytesIO()
    canvas.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


@contextmanager
def _test_output():
    """Use one exact repo-local test-owned path; never use Windows TEMP or remove unknown data."""
    root = Path(__file__).resolve().parent
    output = root / ".r10-pixellab-atlas-test-output"
    if output.exists():
        raise AssertionError(f"Refusing pre-existing test output: {output}")
    try:
        yield output
    finally:
        if output.exists():
            if output.resolve().parent != root:
                raise AssertionError("Test output escaped its owned test directory")
            shutil.rmtree(output)


@pytest.mark.parametrize("size", [51, 52, 56, 59])
def test_pro_4x4_accepts_documented_per_frame_sizes_and_returns_16_exact_crops(size: int) -> None:
    raw = _atlas(size, size)
    frames, records = inspect_atlas(raw)
    assert len(frames) == len(records) == 16
    assert {record["intake_status"] for record in records} == {"PASS"}
    assert [record["index"] for record in records] == list(range(1, 17))
    assert [(record["row"], record["column"]) for record in records] == [
        (row, column) for row in range(1, 5) for column in range(1, 5)
    ]
    assert all(frame.size == (size, size) for frame in frames)
    with Image.open(BytesIO(raw)) as source:
        rgba = source.convert("RGBA")
    for record, frame in zip(records, frames):
        assert frame.tobytes() == rgba.crop(tuple(record["bounds"])).tobytes()


@pytest.mark.parametrize("size", [(52, 56), (56, 59), (59, 51)])
def test_pro_4x4_supports_independent_non_square_dimensions(size: tuple[int, int]) -> None:
    width, height = size
    frames, records = inspect_atlas(_atlas(width, height))
    assert all(frame.size == size for frame in frames)
    assert all((row["width"], row["height"]) == size for row in records)


@pytest.mark.parametrize(
    ("width", "height", "reason"),
    [
        (50, 56, "PRO_4X4_FRAME_COUNT_INCOMPATIBLE"),
        (56, 50, "PRO_4X4_FRAME_COUNT_INCOMPATIBLE"),
        (60, 56, "GAME_DIMENSIONS_OUT_OF_RANGE"),
        (56, 64, "GAME_DIMENSIONS_OUT_OF_RANGE"),
    ],
)
def test_pro_4x4_rejects_incompatible_and_over_59_axes(width: int, height: int, reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        validate_frame_size(width, height)
    with pytest.raises(ValueError, match=reason):
        inspect_atlas(_atlas(width, height))


def test_256_square_atlas_is_rejected_as_64x64_game_overflow() -> None:
    with pytest.raises(ValueError, match="GAME_DIMENSIONS_OUT_OF_RANGE"):
        inspect_atlas(_atlas(64, 64))


def test_nondivisible_atlas_geometry_is_rejected() -> None:
    image = Image.new("RGBA", (207, 208), (0, 0, 0, 0))
    buf = BytesIO()
    image.save(buf, format="PNG")
    with pytest.raises(ValueError, match="PRO_4X4_ATLAS_GEOMETRY_INVALID"):
        inspect_atlas(buf.getvalue())


def test_locked_palette_and_adjustable_max_colors_apply_per_sprite() -> None:
    _, accepted = inspect_atlas(_atlas(56, 56, color_count=7), max_colors=7)
    assert all(record["intake_status"] == "PASS" for record in accepted)
    _, defaulted = inspect_atlas(_atlas(56, 56, color_count=7), max_colors=12)
    assert all(record["used_color_count"] == 7 for record in defaulted)
    _, rejected = inspect_atlas(_atlas(56, 56, color_count=7), max_colors=6)
    assert all(record["reasons"] == ["USED_COLOR_COUNT"] for record in rejected)
    _, minimum = inspect_atlas(_atlas(56, 56, color_count=3), max_colors=3)
    assert all(record["intake_status"] == "PASS" for record in minimum)
    with pytest.raises(ValueError, match="MAX_COLORS_OUT_OF_RANGE"):
        inspect_atlas(_atlas(), max_colors=2)
    with pytest.raises(ValueError, match="MAX_COLORS_OUT_OF_RANGE"):
        inspect_atlas(_atlas(), max_colors=13)


def test_out_of_palette_semi_alpha_and_duplicates_are_individually_rejected() -> None:
    raw = _atlas(repeat=True)
    frames, records = inspect_atlas(raw)
    assert len(frames) == 16
    assert records[0]["intake_status"] == "PASS"
    assert all("DUPLICATE_FRAME" in record["reasons"] for record in records[1:])

    canvas = Image.open(BytesIO(_atlas())).convert("RGBA")
    canvas.putpixel((9, 9), (12, 13, 14, 255))
    canvas.putpixel((10, 9), (255, 168, 0, 128))
    buf = BytesIO()
    canvas.save(buf, format="PNG")
    _, changed = inspect_atlas(buf.getvalue())
    assert "FOREIGN_COLORS" in changed[0]["reasons"]
    assert "ALPHA_CONTRACT" in changed[0]["reasons"]
    assert all(record["intake_status"] == "PASS" for record in changed[1:])


def test_hidden_transparent_rgb_roundtrips_exactly() -> None:
    raw = _atlas(hidden_rgb=True)
    normalized = normalize_frames([_frame(56, 56, index, hidden_rgb=True) for index in range(16)])
    source = Image.open(BytesIO(normalized["atlas_png"])).convert("RGBA")
    assert normalized["width"] == normalized["height"] == DEFAULT_FRAME_SIZE[0]
    assert source.getpixel((0, 0)) == (12, 34, 56, 0)
    frames, _ = inspect_atlas(raw)
    with Image.open(BytesIO(raw)) as original:
        assert frames[0].tobytes() == original.convert("RGBA").crop((0, 0, 56, 56)).tobytes()


def test_opaque_pixels_touching_a_cell_edge_are_rejected_as_clipped() -> None:
    canvas = Image.open(BytesIO(_atlas())).convert("RGBA")
    canvas.putpixel((0, 20), _colors()[0])
    buffer = BytesIO()
    canvas.save(buffer, format="PNG")
    _, records = inspect_atlas(buffer.getvalue())
    assert "EDGE_CLIPPED" in records[0]["reasons"]
    assert all(record["intake_status"] == "PASS" for record in records[1:])


def test_api_frames_are_normalized_then_always_sliced_and_originals_preserved() -> None:
    originals = [_frame(52, 59, index, hidden_rgb=True) for index in range(16)]
    baseline = [sha256(frame).hexdigest() for frame in originals]
    normalized = normalize_frames(originals)
    atlas = normalized["atlas_png"]
    atlas_image = Image.open(BytesIO(atlas)).convert("RGBA")
    assert atlas_image.size == (208, 236)
    assert len(normalized["source_frames"]) == 16
    with _test_output() as output:
        manifest = export_frames(originals, output, max_colors=12)
        assert len(list(output.glob("sprite-*.png"))) == 16
        assert len(list((output / "original-frames").glob("*.png"))) == 16
        assert manifest["source_kind"] == "PRO_API_FRAMES"
        assert manifest["source_dimensions"] == [208, 236]
        assert [row["index"] for row in manifest["frames"]] == list(range(1, 17))
        assert all(row["slice_pixel_match"] is True for row in manifest["frames"])
        saved_manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        assert saved_manifest == manifest
        for index, original in enumerate(originals, start=1):
            kept = output / "original-frames" / f"source-frame-{index:02d}.png"
            assert sha256(kept.read_bytes()).hexdigest() == baseline[index - 1]
            crop = Image.open(BytesIO((output / f"sprite-{index:02d}.png").read_bytes())).convert("RGBA")
            row, column = divmod(index - 1, 4)
            expected = atlas_image.crop((column * 52, row * 59, (column + 1) * 52, (row + 1) * 59))
            assert crop.tobytes() == expected.tobytes()
        assert [sha256(frame).hexdigest() for frame in originals] == baseline


def test_imported_atlas_export_always_slices_and_refuses_existing_output() -> None:
    raw = _atlas(59, 52)
    baseline = sha256(raw).hexdigest()
    with _test_output() as output:
        manifest = export_atlas(raw, output, max_colors=7)
        assert manifest["source_kind"] == "IMPORTED_ATLAS"
        assert manifest["source_dimensions"] == [236, 208]
        assert len(list(output.glob("sprite-*.png"))) == 16
        assert sha256((output / "original-atlas.png").read_bytes()).hexdigest() == baseline
        with pytest.raises(FileExistsError):
            export_atlas(raw, output)
    assert sha256(raw).hexdigest() == baseline


def test_photopea_zip_requires_reliable_positions_then_reconstructs_and_slices() -> None:
    originals = [_frame(56, 52, index) for index in range(16)]
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        for index, raw in enumerate(originals, start=1):
            archive.writestr(f"sprite-{index:02d}.png", raw)
    with _test_output() as output:
        manifest = export_photopea_zip(buffer.getvalue(), output)
        assert manifest["source_kind"] == "PHOTOPEA_SLICES_ZIP"
        assert manifest["source_dimensions"] == [224, 208]
        assert len(list(output.glob("sprite-*.png"))) == 16

    unknown = BytesIO()
    with ZipFile(unknown, "w") as archive:
        for index, raw in enumerate(originals):
            archive.writestr(f"art_{index}.png", raw)
    with pytest.raises(ValueError, match="PHOTOPEA_ZIP_POSITION_REQUIRED"):
        export_photopea_zip(unknown.getvalue(), Path(__file__).parent / ".r10-should-not-be-created")
