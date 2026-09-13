"""Deterministic local normalization of raw semantic provider rasters.

C001 deliberately supports only the project's strict 8-bit, non-interlaced
PNG profile.  This keeps the runtime dependency-free and makes decoding,
alpha handling, and area resampling explicit and reproducible.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
import base64
import hashlib
import json
from pathlib import Path
import struct
import zlib
from types import MappingProxyType

from ..contracts import (
    CandidateStatus,
    ImageInputDescriptor,
    OutputClass,
    SEMANTIC_RAW_RASTER_MAX_DIMENSION,
    SemanticContractError,
    SemanticGenerationRequest,
    SemanticImageCandidate,
    SemanticNormalizationRequiredError,
)


NORMALIZATION_SCHEMA = "scrubbots-semantic-normalization"
NORMALIZATION_SCHEMA_VERSION = 1
NORMALIZATION_POLICY_VERSION = "semantic-normalization-v1"
NORMALIZATION_REPORT_SCHEMA = "scrubbots-semantic-normalization-report"
NORMALIZATION_REPORT_VERSION = 1
RAW_ARTIFACT_SCHEMA = "scrubbots-semantic-raw-artifact"
RAW_ARTIFACT_SCHEMA_VERSION = 1
RAW_ARTIFACT_MAX_BYTES = 128 * 1024 * 1024
MAX_DECODE_PIXELS = 16_777_216
SUPPORTED_MEDIA_TYPE = "image/png"
SUPPORTED_RESIZE_POLICY = "AREA_AVERAGE_V1"
SUPPORTED_CROP_PAD_POLICY = "FIT_CENTER_LETTERBOX_V1"
ALPHA_POLICIES = frozenset({"PRESERVE_ALPHA", "OPAQUE_AS_IS"})
ASSET_PALETTE_POLICY = "PRESERVE_SOURCE_RGBA"
FUTURE_LEVEL_PALETTE_POLICY = "SCRUBBOTS_C01_C16"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_SOURCE_PROVENANCE_CONSTRUCTION_TOKEN = object()
_NORMALIZED_ARTIFACT_CONSTRUCTION_TOKEN = object()


class SemanticNormalizationError(SemanticContractError):
    """Raised when raw semantic bytes or a normalization contract is invalid."""


class SemanticDecodeError(SemanticNormalizationError):
    """Raised when the supported local image profile cannot be decoded."""


class NormalizationStatus(str, Enum):
    SUCCESS = "SUCCESS"


def _canonical_bytes(value: object) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SemanticNormalizationError("normalization value is not canonical JSON") from exc


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_text(value: object, label: str) -> str:
    if type(value) is not str or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise SemanticNormalizationError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _digest(value: object) -> str:
    return _sha256(_canonical_bytes(value))


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise SemanticNormalizationError(f"{label} must be a non-empty string")
    return value.strip()


def _dimension(value: object, label: str, maximum: int = 1024) -> int:
    if type(value) is not int or value < 1 or value > maximum:
        raise SemanticNormalizationError(f"{label} must be an integer from 1 through {maximum}")
    return value


def _typed_seed(seed: int | str) -> dict[str, int | str]:
    return {"type": "int", "value": seed} if isinstance(seed, int) else {"type": "string", "value": seed}


@dataclass(frozen=True, slots=True)
class _DecodedRGBA:
    width: int
    height: int
    pixels: bytes


def _paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    left_distance = abs(estimate - left)
    up_distance = abs(estimate - up)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= up_distance and left_distance <= upper_left_distance:
        return left
    if up_distance <= upper_left_distance:
        return up
    return upper_left


def _png_chunks(raw: bytes) -> list[tuple[bytes, bytes]]:
    if not isinstance(raw, bytes) or len(raw) < len(PNG_SIGNATURE) or raw[:8] != PNG_SIGNATURE:
        raise SemanticDecodeError("raw image is not a PNG")
    position = len(PNG_SIGNATURE)
    chunks: list[tuple[bytes, bytes]] = []
    while position < len(raw):
        if len(raw) - position < 12:
            raise SemanticDecodeError("PNG chunk header or CRC is truncated")
        length = struct.unpack(">I", raw[position : position + 4])[0]
        position += 4
        kind = raw[position : position + 4]
        position += 4
        if len(kind) != 4 or any(byte < ord("A") or (ord("Z") < byte < ord("a")) or byte > ord("z") for byte in kind):
            raise SemanticDecodeError("PNG chunk type code is malformed")
        if kind[2] not in range(ord("A"), ord("Z") + 1):
            raise SemanticDecodeError("PNG chunk type reserved bit is invalid")
        if length > len(raw) - position - 4:
            raise SemanticDecodeError("PNG chunk length exceeds available bytes")
        chunk_data = raw[position : position + length]
        position += length
        expected_crc = struct.unpack(">I", raw[position : position + 4])[0]
        position += 4
        if zlib.crc32(kind + chunk_data) & 0xFFFFFFFF != expected_crc:
            raise SemanticDecodeError("PNG chunk CRC is invalid")
        chunks.append((kind, chunk_data))
    if not chunks or chunks[0][0] != b"IHDR" or chunks[-1][0] != b"IEND":
        raise SemanticDecodeError("PNG must begin with IHDR and end with IEND")
    if chunks[-1][1] != b"":
        raise SemanticDecodeError("PNG IEND payload must be empty")
    if any(kind not in {b"IHDR", b"IDAT", b"IEND"} and kind[0] in range(ord("A"), ord("Z") + 1) for kind, _data in chunks):
        raise SemanticDecodeError("PNG contains an unsupported critical chunk")
    if sum(kind == b"IHDR" for kind, _data in chunks) != 1 or sum(kind == b"IEND" for kind, _data in chunks) != 1:
        raise SemanticDecodeError("PNG must contain exactly one IHDR and IEND")
    if not any(kind == b"IDAT" for kind, _data in chunks):
        raise SemanticDecodeError("PNG must contain IDAT data")
    return chunks


def _decode_png_rgba(raw: bytes) -> _DecodedRGBA:
    chunks = _png_chunks(raw)
    header = chunks[0][1]
    if len(header) != 13:
        raise SemanticDecodeError("PNG IHDR length is invalid")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", header)
    if type(width) is not int or type(height) is not int or width < 1 or height < 1 or width > SEMANTIC_RAW_RASTER_MAX_DIMENSION or height > SEMANTIC_RAW_RASTER_MAX_DIMENSION:
        raise SemanticDecodeError("PNG dimensions exceed the semantic raw-raster bound")
    if width * height > MAX_DECODE_PIXELS:
        raise SemanticDecodeError("PNG exceeds the bounded normalization pixel budget")
    if (bit_depth, compression, filter_method, interlace) != (8, 0, 0, 0):
        raise SemanticDecodeError("PNG must be 8-bit, non-interlaced, with standard compression/filter methods")
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(color_type)
    if channels is None:
        raise SemanticDecodeError("C001 supports grayscale, RGB, grayscale-alpha, and RGBA PNG only")
    row_bytes = width * channels
    expected_length = height * (row_bytes + 1)
    compressed = b"".join(data for kind, data in chunks if kind == b"IDAT")
    decompressor = zlib.decompressobj()
    scanline_budget = expected_length + 1
    scanlines_buffer = bytearray()
    compressed_cursor = 0
    try:
        while compressed_cursor < len(compressed):
            chunk = compressed[compressed_cursor : compressed_cursor + 65_536]
            compressed_cursor += len(chunk)
            while chunk:
                remaining = scanline_budget - len(scanlines_buffer)
                if remaining <= 0:
                    raise SemanticDecodeError("PNG decompressed output exceeds exact budget")
                scanlines_buffer.extend(decompressor.decompress(chunk, remaining))
                if len(scanlines_buffer) > expected_length:
                    raise SemanticDecodeError("PNG decompressed output exceeds exact budget")
                chunk = decompressor.unconsumed_tail
            if decompressor.eof:
                if compressed_cursor != len(compressed) or decompressor.unused_data:
                    raise SemanticDecodeError("PNG IDAT stream contains trailing data")
                break
    except zlib.error as exc:
        raise SemanticDecodeError("PNG IDAT stream is invalid zlib data") from exc
    if not decompressor.eof or len(scanlines_buffer) != expected_length:
        raise SemanticDecodeError("PNG decompressed scanline length or stream termination is invalid")
    scanlines = bytes(scanlines_buffer)
    rows: list[bytes] = []
    cursor = 0
    previous = bytes(row_bytes)
    for _row in range(height):
        filter_type = scanlines[cursor]
        cursor += 1
        encoded = scanlines[cursor : cursor + row_bytes]
        cursor += row_bytes
        if len(encoded) != row_bytes:
            raise SemanticDecodeError("PNG scanline is truncated")
        reconstructed = bytearray(row_bytes)
        for index, value in enumerate(encoded):
            left = reconstructed[index - channels] if index >= channels else 0
            up = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 0:
                prediction = 0
            elif filter_type == 1:
                prediction = left
            elif filter_type == 2:
                prediction = up
            elif filter_type == 3:
                prediction = (left + up) // 2
            elif filter_type == 4:
                prediction = _paeth(left, up, upper_left)
            else:
                raise SemanticDecodeError("PNG uses an unsupported scanline filter")
            reconstructed[index] = (value + prediction) & 0xFF
        row = bytes(reconstructed)
        rows.append(row)
        previous = row
    rgba = bytearray()
    for row in rows:
        for index in range(width):
            pixel = row[index * channels : (index + 1) * channels]
            if color_type == 0:
                rgba.extend((pixel[0], pixel[0], pixel[0], 255))
            elif color_type == 2:
                rgba.extend((pixel[0], pixel[1], pixel[2], 255))
            elif color_type == 4:
                rgba.extend((pixel[0], pixel[0], pixel[0], pixel[1]))
            else:
                rgba.extend(pixel)
    return _DecodedRGBA(width, height, bytes(rgba))


def _apply_alpha(pixels: bytes, policy: str) -> bytes:
    if policy == "PRESERVE_ALPHA":
        return pixels
    if policy == "OPAQUE_AS_IS":
        opaque = bytearray(pixels)
        opaque[3::4] = b"\xff" * (len(opaque) // 4)
        return bytes(opaque)
    raise SemanticNormalizationError("unsupported alpha/background policy")


def _round_ratio(numerator: int, denominator: int) -> int:
    return (numerator + denominator // 2) // denominator


def _fit_dimensions(source_width: int, source_height: int, target_width: int, target_height: int) -> tuple[int, int]:
    if source_width * target_height >= target_width * source_height:
        scaled_width = target_width
        scaled_height = max(1, _round_ratio(source_height * target_width, source_width))
    else:
        scaled_height = target_height
        scaled_width = max(1, _round_ratio(source_width * target_height, source_height))
    return min(target_width, scaled_width), min(target_height, scaled_height)


def _area_resize(pixels: bytes, source_width: int, source_height: int, target_width: int, target_height: int) -> bytes:
    """Resize RGBA with exact integer box-area weights and half-up rounding."""
    if source_width == target_width and source_height == target_height:
        return bytes(pixels)
    output = bytearray(target_width * target_height * 4)
    denominator = source_width * source_height
    for y in range(target_height):
        y0 = y * source_height
        y1 = (y + 1) * source_height
        first_y = y0 // target_height
        last_y = (y1 - 1) // target_height
        for x in range(target_width):
            x0 = x * source_width
            x1 = (x + 1) * source_width
            first_x = x0 // target_width
            last_x = (x1 - 1) // target_width
            totals = [0, 0, 0, 0]
            for source_y in range(first_y, last_y + 1):
                y_weight = min(y1, (source_y + 1) * target_height) - max(y0, source_y * target_height)
                for source_x in range(first_x, last_x + 1):
                    x_weight = min(x1, (source_x + 1) * target_width) - max(x0, source_x * target_width)
                    weight = x_weight * y_weight
                    offset = (source_y * source_width + source_x) * 4
                    for channel in range(4):
                        totals[channel] += pixels[offset + channel] * weight
            output[(y * target_width + x) * 4 : (y * target_width + x + 1) * 4] = bytes(((_total + denominator // 2) // denominator for _total in totals))
    return bytes(output)


def _fit_center(pixels: bytes, source_width: int, source_height: int, target_width: int, target_height: int, alpha_policy: str) -> tuple[bytes, dict[str, int | str]]:
    scaled_width, scaled_height = _fit_dimensions(source_width, source_height, target_width, target_height)
    resized = _area_resize(pixels, source_width, source_height, scaled_width, scaled_height)
    background = (0, 0, 0, 0) if alpha_policy == "PRESERVE_ALPHA" else (0, 0, 0, 255)
    canvas = bytearray(background * (target_width * target_height))
    offset_x, offset_y = (target_width - scaled_width) // 2, (target_height - scaled_height) // 2
    for y in range(scaled_height):
        source_start = y * scaled_width * 4
        target_start = ((y + offset_y) * target_width + offset_x) * 4
        canvas[target_start : target_start + scaled_width * 4] = resized[source_start : source_start + scaled_width * 4]
    return bytes(canvas), {"operation": "FIT_CENTER_LETTERBOX", "scaled_width": scaled_width, "scaled_height": scaled_height, "offset_x": offset_x, "offset_y": offset_y}


@dataclass(frozen=True, slots=True)
class SemanticRawArtifact:
    """Immutable raw provider bytes and provenance before normalization."""

    raw_bytes: bytes = field(repr=False, compare=False)
    raw_sha256: str
    provider_candidate_digest: str
    provider_id: str
    provider_version: str
    workflow_version: str
    model_id: str | None
    request_digest: str
    requested_width: int
    requested_height: int
    returned_width: int
    returned_height: int
    media_type: str
    source_status: CandidateStatus | str
    reference_images: tuple[ImageInputDescriptor, ...] = ()
    style_image: ImageInputDescriptor | None = None
    init_image: ImageInputDescriptor | None = None
    color_reference: ImageInputDescriptor | None = None
    schema: str = RAW_ARTIFACT_SCHEMA
    schema_version: int = RAW_ARTIFACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.raw_bytes, bytes) or not self.raw_bytes or len(self.raw_bytes) > RAW_ARTIFACT_MAX_BYTES:
            raise SemanticNormalizationError("raw artifact bytes are empty or exceed the bounded input size")
        if self.raw_sha256 != _sha256(self.raw_bytes):
            raise SemanticNormalizationError("raw artifact SHA-256 does not match immutable bytes")
        _sha256_text(self.provider_candidate_digest, "provider_candidate_digest")
        for label, value in (("provider_id", self.provider_id), ("provider_version", self.provider_version), ("workflow_version", self.workflow_version), ("request_digest", self.request_digest), ("media_type", self.media_type)):
            _text(value, label)
        _dimension(self.requested_width, "requested_width", SEMANTIC_RAW_RASTER_MAX_DIMENSION)
        _dimension(self.requested_height, "requested_height", SEMANTIC_RAW_RASTER_MAX_DIMENSION)
        _dimension(self.returned_width, "returned_width", SEMANTIC_RAW_RASTER_MAX_DIMENSION)
        _dimension(self.returned_height, "returned_height", SEMANTIC_RAW_RASTER_MAX_DIMENSION)
        try:
            status = self.source_status if isinstance(self.source_status, CandidateStatus) else CandidateStatus(self.source_status)
        except (TypeError, ValueError) as exc:
            raise SemanticNormalizationError("raw artifact source status is invalid") from exc
        if status is not CandidateStatus.SUCCESS:
            raise SemanticNormalizationError("raw artifact source status must be SUCCESS")
        if not isinstance(self.reference_images, tuple) or any(not isinstance(item, ImageInputDescriptor) for item in self.reference_images):
            raise SemanticNormalizationError("raw artifact reference provenance is invalid")
        object.__setattr__(self, "source_status", status)
        object.__setattr__(self, "raw_bytes", bytes(self.raw_bytes))

    @classmethod
    def from_candidate(cls, candidate: SemanticImageCandidate, *, media_type: str = SUPPORTED_MEDIA_TYPE) -> "SemanticRawArtifact":
        if not isinstance(candidate, SemanticImageCandidate) or candidate.status is not CandidateStatus.SUCCESS:
            raise SemanticNormalizationError("raw artifact requires a successful SemanticImageCandidate")
        if candidate.image_bytes is None or candidate.returned_width is None or candidate.returned_height is None:
            raise SemanticNormalizationError("successful candidate lacks immutable raw bytes or dimensions")
        return cls(
            bytes(candidate.image_bytes), candidate.raw_image_sha256 or "", candidate.digest(), candidate.provider_id,
            candidate.provider_version, candidate.workflow_version, candidate.model_id, candidate.request_digest,
            candidate.requested_width, candidate.requested_height, candidate.returned_width, candidate.returned_height,
            _text(media_type, "media_type"), candidate.status, candidate.reference_images, candidate.style_image,
            candidate.init_image, candidate.color_reference,
        )

    @classmethod
    def from_local_file(cls, path: str | Path, *, media_type: str = SUPPORTED_MEDIA_TYPE) -> "SemanticRawArtifact":
        source = Path(path)
        if "\x00" in str(source) or "://" in str(source):
            raise SemanticNormalizationError("normalization input must be a local filesystem path")
        try:
            raw = source.read_bytes()
        except OSError as exc:
            raise SemanticNormalizationError(f"cannot read local normalization input: {exc}") from exc
        decoded = _decode_raw(raw, media_type)
        raw_hash = _sha256(raw)
        request_digest = _digest({"schema": "scrubbots-local-normalization-input", "raw_sha256": raw_hash, "width": decoded.width, "height": decoded.height})
        candidate_digest = _digest({"schema": "scrubbots-local-raw-candidate", "raw_sha256": raw_hash, "request_digest": request_digest})
        return cls(raw, raw_hash, candidate_digest, "LOCAL_FILE", "local-ingest-v1", "local-normalization-v1", None, request_digest, decoded.width, decoded.height, decoded.width, decoded.height, _text(media_type, "media_type"), CandidateStatus.SUCCESS)

    def identity_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema, "schema_version": self.schema_version, "raw_sha256": self.raw_sha256,
            "provider_candidate_digest": self.provider_candidate_digest,
            "provider": {"id": self.provider_id, "version": self.provider_version, "workflow_version": self.workflow_version, "model_id": self.model_id},
            "request_digest": self.request_digest,
            "requested_dimensions": {"width": self.requested_width, "height": self.requested_height},
            "returned_dimensions": {"width": self.returned_width, "height": self.returned_height},
            "media_type": self.media_type, "source_status": self.source_status.value,
            "reference_images": [item.canonical_dict() for item in self.reference_images],
            "style_image": self.style_image.canonical_dict() if self.style_image else None,
            "init_image": self.init_image.canonical_dict() if self.init_image else None,
            "color_reference": self.color_reference.canonical_dict() if self.color_reference else None,
        }

    @property
    def raw_image_sha256(self) -> str:
        return self.raw_sha256

    @property
    def candidate_digest(self) -> str:
        return self.provider_candidate_digest

    def canonical_dict(self) -> dict[str, object]:
        return self.identity_dict()

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _sha256(self.canonical_bytes())


def _decode_raw(raw: bytes, media_type: str) -> _DecodedRGBA:
    if media_type != SUPPORTED_MEDIA_TYPE:
        raise SemanticDecodeError("C001 supports only image/png; JPEG and WebP are not silently decoded")
    if len(raw) > RAW_ARTIFACT_MAX_BYTES:
        raise SemanticDecodeError("raw image exceeds the bounded input size")
    return _decode_png_rgba(raw)


@dataclass(frozen=True, slots=True)
class SemanticNormalizationRequest:
    """Immutable policy selecting one deterministic raw-to-normalized operation."""

    source_raw_artifact_digest: str
    output_class: OutputClass | str
    target_width: int
    target_height: int
    policy_version: str = NORMALIZATION_POLICY_VERSION
    alpha_policy: str = "PRESERVE_ALPHA"
    resize_policy: str = SUPPORTED_RESIZE_POLICY
    crop_pad_policy: str = SUPPORTED_CROP_PAD_POLICY
    palette_policy: str = ASSET_PALETTE_POLICY
    schema: str = NORMALIZATION_SCHEMA
    schema_version: int = NORMALIZATION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _sha256_text(self.source_raw_artifact_digest, "source_raw_artifact_digest")
        try:
            output_class = OutputClass.parse(self.output_class)
        except Exception as exc:
            raise SemanticNormalizationError("output_class is invalid") from exc
        if self.schema != NORMALIZATION_SCHEMA or self.schema_version != NORMALIZATION_SCHEMA_VERSION:
            raise SemanticNormalizationError("unsupported normalization schema/version")
        if self.policy_version != NORMALIZATION_POLICY_VERSION:
            raise SemanticNormalizationError("unsupported normalization policy version")
        _dimension(self.target_width, "target_width")
        _dimension(self.target_height, "target_height")
        if self.alpha_policy not in ALPHA_POLICIES:
            raise SemanticNormalizationError("unsupported alpha/background policy")
        if self.resize_policy != SUPPORTED_RESIZE_POLICY:
            raise SemanticNormalizationError("unsupported deterministic resize policy")
        if self.crop_pad_policy != SUPPORTED_CROP_PAD_POLICY:
            raise SemanticNormalizationError("unsupported deterministic crop/pad policy")
        if output_class is OutputClass.ASSET_ART and self.palette_policy != ASSET_PALETTE_POLICY:
            raise SemanticNormalizationError("ASSET_ART C001 requires PRESERVE_SOURCE_RGBA")
        if output_class is OutputClass.LEVEL_ART:
            raise SemanticNormalizationError("LEVEL_ART normalization requests are not legal until the canonical palette and difficulty policy is implemented")
        object.__setattr__(self, "output_class", output_class)

    @property
    def raw_artifact_digest(self) -> str:
        return self.source_raw_artifact_digest

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "schema_version": self.schema_version, "source_raw_artifact_digest": self.source_raw_artifact_digest, "output_class": self.output_class.value, "target_dimensions": {"width": self.target_width, "height": self.target_height}, "policy_version": self.policy_version, "alpha_policy": self.alpha_policy, "resize_policy": self.resize_policy, "crop_pad_policy": self.crop_pad_policy, "palette_policy": self.palette_policy}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _sha256(self.canonical_bytes())


@dataclass(frozen=True, slots=True)
class SemanticNormalizationReport:
    """Deterministic typed facts about one normalization operation."""

    source_raw_artifact_digest: str
    request_digest: str
    raw_width: int
    raw_height: int
    target_width: int
    target_height: int
    exact_size_fast_path: bool
    resize_applied: bool
    resampler: str
    crop_pad: Mapping[str, int | str]
    alpha_policy: str
    palette_policy: str
    input_raw_sha256: str
    output_rgba_sha256: str
    status: NormalizationStatus | str = NormalizationStatus.SUCCESS
    warnings: tuple[str, ...] = ()
    schema: str = NORMALIZATION_REPORT_SCHEMA
    schema_version: int = NORMALIZATION_REPORT_VERSION

    def __post_init__(self) -> None:
        if self.schema != NORMALIZATION_REPORT_SCHEMA or self.schema_version != NORMALIZATION_REPORT_VERSION:
            raise SemanticNormalizationError("unsupported normalization report schema/version")
        _sha256_text(self.source_raw_artifact_digest, "source_raw_artifact_digest")
        _sha256_text(self.request_digest, "request_digest")
        _sha256_text(self.input_raw_sha256, "input_raw_sha256")
        _sha256_text(self.output_rgba_sha256, "output_rgba_sha256")
        for label, value in (("raw_width", self.raw_width), ("raw_height", self.raw_height)):
            _dimension(value, label, SEMANTIC_RAW_RASTER_MAX_DIMENSION)
        for label, value in (("target_width", self.target_width), ("target_height", self.target_height)):
            _dimension(value, label)
        if self.alpha_policy not in ALPHA_POLICIES or self.palette_policy not in {ASSET_PALETTE_POLICY, FUTURE_LEVEL_PALETTE_POLICY}:
            raise SemanticNormalizationError("normalization report policy is invalid")
        if type(self.exact_size_fast_path) is not bool or type(self.resize_applied) is not bool:
            raise SemanticNormalizationError("normalization report booleans are invalid")
        status = self.status if isinstance(self.status, NormalizationStatus) else NormalizationStatus(self.status)
        if not isinstance(self.crop_pad, Mapping) or any(type(key) is not str for key in self.crop_pad):
            raise SemanticNormalizationError("normalization crop/pad report is invalid")
        frozen_crop_pad = {}
        for key, value in self.crop_pad.items():
            if type(value) not in {int, str}:
                raise SemanticNormalizationError("normalization crop/pad report values are invalid")
            frozen_crop_pad[key] = value
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "crop_pad", MappingProxyType(frozen_crop_pad))
        object.__setattr__(self, "warnings", tuple(self.warnings))

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "schema_version": self.schema_version, "source_raw_artifact_digest": self.source_raw_artifact_digest, "request_digest": self.request_digest, "raw_dimensions": {"width": self.raw_width, "height": self.raw_height}, "target_dimensions": {"width": self.target_width, "height": self.target_height}, "exact_size_fast_path": self.exact_size_fast_path, "resize_applied": self.resize_applied, "resampler": self.resampler, "crop_pad": dict(self.crop_pad), "alpha_policy": self.alpha_policy, "palette_policy": self.palette_policy, "input_raw_sha256": self.input_raw_sha256, "output_rgba_sha256": self.output_rgba_sha256, "status": self.status.value, "warnings": list(self.warnings)}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _sha256(self.canonical_bytes())


@dataclass(frozen=True, slots=True)
class SemanticSourceProvenance:
    """Exact immutable provider/source snapshot carried into normalization."""

    raw_artifact_digest: str
    raw_sha256: str
    provider_candidate_digest: str
    provider_id: str
    provider_version: str
    workflow_version: str
    model_id: str | None
    request_digest: str
    requested_width: int
    requested_height: int
    returned_width: int
    returned_height: int
    media_type: str
    source_status: CandidateStatus | str
    reference_images: tuple[ImageInputDescriptor, ...] = ()
    style_image: ImageInputDescriptor | None = None
    init_image: ImageInputDescriptor | None = None
    color_reference: ImageInputDescriptor | None = None
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    @classmethod
    def from_raw_artifact(cls, raw_artifact: SemanticRawArtifact) -> "SemanticSourceProvenance":
        if not isinstance(raw_artifact, SemanticRawArtifact):
            raise SemanticNormalizationError("source provenance requires a typed raw artifact")
        instance = object.__new__(cls)
        values = {
            "raw_artifact_digest": raw_artifact.digest(), "raw_sha256": raw_artifact.raw_sha256,
            "provider_candidate_digest": raw_artifact.provider_candidate_digest, "provider_id": raw_artifact.provider_id,
            "provider_version": raw_artifact.provider_version, "workflow_version": raw_artifact.workflow_version,
            "model_id": raw_artifact.model_id, "request_digest": raw_artifact.request_digest,
            "requested_width": raw_artifact.requested_width, "requested_height": raw_artifact.requested_height,
            "returned_width": raw_artifact.returned_width, "returned_height": raw_artifact.returned_height,
            "media_type": raw_artifact.media_type, "source_status": raw_artifact.source_status,
            "reference_images": raw_artifact.reference_images, "style_image": raw_artifact.style_image,
            "init_image": raw_artifact.init_image, "color_reference": raw_artifact.color_reference,
        }
        for name, value in values.items():
            object.__setattr__(instance, name, value)
        object.__setattr__(instance, "_construction_token", _SOURCE_PROVENANCE_CONSTRUCTION_TOKEN)
        instance.__post_init__()
        object.__setattr__(instance, "_construction_fingerprint", instance._compute_fingerprint())
        instance._assert_integrity()
        return instance

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _SOURCE_PROVENANCE_CONSTRUCTION_TOKEN:
            raise SemanticNormalizationError("source provenance requires checked construction from a raw artifact")
        _sha256_text(self.raw_artifact_digest, "raw_artifact_digest")
        _sha256_text(self.raw_sha256, "raw_sha256")
        _sha256_text(self.provider_candidate_digest, "provider_candidate_digest")
        _sha256_text(self.request_digest, "request_digest")
        for label, value in (("provider_id", self.provider_id), ("provider_version", self.provider_version), ("workflow_version", self.workflow_version), ("media_type", self.media_type)):
            _text(value, label)
        for label, value in (("requested_width", self.requested_width), ("requested_height", self.requested_height), ("returned_width", self.returned_width), ("returned_height", self.returned_height)):
            _dimension(value, label, SEMANTIC_RAW_RASTER_MAX_DIMENSION)
        try:
            status = self.source_status if isinstance(self.source_status, CandidateStatus) else CandidateStatus(self.source_status)
        except (TypeError, ValueError) as exc:
            raise SemanticNormalizationError("source provenance status is invalid") from exc
        if status is not CandidateStatus.SUCCESS:
            raise SemanticNormalizationError("source provenance status must be SUCCESS")
        if not isinstance(self.reference_images, tuple) or any(not isinstance(item, ImageInputDescriptor) for item in self.reference_images):
            raise SemanticNormalizationError("source provenance reference images are invalid")
        object.__setattr__(self, "source_status", status)

    def _canonical_dict(self) -> dict[str, object]:
        return {
            "raw_artifact_digest": self.raw_artifact_digest,
            "raw_sha256": self.raw_sha256,
            "provider_candidate_digest": self.provider_candidate_digest,
            "provider": {"id": self.provider_id, "version": self.provider_version, "workflow_version": self.workflow_version, "model_id": self.model_id},
            "request_digest": self.request_digest,
            "requested_dimensions": {"width": self.requested_width, "height": self.requested_height},
            "returned_dimensions": {"width": self.returned_width, "height": self.returned_height},
            "media_type": self.media_type,
            "source_status": self.source_status.value,
            "reference_images": [item.canonical_dict() for item in self.reference_images],
            "style_image": self.style_image.canonical_dict() if self.style_image else None,
            "init_image": self.init_image.canonical_dict() if self.init_image else None,
            "color_reference": self.color_reference.canonical_dict() if self.color_reference else None,
        }

    def _compute_fingerprint(self) -> str:
        return _digest(self._canonical_dict())

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _SOURCE_PROVENANCE_CONSTRUCTION_TOKEN:
            raise SemanticNormalizationError("source provenance construction seal is invalid")
        if getattr(self, "_construction_fingerprint", None) != self._compute_fingerprint():
            raise SemanticNormalizationError("source provenance construction fingerprint is invalid")

    def canonical_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return self._canonical_dict()

    def digest(self) -> str:
        self._assert_integrity()
        return _digest(self._canonical_dict())


@dataclass(frozen=True, slots=True)
class SemanticNormalizedArtifact:
    """Immutable normalized RGBA artifact, still separate from M08 LEVEL_ART."""

    source_raw_artifact_digest: str
    normalization_request_digest: str
    output_class: OutputClass
    target_width: int
    target_height: int
    rgba8: bytes = field(repr=False, compare=False)
    normalized_rgba_sha256: str
    report: SemanticNormalizationReport
    palette_policy: str
    provider_id: str
    provider_version: str
    workflow_version: str
    model_id: str | None
    request_digest: str
    schema: str = NORMALIZATION_SCHEMA
    schema_version: int = NORMALIZATION_SCHEMA_VERSION
    source_provenance: SemanticSourceProvenance | None = field(default=None, repr=False, compare=False)
    normalization_request: SemanticNormalizationRequest | None = field(default=None, repr=False, compare=False)
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _NORMALIZED_ARTIFACT_CONSTRUCTION_TOKEN:
            raise SemanticNormalizationError("normalized artifacts require checked construction from a raw artifact")
        if not isinstance(self.source_provenance, SemanticSourceProvenance):
            raise SemanticNormalizationError("normalized artifact source provenance is missing")
        if not isinstance(self.normalization_request, SemanticNormalizationRequest):
            raise SemanticNormalizationError("normalized artifact normalization request is missing")
        _dimension(self.target_width, "target_width")
        _dimension(self.target_height, "target_height")
        if self.output_class is not OutputClass.ASSET_ART:
            raise SemanticNormalizationError("normalized C001 artifact must be ASSET_ART")
        if self.palette_policy != ASSET_PALETTE_POLICY:
            raise SemanticNormalizationError("unsupported normalized asset palette policy")
        if not isinstance(self.rgba8, bytes) or len(self.rgba8) != self.target_width * self.target_height * 4:
            raise SemanticNormalizationError("normalized RGBA8 bytes do not match target dimensions")
        if self.normalized_rgba_sha256 != _sha256(self.rgba8):
            raise SemanticNormalizationError("normalized RGBA8 SHA-256 does not match pixels")
        _sha256_text(self.normalized_rgba_sha256, "normalized_rgba_sha256")
        _sha256_text(self.source_raw_artifact_digest, "source_raw_artifact_digest")
        _sha256_text(self.normalization_request_digest, "normalization_request_digest")
        _sha256_text(self.request_digest, "request_digest")
        _text(self.provider_id, "provider_id")
        _text(self.provider_version, "provider_version")
        _text(self.workflow_version, "workflow_version")
        source = self.source_provenance
        request = self.normalization_request
        if self.source_raw_artifact_digest != source.raw_artifact_digest or self.request_digest != source.request_digest or self.provider_id != source.provider_id or self.provider_version != source.provider_version or self.workflow_version != source.workflow_version or self.model_id != source.model_id or self.normalization_request_digest != request.digest() or request.source_raw_artifact_digest != source.raw_artifact_digest or request.output_class is not OutputClass.ASSET_ART or (request.target_width, request.target_height) != (self.target_width, self.target_height) or self.palette_policy != request.palette_policy:
            raise SemanticNormalizationError("normalized provider provenance is not bound to the raw source snapshot")
        if not isinstance(self.report, SemanticNormalizationReport) or self.report.output_rgba_sha256 != self.normalized_rgba_sha256 or self.report.source_raw_artifact_digest != self.source_raw_artifact_digest or self.report.request_digest != self.normalization_request_digest or (self.report.target_width, self.report.target_height) != (self.target_width, self.target_height) or self.report.input_raw_sha256 != source.raw_sha256 or self.report.alpha_policy != request.alpha_policy or self.report.palette_policy != request.palette_policy:
            raise SemanticNormalizationError("normalized report is not bound to output pixels")
        object.__setattr__(self, "rgba8", bytes(self.rgba8))
        if hasattr(self, "_construction_fingerprint"):
            self._assert_integrity()

    @classmethod
    def from_raw_artifact(cls, raw_artifact: SemanticRawArtifact, request: SemanticNormalizationRequest, rgba8: bytes, report: SemanticNormalizationReport) -> "SemanticNormalizedArtifact":
        if not isinstance(raw_artifact, SemanticRawArtifact) or not isinstance(request, SemanticNormalizationRequest):
            raise SemanticNormalizationError("checked normalized construction requires typed raw artifact and request")
        if request.source_raw_artifact_digest != raw_artifact.digest():
            raise SemanticNormalizationError("normalization request is not bound to the raw artifact")
        if request.output_class is not OutputClass.ASSET_ART:
            raise SemanticNormalizationError("checked normalized construction only supports ASSET_ART")
        source = SemanticSourceProvenance.from_raw_artifact(raw_artifact)
        if report.source_raw_artifact_digest != source.raw_artifact_digest or report.request_digest != request.digest() or report.input_raw_sha256 != source.raw_sha256 or report.alpha_policy != request.alpha_policy or report.palette_policy != request.palette_policy or (report.target_width, report.target_height) != (request.target_width, request.target_height) or report.output_rgba_sha256 != _sha256(rgba8):
            raise SemanticNormalizationError("normalization report is not bound to the exact raw source and request")
        instance = object.__new__(cls)
        values = {
            "source_raw_artifact_digest": source.raw_artifact_digest, "normalization_request_digest": request.digest(),
            "output_class": OutputClass.ASSET_ART, "target_width": request.target_width, "target_height": request.target_height,
            "rgba8": bytes(rgba8), "normalized_rgba_sha256": _sha256(rgba8), "report": report,
            "palette_policy": request.palette_policy, "provider_id": source.provider_id,
            "provider_version": source.provider_version, "workflow_version": source.workflow_version,
            "model_id": source.model_id, "request_digest": source.request_digest, "schema": NORMALIZATION_SCHEMA,
            "schema_version": NORMALIZATION_SCHEMA_VERSION, "source_provenance": source,
            "normalization_request": request,
        }
        for name, value in values.items():
            object.__setattr__(instance, name, value)
        object.__setattr__(instance, "_construction_token", _NORMALIZED_ARTIFACT_CONSTRUCTION_TOKEN)
        instance.__post_init__()
        object.__setattr__(instance, "_construction_fingerprint", instance._compute_fingerprint())
        instance._assert_integrity()
        return instance

    def _compute_fingerprint(self) -> str:
        return _digest({"source_provenance": self.source_provenance.digest(), "normalization_request": self.normalization_request.digest(), "report": self.report.digest(), "output": self.normalized_rgba_sha256, "target": [self.target_width, self.target_height], "provider": [self.provider_id, self.provider_version, self.workflow_version, self.model_id], "request_digest": self.request_digest})

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _NORMALIZED_ARTIFACT_CONSTRUCTION_TOKEN:
            raise SemanticNormalizationError("normalized artifact construction seal is invalid")
        if getattr(self, "_construction_fingerprint", None) != self._compute_fingerprint():
            raise SemanticNormalizationError("normalized artifact construction fingerprint is invalid")
        self.source_provenance._assert_integrity()

    @property
    def normalized_pixel_sha256(self) -> str:
        return self.normalized_rgba_sha256

    @property
    def normalized_pixels(self) -> bytes:
        return self.rgba8

    @property
    def normalization_report(self) -> SemanticNormalizationReport:
        return self.report

    @property
    def report_digest(self) -> str:
        return self.report.digest()

    def identity_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return {"schema": self.schema, "schema_version": self.schema_version, "source_raw_artifact_digest": self.source_raw_artifact_digest, "normalization_request_digest": self.normalization_request_digest, "output_class": self.output_class.value, "target_dimensions": {"width": self.target_width, "height": self.target_height}, "normalized_rgba_sha256": self.normalized_rgba_sha256, "report_digest": self.report_digest, "palette_policy": self.palette_policy, "provider": {"id": self.provider_id, "version": self.provider_version, "workflow_version": self.workflow_version, "model_id": self.model_id}, "request_digest": self.request_digest, "source_provenance_digest": self.source_provenance.digest()}

    def canonical_dict(self) -> dict[str, object]:
        return {**self.identity_dict(), "rgba8_base64": base64.b64encode(self.rgba8).decode("ascii"), "report": self.report.canonical_dict()}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _sha256(_canonical_bytes(self.identity_dict()))

    def as_m08_artwork(self) -> object:
        raise SemanticNormalizationRequiredError("normalized semantic ASSET_ART is not a canonical M08 LEVEL_ART artwork")


def normalize_semantic_artifact(raw_artifact: SemanticRawArtifact, request: SemanticNormalizationRequest) -> SemanticNormalizedArtifact:
    """Decode and deterministically normalize one immutable raw artifact."""
    if not isinstance(raw_artifact, SemanticRawArtifact) or not isinstance(request, SemanticNormalizationRequest):
        raise SemanticNormalizationError("normalization requires typed raw artifact and request")
    if request.source_raw_artifact_digest != raw_artifact.digest():
        raise SemanticNormalizationError("normalization request is not bound to the raw artifact")
    if request.output_class is OutputClass.LEVEL_ART:
        raise SemanticNormalizationError("C001 does not implement final LEVEL_ART palette quantization")
    decoded = _decode_raw(raw_artifact.raw_bytes, raw_artifact.media_type)
    if (decoded.width, decoded.height) != (raw_artifact.returned_width, raw_artifact.returned_height):
        raise SemanticNormalizationError("decoded dimensions do not match provider candidate returned dimensions")
    pixels = _apply_alpha(decoded.pixels, request.alpha_policy)
    exact = (decoded.width, decoded.height) == (request.target_width, request.target_height)
    if exact:
        normalized = pixels
        crop_pad: Mapping[str, int | str] = {"operation": "NONE"}
        resampler = "NONE_EXACT_SIZE"
    else:
        normalized, crop_pad = _fit_center(pixels, decoded.width, decoded.height, request.target_width, request.target_height, request.alpha_policy)
        resampler = request.resize_policy
    output_hash = _sha256(normalized)
    report = SemanticNormalizationReport(
        raw_artifact.digest(), request.digest(), decoded.width, decoded.height, request.target_width, request.target_height,
        exact, not exact, resampler, crop_pad, request.alpha_policy, request.palette_policy, raw_artifact.raw_sha256, output_hash,
    )
    return SemanticNormalizedArtifact.from_raw_artifact(raw_artifact, request, normalized, report)


normalize = normalize_semantic_artifact
normalize_artifact = normalize_semantic_artifact


class SemanticNormalizer:
    """Stateless discoverable facade for the deterministic normalizer."""

    @staticmethod
    def normalize(raw_artifact: SemanticRawArtifact, request: SemanticNormalizationRequest) -> SemanticNormalizedArtifact:
        return normalize_semantic_artifact(raw_artifact, request)


__all__ = [
    "ALPHA_POLICIES", "ASSET_PALETTE_POLICY", "FUTURE_LEVEL_PALETTE_POLICY", "MAX_DECODE_PIXELS", "NORMALIZATION_POLICY_VERSION", "NORMALIZATION_REPORT_SCHEMA", "NORMALIZATION_REPORT_VERSION", "NORMALIZATION_SCHEMA", "NORMALIZATION_SCHEMA_VERSION", "RAW_ARTIFACT_MAX_BYTES", "RAW_ARTIFACT_SCHEMA", "RAW_ARTIFACT_SCHEMA_VERSION", "SemanticDecodeError", "SemanticNormalizedArtifact", "SemanticNormalizationError", "SemanticNormalizationReport", "SemanticNormalizationRequest", "SemanticNormalizer", "SemanticRawArtifact", "SemanticSourceProvenance", "normalize", "normalize_artifact", "normalize_semantic_artifact",
]
