from __future__ import annotations

from scrubbots_pixel_factory import (
    CANONICAL_M23_PREVIEW_AUTHORITY,
    MutationCandidate,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationRequest,
)
from sb_lf07_r01_support import engine, m23_authority


def _parent(depth: int = 3) -> MutationCandidate:
    return MutationCandidate.root(
        "hardening-parent",
        {"gameplay": {"column_count": 3, "preview_depth": depth, "slot_capacity": 5}, "art": {"source": "immutable"}},
        level_data_sha256="c" * 64,
        source_art_sha256="d" * 64,
    )


def test_canonical_preview_depth_hardening_is_real_and_authority_bound() -> None:
    parent = _parent()
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PREVIEW_DEPTH_HARDEN_V1", operator_version="1", seed=11, intent=MutationIntent.HARDEN, authority=m23_authority())
    result = engine().apply(request, parent)
    assert result.disposition is MutationDisposition.APPLIED
    assert result.child is not None
    assert result.child.payload["gameplay"]["preview_depth"] == 4  # type: ignore[index]
    assert result.authority.source_path == "scripts/gameplay/supply/batch_supply_engine.gd"
    assert result.child.source_art_sha256 == parent.source_art_sha256


def test_hardening_is_inapplicable_at_bound_and_does_not_guess() -> None:
    parent = _parent(4)
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PREVIEW_DEPTH_HARDEN_V1", operator_version="1", seed=12, intent=MutationIntent.HARDEN, authority=m23_authority())
    result = engine().apply(request, parent)
    assert result.disposition is MutationDisposition.NO_CHANGE
    assert result.child is None


def test_hardening_cannot_use_dimensions_or_color_count_as_a_shortcut() -> None:
    parent = MutationCandidate.root("hardening-proxy", {"width": 20, "height": 20, "color_count": 3, "gameplay": {"column_count": 3, "preview_depth": 3, "slot_capacity": 5}})
    request = MutationRequest.for_candidate(parent, operator_id="CANONICAL_PREVIEW_DEPTH_HARDEN_V1", operator_version="1", seed=13, intent=MutationIntent.HARDEN, authority=m23_authority())
    result = engine().apply(request, parent)
    assert result.disposition is MutationDisposition.APPLIED
    assert result.child is not None
    assert result.child.payload["width"] == 20  # type: ignore[index]
    assert result.child.payload["height"] == 20  # type: ignore[index]
    assert result.child.payload["color_count"] == 3  # type: ignore[index]
