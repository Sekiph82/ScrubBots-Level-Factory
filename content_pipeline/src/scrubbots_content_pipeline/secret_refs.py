"""Opaque, environment-scoped secret references and deterministic redaction."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from .config import Environment

SECRET_REFERENCE_VERSION = "1.0"
_REFERENCE_ID = re.compile(r"^ref-[A-Za-z0-9][A-Za-z0-9._-]{0,91}$")
_SECRET_FIELD = re.compile(r"(?i)(?:secret|password|api[_-]?key|access[_-]?token|refresh[_-]?token|\btoken\b|client[_-]?secret|private[_-]?key|connection[_-]?string|credential)")
_ASSIGNMENT = re.compile(r"(?i)\b(password|api[_-]?key|access[_-]?token|refresh[_-]?token|token|client[_-]?secret|private[_-]?key|connection[_-]?string)(\s*[:=]\s*)[^\s,;]+")
_URI_CREDENTIALS = re.compile(r"(?i)\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@[^/\s]+")
_PEM = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----", re.DOTALL)
_COMMON_CREDENTIAL_PATTERNS = re.compile(r"(?i)\b(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._~+/-]{12,})\b")


class SecretReferenceReasonCode(StrEnum):
    VALID_REFERENCE = "VALID_REFERENCE"
    INVALID_REFERENCE = "INVALID_REFERENCE"
    SECRET_MATERIAL_FIELD = "SECRET_MATERIAL_FIELD"
    UNKNOWN_FIELD = "UNKNOWN_FIELD"
    ENVIRONMENT_MISMATCH = "ENVIRONMENT_MISMATCH"
    UNKNOWN_ENVIRONMENT = "UNKNOWN_ENVIRONMENT"


@dataclass(frozen=True, slots=True, repr=False)
class SecretReference:
    """A non-secret pointer; the type intentionally has no value-bearing field."""

    reference_id: str
    purpose: str
    environment: Environment
    version_label: str | None = None
    reference_version: str = SECRET_REFERENCE_VERSION
    _representation_marker: str = field(default="opaque", init=False, repr=False, compare=False)

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "reference_version": self.reference_version,
            "reference_id": self.reference_id,
            "purpose": self.purpose,
            "environment": self.environment.value if isinstance(self.environment, Environment) else "unknown",
            "version_label": self.version_label,
        }
        if not isinstance(self.reference_id, str) or not _REFERENCE_ID.fullmatch(self.reference_id) or _contains_obvious_secret(self.reference_id):
            result["reference_id"] = "[INVALID]"
        if not isinstance(self.purpose, str) or not re.fullmatch(r"[a-z][a-z0-9._-]{1,63}", self.purpose) or _contains_obvious_secret(self.purpose):
            result["purpose"] = "[INVALID]"
        if isinstance(self.version_label, str) and _contains_obvious_secret(self.version_label):
            result["version_label"] = "[REDACTED]"
        return result

    def __repr__(self) -> str:
        environment = self.environment.value if isinstance(self.environment, Environment) else "unknown"
        metadata = redact_for_evidence({"purpose": self.purpose, "environment": environment, "version_label": self.version_label, "reference_version": self.reference_version})
        return f"SecretReference(reference_id=<opaque>, metadata={metadata!r})"


@dataclass(frozen=True, slots=True)
class SecretReferenceValidationResult:
    result_version: str
    accepted: bool
    reason_code: SecretReferenceReasonCode
    reference: SecretReference | None = None


def _environment(value: object) -> Environment | None:
    if isinstance(value, Environment):
        return value
    if isinstance(value, str):
        try:
            return Environment(value)
        except ValueError:
            return None
    return None


def validate_secret_reference(value: object, expected_environment: Environment | str | None = None) -> SecretReferenceValidationResult:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        return SecretReferenceValidationResult(SECRET_REFERENCE_VERSION, False, SecretReferenceReasonCode.INVALID_REFERENCE)
    secret_keys = [key for key in value if _SECRET_FIELD.search(key)]
    if secret_keys:
        return SecretReferenceValidationResult(SECRET_REFERENCE_VERSION, False, SecretReferenceReasonCode.SECRET_MATERIAL_FIELD)
    allowed = {"reference_version", "reference_id", "purpose", "environment", "version_label"}
    if set(value) - allowed:
        return SecretReferenceValidationResult(SECRET_REFERENCE_VERSION, False, SecretReferenceReasonCode.UNKNOWN_FIELD)
    if set(value) != allowed:
        return SecretReferenceValidationResult(SECRET_REFERENCE_VERSION, False, SecretReferenceReasonCode.INVALID_REFERENCE)
    env = _environment(value.get("environment"))
    if env is None:
        return SecretReferenceValidationResult(SECRET_REFERENCE_VERSION, False, SecretReferenceReasonCode.UNKNOWN_ENVIRONMENT)
    purpose = value.get("purpose")
    ref_id = value.get("reference_id")
    version = value.get("version_label")
    if (
        value.get("reference_version") != SECRET_REFERENCE_VERSION
        or not isinstance(ref_id, str)
        or not _REFERENCE_ID.fullmatch(ref_id)
        or _contains_obvious_secret(ref_id)
        or not isinstance(purpose, str)
        or not re.fullmatch(r"[a-z][a-z0-9._-]{1,63}", purpose)
        or _contains_obvious_secret(purpose)
        or (version is not None and (not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,31}", version) or _contains_obvious_secret(version)))
    ):
        return SecretReferenceValidationResult(SECRET_REFERENCE_VERSION, False, SecretReferenceReasonCode.INVALID_REFERENCE)
    expected = _environment(expected_environment) if expected_environment is not None else env
    if expected is None:
        return SecretReferenceValidationResult(SECRET_REFERENCE_VERSION, False, SecretReferenceReasonCode.UNKNOWN_ENVIRONMENT)
    if env is not expected:
        return SecretReferenceValidationResult(SECRET_REFERENCE_VERSION, False, SecretReferenceReasonCode.ENVIRONMENT_MISMATCH)
    reference = SecretReference(ref_id, purpose, env, version)
    return SecretReferenceValidationResult(SECRET_REFERENCE_VERSION, True, SecretReferenceReasonCode.VALID_REFERENCE, reference)


def _contains_obvious_secret(value: str) -> bool:
    return bool(_ASSIGNMENT.search(value) or _PEM.search(value) or _COMMON_CREDENTIAL_PATTERNS.search(value) or _URI_CREDENTIALS.search(value))


def redact_for_evidence(value: object) -> object:
    """Redact obvious secret-bearing fields and token/credential forms recursively."""
    if isinstance(value, Mapping):
        result: dict[str, object] = {}
        for key, nested in value.items():
            label = str(key)
            result[label] = "[REDACTED]" if _SECRET_FIELD.search(label) else redact_for_evidence(nested)
        return result
    if isinstance(value, (list, tuple)):
        return [redact_for_evidence(item) for item in value]
    if isinstance(value, str):
        safe = _PEM.sub("[REDACTED]", value)
        safe = _URI_CREDENTIALS.sub("[REDACTED_CONNECTION_STRING]", safe)
        safe = _ASSIGNMENT.sub(lambda match: match.group(1) + match.group(2) + "[REDACTED]", safe)
        return _COMMON_CREDENTIAL_PATTERNS.sub("[REDACTED]", safe)
    return value


def serialize_secret_reference(reference: SecretReference) -> str:
    validated = validate_secret_reference(reference.to_dict())
    if not validated.accepted or validated.reference is None:
        return json.dumps({"reference_version": SECRET_REFERENCE_VERSION, "accepted": False, "reason_code": "INVALID_REFERENCE"}, sort_keys=True, separators=(",", ":")) + "\n"
    return json.dumps(validated.reference.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


__all__ = [
    "SECRET_REFERENCE_VERSION", "SecretReference", "SecretReferenceReasonCode",
    "SecretReferenceValidationResult", "redact_for_evidence", "serialize_secret_reference",
    "validate_secret_reference",
]
