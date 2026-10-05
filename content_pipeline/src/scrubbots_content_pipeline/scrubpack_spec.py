"""Declarative .scrubpack V1 layout and safe logical member-name helpers.

This module describes the container contract. It does not read or write ZIPs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


SCRUBPACK_EXTENSION = ".scrubpack"
SCRUBPACK_SCHEMA = "scrubbots.scrubpack.manifest.v1"
SCRUBPACK_VERSION = 1
SCRUBPACK_MEDIA_TYPE = "application/vnd.scrubbots.scrubpack+zip"
PACK_MANIFEST_PATH = "pack.json"
LEVELS_DIRECTORY = "levels"

_LEVEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_LEVEL_MEMBER = re.compile(
    r"^levels/([A-Za-z0-9][A-Za-z0-9._-]{0,63})/(level|supply-plan|metadata)\.json$"
)


class ScrubpackSpecError(ValueError):
    """Raised when a logical member name or level identity violates V1."""


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
    schema: str = SCRUBPACK_SCHEMA
    version: int = SCRUBPACK_VERSION
    media_type: str = SCRUBPACK_MEDIA_TYPE

    def __post_init__(self) -> None:
        if self.schema != SCRUBPACK_SCHEMA or type(self.version) is not int or self.version != SCRUBPACK_VERSION:
            raise ScrubpackSpecError("unsupported scrubpack manifest contract")
        if self.media_type != SCRUBPACK_MEDIA_TYPE:
            raise ScrubpackSpecError("unsupported scrubpack media type")
        ids = [level.level_id for level in self.levels]
        if len(ids) != len(set(ids)):
            raise ScrubpackSpecError("duplicate level ID")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "version": self.version,
            "mediaType": self.media_type,
            "levels": [
                {
                    "id": level.level_id,
                    "files": {
                        "levelData": level.level_data_path,
                        "supplyPlan": level.supply_plan_path,
                        "metadata": level.metadata_path,
                    },
                }
                for level in self.levels
            ],
        }


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
    for name in names:
        if not validate_member_name(name) or name in seen:
            return False
        seen.add(name)
    return True


def expected_member_names(levels: Iterable[ScrubpackLevelV1]) -> tuple[str, ...]:
    """Return the fixed member set in caller-provided level order."""
    level_list = tuple(levels)
    manifest = ScrubpackManifestV1(level_list)
    return (PACK_MANIFEST_PATH, *(path for level in manifest.levels for path in level.member_paths))


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
    "expected_member_names",
    "validate_member_name",
    "validate_member_names",
]
