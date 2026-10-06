"""Pure compatibility checks between explicit app and manifest capabilities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from .manifest_v1 import check_game_version_compatibility, parse_canonical_game_version


class AppContentCompatibilityReasonCode(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    UNSUPPORTED_SCHEMA_VERSION = "UNSUPPORTED_SCHEMA_VERSION"
    GAME_VERSION_TOO_OLD = "GAME_VERSION_TOO_OLD"
    INVALID_APP_VERSION = "INVALID_APP_VERSION"
    INVALID_APP_CAPABILITY = "INVALID_APP_CAPABILITY"
    INVALID_MANIFEST_COMPATIBILITY_FIELDS = "INVALID_MANIFEST_COMPATIBILITY_FIELDS"


@dataclass(frozen=True, slots=True)
class AppContentCompatibilityResult:
    compatible: bool
    reason_code: AppContentCompatibilityReasonCode


def _supported_versions(value: object) -> frozenset[int] | range | None:
    if isinstance(value, range):
        if value.step != 1 or value.start < 1 or value.stop <= value.start:
            return None
        return value
    if isinstance(value, (set, frozenset, tuple, list)):
        values = tuple(value)
        if not values or any(type(version) is not int or version < 1 for version in values):
            return None
        if len(set(values)) != len(values):
            return None
        return frozenset(values)
    return None


def check_app_content_compatibility(
    *,
    current_game_version: object,
    supported_manifest_schema_versions: object,
    manifest_schema: object,
    manifest_schema_version: object,
    minimum_game_version: object,
) -> AppContentCompatibilityResult:
    """Fail closed using only explicit app capabilities and manifest fields.

    `supported_manifest_schema_versions` maps schema identifiers to a nonempty
    set/sequence of positive schema versions or an inclusive-style Python range
    (`range(start, stop)`, where stop is exclusive).
    """
    try:
        parse_canonical_game_version(current_game_version)
    except (TypeError, ValueError):
        return AppContentCompatibilityResult(False, AppContentCompatibilityReasonCode.INVALID_APP_VERSION)

    if not isinstance(supported_manifest_schema_versions, Mapping) or not supported_manifest_schema_versions:
        return AppContentCompatibilityResult(False, AppContentCompatibilityReasonCode.INVALID_APP_CAPABILITY)
    supported: dict[str, frozenset[int] | range] = {}
    for schema, versions in supported_manifest_schema_versions.items():
        parsed_versions = _supported_versions(versions)
        if not isinstance(schema, str) or not schema or parsed_versions is None:
            return AppContentCompatibilityResult(False, AppContentCompatibilityReasonCode.INVALID_APP_CAPABILITY)
        supported[schema] = parsed_versions

    if (
        not isinstance(manifest_schema, str)
        or not manifest_schema
        or type(manifest_schema_version) is not int
        or manifest_schema_version < 1
        or not isinstance(minimum_game_version, str)
    ):
        return AppContentCompatibilityResult(
            False, AppContentCompatibilityReasonCode.INVALID_MANIFEST_COMPATIBILITY_FIELDS
        )
    try:
        parse_canonical_game_version(minimum_game_version)
    except (TypeError, ValueError):
        return AppContentCompatibilityResult(
            False, AppContentCompatibilityReasonCode.INVALID_MANIFEST_COMPATIBILITY_FIELDS
        )

    if manifest_schema not in supported or manifest_schema_version not in supported[manifest_schema]:
        return AppContentCompatibilityResult(False, AppContentCompatibilityReasonCode.UNSUPPORTED_SCHEMA_VERSION)

    game_check = check_game_version_compatibility(minimum_game_version, current_game_version)
    if not game_check.compatible:
        return AppContentCompatibilityResult(False, AppContentCompatibilityReasonCode.GAME_VERSION_TOO_OLD)
    return AppContentCompatibilityResult(True, AppContentCompatibilityReasonCode.COMPATIBLE)


__all__ = [
    "AppContentCompatibilityReasonCode",
    "AppContentCompatibilityResult",
    "check_app_content_compatibility",
]
