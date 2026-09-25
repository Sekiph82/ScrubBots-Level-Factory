from __future__ import annotations

import dataclasses

from scrubbots_pixel_factory import (
    AuthorityIdentity,
    CANONICAL_GAMEPLAY_REPOSITORY,
    CANONICAL_M39_SLOT_AUTHORITY,
    MutationCandidate,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationRequest,
    CurrentMainAuthorityResolver,
    CANONICAL_M39_CONTRACT_VERSION,
    CANONICAL_M39_SOURCE_PATH,
    resolve_current_main_authority,
)
from scrubbots_pixel_factory.mutation_easing import build_easing_registry
import hashlib
from sb_lf07_r01_support import engine, m39_authority


def _parent(*, booster: str = "+1_SLOT", capacity: int = 5) -> MutationCandidate:
    return MutationCandidate.root(
        "easing-parent",
        {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": capacity, "booster": booster}, "art": {"source": "immutable"}},
        source_art_sha256="e" * 64,
    )


def test_canonical_plus_one_slot_easing_executes_end_to_end() -> None:
    parent = _parent()
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=21, intent=MutationIntent.EASE, authority=m39_authority())
    result = engine().apply(request, parent)
    assert result.disposition is MutationDisposition.APPLIED
    assert result.child is not None
    assert result.child.payload["gameplay"]["slot_capacity"] == 6  # type: ignore[index]
    assert result.child.payload["gameplay"]["booster"] == "+1_SLOT"  # type: ignore[index]
    assert result.child.source_art_sha256 == parent.source_art_sha256


def test_easing_requires_explicit_canonical_booster_and_bound() -> None:
    no_booster = _parent(booster="unknown")
    req = MutationRequest.for_candidate(no_booster, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=22, intent=MutationIntent.EASE, authority=m39_authority())
    assert engine().apply(req, no_booster).disposition is MutationDisposition.INAPPLICABLE
    active = _parent(capacity=6)
    req2 = MutationRequest.for_candidate(active, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=23, intent=MutationIntent.EASE, authority=m39_authority())
    assert engine().apply(req2, active).disposition is MutationDisposition.NO_CHANGE


def test_easing_does_not_change_board_or_color_metadata() -> None:
    parent = MutationCandidate.root("easing-proxy", {"width": 59, "height": 59, "color_count": 12, "difficulty": "VERY_HARD", "gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 5, "booster": "+1_SLOT"}})
    req = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=24, intent=MutationIntent.EASE, authority=m39_authority())
    result = engine().apply(req, parent)
    assert result.child is not None
    assert result.child.payload["width"] == 59  # type: ignore[index]
    assert result.child.payload["height"] == 59  # type: ignore[index]
    assert result.child.payload["color_count"] == 12  # type: ignore[index]
    assert result.child.payload["difficulty"] == "VERY_HARD"  # type: ignore[index]


def test_easing_rejects_stale_current_main_authority() -> None:
    parent = _parent()
    stale = AuthorityIdentity(
        CANONICAL_GAMEPLAY_REPOSITORY,
        "0" * 40,
        m39_authority().source_path,
        m39_authority().contract_version,
        m39_authority().source_blob_sha256,
    )
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=25, intent=MutationIntent.EASE, authority=stale)
    result = engine().apply(request, parent)
    assert result.disposition.value == "ERROR"
    assert "authority" in result.reason


def test_easing_rejects_source_blob_drift() -> None:
    parent = _parent()
    drifted = AuthorityIdentity(
        CANONICAL_GAMEPLAY_REPOSITORY,
        m39_authority().commit_sha,
        m39_authority().source_path,
        m39_authority().contract_version,
        "f" * 64,
    )
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=26, intent=MutationIntent.EASE, authority=drifted)
    result = engine().apply(request, parent)
    assert result.disposition.value == "ERROR"
    assert "authority" in result.reason


def test_r02_easing_registry_is_fresh_and_rejects_prior_sha_with_same_blob() -> None:
    current = "4028de71c2970b7346fe7985a9646aba2728b519"
    source = b"m39-easing-source-at-task-time"
    blob = hashlib.sha256(source).hexdigest()
    resolved = resolve_current_main_authority(CurrentMainAuthorityResolver(lambda: current, lambda _commit, _path: source), source_path=CANONICAL_M39_SOURCE_PATH, contract_version=CANONICAL_M39_CONTRACT_VERSION, expected_blob_sha256=blob)
    registry = build_easing_registry(resolved.authority)
    parent = _parent()
    req = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=27, intent=MutationIntent.EASE, authority=resolved.authority)
    assert MutationEngine(registry).apply(req, parent).disposition is MutationDisposition.APPLIED
    prior = dataclasses.replace(resolved.authority, commit_sha="1" * 40)
    assert MutationEngine(registry).apply(MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=28, intent=MutationIntent.EASE, authority=prior), parent).disposition is MutationDisposition.ERROR
