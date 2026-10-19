"""Deterministic M08 metadata binding and filesystem bundle round trips."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any

from ..contracts.candidate_provenance import (
    CandidateProvenanceError,
    build_candidate_classification,
    build_verified_owner_upload_classification,
    validate_candidate_classification,
    validate_verified_owner_upload_classification,
)
from ..core import DeterministicRNG, GenerationResult, ResultStatus
from ..quality import QualityPolicy, QualityReport, evaluate_grid, logical_grid_hash
from .artwork import ArtworkArtifact, ArtworkContractError, canonical_json_bytes
from .png import PNGContractError, decode_logical_png, decode_png, encode_logical_png, encode_preview_png


METADATA_SCHEMA = "scrubbots-output-metadata"
METADATA_SCHEMA_VERSION = 1
GENERATOR_METADATA_SCHEMA = "scrubbots-generator-metadata"
GENERATOR_METADATA_VERSION = 1
_RICH_MODES = {"WFC", "HYBRID", "AUTO", "ART_FIRST"}
_RICH_NAMESPACES = {"WFC": "wfc", "HYBRID": "hybrid", "AUTO": "auto", "ART_FIRST": "art_first"}


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


def _candidate_payload(candidate: object, explicit_metadata: Mapping[str, object] | None = None) -> tuple[GenerationResult, Mapping[str, object]]:
    result = candidate if isinstance(candidate, GenerationResult) else getattr(candidate, "result", None)
    if not isinstance(result, GenerationResult):
        raise OutputContractError("export requires a GenerationResult or an existing generator candidate wrapper")
    if not result.is_success or result.status is not ResultStatus.SUCCESS:
        raise OutputContractError("failed GenerationResult cannot be exported as a successful bundle")
    candidate_payload: dict[str, object] | None = None
    if not isinstance(candidate, GenerationResult):
        for property_name in ("wfc_metadata", "hybrid_metadata", "auto_metadata", "art_first_metadata"):
            payload = getattr(candidate, property_name, None)
            if isinstance(payload, Mapping):
                candidate_payload = {"namespace": property_name.removesuffix("_metadata"), "data": _mapping_copy(payload, property_name)}
                break
        if candidate_payload is None:
            payload = getattr(candidate, "metadata", None)
            if isinstance(payload, Mapping):
                candidate_payload = {"namespace": "generator", "data": _mapping_copy(payload, "candidate.metadata")}
    supplied_payload: dict[str, object] | None = None
    if explicit_metadata is not None:
        supplied = _mapping_copy(explicit_metadata, "generator_metadata")
        if set(supplied) == {"namespace", "data"}:
            namespace = supplied["namespace"]
            data = _mapping_copy(supplied["data"], "generator_metadata.data")
            if type(namespace) is not str:
                raise OutputContractError("generator metadata namespace must be a string")
            supplied_payload = {"namespace": namespace, "data": data}
        else:
            supplied_payload = {"namespace": _RICH_NAMESPACES.get(result.generator_mode or "", "generator"), "data": supplied}
    if candidate_payload is not None and supplied_payload is not None and candidate_payload != supplied_payload:
        raise OutputContractError("explicit generator metadata conflicts with candidate metadata")
    payload = supplied_payload or candidate_payload
    if result.generator_mode in _RICH_MODES and payload is None:
        raise OutputContractError(f"successful {result.generator_mode} export requires an authoritative candidate wrapper or generator_metadata")
    if payload is None:
        return result, {}
    expected_namespace = _RICH_NAMESPACES.get(result.generator_mode or "")
    if expected_namespace is not None and payload["namespace"] != expected_namespace:
        raise OutputContractError("generator metadata namespace does not match the GenerationResult mode")
    return result, payload


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


def _verified_owner_upload_sha256(
    result: Mapping[str, object],
    candidate_id: str,
    artwork: ArtworkArtifact,
    generator_payload: Mapping[str, object],
) -> str | None:
    """Verify owner-upload source bytes before export can carry production class."""

    if generator_payload.get("namespace") != "owner-upload":
        return None
    data = _mapping_copy(generator_payload.get("data"), "owner-upload generator metadata.data")
    lineage = _mapping_copy(data.get("source_lineage"), "owner-upload source lineage")
    source_id = lineage.get("source_id")
    source_sha256 = lineage.get("source_sha256")
    if (
        type(source_id) is not str
        or type(source_sha256) is not str
        or not _DIGEST.fullmatch(source_sha256)
        or source_id != f"owner-upload-{source_sha256}"
        or lineage.get("derivation") != "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE"
        or lineage.get("source_bytes_unchanged") is not True
        or candidate_id != f"candidate-owner-{source_sha256[:48]}"
    ):
        raise OutputContractError("owner-upload classification lacks canonical source identity")

    try:
        # Import lazily: studio_extensions itself uses the bundle reader for
        # source-library projections.
        from .. import studio_extensions as studio

        verified = studio.verify_owner_source(source_id)
        source_path = Path(str(verified["source_path"]))
        if not source_path.is_absolute():
            source_path = studio._repository_root() / source_path
        source_bytes = source_path.read_bytes()
        width, height, source_cells, foreign, semi_alpha, _transparent, _used = studio._owner_source_grid(source_bytes)
    except (KeyError, OSError, TypeError, ValueError) as exc:
        raise OutputContractError("canonical OWNER_UPLOAD source bytes could not be verified") from exc

    request = _mapping_copy(result.get("request"), "generation result request")
    request_seed = _mapping_copy(request.get("seed"), "generation result request seed")
    generator = _mapping_copy(result.get("generator"), "generation result generator")
    if (
        verified.get("source_id") != source_id
        or verified.get("source_sha256") != source_sha256
        or verified.get("source_bytes_sha256") != source_sha256
        or verified.get("record_path") != lineage.get("source_record")
        or request_seed.get("value") != source_sha256
        or request_seed.get("type") != "string"
        or generator.get("id") != "owner-upload-canonical-derive"
        or generator.get("version") != "1"
        or request.get("generator_mode") != "MASK"
        or (width, height) != (artwork.width, artwork.height)
        or (width, height) != (verified.get("original_width"), verified.get("original_height"))
        or foreign != 0
        or semi_alpha != 0
        or source_cells != artwork.cells
    ):
        raise OutputContractError("owner-upload lineage does not match the exact canonical source bytes and artwork")
    return source_sha256


def _metadata_for(result: GenerationResult, artwork: ArtworkArtifact, generator_metadata: Mapping[str, object], quality_report: QualityReport) -> dict[str, object]:
    result_dict = _mapping_copy(result.canonical_dict(), "generation_result")
    if result_dict.get("status") != ResultStatus.SUCCESS.value:
        raise OutputContractError("only successful GenerationResult values can be exported")
    generator_payload = _mapping_copy(generator_metadata, "generator_metadata")
    owner_source_sha256 = _verified_owner_upload_sha256(
        result_dict, artwork.candidate_id, artwork, generator_payload
    )
    if owner_source_sha256 is not None:
        classification = build_verified_owner_upload_classification(
            result_dict,
            candidate_id=artwork.candidate_id,
            grid_hash=artwork.grid_hash,
            generator_metadata=generator_payload,
            verified_source_sha256=owner_source_sha256,
        )
    else:
        classification = build_candidate_classification(
            result_dict,
            candidate_id=artwork.candidate_id,
            grid_hash=artwork.grid_hash,
            generator_metadata=generator_payload,
        )
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
            "payload": generator_payload,
            "classification": classification,
        },
        "quality": _quality_binding(quality_report, artwork),
    }


_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _request_parts(result_dict: Mapping[str, object]) -> tuple[Mapping[str, object], Mapping[str, object]]:
    request = _mapping_copy(result_dict.get("request"), "generation.result.request")
    options = _mapping_copy(request.get("generator_options"), "generation.result.request.generator_options")
    return request, _mapping_copy(options.get("values"), "generation.result.request.generator_options.values")


def _retry_provenance(result_dict: Mapping[str, object], path: str = "generation.result.rng.provenance") -> Mapping[str, object]:
    rng = _mapping_copy(result_dict.get("rng"), "generation.result.rng")
    return _mapping_copy(rng.get("provenance"), path)


def _typed_seed_value(value: object, path: str) -> int | str:
    seed = _mapping_copy(value, path)
    if seed.get("type") not in {"int", "string"} or type(seed.get("value")) is not (int if seed.get("type") == "int" else str):
        raise OutputContractError(f"{path} is not a valid typed seed")
    return seed["value"]  # type: ignore[return-value]


def _validate_wfc_metadata(data: Mapping[str, object], result_dict: Mapping[str, object], artwork: ArtworkArtifact) -> None:
    if data.get("schema") != "scrubbots-wfc-metadata" or data.get("version") != 1:
        raise OutputContractError("WFC generator metadata schema/version is invalid")
    request, options = _request_parts(result_dict)
    if request.get("style") is not None and data.get("exemplar_id") != request.get("style"):
        raise OutputContractError("WFC exemplar_id does not match the request style")
    if data.get("target_palette") != list(artwork.palette) or data.get("target_palette") != result_dict.get("used_palette"):
        raise OutputContractError("WFC target palette does not match the exported result")
    if data.get("output_dimensions") != {"width": artwork.width, "height": artwork.height}:
        raise OutputContractError("WFC output dimensions do not match the artwork")
    defaults = {
        "pattern_size": 2,
        "input_periodic": False,
        "output_periodic": False,
        "allow_rotations": False,
        "allow_reflections": False,
        "experimental_n4": False,
        "max_attempts": 4,
    }
    for key, default in defaults.items():
        if key in data and data[key] != options.get(key, default):
            raise OutputContractError(f"WFC metadata option binding is invalid: {key}")
    source_palette = data.get("source_palette")
    mapping = data.get("palette_mapping")
    if not isinstance(source_palette, list) or not isinstance(mapping, list):
        raise OutputContractError("WFC palette provenance is malformed")
    pairs: list[list[object]] = []
    for pair in mapping:
        if not isinstance(pair, list) or len(pair) != 2:
            raise OutputContractError("WFC palette mapping pair is malformed")
        pairs.append(pair)
    if [pair[0] for pair in pairs] != source_palette or [pair[1] for pair in pairs] != list(artwork.palette):
        raise OutputContractError("WFC palette mapping is not bound to source and target palettes")
    requested_mapping = options.get("palette_mapping")
    if isinstance(requested_mapping, Mapping):
        expected_mapping = [[key, requested_mapping[key]] for key in sorted(requested_mapping, key=lambda value: int(value[1:]) if value.startswith("C") and value[1:].isdigit() else value)]
        if pairs != expected_mapping:
            raise OutputContractError("WFC palette mapping does not match the request options")
    attempt = data.get("attempt")
    max_attempts = data.get("max_attempts", options.get("max_attempts", 4))
    if type(attempt) is not int or type(max_attempts) is not int or not 0 <= attempt < max_attempts:
        raise OutputContractError("WFC attempt metadata is outside the bounded attempt range")
    retry_seeds = _mapping_copy(_retry_provenance(result_dict).get("retry_seeds"), "WFC result retry provenance")
    expected_retry_keys = {str(index) for index in range(attempt + 1)}
    if set(retry_seeds) != expected_retry_keys or len(retry_seeds) != attempt + 1:
        raise OutputContractError("WFC attempt does not match the GenerationResult retry provenance")
    history = data.get("contradiction_history")
    if not isinstance(history, list):
        raise OutputContractError("WFC contradiction history is malformed")
    if len(history) != attempt:
        raise OutputContractError("WFC contradiction history count does not match the successful attempt")
    for index, entry in enumerate(history):
        if not isinstance(entry, Mapping) or entry.get("attempt") != index:
            raise OutputContractError("WFC contradiction history is not ordered before the successful attempt")


def _grid_digest(cells: object) -> str:
    if not isinstance(cells, list) or any(type(cell) is not str for cell in cells):
        raise OutputContractError("logical grid digest input is malformed")
    return _sha256("\n".join(cells).encode("ascii"))


def _topology_digest(cells: list[str], width: int, height: int, base_color: str) -> str:
    occupied = bytes(1 if cell != base_color else 0 for cell in cells)
    if len(occupied) != width * height:
        raise OutputContractError("topology digest dimensions are invalid")
    return _sha256(occupied)


def _validate_hybrid_metadata(data: Mapping[str, object], result_dict: Mapping[str, object], artwork: ArtworkArtifact) -> None:
    if data.get("schema") != "scrubbots-hybrid-metadata" or data.get("version") != 1:
        raise OutputContractError("HYBRID generator metadata schema/version is invalid")
    request, options = _request_parts(result_dict)
    if data.get("strategy") != options.get("strategy") or data.get("outer_master_seed") != _typed_seed_value(result_dict.get("seed"), "generation.result.seed"):
        raise OutputContractError("HYBRID strategy or master-seed binding is invalid")
    if data.get("resolved_dimensions") != {"width": artwork.width, "height": artwork.height} or data.get("resolved_palette") != list(artwork.palette):
        raise OutputContractError("HYBRID dimensions or palette binding is invalid")
    attempt = data.get("outer_attempt")
    max_attempts = options.get("max_attempts", 4)
    if type(attempt) is not int or type(max_attempts) is not int or not 0 <= attempt < max_attempts:
        raise OutputContractError("HYBRID outer attempt is invalid")
    retry_seeds = _mapping_copy(_retry_provenance(result_dict).get("retry_seeds"), "HYBRID result retry provenance")
    expected_retry_keys = {str(index) for index in range(attempt + 1)}
    if set(retry_seeds) != expected_retry_keys or len(retry_seeds) != attempt + 1:
        raise OutputContractError("HYBRID outer attempt does not match the GenerationResult retry provenance")
    stages = data.get("stages")
    if not isinstance(stages, list) or not stages:
        raise OutputContractError("HYBRID stage metadata is missing")
    strategy = data.get("strategy")
    layouts = {
        "MASK_GEOMETRY_RULE_COLOR_REGIONS": (("MASK_GEOMETRY", "MASK", "MASK"), ("RULE_COLOR_REGIONS", "COMPOSITION", "RULES")),
        "RULE_GEOMETRY_MASK_SYMMETRY": (("RULE_GEOMETRY", "RULES", "RULES"), ("MASK_SYMMETRY_COLOR_REGIONS", "COMPOSITION", "RULES")),
        "RULE_BASE_WFC_DETAIL": (("RULE_BASE", "RULES", "RULES"), ("WFC_DETAIL", "WFC", "WFC")),
        "MASK_BASE_WFC_DETAIL": (("MASK_BASE", "MASK", "MASK"), ("WFC_DETAIL", "WFC", "WFC")),
    }
    expected_layout = layouts.get(strategy)
    if expected_layout is None or len(stages) != len(expected_layout):
        raise OutputContractError("HYBRID strategy-specific stage layout is invalid")
    for index, raw_stage in enumerate(stages):
        stage = _mapping_copy(raw_stage, f"hybrid.stages[{index}]")
        expected_name, expected_kind, expected_mode = expected_layout[index]
        if (stage.get("stage_index"), stage.get("stage_name"), stage.get("stage_kind")) != (index, expected_name, expected_kind):
            raise OutputContractError("HYBRID stage name/kind does not match its strategy")
        if type(stage.get("derived_seed")) is not str or _DIGEST.fullmatch(stage["derived_seed"]) is None:
            raise OutputContractError("HYBRID stages are not deterministically ordered")
        expected_seed = DeterministicRNG(_typed_seed_value(result_dict.get("seed"), "generation.result.seed")).child(
            f"hybrid/{strategy}/{attempt}/{index}/{expected_name}"
        ).next_bytes(32).hex()
        if stage.get("derived_seed") != expected_seed:
            raise OutputContractError("HYBRID stage seed does not match the accepted M06 deterministic derivation")
        child_request = _mapping_copy(stage.get("child_request"), f"hybrid.stages[{index}].child_request")
        if stage.get("child_request_digest") != _sha256(canonical_json_bytes(child_request)):
            raise OutputContractError("HYBRID child request digest is invalid")
        child_seed = _mapping_copy(child_request.get("seed"), f"hybrid.stages[{index}].child_request.seed")
        if child_request.get("generator_mode") != expected_mode:
            raise OutputContractError("HYBRID child request mode contradicts its strategy stage")
        if child_seed.get("type") != "string" or child_seed.get("value") != stage.get("derived_seed"):
            raise OutputContractError("HYBRID child request seed does not match its stage seed")
        if child_request.get("width") != artwork.width or child_request.get("height") != artwork.height or child_request.get("palette_subset") != list(artwork.palette):
            raise OutputContractError("HYBRID child request dimensions or palette are inconsistent")
        for field in ("child_result_digest", "geometry_digest"):
            digest = stage.get(field)
            if digest is not None and (type(digest) is not str or _DIGEST.fullmatch(digest) is None):
                raise OutputContractError(f"HYBRID stage {field} is malformed")
    cells = result_dict.get("logical_grid")
    if data.get("final_logical_grid_digest") != _grid_digest(cells):
        raise OutputContractError("HYBRID final logical-grid digest is invalid")
    if data.get("final_result_digest") != _sha256(canonical_json_bytes(result_dict)):
        raise OutputContractError("HYBRID final result digest is invalid")
    if data.get("final_topology_digest") != _topology_digest(cells, artwork.width, artwork.height, artwork.palette[0]):  # type: ignore[arg-type]
        raise OutputContractError("HYBRID final topology digest is invalid")
    evidence = data.get("topology_evidence")
    if not isinstance(evidence, Mapping):
        raise OutputContractError("HYBRID topology evidence is malformed")
    expected_final = [0 if cell == artwork.palette[0] else 1 for cell in cells]  # type: ignore[union-attr]
    if "final" in evidence and evidence["final"] != expected_final:
        raise OutputContractError("HYBRID final topology evidence is not bound to artwork")
    for name, values in evidence.items():
        if name not in {"before", "after", "final"} or not isinstance(values, list) or len(values) != artwork.width * artwork.height or any(value not in {0, 1} for value in values):
            raise OutputContractError("HYBRID topology evidence shape is invalid")


def _validate_auto_metadata(data: Mapping[str, object], result_dict: Mapping[str, object], artwork: ArtworkArtifact) -> None:
    if data.get("schema") == "scrubbots-evaluator-guided-metadata":
        _validate_evaluator_guided_metadata(data, result_dict, artwork)
        return
    if data.get("schema") != "scrubbots-auto-metadata" or data.get("version") != 1:
        raise OutputContractError("AUTO generator metadata schema/version is invalid")
    request, options = _request_parts(result_dict)
    candidates = options.get("candidates", ["MASK", "RULES"])
    fallback = options.get("fallback_on_failure", False)
    if data.get("candidate_order") != candidates or data.get("fallback_on_failure") != fallback:
        raise OutputContractError("AUTO candidate order or fallback binding is invalid")
    if not isinstance(candidates, list) or not candidates or data.get("initial_selection") not in candidates:
        raise OutputContractError("AUTO initial selection is invalid")
    selected_index = DeterministicRNG(_typed_seed_value(result_dict.get("seed"), "generation.result.seed")).child("auto/selection").randbelow(len(candidates))
    if data.get("initial_selection") != candidates[selected_index]:
        raise OutputContractError("AUTO initial selection is not bound to the root seed")
    attempts = data.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        raise OutputContractError("AUTO attempt metadata is missing")
    initial = data["initial_selection"]
    start = candidates.index(initial)
    expected_modes = candidates[start:] + candidates[:start] if fallback else [initial]
    if [item.get("mode") for item in attempts if isinstance(item, Mapping)] != expected_modes[: len(attempts)]:
        raise OutputContractError("AUTO attempt order does not match configured fallback semantics")
    retry_seeds = _mapping_copy(_retry_provenance(result_dict).get("retry_seeds"), "AUTO result retry provenance")
    expected_retry_keys = {str(index) for index in range(len(attempts))}
    if set(retry_seeds) != expected_retry_keys or len(retry_seeds) != len(attempts):
        raise OutputContractError("AUTO attempt count does not match the GenerationResult retry provenance")
    successful: list[Mapping[str, object]] = []
    for index, raw_attempt in enumerate(attempts):
        attempt = _mapping_copy(raw_attempt, f"auto.attempts[{index}]")
        mode = attempt.get("mode")
        expected_seed = DeterministicRNG(_typed_seed_value(result_dict.get("seed"), "generation.result.seed")).child(f"auto/{mode}/{index}").next_bytes(32).hex()
        if attempt.get("stage_seed") != expected_seed:
            raise OutputContractError("AUTO stage seed is not deterministic for the configured attempt")
        digest = attempt.get("result_digest")
        if digest is not None and (type(digest) is not str or _DIGEST.fullmatch(digest) is None):
            raise OutputContractError("AUTO attempt result digest is malformed")
        if digest is not None:
            successful.append(attempt)
        elif not attempt.get("failure_code"):
            raise OutputContractError("AUTO unsuccessful attempt lacks a failure code")
    if len(successful) != 1 or not isinstance(attempts[-1], Mapping) or attempts[-1].get("result_digest") is None:
        raise OutputContractError("AUTO export must identify exactly one successful selected attempt")
    selected = successful[0]
    if data.get("selected_engine_id") != selected.get("engine_id") or data.get("selected_engine_version") != selected.get("engine_version"):
        raise OutputContractError("AUTO selected engine binding is invalid")
    generator = _mapping_copy(result_dict.get("generator"), "generation.result.generator")
    if selected.get("engine_id") != generator.get("id") or selected.get("engine_version") != generator.get("version"):
        raise OutputContractError("AUTO selected engine does not match the exported result")


def _validate_evaluator_guided_metadata(data: Mapping[str, object], result_dict: Mapping[str, object], artwork: ArtworkArtifact) -> None:
    required_metadata = {
        "schema", "version", "request_digest", "policy", "policy_digest", "candidate_order",
        "fallback_on_failure", "attempts", "selected_index", "selected_result_digest",
        "selected_grid_hash", "selected_quality", "selected_engine_id", "selected_engine_version",
        "selection_class",
    }
    if set(data) != required_metadata or data.get("schema") != "scrubbots-evaluator-guided-metadata":
        raise OutputContractError("evaluator-guided metadata has unsupported or missing fields")
    if data.get("version") != 1 or data.get("selection_class") != "TEST":
        raise OutputContractError("evaluator-guided metadata version or candidate class is invalid")
    request, options = _request_parts(result_dict)
    raw_policy = options.get("evaluator_guided")
    policy = _mapping_copy(raw_policy, "AUTO evaluator policy")
    if set(policy) != {"version", "proposal_budget", "quality_policy"} or type(policy.get("version")) is not int or policy.get("version") != 1:
        raise OutputContractError("evaluator-guided policy is malformed")
    budget = policy.get("proposal_budget")
    if type(budget) is not int or not 2 <= budget <= 8:
        raise OutputContractError("evaluator-guided proposal budget is invalid")
    if data.get("request_digest") != hashlib.sha256(canonical_json_bytes(request)).hexdigest():
        raise OutputContractError("evaluator-guided request digest is invalid")
    if data.get("policy") != policy or data.get("candidate_order") != options.get("candidates", ["MASK", "RULES"]):
        raise OutputContractError("evaluator-guided policy or generator order differs from request")
    fallback = options.get("fallback_on_failure", False)
    if type(fallback) is not bool or data.get("fallback_on_failure") != fallback:
        raise OutputContractError("evaluator-guided fallback binding is invalid")
    policy_digest = hashlib.sha256(canonical_json_bytes(policy)).hexdigest()
    if data.get("policy_digest") != policy_digest:
        raise OutputContractError("evaluator-guided policy digest is invalid")
    try:
        policy_values = _mapping_copy(policy.get("quality_policy"), "M07 policy")
        quality_policy = QualityPolicy(**policy_values)
    except (TypeError, ValueError) as exc:
        raise OutputContractError(f"evaluator-guided M07 policy is invalid: {exc}") from exc
    if quality_policy.difficulty is not None:
        raise OutputContractError("evaluator-guided M07 policy difficulty must be null for modern LEVEL_ART")
    if canonical_json_bytes(quality_policy.as_dict()) != canonical_json_bytes(policy_values):
        raise OutputContractError("evaluator-guided M07 policy must use its canonical representation")
    attempts = data.get("attempts")
    if not isinstance(attempts, list) or len(attempts) != budget:
        raise OutputContractError("evaluator-guided attempt count differs from bounded budget")
    seed = _typed_seed_value(result_dict.get("seed"), "generation.result.seed")
    candidates = data.get("candidate_order")
    if not isinstance(candidates, list) or not candidates:
        raise OutputContractError("evaluator-guided generator order is malformed")
    eligible: list[tuple[tuple[object, ...], int, Mapping[str, object]]] = []
    for index, raw in enumerate(attempts):
        attempt = _mapping_copy(raw, f"evaluator_guided.attempts[{index}]")
        if set(attempt) != {"index", "mode", "seed", "result", "result_digest", "quality", "failure_code"}:
            raise OutputContractError("evaluator-guided attempt has unsupported or missing fields")
        if attempt.get("index") != index or attempt.get("mode") != candidates[index % len(candidates)]:
            raise OutputContractError("evaluator-guided attempt order is invalid")
        expected_seed = DeterministicRNG(seed).child(f"evaluator-guided/proposal/{index}").next_bytes(32).hex()
        if attempt.get("seed") != expected_seed:
            raise OutputContractError("evaluator-guided proposal seed is not derived from the request seed")
        raw_result = attempt.get("result")
        if raw_result is None:
            if attempt.get("quality") is not None or not attempt.get("failure_code") or attempt.get("result_digest") is not None:
                raise OutputContractError("evaluator-guided failed proposal evidence is malformed")
            continue
        proposal = _mapping_copy(raw_result, f"evaluator_guided.attempts[{index}].result")
        if set(proposal) != {"schema", "schema_version", "status", "request", "resolved_dimensions", "logical_grid", "used_palette", "generator", "seed", "rng"} or proposal.get("status") != "SUCCESS":
            raise OutputContractError("evaluator-guided proposal result has unsupported or incomplete fields")
        if hashlib.sha256(canonical_json_bytes(proposal)).hexdigest() != attempt.get("result_digest"):
            raise OutputContractError("evaluator-guided proposal result digest is invalid")
        typed_proposal_seed = proposal.get("seed")
        if _typed_seed_value(typed_proposal_seed, "proposal.seed") != expected_seed:
            raise OutputContractError("evaluator-guided proposal result is bound to another seed")
        proposal_request = _mapping_copy(proposal.get("request"), "proposal.request")
        proposal_generator = _mapping_copy(proposal.get("generator"), "proposal.generator")
        if _typed_seed_value(proposal_request.get("seed"), "proposal.request.seed") != expected_seed or proposal_request.get("generator_mode") != attempt.get("mode") or proposal_generator.get("mode") != attempt.get("mode"):
            raise OutputContractError("evaluator-guided proposal request or engine identity is inconsistent")
        proposal_grid = proposal.get("logical_grid")
        dimensions = proposal.get("resolved_dimensions")
        if not isinstance(dimensions, Mapping):
            raise OutputContractError("evaluator-guided proposal dimensions are missing")
        report = evaluate_grid(dimensions.get("width"), dimensions.get("height"), proposal_grid, policy=quality_policy)
        if report.as_dict() != attempt.get("quality"):
            raise OutputContractError("evaluator-guided M07 evidence does not match proposal grid and policy")
        if report.accepted:
            metrics = report.analysis.metrics if report.analysis is not None else None
            rank = (len(report.rejection_codes), metrics.tiny_region_count, metrics.isolated_occupied_count, abs(metrics.occupied_ratio - 0.45), -metrics.aggregate_symmetry_score, logical_grid_hash(dimensions["width"], dimensions["height"], proposal_grid))
            eligible.append((rank, index, proposal))
    if not eligible:
        raise OutputContractError("evaluator-guided metadata has no accepted proposal")
    _, winner_index, winner = min(eligible, key=lambda item: item[0])
    if data.get("selected_index") != winner_index or data.get("selected_result_digest") != attempts[winner_index].get("result_digest"):
        raise OutputContractError("evaluator-guided selection is not the deterministic quality winner")
    winner_grid = winner.get("logical_grid")
    generator = _mapping_copy(result_dict.get("generator"), "generation.result.generator")
    winner_generator = _mapping_copy(winner.get("generator"), "proposal.generator")
    if winner_grid != result_dict.get("logical_grid") or winner_generator.get("id") != generator.get("id") or winner_generator.get("version") != generator.get("version"):
        raise OutputContractError("evaluator-guided selected proposal differs from exported result")
    if data.get("selected_grid_hash") != artwork.grid_hash or data.get("selected_quality") != attempts[winner_index].get("quality"):
        raise OutputContractError("evaluator-guided winner hash or quality evidence is not bound to artwork")
    if data.get("selected_engine_id") != generator.get("id") or data.get("selected_engine_version") != generator.get("version"):
        raise OutputContractError("evaluator-guided selected generator identity is invalid")


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
    generator_metadata: Mapping[str, object] | None = None,
) -> ExportBundle:
    """Build deterministic bytes from a result or wrapper.

    Rich WFC/HYBRID/AUTO results require their candidate wrapper, or an
    explicit authoritative ``generator_metadata`` mapping. The explicit form
    may be either the wrapper's ``{"namespace": ..., "data": ...}`` payload
    or the raw mode-specific metadata mapping.
    """

    result, candidate_metadata = _candidate_payload(candidate, generator_metadata)
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
        metadata = _validate_metadata(metadata, artwork)
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
    if result_dict.get("logical_grid") != list(artwork.cells) or result_dict.get("used_palette") != list(artwork.palette) or result_dict.get("resolved_dimensions") != {"width": artwork.width, "height": artwork.height}:
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
    classification = generator_metadata.get("classification")
    payload = _mapping_copy(generator_metadata["payload"], "metadata.generator_metadata.payload")
    owner_source_sha256 = _verified_owner_upload_sha256(
        _mapping_copy(_mapping_copy(value["generation"], "metadata.generation").get("result"), "metadata.generation.result"),
        artwork.candidate_id,
        artwork,
        payload,
    )
    if owner_source_sha256 is not None and classification is None:
        # Older immutable owner-upload bundles predate the persisted
        # classification field. Reconstruct the same deterministic projection
        # only after the source bytes and logical grid have been verified above;
        # never write this compatibility projection back into the bundle.
        try:
            classification = build_verified_owner_upload_classification(
                result_dict,
                candidate_id=artwork.candidate_id,
                grid_hash=artwork.grid_hash,
                generator_metadata=payload,
                verified_source_sha256=owner_source_sha256,
            )
        except CandidateProvenanceError as exc:
            raise OutputContractError(str(exc)) from exc
        generator_metadata["classification"] = classification
        value["generator_metadata"] = generator_metadata
    if classification is not None:
        try:
            if owner_source_sha256 is None:
                validate_candidate_classification(
                    classification,
                    result_dict,
                    candidate_id=artwork.candidate_id,
                    grid_hash=artwork.grid_hash,
                    generator_metadata=payload,
                )
            else:
                validate_verified_owner_upload_classification(
                    classification,
                    result_dict,
                    candidate_id=artwork.candidate_id,
                    grid_hash=artwork.grid_hash,
                    generator_metadata=payload,
                    verified_source_sha256=owner_source_sha256,
                )
        except CandidateProvenanceError as exc:
            raise OutputContractError(str(exc)) from exc
    generator_mode = generation.get("generator_mode")
    if generator_mode in _RICH_MODES:
        payload = generator_metadata["payload"]
        namespace = payload.get("namespace") if isinstance(payload, Mapping) else None
        if namespace != _RICH_NAMESPACES[generator_mode]:
            raise OutputContractError("rich generator metadata namespace does not match the generating mode")
        data = _mapping_copy(payload.get("data") if isinstance(payload, Mapping) else None, "metadata.generator_metadata.data")
        if generator_mode == "WFC":
            _validate_wfc_metadata(data, result_dict, artwork)
        elif generator_mode == "HYBRID":
            _validate_hybrid_metadata(data, result_dict, artwork)
        elif generator_mode == "ART_FIRST":
            from ..generators.router.art_first import validate_art_first_bundle

            validate_art_first_bundle(result_dict, payload, artwork.as_dict())
        else:
            _validate_auto_metadata(data, result_dict, artwork)
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
        metadata = _validate_metadata(metadata, artwork)
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
    generator_metadata: Mapping[str, object] | None = None,
) -> Path:
    return write_bundle(build_export_bundle(candidate, candidate_id, quality_report=quality_report, preview_scale=preview_scale, generator_metadata=generator_metadata), destination)


def export_result(
    result: GenerationResult,
    candidate_id: str,
    destination: str | os.PathLike[str],
    *,
    quality_report: QualityReport | None = None,
    preview_scale: int | None = None,
    generator_metadata: Mapping[str, object] | None = None,
) -> Path:
    return export_candidate(result, candidate_id, destination, quality_report=quality_report, preview_scale=preview_scale, generator_metadata=generator_metadata)


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
