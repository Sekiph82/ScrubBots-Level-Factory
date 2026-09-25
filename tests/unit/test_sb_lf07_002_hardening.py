from __future__ import annotations

import dataclasses
import hashlib

from scrubbots_pixel_factory import AuthorityIdentity, CANONICAL_GAMEPLAY_REPOSITORY, CANONICAL_M39_CONTRACT_VERSION, CANONICAL_M39_SOURCE_PATH, CurrentMainAuthorityResolver, MutationCandidate, MutationDisposition, MutationEngine, MutationIntent, MutationRequest, resolve_current_main_authority
from scrubbots_pixel_factory.mutation_hardening import build_hardening_registry
from sb_lf07_r01_support import CURRENT_MAIN_SHA, M39_BLOB_SHA, engine, m39_authority


def _parent(*, capacity: int = 6, sixth_state: str = "EMPTY", live_work: int = 0) -> MutationCandidate:
    return MutationCandidate.root(
        "hardening-parent",
        {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": capacity, "booster": "+1_SLOT", "sixth_slot_state": sixth_state, "live_work_on_sixth": live_work}, "art": {"source": "immutable"}},
        level_data_sha256="c" * 64,
        source_art_sha256="d" * 64,
    )


def _request(parent: MutationCandidate, authority=None) -> MutationRequest:
    return MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1", operator_version="1", seed=11, intent=MutationIntent.HARDEN, authority=authority or m39_authority())


def test_canonical_m39_rollback_is_a_real_hardening_direction() -> None:
    parent = _parent()
    result = engine().apply(_request(parent), parent)
    assert result.disposition is MutationDisposition.APPLIED
    assert result.child is not None
    assert result.child.payload["gameplay"]["slot_capacity"] == 5  # type: ignore[index]
    assert result.child.payload["gameplay"]["booster"] == "+1_SLOT"  # type: ignore[index]
    assert result.authority.commit_sha == CURRENT_MAIN_SHA
    assert result.authority.source_blob_sha256 == M39_BLOB_SHA
    assert result.child.source_art_sha256 == parent.source_art_sha256


def test_rollback_requires_the_canonical_empty_uncommitted_state() -> None:
    occupied = _parent(sixth_state="OCCUPIED")
    assert engine().apply(_request(occupied), occupied).disposition is MutationDisposition.INAPPLICABLE
    committed = _parent(live_work=1)
    assert engine().apply(_request(committed), committed).disposition is MutationDisposition.INAPPLICABLE
    baseline = _parent(capacity=5)
    assert engine().apply(_request(baseline), baseline).disposition is MutationDisposition.NO_CHANGE


def test_stale_or_drifted_authority_cannot_execute_the_hardener() -> None:
    parent = _parent()
    stale = dataclasses.replace(m39_authority(), commit_sha="edf672f61989d28fd1931917ab49b2d64cc416d6")
    assert engine().apply(_request(parent, stale), parent).disposition is MutationDisposition.ERROR
    drifted = dataclasses.replace(m39_authority(), source_blob_sha256="0" * 64)
    assert engine().apply(_request(parent, drifted), parent).disposition is MutationDisposition.ERROR


def test_hardening_does_not_use_size_color_or_difficulty_proxies() -> None:
    parent = MutationCandidate.root("hardening-proxy", {"width": 20, "height": 20, "color_count": 3, "difficulty_label": "EASY", "gameplay": {"slot_capacity": 6, "booster": "+1_SLOT", "sixth_slot_state": "EMPTY", "live_work_on_sixth": 0}})
    result = engine().apply(_request(parent), parent)
    assert result.child is not None
    assert result.child.payload["width"] == 20  # type: ignore[index]
    assert result.child.payload["height"] == 20  # type: ignore[index]
    assert result.child.payload["color_count"] == 3  # type: ignore[index]
    assert result.child.payload["difficulty_label"] == "EASY"  # type: ignore[index]


def test_r02_builds_from_fresh_task_time_main_and_rejects_prior_sha_with_same_blob() -> None:
    current = "4028de71c2970b7346fe7985a9646aba2728b519"
    source = b"m39-source-at-task-time"
    blob = hashlib.sha256(source).hexdigest()
    resolver = CurrentMainAuthorityResolver(lambda: current, lambda _commit, _path: source)
    resolved = resolve_current_main_authority(resolver, source_path=CANONICAL_M39_SOURCE_PATH, contract_version=CANONICAL_M39_CONTRACT_VERSION, expected_blob_sha256=blob)
    assert resolved.available
    registry = build_hardening_registry(resolved.authority)
    parent = _parent()
    request = _request(parent, resolved.authority)
    assert MutationEngine(registry).apply(request, parent).disposition is MutationDisposition.APPLIED
    prior = AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, "1" * 40, CANONICAL_M39_SOURCE_PATH, CANONICAL_M39_CONTRACT_VERSION, blob)
    assert MutationEngine(registry).apply(_request(parent, prior), parent).disposition is MutationDisposition.ERROR
