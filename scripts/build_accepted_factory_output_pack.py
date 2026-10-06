"""Assemble explicit current Factory candidates into a solver-proven scrubpack.

This script is the local integration adapter from Factory's read-only accepted
READY/Release Pool authority into the separate Content Pipeline pack builder.
It does no candidate discovery, review mutation, game write, provider call, or
network IO. It stays outside both core packages to preserve their one-way
dependency boundary.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
import sys
from typing import Any

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
for _SOURCE_ROOT in (_REPOSITORY_ROOT / "src", _REPOSITORY_ROOT / "content_pipeline" / "src"):
    if str(_SOURCE_ROOT) not in sys.path:
        sys.path.insert(0, str(_SOURCE_ROOT))

from scrubbots_pixel_factory import studio_extensions as studio
from scrubbots_pixel_factory.supply_pipeline.scrubpack_identity import (
    SolverSupplyIdentityError,
    current_solver_proof_for_candidate,
    revalidate_current_solver_proofs,
)
from scrubbots_content_pipeline import ScrubpackBuildResult, ScrubpackLevelInput

_CANDIDATE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

class FactoryPackAssemblyError(ValueError):
    """An explicit Factory membership or its current accepted authority is invalid."""


def _canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise FactoryPackAssemblyError("Factory pack metadata is not canonical JSON") from exc


def _payload_descriptor(
    *,
    content_type: str,
    media_type: str,
    descriptor_contract_id: str,
    logical_path: str,
    payload_contract: Mapping[str, object],
    attributes: Mapping[str, object],
) -> dict[str, object]:
    return {
        "attributes": dict(attributes),
        "boundary_version": "1.0",
        "content_type": content_type,
        "descriptor_contract_id": descriptor_contract_id,
        "logical_path": logical_path,
        "media_type": media_type,
        "payload_contract": dict(payload_contract),
    }


def _read_current_factory_file(path_value: object, *, repository_root: Path) -> bytes:
    if not isinstance(path_value, str) or not path_value:
        raise FactoryPackAssemblyError("current READY pipeline source path is missing")
    source = Path(path_value)
    if not source.is_absolute() or source.is_symlink() or not source.is_file():
        raise FactoryPackAssemblyError("current READY pipeline source is not a local regular file")
    try:
        resolved = source.resolve(strict=True)
        root = repository_root.resolve(strict=True)
        if not resolved.is_relative_to(root):
            raise FactoryPackAssemblyError("current READY pipeline source escaped the Factory repository")
        return resolved.read_bytes()
    except OSError as exc:
        raise FactoryPackAssemblyError("current READY pipeline source could not be read") from exc


def _decode_object(raw: bytes, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FactoryPackAssemblyError(f"current Factory {label} payload is malformed") from exc
    if not isinstance(value, dict):
        raise FactoryPackAssemblyError(f"current Factory {label} payload is not an object")
    return value


def _level_input(
    pipeline: Mapping[str, Any], *, repository_root: Path
) -> tuple[str, "ScrubpackLevelInput"]:
    primary = pipeline.get("primary")
    files = primary.get("files") if isinstance(primary, Mapping) else None
    if not isinstance(files, Mapping):
        raise FactoryPackAssemblyError("current READY pipeline has no explicit level and supply-plan files")
    level_bytes = _read_current_factory_file(files.get("level"), repository_root=repository_root)
    plan_bytes = _read_current_factory_file(files.get("supply_plan"), repository_root=repository_root)
    level = _decode_object(level_bytes, label="LevelData")
    plan = _decode_object(plan_bytes, label="supply plan")
    level_id = level.get("id")
    if not isinstance(level_id, str) or plan.get("levelId") != level_id:
        raise FactoryPackAssemblyError("current Factory candidate and source level identities differ")
    width, height = level.get("width"), level.get("height")
    column_count = plan.get("columnCount")
    preview_depth = plan.get("visiblePreviewDepth")
    if (
        type(width) is not int or width < 1
        or type(height) is not int or height < 1
        or type(column_count) is not int or column_count < 1
        or type(preview_depth) is not int or preview_depth < 0
        or not isinstance(level.get("difficulty"), str)
    ):
        raise FactoryPackAssemblyError("current Factory level dimensions or supply configuration are invalid")

    from scrubbots_content_pipeline import ScrubpackLevelInput, ScrubpackPayloadInput

    level_sha256 = hashlib.sha256(level_bytes).hexdigest()
    plan_sha256 = hashlib.sha256(plan_bytes).hexdigest()
    metadata = {
        "schema": "scrubbots.level.metadata.v1",
        "version": 1,
        "builderVersion": "M14-CP03-002-C001",
        "id": level_id,
        "width": width,
        "height": height,
        "cellCount": width * height,
        "difficulty": level["difficulty"],
        "columnCount": column_count,
        "visiblePreviewDepth": preview_depth,
        "fileDigests": {"level": level_sha256, "supply_plan": plan_sha256},
    }
    metadata_bytes = _canonical_json_bytes(metadata)
    level_descriptor = _payload_descriptor(
        content_type="level_data",
        media_type="application/vnd.scrubbots.level+json",
        descriptor_contract_id="scrubbots.content-pipeline.level-data.v1",
        logical_path=f"levels/{level_id}.json",
        payload_contract={"authority": "Level Data Specification", "version": 1},
        attributes={
            "height": height, "level_id": level_id, "payload_sha256": level_sha256, "width": width,
        },
    )
    plan_descriptor = _payload_descriptor(
        content_type="supply_plan_data",
        media_type="application/vnd.scrubbots.supply-plan+json",
        descriptor_contract_id="scrubbots.content-pipeline.supply-plan.v1",
        logical_path=f"supply/{level_id}.json",
        payload_contract={"schema": "scrubbots.level_supply_plan.v1", "version": 1},
        attributes={
            "columns": column_count, "level_id": level_id,
            "preview_depth": preview_depth, "supply_plan_sha256": plan_sha256,
        },
    )
    metadata_descriptor = _payload_descriptor(
        content_type="approved_metadata",
        media_type="application/vnd.scrubbots.approved-metadata+json",
        descriptor_contract_id="scrubbots.content-pipeline.publisher-metadata.v1",
        logical_path=f"metadata/{level_id}.json",
        payload_contract={"schema": "scrubbots.level.metadata.v1", "version": 1},
        attributes={
            "columns": column_count, "height": height, "level_id": level_id,
            "payload_sha256": hashlib.sha256(metadata_bytes).hexdigest(),
            "preview_depth": preview_depth, "width": width,
        },
    )
    return level_id, ScrubpackLevelInput(
        level_id=level_id,
        level_data=ScrubpackPayloadInput(level_descriptor, level_bytes),
        supply_plan=ScrubpackPayloadInput(plan_descriptor, plan_bytes),
        metadata=ScrubpackPayloadInput(metadata_descriptor, metadata_bytes),
    )


def build_accepted_factory_output_pack(
    candidate_ids: Sequence[str],
    *,
    pack_id: str,
    pack_version: int,
    created_at_utc: str,
) -> "ScrubpackBuildResult":
    """Build one deterministic pack from explicitly selected, currently accepted Factory candidates.

    Membership, pack identity, version, and timestamp are required inputs. The
    current CPX-001 revalidator is fixed at the final build boundary so stale
    review, READY, pipeline, Release Pool, or source-file authority rejects the
    pack before successful bytes are returned.
    """
    if isinstance(candidate_ids, (str, bytes)) or not isinstance(candidate_ids, Sequence):
        raise FactoryPackAssemblyError("candidate membership must be an explicit sequence of IDs")
    selected = tuple(candidate_ids)
    if (
        not selected
        or any(not isinstance(item, str) or not _CANDIDATE_ID.fullmatch(item) for item in selected)
        or len({item.casefold() for item in selected}) != len(selected)
    ):
        raise FactoryPackAssemblyError("candidate membership is empty, malformed, or duplicated")
    selected = tuple(sorted(selected, key=lambda item: item.encode("ascii")))

    from scrubbots_content_pipeline import (
        ScrubpackSolverProof,
        build_solver_proven_scrubpack,
    )
    repository_root = studio._repository_root()
    levels = []
    proofs = {}
    for candidate_id in selected:
        try:
            pipeline_bytes, source = current_solver_proof_for_candidate(candidate_id)
        except (SolverSupplyIdentityError, OSError, ValueError) as exc:
            raise FactoryPackAssemblyError("candidate lacks current owner-accepted READY or Release Pool authority") from exc
        if (
            type(pipeline_bytes) is not bytes
            or not isinstance(source, Mapping)
            or source.get("candidate_id") != candidate_id
        ):
            raise FactoryPackAssemblyError("current Factory proof does not match explicit candidate membership")
        pipeline = _decode_object(pipeline_bytes, label="READY pipeline")
        if (
            pipeline.get("disposition") != "READY"
            or pipeline.get("candidate_id") != candidate_id
            or not isinstance(pipeline.get("run_id"), str)
            or pipeline.get("run_id") != source.get("pipeline_run_id")
            or not isinstance(pipeline.get("primary"), Mapping)
            or pipeline["primary"].get("state") != "READY"
            or pipeline["primary"].get("disposition") != "READY"
        ):
            raise FactoryPackAssemblyError("current owner-accepted READY pipeline identity is invalid")
        level_id, level_input = _level_input(pipeline, repository_root=repository_root)
        levels.append(level_input)
        proofs[level_id] = ScrubpackSolverProof(pipeline_bytes, source)

    try:
        return build_solver_proven_scrubpack(
            tuple(levels),
            proofs=proofs,
            pack_id=pack_id,
            pack_version=pack_version,
            created_at_utc=created_at_utc,
            current_authority_check=revalidate_current_solver_proofs,
        )
    except (SolverSupplyIdentityError, ValueError, OSError) as exc:
        raise FactoryPackAssemblyError("current Factory authority rejected deterministic pack assembly") from exc


__all__ = ["FactoryPackAssemblyError", "build_accepted_factory_output_pack"]
