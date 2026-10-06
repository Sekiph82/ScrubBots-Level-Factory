"""Strict external UTF-8 JSON bytes parser for Content Manifest V1."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from enum import Enum

from .manifest_v1 import CONTENT_MANIFEST_SCHEMA, CONTENT_MANIFEST_SCHEMA_VERSION, ContentManifestError, ContentManifestV1


MAX_MANIFEST_BYTES = 1_048_576
MAX_MANIFEST_NESTING_DEPTH = 32
MAX_MANIFEST_COLLECTION_ITEMS = 4_096
MAX_MANIFEST_STRING_LENGTH = 16_384


class ManifestParseReasonCode(str, Enum):
    INPUT_NOT_BYTES = "INPUT_NOT_BYTES"
    MANIFEST_TOO_LARGE = "MANIFEST_TOO_LARGE"
    INVALID_UTF8 = "INVALID_UTF8"
    INVALID_JSON = "INVALID_JSON"
    DUPLICATE_JSON_KEY = "DUPLICATE_JSON_KEY"
    NONFINITE_NUMBER = "NONFINITE_NUMBER"
    NESTING_TOO_DEEP = "NESTING_TOO_DEEP"
    COLLECTION_TOO_LARGE = "COLLECTION_TOO_LARGE"
    STRING_TOO_LONG = "STRING_TOO_LONG"
    ROOT_NOT_OBJECT = "ROOT_NOT_OBJECT"
    INVALID_ROOT_FIELDS = "INVALID_ROOT_FIELDS"
    UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"
    UNSUPPORTED_SCHEMA_VERSION = "UNSUPPORTED_SCHEMA_VERSION"
    INVALID_MANIFEST = "INVALID_MANIFEST"


class ManifestParseError(ValueError):
    """Raised when external manifest bytes fail strict parsing or V1 validation."""

    def __init__(self, reason_code: ManifestParseReasonCode) -> None:
        super().__init__(reason_code.value)
        self.reason_code = reason_code


@dataclass(frozen=True, slots=True)
class _RejectedJson(Exception):
    reason_code: ManifestParseReasonCode


def _object_from_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _RejectedJson(ManifestParseReasonCode.DUPLICATE_JSON_KEY)
        result[key] = value
    return result


def _reject_constant(_value: str) -> object:
    raise _RejectedJson(ManifestParseReasonCode.NONFINITE_NUMBER)


def _parse_finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise _RejectedJson(ManifestParseReasonCode.NONFINITE_NUMBER)
    return parsed


def _check_depth(text: str) -> None:
    depth = 0
    in_string = False
    escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > MAX_MANIFEST_NESTING_DEPTH:
                raise ManifestParseError(ManifestParseReasonCode.NESTING_TOO_DEEP)
        elif char in "]}":
            depth -= 1


def _check_value_limits(value: object) -> None:
    if isinstance(value, str):
        if len(value) > MAX_MANIFEST_STRING_LENGTH:
            raise ManifestParseError(ManifestParseReasonCode.STRING_TOO_LONG)
        return
    if isinstance(value, list):
        if len(value) > MAX_MANIFEST_COLLECTION_ITEMS:
            raise ManifestParseError(ManifestParseReasonCode.COLLECTION_TOO_LARGE)
        for item in value:
            _check_value_limits(item)
        return
    if isinstance(value, dict):
        if len(value) > MAX_MANIFEST_COLLECTION_ITEMS:
            raise ManifestParseError(ManifestParseReasonCode.COLLECTION_TOO_LARGE)
        for key, item in value.items():
            _check_value_limits(key)
            _check_value_limits(item)


def parse_content_manifest_v1(raw: bytes) -> ContentManifestV1:
    """Parse untrusted bytes through strict JSON limits before constructing the immutable model."""
    if type(raw) is not bytes:
        raise ManifestParseError(ManifestParseReasonCode.INPUT_NOT_BYTES)
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ManifestParseError(ManifestParseReasonCode.MANIFEST_TOO_LARGE)
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ManifestParseError(ManifestParseReasonCode.INVALID_UTF8) from exc
    _check_depth(text)
    try:
        value = json.loads(
            text,
            object_pairs_hook=_object_from_pairs,
            parse_constant=_reject_constant,
            parse_float=_parse_finite_float,
        )
    except _RejectedJson as exc:
        raise ManifestParseError(exc.reason_code) from exc
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise ManifestParseError(ManifestParseReasonCode.INVALID_JSON) from exc
    if not isinstance(value, dict):
        raise ManifestParseError(ManifestParseReasonCode.ROOT_NOT_OBJECT)
    _check_value_limits(value)
    required = {
        "schema", "schema_version", "content_version", "minimum_game_version", "disabled_levels",
        "schedules", "packs", "levels",
    }
    if set(value) != required:
        raise ManifestParseError(ManifestParseReasonCode.INVALID_ROOT_FIELDS)
    if value["schema"] != CONTENT_MANIFEST_SCHEMA:
        raise ManifestParseError(ManifestParseReasonCode.UNSUPPORTED_SCHEMA)
    if type(value["schema_version"]) is not int or value["schema_version"] != CONTENT_MANIFEST_SCHEMA_VERSION:
        raise ManifestParseError(ManifestParseReasonCode.UNSUPPORTED_SCHEMA_VERSION)
    try:
        return ContentManifestV1.from_dict(value)
    except ContentManifestError as exc:
        message = str(exc)
        if message == "unsupported manifest schema":
            reason = ManifestParseReasonCode.UNSUPPORTED_SCHEMA
        elif message == "unsupported manifest schema_version":
            reason = ManifestParseReasonCode.UNSUPPORTED_SCHEMA_VERSION
        else:
            reason = ManifestParseReasonCode.INVALID_MANIFEST
        raise ManifestParseError(reason) from exc


__all__ = [
    "MAX_MANIFEST_BYTES",
    "MAX_MANIFEST_COLLECTION_ITEMS",
    "MAX_MANIFEST_NESTING_DEPTH",
    "MAX_MANIFEST_STRING_LENGTH",
    "ManifestParseError",
    "ManifestParseReasonCode",
    "parse_content_manifest_v1",
]
