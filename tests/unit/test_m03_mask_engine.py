import pytest

from scrubbots_pixel_factory.core import DeterministicRNG


def definition(width: int, height: int, required: tuple[tuple[int, int], ...] = ()):
    from scrubbots_pixel_factory.generators.mask import MaskCellState, MaskDefinition
    cells = [MaskCellState.RANDOM] * (width * height)
    for x, y in required:
        cells[y * width + x] = MaskCellState.REQUIRED
    return MaskDefinition(width, height, tuple(cells))


def test_required_and_forbidden_are_hard_and_random_is_seeded() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskCellState, MaskConfig, MaskDefinition, SymmetryMode, resolve_mask
    cells = [MaskCellState.RANDOM] * 100
    cells[0] = MaskCellState.REQUIRED
    cells[99] = MaskCellState.FORBIDDEN
    mask = resolve_mask(MaskDefinition(10, 10, tuple(cells)), DeterministicRNG(11), MaskConfig(symmetry=SymmetryMode.ASYMMETRIC, occupancy_floor_pct=0))
    assert mask.is_foreground(0, 0)
    assert not mask.is_foreground(9, 9)
    assert mask.row_major() == resolve_mask(MaskDefinition(10, 10, tuple(cells)), DeterministicRNG(11), MaskConfig(symmetry=SymmetryMode.ASYMMETRIC, occupancy_floor_pct=0)).row_major()
    assert mask.row_major() != resolve_mask(MaskDefinition(10, 10, tuple(cells)), DeterministicRNG(12), MaskConfig(symmetry=SymmetryMode.ASYMMETRIC, occupancy_floor_pct=0)).row_major()


@pytest.mark.parametrize("mode", ["HORIZONTAL", "VERTICAL", "HORIZONTAL_VERTICAL"])
@pytest.mark.parametrize("width,height", [(7, 6), (8, 5), (9, 7), (10, 8)])
def test_symmetry_handles_odd_even_rectangles(mode, width, height) -> None:
    from scrubbots_pixel_factory.generators.mask import MaskConfig, SymmetryMode, resolve_mask, symmetry_orbits
    mode = SymmetryMode(mode)
    mask = resolve_mask(definition(width, height, ((width // 2, height // 2),)), DeterministicRNG(31), MaskConfig(symmetry=mode, occupancy_floor_pct=0))
    for orbit in symmetry_orbits(width, height, mode):
        assert len({mask.foreground_cells[index] for index in orbit}) == 1


def test_asymmetric_mode_does_not_force_reflection() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskConfig, SymmetryMode, resolve_mask
    source = definition(9, 9)
    config = MaskConfig(symmetry=SymmetryMode.ASYMMETRIC, occupancy_floor_pct=0)
    assert any(
        any(mask.row_major()[y * 9 + x] != mask.row_major()[y * 9 + (8 - x)] for y in range(9) for x in range(9))
        for mask in (resolve_mask(source, DeterministicRNG(seed), config) for seed in (1, 2, 3))
    )


def test_mutation_changes_only_random_capable_cells() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskCellState, MaskConfig, MaskDefinition, SymmetryMode, resolve_mask
    cells = [MaskCellState.RANDOM] * 100
    cells[0] = MaskCellState.REQUIRED
    cells[99] = MaskCellState.FORBIDDEN
    source = MaskDefinition(10, 10, tuple(cells))
    mask = resolve_mask(source, DeterministicRNG(7), MaskConfig(symmetry=SymmetryMode.ASYMMETRIC, mutation=256, occupancy_floor_pct=0))
    assert mask.is_foreground(0, 0)
    assert not mask.is_foreground(9, 9)


def test_occupancy_floor_ceiling_and_impossible_bounds_fail_closed() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskCellState, MaskConfig, MaskContractError, MaskDefinition, SymmetryMode, resolve_mask
    source = definition(10, 10, tuple((x, y) for y in range(4) for x in range(4)))
    with pytest.raises(MaskContractError, match="occupancy ceiling"):
        resolve_mask(source, DeterministicRNG(1), MaskConfig(symmetry=SymmetryMode.ASYMMETRIC, occupancy_ceiling_pct=5))
    sparse = MaskDefinition(10, 10, tuple([MaskCellState.FORBIDDEN] * 99 + [MaskCellState.REQUIRED]))
    with pytest.raises(MaskContractError, match="occupancy floor"):
        resolve_mask(sparse, DeterministicRNG(1), MaskConfig(symmetry=SymmetryMode.ASYMMETRIC, occupancy_floor_pct=2))


def test_illegal_zero_dimensions_cannot_enter_engine() -> None:
    from scrubbots_pixel_factory.generators.mask import MaskConfig, MaskContractError, MaskDefinition
    with pytest.raises(MaskContractError):
        MaskDefinition(0, 10, ())
    with pytest.raises(MaskContractError):
        MaskConfig(occupancy_floor_pct=101)
