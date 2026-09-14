from __future__ import annotations

import hashlib
from pathlib import Path
import struct
import zlib

import pytest

from scrubbots_pixel_factory import SemanticDecodeError, SemanticRawArtifact, SemanticNormalizationRequest, normalize_semantic_artifact
from scrubbots_pixel_factory.semantic.normalization.core import _decode_png_rgba


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, payload: bytes, *, crc: int | None = None) -> bytes:
    if crc is None:
        crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def _png(
    width: int,
    height: int,
    pixels: bytes,
    *,
    before_idat: tuple[tuple[bytes, bytes], ...] = (),
    after_idat: tuple[tuple[bytes, bytes], ...] = (),
    idat_parts: tuple[bytes, ...] | None = None,
) -> bytes:
    assert len(pixels) == width * height * 4
    rows = b"".join(b"\x00" + pixels[row * width * 4 : (row + 1) * width * 4] for row in range(height))
    compressed = zlib.compress(rows, 9)
    if idat_parts is None:
        idat_parts = (compressed,)
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        PNG_SIGNATURE
        + _chunk(b"IHDR", header)
        + b"".join(_chunk(kind, payload) for kind, payload in before_idat)
        + b"".join(_chunk(b"IDAT", part) for part in idat_parts)
        + b"".join(_chunk(kind, payload) for kind, payload in after_idat)
        + _chunk(b"IEND", b"")
    )


def _png_with_raw_chunks(width: int, height: int, pixels: bytes, middle: bytes) -> bytes:
    rows = b"".join(b"\x00" + pixels[row * width * 4 : (row + 1) * width * 4] for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return PNG_SIGNATURE + _chunk(b"IHDR", header) + middle + _chunk(b"IDAT", zlib.compress(rows, 9)) + _chunk(b"IEND", b"")


def test_single_and_consecutive_idat_chunks_decode_identically() -> None:
    pixels = bytes((index * 19 + 7) % 256 for index in range(4 * 3 * 4))
    baseline = _png(4, 3, pixels)
    compressed = zlib.compress(b"".join(b"\x00" + pixels[row * 4 * 4 : (row + 1) * 4 * 4] for row in range(3)), 9)
    split = _png(4, 3, pixels, idat_parts=(compressed[:3], compressed[3:]))
    assert _decode_png_rgba(baseline).pixels == pixels
    assert _decode_png_rgba(split).pixels == pixels
    assert _decode_png_rgba(split).pixels == _decode_png_rgba(baseline).pixels


def test_live_shape_and_legal_post_idat_ancillary_chunks_remain_accepted() -> None:
    pixels = bytes((index * 23 + 5) % 256 for index in range(3 * 2 * 4))
    live_shape = _png(3, 2, pixels, before_idat=((b"caBX", b"synthetic-caBX"), (b"fdEC", b"shape")))
    post_idat = _png(3, 2, pixels, after_idat=((b"tEXt", b"post-idat"),))
    assert _decode_png_rgba(live_shape).pixels == pixels
    assert _decode_png_rgba(post_idat).pixels == pixels


@pytest.mark.parametrize("ancillary_type", [b"caBX", b"tEXt"])
def test_any_ancillary_chunk_between_idat_chunks_is_rejected(ancillary_type: bytes) -> None:
    pixels = bytes((10, 20, 30, 255)) * 4
    compressed = zlib.compress(b"\x00" + pixels, 9)
    middle = _chunk(b"IDAT", compressed[:3]) + _chunk(ancillary_type, b"interleaving") + _chunk(b"IDAT", compressed[3:])
    header = struct.pack(">IIBBBBB", 2, 2, 8, 6, 0, 0, 0)
    encoded = PNG_SIGNATURE + _chunk(b"IHDR", header) + middle + _chunk(b"IEND", b"")
    with pytest.raises(SemanticDecodeError, match="contiguous"):
        _decode_png_rgba(encoded)


def test_unknown_critical_chunk_crc_and_type_safety_remain_fail_closed() -> None:
    pixels = bytes((10, 20, 30, 255)) * 4
    with pytest.raises(SemanticDecodeError, match="unsupported critical"):
        _decode_png_rgba(_png(2, 2, pixels, before_idat=((b"ABCD", b"critical"),)))

    valid_ancillary = _chunk(b"caBX", b"crc")
    corrupt_ancillary = bytearray(valid_ancillary)
    corrupt_ancillary[-1] ^= 1
    with pytest.raises(SemanticDecodeError, match="CRC"):
        _decode_png_rgba(_png_with_raw_chunks(2, 2, pixels, bytes(corrupt_ancillary)))

    with pytest.raises(SemanticDecodeError, match="type code"):
        _decode_png_rgba(_png(2, 2, pixels, before_idat=((b"caB1", b"malformed"),)))
    with pytest.raises(SemanticDecodeError, match="reserved bit"):
        _decode_png_rgba(_png(2, 2, pixels, before_idat=((b"caxX", b"reserved"),)))


def test_raw_provenance_and_normalized_pixels_remain_byte_sensitive(tmp_path: Path) -> None:
    pixels = bytes((index * 31 + 3) % 256 for index in range(2 * 2 * 4))
    baseline_path = tmp_path / "baseline.png"
    ancillary_path = tmp_path / "ancillary.png"
    baseline_path.write_bytes(_png(2, 2, pixels))
    ancillary_path.write_bytes(_png(2, 2, pixels, before_idat=((b"caBX", b"provenance"),)))
    baseline_raw = SemanticRawArtifact.from_local_file(baseline_path)
    ancillary_raw = SemanticRawArtifact.from_local_file(ancillary_path)
    baseline_normalized = normalize_semantic_artifact(baseline_raw, SemanticNormalizationRequest(baseline_raw.digest(), "ASSET_ART", 24, 24))
    ancillary_normalized = normalize_semantic_artifact(ancillary_raw, SemanticNormalizationRequest(ancillary_raw.digest(), "ASSET_ART", 24, 24))
    assert baseline_raw.raw_sha256 != ancillary_raw.raw_sha256
    assert baseline_normalized.rgba8 == ancillary_normalized.rgba8
    assert baseline_normalized.normalized_rgba_sha256 == ancillary_normalized.normalized_rgba_sha256
    assert baseline_normalized.source_raw_artifact_digest != ancillary_normalized.source_raw_artifact_digest
    assert hashlib.sha256(baseline_path.read_bytes()).hexdigest() == baseline_raw.raw_sha256
