"""Thin repository-local launcher for the canonical Python Factory Core CLI."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
from collections.abc import Mapping, Sequence


STUDIO_OPERATION = "manual-art-structural-revalidation"
STUDIO_REQUEST_SCHEMA = "scrubbots-studio-manual-art-revalidation"
STUDIO_REQUEST_VERSION = 1
STUDIO_SCOPE = "STRUCTURAL_ART_QA_ONLY"
STUDIO_REQUEST_KEYS = {
    "schema",
    "schema_version",
    "operation",
    "source_bundle_path",
    "source_candidate_id",
    "source_artwork_sha256",
    "source_width",
    "source_height",
    "source_cells",
    "working_width",
    "working_height",
    "working_cells",
    "dirty_cell_count",
}
DASHBOARD_OPERATION = "factory-operations-dashboard-inspection"
OWNER_UPLOAD_OPERATION = "owner-upload-import"
STUDIO_EXTENSION_OPERATION = "studio-extension"


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _studio_error(message: str) -> dict[str, object]:
    return {
        "operation": STUDIO_OPERATION,
        "scope": STUDIO_SCOPE,
        "state": "ERROR",
        "disposition": "ERROR",
        "error": f"ERROR — manual artwork structural revalidation: {message[:512]}",
    }


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _exact_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{label} must be an integer")
    return int(value)


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _cells(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or any(type(cell) is not str for cell in value):
        raise ValueError(f"{label} must be an array of logical color IDs")
    return list(value)


def _inside_output(path: Path, output_root: Path) -> bool:
    try:
        path.relative_to(output_root)
    except ValueError:
        return False
    return True


def _source_file_hashes(bundle: object) -> dict[str, str]:
    return {
        "artwork.png": hashlib.sha256(bundle.artwork_png).hexdigest(),  # type: ignore[attr-defined]
        "artwork.json": hashlib.sha256(bundle.artwork_json).hexdigest(),  # type: ignore[attr-defined]
        "metadata.json": hashlib.sha256(bundle.metadata_json).hexdigest(),  # type: ignore[attr-defined]
    }


def _dashboard_error(message: str) -> dict[str, object]:
    return {
        "operation": DASHBOARD_OPERATION,
        "state": "ERROR",
        "disposition": "ERROR",
        "error": f"ERROR — canonical batch dashboard inspection: {message[:512]}",
    }


def _dashboard_manifest_path(raw_path: object) -> Path:
    if type(raw_path) is not str or not raw_path.strip():
        raise ValueError("manifest path must be a non-empty local path")
    manifest_path = Path(raw_path).resolve()
    output_root = (_repository_root() / "level_factory" / "output").resolve()
    if manifest_path.name != "batch-manifest.json" or not _inside_output(manifest_path, output_root):
        raise ValueError("manifest path must be batch-manifest.json inside the approved Factory output area")
    if not manifest_path.is_file():
        raise ValueError("canonical batch manifest does not exist")
    return manifest_path


def _dashboard_projection(manifest_path: Path) -> dict[str, object]:
    from scrubbots_pixel_factory.cli.main import (
        _accepted_grids,
        _resume_registry,
        _validate_attempt_history,
        _validate_manifest,
    )

    raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = _validate_manifest(raw_manifest, manifest_path)
    registry = _resume_registry(manifest, None)
    accepted = _accepted_grids(manifest_path.parent, manifest)
    _validate_attempt_history(manifest, registry, accepted)

    attempts = list(manifest["attempts"])
    disposition_counts = {
        "ACCEPTED": 0,
        "QUALITY_REJECTED": 0,
        "GENERATOR_FAILURE": 0,
        "DUPLICATE": 0,
    }
    rejection_code_counts: dict[str, int] = {}
    for attempt in attempts:
        status = str(attempt["status"])
        disposition_counts[status] = disposition_counts.get(status, 0) + 1
        for code in attempt["rejection_codes"]:
            rejection_code_counts[str(code)] = rejection_code_counts.get(str(code), 0) + 1

    request_template = dict(manifest["request_template"])
    latest_attempt = dict(attempts[-1]) if attempts else {}
    return {
        "operation": DASHBOARD_OPERATION,
        "state": "READY",
        "disposition": "READY",
        "source_manifest_path": str(manifest_path),
        "batch_id": manifest["batch_id"],
        "terminal_state": manifest["terminal_state"],
        "requested_count": manifest["requested_count"],
        "max_attempts": manifest["max_attempts"],
        "attempt_count": len(attempts),
        "next_attempt_index": manifest["next_attempt_index"],
        "accepted_count": manifest["accepted_count"],
        "request_context": {
            "difficulty": request_template["difficulty"],
            "width": request_template["width"],
            "height": request_template["height"],
            "generator_mode": request_template["generator_mode"],
        },
        "source_classification": "CANONICAL_BATCH / PROCEDURAL",
        "disposition_counts": disposition_counts,
        "rejection_code_counts": dict(sorted(rejection_code_counts.items())),
        "latest_attempt": latest_attempt,
        "unavailable": {
            "owner_review": "NOT AVAILABLE — no canonical owner-review queue is connected.",
            "solver": "NOT AVAILABLE — gameplay solver evidence is pending M03.",
            "difficulty_v1": "NOT AVAILABLE — measured Difficulty V1 is pending M04.",
            "timing": "NOT AVAILABLE — canonical batch timing evidence is not recorded.",
            "provider_cost": "NOT AVAILABLE — provider accounting is not connected.",
        },
    }


def _dashboard_inspect_main(arguments: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="scrubbots-pixel-factory dashboard-inspect")
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args(list(arguments))
    try:
        manifest_path = _dashboard_manifest_path(args.manifest)
        payload = _dashboard_projection(manifest_path)
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except Exception as exc:  # fail closed at the process boundary
        payload = _dashboard_error(str(exc))
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 2


def _owner_upload_main(arguments: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="scrubbots-pixel-factory owner-upload")
    parser.add_argument("--source", required=True)
    args = parser.parse_args(list(arguments))
    from scrubbots_pixel_factory.owner_upload import import_owner_upload

    payload = import_owner_upload(args.source)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if payload.get("state") in {"IMPORTED", "ALREADY_IMPORTED"} else 2


def _studio_extension_main(arguments: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="scrubbots-pixel-factory studio-extension")
    parser.add_argument("--operation", required=True)
    parser.add_argument("--request-json", default="{}")
    parser.add_argument("--request-file")
    parser.add_argument("--request-base64")
    args = parser.parse_args(list(arguments))
    try:
        if args.request_file:
            request = json.loads(Path(args.request_file).read_text(encoding="utf-8"))
        elif args.request_base64:
            request = json.loads(base64.b64decode(args.request_base64).decode("utf-8"))
        else:
            request = json.loads(args.request_json)
        if not isinstance(request, dict):
            raise ValueError("request-json must be an object")
        from scrubbots_pixel_factory import studio_extensions as extensions
        operation = args.operation
        if operation == "library-refresh":
            payload = extensions.library_refresh()
        elif operation == "library-save":
            payload = extensions.save_library_metadata(str(request["source_id"]), str(request.get("label", "")), request.get("tags", []))
        elif operation == "validate-source":
            payload = extensions.validate_owner_source(str(request["source_id"]))
        elif operation == "candidate-inbox":
            payload = extensions.candidate_inbox()
        elif operation == "owner-review":
            payload = extensions.record_owner_review(str(request["candidate_id"]), str(request["disposition"]), str(request.get("reason", "")), str(request.get("note", "")))
        elif operation == "preset-save":
            payload = extensions.save_preset(str(request["preset_id"]), str(request["name"]), str(request["operation"]), request.get("settings", {}), str(request.get("description", "")))
        elif operation == "preset-load":
            payload = extensions.load_preset(str(request["preset_id"]))
        elif operation == "preset-expand":
            payload = extensions.expand_preset(str(request["preset_id"]), request.get("overrides", {}))
        elif operation == "preset-delete":
            extensions.delete_preset(str(request["preset_id"]))
            payload = {"state": "DELETED", "preset_id": request["preset_id"]}
        elif operation == "discover":
            payload = extensions.discover_records(str(request.get("query", "")), request.get("filters", {}), request.get("collection"))
        elif operation == "reproduce-capability":
            payload = extensions.reproduce_capability(str(request["candidate_id"]))
        elif operation == "record-failure":
            payload = extensions.record_failure(str(request["operation"]), str(request["stage"]), str(request["disposition"]), str(request["reason"]), request.get("inputs", {}))
        elif operation == "retry-failure":
            payload = extensions.retry_failure(str(request["failure_id"]), request.get("changes", {}))
        elif operation == "batch-import":
            payload = extensions.batch_import(request.get("paths", []))
        elif operation == "session-save":
            payload = extensions.save_session(str(request["session_id"]), request.get("state", {}))
        elif operation == "session-restore":
            payload = extensions.restore_session(str(request["session_id"]))
        elif operation == "similarity":
            payload = extensions.similarity(request.get("left", {}), request.get("right", {}), float(request.get("threshold", 0.92)))
        elif operation == "pipeline":
            payload = extensions.run_pipeline(source_id=request.get("source_id"), candidate_id=request.get("candidate_id"), request=request.get("request"))
        elif operation == "comparison":
            payload = extensions.compare_candidates(request.get("candidate_ids", []))
        elif operation == "readiness":
            payload = extensions.readiness_card(str(request["candidate_id"]))
        elif operation == "cost-center":
            payload = extensions.cost_center(request.get("records", []))
        else:
            raise ValueError(f"unsupported Studio extension operation: {operation}")
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except Exception as exc:
        payload = {"operation": STUDIO_EXTENSION_OPERATION, "state": "ERROR", "disposition": "ERROR", "error": f"ERROR — Studio extension: {str(exc)[:512]}"}
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 2


def _validate_studio_request(raw: object) -> dict[str, object]:
    request = dict(_mapping(raw, "request"))
    if set(request) != STUDIO_REQUEST_KEYS:
        raise ValueError("request schema contains unexpected or missing fields")
    if request["schema"] != STUDIO_REQUEST_SCHEMA or request["schema_version"] != STUDIO_REQUEST_VERSION:
        raise ValueError("request schema/version is unsupported")
    if request["operation"] != STUDIO_OPERATION:
        raise ValueError("request operation is unsupported")
    normalized: dict[str, object] = {
        "source_bundle_path": _text(request["source_bundle_path"], "source_bundle_path"),
        "source_candidate_id": _text(request["source_candidate_id"], "source_candidate_id"),
        "source_artwork_sha256": _text(request["source_artwork_sha256"], "source_artwork_sha256"),
        "source_width": _exact_int(request["source_width"], "source_width"),
        "source_height": _exact_int(request["source_height"], "source_height"),
        "source_cells": _cells(request["source_cells"], "source_cells"),
        "working_width": _exact_int(request["working_width"], "working_width"),
        "working_height": _exact_int(request["working_height"], "working_height"),
        "working_cells": _cells(request["working_cells"], "working_cells"),
        "dirty_cell_count": _exact_int(request["dirty_cell_count"], "dirty_cell_count"),
    }
    if len(normalized["source_artwork_sha256"]) != 64 or any(character not in "0123456789abcdef" for character in normalized["source_artwork_sha256"]):  # type: ignore[arg-type]
        raise ValueError("source_artwork_sha256 must be a lowercase SHA-256 digest")
    for key in ("source_width", "source_height", "working_width", "working_height"):
        if normalized[key] <= 0:  # type: ignore[operator]
            raise ValueError(f"{key} must be positive")
    if normalized["source_width"] != normalized["working_width"] or normalized["source_height"] != normalized["working_height"]:
        raise ValueError("working dimensions must equal source dimensions")
    expected_cells = normalized["source_width"] * normalized["source_height"]  # type: ignore[operator]
    if len(normalized["source_cells"]) != expected_cells or len(normalized["working_cells"]) != expected_cells:  # type: ignore[arg-type]
        raise ValueError("logical cell count does not match the source dimensions")
    actual_dirty = sum(source != working for source, working in zip(normalized["source_cells"], normalized["working_cells"]))  # type: ignore[arg-type]
    if normalized["dirty_cell_count"] != actual_dirty:
        raise ValueError("dirty_cell_count does not match the exact source/working difference")
    return normalized


def _run_studio_revalidation(raw_request: object) -> dict[str, object]:
    request = _validate_studio_request(raw_request)
    from scrubbots_pixel_factory import QualityPolicy, evaluate_grid, logical_grid_hash, read_bundle

    output_root = (_repository_root() / "level_factory" / "output").resolve()
    source_bundle = Path(str(request["source_bundle_path"])).resolve()
    if not _inside_output(source_bundle, output_root):
        raise ValueError("source bundle is outside the approved Factory output area")
    bundle = read_bundle(source_bundle)
    source_width = int(request["source_width"])
    source_height = int(request["source_height"])
    source_cells = list(request["source_cells"])  # type: ignore[arg-type]
    working_cells = list(request["working_cells"])  # type: ignore[arg-type]
    source_hash = logical_grid_hash(source_width, source_height, source_cells)
    bundle_source_hash = logical_grid_hash(bundle.artwork.width, bundle.artwork.height, bundle.artwork.cells)
    if bundle.artwork.candidate_id != request["source_candidate_id"]:
        raise ValueError("source candidate identity does not match the canonical bundle")
    if (bundle.artwork.width, bundle.artwork.height) != (source_width, source_height):
        raise ValueError("source dimensions do not match the canonical bundle")
    if tuple(source_cells) != bundle.artwork.cells or source_hash != bundle.artwork.grid_hash or bundle_source_hash != bundle.artwork.grid_hash:
        raise ValueError("source logical grid does not match the canonical bundle")
    file_hashes = _source_file_hashes(bundle)
    if file_hashes["artwork.png"] != request["source_artwork_sha256"]:
        raise ValueError("source artwork bytes do not match the retained editor source")
    quality = _mapping(bundle.metadata.get("quality"), "metadata.quality")
    source_report = _mapping(quality.get("report"), "metadata.quality.report")
    policy_data = dict(_mapping(source_report.get("policy"), "metadata.quality.report.policy"))
    policy = QualityPolicy(**policy_data)
    if policy.as_dict() != policy_data:
        raise ValueError("source quality policy is not canonical")
    canonical_source_report = evaluate_grid(source_width, source_height, source_cells, policy=policy).as_dict()
    if canonical_source_report != dict(source_report):
        raise ValueError("source quality report does not match the exact recorded policy")
    if int(request["dirty_cell_count"]) == 0:
        return {
            "operation": STUDIO_OPERATION,
            "scope": STUDIO_SCOPE,
            "state": "NOT_REQUIRED",
            "disposition": "NOT_REQUIRED",
            "source_candidate_id": bundle.artwork.candidate_id,
            "source_grid_hash": source_hash,
            "working_grid_hash": source_hash,
            "width": source_width,
            "height": source_height,
            "dirty_cell_count": 0,
            "reason": "NOT_REQUIRED — the working artwork matches the immutable source.",
            "source_quality_policy": policy.as_dict(),
            "source_file_sha256": file_hashes,
        }
    working_hash = logical_grid_hash(source_width, source_height, working_cells)
    report = evaluate_grid(source_width, source_height, working_cells, policy=policy)
    return {
        "operation": STUDIO_OPERATION,
        "scope": STUDIO_SCOPE,
        "state": "RESULT",
        "disposition": "ACCEPT" if report.accepted else "REJECT",
        "source_candidate_id": bundle.artwork.candidate_id,
        "source_grid_hash": source_hash,
        "working_grid_hash": working_hash,
        "width": source_width,
        "height": source_height,
        "dirty_cell_count": int(request["dirty_cell_count"]),
        "quality_schema": "scrubbots-quality",
        "quality_schema_version": 1,
        "quality_policy_version": policy.version,
        "source_quality_policy": policy.as_dict(),
        "accepted": report.accepted,
        "decision": "ACCEPT" if report.accepted else "REJECT",
        "rejection_codes": list(report.rejection_codes),
        "quality_report": report.as_dict(),
        "source_file_sha256": file_hashes,
    }


def _studio_revalidate_main(arguments: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="scrubbots-pixel-factory studio-revalidate-art")
    parser.add_argument("--request-file", required=True)
    args = parser.parse_args(list(arguments))
    try:
        request_path = Path(args.request_file).resolve()
        raw_request = json.loads(request_path.read_text(encoding="utf-8"))
        payload = _run_studio_revalidation(raw_request)
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except Exception as exc:  # fail closed at the process boundary
        payload = _studio_error(str(exc))
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 2


def _main() -> int:
    repository_root = _repository_root()
    sys.path.insert(0, str(repository_root / "src"))
    if len(sys.argv) > 1 and sys.argv[1] == "dashboard-inspect":
        return _dashboard_inspect_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "studio-revalidate-art":
        return _studio_revalidate_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "owner-upload":
        return _owner_upload_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "studio-extension":
        return _studio_extension_main(sys.argv[2:])
    from scrubbots_pixel_factory.cli.main import main as canonical_main

    return canonical_main()


if __name__ == "__main__":
    raise SystemExit(_main())
