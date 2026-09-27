from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import tempfile

import pytest

from scrubbots_pixel_factory import (
    MutationCandidate, MutationContractError, MutationDisposition, MutationIntent,
    MutationRequest, ValidationDisposition, revalidate_mutation_from_authentic_adapters,
)
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, LevelIdentity, SolverStateAuthority
from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.difficulty_analysis import build_difficulty_analysis, calculate_challenge_score
from scrubbots_pixel_factory.level_metrics import AnalysisDisposition, LevelMetrics, MetricValues, SolverEvidenceIdentity
from scrubbots_pixel_factory.mutation_evidence import adapt_m03_solver, adapt_m04_difficulty, adapt_m05_qa
from scrubbots_pixel_factory.qa.unified import AuthorityIdentity as QAAuthority, LevelDataIdentity, QAStage, StageDisposition, UnifiedQAReport
from scrubbots_pixel_factory.solver_evidence import SOLVER_EVIDENCE_SCHEMA, SOLVER_EVIDENCE_VERSION, SolverEvidenceReport, SolverMetrics
from sb_lf07_r01_support import engine, m39_authority


AUTHENTIC_SOURCE_PATH = Path(tempfile.gettempdir()) / "scrubbots-r04-authentic-source.bin"


def _authentic_chain(source_bytes: bytes | None = None):
    raw = source_bytes if source_bytes is not None else b"scrubbots-r04-authentic-source"
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


def test_only_authentic_adapter_chain_can_produce_eligible_validation() -> None:
    _, _, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    assert envelope.disposition is ValidationDisposition.ELIGIBLE
    assert envelope.child.state_digest == mutation.child.state_digest  # type: ignore[union-attr]


def test_free_form_and_self_asserted_surfaces_are_not_package_root_eligibility_apis() -> None:
    import scrubbots_pixel_factory as package
    for name in ("evidence", "revalidate_mutation", "revalidate_mutation_from_typed_receipts", "ChallengeTarget", "ProducerEvidenceReceipt", "run_bounded_mutations"):
        assert not hasattr(package, name)


def test_authentic_adapter_rejects_stale_m05_authority_even_when_repository_matches() -> None:
    _, _, mutation, _, _, _, qa, solver, difficulty, _ = _authentic_chain()
    stale_authority = QAAuthority(mutation.authority.repository, "0" * 40, mutation.authority.source_path, mutation.authority.contract_version)
    stale_stages = tuple(QAStage(stage, StageDisposition.PASS, stale_authority, "b" * 64, "stale") for stage in ("LEVEL_DATA_V1", "STRUCTURAL", "PRODUCTION", "FACTORY_PRODUCTION_ENVELOPE", "DIFFICULTY_V1"))
    with pytest.raises(MutationContractError):
        adapt_m05_qa(replace(qa, stages=stale_stages), mutation)


def test_adapter_rejects_unrelated_producer_objects() -> None:
    _, _, mutation, solver, analysis, score, _, solver_adapter, _, _ = _authentic_chain()
    with pytest.raises(MutationContractError):
        adapt_m03_solver(replace(solver, level_id="unrelated-child"), mutation)
    with pytest.raises(MutationContractError):
        adapt_m04_difficulty(replace(analysis, level_source_sha256="c" * 64), score, mutation, solver=solver_adapter)
