"""Immutable logical-artwork JSON contract for M08."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import hashlib
import json

from ..contracts import Difficulty, parse_difficulty, validate_dimensions, validate_used_color_count
from ..quality import logical_grid_hash


ARTWORK_SCHEMA = "scrubbots-logical-artwork"
ARTWORK_SCHEMA_VERSION = 1
ROW_MAJOR_INDEX_RULE = "index = y * width + x"


class ArtworkContractError(ValueError):
    """Raised when immutable logical-artwork truth is malformed."""


def canonical_json_bytes(value: object) -> bytes:
    """Serialize JSON-compatible values without machine or time variance."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _require_candidate_id(value: object) -> str:
    if type(value) is not str or not value or not value.strip():
        raise ArtworkContractError("candidate_id must be an explicit non-empty string")
    if "\x00" in value or "/" in value or "\\" in value or value in {".", ".."}:
        raise ArtworkContractError("candidate_id contains path traversal or a path separator")
    if ":" in value or value.startswith(("/", "~")):
        raise ArtworkContractError("candidate_id must not use absolute-path semantics")
    return value


def _validate_artwork_fields(
    candidate_id: object,
    difficulty: object,
    width: object,
    height: object,
    cells: object,
    palette: object | None = None,
    grid_hash: object | None = None,
) -> tuple[str, Difficulty, int, int, tuple[str, ...], tuple[str, ...], str]:
    identifier = _require_candidate_id(candidate_id)
    try:
        selected = parse_difficulty(difficulty)  # type: ignore[arg-type]
        checked_width, checked_height = validate_dimensions(selected, width, height)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ArtworkContractError(str(exc)) from exc
    if isinstance(cells, (str, bytes, bytearray)) or not isinstance(cells, Iterable):
        raise ArtworkContractError("cells must be an iterable of canonical C-ID values")
    normalized = tuple(cells)
    if len(normalized) != checked_width * checked_height:
        raise ArtworkContractError("cells length must equal width multiplied by height")
    if any(type(cell) is not str for cell in normalized):
        raise ArtworkContractError("cells must contain only canonical C-ID strings")
    try:
        actual_palette = validate_used_color_count(selected, normalized)
    except (TypeError, ValueError) as exc:
        raise ArtworkContractError(str(exc)) from exc
    if palette is not None:
        if not isinstance(palette, (list, tuple)) or tuple(palette) != actual_palette:
            raise ArtworkContractError("palette must equal the ascending actual-used C-ID subset")
    identity = logical_grid_hash(checked_width, checked_height, normalized)
    if grid_hash is not None and grid_hash != identity:
        raise ArtworkContractError("grid_hash does not match the logical cells")
    return identifier, selected, checked_width, checked_height, normalized, actual_palette, identity


@dataclass(frozen=True, slots=True)
class ArtworkArtifact:
    """Immutable logical artwork; quality state is intentionally not a field."""

    candidate_id: str
    difficulty: Difficulty
    width: int
    height: int
    palette: tuple[str, ...]
    cells: tuple[str, ...]
    grid_hash: str

    @classmethod
    def from_cells(
        cls,
        candidate_id: str,
        difficulty: Difficulty | str,
        width: int,
        height: int,
        cells: Iterable[str],
    ) -> "ArtworkArtifact":
        identifier, selected, checked_width, checked_height, normalized, palette, identity = _validate_artwork_fields(
            candidate_id, difficulty, width, height, tuple(cells)
        )
        return cls(identifier, selected, checked_width, checked_height, palette, normalized, identity)

    @classmethod
    def from_dict(cls, value: object) -> "ArtworkArtifact":
        if not isinstance(value, Mapping):
            raise ArtworkContractError("artwork JSON root must be an object")
        required = {"schema", "schema_version", "candidate_id", "difficulty", "width", "height", "palette", "cells", "grid_hash", "index_rule"}
        if set(value) != required:
            raise ArtworkContractError("artwork JSON keys do not match the versioned contract")
        if value["schema"] != ARTWORK_SCHEMA or value["schema_version"] != ARTWORK_SCHEMA_VERSION:
            raise ArtworkContractError("unsupported artwork schema/version")
        if value["index_rule"] != ROW_MAJOR_INDEX_RULE:
            raise ArtworkContractError("artwork index rule is unsupported")
        identifier, selected, width, height, cells, palette, identity = _validate_artwork_fields(
            value["candidate_id"], value["difficulty"], value["width"], value["height"], value["cells"], value["palette"], value["grid_hash"]
        )
        return cls(identifier, selected, width, height, palette, cells, identity)

    @classmethod
    def from_result(cls, result: object, candidate_id: str) -> "ArtworkArtifact":
        if not getattr(result, "is_success", False):
            raise ArtworkContractError("failed GenerationResult cannot be exported as artwork")
        request = getattr(result, "request", None)
        if request is None:
            raise ArtworkContractError("successful GenerationResult must retain its request")
        return cls.from_cells(candidate_id, request.difficulty, result.width, result.height, result.logical_grid)

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": ARTWORK_SCHEMA,
            "schema_version": ARTWORK_SCHEMA_VERSION,
            "candidate_id": self.candidate_id,
            "difficulty": self.difficulty.value,
            "width": self.width,
            "height": self.height,
            "palette": list(self.palette),
            "index_rule": ROW_MAJOR_INDEX_RULE,
            "cells": list(self.cells),
            "grid_hash": self.grid_hash,
        }

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.as_dict())

    def canonical_json(self) -> str:
        return self.canonical_bytes().decode("utf-8")

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


__all__ = [
    "ARTWORK_SCHEMA",
    "ARTWORK_SCHEMA_VERSION",
    "ROW_MAJOR_INDEX_RULE",
    "ArtworkArtifact",
    "ArtworkContractError",
    "canonical_json_bytes",
]
