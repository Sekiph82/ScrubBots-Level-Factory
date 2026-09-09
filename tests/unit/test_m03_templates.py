from scrubbots_pixel_factory.core import DeterministicRNG


DIFFICULTY_RECTANGLES = {
    "EASY": ((20, 20), (29, 23)),
    "MEDIUM": ((30, 39), (37, 32)),
    "HARD": ((40, 49), (48, 41)),
    "VERY_HARD": ((50, 59), (59, 50)),
}


def test_all_ten_families_are_original_logical_definitions() -> None:
    from scrubbots_pixel_factory.generators import FAMILY_NAMES
    from scrubbots_pixel_factory.generators.mask import template_for
    assert len(FAMILY_NAMES) == 10
    for family in FAMILY_NAMES:
        definition = template_for(family, 29, 23)
        assert definition.width == 29 and definition.height == 23
        assert any(cell.value == "REQUIRED" for cell in definition.cells)
        assert any(cell.value == "FORBIDDEN" for cell in definition.cells)


def test_each_family_varies_across_fixed_seeds() -> None:
    from scrubbots_pixel_factory.generators import FAMILY_NAMES
    from scrubbots_pixel_factory.generators.mask import MaskConfig, preferred_symmetry, resolve_mask, template_for
    for family in FAMILY_NAMES:
        masks = {
            resolve_mask(template_for(family, 29, 23, symmetry=preferred_symmetry(family)), DeterministicRNG(seed), MaskConfig(symmetry=preferred_symmetry(family))).row_major()
            for seed in (3, 19, 71)
        }
        assert len(masks) > 1, family


def test_every_family_supports_all_difficulties_and_rectangles() -> None:
    from scrubbots_pixel_factory.generators import FAMILY_NAMES
    from scrubbots_pixel_factory.generators.mask import MaskConfig, ResolvedMask, preferred_symmetry, resolve_mask, template_for
    for family in FAMILY_NAMES:
        for difficulty, rectangles in DIFFICULTY_RECTANGLES.items():
            for width, height in rectangles:
                symmetry = preferred_symmetry(family)
                mask = resolve_mask(template_for(family, width, height, symmetry=symmetry), DeterministicRNG(17), MaskConfig(symmetry=symmetry))
                assert isinstance(mask, ResolvedMask)
                assert len(mask.row_major()) == width * height
                assert 0 < mask.foreground_count < width * height


def test_horizontal_vertical_and_asymmetric_template_modes_are_supported() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskConfig, SymmetryMode, resolve_mask, template_for
    for mode in SymmetryMode:
        mask = resolve_mask(template_for("ROBOT", 28, 22, symmetry=mode), DeterministicRNG(23), MaskConfig(symmetry=mode))
        assert mask.foreground_count > 0


def test_template_source_has_no_resize_or_image_dependency() -> None:
    from pathlib import Path
    source = Path("src/scrubbots_pixel_factory/generators/mask/templates.py").read_text(encoding="utf-8").lower()
    assert "resize" not in source and "interpol" not in source and "image" not in source
