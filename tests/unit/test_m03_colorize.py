from scrubbots_pixel_factory import CANONICAL_PALETTE
from scrubbots_pixel_factory.core import DeterministicRNG
import pytest


def test_colorization_uses_exact_palette_and_no_background_sentinel() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskConfig, colorize_mask, preferred_symmetry, resolve_mask, template_for
    symmetry = preferred_symmetry("FACE_EMBLEM")
    mask = resolve_mask(template_for("FACE_EMBLEM", 29, 23, symmetry=symmetry), DeterministicRNG(12), MaskConfig(symmetry=symmetry))
    palette = ("C01", "C03", "C05", "C07", "C09")
    cells = colorize_mask(mask, palette, DeterministicRNG(12))
    assert len(cells) == 29 * 23
    assert set(cells) == set(palette)
    assert all(cell in CANONICAL_PALETTE.ids for cell in cells)
    assert "BG01" not in cells and None not in cells


def test_colorization_is_deterministic_and_geometry_preserving() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskConfig, colorize_mask, preferred_symmetry, resolve_mask, template_for
    symmetry = preferred_symmetry("CORAL")
    mask = resolve_mask(template_for("CORAL", 31, 27, symmetry=symmetry), DeterministicRNG(12), MaskConfig(symmetry=symmetry))
    first = colorize_mask(mask, ("C01", "C02", "C03", "C04", "C05", "C06"), DeterministicRNG(12))
    second = colorize_mask(mask, ("C01", "C02", "C03", "C04", "C05", "C06"), DeterministicRNG(12))
    assert first == second
    assert tuple(value != first[0] for value in first) == tuple(mask.foreground_cells)


def test_colorization_rejects_too_small_or_invalid_palette() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskConfig, colorize_mask, preferred_symmetry, resolve_mask, template_for
    symmetry = preferred_symmetry("ROBOT")
    mask = resolve_mask(template_for("ROBOT", 20, 20, symmetry=symmetry), DeterministicRNG(1), MaskConfig(symmetry=symmetry))
    import pytest
    with pytest.raises(ValueError):
        colorize_mask(mask, ("C01", "C02"), DeterministicRNG(1))


def test_colorization_exposes_geometry_roles_and_no_singletons() -> None:
    from scrubbots_pixel_factory.generators.mask import (
        ColorRole,
        MaskConfig,
        color_component_sizes,
        colorize_with_roles,
        preferred_symmetry,
        resolve_mask,
        template_for,
    )
    symmetry = preferred_symmetry("ROBOT")
    mask = resolve_mask(
        template_for("ROBOT", 29, 23, symmetry=symmetry),
        DeterministicRNG(12),
        MaskConfig(symmetry=symmetry),
    )
    colored = colorize_with_roles(mask, ("C01", "C03", "C05", "C07", "C09"), DeterministicRNG(12))
    assert len(colored.cells) == len(colored.roles) == 29 * 23
    assert set(colored.roles) >= {
        ColorRole.NEGATIVE_SPACE,
        ColorRole.OUTLINE,
        ColorRole.BODY_PRIMARY,
        ColorRole.SECONDARY,
        ColorRole.DETAIL_ACCENT,
    }
    assert all(size >= 2 for sizes in color_component_sizes(colored.cells, 29, 23).values() for size in sizes)
    assert all(
        (role is ColorRole.NEGATIVE_SPACE) is (not foreground)
        for role, foreground in zip(colored.roles, mask.foreground_cells)
    )


@pytest.mark.parametrize(
    ("palette", "dimensions"),
    [
        (("C01", "C03", "C05"), (29, 23)),
        (("C01", "C03", "C05", "C07"), (29, 23)),
        (("C01", "C03", "C05", "C07", "C09"), (29, 23)),
        (tuple(f"C{i:02d}" for i in range(1, 11)), (59, 50)),
        (tuple(f"C{i:02d}" for i in range(1, 13)), (59, 50)),
    ],
)
def test_every_palette_color_has_explicit_pure_role_binding(
    palette: tuple[str, ...],
    dimensions: tuple[int, int],
) -> None:
    from scrubbots_pixel_factory.generators.mask import (
        MaskConfig,
        color_component_sizes,
        colorize_with_roles,
        preferred_symmetry,
        resolve_mask,
        template_for,
    )
    width, height = dimensions
    symmetry = preferred_symmetry("ROBOT")
    mask = resolve_mask(
        template_for("ROBOT", width, height, symmetry=symmetry),
        DeterministicRNG(23),
        MaskConfig(symmetry=symmetry),
    )
    first = colorize_with_roles(mask, palette, DeterministicRNG(23))
    second = colorize_with_roles(mask, palette, DeterministicRNG(23))
    assert first == second
    assert {item.color_id for item in first.role_assignments} == set(palette)
    observed = {
        item.color_id: {
            role.value
            for color, role in zip(first.cells, first.roles, strict=True)
            if color == item.color_id
        }
        for item in first.role_assignments
    }
    assert all(observed[item.color_id] == {item.role.value} for item in first.role_assignments)
    assert all(size >= 2 for sizes in color_component_sizes(first.cells, width, height).values() for size in sizes)


def test_impossible_role_capacity_fails_closed() -> None:
    from scrubbots_pixel_factory.generators.mask import (
        MaskCellState,
        MaskConfig,
        MaskDefinition,
        MaskContractError,
        SymmetryMode,
        colorize_with_roles,
        resolve_mask,
    )
    definition = MaskDefinition(4, 4, tuple([MaskCellState.REQUIRED] * 16))
    mask = resolve_mask(definition, DeterministicRNG(1), MaskConfig(symmetry=SymmetryMode.ASYMMETRIC, mutation=0, occupancy_floor_pct=0, occupancy_ceiling_pct=100))
    with pytest.raises(MaskContractError):
        colorize_with_roles(mask, tuple(f"C{i:02d}" for i in range(1, 13)), DeterministicRNG(1))
