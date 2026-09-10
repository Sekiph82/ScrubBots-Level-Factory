"""Small deterministic standard-library PNG codec for logical SCRUBBOTS art."""

from __future__ import annotations

from dataclasses import dataclass
import struct
import zlib
from collections.abc import Iterable

from ..contracts import CANONICAL_PALETTE
from .artwork import ArtworkContractError


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_MAX_LOGICAL_DIMENSION = 59
_MAX_DECODE_DIMENSION = 4096


class PNGContractError(ValueError):
    """Raised when a project-profile PNG is malformed or unsupported."""


@dataclass(frozen=True, slots=True)
class DecodedPNG:
    width: int
    height: int
    cells: tuple[str, ...]
    raw_rgb: bytes

    @property
    def palette(self) -> tuple[str, ...]:
        return CANONICAL_PALETTE.used_ids(self.cells)


def logical_rgb_bytes(cells: Iterable[str]) -> bytes:
    """Return exact row-major R,G,B bytes for canonical logical cells."""

    try:
        return b"".join(bytes(CANONICAL_PALETTE.rgb_for(cell)) for cell in cells)
    except (TypeError, ValueError, ArtworkContractError) as exc:
        raise PNGContractError("logical cells must map exactly to canonical C01..C16 RGB values") from exc


def _validate_dimensions(width: object, height: object, maximum: int) -> tuple[int, int]:
    if type(width) is not int or type(height) is not int or width < 1 or height < 1 or width > maximum or height > maximum:
        raise PNGContractError(f"PNG dimensions must be positive integers no larger than {maximum}")
    return width, height


def _chunk(kind: bytes, data: bytes) -> bytes:
    if len(kind) != 4:
        raise PNGContractError("PNG chunk type must be four bytes")
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def _encode_rgb_png(width: int, height: int, raw_rgb: bytes) -> bytes:
    if len(raw_rgb) != width * height * 3:
        raise PNGContractError("raw RGB length does not equal width*height*3")
    scanlines = b"".join(b"\x00" + raw_rgb[row * width * 3 : (row + 1) * width * 3] for row in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    compressed = zlib.compress(scanlines, level=9)
    return PNG_SIGNATURE + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", compressed) + _chunk(b"IEND", b"")


def encode_logical_png(width: int, height: int, cells: Iterable[str]) -> bytes:
    """Encode one flat canonical RGB pixel per logical cell, with no scaling."""

    width, height = _validate_dimensions(width, height, _MAX_LOGICAL_DIMENSION)
    normalized = tuple(cells)
    if len(normalized) != width * height:
        raise PNGContractError("logical cell count does not equal PNG dimensions")
    return _encode_rgb_png(width, height, logical_rgb_bytes(normalized))


def encode_preview_png(width: int, height: int, cells: Iterable[str], scale: int) -> bytes:
    """Encode an optional exact integer nearest-neighbor presentation preview."""

    width, height = _validate_dimensions(width, height, _MAX_LOGICAL_DIMENSION)
    if type(scale) is not int or scale < 1 or scale > 64:
        raise PNGContractError("preview scale must be an integer from 1 through 64")
    normalized = tuple(cells)
    if len(normalized) != width * height:
        raise PNGContractError("logical cell count does not equal preview source dimensions")
    scaled_width, scaled_height = width * scale, height * scale
    if scaled_width > _MAX_DECODE_DIMENSION or scaled_height > _MAX_DECODE_DIMENSION:
        raise PNGContractError("preview dimensions exceed the supported bound")
    source = logical_rgb_bytes(normalized)
    rows: list[bytes] = []
    source_row_bytes = width * 3
    for row in range(height):
        source_row = source[row * source_row_bytes : (row + 1) * source_row_bytes]
        expanded_row = b"".join(source_row[index * 3 : index * 3 + 3] * scale for index in range(width))
        rows.extend([expanded_row] * scale)
    scanlines = b"".join(b"\x00" + row for row in rows)
    ihdr = struct.pack(">IIBBBBB", scaled_width, scaled_height, 8, 2, 0, 0, 0)
    return PNG_SIGNATURE + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(scanlines, level=9)) + _chunk(b"IEND", b"")


def _parse_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    if not isinstance(data, (bytes, bytearray)) or bytes(data[:8]) != PNG_SIGNATURE:
        raise PNGContractError("PNG signature is invalid")
    payload = bytes(data)
    position = len(PNG_SIGNATURE)
    chunks: list[tuple[bytes, bytes]] = []
    while position < len(payload):
        if len(payload) - position < 12:
            raise PNGContractError("PNG chunk header or CRC is truncated")
        length = struct.unpack(">I", payload[position : position + 4])[0]
        position += 4
        kind = payload[position : position + 4]
        position += 4
        if len(kind) != 4 or len(payload) - position < length + 4:
            raise PNGContractError("PNG chunk length exceeds available bytes")
        chunk_data = payload[position : position + length]
        position += length
        expected_crc = struct.unpack(">I", payload[position : position + 4])[0]
        position += 4
        if zlib.crc32(kind + chunk_data) & 0xFFFFFFFF != expected_crc:
            raise PNGContractError("PNG chunk CRC is invalid")
        chunks.append((kind, chunk_data))
    if not chunks or chunks[0][0] != b"IHDR" or chunks[-1][0] != b"IEND":
        raise PNGContractError("PNG must begin with IHDR and end with IEND")
    if any(kind not in {b"IHDR", b"IDAT", b"IEND"} for kind, _ in chunks):
        raise PNGContractError("PNG contains an unsupported chunk")
    if sum(kind == b"IHDR" for kind, _ in chunks) != 1 or sum(kind == b"IEND" for kind, _ in chunks) != 1:
        raise PNGContractError("PNG must contain exactly one IHDR and IEND")
    if not any(kind == b"IDAT" for kind, _ in chunks):
        raise PNGContractError("PNG must contain IDAT data")
    return chunks


def decode_png(data: bytes, *, max_dimension: int = _MAX_LOGICAL_DIMENSION) -> DecodedPNG:
    """Decode only the project's 8-bit RGB, non-interlaced, filter-0 profile."""

    chunks = _parse_chunks(data)
    ihdr = chunks[0][1]
    if len(ihdr) != 13:
        raise PNGContractError("PNG IHDR length is invalid")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", ihdr)
    width, height = _validate_dimensions(width, height, max_dimension)
    if (bit_depth, color_type, compression, filter_method, interlace) != (8, 2, 0, 0, 0):
        raise PNGContractError("PNG must be 8-bit RGB, non-interlaced, with standard compression/filter methods")
    compressed = b"".join(chunk for kind, chunk in chunks if kind == b"IDAT")
    expected_length = height * (1 + width * 3)
    decompressor = zlib.decompressobj()
    try:
        raw = decompressor.decompress(compressed, expected_length + 1)
        raw += decompressor.flush()
    except zlib.error as exc:
        raise PNGContractError("PNG IDAT stream is not valid zlib data") from exc
    if not decompressor.eof or decompressor.unused_data or len(raw) != expected_length:
        raise PNGContractError("PNG decompressed scanline length or stream termination is invalid")
    rgb = bytearray()
    cells: list[str] = []
    cursor = 0
    for _row in range(height):
        if raw[cursor] != 0:
            raise PNGContractError("PNG uses an unsupported non-zero scanline filter")
        cursor += 1
        row = raw[cursor : cursor + width * 3]
        cursor += width * 3
        rgb.extend(row)
        for pixel in range(width):
            triplet = row[pixel * 3 : pixel * 3 + 3]
            try:
                cells.append(CANONICAL_PALETTE.id_for_rgb(tuple(triplet)))
            except (TypeError, ValueError) as exc:
                raise PNGContractError("PNG RGB does not map exactly to a canonical logical C-ID") from exc
    return DecodedPNG(width, height, tuple(cells), bytes(rgb))


def decode_logical_png(data: bytes) -> DecodedPNG:
    return decode_png(data, max_dimension=_MAX_LOGICAL_DIMENSION)


__all__ = [
    "DecodedPNG",
    "PNGContractError",
    "PNG_SIGNATURE",
    "decode_logical_png",
    "decode_png",
    "encode_logical_png",
    "encode_preview_png",
    "logical_rgb_bytes",
]
