from __future__ import annotations

import dataclasses
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
    ProvenanceLedger,
)


def _applied():
    parent = MutationCandidate.root("provenance-parent", {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 5}})
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PREVIEW_DEPTH_HARDEN_V1", operator_version="1", seed=51, intent=MutationIntent.HARDEN, authority=CANONICAL_M23_PREVIEW_AUTHORITY)
    result = MutationEngine().apply(request, parent)
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
    assert ledger.record(provenance) == provenance.digest()
    assert ledger.record(provenance) == provenance.digest()
    conflicting = dataclasses.replace(provenance, attempt_ordinal=1)
    with pytest.raises(MutationContractError):
        ledger.record(conflicting)
