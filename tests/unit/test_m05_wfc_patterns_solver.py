from scrubbots_pixel_factory import DeterministicRNG
from scrubbots_pixel_factory.generators.wfc import Exemplar, WFCConfig, extract_pattern_table, solve_pattern_table


def _exemplar() -> Exemplar:
    colors = ("C01", "C02", "C03", "C04")
    return Exemplar(
        "scrubbots-wfc-exemplar", 1, "pattern-fixture", "TRAINING_MOTIF", 4, 4,
        tuple(colors[(x + y) % len(colors)] for y in range(4) for x in range(4)),
        "test", "project-authored fixture", "SYNTHETIC_TEST_ONLY",
    )


def test_pattern_extraction_transforms_and_adjacency_are_canonical() -> None:
    config = WFCConfig(pattern_size=2, input_periodic=True, allow_rotations=True, allow_reflections=True)
    table = extract_pattern_table(_exemplar(), config, ("C01", "C02", "C03", "C04"))
    assert tuple(pattern.pattern_id for pattern in table.patterns) == tuple(range(len(table.patterns)))
    assert table.digest == extract_pattern_table(_exemplar(), config, ("C01", "C02", "C03", "C04")).digest
    assert all(table.adjacency[direction][pattern.pattern_id] == tuple(sorted(table.adjacency[direction][pattern.pattern_id])) for direction in table.adjacency for pattern in table.patterns)
    assert all(table.adjacency["RIGHT"][index] for index in range(len(table.patterns)))


def test_solver_handles_exact_rectangles_and_periodic_placement() -> None:
    table = extract_pattern_table(_exemplar(), WFCConfig(pattern_size=2, input_periodic=True), ("C01", "C02", "C03", "C04"))
    nonperiodic = solve_pattern_table(table, 9, 7, DeterministicRNG(42), False)
    periodic = solve_pattern_table(table, 8, 8, DeterministicRNG(42), True)
    assert len(nonperiodic.logical_grid) == 63
    assert len(periodic.logical_grid) == 64
    assert (nonperiodic.placement_width, nonperiodic.placement_height) == (8, 6)
    assert (periodic.placement_width, periodic.placement_height) == (8, 8)
    assert set(nonperiodic.logical_grid) == set(periodic.logical_grid) == {"C01", "C02", "C03", "C04"}


def test_solver_is_process_stable_without_hash_order_dependence() -> None:
    table = extract_pattern_table(_exemplar(), WFCConfig(pattern_size=3, input_periodic=True, allow_rotations=True), ("C01", "C02", "C03", "C04"))
    first = solve_pattern_table(table, 11, 8, DeterministicRNG("same"), False)
    second = solve_pattern_table(table, 11, 8, DeterministicRNG("same"), False)
    assert first == second
