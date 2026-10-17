from __future__ import annotations

import hashlib
import json

from scrubbots_pixel_factory.supply_pipeline.current_game_contract import (
    CurrentGameContractDisposition as Disposition,
    REQUIRED_SOURCE_PATHS,
    evaluate_current_game_contract,
)


_COMMIT = "1" * 40


def _fixture_sources() -> dict[str, bytes]:
    contents = {
        "docs/01_GAMEPLAY_SPEC.md": b"Production board 20..59; rectangular boards allowed. C01..C16.",
        "docs/03_LEVEL_DATA_SPEC.md": (
            b"width: 20..59; height: 20..59; rectangular boards allowed. "
            b"Supply conservation, WIN (all non-VOID cells cleared), solver and Difficulty V1 measurements use artwork cells only."
        ),
        "scripts/data/level_data.gd": (
            b"const FORMAT_VERSION := 1\nconst FORMAT_VERSION_VOID := 2\nconst VOID_CELL := -1\n"
            b"func is_void(index: int) -> bool:\n\treturn version == FORMAT_VERSION_VOID and cells[index] == VOID_CELL\n"
        ),
        "scripts/data/level_loader.gd": b"const LevelValidator = preload(\"level_validator.gd\")\nstatic func load_from_text(text: String):\n",
        "scripts/gameplay/supply/supply_plan_loader.gd": (
            b"## The plan's 3, 4 or 5 FIFO columns\nconst MIN_COLUMNS := 3\nconst MAX_COLUMNS := 5\n"
            b"const VISIBLE_PREVIEW_DEPTH := 3\n"
        ),
        "scripts/gameplay/solver/proof_state.gd": b"# VOID cells (ADR-030) start CLEARED\n",
        "scripts/difficulty/level_difficulty_analyzer_v1.gd": b"var cells: int = level.get_artwork_cell_count()\n",
        "data/palettes/scrubbots_palette_v3.json": json.dumps(
            {"schema": "scrubbots-global-palette/v3", "colors": [{"id": f"C{i:02d}"} for i in range(1, 17)]},
            separators=(",", ":"),
        ).encode(),
    }
    assert tuple(contents) == REQUIRED_SOURCE_PATHS
    return contents


def _authority(source_bytes: dict[str, bytes]) -> dict[str, object]:
    return {
        "repository": "Sekiph82/Scrubbots",
        "branch": "main",
        "commit": _COMMIT,
        "main_commit": _COMMIT,
        "source_commit_verified_as_main": True,
        "source_sha256": {path: hashlib.sha256(raw).hexdigest() for path, raw in source_bytes.items()},
    }


def test_current_game_contract_accepts_v1_v2_void_and_fifo_3_to_5() -> None:
    source_bytes = _fixture_sources()
    report = evaluate_current_game_contract(authority=_authority(source_bytes), source_bytes=source_bytes)

    assert report.disposition is Disposition.CURRENT_SOURCE_COMPATIBLE
    assert report.compatible is True
    assert report.contract["level_data"] == {"versions": [1, 2], "void_version": 2, "void_value": -1}
    assert report.contract["supply"] == {"fifo_columns": {"minimum": 3, "maximum": 5}, "visible_preview_depth": 3}
    assert report.contract["global_palette_ids"] == [f"C{i:02d}" for i in range(1, 17)]
    assert len(report.source_sha256) == len(REQUIRED_SOURCE_PATHS)
    assert report.to_dict()["runtime_executed"] is False


def test_contract_fails_closed_when_source_bytes_do_not_match_inventory() -> None:
    source_bytes = _fixture_sources()
    authority = _authority(source_bytes)
    source_bytes["scripts/data/level_data.gd"] = source_bytes["scripts/data/level_data.gd"] + b"# changed"

    report = evaluate_current_game_contract(authority=authority, source_bytes=source_bytes)

    assert report.disposition is Disposition.SOURCE_HASH_MISMATCH
    assert report.compatible is False


def test_contract_distinguishes_stale_or_unattested_main() -> None:
    source_bytes = _fixture_sources()
    stale = _authority(source_bytes)
    stale["main_commit"] = "2" * 40
    stale_report = evaluate_current_game_contract(authority=stale, source_bytes=source_bytes)
    assert stale_report.disposition is Disposition.SOURCE_VERSION_DRIFT

    unattested = _authority(source_bytes)
    unattested["source_commit_verified_as_main"] = False
    unverified_report = evaluate_current_game_contract(authority=unattested, source_bytes=source_bytes)
    assert unverified_report.disposition is Disposition.CURRENT_GAME_UNVERIFIED


def test_contract_reports_missing_inputs_and_semantic_drift() -> None:
    missing = evaluate_current_game_contract(authority=None, source_bytes=None)
    assert missing.disposition is Disposition.CURRENT_GAME_UNVERIFIED

    source_bytes = _fixture_sources()
    source_bytes["scripts/gameplay/supply/supply_plan_loader.gd"] = b"const MIN_COLUMNS := 2\nconst MAX_COLUMNS := 5\nconst VISIBLE_PREVIEW_DEPTH := 3\n"
    report = evaluate_current_game_contract(authority=_authority(source_bytes), source_bytes=source_bytes)
    assert report.disposition is Disposition.CURRENT_GAME_CONTRACT_DRIFT
    assert "CONTRACT_FIELD_MISMATCH:fifo_columns" in report.reason_codes
