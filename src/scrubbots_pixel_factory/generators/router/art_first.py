"""Read-only ART_FIRST consumption of reviewed, exact logical source art.

The request names canonical source/candidate/review identities only. It never
accepts a caller-selected filesystem path, and the resulting generation stays
TEST/PREVIEW even when its source has a current owner review.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from types import MappingProxyType

from ...contracts.palette import VOID_CELL_ID
from ...contracts import CANONICAL_PALETTE
from ...core import DeterministicRNG, FailureCode, GenerationRequest, GenerationResult
from ...core.request import LegacyGenerationRequest
from ...core.rng import RNG_ALGORITHM
from ...generators.mask.model import MaskDefinition, MaskCellState
from ...owner_upload import OWNER_UPLOAD_ORIGIN, OWNER_UPLOAD_STATUS, OWNER_UPLOAD_VALIDATION_STATE, owner_upload_root
from ...quality import logical_grid_hash
from ...semantic.normalization.core import RAW_ARTIFACT_MAX_BYTES, SUPPORTED_MEDIA_TYPE
from ...studio_extensions import (
    StudioExtensionError,
    _owner_source_grid,
    extensions_root,
    validate_owner_review_chain,
    verify_owner_source,
)
from ...output.bundle import OutputContractError, read_bundle


ART_FIRST_OPTIONS_NAMESPACE = "art-first"
ART_FIRST_GENERATOR_ID = "art-first-verified-source"
ART_FIRST_GENERATOR_VERSION = "1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SOURCE_ID = re.compile(r"owner-upload-([0-9a-f]{64})\Z")
_OPTIONS_REQUIRED = {
    "source_id", "source_sha256", "source_record_sha256", "candidate_id", "review_id",
}
_SOURCE_RECORD_FIELDS = {
    "schema", "version", "source_id", "origin", "source_sha256", "byte_length",
    "media_type", "original_filename", "original_width", "original_height",
    "immutable_relative_path", "source_record_relative_path", "status", "validation_state",
}


class ArtFirstUnavailable(ValueError):
    """ART_FIRST cannot proceed without exact source, review and authority."""


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _canonical_source_record_bytes(value: Mapping[str, object]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _safe_file(path: Path, root: Path, limit: int, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ArtFirstUnavailable(f"UNAVAILABLE: {label} is missing or is a symlink")
    try:
        resolved_root = root.resolve(strict=True)
        resolved = path.resolve(strict=True)
        if resolved.parent != resolved_root or not resolved.is_relative_to(resolved_root):
            raise ArtFirstUnavailable(f"UNAVAILABLE: {label} escaped its canonical source directory")
        if path.stat().st_size > limit:
            raise ArtFirstUnavailable(f"UNAVAILABLE: {label} exceeds the bounded byte policy")
        return path.read_bytes()
    except OSError as exc:
        raise ArtFirstUnavailable(f"UNAVAILABLE: {label} is unreadable") from exc


def _load_source(source_id: str, expected_sha: str, expected_record_sha: str) -> tuple[dict[str, object], bytes, tuple[str, ...], int, int]:
    match = _SOURCE_ID.fullmatch(source_id)
    if match is None or not _SHA256.fullmatch(expected_sha) or not _SHA256.fullmatch(expected_record_sha):
        raise ArtFirstUnavailable("UNAVAILABLE: source identity or SHA-256 binding is malformed")
    if match.group(1) != expected_sha:
        raise ArtFirstUnavailable("UNAVAILABLE: source ID does not match the requested source hash")
    root = owner_upload_root()
    if root.is_symlink() or not root.is_dir():
        raise ArtFirstUnavailable("UNAVAILABLE: canonical owner-upload store is missing or unsafe")
    source_dir = root / source_id
    if source_dir.is_symlink() or not source_dir.is_dir():
        raise ArtFirstUnavailable("UNAVAILABLE: source directory is missing or is a symlink")
    try:
        if not source_dir.resolve(strict=True).is_relative_to(root.resolve(strict=True)):
            raise ArtFirstUnavailable("UNAVAILABLE: source directory escaped the canonical owner-upload store")
    except OSError as exc:
        raise ArtFirstUnavailable("UNAVAILABLE: source directory cannot be resolved") from exc

    record_path = source_dir / "source.json"
    png_path = source_dir / "source.png"
    record_bytes = _safe_file(record_path, source_dir, 64 * 1024, "source record")
    png_bytes = _safe_file(png_path, source_dir, RAW_ARTIFACT_MAX_BYTES, "source PNG")
    if _sha256(record_bytes) != expected_record_sha:
        raise ArtFirstUnavailable("UNAVAILABLE: immutable source record hash changed")
    try:
        record = json.loads(record_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ArtFirstUnavailable("UNAVAILABLE: source record is malformed") from exc
    if not isinstance(record, Mapping) or set(record) != _SOURCE_RECORD_FIELDS:
        raise ArtFirstUnavailable("UNAVAILABLE: source record schema is unsupported")
    if _canonical_source_record_bytes(record) != record_bytes:
        raise ArtFirstUnavailable("UNAVAILABLE: source record is not canonical JSON")
    if record.get("schema") != "scrubbots-owner-upload-source" or record.get("version") != 1:
        raise ArtFirstUnavailable("UNAVAILABLE: source record schema/version is unsupported")
    if (
        record.get("source_id") != source_id
        or record.get("origin") != OWNER_UPLOAD_ORIGIN
        or record.get("status") != OWNER_UPLOAD_STATUS
        or record.get("validation_state") != OWNER_UPLOAD_VALIDATION_STATE
        or record.get("source_sha256") != expected_sha
        or record.get("byte_length") != len(png_bytes)
        or record.get("media_type") != SUPPORTED_MEDIA_TYPE
        or record.get("immutable_relative_path") != f"owner-uploads/{source_id}/source.png"
        or record.get("source_record_relative_path") != f"owner-uploads/{source_id}/source.json"
        or _sha256(png_bytes) != expected_sha
    ):
        raise ArtFirstUnavailable("UNAVAILABLE: source record does not bind the exact imported PNG bytes")

    # Reuse the canonical Studio decoder and palette mapping; the import label
    # is retained only as a system-record claim, not proof of owner originality.
    try:
        verified = verify_owner_source(source_id)
        width, height, cells, foreign, semi_alpha, transparent, used = _owner_source_grid(png_bytes)
    except (StudioExtensionError, OSError, TypeError, ValueError) as exc:
        raise ArtFirstUnavailable("UNAVAILABLE: canonical source verification failed") from exc
    if verified.get("source_sha256") != expected_sha or verified.get("source_bytes_sha256") != expected_sha:
        raise ArtFirstUnavailable("UNAVAILABLE: canonical source verifier reports a different byte identity")
    if (record.get("original_width"), record.get("original_height")) != (width, height):
        raise ArtFirstUnavailable("UNAVAILABLE: source dimensions do not match the decoded image")
    if not (20 <= width <= 59 and 20 <= height <= 59):
        raise ArtFirstUnavailable("UNAVAILABLE: logical source dimensions must independently be 20..59")
    if foreign or semi_alpha or not 3 <= len(used) <= 12:
        raise ArtFirstUnavailable("UNAVAILABLE: source must use 3..12 canonical colors and no foreign or semi-alpha pixels")
    if transparent and (width * height - transparent < 200 or (width * height - transparent) < width * height * 0.25):
        raise ArtFirstUnavailable("UNAVAILABLE: transparent source is below the existing minimum-artwork rule")
    if VOID_CELL_ID in cells:
        from ...supply_pipeline.void_capability import void_capability

        capability = void_capability()
        if capability.get("state") != "OPEN":
            raise ArtFirstUnavailable("UNAVAILABLE/VOID_CAPABILITY_REQUIRED: current attested VOID capability is closed")
    return dict(record), png_bytes, cells, width, height


def _candidate_and_review(
    source: Mapping[str, object],
    source_record_sha: str,
    source_id: str,
    candidate_id: str,
    review_id: str,
) -> tuple[object, dict[str, object]]:
    source_sha = str(source["source_sha256"])
    expected_candidate_id = f"candidate-owner-{source_sha[:48]}"
    if candidate_id != expected_candidate_id or not review_id.startswith(f"review-{expected_candidate_id}-"):
        raise ArtFirstUnavailable("UNAVAILABLE: candidate or review identity does not match this exact source")
    output_root = owner_upload_root().parent
    candidate_store = output_root / "studio-derived-candidates"
    if candidate_store.is_symlink() or not candidate_store.is_dir():
        raise ArtFirstUnavailable("UNAVAILABLE/NEEDS_OWNER_ACCEPT: no canonical owner-source candidate exists")
    candidate_dir = candidate_store / expected_candidate_id
    if candidate_dir.is_symlink() or not candidate_dir.is_dir():
        raise ArtFirstUnavailable("UNAVAILABLE/NEEDS_OWNER_ACCEPT: no canonical owner-source candidate exists")
    for name, limit in (("artwork.json", 256 * 1024), ("metadata.json", 1024 * 1024), ("artwork.png", 1024 * 1024), ("artwork.preview.png", 4 * 1024 * 1024)):
        if (candidate_dir / name).exists():
            _safe_file(candidate_dir / name, candidate_dir, limit, f"reviewed candidate {name}")
    if not all((candidate_dir / name).is_file() for name in ("artwork.json", "metadata.json", "artwork.png")):
        raise ArtFirstUnavailable("UNAVAILABLE: reviewed candidate bundle is incomplete")
    try:
        bundle = read_bundle(candidate_dir)
    except (OutputContractError, OSError, ValueError) as exc:
        raise ArtFirstUnavailable("UNAVAILABLE: reviewed candidate bundle failed canonical validation") from exc
    metadata = bundle.metadata
    generation = metadata.get("generation", {})
    generator = generation.get("result", {}).get("generator", {}) if isinstance(generation, Mapping) else {}
    generator_metadata = metadata.get("generator_metadata", {})
    payload = generator_metadata.get("payload", {}) if isinstance(generator_metadata, Mapping) else {}
    payload_data = payload.get("data", {}) if isinstance(payload, Mapping) else {}
    lineage = payload_data.get("source_lineage", {}) if isinstance(payload_data, Mapping) else {}
    source_record_path = owner_upload_root() / source_id / "source.json"
    try:
        expected_record_ref = source_record_path.resolve().relative_to(Path(__file__).resolve().parents[4]).as_posix()
    except ValueError:
        expected_record_ref = str(source_record_path.resolve())
    if (
        bundle.artwork.candidate_id != expected_candidate_id
        or not isinstance(generator, Mapping)
        or generator.get("mode") != "MASK"
        or generator.get("id") != "owner-upload-canonical-derive"
        or generator.get("version") != "1"
        or not isinstance(payload, Mapping)
        or payload.get("namespace") != "owner-upload"
        or not isinstance(generator_metadata, Mapping)
        or not isinstance(generator_metadata.get("classification"), Mapping)
        or generator_metadata["classification"].get("candidate_class") != "PRODUCTION_CANDIDATE"
        or not isinstance(lineage, Mapping)
        or lineage.get("source_id") != source_id
        or lineage.get("source_sha256") != source_sha
        or lineage.get("source_record") != expected_record_ref
        or lineage.get("source_bytes_unchanged") is not True
        or lineage.get("derivation") != "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE"
    ):
        raise ArtFirstUnavailable("UNAVAILABLE: existing candidate is not bound to the exact immutable source")
    if source_record_sha != _sha256(_safe_file(owner_upload_root() / source_id / "source.json", owner_upload_root() / source_id, 64 * 1024, "source record")):
        raise ArtFirstUnavailable("UNAVAILABLE: immutable source record changed during ART_FIRST validation")

    review_root = extensions_root() / "owner-review"
    if review_root.is_symlink() or not review_root.is_dir():
        raise ArtFirstUnavailable("UNAVAILABLE/NEEDS_OWNER_ACCEPT: no durable owner-review chain exists")
    prefix = f"review-{expected_candidate_id}-"
    try:
        paths = sorted(path for path in review_root.iterdir() if path.name.startswith(prefix) and path.suffix == ".json")
    except OSError as exc:
        raise ArtFirstUnavailable("UNAVAILABLE: owner-review chain cannot be enumerated") from exc
    if len(paths) > 256:
        raise ArtFirstUnavailable("UNAVAILABLE: owner-review history exceeds the bounded record policy")
    records: list[dict[str, object]] = []
    for path in paths:
        raw = _safe_file(path, review_root, 64 * 1024, "owner-review record")
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ArtFirstUnavailable("UNAVAILABLE: owner-review record is malformed") from exc
        if not isinstance(value, Mapping):
            raise ArtFirstUnavailable("UNAVAILABLE: owner-review record is not an object")
        records.append(dict(value))
    review_candidate = {
        "candidate_id": expected_candidate_id,
        "artwork_sha256": hashlib.sha256(bundle.artwork_png).hexdigest(),
        "grid_hash": bundle.artwork.grid_hash,
    }
    try:
        chain, invalid = validate_owner_review_chain(review_candidate, records)
    except StudioExtensionError as exc:
        raise ArtFirstUnavailable("UNAVAILABLE: canonical owner-review chain validation failed") from exc
    if invalid or len(chain) != len(records) or not chain:
        raise ArtFirstUnavailable("UNAVAILABLE/NEEDS_OWNER_ACCEPT: owner-review history is incomplete or invalid")
    current = chain[-1]
    if current.get("disposition") != "ACCEPT":
        raise ArtFirstUnavailable("UNAVAILABLE/OWNER_REJECTED: the current review does not accept this artwork")
    if current.get("review_id") != review_id:
        raise ArtFirstUnavailable("UNAVAILABLE/STALE_REVIEW: request does not name the current ACCEPT review")
    binding = {
        "schema": "scrubbots-art-first-source-binding",
        "version": 1,
        "source_id": source_id,
        "source_sha256": source_sha,
        "source_record_sha256": source_record_sha,
        "source_import_record_origin": source.get("origin"),
        "source_role": "VERIFIED_IMPORTED_ORIGIN_UNVERIFIED",
        "upstream_creator_identity": "UNAVAILABLE",
        "approved_candidate_id": expected_candidate_id,
        "review_id": review_id,
        "review_disposition": "ACCEPT",
        "candidate_artwork_sha256": review_candidate["artwork_sha256"],
        "candidate_grid_hash": bundle.artwork.grid_hash,
        "source_bytes_unchanged": True,
        "output_classification": "TEST/PREVIEW",
        "production_candidate_created": False,
        "pipeline_ready_created": False,
        "solver_evidence_created": False,
        "owner_acceptance_created": False,
    }
    return bundle, binding


def _check_mask_constraints(mask_value: object, width: int, height: int, cells: tuple[str, ...]) -> str | None:
    if mask_value is None:
        return None
    if not isinstance(mask_value, Mapping) or set(mask_value) != {"width", "height", "cells"}:
        raise ArtFirstUnavailable("UNAVAILABLE: source mask must contain exactly width, height, and row-major cells")
    try:
        mask = MaskDefinition(mask_value["width"], mask_value["height"], tuple(mask_value["cells"]))
    except (TypeError, ValueError) as exc:
        raise ArtFirstUnavailable("UNAVAILABLE: source mask definition is malformed") from exc
    if (mask.width, mask.height) != (width, height):
        raise ArtFirstUnavailable("UNAVAILABLE: source mask dimensions must exactly match the logical image")
    for source_cell, state in zip(cells, mask.row_major(), strict=True):
        if state is MaskCellState.REQUIRED and source_cell == VOID_CELL_ID:
            raise ArtFirstUnavailable("UNAVAILABLE: REQUIRED mask cell does not match existing source art")
        if state is MaskCellState.FORBIDDEN and source_cell != VOID_CELL_ID:
            raise ArtFirstUnavailable("UNAVAILABLE: FORBIDDEN mask cell does not match existing source art")
    return _sha256(_canonical_bytes({"width": width, "height": height, "cells": [state.value for state in mask.row_major()]}))


def _resolve(request: GenerationRequest) -> tuple[tuple[str, ...], dict[str, object]]:
    options = request.options
    if options.namespace != ART_FIRST_OPTIONS_NAMESPACE or options.version != 1:
        raise ArtFirstUnavailable("UNAVAILABLE: ART_FIRST options require namespace art-first version 1")
    values = options.values
    if not _OPTIONS_REQUIRED.issubset(values) or set(values) - (_OPTIONS_REQUIRED | {"mask_constraints"}):
        raise ArtFirstUnavailable("UNAVAILABLE: ART_FIRST requires exact source, candidate, and review identities")
    if any(type(values[key]) is not str for key in _OPTIONS_REQUIRED):
        raise ArtFirstUnavailable("UNAVAILABLE: ART_FIRST source, candidate, and review identities must be strings")
    source, _raw, cells, width, height = _load_source(
        values["source_id"], values["source_sha256"], values["source_record_sha256"],  # type: ignore[arg-type]
    )
    if (width, height) != (request.width, request.height):
        raise ArtFirstUnavailable("UNAVAILABLE: request dimensions must exactly match the canonical source grid")
    if request.palette_subset is not None and not set(CANONICAL_PALETTE.used_ids(cells)).issubset(request.palette_subset):
        raise ArtFirstUnavailable("UNAVAILABLE: source uses colors outside the requested palette subset")
    source_has_void = VOID_CELL_ID in cells
    if request.background_intent != ("TRANSPARENT" if source_has_void else "BACKGROUND"):
        raise ArtFirstUnavailable("UNAVAILABLE: background intent must exactly match source alpha/VOID semantics")
    record_sha = str(values["source_record_sha256"])
    bundle, binding = _candidate_and_review(
        source, record_sha, str(values["source_id"]), str(values["candidate_id"]), str(values["review_id"]),
    )
    if (bundle.artwork.width, bundle.artwork.height, bundle.artwork.cells) != (width, height, cells):
        raise ArtFirstUnavailable("UNAVAILABLE: reviewed candidate grid differs from exact decoded source art")
    if bundle.artwork.grid_hash != logical_grid_hash(width, height, cells):
        raise ArtFirstUnavailable("UNAVAILABLE: reviewed candidate grid hash does not bind the source image")
    mask_digest = _check_mask_constraints(values.get("mask_constraints"), width, height, cells)
    binding.update({
        "request_digest": request.digest(),
        "input_dimensions": {"width": width, "height": height},
        "source_grid_hash": logical_grid_hash(width, height, cells),
        "mask_constraints_sha256": mask_digest,
        "mask_constraints_role": "UNAPPROVED_CONSTRAINT_ONLY" if mask_digest is not None else "NONE",
        "stage": "ART_FIRST_EXACT_VERIFIED_SOURCE_COPY",
        "stage_version": 1,
    })
    return cells, binding


@dataclass(frozen=True, slots=True)
class ArtFirstCandidate:
    result: GenerationResult
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def art_first_metadata(self) -> Mapping[str, object]:
        return self.metadata


class ArtFirstGenerator:
    """Consume one exact, currently accepted logical source candidate."""

    def generate_candidate(self, request: GenerationRequest, rng: DeterministicRNG):
        if not isinstance(request, GenerationRequest) or request.generator_mode != "ART_FIRST":
            return GenerationResult.failure(code=FailureCode.INVALID_REQUEST, reason="ART_FIRST requires a current ART_FIRST GenerationRequest", request=request if isinstance(request, GenerationRequest) else None)
        try:
            if not isinstance(rng, DeterministicRNG) or rng.domain != "root" or rng.stage_seeds() != DeterministicRNG(request.seed).stage_seeds():
                raise ArtFirstUnavailable("UNAVAILABLE: ART_FIRST requires the canonical root RNG stream")
            cells, binding = _resolve(request)
            result = GenerationResult.success(
                request=request,
                width=request.width,
                height=request.height,
                logical_grid=cells,
                generator_id=ART_FIRST_GENERATOR_ID,
                generator_version=ART_FIRST_GENERATOR_VERSION,
                generator_mode="ART_FIRST",
                seed=request.seed,
                rng_algorithm=RNG_ALGORITHM,
                provenance={"stage_seeds": rng.stage_seeds()},
            )
            return ArtFirstCandidate(result, binding)
        except (ArtFirstUnavailable, OSError, TypeError, ValueError) as exc:
            return GenerationResult.failure(
                code=FailureCode.INVALID_REQUEST,
                reason=str(exc)[:512],
                request=request,
            )


def validate_art_first_bundle(result: Mapping[str, object], payload: Mapping[str, object], artwork: object) -> None:
    """Revalidate the selected source and its live review chain on bundle read/export."""

    if not isinstance(result, Mapping) or not isinstance(payload, Mapping) or not isinstance(artwork, Mapping):
        raise OutputContractError("ART_FIRST bundle binding is malformed")
    request = result.get("request")
    generator = result.get("generator")
    if not isinstance(request, Mapping) or not isinstance(generator, Mapping) or generator.get("mode") != "ART_FIRST":
        raise OutputContractError("ART_FIRST generation request or identity is malformed")
    try:
        request_digest = hashlib.sha256(_canonical_bytes(request)).hexdigest()
        seed_payload = request.get("seed")
        if not isinstance(seed_payload, Mapping) or set(seed_payload) != {"type", "value"}:
            raise ArtFirstUnavailable("UNAVAILABLE: ART_FIRST bundle request seed is malformed")
        seed_value = seed_payload.get("value")
        request_options = request.get("generator_options")
        if not isinstance(request_options, Mapping) or set(request_options) != {"namespace", "version", "values"}:
            raise ArtFirstUnavailable("UNAVAILABLE: ART_FIRST bundle request options are malformed")
        if request_options.get("namespace") != ART_FIRST_OPTIONS_NAMESPACE or request_options.get("version") != 1 or not isinstance(request_options.get("values"), Mapping):
            raise ArtFirstUnavailable("UNAVAILABLE: ART_FIRST bundle request options are unsupported")
        values = request_options["values"]
        fake_request = GenerationRequest(
            seed=seed_value,  # type: ignore[arg-type]
            width=request.get("width"),  # type: ignore[arg-type]
            height=request.get("height"),  # type: ignore[arg-type]
            generator_mode="ART_FIRST",
            palette_subset=request.get("palette_subset"),  # type: ignore[arg-type]
            generator_options={"namespace": "art-first", "version": 1, "values": dict(values)},
            background_intent=request.get("background_intent", "BACKGROUND"),  # type: ignore[arg-type]
        )
        if fake_request.canonical_dict() != dict(request):
            raise ArtFirstUnavailable("UNAVAILABLE: ART_FIRST request is not in its canonical roundtrip representation")
        cells, expected_binding = _resolve(fake_request)
    except (ArtFirstUnavailable, KeyError, TypeError, ValueError) as exc:
        raise OutputContractError(f"ART_FIRST bundle source/review revalidation failed: {exc}") from exc
    if (
        generator.get("id") != ART_FIRST_GENERATOR_ID
        or generator.get("version") != ART_FIRST_GENERATOR_VERSION
        or request_digest != expected_binding.get("request_digest")
        or dict(payload) != {"namespace": "art_first", "data": expected_binding}
        or artwork.get("width") != fake_request.width
        or artwork.get("height") != fake_request.height
        or artwork.get("cells") != list(cells)
        or artwork.get("grid_hash") != expected_binding.get("source_grid_hash")
    ):
        raise OutputContractError("ART_FIRST output differs from its current verified source/review binding")


__all__ = ["ArtFirstCandidate", "ArtFirstGenerator", "validate_art_first_bundle"]
