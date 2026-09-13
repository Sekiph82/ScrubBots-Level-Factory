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


def _png(width: int, height: int, pixels: bytes, ancillary: tuple[tuple[bytes, bytes], ...] = ()) -> bytes:
    assert len(pixels) == width * height * 4
    rows = b"".join(b"\x00" + pixels[row * width * 4 : (row + 1) * width * 4] for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return PNG_SIGNATURE + _chunk(b"IHDR", header) + b"".join(_chunk(kind, payload) for kind, payload in ancillary) + _chunk(b"IDAT", zlib.compress(rows, 9)) + _chunk(b"IEND", b"")


def _normalization(artifact: SemanticRawArtifact):
    return normalize_semantic_artifact(artifact, SemanticNormalizationRequest(artifact.digest(), "ASSET_ART", 24, 24))


def test_live_shape_ancillary_chunks_preserve_pixels_raw_identity_and_normalization(tmp_path: Path) -> None:
    pixels = bytes((index * 37 + 11) % 256 for index in range(2 * 2 * 4))
    baseline = _png(2, 2, pixels)
    ancillary = _png(2, 2, pixels, ((b"caBX", b"synthetic-caBX-payload"), (b"fdEC", b"shape")))

    baseline_decoded = _decode_png_rgba(baseline)
    ancillary_decoded = _decode_png_rgba(ancillary)
    assert (baseline_decoded.width, baseline_decoded.height, baseline_decoded.pixels) == (2, 2, pixels)
    assert (ancillary_decoded.width, ancillary_decoded.height, ancillary_decoded.pixels) == (2, 2, pixels)
    assert baseline_decoded.pixels == ancillary_decoded.pixels
    assert hashlib.sha256(baseline).hexdigest() != hashlib.sha256(ancillary).hexdigest()

    baseline_path = tmp_path / "baseline.png"
    ancillary_path = tmp_path / "ancillary.png"
    baseline_path.write_bytes(baseline)
    ancillary_path.write_bytes(ancillary)
    baseline_raw = SemanticRawArtifact.from_local_file(baseline_path)
    ancillary_raw = SemanticRawArtifact.from_local_file(ancillary_path)
    assert baseline_raw.raw_sha256 != ancillary_raw.raw_sha256
    assert baseline_raw.digest() != ancillary_raw.digest()

    baseline_normalized = _normalization(baseline_raw)
    ancillary_normalized = _normalization(ancillary_raw)
    assert baseline_normalized.rgba8 == ancillary_normalized.rgba8
    assert baseline_normalized.normalized_rgba_sha256 == ancillary_normalized.normalized_rgba_sha256
    assert baseline_normalized.source_raw_artifact_digest != ancillary_normalized.source_raw_artifact_digest
    assert baseline_normalized.source_provenance.raw_sha256 != ancillary_normalized.source_provenance.raw_sha256


def test_unknown_critical_chunk_remains_fail_closed() -> None:
    pixels = bytes((10, 20, 30, 255)) * 4
    encoded = _png(2, 2, pixels[: 2 * 2 * 4], ((b"ABCD", b"unsupported-critical"),))
    with pytest.raises(SemanticDecodeError, match="unsupported critical"):
        _decode_png_rgba(encoded)


def test_ignored_ancillary_chunk_crc_is_still_mandatory() -> None:
    pixels = bytes((10, 20, 30, 255)) * 4
    valid = _chunk(b"caBX", b"synthetic-payload")
    corrupt = bytearray(valid)
    corrupt[-1] ^= 1
    encoded = _png(2, 2, pixels, ())
    ihdr_end = len(PNG_SIGNATURE) + len(_chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 6, 0, 0, 0)))
    encoded = encoded[:ihdr_end] + bytes(corrupt) + encoded[ihdr_end:]
    with pytest.raises(SemanticDecodeError, match="CRC"):
        _decode_png_rgba(encoded)


def test_malformed_chunk_type_is_rejected() -> None:
    pixels = bytes((10, 20, 30, 255)) * 4
    encoded = _png(2, 2, pixels, ((b"caB1", b"malformed-type"),))
    with pytest.raises(SemanticDecodeError, match="type code"):
        _decode_png_rgba(encoded)


def test_truncated_ancillary_chunk_is_rejected() -> None:
    pixels = bytes((10, 20, 30, 255)) * 4
    baseline = _png(2, 2, pixels)
    ancillary = _chunk(b"caBX", b"truncated-payload")
    ihdr_end = len(PNG_SIGNATURE) + len(_chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 6, 0, 0, 0)))
    encoded = baseline[:ihdr_end] + ancillary[:-1] + baseline[ihdr_end:]
    with pytest.raises(SemanticDecodeError):
        _decode_png_rgba(encoded)
