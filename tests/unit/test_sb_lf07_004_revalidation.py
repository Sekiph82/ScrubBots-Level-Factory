from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import tempfile

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.difficulty_analysis import build_difficulty_analysis, calculate_challenge_score
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.qa.unified import AuthorityIdentity as QAAuthority, LevelDataIdentity, QAStage, StageDisposition, UnifiedQAReport
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics
from scrubbots_pixel_factory import (
    CANONICAL_M23_PREVIEW_AUTHORITY,
    EvidenceDisposition,
    MutationCandidate,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationRequest,
    MutationContractError,
    M03SolverEvidenceReceipt,
    M04DifficultyEvidenceReceipt,
    M05QAEvidenceReceipt,
    ValidationDisposition,
    evidence,
    revalidate_mutation,
    revalidate_mutation_from_authentic_adapters,
    revalidate_mutation_from_typed_receipts,
)
from scrubbots_pixel_factory.mutation_evidence import adapt_m03_solver, adapt_m04_difficulty, adapt_m05_qa
from sb_lf07_r01_support import engine, m39_authority


def _mutation():
    parent = MutationCandidate.root("revalidate-parent", {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 6, "booster": "+1_SLOT", "sixth_slot_state": "EMPTY", "live_work_on_sixth": 0}})
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1", operator_version="1", seed=31, intent=MutationIntent.HARDEN, authority=m39_authority())
    result = engine().apply(request, parent)
    assert result.disposition is MutationDisposition.APPLIED
    return result


def _records(mutation, *, solver=EvidenceDisposition.SOLVED, difficulty=EvidenceDisposition.AVAILABLE, qa=EvidenceDisposition.PASS):
    return (
        evidence("M03_SOLVER", solver, mutation, {"status": solver.value}),
        evidence("M04_DIFFICULTY", difficulty, mutation, {"policy_version": "DIFFICULTY_V1", "challenge_score": 62.5, "lane": "HARD"}),
        evidence("M05_QA", qa, mutation, {"structural": True, "production": True}),
    )


def test_applied_mutation_requires_complete_child_evidence_chain() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    envelope = revalidate_mutation(mutation, solver, difficulty, qa)
    assert envelope.disposition is ValidationDisposition.ELIGIBLE
    assert envelope.child.state_digest == mutation.child.state_digest  # type: ignore[union-attr]
    assert envelope.challenge_score == 62.5


def test_unsolvable_inconclusive_and_unavailable_never_become_eligible() -> None:
    mutation = _mutation()
    for solver_status, expected in ((EvidenceDisposition.PROVEN_UNSOLVABLE, ValidationDisposition.REJECTED), (EvidenceDisposition.UNKNOWN_BOUND, ValidationDisposition.INCONCLUSIVE), (EvidenceDisposition.UNAVAILABLE, ValidationDisposition.UNAVAILABLE)):
        solver, difficulty, qa = _records(mutation, solver=solver_status)
        assert revalidate_mutation(mutation, solver, difficulty, qa).disposition is expected


def test_parent_acceptance_cannot_float_to_child_and_stale_evidence_fails_closed() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    stale_parent = type(solver)(solver.stage, solver.disposition, mutation.parent.state_digest, solver.request_digest, solver.parent_state_digest, solver.operator_id, solver.authority_digest, solver.payload)
    with pytest.raises(MutationContractError):
        revalidate_mutation(mutation, stale_parent, difficulty, qa)
    with pytest.raises(MutationContractError):
        revalidate_mutation(mutation, solver, type(difficulty)(difficulty.stage, difficulty.disposition, difficulty.child_state_digest, "0" * 64, difficulty.parent_state_digest, difficulty.operator_id, difficulty.authority_digest, difficulty.payload), qa)


def test_child_hash_and_stage_order_are_bound_not_caller_claims() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    with pytest.raises(MutationContractError):
        revalidate_mutation(mutation, difficulty, solver, qa)
    bad_solver = type(solver)(solver.stage, solver.disposition, "0" * 64, solver.request_digest, solver.parent_state_digest, solver.operator_id, solver.authority_digest, solver.payload)
    with pytest.raises(MutationContractError):
        revalidate_mutation(mutation, bad_solver, difficulty, qa)


def test_production_entry_point_requires_typed_m03_m04_m05_receipts() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    with pytest.raises(MutationContractError):
        revalidate_mutation_from_typed_receipts(mutation, solver, difficulty, qa)  # type: ignore[arg-type]
    typed_solver = M03SolverEvidenceReceipt("M03_SOLVER", "solver-evidence", "1", "1" * 64, solver)
    typed_difficulty = M04DifficultyEvidenceReceipt("M04_DIFFICULTY", "difficulty-evidence", "1", "2" * 64, difficulty)
    typed_qa = M05QAEvidenceReceipt("M05_QA", "qa-evidence", "1", "3" * 64, qa)
    envelope = revalidate_mutation_from_typed_receipts(mutation, typed_solver, typed_difficulty, typed_qa)
    assert envelope.disposition is ValidationDisposition.ELIGIBLE


def test_typed_receipt_rejects_forged_producer_stage_or_missing_score() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    with pytest.raises(MutationContractError):
        M03SolverEvidenceReceipt("M04_DIFFICULTY", "solver-evidence", "1", "1" * 64, solver)
    bad = type(difficulty)(difficulty.stage, difficulty.disposition, difficulty.child_state_digest, difficulty.request_digest, difficulty.parent_state_digest, difficulty.operator_id, difficulty.authority_digest, {"policy_version": "DIFFICULTY_V1"})
    with pytest.raises(MutationContractError):
        M04DifficultyEvidenceReceipt("M04_DIFFICULTY", "difficulty-evidence", "1", "2" * 64, bad)


def test_production_authentic_adapter_entry_point_rejects_self_signed_wrappers() -> None:
    mutation = _mutation()
    solver, difficulty, qa = _records(mutation)
    with pytest.raises(MutationContractError):
        revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)  # type: ignore[arg-type]
    with pytest.raises(MutationContractError):
        revalidate_mutation_from_authentic_adapters(mutation, object(), object(), object())  # type: ignore[arg-type]


AUTHENTIC_SOURCE_PATH = Path(tempfile.gettempdir()) / "scrubbots-r03-authentic-source.bin"


def _authentic_chain(source_bytes: bytes | None = None):
    raw = source_bytes if source_bytes is not None else b"scrubbots-r03-authentic-source"
    AUTHENTIC_SOURCE_PATH.write_bytes(raw)
    source = hashlib.sha256(raw).hexdigest()
    level_data = LevelDataIdentity.from_mapping("authentic-child", source, {"schema": "scrubbots-level-data", "version": 1, "level_id": "authentic-child", "width": 1, "height": 1, "cells": [0]})
    parent = MutationCandidate.root("authentic-parent", {"level_id": "authentic-child", "gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 6, "booster": "+1_SLOT", "sixth_slot_state": "EMPTY", "live_work_on_sixth": 0}}, level_data_sha256=level_data.level_data_sha256, source_art_sha256=source)
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1", operator_version="1", seed=41, intent=MutationIntent.HARDEN, authority=m39_authority())
    mutation = engine().apply(request, parent)
    assert mutation.child is not None
    solver_authority = SolverStateAuthority(mutation.authority.repository, CANONICAL_PROOF_STATE_AUTHORITY_SHA)
    search = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, SearchVerdict.SOLVED, (), "authentic", BaselineSearchPolicy())
    solver = SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, search, SolverMetrics((), False, 1, None, 0, 0, (0,), 0, ()), 0.0, level_id="authentic-child", level_source_sha256=source, request_id=mutation.request_digest, authority=solver_authority, provider_id="canonical-solver", provider_version="v1", state_digest=mutation.child.state_digest)
    metrics = LevelMetrics(LevelIdentity(source, mutation.child.candidate_id, 1, 1, 1), solver_authority, SolverEvidenceIdentity(SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, solver.digest()), AnalysisDisposition.AVAILABLE, metrics=MetricValues(move_count=2, states_visited=3, dead_ends=1, branching=1.0, forced_moves=1))
    score = calculate_challenge_score(metrics)
    analysis = build_difficulty_analysis(metrics, score)
    qa_authority = QAAuthority(mutation.authority.repository, mutation.authority.commit_sha, mutation.authority.source_path, mutation.authority.contract_version)
    stages = tuple(QAStage(stage, StageDisposition.PASS, qa_authority, "b" * 64, "authentic") for stage in ("LEVEL_DATA_V1", "STRUCTURAL", "PRODUCTION", "FACTORY_PRODUCTION_ENVELOPE", "DIFFICULTY_V1"))
    qa = UnifiedQAReport(level_data, stages)
    solver_adapter = adapt_m03_solver(solver, mutation)
    difficulty_adapter = adapt_m04_difficulty(analysis, score, mutation, solver=solver_adapter)
    qa_adapter = adapt_m05_qa(qa, mutation)
    return parent, request, mutation, solver, analysis, score, qa, solver_adapter, difficulty_adapter, qa_adapter


def test_authentic_producer_chain_binds_exact_child_and_rejects_unrelated_objects() -> None:
    _, _, mutation, solver, analysis, score, qa, solver_adapter, difficulty_adapter, qa_adapter = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver_adapter, difficulty_adapter, qa_adapter)
    assert envelope.disposition is ValidationDisposition.ELIGIBLE
    with pytest.raises(MutationContractError):
        adapt_m03_solver(replace(solver, level_id="unrelated-child"), mutation)
    with pytest.raises(MutationContractError):
        adapt_m04_difficulty(replace(analysis, level_source_sha256="c" * 64), score, mutation, solver=solver_adapter)
    with pytest.raises(MutationContractError):
        adapt_m05_qa(replace(qa, level_data=replace(qa.level_data, level_id="unrelated-child")), mutation)
