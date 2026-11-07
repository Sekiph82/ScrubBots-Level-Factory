from __future__ import annotations

import struct
import zlib

import pytest

from scrubbots_pixel_factory import SemanticDecodeError
from scrubbots_pixel_factory.semantic.normalization.core import _decode_png_rgba


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def _indexed_png(width: int, height: int, bit_depth: int, indices: list[int], palette: bytes, alpha: bytes = b"") -> bytes:
    assert len(indices) == width * height
    mask = (1 << bit_depth) - 1
    rows = bytearray()
    for y in range(height):
        packed = bytearray((width * bit_depth + 7) // 8)
        for x in range(width):
            value = indices[y * width + x]
            assert value <= mask
            bit_offset = x * bit_depth
            packed[bit_offset // 8] |= value << (8 - bit_depth - (bit_offset % 8))
        rows.extend(b"\x00" + packed)
    header = struct.pack(">IIBBBBB", width, height, bit_depth, 3, 0, 0, 0)
    chunks = [_chunk(b"IHDR", header), _chunk(b"PLTE", palette)]
    if alpha:
        chunks.append(_chunk(b"tRNS", alpha))
    chunks.extend((_chunk(b"IDAT", zlib.compress(bytes(rows))), _chunk(b"IEND", b"")))
    return PNG_SIGNATURE + b"".join(chunks)


@pytest.mark.parametrize("bit_depth", [1, 2, 4, 8])
def test_indexed_png_unpacks_palette_indices_and_preserves_alpha(bit_depth: int) -> None:
    entries = min(1 << bit_depth, 4)
    palette = bytes(channel for index in range(entries) for channel in (index * 50, 255 - index * 40, index * 20))
    indices = [index % entries for index in range(7 * 2)]
    alpha = bytes((0, 96, 255)[:entries])
    decoded = _decode_png_rgba(_indexed_png(7, 2, bit_depth, indices, palette, alpha))
    expected = bytes(
        channel
        for index in indices
        for channel in (
            index * 50,
            255 - index * 40,
            index * 20,
            alpha[index] if index < len(alpha) else 255,
        )
    )
    assert (decoded.width, decoded.height, decoded.pixels) == (7, 2, expected)


def test_indexed_png_rejects_missing_palette_entries_and_invalid_transparency() -> None:
    palette = bytes((10, 20, 30))
    with pytest.raises(SemanticDecodeError, match="absent PLTE"):
        _decode_png_rgba(_indexed_png(1, 1, 2, [1], palette))
    with pytest.raises(SemanticDecodeError, match="exceeds the PLTE"):
        _decode_png_rgba(_indexed_png(1, 1, 2, [0], palette, b"\x00\xff"))


def test_indexed_png_requires_palette_before_image_data() -> None:
    header = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 4, 3, 0, 0, 0))
    compressed = _chunk(b"IDAT", zlib.compress(b"\x00\x00"))
    palette = _chunk(b"PLTE", bytes((10, 20, 30)))
    encoded = PNG_SIGNATURE + header + compressed + palette + _chunk(b"IEND", b"")
    with pytest.raises(SemanticDecodeError, match="PLTE must precede IDAT"):
        _decode_png_rgba(encoded)
