"""PixelLab Pro 4x4 intake and mandatory lossless sprite extraction.

All Pro 4x4 source frames are 51..59 pixels on each axis. Every accepted source
is normalized to a 4W x 4H atlas and sliced into sixteen independent row-major
PNG files. No resize, filtering, palette snap, or source overwrite occurs here.
"""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
from typing import Any, Sequence
from zipfile import BadZipFile, ZipFile

from PIL import Image

from .contracts import CANONICAL_PALETTE

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
GRID = (4, 4)
MIN_FRAME_SIZE = 51
MAX_FRAME_SIZE = 59
DEFAULT_FRAME_SIZE = (56, 56)
MIN_MAX_COLORS = 3
MAX_MAX_COLORS = 12
DEFAULT_MAX_COLORS = 12
MIN_OPAQUE_PIXELS = 200
# Owner 2026-11-15 (EDGE_CLIPPED): PixelLab ignores prompt requests for an empty margin;
# 36 of 64 frames in atlases 124-127 touched the frame edge. The Factory now asks PixelLab
# for 52x52 frames and pads every cell with a 2-px transparent ring back to 56x56, so a
# sprite can never touch the 56x56 frame edge. Same price (PixelLab bills 51..64 alike).
PROVIDER_FRAME_MARGIN = 2


def provider_frame_size(width: int, height: int) -> tuple[int, int]:
    """Frame size to request from PixelLab for a wanted Factory frame size."""
    margin = 2 * PROVIDER_FRAME_MARGIN
    if width - margin < MIN_FRAME_SIZE or height - margin < MIN_FRAME_SIZE:
        return width, height
    return width - margin, height - margin


def pad_atlas_frames(raw_png: bytes) -> bytes:
    """Centre each cell of a 4x4 atlas with frames smaller than 56x56 on a transparent 56x56 cell.

    Deterministic: the same provider sheet always yields the same padded bytes, so a
    gallery re-import is recognised as the atlas already in the Factory.
    """
    atlas = _decode_png(raw_png, "Input atlas")
    width, height = atlas.width // 4, atlas.height // 4
    target_width, target_height = DEFAULT_FRAME_SIZE
    if atlas.width % 4 or atlas.height % 4 or width >= target_width or height >= target_height:
        return raw_png
    padded = Image.new("RGBA", (4 * target_width, 4 * target_height), (0, 0, 0, 0))
    offset_x, offset_y = (target_width - width) // 2, (target_height - height) // 2
    for row in range(4):
        for column in range(4):
            cell = atlas.crop((column * width, row * height, (column + 1) * width, (row + 1) * height))
            padded.paste(cell, (column * target_width + offset_x, row * target_height + offset_y))
    return _encode_png(padded)
# Owner 2026-11-15: PixelLab sometimes ignores no_background=True and draws a white /
# light-grey card behind every frame (atlases PX-ATLAS-000118..120, the arctic set).
# A frame's light-background ratio is the share of its pixels that are opaque white or
# #D4D7D9 and connect to the frame edge through transparent or such light pixels.
# Measured: clean atlases 100-117 have at most 2 frames above 0.15; the background
# atlases have 12-14. An atlas with >= 6 such frames is rejected as a whole.
LIGHT_BACKGROUND_RGB = frozenset({(255, 255, 255), (212, 215, 217)})
LIGHT_BACKGROUND_FRAME_RATIO = 0.15
LIGHT_BACKGROUND_MIN_FRAMES = 6
# Owner 2026-11-15 (PX-ATLAS-000130): PixelLab can also leave partial white cards that
# do not reach the frame edge, so the ratio above misses them. PixelLab sprites have a
# dark outline; a card (or an outline-less white blob) shows opaque white/#D4D7D9
# pixels directly on the silhouette border. Calibrated on atlases 001-132: >= 5 frames
# with >= 40 such pixels flags only 082 (kept arctic set), 129 and 130; clean white-
# animal atlases such as 019 (max 2 frames) stay accepted.
UNOUTLINED_LIGHT_FRAME_PIXELS = 40
UNOUTLINED_LIGHT_MIN_FRAMES = 5
# Owner 2026-11-15 (gallery sheet of row 0094): a card can sit behind only two or three
# frames. A card has a long perfectly straight outline-less white border; drawn smoke,
# wind or spirit art does not (those reach up to 220 outline-less pixels but their
# straight runs stay short). Measured over 132 atlases: atlas 130 card frames 20-46 px,
# 117 (white water/rock blocks under birds) 27, all other art <= 18 except one bust cut
# flat at the frame bottom (28, atlas 122). One frame with a run >= 20 is rejected alone.
LIGHT_CARD_EDGE_PIXELS = 20


def light_card_edge(frame: Image.Image) -> int:
    """Longest straight run of opaque white/#D4D7D9 pixels bordering transparency on one side."""
    rgba = frame.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()

    def light(x: int, y: int) -> bool:
        red, green, blue, alpha = pixels[x, y]
        return alpha == 255 and (red, green, blue) in LIGHT_BACKGROUND_RGB

    def clear(x: int, y: int) -> bool:
        return not (0 <= x < width and 0 <= y < height) or pixels[x, y][3] == 0

    best = 0
    for x in range(width):
        for side in (-1, 1):
            run = 0
            for y in range(height):
                run = run + 1 if light(x, y) and clear(x + side, y) else 0
                best = max(best, run)
    for y in range(height):
        for side in (-1, 1):
            run = 0
            for x in range(width):
                run = run + 1 if light(x, y) and clear(x, y + side) else 0
                best = max(best, run)
    return best


def unoutlined_light_pixels(frame: Image.Image) -> int:
    """Opaque white/#D4D7D9 pixels with a transparent (or off-frame) 4-neighbour."""
    rgba = frame.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    count = 0
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha != 255 or (red, green, blue) not in LIGHT_BACKGROUND_RGB:
                continue
            if any(not (0 <= nx < width and 0 <= ny < height) or pixels[nx, ny][3] == 0
                   for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))):
                count += 1
    return count


def light_background_ratio(frame: Image.Image) -> float:
    rgba = frame.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    seen: set[tuple[int, int]] = set()
    stack = [(x, y) for x in range(width) for y in (0, height - 1)] + [(x, y) for y in range(height) for x in (0, width - 1)]
    light = 0
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < width and 0 <= y < height):
            continue
        red, green, blue, alpha = pixels[x, y]
        if alpha != 0 and (red, green, blue) not in LIGHT_BACKGROUND_RGB:
            continue
        seen.add((x, y))
        light += alpha != 0
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return light / float(width * height)


def clean_owner_edited_frame(image: Image.Image) -> Image.Image:
    """Make an owner-edited sprite pass intake without redrawing it (owner 2026-11-15).

    Editors leave a few anti-aliased pixels: alpha >= 128 becomes opaque and < 128
    transparent; an opaque colour outside Palette V3 snaps to the nearest V3 colour;
    the sprite is centred on a square canvas (max 59) with an empty 1-px ring. Only
    when the artwork is wider/taller than 57 px is the thinner outermost column/row
    cleared.
    """
    palette = [color.rgb for color in CANONICAL_PALETTE.colors]
    exact = set(palette)
    source = image.convert("RGBA")
    cleaned = Image.new("RGBA", source.size, (0, 0, 0, 0))
    snapped: dict[tuple[int, int, int], tuple[int, int, int]] = {}
    for y in range(source.height):
        for x in range(source.width):
            red, green, blue, alpha = source.getpixel((x, y))
            if alpha < 128:
                continue
            rgb = (red, green, blue)
            if rgb not in exact:
                rgb = snapped.setdefault(rgb, min(palette, key=lambda c: sum((a - b) ** 2 for a, b in zip(c, rgb))))
            cleaned.putpixel((x, y), (*rgb, 255))
    limit = MAX_FRAME_SIZE - 2
    while True:
        box = cleaned.getchannel("A").getbbox()
        if box is None:
            raise ValueError("OWNER_EDIT_EMPTY: the sprite has no opaque pixels")
        left, top, right, bottom = box
        if right - left > limit:
            counts = [sum(cleaned.getpixel((column, y))[3] > 0 for y in range(cleaned.height)) for column in (left, right - 1)]
            column = left if counts[0] <= counts[1] else right - 1
            for y in range(cleaned.height):
                cleaned.putpixel((column, y), (0, 0, 0, 0))
        elif bottom - top > limit:
            counts = [sum(cleaned.getpixel((x, row))[3] > 0 for x in range(cleaned.width)) for row in (top, bottom - 1)]
            row = top if counts[0] <= counts[1] else bottom - 1
            for x in range(cleaned.width):
                cleaned.putpixel((x, row), (0, 0, 0, 0))
        else:
            break
    art = cleaned.crop(box)
    side = min(MAX_FRAME_SIZE, max(source.width, source.height, art.width + 2, art.height + 2, MIN_FRAME_SIZE))
    framed = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    framed.paste(art, ((side - art.width) // 2, (side - art.height) // 2))
    return framed


def validate_frame_size(width: int, height: int) -> tuple[int, int]:
    """Validate one Pro 4x4 sprite size, not its 4x4 composite dimensions."""
    if type(width) is not int or type(height) is not int:
        raise ValueError("GAME_DIMENSIONS_OUT_OF_RANGE: width and height must be integers")
    if width > MAX_FRAME_SIZE or height > MAX_FRAME_SIZE:
        raise ValueError("GAME_DIMENSIONS_OUT_OF_RANGE: ScrubBots maximum is 59x59")
    if width < MIN_FRAME_SIZE or height < MIN_FRAME_SIZE:
        raise ValueError("PRO_4X4_FRAME_COUNT_INCOMPATIBLE: each axis must be 51..59 for 16 frames")
    return width, height


def validate_max_colors(max_colors: int) -> int:
    if type(max_colors) is not int or not MIN_MAX_COLORS <= max_colors <= MAX_MAX_COLORS:
        raise ValueError("MAX_COLORS_OUT_OF_RANGE: choose 3..12")
    return max_colors


def _decode_png(raw_png: bytes, label: str) -> Image.Image:
    if type(raw_png) is not bytes or len(raw_png) > 16 * 1024 * 1024 or not raw_png.startswith(PNG_SIGNATURE):
        raise ValueError(f"{label} must have the exact eight-byte PNG signature")
    try:
        with Image.open(BytesIO(raw_png)) as source:
            if source.format != "PNG" or source.width < 1 or source.height < 1:
                raise ValueError(f"{label} is not a valid PNG")
            if source.width > 236 or source.height > 236:
                raise ValueError("GAME_DIMENSIONS_OUT_OF_RANGE: ScrubBots maximum is 59x59")
            source.load()
            return source.convert("RGBA").copy()
    except (OSError, SyntaxError) as exc:
        raise ValueError(f"{label} is not a readable PNG") from exc


def _encode_png(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=False, compress_level=9)
    return buffer.getvalue()


def normalize_frames(frame_pngs: Sequence[bytes]) -> dict[str, Any]:
    """Build a canonical atlas from exactly 16 equal PNG frames, in row-major order."""
    if isinstance(frame_pngs, (bytes, bytearray, str)) or len(frame_pngs) != 16:
        raise ValueError("PRO_4X4_FRAME_COUNT_INCOMPATIBLE: exactly 16 PNG frames are required")
    images = [_decode_png(raw, f"frame {index}") for index, raw in enumerate(frame_pngs, start=1)]
    width, height = images[0].size
    validate_frame_size(width, height)
    if any(image.size != (width, height) for image in images):
        raise ValueError("PRO_4X4_FRAME_SIZE_MISMATCH: all 16 frames must have identical dimensions")

    atlas = Image.new("RGBA", (4 * width, 4 * height), (0, 0, 0, 0))
    source_records: list[dict[str, Any]] = []
    for index, (raw, image) in enumerate(zip(frame_pngs, images), start=1):
        row, column = divmod(index - 1, 4)
        atlas.paste(image, (column * width, row * height))
        source_records.append({
            "index": index,
            "row": row + 1,
            "column": column + 1,
            "sha256": sha256(raw).hexdigest(),
            "rgba_sha256": sha256(image.tobytes()).hexdigest(),
            "width": width,
            "height": height,
        })

    atlas_png = _encode_png(atlas)
    decoded_atlas = _decode_png(atlas_png, "normalized atlas")
    for record, original in zip(source_records, images):
        left = (record["column"] - 1) * width
        top = (record["row"] - 1) * height
        if decoded_atlas.crop((left, top, left + width, top + height)).tobytes() != original.tobytes():
            raise ValueError("ATLAS_NORMALIZATION_NOT_PIXEL_EXACT")
    return {
        "atlas_png": atlas_png,
        "width": width,
        "height": height,
        "source_frames": source_records,
    }


def _frame_records(atlas: Image.Image, max_colors: int) -> tuple[tuple[Image.Image, ...], list[dict[str, Any]]]:
    atlas_width, atlas_height = atlas.size
    if atlas_width % 4 or atlas_height % 4:
        raise ValueError("PRO_4X4_ATLAS_GEOMETRY_INVALID: atlas sides must divide evenly into four")
    width, height = atlas_width // 4, atlas_height // 4
    validate_frame_size(width, height)

    palette = {color.rgb: color.id for color in CANONICAL_PALETTE.colors}
    frames: list[Image.Image] = []
    records: list[dict[str, Any]] = []
    first_by_pixel_hash: dict[str, int] = {}
    min_opaque = MIN_OPAQUE_PIXELS  # owner decision 2026-11-12: >= 200 artwork cells; the 25%-of-canvas ratio was dropped
    for row in range(4):
        for column in range(4):
            index = row * 4 + column + 1
            left, top = column * width, row * height
            frame = atlas.crop((left, top, left + width, top + height))
            frames.append(frame)
            used: set[str] = set()
            foreign: set[tuple[int, int, int]] = set()
            semi_alpha = 0
            opaque = 0
            edge_clipped = False
            pixels = frame.get_flattened_data() if hasattr(frame, "get_flattened_data") else frame.getdata()
            for red, green, blue, alpha in pixels:
                if alpha == 0:
                    continue
                if alpha != 255:
                    semi_alpha += 1
                    continue
                opaque += 1
                color_id = palette.get((red, green, blue))
                if color_id is None:
                    foreign.add((red, green, blue))
                else:
                    used.add(color_id)

            rgba_sha = sha256(frame.tobytes()).hexdigest()
            for edge_x, edge_y in (
                *((x, 0) for x in range(width)),
                *((x, height - 1) for x in range(width)),
                *((0, y) for y in range(1, height - 1)),
                *((width - 1, y) for y in range(1, height - 1)),
            ):
                if frame.getpixel((edge_x, edge_y))[3] != 0:
                    edge_clipped = True
                    break
            duplicate_of = first_by_pixel_hash.get(rgba_sha)
            first_by_pixel_hash.setdefault(rgba_sha, index)
            reasons: list[str] = []
            if foreign:
                reasons.append("FOREIGN_COLORS")
            if semi_alpha:
                reasons.append("ALPHA_CONTRACT")
            if not MIN_MAX_COLORS <= len(used) <= max_colors:
                reasons.append("USED_COLOR_COUNT")
            if opaque < min_opaque:
                reasons.append("MINIMUM_ARTWORK")
            if edge_clipped:
                reasons.append("EDGE_CLIPPED")
            if duplicate_of is not None:
                reasons.append("DUPLICATE_FRAME")
            records.append({
                "index": index,
                "row": row + 1,
                "column": column + 1,
                "bounds": [left, top, left + width, top + height],
                "width": width,
                "height": height,
                "rgba_sha256": rgba_sha,
                "duplicate_of": duplicate_of,
                "used_palette_ids": sorted(used, key=lambda item: int(item[1:])),
                "used_color_count": len(used),
                "opaque_pixels": opaque,
                "transparent_pixels": width * height - opaque - semi_alpha,
                "semi_alpha_pixels": semi_alpha,
                "foreign_rgb_count": len(foreign),
                "intake_status": "PASS" if not reasons else "REJECTED",
                "reasons": reasons,
                "light_background_ratio": round(light_background_ratio(frame), 4),
                "unoutlined_light_pixels": unoutlined_light_pixels(frame),
                "light_card_edge": light_card_edge(frame),
            })
            if records[-1]["light_card_edge"] >= LIGHT_CARD_EDGE_PIXELS:
                records[-1]["reasons"].append("OPAQUE_BACKGROUND")
                records[-1]["intake_status"] = "REJECTED"

    if (sum(record["light_background_ratio"] > LIGHT_BACKGROUND_FRAME_RATIO for record in records) >= LIGHT_BACKGROUND_MIN_FRAMES
            or sum(record["unoutlined_light_pixels"] >= UNOUTLINED_LIGHT_FRAME_PIXELS for record in records) >= UNOUTLINED_LIGHT_MIN_FRAMES):
        for record in records:
            if "OPAQUE_BACKGROUND" not in record["reasons"]:
                record["reasons"].append("OPAQUE_BACKGROUND")
            record["intake_status"] = "REJECTED"

    reconstructed = Image.new("RGBA", atlas.size, (0, 0, 0, 0))
    for record, frame in zip(records, frames):
        reconstructed.paste(frame, (record["bounds"][0], record["bounds"][1]))
    if reconstructed.tobytes() != atlas.tobytes():
        raise ValueError("ATLAS_RECONSTRUCTION_NOT_PIXEL_EXACT")
    return tuple(frames), records


def inspect_atlas(raw_png: bytes, *, max_colors: int = DEFAULT_MAX_COLORS) -> tuple[tuple[Image.Image, ...], list[dict[str, Any]]]:
    """Read a 4x4 atlas, infer W/H and return all 16 exact crops plus intake facts."""
    validate_max_colors(max_colors)
    atlas = _decode_png(raw_png, "Input atlas")
    return _frame_records(atlas, max_colors)


def _validate_coordinate_name(filename: str) -> tuple[int, int] | int | None:
    base = Path(filename).name.lower()
    match = re.fullmatch(r"(?:row|r)[-_]?(\d)[-_](?:col|column|c)[-_]?(\d)\.png", base)
    if match:
        row, column = int(match.group(1)), int(match.group(2))
        if 1 <= row <= 4 and 1 <= column <= 4:
            return row, column
        return None
    match = re.fullmatch(r"(?:sprite|frame)[-_]?(\d{1,2})\.png", base)
    if match:
        index = int(match.group(1))
        return index if 1 <= index <= 16 else None
    return None


def frames_from_photopea_zip(zip_bytes: bytes) -> tuple[bytes, ...]:
    """Read exactly 16 position-labelled PNGs; never guess order from arbitrary names."""
    if type(zip_bytes) is not bytes:
        raise ValueError("PHOTOPEA_ZIP_INVALID")
    try:
        with ZipFile(BytesIO(zip_bytes)) as archive:
            files = [item for item in archive.infolist() if not item.is_dir()]
            pngs = [item for item in files if item.filename.lower().endswith(".png")]
            if len(files) != 16 or len(pngs) != 16:
                raise ValueError("PRO_4X4_FRAME_COUNT_INCOMPATIBLE: ZIP must contain exactly 16 PNG files")
            if sum(item.file_size for item in pngs) > 128 * 1024 * 1024 or any(item.file_size > 8 * 1024 * 1024 for item in pngs):
                raise ValueError("PHOTOPEA_ZIP_SIZE_LIMIT")
            ordered: list[bytes | None] = [None] * 16
            for item in pngs:
                path_parts = item.filename.replace("\\", "/").split("/")
                if item.filename.startswith(("/", "\\")) or any(part in {"..", ""} for part in path_parts):
                    raise ValueError("PHOTOPEA_ZIP_PATH_INVALID")
                position = _validate_coordinate_name(item.filename)
                if position is None:
                    raise ValueError("PHOTOPEA_ZIP_POSITION_REQUIRED: name each file sprite-01..16 or row-1-col-1..4")
                if isinstance(position, tuple):
                    index = (position[0] - 1) * 4 + position[1]
                else:
                    index = position
                if ordered[index - 1] is not None:
                    raise ValueError("PHOTOPEA_ZIP_DUPLICATE_POSITION")
                ordered[index - 1] = archive.read(item)
    except BadZipFile as exc:
        raise ValueError("PHOTOPEA_ZIP_INVALID") from exc
    if any(item is None for item in ordered):
        raise ValueError("PHOTOPEA_ZIP_POSITION_REQUIRED: all 16 row-major slots are required")
    return tuple(item for item in ordered if item is not None)


def _persist_atlas(
    raw_png: bytes,
    output: Path,
    *,
    max_colors: int,
    source_kind: str,
    source_frames: Sequence[bytes] = (),
) -> dict[str, Any]:
    frames, records = inspect_atlas(raw_png, max_colors=max_colors)
    with Image.open(BytesIO(raw_png)) as image:
        atlas_size = list(image.size)
    width, height = atlas_size[0] // 4, atlas_size[1] // 4
    if output.exists():
        raise FileExistsError(f"Refusing existing output directory: {output}")

    encoded_slices: list[bytes] = []
    for record, frame in zip(records, frames):
        data = _encode_png(frame)
        decoded = _decode_png(data, record["filename"] if "filename" in record else "sprite PNG")
        if decoded.size != (width, height) or decoded.tobytes() != frame.tobytes():
            raise ValueError("SLICE_NOT_PIXEL_EXACT")
        record["filename"] = f"sprite-{record['index']:02d}.png"
        record["sha256"] = sha256(data).hexdigest()
        record["slice_pixel_match"] = True
        encoded_slices.append(data)

    source_records: list[dict[str, Any]] = []
    if source_frames:
        if len(source_frames) != 16:
            raise ValueError("PRO_4X4_FRAME_COUNT_INCOMPATIBLE: exactly 16 source frames are required")
        for index, raw in enumerate(source_frames, start=1):
            image = _decode_png(raw, f"source frame {index}")
            if image.size != (width, height):
                raise ValueError("PRO_4X4_FRAME_SIZE_MISMATCH")
            row, column = divmod(index - 1, 4)
            decoded_slice = frames[index - 1]
            if image.tobytes() != decoded_slice.tobytes():
                raise ValueError("SOURCE_FRAME_PIXEL_MISMATCH")
            source_records.append({
                "index": index, "row": row + 1, "column": column + 1,
                "filename": f"source-frame-{index:02d}.png",
                "sha256": sha256(raw).hexdigest(),
                "rgba_sha256": sha256(image.tobytes()).hexdigest(),
                "slice_pixel_match": True,
            })

    manifest = {
        "schema": "scrubbots-pixellab-pro-4x4-source/v2",
        "source_kind": source_kind,
        "source_atlas_sha256": sha256(raw_png).hexdigest(),
        "source_dimensions": atlas_size,
        "grid": [4, 4],
        "frame_dimensions": [width, height],
        "max_used_colors": max_colors,
        "source_frames": source_records,
        "frames": records,
        "quality_scope": "SOURCE_ONLY; solver/WIN replay/difficulty/VOID/QA are not established by slicing",
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "original-atlas.png").write_bytes(raw_png)
    if source_records:
        originals = output / "original-frames"
        originals.mkdir()
        for record, raw in zip(source_records, source_frames):
            (originals / record["filename"]).write_bytes(raw)
    for record, data in zip(records, encoded_slices):
        (output / record["filename"]).write_bytes(data)
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return manifest


def export_atlas(
    raw_png: bytes,
    new_output_directory: str | Path,
    *,
    max_colors: int = DEFAULT_MAX_COLORS,
) -> dict[str, Any]:
    """Always slice an imported atlas into 16 exact independent PNGs."""
    output = Path(new_output_directory).resolve()
    manifest = _persist_atlas(pad_atlas_frames(raw_png), output, max_colors=max_colors, source_kind="IMPORTED_ATLAS")
    if manifest["source_atlas_sha256"] != sha256(raw_png).hexdigest():
        manifest["provider_atlas_sha256"] = sha256(raw_png).hexdigest()
        manifest["provider_frame_padding"] = PROVIDER_FRAME_MARGIN
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def export_frames(
    frame_pngs: Sequence[bytes],
    new_output_directory: str | Path,
    *,
    max_colors: int = DEFAULT_MAX_COLORS,
    source_kind: str = "PRO_API_FRAMES",
) -> dict[str, Any]:
    """Normalize 16 original frames, then unconditionally re-slice that atlas."""
    validate_max_colors(max_colors)
    normalized = normalize_frames(frame_pngs)
    output = Path(new_output_directory).resolve()
    return _persist_atlas(
        normalized["atlas_png"], output, max_colors=max_colors,
        source_kind=source_kind, source_frames=frame_pngs,
    )


def export_photopea_zip(
    zip_bytes: bytes,
    new_output_directory: str | Path,
    *,
    max_colors: int = DEFAULT_MAX_COLORS,
) -> dict[str, Any]:
    """Rebuild a canonical atlas from explicitly positioned ZIP PNGs, then always slice."""
    return export_frames(
        frames_from_photopea_zip(zip_bytes), new_output_directory,
        max_colors=max_colors, source_kind="PHOTOPEA_SLICES_ZIP",
    )
