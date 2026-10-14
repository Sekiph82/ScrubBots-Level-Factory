"""Deterministic PNG variants and animation sheets for local asset delivery.

The input PNG is read-only. Transformations operate on decoded logical pixels,
never resample, and retain alpha. Results are explicit derivatives, not owner
approval or game-ready claims.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from io import BytesIO
import hashlib
import json
from pathlib import Path
import re

from PIL import Image, UnidentifiedImageError


MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_IMAGE_PIXELS = 1_048_576
MAX_FRAMES = 120
_DIRECTIONS = {"E": Image.Transpose.ROTATE_270, "S": Image.Transpose.ROTATE_180,
               "W": Image.Transpose.ROTATE_90}
_ROTATION_DEGREES = {"N": 0, "E": 90, "S": 180, "W": 270}
_ALL_DIRECTIONS = frozenset({"N", "NE", "E", "SE", "S", "SW", "W", "NW"})
_SAFE_STEM = re.compile(r"[^A-Za-z0-9._-]+")


class AssetArtifactError(ValueError):
    """Raised when a source or derivative asset set is invalid."""


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _decode_png(data: bytes, label: str) -> Image.Image:
    if not isinstance(data, bytes) or not data or len(data) > MAX_SOURCE_BYTES:
        raise AssetArtifactError(f"{label} must be non-empty PNG bytes no larger than {MAX_SOURCE_BYTES} bytes")
    try:
        with Image.open(BytesIO(data)) as opened:
            if opened.format != "PNG" or opened.width < 1 or opened.height < 1:
                raise AssetArtifactError(f"{label} must be a valid PNG")
            if opened.width * opened.height > MAX_IMAGE_PIXELS:
                raise AssetArtifactError(f"{label} exceeds the bounded pixel count")
            opened.load()
            return opened.convert("RGBA")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise AssetArtifactError(f"{label} is not a readable PNG") from exc


def _png_bytes(image: Image.Image) -> bytes:
    stream = BytesIO()
    image.save(stream, format="PNG", optimize=False, compress_level=9)
    return stream.getvalue()


def build_asset_artifacts(
    source_png: bytes,
    *,
    source_name: str,
    directions: Iterable[str] = (),
    direction_frames: Mapping[str, bytes] | None = None,
    animation_frames: Iterable[bytes] = (),
    frame_duration_ms: int = 100,
) -> tuple[Mapping[str, bytes], bytes]:
    """Build rotations and/or a sprite sheet with a content-addressed manifest."""
    if type(source_name) is not str or not source_name.strip() or Path(source_name).name != source_name:
        raise AssetArtifactError("source_name must be one filename, not a path")
    source = _decode_png(source_png, "source")
    requested = tuple(directions)
    if any(type(item) is not str or item not in _ALL_DIRECTIONS for item in requested):
        raise AssetArtifactError("directions must use N, NE, E, SE, S, SW, W, or NW")
    if len(requested) != len(set(requested)):
        raise AssetArtifactError("directions must be unique")
    if direction_frames is not None and not isinstance(direction_frames, Mapping):
        raise AssetArtifactError("direction_frames must be an explicit direction-to-PNG mapping")
    supplied = dict(direction_frames or {})
    if any(type(key) is not str or key not in _ALL_DIRECTIONS or key not in requested for key in supplied):
        raise AssetArtifactError("explicit direction frames must match requested direction labels")
    if type(frame_duration_ms) is not int or not 1 <= frame_duration_ms <= 60_000:
        raise AssetArtifactError("frame_duration_ms must be an integer in 1..60000")
    frames_raw = tuple(animation_frames)
    if len(frames_raw) > MAX_FRAMES:
        raise AssetArtifactError(f"animation may contain at most {MAX_FRAMES} frames")
    stem = _SAFE_STEM.sub("_", Path(source_name).stem).strip("._-") or "artwork"
    files: dict[str, bytes] = {}
    entries: list[dict[str, object]] = []

    for direction in requested:
        if direction in supplied:
            input_bytes = supplied[direction]
            image = _decode_png(input_bytes, f"direction {direction}")
            transform = "EXPLICIT_DIRECTION_PNG"
            rotation = None
        elif direction == "N":
            input_bytes = source_png
            image = source.copy()
            transform = "SOURCE_COPY"
            rotation = 0
        elif direction in _DIRECTIONS:
            input_bytes = source_png
            image = source.transpose(_DIRECTIONS[direction])
            transform = "PIXEL_ROTATION"
            rotation = _ROTATION_DEGREES[direction]
        else:
            raise AssetArtifactError(f"diagonal direction {direction} requires an explicit direction PNG; no 45-degree resampling is performed")
        name = f"{stem}_{direction}.png"
        payload = _png_bytes(image)
        files[name] = payload
        entries.append({"kind": "direction_variant", "direction": direction, "path": name,
                        "transform": transform, "rotation_degrees_clockwise": rotation,
                        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
                        "identity_review": "OWNER_REVIEW_REQUIRED",
                        "width": image.width, "height": image.height,
                        "sha256": hashlib.sha256(payload).hexdigest()})

    if frames_raw:
        decoded = [_decode_png(item, f"animation frame {index}") for index, item in enumerate(frames_raw)]
        frame_size = (decoded[0].width, decoded[0].height)
        if any((image.width, image.height) != frame_size for image in decoded):
            raise AssetArtifactError("animation frames must have identical dimensions; resizing is not permitted")
        palette = set(decoded[0].getdata())
        if any(set(image.getdata()) != palette for image in decoded[1:]):
            raise AssetArtifactError("animation frames must preserve one identical RGBA palette")
        if frame_size[0] * frame_size[1] * len(decoded) > MAX_IMAGE_PIXELS:
            raise AssetArtifactError("animation sheet exceeds the bounded pixel count")
        sheet = Image.new("RGBA", (frame_size[0] * len(decoded), frame_size[1]), (0, 0, 0, 0))
        for index, image in enumerate(decoded):
            sheet.alpha_composite(image, (index * frame_size[0], 0))
            frame_name = f"{stem}_frame_{index:03d}.png"
            frame_payload = _png_bytes(image)
            files[frame_name] = frame_payload
            entries.append({"kind": "animation_frame", "index": index, "path": frame_name,
                            "duration_ms": frame_duration_ms, "width": image.width,
                            "height": image.height, "sha256": hashlib.sha256(frame_payload).hexdigest()})
        sheet_name = f"{stem}_sheet.png"
        sheet_payload = _png_bytes(sheet)
        files[sheet_name] = sheet_payload
        entries.append({"kind": "sprite_sheet", "path": sheet_name, "frame_count": len(decoded),
                        "frame_width": frame_size[0], "frame_height": frame_size[1],
                        "width": sheet.width, "height": sheet.height,
                        "sha256": hashlib.sha256(sheet_payload).hexdigest()})

    if not files:
        raise AssetArtifactError("at least one direction or animation frame is required")
    body = {"schema": "scrubbots-pixel-art-asset-set", "schema_version": 1,
            "source": {"name": source_name, "sha256": hashlib.sha256(source_png).hexdigest(),
                       "width": source.width, "height": source.height},
            "source_orientation_assumption": "input_is_north_facing; rotations_are_mechanical_not_semantic",
            "pixel_policy": "nearest_pixel_transform_only_no_resampling_alpha_preserved",
            "frame_duration_ms": frame_duration_ms if frames_raw else None,
            "artifacts": entries}
    body["asset_set_sha256"] = hashlib.sha256(_canonical_json(body)).hexdigest()
    files[f"{stem}_asset_manifest.json"] = _canonical_json(body) + b"\n"
    return files, _canonical_json(body) + b"\n"


def write_asset_artifacts(output_dir: Path, artifacts: Mapping[str, bytes]) -> tuple[Path, ...]:
    """Write a complete new artifact directory; refuse every pre-existing path."""
    if not isinstance(output_dir, Path) or not artifacts or any(Path(name).name != name for name in artifacts):
        raise AssetArtifactError("output requires a new directory and safe single-component artifact names")
    if output_dir.exists() or output_dir.is_symlink():
        raise AssetArtifactError("output directory already exists; existing owner files are never overwritten")
    output_dir.mkdir(parents=True, exist_ok=False)
    created: list[Path] = []
    for name, payload in artifacts.items():
        target = output_dir / name
        with target.open("xb") as stream:
            stream.write(payload)
        created.append(target)
    return tuple(created)
