import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scrubbots_pixel_factory.quality import (
    GridInput,
    QualityCode,
    QualityInputError,
    QualityPolicy,
    analyze_grid,
    compare_grids,
    diversity_report,
    evaluate_grid,
    exact_duplicate_groups,
    logical_grid_hash,
)


def _subject_grid() -> list[str]:
    return [
        "C01", "C01", "C01", "C01", "C01",
        "C01", "C02", "C02", "C02", "C01",
        "C01", "C02", "C03", "C02", "C01",
        "C01", "C02", "C02", "C02", "C01",
        "C01", "C01", "C01", "C01", "C01",
    ]


def _checkerboard(width: int, height: int) -> list[str]:
    return [f"C{1 + ((x + y) % 2):02d}" for y in range(height) for x in range(width)]


def test_metrics_are_hand_computable_and_include_all_structural_families() -> None:
    analysis = analyze_grid(5, 5, _subject_grid())
    metrics = analysis.metrics
    assert analysis.negative_space.inferred_color == "C01"
    assert analysis.negative_space.boundary_counts == {"C01": 16, "C02": 0, "C03": 0}
    assert metrics.occupied_count == 9
    assert metrics.occupied_component_count == 1
    assert metrics.occupied_component_sizes == (9,)
    assert metrics.color_components[0].color_id == "C02"
    assert metrics.color_components[0].size == 8
    assert metrics.color_components[1].color_id == "C03"
    assert metrics.color_components[1].size == 1
    assert metrics.isolated_occupied_count == 0
    assert metrics.tiny_region_count == 0
    assert metrics.tiny_region_cell_count == 0
    assert metrics.occupied_color_counts == {"C02": 8, "C03": 1}
    assert metrics.largest_occupied_region_dominance == 1.0
    assert metrics.occupied_edge_touch_count == 0
    assert metrics.occupied_bounding_box == (1, 1, 3, 3)
    assert metrics.occupied_center_of_mass == (2.0, 2.0)
    assert metrics.horizontal_symmetry_score == 1.0
    assert metrics.vertical_symmetry_score == 1.0
    assert metrics.negative_space_count == 16
    assert metrics.negative_space_ratio == 0.64
    assert metrics.adjacency_edge_count == 40
    assert metrics.color_entropy > 0


def test_negative_space_ties_use_whole_grid_then_ascending_cid() -> None:
    cells = [
        "C01", "C01", "C01", "C02",
        "C01", "C01", "C02", "C02",
        "C01", "C01", "C02", "C02",
        "C01", "C02", "C02", "C02",
    ]
    analysis = analyze_grid(4, 4, cells)
    assert analysis.negative_space.boundary_counts == {"C01": 6, "C02": 6}
    assert analysis.negative_space.whole_grid_counts == {"C01": 8, "C02": 8}
    assert analysis.negative_space.inferred_color == "C01"


def test_rectangular_grid_and_edge_cases() -> None:
    rectangular = ["C01"] * 6 + ["C01", "C02", "C02", "C02", "C02", "C01"]
    analysis = analyze_grid(6, 2, rectangular)
    assert analysis.metrics.occupied_count == 4
    assert analysis.metrics.occupied_bounding_box == (1, 1, 4, 1)
    assert analyze_grid(1, 1, ["C01"]).metrics.occupied_count == 0
    assert analyze_grid(3, 3, ["C01"] * 9).metrics.color_entropy == 0.0


def test_known_answer_one_cell_full_interior_and_equal_size_components() -> None:
    one_cell = ["C01"] * 25
    one_cell[12] = "C02"
    one_analysis = analyze_grid(5, 5, one_cell)
    assert one_analysis.metrics.occupied_count == 1
    assert one_analysis.metrics.occupied_component_sizes == (1,)
    assert one_analysis.metrics.isolated_occupied_count == 1
    assert one_analysis.metrics.tiny_region_count == 1

    full_interior = ["C01"] * 25
    for y in range(1, 4):
        for x in range(1, 4):
            full_interior[y * 5 + x] = "C02"
    interior_analysis = analyze_grid(5, 5, full_interior)
    assert interior_analysis.metrics.occupied_count == 9
    assert interior_analysis.metrics.occupied_component_count == 1
    assert interior_analysis.metrics.occupied_component_sizes == (9,)
    assert interior_analysis.metrics.negative_space_count == 16

    equal_components = ["C01"] * 25
    for index in (6, 11, 13, 18):
        equal_components[index] = "C02" if index in (6, 11) else "C03"
    equal_analysis = analyze_grid(5, 5, equal_components)
    assert equal_analysis.metrics.occupied_component_sizes == (2, 2)
    assert equal_analysis.metrics.occupied_component_count == 2
    assert equal_analysis.metrics.tiny_region_count == 2
    assert equal_analysis.metrics.largest_occupied_region_dominance == 0.5
    assert equal_analysis.metrics.largest_color_dominance == 0.5


def test_directional_symmetry_reflections_match_documented_axes() -> None:
    # horizontal_symmetry_score is left-right reflection across the vertical
    # centerline: (x, y) compares with (width - 1 - x, y).
    horizontal_only = [
        "C01", "C01", "C01", "C01", "C01",
        "C01", "C02", "C03", "C02", "C01",
        "C01", "C02", "C02", "C02", "C01",
        "C01", "C02", "C04", "C02", "C01",
        "C01", "C01", "C01", "C01", "C01",
    ]
    horizontal_analysis = analyze_grid(5, 5, horizontal_only)
    assert horizontal_analysis.metrics.horizontal_symmetry_score == 1.0
    assert horizontal_analysis.metrics.vertical_symmetry_score < 1.0

    # vertical_symmetry_score is top-bottom reflection across the horizontal
    # centerline: (x, y) compares with (x, height - 1 - y).
    vertical_only = [
        "C01", "C01", "C01", "C01", "C01",
        "C01", "C02", "C03", "C04", "C01",
        "C01", "C02", "C02", "C02", "C01",
        "C01", "C02", "C03", "C04", "C01",
        "C01", "C01", "C01", "C01", "C01",
    ]
    vertical_analysis = analyze_grid(5, 5, vertical_only)
    assert vertical_analysis.metrics.vertical_symmetry_score == 1.0
    assert vertical_analysis.metrics.horizontal_symmetry_score < 1.0

    asymmetric = ["C01"] * 25
    asymmetric[6] = "C02"
    asymmetric[12] = "C02"
    asymmetric[18] = "C03"
    asymmetric_analysis = analyze_grid(5, 5, asymmetric)
    assert asymmetric_analysis.metrics.horizontal_symmetry_score < 1.0
    assert asymmetric_analysis.metrics.vertical_symmetry_score < 1.0


def test_invalid_grid_input_fails_closed_with_stable_codes() -> None:
    assert evaluate_grid(2, 2, ["C01"]).rejection_codes == (QualityCode.DIMENSION_MISMATCH.value,)
    assert evaluate_grid(2, 2, ["BG01"] * 4).rejection_codes == (QualityCode.OFF_PALETTE.value,)
    with pytest.raises(QualityInputError) as error:
        analyze_grid(2, 2, ["C17"] * 4)
    assert error.value.code == QualityCode.OFF_PALETTE.value


def test_rejection_policy_is_explicit_and_multicode_order_is_stable() -> None:
    noisy = _checkerboard(4, 4)
    policy = QualityPolicy(max_isolated_ratio=0.1, max_tiny_cell_ratio=0.1, max_checkerboard_score=0.9, max_color_dominance_ratio=1.0)
    report = evaluate_grid(4, 4, noisy, policy=policy)
    assert report.accepted is False
    assert report.rejection_codes == (
        QualityCode.EXCESSIVE_SALT_AND_PEPPER.value,
        QualityCode.EXCESSIVE_TINY_REGIONS.value,
        QualityCode.CHECKERBOARD_NOISE.value,
    )
    assert report.rejection_codes == evaluate_grid(4, 4, noisy, policy=policy).rejection_codes


def test_required_bad_fixture_classes_and_good_counterexample() -> None:
    checker = evaluate_grid(6, 6, _checkerboard(6, 6))
    assert QualityCode.CHECKERBOARD_NOISE.value in checker.rejection_codes

    isolated = ["C01"] * 25
    for index in (6, 8, 16, 18):
        isolated[index] = "C02"
    isolated_report = evaluate_grid(5, 5, isolated, policy=QualityPolicy(max_isolated_ratio=0.1))
    assert QualityCode.EXCESSIVE_SALT_AND_PEPPER.value in isolated_report.rejection_codes

    fragmented = ["C01"] * 49
    for index in (8, 10, 36, 38):
        fragmented[index] = "C02"
    fragmented_report = evaluate_grid(7, 7, fragmented, policy=QualityPolicy(max_tiny_cell_ratio=0.1))
    assert QualityCode.EXCESSIVE_TINY_REGIONS.value in fragmented_report.rejection_codes

    slab = ["C01"] * 400
    for y in range(1, 19):
        for x in range(1, 19):
            slab[y * 20 + x] = "C02"
    slab_report = evaluate_grid(20, 20, slab)
    assert QualityCode.FULL_SINGLE_SHAPE_SLAB.value in slab_report.rejection_codes

    good = evaluate_grid(5, 5, _subject_grid())
    assert good.accepted is True


def test_each_required_rejection_code_is_directly_asserted() -> None:
    assert evaluate_grid(3, 3, ["C01"] * 9).rejection_codes == (QualityCode.EMPTY_ARTWORK.value,)

    slab = ["C01"] * 400
    for y in range(1, 19):
        for x in range(1, 19):
            slab[y * 20 + x] = "C02"
    assert QualityCode.FULL_SINGLE_SHAPE_SLAB.value in evaluate_grid(20, 20, slab).rejection_codes

    isolated = ["C01"] * 25
    for index in (6, 8, 16, 18):
        isolated[index] = "C02"
    assert QualityCode.EXCESSIVE_SALT_AND_PEPPER.value in evaluate_grid(5, 5, isolated, policy=QualityPolicy(max_isolated_ratio=0.1)).rejection_codes

    fragmented = ["C01"] * 49
    for index in (8, 10, 36, 38):
        fragmented[index] = "C02"
    assert QualityCode.EXCESSIVE_TINY_REGIONS.value in evaluate_grid(7, 7, fragmented, policy=QualityPolicy(max_tiny_cell_ratio=0.1)).rejection_codes

    dominant = ["C01"] * 25
    for index in (6, 7, 8, 11, 13, 16, 17, 18):
        dominant[index] = "C02"
    dominant[12] = "C03"
    assert QualityCode.DOMINANCE_VIOLATION.value in evaluate_grid(5, 5, dominant, policy=QualityPolicy(max_color_dominance_ratio=0.5)).rejection_codes
    assert QualityCode.CHECKERBOARD_NOISE.value in evaluate_grid(4, 4, _checkerboard(4, 4), policy=QualityPolicy(max_checkerboard_score=0.9)).rejection_codes
    assert QualityCode.DIFFICULTY_COLOR_COUNT.value in evaluate_grid(20, 20, ["C01", "C02"] * 200, policy=QualityPolicy(difficulty="EASY")).rejection_codes
    assert QualityCode.OFF_PALETTE.value in evaluate_grid(2, 2, ["BG01"] * 4).rejection_codes
    assert QualityCode.DIMENSION_MISMATCH.value in evaluate_grid(2, 2, ["C01"] * 3).rejection_codes


def test_color_dominance_aggregates_split_components_and_honors_one_color_threshold() -> None:
    split = ["C01"] * 81
    for y in range(1, 4):
        for x in (1, 2, 3, 5, 6, 7):
            split[y * 9 + x] = "C02"
    for y in range(5, 7):
        for x in (3, 4):
            split[y * 9 + x] = "C03"
    split_analysis = analyze_grid(9, 9, split)
    assert split_analysis.metrics.occupied_component_count == 3
    assert split_analysis.metrics.largest_occupied_region_dominance == round(9 / 22, 8)
    assert split_analysis.metrics.largest_color_dominance == round(18 / 22, 8)
    assert split_analysis.metrics.occupied_color_counts == {"C02": 18, "C03": 4}
    assert QualityCode.DOMINANCE_VIOLATION.value in evaluate_grid(9, 9, split, policy=QualityPolicy(max_color_dominance_ratio=0.8)).rejection_codes

    one_color = ["C01"] * 25
    for y in range(1, 4):
        for x in range(1, 4):
            one_color[y * 5 + x] = "C02"
    strict = evaluate_grid(5, 5, one_color, policy=QualityPolicy(max_color_dominance_ratio=0.5))
    assert QualityCode.DOMINANCE_VIOLATION.value in strict.rejection_codes
    assert QualityCode.DOMINANCE_VIOLATION.value not in evaluate_grid(5, 5, one_color).rejection_codes


def test_difficulty_color_count_is_checked_only_when_supplied() -> None:
    cells = ["C01", "C02"] * 200
    report = evaluate_grid(20, 20, cells, policy=QualityPolicy(difficulty="EASY"))
    assert QualityCode.DIFFICULTY_COLOR_COUNT.value in report.rejection_codes


def test_grid_hash_is_framed_stable_and_sensitive() -> None:
    cells = _subject_grid()
    first = logical_grid_hash(5, 5, cells)
    assert first == logical_grid_hash(5, 5, tuple(cells))
    assert first != logical_grid_hash(1, 25, cells)
    changed = list(cells)
    changed[12] = "C04"
    assert first != logical_grid_hash(5, 5, changed)


def test_exact_duplicates_and_separate_near_similarity_metrics() -> None:
    base = GridInput(5, 5, _subject_grid())
    same = GridInput(5, 5, _subject_grid())
    near_cells = _subject_grid()
    near_cells[12] = "C04"
    near = GridInput(5, 5, near_cells)
    different = GridInput(5, 5, ["C01"] * 25)
    assert exact_duplicate_groups((base, same, near)) == ((0, 1),)
    similarity = compare_grids(base, near)
    assert similarity.comparable is True
    assert similarity.occupancy_mask_similarity == 1.0
    assert 0 < similarity.color_layout_similarity < 1
    assert compare_grids(base, GridInput(4, 5, ["C01"] * 20)).comparable is False
    report = diversity_report((base, same, near, different), near_duplicate_threshold=0.9)
    assert report.exact_duplicate_groups == ((0, 1),)
    assert any(pair.first_index == 0 and pair.second_index == 2 for pair in report.near_duplicate_pairs)


def test_canonical_report_is_byte_stable_and_cross_process() -> None:
    cells = _subject_grid()
    report = evaluate_grid(5, 5, cells)
    assert report.canonical_bytes() == evaluate_grid(5, 5, cells).canonical_bytes()
    root = Path(__file__).parents[2]
    code = """
from scrubbots_pixel_factory.quality import evaluate_grid
cells = ['C01','C01','C01','C01','C01','C01','C02','C02','C02','C01','C01','C02','C03','C02','C01','C01','C02','C02','C02','C01','C01','C01','C01','C01','C01']
print(evaluate_grid(5, 5, cells).canonical_bytes().decode())
"""
    values = []
    for seed in ("1", "987"):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(root / "src")
        environment["PYTHONHASHSEED"] = seed
        result = subprocess.run([sys.executable, "-c", code], cwd=root, env=environment, capture_output=True, text=True, check=True)
        values.append(result.stdout)
    assert values[0] == values[1]


def test_no_resize_or_runtime_network_symbols_in_quality_source() -> None:
    root = Path(__file__).parents[2]
    source = "\n".join(path.read_text(encoding="utf-8") for path in (root / "src" / "scrubbots_pixel_factory" / "quality").rglob("*.py"))
    assert "import socket" not in source
    assert "import requests" not in source
    assert "subprocess" not in source
    assert ".resize(" not in source
    assert "resample(" not in source
    assert "Image.Resampling" not in source
