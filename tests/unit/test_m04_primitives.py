import hashlib

import pytest

from scrubbots_pixel_factory import DeterministicRNG
from scrubbots_pixel_factory.generators.rules import (
    PRIMITIVE_NAMES,
    RuleCanvas,
    RuleContractError,
    apply_primitive,
)


def _render(name: str, seed: int = 17):
    canvas = RuleCanvas(29, 23)
    geometry = apply_primitive(canvas, name, DeterministicRNG(seed))
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


def test_invalid_primitive_parameters_fail_closed() -> None:
    with pytest.raises(RuleContractError):
        apply_primitive(RuleCanvas(4, 4), "RING", DeterministicRNG(1), radius=99)
    with pytest.raises(RuleContractError):
        apply_primitive(RuleCanvas(4, 4), "SNAKE", DeterministicRNG(1), max_steps=99)


def test_primitive_digest_is_stable() -> None:
    canvas, _ = _render("BLOB", 31)
    assert hashlib.sha256(canvas.geometry_bytes()).hexdigest() == canvas.geometry_digest()
