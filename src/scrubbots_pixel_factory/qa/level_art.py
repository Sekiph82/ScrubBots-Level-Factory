"""Fact-only validation of the final logical LEVEL_ART contract."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import hashlib
import json

from ..contracts import CANONICAL_PALETTE
from ..contracts.production import validate_production_dimensions, validate_production_used_color_count
from .unified import AuthorityIdentity, LevelDataIdentity, QAContractError, StageDisposition, _canonical_bytes, _digest, _sha


LEVEL_ART_VALIDATION_SCHEMA = "scrubbots-level-art-contract-validation"
LEVEL_ART_VALIDATION_VERSION = 1
LEVEL_ART_REJECTION_CODES = frozenset(
    {
        "ILLEGAL_DIMENSIONS",
        "CELL_COUNT_MISMATCH",
        "FOREIGN_LOGICAL_COLOR",
        "USED_COLOR_COUNT",
        "PALETTE_INDEX_MISMATCH",
        "SEMI_ALPHA_FINAL_CELL",
        "TRANSPARENT_FINAL_CELL",
        "PROVENANCE_MISSING",
        "PROVENANCE_STALE",
        "LEVEL_DATA_DIMENSION_MISMATCH",
        "DUPLICATE_LEVEL_ID",
    }
)


def _read(value: object, *names: str, default: object = None) -> object:
    for name in names:
        if isinstance(value, Mapping) and name in value:
            return value[name]
        if hasattr(value, name):
            return getattr(value, name)
    return default


def _maybe_sha(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _sha(value, label)


@dataclass(frozen=True, slots=True)
class LevelArtValidationReport:
    disposition: StageDisposition
    level_id: str | None
    rejection_codes: tuple[str, ...]
    facts: Mapping[str, object]
    source_sha256: str | None
    level_data_digest: str | None
    artifact_digest: str | None
    authority: AuthorityIdentity
    schema: str = LEVEL_ART_VALIDATION_SCHEMA
    version: int = LEVEL_ART_VALIDATION_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, StageDisposition) or not isinstance(self.authority, AuthorityIdentity):
            raise QAContractError("LEVEL_ART validation identity is malformed")
        if self.level_id is not None and (type(self.level_id) is not str or not self.level_id.strip()):
            raise QAContractError("LEVEL_ART level_id is malformed")
        if type(self.rejection_codes) is not tuple or any(code not in LEVEL_ART_REJECTION_CODES for code in self.rejection_codes):
            raise QAContractError("LEVEL_ART rejection code catalog is malformed")
        if self.schema != LEVEL_ART_VALIDATION_SCHEMA or self.version != LEVEL_ART_VALIDATION_VERSION:
            raise QAContractError("unsupported LEVEL_ART validation schema/version")
        for value, label in ((self.source_sha256, "source SHA-256"), (self.level_data_digest, "Level Data digest"), (self.artifact_digest, "artifact digest")):
            if value is not None:
                _sha(value, label)

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "version": self.version,
            "disposition": self.disposition.value,
            "level_id": self.level_id,
            "rejection_codes": list(self.rejection_codes),
            "facts": dict(self.facts),
            "source_sha256": self.source_sha256,
            "level_data_digest": self.level_data_digest,
            "artifact_digest": self.artifact_digest,
            "authority": self.authority.canonical_dict(),
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def validate_level_art(
    artifact: object,
    *,
    level_data: LevelDataIdentity | None,
    source_sha256: str | None = None,
    catalog_level_ids: Iterable[str] = (),
    authority: AuthorityIdentity | None = None,
) -> LevelArtValidationReport:
    """Return immutable facts/reasons; never transform the supplied artifact."""

    selected_authority = authority or AuthorityIdentity("https://github.com/Sekiph82/ScrubBots-Level-Factory", "UNAVAILABLE", "src/scrubbots_pixel_factory/qa/level_art.py", "LEVEL_ART_VALIDATION_V1")
    codes: set[str] = set()
    facts: dict[str, object] = {}
    level_id_value = _read(artifact, "level_id", "candidate_id")
    level_id = str(level_id_value) if level_id_value is not None else None
    width = _read(artifact, "target_width", "width")
    height = _read(artifact, "target_height", "height")
    cells_value = _read(artifact, "logical_cells", "cells")
    try:
        width_int, height_int = int(width), int(height)
        cells = tuple(cells_value) if not isinstance(cells_value, (str, bytes, bytearray)) else ()
    except (TypeError, ValueError):
        width_int, height_int, cells = 0, 0, ()
    facts.update({"width": width_int, "height": height_int, "cell_count": len(cells)})
    try:
        validate_production_dimensions(width_int, height_int)
    except (TypeError, ValueError):
        codes.add("ILLEGAL_DIMENSIONS")
    if len(cells) != width_int * height_int:
        codes.add("CELL_COUNT_MISMATCH")
    try:
        used = CANONICAL_PALETTE.used_ids(cells)
    except (TypeError, ValueError):
        used = ()
        if cells:
            codes.add("FOREIGN_LOGICAL_COLOR")
    facts["used_palette_ids"] = list(used)
    facts["used_color_count"] = len(used)
    try:
        validate_production_used_color_count(cells)
    except (TypeError, ValueError):
        codes.add("USED_COLOR_COUNT")
    declared_palette = _read(artifact, "used_palette_ids", "palette")
    try:
        if tuple(declared_palette) != used:
            codes.add("PALETTE_INDEX_MISMATCH")
    except TypeError:
        codes.add("PALETTE_INDEX_MISMATCH")
    indices = _read(artifact, "palette_indices", "cell_palette_indices")
    if indices is not None:
        try:
            expected = tuple(CANONICAL_PALETTE.color(cell).index for cell in cells)
            if tuple(indices) != expected:
                codes.add("PALETTE_INDEX_MISMATCH")
        except (TypeError, ValueError):
            codes.add("PALETTE_INDEX_MISMATCH")
    alpha = _read(artifact, "logical_alpha", "alpha", default=None)
    if alpha is not None:
        try:
            alpha_values = tuple(alpha)
            if len(alpha_values) != len(cells):
                codes.add("CELL_COUNT_MISMATCH")
            if any(value == 0 for value in alpha_values):
                codes.add("TRANSPARENT_FINAL_CELL")
            if any(type(value) is not int or value not in (0, 255) for value in alpha_values):
                codes.add("SEMI_ALPHA_FINAL_CELL")
        except TypeError:
            codes.add("SEMI_ALPHA_FINAL_CELL")

    expected_source = _maybe_sha(source_sha256, "source_sha256") if source_sha256 is not None else None
    artifact_source = _read(artifact, "raw_sha256", "source_sha256")
    provenance = _read(artifact, "source_provenance", default=None)
    provenance_source = _read(provenance, "raw_sha256", "source_sha256", default=None) if provenance is not None else None
    if expected_source is None and level_data is not None:
        expected_source = level_data.source_sha256
    if expected_source is None or artifact_source is None or provenance_source is None:
        codes.add("PROVENANCE_MISSING")
    else:
        try:
            artifact_source_sha = _sha(artifact_source, "artifact raw_sha256")
            provenance_source_sha = _sha(provenance_source, "source provenance raw_sha256")
            if artifact_source_sha != expected_source or provenance_source_sha != expected_source:
                codes.add("PROVENANCE_STALE")
        except QAContractError:
            codes.add("PROVENANCE_STALE")
    if level_data is None:
        codes.add("PROVENANCE_MISSING")
        level_data_digest = None
    else:
        level_data_digest = level_data.digest()
        if (width_int, height_int) != (level_data.width, level_data.height):
            codes.add("LEVEL_DATA_DIMENSION_MISMATCH")
    if level_id is not None and level_id in set(catalog_level_ids):
        codes.add("DUPLICATE_LEVEL_ID")
    artifact_digest_value = _read(artifact, "digest", default=None)
    artifact_digest = artifact_digest_value() if callable(artifact_digest_value) else None
    if artifact_digest is not None:
        try:
            _sha(artifact_digest, "artifact digest")
        except QAContractError:
            artifact_digest = None
            codes.add("PROVENANCE_STALE")
    facts["provenance_bound"] = "PROVENANCE_MISSING" not in codes and "PROVENANCE_STALE" not in codes
    facts["source_alpha_is_not_final_alpha"] = True
    disposition = StageDisposition.PASS if not codes else StageDisposition.FAIL
    return LevelArtValidationReport(disposition, level_id, tuple(sorted(codes)), facts, expected_source, level_data_digest, artifact_digest, selected_authority)


class LevelArtContractValidator:
    """Named façade retained for callers that prefer an object boundary."""

    @staticmethod
    def validate(artifact: object, **kwargs: object) -> LevelArtValidationReport:
        return validate_level_art(artifact, **kwargs)  # type: ignore[arg-type]


__all__ = [
    "LEVEL_ART_REJECTION_CODES",
    "LEVEL_ART_VALIDATION_SCHEMA",
    "LEVEL_ART_VALIDATION_VERSION",
    "LevelArtContractValidator",
    "LevelArtValidationReport",
    "validate_level_art",
]
