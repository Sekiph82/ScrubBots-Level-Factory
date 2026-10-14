from __future__ import annotations

import pytest

from scrubbots_pixel_factory.quality.paired_cost import (
    CandidateObservation,
    PairedQualityCostError,
    compare_paired_observations,
)


def _observation(candidate_id: str, cells: tuple[str, ...], elapsed_ns: int) -> CandidateObservation:
    return CandidateObservation(candidate_id, 20, 20, cells, elapsed_ns, "a" * 64, "b" * 64)


def test_paired_comparison_binds_real_grid_hashes_quality_and_measured_cost() -> None:
    baseline = _observation("baseline-01", tuple(["C01"] * 400), 900_000)
    art = ["C01"] * 400
    for y in range(6, 14):
        for x in range(6, 14):
            art[y * 20 + x] = "C02"
    candidate = _observation("candidate-01", tuple(art), 1_100_000)

    report = compare_paired_observations(baseline, candidate)
    assert report["scope"] == "FIXTURE_ONLY_NON_SEMANTIC_NOT_PRODUCTION_ELIGIBILITY"
    assert report["baseline"]["grid_sha256"] != report["candidate"]["grid_sha256"]
    assert report["quality_score_delta"] > 0
    assert report["elapsed_ns_delta"] == 200_000
    assert report["selected_by_fixed_policy"] == "candidate-01"
    assert len(report["comparison_sha256"]) == 64


def test_paired_comparison_rejects_unbound_or_incomparable_observations() -> None:
    base = _observation("baseline-01", tuple(["C01"] * 400), 1)
    with pytest.raises(PairedQualityCostError, match="dimensions"):
        compare_paired_observations(base, CandidateObservation(
            "candidate-01", 20, 19, tuple(["C01"] * 380), 2, "a" * 64, "b" * 64))
    with pytest.raises(PairedQualityCostError, match="provenance"):
        CandidateObservation("candidate-02", 20, 20, tuple(["C01"] * 400), 2, "bad", "b" * 64)
