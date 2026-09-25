"""Fact-only validation of final logical LEVEL_ART and its complete lineage."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import hashlib
import json

from ..contracts import CANONICAL_PALETTE
from ..contracts.production import validate_production_dimensions, validate_production_used_color_count
from .unified import AuthorityIdentity, LevelDataIdentity, QAContractError, StageDisposition, _canonical_bytes, _sha

LEVEL_ART_VALIDATION_SCHEMA = "scrubbots-level-art-contract-validation"
LEVEL_ART_VALIDATION_VERSION = 2
LEVEL_ART_REJECTION_CODES = frozenset({
    "ILLEGAL_DIMENSIONS", "CELL_COUNT_MISMATCH", "FOREIGN_LOGICAL_COLOR", "USED_COLOR_COUNT", "PALETTE_INDEX_MISMATCH",
    "SEMI_ALPHA_FINAL_CELL", "TRANSPARENT_FINAL_CELL", "FINAL_OPACITY_MISSING", "PROVENANCE_MISSING", "PROVENANCE_STALE",
    "LEVEL_DATA_DIMENSION_MISMATCH", "LEVEL_DATA_LINEAGE_MISMATCH", "COMPILER_LINEAGE_MISMATCH", "DUPLICATE_LEVEL_ID",
})


def _read(value: object, *names: str, default: object = None) -> object:
    for name in names:
        if isinstance(value, Mapping) and name in value:
            return value[name]
        if hasattr(value, name):
            return getattr(value, name)
    return default


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
        return {"schema": self.schema, "version": self.version, "disposition": self.disposition.value, "level_id": self.level_id, "rejection_codes": list(self.rejection_codes), "facts": dict(self.facts), "source_sha256": self.source_sha256, "level_data_digest": self.level_data_digest, "artifact_digest": self.artifact_digest, "authority": self.authority.canonical_dict()}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _exact_dimension(value: object) -> bool:
    return type(value) is int


def _sha_or_none(value: object) -> str | None:
    if value is None:
        return None
    return _sha(value, "provenance SHA-256")


def validate_level_art(artifact: object, *, level_data: LevelDataIdentity | None, source_sha256: str | None = None, catalog_level_ids: Iterable[str] = (), authority: AuthorityIdentity | None = None) -> LevelArtValidationReport:
    """Validate facts only; never repair, resize, recolor, or rewrite the artifact."""

    selected_authority = authority or AuthorityIdentity("https://github.com/Sekiph82/ScrubBots-Level-Factory", "UNAVAILABLE", "src/scrubbots_pixel_factory/qa/level_art.py", "LEVEL_ART_VALIDATION_V2")
    codes: set[str] = set()
    facts: dict[str, object] = {}
    raw_level_id = _read(artifact, "level_id", "candidate_id")
    level_id = raw_level_id if type(raw_level_id) is str and raw_level_id.strip() else None
    width, height = _read(artifact, "target_width", "width"), _read(artifact, "target_height", "height")
    cells_value = _read(artifact, "logical_cells", "cells")
    if not _exact_dimension(width) or not _exact_dimension(height):
        codes.add("ILLEGAL_DIMENSIONS")
        width_int = width if _exact_dimension(width) else 0
        height_int = height if _exact_dimension(height) else 0
    else:
        width_int, height_int = width, height
    cells = tuple(cells_value) if isinstance(cells_value, (tuple, list)) else ()
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
    palette_value = _read(artifact, "used_palette_ids", "palette")
    declared_palette = tuple(palette_value) if isinstance(palette_value, (tuple, list)) else ()
    if declared_palette != used or len(set(declared_palette)) != len(declared_palette):
        codes.add("PALETTE_INDEX_MISMATCH")
    indices = _read(artifact, "palette_indices", "cell_palette_indices")
    if not isinstance(indices, (tuple, list)) or len(indices) != len(cells):
        codes.add("PALETTE_INDEX_MISMATCH")
    elif declared_palette and tuple(indices) != tuple(declared_palette.index(cell) if cell in declared_palette else -1 for cell in cells):
        codes.add("PALETTE_INDEX_MISMATCH")
    alpha = _read(artifact, "logical_alpha", "alpha", "final_alpha", default=None)
    if alpha is None:
        codes.add("FINAL_OPACITY_MISSING")
    else:
        alpha_values = tuple(alpha) if isinstance(alpha, (tuple, list)) else ()
        if len(alpha_values) != len(cells):
            codes.add("CELL_COUNT_MISMATCH")
        if any(type(value) is not int or value < 0 or value > 255 or value not in (0, 255) for value in alpha_values):
            codes.add("SEMI_ALPHA_FINAL_CELL")
        if any(value == 0 for value in alpha_values):
            codes.add("TRANSPARENT_FINAL_CELL")

    expected_source = _sha(source_sha256, "source_sha256") if source_sha256 is not None else (level_data.source_sha256 if level_data is not None else None)
    artifact_source = _read(artifact, "raw_sha256", "source_sha256")
    provenance = _read(artifact, "source_provenance", default=None)
    provenance_source = _read(provenance, "raw_sha256", "source_sha256", default=None)
    try:
        if expected_source is None or artifact_source is None or provenance_source is None or _sha(artifact_source, "artifact source SHA-256") != expected_source or _sha(provenance_source, "source provenance SHA-256") != expected_source:
            codes.add("PROVENANCE_MISSING" if expected_source is None or artifact_source is None or provenance_source is None else "PROVENANCE_STALE")
    except QAContractError:
        codes.add("PROVENANCE_STALE")
    level_data_digest = level_data.digest() if level_data is not None else None
    if level_data is None:
        codes.add("PROVENANCE_MISSING")
    else:
        if (width_int, height_int) != (level_data.width, level_data.height):
            codes.add("LEVEL_DATA_DIMENSION_MISMATCH")
        declared_level_data_sha = _read(artifact, "level_data_sha256", "level_data_digest")
        if declared_level_data_sha is None:
            codes.add("LEVEL_DATA_LINEAGE_MISMATCH")
        else:
            try:
                if _sha(declared_level_data_sha, "artifact LevelData SHA-256") != level_data.level_data_sha256:
                    codes.add("LEVEL_DATA_LINEAGE_MISMATCH")
            except QAContractError:
                codes.add("LEVEL_DATA_LINEAGE_MISMATCH")
    compiler_sha = _read(artifact, "compiler_artifact_sha256", "compiler_sha256")
    compiler_source = _read(artifact, "compiler_source_sha256")
    compiler_level_data = _read(artifact, "compiler_level_data_sha256")
    if compiler_sha is None or compiler_source is None or compiler_level_data is None:
        codes.add("COMPILER_LINEAGE_MISMATCH")
    else:
        try:
            if _sha(compiler_source, "compiler source SHA-256") != expected_source or _sha(compiler_level_data, "compiler LevelData SHA-256") != (level_data.level_data_sha256 if level_data else None):
                codes.add("COMPILER_LINEAGE_MISMATCH")
            _sha(compiler_sha, "compiler artifact SHA-256")
        except QAContractError:
            codes.add("COMPILER_LINEAGE_MISMATCH")
    # Hashes alone are insufficient: when the exact serialized LevelData
    # carries cells/palette, every compiler/LevelData fact must cross-bind.
    payload = None
    if level_data is not None and level_data.level_data_bytes:
        try:
            decoded = json.loads(level_data.level_data_bytes.decode("utf-8"))
            payload = decoded if isinstance(decoded, Mapping) else None
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = None
    if payload is not None and isinstance(payload.get("cells"), list):
        expected_level_cells = tuple(payload["cells"])
        expected_level_palette = tuple(dict.fromkeys(expected_level_cells))
        expected_dimensions = (payload.get("width"), payload.get("height"))
        compiler_dimensions = _read(artifact, "compiler_dimensions")
        level_dimensions = _read(artifact, "level_data_dimensions")
        compiler_palette = _read(artifact, "compiler_palette")
        level_palette = _read(artifact, "level_data_palette")
        compiler_cells = _read(artifact, "compiler_cells")
        level_cells = _read(artifact, "level_data_cells")
        if compiler_dimensions != {"width": expected_dimensions[0], "height": expected_dimensions[1]} or level_dimensions != {"width": expected_dimensions[0], "height": expected_dimensions[1]} or tuple(compiler_palette or ()) != expected_level_palette or tuple(level_palette or ()) != expected_level_palette or tuple(compiler_cells or ()) != expected_level_cells or tuple(level_cells or ()) != expected_level_cells:
            codes.add("COMPILER_LINEAGE_MISMATCH")
    if level_id is not None and level_id in set(catalog_level_ids):
        codes.add("DUPLICATE_LEVEL_ID")
    artifact_digest_value = _read(artifact, "digest", default=None)
    artifact_digest = artifact_digest_value() if callable(artifact_digest_value) else artifact_digest_value
    if artifact_digest is not None:
        try:
            _sha(artifact_digest, "artifact digest")
        except QAContractError:
            artifact_digest = None
            codes.add("PROVENANCE_STALE")
    facts.update({"provenance_bound": not bool(codes & {"PROVENANCE_MISSING", "PROVENANCE_STALE", "LEVEL_DATA_LINEAGE_MISMATCH", "COMPILER_LINEAGE_MISMATCH"}), "final_opacity_authoritative": "FINAL_OPACITY_MISSING" not in codes})
    return LevelArtValidationReport(StageDisposition.PASS if not codes else StageDisposition.FAIL, level_id, tuple(sorted(codes)), facts, expected_source, level_data_digest, artifact_digest, selected_authority)


class LevelArtContractValidator:
    @staticmethod
    def validate(artifact: object, **kwargs: object) -> LevelArtValidationReport:
        return validate_level_art(artifact, **kwargs)  # type: ignore[arg-type]


__all__ = ["LEVEL_ART_REJECTION_CODES", "LEVEL_ART_VALIDATION_SCHEMA", "LEVEL_ART_VALIDATION_VERSION", "LevelArtContractValidator", "LevelArtValidationReport", "validate_level_art"]
