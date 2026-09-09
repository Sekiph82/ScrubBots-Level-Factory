from scrubbots_pixel_factory import CANONICAL_PALETTE
from scrubbots_pixel_factory.core import DeterministicRNG


def test_colorization_uses_exact_palette_and_no_background_sentinel() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskConfig, colorize_mask, resolve_mask, template_for
    mask = resolve_mask(template_for("FACE_EMBLEM", 29, 23), DeterministicRNG(12), MaskConfig())
    palette = ("C01", "C03", "C05", "C07", "C09")
    cells = colorize_mask(mask, palette, DeterministicRNG(12))
    assert len(cells) == 29 * 23
    assert set(cells) == set(palette)
    assert all(cell in CANONICAL_PALETTE.ids for cell in cells)
    assert "BG01" not in cells and None not in cells


def test_colorization_is_deterministic_and_geometry_preserving() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskConfig, colorize_mask, resolve_mask, template_for
    mask = resolve_mask(template_for("CORAL", 31, 27), DeterministicRNG(12), MaskConfig())
    first = colorize_mask(mask, ("C01", "C02", "C03", "C04", "C05", "C06"), DeterministicRNG(12))
    second = colorize_mask(mask, ("C01", "C02", "C03", "C04", "C05", "C06"), DeterministicRNG(12))
    assert first == second
    assert tuple(value != first[0] for value in first) == tuple(mask.foreground_cells)


def test_colorization_rejects_too_small_or_invalid_palette() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskConfig, colorize_mask, resolve_mask, template_for
    mask = resolve_mask(template_for("ROBOT", 20, 20), DeterministicRNG(1), MaskConfig())
    import pytest
    with pytest.raises(ValueError):
        colorize_mask(mask, ("C01", "C02"), DeterministicRNG(1))
