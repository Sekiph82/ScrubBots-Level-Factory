from __future__ import annotations

import dataclasses
import hashlib
import json
from types import SimpleNamespace
import pytest

from scrubbots_pixel_factory import (
    CANONICAL_M23_PREVIEW_AUTHORITY,
    MutationCandidate,
    MutationContractError,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationProvenance,
    MutationRequest,
    LineageRootRegistration,
    ProvenanceLedger,
    TypedEvidenceReference,
    AuthenticTargetCandidate,
    SafetyConstraintEvidence,
    TypedChallengeTarget,
    provenance_from_authentic_validation,
    revalidate_mutation_from_authentic_adapters,
    run_authentic_bounded_mutations,
)
from scrubbots_pixel_factory.mutation_base import MutationResult
from scrubbots_pixel_factory.mutation_evidence import AuthenticEvidenceAdapter
from scrubbots_pixel_factory.mutation_targeting import select_authentic_target
from test_sb_lf07_004_revalidation import _authentic_chain
from test_sb_lf07_004_revalidation import AUTHENTIC_SOURCE_PATH
from scrubbots_pixel_factory.mutation_source import SourceLinkedMutationContext
from scrubbots_pixel_factory.qa import OwnerSourceRecord as M05OwnerSourceRecord
from sb_lf07_r01_support import engine, m39_authority


def _applied():
    parent = MutationCandidate.root("provenance-parent", {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 6, "booster": "+1_SLOT", "sixth_slot_state": "EMPTY", "live_work_on_sixth": 0}})
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1", operator_version="1", seed=51, intent=MutationIntent.HARDEN, authority=m39_authority())
    result = engine().apply(request, parent)
    assert result.disposition is MutationDisposition.APPLIED
    return request, result


def test_provenance_round_trip_is_deterministic_and_complete() -> None:
    request, result = _applied()
    first = MutationProvenance.from_result(request, result, attempt_ordinal=2, evidence_digests=("a" * 64, "b" * 64))
    second = MutationProvenance.from_result(request, result, attempt_ordinal=2, evidence_digests=("a" * 64, "b" * 64))
    assert first.digest() == second.digest()
    payload = first.canonical_dict()
    assert payload["seed"] == 51
    assert payload["attempt_ordinal"] == 2
    assert payload["parent"]["state_digest"] == result.parent.state_digest
    assert payload["child"]["state_digest"] == result.child.state_digest  # type: ignore[union-attr]
    assert "timestamp" not in str(payload).lower()


def test_derived_provenance_fields_cannot_be_overridden_or_drifted() -> None:
    request, result = _applied()
    provenance = MutationProvenance.from_result(request, result)
    with pytest.raises(MutationContractError):
        dataclasses.replace(provenance, post_state_digest="0" * 64)
    with pytest.raises(MutationContractError):
        MutationProvenance.from_result(dataclasses.replace(request, seed=52), result)
    mixed_child = dataclasses.replace(result.child.identity, lineage_root="f" * 64)  # type: ignore[union-attr]
    with pytest.raises(MutationContractError):
        dataclasses.replace(provenance, child=mixed_child)


def test_ledger_rejects_conflicting_duplicate_child_provenance() -> None:
    request, result = _applied()
    provenance = MutationProvenance.from_result(request, result, attempt_ordinal=0)
    ledger = ProvenanceLedger()
    ledger.register_root(LineageRootRegistration(provenance.lineage_root, provenance.parent))
    assert ledger.record(provenance) == provenance.digest()
    assert ledger.record(provenance) == provenance.digest()
    conflicting = dataclasses.replace(provenance, attempt_ordinal=1)
    with pytest.raises(MutationContractError):
        ledger.record(conflicting)


def test_ledger_rejects_orphan_parent_and_result_operator_drift() -> None:
    request, result = _applied()
    provenance = MutationProvenance.from_result(request, result)
    orphan_parent = dataclasses.replace(provenance.parent, candidate_id="orphan-intermediate", parent_candidate_id="root-parent")
    orphan_child = dataclasses.replace(provenance.child, parent_candidate_id="orphan-intermediate")
    orphan = dataclasses.replace(provenance, parent=orphan_parent, child=orphan_child)
    with pytest.raises(MutationContractError):
        ProvenanceLedger().record(orphan)
    with pytest.raises(MutationContractError):
        MutationProvenance.from_result(dataclasses.replace(request, operator_version="forged"), result)


def test_registered_root_and_typed_stage_evidence_reject_forgery_and_duplicates() -> None:
    request, result = _applied()
    provenance = MutationProvenance.from_result(request, result)
    ledger = ProvenanceLedger()
    with pytest.raises(MutationContractError):
        ledger.record(provenance)
    ledger.register_root(LineageRootRegistration(provenance.lineage_root, provenance.parent))
    assert ledger.record(provenance) == provenance.digest()
    ref = TypedEvidenceReference("M03_SOLVER", "a" * 64, "b" * 64)
    typed = dataclasses.replace(provenance, evidence_references=(ref,))
    assert typed.canonical_dict()["evidence_references"][0]["stage"] == "M03_SOLVER"  # type: ignore[index]
    with pytest.raises(MutationContractError):
        dataclasses.replace(provenance, evidence_references=(ref, ref))


def test_ledger_rejects_real_multi_edge_cycle() -> None:
    request, result = _applied()
    root_to_a = MutationProvenance.from_result(request, result)
    ledger = ProvenanceLedger()
    ledger.register_root(LineageRootRegistration(root_to_a.lineage_root, root_to_a.parent))
    ledger.record(root_to_a)
    a_identity = root_to_a.child
    b_identity = dataclasses.replace(a_identity, candidate_id="cycle-b", parent_candidate_id=a_identity.candidate_id)
    a_to_b = dataclasses.replace(root_to_a, parent=a_identity, child=b_identity, pre_state_digest=a_identity.state_digest, post_state_digest=b_identity.state_digest)
    ledger.record(a_to_b)
    b_to_a = dataclasses.replace(root_to_a, parent=b_identity, child=dataclasses.replace(a_identity, parent_candidate_id=b_identity.candidate_id), pre_state_digest=b_identity.state_digest, post_state_digest=a_identity.state_digest)
    with pytest.raises(MutationContractError):
        ledger.record(b_to_a)


def test_authentic_runner_emits_unique_typed_producer_references_and_rejects_replay_or_stage_drift() -> None:
    parent, request, mutation, solver, analysis, score, qa, solver_adapter, difficulty_adapter, qa_adapter = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver_adapter, difficulty_adapter, qa_adapter)
    provenance = provenance_from_authentic_validation(request, mutation, envelope, solver_adapter, difficulty_adapter, qa_adapter)
    assert [item.stage for item in provenance.evidence_references] == ["M03_SOLVER", "M04_DIFFICULTY", "M05_QA"]
    assert all(item.producer_digest for item in provenance.evidence_references)
    policy_digest = hashlib.sha256(json.dumps({"producer": difficulty_adapter.producer_digest, "policy_version": difficulty_adapter.record.payload["policy_version"]}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    target = TypedChallengeTarget(0.0, 100.0, policy_digest, SafetyConstraintEvidence("scrubbots-m05-safety", "1", policy_digest, True, True, True, qa_adapter.producer_digest))
    candidate = AuthenticTargetCandidate(envelope, solver_adapter, difficulty_adapter, qa_adapter)
    report = run_authentic_bounded_mutations(
        parent,
        base_seed=request.seed,
        budget=__import__("scrubbots_pixel_factory").AttemptBudget(1),
        request_factory=lambda parent, ordinal, seed: request,
        engine=__import__("sb_lf07_r01_support", fromlist=["engine"]).engine(),
        validator=lambda result: candidate if result.digest() == mutation.digest() else (_ for _ in ()).throw(AssertionError("runner replay drift")),
        target=target,
        source_context=SourceLinkedMutationContext.establish(M05OwnerSourceRecord("r03-provenance-source", str(AUTHENTIC_SOURCE_PATH), hashlib.sha256(AUTHENTIC_SOURCE_PATH.read_bytes()).hexdigest(), len(AUTHENTIC_SOURCE_PATH.read_bytes()), 20, 20)),
    )
    assert report.attempts[0].provenance is not None
    assert report.attempts[0].provenance.evidence_references == provenance.evidence_references
    with pytest.raises(MutationContractError):
        provenance_from_authentic_validation(request, mutation, envelope, difficulty_adapter, solver_adapter, qa_adapter)
    with pytest.raises(MutationContractError):
        provenance_from_authentic_validation(dataclasses.replace(request, seed=52), mutation, envelope, solver_adapter, difficulty_adapter, qa_adapter)
    with pytest.raises(MutationContractError):
        provenance_from_authentic_validation(request, mutation, envelope, solver_adapter, object(), qa_adapter)  # type: ignore[arg-type]
