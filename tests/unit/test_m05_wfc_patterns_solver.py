from scrubbots_pixel_factory import DeterministicRNG
import pytest

from scrubbots_pixel_factory.generators.wfc import Exemplar, Pattern, PatternTable, WFCConfig, WFCContradiction, extract_pattern_table, solve_pattern_table


def _exemplar() -> Exemplar:
    colors = ("C01", "C02", "C03", "C04")
    return Exemplar(
        "scrubbots-wfc-exemplar", 1, "pattern-fixture", "TRAINING_MOTIF", 4, 4,
        tuple(colors[(x + y) % len(colors)] for y in range(4) for x in range(4)),
        "test", "project-authored fixture", "SYNTHETIC_TEST_ONLY",
    )


def _cyclic(size: int, colors: tuple[str, ...], identifier: str) -> Exemplar:
    return Exemplar(
        "scrubbots-wfc-exemplar", 1, identifier, "TRAINING_MOTIF", size, size,
        tuple(colors[(x + y) % len(colors)] for y in range(size) for x in range(size)),
        "test", "project-authored fixture", "SYNTHETIC_TEST_ONLY",
    )


def test_pattern_extraction_transforms_and_adjacency_are_canonical() -> None:
    config = WFCConfig(pattern_size=2, input_periodic=True, allow_rotations=True, allow_reflections=True)
    table = extract_pattern_table(_exemplar(), config, ("C01", "C02", "C03", "C04"))
    assert tuple(pattern.pattern_id for pattern in table.patterns) == tuple(range(len(table.patterns)))
    assert table.digest == extract_pattern_table(_exemplar(), config, ("C01", "C02", "C03", "C04")).digest
    assert all(table.adjacency[direction][pattern.pattern_id] == tuple(sorted(table.adjacency[direction][pattern.pattern_id])) for direction in table.adjacency for pattern in table.patterns)
    assert all(table.adjacency["RIGHT"][index] for index in range(len(table.patterns)))


def test_pattern_counts_separate_raw_windows_from_transform_observations() -> None:
    periodic_n2 = extract_pattern_table(_cyclic(6, ("C01", "C02", "C03"), "six"), WFCConfig(pattern_size=2, input_periodic=True), ("C01", "C02", "C03"))
    periodic_n3 = extract_pattern_table(_cyclic(8, ("C01", "C02", "C03", "C04", "C05", "C06"), "eight"), WFCConfig(pattern_size=3, input_periodic=True, allow_rotations=True), ("C01", "C02", "C03", "C04", "C05", "C06"))
    periodic_n3_both = extract_pattern_table(_cyclic(12, ("C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10"), "twelve"), WFCConfig(pattern_size=3, input_periodic=True, allow_rotations=True, allow_reflections=True), ("C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10"))
    nonperiodic = extract_pattern_table(_exemplar(), WFCConfig(pattern_size=2, input_periodic=False), ("C01", "C02", "C03", "C04"))
    assert periodic_n2.raw_extracted_window_count == 36
    assert periodic_n3.raw_extracted_window_count == 64
    assert periodic_n3_both.raw_extracted_window_count == 144
    assert periodic_n3.transformed_observation_count >= periodic_n3.raw_extracted_window_count
    assert periodic_n3_both.transformed_observation_count >= periodic_n3_both.raw_extracted_window_count
    assert nonperiodic.raw_extracted_window_count == 9


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


def test_solver_reports_deterministic_empty_wave_contradiction() -> None:
    table = PatternTable(
        2,
        (Pattern(0, ("C01", "C01", "C01", "C01"), 1), Pattern(1, ("C02", "C02", "C02", "C02"), 1)),
        {direction: ((), ()) for direction in ("LEFT", "RIGHT", "UP", "DOWN")},
        ("C01", "C02"), ("C01", "C02"), "diagnostic-table", 1, 1,
    )
    with pytest.raises(WFCContradiction) as error:
        solve_pattern_table(table, 4, 4, DeterministicRNG(1), False)
    assert (error.value.code, error.value.placement, error.value.detail) == ("EMPTY_WAVE", (1, 0), "no patterns remain from RIGHT constraint")


def test_solver_can_report_reconstruction_conflict_from_invalid_adjacency() -> None:
    patterns = (Pattern(0, ("C01", "C01", "C01", "C01"), 1), Pattern(1, ("C02", "C02", "C02", "C02"), 1))
    all_ids = ((0, 1), (0, 1))
    table = PatternTable(2, patterns, {direction: all_ids for direction in ("LEFT", "RIGHT", "UP", "DOWN")}, ("C01", "C02"), ("C01", "C02"), "conflict-table", 1, 1)
    found = None
    for seed in range(30):
        try:
            solve_pattern_table(table, 3, 3, DeterministicRNG(seed), False)
        except WFCContradiction as error:
            found = error
            break
    assert found is not None and found.code == "RECONSTRUCTION_CONFLICT"
