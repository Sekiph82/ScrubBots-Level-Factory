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
    report = evaluate_grid(result.width, result.height, result.logical_grid, policy=_quality_policy(request))  # type: ignore[arg-type]
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
    report = evaluate_grid(result.width, result.height, result.logical_grid, policy=_quality_policy(request))  # type: ignore[arg-type]
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
    return request, config


def _batch_id(config: Mapping[str, object], seed: int | str, count: int, max_attempts: int) -> str:
    immutable = {"config": config, "root_seed": _typed_seed(seed), "requested_count": count, "max_attempts": max_attempts}
    return f"batch-{hashlib.sha256(canonical_json_bytes(immutable)).hexdigest()}"


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
    if type(value["next_attempt_index"]) is not int or value["next_attempt_index"] < 0:
        raise CLIError("batch manifest next attempt index is invalid")
    if type(value["accepted_count"]) is not int or value["accepted_count"] < 0:
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
    if value["batch_id"] != _batch_id(template, root_seed, int(value["requested_count"]), int(value["max_attempts"])):
        raise CLIError("batch manifest identity does not match its immutable configuration")
    try:
        _request_from_manifest(dict(value), DeterministicRNG(root_seed).retry_seed(0))
        QualityPolicy(**value["quality_policy"])  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise CLIError(f"batch manifest contains an invalid immutable contract: {exc}") from exc
    if len(value["attempts"]) != value["next_attempt_index"]:
        raise CLIError("batch manifest attempts are not contiguous with next_attempt_index")
    accepted = value["accepted"]
    if len(accepted) != value["accepted_count"]:
        raise CLIError("batch manifest accepted count is inconsistent")
    for index, record in enumerate(value["attempts"]):
        if not isinstance(record, Mapping) or record.get("attempt_index") != index:
            raise CLIError("batch manifest attempt history is not ordered")
    for index, record in enumerate(accepted):
        if not isinstance(record, Mapping) or type(record.get("attempt_index")) is not int or record.get("attempt_index") < 0:
            raise CLIError("batch manifest accepted history is malformed")
        _safe_relative_path(record.get("relative_path"), f"accepted[{index}].relative_path")
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
        if root.resolve() not in candidate_root.parents:
            raise CLIError("accepted bundle path escapes the batch root")
        try:
            bundle = read_bundle(candidate_root)
        except (OSError, TypeError, ValueError) as exc:
            raise CLIError(f"accepted bundle is invalid during resume: {exc}") from exc
        if bundle.artwork.grid_hash != record["grid_hash"]:
            raise CLIError("accepted bundle hash does not match the batch manifest")
        output.append((record, bundle.artwork.cells))
    return output


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
    policy = _quality_policy(request)
    batch_id = _batch_id(config, seed, args.count, args.max_attempts)
    return {
        "schema": _MANIFEST_SCHEMA,
        "version": _MANIFEST_VERSION,
        "batch_id": batch_id,
        "requested_count": args.count,
        "max_attempts": args.max_attempts,
        "root_seed": _typed_seed(seed),
        "request_template": config,
        "exemplar_identities": _exemplar_identities(registry),
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
        forbidden = (args.difficulty, args.count, args.max_attempts, args.mode, args.width, args.height, args.style, args.theme, args.seed, args.palette, args.options_json, args.output)
        if any(value is not None for value in forbidden):
            raise CLIError("--resume cannot be combined with immutable batch configuration flags")
        registry = _resume_registry(manifest, args.exemplar_json)
        if manifest["terminal_state"] == "COMPLETE":
            _accepted_grids(root, manifest)
            print(f"COMPLETE batch_id={manifest['batch_id']} accepted={manifest['accepted_count']} attempts={manifest['next_attempt_index']}")
            return ExitCode.SUCCESS
        if manifest["terminal_state"] == "EXHAUSTED":
            print(f"EXHAUSTED batch_id={manifest['batch_id']} accepted={manifest['accepted_count']} attempts={manifest['next_attempt_index']}", file=sys.stderr)
            return ExitCode.BATCH_EXHAUSTED
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
                    candidate_id = f"{manifest['batch_id']}-{index:06d}"
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
