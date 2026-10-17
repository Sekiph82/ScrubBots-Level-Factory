"""Pure, versioned compatibility contract for caller-supplied ScrubBots source.

This module never discovers, fetches, or executes a game checkout. Callers must
provide immutable source bytes, their SHA-256 inventory, and an independently
verified current-main commit identity.
"""

from __future__ import annotations

import hashlib
import base64
import binascii
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any


CONTRACT_VERSION = "scrubbots-current-game-contract/v1"
GAME_REPOSITORY = "Sekiph82/Scrubbots"
REQUIRED_SOURCE_PATHS = (
    "docs/01_GAMEPLAY_SPEC.md",
    "docs/03_LEVEL_DATA_SPEC.md",
    "scripts/data/level_data.gd",
    "scripts/data/level_loader.gd",
    "scripts/gameplay/supply/supply_plan_loader.gd",
    "scripts/gameplay/solver/proof_state.gd",
    "scripts/difficulty/level_difficulty_analyzer_v1.gd",
    "data/palettes/scrubbots_palette_v3.json",
)
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class CurrentGameContractDisposition(str, Enum):
    CURRENT_SOURCE_COMPATIBLE = "CURRENT_SOURCE_COMPATIBLE"
    CURRENT_GAME_UNVERIFIED = "CURRENT_GAME_UNVERIFIED"
    SOURCE_VERSION_DRIFT = "SOURCE_VERSION_DRIFT"
    SOURCE_HASH_MISMATCH = "SOURCE_HASH_MISMATCH"
    SOURCE_INVENTORY_INCOMPLETE = "SOURCE_INVENTORY_INCOMPLETE"
    CURRENT_GAME_CONTRACT_DRIFT = "CURRENT_GAME_CONTRACT_DRIFT"
    CURRENT_GAME_CONTRACT_UNSUPPORTED = "CURRENT_GAME_CONTRACT_UNSUPPORTED"


@dataclass(frozen=True, slots=True)
class CurrentGameContractReport:
    disposition: CurrentGameContractDisposition
    compatible: bool
    repository: str | None
    branch: str | None
    commit: str | None
    source_sha256: Mapping[str, str]
    reason_codes: tuple[str, ...]
    contract: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": CONTRACT_VERSION,
            "disposition": self.disposition.value,
            "compatible": self.compatible,
            "repository": self.repository,
            "branch": self.branch,
            "commit": self.commit,
            "source_sha256": dict(self.source_sha256),
            "reason_codes": list(self.reason_codes),
            "contract": dict(self.contract) if self.contract is not None else None,
            "runtime_executed": False,
        }


def evaluate_current_game_contract(
    *,
    authority: Mapping[str, object] | None,
    source_bytes: Mapping[str, bytes] | None,
) -> CurrentGameContractReport:
    """Compare supplied source bytes to their claimed hashes and parse contracts.

    ``source_commit_verified_as_main`` is a caller attestation: this pure parser
    cannot prove a GitHub ref or download a checkout. A missing/false attestation
    is reported as unverified, even when the byte-level contract parses.
    """

    if not isinstance(authority, Mapping) or not isinstance(source_bytes, Mapping):
        return _report(CurrentGameContractDisposition.CURRENT_GAME_UNVERIFIED, "AUTHORITY_OR_SOURCE_BYTES_MISSING")

    repository = authority.get("repository")
    branch = authority.get("branch")
    commit = authority.get("commit")
    main_commit = authority.get("main_commit")
    if repository != GAME_REPOSITORY or branch != "main" or not _is_sha(commit) or not _is_sha(main_commit):
        return _report(
            CurrentGameContractDisposition.CURRENT_GAME_UNVERIFIED,
            "INVALID_CURRENT_GAME_AUTHORITY",
            repository=repository if isinstance(repository, str) else None,
            branch=branch if isinstance(branch, str) else None,
            commit=commit if isinstance(commit, str) else None,
        )
    if commit != main_commit:
        return _report(
            CurrentGameContractDisposition.SOURCE_VERSION_DRIFT,
            "GAME_COMMIT_DIFFERS_FROM_CURRENT_MAIN",
            repository=repository,
            branch=branch,
            commit=commit,
        )

    claimed_hashes = authority.get("source_sha256")
    if not isinstance(claimed_hashes, Mapping) or set(claimed_hashes) != set(REQUIRED_SOURCE_PATHS):
        return _report(
            CurrentGameContractDisposition.SOURCE_INVENTORY_INCOMPLETE,
            "REQUIRED_SOURCE_SHA_INVENTORY_MISSING",
            repository=repository,
            branch=branch,
            commit=commit,
        )
    if set(source_bytes) != set(REQUIRED_SOURCE_PATHS) or any(type(raw) is not bytes for raw in source_bytes.values()):
        return _report(
            CurrentGameContractDisposition.SOURCE_INVENTORY_INCOMPLETE,
            "REQUIRED_IMMUTABLE_SOURCE_BYTES_MISSING",
            repository=repository,
            branch=branch,
            commit=commit,
        )

    actual_hashes = {path: hashlib.sha256(source_bytes[path]).hexdigest() for path in REQUIRED_SOURCE_PATHS}
    if any(not _is_sha256(claimed_hashes.get(path)) for path in REQUIRED_SOURCE_PATHS):
        return _report(
            CurrentGameContractDisposition.SOURCE_INVENTORY_INCOMPLETE,
            "MALFORMED_SOURCE_SHA256_INVENTORY",
            repository=repository,
            branch=branch,
            commit=commit,
            source_sha256=actual_hashes,
        )
    if any(actual_hashes[path] != claimed_hashes[path] for path in REQUIRED_SOURCE_PATHS):
        return _report(
            CurrentGameContractDisposition.SOURCE_HASH_MISMATCH,
            "SOURCE_BYTES_DO_NOT_MATCH_SHA256_INVENTORY",
            repository=repository,
            branch=branch,
            commit=commit,
            source_sha256=actual_hashes,
        )
    if authority.get("source_commit_verified_as_main") is not True:
        return _report(
            CurrentGameContractDisposition.CURRENT_GAME_UNVERIFIED,
            "CURRENT_MAIN_REF_ATTESTATION_MISSING",
            repository=repository,
            branch=branch,
            commit=commit,
            source_sha256=actual_hashes,
        )

    try:
        parsed, drift = _parse_contract(source_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
        return _report(
            CurrentGameContractDisposition.CURRENT_GAME_CONTRACT_UNSUPPORTED,
            "SOURCE_CONTRACT_PARSE_FAILED",
            repository=repository,
            branch=branch,
            commit=commit,
            source_sha256=actual_hashes,
            contract={"detail": str(exc)[:240]},
        )
    if drift:
        return _report(
            CurrentGameContractDisposition.CURRENT_GAME_CONTRACT_DRIFT,
            *drift,
            repository=repository,
            branch=branch,
            commit=commit,
            source_sha256=actual_hashes,
            contract=parsed,
        )
    return _report(
        CurrentGameContractDisposition.CURRENT_SOURCE_COMPATIBLE,
        "VERSIONED_LEVEL_SUPPLY_CONTRACT_MATCHED",
        repository=repository,
        branch=branch,
        commit=commit,
        source_sha256=actual_hashes,
        contract=parsed,
    )


def preflight_level_supply_bytes(
    *,
    contract_report: CurrentGameContractReport | None,
    level_data_bytes: bytes | None,
    supply_plan_bytes: bytes | None,
    candidate_id: str | None = None,
) -> dict[str, object]:
    """Read-only static LevelData/supply validation; never calls the game solver."""

    if contract_report is None or not contract_report.compatible or not isinstance(contract_report.contract, Mapping):
        disposition = (
            contract_report.disposition.value
            if isinstance(contract_report, CurrentGameContractReport)
            else CurrentGameContractDisposition.CURRENT_GAME_UNVERIFIED.value
        )
        return {
            "schema": "scrubbots-current-game-static-preflight/v1",
            "disposition": disposition,
            "compatible": False,
            "reason_codes": list(contract_report.reason_codes) if contract_report else ["CURRENT_GAME_AUTHORITY_REQUIRED"],
            "game_commit": contract_report.commit if contract_report else None,
            "source_sha256": dict(contract_report.source_sha256) if contract_report else {},
            "runtime_executed": False,
            "solver_invocations": 0,
        }
    if type(level_data_bytes) is not bytes or type(supply_plan_bytes) is not bytes:
        return _static_failure(contract_report, "LEVEL_DATA_OR_SUPPLY_PLAN_BYTES_REQUIRED")
    try:
        level = _strict_json_object(level_data_bytes)
        plan = _strict_json_object(supply_plan_bytes)
        contract = contract_report.contract
        level_result = _validate_level_data(level, contract)
        plan_result = _validate_supply_plan(plan, level, level_result, contract)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
        return _static_failure(contract_report, f"STATIC_INPUT_INVALID:{str(exc)[:160]}")
    if level_result["reason_codes"]:
        return _static_failure(contract_report, *level_result["reason_codes"])
    if plan_result:
        return _static_failure(contract_report, *plan_result)
    from ..quality.core import logical_grid_hash
    logical_cells = ["VOID" if cell == -1 else level_result["local_to_global"][cell] for cell in level["cells"]]
    return {
        "schema": "scrubbots-current-game-static-preflight/v1",
        "disposition": "SOURCE_CONTRACT_COMPATIBLE_NOT_REPLAYED",
        "compatible": True,
        "reason_codes": ["LEVEL_DATA_AND_FIFO_STATIC_CONTRACT_MATCHED", "CURRENT_MAIN_RUNTIME_NOT_EXECUTED"],
        "game_commit": contract_report.commit,
        "source_sha256": dict(contract_report.source_sha256),
        "level_id": level.get("id"),
        "candidate_id": candidate_id,
        "logical_grid_hash": logical_grid_hash(level["width"], level["height"], logical_cells),
        "level_data_sha256": hashlib.sha256(level_data_bytes).hexdigest(),
        "supply_plan_sha256": hashlib.sha256(supply_plan_bytes).hexdigest(),
        "level_data_version": level_result["version"],
        "void_cell_count": level_result["void_cells"],
        "artwork_cell_count": level_result["artwork_cells"],
        "fifo_column_count": plan["columnCount"],
        "visible_preview_depth": plan["visiblePreviewDepth"],
        "runtime_executed": False,
        "solver_invocations": 0,
    }


def preflight_json_snapshot(value: Mapping[str, object] | None) -> dict[str, object]:
    """Decode the JSON transport accepted by Factory's existing read-only readiness call."""

    if not isinstance(value, Mapping):
        return preflight_level_supply_bytes(contract_report=None, level_data_bytes=None, supply_plan_bytes=None)
    authority = value.get("authority")
    source_encoded = value.get("source_bytes_b64")
    try:
        if not isinstance(source_encoded, Mapping) or set(source_encoded) != set(REQUIRED_SOURCE_PATHS):
            return _static_failure_from_missing("REQUIRED_IMMUTABLE_SOURCE_BYTES_MISSING")
        source_bytes = {
            path: base64.b64decode(encoded, validate=True)
            for path, encoded in source_encoded.items()
            if isinstance(path, str) and isinstance(encoded, str)
        }
        level_bytes_value = value.get("level_data_b64")
        plan_bytes_value = value.get("supply_plan_b64")
        level_bytes = base64.b64decode(level_bytes_value, validate=True) if isinstance(level_bytes_value, str) else None
        plan_bytes = base64.b64decode(plan_bytes_value, validate=True) if isinstance(plan_bytes_value, str) else None
    except (binascii.Error, ValueError, TypeError):
        return _static_failure_from_missing("BASE64_SNAPSHOT_INVALID")
    report = evaluate_current_game_contract(authority=authority if isinstance(authority, Mapping) else None, source_bytes=source_bytes)
    candidate_id = value.get("candidate_id")
    return preflight_level_supply_bytes(contract_report=report, level_data_bytes=level_bytes,
                                        supply_plan_bytes=plan_bytes,
                                        candidate_id=candidate_id if isinstance(candidate_id, str) else None)


def current_main_replay_bridge(
    *,
    current_game_preflight: Mapping[str, object] | None,
    owner_provenance: Mapping[str, object] | None,
    cpx002_authority: Mapping[str, object] | None = None,
    replay_evidence: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Describe the CPX002 replay fence without invoking its runtime adapter."""
    missing: list[str] = []
    if not isinstance(current_game_preflight, Mapping) or current_game_preflight.get("compatible") is not True:
        missing.append("CURRENT_GAME_CONTRACT_AND_STATIC_LEVEL_PLAN_PREFLIGHT")
    if not isinstance(owner_provenance, Mapping) or owner_provenance.get("compatible") is not True:
        missing.append("SELECTED_OWNER_SOURCE_REVIEW_READY_LOAD_CHECK_PROVENANCE")
    if not isinstance(cpx002_authority, Mapping) or cpx002_authority.get("explicit_isolated_temp_game_authority") is not True:
        missing.append("EXPLICIT_ISOLATED_TEMP_SCRUBBOTS_PROJECT_AUTHORITY")
    if not isinstance(replay_evidence, Mapping):
        missing.extend(("CURRENT_GAME_MANIFEST_SHA256", "CURRENT_GAME_PACK_SHA256", "CURRENT_GAME_LEVEL_BYTES", "CURRENT_GAME_SUPPLY_PLAN_BYTES", "CURRENT_MAIN_RUNTIME_WIN_DIFFICULTY_LOAD_CHECK"))
    else:
        for field in ("manifest_sha256", "pack_sha256", "game_level_sha256", "game_supply_plan_sha256", "runtime_win", "difficulty", "load_check"):
            if replay_evidence.get(field) in (None, False, ""):
                missing.append({"manifest_sha256": "CURRENT_GAME_MANIFEST_SHA256", "pack_sha256": "CURRENT_GAME_PACK_SHA256",
                                "game_level_sha256": "CURRENT_GAME_LEVEL_BYTES", "game_supply_plan_sha256": "CURRENT_GAME_SUPPLY_PLAN_BYTES",
                                "runtime_win": "CURRENT_MAIN_RUNTIME_WIN_DIFFICULTY_LOAD_CHECK", "difficulty": "CURRENT_MAIN_RUNTIME_WIN_DIFFICULTY_LOAD_CHECK",
                                "load_check": "CURRENT_MAIN_RUNTIME_WIN_DIFFICULTY_LOAD_CHECK"}[field])
    return {
        "schema": "scrubbots-cpx002-current-main-bridge/v1",
        "disposition": "CPX002_AUTHORITY_REQUIRED" if missing else "CPX002_EVIDENCE_PRESENT_NOT_EXECUTED",
        "compatible": False,
        "missing_evidence": list(dict.fromkeys(missing)),
        "reason_codes": ["CURRENT_MAIN_RUNTIME_NOT_EXECUTED"],
        "runtime_executed": False,
        "solver_invocations": 0,
        "release_pool_mutated": False,
    }


def _strict_json_object(raw: bytes) -> dict[str, object]:
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("input must be a JSON object")
    return value


def _validate_level_data(level: Mapping[str, object], contract: Mapping[str, object]) -> dict[str, object]:
    reasons: list[str] = []
    version = level.get("version")
    width, height = level.get("width"), level.get("height")
    cells, palette = level.get("cells"), level.get("palette")
    if type(width) is not int or type(height) is not int or not (20 <= width <= 59 and 20 <= height <= 59):
        reasons.append("LEVEL_DIMENSIONS_OUTSIDE_CURRENT_PRODUCTION_ENVELOPE")
    if not isinstance(cells, list) or any(type(cell) is not int for cell in cells):
        reasons.append("LEVEL_CELLS_MUST_BE_INTEGER_PALETTE_IDS_OR_VOID")
        cells = []
    if type(width) is int and type(height) is int and len(cells) != width * height:
        reasons.append("LEVEL_CELL_COUNT_MISMATCH")
    if not isinstance(palette, list) or not palette or any(not isinstance(color, str) for color in palette):
        reasons.append("LEVEL_LOCAL_PALETTE_INVALID")
        palette = []
    void_cells = sum(cell == -1 for cell in cells)
    artwork_cells = len(cells) - void_cells
    if any(cell < -1 for cell in cells):
        reasons.append("LEVEL_CELL_VALUE_UNSUPPORTED")
    if type(version) is not int or version not in (1, 2):
        reasons.append("LEVEL_DATA_VERSION_UNSUPPORTED")
    elif version == 1 and void_cells:
        reasons.append("VOID_REQUIRES_LEVEL_DATA_V2")
    elif version == 1 and not void_cells:
        pass
    elif version == 2 and (void_cells == 0 or artwork_cells == 0):
        reasons.append("LEVEL_DATA_V2_REQUIRES_VOID_AND_ARTWORK")
    if any(cell >= len(palette) for cell in cells):
        reasons.append("LEVEL_CELL_PALETTE_INDEX_OUT_OF_RANGE")

    global_palette = contract.get("global_palette_hex")
    if not isinstance(global_palette, Mapping):
        reasons.append("CURRENT_GLOBAL_PALETTE_UNAVAILABLE")
        global_palette = {}
    normalized_global = {key: _normalize_hex(value) for key, value in global_palette.items() if isinstance(key, str) and isinstance(value, str)}
    normalized_local = [_normalize_hex(color) for color in palette]
    if any(color is None for color in normalized_local):
        reasons.append("LEVEL_PALETTE_COLOR_INVALID")
    used = {cell for cell in cells if type(cell) is int and cell >= 0}
    if used and any(index not in range(len(palette)) for index in used):
        reasons.append("LEVEL_CELL_PALETTE_INDEX_OUT_OF_RANGE")
    if isinstance(palette, list) and len(set(normalized_local)) != len(normalized_local):
        reasons.append("LEVEL_PALETTE_DUPLICATE_COLOR")
    local_to_global: list[str | None] = []
    for local_color in normalized_local:
        matches = [cid for cid, hex_value in normalized_global.items() if hex_value == local_color]
        local_to_global.append(matches[0] if len(matches) == 1 else None)
    if any(local_to_global[index] is None for index in used if index < len(local_to_global)):
        reasons.append("LEVEL_PALETTE_NOT_CANONICAL_C01_C16")
    used_globals = [local_to_global[index] for index in sorted(used) if index < len(local_to_global)]
    if any(value is None for value in used_globals) or used_globals != sorted(used_globals):
        reasons.append("LEVEL_PALETTE_MUST_BE_USED_ONLY_ASCENDING_GLOBAL_CID")
    if isinstance(palette, list) and used != set(range(len(palette))):
        reasons.append("LEVEL_PALETTE_MUST_CONTAIN_ONLY_USED_COLORS")
    if type(width) is int and type(height) is int and width >= 20 and height >= 20:
        if artwork_cells < 200 or artwork_cells * 4 < width * height:
            reasons.append("PRODUCTION_ARTWORK_MINIMUM_NOT_MET")
    per_color: dict[int, int] = {}
    for cell in cells:
        if type(cell) is int and cell >= 0:
            per_color[cell] = per_color.get(cell, 0) + 1
    return {"reason_codes": tuple(dict.fromkeys(reasons)), "version": version, "void_cells": void_cells, "artwork_cells": artwork_cells, "per_color": per_color, "local_to_global": local_to_global}


def _validate_supply_plan(
    plan: Mapping[str, object], level: Mapping[str, object], level_result: Mapping[str, object], contract: Mapping[str, object]
) -> tuple[str, ...]:
    reasons: list[str] = []
    supply_contract = contract.get("supply")
    columns_contract = supply_contract.get("fifo_columns") if isinstance(supply_contract, Mapping) else None
    minimum = columns_contract.get("minimum") if isinstance(columns_contract, Mapping) else None
    maximum = columns_contract.get("maximum") if isinstance(columns_contract, Mapping) else None
    column_count = plan.get("columnCount")
    preview = plan.get("visiblePreviewDepth")
    columns = plan.get("columns")
    bound = plan.get("maxRobotsPerBatch")
    if plan.get("schema") != "scrubbots.level_supply_plan.v1" or type(plan.get("version")) is not int or plan.get("version") != 1:
        reasons.append("SUPPLY_PLAN_SCHEMA_OR_VERSION_INVALID")
    if plan.get("levelId") != level.get("id"):
        reasons.append("SUPPLY_PLAN_LEVEL_ID_MISMATCH")
    if type(column_count) is not int or not (type(minimum) is int and type(maximum) is int and minimum <= column_count <= maximum):
        reasons.append("FIFO_COLUMN_COUNT_OUTSIDE_CURRENT_GAME_RANGE")
    if preview != 3:
        reasons.append("FIFO_VISIBLE_PREVIEW_DEPTH_MISMATCH")
    if type(bound) is not int or bound < 1:
        reasons.append("SUPPLY_MAX_ROBOTS_PER_BATCH_INVALID")
    if not isinstance(columns, list) or type(column_count) is int and len(columns) != column_count:
        reasons.append("SUPPLY_COLUMNS_SHAPE_MISMATCH")
        columns = []
    totals: dict[str, int] = {}
    local_to_global = level_result.get("local_to_global", [])
    for column in columns:
        if not isinstance(column, list) or not column:
            reasons.append("SUPPLY_FIFO_COLUMN_EMPTY_OR_MALFORMED")
            continue
        for batch in column:
            if not isinstance(batch, Mapping):
                reasons.append("SUPPLY_BATCH_MALFORMED")
                continue
            cid, robots = batch.get("cid"), batch.get("robots")
            if not isinstance(cid, str) or cid not in local_to_global:
                reasons.append("SUPPLY_COLOR_NOT_PRESENT_IN_LEVEL_PALETTE")
                continue
            if type(robots) is not int or robots < 1 or type(bound) is not int or robots > bound:
                reasons.append("SUPPLY_BATCH_COUNT_OUTSIDE_POSITIVE_PLAN_BOUND")
                continue
            totals[cid] = totals.get(cid, 0) + robots
    expected: dict[str, int] = {}
    per_color = level_result.get("per_color", {})
    if isinstance(per_color, Mapping):
        for local_index, amount in per_color.items():
            if type(local_index) is int and local_index < len(local_to_global):
                cid = local_to_global[local_index]
                if isinstance(cid, str):
                    expected[cid] = int(amount)
    if totals != expected:
        reasons.append("SUPPLY_ARTWORK_CELL_CONSERVATION_MISMATCH")
    return tuple(dict.fromkeys(reasons))


def _normalize_hex(value: str) -> str | None:
    normalized = value.strip().upper()
    if not re.fullmatch(r"#[0-9A-F]{6}(?:[0-9A-F]{2})?", normalized):
        return None
    if len(normalized) == 7:
        normalized += "FF"
    return normalized if normalized.endswith("FF") else None


def _static_failure(contract_report: CurrentGameContractReport, *reason_codes: str) -> dict[str, object]:
    return {
        "schema": "scrubbots-current-game-static-preflight/v1",
        "disposition": "STATIC_CONTRACT_REJECTED",
        "compatible": False,
        "reason_codes": list(reason_codes),
        "game_commit": contract_report.commit,
        "source_sha256": dict(contract_report.source_sha256),
        "runtime_executed": False,
        "solver_invocations": 0,
    }


def _static_failure_from_missing(reason: str) -> dict[str, object]:
    return {
        "schema": "scrubbots-current-game-static-preflight/v1",
        "disposition": CurrentGameContractDisposition.CURRENT_GAME_UNVERIFIED.value,
        "compatible": False,
        "reason_codes": [reason],
        "game_commit": None,
        "source_sha256": {},
        "runtime_executed": False,
        "solver_invocations": 0,
    }


def _parse_contract(source_bytes: Mapping[str, bytes]) -> tuple[dict[str, object], tuple[str, ...]]:
    gameplay = _decode(source_bytes, "docs/01_GAMEPLAY_SPEC.md")
    level_spec = _decode(source_bytes, "docs/03_LEVEL_DATA_SPEC.md")
    level_data = _decode(source_bytes, "scripts/data/level_data.gd")
    level_loader = _decode(source_bytes, "scripts/data/level_loader.gd")
    supply_loader = _decode(source_bytes, "scripts/gameplay/supply/supply_plan_loader.gd")
    proof_state = _decode(source_bytes, "scripts/gameplay/solver/proof_state.gd")
    difficulty = _decode(source_bytes, "scripts/difficulty/level_difficulty_analyzer_v1.gd")
    palette_doc = json.loads(_decode(source_bytes, "data/palettes/scrubbots_palette_v3.json"))
    palette_entries = palette_doc["colors"]

    v1 = _gd_constant(level_data, "FORMAT_VERSION")
    v2 = _gd_constant(level_data, "FORMAT_VERSION_VOID")
    void_value = _gd_constant(level_data, "VOID_CELL")
    minimum_columns = _gd_constant(supply_loader, "MIN_COLUMNS")
    maximum_columns = _gd_constant(supply_loader, "MAX_COLUMNS")
    preview_depth = _gd_constant(supply_loader, "VISIBLE_PREVIEW_DEPTH")
    palette_ids = tuple(item.get("id") for item in palette_entries if isinstance(item, Mapping))
    palette_colors = {
        str(item["id"]): str(item["hex"]).upper()
        for item in palette_entries
        if isinstance(item, Mapping) and isinstance(item.get("id"), str) and isinstance(item.get("hex"), str)
    }

    checks = {
        "level_data_versions": v1 == 1 and v2 == 2,
        "void_encoding": void_value == -1 and "FORMAT_VERSION_VOID" in level_data and "version == FORMAT_VERSION_VOID" in level_data,
        "production_dimensions": bool(re.search(r"width:\s*20\.\.59", level_spec) and re.search(r"height:\s*20\.\.59", level_spec) and "rectangular boards allowed" in level_spec),
        "gameplay_dimensions_agree": "20..59" in gameplay,
        "palette_authority": palette_doc.get("schema") == "scrubbots-global-palette/v3" and palette_ids == tuple(f"C{i:02d}" for i in range(1, 17)),
        "fifo_columns": minimum_columns == 3 and maximum_columns == 5 and "3, 4 or 5 FIFO columns" in supply_loader,
        "preview_depth": preview_depth == 3,
        "artwork_conservation": "Supply conservation" in level_spec and "artwork cells only" in level_spec and "get_artwork_cell_count()" in difficulty,
        "void_runtime_semantics": "VOID cells (ADR-030) start CLEARED" in proof_state and "func is_void(index: int) -> bool:" in level_data,
        "level_loader_validation": "LevelValidator" in level_loader and "load_from_text" in level_loader,
    }
    contract = {
        "level_data": {"versions": [v1, v2], "void_version": v2, "void_value": void_value},
        "production_dimensions": {"minimum": 20, "maximum": 59, "rectangular": True},
        "global_palette_ids": list(palette_ids),
        "global_palette_hex": palette_colors,
        "supply": {"fifo_columns": {"minimum": minimum_columns, "maximum": maximum_columns}, "visible_preview_depth": preview_depth},
        "conservation_basis": "NON_VOID_ARTWORK_CELLS",
        "checks": checks,
    }
    failed = tuple(f"CONTRACT_FIELD_MISMATCH:{key}" for key, passed in checks.items() if not passed)
    return contract, failed


def _decode(source_bytes: Mapping[str, bytes], path: str) -> str:
    return source_bytes[path].decode("utf-8")


def _gd_constant(source: str, name: str) -> int:
    match = re.search(rf"(?m)^\s*const\s+{re.escape(name)}(?:\s*:\s*[A-Za-z_][A-Za-z0-9_]*)?\s*(?::=|=)\s*(-?\d+)\b", source)
    if match is None:
        raise ValueError(f"missing source constant {name}")
    return int(match.group(1))


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and _GIT_SHA.fullmatch(value) is not None


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _report(
    disposition: CurrentGameContractDisposition,
    *reason_codes: str,
    repository: str | None = None,
    branch: str | None = None,
    commit: str | None = None,
    source_sha256: Mapping[str, str] | None = None,
    contract: Mapping[str, object] | None = None,
) -> CurrentGameContractReport:
    return CurrentGameContractReport(
        disposition=disposition,
        compatible=disposition is CurrentGameContractDisposition.CURRENT_SOURCE_COMPATIBLE,
        repository=repository,
        branch=branch,
        commit=commit,
        source_sha256=dict(source_sha256 or {}),
        reason_codes=tuple(reason_codes),
        contract=contract,
    )


__all__ = [
    "CONTRACT_VERSION",
    "GAME_REPOSITORY",
    "REQUIRED_SOURCE_PATHS",
    "CurrentGameContractDisposition",
    "CurrentGameContractReport",
    "evaluate_current_game_contract",
    "preflight_level_supply_bytes",
    "preflight_json_snapshot",
    "current_main_replay_bridge",
]
