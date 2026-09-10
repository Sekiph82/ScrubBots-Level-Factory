from __future__ import annotations

import struct
import zlib

import pytest

from scrubbots_pixel_factory.output import (
    ArtworkArtifact,
    ArtworkContractError,
    PNGContractError,
    decode_logical_png,
    encode_logical_png,
    encode_preview_png,
    logical_rgb_bytes,
)
from scrubbots_pixel_factory.core import FailureCode, GenerationResult


def _cells(width: int = 20, height: int = 20) -> list[str]:
    return ["C01" if x in {0, width - 1} or y in {0, height - 1} else ("C02" if x < width // 2 else "C03") for y in range(height) for x in range(width)]


def _rectangular_cells(width: int = 20, height: int = 21) -> list[str]:
    return [
        "C01" if y == 0 else ("C02" if y == 1 or (x + y) % 3 else "C03")
        for y in range(height)
        for x in range(width)
    ]


def test_artwork_json_contract_and_rectangular_row_major_index() -> None:
    width, height = 20, 21
    cells = _rectangular_cells(width, height)
    artifact = ArtworkArtifact.from_cells("rectangular", "EASY", width, height, cells)
    raw = artifact.as_dict()
    assert raw["index_rule"] == "index = y * width + x"
    assert artifact.width != artifact.height
    assert raw["cells"][0] == cells[0] == "C01"  # (0, 0)
    assert raw["cells"][width - 1] == cells[width - 1] == "C01"  # (width-1, 0)
    assert raw["cells"][width] == cells[width] == "C02"  # (0, 1)
    later_index = 2 * width + 7
    assert raw["cells"][later_index] == cells[later_index] == "C03"  # (7, 2)
    assert len(raw["cells"]) == width * height
    assert artifact.canonical_bytes() == artifact.canonical_bytes()
    assert "quality" not in raw
    with pytest.raises(ArtworkContractError):
        ArtworkArtifact.from_cells("../escape", "EASY", 20, 20, _cells())


def test_logical_png_is_exact_rgb_and_one_pixel_per_cell() -> None:
    width, height = 20, 20
    cells = tuple(_cells(width, height))
    encoded = encode_logical_png(width, height, cells)
    assert encoded[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", encoded[16:24]) == (width, height)
    decoded = decode_logical_png(encoded)
    assert decoded.cells == cells
    assert decoded.raw_rgb == logical_rgb_bytes(cells)
    assert decoded.palette == ("C01", "C02", "C03")


def test_png_corruption_and_off_palette_fail_closed() -> None:
    encoded = bytearray(encode_logical_png(20, 20, _cells()))
    encoded[-1] ^= 1
    with pytest.raises(PNGContractError):
        decode_logical_png(bytes(encoded))

    raw = bytearray(encode_logical_png(20, 20, _cells()))
    idat_start = raw.index(b"IDAT")
    idat_length = struct.unpack(">I", raw[idat_start - 4 : idat_start])[0]
    compressed_start = idat_start + 4
    compressed_end = compressed_start + idat_length
    scanlines = bytearray(zlib.decompress(raw[compressed_start:compressed_end]))
    scanlines[1:4] = bytes((1, 2, 3))
    replacement = zlib.compress(bytes(scanlines), level=9)
    rebuilt = bytes(raw[: idat_start - 4]) + struct.pack(">I", len(replacement)) + b"IDAT" + replacement + struct.pack(">I", zlib.crc32(b"IDAT" + replacement) & 0xFFFFFFFF) + bytes(raw[compressed_end + 4 :])
    with pytest.raises(PNGContractError):
        decode_logical_png(rebuilt)

    with pytest.raises(PNGContractError):
        encode_preview_png(20, 20, _cells(), 0)
    with pytest.raises(PNGContractError):
        decode_logical_png(encode_logical_png(20, 20, _cells())[:-5])


def test_png_rejects_non_empty_iend_payload_even_with_valid_crc() -> None:
    encoded = encode_logical_png(20, 20, _cells())
    payload = b"x"
    iend = struct.pack(">I", len(payload)) + b"IEND" + payload + struct.pack(">I", zlib.crc32(b"IEND" + payload) & 0xFFFFFFFF)
    malformed = encoded[:-12] + iend
    with pytest.raises(PNGContractError):
        decode_logical_png(malformed)


def test_artwork_and_png_reject_tampered_schema_palette_hash_and_failed_result() -> None:
    artifact = ArtworkArtifact.from_cells("negative", "EASY", 20, 20, _cells())
    raw = artifact.as_dict()
    for key, value in (("schema_version", 99), ("grid_hash", "0" * 64), ("palette", ["C03", "C02", "C01"])):
        tampered = dict(raw)
        tampered[key] = value
        with pytest.raises(ArtworkContractError):
            ArtworkArtifact.from_dict(tampered)
    failed = GenerationResult.failure(code=FailureCode.GENERATION_FAILED, reason="test failure")
    from scrubbots_pixel_factory.output import build_export_bundle, OutputContractError

    with pytest.raises(OutputContractError):
        build_export_bundle(failed, "failed")
    with pytest.raises(PNGContractError):
        encode_logical_png(20, 20, ["BG01"] * 400)
