from __future__ import annotations

import pytest

from scrubbots_pixel_factory import (
    EfficiencyCounters,
    EfficiencyWorkload,
    MutationContractError,
    compare_efficiency,
)


def _workload() -> EfficiencyWorkload:
    return EfficiencyWorkload("a" * 64, "b" * 64, "c" * 64, "d" * 64)


def test_matched_efficiency_comparison_is_reproducible_and_telemetry_free() -> None:
    workload = _workload()
    mutation = EfficiencyCounters(5, 5, 2, 1, 2, 90)
    regenerate = EfficiencyCounters(5, 5, 1, 2, 2, 110)
    first = compare_efficiency(workload, workload, mutation, regenerate, mutation_cost={"trusted": True, "credits": 2}, regenerate_cost={"trusted": False, "credits": 999}, telemetry={"wall_clock_ms": 999999, "machine": "local"})
    second = compare_efficiency(workload, workload, mutation, regenerate, mutation_cost={"trusted": True, "credits": 2}, regenerate_cost={"trusted": False, "credits": 999}, telemetry={"wall_clock_ms": 1})
    assert first.digest() == second.digest()
    assert first.canonical_dict()["mutation_cost"] == {"credits": 2}
    assert first.canonical_dict()["regenerate_cost"] is None
    assert "wall_clock_ms" not in str(first.canonical_dict())


def test_mismatched_target_or_budget_is_rejected() -> None:
    left = _workload()
    right = EfficiencyWorkload("e" * 64, left.seed_config_digest, left.validation_policy_digest, left.budget_digest)
    with pytest.raises(MutationContractError):
        compare_efficiency(left, right, EfficiencyCounters(1, 1, 0, 0, 1, 1), EfficiencyCounters(1, 1, 0, 0, 1, 1))


def test_zero_acceptance_and_inconclusive_counts_remain_truthful() -> None:
    comparison = compare_efficiency(_workload(), _workload(), EfficiencyCounters(2, 2, 0, 2, 0, 10), EfficiencyCounters(2, 2, 0, 1, 1, 20))
    assert comparison.mutation.accepted == 0
    assert comparison.mutation.inconclusive == 2
    assert comparison.regenerate.rejected == 1


def test_negative_or_non_integer_counters_fail_closed() -> None:
    with pytest.raises(MutationContractError):
        EfficiencyCounters(-1, 0, 0, 0, 0, 0)
    with pytest.raises(MutationContractError):
        EfficiencyCounters(1.0, 0, 0, 0, 0, 0)  # type: ignore[arg-type]
