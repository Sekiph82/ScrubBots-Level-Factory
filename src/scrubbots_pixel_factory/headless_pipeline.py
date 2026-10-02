"""Headless execution of producer jobs through the canonical Studio pipeline.

The producer manifest is a read-only list of references to already imported
OWNER_UPLOAD records.  This module stores only job progress and references;
source, candidate, supply, QA, and review truth remain in their canonical
stores and are consumed through :mod:`studio_extensions`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from . import studio_extensions as studio


JOB_SCHEMA = "scrubbots-producer-pipeline-job"
JOB_VERSION = 1
EVENT_SCHEMA = "scrubbots-headless-pipeline-event"
EVENT_VERSION = 1
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_JOB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SOURCE_ID = re.compile(r"^owner-upload-([0-9a-f]{64})$")
STAGES = ("IMPORT", "NORMALIZE", "VALIDATE", "CANDIDATE", "ZIP_SUPPLY_SOLVE_DIFFICULTY", "QA", "REVIEW")


class HeadlessPipelineError(ValueError):
    """A producer job is malformed or its canonical evidence is inconsistent."""


class PipelineInterruption(BaseException):
    """Test-only interruption raised after a durable stage checkpoint."""


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _job_root() -> Path:
    return studio.extensions_root() / "pipelines" / "jobs"


def _event_dir(job_key: str) -> Path:
    return _job_root() / job_key / "events"


def _json_file(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HeadlessPipelineError(f"{label} is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise HeadlessPipelineError(f"{label} must contain a JSON object")
    return value


def _exact_int(value: object, label: str) -> int:
    if type(value) is not int or not 20 <= value <= 59:
        raise HeadlessPipelineError(f"{label} must be an integer from 20 through 59")
    return value


def _normalize_source(value: object, index: int) -> dict[str, Any]:
    label = f"sources[{index}]"
    if not isinstance(value, Mapping):
        raise HeadlessPipelineError(f"{label} must be an object")
    allowed = {
        "source_id", "source_sha256", "sha256", "requested_width", "requested_height",
        "requested_size", "background_intent", "csv_row_id",
    }
    if set(value) - allowed:
        raise HeadlessPipelineError(f"{label} contains unsupported fields")
    source_id = value.get("source_id")
    digest = value.get("source_sha256", value.get("sha256"))
    if "source_sha256" in value and "sha256" in value:
        raise HeadlessPipelineError(f"{label} must not specify both source_sha256 and sha256")
    match = _SOURCE_ID.fullmatch(source_id) if type(source_id) is str else None
    if match is None and digest is None:
        raise HeadlessPipelineError(f"{label} requires a canonical source_id or source SHA-256")
    if digest is None:
        digest = match.group(1) if match else None
    if type(digest) is not str or not _SHA256.fullmatch(digest):
        raise HeadlessPipelineError(f"{label}.source_sha256 must be lowercase SHA-256")
    if source_id is None:
        source_id = f"owner-upload-{digest}"
        match = _SOURCE_ID.fullmatch(source_id)
    if match is None or match.group(1) != digest:
        raise HeadlessPipelineError(f"{label} source_id and SHA-256 do not identify the same OWNER_UPLOAD")

    if "requested_size" in value:
        if "requested_width" in value or "requested_height" in value:
            raise HeadlessPipelineError(f"{label} must use requested_size or requested_width/requested_height")
        size = value["requested_size"]
        if not isinstance(size, Mapping) or set(size) != {"width", "height"}:
            raise HeadlessPipelineError(f"{label}.requested_size must contain exactly width and height")
        width, height = size["width"], size["height"]
    else:
        width, height = value.get("requested_width"), value.get("requested_height")
    width = _exact_int(width, f"{label}.requested_width")
    height = _exact_int(height, f"{label}.requested_height")
    background = value.get("background_intent")
    if background != "FULL":
        raise HeadlessPipelineError(f"{label}.background_intent must be FULL")
    row_id = value.get("csv_row_id")
    if type(row_id) is not str or not row_id.strip() or len(row_id) > 128 or "\x00" in row_id:
        raise HeadlessPipelineError(f"{label}.csv_row_id must be a non-empty string of at most 128 characters")
    return {
        "source_id": source_id,
        "source_sha256": digest,
        "requested_width": width,
        "requested_height": height,
        "background_intent": background,
        "csv_row_id": row_id,
    }


def load_job(path: str | Path) -> dict[str, Any]:
    """Read and strictly normalize a producer job without modifying it."""

    job_path = Path(path)
    raw = _json_file(job_path, "producer job manifest")
    allowed = {"schema", "schema_version", "job_id", "sources"}
    if set(raw) - allowed or raw.get("schema") != JOB_SCHEMA or raw.get("schema_version") != JOB_VERSION:
        raise HeadlessPipelineError(f"producer job schema must be {JOB_SCHEMA} version {JOB_VERSION}")
    supplied_job_id = raw.get("job_id")
    if supplied_job_id is not None and (type(supplied_job_id) is not str or not _JOB_ID.fullmatch(supplied_job_id)):
        raise HeadlessPipelineError("job_id is malformed")
    rows = raw.get("sources")
    if type(rows) is not list or not rows:
        raise HeadlessPipelineError("sources must be a non-empty array")
    sources = [_normalize_source(item, index) for index, item in enumerate(rows)]
    source_ids = [item["source_id"] for item in sources]
    row_ids = [item["csv_row_id"] for item in sources]
    if len(set(source_ids)) != len(source_ids):
        raise HeadlessPipelineError("a producer job cannot repeat an OWNER_UPLOAD source identity")
    if len(set(row_ids)) != len(row_ids):
        raise HeadlessPipelineError("a producer job cannot repeat a CSV row identity")
    canonical = {"schema": JOB_SCHEMA, "schema_version": JOB_VERSION, "sources": sources}
    content_digest = _sha256(_canonical_bytes(canonical))
    job_id = supplied_job_id or f"job-{content_digest[:24]}"
    manifest_digest = _sha256(_canonical_bytes({"job_id": job_id, **canonical}))
    return {
        "job_id": job_id,
        "manifest_digest": manifest_digest,
        "manifest_path": str(job_path.resolve()),
        "manifest_bytes_sha256": _sha256(job_path.read_bytes()),
        "sources": sources,
    }


def _read_events(job: Mapping[str, Any]) -> list[dict[str, Any]]:
    directory = _event_dir(str(job["manifest_digest"]))
    if not directory.exists():
        return []
    events: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        event = _json_file(path, "headless job event")
        required = {"schema", "version", "job_id", "manifest_digest", "sequence", "source_id", "csv_row_id", "stage", "disposition", "canonical_references", "identities", "reason", "recorded_at"}
        if set(event) != required or event.get("schema") != EVENT_SCHEMA or event.get("version") != EVENT_VERSION:
            raise HeadlessPipelineError(f"job event schema is invalid: {path.name}")
        if event.get("job_id") != job["job_id"] or event.get("manifest_digest") != job["manifest_digest"]:
            raise HeadlessPipelineError("job event belongs to a different immutable manifest")
        if type(event.get("sequence")) is not int or event["sequence"] != len(events) + 1:
            raise HeadlessPipelineError("job event sequence is not contiguous")
        if not isinstance(event.get("canonical_references"), list) or not isinstance(event.get("identities"), Mapping):
            raise HeadlessPipelineError("job event references are malformed")
        events.append(event)
    return events


def _emit(event: Mapping[str, Any]) -> None:
    print(json.dumps(dict(event), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _append_event(
    job: Mapping[str, Any],
    events: list[dict[str, Any]],
    *,
    source: Mapping[str, Any] | None,
    stage: str,
    disposition: str,
    references: list[str] | None = None,
    identities: Mapping[str, Any] | None = None,
    reason: str = "",
    after_checkpoint: Callable[[str, str], None] | None = None,
) -> dict[str, Any]:
    identity_data = dict(identities or {})
    if source is not None:
        identity_data.update({
            "source_sha256": source["source_sha256"],
            "requested_width": source["requested_width"],
            "requested_height": source["requested_height"],
            "background_intent": source["background_intent"],
        })
    event = {
        "schema": EVENT_SCHEMA,
        "version": EVENT_VERSION,
        "job_id": job["job_id"],
        "manifest_digest": job["manifest_digest"],
        "sequence": len(events) + 1,
        "source_id": source.get("source_id") if source else None,
        "csv_row_id": source.get("csv_row_id") if source else None,
        "stage": stage,
        "disposition": disposition,
        "canonical_references": sorted(set(references or [])),
        "identities": identity_data,
        "reason": str(reason)[:512],
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    directory = _event_dir(str(job["manifest_digest"]))
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{event['sequence']:08d}.json"
    try:
        studio._write_json(path, event, immutable=True)
    except studio.StudioExtensionError as exc:
        raise HeadlessPipelineError("concurrent pipeline run attempted to reuse an event sequence") from exc
    events.append(event)
    _emit({"event": "progress", **event})
    if after_checkpoint is not None and source is not None:
        after_checkpoint(str(source["csv_row_id"]), stage)
    return event


def _latest_by_stage(events: list[dict[str, Any]], source_id: str) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for event in events:
        if event.get("source_id") == source_id and event.get("stage") in {*STAGES, "TERMINAL"}:
            latest[str(event["stage"])] = event
    return latest


def _verify_source(source: Mapping[str, Any]) -> dict[str, Any]:
    verified = studio.verify_owner_source(str(source["source_id"]))
    if verified.get("source_sha256") != source["source_sha256"]:
        raise HeadlessPipelineError("manifest SHA-256 does not match canonical OWNER_UPLOAD bytes")
    return verified


class SourceRejected(HeadlessPipelineError):
    """Canonical source is validly identified but cannot satisfy the job."""


def _source_terminal(latest: Mapping[str, Mapping[str, Any]]) -> str | None:
    terminal = latest.get("TERMINAL")
    return str(terminal.get("disposition")) if terminal else None


def _append_stage_start(job: Mapping[str, Any], events: list[dict[str, Any]], source: Mapping[str, Any], stage: str, after_checkpoint) -> None:
    latest = _latest_by_stage(events, str(source["source_id"])).get(stage)
    if latest is not None and latest["disposition"] not in {"RUNNING"}:
        return
    _append_event(job, events, source=source, stage=stage, disposition="RUNNING", identities={"source_sha256": source["source_sha256"]}, after_checkpoint=after_checkpoint)


def _completed_stage(events: list[dict[str, Any]], source_id: str, stage: str) -> dict[str, Any] | None:
    value = _latest_by_stage(events, source_id).get(stage)
    return value if value is not None and value.get("disposition") != "RUNNING" else None


def _load_validation_checkpoint(event: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    references = event.get("canonical_references", [])
    if len(references) != 1:
        raise HeadlessPipelineError("validation checkpoint must reference one canonical report")
    path = (studio._repository_root() / str(references[0])).resolve()
    root = studio.extensions_root().resolve()
    if root not in path.parents:
        raise HeadlessPipelineError("validation checkpoint escaped the Studio evidence root")
    report = studio._read_json(path)
    if report.get("source_id") != source["source_id"] or report.get("source_sha256") != source["source_sha256"]:
        raise HeadlessPipelineError("validation checkpoint no longer matches its canonical source")
    if _sha256(_canonical_bytes(report)) != event.get("identities", {}).get("validation_digest"):
        raise HeadlessPipelineError("validation report changed after its job checkpoint")
    if report.get("exact_logical_source") is not True or report.get("structural", {}).get("disposition") != "PASS":
        raise HeadlessPipelineError("successful validation checkpoint no longer has canonical PASS evidence")
    return {**report, "evidence_path": str(references[0])}


def _pipeline_for_job(job: Mapping[str, Any], source: Mapping[str, Any], candidate_id: str) -> dict[str, Any] | None:
    """Recover a canonical Studio run written just before a job checkpoint."""

    directory = studio.extensions_root() / "pipelines"
    matches: list[dict[str, Any]] = []
    for path in directory.glob("pipeline-*.json") if directory.exists() else ():
        try:
            value = studio._read_json(path)
        except studio.StudioExtensionError:
            continue
        request = value.get("request", {})
        if (
            value.get("schema") == studio.PIPELINE_SCHEMA
            and value.get("candidate_id") == candidate_id
            and isinstance(request, Mapping)
            and request.get("headless_job_id") == job["job_id"]
            and request.get("headless_manifest_digest") == job["manifest_digest"]
            and request.get("headless_csv_row_id") == source["csv_row_id"]
            and request.get("source_id") == source["source_id"]
        ):
            matches.append(value)
    return max(matches, key=lambda item: str(item.get("created_at", ""))) if matches else None


def _verify_pipeline_event(event: Mapping[str, Any]) -> dict[str, Any]:
    references = event.get("canonical_references", [])
    if len(references) != 1:
        raise HeadlessPipelineError("canonical pipeline event must reference exactly one pipeline record")
    path = (studio._repository_root() / str(references[0])).resolve()
    root = studio.extensions_root().resolve()
    if root not in path.parents:
        raise HeadlessPipelineError("canonical pipeline event escaped the Studio evidence root")
    payload = studio._read_json(path)
    digest = _sha256(path.read_bytes())
    if event.get("identities", {}).get("pipeline_sha256") != digest:
        raise HeadlessPipelineError("canonical pipeline record changed after its job checkpoint")
    if payload.get("schema") != studio.PIPELINE_SCHEMA or payload.get("run_id") != event.get("identities", {}).get("pipeline_run_id"):
        raise HeadlessPipelineError("canonical pipeline reference is stale or malformed")
    return payload


def _candidate_in_review_queue(candidate_id: str) -> bool:
    projection = studio.candidate_inbox()
    for item in projection.get("candidates", []):
        if item.get("candidate_id") == candidate_id:
            review = item.get("owner_review", {})
            return review.get("disposition") == "NEEDS_REVIEW"
    return False


def _terminal_event(job, events, source, disposition, reason, **kwargs):
    return _append_event(job, events, source=source, stage="TERMINAL", disposition=disposition, reason=reason, **kwargs)


def _process_source(
    job: Mapping[str, Any],
    events: list[dict[str, Any]],
    source: Mapping[str, Any],
    *,
    after_checkpoint: Callable[[str, str], None] | None = None,
) -> None:
    source_id = str(source["source_id"])
    latest = _latest_by_stage(events, source_id)
    if _source_terminal(latest) is not None:
        return

    try:
        # Always revalidate the canonical source before trusting old job references.
        verified = _verify_source(source)
    except SourceRejected as exc:
        _terminal_event(job, events, source, "REJECTED", str(exc), after_checkpoint=after_checkpoint)
        return
    except Exception as exc:
        if _completed_stage(events, source_id, "IMPORT") is None:
            _append_event(job, events, source=source, stage="IMPORT", disposition="FAIL", identities={"source_id": source_id, "expected_source_sha256": source["source_sha256"]}, reason=str(exc), after_checkpoint=after_checkpoint)
        for stage in ("NORMALIZE", "VALIDATE", "CANDIDATE", "ZIP_SUPPLY_SOLVE_DIFFICULTY", "QA", "REVIEW"):
            if _completed_stage(events, source_id, stage) is None:
                _append_event(job, events, source=source, stage=stage, disposition="NOT_AVAILABLE", identities={"source_sha256": source["source_sha256"]}, reason="Stopped because the canonical OWNER_UPLOAD source could not be verified.", after_checkpoint=after_checkpoint)
        _terminal_event(job, events, source, "FAILED", f"IMPORT: {exc}", after_checkpoint=after_checkpoint)
        return

    if _completed_stage(events, source_id, "IMPORT") is None:
        _append_stage_start(job, events, source, "IMPORT", after_checkpoint)
        _append_event(job, events, source=source, stage="IMPORT", disposition="PASS", references=[verified["record_path"], verified["source_path"]], identities={"source_id": source_id, "source_sha256": verified["source_sha256"]}, reason="Read-only verification of an already imported immutable OWNER_UPLOAD record.", after_checkpoint=after_checkpoint)
    if _completed_stage(events, source_id, "NORMALIZE") is None:
        _append_stage_start(job, events, source, "NORMALIZE", after_checkpoint)
        actual_size = (int(verified["original_width"]), int(verified["original_height"]))
        requested_size = (int(source["requested_width"]), int(source["requested_height"]))
        if actual_size != requested_size:
            reason = "REQUESTED_DIMENSIONS_DO_NOT_MATCH_SOURCE; logical source art is never resized or resampled"
            _append_event(job, events, source=source, stage="NORMALIZE", disposition="FAIL", references=[verified["source_path"]], identities={"source_sha256": verified["source_sha256"]}, reason=reason, after_checkpoint=after_checkpoint)
            for stage in ("VALIDATE", "CANDIDATE", "ZIP_SUPPLY_SOLVE_DIFFICULTY", "QA", "REVIEW"):
                if _completed_stage(events, source_id, stage) is None:
                    _append_event(job, events, source=source, stage=stage, disposition="NOT_AVAILABLE", identities={"source_sha256": verified["source_sha256"]}, reason="Stopped because requested dimensions would require source-art resizing.", after_checkpoint=after_checkpoint)
            _terminal_event(job, events, source, "REJECTED", reason, after_checkpoint=after_checkpoint)
            return
        _append_event(job, events, source=source, stage="NORMALIZE", disposition="NOT_APPLICABLE", references=[verified["source_path"]], identities={"source_sha256": verified["source_sha256"]}, reason="Exact logical source cells are consumed as-is; source-art resizing/resampling is forbidden.", after_checkpoint=after_checkpoint)

    validation: dict[str, Any] | None = None
    validation_event = _completed_stage(events, source_id, "VALIDATE")
    if validation_event is None:
        _append_stage_start(job, events, source, "VALIDATE", after_checkpoint)
        validation = studio.validate_owner_source(source_id)
        valid = validation.get("exact_logical_source") is True and validation.get("structural", {}).get("disposition") == "PASS"
        reason = "Canonical OWNER_UPLOAD palette, alpha, dimensions, logical-cell, and structural checks passed." if valid else str(validation.get("structural", {}).get("reason") or ",".join(validation.get("structural", {}).get("rejection_codes", [])) or "Canonical OWNER_UPLOAD validation did not produce exact logical cells.")
        validation_event = _append_event(
            job, events, source=source, stage="VALIDATE", disposition="PASS" if valid else "FAIL",
            references=[str(validation.get("evidence_path", verified["record_path"]))],
            identities={"source_sha256": verified["source_sha256"], "validation_digest": _sha256(_canonical_bytes({key: value for key, value in validation.items() if key != "evidence_path"}))},
            reason=reason, after_checkpoint=after_checkpoint,
        )
    if validation_event["disposition"] != "PASS":
        for stage in ("CANDIDATE", "ZIP_SUPPLY_SOLVE_DIFFICULTY", "QA", "REVIEW"):
            if _completed_stage(events, source_id, stage) is None:
                _append_event(job, events, source=source, stage=stage, disposition="NOT_AVAILABLE", identities={"source_sha256": verified["source_sha256"]}, reason="Stopped after canonical source validation failed.", after_checkpoint=after_checkpoint)
        _terminal_event(job, events, source, "REJECTED", str(validation_event["reason"]), after_checkpoint=after_checkpoint)
        return

    candidate_event = _completed_stage(events, source_id, "CANDIDATE")
    candidate_id = str(candidate_event.get("identities", {}).get("candidate_id", "")) if candidate_event else ""
    if candidate_event is None:
        _append_stage_start(job, events, source, "CANDIDATE", after_checkpoint)
        if validation is None:
            validation = _load_validation_checkpoint(validation_event, source)
        _record_path, source_png = studio._source_record_paths(source_id)
        candidate_id, bundle_path = studio._derive_owner_candidate(source_id, validation, source_png)
        bundle = studio.read_bundle(bundle_path)
        candidate_hash = hashlib.sha256(bundle.artwork_png).hexdigest()
        candidate_event = _append_event(
            job, events, source=source, stage="CANDIDATE", disposition="PASS",
            references=[studio._relative(bundle_path), studio._relative(bundle_path / "artwork.png")],
            identities={"candidate_id": candidate_id, "artwork_sha256": candidate_hash, "grid_hash": bundle.artwork.grid_hash, "source_sha256": verified["source_sha256"]},
            reason="Deterministic canonical OWNER_UPLOAD derivation created/reused the same candidate identity as Factory Studio.", after_checkpoint=after_checkpoint,
        )
    else:
        candidate_id = str(candidate_event.get("identities", {}).get("candidate_id", ""))
        if not candidate_id:
            raise HeadlessPipelineError("durable candidate checkpoint has no candidate identity")
        candidate = next((item for item in studio.list_candidates() if item["candidate_id"] == candidate_id), None)
        lineage = candidate.get("source_lineage") if candidate is not None else None
        if candidate is None or not isinstance(lineage, Mapping) or lineage.get("source_sha256") != verified["source_sha256"]:
            raise HeadlessPipelineError("durable candidate reference no longer matches the verified OWNER_UPLOAD source")

    pipeline_event = _completed_stage(events, source_id, "ZIP_SUPPLY_SOLVE_DIFFICULTY")
    pipeline: dict[str, Any] | None = None
    if pipeline_event is not None:
        pipeline = _verify_pipeline_event(pipeline_event)
    else:
        _append_stage_start(job, events, source, "ZIP_SUPPLY_SOLVE_DIFFICULTY", after_checkpoint)
        pipeline = _pipeline_for_job(job, source, candidate_id)
        if pipeline is None:
            candidate = next((item for item in studio.list_candidates() if item["candidate_id"] == candidate_id), None)
            if candidate is None:
                raise HeadlessPipelineError("canonical candidate disappeared before ZIP processing")
            pipeline_request = {
                "source_id": source_id,
                "source_lineage": studio.read_bundle((studio._repository_root() / candidate["source_path"]).resolve()).metadata.get("generator_metadata", {}),
                "headless_job_id": job["job_id"],
                "headless_manifest_digest": job["manifest_digest"],
                "headless_csv_row_id": source["csv_row_id"],
                "producer_request": {
                    "csv_row_id": source["csv_row_id"],
                    "requested_size": {"width": source["requested_width"], "height": source["requested_height"]},
                    "background_intent": source["background_intent"],
                },
            }
            # This is the same candidate-bound canonical pipeline route used by Studio.
            pipeline = studio.run_pipeline(candidate_id=candidate_id, request=pipeline_request)
        pipeline_path = studio._pipeline_path(str(pipeline.get("run_id", "")))
        pipeline_bytes = pipeline_path.read_bytes()
        pipeline_relative = studio._relative(pipeline_path)
        zip_stage = next((item for item in pipeline.get("stages", []) if item.get("stage") == "SOLVE"), {})
        replay_stage = next((item for item in pipeline.get("stages", []) if item.get("stage") == "REPLAY"), {})
        difficulty_stage = next((item for item in pipeline.get("stages", []) if item.get("stage") == "DIFFICULTY"), {})
        zip_ok = (
            pipeline.get("disposition") == "READY"
            and zip_stage.get("disposition") == "PASS"
            and replay_stage.get("disposition") == "PASS"
            and difficulty_stage.get("disposition") == "PASS"
        )
        failed_pipeline_stage = next((item for item in (zip_stage, replay_stage, difficulty_stage) if item.get("disposition") != "PASS"), {})
        pipeline_event = _append_event(
            job, events, source=source, stage="ZIP_SUPPLY_SOLVE_DIFFICULTY", disposition="PASS" if zip_ok else "UNAVAILABLE",
            references=[pipeline_relative], identities={"pipeline_run_id": pipeline.get("run_id"), "pipeline_sha256": _sha256(pipeline_bytes), "candidate_id": candidate_id},
            reason="Canonical Factory Studio ZIP supply, ScrubBots solve/replay, and Difficulty V1 route completed." if zip_ok else str(failed_pipeline_stage.get("reason") or pipeline.get("disposition", "Canonical ZIP pipeline did not become READY.")),
            after_checkpoint=after_checkpoint,
        )

    stages = pipeline.get("stages", [])
    qa_stage = next((item for item in stages if item.get("stage") == "QA"), {})
    qa_event = _completed_stage(events, source_id, "QA")
    if qa_event is None:
        qa_ok = qa_stage.get("disposition") == "PASS" and pipeline.get("disposition") == "READY"
        qa_event = _append_event(
            job, events, source=source, stage="QA", disposition="PASS" if qa_ok else "NOT_AVAILABLE",
            references=[str(qa_stage.get("evidence_reference"))] if qa_stage.get("evidence_reference") else [],
            identities={"pipeline_run_id": pipeline.get("run_id"), "candidate_id": candidate_id},
            reason=str(qa_stage.get("reason") or "Canonical QA evidence is unavailable."), after_checkpoint=after_checkpoint,
        )

    review_event = _completed_stage(events, source_id, "REVIEW")
    if review_event is None:
        queued = _candidate_in_review_queue(candidate_id) if qa_event["disposition"] == "PASS" else False
        review_event = _append_event(
            job, events, source=source, stage="REVIEW", disposition="READY_FOR_OWNER_REVIEW" if queued else "NOT_AVAILABLE",
            references=[str(item) for item in [candidate_event.get("canonical_references", [None])[0], pipeline_event.get("canonical_references", [None])[0]] if item],
            identities={"candidate_id": candidate_id, "owner_review": "NEEDS_REVIEW" if queued else "NOT AVAILABLE"},
            reason="Candidate is visible in Studio's owner Review Queue; no owner decision or publication was created." if queued else "Canonical candidate is not ready in the owner Review Queue.",
            after_checkpoint=after_checkpoint,
        )
    terminal = "READY" if pipeline.get("disposition") == "READY" and qa_event["disposition"] == "PASS" and review_event["disposition"] == "READY_FOR_OWNER_REVIEW" else "FAILED"
    reason = "" if terminal == "READY" else str(qa_event.get("reason") or pipeline.get("disposition") or "Canonical pipeline did not reach Review Queue readiness.")
    _terminal_event(job, events, source, terminal, reason, identities={"candidate_id": candidate_id, "pipeline_run_id": pipeline.get("run_id")}, after_checkpoint=after_checkpoint)


def _summary(job: Mapping[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for source in job["sources"]:
        latest = _latest_by_stage(events, source["source_id"])
        terminal = latest.get("TERMINAL")
        results.append({
            "source_id": source["source_id"],
            "csv_row_id": source["csv_row_id"],
            "disposition": terminal["disposition"] if terminal else "PENDING",
            "reason": terminal["reason"] if terminal else "",
            "completed_stages": [stage for stage in STAGES if stage in latest and latest[stage]["disposition"] not in {"RUNNING", "NOT_AVAILABLE"}],
        })
    counts = {name: sum(item["disposition"] == name for item in results) for name in ("READY", "REJECTED", "FAILED", "PENDING")}
    complete = counts["PENDING"] == 0
    return {"schema": "scrubbots-headless-pipeline-summary", "version": 1, "job_id": job["job_id"], "manifest_digest": job["manifest_digest"], "state": "COMPLETE" if complete else "IN_PROGRESS", **counts, "sources": results}


def run_job(path: str | Path, *, after_checkpoint: Callable[[str, str], None] | None = None) -> dict[str, Any]:
    job = load_job(path)
    events = _read_events(job)
    if not events:
        _append_event(job, events, source=None, stage="JOB", disposition="STARTED", identities={"source_count": len(job["sources"])}, reason="Read-only producer manifest accepted; canonical source processing is sequential with concurrency 1.")
    for source in job["sources"]:
        if _source_terminal(_latest_by_stage(events, source["source_id"])) is None:
            try:
                _process_source(job, events, source, after_checkpoint=after_checkpoint)
            except PipelineInterruption:
                raise
            except Exception as exc:
                latest = _latest_by_stage(events, source["source_id"])
                if _source_terminal(latest) is None:
                    _terminal_event(job, events, source, "FAILED", f"{type(exc).__name__}: {exc}", after_checkpoint=after_checkpoint)
    summary = _summary(job, events)
    # Detect accidental/external producer-manifest mutation; the CLI itself only reads it.
    if _sha256(Path(job["manifest_path"]).read_bytes()) != job["manifest_bytes_sha256"]:
        raise HeadlessPipelineError("producer job manifest changed during processing")
    if summary["state"] == "COMPLETE" and not any(item.get("stage") == "JOB_TERMINAL" for item in events):
        _append_event(job, events, source=None, stage="JOB_TERMINAL", disposition="COMPLETE", identities={key: summary[key] for key in ("READY", "REJECTED", "FAILED")}, reason="All producer rows reached an explicit terminal disposition.")
    _emit({"event": "summary", **summary})
    return summary


def status_job(path: str | Path) -> dict[str, Any]:
    """Read job progress and references without executing canonical work."""

    job = load_job(path)
    summary = _summary(job, _read_events(job))
    _emit({"event": "status", **summary})
    return summary


__all__ = ["EVENT_SCHEMA", "HeadlessPipelineError", "JOB_SCHEMA", "PipelineInterruption", "STAGES", "load_job", "run_job", "status_job"]
