from __future__ import annotations

import json
from pathlib import Path

from scrubbots_pixel_factory.output import ArtworkArtifact, decode_logical_png, encode_logical_png, logical_rgb_bytes


GOLDEN_ROOT = Path(__file__).parent / "fixtures" / "m08"


def test_committed_m08_artwork_json_png_pair_is_byte_stable_and_exact() -> None:
    artwork_path = GOLDEN_ROOT / "golden-easy.json"
    png_path = GOLDEN_ROOT / "golden-easy.png"
    artwork_bytes = artwork_path.read_bytes()
    artifact = ArtworkArtifact.from_dict(json.loads(artwork_bytes.decode("utf-8")))
    png_bytes = png_path.read_bytes()
    assert artifact.canonical_bytes() == artwork_bytes
    assert encode_logical_png(artifact.width, artifact.height, artifact.cells) == png_bytes
    decoded = decode_logical_png(png_bytes)
    assert (decoded.width, decoded.height, decoded.cells) == (artifact.width, artifact.height, artifact.cells)
    assert decoded.raw_rgb == logical_rgb_bytes(artifact.cells)
    assert decoded.palette == artifact.palette
    assert (artifact.width, artifact.height) == (20, 20)
    assert len(artifact.palette) == 3


def test_committed_m08_rectangular_pair_proves_row_boundaries_and_rgb_truth() -> None:
    artwork_path = GOLDEN_ROOT / "golden-rectangular.json"
    png_path = GOLDEN_ROOT / "golden-rectangular.png"
    artwork_bytes = artwork_path.read_bytes()
    artifact = ArtworkArtifact.from_dict(json.loads(artwork_bytes.decode("utf-8")))
    png_bytes = png_path.read_bytes()
    assert artifact.canonical_bytes() == artwork_bytes
    assert artifact.width == 20 and artifact.height == 21 and artifact.width != artifact.height
    assert artifact.palette == ("C01", "C02", "C03")
    assert encode_logical_png(artifact.width, artifact.height, artifact.cells) == png_bytes
    decoded = decode_logical_png(png_bytes)
    assert (decoded.width, decoded.height, decoded.cells) == (artifact.width, artifact.height, artifact.cells)
    assert decoded.raw_rgb == logical_rgb_bytes(artifact.cells)
    assert artifact.cells[0] == "C01"  # (0, 0)
    assert artifact.cells[artifact.width - 1] == "C01"  # (width-1, 0)
    assert artifact.cells[artifact.width] == "C02"  # (0, 1)
    assert artifact.cells[2 * artifact.width + 7] == "C03"  # (7, 2)
