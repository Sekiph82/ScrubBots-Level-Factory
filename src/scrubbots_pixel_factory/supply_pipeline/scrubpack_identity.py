"""Canonical digests that bind exported supply bytes to a READY solver result."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
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
    evidence_body = solver_evidence_body(result, authority)
    return {
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


__all__ = [
    "IDENTITY_SCHEMA",
    "SolverSupplyIdentityError",
    "canonical_json_bytes",
    "canonical_sha256",
    "current_solver_proof_for_candidate",
    "derive_solver_supply_identity",
    "solver_evidence_body",
]
