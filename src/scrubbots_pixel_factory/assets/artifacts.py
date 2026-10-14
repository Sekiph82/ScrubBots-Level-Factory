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
    requested_list: list[str] = []
    for direction in directions:
        if len(requested_list) >= len(_ALL_DIRECTIONS):
            raise AssetArtifactError("directions may contain at most the eight supported labels")
        requested_list.append(direction)
    requested = tuple(requested_list)
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
    frames_raw: list[bytes] = []
    for frame in animation_frames:
        if len(frames_raw) >= MAX_FRAMES:
            raise AssetArtifactError(f"animation may contain at most {MAX_FRAMES} frames")
        frames_raw.append(frame)
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
        decoded: list[Image.Image] = []
        frame_size: tuple[int, int] | None = None
        palette: set[tuple[int, int, int, int]] | None = None
        total_frame_pixels = 0
        for index, raw in enumerate(frames_raw):
            image = _decode_png(raw, f"animation frame {index}")
            image_size = (image.width, image.height)
            if frame_size is None:
                frame_size = image_size
                palette = set(image.getdata())
            elif image_size != frame_size:
                raise AssetArtifactError("animation frames must have identical dimensions; resizing is not permitted")
            total_frame_pixels += image.width * image.height
            if total_frame_pixels > MAX_IMAGE_PIXELS:
                raise AssetArtifactError("animation sheet exceeds the bounded pixel count")
            if set(image.getdata()) != palette:
                raise AssetArtifactError("animation frames must preserve one identical RGBA palette")
            decoded.append(image)
        assert frame_size is not None
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
    validate_asset_artifact_set(files, files[f"{stem}_asset_manifest.json"])
    return files, _canonical_json(body) + b"\n"


def validate_asset_artifact_set(artifacts: Mapping[str, bytes], manifest_bytes: bytes) -> bool:
    """Verify a derivative set and manifest entirely in memory.

    This verifies byte identity and structural bounds only. It does not infer
    semantic direction, owner approval, or game-import readiness.
    """
    if not isinstance(artifacts, Mapping) or not artifacts or type(manifest_bytes) is not bytes:
        raise AssetArtifactError("asset set and manifest bytes are required")
    try:
        document = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssetArtifactError("asset manifest is not valid UTF-8 JSON") from exc
    if not isinstance(document, dict) or set(document) != {
        "schema", "schema_version", "source", "source_orientation_assumption",
        "pixel_policy", "frame_duration_ms", "artifacts", "asset_set_sha256",
    }:
        raise AssetArtifactError("asset manifest fields do not match the supported schema")
    if document.get("schema") != "scrubbots-pixel-art-asset-set" or document.get("schema_version") != 1:
        raise AssetArtifactError("asset manifest schema or version is unsupported")
    if (document.get("source_orientation_assumption") != "input_is_north_facing; rotations_are_mechanical_not_semantic"
            or document.get("pixel_policy") != "nearest_pixel_transform_only_no_resampling_alpha_preserved"):
        raise AssetArtifactError("asset manifest pixel or orientation policy is unsupported")
    if manifest_bytes != _canonical_json(document) + b"\n":
        raise AssetArtifactError("asset manifest bytes are not canonical JSON")
    body = {key: value for key, value in document.items() if key != "asset_set_sha256"}
    expected_set_sha = document.get("asset_set_sha256")
    if type(expected_set_sha) is not str or hashlib.sha256(_canonical_json(body)).hexdigest() != expected_set_sha:
        raise AssetArtifactError("asset manifest digest does not match its canonical fields")
    source = document.get("source")
    if not isinstance(source, dict) or set(source) != {"name", "sha256", "width", "height"}:
        raise AssetArtifactError("asset manifest source identity is malformed")
    if type(source["name"]) is not str or Path(source["name"]).name != source["name"]:
        raise AssetArtifactError("asset manifest source name is unsafe")
    if type(source["sha256"]) is not str or re.fullmatch(r"[0-9a-f]{64}", source["sha256"]) is None:
        raise AssetArtifactError("asset manifest source digest is malformed")
    if any(type(source[key]) is not int or source[key] < 1 for key in ("width", "height")):
        raise AssetArtifactError("asset manifest source dimensions are malformed")
    if source["width"] * source["height"] > MAX_IMAGE_PIXELS:
        raise AssetArtifactError("asset manifest source exceeds the bounded pixel count")
    entries = document.get("artifacts")
    if not isinstance(entries, list) or not entries:
        raise AssetArtifactError("asset manifest must contain at least one derivative")
    referenced: set[str] = set()
    artifact_images: dict[str, Image.Image] = {}
    direction_rows: list[Mapping[str, object]] = []
    frame_rows: list[Mapping[str, object]] = []
    sheet_rows: list[Mapping[str, object]] = []
    for entry in entries:
        if not isinstance(entry, dict) or type(entry.get("path")) is not str:
            raise AssetArtifactError("asset manifest entry is malformed")
        path = entry["path"]
        if Path(path).name != path or path in referenced or path not in artifacts:
            raise AssetArtifactError("asset manifest path is unsafe, duplicated, or missing")
        referenced.add(path)
        payload = artifacts[path]
        if type(payload) is not bytes or type(entry.get("sha256")) is not str:
            raise AssetArtifactError("asset artifact bytes or digest are malformed")
        if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise AssetArtifactError("asset artifact bytes do not match the manifest digest")
        image = _decode_png(payload, f"artifact {path}")
        artifact_images[path] = image
        if (type(entry.get("width")) is not int or type(entry.get("height")) is not int
                or (image.width, image.height) != (entry["width"], entry["height"])):
            raise AssetArtifactError("asset artifact dimensions do not match the manifest")
        kind = entry.get("kind")
        if kind == "direction_variant":
            direction_rows.append(entry)
        elif kind == "animation_frame":
            frame_rows.append(entry)
        elif kind == "sprite_sheet":
            sheet_rows.append(entry)
        else:
            raise AssetArtifactError("asset manifest entry kind is unsupported")
    manifest_names = [name for name in artifacts if name.endswith("_asset_manifest.json")]
    if len(manifest_names) != 1 or artifacts[manifest_names[0]] != manifest_bytes:
        raise AssetArtifactError("asset set must contain the exact matching manifest bytes")
    if set(artifacts) - referenced != {manifest_names[0]}:
        raise AssetArtifactError("asset set contains unreferenced files")
    if (not frame_rows and sheet_rows) or (frame_rows and len(sheet_rows) != 1):
        raise AssetArtifactError("animation frame and sprite sheet membership is inconsistent")
    directions_seen: set[str] = set()
    for row in direction_rows:
        direction = row.get("direction")
        transform = row.get("transform")
        if (type(direction) is not str or direction not in _ALL_DIRECTIONS or direction in directions_seen
                or row.get("identity_review") != "OWNER_REVIEW_REQUIRED"):
            raise AssetArtifactError("direction entry identity or review gate is invalid")
        directions_seen.add(direction)
        input_sha = row.get("input_sha256")
        if type(input_sha) is not str or re.fullmatch(r"[0-9a-f]{64}", input_sha) is None:
            raise AssetArtifactError("direction entry input digest is malformed")
        if transform == "PIXEL_ROTATION":
            if direction not in _DIRECTIONS or row.get("rotation_degrees_clockwise") != _ROTATION_DEGREES[direction]:
                raise AssetArtifactError("direction rotation is not a supported cardinal pixel transform")
        elif transform == "SOURCE_COPY":
            if direction != "N" or row.get("rotation_degrees_clockwise") != 0:
                raise AssetArtifactError("source-copy transform is valid only for north")
        elif transform == "EXPLICIT_DIRECTION_PNG":
            if row.get("rotation_degrees_clockwise") is not None:
                raise AssetArtifactError("explicit direction art cannot claim a mechanical rotation")
        else:
            raise AssetArtifactError("direction transform is unsupported")
    if frame_rows:
        if any(type(row.get("index")) is not int for row in frame_rows) or len(frame_rows) > MAX_FRAMES:
            raise AssetArtifactError("animation frame ordering or count is invalid")
        frame_rows.sort(key=lambda row: row["index"])
        if [row.get("index") for row in frame_rows] != list(range(len(frame_rows))):
            raise AssetArtifactError("animation frame ordering or count is invalid")
        durations = [row.get("duration_ms") for row in frame_rows]
        if (any(type(item) is not int for item in durations) or len(set(durations)) != 1
                or not 1 <= durations[0] <= 60_000):
            raise AssetArtifactError("animation frame duration is invalid")
        sheet = sheet_rows[0]
        if type(sheet.get("frame_count")) is not int or sheet.get("frame_count") != len(frame_rows):
            raise AssetArtifactError("sprite sheet frame count does not match the animation")
        frame_size = (frame_rows[0].get("width"), frame_rows[0].get("height"))
        if any((row.get("width"), row.get("height")) != frame_size for row in frame_rows):
            raise AssetArtifactError("animation frame dimensions are inconsistent")
        frame_images = [artifact_images[row["path"]] for row in frame_rows]
        frame_palette = set(frame_images[0].getdata())
        if any(set(image.getdata()) != frame_palette for image in frame_images[1:]):
            raise AssetArtifactError("animation frames do not preserve one identical RGBA palette")
        if (sheet.get("frame_width"), sheet.get("frame_height")) != frame_size:
            raise AssetArtifactError("sprite sheet frame dimensions do not match the animation")
        if sheet.get("width") != frame_size[0] * len(frame_rows) or sheet.get("height") != frame_size[1]:
            raise AssetArtifactError("sprite sheet dimensions do not match its ordered frames")
        if frame_size[0] * frame_size[1] * len(frame_rows) > MAX_IMAGE_PIXELS:
            raise AssetArtifactError("animation sheet exceeds the bounded pixel count")
        expected_sheet = Image.new("RGBA", (frame_size[0] * len(frame_rows), frame_size[1]), (0, 0, 0, 0))
        for index, image in enumerate(frame_images):
            expected_sheet.alpha_composite(image, (index * frame_size[0], 0))
        if list(expected_sheet.getdata()) != list(artifact_images[sheet["path"]].getdata()):
            raise AssetArtifactError("sprite sheet pixels do not match the ordered animation frames")
    return True


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
