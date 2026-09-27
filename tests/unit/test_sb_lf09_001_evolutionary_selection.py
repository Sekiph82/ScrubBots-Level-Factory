from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

import pytest

from scrubbots_pixel_factory import (
    CandidateEvidence,
    EvolutionarySelectionError,
    EvolutionarySelectionPolicy,
    EXPERIMENTAL_OPT_IN,
    M08ContractError,
    SelectionDisposition,
    run_experimental_evolutionary_selection,
)
from scrubbots_pixel_factory.difficulty_analysis import LaneClass
from scrubbots_pixel_factory.m08_batch import lineage_digest_for


def _evidence(candidate: str, *, bundle_key: str | None = None) -> CandidateEvidence:
    bundle_key = bundle_key or candidate
    raw = {
        "m03_digest": f"m03:{candidate}".encode(),
        "m04_digest": f"m04:{candidate}".encode(),
        "m04_lane_digest": f"lane:{candidate}".encode(),
        "m05_digest": f"m05:{candidate}".encode(),
        "level_data_digest": f"level:{candidate}".encode(),
        "logical_art_digest": f"art:{candidate}".encode(),
        "grid_hash": f"grid:{candidate}".encode(),
        "source_provenance_digest": f"source:{candidate}".encode(),
        "generation_request_digest": f"request:{candidate}".encode(),
        "generation_result_digest": f"result:{candidate}".encode(),
        "generation_metadata_digest": f"generation:{candidate}".encode(),
        "bundle_digest": f"bundle:{bundle_key}".encode(),
    }
    values = {
        **{key: hashlib.sha256(value).hexdigest() for key, value in raw.items()},
        "level_data_ref": f"level-data/{candidate}.json",
        "logical_art_ref": f"art/{candidate}.png",
        "bundle_ref": f"bundles/{candidate}",
        "source_provenance_ref": f"provenance/{candidate}.json",
        "m03_ref": f"evidence/m03-{candidate}.json",
        "m04_ref": f"evidence/m04-{candidate}.json",
        "m05_ref": f"evidence/m05-{candidate}.json",
        "generation_request_ref": f"generation/request-{candidate}.json",
        "generation_result_ref": f"generation/result-{candidate}.json",
        "generation_metadata_ref": f"generation/metadata-{candidate}.json",
        "preview_digest": None,
        "preview_ref": None,
        "mutation_digest": None,
        "mutation_ref": None,
    }
    values["lineage_digest"] = lineage_digest_for(
        {"candidate_id": candidate, "lane": LaneClass.EASY.value, "m03_disposition": "ACCEPT", "m04_disposition": "ACCEPT", "m05_disposition": "ACCEPT", **values}
    )
    return CandidateEvidence(candidate_id=candidate, lane=LaneClass.EASY, m03_disposition="ACCEPT", m04_disposition="ACCEPT", m05_disposition="ACCEPT", **values)


def _population(count: int = 5) -> tuple[CandidateEvidence, ...]:
    return tuple(_evidence(f"candidate-{index}") for index in range(count))


def test_positive_selection_is_opt_in_bounded_and_lineage_preserving() -> None:
    population = _population()
    policy = EvolutionarySelectionPolicy(population_size=3, generations=2, evaluation_budget=10, elite_count=2, seed=17)

    result = run_experimental_evolutionary_selection(population, policy, opt_in=EXPERIMENTAL_OPT_IN)

    assert result.disposition is SelectionDisposition.SELECTED
    assert len(result.selected) == 2
    assert result.generations_completed == 2
    assert result.evaluations == 10
    assert result.provenance is not None
    assert result.provenance.selected_lineage_digests == tuple(item.lineage_digest for item in result.selected)
    assert all(item in population for item in result.selected)
    assert result.canonical_dict()["provenance"]["opt_in"] == EXPERIMENTAL_OPT_IN


def test_same_inputs_policy_and_seed_replay_byte_identically() -> None:
    population = _population()
    policy = EvolutionarySelectionPolicy(population_size=3, generations=2, evaluation_budget=10, seed=42)

    first = run_experimental_evolutionary_selection(population, policy, opt_in=EXPERIMENTAL_OPT_IN)
    second = run_experimental_evolutionary_selection(tuple(reversed(population)), policy, opt_in=EXPERIMENTAL_OPT_IN)
    changed = run_experimental_evolutionary_selection(
        population,
        replace(policy, seed=43),
        opt_in=EXPERIMENTAL_OPT_IN,
    )

    assert first.canonical_dict() == second.canonical_dict()
    assert first.digest() == second.digest()
    assert changed.digest() != first.digest()


def test_budget_is_finite_and_fails_closed_before_selection() -> None:
    population = _population()
    policy = EvolutionarySelectionPolicy(population_size=3, generations=2, evaluation_budget=9, seed=1)

    result = run_experimental_evolutionary_selection(population, policy, opt_in=EXPERIMENTAL_OPT_IN)

    assert result.disposition is SelectionDisposition.BUDGET_EXCEEDED
    assert result.selected == ()
    assert result.evaluations == 0
    assert result.provenance is None


def test_default_invocation_cannot_reach_experimental_path() -> None:
    policy = EvolutionarySelectionPolicy()

    result = run_experimental_evolutionary_selection(_population(), policy)

    assert result.disposition is SelectionDisposition.OPT_IN_REQUIRED
    assert result.selected == ()
    assert result.evaluations == 0


def test_unavailable_or_invalid_evidence_fails_closed() -> None:
    policy = EvolutionarySelectionPolicy(population_size=1, generations=1, evaluation_budget=1)

    unavailable = run_experimental_evolutionary_selection(None, policy, opt_in=EXPERIMENTAL_OPT_IN)
    malformed = run_experimental_evolutionary_selection((None,), policy, opt_in=EXPERIMENTAL_OPT_IN)  # type: ignore[arg-type]

    assert unavailable.disposition is SelectionDisposition.UNAVAILABLE
    assert malformed.disposition is SelectionDisposition.INVALID_INPUT
    assert unavailable.selected == malformed.selected == ()


def test_duplicate_and_cross_candidate_artifact_identity_fails_closed() -> None:
    policy = EvolutionarySelectionPolicy(population_size=1, generations=1, evaluation_budget=2)
    first = _evidence("candidate-a")
    duplicate = run_experimental_evolutionary_selection((first, first), policy, opt_in=EXPERIMENTAL_OPT_IN)
    shared_bundle = run_experimental_evolutionary_selection(
        (first, _evidence("candidate-b", bundle_key="candidate-a")),
        policy,
        opt_in=EXPERIMENTAL_OPT_IN,
    )

    assert duplicate.disposition is SelectionDisposition.INVALID_INPUT
    assert shared_bundle.disposition is SelectionDisposition.INVALID_INPUT
    assert "identity" in duplicate.reason
    assert "bundle" in shared_bundle.reason


def test_canonical_evidence_constructor_rejects_forged_lineage_binding() -> None:
    with pytest.raises(M08ContractError):
        replace(_evidence("candidate-a"), lineage_digest="f" * 64)


def test_policy_rejects_unbounded_or_malformed_configuration() -> None:
    with pytest.raises(EvolutionarySelectionError):
        EvolutionarySelectionPolicy(population_size=0)
    with pytest.raises(EvolutionarySelectionError):
        EvolutionarySelectionPolicy(generations=0)
    with pytest.raises(EvolutionarySelectionError):
        EvolutionarySelectionPolicy(evaluation_budget=0)
    with pytest.raises(EvolutionarySelectionError):
        EvolutionarySelectionPolicy(elite_count=5, population_size=4)


def test_experimental_module_has_no_production_generation_or_network_path() -> None:
    root = Path(__file__).resolve().parents[2]
    router = (root / "src" / "scrubbots_pixel_factory" / "generators" / "router" / "router.py").read_text(encoding="utf-8")
    cli = (root / "src" / "scrubbots_pixel_factory" / "cli" / "main.py").read_text(encoding="utf-8")
    module = (root / "src" / "scrubbots_pixel_factory" / "evolutionary_selection.py").read_text(encoding="utf-8")

    assert "evolutionary_selection" not in router
    assert "evolutionary_selection" not in cli
    assert "guarded_network_request" not in module
    assert "urlopen" not in module
    assert "promotion" not in run_experimental_evolutionary_selection(_population(), EvolutionarySelectionPolicy()).canonical_dict()
