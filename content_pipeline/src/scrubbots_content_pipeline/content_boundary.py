"""Pure, fail-closed app-code versus remote-declarative-content classifier."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath


BOUNDARY_VERSION = "1.0"


class ContentDisposition(StrEnum):
    REMOTE_DECLARATIVE = "REMOTE_DECLARATIVE"
    APP_OWNED = "APP_OWNED"
    REJECTED = "REJECTED"


class ReasonCode(StrEnum):
    ALLOWLIST_MATCH = "ALLOWLIST_MATCH"
    APP_CODE_EXTENSION = "APP_CODE_EXTENSION"
    APP_OWNED_RESOURCE_TYPE = "APP_OWNED_RESOURCE_TYPE"
    PLUGIN_OR_ADDON_PATH = "PLUGIN_OR_ADDON_PATH"
    ABSOLUTE_PATH = "ABSOLUTE_PATH"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    NON_CANONICAL_PATH = "NON_CANONICAL_PATH"
    INVALID_DESCRIPTOR = "INVALID_DESCRIPTOR"
    PAYLOAD_CONTRACT_MISMATCH = "PAYLOAD_CONTRACT_MISMATCH"
    EXECUTABLE_FIELD = "EXECUTABLE_FIELD"
    EXECUTABLE_REFERENCE = "EXECUTABLE_REFERENCE"
    UNKNOWN_EXTENSION = "UNKNOWN_EXTENSION"
    UNKNOWN_CONTENT_TYPE = "UNKNOWN_CONTENT_TYPE"
    UNKNOWN_SCHEMA = "UNKNOWN_SCHEMA"
    SCHEMA_TYPE_MISMATCH = "SCHEMA_TYPE_MISMATCH"
    MEDIA_TYPE_MISMATCH = "MEDIA_TYPE_MISMATCH"
    UNKNOWN_DESCRIPTOR_FIELD = "UNKNOWN_DESCRIPTOR_FIELD"
    UNKNOWN_ATTRIBUTE_FIELD = "UNKNOWN_ATTRIBUTE_FIELD"
    INVALID_ATTRIBUTES = "INVALID_ATTRIBUTES"
    INVALID_ATTRIBUTE_VALUE = "INVALID_ATTRIBUTE_VALUE"


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    boundary_version: str
    disposition: ContentDisposition
    reason_codes: tuple[ReasonCode, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a stable JSON-ready representation of the classification."""

        return {
            "boundary_version": self.boundary_version,
            "disposition": self.disposition.value,
            "reason_codes": [reason.value for reason in self.reason_codes],
        }


def serialize_result(result: ClassificationResult) -> str:
    """Serialize a result deterministically for local reports and tests."""

    return json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":")) + "\n"


_CONTRACTS: dict[
    str,
    tuple[str, str, dict[str, str | int], frozenset[str], frozenset[str]],
] = {
    "level_data": (
        "application/vnd.scrubbots.level+json",
        "scrubbots.content-pipeline.level-data.v1",
        {"authority": "Level Data Specification", "version": 1},
        frozenset({"level_id", "payload_sha256", "width", "height"}),
        frozenset({"level_id", "payload_sha256", "width", "height"}),
    ),
    "supply_plan_data": (
        "application/vnd.scrubbots.supply-plan+json",
        "scrubbots.content-pipeline.supply-plan.v1",
        {"schema": "scrubbots.level_supply_plan.v1", "version": 1},
        frozenset({"level_id", "supply_plan_sha256", "columns", "preview_depth"}),
        frozenset({"level_id", "supply_plan_sha256", "columns", "preview_depth"}),
    ),
    "approved_metadata": (
        "application/vnd.scrubbots.approved-metadata+json",
        "scrubbots.content-pipeline.publisher-metadata.v1",
        {"schema": "scrubbots.level.metadata.v1", "version": 1},
        frozenset({"level_id", "payload_sha256", "width", "height", "columns", "preview_depth"}),
        frozenset({"level_id", "payload_sha256", "width", "height", "columns", "preview_depth"}),
    ),
}
_DESCRIPTOR_CONTRACT_TO_TYPE = {
    descriptor_contract_id: content_type
    for content_type, (_, descriptor_contract_id, _, _, _) in _CONTRACTS.items()
}
_ROOT_FIELDS = frozenset(
    {
        "boundary_version",
        "content_type",
        "logical_path",
        "media_type",
        "descriptor_contract_id",
        "payload_contract",
        "attributes",
    }
)
_APP_CODE_EXTENSIONS = frozenset(
    {
        ".gd", ".py", ".pyc", ".pyo", ".cs", ".js", ".mjs", ".c", ".cc", ".cpp",
        ".h", ".hpp", ".exe", ".dll", ".so", ".dylib", ".pyd", ".wasm", ".jar",
        ".class", ".sh", ".bat", ".cmd", ".ps1",
    }
)
_APP_RESOURCE_EXTENSIONS = frozenset({".tscn", ".tres", ".res", ".scn", ".shader", ".gdshader"})
_EXECUTABLE_KEY_PARTS = (
    "script", "expression", "bytecode", "eval", "exec", "plugin", "addon", "shader",
    "resource", "autoload", "nativecode", "modulepath",
)
_EXECUTABLE_COMPOUND_MARKERS = ("nativecode", "modulepath")
_EXECUTABLE_REFERENCE = re.compile(
    r"(?i)(?:\b(?:eval|exec|__import__|compile|load|preload)\s*\(|"
    r"(?:res|user)://|\$\{|\{\{.*\}\}|"
    r"\.(?:gd|py|pyc|cs|js|exe|dll|so|dylib|pyd|wasm|jar|class|tscn|tres|res|scn|shader|gdshader)\b)"
)
_LEVEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


def _result(disposition: ContentDisposition, reason: ReasonCode) -> ClassificationResult:
    return ClassificationResult(BOUNDARY_VERSION, disposition, (reason,))


def _path_reason(path: str) -> ReasonCode | None:
    windows_path = PureWindowsPath(path)
    if path.startswith("/") or path.startswith("\\\\") or windows_path.is_absolute() or windows_path.drive:
        return ReasonCode.ABSOLUTE_PATH
    if re.search(r"(?:^|[/\\])\.\.(?:[/\\]|$)", path):
        return ReasonCode.PATH_TRAVERSAL
    if "\\" in path or "//" in path or any(part == "." for part in path.split("/")):
        return ReasonCode.NON_CANONICAL_PATH
    if not path or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*)*", path):
        return ReasonCode.NON_CANONICAL_PATH
    return None


def _has_executable_marker(value: object, seen: set[int] | None = None) -> ReasonCode | None:
    if seen is None:
        seen = set()
    if isinstance(value, str):
        return ReasonCode.EXECUTABLE_REFERENCE if _EXECUTABLE_REFERENCE.search(value) else None
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in seen:
            return ReasonCode.INVALID_DESCRIPTOR
        seen.add(identity)
        for key, nested in value.items():
            if isinstance(key, str):
                split_camel_case = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
                key_tokens = set(re.findall(r"[a-z0-9]+", split_camel_case.casefold()))
                compact_key = re.sub(r"[^a-z0-9]", "", key.casefold())
                if (key_tokens & (set(_EXECUTABLE_KEY_PARTS) - set(_EXECUTABLE_COMPOUND_MARKERS))) or any(
                    marker in compact_key for marker in _EXECUTABLE_COMPOUND_MARKERS
                ):
                    return ReasonCode.EXECUTABLE_FIELD
            marker = _has_executable_marker(nested, seen)
            if marker is not None:
                return marker
        return None
    if isinstance(value, (list, tuple)):
        identity = id(value)
        if identity in seen:
            return ReasonCode.INVALID_DESCRIPTOR
        seen.add(identity)
        for nested in value:
            marker = _has_executable_marker(nested, seen)
            if marker is not None:
                return marker
    return None


def _attributes_are_valid(content_type: str, attributes: object) -> ReasonCode | None:
    if not isinstance(attributes, Mapping):
        return ReasonCode.INVALID_ATTRIBUTES
    _, _, _, required, allowed = _CONTRACTS[content_type]
    if not all(isinstance(key, str) for key in attributes):
        return ReasonCode.INVALID_ATTRIBUTES
    keys = frozenset(attributes)
    if keys - allowed:
        return ReasonCode.UNKNOWN_ATTRIBUTE_FIELD
    if required - keys:
        return ReasonCode.INVALID_ATTRIBUTES

    level_id = attributes.get("level_id")
    if not isinstance(level_id, str) or not _LEVEL_ID.fullmatch(level_id):
        return ReasonCode.INVALID_ATTRIBUTE_VALUE
    if content_type == "level_data":
        digest = attributes.get("payload_sha256")
        width = attributes.get("width")
        height = attributes.get("height")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
        if type(width) is not int or not 1 <= width <= 256:
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
        if type(height) is not int or not 1 <= height <= 256:
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
    elif content_type == "supply_plan_data":
        digest = attributes.get("supply_plan_sha256")
        columns = attributes.get("columns")
        preview_depth = attributes.get("preview_depth")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
        if type(columns) is not int or columns not in {3, 4, 5}:
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
        if type(preview_depth) is not int or preview_depth != 3:
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
    else:
        digest = attributes.get("payload_sha256")
        width = attributes.get("width")
        height = attributes.get("height")
        columns = attributes.get("columns")
        preview_depth = attributes.get("preview_depth")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
        if type(width) is not int or not 1 <= width <= 256:
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
        if type(height) is not int or not 1 <= height <= 256:
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
        if type(columns) is not int or columns not in {3, 4, 5}:
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
        if type(preview_depth) is not int or preview_depth != 3:
            return ReasonCode.INVALID_ATTRIBUTE_VALUE
    return None


def classify_content(descriptor: object) -> ClassificationResult:
    """Classify a JSON-like logical descriptor without reading or running payloads.

    Only the three versioned data contracts in this module are remotely eligible.
    Known app-code/plugin/resource paths are classified APP_OWNED. Malformed,
    unsupported, unsafe, or executable-bearing descriptors are REJECTED.
    """

    if not isinstance(descriptor, Mapping):
        return _result(ContentDisposition.REJECTED, ReasonCode.INVALID_DESCRIPTOR)

    marker_source = {key: value for key, value in descriptor.items() if key != "logical_path"}
    marker = _has_executable_marker(marker_source)
    if marker is not None:
        return _result(ContentDisposition.REJECTED, marker)

    path = descriptor.get("logical_path")
    if not isinstance(path, str):
        return _result(ContentDisposition.REJECTED, ReasonCode.INVALID_DESCRIPTOR)
    path_reason = _path_reason(path)
    if path_reason is not None:
        return _result(ContentDisposition.REJECTED, path_reason)

    path_parts = PurePosixPath(path).parts
    if any(part.casefold() in {"addons", "plugins"} for part in path_parts):
        return _result(ContentDisposition.APP_OWNED, ReasonCode.PLUGIN_OR_ADDON_PATH)

    extension = PurePosixPath(path).suffix.casefold()
    if extension in _APP_CODE_EXTENSIONS:
        return _result(ContentDisposition.APP_OWNED, ReasonCode.APP_CODE_EXTENSION)
    if extension in _APP_RESOURCE_EXTENSIONS:
        return _result(ContentDisposition.APP_OWNED, ReasonCode.APP_OWNED_RESOURCE_TYPE)
    if extension != ".json":
        return _result(ContentDisposition.REJECTED, ReasonCode.UNKNOWN_EXTENSION)

    if descriptor.get("boundary_version") != BOUNDARY_VERSION:
        return _result(ContentDisposition.REJECTED, ReasonCode.INVALID_DESCRIPTOR)
    if not all(isinstance(key, str) for key in descriptor):
        return _result(ContentDisposition.REJECTED, ReasonCode.INVALID_DESCRIPTOR)
    root_keys = frozenset(descriptor)
    if root_keys - _ROOT_FIELDS:
        return _result(ContentDisposition.REJECTED, ReasonCode.UNKNOWN_DESCRIPTOR_FIELD)
    if _ROOT_FIELDS - root_keys:
        return _result(ContentDisposition.REJECTED, ReasonCode.INVALID_DESCRIPTOR)

    content_type = descriptor.get("content_type")
    if not isinstance(content_type, str) or content_type not in _CONTRACTS:
        return _result(ContentDisposition.REJECTED, ReasonCode.UNKNOWN_CONTENT_TYPE)
    descriptor_contract_id = descriptor.get("descriptor_contract_id")
    if (
        not isinstance(descriptor_contract_id, str)
        or descriptor_contract_id not in _DESCRIPTOR_CONTRACT_TO_TYPE
    ):
        return _result(ContentDisposition.REJECTED, ReasonCode.UNKNOWN_SCHEMA)
    if _DESCRIPTOR_CONTRACT_TO_TYPE[descriptor_contract_id] != content_type:
        return _result(ContentDisposition.REJECTED, ReasonCode.SCHEMA_TYPE_MISMATCH)
    expected_media_type, expected_contract_id, expected_payload_contract, _, _ = _CONTRACTS[
        content_type
    ]
    if descriptor_contract_id != expected_contract_id:
        return _result(ContentDisposition.REJECTED, ReasonCode.SCHEMA_TYPE_MISMATCH)
    payload_contract = descriptor.get("payload_contract")
    if not isinstance(payload_contract, Mapping) or dict(payload_contract) != expected_payload_contract:
        return _result(ContentDisposition.REJECTED, ReasonCode.PAYLOAD_CONTRACT_MISMATCH)
    if descriptor.get("media_type") != expected_media_type:
        return _result(ContentDisposition.REJECTED, ReasonCode.MEDIA_TYPE_MISMATCH)

    attribute_reason = _attributes_are_valid(content_type, descriptor.get("attributes"))
    if attribute_reason is not None:
        return _result(ContentDisposition.REJECTED, attribute_reason)
    return _result(ContentDisposition.REMOTE_DECLARATIVE, ReasonCode.ALLOWLIST_MATCH)
