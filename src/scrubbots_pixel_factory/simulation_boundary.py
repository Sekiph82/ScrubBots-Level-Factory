"""Pure/headless boundary for the canonical SCRUBBOTS gameplay proof kernel.

This module deliberately transports opaque canonical input bytes.  It does not
parse LevelData, reconstruct BoardState, select moves, or implement gameplay.
The main-game repository remains the only mechanics authority.  C001 exposes a
truthful capability result until a separately configured, stable headless
bridge can invoke that authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Mapping


SIMULATION_BOUNDARY_SCHEMA = "scrubbots-headless-puzzle-simulation-boundary"
SIMULATION_BOUNDARY_VERSION = 1
CANONICAL_GAMEPLAY_REPOSITORY = "https://github.com/Sekiph82/Scrubbots"
CANONICAL_CHECKOUT_ENVIRONMENT = "SCRUBBOTS_CANONICAL_CHECKOUT"
BOUNDARY_BRIDGE_VERSION = "canonical-proof-kernel-bridge-v1"
AUTHORITY_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_CANONICAL_SOURCE_PATHS = (
    "docs/01_GAMEPLAY_SPEC.md",
    "docs/03_LEVEL_DATA_SPEC.md",
    "scripts/gameplay/board/board_state.gd",
    "scripts/gameplay/solver/proof_state.gd",
    "scripts/gameplay/solver/proof_kernel.gd",
    "scripts/gameplay/solver/solvability_solver.gd",
)


class BoundaryContractError(ValueError):
    """Raised when the boundary envelope is malformed."""


class BoundaryDisposition(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


def _canonical_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _bounded_reason(value: object) -> str:
    text = str(value).strip() or "unspecified boundary error"
    return text[:512]


def _nonblank(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise BoundaryContractError(f"{label} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class AuthorityDescriptor:
    """Identity of the external gameplay authority inspected by a request."""

    repository: str
    commit_sha: str
    bridge_version: str = BOUNDARY_BRIDGE_VERSION
    source_paths: tuple[str, ...] = REQUIRED_CANONICAL_SOURCE_PATHS

    def __post_init__(self) -> None:
        repository = _nonblank(self.repository, "authority repository")
        commit_sha = _nonblank(self.commit_sha, "authority commit SHA")
        bridge_version = _nonblank(self.bridge_version, "bridge version")
        if repository != CANONICAL_GAMEPLAY_REPOSITORY:
            raise BoundaryContractError("authority repository is not the canonical SCRUBBOTS repository")
        if AUTHORITY_SHA_PATTERN.fullmatch(commit_sha) is None:
            raise BoundaryContractError("authority commit SHA must be a lowercase 40-character Git SHA")
        if tuple(self.source_paths) != REQUIRED_CANONICAL_SOURCE_PATHS:
            raise BoundaryContractError("authority source paths do not match the locked proof-kernel inspection set")
        object.__setattr__(self, "repository", repository)
        object.__setattr__(self, "commit_sha", commit_sha)
        object.__setattr__(self, "bridge_version", bridge_version)
        object.__setattr__(self, "source_paths", REQUIRED_CANONICAL_SOURCE_PATHS)

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": "scrubbots-canonical-gameplay-authority",
            "version": 1,
            "repository": self.repository,
            "commit_sha": self.commit_sha,
            "bridge_version": self.bridge_version,
            "source_paths": list(self.source_paths),
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class BridgeConfiguration:
    """Read-only capability discovery inputs; no command is executed in C001."""

    checkout_path: str | None = None
    environment_variable: str = CANONICAL_CHECKOUT_ENVIRONMENT

    def __post_init__(self) -> None:
        if self.checkout_path is not None:
            path = _nonblank(self.checkout_path, "canonical checkout path")
            if not Path(path).is_absolute():
                raise BoundaryContractError("canonical checkout path must be absolute")
            object.__setattr__(self, "checkout_path", path)
        variable = _nonblank(self.environment_variable, "checkout environment variable")
        if re.fullmatch(r"[A-Z][A-Z0-9_]*", variable) is None:
            raise BoundaryContractError("checkout environment variable is malformed")
        object.__setattr__(self, "environment_variable", variable)

    def configured_checkout(self) -> Path | None:
        raw = self.checkout_path or os.environ.get(self.environment_variable)
        return Path(raw).resolve() if raw else None


@dataclass(frozen=True, slots=True)
class SimulationRequest:
    """Versioned request envelope carrying immutable opaque canonical input."""

    authority: AuthorityDescriptor
    canonical_input_bytes: bytes
    input_schema: str = "opaque-canonical-level-data"

    def __post_init__(self) -> None:
        if not isinstance(self.authority, AuthorityDescriptor):
            raise BoundaryContractError("request authority must be an AuthorityDescriptor")
        if not isinstance(self.canonical_input_bytes, (bytes, bytearray, memoryview)):
            raise BoundaryContractError("canonical input must be bytes")
        input_schema = _nonblank(self.input_schema, "input schema")
        object.__setattr__(self, "canonical_input_bytes", bytes(self.canonical_input_bytes))
        object.__setattr__(self, "input_schema", input_schema)

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": SIMULATION_BOUNDARY_SCHEMA + ".request",
            "version": SIMULATION_BOUNDARY_VERSION,
            "authority": self.authority.canonical_dict(),
            "input_schema": self.input_schema,
            "canonical_input_sha256": hashlib.sha256(self.canonical_input_bytes).hexdigest(),
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class BoundaryCapability:
    schema: str
    version: int
    disposition: BoundaryDisposition
    authority: AuthorityDescriptor | None
    authority_digest: str | None
    bridge_version: str
    reason: str

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "version": self.version,
            "disposition": self.disposition.value,
            "authority": self.authority.canonical_dict() if self.authority is not None else None,
            "authority_digest": self.authority_digest,
            "bridge_version": self.bridge_version,
            "reason": self.reason,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class SimulationResult:
    schema: str
    version: int
    disposition: BoundaryDisposition
    request_digest: str | None
    authority: AuthorityDescriptor | None
    authority_digest: str | None
    bridge_version: str
    reason: str
    canonical_disposition: str | None = None

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "version": self.version,
            "disposition": self.disposition.value,
            "request_digest": self.request_digest,
            "authority": self.authority.canonical_dict() if self.authority is not None else None,
            "authority_digest": self.authority_digest,
            "bridge_version": self.bridge_version,
            "reason": self.reason,
            "canonical_disposition": self.canonical_disposition,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class CanonicalGameplayBridge:
    """Discover the canonical bridge without inventing a gameplay fallback.

    C001 intentionally has no executable bridge command.  Presence of the
    canonical Godot source files is evidence of authority, not evidence that a
    safe, stable headless invocation path exists.
    """

    def __init__(self, configuration: BridgeConfiguration | None = None) -> None:
        self._configuration = configuration or BridgeConfiguration()

    @property
    def configuration(self) -> BridgeConfiguration:
        return self._configuration

    def capability(self, authority: AuthorityDescriptor | object) -> BoundaryCapability:
        try:
            if not isinstance(authority, AuthorityDescriptor):
                raise BoundaryContractError("authority must be an AuthorityDescriptor")
            checkout = self._configuration.configured_checkout()
        except (BoundaryContractError, OSError, RuntimeError) as exc:
            return _capability_error(authority if isinstance(authority, AuthorityDescriptor) else None, exc)

        if checkout is None:
            return _capability_unavailable(
                authority,
                "canonical gameplay checkout is not configured; no proof-kernel bridge was invoked",
            )
        if not checkout.is_dir():
            return _capability_unavailable(authority, "configured canonical gameplay checkout does not exist")
        missing = [path for path in authority.source_paths if not (checkout / path).is_file()]
        if missing:
            return _capability_unavailable(
                authority,
                "canonical gameplay checkout is missing required authority source: " + missing[0],
            )
        return _capability_unavailable(
            authority,
            "canonical gameplay sources are present, but no stable configured headless proof-kernel bridge exists; source files are not an invocation path",
        )

    def simulate(self, request: SimulationRequest | object) -> SimulationResult:
        if not isinstance(request, SimulationRequest):
            return _simulation_error(None, "request must be a SimulationRequest")
        capability = self.capability(request.authority)
        if capability.disposition is BoundaryDisposition.ERROR:
            return _simulation_error(request, capability.reason)
        return SimulationResult(
            schema=SIMULATION_BOUNDARY_SCHEMA + ".result",
            version=SIMULATION_BOUNDARY_VERSION,
            disposition=capability.disposition,
            request_digest=request.digest(),
            authority=request.authority,
            authority_digest=request.authority.digest(),
            bridge_version=request.authority.bridge_version,
            reason=capability.reason,
        )


def _capability_unavailable(authority: AuthorityDescriptor, reason: object) -> BoundaryCapability:
    return BoundaryCapability(
        schema=SIMULATION_BOUNDARY_SCHEMA + ".capability",
        version=SIMULATION_BOUNDARY_VERSION,
        disposition=BoundaryDisposition.UNAVAILABLE,
        authority=authority,
        authority_digest=authority.digest(),
        bridge_version=authority.bridge_version,
        reason=_bounded_reason(reason),
    )


def _capability_error(authority: AuthorityDescriptor | None, reason: object) -> BoundaryCapability:
    return BoundaryCapability(
        schema=SIMULATION_BOUNDARY_SCHEMA + ".capability",
        version=SIMULATION_BOUNDARY_VERSION,
        disposition=BoundaryDisposition.ERROR,
        authority=authority,
        authority_digest=authority.digest() if authority is not None else None,
        bridge_version=authority.bridge_version if authority is not None else BOUNDARY_BRIDGE_VERSION,
        reason=_bounded_reason(reason),
    )


def _simulation_error(request: SimulationRequest | None, reason: object) -> SimulationResult:
    authority = request.authority if request is not None else None
    return SimulationResult(
        schema=SIMULATION_BOUNDARY_SCHEMA + ".result",
        version=SIMULATION_BOUNDARY_VERSION,
        disposition=BoundaryDisposition.ERROR,
        request_digest=request.digest() if request is not None else None,
        authority=authority,
        authority_digest=authority.digest() if authority is not None else None,
        bridge_version=authority.bridge_version if authority is not None else BOUNDARY_BRIDGE_VERSION,
        reason=_bounded_reason(reason),
    )


__all__ = [
    "AUTHORITY_SHA_PATTERN",
    "AuthorityDescriptor",
    "BOUNDARY_BRIDGE_VERSION",
    "BoundaryCapability",
    "BoundaryContractError",
    "BoundaryDisposition",
    "BridgeConfiguration",
    "CANONICAL_CHECKOUT_ENVIRONMENT",
    "CANONICAL_GAMEPLAY_REPOSITORY",
    "CanonicalGameplayBridge",
    "REQUIRED_CANONICAL_SOURCE_PATHS",
    "SIMULATION_BOUNDARY_SCHEMA",
    "SIMULATION_BOUNDARY_VERSION",
    "SimulationRequest",
    "SimulationResult",
]
