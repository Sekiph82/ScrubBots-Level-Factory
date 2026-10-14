from __future__ import annotations

from io import BytesIO
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from scrubbots_pixel_factory.assets.artifacts import (
    AssetArtifactError,
    build_asset_artifacts,
    validate_asset_artifact_set,
)


def _pixel_png(color: tuple[int, int, int, int]) -> bytes:
    stream = BytesIO()
    Image.new("RGBA", (1, 1), color).save(stream, format="PNG")
    return stream.getvalue()


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _replace_manifest_entry(
    files: dict[str, bytes], manifest: bytes, *, path: str, changes: dict[str, object], payload: bytes | None = None,
) -> tuple[dict[str, bytes], bytes]:
    document = json.loads(manifest)
    for entry in document["artifacts"]:
        if entry["path"] == path:
            entry.update(changes)
    if payload is not None:
        for entry in document["artifacts"]:
            if entry["path"] == path:
                entry["sha256"] = hashlib.sha256(payload).hexdigest()
    body = {key: value for key, value in document.items() if key != "asset_set_sha256"}
    document["asset_set_sha256"] = hashlib.sha256(_canonical(body)).hexdigest()
    updated_manifest = _canonical(document) + b"\n"
    updated = dict(files)
    if payload is not None:
        updated[path] = payload
    manifest_path = next(name for name in updated if name.endswith("_asset_manifest.json"))
    updated[manifest_path] = updated_manifest
    return updated, updated_manifest


def test_asset_set_validation_and_animation_iteration_are_bounded_in_memory() -> None:
    source = _pixel_png((20, 40, 60, 255))
    files, manifest = build_asset_artifacts(
        source,
        source_name="test-art.png",
        directions=("N", "E"),
        animation_frames=(source, source),
        frame_duration_ms=80,
    )
    assert validate_asset_artifact_set(files, manifest)

    corrupted = dict(files)
    corrupted["test-art_frame_001.png"] = source + b"changed"
    try:
        validate_asset_artifact_set(corrupted, manifest)
    except AssetArtifactError:
        pass
    else:
        raise AssertionError("changed derivative bytes must fail the manifest hash check")

    sheet_path = "test-art_sheet.png"
    # The wrong sheet has 1x1 dimensions, so use a correctly sized 2x1 PNG.
    wrong_sheet_stream = BytesIO()
    Image.new("RGBA", (2, 1), (200, 100, 50, 255)).save(wrong_sheet_stream, format="PNG")
    wrong_sheet = wrong_sheet_stream.getvalue()
    wrong_files, wrong_manifest = _replace_manifest_entry(
        dict(files), manifest, path=sheet_path, changes={}, payload=wrong_sheet,
    )
    try:
        validate_asset_artifact_set(wrong_files, wrong_manifest)
    except AssetArtifactError:
        pass
    else:
        raise AssertionError("a re-hashed sheet with pixels unrelated to its frames must be rejected")

    wrong_order, wrong_order_manifest = _replace_manifest_entry(
        dict(files), manifest, path="test-art_frame_001.png", changes={"index": 9},
    )
    try:
        validate_asset_artifact_set(wrong_order, wrong_order_manifest)
    except AssetArtifactError:
        pass
    else:
        raise AssertionError("noncontiguous animation indexes must be rejected")

    consumed = 0

    def too_many_directions():
        nonlocal consumed
        while True:
            consumed += 1
            yield "N"

    try:
        build_asset_artifacts(source, source_name="bounded.png", directions=too_many_directions())
    except AssetArtifactError:
        pass
    else:
        raise AssertionError("unbounded direction iterables must be rejected")
    assert consumed == 9

    try:
        build_asset_artifacts(
            source,
            source_name="bounded-animation.png",
            animation_frames=(source for _ in range(121)),
        )
    except AssetArtifactError:
        pass
    else:
        raise AssertionError("animation frame iterables above MAX_FRAMES must be rejected")
