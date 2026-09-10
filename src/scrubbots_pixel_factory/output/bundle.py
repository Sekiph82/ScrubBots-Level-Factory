"""Deterministic M08 metadata binding and filesystem bundle round trips."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

from ..core import GenerationResult, ResultStatus
from ..quality import QualityPolicy, QualityReport, evaluate_grid
from .artwork import ArtworkArtifact, ArtworkContractError, canonical_json_bytes
from .png import PNGContractError, decode_logical_png, decode_png, encode_logical_png, encode_preview_png


METADATA_SCHEMA = "scrubbots-output-metadata"
METADATA_SCHEMA_VERSION = 1
GENERATOR_METADATA_SCHEMA = "scrubbots-generator-metadata"
GENERATOR_METADATA_VERSION = 1


class OutputContractError(ValueError):
    """Raised when an M08 export or bundle violates a stable contract."""


class BundleConflictError(OutputContractError):
    """Raised when a candidate directory already contains different content."""


def _json_value(value: object, path: str = "value") -> object:
    if value is None or type(value) is bool or type(value) is str or type(value) is int:
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise OutputContractError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        result: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise OutputContractError(f"{path} contains a non-string object key")
            result[key] = _json_value(item, f"{path}.{key}")
        return result
    if isinstance(value, (list, tuple)):
        return [_json_value(item, f"{path}[]") for item in value]
    raise OutputContractError(f"{path} contains an unsupported value")


def _mapping_copy(value: object, path: str) -> dict[str, object]:
    checked = _json_value(value, path)
    if not isinstance(checked, dict):
        raise OutputContractError(f"{path} must be a JSON object")
    return checked


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _candidate_payload(candidate: object) -> tuple[GenerationResult, Mapping[str, object]]:
    result = candidate if isinstance(candidate, GenerationResult) else getattr(candidate, "result", None)
    if not isinstance(result, GenerationResult):
        raise OutputContractError("export requires a GenerationResult or an existing generator candidate wrapper")
    if not result.is_success or result.status is not ResultStatus.SUCCESS:
        raise OutputContractError("failed GenerationResult cannot be exported as a successful bundle")
    if isinstance(candidate, GenerationResult):
        return result, {}
    for property_name in ("wfc_metadata", "hybrid_metadata", "auto_metadata"):
        payload = getattr(candidate, property_name, None)
        if isinstance(payload, Mapping):
            return result, {"namespace": property_name.removesuffix("_metadata"), "data": _mapping_copy(payload, property_name)}
    payload = getattr(candidate, "metadata", None)
    if isinstance(payload, Mapping):
        return result, {"namespace": "generator", "data": _mapping_copy(payload, "candidate.metadata")}
    return result, {}


def _quality_binding(report: QualityReport, artwork: ArtworkArtifact) -> dict[str, object]:
    analysis = report.analysis
    if analysis is None:
        raise OutputContractError("quality report must contain analysis for a successful artwork")
    if analysis.width != artwork.width or analysis.height != artwork.height or tuple(analysis.cells) != artwork.cells:
        raise OutputContractError("quality report is bound to different logical dimensions or cells")
    report_dict = _mapping_copy(report.as_dict(), "quality_report")
    return {
        "schema": "scrubbots-output-quality-binding",
        "version": 1,
        "candidate_id": artwork.candidate_id,
        "width": artwork.width,
        "height": artwork.height,
        "grid_hash": artwork.grid_hash,
        "decision": "ACCEPT" if report.accepted else "REJECT",
        "rejection_codes": list(report.rejection_codes),
        "report": report_dict,
    }


def _metadata_for(result: GenerationResult, artwork: ArtworkArtifact, generator_metadata: Mapping[str, object], quality_report: QualityReport) -> dict[str, object]:
    result_dict = _mapping_copy(result.canonical_dict(), "generation_result")
    if result_dict.get("status") != ResultStatus.SUCCESS.value:
        raise OutputContractError("only successful GenerationResult values can be exported")
    return {
        "schema": METADATA_SCHEMA,
        "schema_version": METADATA_SCHEMA_VERSION,
        "candidate_id": artwork.candidate_id,
        "artwork": {
            "schema": artwork.as_dict()["schema"],
            "schema_version": artwork.as_dict()["schema_version"],
            "candidate_id": artwork.candidate_id,
            "width": artwork.width,
            "height": artwork.height,
            "palette": list(artwork.palette),
            "grid_hash": artwork.grid_hash,
        },
        "generation": {
            "result": result_dict,
            "result_digest": result.digest(),
            "request": result.request.canonical_dict(),  # type: ignore[union-attr]
            "generator_mode": result.generator_mode,
            "generator_id": result.generator_id,
            "generator_version": result.generator_version,
            "seed": result_dict["seed"],
            "rng": result_dict["rng"],
            "provenance": _mapping_copy(result.provenance or {}, "generation.provenance"),
        },
        "generator_metadata": {
            "schema": GENERATOR_METADATA_SCHEMA,
            "version": GENERATOR_METADATA_VERSION,
            "present": bool(generator_metadata),
            "payload": _mapping_copy(generator_metadata, "generator_metadata"),
        },
        "quality": _quality_binding(quality_report, artwork),
    }


@dataclass(frozen=True, slots=True)
class ExportBundle:
    """Fully materialized deterministic bundle bytes and immutable truth."""

    artwork: ArtworkArtifact
    metadata: Mapping[str, object]
    artwork_json: bytes
    metadata_json: bytes
    artwork_png: bytes
    preview_png: bytes | None = None

    @property
    def files(self) -> dict[str, bytes]:
        files = {
            "artwork.json": self.artwork_json,
            "metadata.json": self.metadata_json,
            "artwork.png": self.artwork_png,
        }
        if self.preview_png is not None:
            files["artwork.preview.png"] = self.preview_png
        return files


def build_export_bundle(
    candidate: object,
    candidate_id: str,
    *,
    quality_report: QualityReport | None = None,
    preview_scale: int | None = None,
) -> ExportBundle:
    """Build deterministic bytes from a successful result or candidate wrapper."""

    result, candidate_metadata = _candidate_payload(candidate)
    try:
        artwork = ArtworkArtifact.from_result(result, candidate_id)
        report = quality_report if quality_report is not None else evaluate_grid(artwork.width, artwork.height, artwork.cells)
        metadata = _metadata_for(result, artwork, candidate_metadata, report)
        artwork_json = artwork.canonical_bytes()
        metadata_json = canonical_json_bytes(metadata)
        artwork_png = encode_logical_png(artwork.width, artwork.height, artwork.cells)
        preview_png = None if preview_scale is None else encode_preview_png(artwork.width, artwork.height, artwork.cells, preview_scale)
        if preview_scale is not None:
            metadata["preview"] = {
                "enabled": True,
                "scale": preview_scale,
                "width": artwork.width * preview_scale,
                "height": artwork.height * preview_scale,
            }
            metadata_json = canonical_json_bytes(metadata)
        else:
            metadata["preview"] = {"enabled": False, "scale": None, "width": None, "height": None}
            metadata_json = canonical_json_bytes(metadata)
    except (ArtworkContractError, PNGContractError, TypeError, ValueError) as exc:
        if isinstance(exc, OutputContractError):
            raise
        raise OutputContractError(str(exc)) from exc
    return ExportBundle(artwork, metadata, artwork_json, metadata_json, artwork_png, preview_png)


def _validate_metadata(metadata: object, artwork: ArtworkArtifact) -> dict[str, object]:
    value = _mapping_copy(metadata, "metadata")
    required = {"schema", "schema_version", "candidate_id", "artwork", "generation", "generator_metadata", "quality", "preview"}
    if set(value) != required or value["schema"] != METADATA_SCHEMA or value["schema_version"] != METADATA_SCHEMA_VERSION:
        raise OutputContractError("unsupported or incomplete metadata schema/version")
    if value["candidate_id"] != artwork.candidate_id:
        raise OutputContractError("metadata candidate_id does not match artwork")
    artwork_binding = _mapping_copy(value["artwork"], "metadata.artwork")
    expected_binding = {
        "schema": artwork.as_dict()["schema"],
        "schema_version": artwork.as_dict()["schema_version"],
        "candidate_id": artwork.candidate_id,
        "width": artwork.width,
        "height": artwork.height,
        "palette": list(artwork.palette),
        "grid_hash": artwork.grid_hash,
    }
    if artwork_binding != expected_binding:
        raise OutputContractError("metadata artwork binding does not match artwork.json")
    generation = _mapping_copy(value["generation"], "metadata.generation")
    result_dict = _mapping_copy(generation.get("result"), "metadata.generation.result")
    if result_dict.get("status") != ResultStatus.SUCCESS.value:
        raise OutputContractError("metadata cannot bind a failed GenerationResult")
    if result_dict.get("logical_grid") != list(artwork.cells) or result_dict.get("resolved_dimensions") != {"width": artwork.width, "height": artwork.height}:
        raise OutputContractError("metadata GenerationResult does not match artwork")
    if generation.get("result_digest") != _sha256(canonical_json_bytes(result_dict)):
        raise OutputContractError("metadata GenerationResult digest is invalid")
    generator = result_dict.get("generator")
    if not isinstance(generator, Mapping):
        raise OutputContractError("metadata GenerationResult generator binding is invalid")
    if generation.get("generator_mode") != generator.get("mode"):
        raise OutputContractError("metadata generator mode binding is invalid")
    if generation.get("generator_id") != generator.get("id") or generation.get("generator_version") != generator.get("version"):
        raise OutputContractError("metadata generator identity binding is invalid")
    if generation.get("request") != result_dict.get("request"):
        raise OutputContractError("metadata request binding is invalid")
    if generation.get("seed") != result_dict.get("seed"):
        raise OutputContractError("metadata typed seed binding is invalid")
    result_rng = result_dict.get("rng")
    if not isinstance(result_rng, Mapping) or generation.get("rng") != result_rng:
        raise OutputContractError("metadata RNG provenance binding is invalid")
    if generation.get("provenance") != result_rng.get("provenance"):
        raise OutputContractError("metadata provenance binding is invalid")
    quality = _mapping_copy(value["quality"], "metadata.quality")
    if quality.get("candidate_id") != artwork.candidate_id or quality.get("width") != artwork.width or quality.get("height") != artwork.height or quality.get("grid_hash") != artwork.grid_hash:
        raise OutputContractError("quality report is bound to a different logical artifact")
    report = _mapping_copy(quality.get("report"), "metadata.quality.report")
    analysis = report.get("analysis")
    if not isinstance(analysis, Mapping) or analysis.get("width") != artwork.width or analysis.get("height") != artwork.height:
        raise OutputContractError("quality report dimensions do not match artwork")
    try:
        policy_data = _mapping_copy(report.get("policy"), "metadata.quality.report.policy")
        expected_report = evaluate_grid(artwork.width, artwork.height, artwork.cells, policy=QualityPolicy(**policy_data)).as_dict()
    except (TypeError, ValueError) as exc:
        raise OutputContractError("quality report policy is malformed") from exc
    if report != expected_report:
        raise OutputContractError("quality report is not the deterministic report for artwork.json")
    expected_decision = "ACCEPT" if expected_report["accepted"] else "REJECT"
    if quality.get("decision") != expected_decision or quality.get("rejection_codes") != expected_report["rejection_codes"]:
        raise OutputContractError("quality binding decision or rejection codes are invalid")
    generator_metadata = _mapping_copy(value["generator_metadata"], "metadata.generator_metadata")
    if (
        generator_metadata.get("schema") != GENERATOR_METADATA_SCHEMA
        or generator_metadata.get("version") != GENERATOR_METADATA_VERSION
        or type(generator_metadata.get("present")) is not bool
        or not isinstance(generator_metadata.get("payload"), Mapping)
        or generator_metadata.get("present") != bool(generator_metadata["payload"])
    ):
        raise OutputContractError("generator metadata binding is invalid")
    preview = _mapping_copy(value["preview"], "metadata.preview")
    enabled = preview.get("enabled")
    if enabled not in {True, False}:
        raise OutputContractError("metadata preview enabled flag is invalid")
    if enabled:
        scale = preview.get("scale")
        if type(scale) is not int or scale < 1 or scale > 64 or preview.get("width") != artwork.width * scale or preview.get("height") != artwork.height * scale:
            raise OutputContractError("metadata preview dimensions or scale are invalid")
    elif any(preview.get(key) is not None for key in ("scale", "width", "height")):
        raise OutputContractError("disabled preview must not carry dimensions or scale")
    return value


def read_bundle(directory: str | os.PathLike[str]) -> ExportBundle:
    """Read and fail-closed validate one deterministic candidate bundle."""

    root = Path(directory)
    if not root.is_dir():
        raise OutputContractError("bundle directory does not exist")
    allowed = {"artwork.json", "metadata.json", "artwork.png", "artwork.preview.png"}
    actual = {path.name for path in root.iterdir() if path.is_file()}
    if not {"artwork.json", "metadata.json", "artwork.png"}.issubset(actual) or not actual.issubset(allowed):
        raise OutputContractError("bundle file set is incomplete or contains unexpected files")
    try:
        artwork_json = (root / "artwork.json").read_bytes()
        metadata_json = (root / "metadata.json").read_bytes()
        artwork_png = (root / "artwork.png").read_bytes()
        artwork = ArtworkArtifact.from_dict(json.loads(artwork_json.decode("utf-8")))
        metadata = json.loads(metadata_json.decode("utf-8"))
        _validate_metadata(metadata, artwork)
        decoded = decode_logical_png(artwork_png)
    except (OSError, UnicodeError, json.JSONDecodeError, ArtworkContractError, PNGContractError) as exc:
        raise OutputContractError(str(exc)) from exc
    if (decoded.width, decoded.height, decoded.cells, decoded.palette) != (artwork.width, artwork.height, artwork.cells, artwork.palette):
        raise OutputContractError("artwork.png does not exactly match artwork.json")
    preview_png = None
    try:
        if "artwork.preview.png" in actual:
            preview_png = (root / "artwork.preview.png").read_bytes()
            preview = metadata["preview"]
            if not preview["enabled"]:
                raise OutputContractError("preview file exists while metadata disables preview")
            preview_decoded = decode_png(preview_png, max_dimension=4096)
            expected_rows: list[tuple[str, ...]] = []
            for row in range(artwork.height):
                row_cells = artwork.cells[row * artwork.width : (row + 1) * artwork.width]
                expanded_row = tuple(cell for cell in row_cells for _ in range(preview["scale"]))
                expected_rows.extend(expanded_row for _ in range(preview["scale"]))
            expected_cells = tuple(cell for row in expected_rows for cell in row)
            if (preview_decoded.width, preview_decoded.height, preview_decoded.cells) != (preview["width"], preview["height"], expected_cells):
                raise OutputContractError("preview PNG is not exact integer replication of logical artwork")
        elif metadata["preview"]["enabled"]:
            raise OutputContractError("metadata enables a preview but the preview file is missing")
    except (OSError, PNGContractError, TypeError, KeyError, ValueError) as exc:
        raise OutputContractError(str(exc)) from exc
    return ExportBundle(artwork, _mapping_copy(metadata, "metadata"), artwork_json, metadata_json, artwork_png, preview_png)


def write_bundle(bundle: ExportBundle, destination: str | os.PathLike[str]) -> Path:
    """Write only one candidate directory, allowing identical rewrites."""

    if not isinstance(bundle, ExportBundle):
        raise OutputContractError("write_bundle requires an ExportBundle")
    parent = Path(destination)
    parent.mkdir(parents=True, exist_ok=True)
    target = parent / bundle.artwork.candidate_id
    expected = bundle.files
    if target.exists():
        if not target.is_dir():
            raise BundleConflictError("candidate destination exists but is not a directory")
        actual = {path.name for path in target.iterdir() if path.is_file()}
        if actual != set(expected):
            raise BundleConflictError("existing candidate bundle has a conflicting file set")
        for name, content in expected.items():
            if (target / name).read_bytes() != content:
                raise BundleConflictError("existing candidate bundle contains conflicting content")
        return target
    temporary = Path(tempfile.mkdtemp(prefix=f".{bundle.artwork.candidate_id}.", dir=parent))
    try:
        for name, content in expected.items():
            (temporary / name).write_bytes(content)
        os.replace(temporary, target)
    except (OSError, ValueError) as exc:
        shutil.rmtree(temporary, ignore_errors=True)
        raise OutputContractError(f"bundle write failed: {exc}") from exc
    return target


def export_candidate(
    candidate: object,
    candidate_id: str,
    destination: str | os.PathLike[str],
    *,
    quality_report: QualityReport | None = None,
    preview_scale: int | None = None,
) -> Path:
    return write_bundle(build_export_bundle(candidate, candidate_id, quality_report=quality_report, preview_scale=preview_scale), destination)


def export_result(
    result: GenerationResult,
    candidate_id: str,
    destination: str | os.PathLike[str],
    *,
    quality_report: QualityReport | None = None,
    preview_scale: int | None = None,
) -> Path:
    return export_candidate(result, candidate_id, destination, quality_report=quality_report, preview_scale=preview_scale)


__all__ = [
    "BundleConflictError",
    "ExportBundle",
    "GENERATOR_METADATA_SCHEMA",
    "GENERATOR_METADATA_VERSION",
    "METADATA_SCHEMA",
    "METADATA_SCHEMA_VERSION",
    "OutputContractError",
    "build_export_bundle",
    "export_candidate",
    "export_result",
    "read_bundle",
    "write_bundle",
]
