from __future__ import annotations

from scrubbots_pixel_factory import (
    CANONICAL_M39_SLOT_AUTHORITY,
    MutationCandidate,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationRequest,
)


def _parent(*, booster: str = "+1_SLOT", capacity: int = 5) -> MutationCandidate:
    return MutationCandidate.root(
        "easing-parent",
        {"gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": capacity, "booster": booster}, "art": {"source": "immutable"}},
        source_art_sha256="e" * 64,
    )


def test_canonical_plus_one_slot_easing_executes_end_to_end() -> None:
    parent = _parent()
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=21, intent=MutationIntent.EASE, authority=CANONICAL_M39_SLOT_AUTHORITY)
    result = MutationEngine().apply(request, parent)
    assert result.disposition is MutationDisposition.APPLIED
    assert result.child is not None
    assert result.child.payload["gameplay"]["slot_capacity"] == 6  # type: ignore[index]
    assert result.child.payload["gameplay"]["booster"] == "+1_SLOT"  # type: ignore[index]
    assert result.child.source_art_sha256 == parent.source_art_sha256


def test_easing_requires_explicit_canonical_booster_and_bound() -> None:
    no_booster = _parent(booster="unknown")
    req = MutationRequest.for_candidate(no_booster, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=22, intent=MutationIntent.EASE, authority=CANONICAL_M39_SLOT_AUTHORITY)
    assert MutationEngine().apply(req, no_booster).disposition is MutationDisposition.INAPPLICABLE
    active = _parent(capacity=6)
    req2 = MutationRequest.for_candidate(active, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=23, intent=MutationIntent.EASE, authority=CANONICAL_M39_SLOT_AUTHORITY)
    assert MutationEngine().apply(req2, active).disposition is MutationDisposition.NO_CHANGE


def test_easing_does_not_change_board_or_color_metadata() -> None:
    parent = MutationCandidate.root("easing-proxy", {"width": 59, "height": 59, "color_count": 12, "difficulty": "VERY_HARD", "gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 5, "booster": "+1_SLOT"}})
    req = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PLUS_ONE_SLOT_EASE_V1", operator_version="1", seed=24, intent=MutationIntent.EASE, authority=CANONICAL_M39_SLOT_AUTHORITY)
    result = MutationEngine().apply(req, parent)
    assert result.child is not None
    assert result.child.payload["width"] == 59  # type: ignore[index]
    assert result.child.payload["height"] == 59  # type: ignore[index]
    assert result.child.payload["color_count"] == 12  # type: ignore[index]
    assert result.child.payload["difficulty"] == "VERY_HARD"  # type: ignore[index]
