import pytest

from scrubbots_pixel_factory import DeterministicRNG
from scrubbots_pixel_factory.generators.rules import (
    RewriteRule,
    RuleCanvas,
    RuleContractError,
    constrained_connected_growth,
    connected_components,
    contour_extraction,
    controlled_fragmentation,
    dilation,
    erosion,
    hole_carving,
    local_rewrite,
    nested_region,
    seeded_frontier_growth,
)


def _canvas() -> RuleCanvas:
    canvas = RuleCanvas(15, 13)
    canvas.mark_many({canvas.index(x, y) for y in range(3, 10) for x in range(3, 12)}, "subject")
    return canvas


def test_growth_is_connected_and_bounded() -> None:
    canvas = RuleCanvas(15, 13)
    seed = {canvas.index(7, 6)}
    result = seeded_frontier_growth(canvas, seed, 25, DeterministicRNG(3))
    assert len(result) == 25 and len(connected_components(result, canvas)) == 1


def test_constrained_growth_fails_boundedly_when_impossible() -> None:
    canvas = RuleCanvas(5, 5)
    with pytest.raises(RuleContractError):
        constrained_connected_growth(canvas, {12}, 4, 6, DeterministicRNG(3), allowed={12, 13})


def test_erosion_and_dilation_respect_protected_cells() -> None:
    canvas = _canvas()
    protected = {canvas.index(7, 6)}
    canvas.protect_occupied(protected)
    remaining = erosion(canvas, set(canvas.occupied), 2)
    assert protected.issubset(remaining)
    forbidden = {canvas.index(1, 1)}
    canvas.protect_negative(forbidden)
    assert forbidden.isdisjoint(dilation(canvas, remaining, 2))


def test_hole_contour_and_nested_regions_are_structural() -> None:
    canvas = _canvas()
    parent = set(canvas.occupied)
    hole = {canvas.index(7, 6), canvas.index(8, 6), canvas.index(7, 7), canvas.index(8, 7)}
    carved = hole_carving(canvas, parent, (hole,))
    assert hole.isdisjoint(carved)
    assert contour_extraction(canvas, carved)
    child = nested_region(canvas, carved, 9, DeterministicRNG(4))
    assert child.issubset(carved) and len(child) == 9


def test_fragmentation_keeps_coherent_minimum_sized_parts() -> None:
    canvas = _canvas()
    parts = controlled_fragmentation(canvas, set(canvas.occupied), 3, 2, DeterministicRNG(8))
    assert len(parts) == 3
    assert all(len(part) >= 2 and len(connected_components(part, canvas)) == 1 for part in parts.values())


@pytest.mark.parametrize("rule_name", ["FILL_NOTCH", "BRIDGE_GAP", "REMOVE_PROTRUSION"])
def test_local_rewrite_rules_are_deterministic_and_bounded(rule_name: str) -> None:
    first = _canvas()
    second = _canvas()
    a = local_rewrite(first, RewriteRule(rule_name, 3))
    b = local_rewrite(second, RewriteRule(rule_name, 3))
    assert a == b


def test_rewrite_cannot_mutate_protected_occupied_cell() -> None:
    canvas = _canvas()
    protected = canvas.index(3, 3)
    canvas.protect_occupied({protected})
    local_rewrite(canvas, RewriteRule("REMOVE_PROTRUSION", 2))
    assert protected in canvas.occupied


def test_fill_notch_and_bridge_gap_have_distinct_predicates() -> None:
    notch = RuleCanvas(7, 7)
    notch.mark_many({notch.index(3, 2), notch.index(2, 3), notch.index(4, 3)}, "subject")
    notch_fill = local_rewrite(notch, RewriteRule("FILL_NOTCH", 1))
    assert notch.index(3, 3) in notch_fill

    gap = RuleCanvas(7, 7)
    gap.mark_many({gap.index(2, 3), gap.index(4, 3)}, "subject")
    bridge_fill = local_rewrite(gap, RewriteRule("BRIDGE_GAP", 1))
    assert gap.index(3, 3) in bridge_fill

    notch_only = RuleCanvas(7, 7)
    notch_only.mark_many({notch_only.index(3, 2), notch_only.index(2, 3), notch_only.index(4, 3)}, "subject")
    assert notch_only.index(3, 3) not in local_rewrite(notch_only, RewriteRule("BRIDGE_GAP", 1))

    gap_only = RuleCanvas(7, 7)
    gap_only.mark_many({gap_only.index(2, 3), gap_only.index(4, 3)}, "subject")
    assert gap_only.index(3, 3) not in local_rewrite(gap_only, RewriteRule("FILL_NOTCH", 1))


def test_bridge_gap_respects_protected_negative_cells() -> None:
    canvas = RuleCanvas(7, 7)
    gap = canvas.index(3, 3)
    canvas.mark_many({canvas.index(2, 3), canvas.index(4, 3)}, "subject")
    canvas.protect_negative({gap})
    assert gap not in local_rewrite(canvas, RewriteRule("BRIDGE_GAP", 2))


def test_protected_occupied_semantic_label_survives_all_overlapping_operations() -> None:
    canvas = _canvas()
    protected = canvas.index(7, 6)
    canvas.set_region(protected, "CENTRAL_SUBJECT")
    canvas.protect_occupied({protected}, "CENTRAL_SUBJECT")
    canvas.mark(protected, "dilation")
    dilation(canvas, {protected}, 1, label="other")
    controlled_fragmentation(canvas, set(canvas.occupied), 3, 2, DeterministicRNG(8), label="fragment")
    local_rewrite(canvas, RewriteRule("FILL_NOTCH", 2), label="rewrite")
    assert canvas.regions["CENTRAL_SUBJECT"] == frozenset({protected})
    assert protected in canvas.occupied
    assert canvas.copy().regions["CENTRAL_SUBJECT"] == frozenset({protected})
