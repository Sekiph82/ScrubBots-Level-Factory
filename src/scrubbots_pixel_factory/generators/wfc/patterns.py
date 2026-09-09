"""Deterministic overlapping-pattern extraction and adjacency construction."""

import hashlib
import json

from .model import DIRECTIONS, Exemplar, Pattern, PatternTable, WFCConfig, WFCContractError
from .exemplar import map_exemplar_pixels


def _rotate(cells: tuple[str, ...], size: int) -> tuple[str, ...]:
    return tuple(cells[(size - 1 - row) + column * size] for row in range(size) for column in range(size))


def _reflect(cells: tuple[str, ...], size: int) -> tuple[str, ...]:
    return tuple(cells[row * size + (size - 1 - column)] for row in range(size) for column in range(size))


def transformed_patterns(base: tuple[str, ...], size: int, config: WFCConfig) -> tuple[tuple[str, ...], ...]:
    variants: list[tuple[str, ...]] = [base]
    if config.allow_rotations:
        current = base
        for _ in range(3):
            current = _rotate(current, size)
            variants.append(current)
    if config.allow_reflections:
        reflected = _reflect(base, size)
        variants.append(reflected)
        if config.allow_rotations:
            current = reflected
            for _ in range(3):
                current = _rotate(current, size)
                variants.append(current)
    unique: list[tuple[str, ...]] = []
    for variant in variants:
        if variant not in unique:
            unique.append(variant)
    return tuple(unique)


def _cell(mapped: tuple[str, ...], width: int, height: int, x: int, y: int, periodic: bool) -> str:
    if periodic:
        x %= width
        y %= height
    return mapped[y * width + x]


def extract_pattern_table(exemplar: Exemplar, config: WFCConfig, target_palette: tuple[str, ...]) -> PatternTable:
    size = config.pattern_size
    if exemplar.width < size or exemplar.height < size:
        raise WFCContractError("exemplar is smaller than the requested WFC pattern size")
    mapped, mapping = map_exemplar_pixels(exemplar, target_palette, config)
    max_x = exemplar.width if config.input_periodic else exemplar.width - size + 1
    max_y = exemplar.height if config.input_periodic else exemplar.height - size + 1
    frequency: dict[tuple[str, ...], int] = {}
    raw_extracted_window_count = 0
    transformed_observation_count = 0
    for y in range(max_y):
        for x in range(max_x):
            raw_extracted_window_count += 1
            base = tuple(
                _cell(mapped, exemplar.width, exemplar.height, x + column, y + row, config.input_periodic)
                for row in range(size)
                for column in range(size)
            )
            variants = transformed_patterns(base, size, config)
            transformed_observation_count += len(variants)
            for variant in variants:
                frequency[variant] = frequency.get(variant, 0) + 1
    ordered_cells = tuple(sorted(frequency, key=lambda cells: tuple(int(value[1:]) for value in cells)))
    patterns = tuple(Pattern(index, cells, frequency[cells]) for index, cells in enumerate(ordered_cells))
    ids_by_cells = {pattern.cells: pattern.pattern_id for pattern in patterns}

    def compatible(left: tuple[str, ...], right: tuple[str, ...], direction: str) -> bool:
        if direction == "RIGHT":
            return all(left[row * size + column + 1] == right[row * size + column] for row in range(size) for column in range(size - 1))
        if direction == "LEFT":
            return compatible(right, left, "RIGHT")
        if direction == "DOWN":
            return all(left[(row + 1) * size + column] == right[row * size + column] for row in range(size - 1) for column in range(size))
        if direction == "UP":
            return compatible(right, left, "DOWN")
        raise WFCContractError("unknown WFC adjacency direction")

    adjacency: dict[str, tuple[tuple[int, ...], ...]] = {}
    for direction in DIRECTIONS:
        adjacency[direction] = tuple(
            tuple(
                ids_by_cells[other.cells]
                for other in patterns
                if compatible(pattern.cells, other.cells, direction)
            )
            for pattern in patterns
        )
    canonical = {
        "N": size,
        "patterns": [{"id": p.pattern_id, "cells": p.cells, "frequency": p.frequency} for p in patterns],
        "adjacency": {direction: adjacency[direction] for direction in DIRECTIONS},
        "source_palette": exemplar.source_palette,
        "target_palette": target_palette,
        "mapping": mapping,
        "raw_extracted_window_count": raw_extracted_window_count,
        "transformed_observation_count": transformed_observation_count,
    }
    digest = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return PatternTable(size, patterns, adjacency, exemplar.source_palette, target_palette, digest, raw_extracted_window_count, transformed_observation_count)
