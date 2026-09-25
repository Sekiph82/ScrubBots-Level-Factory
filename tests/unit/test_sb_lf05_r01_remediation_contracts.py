from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
import hashlib

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.output.png import encode_logical_png
from scrubbots_pixel_factory.qa import (
    AuthorityIdentity,
    CurrentMainResolution,
    ExternalValidationResult,
    HandoffValidationReceipt,
    LevelDataIdentity,
    M09RoundTripReceipt,
    OwnerSourceRecord,
    QAContractError,
    QAOutcome,
    QAOutcomeStatistics,
    SemanticReviewDisposition,
    SolverEvidenceProvenance,
    SolverGateDisposition,
    StageDisposition,
    build_main_game_handoff,
    build_qa_report,
    evaluate_m09_round_trip,
    evaluate_solver_gate,
    evaluate_unified_qa,
    verify_owner_source_preservation,
)
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition
from scrubbots_pixel_factory.solver_evidence import SolverEvidenceReport, SolverMetrics


SOURCE = "a" * 64
AUTHORITY = AuthorityIdentity("https://github.com/Sekiph82/Scrubbots", "b" * 40, "scripts/qa/current.gd", "M05_R01_V1")


def _level() -> LevelDataIdentity:
    cells = ["C01", "C02", "C03", "C01"]
    return LevelDataIdentity.from_mapping("r01-level", SOURCE, {"schema": "scrubbots-level-data", "version": 1, "level_id": "r01-level", "width": 2, "height": 2, "cells": cells}, 2, 2)


def _evidence() -> SolverEvidenceReport:
    policy = SolverBudgetPolicy(max_visited_states=10, max_depth=4, max_solutions=2)
    result = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, (), "fixture", BaselineSearchPolicy(max_depth=4))
    budget = BudgetedSolverResult(SolverOutcomeDisposition.SOLVED, policy, "fixture", "SOLVED", "fixture")
    return SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, result, SolverMetrics((), False, 1, None, 0, 0, (1,), 1, ()), 0.0, budget_policy=policy, budget_result=budget)


def test_exact_leveldata_payload_and_provider_cross_lineage_fail_closed() -> None:
    with pytest.raises(QAContractError):
        LevelDataIdentity.from_mapping("r01-level", SOURCE, {"schema": "scrubbots-level-data", "version": 2, "level_id": "r01-level", "width": 2, "height": 2, "cells": ["C01"] * 4}, 2, 2)

    class Provider:
        def validate(self, stage, level_data, artifact):
            return ExternalValidationResult(StageDisposition.PASS, AUTHORITY, "c" * 64, "cross-lineage", level_data_sha256="d" * 64, level_data_source_sha256=level_data.source_sha256, level_id=level_data.level_id)

    artifact = SimpleNamespace(width=20, height=20, cells=("C01", "C02", "C03") * 133 + ("C01",), palette=("C01", "C02", "C03"), source_sha256=SOURCE)
    report = evaluate_unified_qa(_level(), artifact, provider=Provider(), main_game_authority=AUTHORITY, difficulty_analysis=None)
    assert report.stages[1].disposition is StageDisposition.ERROR


def test_m09_strict_receipt_rejects_mixed_leveldata_lineage() -> None:
    source = encode_logical_png(2, 2, ("C01", "C02", "C03", "C01"))
    level = _level()
    class Provider:
        def round_trip(self, source_png):
            cells = ("C01", "C02", "C03", "C01")
            palette = ("C01", "C02", "C03")
            return M09RoundTripReceipt(StageDisposition.PASS, AUTHORITY, hashlib.sha256(source_png).hexdigest(), "d" * 64, 2, 2, cells, cells, "e" * 64, "receipt", level_data_bytes=b"wrong", level_data_sha256=hashlib.sha256(b"wrong").hexdigest(), first_seen_palette=palette, source_cell_indices=(0, 1, 2, 0), reconstructed_cell_indices=(0, 1, 2, 0), reconstructed_logical_pixels=cells)
    report = evaluate_m09_round_trip(source, provider=Provider(), main_game_authority=AUTHORITY, level_data=level)
    assert report.disposition is StageDisposition.ERROR


def test_level_art_requires_exact_final_opacity_and_noncoercive_dimensions() -> None:
    from scrubbots_pixel_factory.qa import validate_level_art
    artifact = SimpleNamespace(level_id="r01-level", width="20", height=20, cells=("C01",) * 400, palette=("C01",), palette_indices=(0,) * 400, raw_sha256=SOURCE, source_provenance=SimpleNamespace(raw_sha256=SOURCE))
    report = validate_level_art(artifact, level_data=None, authority=AUTHORITY)
    assert {"ILLEGAL_DIMENSIONS", "FINAL_OPACITY_MISSING", "PROVENANCE_MISSING"}.issubset(report.rejection_codes)


def test_solver_provenance_replay_and_digest_mismatch_are_errors() -> None:
    evidence = _evidence()
    provenance = SolverEvidenceProvenance("level-a", SOURCE, "request-a", AUTHORITY, "provider", "v1", evidence.digest(), evidence.budget_policy.digest(), "c" * 64)
    replay = evaluate_solver_gate(evidence, authority=AUTHORITY, level_source_sha256=SOURCE, level_id="level-b", request_id="request-a", evidence_provenance=provenance)
    assert replay.disposition is SolverGateDisposition.ERROR
    tampered = SolverEvidenceProvenance("level-a", SOURCE, "request-a", AUTHORITY, "provider", "v1", "d" * 64, evidence.budget_policy.digest(), "c" * 64)
    assert evaluate_solver_gate(evidence, authority=AUTHORITY, level_source_sha256=SOURCE, level_id="level-a", request_id="request-a", evidence_provenance=tampered).disposition is SolverGateDisposition.ERROR


def test_outcome_statistics_reject_unknown_keys_and_duplicates() -> None:
    with pytest.raises(QAContractError):
        QAOutcomeStatistics(1, (("NOT_A_REAL_OUTCOME", 1),))
    with pytest.raises(QAContractError):
        QAOutcomeStatistics(1, ((QAOutcome.ERROR, 1), (QAOutcome.ERROR, 0)))


def test_report_rejects_open_stage_reason_and_missing_identity() -> None:
    with pytest.raises(QAContractError):
        build_qa_report(source_sha256=SOURCE, level_data_digest="b" * 64, logical_art_digest="c" * 64, stages={"UNKNOWN": "PASS"}, semantic_review=SemanticReviewDisposition.ACCEPT)
    with pytest.raises(QAContractError):
        build_qa_report(source_sha256=SOURCE, level_data_digest="b" * 64, logical_art_digest="c" * 64, stages={"STRUCTURAL": "PASS"}, semantic_review=SemanticReviewDisposition.ACCEPT)


def test_owner_record_rejects_source_alias_and_is_idempotent(tmp_path) -> None:
    source = tmp_path / "source.png"
    raw = b"owner"
    source.write_bytes(raw)
    record = OwnerSourceRecord("owner-r01", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    aliased = verify_owner_source_preservation(record, derived_artifact_paths=(str(source),))
    assert aliased.disposition == "FAIL"
    first = verify_owner_source_preservation(record)
    second = verify_owner_source_preservation(record)
    assert first.digest() == second.digest()


def test_handoff_never_marks_m30_for_stale_current_main(tmp_path) -> None:
    ids = {"source_sha256": SOURCE, "level_data_digest": "b" * 64, "logical_art_digest": "c" * 64, "main_game_authority_digest": "d" * 64, "main_game_result_digest": "e" * 64, "production_facts_digest": "f" * 64, "solver_evidence_digest": "1" * 64}
    report = build_qa_report(**ids, stages={"STRUCTURAL": "PASS", "PRODUCTION": "PASS", "SOLVER": "PASS"}, semantic_review=SemanticReviewDisposition.ACCEPT)
    class Resolver:
        def resolve_current_main(self):
            return CurrentMainResolution("RESOLVED", AuthorityIdentity("https://github.com/other/repo", "b" * 40, "x", "v1"), True, "wrong repo")
    handoff = build_main_game_handoff(level_data_sha256="b" * 64, logical_art_png_sha256="c" * 64, source_provenance_sha256=SOURCE, qa_report=report, solver_evidence_digest="1" * 64, difficulty_analysis_digest="5" * 64, semantic_evidence_digest="6" * 64, factory_schema="factory", factory_version=1, main_game_resolver=Resolver(), provider=None)
    assert handoff.disposition == "UNAVAILABLE"
    assert dict(handoff.downstream_gates)["M30_COMPATIBLE"] == "PENDING"
