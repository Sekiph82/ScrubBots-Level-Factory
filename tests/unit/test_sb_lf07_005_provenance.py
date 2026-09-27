from __future__ import annotations

from dataclasses import replace
import pytest

from scrubbots_pixel_factory import LineageRootRegistration, MutationContractError, MutationProvenance, ProvenanceLedger, revalidate_mutation_from_authentic_adapters, provenance_from_authentic_validation
from test_sb_lf07_004_revalidation import _authentic_chain


def test_authentic_provenance_is_sealed_and_deterministic() -> None:
    _, request, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    first = provenance_from_authentic_validation(request, mutation, envelope, solver, difficulty, qa, attempt_ordinal=2)
    second = provenance_from_authentic_validation(request, mutation, envelope, solver, difficulty, qa, attempt_ordinal=2)
    assert first.is_authentic_sealed
    assert first.digest() == second.digest()
    assert [ref.stage for ref in first.evidence_references] == ["M03_SOLVER", "M04_DIFFICULTY", "M05_QA"]
    assert first.evidence_digests == tuple(ref.evidence_digest for ref in first.evidence_references)


def test_caller_cannot_replace_sealed_evidence_references_or_construct_production_refs() -> None:
    _, request, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    provenance = provenance_from_authentic_validation(request, mutation, envelope, solver, difficulty, qa)
    with pytest.raises(MutationContractError):
        replace(provenance, evidence_references=(provenance.evidence_references[0],))
    with pytest.raises(MutationContractError):
        MutationProvenance.seal_authentic(request, mutation, provenance.evidence_references[:2])


def test_ledger_requires_sealed_provenance_and_preserves_graph_guards() -> None:
    _, request, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    provenance = provenance_from_authentic_validation(request, mutation, envelope, solver, difficulty, qa)
    ledger = ProvenanceLedger()
    ledger.register_root(LineageRootRegistration(provenance.lineage_root, provenance.parent))
    assert ledger.record(provenance) == provenance.digest()
    assert ledger.record(provenance) == provenance.digest()
    with pytest.raises(MutationContractError):
        ledger.record(replace(provenance, attempt_ordinal=1))
    legacy = MutationProvenance.from_result(request, mutation)
    with pytest.raises(MutationContractError):
        ledger.record(legacy)
