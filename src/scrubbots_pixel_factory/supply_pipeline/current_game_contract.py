"""Pure, versioned compatibility contract for caller-supplied ScrubBots source.

This module never discovers, fetches, or executes a game checkout. Callers must
provide immutable source bytes, their SHA-256 inventory, and an independently
verified current-main commit identity.
"""

from __future__ import annotations

import hashlib
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


def _parse_contract(source_bytes: Mapping[str, bytes]) -> tuple[dict[str, object], tuple[str, ...]]:
    gameplay = _decode(source_bytes, "docs/01_GAMEPLAY_SPEC.md")
    level_spec = _decode(source_bytes, "docs/03_LEVEL_DATA_SPEC.md")
    level_data = _decode(source_bytes, "scripts/data/level_data.gd")
    level_loader = _decode(source_bytes, "scripts/data/level_loader.gd")
    supply_loader = _decode(source_bytes, "scripts/gameplay/supply/supply_plan_loader.gd")
    proof_state = _decode(source_bytes, "scripts/gameplay/solver/proof_state.gd")
    difficulty = _decode(source_bytes, "scripts/difficulty/level_difficulty_analyzer_v1.gd")
    palette_doc = json.loads(_decode(source_bytes, "data/palettes/scrubbots_palette_v3.json"))

    v1 = _gd_constant(level_data, "FORMAT_VERSION")
    v2 = _gd_constant(level_data, "FORMAT_VERSION_VOID")
    void_value = _gd_constant(level_data, "VOID_CELL")
    minimum_columns = _gd_constant(supply_loader, "MIN_COLUMNS")
    maximum_columns = _gd_constant(supply_loader, "MAX_COLUMNS")
    preview_depth = _gd_constant(supply_loader, "VISIBLE_PREVIEW_DEPTH")
    palette_ids = tuple(item.get("id") for item in palette_doc["colors"] if isinstance(item, Mapping))

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
]
