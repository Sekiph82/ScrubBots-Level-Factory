from __future__ import annotations

import json

import pytest

from scrubbots_pixel_factory import (
    AuthorityIdentity,
    CANONICAL_GAMEPLAY_REPOSITORY,
    CANONICAL_GAMEPLAY_SHA,
    MutationCandidate,
    MutationContractError,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationRequest,
)
from sb_lf07_r01_support import engine, m39_authority


def _parent() -> MutationCandidate:
    return MutationCandidate.root(
        "candidate-root",
        {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 6, "booster": "+1_SLOT", "sixth_slot_state": "EMPTY", "live_work_on_sixth": 0}, "config": {"seed_class": "fixture"}},
        level_data_sha256="a" * 64,
        source_art_sha256="b" * 64,
    )


def _unknown_request(parent: MutationCandidate) -> MutationRequest:
    authority = AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, CANONICAL_GAMEPLAY_SHA, "scripts/gameplay/solver/proof_state.gd", "M27_PROOF_STATE_V1")
    return MutationRequest.for_candidate(parent, operator_id="UNKNOWN", operator_version="1", seed=7, intent=MutationIntent.HARDEN, authority=authority)


def test_unknown_operator_is_closed_and_cannot_mint_gameplay_truth() -> None:
    parent = _parent()
    result = MutationEngine().apply(_unknown_request(parent), parent)
    assert result.disposition is MutationDisposition.INAPPLICABLE
    assert result.child is None
    assert result.eligible is False


def test_root_parent_is_deeply_immutable_and_request_replay_is_deterministic() -> None:
    parent = _parent()
    before = json.dumps(parent.canonical_dict(), sort_keys=True)
    request = MutationRequest.for_candidate(
        parent,
        operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1",
        operator_version="1",
        seed=41,
        intent=MutationIntent.HARDEN,
        authority=m39_authority(),
    )
    first = engine().apply(request, parent)
    second = engine().apply(request, parent)
    assert first.disposition is MutationDisposition.APPLIED
    assert first.child is not None and second.child is not None
    assert first.child is not second.child
    assert first.child.digest() == second.child.digest()
    assert first.child.identity != parent.identity
    assert first.child.parent_candidate_id == parent.candidate_id
    assert json.dumps(parent.canonical_dict(), sort_keys=True) == before
    with pytest.raises(TypeError):
        parent.payload["gameplay"]["slot_capacity"] = 5  # type: ignore[index]


def test_stale_parent_authority_and_operator_drift_fail_closed() -> None:
    parent = _parent()
    request = MutationRequest.for_candidate(
        parent,
        operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1",
        operator_version="1",
        seed=8,
        intent=MutationIntent.HARDEN,
        authority=m39_authority(),
    )
    stale = MutationCandidate.root("candidate-root", {"gameplay": {"column_count": 3, "preview_depth": 4, "slot_capacity": 5, "booster": "+1_SLOT", "sixth_slot_state": "EMPTY", "live_work_on_sixth": 0}, "config": {"seed_class": "fixture"}}, level_data_sha256="a" * 64, source_art_sha256="b" * 64)
    assert engine().apply(request, stale).disposition is MutationDisposition.ERROR
    bad = MutationRequest(parent.identity, request.operator_id, request.operator_version, request.seed, MutationIntent.EASE, request.authority)
    assert engine().apply(bad, parent).disposition is MutationDisposition.ERROR


def test_identity_digests_exclude_paths_and_wall_clock_metadata() -> None:
    parent = _parent()
    a = MutationRequest.for_candidate(parent, operator_id="UNKNOWN", operator_version="1", seed=1, intent=MutationIntent.HARDEN, authority=AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, CANONICAL_GAMEPLAY_SHA, "scripts/gameplay/solver/proof_state.gd", "M27_PROOF_STATE_V1"))
    b = MutationRequest.for_candidate(parent, operator_id="UNKNOWN", operator_version="1", seed=1, intent=MutationIntent.HARDEN, authority=AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, CANONICAL_GAMEPLAY_SHA, "scripts/gameplay/solver/proof_state.gd", "M27_PROOF_STATE_V1"))
    assert a.digest() == b.digest()
    assert "timestamp" not in json.dumps(a.canonical_dict()).lower()
    with pytest.raises(MutationContractError):
        AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, CANONICAL_GAMEPLAY_SHA, "../proof_state.gd", "bad")
