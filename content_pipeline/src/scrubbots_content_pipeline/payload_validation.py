"""Strict, side-effect-free validation for current remote declarative payloads."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .content_boundary import ContentDisposition, classify_content

PAYLOAD_VALIDATION_VERSION = "1.0"
MAX_PAYLOAD_BYTES = 1_048_576
MAX_NESTING_DEPTH = 32
MAX_COLLECTION_ITEMS = 65_536
MAX_STRING_CHARACTERS = 8_192
MAX_LEVEL_DIMENSION = 256


class PayloadReasonCode(StrEnum):
    VALID_PAYLOAD = "VALID_PAYLOAD"
    INVALID_DESCRIPTOR = "INVALID_DESCRIPTOR"
    INVALID_UTF8 = "INVALID_UTF8"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
    MALFORMED_JSON = "MALFORMED_JSON"
    DUPLICATE_KEY = "DUPLICATE_KEY"
    NON_FINITE_NUMBER = "NON_FINITE_NUMBER"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    WRONG_TOP_LEVEL_TYPE = "WRONG_TOP_LEVEL_TYPE"
    UNKNOWN_PAYLOAD_FIELD = "UNKNOWN_PAYLOAD_FIELD"
    EXECUTABLE_CONTENT = "EXECUTABLE_CONTENT"
    CONTRACT_MISMATCH = "CONTRACT_MISMATCH"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    DESCRIPTOR_MISMATCH = "DESCRIPTOR_MISMATCH"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"


@dataclass(frozen=True, slots=True)
class PayloadValidationResult:
    validation_version: str
    accepted: bool
    reason_code: PayloadReasonCode

    def to_dict(self) -> dict[str, object]:
        return {
            "validation_version": self.validation_version,
            "accepted": self.accepted,
            "reason_code": self.reason_code.value,
        }


def serialize_payload_result(result: PayloadValidationResult) -> str:
    """Serialize a result using a stable representation."""
    return json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":")) + "\n"


class _DuplicateKeyError(ValueError):
    pass


class _NonFiniteNumberError(ValueError):
    pass


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise _NonFiniteNumberError(value)


def _safe_tree(value: object, depth: int = 0) -> bool:
    if depth > MAX_NESTING_DEPTH:
        return False
    if isinstance(value, str):
        return len(value) <= MAX_STRING_CHARACTERS
    if isinstance(value, Mapping):
        return len(value) <= MAX_COLLECTION_ITEMS and all(
            isinstance(key, str) and len(key) <= MAX_STRING_CHARACTERS and _safe_tree(item, depth + 1)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return len(value) <= MAX_COLLECTION_ITEMS and all(_safe_tree(item, depth + 1) for item in value)
    return value is None or type(value) in {bool, int} or (type(value) is float and math.isfinite(value))


_EXECUTABLE_KEY = re.compile(
    r"(?i)(?:script|expression|bytecode|plugin|addon|autoload|native.?code|module.?path|shader|resource|command|process|network|file.?operation|eval|exec)"
)
_EXECUTABLE_VALUE = re.compile(
    r"(?i)(?:\b(?:eval|exec|compile|__import__|load|preload)\s*\(|(?:res|user)://|"
    r"\$\{|\{\{.*\}\}|\.(?:gd|py|pyc|cs|js|exe|dll|so|dylib|pyd|wasm|jar|class|tscn|tres|res|scn|shader|gdshader)\b)"
)


def _contains_executable_surface(value: object) -> bool:
    if isinstance(value, Mapping):
        return any(_EXECUTABLE_KEY.search(key) or _contains_executable_surface(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_executable_surface(item) for item in value)
    return isinstance(value, str) and bool(_EXECUTABLE_VALUE.search(value))


def _keys_are(value: Mapping[str, Any], required: set[str], optional: set[str] | frozenset[str] = frozenset()) -> bool:
    keys = set(value)
    return required <= keys and not keys - required - optional


_LEVEL_FIELDS = {"version", "id", "name", "difficulty", "width", "height", "palette", "cells"}


def _valid_level(value: Mapping[str, Any]) -> bool:
    if not _keys_are(value, _LEVEL_FIELDS):
        return False
    width, height, palette, cells = value["width"], value["height"], value["palette"], value["cells"]
    return (
        type(value["version"]) is int and value["version"] == 1
        and isinstance(value["id"], str) and bool(value["id"])
        and isinstance(value["name"], str) and bool(value["name"])
        and isinstance(value["difficulty"], str) and bool(value["difficulty"])
        and type(width) is int and 1 <= width <= MAX_LEVEL_DIMENSION
        and type(height) is int and 1 <= height <= MAX_LEVEL_DIMENSION
        and isinstance(palette, list) and 1 <= len(palette) <= 256
        and all(isinstance(color, str) and bool(color) for color in palette)
        and len(set(palette)) == len(palette)
        and isinstance(cells, list) and len(cells) == width * height
        and all(isinstance(cell, str) and cell in palette for cell in cells)
    )


_SUPPLY_FIELDS = {
    "schema", "version", "levelId", "ownerInput", "ownerInputSha256", "columnCount",
    "visiblePreviewDepth", "maxRobotsPerBatch", "intendedColumnClicks", "columns",
}


def _valid_supply_plan(value: Mapping[str, Any]) -> bool:
    if not _keys_are(value, _SUPPLY_FIELDS):
        return False
    count, columns = value["columnCount"], value["columns"]
    if not (
        value["schema"] == "scrubbots.level_supply_plan.v1"
        and type(value["version"]) is int and value["version"] == 1
        and isinstance(value["levelId"], str) and bool(value["levelId"])
        and isinstance(value["ownerInput"], str) and bool(value["ownerInput"])
        and isinstance(value["ownerInputSha256"], str) and re.fullmatch(r"[a-f0-9]{64}", value["ownerInputSha256"])
        and type(count) is int and count in {3, 4, 5}
        and type(value["visiblePreviewDepth"]) is int and value["visiblePreviewDepth"] == 3
        and type(value["maxRobotsPerBatch"]) is int and value["maxRobotsPerBatch"] > 0
        and isinstance(value["intendedColumnClicks"], list) and bool(value["intendedColumnClicks"])
        and all(type(index) is int and 0 <= index < count for index in value["intendedColumnClicks"])
        and isinstance(columns, list) and len(columns) == count
    ):
        return False
    for column in columns:
        if not isinstance(column, list) or not column:
            return False
        for batch in column:
            if not isinstance(batch, Mapping) or not _keys_are(batch, {"batchId", "cid", "robots"}):
                return False
            if not (
                isinstance(batch["batchId"], str) and bool(batch["batchId"])
                and isinstance(batch["cid"], str) and bool(batch["cid"])
                and type(batch["robots"]) is int and batch["robots"] > 0
            ):
                return False
    return True


_METADATA_FIELDS = {
    "schema", "version", "builderVersion", "id", "width", "height", "cellCount", "difficulty",
    "challengeScore", "columnCount", "visiblePreviewDepth", "sourceCandidateId", "sourceArtworkSha256",
    "sourceGridHash", "sourceLineage", "pipelineRunId", "loadCheck", "progression", "fileDigests",
    "challengeVector", "sessionLoad", "dominantProfile", "frustrationRisk", "official_difficulty_v1",
    "noveltySignature",
}


def _valid_metadata(value: Mapping[str, Any]) -> bool:
    required = {"schema", "version", "builderVersion", "id", "width", "height", "cellCount", "difficulty", "columnCount", "visiblePreviewDepth", "fileDigests"}
    return (
        _keys_are(value, required, _METADATA_FIELDS - required)
        and value["schema"] == "scrubbots.level.metadata.v1"
        and type(value["version"]) is int and value["version"] == 1
        and isinstance(value["builderVersion"], str) and bool(value["builderVersion"])
        and isinstance(value["id"], str) and bool(value["id"])
        and type(value["width"]) is int and 1 <= value["width"] <= MAX_LEVEL_DIMENSION
        and type(value["height"]) is int and 1 <= value["height"] <= MAX_LEVEL_DIMENSION
        and type(value["cellCount"]) is int and value["cellCount"] == value["width"] * value["height"]
        and isinstance(value["difficulty"], str)
        and type(value["columnCount"]) is int and value["columnCount"] in {3, 4, 5}
        and type(value["visiblePreviewDepth"]) is int and value["visiblePreviewDepth"] == 3
        and isinstance(value["fileDigests"], Mapping)
    )


def _result(accepted: bool, reason: PayloadReasonCode) -> PayloadValidationResult:
    return PayloadValidationResult(PAYLOAD_VALIDATION_VERSION, accepted, reason)


def validate_remote_payload(descriptor: object, payload: object) -> PayloadValidationResult:
    """Validate payload bytes/data against an already eligible descriptor.

    Bytes are preferred and are digest-bound exactly as provided. Parsed data is
    rejected when the descriptor carries a digest because byte provenance cannot
    be established. The validator never performs I/O or imports payload content.
    """
    classification = classify_content(descriptor)
    if classification.disposition is not ContentDisposition.REMOTE_DECLARATIVE or not isinstance(descriptor, Mapping):
        return _result(False, PayloadReasonCode.INVALID_DESCRIPTOR)
    attrs = descriptor.get("attributes")
    if not isinstance(attrs, Mapping):
        return _result(False, PayloadReasonCode.INVALID_DESCRIPTOR)
    digest_field = "supply_plan_sha256" if descriptor.get("content_type") == "supply_plan_data" else "payload_sha256"
    expected_digest = attrs.get(digest_field)

    raw: bytes | None = None
    if isinstance(payload, (bytes, bytearray, memoryview)):
        raw = bytes(payload)
        if len(raw) > MAX_PAYLOAD_BYTES:
            return _result(False, PayloadReasonCode.PAYLOAD_TOO_LARGE)
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return _result(False, PayloadReasonCode.INVALID_UTF8)
        try:
            parsed = json.loads(text, object_pairs_hook=_object_without_duplicates, parse_constant=_reject_constant)
        except _DuplicateKeyError:
            return _result(False, PayloadReasonCode.DUPLICATE_KEY)
        except _NonFiniteNumberError:
            return _result(False, PayloadReasonCode.NON_FINITE_NUMBER)
        except (json.JSONDecodeError, RecursionError, ValueError):
            return _result(False, PayloadReasonCode.MALFORMED_JSON)
    else:
        if isinstance(expected_digest, str):
            return _result(False, PayloadReasonCode.DIGEST_MISMATCH)
        parsed = payload

    if not _safe_tree(parsed):
        return _result(False, PayloadReasonCode.NON_FINITE_NUMBER if _has_nonfinite(parsed) else PayloadReasonCode.LIMIT_EXCEEDED)
    if not isinstance(parsed, Mapping):
        return _result(False, PayloadReasonCode.WRONG_TOP_LEVEL_TYPE)
    if _contains_executable_surface(parsed):
        return _result(False, PayloadReasonCode.EXECUTABLE_CONTENT)

    content_type = descriptor.get("content_type")
    contract = descriptor.get("payload_contract")
    if not isinstance(contract, Mapping):
        return _result(False, PayloadReasonCode.INVALID_DESCRIPTOR)
    if content_type == "level_data":
        valid = _valid_level(parsed)
        contract_ok = contract == {"authority": "Level Data Specification", "version": 1} and parsed.get("version") == 1
        allowed = _LEVEL_FIELDS
    elif content_type == "supply_plan_data":
        valid = _valid_supply_plan(parsed)
        contract_ok = contract == {"schema": "scrubbots.level_supply_plan.v1", "version": 1} and parsed.get("schema") == contract.get("schema") and parsed.get("version") == contract.get("version")
        allowed = _SUPPLY_FIELDS
    elif content_type == "approved_metadata":
        valid = _valid_metadata(parsed)
        contract_ok = contract == {"schema": "scrubbots.level.metadata.v1", "version": 1} and parsed.get("schema") == contract.get("schema") and parsed.get("version") == contract.get("version")
        allowed = _METADATA_FIELDS
    else:
        return _result(False, PayloadReasonCode.CONTRACT_MISMATCH)
    if not contract_ok:
        return _result(False, PayloadReasonCode.CONTRACT_MISMATCH)
    if not valid:
        return _result(False, PayloadReasonCode.UNKNOWN_PAYLOAD_FIELD if set(parsed) - allowed else PayloadReasonCode.INVALID_PAYLOAD)

    identity_key = "levelId" if content_type == "supply_plan_data" else "id"
    if parsed.get(identity_key) != attrs.get("level_id"):
        return _result(False, PayloadReasonCode.DESCRIPTOR_MISMATCH)
    if content_type in {"level_data", "approved_metadata"} and (parsed.get("width") != attrs.get("width") or parsed.get("height") != attrs.get("height")):
        return _result(False, PayloadReasonCode.DESCRIPTOR_MISMATCH)
    if content_type in {"supply_plan_data", "approved_metadata"} and (parsed.get("columnCount") != attrs.get("columns") or parsed.get("visiblePreviewDepth") != attrs.get("preview_depth")):
        return _result(False, PayloadReasonCode.DESCRIPTOR_MISMATCH)
    if raw is not None and isinstance(expected_digest, str) and hashlib.sha256(raw).hexdigest() != expected_digest:
        return _result(False, PayloadReasonCode.DIGEST_MISMATCH)
    return _result(True, PayloadReasonCode.VALID_PAYLOAD)


def _has_nonfinite(value: object) -> bool:
    if type(value) is float:
        return not math.isfinite(value)
    if isinstance(value, Mapping):
        return any(_has_nonfinite(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_nonfinite(item) for item in value)
    return False


__all__ = [
    "MAX_COLLECTION_ITEMS", "MAX_LEVEL_DIMENSION", "MAX_NESTING_DEPTH", "MAX_PAYLOAD_BYTES",
    "MAX_STRING_CHARACTERS", "PAYLOAD_VALIDATION_VERSION", "PayloadReasonCode",
    "PayloadValidationResult", "serialize_payload_result", "validate_remote_payload",
]
