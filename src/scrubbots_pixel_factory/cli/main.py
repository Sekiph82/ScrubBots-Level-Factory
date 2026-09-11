"""Standard-library, offline CLI for single and finite batch generation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import IntEnum
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import secrets
import sys
import tempfile
from typing import Any

from .. import (
    DeterministicRNG,
    GenerationRequest,
    GeneratorMode,
    GeneratorOptions,
    GeneratorRouter,
    FailureCode,
    QualityPolicy,
    ReviewEntry,
    evaluate_grid,
    logical_grid_hash,
    write_review_pack,
)
from ..core.request import RequestContractError
from ..core.result import GenerationResult
from ..generators.mask import MaskCandidate
from ..generators.rules import RuleCandidate
from ..generators.router import AutoCandidate, HybridCandidate
from ..generators.wfc import Exemplar, ExemplarRegistry, WFCCandidate, WFCContractError, WFCGenerator
from ..output import (
    ArtworkArtifact,
    OutputContractError,
    build_export_bundle,
    canonical_json_bytes,
    export_candidate,
    read_bundle,
)


class ExitCode(IntEnum):
    SUCCESS = 0
    USAGE = 2
    INVALID_REQUEST = 3
    GENERATION_FAILURE = 4
    QUALITY_REJECTED = 5
    REPRODUCE_MISMATCH = 6
    BATCH_EXHAUSTED = 7
    FILESYSTEM = 8


_SEED_TOKEN = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
_MANIFEST_SCHEMA = "scrubbots-batch-manifest"
_MANIFEST_VERSION = 1
_BATCH_MODES = {mode.value for mode in GeneratorMode}
_CANDIDATE_TYPES = (MaskCandidate, RuleCandidate, WFCCandidate, HybridCandidate, AutoCandidate)
_ATTEMPT_FIELDS = {
    "attempt_index", "attempt_seed", "status", "failure_code", "quality_decision",
    "rejection_codes", "grid_hash", "duplicate_of", "candidate_id", "relative_path",
    "width", "height",
}
_ACCEPTED_FIELDS = {"attempt_index", "attempt_seed", "candidate_id", "grid_hash", "relative_path", "width", "height"}
_ATTEMPT_STATUSES = {"GENERATOR_FAILURE", "QUALITY_REJECTED", "DUPLICATE", "ACCEPTED"}
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_PORTABLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class CLIError(ValueError):
    """Expected user-facing CLI failure with a stable exit code."""

    def __init__(self, message: str, code: ExitCode = ExitCode.INVALID_REQUEST) -> None:
        super().__init__(message)
        self.code = code


def _json_load(path: Path, label: str) -> object:
    if not _is_local_path(path):
        raise CLIError(f"{label} must be a local filesystem path")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CLIError(f"cannot read {label}: {exc}", ExitCode.FILESYSTEM) from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CLIError(f"{label} is not valid UTF-8 JSON: {exc}") from exc


def _is_local_path(path: Path) -> bool:
    value = str(path)
    return "://" not in value and not value.lower().startswith(("http:", "https:"))


def _canonical_seed(token: str) -> int | str:
    return int(token) if _SEED_TOKEN.fullmatch(token) else token


def _typed_seed(seed: int | str) -> dict[str, int | str]:
    return {"type": "int", "value": seed} if isinstance(seed, int) else {"type": "string", "value": seed}


def _parse_typed_seed(value: object, path: str) -> int | str:
    if not isinstance(value, Mapping) or set(value) != {"type", "value"}:
        raise CLIError(f"{path} must be a typed seed")
    kind = value.get("type")
    raw = value.get("value")
    if kind == "int" and type(raw) is int:
        return raw
    if kind == "string" and type(raw) is str:
        return raw
    raise CLIError(f"{path} has an invalid type/value pair")


def _options_from_json(path: Path | None, mode: str) -> GeneratorOptions:
    if path is None:
        return GeneratorOptions(mode.lower(), 1, {})
    value = _json_load(path, "options JSON")
    if not isinstance(value, Mapping) or set(value) != {"namespace", "version", "values"}:
        raise CLIError("options JSON must contain exactly namespace, version, and values")
    try:
        return GeneratorOptions(value["namespace"], value["version"], value["values"])  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise CLIError(f"invalid generator options: {exc}") from exc


def _palette_from_text(value: str | None) -> tuple[str, ...] | None:
    if value is None:
        return None
    parts = tuple(part.strip() for part in value.split(","))
    if not parts or any(not part for part in parts):
        raise CLIError("--palette must be a comma-separated list of C01..C16 IDs")
    return parts


def _load_exemplars(path: Path | None) -> ExemplarRegistry:
    if path is None:
        return ExemplarRegistry()
    raw = _json_load(path, "exemplar JSON")
    if isinstance(raw, Mapping) and set(raw) == {"exemplars"}:
        records = raw["exemplars"]
    else:
        records = raw
    if isinstance(records, Mapping):
        records = [records]
    if not isinstance(records, list) or not records:
        raise CLIError("exemplar JSON must contain one or more exemplar objects")
    allowed = {
        "schema", "version", "exemplar_id", "role", "width", "height", "pixels",
        "provenance_type", "provenance_description", "ownership", "approved_by",
        "production_difficulty", "difficulty_context",
    }
    exemplars: list[Exemplar] = []
    for index, record in enumerate(records):
        if not isinstance(record, Mapping) or set(record) - allowed:
            raise CLIError(f"exemplar {index} has unsupported or malformed fields")
        production_difficulty = record.get("production_difficulty")
        context = record.get("difficulty_context")
        if production_difficulty is not None and context is not None and production_difficulty != context:
            raise CLIError(f"exemplar {index} has conflicting production difficulty fields")
        try:
            exemplar = Exemplar(
                record["schema"], record["version"], record["exemplar_id"], record["role"],
                record["width"], record["height"], tuple(record["pixels"]),
                record["provenance_type"], record["provenance_description"], record["ownership"],
                record.get("approved_by"), production_difficulty if production_difficulty is not None else context,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise CLIError(f"exemplar {index} violates the M05 contract: {exc}") from exc
        exemplars.append(exemplar)
    try:
        return ExemplarRegistry(exemplars)
    except WFCContractError as exc:
        raise CLIError(f"exemplar registry is invalid: {exc}") from exc


def _exemplar_identities(registry: ExemplarRegistry) -> list[dict[str, object]]:
    return [
        {
            "exemplar_id": exemplar.exemplar_id,
            "digest": exemplar.digest,
            "role": exemplar.role,
            "provenance_identity": exemplar.provenance_identity,
            "ownership": exemplar.ownership,
            "schema": exemplar.schema,
            "version": exemplar.version,
            "width": exemplar.width,
            "height": exemplar.height,
            "provenance_type": exemplar.provenance_type,
            "provenance_description": exemplar.provenance_description,
            "approved_by": exemplar.approved_by,
            "production_difficulty": exemplar.production_difficulty,
        }
        for exemplar in registry.exemplars
    ]


def _router(registry: ExemplarRegistry) -> GeneratorRouter:
    return GeneratorRouter(wfc_generator=WFCGenerator(registry))


def _candidate_result(candidate: object) -> GenerationResult:
    result = candidate if isinstance(candidate, GenerationResult) else getattr(candidate, "result", None)
    if not isinstance(result, GenerationResult):
        raise CLIError("generator returned an invalid result", ExitCode.GENERATION_FAILURE)
    return result


def _candidate_id(request: GenerationRequest, explicit: str | None = None) -> str:
    return explicit if explicit is not None else f"candidate-{request.digest()}"


def _quality_policy(request: GenerationRequest) -> QualityPolicy:
    return QualityPolicy(difficulty=request.difficulty)


def _quality_policy_from_json(path: Path | None, request: GenerationRequest) -> QualityPolicy:
    if path is None:
        return _quality_policy(request)
    value = _json_load(path, "quality policy JSON")
    if not isinstance(value, Mapping):
        raise CLIError("quality policy JSON must be an object")
    try:
        policy = QualityPolicy(**value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise CLIError(f"invalid quality policy: {exc}") from exc
    if policy.as_dict() != dict(value):
        raise CLIError("quality policy JSON is not the canonical versioned policy")
    if policy.difficulty is None or policy.difficulty.value != request.difficulty.value:
        raise CLIError("quality policy difficulty must match the generation request")
    return policy


def _request_from_canonical(value: object, path: str = "request") -> GenerationRequest:
    if not isinstance(value, Mapping):
        raise CLIError(f"{path} must be an object")
    required = {"schema", "schema_version", "difficulty", "width", "height", "seed", "generator_mode", "style", "theme", "palette_subset", "generator_options"}
    if set(value) != required or value.get("schema") != "scrubbots-generation-request" or value.get("schema_version") != 1:
        raise CLIError(f"{path} schema/version or fields are unsupported")
    seed = _parse_typed_seed(value.get("seed"), f"{path}.seed")
    options = value.get("generator_options")
    if not isinstance(options, Mapping) or set(options) != {"namespace", "version", "values"}:
        raise CLIError(f"{path}.generator_options is not the accepted versioned contract")
    try:
        return GenerationRequest(
            value["difficulty"], seed, value["generator_mode"],
            width=value["width"], height=value["height"], style=value["style"], theme=value["theme"],
            palette_subset=value["palette_subset"], generator_options=GeneratorOptions(options["namespace"], options["version"], options["values"]),
        )  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise CLIError(f"{path} violates the request contract: {exc}") from exc


def _request_from_args(args: argparse.Namespace, *, seed: int | str | None = None) -> GenerationRequest:
    mode = getattr(args, "mode", None)
    difficulty = getattr(args, "difficulty", None)
    if difficulty is None or mode is None:
        raise CLIError("--difficulty and --mode are required")
    chosen_seed = seed if seed is not None else _canonical_seed(args.seed) if args.seed is not None else None
    if chosen_seed is None:
        chosen_seed = secrets.randbits(128)
    try:
        return GenerationRequest(
            difficulty, chosen_seed, mode, width=args.width, height=args.height,
            style=args.style, theme=args.theme, palette_subset=_palette_from_text(args.palette),
            generator_options=_options_from_json(args.options_json, mode),
        )
    except (TypeError, ValueError, RequestContractError) as exc:
        raise CLIError(f"invalid generation request: {exc}") from exc


def _summary(result: GenerationResult, candidate_id: str, output: Path, *, prefix: str = "SUCCESS") -> str:
    assert result.width is not None and result.height is not None and result.logical_grid is not None
    return (
        f"{prefix} candidate_id={candidate_id} seed={json.dumps(_typed_seed(result.seed), sort_keys=True, separators=(',', ':'))} "
        f"mode={result.generator_mode} dimensions={result.width}x{result.height} "
        f"grid_hash={logical_grid_hash(result.width, result.height, result.logical_grid)} output={output}"
    )


def _generate(args: argparse.Namespace) -> ExitCode:
    registry = _load_exemplars(args.exemplar_json)
    request = _request_from_args(args)
    candidate = _router(registry).generate_candidate(request)
    result = _candidate_result(candidate)
    if not result.is_success:
        print(f"GENERATION_FAILURE code={result.failure_code.value if result.failure_code else 'GENERATION_FAILED'}", file=sys.stderr)
        return ExitCode.GENERATION_FAILURE
    report = evaluate_grid(result.width, result.height, result.logical_grid, policy=_quality_policy_from_json(args.quality_policy_json, request))  # type: ignore[arg-type]
    if not report.accepted:
        print(f"QUALITY_REJECTED codes={','.join(report.rejection_codes)}", file=sys.stderr)
        return ExitCode.QUALITY_REJECTED
    candidate_id = _candidate_id(request, args.candidate_id)
    try:
        destination = export_candidate(candidate, candidate_id, args.output, quality_report=report, preview_scale=args.preview_scale)
    except (OSError, TypeError, ValueError) as exc:
        raise CLIError(f"could not export candidate: {exc}", ExitCode.FILESYSTEM) from exc
    print(f"seed_selected={json.dumps(_typed_seed(request.seed), sort_keys=True, separators=(',', ':'))}")
    print(_summary(result, candidate_id, destination))
    return ExitCode.SUCCESS


def _bundle_from_metadata_path(path: Path):
    if path.name != "metadata.json":
        raise CLIError("reproduce input must be a candidate metadata.json file")
    try:
        return read_bundle(path.parent)
    except (OSError, TypeError, ValueError) as exc:
        raise CLIError(f"metadata bundle is invalid: {exc}", ExitCode.REPRODUCE_MISMATCH) from exc


def _reproduce(args: argparse.Namespace) -> ExitCode:
    bundle = _bundle_from_metadata_path(args.metadata)
    request = _request_from_canonical(bundle.metadata.get("generation", {}).get("request"), "metadata.generation.request")  # type: ignore[union-attr]
    registry = _load_exemplars(args.exemplar_json)
    candidate = _router(registry).generate_candidate(request)
    result = _candidate_result(candidate)
    reproduced_hash = logical_grid_hash(result.width, result.height, result.logical_grid) if result.is_success else None  # type: ignore[arg-type]
    if not result.is_success or reproduced_hash != bundle.artwork.grid_hash or result.logical_grid != bundle.artwork.cells:
        print("MISMATCH", file=sys.stderr)
        return ExitCode.REPRODUCE_MISMATCH
    try:
        quality = bundle.metadata["quality"]
        if not isinstance(quality, Mapping):
            raise CLIError("metadata quality binding is malformed", ExitCode.REPRODUCE_MISMATCH)
        recorded = quality.get("report")
        if not isinstance(recorded, Mapping):
            raise CLIError("metadata quality report is missing", ExitCode.REPRODUCE_MISMATCH)
        policy_data = recorded.get("policy")
        if not isinstance(policy_data, Mapping):
            raise CLIError("metadata quality policy is missing", ExitCode.REPRODUCE_MISMATCH)
        policy = QualityPolicy(**policy_data)  # type: ignore[arg-type]
        if policy.as_dict() != dict(policy_data):
            raise CLIError("metadata quality policy is not canonical", ExitCode.REPRODUCE_MISMATCH)
        report = evaluate_grid(result.width, result.height, result.logical_grid, policy=policy)  # type: ignore[arg-type]
        if report.as_dict() != dict(recorded):
            raise CLIError("metadata quality report does not reproduce under its recorded policy", ExitCode.REPRODUCE_MISMATCH)
        if quality.get("decision") != ("ACCEPT" if report.accepted else "REJECT") or quality.get("rejection_codes") != list(report.rejection_codes):
            raise CLIError("metadata quality decision binding is invalid", ExitCode.REPRODUCE_MISMATCH)
    except CLIError:
        raise
    except (TypeError, ValueError) as exc:
        raise CLIError(f"metadata quality policy is invalid: {exc}", ExitCode.REPRODUCE_MISMATCH) from exc
    try:
        regenerated = build_export_bundle(candidate, bundle.artwork.candidate_id, quality_report=report, preview_scale=(bundle.metadata.get("preview") or {}).get("scale") if (bundle.metadata.get("preview") or {}).get("enabled") else None)  # type: ignore[union-attr]
    except (OSError, TypeError, ValueError) as exc:
        raise CLIError(f"reproduction could not rebuild the accepted bundle: {exc}", ExitCode.REPRODUCE_MISMATCH) from exc
    if regenerated.metadata_json != bundle.metadata_json or regenerated.artwork_json != bundle.artwork_json or regenerated.artwork_png != bundle.artwork_png or regenerated.preview_png != bundle.preview_png:
        print("MISMATCH", file=sys.stderr)
        return ExitCode.REPRODUCE_MISMATCH
    if args.output is not None:
        try:
            destination = export_candidate(candidate, bundle.artwork.candidate_id, args.output, quality_report=report, preview_scale=(bundle.metadata.get("preview") or {}).get("scale") if (bundle.metadata.get("preview") or {}).get("enabled") else None)  # type: ignore[union-attr]
        except (OSError, TypeError, ValueError) as exc:
            raise CLIError(f"could not export reproduced bundle: {exc}", ExitCode.FILESYSTEM) from exc
    else:
        destination = bundle.artwork.candidate_id
    print(_summary(result, bundle.artwork.candidate_id, Path(destination), prefix="MATCH"))
    return ExitCode.SUCCESS


def _manifest_bytes(value: Mapping[str, object]) -> bytes:
    return canonical_json_bytes(value) + b"\n"


def _atomic_manifest_write(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(_manifest_bytes(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise CLIError(f"could not write batch manifest: {exc}", ExitCode.FILESYSTEM) from exc


def _batch_config(args: argparse.Namespace, seed: int | str, registry: ExemplarRegistry) -> tuple[GenerationRequest, dict[str, object]]:
    request = _request_from_args(args, seed=seed)
    return request, _request_template(request)


def _request_template(request: GenerationRequest) -> dict[str, object]:
    config = {
        "difficulty": request.difficulty.value,
        "width": request.width,
        "height": request.height,
        "generator_mode": request.generator_mode,
        "style": request.style,
        "theme": request.theme,
        "palette_subset": list(request.palette_subset) if request.palette_subset is not None else None,
        "generator_options": request.options.canonical_dict(),
    }
    return config


def _batch_id(
    config: Mapping[str, object],
    seed: int | str,
    count: int,
    max_attempts: int,
    exemplar_identities: Sequence[Mapping[str, object]],
    quality_policy: Mapping[str, object],
) -> str:
    immutable = {
        "request_template": config,
        "root_seed": _typed_seed(seed),
        "requested_count": count,
        "max_attempts": max_attempts,
        "exemplar_identities": list(exemplar_identities),
        "quality_policy": quality_policy,
    }
    return f"batch-{hashlib.sha256(canonical_json_bytes(immutable)).hexdigest()}"


def _batch_candidate_id(manifest_or_batch_id: Mapping[str, object] | str, attempt_index: int) -> str:
    """Return the sole deterministic identity formula for an accepted batch attempt."""
    batch_id = manifest_or_batch_id.get("batch_id") if isinstance(manifest_or_batch_id, Mapping) else manifest_or_batch_id
    if type(batch_id) is not str or not batch_id or type(attempt_index) is not int or attempt_index < 0:
        raise CLIError("batch candidate identity inputs are invalid")
    return f"{batch_id}-{attempt_index:06d}"


def _safe_relative_path(value: object, label: str) -> Path:
    if type(value) is not str or not value or "\\" in value:
        raise CLIError(f"{label} is not a portable relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise CLIError(f"{label} escapes the batch root")
    return path


def _validate_manifest(value: object, path: Path) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise CLIError("batch manifest root must be an object")
    required = {"schema", "version", "batch_id", "requested_count", "max_attempts", "root_seed", "request_template", "exemplar_identities", "quality_policy", "next_attempt_index", "attempts", "accepted", "accepted_count", "terminal_state"}
    if set(value) != required or value.get("schema") != _MANIFEST_SCHEMA or value.get("version") != _MANIFEST_VERSION:
        raise CLIError("unsupported or incomplete batch manifest")
    if path.name != "batch-manifest.json":
        raise CLIError("resume input must be named batch-manifest.json")
    if type(value["requested_count"]) is not int or value["requested_count"] <= 0 or type(value["max_attempts"]) is not int or value["max_attempts"] <= 0:
        raise CLIError("batch manifest counts are invalid")
    if type(value["next_attempt_index"]) is not int or not 0 <= value["next_attempt_index"] <= value["max_attempts"]:
        raise CLIError("batch manifest next attempt index is invalid")
    if type(value["accepted_count"]) is not int or not 0 <= value["accepted_count"] <= value["requested_count"]:
        raise CLIError("batch manifest accepted count is invalid")
    if value["terminal_state"] not in {"IN_PROGRESS", "COMPLETE", "EXHAUSTED"}:
        raise CLIError("batch manifest terminal state is invalid")
    if not isinstance(value["attempts"], list) or not isinstance(value["accepted"], list) or not isinstance(value["exemplar_identities"], list):
        raise CLIError("batch manifest ordered sections are malformed")
    template = value["request_template"]
    if not isinstance(template, Mapping) or set(template) != {"difficulty", "width", "height", "generator_mode", "style", "theme", "palette_subset", "generator_options"}:
        raise CLIError("batch manifest request template is malformed")
    if not isinstance(template["generator_options"], Mapping) or set(template["generator_options"]) != {"namespace", "version", "values"}:
        raise CLIError("batch manifest generator options are malformed")
    root_seed = _parse_typed_seed(value["root_seed"], "manifest.root_seed")
    try:
        first_request = _request_from_manifest(dict(value), DeterministicRNG(root_seed).retry_seed(0))
        if template != _request_template(first_request):
            raise CLIError("batch manifest request template is not canonical")
        policy_data = value["quality_policy"]
        if not isinstance(policy_data, Mapping):
            raise CLIError("batch manifest quality policy is malformed")
        policy = QualityPolicy(**policy_data)  # type: ignore[arg-type]
        if policy.as_dict() != dict(policy_data) or policy.difficulty is None or policy.difficulty.value != first_request.difficulty.value:
            raise CLIError("batch manifest quality policy is not the exact request policy")
    except (TypeError, ValueError) as exc:
        raise CLIError(f"batch manifest contains an invalid immutable contract: {exc}") from exc
    exemplar_fields = {
        "exemplar_id", "digest", "role", "provenance_identity", "ownership", "schema", "version",
        "width", "height", "provenance_type", "provenance_description", "approved_by", "production_difficulty",
    }
    for index, identity in enumerate(value["exemplar_identities"]):
        if not isinstance(identity, Mapping) or set(identity) != exemplar_fields:
            raise CLIError(f"manifest exemplar identity {index} is incomplete")
        if type(identity["exemplar_id"]) is not str or type(identity["digest"]) is not str or not _DIGEST.fullmatch(identity["digest"]):
            raise CLIError(f"manifest exemplar identity {index} is malformed")
        if type(identity["schema"]) is not str or identity["schema"] != "scrubbots-wfc-exemplar" or identity["version"] != 1:
            raise CLIError(f"manifest exemplar identity {index} has an unsupported schema")
        if type(identity["width"]) is not int or type(identity["height"]) is not int or identity["width"] < 2 or identity["height"] < 2:
            raise CLIError(f"manifest exemplar identity {index} has invalid dimensions")
    expected_batch_id = _batch_id(
        template, root_seed, int(value["requested_count"]), int(value["max_attempts"]),
        value["exemplar_identities"], value["quality_policy"],  # type: ignore[arg-type]
    )
    if value["batch_id"] != expected_batch_id:
        raise CLIError("batch manifest identity does not match its complete immutable configuration")
    if len(value["attempts"]) != value["next_attempt_index"]:
        raise CLIError("batch manifest attempts are not contiguous with next_attempt_index")
    accepted = value["accepted"]
    if len(accepted) != value["accepted_count"]:
        raise CLIError("batch manifest accepted count is inconsistent")
    accepted_attempts: list[Mapping[str, object]] = []
    accepted_ids_so_far: set[str] = set()
    for index, record in enumerate(value["attempts"]):
        if not isinstance(record, Mapping) or set(record) != _ATTEMPT_FIELDS or record.get("attempt_index") != index:
            raise CLIError("batch manifest attempt history is not ordered or complete")
        if record["attempt_seed"] != _typed_seed(DeterministicRNG(root_seed).retry_seed(index)):
            raise CLIError(f"attempt {index} seed is not derived from the manifest root seed")
        status = record["status"]
        if status not in _ATTEMPT_STATUSES:
            raise CLIError(f"attempt {index} has an unsupported status")
        if type(record["rejection_codes"]) is not list or any(type(code) is not str or not code for code in record["rejection_codes"]):
            raise CLIError(f"attempt {index} rejection codes are malformed")
        request = _request_from_manifest(dict(value), _parse_typed_seed(record["attempt_seed"], f"attempts[{index}].attempt_seed"))
        expected_width, expected_height = request.resolve_dimensions()
        if status == "GENERATOR_FAILURE":
            if type(record["failure_code"]) is not str or record["failure_code"] not in {code.value for code in FailureCode}:
                raise CLIError(f"attempt {index} failure code is invalid")
            if any(record[key] is not None for key in ("quality_decision", "grid_hash", "duplicate_of", "candidate_id", "relative_path", "width", "height")) or record["rejection_codes"]:
                raise CLIError(f"attempt {index} generator failure contains success data")
        else:
            if record["failure_code"] is not None or record["quality_decision"] not in {"ACCEPT", "REJECT"}:
                raise CLIError(f"attempt {index} successful result fields are malformed")
            if record["width"] != expected_width or record["height"] != expected_height or type(record["width"]) is not int or type(record["height"]) is not int:
                raise CLIError(f"attempt {index} dimensions do not match its request")
            if type(record["grid_hash"]) is not str or not _DIGEST.fullmatch(record["grid_hash"]):
                raise CLIError(f"attempt {index} grid hash is invalid")
            if status == "QUALITY_REJECTED":
                if record["quality_decision"] != "REJECT" or not record["rejection_codes"] or any(record[key] is not None for key in ("duplicate_of", "candidate_id", "relative_path")):
                    raise CLIError(f"attempt {index} quality rejection fields are inconsistent")
            elif status == "DUPLICATE":
                if record["quality_decision"] != "ACCEPT" or record["rejection_codes"] or type(record["duplicate_of"]) is not str or not _PORTABLE_ID.fullmatch(record["duplicate_of"]) or record["duplicate_of"] not in accepted_ids_so_far:
                    raise CLIError(f"attempt {index} duplicate fields are inconsistent")
                if any(record[key] is not None for key in ("candidate_id", "relative_path")):
                    raise CLIError(f"attempt {index} duplicate contains a new candidate path")
            else:
                if record["quality_decision"] != "ACCEPT" or record["rejection_codes"] or record["duplicate_of"] is not None:
                    raise CLIError(f"attempt {index} accepted fields are inconsistent")
                if type(record["candidate_id"]) is not str or not _PORTABLE_ID.fullmatch(record["candidate_id"]):
                    raise CLIError(f"attempt {index} candidate ID is invalid")
                expected_candidate_id = _batch_candidate_id(value, index)
                if record["candidate_id"] != expected_candidate_id:
                    raise CLIError(f"attempt {index} candidate ID is not deterministic for the batch")
                relative = _safe_relative_path(record["relative_path"], f"attempts[{index}].relative_path")
                if relative.as_posix() != f"candidates/{expected_candidate_id}":
                    raise CLIError(f"attempt {index} candidate path is not canonical")
                accepted_attempts.append(record)
                accepted_ids_so_far.add(record["candidate_id"])
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, record in enumerate(accepted):
        if not isinstance(record, Mapping) or set(record) != _ACCEPTED_FIELDS:
            raise CLIError("batch manifest accepted history is incomplete")
        attempt_index = record["attempt_index"]
        if type(attempt_index) is not int or not 0 <= attempt_index < len(value["attempts"]):
            raise CLIError("batch manifest accepted history index is invalid")
        attempt = value["attempts"][attempt_index]
        if not isinstance(attempt, Mapping) or attempt.get("status") != "ACCEPTED" or record != {key: attempt[key] for key in _ACCEPTED_FIELDS}:
            raise CLIError(f"accepted record {index} does not exactly match its ACCEPTED attempt")
        candidate_id = record["candidate_id"]
        relative = _safe_relative_path(record["relative_path"], f"accepted[{index}].relative_path")
        expected_candidate_id = _batch_candidate_id(value, attempt_index)
        if type(candidate_id) is not str or not _PORTABLE_ID.fullmatch(candidate_id) or candidate_id != expected_candidate_id or relative.as_posix() != f"candidates/{expected_candidate_id}":
            raise CLIError(f"accepted record {index} has a non-canonical candidate identity/path")
        if candidate_id in seen_ids or relative.as_posix() in seen_paths:
            raise CLIError("accepted candidate IDs and paths must be unique")
        seen_ids.add(candidate_id)
        seen_paths.add(relative.as_posix())
    if len(accepted_attempts) != value["accepted_count"] or [record["attempt_index"] for record in accepted_attempts] != [record["attempt_index"] for record in accepted]:
        raise CLIError("accepted records are not one-to-one with ACCEPTED attempt history")
    accepted_count = int(value["accepted_count"])
    next_index = int(value["next_attempt_index"])
    maximum = int(value["max_attempts"])
    target = int(value["requested_count"])
    expected_state = "COMPLETE" if accepted_count == target else "EXHAUSTED" if next_index == maximum else "IN_PROGRESS"
    if value["terminal_state"] != expected_state:
        raise CLIError("batch manifest terminal state is inconsistent with counts and attempt bound")
    return dict(value)


def _immutable_manifest_config(manifest: Mapping[str, object]) -> tuple[int | str, dict[str, object]]:
    seed = _parse_typed_seed(manifest["root_seed"], "manifest.root_seed")
    template = manifest["request_template"]
    if not isinstance(template, Mapping):
        raise CLIError("manifest request_template is malformed")
    return seed, dict(template)


def _resume_registry(manifest: Mapping[str, object], path: Path | None) -> ExemplarRegistry:
    registry = _load_exemplars(path)
    expected = manifest["exemplar_identities"]
    actual = _exemplar_identities(registry)
    if actual != expected:
        if expected:
            raise CLIError("resume requires the exact local exemplar identity/provenance recorded in the manifest")
        if actual:
            raise CLIError("resume exemplar input changes the immutable batch configuration")
    return registry


def _request_from_manifest(manifest: Mapping[str, object], attempt_seed: int | str) -> GenerationRequest:
    template = manifest["request_template"]
    if not isinstance(template, Mapping):
        raise CLIError("manifest request_template is malformed")
    try:
        return GenerationRequest(
            template["difficulty"], attempt_seed, template["generator_mode"], width=template["width"], height=template["height"],
            style=template["style"], theme=template["theme"], palette_subset=template["palette_subset"],
            generator_options=GeneratorOptions(**template["generator_options"]),  # type: ignore[arg-type]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise CLIError(f"manifest request template violates the request contract: {exc}") from exc


def _accepted_grids(root: Path, manifest: Mapping[str, object]) -> list[tuple[Mapping[str, object], tuple[str, ...]]]:
    output: list[tuple[Mapping[str, object], tuple[str, ...]]] = []
    for record in manifest["accepted"]:  # type: ignore[union-attr]
        relative = _safe_relative_path(record["relative_path"], "accepted.relative_path")  # type: ignore[index]
        candidate_root = (root / relative).resolve()
        if candidate_root == root.resolve() or root.resolve() not in candidate_root.parents:
            raise CLIError("accepted bundle path escapes the batch root")
        try:
            bundle = read_bundle(candidate_root)
        except (OSError, TypeError, ValueError) as exc:
            raise CLIError(f"accepted bundle is invalid during resume: {exc}") from exc
        if bundle.artwork.candidate_id != record["candidate_id"] or bundle.artwork.grid_hash != record["grid_hash"]:
            raise CLIError("accepted bundle identity or hash does not match the batch manifest")
        expected_candidate_id = _batch_candidate_id(manifest, int(record["attempt_index"]))
        if bundle.artwork.candidate_id != expected_candidate_id:
            raise CLIError("accepted bundle candidate ID is not deterministic for the batch")
        if relative.as_posix() != f"candidates/{expected_candidate_id}":
            raise CLIError("accepted bundle path is not deterministic for the batch")
        if (bundle.artwork.width, bundle.artwork.height) != (record["width"], record["height"]):
            raise CLIError("accepted bundle dimensions do not match the batch manifest")
        generation = bundle.metadata.get("generation")
        expected_request = _request_from_manifest(
            manifest, _parse_typed_seed(record["attempt_seed"], "accepted.attempt_seed")
        )
        if not isinstance(generation, Mapping) or generation.get("request") != expected_request.canonical_dict() or generation.get("seed") != record["attempt_seed"]:
            raise CLIError("accepted bundle request or seed does not match the recorded attempt")
        quality = bundle.metadata.get("quality")
        if not isinstance(quality, Mapping) or not isinstance(quality.get("report"), Mapping) or quality["report"].get("policy") != manifest["quality_policy"]:
            raise CLIError("accepted bundle quality policy is not the persisted batch policy")
        output.append((record, bundle.artwork.cells))
    return output


def _validate_attempt_history(
    manifest: Mapping[str, object],
    registry: ExemplarRegistry,
    accepted: Sequence[tuple[Mapping[str, object], tuple[str, ...]]],
) -> None:
    """Replay every recorded attempt before allowing a resume.

    The manifest is an execution journal, not merely a progress cache.  Replaying
    the bounded deterministic attempts makes edits to hashes, quality decisions,
    rejection codes, failure codes, duplicate links, and accepted relationships
    fail closed even when the edited JSON remains structurally valid.
    """
    policy = QualityPolicy(**manifest["quality_policy"])  # type: ignore[arg-type]
    accepted_by_index = {record["attempt_index"]: (record, cells) for record, cells in accepted}
    prior: list[tuple[str, tuple[str, ...], str]] = []
    router = _router(registry)
    root_seed = _parse_typed_seed(manifest["root_seed"], "manifest.root_seed")
    for index, raw_record in enumerate(manifest["attempts"]):  # type: ignore[union-attr]
        record = raw_record
        request = _request_from_manifest(manifest, DeterministicRNG(root_seed).retry_seed(index))
        candidate = router.generate_candidate(request)
        result = _candidate_result(candidate)
        if not result.is_success:
            if record["status"] != "GENERATOR_FAILURE" or record["failure_code"] != (result.failure_code.value if result.failure_code else "GENERATION_FAILED"):
                raise CLIError(f"attempt {index} does not reproduce its generator failure")
            continue
        width, height = result.width, result.height
        digest = logical_grid_hash(width, height, result.logical_grid)  # type: ignore[arg-type]
        report = evaluate_grid(width, height, result.logical_grid, policy=policy)  # type: ignore[arg-type]
        if record["width"] != width or record["height"] != height or record["grid_hash"] != digest or record["quality_decision"] != ("ACCEPT" if report.accepted else "REJECT") or record["rejection_codes"] != list(report.rejection_codes):
            raise CLIError(f"attempt {index} result, quality, or grid history does not reproduce")
        if not report.accepted:
            if record["status"] != "QUALITY_REJECTED":
                raise CLIError(f"attempt {index} is not a truthful quality rejection")
            continue
        duplicate = next(((candidate_id, grid) for prior_hash, grid, candidate_id in prior if prior_hash == digest and grid == result.logical_grid), None)
        if duplicate is not None:
            if record["status"] != "DUPLICATE" or record["duplicate_of"] != duplicate[0]:
                raise CLIError(f"attempt {index} does not reproduce its duplicate relationship")
            continue
        if record["status"] != "ACCEPTED" or record["attempt_index"] not in accepted_by_index:
            raise CLIError(f"attempt {index} does not reproduce its accepted relationship")
        expected_candidate_id = _batch_candidate_id(manifest, index)
        if record["candidate_id"] != expected_candidate_id:
            raise CLIError(f"attempt {index} accepted candidate ID is not deterministic for the batch")
        accepted_record, bundle_cells = accepted_by_index[record["attempt_index"]]
        if accepted_record["candidate_id"] != record["candidate_id"] or accepted_record["grid_hash"] != digest or bundle_cells != result.logical_grid:
            raise CLIError(f"attempt {index} accepted bundle does not reproduce its recorded grid")
        prior.append((digest, tuple(result.logical_grid), str(record["candidate_id"])))


def _write_batch_review(root: Path, manifest: Mapping[str, object]) -> None:
    review_dir = root / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for record in manifest["accepted"]:  # type: ignore[union-attr]
        relative = _safe_relative_path(record["relative_path"], "accepted.relative_path")  # type: ignore[index]
        bundle = read_bundle(root / relative)
        entries.append(
            ReviewEntry(
                str(record["candidate_id"]), bundle.artwork.width, bundle.artwork.height, bundle.artwork.cells,
                mode=manifest["request_template"]["generator_mode"], seed=record["attempt_seed"]["value"],  # type: ignore[index]
                difficulty=manifest["request_template"]["difficulty"], classification="ACCEPTED",
                policy=QualityPolicy(**manifest["quality_policy"]),  # type: ignore[arg-type]
            )
        )
    if entries:
        write_review_pack(entries, review_dir)
    rows: list[str] = []
    for record in manifest["attempts"]:  # type: ignore[union-attr]
        row = {key: record.get(key) for key in ("attempt_index", "attempt_seed", "status", "failure_code", "quality_decision", "rejection_codes", "grid_hash", "duplicate_of", "candidate_id", "relative_path", "width", "height")}
        rows.append("<tr>" + "".join(f"<td>{html.escape(json.dumps(row[key], sort_keys=True, separators=(',', ':')) if isinstance(row[key], (dict, list)) else str(row[key] if row[key] is not None else ''))}</td>" for key in row) + "</tr>")
    headings = ("attempt_index", "attempt_seed", "status", "failure_code", "quality_decision", "rejection_codes", "grid_hash", "duplicate_of", "candidate_id", "relative_path", "width", "height")
    content = "<!doctype html>\n<html><head><meta charset=\"utf-8\"><title>SCRUBBOTS M09 Batch Report</title></head><body><h1>PAG-M09 — Batch Report</h1><table><thead><tr>" + "".join(f"<th>{heading}</th>" for heading in headings) + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></body></html>\n"
    (review_dir / "batch-report.html").write_text(content, encoding="utf-8")


def _new_manifest(args: argparse.Namespace, root: Path, registry: ExemplarRegistry) -> dict[str, object]:
    if args.seed is None:
        raise CLIError("batch requires an explicit --seed")
    if args.count is None or args.count <= 0:
        raise CLIError("batch requires a positive --count")
    if args.max_attempts is None or args.max_attempts <= 0:
        raise CLIError("batch requires a positive --max-attempts")
    seed = _canonical_seed(args.seed)
    request, config = _batch_config(args, seed, registry)
    policy = _quality_policy_from_json(args.quality_policy_json, request)
    identities = _exemplar_identities(registry)
    batch_id = _batch_id(config, seed, args.count, args.max_attempts, identities, policy.as_dict())
    return {
        "schema": _MANIFEST_SCHEMA,
        "version": _MANIFEST_VERSION,
        "batch_id": batch_id,
        "requested_count": args.count,
        "max_attempts": args.max_attempts,
        "root_seed": _typed_seed(seed),
        "request_template": config,
        "exemplar_identities": identities,
        "quality_policy": policy.as_dict(),
        "next_attempt_index": 0,
        "attempts": [],
        "accepted": [],
        "accepted_count": 0,
        "terminal_state": "IN_PROGRESS",
    }


def _batch(args: argparse.Namespace) -> ExitCode:
    if args.resume is not None:
        root = args.resume.parent
        raw = _json_load(args.resume, "batch manifest")
        manifest = _validate_manifest(raw, args.resume)
        forbidden = (args.difficulty, args.count, args.max_attempts, args.mode, args.width, args.height, args.style, args.theme, args.seed, args.palette, args.options_json, args.output, args.quality_policy_json)
        if any(value is not None for value in forbidden):
            raise CLIError("--resume cannot be combined with immutable batch configuration flags")
        registry = _resume_registry(manifest, args.exemplar_json)
    else:
        root = args.output or Path("batch-output")
        manifest_path = root / "batch-manifest.json"
        if manifest_path.exists():
            raise CLIError("batch output already contains a manifest; use --resume", ExitCode.FILESYSTEM)
        registry = _load_exemplars(args.exemplar_json)
        manifest = _new_manifest(args, root, registry)
        manifest_path = root / "batch-manifest.json"
        _atomic_manifest_write(manifest_path, manifest)

    accepted = _accepted_grids(root, manifest)
    _validate_attempt_history(manifest, registry, accepted)
    if args.resume is not None and manifest["terminal_state"] == "COMPLETE":
        print(f"COMPLETE batch_id={manifest['batch_id']} accepted={manifest['accepted_count']} attempts={manifest['next_attempt_index']}")
        return ExitCode.SUCCESS
    if args.resume is not None and manifest["terminal_state"] == "EXHAUSTED":
        print(f"EXHAUSTED batch_id={manifest['batch_id']} accepted={manifest['accepted_count']} attempts={manifest['next_attempt_index']}", file=sys.stderr)
        return ExitCode.BATCH_EXHAUSTED
    accepted_hashes = [(record["grid_hash"], cells, record["candidate_id"]) for record, cells in accepted]
    router = _router(registry)
    target = int(manifest["requested_count"])
    max_attempts = int(manifest["max_attempts"])
    while int(manifest["accepted_count"]) < target and int(manifest["next_attempt_index"]) < max_attempts:
        index = int(manifest["next_attempt_index"])
        root_seed = _parse_typed_seed(manifest["root_seed"], "manifest.root_seed")
        attempt_seed = DeterministicRNG(root_seed).retry_seed(index)
        request = _request_from_manifest(manifest, attempt_seed)
        candidate = router.generate_candidate(request)
        result = _candidate_result(candidate)
        record: dict[str, object] = {
            "attempt_index": index,
            "attempt_seed": _typed_seed(attempt_seed),
            "status": "GENERATOR_FAILURE",
            "failure_code": None,
            "quality_decision": None,
            "rejection_codes": [],
            "grid_hash": None,
            "duplicate_of": None,
            "candidate_id": None,
            "relative_path": None,
            "width": result.width,
            "height": result.height,
        }
        if not result.is_success:
            record["failure_code"] = result.failure_code.value if result.failure_code else "GENERATION_FAILED"
        else:
            report = evaluate_grid(result.width, result.height, result.logical_grid, policy=QualityPolicy(**manifest["quality_policy"]))  # type: ignore[arg-type]
            record["quality_decision"] = "ACCEPT" if report.accepted else "REJECT"
            record["rejection_codes"] = list(report.rejection_codes)
            record["grid_hash"] = logical_grid_hash(result.width, result.height, result.logical_grid)  # type: ignore[arg-type]
            if not report.accepted:
                record["status"] = "QUALITY_REJECTED"
            else:
                equal = next(((grid, candidate_id) for digest, grid, candidate_id in accepted_hashes if digest == record["grid_hash"] and grid == result.logical_grid), None)
                if equal is not None:
                    record["status"] = "DUPLICATE"
                    record["duplicate_of"] = equal[1]
                else:
                    candidate_id = _batch_candidate_id(manifest, index)
                    destination = export_candidate(candidate, candidate_id, root / "candidates", quality_report=report)
                    record.update({"status": "ACCEPTED", "candidate_id": candidate_id, "relative_path": destination.relative_to(root).as_posix()})
                    manifest["accepted"].append({"attempt_index": index, "attempt_seed": _typed_seed(attempt_seed), "candidate_id": candidate_id, "grid_hash": record["grid_hash"], "relative_path": record["relative_path"], "width": result.width, "height": result.height})  # type: ignore[union-attr]
                    manifest["accepted_count"] = int(manifest["accepted_count"]) + 1
                    accepted_hashes.append((record["grid_hash"], tuple(result.logical_grid), candidate_id))
        manifest["attempts"].append(record)  # type: ignore[union-attr]
        manifest["next_attempt_index"] = index + 1
        if int(manifest["accepted_count"]) >= target:
            manifest["terminal_state"] = "COMPLETE"
        elif int(manifest["next_attempt_index"]) >= max_attempts:
            manifest["terminal_state"] = "EXHAUSTED"
        else:
            manifest["terminal_state"] = "IN_PROGRESS"
        _atomic_manifest_write(root / "batch-manifest.json", manifest)
    _write_batch_review(root, manifest)
    if manifest["terminal_state"] == "COMPLETE":
        print(f"COMPLETE batch_id={manifest['batch_id']} accepted={manifest['accepted_count']} attempts={manifest['next_attempt_index']} manifest={root / 'batch-manifest.json'}")
        return ExitCode.SUCCESS
    print(f"EXHAUSTED batch_id={manifest['batch_id']} accepted={manifest['accepted_count']} attempts={manifest['next_attempt_index']}", file=sys.stderr)
    return ExitCode.BATCH_EXHAUSTED


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scrubbots-pixel", description="Offline deterministic SCRUBBOTS logical-pixel generator")
    sub = parser.add_subparsers(dest="command", required=True)
    generate = sub.add_parser("generate", help="generate one accepted candidate bundle")
    _add_request_flags(generate, required=True)
    generate.add_argument("--seed", help="canonical decimal integer token or string; omitted uses local OS entropy")
    generate.add_argument("--output", type=Path, default=Path("output"))
    generate.add_argument("--candidate-id")
    generate.add_argument("--preview-scale", type=int)
    generate.add_argument("--exemplar-json", type=Path)
    generate.add_argument("--quality-policy-json", type=Path, help="canonical local M07 QualityPolicy JSON")
    generate.set_defaults(handler=_generate)

    reproduce = sub.add_parser("reproduce", help="reproduce and verify a recorded metadata.json")
    reproduce.add_argument("metadata", type=Path)
    reproduce.add_argument("--output", type=Path)
    reproduce.add_argument("--exemplar-json", type=Path)
    reproduce.set_defaults(handler=_reproduce)

    batch = sub.add_parser("batch", help="run or resume a finite deterministic batch")
    batch.add_argument("--resume", type=Path)
    _add_request_flags(batch, required=False)
    batch.add_argument("--seed")
    batch.add_argument("--count", type=int)
    batch.add_argument("--max-attempts", type=int)
    batch.add_argument("--output", type=Path)
    batch.add_argument("--exemplar-json", type=Path)
    batch.add_argument("--quality-policy-json", type=Path, help="canonical local M07 QualityPolicy JSON for a new batch")
    batch.set_defaults(handler=_batch)
    return parser


def _add_request_flags(parser: argparse.ArgumentParser, *, required: bool) -> None:
    parser.add_argument("--difficulty", required=required, choices=("EASY", "MEDIUM", "HARD", "VERY_HARD"))
    parser.add_argument("--mode", required=required, choices=tuple(sorted(_BATCH_MODES)))
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--style")
    parser.add_argument("--theme")
    parser.add_argument("--palette", help="comma-separated requested logical C-ID subset")
    parser.add_argument("--options-json", type=Path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
        return int(args.handler(args))
    except CLIError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return int(exc.code)
    except (OSError, TypeError, ValueError, WFCContractError, OutputContractError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return int(ExitCode.INVALID_REQUEST)


__all__ = ["ExitCode", "CLIError", "main"]
