"""Content-addressed binding from packaged supply bytes to current READY evidence."""

from __future__ import annotations

import hashlib
import io
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable
from zipfile import ZipFile

from .scrubpack_builder import (
    ScrubpackBuildError,
    ScrubpackBuildResult,
    ScrubpackLevelInput,
    build_scrubpack,
    verify_scrubpack_build,
)
from .scrubpack_spec import PACK_MANIFEST_PATH


SOLVER_IDENTITY_SCHEMA = "scrubbots.factory.solver-supply-identity.v1"
SOLVER_IDENTITY_ARTIFACT_SCHEMA = "scrubbots.scrubpack.solver-supply-identity-artifact.v1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


class ScrubpackSolverIdentityError(ScrubpackBuildError):
    """Raised when current Factory solver evidence does not bind the exact pack inputs."""


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_digest(value: object) -> str:
    return _sha256(_canonical_bytes(value))


@dataclass(frozen=True, slots=True)
class ScrubpackSolverProof:
    """Exact pipeline bytes plus one entry returned by the live Release Pool reader."""

    pipeline_bytes: bytes
    release_pool_entry: Mapping[str, object]

    def __post_init__(self) -> None:
        if type(self.pipeline_bytes) is not bytes or not isinstance(self.release_pool_entry, Mapping):
            raise ScrubpackSolverIdentityError("solver proof must contain immutable pipeline bytes and a Release Pool entry")
        object.__setattr__(self, "release_pool_entry", MappingProxyType(dict(self.release_pool_entry)))


def _solver_evidence_body(result: Mapping[str, Any], authority: Mapping[str, Any]) -> dict[str, object]:
    metrics = result.get("solver_metrics")
    if not isinstance(metrics, Mapping):
        raise ScrubpackSolverIdentityError("canonical solver metrics are missing")
    official = metrics.get("official_difficulty_v1")
    if not isinstance(official, Mapping):
        raise ScrubpackSolverIdentityError("official Difficulty V1 result is missing")
    return {
        "schema": SOLVER_IDENTITY_SCHEMA,
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


def _proof_for_level(
    level: ScrubpackLevelInput,
    proof: ScrubpackSolverProof,
) -> dict[str, object]:
    try:
        pipeline = json.loads(proof.pipeline_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScrubpackSolverIdentityError("READY pipeline evidence is malformed") from exc
    entry = dict(proof.release_pool_entry)
    is_release_pool = entry.get("schema") == "scrubbots-release-pool-entry/v1"
    if is_release_pool:
        entry_digest = entry.get("entry_digest")
        entry_body = {key: value for key, value in entry.items() if key != "entry_digest"}
        if not isinstance(entry_digest, str) or not _SHA256.fullmatch(entry_digest) or _canonical_digest(entry_body) != entry_digest:
            raise ScrubpackSolverIdentityError("Release Pool entry digest is missing or invalid")
    elif entry.get("schema") != "scrubbots.factory.accepted-ready-proof/v1":
        raise ScrubpackSolverIdentityError("solver proof source is not current Release Pool or accepted READY evidence")
    if not isinstance(pipeline, dict):
        raise ScrubpackSolverIdentityError("READY pipeline root must be an object")
    pipeline_sha256 = _sha256(proof.pipeline_bytes)
    if (
        pipeline.get("schema") != "scrubbots-studio-pipeline-run"
        or type(pipeline.get("version")) is not int
        or pipeline.get("version") != 2
        or pipeline.get("disposition") != "READY"
        or pipeline.get("run_id") != entry.get("pipeline_run_id")
        or pipeline.get("candidate_id") != entry.get("candidate_id")
        or pipeline_sha256 != entry.get("pipeline_sha256")
        or (is_release_pool and entry.get("pipeline") != pipeline)
        or not isinstance(entry.get("review_id"), str)
        or not entry["review_id"].startswith(f"review-{entry.get('candidate_id')}-")
    ):
        raise ScrubpackSolverIdentityError("READY pipeline, candidate, review, or Release Pool identity is stale or mismatched")
    primary = pipeline.get("primary")
    if not isinstance(primary, Mapping) or primary.get("state") != "READY" or primary.get("disposition") != "READY":
        raise ScrubpackSolverIdentityError("Release Pool pipeline is not a READY canonical supply run")
    stages = pipeline.get("stages")
    if not isinstance(stages, list):
        raise ScrubpackSolverIdentityError("pipeline stage evidence is malformed")
    stage_states = {stage.get("stage"): stage.get("disposition") for stage in stages if isinstance(stage, Mapping)}
    if any(stage_states.get(name) != "PASS" for name in ("SOLVE", "REPLAY", "QA")):
        raise ScrubpackSolverIdentityError("pipeline lacks canonical solver PASS, replay PASS, or QA PASS")
    result = primary.get("result")
    identity = primary.get("solver_supply_identity")
    if not isinstance(result, Mapping) or not isinstance(identity, Mapping) or result.get("solver_supply_identity") != identity:
        raise ScrubpackSolverIdentityError("READY pipeline is missing its immutable solver supply identity")

    level_raw = level.level_data.payload
    plan_raw = level.supply_plan.payload
    try:
        level_data = json.loads(level_raw.decode("utf-8"))
        plan = json.loads(plan_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScrubpackSolverIdentityError("packaging level or supply bytes are malformed") from exc
    if not isinstance(level_data, dict) or not isinstance(plan, dict):
        raise ScrubpackSolverIdentityError("packaging level and supply payloads must be objects")
    level_sha256 = _sha256(level_raw)
    plan_sha256 = _sha256(plan_raw)
    pipeline_files = primary.get("files")
    files = entry.get("files") if is_release_pool else None
    if not isinstance(pipeline_files, Mapping) or (is_release_pool and not isinstance(files, Mapping)):
        raise ScrubpackSolverIdentityError("READY or Release Pool file bindings are missing")
    for key, raw, path_key in (("level", level_raw, "level"), ("supply_plan", plan_raw, "supply_plan")):
        pipeline_path = str(pipeline_files.get(path_key, ""))
        if not pipeline_path:
            raise ScrubpackSolverIdentityError(f"READY pipeline {key} path is missing")
        if is_release_pool:
            record = files.get(key)
            if not isinstance(record, Mapping) or record.get("sha256") != _sha256(raw):
                raise ScrubpackSolverIdentityError(f"packaged {key} bytes differ from current Release Pool identity")
            if str(record.get("path", "")) != pipeline_path:
                raise ScrubpackSolverIdentityError(f"packaged {key} path differs from READY pipeline evidence")
        else:
            try:
                current_file_bytes = Path(pipeline_path).read_bytes()
            except OSError as exc:
                raise ScrubpackSolverIdentityError(f"current READY pipeline {key} file is unavailable") from exc
            if _sha256(current_file_bytes) != _sha256(raw):
                raise ScrubpackSolverIdentityError(f"packaged {key} bytes differ from current READY pipeline files")
    if (
        level.level_id != level_data.get("id")
        or plan.get("levelId") != level.level_id
        or plan.get("schema") != "scrubbots.level_supply_plan.v1"
        or plan.get("version") != 1
        or not isinstance(plan.get("columns"), list)
        or not isinstance(identity.get("authority"), Mapping)
    ):
        raise ScrubpackSolverIdentityError("packaged LevelData or supply-plan identity differs from the solver run")
    authority = identity["authority"]
    git_head = authority.get("git_head")
    if (
        authority.get("repository") != "Sekiph82/Scrubbots"
        or authority.get("branch") != "main"
        or not isinstance(git_head, str)
        or not _GIT_SHA.fullmatch(git_head)
        or primary.get("authority") != authority
    ):
        raise ScrubpackSolverIdentityError("solver evidence does not name the canonical current ScrubBots main authority")
    identity_columns = identity.get("fifo_columns")
    if (
        identity.get("schema") != SOLVER_IDENTITY_SCHEMA
        or identity.get("version") != 1
        or identity.get("level_id") != level.level_id
        or identity.get("level_data_sha256") != level_sha256
        or identity.get("supply_plan_sha256") != plan_sha256
        or identity_columns != plan.get("columns")
        or identity.get("column_count") != plan.get("columnCount")
        or identity.get("visible_preview_depth") != plan.get("visiblePreviewDepth")
        or identity.get("max_robots_per_batch") != plan.get("maxRobotsPerBatch")
    ):
        raise ScrubpackSolverIdentityError("FIFO batches, configuration, or content digests differ from the solver binding")
    for key in ("solver_state_sha256", "solver_evidence_sha256"):
        value = identity.get(key)
        if not isinstance(value, str) or not _SHA256.fullmatch(value):
            raise ScrubpackSolverIdentityError(f"{key} is missing or malformed")
    state_body = {
        "schema": f"{SOLVER_IDENTITY_SCHEMA}.initial-state",
        "version": 1,
        "level_id": level.level_id,
        "level_data_sha256": level_sha256,
        "supply_plan_sha256": plan_sha256,
        "fifo_columns": plan["columns"],
        "column_count": plan["columnCount"],
        "visible_preview_depth": plan["visiblePreviewDepth"],
        "max_robots_per_batch": plan["maxRobotsPerBatch"],
        "authority": dict(authority),
    }
    if _canonical_digest(state_body) != identity["solver_state_sha256"]:
        raise ScrubpackSolverIdentityError("canonical initial solver-state digest does not match exact pack inputs")
    evidence_body = _solver_evidence_body(result, authority)
    if (
        result.get("solver_status") != "SOLVED"
        or result.get("solution_final") != "WIN"
        or _canonical_digest(evidence_body) != identity["solver_evidence_sha256"]
    ):
        raise ScrubpackSolverIdentityError("canonical solver PASS evidence digest does not match the current READY run")
    replay = result.get("solution_replay")
    if not isinstance(replay, Mapping) or replay.get("ok") is not True or replay.get("solved") is not True or replay.get("finalActive") != 0:
        raise ScrubpackSolverIdentityError("canonical solver replay does not prove the packaged initial supply")
    if primary.get("load_check", {}).get("state") != "READY":
        raise ScrubpackSolverIdentityError("current canonical supply-plan load check is not READY")

    return {
        "level_id": level.level_id,
        "level_data_sha256": level_sha256,
        "supply_plan_sha256": plan_sha256,
        "fifo_columns": plan["columns"],
        "column_count": plan["columnCount"],
        "visible_preview_depth": plan["visiblePreviewDepth"],
        "max_robots_per_batch": plan["maxRobotsPerBatch"],
        "solver_state_sha256": identity["solver_state_sha256"],
        "solver_evidence_sha256": identity["solver_evidence_sha256"],
        "authority": dict(authority),
        "source": {
            "candidate_id": entry["candidate_id"],
            "review_id": entry["review_id"],
            "authority_type": "release_pool" if is_release_pool else "accepted_ready_pipeline",
            "release_pool_entry_digest": entry.get("entry_digest") if is_release_pool else None,
            "pipeline_run_id": pipeline["run_id"],
            "pipeline_sha256": pipeline_sha256,
        },
    }


def build_solver_proven_scrubpack(
    levels: Sequence[ScrubpackLevelInput],
    *,
    proofs: Mapping[str, ScrubpackSolverProof],
    pack_id: str,
    pack_version: int,
    created_at_utc: str,
    current_authority_check: Callable[
        [Sequence[ScrubpackLevelInput], Mapping[str, ScrubpackSolverProof]], bool
    ],
) -> ScrubpackBuildResult:
    """Build a pack only after its injected Factory authority seam confirms freshness.

    The callback must re-read the current owner review, READY/Release Pool projection,
    pipeline bytes, and source level/supply files. This module does not import Factory
    implementation. The callback runs after cryptographic and pack construction checks,
    immediately before any pack bytes or success evidence are returned.
    """
    if not callable(current_authority_check):
        raise ScrubpackSolverIdentityError("a current Factory authority verifier is required")
    level_inputs = tuple(levels)
    level_ids = tuple(level.level_id for level in level_inputs if isinstance(level, ScrubpackLevelInput))
    if len(level_ids) != len(level_inputs) or set(proofs) != set(level_ids) or len(set(level_ids)) != len(level_ids):
        raise ScrubpackSolverIdentityError("every packaged level must have exactly one current solver proof")
    bindings = [_proof_for_level(level, proofs[level.level_id]) for level in level_inputs]
    pack_result = build_scrubpack(
        level_inputs, pack_id=pack_id, pack_version=pack_version, created_at_utc=created_at_utc
    )
    artifact = {
        "schema": SOLVER_IDENTITY_ARTIFACT_SCHEMA,
        "version": 1,
        "pack_sha256": pack_result.evidence.archive_sha256,
        "levels": bindings,
    }
    artifact_bytes = _canonical_bytes(artifact) + b"\n"
    artifact_sha256 = _sha256(artifact_bytes)
    evidence = replace(pack_result.evidence, solver_identity_artifact_sha256=artifact_sha256)
    result = ScrubpackBuildResult(
        archive_bytes=pack_result.archive_bytes,
        evidence=evidence,
        solver_identity_artifact_bytes=artifact_bytes,
    )
    if current_authority_check(level_inputs, proofs) is not True:
        raise ScrubpackSolverIdentityError("current Factory owner/review/READY authority verification failed")
    return result


def verify_solver_proven_scrubpack(
    archive_bytes: bytes,
    identity_artifact_bytes: bytes,
    evidence: object,
) -> bool:
    if not verify_scrubpack_build(
        archive_bytes, evidence, solver_identity_artifact_bytes=identity_artifact_bytes
    ):
        return False
    try:
        artifact = json.loads(identity_artifact_bytes.decode("utf-8"))
        with ZipFile(io.BytesIO(archive_bytes)) as archive:
            manifest = json.loads(archive.read(PACK_MANIFEST_PATH))
    except (UnicodeDecodeError, json.JSONDecodeError, OSError, KeyError, ValueError):
        return False
    if (
        not isinstance(artifact, dict)
        or artifact.get("schema") != SOLVER_IDENTITY_ARTIFACT_SCHEMA
        or artifact.get("version") != 1
        or artifact.get("pack_sha256") != _sha256(archive_bytes)
        or not isinstance(artifact.get("levels"), list)
    ):
        return False
    digest_by_path: dict[str, str] = {}
    for level in manifest.get("levels", []):
        files = level.get("files", {})
        digests = level.get("sha256", {})
        digest_by_path[files.get("levelData")] = digests.get("levelData")
        digest_by_path[files.get("supplyPlan")] = digests.get("supplyPlan")
    for binding in artifact["levels"]:
        if (
            not isinstance(binding, dict)
            or digest_by_path.get(f"levels/{binding.get('level_id')}/level.json") != binding.get("level_data_sha256")
            or digest_by_path.get(f"levels/{binding.get('level_id')}/supply-plan.json") != binding.get("supply_plan_sha256")
            or not isinstance(binding.get("source"), dict)
            or not _SHA256.fullmatch(str(binding.get("solver_state_sha256", "")))
            or not _SHA256.fullmatch(str(binding.get("solver_evidence_sha256", "")))
        ):
            return False
    return True


__all__ = [
    "SOLVER_IDENTITY_ARTIFACT_SCHEMA",
    "SOLVER_IDENTITY_SCHEMA",
    "ScrubpackSolverIdentityError",
    "ScrubpackSolverProof",
    "build_solver_proven_scrubpack",
    "verify_solver_proven_scrubpack",
]
