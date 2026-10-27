"""PixelLab Pro atlas intake, entirely offline and pixel-exact.

A 224x224 PNG representing a four-by-four, 56x56 sprite atlas is separated
without filtering, interpolation, resizing, recoloring, or changing the
original source. Valid source frames are NOT automatically READY levels.
"""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from typing import Any

from PIL import Image

from .contracts import CANONICAL_PALETTE

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ATLAS_SIZE = (224, 224)
CELL_SIZE = (56, 56)
GRID = (4, 4)


def inspect_atlas(raw_png: bytes) -> tuple[tuple[Image.Image, ...], list[dict[str, Any]]]:
    """Pure read: return the 16 exact pixel crops and per-frame intake facts."""
    if type(raw_png) is not bytes or not raw_png.startswith(PNG_SIGNATURE):
        raise ValueError("Input must have the exact eight-byte PNG signature")
    with Image.open(BytesIO(raw_png)) as source:
        source.load()
        if source.format != "PNG" or source.size != ATLAS_SIZE:
            raise ValueError(f"Expected 224x224 PNG atlas, got {source.size}")
        rgba = source.convert("RGBA")

    ids = {color.rgb: color.id for color in CANONICAL_PALETTE.colors}
    frames: list[Image.Image] = []
    records: list[dict[str, Any]] = []
    for row in range(4):
        for col in range(4):
            ordinal = row * 4 + col + 1
            left, top = col * 56, row * 56
            frame = rgba.crop((left, top, left + 56, top + 56))
            frames.append(frame)
            used: set[str] = set()
            foreign: set[tuple[int, int, int]] = set()
            semi = 0
            occupied = 0
            for red, green, blue, alpha in frame.getdata():
                if alpha == 0:
                    continue
                if alpha != 255:
                    semi += 1
                    continue
                occupied += 1
                color_id = ids.get((red, green, blue))
                if color_id is None:
                    foreign.add((red, green, blue))
                else:
                    used.add(color_id)
            problems: list[str] = []
            if foreign:
                problems.append("FOREIGN_COLORS")
            if semi:
                problems.append("ALPHA_CONTRACT")
            if not 3 <= len(used) <= 12:
                problems.append("USED_COLOR_COUNT")
            if occupied < 200 or occupied * 4 < 56 * 56:
                problems.append("MINIMUM_ARTWORK")
            records.append({
                "index": ordinal, "row": row + 1, "column": col + 1,
                "bounds": [left, top, left + 56, top + 56],
                "width": 56, "height": 56,
                "used_color_ids": sorted(used, key=lambda x: int(x[1:])),
                "used_color_count": len(used),
                "opaque_pixels": occupied, "transparent_pixels": 56 * 56 - occupied - semi,
                "semi_alpha_pixels": semi, "foreign_rgb_count": len(foreign),
                "intake_status": "PASS" if not problems else "REJECTED",
                "reasons": problems,
            })
    joined = Image.new("RGBA", ATLAS_SIZE, (0, 0, 0, 0))
    for record, frame in zip(records, frames):
        joined.paste(frame, record["bounds"][:2])
    if joined.tobytes() != rgba.tobytes():
        raise AssertionError("Atlas pixel reconstruction is not exact")
    return tuple(frames), records


def export_atlas(raw_png: bytes, new_output_directory: str | Path) -> dict[str, Any]:
    """Write original source + 16 independent PNGs to a NEW directory only.

    A source PASS only makes a sprite eligible for subsequent Level Factory
    stages. NEVER mutate the original 140-job, existing Pool or Release here.
    """
    frames, records = inspect_atlas(raw_png)
    output = Path(new_output_directory).resolve()
    if output.exists():
        raise FileExistsError(f"Refusing existing output directory: {output}")
    encoded: list[bytes] = []
    for record, frame in zip(records, frames):
        stream = BytesIO()
        frame.save(stream, "PNG")
        data = stream.getvalue()
        with Image.open(BytesIO(data)) as check:
            if check.convert("RGBA").tobytes() != frame.tobytes():
                raise AssertionError("Export changed sprite RGBA pixels")
        record["filename"] = f"sprite-{record['index']:02d}.png"
        record["sha256"] = sha256(data).hexdigest()
        encoded.append(data)
    manifest = {
        "schema": "scrubbots-pixellab-pro-4x4-source/v1",
        "source_atlas_sha256": sha256(raw_png).hexdigest(),
        "source_dimensions": [224, 224],
        "grid": [4, 4], "frame_dimensions": [56, 56],
        "frames": records,
        "quality_scope": "SOURCE_ONLY; solver/replay/difficulty/VOID authority unverified",
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "original-atlas.png").write_bytes(raw_png)
    for record, data in zip(records, encoded):
        (output / record["filename"]).write_bytes(data)
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return manifest
