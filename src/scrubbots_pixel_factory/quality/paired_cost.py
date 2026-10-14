"""Bounded paired M07 structural-quality and measured-cost comparison.

This is an offline evaluator for explicit observations. It does not infer
semantic recognizability, playability, difficulty, or production eligibility.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import hashlib
import json
import re

from .core import QualityPolicy, evaluate_grid, logical_grid_hash


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SCORE_SCALE = 1_000_000


class PairedQualityCostError(ValueError):
    """Raised when a paired measurement is unbounded or lacks provenance."""


@dataclass(frozen=True, slots=True)
class CandidateObservation:
    candidate_id: str
    width: int
    height: int
    cells: tuple[str, ...]
    elapsed_ns: int
    source_sha256: str
    request_sha256: str

    def __init__(self, candidate_id: str, width: int, height: int, cells: Iterable[str],
                 elapsed_ns: int, source_sha256: str, request_sha256: str) -> None:
        if type(candidate_id) is not str or not _IDENTIFIER.fullmatch(candidate_id):
            raise PairedQualityCostError("candidate_id is malformed")
        if (type(width) is not int or type(height) is not int or not 2 <= width <= 59
                or not 2 <= height <= 59 or width * height > 3481):
            raise PairedQualityCostError("candidate board exceeds the bounded 2..59 dimension envelope")
        if type(elapsed_ns) is not int or not 0 <= elapsed_ns <= 60_000_000_000:
            raise PairedQualityCostError("elapsed_ns must be a measured integer in 0..60 seconds")
        if any(type(value) is not str or not _SHA256.fullmatch(value)
               for value in (source_sha256, request_sha256)):
            raise PairedQualityCostError("source and request SHA-256 provenance are required")
        if isinstance(cells, (str, bytes, bytearray)):
            raise PairedQualityCostError("cells must be an explicit bounded sequence")
        try:
            normalized = tuple(cells)
        except TypeError as exc:
            raise PairedQualityCostError("cells must be iterable") from exc
        if len(normalized) != width * height or any(type(cell) is not str for cell in normalized):
            raise PairedQualityCostError("logical grid does not match the exact dimensions")
        object.__setattr__(self, "candidate_id", candidate_id)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)
        object.__setattr__(self, "cells", normalized)
        object.__setattr__(self, "elapsed_ns", elapsed_ns)
        object.__setattr__(self, "source_sha256", source_sha256)
        object.__setattr__(self, "request_sha256", request_sha256)


def _quality_score(report: object) -> int:
    if not getattr(report, "accepted", False) or getattr(report, "analysis", None) is None:
        return 0
    metrics = report.analysis.metrics
    largest_region = round(metrics.largest_occupied_region_dominance * _SCORE_SCALE)
    symmetry = round(metrics.aggregate_symmetry_score * _SCORE_SCALE)
    low_checkerboard = _SCORE_SCALE - round(metrics.checkerboard_score * _SCORE_SCALE)
    # Fixed integer weighting: connectivity 3, symmetry 1, low checkerboard 1.
    return (3 * largest_region + symmetry + low_checkerboard) // 5


def compare_paired_observations(
    baseline: CandidateObservation,
    candidate: CandidateObservation,
    *,
    policy: QualityPolicy | None = None,
) -> dict[str, object]:
    """Compare two explicitly measured outputs with the same M07 structural policy."""
    if not isinstance(baseline, CandidateObservation) or not isinstance(candidate, CandidateObservation):
        raise PairedQualityCostError("paired comparison requires two CandidateObservation values")
    if baseline.candidate_id == candidate.candidate_id:
        raise PairedQualityCostError("paired observations require distinct candidate identities")
    if (baseline.width, baseline.height) != (candidate.width, candidate.height):
        raise PairedQualityCostError("paired observations must use identical dimensions")
    selected_policy = policy or QualityPolicy()
    left = evaluate_grid(baseline.width, baseline.height, baseline.cells, policy=selected_policy)
    right = evaluate_grid(candidate.width, candidate.height, candidate.cells, policy=selected_policy)
    left_score = _quality_score(left)
    right_score = _quality_score(right)
    left_rank = (int(left.accepted), left_score, -baseline.elapsed_ns)
    right_rank = (int(right.accepted), right_score, -candidate.elapsed_ns)
    selected = candidate.candidate_id if right_rank > left_rank else baseline.candidate_id
    payload: dict[str, object] = {
        "schema": "scrubbots-paired-structural-quality-cost",
        "version": 1,
        "policy": "M07_STRUCTURE_V1_CONNECTIVITY_3_SYMMETRY_1_LOW_CHECKERBOARD_1",
        "scope": "FIXTURE_ONLY_NON_SEMANTIC_NOT_PRODUCTION_ELIGIBILITY",
        "baseline": {
            "candidate_id": baseline.candidate_id,
            "grid_sha256": logical_grid_hash(baseline.width, baseline.height, baseline.cells),
            "source_sha256": baseline.source_sha256,
            "request_sha256": baseline.request_sha256,
            "elapsed_ns": baseline.elapsed_ns,
            "quality_accepted": left.accepted,
            "quality_score": left_score,
            "rejection_codes": list(left.rejection_codes),
        },
        "candidate": {
            "candidate_id": candidate.candidate_id,
            "grid_sha256": logical_grid_hash(candidate.width, candidate.height, candidate.cells),
            "source_sha256": candidate.source_sha256,
            "request_sha256": candidate.request_sha256,
            "elapsed_ns": candidate.elapsed_ns,
            "quality_accepted": right.accepted,
            "quality_score": right_score,
            "rejection_codes": list(right.rejection_codes),
        },
        "quality_score_delta": right_score - left_score,
        "elapsed_ns_delta": candidate.elapsed_ns - baseline.elapsed_ns,
        "selected_by_fixed_policy": selected,
    }
    payload["comparison_sha256"] = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return payload


__all__ = ["CandidateObservation", "PairedQualityCostError", "compare_paired_observations"]
