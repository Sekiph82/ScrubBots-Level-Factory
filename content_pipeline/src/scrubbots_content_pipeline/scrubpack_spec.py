"""Declarative .scrubpack V1 layout and safe logical member-name helpers.

This module describes the container contract. It does not read or write ZIPs.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Iterable


SCRUBPACK_EXTENSION = ".scrubpack"
SCRUBPACK_SCHEMA = "scrubbots.scrubpack.manifest.v1"
SCRUBPACK_VERSION = 1
SCRUBPACK_MEDIA_TYPE = "application/vnd.scrubbots.scrubpack+zip"
PACK_MANIFEST_PATH = "pack.json"
LEVELS_DIRECTORY = "levels"

_LEVEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_PACK_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_LEVEL_MEMBER = re.compile(
    r"^levels/([A-Za-z0-9][A-Za-z0-9._-]{0,63})/(level|supply-plan|metadata)\.json$"
)


class ScrubpackSpecError(ValueError):
    """Raised when a logical member name or level identity violates V1."""


def canonical_level_sort_key(level_id: str) -> bytes:
    """Return the V1 case-sensitive ASCII-byte ordering key for a level ID."""
    if not isinstance(level_id, str) or not _LEVEL_ID.fullmatch(level_id):
        raise ScrubpackSpecError("invalid level ID")
    return level_id.encode("ascii")


def canonical_json_bytes(value: object) -> bytes:
    """Serialize canonical JSON as sorted compact UTF-8 bytes."""
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ScrubpackSpecError("value cannot be represented as canonical JSON") from exc


def _validate_unique_level_ids(level_ids: Iterable[str]) -> None:
    seen: set[str] = set()
    folded: set[str] = set()
    for level_id in level_ids:
        if level_id in seen:
            raise ScrubpackSpecError("duplicate level ID")
        normalized = level_id.casefold()
        if normalized in folded:
            raise ScrubpackSpecError("case-normalized level ID collision")
        seen.add(level_id)
        folded.add(normalized)


def normalize_created_at_utc(value: str | datetime) -> str:
    """Validate explicit timezone-aware time and serialize canonical UTC seconds."""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and _TIMESTAMP.fullmatch(value):
        try:
            parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
        except ValueError as exc:
            raise ScrubpackSpecError("invalid created_at_utc timestamp") from exc
    else:
        raise ScrubpackSpecError("created_at_utc must include an explicit timezone")
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.microsecond != 0:
        raise ScrubpackSpecError("created_at_utc must be timezone-aware whole seconds")
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True, slots=True)
class ScrubpackLevelV1:
    """A level's fixed declarative member paths; no paths come from callers."""

    level_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.level_id, str) or not _LEVEL_ID.fullmatch(self.level_id):
            raise ScrubpackSpecError("invalid level ID")

    @property
    def level_data_path(self) -> str:
        return f"{LEVELS_DIRECTORY}/{self.level_id}/level.json"

    @property
    def supply_plan_path(self) -> str:
        return f"{LEVELS_DIRECTORY}/{self.level_id}/supply-plan.json"

    @property
    def metadata_path(self) -> str:
        return f"{LEVELS_DIRECTORY}/{self.level_id}/metadata.json"

    @property
    def member_paths(self) -> tuple[str, str, str]:
        return (self.level_data_path, self.supply_plan_path, self.metadata_path)


@dataclass(frozen=True, slots=True)
class ScrubpackManifestV1:
    """Minimal versioned manifest model for the V1 declarative layout."""

    levels: tuple[ScrubpackLevelV1, ...]
    pack_id: str
    pack_version: int
    created_at_utc: str | datetime
    member_sha256: Mapping[str, str]
    schema: str = SCRUBPACK_SCHEMA
    version: int = SCRUBPACK_VERSION
    media_type: str = SCRUBPACK_MEDIA_TYPE

    def __post_init__(self) -> None:
        if self.schema != SCRUBPACK_SCHEMA or type(self.version) is not int or self.version != SCRUBPACK_VERSION:
            raise ScrubpackSpecError("unsupported scrubpack manifest contract")
        if self.media_type != SCRUBPACK_MEDIA_TYPE:
            raise ScrubpackSpecError("unsupported scrubpack media type")
        if not isinstance(self.pack_id, str) or not _PACK_ID.fullmatch(self.pack_id):
            raise ScrubpackSpecError("invalid pack ID")
        if type(self.pack_version) is not int or self.pack_version <= 0:
            raise ScrubpackSpecError("pack version must be a positive integer")
        object.__setattr__(self, "created_at_utc", normalize_created_at_utc(self.created_at_utc))
        if not self.levels:
            raise ScrubpackSpecError("at least one level is required")
        ids = [level.level_id for level in self.levels]
        _validate_unique_level_ids(ids)
        object.__setattr__(
            self,
            "levels",
            tuple(sorted(self.levels, key=lambda level: canonical_level_sort_key(level.level_id))),
        )
        if not isinstance(self.member_sha256, Mapping):
            raise ScrubpackSpecError("member SHA-256 values must be a mapping")
        expected_paths = {path for level in self.levels for path in level.member_paths}
        if set(self.member_sha256) != expected_paths or any(
            not isinstance(path, str)
            or not isinstance(digest, str)
            or not _SHA256.fullmatch(digest)
            for path, digest in self.member_sha256.items()
        ):
            raise ScrubpackSpecError("member SHA-256 values must cover every exact payload path")
        object.__setattr__(self, "member_sha256", MappingProxyType(dict(self.member_sha256)))

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "version": self.version,
            "mediaType": self.media_type,
            "packId": self.pack_id,
            "packVersion": self.pack_version,
            "createdAtUtc": self.created_at_utc,
            "levelCount": len(self.levels),
            "levels": [
                {
                    "id": level.level_id,
                    "files": {
                        "levelData": level.level_data_path,
                        "supplyPlan": level.supply_plan_path,
                        "metadata": level.metadata_path,
                    },
                    "sha256": {
                        "levelData": self.member_sha256[level.level_data_path],
                        "supplyPlan": self.member_sha256[level.supply_plan_path],
                        "metadata": self.member_sha256[level.metadata_path],
                    },
                }
                for level in self.levels
            ],
        }

    @classmethod
    def from_dict(cls, value: object) -> ScrubpackManifestV1:
        """Validate and recover exact V1 identity, count, and ordered membership."""
        required = {
            "schema", "version", "mediaType", "packId", "packVersion",
            "createdAtUtc", "levelCount", "levels",
        }
        if not isinstance(value, Mapping) or set(value) != required:
            raise ScrubpackSpecError("invalid manifest fields")
        raw_levels = value["levels"]
        if type(value["levelCount"]) is not int or not isinstance(raw_levels, list):
            raise ScrubpackSpecError("invalid manifest level count or membership")
        if value["levelCount"] != len(raw_levels):
            raise ScrubpackSpecError("manifest level count mismatch")
        levels: list[ScrubpackLevelV1] = []
        member_digests: dict[str, str] = {}
        for raw_level in raw_levels:
            if not isinstance(raw_level, Mapping) or set(raw_level) != {"id", "files", "sha256"}:
                raise ScrubpackSpecError("invalid manifest level entry")
            level = ScrubpackLevelV1(raw_level["id"])
            files = raw_level["files"]
            if not isinstance(files, Mapping) or set(files) != {"levelData", "supplyPlan", "metadata"}:
                raise ScrubpackSpecError("invalid manifest level file map")
            expected = {
                "levelData": level.level_data_path,
                "supplyPlan": level.supply_plan_path,
                "metadata": level.metadata_path,
            }
            if dict(files) != expected:
                raise ScrubpackSpecError("manifest level paths do not match level identity")
            digests = raw_level["sha256"]
            if not isinstance(digests, Mapping) or set(digests) != {"levelData", "supplyPlan", "metadata"}:
                raise ScrubpackSpecError("invalid manifest level SHA-256 map")
            for role, path_key in (("levelData", "levelData"), ("supplyPlan", "supplyPlan"), ("metadata", "metadata")):
                member_digests[expected[path_key]] = digests[role]
            levels.append(level)
        ids = [level.level_id for level in levels]
        if ids != sorted(ids, key=canonical_level_sort_key):
            raise ScrubpackSpecError("manifest levels are not in canonical order")
        return cls(
            levels=tuple(levels),
            pack_id=value["packId"],
            pack_version=value["packVersion"],
            created_at_utc=value["createdAtUtc"],
            member_sha256=member_digests,
            schema=value["schema"],
            version=value["version"],
            media_type=value["mediaType"],
        )


def validate_member_name(name: object) -> bool:
    """Return whether a ZIP member name is one canonical V1 JSON path."""
    if not isinstance(name, str) or not name:
        return False
    if name == PACK_MANIFEST_PATH:
        return True
    match = _LEVEL_MEMBER.fullmatch(name)
    return match is not None


def validate_member_names(names: Iterable[object]) -> bool:
    """Fail closed on invalid or duplicate V1 member names."""
    seen: set[str] = set()
    normalized_seen: set[str] = set()
    for name in names:
        if not validate_member_name(name) or name in seen:
            return False
        normalized = name.casefold().replace("\\", "/")
        if normalized in normalized_seen:
            return False
        seen.add(name)
        normalized_seen.add(normalized)
    return True


def expected_member_names(levels: Iterable[ScrubpackLevelV1]) -> tuple[str, ...]:
    """Return the fixed member set in caller-provided level order."""
    level_list = tuple(levels)
    ids = [level.level_id for level in level_list]
    _validate_unique_level_ids(ids)
    if not level_list:
        raise ScrubpackSpecError("at least one level is required")
    level_list = tuple(sorted(level_list, key=lambda level: canonical_level_sort_key(level.level_id)))
    return (PACK_MANIFEST_PATH, *(path for level in level_list for path in level.member_paths))


__all__ = [
    "LEVELS_DIRECTORY",
    "PACK_MANIFEST_PATH",
    "SCRUBPACK_EXTENSION",
    "SCRUBPACK_MEDIA_TYPE",
    "SCRUBPACK_SCHEMA",
    "SCRUBPACK_VERSION",
    "ScrubpackLevelV1",
    "ScrubpackManifestV1",
    "ScrubpackSpecError",
    "canonical_json_bytes",
    "canonical_level_sort_key",
    "expected_member_names",
    "normalize_created_at_utc",
    "validate_member_name",
    "validate_member_names",
]
