"""Immutable data contract for the canonical SCRUBBOTS ProofState shape.

This module intentionally contains no gameplay transitions.  It validates and
serializes a compact state envelope so a future canonical bridge can transport
ProofState data without copying the main-game mechanics into Factory Python.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Mapping, Sequence


COMPACT_STATE_SCHEMA = "scrubbots-compact-solver-state"
COMPACT_STATE_VERSION = 1
AUTHORITY_SCHEMA = "scrubbots-proof-state-authority"
AUTHORITY_VERSION = 1
CANONICAL_GAMEPLAY_REPOSITORY = "https://github.com/Sekiph82/Scrubbots"
PROOF_STATE_SOURCE_PATH = "scripts/gameplay/solver/proof_state.gd"
AUTHORITY_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SOURCE_SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")

# These values are copied from the inspected canonical ProofState and its
# directly referenced M23/M24 data engines. They describe shape, not behavior.
ACTIVE_BYTE = 1
CLEARED_BYTE = 0
SLOT_COUNT = 5
MIN_COLUMN_COUNT = 3
MAX_COLUMN_COUNT = 5
MIN_PREVIEW_DEPTH = 3
MAX_PREVIEW_DEPTH = 4
MIN_PALETTE_SIZE = -1
PROOF_STATE_FIELDS = (
    "level",
    "active",
    "supply",
    "slots",
    "next_seq",
    "column_count",
    "preview_depth",
    "palette_size",
)
SUPPLY_ENTRY_FIELDS = ("id", "color", "count")
OCCUPIED_SLOT_FIELDS = ("batch_id", "color", "remaining", "seq", "state")
SLOT_STATES = ("ACTIVE", "WAITING")


class CompactStateContractError(ValueError):
    """Raised when a compact state envelope is malformed."""


class AuthorityVerificationDisposition(str, Enum):
    VERIFIED = "VERIFIED"
    UNAVAILABLE = "UNAVAILABLE"
    MISMATCH = "MISMATCH"
    ERROR = "ERROR"


def _canonical_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _bounded_reason(value: object) -> str:
    text = str(value).strip() or "unspecified compact-state error"
    return text[:512]


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise CompactStateContractError(f"{label} must be a non-empty string")
    return value.strip()


def _exact_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise CompactStateContractError(f"{label} must be an integer")
    return int(value)


def _closed_mapping(value: object, fields: Sequence[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise CompactStateContractError(f"{label} must be an object")
    if set(value) != set(fields):
        raise CompactStateContractError(f"{label} has unknown or missing fields")
    return value


def _digest(value: Mapping[str, object]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class SolverStateAuthority:
    """Declared external authority identity; declaration is not verification."""

    repository: str
    commit_sha: str
    proof_state_source_path: str = PROOF_STATE_SOURCE_PATH
    authority_version: int = AUTHORITY_VERSION

    def __post_init__(self) -> None:
        repository = _text(self.repository, "authority repository")
        commit_sha = _text(self.commit_sha, "authority commit SHA")
        source_path = _text(self.proof_state_source_path, "ProofState source path")
        version = _exact_int(self.authority_version, "authority version")
        if repository != CANONICAL_GAMEPLAY_REPOSITORY:
            raise CompactStateContractError("authority repository is not the canonical SCRUBBOTS repository")
        if AUTHORITY_SHA_PATTERN.fullmatch(commit_sha) is None:
            raise CompactStateContractError("authority commit SHA must be a lowercase 40-character Git SHA")
        if source_path != PROOF_STATE_SOURCE_PATH or source_path.startswith(("/", "\\")) or ".." in Path(source_path).parts:
            raise CompactStateContractError("ProofState source path is not the locked relative path")
        if version != AUTHORITY_VERSION:
            raise CompactStateContractError("unsupported authority identity version")
        object.__setattr__(self, "repository", repository)
        object.__setattr__(self, "commit_sha", commit_sha)
        object.__setattr__(self, "proof_state_source_path", source_path)
        object.__setattr__(self, "authority_version", version)

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": AUTHORITY_SCHEMA,
            "version": self.authority_version,
            "repository": self.repository,
            "commit_sha": self.commit_sha,
            "proof_state_source_path": self.proof_state_source_path,
        }

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class AuthorityVerification:
    """Read-only checkout verification result, never gameplay state."""

    disposition: AuthorityVerificationDisposition
    declared_commit_sha: str
    observed_commit_sha: str | None
    proof_state_source_present: bool
    reason: str

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": "scrubbots-proof-state-authority-verification",
            "version": 1,
            "disposition": self.disposition.value,
            "declared_commit_sha": self.declared_commit_sha,
            "observed_commit_sha": self.observed_commit_sha,
            "proof_state_source_present": self.proof_state_source_present,
            "reason": self.reason,
        }


def verify_authority_checkout(authority: SolverStateAuthority, checkout_path: str | os.PathLike[str]) -> AuthorityVerification:
    """Verify a declared SHA against an explicit local checkout without writes.

    This is capability evidence for a future bridge, not a gameplay operation.
    The path is supplied by the caller and is never persisted into state
    identity. Network access is neither requested nor used.
    """

    try:
        if not isinstance(authority, SolverStateAuthority):
            raise CompactStateContractError("authority must be a SolverStateAuthority")
        raw_path = os.fspath(checkout_path)
        if type(raw_path) is not str or not raw_path.strip():
            raise CompactStateContractError("checkout path must be a non-empty path")
        checkout = Path(raw_path).resolve()
        if not checkout.is_absolute() or not checkout.is_dir():
            return AuthorityVerification(
                AuthorityVerificationDisposition.UNAVAILABLE,
                authority.commit_sha,
                None,
                False,
                "canonical gameplay checkout does not exist",
            )
        proof_path = checkout / authority.proof_state_source_path
        if not proof_path.is_file():
            return AuthorityVerification(
                AuthorityVerificationDisposition.UNAVAILABLE,
                authority.commit_sha,
                None,
                False,
                "declared ProofState source is missing from the checkout",
            )
        try:
            process = subprocess.run(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
        except FileNotFoundError:
            return AuthorityVerification(
                AuthorityVerificationDisposition.UNAVAILABLE,
                authority.commit_sha,
                None,
                True,
                "git executable is unavailable for checkout identity verification",
            )
        except subprocess.TimeoutExpired:
            return AuthorityVerification(
                AuthorityVerificationDisposition.ERROR,
                authority.commit_sha,
                None,
                True,
                "checkout identity verification timed out",
            )
        observed = process.stdout.strip().lower() if process.returncode == 0 else None
        if observed is None or AUTHORITY_SHA_PATTERN.fullmatch(observed) is None:
            return AuthorityVerification(
                AuthorityVerificationDisposition.UNAVAILABLE,
                authority.commit_sha,
                None,
                True,
                "checkout HEAD could not be resolved without trusting a caller-provided SHA",
            )
        if observed != authority.commit_sha:
            return AuthorityVerification(
                AuthorityVerificationDisposition.MISMATCH,
                authority.commit_sha,
                observed,
                True,
                "checkout HEAD does not match the declared canonical authority SHA",
            )
        return AuthorityVerification(
            AuthorityVerificationDisposition.VERIFIED,
            authority.commit_sha,
            observed,
            True,
            "checkout HEAD and declared ProofState authority match",
        )
    except (CompactStateContractError, OSError, RuntimeError) as exc:
        declared = authority.commit_sha if isinstance(authority, SolverStateAuthority) else ""
        return AuthorityVerification(
            AuthorityVerificationDisposition.ERROR,
            declared,
            None,
            False,
            _bounded_reason(exc),
        )


@dataclass(frozen=True, slots=True)
class LevelIdentity:
    """Immutable LevelData identity and mask-shape metadata, not LevelData itself."""

    source_sha256: str
    level_id: str
    width: int
    height: int
    cell_count: int

    def __post_init__(self) -> None:
        source_sha256 = _text(self.source_sha256, "LevelData source SHA-256")
        level_id = _text(self.level_id, "level ID")
        width = _exact_int(self.width, "level width")
        height = _exact_int(self.height, "level height")
        cell_count = _exact_int(self.cell_count, "level cell count")
        if SOURCE_SHA_PATTERN.fullmatch(source_sha256) is None:
            raise CompactStateContractError("LevelData source SHA-256 is malformed")
        if width <= 0 or height <= 0 or cell_count != width * height:
            raise CompactStateContractError("LevelData dimensions/cell count are inconsistent")
        object.__setattr__(self, "source_sha256", source_sha256)
        object.__setattr__(self, "level_id", level_id)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)
        object.__setattr__(self, "cell_count", cell_count)

    @classmethod
    def from_source_bytes(cls, source_bytes: bytes | bytearray | memoryview, *, level_id: str, width: int, height: int) -> "LevelIdentity":
        if not isinstance(source_bytes, (bytes, bytearray, memoryview)):
            raise CompactStateContractError("LevelData source bytes must be bytes")
        copied = bytes(source_bytes)
        return cls(hashlib.sha256(copied).hexdigest(), level_id, width, height, width * height)

    def canonical_dict(self) -> dict[str, object]:
        return {
            "source_sha256": self.source_sha256,
            "level_id": self.level_id,
            "width": self.width,
            "height": self.height,
            "cell_count": self.cell_count,
        }


@dataclass(frozen=True, slots=True)
class SupplyBatch:
    """Exact canonical ProofState FIFO batch entry."""

    batch_id: str
    color: int
    count: int

    def __post_init__(self) -> None:
        batch_id = _text(self.batch_id, "supply batch id")
        color = _exact_int(self.color, "supply color")
        count = _exact_int(self.count, "supply count")
        if color < 0 or count <= 0:
            raise CompactStateContractError("supply color/count is outside the canonical range")
        object.__setattr__(self, "batch_id", batch_id)
        object.__setattr__(self, "color", color)
        object.__setattr__(self, "count", count)

    def canonical_dict(self) -> dict[str, object]:
        return {"id": self.batch_id, "color": self.color, "count": self.count}


@dataclass(frozen=True, slots=True)
class OccupiedSlot:
    """Exact occupied ProofState slot entry; EMPTY is represented by None."""

    batch_id: str
    color: int
    remaining: int
    seq: int
    state: str

    def __post_init__(self) -> None:
        batch_id = _text(self.batch_id, "slot batch id")
        color = _exact_int(self.color, "slot color")
        remaining = _exact_int(self.remaining, "slot remaining")
        seq = _exact_int(self.seq, "slot sequence")
        state = _text(self.state, "slot state")
        if color < 0 or remaining < 0 or seq < 0 or state not in SLOT_STATES:
            raise CompactStateContractError("occupied slot scalar is outside the canonical range")
        object.__setattr__(self, "batch_id", batch_id)
        object.__setattr__(self, "color", color)
        object.__setattr__(self, "remaining", remaining)
        object.__setattr__(self, "seq", seq)
        object.__setattr__(self, "state", state)

    def canonical_dict(self) -> dict[str, object]:
        return {
            "batch_id": self.batch_id,
            "color": self.color,
            "remaining": self.remaining,
            "seq": self.seq,
            "state": self.state,
        }


@dataclass(frozen=True, slots=True)
class CompactSolverState:
    """Versioned, immutable ProofState data envelope with no transition API."""

    authority: SolverStateAuthority
    level: LevelIdentity
    active_mask: bytes
    supply: tuple[tuple[SupplyBatch, ...], ...]
    slots: tuple[OccupiedSlot | None, ...]
    next_seq: int
    column_count: int
    preview_depth: int
    palette_size: int

    def __post_init__(self) -> None:
        if not isinstance(self.authority, SolverStateAuthority):
            raise CompactStateContractError("state authority is malformed")
        if not isinstance(self.level, LevelIdentity):
            raise CompactStateContractError("state LevelData identity is malformed")
        if not isinstance(self.active_mask, (bytes, bytearray, memoryview)):
            raise CompactStateContractError("active mask must be bytes")
        mask = bytes(self.active_mask)
        if len(mask) != self.level.cell_count or any(value not in (ACTIVE_BYTE, CLEARED_BYTE) for value in mask):
            raise CompactStateContractError("active mask is not a row-major ACTIVE/CLEARED mask of exact cell count")
        next_seq = _exact_int(self.next_seq, "next placement sequence")
        column_count = _exact_int(self.column_count, "column count")
        preview_depth = _exact_int(self.preview_depth, "preview depth")
        palette_size = _exact_int(self.palette_size, "palette size")
        if next_seq < 1 or not MIN_COLUMN_COUNT <= column_count <= MAX_COLUMN_COUNT:
            raise CompactStateContractError("state sequencing/column count is outside the canonical range")
        if not MIN_PREVIEW_DEPTH <= preview_depth <= MAX_PREVIEW_DEPTH or palette_size < MIN_PALETTE_SIZE:
            raise CompactStateContractError("state preview/palette configuration is outside the canonical range")
        if not isinstance(self.supply, tuple) or len(self.supply) != column_count:
            raise CompactStateContractError("supply column count does not match state configuration")
        if not isinstance(self.slots, tuple) or len(self.slots) != SLOT_COUNT:
            raise CompactStateContractError("slot count does not match canonical ProofState")

        identifiers: set[str] = set()
        frozen_supply: list[tuple[SupplyBatch, ...]] = []
        for column in self.supply:
            if not isinstance(column, tuple):
                raise CompactStateContractError("supply columns must be immutable tuples")
            frozen_column: list[SupplyBatch] = []
            for batch in column:
                if not isinstance(batch, SupplyBatch):
                    raise CompactStateContractError("supply entry is not a SupplyBatch")
                if palette_size >= 0 and batch.color >= palette_size:
                    raise CompactStateContractError("supply color is outside the state palette size")
                if batch.batch_id in identifiers:
                    raise CompactStateContractError("batch identity is duplicated in state")
                identifiers.add(batch.batch_id)
                frozen_column.append(batch)
            frozen_supply.append(tuple(frozen_column))

        frozen_slots: list[OccupiedSlot | None] = []
        for slot in self.slots:
            if slot is not None:
                if not isinstance(slot, OccupiedSlot):
                    raise CompactStateContractError("occupied slot entry is malformed")
                if palette_size >= 0 and slot.color >= palette_size:
                    raise CompactStateContractError("slot color is outside the state palette size")
                if slot.batch_id in identifiers:
                    raise CompactStateContractError("slot batch identity is duplicated in state")
                identifiers.add(slot.batch_id)
            frozen_slots.append(slot)

        object.__setattr__(self, "active_mask", mask)
        object.__setattr__(self, "supply", tuple(frozen_supply))
        object.__setattr__(self, "slots", tuple(frozen_slots))
        object.__setattr__(self, "next_seq", next_seq)
        object.__setattr__(self, "column_count", column_count)
        object.__setattr__(self, "preview_depth", preview_depth)
        object.__setattr__(self, "palette_size", palette_size)

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": COMPACT_STATE_SCHEMA,
            "version": COMPACT_STATE_VERSION,
            "authority": self.authority.canonical_dict(),
            "level": self.level.canonical_dict(),
            "active_mask_hex": self.active_mask.hex(),
            "supply": [[batch.canonical_dict() for batch in column] for column in self.supply],
            "slots": [slot.canonical_dict() if slot is not None else None for slot in self.slots],
            "next_seq": self.next_seq,
            "column_count": self.column_count,
            "preview_depth": self.preview_depth,
            "palette_size": self.palette_size,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        """Return the Factory envelope digest, never ProofState.canonical_key()."""

        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "CompactSolverState":
        fields = ("schema", "version", "authority", "level", "active_mask_hex", "supply", "slots", "next_seq", "column_count", "preview_depth", "palette_size")
        value = _closed_mapping(payload, fields, "compact solver state")
        if value["schema"] != COMPACT_STATE_SCHEMA or type(value["version"]) is not int or value["version"] != COMPACT_STATE_VERSION:
            raise CompactStateContractError("compact solver state schema/version is unsupported")
        authority_data = _closed_mapping(value["authority"], ("schema", "version", "repository", "commit_sha", "proof_state_source_path"), "authority")
        if authority_data["schema"] != AUTHORITY_SCHEMA:
            raise CompactStateContractError("authority schema is unsupported")
        authority = SolverStateAuthority(
            repository=authority_data["repository"],
            commit_sha=authority_data["commit_sha"],
            proof_state_source_path=authority_data["proof_state_source_path"],
            authority_version=authority_data["version"],
        )
        level_data = _closed_mapping(value["level"], ("source_sha256", "level_id", "width", "height", "cell_count"), "level identity")
        level = LevelIdentity(**level_data)
        mask_hex = value["active_mask_hex"]
        if type(mask_hex) is not str or len(mask_hex) % 2 != 0:
            raise CompactStateContractError("active mask hex is malformed")
        try:
            mask = bytes.fromhex(mask_hex)
        except ValueError as exc:
            raise CompactStateContractError("active mask hex is malformed") from exc

        supply_data = value["supply"]
        if not isinstance(supply_data, list):
            raise CompactStateContractError("supply must be an array of columns")
        supply: list[tuple[SupplyBatch, ...]] = []
        for column in supply_data:
            if not isinstance(column, list):
                raise CompactStateContractError("supply column must be an array")
            supply.append(
                tuple(
                    SupplyBatch(
                        batch_id=_closed_mapping(batch, SUPPLY_ENTRY_FIELDS, "supply batch")["id"],
                        color=_closed_mapping(batch, SUPPLY_ENTRY_FIELDS, "supply batch")["color"],
                        count=_closed_mapping(batch, SUPPLY_ENTRY_FIELDS, "supply batch")["count"],
                    )
                    for batch in column
                )
            )

        slots_data = value["slots"]
        if not isinstance(slots_data, list):
            raise CompactStateContractError("slots must be an array")
        slots: list[OccupiedSlot | None] = []
        for slot in slots_data:
            if slot is None:
                slots.append(None)
                continue
            slot_value = _closed_mapping(slot, OCCUPIED_SLOT_FIELDS, "occupied slot")
            slots.append(OccupiedSlot(batch_id=slot_value["batch_id"], color=slot_value["color"], remaining=slot_value["remaining"], seq=slot_value["seq"], state=slot_value["state"]))
        return cls(
            authority=authority,
            level=level,
            active_mask=mask,
            supply=tuple(supply),
            slots=tuple(slots),
            next_seq=value["next_seq"],
            column_count=value["column_count"],
            preview_depth=value["preview_depth"],
            palette_size=value["palette_size"],
        )


__all__ = [
    "ACTIVE_BYTE",
    "AUTHORITY_SCHEMA",
    "AUTHORITY_SHA_PATTERN",
    "AUTHORITY_VERSION",
    "AuthorityVerification",
    "AuthorityVerificationDisposition",
    "CLEARED_BYTE",
    "COMPACT_STATE_SCHEMA",
    "COMPACT_STATE_VERSION",
    "CompactSolverState",
    "CompactStateContractError",
    "LevelIdentity",
    "MAX_COLUMN_COUNT",
    "MAX_PREVIEW_DEPTH",
    "MIN_COLUMN_COUNT",
    "MIN_PALETTE_SIZE",
    "MIN_PREVIEW_DEPTH",
    "OCCUPIED_SLOT_FIELDS",
    "PROOF_STATE_FIELDS",
    "PROOF_STATE_SOURCE_PATH",
    "SLOT_COUNT",
    "SLOT_STATES",
    "SolverStateAuthority",
    "SUPPLY_ENTRY_FIELDS",
    "SupplyBatch",
    "OccupiedSlot",
    "verify_authority_checkout",
]
