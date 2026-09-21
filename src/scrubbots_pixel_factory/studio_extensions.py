"""Canonical, local-only Factory Studio extension contracts.

The Studio surfaces are deliberately thin views over these records.  This
module never copies immutable source bytes into an index and never invents
solver, difficulty, owner-review, provider, or production truth.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import uuid
from typing import Any

from .contracts import CANONICAL_PALETTE
from .output.bundle import read_bundle
from .output.png import decode_logical_png
from .owner_upload import OWNER_UPLOAD_ORIGIN, OWNER_UPLOAD_STATUS, OWNER_UPLOAD_VALIDATION_STATE, owner_upload_root, import_owner_upload
from .quality.core import QualityPolicy, evaluate_grid, logical_grid_hash
from .semantic.normalization.core import SUPPORTED_MEDIA_TYPE, _decode_raw


EXTENSIONS_SCHEMA_VERSION = 1
CATALOG_SCHEMA = "scrubbots-source-library-metadata"
VALIDATION_SCHEMA = "scrubbots-owner-upload-validation"
PIPELINE_SCHEMA = "scrubbots-studio-pipeline-run"
REVIEW_SCHEMA = "scrubbots-owner-review-evidence"
PRESET_SCHEMA = "scrubbots-studio-preset"
REVISION_SCHEMA = "scrubbots-manual-art-revision"
BATCH_SCHEMA = "scrubbots-owner-upload-batch"
SESSION_SCHEMA = "scrubbots-studio-session"
SIMILARITY_SCHEMA = "scrubbots-art-similarity-evidence"
SIMILARITY_POLICY = "SIMILARITY_POLICY_V1"
ACCOUNTING_SCHEMA = "scrubbots-provider-accounting-record"
_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_TAG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.-]{0,31}$")


class StudioExtensionError(ValueError):
    """Raised when extension evidence cannot be trusted or is malformed."""


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def extensions_root() -> Path:
    return (_repository_root() / "level_factory" / "output" / "studio-extensions").resolve()


def _accounting_root() -> Path:
    return extensions_root() / "accounting"


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StudioExtensionError(f"evidence is unreadable: {path.name}") from exc
    if not isinstance(value, dict):
        raise StudioExtensionError(f"evidence root is not an object: {path.name}")
    return value


def _write_json(path: Path, value: Mapping[str, object], *, immutable: bool = False) -> None:
    payload = _canonical_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if immutable and path.exists():
        if path.read_bytes() != payload:
            raise StudioExtensionError(f"immutable evidence already exists with different content: {path.name}")
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def _relative(path: Path) -> str:
    return path.resolve().relative_to(_repository_root().resolve()).as_posix()


def _source_record_paths(source_id: str) -> tuple[Path, Path]:
    if not isinstance(source_id, str) or not source_id.startswith("owner-upload-"):
        raise StudioExtensionError("source_id is not an OWNER_UPLOAD identity")
    root = (owner_upload_root() / source_id).resolve()
    if owner_upload_root().resolve() not in root.parents:
        raise StudioExtensionError("source path escaped the canonical OWNER_UPLOAD area")
    return root / "source.json", root / "source.png"


def verify_owner_source(source_id: str) -> dict[str, Any]:
    """Re-verify one canonical OWNER_UPLOAD record and its exact bytes."""

    record_path, source_path = _source_record_paths(source_id)
    record = _read_json(record_path)
    expected_keys = {
        "schema", "version", "source_id", "origin", "source_sha256", "byte_length", "media_type",
        "original_filename", "original_width", "original_height", "immutable_relative_path",
        "source_record_relative_path", "status", "validation_state",
    }
    if set(record) != expected_keys or record.get("source_id") != source_id:
        raise StudioExtensionError("OWNER_UPLOAD source record schema or identity is invalid")
    if record.get("origin") != OWNER_UPLOAD_ORIGIN or record.get("status") != OWNER_UPLOAD_STATUS or record.get("validation_state") != OWNER_UPLOAD_VALIDATION_STATE:
        raise StudioExtensionError("source is not an immutable OWNER_UPLOAD SOURCE_ONLY record")
    raw = source_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != record.get("source_sha256") or len(raw) != record.get("byte_length"):
        raise StudioExtensionError("source bytes do not match source.json identity")
    expected_source = f"owner-uploads/{source_id}/source.png"
    expected_record = f"owner-uploads/{source_id}/source.json"
    if record.get("immutable_relative_path") != expected_source or record.get("source_record_relative_path") != expected_record:
        raise StudioExtensionError("OWNER_UPLOAD relative paths are not canonical")
    return {
        **record,
        "source_path": _relative(source_path),
        "record_path": _relative(record_path),
        "source_bytes_sha256": digest,
    }


def _metadata_path(source_id: str) -> Path:
    return extensions_root() / "source-library" / "metadata" / f"{source_id}.json"


def _read_catalog_metadata(source_id: str) -> dict[str, Any]:
    path = _metadata_path(source_id)
    if not path.exists():
        return {"schema": CATALOG_SCHEMA, "version": 1, "source_id": source_id, "label": "", "tags": []}
    value = _read_json(path)
    if set(value) != {"schema", "version", "source_id", "label", "tags"} or value.get("schema") != CATALOG_SCHEMA or value.get("version") != 1 or value.get("source_id") != source_id:
        raise StudioExtensionError("catalog metadata is not a bound versioned sidecar")
    label, tags = value.get("label"), value.get("tags")
    if type(label) is not str or len(label) > 80 or type(tags) is not list or any(type(tag) is not str or not _TAG.fullmatch(tag) for tag in tags) or len(tags) != len(set(tags)) or len(tags) > 24:
        raise StudioExtensionError("catalog label or tags are malformed")
    return value


def save_library_metadata(source_id: str, label: str = "", tags: Sequence[str] = ()) -> dict[str, Any]:
    """Persist only bounded label/tag catalog metadata, never source truth."""

    source = verify_owner_source(source_id)
    if type(label) is not str or len(label.strip()) > 80:
        raise StudioExtensionError("label must be a trimmed string of at most 80 characters")
    normalized_tags = [str(tag).strip() for tag in tags]
    if len(normalized_tags) > 24 or any(not _TAG.fullmatch(tag) for tag in normalized_tags) or len(set(normalized_tags)) != len(normalized_tags):
        raise StudioExtensionError("tags must be unique bounded strings")
    metadata = {"schema": CATALOG_SCHEMA, "version": 1, "source_id": source_id, "label": label.strip(), "tags": sorted(normalized_tags, key=str.casefold)}
    _write_json(_metadata_path(source_id), metadata)
    return {**source, "catalog": metadata}


def library_refresh() -> dict[str, Any]:
    """Build a fresh catalog from verified OWNER_UPLOAD directories."""

    sources: list[dict[str, Any]] = []
    invalid: list[dict[str, str]] = []
    root = owner_upload_root()
    if root.exists():
        for directory in sorted((item for item in root.iterdir() if item.is_dir()), key=lambda item: item.name):
            try:
                source = verify_owner_source(directory.name)
                metadata = _read_catalog_metadata(directory.name)
                sources.append({
                    "source_id": source["source_id"], "origin": source["origin"], "source_sha256": source["source_sha256"],
                    "original_filename": source["original_filename"], "original_width": source["original_width"], "original_height": source["original_height"],
                    "status": source["status"], "validation_state": source["validation_state"], "immutable_source_path": source["source_path"],
                    "source_record_path": source["record_path"], "catalog": metadata,
                    "owner_review": {"disposition": "NOT AVAILABLE", "reason": "No canonical owner-review evidence is connected."},
                    "derived_dimensions": {"disposition": "NOT AVAILABLE", "reason": "Pending SB-LFX-004 validation evidence."},
                    "palette": {"disposition": "NOT AVAILABLE", "reason": "Pending SB-LFX-004 validation evidence."},
                    "usages": {"disposition": "NOT AVAILABLE", "reason": "No canonical candidate/level usage index is connected."},
                })
            except (StudioExtensionError, OSError) as exc:
                invalid.append({"source_id": directory.name, "disposition": "INVALID / QUARANTINED", "reason": str(exc)[:512]})
    return {
        "schema": "scrubbots-source-library-view", "version": 1, "state": "READY", "disposition": "DERIVED_CATALOG",
        "sources": sources, "invalid_sources": invalid,
        "notice": "ASSET CATALOG ONLY — source art is not training data and Library membership is not owner acceptance.",
    }


def _validation_pixels(raw: bytes) -> tuple[int, int, bytes]:
    decoded = _decode_raw(raw, SUPPORTED_MEDIA_TYPE)
    return decoded.width, decoded.height, decoded.pixels


def validate_owner_source(source_id: str, *, persist: bool = True) -> dict[str, Any]:
    source = verify_owner_source(source_id)
    raw = Path(_repository_root() / source["source_path"]).read_bytes()
    width, height, pixels = _validation_pixels(raw)
    foreign = 0
    semi_alpha = 0
    transparent = 0
    used: set[str] = set()
    cells: list[str] = []
    for index in range(width * height):
        red, green, blue, alpha = pixels[index * 4 : index * 4 + 4]
        if alpha == 0:
            transparent += 1
        elif alpha != 255:
            semi_alpha += 1
        try:
            color_id = CANONICAL_PALETTE.id_for_rgb((red, green, blue))
        except ValueError:
            foreign += 1
            color_id = "FOREIGN"
        if color_id != "FOREIGN":
            used.add(color_id)
        cells.append(color_id)
    legal_dimensions = 20 <= width <= 59 and 20 <= height <= 59
    exact_logical = legal_dimensions and foreign == 0 and semi_alpha == 0 and transparent == 0
    structural: dict[str, Any]
    if exact_logical:
        report = evaluate_grid(width, height, cells, policy=QualityPolicy())
        structural = {"disposition": "PASS" if report.accepted else "FAIL", "policy": report.policy.as_dict(), "rejection_codes": list(report.rejection_codes), "report": report.as_dict()}
    else:
        reasons: list[str] = []
        if not legal_dimensions: reasons.append("ILLEGAL_LOGICAL_DIMENSIONS")
        if foreign: reasons.append("FOREIGN_COLORS")
        if semi_alpha or transparent: reasons.append("ALPHA_CONTRACT")
        structural = {"disposition": "NOT APPLICABLE / NEEDS DERIVATION", "rejection_codes": reasons, "reason": "Exact logical C-ID grid is not available without an explicit derived artifact."}
    report = {
        "schema": VALIDATION_SCHEMA, "version": 1, "analysis_policy": "SB-LFX-004-C001_CANONICAL_IMPORT_ANALYSIS_V1",
        "source_id": source_id, "source_sha256": source["source_sha256"], "source_record_identity": _digest(source),
        "format": {"media_type": source["media_type"], "disposition": "SUPPORTED_STRICT_PNG"},
        "original_dimensions": {"width": width, "height": height}, "legal_logical_dimensions": legal_dimensions,
        "exact_logical_source": exact_logical, "logical_dimension_status": "EXACT" if exact_logical else "DERIVED_ARTIFACT_REQUIRED",
        "palette": {"canonical_ids": sorted(used, key=lambda value: int(value[1:])), "used_color_count": len(used), "foreign_color_count": foreign},
        "alpha": {"transparent_count": transparent, "semi_alpha_count": semi_alpha, "opaque_count": width * height - transparent - semi_alpha},
        "grid_hash": logical_grid_hash(width, height, cells) if exact_logical else None,
        "structural": structural,
        "policies": {"resize": "CELL_MAJORITY_V1", "palette": "PALETTE_SNAP_V1"} if not exact_logical else {"logical_interpretation": "READ_ONLY_SOURCE_PIXELS"},
        "claims": {"solver": "NOT AVAILABLE — pending M03", "difficulty": "NOT AVAILABLE — pending M04", "owner_acceptance": "NOT AVAILABLE — validation is not acceptance"},
    }
    if persist:
        path = extensions_root() / "validation" / f"{source_id}-{source['source_sha256']}.json"
        _write_json(path, report, immutable=True)
        report = {**report, "evidence_path": _relative(path)}
    return report


def _candidate_roots() -> Iterable[Path]:
    output = (_repository_root() / "level_factory" / "output").resolve()
    if not output.exists():
        return ()
    return (path.parent for path in output.rglob("metadata.json") if "studio-reproductions" not in path.parent.parts and path.parent.name and (path.parent / "artwork.json").is_file() and (path.parent / "artwork.png").is_file())


def list_candidates() -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for root in sorted(_candidate_roots(), key=lambda path: path.as_posix()):
        try:
            bundle = read_bundle(root)
            if bundle.artwork.candidate_id in seen:
                continue
            seen.add(bundle.artwork.candidate_id)
            metadata = bundle.metadata
            quality = metadata.get("quality", {}) if isinstance(metadata.get("quality", {}), Mapping) else {}
            generation = metadata.get("generation", {}) if isinstance(metadata.get("generation", {}), Mapping) else {}
            candidates.append({
                "candidate_id": bundle.artwork.candidate_id, "artwork_sha256": hashlib.sha256(bundle.artwork_png).hexdigest(),
                "grid_hash": bundle.artwork.grid_hash, "width": bundle.artwork.width, "height": bundle.artwork.height,
                "used_colors": sorted(set(bundle.artwork.cells), key=lambda value: int(value[1:])), "origin": str(generation.get("generator_mode", "PROCEDURAL")),
                "source_path": _relative(root), "artwork_path": _relative(root / "artwork.png"),
                "quality": dict(quality), "metadata": metadata,
            })
        except Exception:
            continue
    return candidates


def _review_root() -> Path:
    return extensions_root() / "owner-review"


def _validate_review_record(candidate: Mapping[str, Any], value: Mapping[str, Any], expected_sequence: int, previous_review_id: str | None) -> dict[str, Any]:
    """Validate one immutable owner-review record against its live candidate."""

    required = {"schema", "version", "review_id", "candidate_id", "candidate_identity_hash", "artwork_sha256", "grid_hash", "disposition", "reason", "note", "sequence", "created_at", "previous_review_id"}
    if set(value) != required:
        raise StudioExtensionError("review evidence schema is incomplete")
    candidate_id = str(candidate["candidate_id"])
    sequence = value.get("sequence")
    expected_id = f"review-{candidate_id}-{expected_sequence:04d}"
    expected_identity = _digest({"candidate_id": candidate_id, "grid_hash": candidate["grid_hash"]})
    if value.get("schema") != REVIEW_SCHEMA or value.get("version") != 1 or value.get("review_id") != expected_id:
        raise StudioExtensionError("review schema or deterministic identity is invalid")
    if value.get("candidate_id") != candidate_id or value.get("candidate_identity_hash") != expected_identity or value.get("artwork_sha256") != candidate["artwork_sha256"] or value.get("grid_hash") != candidate["grid_hash"]:
        raise StudioExtensionError("review evidence is bound to a different candidate/artwork/grid identity")
    if value.get("disposition") not in {"ACCEPT", "REJECT"} or type(sequence) is not int or sequence != expected_sequence:
        raise StudioExtensionError("review disposition or sequence is invalid")
    if value.get("previous_review_id") != previous_review_id:
        raise StudioExtensionError("review chain predecessor is invalid")
    if any(type(value.get(key)) is not str or len(str(value.get(key))) > 512 for key in ("reason", "note", "created_at")):
        raise StudioExtensionError("review text or timestamp is invalid")
    return dict(value)


def _validated_review_chain(candidate: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Return only the contiguous valid review chain; malformed records are excluded."""

    candidate_id = str(candidate["candidate_id"])
    artwork_sha256 = str(candidate["artwork_sha256"])
    raw_records: list[dict[str, Any]] = []
    invalid: list[str] = []
    if _review_root().exists():
        for path in sorted(_review_root().glob("*.json")):
            try:
                value = _read_json(path)
            except StudioExtensionError:
                invalid.append(path.name)
                continue
            if value.get("candidate_id") == candidate_id and value.get("artwork_sha256") == artwork_sha256:
                raw_records.append(value)
    by_sequence: dict[int, dict[str, Any]] = {}
    for value in raw_records:
        sequence = value.get("sequence")
        if type(sequence) is not int or sequence in by_sequence:
            invalid.append(str(value.get("review_id", "unknown")))
        else:
            by_sequence[sequence] = value
    chain: list[dict[str, Any]] = []
    previous_id: str | None = None
    sequence = 1
    while sequence in by_sequence:
        try:
            checked = _validate_review_record(candidate, by_sequence[sequence], sequence, previous_id)
        except StudioExtensionError:
            invalid.append(str(by_sequence[sequence].get("review_id", "unknown")))
            break
        chain.append(checked)
        previous_id = str(checked["review_id"])
        sequence += 1
    return chain, invalid


def _latest_review(candidate_id: str, artwork_sha256: str | None = None) -> dict[str, Any] | None:
    candidate = next((item for item in list_candidates() if item["candidate_id"] == candidate_id and (artwork_sha256 is None or item["artwork_sha256"] == artwork_sha256)), None)
    if candidate is None:
        return None
    chain, _invalid = _validated_review_chain(candidate)
    return chain[-1] if chain else None


def record_owner_review(candidate_id: str, disposition: str, reason: str = "", note: str = "") -> dict[str, Any]:
    candidate = next((item for item in list_candidates() if item["candidate_id"] == candidate_id), None)
    if candidate is None or disposition not in {"ACCEPT", "REJECT"}:
        raise StudioExtensionError("review requires a real candidate and ACCEPT or REJECT")
    if any(type(value) is not str or len(value) > 512 for value in (reason, note)):
        raise StudioExtensionError("review reason/note is bounded text")
    previous = _latest_review(candidate_id, candidate["artwork_sha256"])
    sequence = 1 if previous is None else int(previous["sequence"]) + 1
    payload = {"schema": REVIEW_SCHEMA, "version": 1, "review_id": f"review-{candidate_id}-{sequence:04d}", "candidate_id": candidate_id, "candidate_identity_hash": _digest({"candidate_id": candidate_id, "grid_hash": candidate["grid_hash"]}), "artwork_sha256": candidate["artwork_sha256"], "grid_hash": candidate["grid_hash"], "disposition": disposition, "reason": reason.strip(), "note": note.strip(), "sequence": sequence, "created_at": datetime.now(timezone.utc).isoformat(), "previous_review_id": previous.get("review_id") if previous else None}
    _write_json(_review_root() / f"{payload['review_id']}.json", payload, immutable=True)
    return payload


def candidate_inbox() -> dict[str, Any]:
    items = []
    for candidate in list_candidates():
        review = _latest_review(candidate["candidate_id"], candidate["artwork_sha256"])
        chain, invalid = _validated_review_chain(candidate)
        items.append({**candidate, "owner_review": review or {"disposition": "NEEDS_REVIEW", "reason": "No valid owner-review evidence exists."}, "owner_review_history": chain, "owner_review_invalid": invalid, "provenance": {"origin": candidate["origin"], "source_path": candidate["source_path"]}, "structural": candidate["quality"], "evidence_references": [candidate["source_path"], candidate["artwork_path"]], "similarity_advisory": {"disposition": "NOT AVAILABLE", "reason": "Select a canonical comparison pair; similarity is never inferred in the inbox."}, "solver": {"disposition": "NOT AVAILABLE", "reason": "Pending M03."}, "difficulty": {"disposition": "NOT AVAILABLE", "reason": "Pending M04."}})
    return {"schema": "scrubbots-candidate-inbox-view", "version": 1, "state": "READY", "candidates": items}


def discover_records(query: str = "", filters: Mapping[str, Any] | None = None, collection: str | None = None) -> dict[str, Any]:
    """Return a deterministic, non-persisted discovery view over canonical records."""

    wanted = dict(filters or {})
    allowed_filters = {"record_type", "origin", "width", "height", "review", "qa", "used_color_count"}
    if set(wanted) - allowed_filters:
        raise StudioExtensionError("discovery filter is not a grounded canonical field")
    if collection in {"Ready for Production", "Unused in Campaign"}:
        return {"schema": "scrubbots-discovery-view", "version": 1, "state": "NOT AVAILABLE", "disposition": "NOT AVAILABLE", "reason": "Required canonical export/campaign evidence is not connected.", "records": []}
    records: list[dict[str, Any]] = []
    for source in library_refresh()["sources"]:
        records.append({"record_type": "SOURCE", "record_id": source["source_id"], "origin": source["origin"], "filename": source["original_filename"], "width": source["original_width"], "height": source["original_height"], "label": source["catalog"]["label"], "tags": source["catalog"]["tags"], "review": source["owner_review"]["disposition"], "qa": "NOT AVAILABLE"})
    for candidate in candidate_inbox()["candidates"]:
        records.append({"record_type": "CANDIDATE", "record_id": candidate["candidate_id"], "origin": candidate["origin"], "filename": "", "width": candidate["width"], "height": candidate["height"], "label": "", "tags": [], "review": candidate["owner_review"].get("disposition", "NEEDS_REVIEW"), "qa": candidate["quality"].get("decision", "NOT AVAILABLE"), "used_colors": candidate["used_colors"], "used_color_count": len(candidate["used_colors"]), "similarity_advisory": {"disposition": "NOT AVAILABLE", "reason": "Select a canonical comparison pair."}})
    if collection == "Imported Sources": records = [record for record in records if record["record_type"] == "SOURCE"]
    elif collection == "Needs Review": records = [record for record in records if record["review"] == "NEEDS_REVIEW"]
    elif collection == "Owner Accepted": records = [record for record in records if record["review"] == "ACCEPT"]
    elif collection == "Owner Rejected": records = [record for record in records if record["review"] == "REJECT"]
    needle = query.strip().casefold()
    if needle: records = [record for record in records if needle in json.dumps(record, ensure_ascii=False, sort_keys=True).casefold()]
    for key, value in wanted.items():
        records = [record for record in records if record.get(key) == value]
    records.sort(key=lambda record: (str(record["record_type"]), str(record["record_id"])))
    return {"schema": "scrubbots-discovery-view", "version": 1, "state": "READY", "disposition": "DERIVED_VIEW", "collection": collection or "ALL", "records": records, "mutated": False}


def compare_candidates(candidate_ids: Sequence[str]) -> dict[str, Any]:
    if len(candidate_ids) < 2 or len(set(candidate_ids)) != len(candidate_ids):
        raise StudioExtensionError("comparison requires at least two distinct candidate IDs")
    selected = []
    for candidate_id in candidate_ids:
        candidate = next((item for item in list_candidates() if item["candidate_id"] == candidate_id), None)
        if candidate is None:
            raise StudioExtensionError("comparison candidate is unavailable")
        review = _latest_review(candidate_id, candidate["artwork_sha256"])
        _history, invalid_reviews = _validated_review_chain(candidate)
        current_review: dict[str, Any] = review or ({"disposition": "STALE", "reason": "Mismatched or corrupt review evidence is excluded."} if invalid_reviews else {"disposition": "NOT AVAILABLE", "reason": "No review evidence."})
        selected.append({k: candidate[k] for k in ("candidate_id", "artwork_sha256", "grid_hash", "width", "height", "used_colors", "origin", "source_path", "artwork_path", "quality") } | {"provenance": {"origin": candidate["origin"], "source_path": candidate["source_path"]}, "structural": candidate["quality"], "owner_review": current_review, "owner_review_invalid": invalid_reviews, "evidence_references": [candidate["source_path"], candidate["artwork_path"]], "solver": {"disposition": "NOT AVAILABLE", "reason": "Pending M03."}, "difficulty": {"disposition": "NOT AVAILABLE", "reason": "Pending M04."}, "provider_cost": {"disposition": "NOT AVAILABLE", "reason": "Pending reliable provider evidence."}})
    similarity_evidence = similarity_canonical(str(candidate_ids[0]), str(candidate_ids[1])) if len(candidate_ids) == 2 else {"disposition": "NOT AVAILABLE", "reason": "Similarity requires exactly two canonical identities."}
    for item in selected: item["similarity_advisory"] = similarity_evidence
    return {"schema": "scrubbots-candidate-comparison-view", "version": 1, "read_only": True, "candidates": selected, "similarity_advisory": similarity_evidence, "winner": {"disposition": "NOT AVAILABLE", "reason": "Comparison never computes a winner."}}


def _pipeline_path(run_id: str) -> Path:
    return extensions_root() / "pipelines" / f"{run_id}.json"


def _pipeline_stage(
    stage: str,
    disposition: str,
    *,
    inputs: Iterable[str] = (),
    outputs: Iterable[str] = (),
    evidence: str | None = None,
    reason: str,
) -> dict[str, Any]:
    """Build the one durable stage lineage shape used by every pipeline run."""

    input_identities = [str(value) for value in inputs if str(value)]
    output_identities = [str(value) for value in outputs if str(value)]
    return {
        "schema": "scrubbots-studio-pipeline-stage",
        "version": 1,
        "stage": stage,
        "disposition": disposition,
        "input_identities": input_identities,
        "output_identities": output_identities,
        "evidence_reference": evidence,
        "reason": reason[:512],
    }


def run_pipeline(*, source_id: str | None = None, candidate_id: str | None = None, request: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if (source_id is None) == (candidate_id is None):
        raise StudioExtensionError("pipeline requires exactly one source or candidate identity")
    stages: list[dict[str, Any]] = []
    known_inputs: list[str] = [source_id or candidate_id or ""]
    if source_id is not None:
        validation = validate_owner_source(source_id)
        source_evidence = str(validation.get("record_path", ""))
        stages.append(_pipeline_stage("SOURCE", "PASS", inputs=[source_id], outputs=[source_id], evidence=source_evidence, reason="Verified immutable OWNER_UPLOAD source identity."))
        stages.append(_pipeline_stage("NORMALIZE/DERIVE", "NOT_APPLICABLE" if validation["exact_logical_source"] else "BLOCKED", inputs=[source_id], outputs=[source_id] if validation["exact_logical_source"] else (), evidence=validation.get("evidence_path"), reason="Exact source pixels are already logical." if validation["exact_logical_source"] else "DERIVED_ARTIFACT_REQUIRED — no implicit transform."))
        stages.append(_pipeline_stage("PALETTE/STRUCTURE VALIDATION", validation["structural"]["disposition"], inputs=[source_id], outputs=[source_id] if validation["exact_logical_source"] else (), evidence=validation.get("evidence_path"), reason=validation["structural"].get("reason", "Canonical validation evidence.")))
        if validation["exact_logical_source"] and validation["structural"]["disposition"] == "PASS":
            stages.append(_pipeline_stage("CANDIDATE", "NOT_AVAILABLE", inputs=[source_id], evidence=validation.get("evidence_path"), reason="OWNER_UPLOAD source is not automatically a candidate."))
        else:
            stages.append(_pipeline_stage("CANDIDATE", "BLOCKED", inputs=[source_id], evidence=validation.get("evidence_path"), reason="Pipeline stopped at source validation."))
    else:
        candidate = next((item for item in list_candidates() if item["candidate_id"] == candidate_id), None)
        if candidate is None: raise StudioExtensionError("candidate is unavailable")
        quality_disposition = "PASS" if candidate["quality"].get("decision") in {"ACCEPT", "PASS"} else "NOT_AVAILABLE"
        quality_reason = "Canonical structural evidence is present." if quality_disposition == "PASS" else "Canonical structural evidence is unavailable for this candidate."
        stages.extend([
            _pipeline_stage("SOURCE", "PASS", inputs=[candidate_id], outputs=[candidate["artwork_sha256"]], evidence=candidate["source_path"], reason="Verified canonical candidate bundle source."),
            _pipeline_stage("NORMALIZE/DERIVE", "NOT_APPLICABLE", inputs=[candidate["artwork_sha256"]], outputs=[candidate["artwork_sha256"]], evidence=candidate["source_path"], reason="Canonical candidate is already in logical representation."),
            _pipeline_stage("PALETTE/STRUCTURE VALIDATION", quality_disposition, inputs=[candidate["artwork_sha256"]], outputs=[candidate["artwork_sha256"]] if quality_disposition == "PASS" else (), evidence=candidate["source_path"], reason=quality_reason),
            _pipeline_stage("CANDIDATE", "PASS", inputs=[candidate["artwork_sha256"]], outputs=[candidate_id], evidence=candidate["source_path"], reason="Canonical candidate identity is retained."),
        ])
    hard_stop = next((stage for stage in stages if stage["disposition"] in {"FAIL", "BLOCKED", "NOT_AVAILABLE", "NOT AVAILABLE"}), None)
    current_identity = source_id or candidate_id or ""
    for name in ("SOLVE", "DIFFICULTY", "QA", "REVIEW"):
        if hard_stop is not None:
            stages.append(_pipeline_stage(name, "NOT_AVAILABLE", inputs=[current_identity], evidence=hard_stop.get("evidence_reference"), reason=f"Stopped after {hard_stop['stage']}: {hard_stop.get('reason', hard_stop['disposition'])}"))
        elif name == "SOLVE":
            stages.append(_pipeline_stage(name, "NOT_AVAILABLE", inputs=[current_identity], reason="Gameplay solver pending M03."))
            hard_stop = stages[-1]
        elif name == "DIFFICULTY":
            stages.append(_pipeline_stage(name, "NOT_AVAILABLE", inputs=[current_identity], reason="Measured difficulty pending M04."))
            hard_stop = stages[-1]
        else:
            stages.append(_pipeline_stage(name, "NOT_AVAILABLE", inputs=[current_identity], reason="Canonical downstream dependency is unavailable."))
    run_id = f"pipeline-{_digest({'source_id': source_id, 'candidate_id': candidate_id, 'request': dict(request or {}), 'sequence': datetime.now(timezone.utc).isoformat()})[:24]}"
    payload = {"schema": PIPELINE_SCHEMA, "version": 1, "run_id": run_id, "source_id": source_id, "candidate_id": candidate_id, "request": dict(request or {}), "stages": stages, "disposition": "PARTIAL / STOPPED" if hard_stop else "COMPLETE", "created_at": datetime.now(timezone.utc).isoformat()}
    _write_json(_pipeline_path(run_id), payload, immutable=True)
    return payload


def _preset_root() -> Path: return extensions_root() / "presets"


def save_preset(preset_id: str, name: str, operation: str, settings: Mapping[str, Any], description: str = "") -> dict[str, Any]:
    if not _ID.fullmatch(preset_id) or type(name) is not str or not 1 <= len(name.strip()) <= 80 or type(description) is not str or len(description) > 240:
        raise StudioExtensionError("preset identity/name/description is invalid")
    if operation != "Generate":
        raise StudioExtensionError("only the canonical Generate preset operation is currently supported")
    expanded = _validate_generate_preset_settings(settings)
    payload = {"schema": PRESET_SCHEMA, "version": 1, "preset_id": preset_id, "name": name.strip(), "description": description.strip(), "operation": operation, "settings": expanded}
    _write_json(_preset_root() / f"{preset_id}.json", payload)
    return payload


def load_preset(preset_id: str) -> dict[str, Any]:
    value = _read_json(_preset_root() / f"{preset_id}.json")
    if value.get("schema") != PRESET_SCHEMA or value.get("preset_id") != preset_id: raise StudioExtensionError("preset is malformed")
    return value


def delete_preset(preset_id: str) -> None:
    path = _preset_root() / f"{preset_id}.json"
    if path.exists(): path.unlink()


def expand_preset(preset_id: str, overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preset = load_preset(preset_id)
    expanded = dict(preset["settings"])
    expanded.update(dict(overrides or {}))
    return {"operation": preset["operation"], "request_schema": "scrubbots-studio-expanded-request", "request_version": 1, "preset_id": preset_id, "settings": _validate_generate_preset_settings(expanded)}


def _validate_generate_preset_settings(settings: Mapping[str, Any]) -> dict[str, Any]:
    allowed = {"difficulty", "width", "height", "seed", "mode"}
    if not isinstance(settings, Mapping) or set(settings) != allowed:
        raise StudioExtensionError("Generate preset must contain exactly difficulty, width, height, seed and mode")
    normalized = json.loads(json.dumps(dict(settings), sort_keys=True, separators=(",", ":")))
    if type(normalized["difficulty"]) is not str or normalized["difficulty"] not in {"EASY", "MEDIUM", "HARD"}:
        raise StudioExtensionError("preset difficulty is invalid")
    if type(normalized["width"]) is not int or type(normalized["height"]) is not int or not 20 <= normalized["width"] <= 59 or not 20 <= normalized["height"] <= 59:
        raise StudioExtensionError("preset dimensions must be integers from 20 through 59")
    if type(normalized["seed"]) not in {int, str} or (type(normalized["seed"]) is str and not normalized["seed"].strip()):
        raise StudioExtensionError("preset seed must be a typed integer or non-empty string")
    if type(normalized["mode"]) is not str or normalized["mode"] not in {"MASK", "RULES", "WFC", "HYBRID", "AUTO"}:
        raise StudioExtensionError("preset generator mode is invalid")
    return normalized


def apply_preset(preset_id: str, overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Execute canonical Generate from a fully expanded request, never preset identity."""

    expanded = expand_preset(preset_id, overrides)
    settings = expanded["settings"]
    from .core.request import GenerationRequest
    from .generators.router import GeneratorRouter
    from .output.bundle import export_candidate

    try:
        request = GenerationRequest(settings["difficulty"], settings["seed"], settings["mode"], width=settings["width"], height=settings["height"])
        candidate = GeneratorRouter().generate_candidate(request)
        if not hasattr(candidate, "result") and not hasattr(candidate, "canonical_dict"):
            raise StudioExtensionError("canonical Generate did not return a candidate")
        candidate_id = f"preset-{preset_id}-{_digest(settings)[:16]}"
        destination = (_repository_root() / "level_factory" / "output" / "studio-preset-runs").resolve()
        bundle_path = export_candidate(candidate, candidate_id, destination)
    except Exception as exc:
        raise StudioExtensionError(f"canonical preset Generate failed: {exc}") from exc
    canonical_request = request.canonical_dict()
    bundle = read_bundle(bundle_path)
    if bundle.metadata.get("generation", {}).get("request") != canonical_request:
        raise StudioExtensionError("preset expanded request does not match canonical bundle metadata")
    execution = {"schema": "scrubbots-preset-execution", "version": 2, "execution_id": f"preset-execution-{_digest(canonical_request)[:24]}", "preset_id_at_launch": preset_id, "operation": "Generate", "operator_settings": settings, "expanded_request": canonical_request, "expanded_request_digest": _digest(canonical_request), "candidate_id": candidate_id, "source_bundle_path": _relative(bundle_path)}
    execution_path = extensions_root() / "preset-executions" / f"{execution['execution_id']}.json"
    _write_json(execution_path, execution, immutable=True)
    return {"state": "SUCCESS", "disposition": "SUCCESS", "operation": "Generate", "execution": execution, "expanded_request": {**expanded, "canonical_request": canonical_request, "canonical_request_digest": _digest(canonical_request)}}


def readiness_card(candidate_id: str) -> dict[str, Any]:
    candidate = next((item for item in list_candidates() if item["candidate_id"] == candidate_id), None)
    if candidate is None: raise StudioExtensionError("candidate is unavailable")
    review = _latest_review(candidate_id, candidate["artwork_sha256"])
    _review_history, invalid_reviews = _validated_review_chain(candidate)
    quality = candidate["quality"]
    gates = {
        "SOURCE": {"disposition": "PASS", "reason": "Verified canonical candidate bundle.", "evidence": candidate["artwork_sha256"]},
        "PALETTE": {"disposition": "PASS", "reason": "Canonical artwork bundle validates palette identity.", "evidence": candidate["grid_hash"]},
        "STRUCTURE": {"disposition": "PASS" if quality.get("decision") in {"ACCEPT", "PASS"} else "FAIL", "reason": "Canonical quality evidence.", "evidence": quality.get("grid_hash")},
        "SOLVER": {"disposition": "NOT_AVAILABLE", "reason": "Gameplay solver pending M03.", "evidence": None},
        "DIFFICULTY": {"disposition": "NOT_AVAILABLE", "reason": "Measured difficulty pending M04.", "evidence": None},
        "QA": {"disposition": "NOT_AVAILABLE", "reason": "Authoritative M05 QA evidence is not connected; structural evidence is not QA.", "evidence": None},
        "OWNER": {"disposition": "PASS" if review and review["disposition"] == "ACCEPT" else "FAIL" if review and review["disposition"] == "REJECT" else "STALE" if invalid_reviews else "PENDING", "reason": "Latest validated append-only owner review evidence." if review else "Mismatched/corrupt review evidence is excluded." if invalid_reviews else "No valid owner review exists.", "evidence": review.get("review_id") if review else None, "invalid_evidence": invalid_reviews},
        "EXPORT": {"disposition": "NOT_AVAILABLE", "reason": "Authoritative export/promotion evidence is not connected; bundle presence is not export authority.", "evidence": None},
    }
    ready = all(gate["disposition"] == "PASS" for gate in gates.values())
    return {"schema": "scrubbots-production-readiness-card", "version": 1, "candidate_id": candidate_id, "gates": gates, "overall": "READY" if ready else "NOT READY", "reason": "Every required gate must be authoritative PASS." if not ready else "All required gates pass."}


def _reproduction_contract(candidate: Mapping[str, Any]) -> tuple[Path, Any]:
    """Validate the complete recorded Generate contract before claiming replay."""

    source = (_repository_root() / str(candidate["source_path"])).resolve()
    if _repository_root().resolve() not in source.parents:
        raise StudioExtensionError("recorded candidate path escaped the repository")
    bundle = read_bundle(source)
    metadata = bundle.metadata
    generation = metadata.get("generation")
    if not isinstance(generation, Mapping) or not isinstance(generation.get("request"), Mapping):
        raise StudioExtensionError("recorded generation request is missing")
    if metadata.get("candidate_id") != candidate["candidate_id"] or bundle.artwork.candidate_id != candidate["candidate_id"]:
        raise StudioExtensionError("recorded candidate identity is inconsistent")
    if hashlib.sha256(bundle.artwork_png).hexdigest() != candidate["artwork_sha256"] or bundle.artwork.grid_hash != candidate["grid_hash"]:
        raise StudioExtensionError("recorded artwork identity is inconsistent")
    request = generation["request"]
    required_request = {"schema", "schema_version", "difficulty", "width", "height", "generator_mode", "style", "theme", "palette_subset", "generator_options", "seed"}
    if set(request) != required_request or request.get("schema") != "scrubbots-generation-request":
        raise StudioExtensionError("recorded generation request schema is invalid")
    if type(request.get("schema_version")) is not int or type(request.get("width")) is not int or type(request.get("height")) is not int:
        raise StudioExtensionError("recorded generation request types are invalid")
    if not isinstance(generation.get("seed"), Mapping) or set(generation["seed"]) != {"type", "value"}:
        raise StudioExtensionError("recorded generation seed is not typed")
    if generation.get("generator_mode") != request.get("generator_mode") or not generation.get("generator_id") or not generation.get("generator_version"):
        raise StudioExtensionError("recorded generator identity is incomplete")
    return source / "metadata.json", bundle


def reproduce_capability(candidate_id: str) -> dict[str, Any]:
    candidate = next((item for item in list_candidates() if item["candidate_id"] == candidate_id), None)
    if candidate is None:
        if candidate_id.startswith("owner-upload-"):
            try:
                source = verify_owner_source(candidate_id)
            except (StudioExtensionError, OSError) as exc:
                return {"disposition": "STALE/INVALID", "candidate_id": candidate_id, "reason": f"OWNER_UPLOAD source verification failed: {exc}"}
            return {"disposition": "SOURCE_RETRIEVABLE_ONLY", "candidate_id": candidate_id, "source_record": source["record_path"], "reason": "Verified OWNER_UPLOAD source retrieval is not deterministic regeneration."}
        return {"disposition": "STALE/INVALID", "candidate_id": candidate_id, "reason": "Candidate is not a verified canonical bundle."}
    try:
        metadata_path, bundle = _reproduction_contract(candidate)
    except StudioExtensionError as exc:
        return {"disposition": "STALE/INVALID", "candidate_id": candidate_id, "reason": f"Recorded replay contract is invalid: {exc}"}
    if str(candidate["origin"]).upper() == "OWNER_UPLOAD":
        return {"disposition": "SOURCE_RETRIEVABLE_ONLY", "candidate_id": candidate_id, "reason": "OWNER_UPLOAD source retrieval is not deterministic regeneration."}
    return {"disposition": "EXACT_REPRODUCIBLE", "candidate_id": candidate_id, "recorded_metadata": _relative(metadata_path), "request_identity": _digest(bundle.metadata["generation"]["request"]), "artwork_sha256": candidate["artwork_sha256"], "grid_hash": candidate["grid_hash"], "reason": "Canonical recorded Generate request, seed, generator identity, and bundle evidence are valid."}


def reproduce_exact(candidate_id: str) -> dict[str, Any]:
    """Run the canonical offline Reproduce command and verify byte identity."""

    candidate = next((item for item in list_candidates() if item["candidate_id"] == candidate_id), None)
    if candidate is None:
        raise StudioExtensionError("candidate is unavailable")
    capability = reproduce_capability(candidate_id)
    if capability.get("disposition") != "EXACT_REPRODUCIBLE":
        raise StudioExtensionError(f"exact reproduction is not available: {capability.get('reason', 'capability rejected')}")
    metadata_path, original = _reproduction_contract(candidate)
    run_root = (_repository_root() / "level_factory" / "output" / "studio-reproductions" / f"{candidate_id}-{candidate['artwork_sha256'][:16]}").resolve()
    destination = run_root / candidate_id
    launcher = _repository_root() / "level_factory" / "scripts" / "factory_core_launcher.py"
    process = subprocess.run([sys.executable, str(launcher), "reproduce", str(metadata_path), "--output", str(run_root)], cwd=_repository_root(), capture_output=True, text=True, check=False)
    if process.returncode != 0 or "MATCH" not in process.stdout:
        raise StudioExtensionError(f"canonical Reproduce failed: {(process.stderr or process.stdout).strip()[:512]}")
    reproduced = read_bundle(destination)
    files = {name: hashlib.sha256(data).hexdigest() for name, data in reproduced.files.items()}
    original_files = {name: hashlib.sha256(data).hexdigest() for name, data in original.files.items()}
    if reproduced.files != original.files:
        raise StudioExtensionError("canonical Reproduce did not preserve exact bundle bytes")
    evidence = {"schema": "scrubbots-studio-exact-reproduction", "version": 1, "reproduction_id": f"reproduction-{candidate_id}-{candidate['artwork_sha256'][:24]}", "candidate_id": candidate_id, "source_metadata_path": _relative(metadata_path), "reproduced_output_path": _relative(destination), "disposition": "MATCH", "match": True, "original_file_sha256": original_files, "reproduced_file_sha256": files, "canonical_stdout": process.stdout.strip()[:2048]}
    evidence_path = extensions_root() / "reproductions" / f"{evidence['reproduction_id']}.json"
    _write_json(evidence_path, evidence, immutable=True)
    return {"state": "SUCCESS", "disposition": "MATCH", "capability": capability, "candidate_id": candidate_id, "output_path": _relative(destination), "evidence": evidence, "evidence_path": _relative(evidence_path)}


def create_revision(candidate_id: str, width: int, height: int, cells: Sequence[str], parent_revision_id: str | None = None, change_summary: str = "", edit_operations: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    if type(width) is not int or type(height) is not int or len(cells) != width * height or any(cell not in CANONICAL_PALETTE.ids for cell in cells): raise StudioExtensionError("revision logical grid is invalid")
    candidate = next((item for item in list_candidates() if item["candidate_id"] == candidate_id), None)
    if candidate is None: raise StudioExtensionError("revision source candidate is unavailable")
    root = extensions_root() / "revisions" / candidate_id
    existing = list_revisions(candidate_id) if root.exists() else []
    sequence = len(existing)
    parent = None
    if sequence and parent_revision_id is None:
        raise StudioExtensionError("every revision after the root must name its explicit parent revision")
    if not sequence and parent_revision_id is not None:
        raise StudioExtensionError("revision 0 cannot have a parent")
    if parent_revision_id is not None:
        parent = load_revision(candidate_id, parent_revision_id)
        if parent.get("width") != width or parent.get("height") != height or not isinstance(parent.get("cells"), list) or len(parent["cells"]) != len(cells):
            raise StudioExtensionError("revision parent dimensions or logical grid are invalid")
    grid_hash = logical_grid_hash(width, height, cells)
    if parent is None and (width != candidate["width"] or height != candidate["height"] or list(cells) != list(read_bundle((_repository_root() / candidate["source_path"]).resolve()).artwork.cells)):
        raise StudioExtensionError("revision 0 must exactly match the canonical source artwork baseline")
    changed_indices = [index for index, (before, after) in enumerate(zip(parent["cells"], cells)) if before != after] if parent else []
    operations = json.loads(json.dumps(list(edit_operations or []), sort_keys=True, separators=(",", ":")))
    if any(not isinstance(operation, Mapping) or set(operation) - {"operation", "indices", "summary"} or not isinstance(operation.get("operation"), str) or not isinstance(operation.get("indices", []), list) or any(type(index) is not int or index < 0 or index >= width * height for index in operation.get("indices", [])) for operation in operations):
        raise StudioExtensionError("revision edit operations are malformed")
    if parent and not operations:
        operations = [{"operation": "GRID_EDIT", "indices": changed_indices, "summary": change_summary[:240]}]
    payload = {"schema": REVISION_SCHEMA, "version": 2, "revision_id": f"revision-{candidate_id}-{sequence:04d}", "candidate_id": candidate_id, "source_artwork_sha256": candidate["artwork_sha256"], "parent_revision_id": parent_revision_id, "width": width, "height": height, "cells": list(cells), "working_grid_hash": grid_hash, "change_summary": change_summary[:240], "change_count": len(changed_indices), "edit_operations": operations, "sequence": sequence, "validation": {"disposition": "STALE / NOT CURRENT", "reason": "Manual revisions are not authoritative production validation."}, "created_at": datetime.now(timezone.utc).isoformat()}
    payload["revision_digest"] = _digest({key: value for key, value in payload.items() if key != "created_at"})
    _write_json(root / f"revision-{sequence:04d}.json", payload, immutable=True)
    return payload


def revision_create(candidate_id: str, width: int, height: int, cells: Sequence[str], parent_revision_id: str | None = None, change_summary: str = "", edit_operations: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    return {"state": "SUCCESS", "disposition": "CREATED", "revision": create_revision(candidate_id, width, height, cells, parent_revision_id, change_summary, edit_operations)}


def revision_list(candidate_id: str) -> dict[str, Any]:
    return {"state": "SUCCESS", "disposition": "READY", "candidate_id": candidate_id, "revisions": list_revisions(candidate_id)}


def revision_compare(candidate_id: str, left_revision_id: str, right_revision_id: str) -> dict[str, Any]:
    left, right = load_revision(candidate_id, left_revision_id), load_revision(candidate_id, right_revision_id)
    return {"state": "SUCCESS", "disposition": "READY", "comparison": compare_revisions(left, right)}


def revision_load(candidate_id: str, revision_id: str) -> dict[str, Any]:
    return {"state": "SUCCESS", "disposition": "READY", "revision": load_revision(candidate_id, revision_id)}


def compare_revisions(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    if left.get("candidate_id") != right.get("candidate_id"): raise StudioExtensionError("revisions must belong to one candidate")
    changed = [index for index, (a, b) in enumerate(zip(left.get("cells", []), right.get("cells", []))) if a != b]
    return {"left_revision_id": left.get("revision_id"), "right_revision_id": right.get("revision_id"), "changed_cell_count": len(changed), "changed_indices": changed}


def list_revisions(candidate_id: str) -> list[dict[str, Any]]:
    root = extensions_root() / "revisions" / candidate_id
    if not root.exists(): return []
    candidate = next((item for item in list_candidates() if item["candidate_id"] == candidate_id), None)
    if candidate is None: raise StudioExtensionError("revision source candidate is unavailable")
    values: list[dict[str, Any]] = []
    for path in sorted(root.glob("revision-*.json")):
        value = _read_json(path)
        required = {"schema", "version", "revision_id", "candidate_id", "source_artwork_sha256", "parent_revision_id", "width", "height", "cells", "working_grid_hash", "change_summary", "change_count", "edit_operations", "sequence", "validation", "created_at", "revision_digest"}
        if set(value) != required or value.get("schema") != REVISION_SCHEMA or value.get("version") != 2 or value.get("candidate_id") != candidate_id or value.get("source_artwork_sha256") != candidate["artwork_sha256"]:
            raise StudioExtensionError("revision lineage schema or source identity is invalid")
        if value.get("revision_digest") != _digest({key: item for key, item in value.items() if key not in {"created_at", "revision_digest"}}):
            raise StudioExtensionError("revision content digest is invalid")
        width, height, cells = value.get("width"), value.get("height"), value.get("cells")
        if type(width) is not int or type(height) is not int or not isinstance(cells, list) or len(cells) != width * height or any(cell not in CANONICAL_PALETTE.ids for cell in cells) or value.get("working_grid_hash") != logical_grid_hash(width, height, cells):
            raise StudioExtensionError("revision grid identity is invalid")
        values.append(value)
    values.sort(key=lambda item: int(item["sequence"]))
    baseline = list(read_bundle((_repository_root() / candidate["source_path"]).resolve()).artwork.cells)
    by_id: dict[str, dict[str, Any]] = {}
    for expected_sequence, value in enumerate(values):
        if value.get("sequence") != expected_sequence or value.get("revision_id") != f"revision-{candidate_id}-{expected_sequence:04d}" or value.get("revision_id") in by_id:
            raise StudioExtensionError("revision sequence or parent chain is invalid")
        if expected_sequence == 0 and (value["width"] != candidate["width"] or value["height"] != candidate["height"] or value["cells"] != baseline or value["change_count"] != 0):
            raise StudioExtensionError("revision 0 is not the immutable source baseline")
        if expected_sequence > 0:
            parent_id = value.get("parent_revision_id")
            if parent_id not in by_id: raise StudioExtensionError("revision parent is missing or is not an earlier revision")
            parent = by_id[parent_id]
            changed = [index for index, (before, after) in enumerate(zip(parent["cells"], value["cells"])) if before != after]
            if value.get("change_count") != len(changed): raise StudioExtensionError("revision change_count does not match parent delta")
            operation_indices = sorted({index for operation in value.get("edit_operations", []) for index in operation.get("indices", [])})
            if operation_indices != sorted(changed): raise StudioExtensionError("revision edit operations do not match parent delta")
        by_id[value["revision_id"]] = value
    return values


def load_revision(candidate_id: str, revision_id: str) -> dict[str, Any]:
    for value in list_revisions(candidate_id):
        if value.get("revision_id") == revision_id: return value
    raise StudioExtensionError("revision is unavailable")


def record_failure(operation: str, stage: str, disposition: str, reason: str, inputs: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if disposition not in {"FAILED", "REJECTED", "INCONCLUSIVE"}: raise StudioExtensionError("failure disposition is not retryable evidence")
    if operation not in {"import-validation", "pipeline"} or stage not in {"VALIDATE", "SOURCE", "NORMALIZE/DERIVE", "CANDIDATE", "SOLVE", "DIFFICULTY"}:
        raise StudioExtensionError("failure operation/stage is outside the canonical retry contract")
    inputs_data = json.loads(json.dumps(dict(inputs or {}), sort_keys=True, separators=(",", ":")))
    if any(any(secret in str(key).lower() for secret in ("secret", "token", "password", "api_key")) for key in inputs_data):
        raise StudioExtensionError("failure inputs contain prohibited secret-like fields")
    failure_id = f"failure-{_digest({'operation': operation, 'stage': stage, 'reason': reason, 'inputs': inputs_data, 'time': datetime.now(timezone.utc).isoformat()})[:24]}"
    eligible = operation == "import-validation" and stage == "VALIDATE" and isinstance(inputs_data.get("source_id"), str) or operation == "pipeline" and stage in {"SOURCE", "VALIDATE", "NORMALIZE/DERIVE", "CANDIDATE"} and bool(inputs_data.get("source_id") or inputs_data.get("candidate_id"))
    payload = {"schema": "scrubbots-failure-evidence", "version": 1, "failure_id": failure_id, "operation": operation, "stage": stage, "disposition": disposition, "reason": reason[:512], "inputs": inputs_data, "retryable": eligible, "retry_contract": "CANONICAL_LOCAL_RETRY_V1" if eligible else "NOT_AVAILABLE", "created_at": datetime.now(timezone.utc).isoformat()}
    _write_json(extensions_root() / "failures" / f"{failure_id}.json", payload, immutable=True)
    return payload


def retry_failure(failure_id: str, changes: Mapping[str, Any] | None = None) -> dict[str, Any]:
    failure = next((item for item in _canonical_failure_records() if item.get("failure_id") == failure_id), None)
    if failure is None:
        fallback = extensions_root() / "failures" / f"{failure_id}.json"
        if not fallback.exists(): raise StudioExtensionError("failure evidence is unavailable")
        failure = _read_json(fallback)
    if not failure.get("retryable"): return {"disposition": "NOT_AVAILABLE", "reason": "This stage has no safe retry capability.", "parent_failure_id": failure_id}
    requested_changes = dict(changes or {})
    if set(requested_changes) - {"operator_note"} or type(requested_changes.get("operator_note", "")) is not str or len(str(requested_changes.get("operator_note", ""))) > 512:
        raise StudioExtensionError("retry changes are restricted to a bounded operator_note")
    attempt_id = f"retry-{_digest({'parent': failure_id, 'changes': dict(changes or {})})[:24]}"
    execution: dict[str, Any]
    try:
        if failure["operation"] == "import-validation":
            execution = validate_owner_source(str(failure["inputs"]["source_id"]))
        else:
            execution = run_pipeline(source_id=failure["inputs"].get("source_id"), candidate_id=failure["inputs"].get("candidate_id"))
        disposition = "RETRY_EXECUTED" if execution.get("state") not in {"ERROR", "UNAVAILABLE"} else "RETRY_FAILED"
    except Exception as exc:
        execution = {"state": "ERROR", "disposition": "ERROR", "error": str(exc)[:512]}
        disposition = "RETRY_FAILED"
    payload = {"schema": "scrubbots-retry-attempt", "version": 1, "attempt_id": attempt_id, "parent_failure_id": failure_id, "operation": failure["operation"], "stage": failure["stage"], "original_inputs": failure["inputs"], "authorized_changes": requested_changes, "disposition": disposition, "execution": execution, "created_at": datetime.now(timezone.utc).isoformat()}
    _write_json(extensions_root() / "retries" / f"{attempt_id}.json", payload, immutable=True)
    return payload


def list_failures() -> dict[str, Any]:
    return {"state": "SUCCESS", "disposition": "READY", "failures": _canonical_failure_records()}


def _canonical_failure_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def add(*, evidence_id: str, evidence_path: Path, operation: str, stage: str, disposition: str, reason: str, inputs: Mapping[str, Any], retryable: bool, non_retryable_reason: str = "") -> None:
        raw = evidence_path.read_bytes()
        failure_id = f"failure-{_digest({'evidence_id': evidence_id, 'stage': stage, 'disposition': disposition})[:24]}"
        records.append({"schema": "scrubbots-derived-failure-inbox-entry", "version": 2, "failure_id": failure_id, "operation": operation, "stage": stage, "disposition": disposition, "reason": reason[:512], "inputs": dict(inputs), "retryable": retryable, "non_retryable_reason": non_retryable_reason if not retryable else "", "originating_evidence_id": evidence_id, "evidence_reference": _relative(evidence_path), "evidence_sha256": hashlib.sha256(raw).hexdigest()})

    validation_root = extensions_root() / "validation"
    for path in sorted(validation_root.glob("*.json")) if validation_root.exists() else []:
        try:
            value = _read_json(path)
            structural = value.get("structural", {})
            if value.get("schema") == VALIDATION_SCHEMA and structural.get("disposition") != "PASS":
                add(evidence_id=str(value.get("source_id", path.stem)), evidence_path=path, operation="import-validation", stage="VALIDATE", disposition="REJECTED", reason="; ".join(value.get("palette", {}).get("foreign_color_count", []) if isinstance(value.get("palette", {}).get("foreign_color_count"), list) else value.get("structural", {}).get("rejection_codes", [])) or str(structural.get("reason", "SOURCE_INVALID")), inputs={"source_id": value.get("source_id")}, retryable=True)
        except (StudioExtensionError, OSError):
            continue
    pipeline_root = extensions_root() / "pipelines"
    for path in sorted(pipeline_root.glob("*.json")) if pipeline_root.exists() else []:
        try:
            value = _read_json(path)
            for stage in value.get("stages", []):
                disposition = str(stage.get("disposition", ""))
                if disposition in {"FAIL", "BLOCKED", "INCONCLUSIVE", "NOT_AVAILABLE"}:
                    retryable = disposition in {"FAIL", "BLOCKED", "INCONCLUSIVE"} and str(stage.get("stage", "")) in {"SOURCE", "NORMALIZE/DERIVE", "CANDIDATE"}
                    add(evidence_id=str(value.get("run_id", path.stem)) + ":" + str(stage.get("stage", "")), evidence_path=path, operation="pipeline", stage=str(stage.get("stage", "")), disposition="INCONCLUSIVE" if disposition == "NOT_AVAILABLE" else disposition, reason=str(stage.get("reason", disposition)), inputs={"source_id": value.get("source_id"), "candidate_id": value.get("candidate_id")}, retryable=retryable, non_retryable_reason="Canonical stage is unavailable or is not safely retryable." if not retryable else "")
                    break
        except (StudioExtensionError, OSError):
            continue
    batch_root = extensions_root() / "batches"
    for path in sorted(batch_root.glob("*.json")) if batch_root.exists() else []:
        try:
            value = _read_json(path)
            for item in value.get("items", []):
                if item.get("disposition") not in {"IMPORTED", "ALREADY_IMPORTED"}:
                    add(evidence_id=str(value.get("batch_id", path.stem)) + ":" + str(item.get("index", "")), evidence_path=path, operation="batch-import", stage="IMPORT", disposition="REJECTED", reason=str(item.get("error", "IMPORT_REJECTED")), inputs={"display_path": item.get("display_path")}, retryable=False, non_retryable_reason="Batch item retry requires a new canonical import selection.")
        except (StudioExtensionError, OSError):
            continue
    return sorted({record["failure_id"]: record for record in records}.values(), key=lambda record: (record["evidence_reference"], record["stage"], record["failure_id"]))


def batch_import(paths: Sequence[str | Path]) -> dict[str, Any]:
    items = []
    for index, path in enumerate(paths):
        result = import_owner_upload(path)
        items.append({"index": index, "display_path": Path(path).name, "source_id": result.get("source_id"), "disposition": result.get("state", "ERROR"), "error": result.get("error")})
    batch_id = f"batch-import-{_digest(items)[:24]}-{uuid.uuid4().hex[:12]}"
    payload = {"schema": BATCH_SCHEMA, "version": 1, "batch_id": batch_id, "items": items, "counts": {"success": sum(item["disposition"] in {"IMPORTED", "ALREADY_IMPORTED"} for item in items), "failed": sum(item["disposition"] not in {"IMPORTED", "ALREADY_IMPORTED"} for item in items)}, "created_at": datetime.now(timezone.utc).isoformat()}
    _write_json(extensions_root() / "batches" / f"{batch_id}.json", payload, immutable=True)
    return payload


def batch_load(batch_id: str) -> dict[str, Any]:
    if not _ID.fullmatch(batch_id): raise StudioExtensionError("batch ID is invalid")
    value = _read_json(extensions_root() / "batches" / f"{batch_id}.json")
    if value.get("schema") != BATCH_SCHEMA or value.get("version") != 1 or value.get("batch_id") != batch_id or not isinstance(value.get("items"), list) or not isinstance(value.get("counts"), Mapping):
        raise StudioExtensionError("batch evidence schema or identity is invalid")
    return {"state": "SUCCESS", "disposition": "RELOADED", "batch": value}


_SESSION_FIELDS = {"surface", "selected_source_id", "selected_candidate_id", "active_batch_id", "active_pipeline_run_id", "active_retry_id", "active_revision_id", "autosave_generation", "draft"}
_SESSION_DRAFT_FIELDS = {"difficulty", "width", "height", "seed", "mode"}
_SESSION_REFERENCE_FIELDS = {"selected_source_id": "source", "selected_candidate_id": "candidate", "active_batch_id": "batch", "active_pipeline_run_id": "pipeline", "active_retry_id": "retry", "active_revision_id": "revision"}


def _validate_session_state(state: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(state, Mapping) or set(state) - _SESSION_FIELDS:
        raise StudioExtensionError("session contains an unknown field; allowlisted state is required")
    normalized: dict[str, Any] = {}
    for key, value in state.items():
        if key == "surface":
            if type(value) is not str or not 1 <= len(value) <= 80: raise StudioExtensionError("session surface is invalid")
            normalized[key] = value
        elif key == "autosave_generation":
            if type(value) is not int or value < 0: raise StudioExtensionError("session autosave generation is invalid")
            normalized[key] = value
        elif key == "draft":
            if not isinstance(value, Mapping) or set(value) - _SESSION_DRAFT_FIELDS: raise StudioExtensionError("session draft contains an unknown field")
            draft = dict(value)
            if any(type(draft.get(field)) not in {type(None), str, int} for field in _SESSION_DRAFT_FIELDS): raise StudioExtensionError("session draft field type is invalid")
            normalized[key] = draft
        elif key in _SESSION_REFERENCE_FIELDS:
            if type(value) is not str or not _ID.fullmatch(value): raise StudioExtensionError(f"session reference {key} is invalid")
            normalized[key] = value
    return normalized


def _session_reference_checks(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for field, kind in _SESSION_REFERENCE_FIELDS.items():
        value = state.get(field)
        if value is None: continue
        disposition = "VALID"
        reason = "Canonical reference resolved."
        try:
            if kind == "source": verify_owner_source(str(value))
            elif kind == "candidate":
                if not any(item["candidate_id"] == value for item in list_candidates()): raise StudioExtensionError("candidate is unavailable")
            elif kind == "batch": batch_load(str(value))
            elif kind == "pipeline":
                run = _read_json(_pipeline_path(str(value)))
                if run.get("schema") != PIPELINE_SCHEMA or run.get("run_id") != value: raise StudioExtensionError("pipeline run is invalid")
            elif kind == "retry":
                retry_path = extensions_root() / "retries" / f"{value}.json"; retry = _read_json(retry_path)
                if retry.get("schema") != "scrubbots-retry-attempt" or retry.get("attempt_id") != value: raise StudioExtensionError("retry evidence is invalid")
            elif kind == "revision":
                candidate_id = str(state.get("selected_candidate_id", "")); load_revision(candidate_id, str(value))
        except (StudioExtensionError, OSError, ValueError) as exc:
            disposition = "NEEDS_OPERATOR_ACTION"; reason = str(exc)[:240]
        checks.append({"field": field, "type": kind, "value": value, "disposition": disposition, "reason": reason})
    return checks


def save_session(session_id: str, state: Mapping[str, Any]) -> dict[str, Any]:
    if not _ID.fullmatch(session_id): raise StudioExtensionError("session ID is invalid")
    normalized = _validate_session_state(state)
    references = _session_reference_checks(normalized)
    payload = {"schema": SESSION_SCHEMA, "version": 2, "session_id": session_id, "state": normalized, "reference_validation": references, "autosave_generation": int(normalized.get("autosave_generation", 0)) + 1}
    payload["session_digest"] = _digest({key: value for key, value in payload.items() if key != "session_digest"})
    _write_json(extensions_root() / "sessions" / f"{session_id}.json", payload)
    return payload


def restore_session(session_id: str) -> dict[str, Any]:
    value = _read_json(extensions_root() / "sessions" / f"{session_id}.json")
    required = {"schema", "version", "session_id", "state", "reference_validation", "autosave_generation", "session_digest"}
    if set(value) != required or value.get("schema") != SESSION_SCHEMA or value.get("version") != 2 or value.get("session_id") != session_id or value.get("session_digest") != _digest({key: item for key, item in value.items() if key != "session_digest"}): raise StudioExtensionError("session schema, identity, or integrity digest is invalid")
    state = _validate_session_state(value.get("state", {}))
    checks = _session_reference_checks(state)
    valid = all(check["disposition"] == "VALID" for check in checks)
    if not checks: recovery = "NEW"
    elif not valid: recovery = "NEEDS_OPERATOR_ACTION"
    elif state.get("active_retry_id"): recovery = "RETRIED"
    elif state.get("active_pipeline_run_id") or state.get("active_batch_id"): recovery = "RESUMED"
    else: recovery = "NOT_RESUMABLE"
    return {**value, "state": state, "reference_validation": checks, "recovery": recovery, "validated_references": valid}


def similarity(left: Mapping[str, Any], right: Mapping[str, Any], threshold: float = 0.92) -> dict[str, Any]:
    if left.get("width") != right.get("width") or left.get("height") != right.get("height"): return {"disposition": "DISTINCT", "reason": "Dimensions are not comparable."}
    left_cells, right_cells = list(left.get("cells", [])), list(right.get("cells", []))
    if len(left_cells) != len(right_cells): return {"disposition": "DISTINCT", "reason": "Logical representations are not comparable."}
    distance = sum(a != b for a, b in zip(left_cells, right_cells))
    score = 1.0 - distance / len(left_cells) if left_cells else 1.0
    disposition = "EXACT_DUPLICATE" if left.get("grid_hash") == right.get("grid_hash") else "POSSIBLE_SIMILAR" if score >= threshold else "DISTINCT"
    return {"schema": SIMILARITY_SCHEMA, "version": 1, "algorithm": "LOGICAL_CELL_HAMMING_V1", "left_identity": left.get("candidate_id"), "right_identity": right.get("candidate_id"), "left_grid_hash": left.get("grid_hash"), "right_grid_hash": right.get("grid_hash"), "distance": distance, "score": round(score, 8), "threshold": threshold, "disposition": disposition, "advisory": True}


def _similarity_artifact(identity: str) -> dict[str, Any]:
    if not isinstance(identity, str) or not _ID.fullmatch(identity):
        raise StudioExtensionError("similarity identity is not a canonical artifact ID")
    candidate = next((item for item in list_candidates() if item["candidate_id"] == identity), None)
    if candidate is not None:
        bundle = read_bundle((_repository_root() / candidate["source_path"]).resolve())
        if bundle.artwork.grid_hash != candidate["grid_hash"] or hashlib.sha256(bundle.artwork_png).hexdigest() != candidate["artwork_sha256"]:
            raise StudioExtensionError("candidate representation identity is stale")
        return {"identity": identity, "candidate_id": identity, "width": bundle.artwork.width, "height": bundle.artwork.height, "cells": list(bundle.artwork.cells), "grid_hash": bundle.artwork.grid_hash, "evidence_reference": candidate["source_path"]}
    for candidate in list_candidates():
        try:
            revision = load_revision(candidate["candidate_id"], identity)
        except StudioExtensionError:
            continue
        cells = revision.get("cells")
        if not isinstance(cells, list) or revision.get("working_grid_hash") != logical_grid_hash(int(revision.get("width", 0)), int(revision.get("height", 0)), cells):
            raise StudioExtensionError("revision representation identity is stale")
        return {"identity": identity, "candidate_id": candidate["candidate_id"], "width": revision["width"], "height": revision["height"], "cells": cells, "grid_hash": revision["working_grid_hash"], "evidence_reference": f"studio-extensions/revisions/{candidate['candidate_id']}/{identity}.json"}
    raise StudioExtensionError("similarity artifact identity is unavailable")


def similarity_canonical(left_id: str, right_id: str, threshold: float = 0.92) -> dict[str, Any]:
    if type(threshold) not in {int, float} or not 0.0 <= float(threshold) <= 1.0:
        raise StudioExtensionError("similarity threshold must be between 0 and 1")
    left, right = _similarity_artifact(left_id), _similarity_artifact(right_id)
    result = similarity(left, right, float(threshold))
    return {**result, "policy": SIMILARITY_POLICY, "left_identity": left["identity"], "right_identity": right["identity"], "left_grid_hash": left["grid_hash"], "right_grid_hash": right["grid_hash"], "evidence_references": {"left": left["evidence_reference"], "right": right["evidence_reference"]}, "advisory_note": "Advisory similarity only; it does not change review, readiness, or production disposition."}


def cost_center(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        provider, unit = str(record.get("provider", "UNKNOWN")), str(record.get("unit", "UNKNOWN"))
        group = groups.setdefault((provider, unit), {"provider": provider, "unit": unit, "jobs": 0, "success": 0, "failure": 0, "consumed": None, "remaining": None, "accepted": 0})
        group["jobs"] += 1
        group["success"] += 1 if record.get("status") == "SUCCESS" else 0
        group["failure"] += 1 if record.get("status") == "FAILED" else 0
        group["accepted"] += 1 if record.get("owner_acceptance") == "ACCEPT" else 0
        if isinstance(record.get("consumed"), (int, float)): group["consumed"] = (group["consumed"] or 0) + record["consumed"]
        if isinstance(record.get("remaining"), (int, float)): group["remaining"] = record["remaining"]
    for group in groups.values():
        group["cost_per_success"] = group["consumed"] / group["success"] if group["consumed"] is not None and group["success"] else None
        group["cost_per_owner_accepted"] = group["consumed"] / group["accepted"] if group["consumed"] is not None and group["accepted"] else None
        group["unknown"] = [key for key in ("consumed", "remaining", "cost_per_success", "cost_per_owner_accepted") if group[key] is None]
    return {"schema": "scrubbots-provider-cost-center-view", "version": 1, "groups": sorted(groups.values(), key=lambda item: (item["provider"], item["unit"])), "read_only": True}


def _validated_accounting_records(scope: str | None = None, provider: str | None = None) -> list[dict[str, Any]]:
    required = {"schema", "version", "record_id", "provider", "unit", "scope", "status", "consumed", "remaining", "candidate_id", "owner_review_id", "recorded_at", "evidence_reference"}
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in sorted(_accounting_root().glob("*.json")) if _accounting_root().exists() else []:
        value = _read_json(path)
        if set(value) != required or value.get("schema") != ACCOUNTING_SCHEMA or value.get("version") != 1 or value.get("record_id") != path.stem or value["record_id"] in seen:
            continue
        if type(value.get("provider")) is not str or not value["provider"] or type(value.get("unit")) is not str or not value["unit"] or type(value.get("scope")) is not str or not value["scope"]:
            continue
        if scope is not None and value["scope"] != scope or provider is not None and value["provider"] != provider:
            continue
        if value.get("status") not in {"SUCCESS", "FAILED"} or (value.get("consumed") is not None and (type(value["consumed"]) not in {int, float} or value["consumed"] < 0)) or (value.get("remaining") is not None and (type(value["remaining"]) not in {int, float} or value["remaining"] < 0)):
            continue
        try:
            datetime.fromisoformat(str(value["recorded_at"]).replace("Z", "+00:00"))
        except ValueError:
            continue
        seen.add(value["record_id"])
        records.append(value)
    return records


def canonical_cost_center(scope: str | None = None, provider: str | None = None) -> dict[str, Any]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    rejected: list[str] = []
    if _accounting_root().exists():
        for path in sorted(_accounting_root().glob("*.json")):
            try: value = _read_json(path)
            except StudioExtensionError: rejected.append(path.stem); continue
            record_id = str(value.get("record_id", path.stem))
            if set(value) != {"schema", "version", "record_id", "provider", "unit", "scope", "status", "consumed", "remaining", "candidate_id", "owner_review_id", "recorded_at", "evidence_reference"} or value.get("schema") != ACCOUNTING_SCHEMA:
                rejected.append(record_id); continue
            record_scope, record_provider = str(value.get("scope", "UNKNOWN")), str(value.get("provider", "UNKNOWN"))
            if scope is not None and record_scope != scope or provider is not None and record_provider != provider: continue
            key = (record_provider, str(value.get("unit", "UNKNOWN")))
            groups.setdefault(key, {"provider": key[0], "unit": key[1], "scope": record_scope, "jobs": None, "success": None, "failure": None, "consumed": None, "remaining": None, "accepted": None, "cost_per_success": None, "cost_per_owner_accepted": None, "evidence_record_ids": [], "as_of": None, "unknown": ["jobs", "success", "failure", "consumed", "remaining", "cost_per_success", "cost_per_owner_accepted"], "status": "NOT AVAILABLE", "reason": "Local record is not bound to an authoritative provider/job execution source.", "rejected_record_ids": []})["rejected_record_ids"].append(record_id)
    if not groups:
        key = (provider or "NOT AVAILABLE", "NOT AVAILABLE")
        groups[key] = {"provider": key[0], "unit": key[1], "scope": scope or "NOT AVAILABLE", "jobs": None, "success": None, "failure": None, "consumed": None, "remaining": None, "accepted": None, "cost_per_success": None, "cost_per_owner_accepted": None, "evidence_record_ids": [], "as_of": None, "unknown": ["jobs", "success", "failure", "consumed", "remaining", "cost_per_success", "cost_per_owner_accepted"], "status": "NOT AVAILABLE", "reason": "No authoritative provider/job accounting source is connected.", "rejected_record_ids": []}
    return {"schema": "scrubbots-provider-cost-center-view", "version": 3, "scope": scope, "provider_filter": provider, "groups": sorted(groups.values(), key=lambda item: (item["provider"], item["unit"])), "read_only": True, "source": "NOT AVAILABLE — no authoritative provider execution accounting source", "authoritative": False, "rejected_record_ids": sorted(set(rejected)), "network_calls": 0, "credit_spend": 0}


__all__ = [
    "StudioExtensionError", "extensions_root", "verify_owner_source", "save_library_metadata", "library_refresh", "validate_owner_source",
    "list_candidates", "record_owner_review", "candidate_inbox", "discover_records", "compare_candidates", "run_pipeline", "save_preset", "load_preset", "delete_preset", "expand_preset",
    "readiness_card", "reproduce_capability", "reproduce_exact", "create_revision", "revision_create", "revision_list", "revision_compare", "revision_load", "list_revisions", "load_revision", "compare_revisions", "record_failure", "retry_failure", "list_failures", "batch_import", "batch_load", "save_session", "restore_session", "similarity", "similarity_canonical", "cost_center", "canonical_cost_center",
]
