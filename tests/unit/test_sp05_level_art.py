from __future__ import annotations

from dataclasses import replace
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
)


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


@pytest.mark.parametrize(
    ("difficulty", "expected_max"),
    [(Difficulty.EASY, 5), (Difficulty.MEDIUM, 7), (Difficulty.HARD, 9), (Difficulty.VERY_HARD, 12)],
)
def test_above_maximum_budget_reduces_to_exact_difficulty_maximum(difficulty: Difficulty, expected_max: int) -> None:
    cells = _cells_with_counts(tuple(f"C{index:02d}" for index in range(1, 17)))
    final, details = enforce_difficulty_color_budget(difficulty, cells)
    assert len(actual_used_palette_ids(final)) == expected_max
    assert details["final_used_color_count"] == expected_max


def test_budget_preserves_in_band_and_rejects_below_minimum_without_fabrication() -> None:
    cells = _cells_with_counts(("C01", "C02", "C03"), (4, 3, 2))
    final, details = enforce_difficulty_color_budget(Difficulty.EASY, cells)
    assert final == cells and details["weighted_subset_cost"] == 0
    with pytest.raises(SemanticLevelArtError) as error:
        enforce_difficulty_color_budget(Difficulty.EASY, ("C01",) * 10)
    assert error.value.code == "INSUFFICIENT_USED_COLORS"


def test_weighted_subset_optimization_retains_the_hand_computed_low_cost_subset() -> None:
    ids = ("C01", "C02", "C03", "C04", "C05", "C06")
    cells = _cells_with_counts(ids, (20, 20, 1, 20, 20, 20))
    final, details = enforce_difficulty_color_budget(Difficulty.EASY, cells)
    assert details["retained_palette_ids"] == ("C01", "C02", "C04", "C05", "C06")
    assert len(actual_used_palette_ids(final)) == 5


def test_weighted_subset_ties_resolve_by_canonical_palette_tuple() -> None:
    ids = ("C01", "C02", "C03", "C04", "C05", "C06")
    final, details = enforce_difficulty_color_budget(Difficulty.EASY, ids)
    assert details["retained_palette_ids"] == ("C01", "C02", "C04", "C05", "C06")
    assert "C03" not in actual_used_palette_ids(final)


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


def test_existing_asset_art_behavior_remains_separate(tmp_path: Path) -> None:
    pixels = _rgb("C01") * (24 * 24)
    raw = _raw(tmp_path, "asset.png", 24, 24, pixels)
    normalized = normalize_semantic_artifact(raw, SemanticNormalizationRequest(raw.digest(), "ASSET_ART", 24, 24))
    assert isinstance(normalized, SemanticNormalizedArtifact)
    assert normalized.report.resampler == "NONE_EXACT_SIZE"
