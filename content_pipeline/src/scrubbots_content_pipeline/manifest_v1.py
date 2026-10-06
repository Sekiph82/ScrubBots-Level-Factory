"""Immutable, declarative remote content manifest V1 model.

This module owns local manifest shape and canonical serialization only. It does
not resolve references, access the network, or mutate content.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


CONTENT_MANIFEST_SCHEMA = "scrubbots.content.manifest.v1"
CONTENT_MANIFEST_SCHEMA_VERSION = 1
_PACK_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_LEVEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_GAME_VERSION = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_PACK_OBJECT_KEY = re.compile(
    r"^packs/[a-z0-9][a-z0-9_-]{0,63}/[a-z0-9][a-z0-9._-]*(?:/[a-z0-9][a-z0-9._-]*)*\.scrubpack$"
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_UTC_TIMESTAMP = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")


class ContentManifestError(ValueError):
    """Raised when a manifest does not satisfy the closed V1 contract."""


class ManifestSuccessorReasonCode(str, Enum):
    """Stable local outcomes for checking one proposed manifest successor."""

    VALID_SUCCESSOR = "VALID_SUCCESSOR"
    INVALID_PREVIOUS_CONTENT_VERSION = "INVALID_PREVIOUS_CONTENT_VERSION"
    INVALID_CANDIDATE_MANIFEST = "INVALID_CANDIDATE_MANIFEST"
    CONTENT_VERSION_NOT_INCREASED = "CONTENT_VERSION_NOT_INCREASED"


@dataclass(frozen=True, slots=True)
class ManifestSuccessorResult:
    """Deterministic, side-effect-free result for a manifest version check."""

    accepted: bool
    reason_code: ManifestSuccessorReasonCode


class ManifestCompatibilityReasonCode(str, Enum):
    """Stable local outcomes for an explicit game/minimum version comparison."""

    COMPATIBLE = "COMPATIBLE"
    GAME_VERSION_TOO_OLD = "GAME_VERSION_TOO_OLD"
    INVALID_MINIMUM_GAME_VERSION = "INVALID_MINIMUM_GAME_VERSION"
    INVALID_CURRENT_GAME_VERSION = "INVALID_CURRENT_GAME_VERSION"


@dataclass(frozen=True, slots=True)
class ManifestCompatibilityResult:
    """Deterministic result for checking an explicit game version."""

    compatible: bool
    reason_code: ManifestCompatibilityReasonCode


def parse_canonical_game_version(value: object) -> tuple[int, int, int]:
    """Parse strict MAJOR.MINOR.PATCH decimal triplets without whitespace or leading zeroes."""
    if not isinstance(value, str):
        raise ContentManifestError("game version must be a canonical string")
    match = _GAME_VERSION.fullmatch(value)
    if match is None:
        raise ContentManifestError("game version must use canonical MAJOR.MINOR.PATCH")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class ManifestPackV1:
    """Stable identity and provider-neutral immutable archive reference."""

    pack_id: str
    pack_version: int
    object_key: str
    sha256: str
    byte_length: int

    def __post_init__(self) -> None:
        if not isinstance(self.pack_id, str) or not _PACK_ID.fullmatch(self.pack_id):
            raise ContentManifestError("invalid pack_id")
        if type(self.pack_version) is not int or self.pack_version < 1:
            raise ContentManifestError("pack_version must be a positive integer")
        if not isinstance(self.object_key, str) or not _PACK_OBJECT_KEY.fullmatch(self.object_key):
            raise ContentManifestError("invalid provider-neutral pack object_key")
        if not isinstance(self.sha256, str) or not _SHA256.fullmatch(self.sha256):
            raise ContentManifestError("sha256 must be lowercase 64-hex")
        if type(self.byte_length) is not int or self.byte_length < 1:
            raise ContentManifestError("byte_length must be a positive integer")

    def to_dict(self) -> dict[str, object]:
        return {
            "pack_id": self.pack_id,
            "pack_version": self.pack_version,
            "object_key": self.object_key,
            "sha256": self.sha256,
            "byte_length": self.byte_length,
        }

    def to_json_bytes(self) -> bytes:
        """Return deterministic UTF-8 bytes for this provider-neutral pack record."""
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True, slots=True)
class ManifestLevelV1:
    """Stable level identity and its declared pack owner."""

    level_id: str
    pack_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.level_id, str) or not _LEVEL_ID.fullmatch(self.level_id):
            raise ContentManifestError("invalid level_id")
        if not isinstance(self.pack_id, str) or not _PACK_ID.fullmatch(self.pack_id):
            raise ContentManifestError("invalid pack_id")

    def to_dict(self) -> dict[str, object]:
        return {"level_id": self.level_id, "pack_id": self.pack_id}


def _parse_utc_timestamp(value: object) -> datetime:
    if not isinstance(value, str) or not _UTC_TIMESTAMP.fullmatch(value):
        raise ContentManifestError("timestamp must be whole-second UTC in YYYY-MM-DDTHH:MM:SSZ form")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ContentManifestError("timestamp is not a valid UTC instant") from exc
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise ContentManifestError("timestamp is not canonical UTC")
    return parsed


@dataclass(frozen=True, slots=True)
class ManifestScheduleV1:
    """One explicit UTC activation window for a pack or level target."""

    target_kind: str
    target_id: str
    not_before: str
    not_after: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.target_kind, str) or self.target_kind not in {"pack", "level"}:
            raise ContentManifestError("schedule target_kind must be pack or level")
        target_pattern = _PACK_ID if self.target_kind == "pack" else _LEVEL_ID
        if not isinstance(self.target_id, str) or not target_pattern.fullmatch(self.target_id):
            raise ContentManifestError("invalid schedule target_id")
        start = _parse_utc_timestamp(self.not_before)
        if self.not_after is not None:
            end = _parse_utc_timestamp(self.not_after)
            if end <= start:
                raise ContentManifestError("schedule not_after must be later than not_before")

    def to_dict(self) -> dict[str, object]:
        return {
            "target_kind": self.target_kind,
            "target_id": self.target_id,
            "not_before": self.not_before,
            "not_after": self.not_after,
        }

    def to_json_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True, slots=True)
class ContentManifestV1:
    """Closed immutable manifest root with deterministic pack and level order."""

    packs: tuple[ManifestPackV1, ...] = ()
    levels: tuple[ManifestLevelV1, ...] = ()
    schema: str = CONTENT_MANIFEST_SCHEMA
    schema_version: int = CONTENT_MANIFEST_SCHEMA_VERSION
    content_version: int = 1
    minimum_game_version: str = "0.0.0"
    disabled_levels: tuple[str, ...] = ()
    schedules: tuple[ManifestScheduleV1, ...] = ()

    def __post_init__(self) -> None:
        if self.schema != CONTENT_MANIFEST_SCHEMA:
            raise ContentManifestError("unsupported manifest schema")
        if type(self.schema_version) is not int or self.schema_version != CONTENT_MANIFEST_SCHEMA_VERSION:
            raise ContentManifestError("unsupported manifest schema_version")
        if type(self.content_version) is not int or self.content_version < 1:
            raise ContentManifestError("content_version must be a positive integer")
        parse_canonical_game_version(self.minimum_game_version)
        if not isinstance(self.packs, tuple) or any(not isinstance(pack, ManifestPackV1) for pack in self.packs):
            raise ContentManifestError("packs must contain ManifestPackV1 values")
        if not isinstance(self.levels, tuple) or any(not isinstance(level, ManifestLevelV1) for level in self.levels):
            raise ContentManifestError("levels must contain ManifestLevelV1 values")
        if not isinstance(self.disabled_levels, tuple) or any(
            not isinstance(level_id, str) or not _LEVEL_ID.fullmatch(level_id) for level_id in self.disabled_levels
        ):
            raise ContentManifestError("disabled_levels must contain canonical level IDs")
        if not isinstance(self.schedules, tuple) or any(
            not isinstance(schedule, ManifestScheduleV1) for schedule in self.schedules
        ):
            raise ContentManifestError("schedules must contain ManifestScheduleV1 values")
        pack_ids = [pack.pack_id for pack in self.packs]
        normalized_pack_ids = [pack_id.casefold() for pack_id in pack_ids]
        object_keys = [pack.object_key for pack in self.packs]
        level_ids = [level.level_id for level in self.levels]
        normalized_level_ids = [level_id.casefold() for level_id in level_ids]
        level_owners: dict[str, set[str]] = {}
        for level in self.levels:
            level_owners.setdefault(level.level_id.casefold(), set()).add(level.pack_id.casefold())
        normalized_disabled_ids = [level_id.casefold() for level_id in self.disabled_levels]
        if len(normalized_pack_ids) != len(set(normalized_pack_ids)):
            raise ContentManifestError("duplicate pack_id")
        if len(object_keys) != len(set(object_keys)):
            raise ContentManifestError("duplicate pack object_key")
        if any(len(owners) > 1 for _, owners in sorted(level_owners.items())):
            raise ContentManifestError("conflicting level ownership")
        if len(normalized_level_ids) != len(set(normalized_level_ids)):
            raise ContentManifestError("duplicate level_id")
        if len(normalized_disabled_ids) != len(set(normalized_disabled_ids)):
            raise ContentManifestError("duplicate disabled level ID")
        schedule_targets = [(schedule.target_kind, schedule.target_id.casefold()) for schedule in self.schedules]
        if len(schedule_targets) != len(set(schedule_targets)):
            raise ContentManifestError("duplicate schedule target")
        object.__setattr__(self, "packs", tuple(sorted(self.packs, key=lambda pack: pack.pack_id.encode("ascii"))))
        object.__setattr__(
            self, "disabled_levels", tuple(sorted(self.disabled_levels, key=lambda level_id: level_id.encode("ascii")))
        )
        object.__setattr__(
            self,
            "schedules",
            tuple(sorted(self.schedules, key=lambda schedule: (schedule.target_kind, schedule.target_id.encode("ascii")))),
        )
        # Preserve declared level array order; level identity never implies catalog order.

    def to_dict(self) -> dict[str, object]:
        """Return fresh JSON-compatible data in the canonical V1 shape."""
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "content_version": self.content_version,
            "minimum_game_version": self.minimum_game_version,
            "disabled_levels": list(self.disabled_levels),
            "schedules": [schedule.to_dict() for schedule in self.schedules],
            "packs": [pack.to_dict() for pack in self.packs],
            "levels": [level.to_dict() for level in self.levels],
        }

    def to_json_bytes(self) -> bytes:
        """Serialize a stable UTF-8 representation with canonical object keys."""
        return json.dumps(
            self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")

    @classmethod
    def from_dict(cls, value: object) -> ContentManifestV1:
        """Parse a mapping only when every root and item field is explicitly known."""
        required = {
            "schema", "schema_version", "content_version", "minimum_game_version", "disabled_levels", "schedules",
            "packs", "levels"
        }
        if not isinstance(value, Mapping) or set(value) != required:
            raise ContentManifestError("invalid manifest fields")
        if value["schema"] != CONTENT_MANIFEST_SCHEMA:
            raise ContentManifestError("unsupported manifest schema")
        if type(value["schema_version"]) is not int or value["schema_version"] != 1:
            raise ContentManifestError("unsupported manifest schema_version")
        if type(value["content_version"]) is not int or value["content_version"] < 1:
            raise ContentManifestError("content_version must be a positive integer")
        parse_canonical_game_version(value["minimum_game_version"])
        if not all(isinstance(value[key], list) for key in ("packs", "levels", "disabled_levels", "schedules")):
            raise ContentManifestError("packs, levels, disabled_levels, and schedules must be arrays")
        packs: list[ManifestPackV1] = []
        for item in value["packs"]:
            if not isinstance(item, Mapping) or set(item) != {
                "pack_id", "pack_version", "object_key", "sha256", "byte_length"
            }:
                raise ContentManifestError("invalid pack fields")
            packs.append(
                ManifestPackV1(
                    item["pack_id"],
                    item["pack_version"],
                    item["object_key"],
                    item["sha256"],
                    item["byte_length"],
                )
            )
        levels: list[ManifestLevelV1] = []
        for item in value["levels"]:
            if not isinstance(item, Mapping) or set(item) != {"level_id", "pack_id"}:
                raise ContentManifestError("invalid level fields")
            levels.append(ManifestLevelV1(item["level_id"], item["pack_id"]))
        schedules: list[ManifestScheduleV1] = []
        for item in value["schedules"]:
            if not isinstance(item, Mapping) or set(item) not in (
                {"target_kind", "target_id", "not_before"},
                {"target_kind", "target_id", "not_before", "not_after"},
            ):
                raise ContentManifestError("invalid schedule fields")
            schedules.append(
                ManifestScheduleV1(
                    item["target_kind"], item["target_id"], item["not_before"], item.get("not_after")
                )
            )
        return cls(
            tuple(packs),
            tuple(levels),
            value["schema"],
            value["schema_version"],
            value["content_version"],
            value["minimum_game_version"],
            tuple(value["disabled_levels"]),
            tuple(schedules),
        )


def is_level_disabled(manifest: ContentManifestV1, level_id: object) -> bool:
    """Return whether a valid logical level ID appears in this manifest's disable list."""
    if not isinstance(manifest, ContentManifestV1):
        raise ContentManifestError("manifest must be a ContentManifestV1")
    if not isinstance(level_id, str) or not _LEVEL_ID.fullmatch(level_id):
        raise ContentManifestError("invalid level_id")
    return level_id.casefold() in {disabled_id.casefold() for disabled_id in manifest.disabled_levels}


def is_schedule_active(schedule: ManifestScheduleV1, at_utc: object) -> bool:
    """Evaluate one UTC window solely against an explicit canonical instant."""
    if not isinstance(schedule, ManifestScheduleV1):
        raise ContentManifestError("schedule must be a ManifestScheduleV1")
    instant = _parse_utc_timestamp(at_utc)
    start = _parse_utc_timestamp(schedule.not_before)
    if instant < start:
        return False
    return schedule.not_after is None or instant < _parse_utc_timestamp(schedule.not_after)


def check_manifest_successor(
    previous_content_version: object, candidate: object
) -> ManifestSuccessorResult:
    """Check a candidate manifest against an accepted version without storing history."""
    if type(previous_content_version) is not int or previous_content_version < 1:
        return ManifestSuccessorResult(False, ManifestSuccessorReasonCode.INVALID_PREVIOUS_CONTENT_VERSION)
    try:
        manifest = ContentManifestV1.from_dict(candidate)
    except ContentManifestError:
        return ManifestSuccessorResult(False, ManifestSuccessorReasonCode.INVALID_CANDIDATE_MANIFEST)
    if manifest.content_version <= previous_content_version:
        return ManifestSuccessorResult(False, ManifestSuccessorReasonCode.CONTENT_VERSION_NOT_INCREASED)
    return ManifestSuccessorResult(True, ManifestSuccessorReasonCode.VALID_SUCCESSOR)


def check_game_version_compatibility(
    minimum_game_version: object, current_game_version: object
) -> ManifestCompatibilityResult:
    """Compare explicit canonical versions numerically without external lookups."""
    try:
        minimum = parse_canonical_game_version(minimum_game_version)
    except ContentManifestError:
        return ManifestCompatibilityResult(False, ManifestCompatibilityReasonCode.INVALID_MINIMUM_GAME_VERSION)
    try:
        current = parse_canonical_game_version(current_game_version)
    except ContentManifestError:
        return ManifestCompatibilityResult(False, ManifestCompatibilityReasonCode.INVALID_CURRENT_GAME_VERSION)
    if current < minimum:
        return ManifestCompatibilityResult(False, ManifestCompatibilityReasonCode.GAME_VERSION_TOO_OLD)
    return ManifestCompatibilityResult(True, ManifestCompatibilityReasonCode.COMPATIBLE)


__all__ = [
    "CONTENT_MANIFEST_SCHEMA",
    "CONTENT_MANIFEST_SCHEMA_VERSION",
    "ContentManifestError",
    "ContentManifestV1",
    "ManifestCompatibilityReasonCode",
    "ManifestCompatibilityResult",
    "ManifestSuccessorReasonCode",
    "ManifestSuccessorResult",
    "ManifestLevelV1",
    "ManifestPackV1",
    "ManifestScheduleV1",
    "is_level_disabled",
    "is_schedule_active",
    "check_manifest_successor",
    "check_game_version_compatibility",
    "parse_canonical_game_version",
]
