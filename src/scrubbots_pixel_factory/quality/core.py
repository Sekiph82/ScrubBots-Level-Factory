"""Deterministic, offline and generator-independent M07 quality analysis.

The analyzer intentionally treats a logical grid as a structural artifact, not
as a gameplay board or a semantic image.  In particular, negative space is a
documented heuristic inferred from the grid itself; generator-private topology
is never consulted.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
from types import MappingProxyType
from typing import Any

from ..contracts import CANONICAL_PALETTE, Difficulty, dimension_band, parse_difficulty, validate_used_color_count
from ..contracts.color_usage import ColorUsageContractError
from ..contracts.palette import PaletteContractError


QUALITY_SCHEMA = "scrubbots-quality"
QUALITY_VERSION = 1
GRID_HASH_SCHEMA = "scrubbots-logical-grid-hash"
GRID_HASH_VERSION = 1


class QualityCode(str, Enum):
    """Stable machine-readable M07 decision/input codes."""

    EMPTY_ARTWORK = "EMPTY_ARTWORK"
    FULL_SINGLE_SHAPE_SLAB = "FULL_SINGLE_SHAPE_SLAB"
    EXCESSIVE_SALT_AND_PEPPER = "EXCESSIVE_SALT_AND_PEPPER"
    EXCESSIVE_TINY_REGIONS = "EXCESSIVE_TINY_REGIONS"
    DOMINANCE_VIOLATION = "DOMINANCE_VIOLATION"
    CHECKERBOARD_NOISE = "CHECKERBOARD_NOISE"
    DIFFICULTY_COLOR_COUNT = "DIFFICULTY_COLOR_COUNT"
    OFF_PALETTE = "OFF_PALETTE"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    UNEQUAL_DIMENSIONS = "UNEQUAL_DIMENSIONS"


class QualityInputError(ValueError):
    """Fail-closed invalid M07 input with a stable code."""

    def __init__(self, code: QualityCode | str, message: str) -> None:
        self.code = code.value if isinstance(code, QualityCode) else str(code)
        super().__init__(message)


def _cid_key(value: str) -> int:
    return int(value[1:])


def _sorted_ids(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(values, key=_cid_key))


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class QualityPolicy:
    """Versioned conservative structural rejection thresholds.

    The defaults are intentionally conservative.  They are structural garbage
    gates, not a claim that a candidate is playable, fun, or semantically good.
    """

    version: str = "m07-quality-policy-v1"
    difficulty: Difficulty | str | None = None
    tiny_region_max_size: int = 3
    max_isolated_ratio: float = 0.20
    max_tiny_cell_ratio: float = 0.35
    max_largest_region_ratio: float = 1.0
    max_color_dominance_ratio: float = 1.0
    full_slab_min_occupied_ratio: float = 0.80
    max_checkerboard_score: float = 0.98
    reject_full_single_shape_slab: bool = True

    def __post_init__(self) -> None:
        if type(self.version) is not str or not self.version:
            raise ValueError("quality policy version must be a non-empty string")
        if self.difficulty is not None:
            object.__setattr__(self, "difficulty", parse_difficulty(self.difficulty))
        if type(self.tiny_region_max_size) is not int or self.tiny_region_max_size < 1:
            raise ValueError("tiny_region_max_size must be a positive integer")
        for name in (
            "max_isolated_ratio",
            "max_tiny_cell_ratio",
            "max_largest_region_ratio",
            "max_color_dominance_ratio",
            "full_slab_min_occupied_ratio",
            "max_checkerboard_score",
        ):
            value = getattr(self, name)
            if type(value) not in (int, float) or not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if type(self.reject_full_single_shape_slab) is not bool:
            raise ValueError("reject_full_single_shape_slab must be boolean")

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "difficulty": self.difficulty.value if isinstance(self.difficulty, Difficulty) else None,
            "tiny_region_max_size": self.tiny_region_max_size,
            "max_isolated_ratio": round(float(self.max_isolated_ratio), 8),
            "max_tiny_cell_ratio": round(float(self.max_tiny_cell_ratio), 8),
            "max_largest_region_ratio": round(float(self.max_largest_region_ratio), 8),
            "max_color_dominance_ratio": round(float(self.max_color_dominance_ratio), 8),
            "full_slab_min_occupied_ratio": round(float(self.full_slab_min_occupied_ratio), 8),
            "max_checkerboard_score": round(float(self.max_checkerboard_score), 8),
            "reject_full_single_shape_slab": self.reject_full_single_shape_slab,
        }


@dataclass(frozen=True, slots=True)
class NegativeSpaceEvidence:
    """Evidence for the deterministic boundary-majority inference heuristic."""

    inferred_color: str
    boundary_counts: Mapping[str, int]
    whole_grid_counts: Mapping[str, int]
    boundary_cell_count: int
    inferred_count: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "boundary_counts", _freeze_mapping(self.boundary_counts))
        object.__setattr__(self, "whole_grid_counts", _freeze_mapping(self.whole_grid_counts))

    def as_dict(self) -> dict[str, object]:
        return {
            "rule": "boundary-majority; whole-grid-count; ascending-C-ID tie-break",
            "inferred_color": self.inferred_color,
            "boundary_counts": {key: self.boundary_counts[key] for key in _sorted_ids(self.boundary_counts)},
            "whole_grid_counts": {key: self.whole_grid_counts[key] for key in _sorted_ids(self.whole_grid_counts)},
            "boundary_cell_count": self.boundary_cell_count,
            "inferred_count": self.inferred_count,
        }


@dataclass(frozen=True, slots=True)
class ColorComponent:
    color_id: str
    size: int
    cells: tuple[tuple[int, int], ...]

    def as_dict(self) -> dict[str, object]:
        return {"color": self.color_id, "size": self.size, "cells": [list(cell) for cell in self.cells]}


@dataclass(frozen=True, slots=True)
class QualityMetrics:
    occupied_count: int
    occupied_ratio: float
    occupied_component_count: int
    occupied_component_sizes: tuple[int, ...]
    color_components: tuple[ColorComponent, ...]
    occupied_color_counts: Mapping[str, int]
    isolated_occupied_count: int
    tiny_region_count: int
    tiny_region_cell_count: int
    largest_occupied_region_dominance: float
    largest_color_dominance: float
    occupied_edge_touch_count: int
    occupied_edge_touch_ratio: float
    horizontal_symmetry_score: float
    vertical_symmetry_score: float
    aggregate_symmetry_score: float
    color_entropy: float
    color_entropy_scaled: int
    adjacency_edge_count: int
    color_adjacency: Mapping[str, int]
    occupied_bounding_box: tuple[int, int, int, int] | None
    occupied_center_of_mass: tuple[float, float] | None
    occupied_center_of_mass_scaled: tuple[int, int] | None
    negative_space_count: int
    negative_space_ratio: float
    checkerboard_score: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "color_components", tuple(self.color_components))
        object.__setattr__(self, "occupied_component_sizes", tuple(self.occupied_component_sizes))
        object.__setattr__(self, "occupied_color_counts", _freeze_mapping(self.occupied_color_counts))
        object.__setattr__(self, "color_adjacency", _freeze_mapping(self.color_adjacency))

    def as_dict(self) -> dict[str, object]:
        return {
            "occupied_count": self.occupied_count,
            "occupied_ratio": round(self.occupied_ratio, 8),
            "occupied_component_count": self.occupied_component_count,
            "occupied_component_sizes": list(self.occupied_component_sizes),
            "color_components": [component.as_dict() for component in self.color_components],
            "occupied_color_counts": {
                key: self.occupied_color_counts[key] for key in _sorted_ids(self.occupied_color_counts)
            },
            "isolated_occupied_count": self.isolated_occupied_count,
            "tiny_region_count": self.tiny_region_count,
            "tiny_region_cell_count": self.tiny_region_cell_count,
            "largest_occupied_region_dominance": round(self.largest_occupied_region_dominance, 8),
            "largest_color_dominance": round(self.largest_color_dominance, 8),
            "occupied_edge_touch_count": self.occupied_edge_touch_count,
            "occupied_edge_touch_ratio": round(self.occupied_edge_touch_ratio, 8),
            "horizontal_symmetry_score": round(self.horizontal_symmetry_score, 8),
            "vertical_symmetry_score": round(self.vertical_symmetry_score, 8),
            "aggregate_symmetry_score": round(self.aggregate_symmetry_score, 8),
            "color_entropy": round(self.color_entropy, 8),
            "color_entropy_scaled": self.color_entropy_scaled,
            "adjacency_edge_count": self.adjacency_edge_count,
            "color_adjacency": {key: self.color_adjacency[key] for key in sorted(self.color_adjacency)},
            "occupied_bounding_box": list(self.occupied_bounding_box) if self.occupied_bounding_box else None,
            "occupied_center_of_mass": list(self.occupied_center_of_mass) if self.occupied_center_of_mass else None,
            "occupied_center_of_mass_scaled": list(self.occupied_center_of_mass_scaled)
            if self.occupied_center_of_mass_scaled
            else None,
            "negative_space_count": self.negative_space_count,
            "negative_space_ratio": round(self.negative_space_ratio, 8),
            "checkerboard_score": round(self.checkerboard_score, 8),
        }


@dataclass(frozen=True, slots=True)
class QualityAnalysis:
    width: int
    height: int
    cells: tuple[str, ...]
    used_colors: tuple[str, ...]
    negative_space: NegativeSpaceEvidence
    metrics: QualityMetrics

    def as_dict(self) -> dict[str, object]:
        return {
            "width": self.width,
            "height": self.height,
            "used_colors": list(self.used_colors),
            "negative_space": self.negative_space.as_dict(),
            "metrics": self.metrics.as_dict(),
        }


@dataclass(frozen=True, slots=True)
class QualityReport:
    analysis: QualityAnalysis | None
    policy: QualityPolicy
    accepted: bool
    rejection_codes: tuple[str, ...]
    input_error: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "rejection_codes", tuple(self.rejection_codes))

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": QUALITY_SCHEMA,
            "version": QUALITY_VERSION,
            "accepted": self.accepted,
            "rejection_codes": list(self.rejection_codes),
            "input_error": self.input_error,
            "policy": self.policy.as_dict(),
            "analysis": self.analysis.as_dict() if self.analysis else None,
        }

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.as_dict(), ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )


def _validate_grid(width: int, height: int, cells: Iterable[str]) -> tuple[str, ...]:
    if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
        raise QualityInputError(QualityCode.DIMENSION_MISMATCH, "width and height must be positive integers")
    if isinstance(cells, (str, bytes, bytearray)):
        raise QualityInputError(QualityCode.DIMENSION_MISMATCH, "logical cells must be an iterable of C-ID values")
    try:
        normalized = tuple(cells)
    except TypeError as exc:
        raise QualityInputError(QualityCode.DIMENSION_MISMATCH, "logical cells must be iterable") from exc
    if len(normalized) != width * height:
        raise QualityInputError(
            QualityCode.DIMENSION_MISMATCH,
            f"logical cell count {len(normalized)} does not equal width*height {width * height}",
        )
    for index, value in enumerate(normalized):
        try:
            CANONICAL_PALETTE.validate_logical_id(value)
        except (PaletteContractError, TypeError) as exc:
            raise QualityInputError(QualityCode.OFF_PALETTE, f"cell {index} is not a canonical C01..C16 ID: {value!r}") from exc
    return normalized


def _boundary_indices(width: int, height: int) -> tuple[int, ...]:
    return tuple(
        index
        for index in range(width * height)
        if index // width in (0, height - 1) or index % width in (0, width - 1)
    )


def _infer_negative_space(width: int, height: int, cells: tuple[str, ...]) -> NegativeSpaceEvidence:
    whole: dict[str, int] = {color: 0 for color in _sorted_ids(set(cells))}
    for cell in cells:
        whole[cell] += 1
    boundary: dict[str, int] = {color: 0 for color in whole}
    boundary_indices = _boundary_indices(width, height)
    for index in boundary_indices:
        boundary[cells[index]] += 1
    chosen = min(
        whole,
        key=lambda color: (-boundary[color], -whole[color], _cid_key(color)),
    )
    return NegativeSpaceEvidence(chosen, boundary, whole, len(boundary_indices), whole[chosen])


def _neighbors(index: int, width: int, height: int) -> tuple[int, ...]:
    x = index % width
    y = index // width
    points: list[tuple[int, int]] = []
    for nx, ny in ((x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)):
        if 0 <= nx < width and 0 <= ny < height:
            points.append((nx, ny))
    points.sort(key=lambda point: point[1] * width + point[0])
    return tuple(y_value * width + x_value for x_value, y_value in points)


def _components(mask: Sequence[bool], width: int, height: int) -> tuple[tuple[int, ...], ...]:
    seen: set[int] = set()
    components: list[tuple[int, ...]] = []
    for root in range(width * height):
        if not mask[root] or root in seen:
            continue
        queue = [root]
        seen.add(root)
        members: list[int] = []
        while queue:
            current = queue.pop(0)
            members.append(current)
            for neighbor in _neighbors(current, width, height):
                if mask[neighbor] and neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        components.append(tuple(sorted(members)))
    return tuple(components)


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 8) if denominator else 0.0


def _symmetry(cells: tuple[str, ...], width: int, height: int, horizontal: bool) -> float:
    matches = 0
    total = width * height
    for y in range(height):
        for x in range(width):
            other_x = width - 1 - x if horizontal else x
            other_y = y if horizontal else height - 1 - y
            if cells[y * width + x] == cells[other_y * width + other_x]:
                matches += 1
    return _ratio(matches, total)


def _checkerboard_score(cells: tuple[str, ...], width: int, height: int) -> float:
    used = _sorted_ids(set(cells))
    if len(used) != 2:
        return 0.0
    matches_a = 0
    matches_b = 0
    for y in range(height):
        for x in range(width):
            expected_a = used[(x + y) % 2]
            expected_b = used[1 - ((x + y) % 2)]
            actual = cells[y * width + x]
            matches_a += actual == expected_a
            matches_b += actual == expected_b
    return _ratio(max(matches_a, matches_b), width * height)


def analyze_grid(
    width: int,
    height: int,
    cells: Iterable[str],
    *,
    tiny_region_max_size: int = 3,
) -> QualityAnalysis:
    """Compute all M07 structural metrics from only dimensions and logical cells."""

    normalized = _validate_grid(width, height, cells)
    if type(tiny_region_max_size) is not int or tiny_region_max_size < 1:
        raise ValueError("tiny_region_max_size must be a positive integer")
    negative_space = _infer_negative_space(width, height, normalized)
    occupied_mask = tuple(cell != negative_space.inferred_color for cell in normalized)
    occupied_indices = tuple(index for index, value in enumerate(occupied_mask) if value)
    occupied_count = len(occupied_indices)
    occupied_components = _components(occupied_mask, width, height)
    occupied_sizes = tuple(len(component) for component in occupied_components)

    color_components: list[ColorComponent] = []
    for color in _sorted_ids(set(normalized)):
        color_mask = tuple(occupied_mask[index] and normalized[index] == color for index in range(width * height))
        for component in _components(color_mask, width, height):
            color_components.append(
                ColorComponent(color, len(component), tuple((index % width, index // width) for index in component))
            )
    color_components.sort(key=lambda component: (_cid_key(component.color_id), component.cells[0] if component.cells else (0, 0)))

    isolated_count = sum(1 for component in occupied_components if len(component) == 1)
    tiny_components = tuple(component for component in occupied_components if len(component) <= tiny_region_max_size)
    largest_region = max(occupied_sizes, default=0)
    occupied_color_counts = {
        color: sum(1 for index in occupied_indices if normalized[index] == color)
        for color in _sorted_ids(set(normalized) - {negative_space.inferred_color})
    }
    largest_color = max(occupied_color_counts.values(), default=0)
    edge_indices = set(_boundary_indices(width, height))
    edge_touch_count = sum(index in edge_indices for index in occupied_indices)

    if occupied_indices:
        xs = tuple(index % width for index in occupied_indices)
        ys = tuple(index // width for index in occupied_indices)
        bbox = (min(xs), min(ys), max(xs), max(ys))
        x_sum = sum(xs)
        y_sum = sum(ys)
        center = (round(x_sum / occupied_count, 8), round(y_sum / occupied_count, 8))
        center_scaled = (x_sum * 1_000_000 // occupied_count, y_sum * 1_000_000 // occupied_count)
    else:
        bbox = None
        center = None
        center_scaled = None

    counts = tuple(negative_space.whole_grid_counts[color] for color in _sorted_ids(negative_space.whole_grid_counts))
    entropy = 0.0
    for count in counts:
        probability = count / len(normalized)
        entropy -= probability * math.log2(probability)
    entropy = round(entropy, 8)

    adjacency: dict[str, int] = {}
    adjacency_edges = 0
    for y in range(height):
        for x in range(width):
            index = y * width + x
            for nx, ny in ((x + 1, y), (x, y + 1)):
                if nx >= width or ny >= height:
                    continue
                other = ny * width + nx
                left, right = sorted((normalized[index], normalized[other]), key=_cid_key)
                key = f"{left}|{right}"
                adjacency[key] = adjacency.get(key, 0) + 1
                adjacency_edges += 1

    metrics = QualityMetrics(
        occupied_count=occupied_count,
        occupied_ratio=_ratio(occupied_count, len(normalized)),
        occupied_component_count=len(occupied_components),
        occupied_component_sizes=occupied_sizes,
        color_components=tuple(color_components),
        occupied_color_counts=occupied_color_counts,
        isolated_occupied_count=isolated_count,
        tiny_region_count=len(tiny_components),
        tiny_region_cell_count=sum(len(component) for component in tiny_components),
        largest_occupied_region_dominance=_ratio(largest_region, occupied_count),
        largest_color_dominance=_ratio(largest_color, occupied_count),
        occupied_edge_touch_count=edge_touch_count,
        occupied_edge_touch_ratio=_ratio(edge_touch_count, occupied_count),
        horizontal_symmetry_score=_symmetry(normalized, width, height, True),
        vertical_symmetry_score=_symmetry(normalized, width, height, False),
        aggregate_symmetry_score=round(
            (_symmetry(normalized, width, height, True) + _symmetry(normalized, width, height, False)) / 2,
            8,
        ),
        color_entropy=entropy,
        color_entropy_scaled=round(entropy * 1_000_000),
        adjacency_edge_count=adjacency_edges,
        color_adjacency=adjacency,
        occupied_bounding_box=bbox,
        occupied_center_of_mass=center,
        occupied_center_of_mass_scaled=center_scaled,
        negative_space_count=negative_space.inferred_count,
        negative_space_ratio=_ratio(negative_space.inferred_count, len(normalized)),
        checkerboard_score=_checkerboard_score(normalized, width, height),
    )
    return QualityAnalysis(width, height, normalized, _sorted_ids(set(normalized)), negative_space, metrics)


def _quality_codes(analysis: QualityAnalysis, policy: QualityPolicy) -> tuple[str, ...]:
    metrics = analysis.metrics
    codes: list[str] = []
    if metrics.occupied_count == 0:
        codes.append(QualityCode.EMPTY_ARTWORK.value)
    occupied_colors = _sorted_ids(
        color for color in analysis.used_colors if color != analysis.negative_space.inferred_color and any(
            cell == color for cell in analysis.cells
        )
    )
    if (
        policy.reject_full_single_shape_slab
        and metrics.occupied_ratio >= policy.full_slab_min_occupied_ratio
        and len(occupied_colors) <= 1
        and metrics.occupied_count > 0
    ):
        codes.append(QualityCode.FULL_SINGLE_SHAPE_SLAB.value)
    if metrics.occupied_count and metrics.isolated_occupied_count / metrics.occupied_count > policy.max_isolated_ratio:
        codes.append(QualityCode.EXCESSIVE_SALT_AND_PEPPER.value)
    if (
        metrics.occupied_count
        and metrics.tiny_region_cell_count / metrics.occupied_count > policy.max_tiny_cell_ratio
        and metrics.tiny_region_count >= 2
    ):
        codes.append(QualityCode.EXCESSIVE_TINY_REGIONS.value)
    if (
        metrics.occupied_count
        and (
            metrics.largest_occupied_region_dominance > policy.max_largest_region_ratio
            or metrics.largest_color_dominance > policy.max_color_dominance_ratio
        )
    ):
        codes.append(QualityCode.DOMINANCE_VIOLATION.value)
    if len(analysis.used_colors) == 2 and metrics.checkerboard_score >= policy.max_checkerboard_score:
        codes.append(QualityCode.CHECKERBOARD_NOISE.value)
    if policy.difficulty is not None:
        band = dimension_band(policy.difficulty)
        try:
            validate_used_color_count(policy.difficulty, analysis.cells)
        except ColorUsageContractError:
            codes.append(QualityCode.DIFFICULTY_COLOR_COUNT.value)
        if not band.contains(analysis.width) or not band.contains(analysis.height):
            codes.append(QualityCode.DIMENSION_MISMATCH.value)
    code_order = {code.value: index for index, code in enumerate(QualityCode)}
    return tuple(sorted(codes, key=lambda code: code_order[code]))


def evaluate_grid(
    width: int,
    height: int,
    cells: Iterable[str],
    *,
    policy: QualityPolicy | None = None,
) -> QualityReport:
    """Return a separate quality decision without mutating the input grid."""

    selected_policy = policy or QualityPolicy()
    try:
        analysis = analyze_grid(
            width,
            height,
            cells,
            tiny_region_max_size=selected_policy.tiny_region_max_size,
        )
    except QualityInputError as exc:
        return QualityReport(None, selected_policy, False, (exc.code,), str(exc))
    codes = _quality_codes(analysis, selected_policy)
    return QualityReport(analysis, selected_policy, not codes, codes)


def canonical_grid_bytes(width: int, height: int, cells: Iterable[str]) -> bytes:
    """Canonical framed serialization used by the versioned logical-grid hash."""

    normalized = _validate_grid(width, height, cells)
    payload = {
        "schema": GRID_HASH_SCHEMA,
        "version": GRID_HASH_VERSION,
        "width": width,
        "height": height,
        "cells": list(normalized),
    }
    return json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def logical_grid_hash(width: int, height: int, cells: Iterable[str]) -> str:
    return hashlib.sha256(canonical_grid_bytes(width, height, cells)).hexdigest()


@dataclass(frozen=True, slots=True)
class GridInput:
    width: int
    height: int
    cells: tuple[str, ...]

    def __init__(self, width: int, height: int, cells: Iterable[str]) -> None:
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)
        object.__setattr__(self, "cells", tuple(cells))


@dataclass(frozen=True, slots=True)
class SimilarityMetrics:
    comparable: bool
    occupancy_mask_similarity: float | None
    color_layout_similarity: float | None

    def as_dict(self) -> dict[str, object]:
        return {
            "comparable": self.comparable,
            "occupancy_mask_similarity": self.occupancy_mask_similarity,
            "color_layout_similarity": self.color_layout_similarity,
        }


def _occupied_set(analysis: QualityAnalysis) -> set[int]:
    return {index for index, cell in enumerate(analysis.cells) if cell != analysis.negative_space.inferred_color}


def compare_grids(first: GridInput, second: GridInput) -> SimilarityMetrics:
    """Compare equal-sized grids without resizing or interpolation."""

    first_analysis = analyze_grid(first.width, first.height, first.cells)
    second_analysis = analyze_grid(second.width, second.height, second.cells)
    if (first.width, first.height) != (second.width, second.height):
        return SimilarityMetrics(False, None, None)
    left = _occupied_set(first_analysis)
    right = _occupied_set(second_analysis)
    union = left | right
    if not union:
        occupancy = 1.0
    else:
        occupancy = round(len(left & right) / len(union), 8)
    exact = sum(a == b for a, b in zip(first.cells, second.cells))
    return SimilarityMetrics(True, occupancy, round(exact / len(first.cells), 8))


@dataclass(frozen=True, slots=True)
class DuplicatePair:
    first_index: int
    second_index: int
    similarity: SimilarityMetrics


@dataclass(frozen=True, slots=True)
class DiversityReport:
    exact_duplicate_groups: tuple[tuple[int, ...], ...]
    near_duplicate_pairs: tuple[DuplicatePair, ...]
    threshold: float

    def as_dict(self) -> dict[str, object]:
        return {
            "exact_duplicate_groups": [list(group) for group in self.exact_duplicate_groups],
            "near_duplicate_pairs": [
                {
                    "first_index": pair.first_index,
                    "second_index": pair.second_index,
                    "similarity": pair.similarity.as_dict(),
                }
                for pair in self.near_duplicate_pairs
            ],
            "threshold": self.threshold,
        }


def exact_duplicate_groups(grids: Sequence[GridInput]) -> tuple[tuple[int, ...], ...]:
    records = [(logical_grid_hash(grid.width, grid.height, grid.cells), index, grid) for index, grid in enumerate(grids)]
    records.sort(key=lambda record: (record[0], record[1]))
    groups: list[tuple[int, ...]] = []
    current_digest: str | None = None
    current: list[int] = []
    reference: GridInput | None = None
    for digest, index, grid in records:
        if digest != current_digest:
            if len(current) > 1:
                groups.append(tuple(sorted(current)))
            current_digest = digest
            current = [index]
            reference = grid
        elif reference is not None and (reference.width, reference.height, reference.cells) == (grid.width, grid.height, grid.cells):
            current.append(index)
        else:
            groups.append((current[0],))
            current_digest = f"{digest}:{index}"
            current = [index]
            reference = grid
    if len(current) > 1:
        groups.append(tuple(sorted(current)))
    return tuple(sorted(groups))


def diversity_report(grids: Sequence[GridInput], *, near_duplicate_threshold: float = 0.95) -> DiversityReport:
    if type(near_duplicate_threshold) not in (int, float) or not 0.0 <= float(near_duplicate_threshold) <= 1.0:
        raise ValueError("near_duplicate_threshold must be between 0 and 1")
    exact = exact_duplicate_groups(grids)
    near: list[DuplicatePair] = []
    for first_index in range(len(grids)):
        for second_index in range(first_index + 1, len(grids)):
            similarity = compare_grids(grids[first_index], grids[second_index])
            if similarity.comparable and similarity.occupancy_mask_similarity is not None and similarity.color_layout_similarity is not None:
                score = min(similarity.occupancy_mask_similarity, similarity.color_layout_similarity)
                if score >= float(near_duplicate_threshold):
                    near.append(DuplicatePair(first_index, second_index, similarity))
    return DiversityReport(exact, tuple(near), round(float(near_duplicate_threshold), 8))


__all__ = [
    "DiversityReport",
    "DuplicatePair",
    "GridInput",
    "GRID_HASH_SCHEMA",
    "GRID_HASH_VERSION",
    "NegativeSpaceEvidence",
    "QualityAnalysis",
    "QualityCode",
    "QualityInputError",
    "QualityMetrics",
    "QualityPolicy",
    "QualityReport",
    "SimilarityMetrics",
    "analyze_grid",
    "canonical_grid_bytes",
    "compare_grids",
    "diversity_report",
    "evaluate_grid",
    "exact_duplicate_groups",
    "logical_grid_hash",
]
