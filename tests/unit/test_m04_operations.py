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
