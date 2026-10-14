from __future__ import annotations

from io import BytesIO
import hashlib
import json
from pathlib import Path

from PIL import Image
import pytest

from scrubbots_pixel_factory.assets import AssetArtifactError, build_asset_artifacts, write_asset_artifacts
from scrubbots_pixel_factory.cli.main import _parser


def _png(pixels: list[tuple[int, int, int, int]], size: tuple[int, int]) -> bytes:
    image = Image.new("RGBA", size)
    image.putdata(pixels)
    stream = BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()


def _image(data: bytes) -> Image.Image:
    with Image.open(BytesIO(data)) as image:
        image.load()
        return image.copy()


def test_directional_asset_exports_are_deterministic_and_keep_pixels_and_alpha() -> None:
    source = _png([(255, 0, 0, 255), (0, 0, 0, 0), (0, 255, 0, 127), (0, 0, 255, 255)], (2, 2))
    first, manifest_bytes = build_asset_artifacts(source, source_name="owl.png", directions=("N", "E", "S", "W"))
    second, second_manifest = build_asset_artifacts(source, source_name="owl.png", directions=("N", "E", "S", "W"))
    assert first == second and manifest_bytes == second_manifest
    assert _image(first["owl_N.png"]).size == (2, 2)
    assert list(_image(first["owl_N.png"]).getdata()) == list(_image(source).getdata())
    assert _image(first["owl_E.png"]).size == (2, 2)
    assert _image(first["owl_E.png"]).getpixel((0, 0)) == (0, 255, 0, 127)
    assert _image(first["owl_W.png"]).getpixel((0, 0)) == (0, 0, 0, 0)
    manifest = json.loads(manifest_bytes)
    assert manifest["source"]["sha256"] == hashlib.sha256(source).hexdigest()
    assert manifest["source_orientation_assumption"] == "input_is_north_facing; rotations_are_mechanical_not_semantic"
    direction_entries = [entry for entry in manifest["artifacts"] if entry["kind"] == "direction_variant"]
    assert [entry["rotation_degrees_clockwise"] for entry in direction_entries] == [0, 90, 180, 270]
    assert manifest["pixel_policy"] == "nearest_pixel_transform_only_no_resampling_alpha_preserved"
    assert manifest["asset_set_sha256"] == hashlib.sha256(
        json.dumps({key: value for key, value in manifest.items() if key != "asset_set_sha256"},
                   ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def test_animation_artifacts_preserve_frame_order_and_fail_on_resize_requirement() -> None:
    first = _png([(255, 0, 0, 255), (0, 0, 0, 0)], (2, 1))
    second = _png([(0, 0, 0, 0), (255, 0, 0, 255)], (2, 1))
    files, manifest_bytes = build_asset_artifacts(first, source_name="walk-cycle.png", animation_frames=(first, second), frame_duration_ms=80)
    sheet = _image(files["walk-cycle_sheet.png"])
    assert sheet.size == (4, 1)
    assert list(sheet.getdata()) == list(_image(first).getdata()) + list(_image(second).getdata())
    manifest = json.loads(manifest_bytes)
    frame_entries = [entry for entry in manifest["artifacts"] if entry["kind"] == "animation_frame"]
    assert [entry["index"] for entry in frame_entries] == [0, 1]
    assert [entry["duration_ms"] for entry in frame_entries] == [80, 80]
    assert len([entry for entry in manifest["artifacts"] if entry["kind"] == "sprite_sheet"]) == 1
    wrong_size = _png([(1, 2, 3, 255)] * 3, (3, 1))
    with pytest.raises(AssetArtifactError, match="identical dimensions"):
        build_asset_artifacts(first, source_name="walk-cycle.png", animation_frames=(first, wrong_size))


def test_eight_direction_sets_require_explicit_diagonals_without_interpolation() -> None:
    source = _png([(255, 0, 0, 255)] * 4, (2, 2))
    diagonal = _png([(0, 255, 0, 255)] * 4, (2, 2))
    directions = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
    with pytest.raises(AssetArtifactError, match="requires an explicit direction PNG"):
        build_asset_artifacts(source, source_name="robot.png", directions=directions)
    files, manifest_bytes = build_asset_artifacts(
        source, source_name="robot.png", directions=directions,
        direction_frames={"NE": diagonal, "SE": diagonal, "SW": diagonal, "NW": diagonal},
    )
    manifest = json.loads(manifest_bytes)
    assert len([entry for entry in manifest["artifacts"] if entry["kind"] == "direction_variant"]) == 8
    diagonal_entries = [entry for entry in manifest["artifacts"] if entry.get("direction") in {"NE", "SE", "SW", "NW"}]
    assert all(entry["transform"] == "EXPLICIT_DIRECTION_PNG" for entry in diagonal_entries)
    assert all(entry["rotation_degrees_clockwise"] is None for entry in diagonal_entries)
    assert all(entry["identity_review"] == "OWNER_REVIEW_REQUIRED" for entry in diagonal_entries)
    assert _image(files["robot_NE.png"]).getpixel((0, 0)) == (0, 255, 0, 255)


def test_asset_export_contract_rejects_invalid_source_paths_and_existing_output() -> None:
    source = _png([(1, 2, 3, 255)], (1, 1))
    with pytest.raises(AssetArtifactError, match="one filename"):
        build_asset_artifacts(source, source_name="../owner.png", directions=("N",))
    with pytest.raises(AssetArtifactError, match="directions must be unique"):
        build_asset_artifacts(source, source_name="owner.png", directions=("N", "N"))
    files, _ = build_asset_artifacts(source, source_name="owner.png", directions=("N",))
    with pytest.raises(AssetArtifactError, match="already exists"):
        write_asset_artifacts(Path(__file__).parent, files)


def test_asset_export_cli_exposes_explicit_directions_frames_and_new_output_directory() -> None:
    args = _parser().parse_args(["asset-export", "source.png", "--output-dir", "derived",
                                 "--direction", "N", "--direction", "NE",
                                 "--direction-file", "NE=diagonal.png", "--frame", "frame-0.png",
                                 "--frame-duration-ms", "80"])
    assert args.command == "asset-export"
    assert args.direction == ["N", "NE"]
    assert args.direction_file == ["NE=diagonal.png"]
    assert [path.name for path in args.frame] == ["frame-0.png"]
    assert args.frame_duration_ms == 80
