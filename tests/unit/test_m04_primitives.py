import hashlib

import pytest

from scrubbots_pixel_factory import DeterministicRNG
from scrubbots_pixel_factory.generators.rules import (
    PRIMITIVE_NAMES,
    RuleCanvas,
    RuleContractError,
    apply_primitive,
    connected_components,
)


def _render(name: str, seed: int = 17):
    canvas = RuleCanvas(29, 23)
    rng = DeterministicRNG(seed)
    if name == "POCKET":
        apply_primitive(canvas, "CHAMBER", rng.child("context"), chamber_width=11, chamber_height=9)
        geometry = apply_primitive(canvas, name, rng.child("target"), size=3)
    else:
        geometry = apply_primitive(canvas, name, rng)
    return canvas, geometry


def test_all_twelve_primitives_are_bounded_deterministic_and_rectangular() -> None:
    for name in PRIMITIVE_NAMES:
        first, geometry = _render(name)
        second, _ = _render(name)
        assert first.geometry_digest() == second.geometry_digest()
        assert first.occupied
        assert all(0 <= index < first.size for index in first.occupied)
        assert first.width == 29 and first.height == 23
        if isinstance(geometry, dict):
            assert set().union(*geometry.values()) == set(range(first.size))
        elif name == "POCKET":
            assert set(geometry).isdisjoint(first.occupied)
        else:
            assert set(geometry) == set(first.occupied)


def test_stochastic_primitives_vary_without_invalid_geometry() -> None:
    for name in ("BLOB", "ISLAND", "CORRIDOR", "SNAKE"):
        first = _render(name, 17)[1]
        second = _render(name, 18)[1]
        assert first != second
    assert _render("VORONOI", 17)[1] != _render("VORONOI", 18)[1]


def test_required_primitive_topologies() -> None:
    canvas, ring = _render("RING")
    assert canvas.index(canvas.width // 2, canvas.height // 2) not in ring
    corridor = _render("CORRIDOR")[1]
    assert canvas.index(1, canvas.height // 2) in corridor
    assert canvas.index(canvas.width - 2, canvas.height // 2) in corridor
    snake = _render("SNAKE")[1]
    assert len(snake) == len(set(snake)) and len(snake) <= 24
    voronoi = _render("VORONOI")[1]
    assert isinstance(voronoi, dict) and all(voronoi.values())


def test_primitive_respects_protected_negative_space() -> None:
    canvas = RuleCanvas(29, 23)
    protected = {canvas.index(14, 11)}
    canvas.protect_negative(protected)
    apply_primitive(canvas, "BLOB", DeterministicRNG(9))
    assert protected.isdisjoint(canvas.occupied)


def test_pocket_is_a_bounded_carving_primitive() -> None:
    canvas = RuleCanvas(15, 13)
    apply_primitive(canvas, "CHAMBER", DeterministicRNG(2), chamber_width=9, chamber_height=9)
    before = set(canvas.occupied)
    carved = apply_primitive(canvas, "POCKET", DeterministicRNG(3), size=3)
    assert isinstance(carved, set)
    assert carved and carved.issubset(before)
    assert carved.isdisjoint(canvas.occupied)
    assert len(before) - len(canvas.occupied) == len(carved)
    assert len(connected_components(carved, canvas)) == 1
    assert len(carved) <= 9


def test_pocket_fails_closed_on_empty_or_protected_geometry() -> None:
    with pytest.raises(RuleContractError):
        apply_primitive(RuleCanvas(15, 13), "POCKET", DeterministicRNG(3), size=3)
    canvas = RuleCanvas(15, 13)
    apply_primitive(canvas, "CHAMBER", DeterministicRNG(2), chamber_width=9, chamber_height=9)
    pocket_cells = {canvas.index(x, y) for y in range(5, 8) for x in range(6, 9)}
    canvas.protect_occupied(pocket_cells)
    with pytest.raises(RuleContractError):
        apply_primitive(canvas, "POCKET", DeterministicRNG(3), size=3)


def test_invalid_primitive_parameters_fail_closed() -> None:
    with pytest.raises(RuleContractError):
        apply_primitive(RuleCanvas(4, 4), "RING", DeterministicRNG(1), radius=99)
    with pytest.raises(RuleContractError):
        apply_primitive(RuleCanvas(4, 4), "SNAKE", DeterministicRNG(1), max_steps=99)


def test_primitive_digest_is_stable() -> None:
    canvas, _ = _render("BLOB", 31)
    assert hashlib.sha256(canvas.geometry_bytes()).hexdigest() == canvas.geometry_digest()
