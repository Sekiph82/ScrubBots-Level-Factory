"""Deterministic semantic-image to logical LEVEL_ART compilation."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
import hashlib
import json
from types import MappingProxyType

from ...contracts import (
    CANONICAL_PALETTE,
    Difficulty,
    actual_used_palette_ids,
    parse_difficulty,
    validate_production_dimensions,
    validate_production_used_color_count,
)
from ...contracts import PRODUCTION_COLOR_MAX, PRODUCTION_COLOR_MIN
from ..contracts import SEMANTIC_RAW_RASTER_MAX_DIMENSION, SemanticContractError
from .core import (
    SemanticRawArtifact,
    SemanticSourceProvenance,
    _canonical_bytes,
    _decode_raw,
    _sha256,
)


LEVEL_ART_SCHEMA = "scrubbots-semantic-level-art"
LEVEL_ART_SCHEMA_VERSION = 1
LEVEL_ART_REPORT_SCHEMA = "scrubbots-semantic-level-art-report"
LEVEL_ART_REPORT_VERSION = 1
CELL_MAJORITY_POLICY_VERSION = "CELL_MAJORITY_V1"
PALETTE_SNAP_POLICY_VERSION = "PALETTE_SNAP_V1"
PRODUCTION_COLOR_ENVELOPE_POLICY_VERSION = "PRODUCTION_COLOR_ENVELOPE_V1"

# Kept as a source-compatibility name; new trusted artifacts use the explicit
# current-production policy identity below rather than the historical class bands.
DIFFICULTY_BUDGET_POLICY_VERSION = PRODUCTION_COLOR_ENVELOPE_POLICY_VERSION

_LEVEL_ART_ARTIFACT_TOKEN = object()
_LEVEL_ART_REPORT_TOKEN = object()
_SHA256_LENGTH = 64


class SemanticLevelArtError(SemanticContractError):
    """Raised when a LEVEL_ART compilation or contract check fails."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


class LevelArtStatus(str, Enum):
    SUCCESS = "SUCCESS"


def _require_sha256(value: object, label: str) -> str:
    if type(value) is not str or len(value) != _SHA256_LENGTH or any(char not in "0123456789abcdef" for char in value):
        raise SemanticLevelArtError("INVALID_DIGEST", f"{label} must be a lowercase SHA-256 digest")
    return value


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _grid_digest(cells: Sequence[str]) -> str:
    return _canonical_digest({"schema": LEVEL_ART_SCHEMA, "row_major_cells": list(cells)})


def _palette_index(color_id: str) -> int:
    return CANONICAL_PALETTE.color(color_id).index


def _rgb_distance(left: tuple[int, int, int], right: tuple[int, int, int]) -> int:
    return sum((a - b) ** 2 for a, b in zip(left, right))


def _validate_rgba(value: object) -> tuple[int, int, int, int]:
    if isinstance(value, bytes):
        channels = tuple(value)
    else:
        try:
            channels = tuple(value)  # type: ignore[arg-type]
        except TypeError as exc:
            raise SemanticLevelArtError("INVALID_RGBA", "CELL_MAJORITY values must be four integer channels") from exc
    if len(channels) != 4 or any(type(channel) is not int or not 0 <= channel <= 255 for channel in channels):
        raise SemanticLevelArtError("INVALID_RGBA", "CELL_MAJORITY values must be four integer channels from 0 through 255")
    return channels  # type: ignore[return-value]


def cell_majority_rgba_grid(
    pixels: bytes,
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
) -> tuple[bytes, ...]:
    """Reduce decoded RGBA pixels to row-major CELL_MAJORITY_V1 winners."""

    if type(source_width) is not int or type(source_height) is not int or type(target_width) is not int or type(target_height) is not int or min(source_width, source_height, target_width, target_height) < 1:
        raise SemanticLevelArtError("INVALID_DIMENSIONS", "CELL_MAJORITY dimensions must be integers")
    if source_width < target_width or source_height < target_height:
        raise SemanticLevelArtError("SOURCE_SMALLER_THAN_TARGET", "CELL_MAJORITY V1 requires source dimensions to cover the target")
    if not isinstance(pixels, bytes) or len(pixels) != source_width * source_height * 4:
        raise SemanticLevelArtError("INVALID_RGBA", "decoded RGBA bytes do not match source dimensions")

    winners: list[bytes] = []
    for target_y in range(target_height):
        y0 = (target_y * source_height) // target_height
        y1 = ((target_y + 1) * source_height) // target_height
        for target_x in range(target_width):
            x0 = (target_x * source_width) // target_width
            x1 = ((target_x + 1) * source_width) // target_width
            if x0 >= x1 or y0 >= y1:
                raise SemanticLevelArtError("EMPTY_CELL_FOOTPRINT", "CELL_MAJORITY source footprint is empty")
            values: list[bytes] = []
            for source_y in range(y0, y1):
                for source_x in range(x0, x1):
                    offset = (source_y * source_width + source_x) * 4
                    values.append(pixels[offset : offset + 4])
            counts = Counter(values)
            winner = min(counts, key=lambda value: (-counts[value], value))
            if winner[3] != 255:
                raise SemanticLevelArtError("NON_OPAQUE_CELL", "LEVEL_ART logical cells require opaque CELL_MAJORITY winners")
            winners.append(winner)
    return tuple(winners)


def palette_snap_grid(majority_rgba: Iterable[bytes | Sequence[int]]) -> tuple[str, ...]:
    """Snap opaque RGBA winners to C01..C16 with deterministic RGB ties."""

    snapped: list[str] = []
    for value in majority_rgba:
        red, green, blue, alpha = _validate_rgba(value)
        if alpha != 255:
            raise SemanticLevelArtError("NON_OPAQUE_CELL", "palette snap requires opaque CELL_MAJORITY winners")
        source_rgb = (red, green, blue)
        winner = min(
            CANONICAL_PALETTE.colors,
            key=lambda color: (_rgb_distance(source_rgb, color.rgb), color.index),
        )
        snapped.append(winner.id)
    return tuple(snapped)


def _weighted_subset_cost(source_ids: tuple[str, ...], frequencies: Mapping[str, int], retained: tuple[str, ...]) -> int:
    total = 0
    for source_id in source_ids:
        source_rgb = CANONICAL_PALETTE.rgb_for(source_id)
        nearest = min(_rgb_distance(source_rgb, CANONICAL_PALETTE.rgb_for(retained_id)) for retained_id in retained)
        total += frequencies[source_id] * nearest
    return total


def _nearest_retained(source_id: str, retained: tuple[str, ...]) -> str:
    source_rgb = CANONICAL_PALETTE.rgb_for(source_id)
    return min(
        retained,
        key=lambda retained_id: (_rgb_distance(source_rgb, CANONICAL_PALETTE.rgb_for(retained_id)), _palette_index(retained_id)),
    )


def enforce_difficulty_color_budget(
    difficulty: Difficulty | str,
    snapped_cells: Sequence[str],
) -> tuple[tuple[str, ...], Mapping[str, object]]:
    """Apply the owner-locked deterministic post-snap used-color budget."""

    try:
        selected = parse_difficulty(difficulty)
        used = actual_used_palette_ids(snapped_cells)
    except Exception as exc:
        raise SemanticLevelArtError("INVALID_LOGICAL_GRID", "palette-snapped cells are not canonical C-ID values") from exc
    minimum, maximum = PRODUCTION_COLOR_MIN, PRODUCTION_COLOR_MAX
    if len(used) < minimum:
        raise SemanticLevelArtError(
            "INSUFFICIENT_USED_COLORS",
            f"{selected.value} requires {minimum}..{maximum} distinct used colors; received {len(used)}",
        )
    frequencies = Counter(snapped_cells)
    if len(used) <= maximum:
        retained = used
        objective = 0
        final_cells = tuple(snapped_cells)
    else:
        candidates = tuple(combinations(used, maximum))
        retained = min(
            candidates,
            key=lambda subset: (_weighted_subset_cost(used, frequencies, subset), tuple(_palette_index(value) for value in subset)),
        )
        objective = _weighted_subset_cost(used, frequencies, retained)
        final_cells = tuple(value if value in retained else _nearest_retained(value, retained) for value in snapped_cells)
    try:
        final_used = validate_production_used_color_count(final_cells)
    except Exception as exc:
        raise SemanticLevelArtError("INVALID_DIFFICULTY_BUDGET", "final logical grid failed the canonical color-count contract") from exc
    return final_cells, MappingProxyType(
        {
            "original_used_palette_ids": used,
            "original_used_color_count": len(used),
            "retained_palette_ids": retained,
            "weighted_subset_cost": objective,
            "final_used_palette_ids": final_used,
            "final_used_color_count": len(final_used),
        }
    )


@dataclass(frozen=True, slots=True)
class SemanticLevelArtRequest:
    source_raw_artifact_digest: str
    difficulty: Difficulty | str
    target_width: int
    target_height: int
    cell_majority_policy_version: str = CELL_MAJORITY_POLICY_VERSION
    palette_snap_policy_version: str = PALETTE_SNAP_POLICY_VERSION
    difficulty_budget_policy_version: str = PRODUCTION_COLOR_ENVELOPE_POLICY_VERSION
    schema: str = LEVEL_ART_SCHEMA
    schema_version: int = LEVEL_ART_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_sha256(self.source_raw_artifact_digest, "source_raw_artifact_digest")
        try:
            selected = parse_difficulty(self.difficulty)
            validate_production_dimensions(self.target_width, self.target_height)
        except Exception as exc:
            raise SemanticLevelArtError("INVALID_DIFFICULTY_OR_DIMENSIONS", "difficulty and target dimensions are not legal") from exc
        if self.schema != LEVEL_ART_SCHEMA or self.schema_version != LEVEL_ART_SCHEMA_VERSION:
            raise SemanticLevelArtError("UNSUPPORTED_SCHEMA", "unsupported LEVEL_ART request schema/version")
        if self.cell_majority_policy_version != CELL_MAJORITY_POLICY_VERSION:
            raise SemanticLevelArtError("UNSUPPORTED_CELL_MAJORITY_POLICY", "unsupported CELL_MAJORITY policy version")
        if self.palette_snap_policy_version != PALETTE_SNAP_POLICY_VERSION:
            raise SemanticLevelArtError("UNSUPPORTED_PALETTE_SNAP_POLICY", "unsupported PALETTE_SNAP policy version")
        if self.difficulty_budget_policy_version != PRODUCTION_COLOR_ENVELOPE_POLICY_VERSION:
            raise SemanticLevelArtError("UNSUPPORTED_DIFFICULTY_BUDGET_POLICY", "unsupported difficulty-budget policy version")
        object.__setattr__(self, "difficulty", selected)

    @property
    def raw_artifact_digest(self) -> str:
        return self.source_raw_artifact_digest

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "source_raw_artifact_digest": self.source_raw_artifact_digest,
            "difficulty": self.difficulty.value,
            "target_dimensions": {"width": self.target_width, "height": self.target_height},
            "cell_majority_policy_version": self.cell_majority_policy_version,
            "palette_snap_policy_version": self.palette_snap_policy_version,
            "difficulty_budget_policy_version": self.difficulty_budget_policy_version,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _sha256(self.canonical_bytes())


@dataclass(frozen=True, slots=True)
class SemanticLevelArtReport:
    source_raw_artifact_digest: str
    raw_sha256: str
    request_digest: str
    difficulty: Difficulty | str
    raw_width: int
    raw_height: int
    target_width: int
    target_height: int
    cell_majority_policy_version: str
    palette_snap_policy_version: str
    difficulty_budget_policy_version: str
    majority_rgba_sha256: str
    snapped_grid_digest: str
    original_used_palette_ids: tuple[str, ...]
    original_used_color_count: int
    retained_palette_ids: tuple[str, ...]
    weighted_subset_cost: int
    final_used_palette_ids: tuple[str, ...]
    final_used_color_count: int
    final_logical_grid_digest: str
    status: LevelArtStatus | str = LevelArtStatus.SUCCESS
    schema: str = LEVEL_ART_REPORT_SCHEMA
    schema_version: int = LEVEL_ART_REPORT_VERSION
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _LEVEL_ART_REPORT_TOKEN:
            raise SemanticLevelArtError("UNSEALED_REPORT", "LEVEL_ART reports require canonical compiler construction")
        _require_sha256(self.source_raw_artifact_digest, "source_raw_artifact_digest")
        _require_sha256(self.raw_sha256, "raw_sha256")
        _require_sha256(self.request_digest, "request_digest")
        _require_sha256(self.majority_rgba_sha256, "majority_rgba_sha256")
        _require_sha256(self.snapped_grid_digest, "snapped_grid_digest")
        _require_sha256(self.final_logical_grid_digest, "final_logical_grid_digest")
        try:
            selected = parse_difficulty(self.difficulty)
            validate_production_dimensions(self.target_width, self.target_height)
            if type(self.raw_width) is not int or type(self.raw_height) is not int or not 1 <= self.raw_width <= SEMANTIC_RAW_RASTER_MAX_DIMENSION or not 1 <= self.raw_height <= SEMANTIC_RAW_RASTER_MAX_DIMENSION:
                raise ValueError("raw dimensions are invalid")
        except Exception as exc:
            raise SemanticLevelArtError("INVALID_REPORT", "LEVEL_ART report difficulty or dimensions are invalid") from exc
        if self.schema != LEVEL_ART_REPORT_SCHEMA or self.schema_version != LEVEL_ART_REPORT_VERSION:
            raise SemanticLevelArtError("UNSUPPORTED_REPORT_SCHEMA", "unsupported LEVEL_ART report schema/version")
        if (self.cell_majority_policy_version, self.palette_snap_policy_version, self.difficulty_budget_policy_version) != (CELL_MAJORITY_POLICY_VERSION, PALETTE_SNAP_POLICY_VERSION, PRODUCTION_COLOR_ENVELOPE_POLICY_VERSION):
            raise SemanticLevelArtError("UNSUPPORTED_POLICY", "LEVEL_ART report policy version is unsupported")
        for values in (self.original_used_palette_ids, self.retained_palette_ids, self.final_used_palette_ids):
            if not isinstance(values, tuple) or any(not isinstance(value, str) for value in values):
                raise SemanticLevelArtError("INVALID_REPORT", "LEVEL_ART report palette IDs are invalid")
            try:
                for value in values:
                    CANONICAL_PALETTE.validate_logical_id(value)
            except Exception as exc:
                raise SemanticLevelArtError("INVALID_REPORT", "LEVEL_ART report contains an off-palette ID") from exc
        if self.original_used_color_count != len(self.original_used_palette_ids) or self.final_used_color_count != len(self.final_used_palette_ids) or type(self.weighted_subset_cost) is not int or self.weighted_subset_cost < 0:
            raise SemanticLevelArtError("INVALID_REPORT", "LEVEL_ART report color counts or subset cost are inconsistent")
        status = self.status if isinstance(self.status, LevelArtStatus) else LevelArtStatus(self.status)
        object.__setattr__(self, "difficulty", selected)
        object.__setattr__(self, "status", status)
        if hasattr(self, "_construction_fingerprint"):
            self._assert_integrity()

    def _compute_fingerprint(self) -> str:
        return _canonical_digest({"report": self.canonical_dict()})

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _LEVEL_ART_REPORT_TOKEN:
            raise SemanticLevelArtError("UNSEALED_REPORT", "LEVEL_ART report construction seal is invalid")
        if getattr(self, "_construction_fingerprint", None) != self._compute_fingerprint():
            raise SemanticLevelArtError("TAMPERED_REPORT", "LEVEL_ART report construction fingerprint is invalid")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "source_raw_artifact_digest": self.source_raw_artifact_digest,
            "raw_sha256": self.raw_sha256,
            "request_digest": self.request_digest,
            "difficulty": self.difficulty.value,
            "raw_dimensions": {"width": self.raw_width, "height": self.raw_height},
            "target_dimensions": {"width": self.target_width, "height": self.target_height},
            "cell_majority_policy_version": self.cell_majority_policy_version,
            "palette_snap_policy_version": self.palette_snap_policy_version,
            "difficulty_budget_policy_version": self.difficulty_budget_policy_version,
            "majority_rgba_sha256": self.majority_rgba_sha256,
            "snapped_grid_digest": self.snapped_grid_digest,
            "original_used_palette_ids": list(self.original_used_palette_ids),
            "original_used_color_count": self.original_used_color_count,
            "retained_palette_ids": list(self.retained_palette_ids),
            "weighted_subset_cost": self.weighted_subset_cost,
            "final_used_palette_ids": list(self.final_used_palette_ids),
            "final_used_color_count": self.final_used_color_count,
            "final_logical_grid_digest": self.final_logical_grid_digest,
            "status": self.status.value,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        self._assert_integrity()
        return _sha256(self.canonical_bytes())


def _build_report(**values: object) -> SemanticLevelArtReport:
    values.setdefault("status", LevelArtStatus.SUCCESS)
    values.setdefault("schema", LEVEL_ART_REPORT_SCHEMA)
    values.setdefault("schema_version", LEVEL_ART_REPORT_VERSION)
    report = object.__new__(SemanticLevelArtReport)
    for name, value in values.items():
        object.__setattr__(report, name, value)
    object.__setattr__(report, "_construction_token", _LEVEL_ART_REPORT_TOKEN)
    report.__post_init__()
    object.__setattr__(report, "_construction_fingerprint", report._compute_fingerprint())
    report._assert_integrity()
    return report


@dataclass(frozen=True, slots=True)
class SemanticLevelArtArtifact:
    """Sealed immutable canonical LEVEL_ART logical-cell artifact."""

    source_raw_artifact_digest: str
    raw_sha256: str
    request_digest: str
    difficulty: Difficulty
    target_width: int
    target_height: int
    logical_cells: tuple[str, ...]
    used_palette_ids: tuple[str, ...]
    majority_rgba_sha256: str
    snapped_grid_digest: str
    final_logical_grid_digest: str
    report: SemanticLevelArtReport
    source_provenance: SemanticSourceProvenance
    schema: str = LEVEL_ART_SCHEMA
    schema_version: int = LEVEL_ART_SCHEMA_VERSION
    _construction_token: object = field(init=False, repr=False, compare=False)
    _construction_fingerprint: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if getattr(self, "_construction_token", None) is not _LEVEL_ART_ARTIFACT_TOKEN:
            raise SemanticLevelArtError("UNSEALED_ARTIFACT", "LEVEL_ART artifacts require checked construction")
        if self.schema != LEVEL_ART_SCHEMA or self.schema_version != LEVEL_ART_SCHEMA_VERSION:
            raise SemanticLevelArtError("UNSUPPORTED_SCHEMA", "unsupported LEVEL_ART artifact schema/version")
        try:
            selected = parse_difficulty(self.difficulty)
            validate_production_dimensions(self.target_width, self.target_height)
            used = actual_used_palette_ids(self.logical_cells)
            validate_production_used_color_count(self.logical_cells)
        except Exception as exc:
            raise SemanticLevelArtError("INVALID_ARTIFACT", "LEVEL_ART logical cells are not legal") from exc
        if not isinstance(self.logical_cells, tuple) or len(self.logical_cells) != self.target_width * self.target_height:
            raise SemanticLevelArtError("INVALID_ARTIFACT", "LEVEL_ART logical cells do not match target dimensions")
        if tuple(self.used_palette_ids) != used:
            raise SemanticLevelArtError("INVALID_ARTIFACT", "LEVEL_ART used palette declaration is not derived from cells")
        _require_sha256(self.source_raw_artifact_digest, "source_raw_artifact_digest")
        _require_sha256(self.raw_sha256, "raw_sha256")
        _require_sha256(self.request_digest, "request_digest")
        _require_sha256(self.majority_rgba_sha256, "majority_rgba_sha256")
        _require_sha256(self.snapped_grid_digest, "snapped_grid_digest")
        _require_sha256(self.final_logical_grid_digest, "final_logical_grid_digest")
        if not isinstance(self.report, SemanticLevelArtReport) or not isinstance(self.source_provenance, SemanticSourceProvenance):
            raise SemanticLevelArtError("INVALID_ARTIFACT", "LEVEL_ART report or source provenance is missing")
        self.report._assert_integrity()
        if (
            self.source_raw_artifact_digest != self.source_provenance.raw_artifact_digest
            or self.raw_sha256 != self.source_provenance.raw_sha256
            or self.request_digest != self.report.request_digest
            or self.source_raw_artifact_digest != self.report.source_raw_artifact_digest
            or self.difficulty is not self.report.difficulty
            or (self.report.raw_width, self.report.raw_height) != (self.source_provenance.returned_width, self.source_provenance.returned_height)
            or (self.target_width, self.target_height) != (self.report.target_width, self.report.target_height)
            or self.majority_rgba_sha256 != self.report.majority_rgba_sha256
            or self.snapped_grid_digest != self.report.snapped_grid_digest
            or self.final_logical_grid_digest != self.report.final_logical_grid_digest
            or self.used_palette_ids != self.report.final_used_palette_ids
            or _grid_digest(self.logical_cells) != self.final_logical_grid_digest
        ):
            raise SemanticLevelArtError("INVALID_ARTIFACT", "LEVEL_ART provenance/report/grid bindings do not match")
        object.__setattr__(self, "difficulty", selected)
        object.__setattr__(self, "logical_cells", tuple(self.logical_cells))
        object.__setattr__(self, "used_palette_ids", tuple(self.used_palette_ids))
        self.source_provenance._assert_integrity()
        if hasattr(self, "_construction_fingerprint"):
            self._assert_integrity()

    @classmethod
    def from_compilation(
        cls,
        raw_artifact: SemanticRawArtifact,
        request: SemanticLevelArtRequest,
        logical_cells: tuple[str, ...],
        majority_rgba_sha256: str,
        snapped_grid_digest: str,
        report: SemanticLevelArtReport,
    ) -> "SemanticLevelArtArtifact":
        # Retain the historical API name without retaining its assertion-based
        # trust capability: all caller-supplied stage facts are ignored and the
        # canonical compiler recomputes them from the typed source/request.
        del logical_cells, majority_rgba_sha256, snapped_grid_digest, report
        return compile_semantic_level_art(raw_artifact, request)

    def _compute_fingerprint(self) -> str:
        return _canonical_digest(
            {
                "source_provenance": self.source_provenance.digest(),
                "source_raw_artifact_digest": self.source_raw_artifact_digest,
                "raw_sha256": self.raw_sha256,
                "request_digest": self.request_digest,
                "difficulty": self.difficulty.value,
                "target_dimensions": [self.target_width, self.target_height],
                "logical_cells": list(self.logical_cells),
                "used_palette_ids": list(self.used_palette_ids),
                "majority_rgba_sha256": self.majority_rgba_sha256,
                "snapped_grid_digest": self.snapped_grid_digest,
                "report": self.report.digest(),
                "final_logical_grid_digest": self.final_logical_grid_digest,
            }
        )

    def _assert_integrity(self) -> None:
        if getattr(self, "_construction_token", None) is not _LEVEL_ART_ARTIFACT_TOKEN:
            raise SemanticLevelArtError("UNSEALED_ARTIFACT", "LEVEL_ART artifact construction seal is invalid")
        if getattr(self, "_construction_fingerprint", None) != self._compute_fingerprint():
            raise SemanticLevelArtError("TAMPERED_ARTIFACT", "LEVEL_ART artifact construction fingerprint is invalid")
        self.source_provenance._assert_integrity()

    @property
    def cells(self) -> tuple[str, ...]:
        return self.logical_cells

    @property
    def logical_grid(self) -> tuple[str, ...]:
        return self.logical_cells

    @property
    def logical_grid_digest(self) -> str:
        return self.final_logical_grid_digest

    @property
    def final_used_palette_ids(self) -> tuple[str, ...]:
        return self.used_palette_ids

    def identity_dict(self) -> dict[str, object]:
        self._assert_integrity()
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "source_raw_artifact_digest": self.source_raw_artifact_digest,
            "raw_sha256": self.raw_sha256,
            "request_digest": self.request_digest,
            "difficulty": self.difficulty.value,
            "target_dimensions": {"width": self.target_width, "height": self.target_height},
            "logical_cells": list(self.logical_cells),
            "used_palette_ids": list(self.used_palette_ids),
            "majority_rgba_sha256": self.majority_rgba_sha256,
            "snapped_grid_digest": self.snapped_grid_digest,
            "final_logical_grid_digest": self.final_logical_grid_digest,
            "report_digest": self.report.digest(),
            "source_provenance_digest": self.source_provenance.digest(),
        }

    def canonical_dict(self) -> dict[str, object]:
        return {**self.identity_dict(), "report": self.report.canonical_dict(), "source_provenance": self.source_provenance.canonical_dict()}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _sha256(_canonical_bytes(self.identity_dict()))


def _build_artifact(
    raw_artifact: SemanticRawArtifact,
    request: SemanticLevelArtRequest,
    logical_cells: tuple[str, ...],
    majority_rgba_sha256: str,
    snapped_grid_digest: str,
    report: SemanticLevelArtReport,
) -> SemanticLevelArtArtifact:
    if not isinstance(raw_artifact, SemanticRawArtifact) or not isinstance(request, SemanticLevelArtRequest):
        raise SemanticLevelArtError("INVALID_INPUT", "LEVEL_ART compilation requires typed raw artifact and request")
    if request.source_raw_artifact_digest != raw_artifact.digest():
        raise SemanticLevelArtError("SOURCE_PROVENANCE_MISMATCH", "LEVEL_ART request is not bound to the raw artifact")
    if not isinstance(report, SemanticLevelArtReport):
        raise SemanticLevelArtError("INVALID_REPORT", "LEVEL_ART compiler produced no trusted report")
    source = SemanticSourceProvenance.from_raw_artifact(raw_artifact)
    instance = object.__new__(SemanticLevelArtArtifact)
    values = {
        "source_raw_artifact_digest": source.raw_artifact_digest,
        "raw_sha256": source.raw_sha256,
        "request_digest": request.digest(),
        "difficulty": request.difficulty,
        "target_width": request.target_width,
        "target_height": request.target_height,
        "logical_cells": tuple(logical_cells),
        "used_palette_ids": tuple(report.final_used_palette_ids),
        "majority_rgba_sha256": majority_rgba_sha256,
        "snapped_grid_digest": snapped_grid_digest,
        "final_logical_grid_digest": report.final_logical_grid_digest,
        "report": report,
        "source_provenance": source,
        "schema": LEVEL_ART_SCHEMA,
        "schema_version": LEVEL_ART_SCHEMA_VERSION,
    }
    for name, value in values.items():
        object.__setattr__(instance, name, value)
    object.__setattr__(instance, "_construction_token", _LEVEL_ART_ARTIFACT_TOKEN)
    instance.__post_init__()
    object.__setattr__(instance, "_construction_fingerprint", instance._compute_fingerprint())
    instance._assert_integrity()
    return instance


def compile_semantic_level_art(raw_artifact: SemanticRawArtifact, request: SemanticLevelArtRequest) -> SemanticLevelArtArtifact:
    """Compile one immutable raw semantic PNG into canonical logical LEVEL_ART."""

    if not isinstance(raw_artifact, SemanticRawArtifact) or not isinstance(request, SemanticLevelArtRequest):
        raise SemanticLevelArtError("INVALID_INPUT", "LEVEL_ART compilation requires typed raw artifact and request")
    if request.source_raw_artifact_digest != raw_artifact.digest():
        raise SemanticLevelArtError("SOURCE_PROVENANCE_MISMATCH", "LEVEL_ART request is not bound to the raw artifact")
    try:
        decoded = _decode_raw(raw_artifact.raw_bytes, raw_artifact.media_type)
    except Exception as exc:
        raise SemanticLevelArtError("SOURCE_DECODE_FAILED", "raw semantic source could not be decoded") from exc
    if (decoded.width, decoded.height) != (raw_artifact.returned_width, raw_artifact.returned_height):
        raise SemanticLevelArtError("SOURCE_DIMENSION_MISMATCH", "decoded dimensions do not match raw artifact dimensions")
    try:
        majority = cell_majority_rgba_grid(decoded.pixels, decoded.width, decoded.height, request.target_width, request.target_height)
        majority_bytes = b"".join(majority)
        snapped = palette_snap_grid(majority)
        snapped_digest = _grid_digest(snapped)
        logical_cells, budget = enforce_difficulty_color_budget(request.difficulty, snapped)
        final_digest = _grid_digest(logical_cells)
    except SemanticLevelArtError:
        raise
    except Exception as exc:
        raise SemanticLevelArtError("COMPILATION_FAILED", "LEVEL_ART compilation failed closed") from exc
    report = _build_report(
        source_raw_artifact_digest=raw_artifact.digest(),
        raw_sha256=raw_artifact.raw_sha256,
        request_digest=request.digest(),
        difficulty=request.difficulty,
        raw_width=decoded.width,
        raw_height=decoded.height,
        target_width=request.target_width,
        target_height=request.target_height,
        cell_majority_policy_version=request.cell_majority_policy_version,
        palette_snap_policy_version=request.palette_snap_policy_version,
        difficulty_budget_policy_version=request.difficulty_budget_policy_version,
        majority_rgba_sha256=_sha256(majority_bytes),
        snapped_grid_digest=snapped_digest,
        original_used_palette_ids=tuple(budget["original_used_palette_ids"]),  # type: ignore[arg-type]
        original_used_color_count=int(budget["original_used_color_count"]),
        retained_palette_ids=tuple(budget["retained_palette_ids"]),  # type: ignore[arg-type]
        weighted_subset_cost=int(budget["weighted_subset_cost"]),
        final_used_palette_ids=tuple(budget["final_used_palette_ids"]),  # type: ignore[arg-type]
        final_used_color_count=int(budget["final_used_color_count"]),
        final_logical_grid_digest=final_digest,
    )
    return _build_artifact(raw_artifact, request, logical_cells, _sha256(majority_bytes), snapped_digest, report)


compile_level_art = compile_semantic_level_art


class SemanticLevelArtCompiler:
    """Discoverable stateless facade for the LEVEL_ART compiler."""

    @staticmethod
    def compile(raw_artifact: SemanticRawArtifact, request: SemanticLevelArtRequest) -> SemanticLevelArtArtifact:
        return compile_semantic_level_art(raw_artifact, request)


__all__ = [
    "CELL_MAJORITY_POLICY_VERSION",
    "DIFFICULTY_BUDGET_POLICY_VERSION",
    "LEVEL_ART_REPORT_SCHEMA",
    "LEVEL_ART_REPORT_VERSION",
    "LEVEL_ART_SCHEMA",
    "LEVEL_ART_SCHEMA_VERSION",
    "LevelArtStatus",
    "PALETTE_SNAP_POLICY_VERSION",
    "SemanticLevelArtArtifact",
    "SemanticLevelArtCompiler",
    "SemanticLevelArtError",
    "SemanticLevelArtReport",
    "SemanticLevelArtRequest",
    "cell_majority_rgba_grid",
    "compile_level_art",
    "compile_semantic_level_art",
    "enforce_difficulty_color_budget",
    "palette_snap_grid",
]
