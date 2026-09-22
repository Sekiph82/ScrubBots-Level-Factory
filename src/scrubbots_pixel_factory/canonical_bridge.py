"""Strict external adapter for the canonical ScrubBots headless authority.

The adapter transports envelopes and invokes a caller-supplied runner only
after read-only authority verification. It contains no gameplay operations.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Mapping

from .compact_solver_state import (
    CANONICAL_PROOF_STATE_SOURCE_SHA256,
    PROOF_STATE_SOURCE_PATH,
    SolverStateAuthority,
    verify_authority_checkout,
    verify_authority_source_contract,
)
from .simulation_boundary import REQUIRED_CANONICAL_SOURCE_PATHS


CANONICAL_BRIDGE_SCHEMA = "scrubbots-canonical-headless-bridge"
CANONICAL_BRIDGE_VERSION = 1
CANONICAL_BRIDGE_RUNNER_VERSION = "external-godot-runner-v1"
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class CanonicalBridgeError(ValueError):
    """Raised when a canonical bridge envelope or configuration is malformed."""


class CanonicalBridgeDisposition(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


def _canonical_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise CanonicalBridgeError(f"{label} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class CanonicalBridgeRequest:
    authority: SolverStateAuthority
    operation: str
    request_payload: bytes
    state_digest: str
    level_data_source_sha256: str
    bridge_version: str = CANONICAL_BRIDGE_RUNNER_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.authority, SolverStateAuthority):
            raise CanonicalBridgeError("request authority is malformed")
        operation = _text(self.operation, "operation")
        if not isinstance(self.request_payload, (bytes, bytearray, memoryview)):
            raise CanonicalBridgeError("request payload must be bytes")
        state_digest = _text(self.state_digest, "state digest")
        source_sha256 = _text(self.level_data_source_sha256, "LevelData source SHA-256")
        if not _SHA256_PATTERN.fullmatch(state_digest) or not _SHA256_PATTERN.fullmatch(source_sha256):
            raise CanonicalBridgeError("request identity digest is malformed")
        object.__setattr__(self, "operation", operation)
        object.__setattr__(self, "request_payload", bytes(self.request_payload))
        object.__setattr__(self, "state_digest", state_digest)
        object.__setattr__(self, "level_data_source_sha256", source_sha256)
        object.__setattr__(self, "bridge_version", _text(self.bridge_version, "bridge version"))

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": CANONICAL_BRIDGE_SCHEMA + ".request",
            "version": CANONICAL_BRIDGE_VERSION,
            "bridge_version": self.bridge_version,
            "authority": self.authority.canonical_dict(),
            "operation": self.operation,
            "state_digest": self.state_digest,
            "level_data_source_sha256": self.level_data_source_sha256,
            "request_payload_sha256": _sha256(self.request_payload),
        }

    def digest(self) -> str:
        return _sha256(_canonical_bytes(self.canonical_dict()))

    def runner_payload(self) -> dict[str, object]:
        return {**self.canonical_dict(), "request_payload_base64": base64.b64encode(self.request_payload).decode("ascii"), "request_digest": self.digest()}


@dataclass(frozen=True, slots=True)
class CanonicalBridgeResponse:
    disposition: CanonicalBridgeDisposition
    request_digest: str | None
    authority_sha: str | None
    source_sha256: str | None
    operation: str | None
    result: Mapping[str, object] | None
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, CanonicalBridgeDisposition):
            raise CanonicalBridgeError("bridge response disposition is malformed")
        if type(self.reason) is not str or not self.reason.strip():
            raise CanonicalBridgeError("bridge response reason is required")
        if self.disposition is CanonicalBridgeDisposition.AVAILABLE and (self.result is None or self.request_digest is None or self.authority_sha is None or self.source_sha256 is None or self.operation is None):
            raise CanonicalBridgeError("AVAILABLE bridge response is missing identity or result")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": CANONICAL_BRIDGE_SCHEMA + ".response",
            "version": CANONICAL_BRIDGE_VERSION,
            "disposition": self.disposition.value,
            "request_digest": self.request_digest,
            "authority_sha": self.authority_sha,
            "source_sha256": self.source_sha256,
            "operation": self.operation,
            "result": dict(self.result) if self.result is not None else None,
            "reason": self.reason[:512],
        }


@dataclass(frozen=True, slots=True)
class CanonicalBridgeConfiguration:
    checkout_path: str | None = None
    runner_path: str | None = None
    godot_executable: str = "godot_console.exe"
    timeout_seconds: float = 15.0

    def __post_init__(self) -> None:
        for name in ("checkout_path", "runner_path"):
            value = getattr(self, name)
            if value is not None:
                path = Path(_text(value, name)).resolve()
                if not path.is_absolute():
                    raise CanonicalBridgeError(f"{name} must be absolute")
                object.__setattr__(self, name, str(path))
        executable = _text(self.godot_executable, "Godot executable")
        if type(self.timeout_seconds) not in {int, float} or isinstance(self.timeout_seconds, bool) or self.timeout_seconds <= 0 or self.timeout_seconds > 120:
            raise CanonicalBridgeError("bridge timeout must be between 0 and 120 seconds")
        object.__setattr__(self, "godot_executable", executable)

    def resolved_checkout(self) -> Path | None:
        raw = self.checkout_path or os.environ.get("SCRUBBOTS_CANONICAL_CHECKOUT")
        return Path(raw).resolve() if raw else None


class CanonicalHeadlessBridge:
    """Invoke only a verified, caller-supplied canonical Godot runner."""

    def __init__(self, configuration: CanonicalBridgeConfiguration | None = None) -> None:
        self._configuration = configuration or CanonicalBridgeConfiguration()

    @property
    def configuration(self) -> CanonicalBridgeConfiguration:
        return self._configuration

    def capability(self, authority: SolverStateAuthority | object) -> CanonicalBridgeResponse:
        if not isinstance(authority, SolverStateAuthority):
            return CanonicalBridgeResponse(CanonicalBridgeDisposition.ERROR, None, None, None, None, None, "authority is malformed")
        verified, reason = self._verify(authority)
        if not verified:
            return CanonicalBridgeResponse(CanonicalBridgeDisposition.UNAVAILABLE, None, authority.commit_sha, None, None, None, reason)
        if self._configuration.runner_path is None:
            return CanonicalBridgeResponse(CanonicalBridgeDisposition.UNAVAILABLE, None, authority.commit_sha, CANONICAL_PROOF_STATE_SOURCE_SHA256, None, None, "canonical checkout is verified but no external read-only Godot bridge runner is configured")
        if not Path(self._configuration.runner_path).is_file():
            return CanonicalBridgeResponse(CanonicalBridgeDisposition.UNAVAILABLE, None, authority.commit_sha, CANONICAL_PROOF_STATE_SOURCE_SHA256, None, None, "configured external bridge runner does not exist")
        return CanonicalBridgeResponse(CanonicalBridgeDisposition.AVAILABLE, "capability", authority.commit_sha, CANONICAL_PROOF_STATE_SOURCE_SHA256, "CAPABILITY", {}, "canonical checkout and external runner are configured and verified")

    def invoke(self, request: CanonicalBridgeRequest | object) -> CanonicalBridgeResponse:
        if not isinstance(request, CanonicalBridgeRequest):
            return CanonicalBridgeResponse(CanonicalBridgeDisposition.ERROR, None, None, None, None, None, "request is malformed")
        verified, reason = self._verify(request.authority)
        if not verified:
            return CanonicalBridgeResponse(CanonicalBridgeDisposition.UNAVAILABLE, request.digest(), request.authority.commit_sha, None, request.operation, None, reason)
        runner = self._configuration.runner_path
        checkout = self._configuration.resolved_checkout()
        if runner is None or checkout is None:
            return CanonicalBridgeResponse(CanonicalBridgeDisposition.UNAVAILABLE, request.digest(), request.authority.commit_sha, CANONICAL_PROOF_STATE_SOURCE_SHA256, request.operation, None, "canonical headless bridge runner or checkout is not configured")
        runner_file = Path(runner).resolve()
        try:
            runner_file.relative_to(checkout)
        except ValueError:
            pass
        else:
            return CanonicalBridgeResponse(CanonicalBridgeDisposition.ERROR, request.digest(), request.authority.commit_sha, CANONICAL_PROOF_STATE_SOURCE_SHA256, request.operation, None, "external runner must not live inside the canonical checkout")
        with tempfile.TemporaryDirectory(prefix="scrubbots-canonical-bridge-") as temp_dir:
            temp = Path(temp_dir)
            request_path = temp / "request.json"
            response_path = temp / "response.json"
            request_path.write_bytes(_canonical_bytes(request.runner_payload()))
            command = [self._configuration.godot_executable, "--headless", "--path", str(checkout), "--script", str(runner_file), "--", "--request", str(request_path), "--response", str(response_path)]
            try:
                completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=self._configuration.timeout_seconds)
            except (OSError, subprocess.TimeoutExpired) as exc:
                return CanonicalBridgeResponse(CanonicalBridgeDisposition.ERROR, request.digest(), request.authority.commit_sha, CANONICAL_PROOF_STATE_SOURCE_SHA256, request.operation, None, f"canonical bridge invocation failed: {type(exc).__name__}")
            if completed.returncode != 0 or not response_path.is_file():
                return CanonicalBridgeResponse(CanonicalBridgeDisposition.ERROR, request.digest(), request.authority.commit_sha, CANONICAL_PROOF_STATE_SOURCE_SHA256, request.operation, None, "canonical bridge runner did not return a response envelope")
            try:
                raw = json.loads(response_path.read_text(encoding="utf-8"))
                response = self._parse_response(raw, request)
            except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError, CanonicalBridgeError) as exc:
                return CanonicalBridgeResponse(CanonicalBridgeDisposition.ERROR, request.digest(), request.authority.commit_sha, CANONICAL_PROOF_STATE_SOURCE_SHA256, request.operation, None, f"canonical bridge response rejected: {type(exc).__name__}")
            return response

    def _verify(self, authority: SolverStateAuthority) -> tuple[bool, str]:
        checkout = self._configuration.resolved_checkout()
        if checkout is None:
            return False, "canonical gameplay checkout is not configured; canonical adapter is UNAVAILABLE"
        verification = verify_authority_checkout(authority, checkout)
        if verification.disposition.value != "VERIFIED":
            return False, verification.reason
        for relative in REQUIRED_CANONICAL_SOURCE_PATHS:
            if not (checkout / relative).is_file():
                return False, f"required canonical source is missing: {relative}"
        source_verification = verify_authority_source_contract(authority, (checkout / PROOF_STATE_SOURCE_PATH).read_bytes())
        if source_verification.disposition.value != "VERIFIED" or source_verification.source_sha256 != CANONICAL_PROOF_STATE_SOURCE_SHA256:
            return False, source_verification.reason
        return True, "canonical authority and source contract verified"

    def _parse_response(self, raw: object, request: CanonicalBridgeRequest) -> CanonicalBridgeResponse:
        if not isinstance(raw, Mapping) or raw.get("schema") != CANONICAL_BRIDGE_SCHEMA + ".response" or raw.get("version") != CANONICAL_BRIDGE_VERSION:
            raise CanonicalBridgeError("response schema/version mismatch")
        disposition = CanonicalBridgeDisposition(raw["disposition"])
        response = CanonicalBridgeResponse(disposition, raw.get("request_digest"), raw.get("authority_sha"), raw.get("source_sha256"), raw.get("operation"), raw.get("result"), _text(raw.get("reason"), "response reason"))
        if disposition is CanonicalBridgeDisposition.AVAILABLE and (response.request_digest != request.digest() or response.authority_sha != request.authority.commit_sha or response.source_sha256 != CANONICAL_PROOF_STATE_SOURCE_SHA256 or response.operation != request.operation):
            raise CanonicalBridgeError("response identity does not match the verified request")
        return response


__all__ = [
    "CANONICAL_BRIDGE_RUNNER_VERSION",
    "CANONICAL_BRIDGE_SCHEMA",
    "CANONICAL_BRIDGE_VERSION",
    "CanonicalBridgeConfiguration",
    "CanonicalBridgeDisposition",
    "CanonicalBridgeError",
    "CanonicalBridgeRequest",
    "CanonicalBridgeResponse",
    "CanonicalHeadlessBridge",
]
