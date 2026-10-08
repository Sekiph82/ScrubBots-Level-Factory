"""Canonical digests that bind exported supply bytes to a READY solver result."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


IDENTITY_SCHEMA = "scrubbots.factory.solver-supply-identity.v1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


class SolverSupplyIdentityError(ValueError):
    """Raised when a solver-passed result cannot bind exact exported supply bytes."""


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def solver_evidence_body(result: Mapping[str, Any], authority: Mapping[str, Any]) -> dict[str, object]:
    metrics = result.get("solver_metrics")
    if not isinstance(metrics, Mapping):
        raise SolverSupplyIdentityError("solver metrics are unavailable")
    official = metrics.get("official_difficulty_v1")
    if not isinstance(official, Mapping) or official.get("ok") is not True:
        raise SolverSupplyIdentityError("official Difficulty V1 evidence is unavailable")
    return {
        "schema": IDENTITY_SCHEMA,
        "version": 1,
        "authority": dict(authority),
        "solver_status": result.get("solver_status"),
        "solution_final": result.get("solution_final"),
        "solution_trace": result.get("solution_trace"),
        "solution_replay": result.get("solution_replay"),
        "game_solver": metrics.get("game_solver"),
        "trace_hash": metrics.get("trace_hash"),
        "official_difficulty_v1": dict(official),
        "color_conservation_verification": result.get("color_conservation_verification"),
    }


def derive_solver_supply_identity(
    level_data_bytes: bytes,
    supply_plan_bytes: bytes,
    result: Mapping[str, Any],
    authority: Mapping[str, Any],
) -> dict[str, object]:
    """Hash the exact solver inputs and the existing canonical PASS result, without rerunning it."""
    if type(level_data_bytes) is not bytes or type(supply_plan_bytes) is not bytes:
        raise SolverSupplyIdentityError("level and supply plan must be exact immutable bytes")
    if not isinstance(result, Mapping) or not isinstance(authority, Mapping):
        raise SolverSupplyIdentityError("solver result and authority must be explicit objects")
    try:
        level = json.loads(level_data_bytes.decode("utf-8"))
        plan = json.loads(supply_plan_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SolverSupplyIdentityError("solver level or supply input is malformed JSON") from exc
    if not isinstance(level, dict) or not isinstance(plan, dict):
        raise SolverSupplyIdentityError("solver level and supply inputs must be JSON objects")
    level_id = level.get("id")
    cells = level.get("cells")
    if not isinstance(cells, list) or any(type(value) is not int for value in cells):
        raise SolverSupplyIdentityError("level cells must be integer palette IDs or VOID -1")
    void_count = cells.count(-1)
    artwork_count = len(cells) - void_count
    if any(value < -1 for value in cells) or (level.get("version") == 1 and void_count) or (level.get("version") == 2 and (void_count == 0 or artwork_count == 0)) or level.get("version") not in (1, 2):
        raise SolverSupplyIdentityError("level V1/V2 VOID encoding is not canonical")
    if (
        not isinstance(level_id, str)
        or plan.get("schema") != "scrubbots.level_supply_plan.v1"
        or type(plan.get("version")) is not int
        or plan.get("version") != 1
        or plan.get("levelId") != level_id
    ):
        raise SolverSupplyIdentityError("level and supply plan identity do not match V1")
    columns = plan.get("columns")
    column_count = plan.get("columnCount")
    preview_depth = plan.get("visiblePreviewDepth")
    max_robots = plan.get("maxRobotsPerBatch")
    if (
        not isinstance(columns, list)
        or type(column_count) is not int
        or len(columns) != column_count
        or type(preview_depth) is not int
        or type(max_robots) is not int
        or max_robots < 1
    ):
        raise SolverSupplyIdentityError("supply columns or configuration are malformed")
    seen_batch_ids: set[str] = set()
    normalized_columns: list[list[dict[str, object]]] = []
    for column in columns:
        if not isinstance(column, list) or not column:
            raise SolverSupplyIdentityError("FIFO supply columns must be non-empty arrays")
        normalized_column: list[dict[str, object]] = []
        for batch in column:
            if not isinstance(batch, Mapping):
                raise SolverSupplyIdentityError("FIFO supply batch must be an object")
            batch_id, cid, robots = batch.get("batchId"), batch.get("cid"), batch.get("robots")
            if (
                not isinstance(batch_id, str)
                or not batch_id
                or batch_id.casefold() in seen_batch_ids
                or not isinstance(cid, str)
                or not cid
                or type(robots) is not int
                or robots < 1
                or robots > max_robots
            ):
                raise SolverSupplyIdentityError("FIFO batch identity, color, or robot count is invalid")
            seen_batch_ids.add(batch_id.casefold())
            normalized_column.append({"batchId": batch_id, "cid": cid, "robots": robots})
        normalized_columns.append(normalized_column)
    git_head = authority.get("git_head")
    if (
        authority.get("repository") != "Sekiph82/Scrubbots"
        or authority.get("branch") != "main"
        or not isinstance(git_head, str)
        or not _GIT_SHA.fullmatch(git_head)
    ):
        raise SolverSupplyIdentityError("canonical ScrubBots main authority identity is unavailable")
    if (
        result.get("solver_status") != "SOLVED"
        or result.get("solution_final") != "WIN"
        or not isinstance(result.get("solution_replay"), Mapping)
        or result["solution_replay"].get("ok") is not True
        or result["solution_replay"].get("solved") is not True
        or result["solution_replay"].get("finalActive") != 0
        or not isinstance(result.get("color_conservation_verification"), Mapping)
        or result["color_conservation_verification"].get("all_ok") is not True
    ):
        raise SolverSupplyIdentityError("canonical solver PASS, replay, or conservation evidence is incomplete")

    level_sha256 = hashlib.sha256(level_data_bytes).hexdigest()
    plan_sha256 = hashlib.sha256(supply_plan_bytes).hexdigest()
    state_body = {
        "schema": f"{IDENTITY_SCHEMA}.initial-state",
        "version": 1,
        "level_id": level_id,
        "level_data_sha256": level_sha256,
        "supply_plan_sha256": plan_sha256,
        "fifo_columns": normalized_columns,
        "column_count": column_count,
        "visible_preview_depth": preview_depth,
        "max_robots_per_batch": max_robots,
        "authority": dict(authority),
    }
    if void_count:
        state_body["artwork_cell_count"] = artwork_count
        state_body["void_cell_count"] = void_count
    evidence_body = solver_evidence_body(result, authority)
    identity = {
        "schema": IDENTITY_SCHEMA,
        "version": 1,
        "level_id": level_id,
        "level_data_sha256": level_sha256,
        "supply_plan_sha256": plan_sha256,
        "fifo_columns": normalized_columns,
        "column_count": column_count,
        "visible_preview_depth": preview_depth,
        "max_robots_per_batch": max_robots,
        "authority": dict(authority),
        "solver_state_sha256": canonical_sha256(state_body),
        "solver_evidence_sha256": canonical_sha256(evidence_body),
    }
    if void_count:
        identity["artwork_cell_count"] = artwork_count
        identity["void_cell_count"] = void_count
    return identity


def current_solver_proof_for_candidate(candidate_id: str) -> tuple[bytes, dict[str, Any]]:
    """Return current accepted READY proof, preferring Release Pool authority when present."""
    from . import release_pool
    from .. import studio_extensions as studio

    if not isinstance(candidate_id, str) or not candidate_id:
        raise SolverSupplyIdentityError("candidate identity is required")
    entry = next(
        (item for item in release_pool.release_entries() if item.get("candidate_id") == candidate_id),
        None,
    )
    if entry is None:
        candidate = next((item for item in studio.list_candidates() if item.get("candidate_id") == candidate_id), None)
        review = studio._latest_review(candidate_id)
        pipeline = studio._latest_ready_pipeline(candidate_id)
        if candidate is None or not isinstance(review, Mapping) or review.get("disposition") != "ACCEPT":
            raise SolverSupplyIdentityError("candidate has no current owner-accepted READY pipeline")
        if not isinstance(pipeline, Mapping):
            raise SolverSupplyIdentityError("candidate has no current READY canonical pipeline")
        run_id = pipeline.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise SolverSupplyIdentityError("current READY pipeline identity is missing")
        path = studio._pipeline_path(run_id)
        try:
            pipeline_bytes = path.read_bytes()
        except OSError as exc:
            raise SolverSupplyIdentityError("current READY pipeline evidence is unavailable") from exc
        pipeline_sha256 = hashlib.sha256(pipeline_bytes).hexdigest()
        if json.loads(pipeline_bytes.decode("utf-8")) != dict(pipeline):
            raise SolverSupplyIdentityError("current READY pipeline evidence changed during proof resolution")
        return pipeline_bytes, {
            "schema": "scrubbots.factory.accepted-ready-proof/v1",
            "candidate_id": candidate_id,
            "review_id": review.get("review_id"),
            "pipeline_run_id": run_id,
            "pipeline_sha256": pipeline_sha256,
            "candidate_artwork_sha256": candidate.get("artwork_sha256"),
        }
    run_id = entry.get("pipeline_run_id")
    if not isinstance(run_id, str) or not run_id:
        raise SolverSupplyIdentityError("Release Pool entry has no current READY pipeline identity")
    path = studio._pipeline_path(run_id)
    try:
        pipeline_bytes = path.read_bytes()
    except OSError as exc:
        raise SolverSupplyIdentityError("current READY pipeline evidence is unavailable") from exc
    if hashlib.sha256(pipeline_bytes).hexdigest() != entry.get("pipeline_sha256"):
        raise SolverSupplyIdentityError("current READY pipeline evidence digest changed")
    return pipeline_bytes, entry


def revalidate_current_solver_proofs(levels: Sequence[Any], proofs: Mapping[str, Any]) -> bool:
    """Callback for the final Content Pipeline build boundary; re-read live Factory authority.

    This function deliberately accepts the Content Pipeline's small proof/level shape
    by protocol, so the Factory does not import the publisher project. It must be passed
    as ``current_authority_check`` to the final solver-proven pack build.
    """
    if not isinstance(levels, Sequence) or not isinstance(proofs, Mapping):
        raise SolverSupplyIdentityError("current solver proof verification inputs are malformed")
    from .. import studio_extensions as studio

    for level in levels:
        level_id = getattr(level, "level_id", None)
        proof = proofs.get(level_id) if isinstance(level_id, str) else None
        if proof is None:
            raise SolverSupplyIdentityError("current solver proof is missing for a packaged level")
        proof_bytes = getattr(proof, "pipeline_bytes", None)
        source = getattr(proof, "release_pool_entry", None)
        if type(proof_bytes) is not bytes or not isinstance(source, Mapping):
            raise SolverSupplyIdentityError("current solver proof snapshot is malformed")
        source = dict(source)
        candidate_id = source.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            raise SolverSupplyIdentityError("current solver proof has no candidate identity")
        current_bytes, current_source = current_solver_proof_for_candidate(candidate_id)
        if current_bytes != proof_bytes or current_source != source:
            raise SolverSupplyIdentityError("current owner review, READY pipeline, or Release Pool proof changed")
        try:
            pipeline = json.loads(current_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SolverSupplyIdentityError("current READY pipeline evidence is malformed") from exc
        primary = pipeline.get("primary") if isinstance(pipeline, Mapping) else None
        files = primary.get("files") if isinstance(primary, Mapping) else None
        if not isinstance(files, Mapping) or pipeline.get("run_id") != source.get("pipeline_run_id"):
            raise SolverSupplyIdentityError("current READY pipeline identity does not match the proof")
        pool_files = source.get("files") if source.get("schema") == "scrubbots-release-pool-entry/v1" else None
        for member_name, pipeline_key, payload_attr in (
            ("level", "level", "level_data"),
            ("supply_plan", "supply_plan", "supply_plan"),
        ):
            payload_container = getattr(level, payload_attr, None)
            expected_bytes = getattr(payload_container, "payload", None)
            source_path = files.get(pipeline_key)
            if type(expected_bytes) is not bytes or not isinstance(source_path, str) or not source_path:
                raise SolverSupplyIdentityError(f"current READY {member_name} source binding is missing")
            try:
                current_file_bytes = Path(source_path).read_bytes()
            except OSError as exc:
                raise SolverSupplyIdentityError(f"current READY {member_name} source file is unavailable") from exc
            if current_file_bytes != expected_bytes:
                raise SolverSupplyIdentityError(f"current READY {member_name} source bytes changed")
            if pool_files is not None:
                record = pool_files.get(member_name)
                if (
                    not isinstance(record, Mapping)
                    or str(record.get("path", "")) != source_path
                    or record.get("sha256") != hashlib.sha256(current_file_bytes).hexdigest()
                ):
                    raise SolverSupplyIdentityError(f"current Release Pool {member_name} binding changed")
        if source.get("schema") == "scrubbots-release-pool-entry/v1":
            entry_digest = source.get("entry_digest")
            body = {key: value for key, value in source.items() if key != "entry_digest"}
            if not isinstance(entry_digest, str) or canonical_sha256(body) != entry_digest:
                raise SolverSupplyIdentityError("current Release Pool entry digest is invalid")
        # Re-read the selected authority last, then verify its owner and READY
        # identities. This catches changes made after the frozen proof was issued.
        final_bytes, final_source = current_solver_proof_for_candidate(candidate_id)
        candidate_exists = any(
            item.get("candidate_id") == candidate_id for item in studio.list_candidates()
        )
        latest_review = studio._latest_review(candidate_id)
        latest_ready = studio._latest_ready_pipeline(candidate_id)
        if (
            final_bytes != proof_bytes
            or final_source != source
            or not candidate_exists
            or not isinstance(latest_review, Mapping)
            or latest_review.get("disposition") != "ACCEPT"
            or latest_review.get("review_id") != source.get("review_id")
            or not isinstance(latest_ready, Mapping)
            or latest_ready.get("run_id") != source.get("pipeline_run_id")
        ):
            raise SolverSupplyIdentityError("current owner review or READY pipeline identity changed")
    return True


__all__ = [
    "IDENTITY_SCHEMA",
    "SolverSupplyIdentityError",
    "canonical_json_bytes",
    "canonical_sha256",
    "current_solver_proof_for_candidate",
    "derive_solver_supply_identity",
    "revalidate_current_solver_proofs",
    "solver_evidence_body",
]
