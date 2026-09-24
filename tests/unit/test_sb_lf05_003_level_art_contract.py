from __future__ import annotations

from types import SimpleNamespace

from scrubbots_pixel_factory.qa import AuthorityIdentity, LevelDataIdentity, StageDisposition, validate_level_art


SOURCE_SHA = "a" * 64
AUTHORITY = AuthorityIdentity("https://github.com/Sekiph82/ScrubBots-Level-Factory", "c" * 40, "qa/level_art.py", "LEVEL_ART_VALIDATION_V1")


def _level_data(width: int = 20, height: int = 20) -> LevelDataIdentity:
    return LevelDataIdentity.from_mapping("level-003", SOURCE_SHA, {"cells": width * height}, width, height)


def _artifact(width: int = 20, height: int = 20, colors: tuple[str, ...] = ("C01", "C02", "C03"), **extra: object) -> SimpleNamespace:
    cells = tuple(colors[index % len(colors)] for index in range(width * height))
    values = {"level_id": "level-003", "width": width, "height": height, "cells": cells, "palette": tuple(colors), "raw_sha256": SOURCE_SHA, "source_provenance": SimpleNamespace(raw_sha256=SOURCE_SHA)}
    values.update(extra)
    return SimpleNamespace(**values)


def test_current_rectangular_bounds_and_lineage_are_legal_without_class_bands() -> None:
    for width, height in ((20, 59), (59, 20)):
        report = validate_level_art(_artifact(width, height), level_data=_level_data(width, height), authority=AUTHORITY)
        assert report.disposition is StageDisposition.PASS
        assert report.rejection_codes == ()


def test_illegal_dimensions_colors_alpha_indices_and_duplicate_id_are_facts_only() -> None:
    report = validate_level_art(
        _artifact(19, 20, ("C01", "C02"), logical_alpha=(255,) * 399 + (128,), palette_indices=(99,) * 380),
        level_data=_level_data(19, 20),
        catalog_level_ids=("level-003",),
        authority=AUTHORITY,
    )
    assert report.disposition is StageDisposition.FAIL
    assert {"ILLEGAL_DIMENSIONS", "USED_COLOR_COUNT", "SEMI_ALPHA_FINAL_CELL", "PALETTE_INDEX_MISMATCH", "DUPLICATE_LEVEL_ID"}.issubset(report.rejection_codes)


def test_source_and_provenance_mismatch_is_rejected_without_repair() -> None:
    artifact = _artifact(raw_sha256="e" * 64)
    before = artifact.cells
    report = validate_level_art(artifact, level_data=_level_data(), source_sha256=SOURCE_SHA, authority=AUTHORITY)
    assert report.disposition is StageDisposition.FAIL
    assert "PROVENANCE_STALE" in report.rejection_codes
    assert artifact.cells == before
