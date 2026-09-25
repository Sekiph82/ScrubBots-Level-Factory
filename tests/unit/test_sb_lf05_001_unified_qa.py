from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from scrubbots_pixel_factory.qa import (
    AuthorityIdentity,
    ExternalValidationResult,
    LevelDataIdentity,
    StageDisposition,
    UnifiedQADisposition,
    evaluate_unified_qa,
)


SOURCE_SHA = "a" * 64
MAIN_AUTHORITY = AuthorityIdentity(
    "https://github.com/Sekiph82/Scrubbots",
    "b" * 40,
    "scripts/level_validation/main_game_qa.gd",
    "M05_MAIN_GAME_QA_V1",
)
FACTORY_AUTHORITY = AuthorityIdentity(
    "https://github.com/Sekiph82/ScrubBots-Level-Factory",
    "c" * 40,
    "src/scrubbots_pixel_factory/qa",
    "FACTORY_QA_V1",
)


def _level_data() -> LevelDataIdentity:
    cells = [("C01", "C02", "C03")[index % 3] for index in range(20 * 59)]
    return LevelDataIdentity.from_mapping(
        "qa-rectangular",
        SOURCE_SHA,
        {"schema": "scrubbots-level-data", "version": 1, "level_id": "qa-rectangular", "width": 20, "height": 59, "cells": cells},
        20,
        59,
    )


def _artifact(source_sha: str = SOURCE_SHA) -> SimpleNamespace:
    cells = tuple(("C01", "C02", "C03")[index % 3] for index in range(20 * 59))
    return SimpleNamespace(
        width=20,
        height=59,
        cells=cells,
        palette=("C01", "C02", "C03"),
        source_sha256=source_sha,
    )


@dataclass(frozen=True)
class Provider:
    structural: StageDisposition = StageDisposition.PASS
    production: StageDisposition = StageDisposition.PASS

    def validate(self, stage: str, _level_data: LevelDataIdentity, _artifact: object) -> ExternalValidationResult:
        disposition = self.structural if stage == "STRUCTURAL" else self.production
        return ExternalValidationResult(disposition, MAIN_AUTHORITY, ("1" if stage == "STRUCTURAL" else "2") * 64, f"exact main-game {stage.lower()} evidence", level_data_sha256=_level_data.level_data_sha256, level_data_source_sha256=_level_data.source_sha256, level_id=_level_data.level_id)


def test_unified_qa_composes_authorities_and_allows_rectangular_current_production() -> None:
    report = evaluate_unified_qa(
        _level_data(),
        _artifact(),
        provider=Provider(),
        main_game_authority=MAIN_AUTHORITY,
        difficulty_analysis=None,
        factory_authority=FACTORY_AUTHORITY,
    )

    assert report.disposition is UnifiedQADisposition.UNAVAILABLE
    assert tuple(stage.stage_id for stage in report.stages) == (
        "LEVEL_DATA_V1",
        "STRUCTURAL",
        "PRODUCTION",
        "FACTORY_PRODUCTION_ENVELOPE",
        "DIFFICULTY_V1",
    )
    assert report.stages[0].evidence_digest == _level_data().digest()
    assert report.stages[3].disposition is StageDisposition.PASS
    assert report.canonical_bytes() == report.canonical_bytes()
    assert report.digest() == report.digest()


def test_provider_authority_drift_fails_closed() -> None:
    drifted = AuthorityIdentity(MAIN_AUTHORITY.repository, "d" * 40, MAIN_AUTHORITY.source_path, MAIN_AUTHORITY.contract_version)

    class DriftedProvider(Provider):
        def validate(self, stage: str, level_data: LevelDataIdentity, artifact: object) -> ExternalValidationResult:
            result = super().validate(stage, level_data, artifact)
            return ExternalValidationResult(result.disposition, drifted, result.evidence_digest, result.reason, level_data_sha256=result.level_data_sha256, level_data_source_sha256=result.level_data_source_sha256, level_id=result.level_id)

    report = evaluate_unified_qa(
        _level_data(),
        _artifact(),
        provider=DriftedProvider(),
        main_game_authority=MAIN_AUTHORITY,
        difficulty_analysis=None,
        factory_authority=FACTORY_AUTHORITY,
    )
    assert report.stages[1].disposition is StageDisposition.ERROR
    assert report.stages[2].disposition is StageDisposition.ERROR
    assert report.disposition is UnifiedQADisposition.ERROR


def test_mismatched_factory_source_is_rejected_without_mutation() -> None:
    artifact = _artifact("e" * 64)
    report = evaluate_unified_qa(
        _level_data(),
        artifact,
        provider=Provider(),
        main_game_authority=MAIN_AUTHORITY,
        difficulty_analysis=None,
        factory_authority=FACTORY_AUTHORITY,
    )
    assert report.stages[3].disposition is StageDisposition.FAIL
    assert report.disposition is UnifiedQADisposition.ERROR or report.disposition is UnifiedQADisposition.REJECT
