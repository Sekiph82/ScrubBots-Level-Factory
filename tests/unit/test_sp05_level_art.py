from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
import struct
import zlib

import pytest

from scrubbots_pixel_factory import (
    BG01,
    CANONICAL_PALETTE,
    Difficulty,
    SemanticDecodeError,
    SemanticLevelArtArtifact,
    SemanticLevelArtError,
    SemanticLevelArtReport,
    SemanticLevelArtRequest,
    SemanticNormalizedArtifact,
    SemanticRawArtifact,
    SemanticNormalizationRequest,
    actual_used_palette_ids,
    cell_majority_rgba_grid,
    compile_semantic_level_art,
    enforce_difficulty_color_budget,
    normalize_semantic_artifact,
    palette_snap_grid,
    PRODUCTION_COLOR_ENVELOPE_POLICY_VERSION,
    validate_production_dimensions,
)
from scrubbots_pixel_factory.semantic.normalization.level_art import _build_artifact, _build_report


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def _rgba_png(width: int, height: int, pixels: bytes, ancillary: bytes = b"") -> bytes:
    assert len(pixels) == width * height * 4
    rows = b"".join(b"\x00" + pixels[row * width * 4 : (row + 1) * width * 4] for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return PNG_SIGNATURE + _chunk(b"IHDR", header) + ancillary + _chunk(b"IDAT", zlib.compress(rows, 9)) + _chunk(b"IEND", b"")


def _rgb(color_id: str) -> bytes:
    return bytes(CANONICAL_PALETTE.rgb_for(color_id) + (255,))


def _raw(tmp_path: Path, name: str, width: int, height: int, pixels: bytes, ancillary: bytes = b"") -> SemanticRawArtifact:
    path = tmp_path / name
    path.write_bytes(_rgba_png(width, height, pixels, ancillary))
    return SemanticRawArtifact.from_local_file(path)


def _request(raw: SemanticRawArtifact, difficulty: Difficulty | str = Difficulty.EASY, width: int = 20, height: int = 20, **changes: object) -> SemanticLevelArtRequest:
    values: dict[str, object] = {"source_raw_artifact_digest": raw.digest(), "difficulty": difficulty, "target_width": width, "target_height": height}
    values.update(changes)
    return SemanticLevelArtRequest(**values)


def _cells_with_counts(ids: tuple[str, ...], repeats: tuple[int, ...] | None = None) -> tuple[str, ...]:
    if repeats is None:
        repeats = tuple(1 for _ in ids)
    return tuple(color_id for color_id, count in zip(ids, repeats) for _ in range(count))


def test_exact_size_level_art_is_one_source_pixel_per_cell_and_not_area_average(tmp_path: Path) -> None:
    colors = (_rgb("C01"), _rgb("C02"), _rgb("C03"))
    pixels = b"".join(colors[(index + index // 20) % 3] for index in range(20 * 20))
    raw = _raw(tmp_path, "exact.png", 20, 20, pixels)
    artifact = compile_semantic_level_art(raw, _request(raw))
    assert artifact.logical_cells == tuple(f"C{(index + index // 20) % 3 + 1:02d}" for index in range(20 * 20))
    assert artifact.used_palette_ids == ("C01", "C02", "C03")
    assert artifact.report.cell_majority_policy_version == "CELL_MAJORITY_V1"
    assert artifact.report.final_logical_grid_digest == artifact.logical_grid_digest
    assert "AREA_AVERAGE_V1" not in artifact.canonical_bytes().decode("utf-8")


def test_cell_majority_4x4_to_2x2_chooses_local_winners() -> None:
    red = bytes((230, 20, 20, 255))
    blue = bytes((20, 20, 230, 255))
    green = bytes((20, 230, 20, 255))
    rows = [
        (red, red, blue, blue),
        (red, blue, blue, blue),
        (green, green, red, red),
        (green, red, red, red),
    ]
    winners = cell_majority_rgba_grid(b"".join(pixel for row in rows for pixel in row), 4, 4, 2, 2)
    assert winners == (red, blue, green, red)


def test_non_divisible_rectangular_footprints_are_deterministic() -> None:
    pixels = b"".join(bytes(((index * 13 + 1) % 256, (index * 17 + 2) % 256, (index * 19 + 3) % 256, 255)) for index in range(7 * 5))
    first = cell_majority_rgba_grid(pixels, 7, 5, 3, 2)
    second = cell_majority_rgba_grid(pixels, 7, 5, 3, 2)
    assert first == second and len(first) == 6 and all(len(value) == 4 and value[3] == 255 for value in first)


def test_exact_majority_ties_use_lexicographic_rgba() -> None:
    low = bytes((10, 20, 30, 255))
    high = bytes((11, 19, 30, 255))
    assert cell_majority_rgba_grid(low + high + high + low, 2, 2, 1, 1) == (low,)


def test_source_smaller_than_target_and_nonopaque_winners_fail_closed(tmp_path: Path) -> None:
    raw = _raw(tmp_path, "small.png", 20, 19, _rgb("C01") * (20 * 19))
    with pytest.raises(SemanticLevelArtError) as error:
        compile_semantic_level_art(raw, _request(raw, width=20, height=20))
    assert error.value.code == "SOURCE_SMALLER_THAN_TARGET"
    with pytest.raises(SemanticLevelArtError) as error:
        cell_majority_rgba_grid(bytes((10, 20, 30, 0)) * 4, 2, 2, 1, 1)
    assert error.value.code == "NON_OPAQUE_CELL"


def test_palette_snap_uses_canonical_exact_nearest_and_index_tie_rules() -> None:
    assert palette_snap_grid([_rgb("C07")]) == ("C07",)
    assert palette_snap_grid([(67, 130, 216, 255)]) == ("C07",)
    assert palette_snap_grid([(237, 204, 118, 255)]) == ("C03",)  # equal distance to C03/C12; C03 has lower index
    assert palette_snap_grid([BG01.rgb + (255,)])[0] != BG01.id
    assert all(value in CANONICAL_PALETTE.ids for value in palette_snap_grid([(1, 2, 3, 255), (254, 253, 252, 255)]))


@pytest.mark.parametrize("difficulty", list(Difficulty))
def test_above_production_maximum_reduces_to_exact_global_maximum(difficulty: Difficulty) -> None:
    cells = _cells_with_counts(tuple(f"C{index:02d}" for index in range(1, 17)))
    final, details = enforce_difficulty_color_budget(difficulty, cells)
    assert len(actual_used_palette_ids(final)) == 12
    assert details["final_used_color_count"] == 12


@pytest.mark.parametrize("color_count", [13, 14, 15, 16])
def test_every_over_envelope_color_count_reduces_deterministically_without_new_ids(color_count: int) -> None:
    cells = _cells_with_counts(tuple(f"C{index:02d}" for index in range(1, color_count + 1)))
    first, first_details = enforce_difficulty_color_budget(Difficulty.VERY_HARD, cells)
    repeat, repeat_details = enforce_difficulty_color_budget(Difficulty.VERY_HARD, cells)
    second, second_details = enforce_difficulty_color_budget(Difficulty.EASY, cells)
    assert first == repeat
    assert first_details == repeat_details
    assert len(actual_used_palette_ids(first)) == len(actual_used_palette_ids(second)) == 12
    assert set(actual_used_palette_ids(first)) <= set(cells)
    assert first == second
    assert first_details == second_details


def test_budget_preserves_in_band_and_rejects_below_minimum_without_fabrication() -> None:
    cells = _cells_with_counts(("C01", "C02", "C03"), (4, 3, 2))
    final, details = enforce_difficulty_color_budget(Difficulty.EASY, cells)
    assert final == cells and details["weighted_subset_cost"] == 0
    with pytest.raises(SemanticLevelArtError) as error:
        enforce_difficulty_color_budget(Difficulty.EASY, ("C01",) * 10)
    assert error.value.code == "INSUFFICIENT_USED_COLORS"


def test_current_production_color_envelope_is_lane_independent() -> None:
    for difficulty, count in ((Difficulty.EASY, 3), (Difficulty.EASY, 8), (Difficulty.VERY_HARD, 5), (Difficulty.HARD, 12)):
        cells = _cells_with_counts(tuple(f"C{index:02d}" for index in range(1, count + 1)))
        final, details = enforce_difficulty_color_budget(difficulty, cells)
        assert final == cells
        assert details["final_used_color_count"] == count


def test_removed_colors_map_cell_by_cell_to_nearest_retained_palette_color() -> None:
    ids = tuple(f"C{index:02d}" for index in range(1, 17))
    cells = _cells_with_counts(ids)
    final, details = enforce_difficulty_color_budget(Difficulty.EASY, cells)
    retained = tuple(details["retained_palette_ids"])
    assert len(retained) == 12
    for source_id, final_id in zip(cells, final):
        if source_id in retained:
            assert final_id == source_id
            continue
        source_rgb = CANONICAL_PALETTE.rgb_for(source_id)
        expected = min(
            retained,
            key=lambda candidate: (sum((left - right) ** 2 for left, right in zip(source_rgb, CANONICAL_PALETTE.rgb_for(candidate))), int(candidate[1:])),
        )
        assert final_id == expected
    assert set(actual_used_palette_ids(final)) <= set(ids)


def test_weighted_subset_optimization_retains_the_hand_computed_low_cost_subset() -> None:
    ids = tuple(f"C{index:02d}" for index in range(1, 14))
    cells = _cells_with_counts(ids, (20,) * 12 + (1,))
    final, details = enforce_difficulty_color_budget(Difficulty.EASY, cells)
    assert details["retained_palette_ids"] == tuple(f"C{index:02d}" for index in range(1, 13))
    assert len(actual_used_palette_ids(final)) == 12


def test_weighted_subset_ties_resolve_by_canonical_palette_tuple() -> None:
    ids = tuple(f"C{index:02d}" for index in range(1, 14))
    final, details = enforce_difficulty_color_budget(Difficulty.EASY, ids)
    assert details["retained_palette_ids"] == tuple(f"C{index:02d}" for index in range(1, 13))
    assert actual_used_palette_ids(final) == tuple(f"C{index:02d}" for index in range(1, 13))


def test_legal_rectangles_work_for_each_difficulty_and_24x24_is_not_special(tmp_path: Path) -> None:
    cases = [(Difficulty.EASY, 20, 29, 3), (Difficulty.MEDIUM, 30, 31, 6), (Difficulty.HARD, 40, 41, 8), (Difficulty.VERY_HARD, 50, 51, 10)]
    for index, (difficulty, width, height, color_count) in enumerate(cases):
        palette = tuple(f"C{color:02d}" for color in range(1, color_count + 1))
        pixels = b"".join(_rgb(palette[cell % color_count]) for cell in range(width * height))
        raw = _raw(tmp_path, f"rectangle-{index}.png", width, height, pixels)
        artifact = compile_semantic_level_art(raw, _request(raw, difficulty, width, height))
        assert (artifact.target_width, artifact.target_height) == (width, height)
        assert artifact.used_palette_ids == palette
    bad = SemanticRawArtifact.from_local_file(tmp_path / "rectangle-0.png")
    with pytest.raises(SemanticLevelArtError):
        _request(bad, Difficulty.EASY, width=19)


def test_current_production_dimensions_are_independent_of_lane(tmp_path: Path) -> None:
    assert validate_production_dimensions(20, 20) == (20, 20)
    assert validate_production_dimensions(20, 59) == (20, 59)
    assert validate_production_dimensions(59, 20) == (59, 20)
    assert validate_production_dimensions(59, 59) == (59, 59)
    for invalid in (19, 60):
        with pytest.raises(ValueError):
            validate_production_dimensions(invalid, 20)
        with pytest.raises(ValueError):
            validate_production_dimensions(20, invalid)
    pixels = b"".join(_rgb(f"C{index % 8 + 1:02d}") for index in range(38 * 38))
    raw = _raw(tmp_path, "easy-38.png", 38, 38, pixels)
    easy = compile_semantic_level_art(raw, _request(raw, Difficulty.EASY, 38, 38))
    very_hard = compile_semantic_level_art(raw, _request(raw, Difficulty.VERY_HARD, 38, 38))
    very_hard_24 = compile_semantic_level_art(raw, _request(raw, Difficulty.VERY_HARD, 24, 24))
    assert easy.used_palette_ids == tuple(f"C{index:02d}" for index in range(1, 9))
    assert very_hard.used_palette_ids == easy.used_palette_ids
    assert very_hard.logical_cells == easy.logical_cells
    assert very_hard_24.target_width == 24 and very_hard_24.target_height == 24
    assert very_hard.report.majority_rgba_sha256 == easy.report.majority_rgba_sha256
    assert very_hard.report.snapped_grid_digest == easy.report.snapped_grid_digest
    assert very_hard.report.final_logical_grid_digest == easy.report.final_logical_grid_digest
    assert very_hard.report.original_used_palette_ids == easy.report.original_used_palette_ids
    assert very_hard.report.original_used_color_count == easy.report.original_used_color_count
    assert very_hard.report.retained_palette_ids == easy.report.retained_palette_ids
    assert very_hard.report.weighted_subset_cost == easy.report.weighted_subset_cost
    assert very_hard.report.final_used_palette_ids == easy.report.final_used_palette_ids
    assert very_hard.report.final_used_color_count == easy.report.final_used_color_count
    assert easy.report.difficulty_budget_policy_version == PRODUCTION_COLOR_ENVELOPE_POLICY_VERSION


def test_provenance_determinism_raw_change_and_request_identity(tmp_path: Path) -> None:
    pixels = _rgb("C01") * 100 + _rgb("C02") * 100 + _rgb("C03") * 200
    first_raw = _raw(tmp_path, "first.png", 20, 20, pixels)
    second_raw = _raw(tmp_path, "second.png", 20, 20, pixels, _chunk(b"tEXt", b"byte-distinct"))
    first_request = _request(first_raw)
    first = compile_semantic_level_art(first_raw, first_request)
    repeat = compile_semantic_level_art(first_raw, first_request)
    second = compile_semantic_level_art(second_raw, _request(second_raw))
    assert first.canonical_bytes() == repeat.canonical_bytes() and first.digest() == repeat.digest()
    assert first.logical_cells == second.logical_cells
    assert first.source_raw_artifact_digest != second.source_raw_artifact_digest and first.digest() != second.digest()
    assert first_request.digest() != _request(first_raw, Difficulty.MEDIUM, 30, 30).digest()


def test_level_art_artifact_is_sealed_and_cannot_be_minted_by_direct_or_replace_construction(tmp_path: Path) -> None:
    pixels = _rgb("C01") * 100 + _rgb("C02") * 100 + _rgb("C03") * 200
    raw = _raw(tmp_path, "sealed.png", 20, 20, pixels)
    artifact = compile_semantic_level_art(raw, _request(raw))
    report_values = {item.name: getattr(artifact.report, item.name) for item in fields(SemanticLevelArtReport) if item.init}
    with pytest.raises(SemanticLevelArtError):
        SemanticLevelArtReport(**report_values)
    with pytest.raises(SemanticLevelArtError):
        replace(artifact.report, raw_sha256="e" * 64)
    tampered_report = artifact.report
    report_tamper_values = {
        "raw_sha256": "e" * 64,
        "majority_rgba_sha256": "d" * 64,
        "snapped_grid_digest": "c" * 64,
        "original_used_palette_ids": ("C01",),
        "original_used_color_count": 1,
        "retained_palette_ids": ("C01",),
        "weighted_subset_cost": 1,
        "final_used_palette_ids": ("C01",),
        "final_used_color_count": 1,
        "final_logical_grid_digest": "b" * 64,
    }
    for field_name, replacement in report_tamper_values.items():
        original = getattr(tampered_report, field_name)
        object.__setattr__(tampered_report, field_name, replacement)
        with pytest.raises(SemanticLevelArtError):
            tampered_report.digest()
        with pytest.raises(SemanticLevelArtError):
            artifact.canonical_dict()
        object.__setattr__(tampered_report, field_name, original)
    with pytest.raises(SemanticLevelArtError):
        replace(artifact, raw_sha256="e" * 64)
    with pytest.raises(SemanticLevelArtError):
        SemanticLevelArtArtifact(
            artifact.source_raw_artifact_digest,
            artifact.raw_sha256,
            artifact.request_digest,
            artifact.difficulty,
            artifact.target_width,
            artifact.target_height,
            artifact.logical_cells,
            artifact.used_palette_ids,
            artifact.majority_rgba_sha256,
            artifact.snapped_grid_digest,
            artifact.final_logical_grid_digest,
            artifact.report,
            artifact.source_provenance,
        )
    with pytest.raises(SemanticLevelArtError):
        object.__setattr__(artifact, "raw_sha256", "e" * 64)
        artifact.canonical_dict()


def test_public_checked_constructor_recomputes_instead_of_sealing_assertions(tmp_path: Path) -> None:
    raw = _raw(tmp_path, "compatibility.png", 20, 20, _rgb("C01") * 120 + _rgb("C02") * 120 + _rgb("C03") * 160)
    request = _request(raw)
    expected = compile_semantic_level_art(raw, request)
    result = SemanticLevelArtArtifact.from_compilation(
        raw,
        request,
        ("C01",) * 400,
        "0" * 64,
        "1" * 64,
        expected.report,
    )
    assert result.canonical_bytes() == expected.canonical_bytes()


def test_fingerprint_valid_wrong_raw_sha_reaches_artifact_source_binding(tmp_path: Path) -> None:
    raw = _raw(tmp_path, "binding.png", 20, 20, _rgb("C01") * 120 + _rgb("C02") * 120 + _rgb("C03") * 160)
    request = _request(raw)
    artifact = compile_semantic_level_art(raw, request)
    report_values = {item.name: getattr(artifact.report, item.name) for item in fields(SemanticLevelArtReport) if item.init}
    report_values["raw_sha256"] = "f" * 64
    forged_report = _build_report(**report_values)
    forged_report._assert_integrity()
    assert forged_report.raw_sha256 != artifact.raw_sha256
    with pytest.raises(SemanticLevelArtError) as error:
        _build_artifact(
            raw,
            request,
            artifact.logical_cells,
            artifact.majority_rgba_sha256,
            artifact.snapped_grid_digest,
            forged_report,
        )
    assert error.value.code == "INVALID_ARTIFACT"


def test_existing_asset_art_behavior_remains_separate(tmp_path: Path) -> None:
    pixels = _rgb("C01") * (24 * 24)
    raw = _raw(tmp_path, "asset.png", 24, 24, pixels)
    normalized = normalize_semantic_artifact(raw, SemanticNormalizationRequest(raw.digest(), "ASSET_ART", 24, 24))
    assert isinstance(normalized, SemanticNormalizedArtifact)
    assert normalized.report.resampler == "NONE_EXACT_SIZE"
