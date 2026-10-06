"""Pure gate for exact staged supply bytes and current-game replay evidence."""

from __future__ import annotations

import hashlib
import io
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol
from zipfile import BadZipFile, ZipFile

from .config import Environment
from .scrubpack_inspection import inspect_scrubpack
from .scrubpack_solver_identity import verify_solver_proven_scrubpack
from .scrubpack_spec import PACK_MANIFEST_PATH
from .staging_download_verify import (
    StagingDownloadReasonCode,
    StagingDownloadVerificationReport,
    serialize_staging_download_verification_receipt,
)

CURRENT_MAIN_REPLAY_VERSION = "1.0"
REPOSITORY = "Sekiph82/Scrubbots"
GAME_REMOTE = "https://github.com/Sekiph82/Scrubbots.git"
AUTHORITY_SOURCE_PATHS = (
    "scripts/data/level_loader.gd",
    "scripts/gameplay/supply/supply_plan_loader.gd",
    "scripts/gameplay/solver/proof_state.gd",
    "scripts/gameplay/solver/solvability_solver.gd",
    "scripts/gameplay/solver/proof_kernel.gd",
)
_SHA = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


class CurrentGameRunner(Protocol):
    def __call__(self, levels: Sequence[Mapping[str, object]]) -> Mapping[str, object]: ...


class AuthorityCheck(Protocol):
    def __call__(self) -> Mapping[str, object]: ...


@dataclass(frozen=True, slots=True)
class CurrentMainReplayReceipt:
    accepted: bool
    reason_code: str
    game_repository: str
    game_branch: str
    game_commit: str
    authority_source_sha256: Mapping[str, str]
    manifest_sha256: str
    pack_results: tuple[Mapping[str, object], ...]
    target_environment: str = "STAGING"
    schema_version: str = CURRENT_MAIN_REPLAY_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "accepted": self.accepted,
            "reason_code": self.reason_code,
            "target_environment": self.target_environment,
            "game_authority": {
                "repository": self.game_repository,
                "branch": self.game_branch,
                "commit": self.game_commit,
                "source_sha256": dict(self.authority_source_sha256),
            },
            "manifest_sha256": self.manifest_sha256,
            "packs": [dict(row) for row in self.pack_results],
        }


class CurrentMainReplayError(ValueError):
    """Input or authority did not meet the current-main promotion gate."""


def verify_current_main_supply_replay(
    *,
    staging_report: StagingDownloadVerificationReport,
    downloaded_manifest_bytes: bytes,
    downloaded_pack_bytes: Mapping[str, bytes],
    solver_identity_artifacts: Mapping[str, bytes],
    pack_build_evidence: Mapping[str, object],
    game_authority: Mapping[str, object],
    authority_check: AuthorityCheck,
    game_runner: CurrentGameRunner,
) -> CurrentMainReplayReceipt:
    """Verify CP03-007 bytes and require the injected current-main game to solve all.

    Process execution and filesystem/Git access belong to the host adapter; this package
    verifies byte identity, CPX-001 bindings, the canonical game result, and drift.
    """
    try:
        _require_staging_inputs(
            staging_report, downloaded_manifest_bytes, downloaded_pack_bytes,
            solver_identity_artifacts, pack_build_evidence,
        )
        before = _valid_authority(game_authority)
        if not callable(authority_check) or not callable(game_runner):
            raise CurrentMainReplayError("CURRENT_GAME_ADAPTER_REQUIRED")
        pack_results: list[Mapping[str, object]] = []
        for pack in staging_report.receipt.packs:  # type: ignore[union-attr]
            raw = downloaded_pack_bytes[pack.pack_id]
            artifact = solver_identity_artifacts[pack.pack_id]
            evidence = pack_build_evidence[pack.pack_id]
            if not verify_solver_proven_scrubpack(raw, artifact, evidence):
                raise CurrentMainReplayError("CPX001_IDENTITY_REJECTED")
            artifact_doc = json.loads(artifact.decode("utf-8"))
            artifact_levels = {row["level_id"]: row for row in artifact_doc["levels"]}
            if any(
                not isinstance(row.get("authority"), dict)
                or row["authority"].get("repository") != REPOSITORY
                or row["authority"].get("branch") != "main"
                or row["authority"].get("git_head") != before["commit"]
                for row in artifact_levels.values()
            ):
                raise CurrentMainReplayError("CPX001_GAME_AUTHORITY_MISMATCH")
            pack_levels = _inspect_pack_levels(raw)
            if set(pack_levels) != set(artifact_levels):
                raise CurrentMainReplayError("CPX001_LEVEL_SET_MISMATCH")
            game_levels: list[Mapping[str, object]] = []
            for level_id, (level_bytes, plan_bytes) in sorted(pack_levels.items()):
                binding = artifact_levels[level_id]
                if (
                    hashlib.sha256(level_bytes).hexdigest() != binding["level_data_sha256"]
                    or hashlib.sha256(plan_bytes).hexdigest() != binding["supply_plan_sha256"]
                ):
                    raise CurrentMainReplayError("CPX001_DIGEST_MISMATCH")
                level_doc = _strict_json(level_bytes)
                plan_doc = _strict_json(plan_bytes)
                if (
                    level_doc.get("id") != level_id
                    or plan_doc.get("schema") != "scrubbots.level_supply_plan.v1"
                    or plan_doc.get("levelId") != level_id
                    or plan_doc.get("columns") != binding.get("fifo_columns")
                    or plan_doc.get("columnCount") != binding.get("column_count")
                    or plan_doc.get("visiblePreviewDepth") != binding.get("visible_preview_depth")
                    or plan_doc.get("maxRobotsPerBatch") != binding.get("max_robots_per_batch")
                ):
                    raise CurrentMainReplayError("CPX001_IDENTITY_MISMATCH")
                game_levels.append({
                    "level_id": level_id,
                    "level_data_bytes": level_bytes,
                    "supply_plan_bytes": plan_bytes,
                    "level_sha256": hashlib.sha256(level_bytes).hexdigest(),
                    "plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
                    "fifo_columns": binding["fifo_columns"],
                    "solver_state_sha256": binding["solver_state_sha256"],
                    "solver_evidence_sha256": binding["solver_evidence_sha256"],
                })
            result = game_runner(tuple(game_levels))
            if not isinstance(result, Mapping) or result.get("accepted") is not True:
                raise CurrentMainReplayError("GAME_REPLAY_REJECTED")
            rows_value = result.get("levels")
            if not isinstance(rows_value, list) or len(rows_value) != len(game_levels):
                raise CurrentMainReplayError("GAME_REPLAY_REJECTED")
            rows = {row.get("level_id"): row for row in rows_value if isinstance(row, Mapping)}
            if set(rows) != {row["level_id"] for row in game_levels} or any(
                not _level_pass(rows[level_id], expected)
                for level_id, expected in ((row["level_id"], row) for row in game_levels)
            ):
                raise CurrentMainReplayError("GAME_REPLAY_REJECTED")
            pack_results.append({
                "pack_id": pack.pack_id,
                "pack_sha256": hashlib.sha256(raw).hexdigest(),
                "solver_identity_artifact_sha256": hashlib.sha256(artifact).hexdigest(),
                "levels": [rows[level_id] for level_id in sorted(rows)],
            })
        after = _valid_authority(authority_check())
        if before != after:
            raise CurrentMainReplayError("STALE_GAME_AUTHORITY")
        return CurrentMainReplayReceipt(
            True, "VERIFIED", REPOSITORY, "main", before["commit"], before["source_sha256"],
            hashlib.sha256(downloaded_manifest_bytes).hexdigest(), tuple(pack_results),
        )
    except CurrentMainReplayError as exc:
        return _failure(str(exc), downloaded_manifest_bytes)
    except (OSError, ValueError, TypeError, KeyError, BadZipFile, json.JSONDecodeError):
        return _failure("VERIFICATION_ERROR", downloaded_manifest_bytes)


def _require_staging_inputs(report, manifest_bytes, packs, artifacts, evidence) -> None:
    if (
        not isinstance(report, StagingDownloadVerificationReport)
        or report.accepted is not True
        or report.reason_code is not StagingDownloadReasonCode.VERIFIED
        or report.receipt is None
    ):
        raise CurrentMainReplayError("STAGING_DOWNLOAD_NOT_VERIFIED")
    receipt = report.receipt
    try:
        serialize_staging_download_verification_receipt(receipt)
    except (TypeError, ValueError, AttributeError) as exc:
        raise CurrentMainReplayError("INVALID_STAGING_RECEIPT") from exc
    if receipt.target_environment != Environment.STAGING.value or type(manifest_bytes) is not bytes:
        raise CurrentMainReplayError("INVALID_STAGING_INPUT")
    if hashlib.sha256(manifest_bytes).hexdigest() != receipt.manifest_sha256 or manifest_bytes != receipt.manifest_bytes:
        raise CurrentMainReplayError("MANIFEST_DIGEST_MISMATCH")
    if set(packs) != {row.pack_id for row in receipt.packs}:
        raise CurrentMainReplayError("STAGED_PACK_SET_MISMATCH")
    if set(artifacts) != set(packs) or set(evidence) != set(packs):
        raise CurrentMainReplayError("CPX001_EVIDENCE_MISSING")
    for row in receipt.packs:
        raw = packs[row.pack_id]
        if type(raw) is not bytes or len(raw) != row.byte_length or hashlib.sha256(raw).hexdigest() != row.sha256:
            raise CurrentMainReplayError("STAGED_PACK_DIGEST_MISMATCH")
        inspection = inspect_scrubpack(raw)
        if not inspection.accepted or inspection.pack_id != row.pack_id or inspection.level_ids != row.level_ids:
            raise CurrentMainReplayError("STAGED_PACK_INVALID")


def _valid_authority(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise CurrentMainReplayError("INVALID_GAME_AUTHORITY")
    commit = value.get("commit")
    sources = value.get("source_sha256")
    if (
        value.get("repository") != REPOSITORY
        or value.get("branch") != "main"
        or not isinstance(commit, str)
        or not _GIT_SHA.fullmatch(commit)
        or not isinstance(sources, Mapping)
        or set(sources) != set(AUTHORITY_SOURCE_PATHS)
        or any(not isinstance(digest, str) or not _SHA.fullmatch(digest) for digest in sources.values())
    ):
        raise CurrentMainReplayError("INVALID_GAME_AUTHORITY")
    return {"repository": REPOSITORY, "branch": "main", "commit": commit, "source_sha256": dict(sources)}


def _inspect_pack_levels(raw: bytes) -> dict[str, tuple[bytes, bytes]]:
    inspection = inspect_scrubpack(raw)
    if not inspection.accepted:
        raise CurrentMainReplayError("STAGED_PACK_INVALID")
    result = {}
    with ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise CurrentMainReplayError("PACK_DUPLICATE_PATH")
        for name in names:
            if name.startswith("/") or "\\" in name or any(part in {"", ".", ".."} for part in name.split("/")):
                raise CurrentMainReplayError("PACK_UNSAFE_PATH")
        manifest = _strict_json(archive.read(PACK_MANIFEST_PATH))
        if not isinstance(manifest.get("levels"), list):
            raise CurrentMainReplayError("PACK_MANIFEST_INVALID")
        for item in manifest["levels"]:
            level_id = item["id"]
            if not isinstance(level_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", level_id):
                raise CurrentMainReplayError("PACK_LEVEL_ID_INVALID")
            files = item["files"]
            level_path = files["levelData"]
            plan_path = files["supplyPlan"]
            expected_prefix = f"levels/{level_id}/"
            if level_path != expected_prefix + "level.json" or plan_path != expected_prefix + "supply-plan.json":
                raise CurrentMainReplayError("PACK_LEVEL_PATH_INVALID")
            level_bytes, plan_bytes = archive.read(level_path), archive.read(plan_path)
            digests = item["sha256"]
            if hashlib.sha256(level_bytes).hexdigest() != digests["levelData"] or hashlib.sha256(plan_bytes).hexdigest() != digests["supplyPlan"]:
                raise CurrentMainReplayError("PACK_LEVEL_DIGEST_INVALID")
            result[level_id] = (level_bytes, plan_bytes)
    if set(result) != set(inspection.level_ids):
        raise CurrentMainReplayError("PACK_LEVEL_SET_MISMATCH")
    return result


def _strict_json(raw: bytes) -> dict[str, object]:
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise CurrentMainReplayError("INVALID_JSON_OBJECT")
    return value


def _level_pass(actual: Mapping[str, object], expected: Mapping[str, object]) -> bool:
    return (
        actual.get("accepted") is True
        and actual.get("level_id") == expected["level_id"]
        and actual.get("level_sha256") == expected["level_sha256"]
        and actual.get("plan_sha256") == expected["plan_sha256"]
        and actual.get("fifo_columns") == expected["fifo_columns"]
        and actual.get("solver_state_sha256") == expected["solver_state_sha256"]
        and actual.get("solver_evidence_sha256") == expected["solver_evidence_sha256"]
        and actual.get("solver_status") == "SOLVED"
        and actual.get("replay_ok") is True
        and actual.get("replay_solved") is True
        and actual.get("final_active") == 0
        and actual.get("unresolved") == 0
        and actual.get("supply_exhausted") is True
    )


def _failure(reason: str, manifest: bytes) -> CurrentMainReplayReceipt:
    return CurrentMainReplayReceipt(
        False, reason, REPOSITORY, "main", "", {},
        hashlib.sha256(manifest).hexdigest() if type(manifest) is bytes else "",
        (),
    )


__all__ = [
    "AUTHORITY_SOURCE_PATHS", "CURRENT_MAIN_REPLAY_VERSION", "CurrentMainReplayError",
    "CurrentMainReplayReceipt", "verify_current_main_supply_replay",
]
