import pytest

from scrubbots_pixel_factory import DeterministicRNG
from scrubbots_pixel_factory.generators.rules import (
    RECIPE_NAMES,
    connected_components,
    recipe_for,
    render_recipe,
)


def test_all_required_recipes_are_immutable_and_rectangular() -> None:
    for name in RECIPE_NAMES:
        recipe = recipe_for(name, DeterministicRNG(1))
        first = render_recipe(recipe, 29, 23, DeterministicRNG(11))
        second = render_recipe(recipe, 29, 23, DeterministicRNG(11))
        assert first.geometry_digest() == second.geometry_digest()
        assert first.occupied and len(first.occupied) < first.size
        assert all(0 <= index < first.size for index in first.occupied)
        assert recipe.version == 1 and recipe.layers


def test_recipe_selection_is_seeded_and_unknown_style_fails() -> None:
    assert recipe_for(None, DeterministicRNG(4)) == recipe_for(None, DeterministicRNG(4))
    with pytest.raises(ValueError):
        recipe_for("M03_FAMILY", DeterministicRNG(4))


def test_protected_semantic_regions_survive_recipe_composition() -> None:
    central = render_recipe(recipe_for("CENTRAL_SUBJECT", DeterministicRNG(1)), 31, 27, DeterministicRNG(5))
    assert central.protected_occupied == central.occupied
    frame = render_recipe(recipe_for("BORDER_FRAME_EMBLEM", DeterministicRNG(1)), 31, 27, DeterministicRNG(5))
    assert frame.protected_negative


def test_recipe_families_preserve_their_structural_signatures() -> None:
    organic = render_recipe(recipe_for("ORGANIC", DeterministicRNG(1)), 29, 23, DeterministicRNG(54))
    assert len(connected_components(organic.occupied, organic)) == 1

    multi = render_recipe(recipe_for("MULTI_ISLAND", DeterministicRNG(1)), 29, 23, DeterministicRNG(56))
    assert len(connected_components(multi.occupied, multi)) >= 2

    dense = render_recipe(recipe_for("DENSE_FULL_BOARD", DeterministicRNG(1)), 29, 23, DeterministicRNG(58))
    assert len(dense.occupied) * 100 / dense.size >= 25

    sparse = render_recipe(recipe_for("SPARSE_NEGATIVE_SPACE", DeterministicRNG(1)), 29, 23, DeterministicRNG(59))
    assert len(sparse.occupied) * 100 / sparse.size < 50
