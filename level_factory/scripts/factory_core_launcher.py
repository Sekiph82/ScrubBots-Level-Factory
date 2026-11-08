"""Thin repository-local launcher for the canonical Python Factory Core CLI."""

from __future__ import annotations

import argparse
import base64
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import uuid
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
_MAX_STUDIO_REQUEST_BYTES = 384 * 1024


def _repository_root() -> Path:
    from scrubbots_pixel_factory.owner_art_storage import factory_repository_root

    return factory_repository_root(__file__)


def _set_studio_project_root() -> Path | None:
    """Tell imported canonical modules which installed/source Studio launched this worker."""
    project_root = Path(__file__).resolve().parents[1]
    if not (project_root / "project.godot").is_file():
        os.environ.pop("SCRUBBOTS_STUDIO_PROJECT_ROOT", None)
        return None
    os.environ["SCRUBBOTS_STUDIO_PROJECT_ROOT"] = str(project_root)
    return project_root


def _folder_activity_context(request: Mapping[str, object]):
    run_id = str(request.get("activity_run_id", ""))
    source_id = str(request.get("activity_source_id", ""))
    source_sha = str(request.get("activity_source_sha256", ""))
    if not run_id and not source_id and not source_sha:
        return None, None, []
    folder_identity = Path(str(request.get("folder", ""))).expanduser().resolve(strict=False).as_posix().lower()
    expected_sha = hashlib.sha256(folder_identity.encode("utf-8")).hexdigest()
    if source_id != "owner-folder-preview-" + expected_sha or source_sha != expected_sha:
        raise ValueError("folder activity identity does not match the selected canonical path")
    from scrubbots_pixel_factory.pipeline_activity import PipelineActivityWriter

    project_output = Path(__file__).resolve().parents[1] / "output" / "studio-pipeline-activity"
    expected_log_path = project_output / (run_id + ".jsonl")
    requested_log_path = str(request.get("activity_log_path", ""))
    if requested_log_path:
        resolved_requested_log = Path(requested_log_path).resolve(strict=False)
        if resolved_requested_log != expected_log_path.resolve(strict=False):
            raise ValueError("folder activity log path does not match this Studio project's output directory")
    writer = PipelineActivityWriter(
        _repository_root(), run_id, source_id, source_sha,
        output_directory=project_output,
    )
    errors: list[str] = []

    def emit(event: Mapping[str, object]) -> None:
        writer.emit(
            str(event.get("stage", "FOLDER")),
            str(event.get("state", "RUNNING")),
            str(event.get("message", "")),
        )

    emit({"stage": "FOLDER", "state": "RUNNING", "message": "Selected folder: " + str(request.get("folder", ""))})
    return writer, emit, errors


def _finish_folder_activity(writer, emit, errors: list[str], payload: dict[str, object], *, phase: str) -> dict[str, object]:
    if writer is None:
        return payload
    try:
        if phase == "PREVIEW":
            entries = payload.get("entries", [])
            dispositions = [str(item.get("disposition", "REJECTED")) for item in entries if isinstance(item, Mapping)] if isinstance(entries, list) else []
            eligible = sum(value == "ELIGIBLE" for value in dispositions)
            existing = sum(value in {"ALREADY_IMPORTED", "SKIPPED_DUPLICATE"} for value in dispositions)
            rejected = sum(value == "REJECTED" for value in dispositions)
            failed = sum(value == "FAILED" for value in dispositions)
            message = "Preview complete: %d/%d checked · %d new · %d already imported · %d failed · %d rejected." % (
                len(dispositions), int(payload.get("png_count", len(dispositions))), eligible, existing, failed, rejected,
            )
            writer.emit("PIPELINE", "COMPLETE", message, backend_disposition="FOLDER_PREVIEW_COMPLETE")
        else:
            counts = payload.get("counts", {})
            counts = counts if isinstance(counts, Mapping) else {}
            items = payload.get("items", [])
            total = len(items) if isinstance(items, list) else 0
            writer.emit("PIPELINE", "COMPLETE", "Import complete: %d/%d processed · %d imported · %d already present · %d failed · %d rejected." % (
                total, total, int(counts.get("imported", 0)), int(counts.get("skipped", 0)),
                int(counts.get("failed", 0)), int(counts.get("rejected", 0)),
            ), backend_disposition="FOLDER_IMPORT_COMPLETE")
    except Exception as exc:
        if not errors:
            errors.append(str(exc)[:160])
    payload["activity_log_path"] = str(writer.path)
    payload["activity_log_state"] = "COMPLETE" if not errors and writer.terminal_emitted else "INCOMPLETE"
    if errors:
        payload["activity_log_error"] = errors[0]
    return payload


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


def _canonical_final_source_gate(source_ids: Sequence[object]) -> dict[str, object] | None:
    """Fail closed unless every requested source is a current valid PixelLab Final PNG."""

    from scrubbots_pixel_factory import studio_extensions

    requested = [str(source_id) for source_id in source_ids if str(source_id)]
    try:
        from scrubbots_pixel_factory.supply_pipeline.pinned_game_source import expected_runtime_root

        active_ids, inventory_errors = studio_extensions._sync_current_pixellab_final_sources(
            _repository_root(), game_project=expected_runtime_root()
        )
    except Exception as exc:
        return {"state": "BLOCKED", "disposition": "CANONICAL_FINAL_INVENTORY_UNAVAILABLE",
                "error": str(exc)[:512], "invalid_final_sources": []}
    excluded = sorted(set(requested) - active_ids)
    if excluded:
        return {"state": "BLOCKED", "disposition": "PIXELLAB_FINAL_ONLY",
                "error": "New solving accepts only currently validated PNGs in data/output/Pixellab/Final.",
                "excluded_source_ids": excluded, "invalid_final_sources": inventory_errors}
    return None


def _canonical_final_membership_gate(source_ids: Sequence[object]) -> dict[str, object] | None:
    """Require source identities to belong to valid direct PNGs in current Final.

    Logical LevelData/palette validation is deliberately left to the batch plan,
    which records invalid artwork as REJECTED per item instead of blocking every
    otherwise eligible source in a large folder.
    """
    from scrubbots_pixel_factory import owner_art_storage
    from scrubbots_pixel_factory.owner_folder_batch import scan_owner_source_folder

    requested = [str(source_id) for source_id in source_ids if str(source_id)]
    try:
        final_directory = owner_art_storage.owner_art_paths(_repository_root())["pixellab_final"]
        scan = scan_owner_source_folder(final_directory, repository_root=_repository_root())
        if scan.get("provider") != "PIXELLAB":
            raise ValueError("canonical PixelLab Final source authority could not be established")
        members = {
            "owner-upload-" + str(entry.get("source_sha256", ""))
            for entry in scan.get("entries", [])
            if isinstance(entry, Mapping)
            and entry.get("disposition") in {"ELIGIBLE", "ALREADY_IMPORTED"}
            and re.fullmatch(r"[0-9a-f]{64}", str(entry.get("source_sha256", "")))
        }
    except Exception as exc:
        return {"state": "BLOCKED", "disposition": "CANONICAL_FINAL_INVENTORY_UNAVAILABLE",
                "error": str(exc)[:512]}
    excluded = sorted(set(requested) - members)
    if excluded:
        return {"state": "BLOCKED", "disposition": "PIXELLAB_FINAL_ONLY",
                "error": "New solving accepts only direct PNG identities currently present in PixelLab Final.",
                "excluded_source_ids": excluded}
    return None


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


def _create_exclusive_json(path: Path, value: Mapping[str, object]) -> bool:
    """Create one durable claim atomically; never replace an existing claim."""
    payload = (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                          separators=(",", ":")) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    return True


def _write_durable_json(path: Path, value: Mapping[str, object]) -> None:
    """Atomically replace one owned ledger record after flushing its contents."""
    payload = (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                          separators=(",", ":")) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    except Exception:
        # Do not remove a possibly unrelated path after an unexpected error.
        # The digest claim remains and therefore still blocks repeat billing.
        raise


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
            "width": request_template["width"],
            "height": request_template["height"],
            "generator_mode": request_template["generator_mode"],
            "background_intent": request_template.get("background_intent", "BACKGROUND"),
        },
        "source_classification": "CANONICAL_BATCH / PROCEDURAL",
        "disposition_counts": disposition_counts,
        "rejection_code_counts": dict(sorted(rejection_code_counts.items())),
        "latest_attempt": latest_attempt,
        "unavailable": {
            "owner_review": "NOT AVAILABLE — no canonical owner-review queue is connected.",
            "solver": "NOT AVAILABLE — canonical ZIP solver evidence is not connected.",
            "difficulty_v1": "NOT AVAILABLE — official Difficulty V1 evidence is not connected.",
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
            request_path = Path(args.request_file)
            if request_path.stat().st_size > _MAX_STUDIO_REQUEST_BYTES:
                raise ValueError("studio request exceeds the bounded 384 KiB input limit")
            request_text = request_path.read_text(encoding="utf-8")
        elif args.request_base64:
            if len(args.request_base64) > ((_MAX_STUDIO_REQUEST_BYTES * 4 // 3) + 8):
                raise ValueError("base64 studio request exceeds the bounded 384 KiB input limit")
            request_text = base64.b64decode(args.request_base64, validate=True).decode("utf-8")
        else:
            request_text = args.request_json
        if len(request_text.encode("utf-8")) > _MAX_STUDIO_REQUEST_BYTES:
            raise ValueError("studio request exceeds the bounded 384 KiB input limit")
        request = json.loads(request_text)
        if not isinstance(request, dict):
            raise ValueError("request-json must be an object")
        from scrubbots_pixel_factory import studio_extensions as extensions
        operation = args.operation
        if operation != "png-batch-control":
            from scrubbots_pixel_factory.studio_lifecycle import studio_shutdown_requested
            if studio_shutdown_requested():
                print(json.dumps({"operation": STUDIO_EXTENSION_OPERATION, "state": "CANCELLED",
                                  "disposition": "STUDIO_SHUTDOWN", "error": "Factory Studio is closing."},
                                 ensure_ascii=False, sort_keys=True, separators=(",", ":")))
                return 0
        if operation == "owner-pages":
            payload = extensions.owner_pages_snapshot()
        elif operation == "library-refresh":
            payload = extensions.library_refresh()
        elif operation == "library-save":
            payload = extensions.save_library_metadata(str(request["source_id"]), str(request.get("label", "")), request.get("tags", []))
        elif operation == "validate-source":
            payload = extensions.validate_owner_source(str(request["source_id"]))
        elif operation == "validate-source-readonly":
            payload = extensions.validate_owner_source(
                str(request["source_id"]),
                persist=False,
                game_project=request.get("game_project"),
            )
        elif operation == "restore-source-run-readonly":
            payload = extensions.restore_source_run(
                str(request["source_id"]),
                game_project=request.get("game_project"),
                source_directory=request.get("source_directory"),
            )
        elif operation == "candidate-inbox":
            payload = extensions.candidate_inbox()
        elif operation == "owner-review":
            payload = extensions.record_owner_review(str(request["candidate_id"]), str(request["disposition"]), str(request.get("reason", "")), str(request.get("note", "")))
            from scrubbots_pixel_factory.owner_release_library import record_review_outcome
            payload["owner_release_status"] = record_review_outcome(str(request["candidate_id"]), str(request["disposition"]), payload)
        elif operation == "preset-save":
            payload = extensions.save_preset(str(request["preset_id"]), str(request["name"]), str(request["operation"]), request.get("settings", {}), str(request.get("description", "")))
        elif operation == "preset-load":
            payload = extensions.load_preset(str(request["preset_id"]))
        elif operation == "preset-expand":
            payload = extensions.expand_preset(str(request["preset_id"]), request.get("overrides", {}))
        elif operation == "preset-apply":
            payload = extensions.apply_preset(str(request["preset_id"]), request.get("overrides", {}))
        elif operation == "preset-delete":
            extensions.delete_preset(str(request["preset_id"]))
            payload = {"state": "DELETED", "preset_id": request["preset_id"]}
        elif operation == "discover":
            payload = extensions.discover_records(str(request.get("query", "")), request.get("filters", {}), request.get("collection"), request.get("similarity_peer_id"))
        elif operation == "reproduce-capability":
            payload = extensions.reproduce_capability(str(request["candidate_id"]))
        elif operation == "reproduce-exact":
            payload = extensions.reproduce_exact(str(request["candidate_id"]))
        elif operation == "revision-create":
            payload = extensions.revision_create(str(request["candidate_id"]), int(request["width"]), int(request["height"]), request["cells"], request.get("parent_revision_id"), str(request.get("change_summary", "")), request.get("edit_operations", []))
        elif operation == "revision-list":
            payload = extensions.revision_list(str(request["candidate_id"]))
        elif operation == "revision-compare":
            payload = extensions.revision_compare(str(request["candidate_id"]), str(request["left_revision_id"]), str(request["right_revision_id"]))
        elif operation == "revision-load":
            payload = extensions.revision_load(str(request["candidate_id"]), str(request["revision_id"]))
        elif operation == "retry-failure":
            payload = extensions.retry_failure(str(request["failure_id"]), request.get("changes", {}))
        elif operation == "failures-list":
            payload = extensions.list_failures()
        elif operation == "batch-import":
            payload = extensions.batch_import(request.get("paths", []))
            from scrubbots_pixel_factory.owner_release_library import record_import_items
            payload["owner_release_archive"] = record_import_items(payload)
        elif operation == "owner-folder-import":
            from scrubbots_pixel_factory.owner_folder_batch import import_owner_source_folder
            activity_writer, progress_callback, activity_errors = _folder_activity_context(request)
            try:
                payload = import_owner_source_folder(
                    str(request.get("folder", "")),
                    explicit_alternative=request.get("explicit_alternative") is True,
                    progress_callback=progress_callback,
                )
                from scrubbots_pixel_factory.owner_release_library import record_import_items
                payload["owner_release_archive"] = record_import_items(payload)
            except Exception as exc:
                if activity_writer is not None and not activity_writer.terminal_emitted:
                    try:
                        activity_writer.emit("PIPELINE", "ERROR", "Folder import failed: " + str(exc)[:180], backend_disposition="FOLDER_IMPORT_ERROR")
                    except Exception:
                        pass
                raise
            payload = _finish_folder_activity(activity_writer, progress_callback, activity_errors, payload, phase="IMPORT")
        elif operation == "owner-folder-preview":
            from scrubbots_pixel_factory.owner_folder_batch import scan_owner_source_folder
            activity_writer, progress_callback, activity_errors = _folder_activity_context(request)
            try:
                payload = scan_owner_source_folder(
                    str(request.get("folder", "")),
                    explicit_alternative=request.get("explicit_alternative") is True,
                    progress_callback=progress_callback,
                )
            except Exception as exc:
                if activity_writer is not None and not activity_writer.terminal_emitted:
                    try:
                        activity_writer.emit("PIPELINE", "ERROR", "Folder preview failed: " + str(exc)[:180], backend_disposition="FOLDER_PREVIEW_ERROR")
                    except Exception:
                        pass
                raise
            payload = _finish_folder_activity(activity_writer, progress_callback, activity_errors, payload, phase="PREVIEW")
        elif operation == "batch-load":
            payload = extensions.batch_load(str(request["batch_id"]))
        elif operation == "loaded-png-batch-create":
            source_ids = request.get("source_ids", [])
            gate = _canonical_final_membership_gate(source_ids) if isinstance(source_ids, Sequence) and not isinstance(source_ids, (str, bytes)) else {
                "state": "BLOCKED", "disposition": "PIXELLAB_FINAL_ONLY", "error": "source_ids must be a list of canonical Final identities."}
            payload = gate if gate is not None else extensions.loaded_png_batch_create(source_ids)
        elif operation == "loaded-png-batch-find":
            payload = extensions.loaded_png_batch_find(request.get("source_ids", []))
        elif operation == "png-batch-create":
            loaded = extensions.batch_load(str(request["batch_id"]))
            batch = loaded.get("batch", {})
            source_ids = [str(item.get("source_id", "")) for item in batch.get("items", []) if isinstance(item, Mapping)]
            gate = _canonical_final_membership_gate(source_ids)
            payload = gate if gate is not None else extensions.png_batch_create(str(request["batch_id"]), request.get("settings", {}))
        elif operation == "png-batch-retry-failed":
            status = extensions.png_batch_status(str(request["job_id"]))
            job = status.get("job", {})
            source_ids = [str(item.get("source_id", "")) for item in job.get("items", []) if isinstance(item, Mapping)]
            gate = _canonical_final_source_gate(source_ids)
            payload = gate if gate is not None else extensions.png_batch_retry_failed(str(request["job_id"]))
        elif operation == "png-batch-status":
            payload = extensions.png_batch_status(str(request["job_id"]))
        elif operation == "png-batch-latest":
            payload = extensions.png_batch_latest(request.get("batch_id"))
        elif operation == "png-batch-control":
            payload = extensions.png_batch_control(str(request["job_id"]), str(request["action"]))
        elif operation == "png-batch-run":
            before = extensions.png_batch_status(str(request["job_id"]))
            job = before.get("job", {}) if isinstance(before, Mapping) else {}
            sources = [
                str(item.get("source_id", "")) for item in job.get("items", [])
                if isinstance(item, Mapping) and str(item.get("status", "")) in {"QUEUED", "RUNNING"}
            ]
            gate = _canonical_final_source_gate(sources)
            if gate is not None:
                payload = gate
            else:
                from scrubbots_pixel_factory.owner_release_library import assert_solver_allowed
                assert_solver_allowed(sources)
                payload = extensions.png_batch_run(str(request["job_id"]), request.get("expected_batch_id"))
                completed_job = payload.get("job", {}) if isinstance(payload, Mapping) else {}
                if isinstance(completed_job, Mapping) and completed_job.get("state") != "INTERRUPTED":
                    from scrubbots_pixel_factory.owner_release_library import record_batch_outcomes
                    payload["owner_release_archive"] = record_batch_outcomes(completed_job)
        elif operation == "session-save":
            payload = extensions.save_session(str(request["session_id"]), request.get("state", {}))
        elif operation == "session-restore":
            payload = extensions.restore_session(str(request["session_id"]))
        elif operation == "similarity":
            payload = extensions.similarity_canonical(str(request["left_id"]), str(request["right_id"]), float(request.get("threshold", 0.92)))
        elif operation == "pipeline":
            if request.get("source_id"):
                gate = _canonical_final_source_gate([str(request["source_id"])])
            else:
                gate = None
            if gate is not None:
                payload = gate
            else:
                if request.get("source_id"):
                    from scrubbots_pixel_factory.owner_release_library import assert_solver_allowed
                    assert_solver_allowed([str(request["source_id"])])
                payload = extensions.run_pipeline(source_id=request.get("source_id"), candidate_id=request.get("candidate_id"), request=request.get("request"))
            if request.get("source_id") and gate is None:
                from scrubbots_pixel_factory.owner_release_library import transition_pipeline
                payload["owner_release_status"] = transition_pipeline(str(request["source_id"]), payload)
        elif operation == "comparison":
            payload = extensions.compare_candidates(request.get("candidate_ids", []))
        elif operation == "readiness":
            payload = extensions.readiness_card(
                str(request["candidate_id"]), request.get("current_game_preflight")
            )
        elif operation == "cost-center":
            payload = extensions.canonical_cost_center(request.get("scope"), request.get("provider"))
        elif operation == "owner-release-library":
            from scrubbots_pixel_factory.owner_release_library import list_records
            payload = list_records(str(request.get("status")) if request.get("status") else None)
        elif operation == "release-pool":
            from scrubbots_pixel_factory.supply_pipeline.release_pool import release_entries
            entries = release_entries()
            payload = {"state": "READY", "pool_size": len(entries), "entries": entries}
        elif operation == "semantic-generate":
            payload = _semantic_generate(request)
        elif operation == "pixellab-pro-4x4-reconcile":
            payload = _semantic_reconcile_pixellab_pro_4x4(request)
        elif operation == "pixellab-batch-inspect":
            payload = _inspect_pixellab_batch(request, extensions)
        elif operation == "pixellab-pro-4x4-import":
            payload = _semantic_import_pixellab_pro_4x4(request)
        elif operation == "provider-options":
            payload = _provider_options()
        elif operation == "canonical-palette":
            from scrubbots_pixel_factory import CANONICAL_PALETTE
            payload = {"state": "READY", "palette_id": "V3", "colors": [
                {"id": color.id, "hex": color.hex} for color in CANONICAL_PALETTE.colors
            ]}
        elif operation == "alpix-generate":
            payload = _alpix_generate(request)
        elif operation == "alpix-csv-job":
            payload = _alpix_csv_job(request)
        elif operation == "campaign-build":
            from scrubbots_pixel_factory.supply_pipeline.release_pool import build_release_plan
            payload = build_release_plan(k=int(request.get("k", 100)), locks=request.get("locks", {}))
        elif operation == "campaign-approve":
            from scrubbots_pixel_factory.supply_pipeline.release_route_a import release_approved_campaign
            from scrubbots_pixel_factory import studio_extensions as extensions
            import os
            game_project = os.environ.get("SCRUBBOTS_PROJECT", "").strip()
            if not game_project:
                raise ValueError("SCRUBBOTS_PROJECT must identify the configured Sekiph82/Scrubbots checkout")
            payload = release_approved_campaign(plan_hash=str(request["plan_hash"]), game_project=game_project, studio_approval=True)
        elif operation == "scrubbots-publish":
            from scrubbots_publish_handoff import (
                publish_preflight, publish_to_staging, publish_to_production,
            )
            action = str(request.get("action", "preflight"))
            if action == "preflight":
                payload = publish_preflight(request)
            elif action == "publish-staging":
                payload = publish_to_staging(request)
            elif action == "publish-production":
                payload = publish_to_production(request, owner_confirmation=request.get("owner_confirmation", {}))
            else:
                raise ValueError("scrubbots-publish action must be preflight, publish-staging, or publish-production")
        else:
            raise ValueError(f"unsupported Studio extension operation: {operation}")
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except Exception as exc:
        payload = {"operation": STUDIO_EXTENSION_OPERATION, "state": "ERROR", "disposition": "ERROR", "error": f"ERROR — Studio extension: {str(exc)[:512]}"}
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 2


def _semantic_generate(request: Mapping[str, object]) -> dict[str, object]:
    """Run an explicitly selected registered semantic provider and import its bytes.

    Secrets are read only by the provider adapter from process environment. They
    are never accepted in the request payload or copied into the result.
    """
    allowed = {"prompt", "style", "provider_id", "provider_model", "width", "height", "max_colors", "seed", "background_intent", "operation_id"}
    if set(request) - allowed or "prompt" not in request:
        raise ValueError("semantic generation request contains unsupported or missing fields")
    if request.get("provider_id") != "PIXELLAB":
        raise ValueError("only the configured PIXELLAB provider is currently executable")
    prompt = _text(request.get("prompt"), "prompt")
    style_value = request.get("style", "")
    if type(style_value) is not str:
        raise ValueError("style must be a string")
    style = style_value.strip()
    width, height = _exact_int(request.get("width"), "width"), _exact_int(request.get("height"), "height")
    seed = request.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, (str, int)):
        raise ValueError("seed must be a string or integer")
    model = _text(request.get("provider_model"), "provider_model").upper()
    background = request.get("background_intent", "TRANSPARENT")
    if background not in {"TRANSPARENT", "BACKGROUND"}:
        raise ValueError("background_intent must be TRANSPARENT or BACKGROUND")
    if model == "PRO_4X4":
        max_colors = _exact_int(request.get("max_colors", 12), "max_colors")
        if not 51 <= width <= 59 or not 51 <= height <= 59:
            raise ValueError("GAME_DIMENSIONS_OUT_OF_RANGE: PixelLab Pro 4x4 requires each axis in 51..59.")
        if not 3 <= max_colors <= 12:
            raise ValueError("MAX_COLORS_OUT_OF_RANGE: choose 3..12.")
        if background != "TRANSPARENT":
            raise ValueError("PixelLab Pro 4x4 requires transparent-background intent.")
        return _semantic_generate_pixellab_pro_4x4(
            prompt=prompt,
            style=style,
            width=width,
            height=height,
            max_colors=max_colors,
            seed=seed,
            operation_id=request.get("operation_id"),
        )
    raise ValueError("PIXELLAB supports only the PRO_4X4 model.")
    descriptor = get_provider_descriptor("PIXELLAB")
    semantic_request = SemanticGenerationRequest(
        output_class=OutputClass.ASSET_ART,
        description=f"{prompt}. Pixel art style: {style}.",
        width=width,
        height=height,
        seed=seed,
        no_background=background == "TRANSPARENT",
        provider_id="PIXELLAB",
        provider_model=model,
        provider_config_version=descriptor.config_version,
    )


def _pixellab_explicit_http_400_rejection(record: Mapping[str, object]) -> bool:
    """Recognize only a definite 400 response without an accepted provider job."""
    if record.get("state") != "HTTP_ERROR" or record.get("job_id"):
        return False
    if record.get("provider_http_status") == 400:
        return True
    # Compatibility with durable records written before HTTP status was stored.
    return record.get("error_code") == "HTTP_ERROR" and record.get("error") == "PixelLab returned HTTP 400."


def _resolved_pixellab_batch_seed(seed: str | int, extensions: object) -> int:
    """Return the exact canonical seed used by the paid PixelLab request path."""
    return extensions._resolved_seed(extensions._resolved_seed(seed))


def _inspect_pixellab_batch(request: Mapping[str, object], extensions: object) -> dict[str, object]:
    """Read prior Pro 4x4 request claims and this month's local request count."""
    import re

    if set(request) != {"csv_path", "source_sha256", "width", "height", "max_colors"}:
        return {"state": "ERROR", "error": "PIXELLAB_BATCH_INSPECT_REQUEST_INVALID"}
    csv_path_value = request.get("csv_path")
    expected_source_sha256 = request.get("source_sha256")
    if (type(csv_path_value) is not str or not csv_path_value.strip()
            or not isinstance(expected_source_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", expected_source_sha256)
            or request.get("width") != 56 or request.get("height") != 56
            or request.get("max_colors") != 12):
        return {"state": "ERROR", "error": "PIXELLAB_BATCH_INSPECT_REQUEST_INVALID"}

    try:
        from scrubbots_pixel_factory.owner_art_storage import OwnerArtStorageError, validate_owner_input_csv
        csv_path = validate_owner_input_csv(csv_path_value, repository_root=_repository_root())
    except (OwnerArtStorageError, OSError, ValueError):
        return {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_OUTSIDE_CANONICAL_INPUT"}
    if csv_path.stat().st_size > 16 * 1024 * 1024:
        return {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_INVALID"}
    source_sha256 = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    if source_sha256 != expected_source_sha256:
        return {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_CHANGED_DURING_PREFLIGHT"}
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            source_rows = list(csv.reader(csv_file))
    except (OSError, UnicodeError, csv.Error):
        return {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_UNREADABLE"}
    source_rows = [row for row in source_rows if row and any(cell.strip() for cell in row)]
    if not source_rows or len(source_rows) > 2001:
        return {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_ROW_COUNT_INVALID"}
    first_cell = source_rows[0][0].strip().lower()
    has_header = first_cell in {"id", "prompt_id", "sprite_id", "prompt"}
    prompt_column = 1
    if has_header:
        normalized_header = [field.strip().lower() for field in source_rows[0]]
        prompt_column = normalized_header.index("prompt") if "prompt" in normalized_header else normalized_header.index("description") if "description" in normalized_header else -1
        if prompt_column < 0:
            return {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_PROMPT_HEADER_MISSING"}
        source_rows = source_rows[1:]
    if not source_rows or len(source_rows) > 2000:
        return {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_ROW_COUNT_INVALID"}

    normalized_rows: list[tuple[int, str, int]] = []
    seen_indexes: set[int] = set()
    try:
        for row_index, row in enumerate(source_rows, start=1):
            if len(row) <= prompt_column:
                return {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_ROW_INVALID"}
            prompt = row[prompt_column].strip()
            if not prompt or len(prompt) > 2000:
                return {"state": "ERROR", "error": "PIXELLAB_BATCH_CSV_PROMPT_INVALID"}
            description_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            identity = row[0].strip() if row[0].strip().lower() not in {"id", "prompt_id", "sprite_id", "prompt"} else str(row_index)
            seed = f"sb-lfx018-csv:{identity}:{description_sha256}"
            seen_indexes.add(row_index)
            normalized_rows.append((row_index, description_sha256, _resolved_pixellab_batch_seed(seed, extensions)))
    except Exception:
        return {"state": "ERROR", "error": "PIXELLAB_BATCH_INSPECT_ROW_INVALID"}

    job_root = (extensions.extensions_root() / "pixellab-jobs").resolve()
    request_records: list[dict[str, object]] = []
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    monthly_paid_requests = 0
    if job_root.exists():
        if not job_root.is_dir():
            return {"state": "ERROR", "error": "PIXELLAB_JOB_LEDGER_UNAVAILABLE"}
        for record_path in sorted(job_root.glob("*.json")):
            if record_path.name.endswith(".claim.json"):
                continue
            try:
                resolved_path = record_path.resolve()
                resolved_path.relative_to(job_root)
                record = json.loads(resolved_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
                return {"state": "ERROR", "error": "PIXELLAB_JOB_LEDGER_UNREADABLE"}
            if (not isinstance(record, dict)
                    or record.get("schema") != "scrubbots-pixellab-pro-4x4-job-v1"
                    or record.get("provider_id") != "PIXELLAB"
                    or record.get("provider_model") != "PRO_4X4"):
                continue
            if record.get("paid_submission_possible") is True and not _pixellab_explicit_http_400_rejection(record):
                created_at = record.get("created_at_utc")
                try:
                    created_month = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y-%m") if isinstance(created_at, str) else ""
                except ValueError:
                    created_month = ""
                if not created_month:
                    # Older durable records predate the explicit timestamp.
                    # Their filesystem creation time is the conservative local
                    # fallback so a monthly rollover cannot forget a request.
                    try:
                        created_month = datetime.fromtimestamp(record_path.stat().st_mtime, timezone.utc).strftime("%Y-%m")
                    except OSError:
                        return {"state": "ERROR", "error": "PIXELLAB_JOB_LEDGER_UNREADABLE"}
                if created_month == month:
                    monthly_paid_requests += 1
            request_records.append(record)

    result_rows: list[dict[str, object]] = []
    for row_index, description_sha256, seed in normalized_rows:
        matches = [record for record in request_records
                   if record.get("description_sha256") == description_sha256
                   and record.get("seed") == seed
                   and record.get("width") == 56 and record.get("height") == 56
                   and record.get("max_colors") == 12]
        if matches:
            # A definite provider-side 400 with no job ID is a failed attempt,
            # not a completed or consumed generation. Permit it in a future
            # user-confirmed run. Any ambiguous or accepted matching attempt
            # keeps the row fail-closed.
            retry_eligible = all(_pixellab_explicit_http_400_rejection(record) for record in matches)
            prior = next((record for record in matches
                          if not _pixellab_explicit_http_400_rejection(record)), matches[-1])
            result_rows.append({
                "row_index": row_index,
                "disposition": "RETRY_ELIGIBLE" if retry_eligible else "ALREADY_ATTEMPTED",
                "state": str(prior.get("state", "UNKNOWN")),
                "paid_submission_possible": prior.get("paid_submission_possible") is True,
            })
        else:
            result_rows.append({"row_index": row_index, "disposition": "NEW"})
    return {
        "state": "READY", "current_month_utc": month,
        "monthly_paid_requests": monthly_paid_requests,
        "monthly_request_limit": 200, "source_sha256": source_sha256,
        "source_prompt_count": len(normalized_rows), "rows": result_rows,
    }
    provider = create_provider("PIXELLAB", engine=model)
    candidate = provider.generate_checked(semantic_request)
    if candidate.status.value != "SUCCESS":
        raise ValueError(candidate.reason or "selected provider did not return an image")
    factory_output = (_repository_root() / "level_factory" / "output").resolve()
    output_root = (factory_output / "semantic-generated").resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    destination = (output_root / f"{candidate.candidate_id}.png").resolve()
    if not _inside_output(destination, factory_output):
        raise ValueError("semantic output path escaped the Factory output directory")
    destination.write_bytes(candidate.image_bytes)
    imported = extensions.batch_import([str(destination)])
    items = imported.get("items", [])
    if not isinstance(items, list) or not items or not isinstance(items[0], Mapping):
        raise ValueError("semantic output was not accepted by canonical artwork import")
    item = items[0]
    source_id = item.get("source_id")
    if not isinstance(source_id, str) or not source_id:
        raise ValueError(str(item.get("reason", item.get("state", "canonical artwork import failed"))))
    return {
        "operation": STUDIO_EXTENSION_OPERATION,
        "state": "IMPORTED",
        "candidate_id": candidate.candidate_id,
        "source_id": source_id,
        "provider_id": candidate.provider_id,
        "provider_version": candidate.provider_version,
        "width": candidate.returned_width,
        "height": candidate.returned_height,
        "content_sha256": candidate.content_sha256,
        "source_path": str(destination),
    }




def _semantic_generate_pixellab_pro_4x4(
    *, prompt: str, style: str, width: int, height: int, max_colors: int,
    seed: str | int, operation_id: object,
) -> dict[str, object]:
    """Persist one explicit 4x4 request, normalize and always slice all 16 frames."""
    import re
    import uuid
    from scrubbots_pixel_factory import studio_extensions as extensions
    from scrubbots_pixel_factory.contracts.palette import PALETTE_DATA_PATH
    from scrubbots_pixel_factory.owner_art_storage import archive_pixellab_export
    from scrubbots_pixel_factory.pixellab_pro_atlas import export_atlas

    resolved_operation_id = str(operation_id or uuid.uuid4().hex)
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", resolved_operation_id):
        raise ValueError("PixelLab Pro 4x4 operation_id is invalid")
    if type(width) is not int or type(height) is not int or not 51 <= width <= 59 or not 51 <= height <= 59:
        raise ValueError("GAME_DIMENSIONS_OUT_OF_RANGE: ScrubBots Pro 4x4 axes must each be 51..59.")
    if type(max_colors) is not int or not 3 <= max_colors <= 12:
        raise ValueError("MAX_COLORS_OUT_OF_RANGE: choose 3..12.")
    if type(prompt) is not str or not prompt.strip() or type(style) is not str:
        raise ValueError("INVALID_DESCRIPTION: Pro 4x4 prompt/style are invalid.")
    if isinstance(seed, bool) or not isinstance(seed, (str, int)):
        raise ValueError("INVALID_SEED: Pro 4x4 seed must be text or integer.")

    description = f"{prompt}. Pixel art style: {style}." if style else prompt
    normalized_description = description.strip()
    if len(normalized_description) > 2000:
        raise ValueError("INVALID_DESCRIPTION: Pro 4x4 description exceeds 2000 characters.")
    normalized_seed = _resolved_pixellab_batch_seed(seed, extensions)
    palette_sha256 = hashlib.sha256(PALETTE_DATA_PATH.read_bytes()).hexdigest()
    request_digest = hashlib.sha256(json.dumps({
        "provider": "PIXELLAB", "model": "PRO_4X4", "adapter_version": "pixellab-pro-4x4-v1",
        "api_version": "v2", "palette_sha256": palette_sha256, "description": normalized_description,
        "width": width, "height": height, "max_colors": max_colors, "seed": normalized_seed,
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    # V02 hashed raw text and the caller's seed representation. Keep that
    # fingerprint for read-only matching so old paid records stay protected.
    legacy_request_digest = hashlib.sha256(json.dumps({
        "provider": "PIXELLAB", "model": "PRO_4X4", "adapter_version": "pixellab-pro-4x4-v1",
        "api_version": "v2", "palette_sha256": palette_sha256, "description": description,
        "width": width, "height": height, "max_colors": max_colors, "seed": seed,
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    job_root = (extensions.extensions_root() / "pixellab-jobs").resolve()
    job_path = (job_root / f"{resolved_operation_id}.json").resolve()
    if not _inside_output(job_path, extensions.extensions_root().resolve()):
        raise ValueError("PixelLab Pro 4x4 job record escaped the Studio output directory")
    if job_path.exists():
        previous = json.loads(job_path.read_text(encoding="utf-8"))
        return {"operation": STUDIO_EXTENSION_OPERATION, "state": "NEEDS_OWNER_REVIEW_IDENTICAL_REQUEST",
                "reason": "This operation ID already has a durable PixelLab record; no request was submitted again.",
                "job_id": previous.get("job_id"), "job_state": previous.get("state"),
                "operation_id": resolved_operation_id}

    claim_path = (job_root / f"{request_digest}.claim.json").resolve()
    if not _inside_output(claim_path, job_root):
        raise ValueError("PixelLab Pro 4x4 request claim escaped its ledger directory")

    def blocked_claim(claim: Mapping[str, object] | None) -> dict[str, object]:
        effective: dict[str, object] = dict(claim or {})
        try:
            paired_operation_id = effective.get("operation_id")
            if isinstance(paired_operation_id, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,80}", paired_operation_id):
                job_record_path = (job_root / f"{paired_operation_id}.json").resolve()
                if _inside_output(job_record_path, job_root):
                    paired = json.loads(job_record_path.read_text(encoding="utf-8"))
                    if isinstance(paired, dict) and paired.get("request_sha256") in {request_digest, legacy_request_digest}:
                        effective.update(paired)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            pass
        prior_id = str(effective.get("operation_id", "")) if effective else ""
        prior_job_id = effective.get("job_id") if effective else None
        prior_state = str(effective.get("state", "UNKNOWN")) if effective else "UNKNOWN"
        post_possible_states = {
            "SUBMITTING", "SUBMISSION_UNKNOWN", "POLLING", "POLL_TIMEOUT", "POLL_NETWORK_ERROR",
            "NORMALIZING", "POST_SUBMISSION_ERROR", "SUCCEEDED", "FAILED_AFTER_POST",
            "SOURCES_IMPORTED_NOT_READY", "SOURCE_IMPORT_FAILED", "FRAMES_REJECTED",
        }
        paid_possible = bool(effective) and (
            effective.get("paid_submission_possible") is True
            or prior_state in post_possible_states
            or isinstance(prior_job_id, str) and bool(prior_job_id)
        )
        if not effective or paid_possible and not prior_job_id:
            state = "NEEDS_OWNER_REVIEW_UNKNOWN_SUBMISSION"
            reason = "A matching claim has an unknown or possibly charged outcome; reconcile PixelLab manually before any new request."
        elif paid_possible:
            state = "NEEDS_OWNER_REVIEW_ACCEPTED_JOB"
            reason = "An identical paid request is already recorded; use explicit GET-only job reconciliation, never submit it again."
        else:
            state = "NEEDS_OWNER_REVIEW_ACTIVE_OR_STALE_CLAIM"
            reason = "An identical request claim already exists; it is not automatically reclaimed or resubmitted."
        return {"operation": STUDIO_EXTENSION_OPERATION, "state": state, "reason": reason,
                "job_id": prior_job_id, "job_state": prior_state,
                "prior_operation_id": prior_id, "operation_id": resolved_operation_id}

    matching_prior_records: list[dict[str, object]] = []
    if job_root.exists():
        for prior_path in sorted(job_root.glob("*.json")):
            if prior_path.name.endswith(".claim.json") or prior_path == job_path:
                continue
            try:
                prior_resolved = prior_path.resolve()
                prior_resolved.relative_to(job_root)
                prior = json.loads(prior_resolved.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
                return blocked_claim(None)
            if isinstance(prior, dict) and {request_digest, legacy_request_digest}.intersection({
                    prior.get("request_sha256"), prior.get("legacy_request_sha256")
            }):
                matching_prior_records.append(prior)

    prior_match_needs_block: dict[str, object] | None = None
    if matching_prior_records:
        # Keep each failed 400 attempt and its claim immutable. A later
        # user-confirmed retry gets a distinct exclusive claim slot; any
        # ambiguous, active, accepted, or completed matching record blocks it.
        if all(_pixellab_explicit_http_400_rejection(record) for record in matching_prior_records):
            retry_number = len(matching_prior_records)
            claim_path = (job_root / f"{request_digest}.retry-{retry_number}.claim.json").resolve()
            if not _inside_output(claim_path, job_root):
                raise ValueError("PixelLab Pro 4x4 retry claim escaped its ledger directory")
        else:
            prior_match_needs_block = matching_prior_records[-1]

    if claim_path.exists():
        try:
            previous_claim = json.loads(claim_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return blocked_claim(None)
        if not isinstance(previous_claim, dict) or previous_claim.get("request_sha256") != request_digest:
            return blocked_claim(None)
        return blocked_claim(previous_claim)
    if prior_match_needs_block is not None:
        return blocked_claim(prior_match_needs_block)

    job_record: dict[str, object] = {
        "schema": "scrubbots-pixellab-pro-4x4-job-v1",
        "operation_id": resolved_operation_id, "request_sha256": request_digest,
        "legacy_request_sha256": legacy_request_digest,
        "provider_id": "PIXELLAB", "provider_model": "PRO_4X4",
        "adapter_version": "pixellab-pro-4x4-mcp-v1", "api_version": "mcp",
        "transport": "PIXELLAB_REMOTE_MCP_HTTP", "mcp_endpoint": "https://api.pixellab.ai/mcp",
        "state": "CLAIMED_BEFORE_POST", "paid_submission_possible": False,
        "width": width, "height": height, "max_colors": max_colors,
        "seed": normalized_seed, "description_sha256": hashlib.sha256(normalized_description.encode("utf-8")).hexdigest(),
        "palette_source": "data/palette/scrubbots_palette_v3.json",
        "palette_sha256": palette_sha256,
        "palette_enforcement": "FULL_V3_TARGET_PALETTE_AND_PER_FRAME_LOCAL_VALIDATION",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    # This status-only check may consult Windows Credential Manager, but it
    # never returns or persists a credential value. Do it before creating the
    # job directory, digest claim, or operation record so first-use setup is
    # retryable after credentials are configured.
    credential_status = extensions.pixellab_secret_status()
    if credential_status.get("configured") is not True:
        credential_state = str(credential_status.get("status", "PIXELLAB_CREDENTIAL_PREFLIGHT_FAILED"))
        if credential_state not in {"PIXELLAB_API_TOKEN_NOT_CONFIGURED", "PIXELLAB_CREDENTIALS_CONFLICT"}:
            credential_state = "PIXELLAB_CREDENTIAL_PREFLIGHT_FAILED"
        return {
            "operation": STUDIO_EXTENSION_OPERATION, "state": credential_state,
            "status": credential_state, "reason": str(credential_status.get("reason", credential_state)),
            "provider_id": "PIXELLAB", "provider_model": "PRO_4X4",
            "operation_id": resolved_operation_id, "paid_submission_possible": False,
            "job_record_created": False, "digest_claim_created": False,
        }

    job_root.mkdir(parents=True, exist_ok=True)
    if not _create_exclusive_json(claim_path, job_record):
        try:
            previous_claim = json.loads(claim_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            previous_claim = None
        return blocked_claim(previous_claim if isinstance(previous_claim, dict) else None)
    if not _create_exclusive_json(job_path, job_record):
        # The digest claim stays in place; ambiguous filesystem state always
        # blocks another billable attempt.
        return blocked_claim(job_record)

    def persist_job() -> None:
        _write_durable_json(job_path, job_record)
        _write_durable_json(claim_path, job_record)

    def submission_started() -> None:
        # The monotonic marker reaches both durable records before the adapter
        # is allowed to invoke its single POST.
        job_record.update({"state": "SUBMITTING", "paid_submission_possible": True})
        persist_job()

    def accepted(job_id: str) -> None:
        job_record.update({"state": "POLLING", "job_id": job_id})
        persist_job()

    def mcp_request_started(count: int) -> None:
        job_record["provider_mcp_request_count"] = count
        persist_job()

    persist_job()
    try:
        generated = extensions.generate_pixellab_pro_4x4_atlas_mcp(
            description=normalized_description, width=width, height=height,
            max_colors=max_colors, seed=normalized_seed, on_submission_started=submission_started,
            on_job_accepted=accepted, on_mcp_request_started=mcp_request_started,
        )
        job_record.update({"state": "NORMALIZING", "job_id": generated.job_id})
        persist_job()
        factory_output = (_repository_root() / "level_factory" / "output").resolve()
        source_root = (factory_output / "semantic-generated" /
                       f"pixellab-pro-4x4-{generated.job_id[:20]}-{resolved_operation_id[:12]}").resolve()
        if not _inside_output(source_root, factory_output):
            raise ValueError("PixelLab Pro 4x4 source directory escaped Factory output")
        manifest = export_atlas(generated.atlas_png, source_root, max_colors=max_colors)
        owner_catalog = archive_pixellab_export(source_root, manifest)
        imported_sources: list[dict[str, object]] = []
        for frame in manifest["frames"]:
            if frame["intake_status"] != "PASS":
                continue
            frame_path = source_root / frame["filename"]
            imported = extensions.batch_import([str(frame_path)])
            items = imported.get("items", [])
            item = items[0] if isinstance(items, list) and items and isinstance(items[0], Mapping) else {}
            imported_sources.append({
                "index": frame["index"], "status": str(item.get("disposition", item.get("state", "IMPORT_REJECTED"))),
                "source_id": item.get("source_id"), "reason": item.get("error", item.get("reason")),
                "sha256": frame["sha256"],
            })
        pass_count = sum(item.get("intake_status") == "PASS" for item in manifest["frames"])
        rejected_count = 16 - pass_count
        imported_source_ids = [item["source_id"] for item in imported_sources if item.get("source_id")]
        final_state = "SOURCES_IMPORTED_NOT_READY" if imported_source_ids else "SOURCE_IMPORT_FAILED" if pass_count else "FRAMES_REJECTED"
        job_record.update({
            "state": final_state,
            "output_directory": str(source_root), "atlas_sha256": manifest["source_atlas_sha256"],
            "frames": manifest["frames"], "imported_sources": imported_sources,
            "owner_catalog_path": owner_catalog["catalog_path"],
            "pass_count": pass_count, "rejected_count": rejected_count,
            "provider_mcp_request_count": generated.mcp_request_count,
            "quality_scope": "SOURCE_ONLY; no solver/WIN replay/difficulty/VOID/QA readiness established",
        })
        persist_job()
        statuses = [
            {"index": frame["index"], "intake_status": frame["intake_status"],
             "reasons": frame["reasons"], "width": frame["width"], "height": frame["height"],
             "import_status": next((item.get("status") for item in imported_sources if item["index"] == frame["index"]), "NOT_IMPORTED"),
             "import_reason": next((item.get("reason") for item in imported_sources if item["index"] == frame["index"]), None),
             "source_id": next((item.get("source_id") for item in imported_sources if item["index"] == frame["index"]), None),
             "path": str(owner_catalog["slices"][int(frame["index"]) - 1]["path"])}
            for frame in manifest["frames"]
        ]
        return {
            "operation": STUDIO_EXTENSION_OPERATION,
            "state": str(job_record["state"]), "operation_id": resolved_operation_id,
            "job_id": generated.job_id, "provider_id": "PIXELLAB", "provider_model": "PRO_4X4",
            "width": width, "height": height, "atlas_width": width * 4, "atlas_height": height * 4,
            "max_colors": max_colors, "pass_count": pass_count, "rejected_count": rejected_count,
            "frame_statuses": statuses, "source_ids": imported_source_ids,
            "atlas_path": str(owner_catalog["atlas_path"]),
            "manifest_path": str(owner_catalog["catalog_path"]),
            "provider_transport": "PIXELLAB_REMOTE_MCP_HTTP",
            "provider_mcp_request_count": generated.mcp_request_count,
        }
    except extensions.PixelLabProviderError as exc:
        state = exc.code if job_record.get("paid_submission_possible") is True else "PRE_SUBMISSION_ERROR"
        job_record.update({"state": state, "job_id": exc.job_id or job_record.get("job_id"),
                           "error_code": exc.code, "error": str(exc),
                           "provider_http_status": exc.http_status,
                           "provider_mcp_request_count": exc.http_request_count
                           if exc.http_request_count is not None else job_record.get("provider_mcp_request_count", 0)})
        if exc.provider_request_id is not None:
            job_record["provider_request_id"] = exc.provider_request_id
        persist_job()
        suffix = f" Provider request ID: {exc.provider_request_id}." if exc.provider_request_id else ""
        raise ValueError(f"{exc.code}: {exc}{suffix}") from None
    except Exception as exc:
        state = "POST_SUBMISSION_ERROR" if job_record.get("paid_submission_possible") is True else "PRE_SUBMISSION_ERROR"
        job_record.update({"state": state, "error": str(exc)[:512]})
        persist_job()
        raise


def _semantic_reconcile_pixellab_pro_4x4(request: Mapping[str, object]) -> dict[str, object]:
    """Read a durable Pro 4x4 job and explicitly reconcile it with GET only."""
    import re
    from scrubbots_pixel_factory import studio_extensions as extensions

    if set(request) - {"operation_id", "network_consent"}:
        raise ValueError("PixelLab reconciliation request contains unsupported fields")
    operation_id = request.get("operation_id")
    if type(operation_id) is not str or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", operation_id):
        raise ValueError("PixelLab reconciliation requires a valid persisted operation ID")
    if request.get("network_consent") is not True:
        raise ValueError("NETWORK_CONSENT_REQUIRED: owner must explicitly approve the status-only network check")
    job_root = (extensions.extensions_root() / "pixellab-jobs").resolve()
    record_path = (job_root / f"{operation_id}.json").resolve()
    if not _inside_output(record_path, job_root) or not record_path.is_file():
        raise ValueError("PIXELLAB_JOB_RECORD_NOT_FOUND: no durable PixelLab job matches this operation ID")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or record.get("provider_id") != "PIXELLAB" or record.get("provider_model") != "PRO_4X4":
        raise ValueError("PIXELLAB_JOB_RECORD_INVALID: refusing to reconcile an unrecognized record")
    if record.get("paid_submission_possible") is not True:
        return {"operation": "pixellab-pro-4x4-reconcile", "state": "NO_PAID_SUBMISSION_RECORDED",
                "operation_id": operation_id, "job_state": record.get("state"),
                "paid_submission_possible": False, "network_requests": 0}
    job_id = record.get("job_id")
    if type(job_id) is not str or not job_id:
        return {"operation": "pixellab-pro-4x4-reconcile", "state": "NEEDS_OWNER_REVIEW_UNKNOWN_SUBMISSION",
                "operation_id": operation_id, "job_state": record.get("state"),
                "paid_submission_possible": True, "network_requests": 0,
                "reason": "No provider job ID was persisted; manually reconcile PixelLab account history before any new generation."}
    if record.get("transport") == "PIXELLAB_REMOTE_MCP_HTTP":
        reconciled = extensions.reconcile_pixellab_pro_4x4_job_mcp(job_id, network_consent=True)
    else:
        # Historical v2 REST jobs remain GET-only reconciled on their original route.
        reconciled = extensions.reconcile_pixellab_pro_4x4_job(job_id, network_consent=True)
    provider_status = reconciled.get("provider_status", {})
    provider_state = str(reconciled.get("state", "UNKNOWN"))
    record["last_reconciliation_state"] = provider_state
    record["last_reconciliation_job_id"] = job_id
    _write_durable_json(record_path, record)
    return {"operation": "pixellab-pro-4x4-reconcile", "state": "RECONCILED",
            "operation_id": operation_id, "job_id": job_id,
            "provider_state": provider_state, "provider_status": provider_status,
            "network_method": "GET", "paid_submission_possible": True}


def _semantic_import_pixellab_pro_4x4(request: Mapping[str, object]) -> dict[str, object]:
    """Normalize a user-selected atlas or coordinate-labelled ZIP, then always slice."""
    import uuid
    from scrubbots_pixel_factory import studio_extensions as extensions
    from scrubbots_pixel_factory.owner_art_storage import archive_pixellab_export
    from scrubbots_pixel_factory.pixellab_pro_atlas import export_atlas, export_photopea_zip

    if set(request) - {"path", "max_colors"}:
        raise ValueError("PixelLab Pro 4x4 import contains unsupported fields")
    source_path = Path(_text(request.get("path"), "path")).resolve()
    max_colors = _exact_int(request.get("max_colors", 12), "max_colors")
    if not 3 <= max_colors <= 12:
        raise ValueError("MAX_COLORS_OUT_OF_RANGE: choose 3..12.")
    if not source_path.is_file() or source_path.suffix.lower() not in {".png", ".zip"}:
        raise ValueError("PIXELLAB_PRO_4X4_SOURCE_INVALID: select one PNG atlas or Photopea ZIP.")
    size_limit = 128 * 1024 * 1024 if source_path.suffix.lower() == ".zip" else 16 * 1024 * 1024
    if source_path.stat().st_size > size_limit:
        raise ValueError("PIXELLAB_PRO_4X4_SOURCE_TOO_LARGE")
    raw = source_path.read_bytes()
    output_root = (_repository_root() / "level_factory" / "output" / "semantic-generated").resolve()
    output_directory = (output_root / f"pixellab-pro-4x4-import-{uuid.uuid4().hex}").resolve()
    if not _inside_output(output_directory, (_repository_root() / "level_factory" / "output").resolve()):
        raise ValueError("PixelLab Pro 4x4 import output escaped Factory output")
    manifest = (
        export_photopea_zip(raw, output_directory, max_colors=max_colors)
        if source_path.suffix.lower() == ".zip"
        else export_atlas(raw, output_directory, max_colors=max_colors)
    )
    owner_catalog = archive_pixellab_export(output_directory, manifest)
    imported_sources: list[dict[str, object]] = []
    for frame in manifest["frames"]:
        if frame["intake_status"] != "PASS":
            continue
        imported = extensions.batch_import([str(output_directory / frame["filename"])])
        items = imported.get("items", [])
        item = items[0] if isinstance(items, list) and items and isinstance(items[0], Mapping) else {}
        imported_sources.append({
            "index": frame["index"], "status": str(item.get("disposition", item.get("state", "IMPORT_REJECTED"))),
            "source_id": item.get("source_id"), "reason": item.get("error", item.get("reason")),
        })
    source_ids = [item["source_id"] for item in imported_sources if item.get("source_id")]
    pass_count = sum(frame["intake_status"] == "PASS" for frame in manifest["frames"])
    return {
        "operation": STUDIO_EXTENSION_OPERATION,
        "state": "SOURCES_IMPORTED_NOT_READY" if source_ids else "SOURCE_IMPORT_FAILED" if pass_count else "FRAMES_REJECTED",
        "source_kind": manifest["source_kind"], "output_directory": str(output_directory),
        "atlas_path": str(owner_catalog["atlas_path"]),
        "manifest_path": str(owner_catalog["catalog_path"]),
        "owner_catalog_path": str(owner_catalog["catalog_path"]),
        "frame_statuses": [
            {"index": frame["index"], "intake_status": frame["intake_status"], "reasons": frame["reasons"],
             "width": frame["width"], "height": frame["height"],
             "import_status": next((item.get("status") for item in imported_sources if item["index"] == frame["index"]), "NOT_IMPORTED"),
             "import_reason": next((item.get("reason") for item in imported_sources if item["index"] == frame["index"]), None),
             "source_id": next((item.get("source_id") for item in imported_sources if item["index"] == frame["index"]), None),
             "path": str(owner_catalog["slices"][int(frame["index"]) - 1]["path"])}
            for frame in manifest["frames"]
        ],
        "source_ids": source_ids, "pass_count": pass_count, "rejected_count": 16 - pass_count,
        "quality_scope": "SOURCE_ONLY; solver/WIN replay/difficulty/VOID/QA remain required for READY",
    }


def _provider_options() -> dict[str, object]:
    """Expose only adapters that are actually executable in this process."""
    from scrubbots_pixel_factory.alpix_batch import discover_alpix
    from scrubbots_pixel_factory.studio_extensions import pixellab_secret_status
    from scrubbots_pixel_factory.semantic.providers.registry import active_factory_studio_provider_ids

    alpix = discover_alpix(project_root=Path(_repository_root()))
    options: list[dict[str, object]] = []
    for provider_id in active_factory_studio_provider_ids():
        if provider_id == "ALPIX (Claude)":
            options.append({"id": provider_id, "available": alpix.get("available") is True,
                "prompt_capable": True, "status": alpix.get("status", "ALPIX_INVALID_CONFIG"),
                "reason": alpix.get("reason", "ALPIX_INVALID_CONFIG: Claude Alpix configuration could not be verified."),
                "plugin_id": alpix.get("plugin_id"), "mcp_servers": alpix.get("mcp_servers")})
        elif provider_id == "PIXELLAB":
            credential = pixellab_secret_status()
            options.append({"id": provider_id, "available": credential.get("configured") is True, "prompt_capable": True,
                "execution_mode": "PRO_4X4", "status": credential.get("status", "PIXELLAB_CREDENTIALS_CONFLICT"),
                "reason": credential.get("reason", "PIXELLAB_CREDENTIALS_CONFLICT: credential state could not be verified.")})
    return {"operation": STUDIO_EXTENSION_OPERATION, "state": "READY", "providers": options}


def _alpix_generate(request: Mapping[str, object]) -> dict[str, object]:
    """Generate exactly one image through the installed Claude Code Alpix tool."""
    from scrubbots_pixel_factory.alpix_batch import generate_alpix_png
    from scrubbots_pixel_factory import studio_extensions as extensions

    if set(request) - {"prompt", "width", "height", "output_path"}:
        raise ValueError("ALPIX request contains unsupported fields")
    output = _alpix_output_path(request.get("output_path"))
    generated = generate_alpix_png(prompt=_text(request.get("prompt"), "prompt"),
        width=_exact_int(request.get("width"), "width"), height=_exact_int(request.get("height"), "height"),
        destination=output, project_root=Path(_repository_root()))
    from scrubbots_pixel_factory.studio_lifecycle import studio_shutdown_requested
    if studio_shutdown_requested():
        return {"operation": "alpix-generate", "state": "CANCELLED",
                "reason": "Factory Studio closed after the provider completed; the generated PNG was preserved."}
    imported = extensions.batch_import([str(output)])
    items = imported.get("items", [])
    item = items[0] if isinstance(items, list) and items else {}
    source_id = item.get("source_id") if isinstance(item, Mapping) else None
    if not isinstance(source_id, str) or not source_id:
        raise ValueError("ALPIX PNG was not accepted by canonical artwork import")
    return {"operation": "alpix-generate", "state": "IMPORTED", "provider_id": "ALPIX_CLAUDE",
            "source_id": source_id, "source_path": str(output), "content_sha256": generated["sha256"],
            "width": generated["width"], "height": generated["height"]}


def _alpix_csv_job(request: Mapping[str, object]) -> dict[str, object]:
    """Open or resume the CSV-SHA job and pass each row through canonical import."""
    from scrubbots_pixel_factory.alpix_batch import generate_alpix_png, run_csv_job
    from scrubbots_pixel_factory import studio_extensions as extensions
    from scrubbots_pixel_factory.owner_art_storage import OwnerArtStorageError, validate_owner_input_csv

    if set(request) - {"csv_path", "default_width", "default_height"}:
        raise ValueError("ALPIX batch request contains unsupported fields")
    try:
        csv_path = validate_owner_input_csv(_text(request.get("csv_path"), "csv_path"), repository_root=_repository_root())
    except (OwnerArtStorageError, OSError, ValueError) as exc:
        raise ValueError("ALPIX_BATCH_CSV_OUTSIDE_CANONICAL_INPUT: select a .csv directly from data/input") from exc
    root = extensions.extensions_root() / "alpix-jobs"
    default_width = _exact_int(request.get("default_width", 32), "default_width")
    default_height = _exact_int(request.get("default_height", 32), "default_height")

    def render(prompt: str, width: int, height: int, destination: Path) -> Mapping[str, object]:
        return generate_alpix_png(prompt=prompt, width=width, height=height, destination=destination,
                                  project_root=Path(_repository_root()))

    def import_png(path: Path) -> Mapping[str, object]:
        result = extensions.batch_import([str(path)])
        items = result.get("items", [])
        item = items[0] if isinstance(items, list) and items else {}
        return item if isinstance(item, Mapping) else {}

    job_result = run_csv_job(csv_path, root, renderer=render,
        importer=import_png, default_size=(default_width, default_height))
    if job_result.state == "INTERRUPTED":
        return {"operation": "alpix-csv-job", **job_result.to_dict()}
    from scrubbots_pixel_factory.owner_art_storage import archive_alpix_png
    rows: list[dict[str, object]] = []
    job_artifact_root = (root / job_result.job_id).resolve()
    for index, row_value in enumerate(job_result.rows):
        from scrubbots_pixel_factory.studio_lifecycle import studio_shutdown_requested
        if studio_shutdown_requested():
            return {"operation": "alpix-csv-job", **job_result.to_dict(), "state": "INTERRUPTED",
                    "rows": rows + [dict(value) for value in job_result.rows[index:]]}
        row = dict(row_value)
        artifact = job_artifact_root / f"row-{index + 1:05d}.png"
        row["artifact_path"] = str(artifact)
        expected_sha = row.get("artifact_sha256")
        if row.get("state") in {"DRAWN", "VALIDATED", "IMPORTED"}:
            if (artifact.is_symlink() or not artifact.is_file()
                    or artifact.resolve().parent != job_artifact_root):
                row["owner_catalog_status"] = "ARTIFACT_MISSING_OR_UNSAFE"
                rows.append(row)
                continue
            raw_png = artifact.read_bytes()
            if not isinstance(expected_sha, str) or hashlib.sha256(raw_png).hexdigest() != expected_sha:
                row["owner_catalog_status"] = "ARTIFACT_SHA_MISMATCH"
            else:
                if row.get("state") == "IMPORTED":
                    source_id = row.get("source_id")
                    expected_source_id = f"owner-upload-{expected_sha}"
                    if source_id != expected_source_id:
                        row["owner_catalog_status"] = "SOURCE_IDENTITY_MISMATCH"
                        rows.append(row)
                        continue
                    try:
                        source = extensions.verify_owner_source(expected_source_id)
                    except Exception:
                        row["owner_catalog_status"] = "SOURCE_IDENTITY_UNVERIFIED"
                        rows.append(row)
                        continue
                    if (source.get("source_sha256") != expected_sha
                            or source.get("source_bytes_sha256") != expected_sha):
                        row["owner_catalog_status"] = "SOURCE_IDENTITY_MISMATCH"
                        rows.append(row)
                        continue
                row["owner_catalog_path"] = str(archive_alpix_png(raw_png, repository_root=_repository_root()))
                row["owner_catalog_status"] = "ARCHIVED"
        rows.append(row)
    return {"operation": "alpix-csv-job", **job_result.to_dict(), "rows": rows}
def _magnific_prepare(request: Mapping[str, object]) -> dict[str, object]:
    """Delegate to the existing Magnific adapter's truthful prepare/import contract."""
    from scrubbots_pixel_factory.semantic.contracts import OutputClass, SemanticGenerationRequest
    from scrubbots_pixel_factory.semantic.providers.registry import create_provider, get_provider_descriptor

    if set(request) - {"prompt", "width", "height", "background_intent"}:
        raise ValueError("Magnific request contains unsupported fields")
    prompt = _text(request.get("prompt"), "prompt")
    width, height = _exact_int(request.get("width"), "width"), _exact_int(request.get("height"), "height")
    descriptor = get_provider_descriptor("MAGNIFIC")
    semantic_request = SemanticGenerationRequest(output_class=OutputClass.ASSET_ART, description=prompt,
        width=width, height=height, no_background=request.get("background_intent", "TRANSPARENT") == "TRANSPARENT",
        provider_id="MAGNIFIC", provider_model="recraft-v4-1",
        provider_config_version=descriptor.config_version)
    provider = create_provider("MAGNIFIC")
    job = provider.prepare_job(semantic_request)
    canonical = job.canonical_dict()
    return {"operation": "magnific-prepare", "state": "PREPARED_FOR_EXTERNAL_EXECUTION",
            "provider_id": "MAGNIFIC", "request": canonical,
            "message": "Magnific job prepared. Import the returned image and result manifest to continue."}


def _alpix_output_path(raw: object) -> Path:
    from scrubbots_pixel_factory.owner_art_storage import ensure_owner_art_layout
    root = ensure_owner_art_layout(_repository_root())["alpix"].resolve()
    if raw is None or not str(raw).strip():
        import uuid
        target = root / f"alpix-{uuid.uuid4().hex}.png"
    else:
        target = Path(_text(raw, "output_path")).resolve()
    if not _inside_output(target, root) or target.suffix.lower() != ".png":
        raise ValueError("ALPIX output must be a PNG inside data/output/Alpix")
    return target


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


def _primary_supply_main(arguments: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="scrubbots-pixel-factory supply-optimize")
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--level-id", default="pixelart_level")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--candidates", type=int, default=300)
    parser.add_argument("--column-count", type=int, choices=(3, 4, 5), default=3)
    parser.add_argument("--verify-top", type=int, default=1)
    parser.add_argument("--screen-budget", type=int, default=3000)
    parser.add_argument("--metric-top", type=int, default=12)
    parser.add_argument("--viability-budget", type=int, default=3000)
    parser.add_argument("--real-max-visited", type=int)
    parser.add_argument("--level-number", type=int, default=1)
    args = parser.parse_args(list(arguments))
    from scrubbots_pixel_factory.supply_pipeline.primary import run_primary_supply_pipeline
    payload = run_primary_supply_pipeline(
        args.image, output=args.output, level_id=args.level_id, seed=args.seed,
        candidates=args.candidates, column_count=args.column_count, verify_top=args.verify_top,
        screen_budget=args.screen_budget, metric_top=args.metric_top,
        viability_budget=args.viability_budget, real_max_visited=args.real_max_visited,
        level_number=args.level_number,
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if payload.get("state") == "READY" else 2


def _primary_supply_verify_main(arguments: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="scrubbots-pixel-factory supply-verify")
    parser.add_argument("--level", required=True)
    parser.add_argument("--plan", required=True)
    args = parser.parse_args(list(arguments))
    from scrubbots_pixel_factory.supply_pipeline.verify import verify_exported_supply
    payload = verify_exported_supply(args.level, args.plan)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if payload.get("state") == "READY" else 2


def _main() -> int:
    # The launcher can live under Release while its Python modules are imported
    # from the canonical checkout. Preserve the active GUI's output location.
    _set_studio_project_root()
    repository_root = _repository_root()
    sys.path.insert(0, str(repository_root / "src"))
    sys.path.insert(0, str(repository_root / "scripts"))
    if len(sys.argv) > 1 and sys.argv[1] == "dashboard-inspect":
        return _dashboard_inspect_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "studio-revalidate-art":
        return _studio_revalidate_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "owner-upload":
        return _owner_upload_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "studio-extension":
        return _studio_extension_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "supply-optimize":
        return _primary_supply_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "supply-verify":
        return _primary_supply_verify_main(sys.argv[2:])
    from scrubbots_pixel_factory.cli.main import main as canonical_main

    return canonical_main()


if __name__ == "__main__":
    raise SystemExit(_main())
