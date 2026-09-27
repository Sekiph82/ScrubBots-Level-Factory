from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

import pytest

from scrubbots_pixel_factory import (
    CANDIDATE_ARTIFACT_IDENTITY_FIELDS,
    CANDIDATE_ARTIFACT_IDENTITY_POLICY_VERSION,
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


def _artifact_material(
    candidate: str,
    *,
    bundle_key: str | None = None,
    shared_tokens: dict[str, str] | None = None,
    shared_refs: dict[str, str] | None = None,
) -> tuple[dict[str, bytes], dict[str, bytes]]:
    tokens = {field: candidate for field in (
        "m03_digest", "m04_digest", "m04_lane_digest", "m05_digest",
        "level_data_digest", "logical_art_digest", "grid_hash",
        "source_provenance_digest", "generation_request_digest",
        "generation_result_digest", "generation_metadata_digest", "bundle_digest",
    )}
    tokens.update(shared_tokens or {})
    if bundle_key is not None:
        tokens["bundle_digest"] = bundle_key
    raw = {
        "m03_digest": f"m03:{tokens['m03_digest']}".encode(),
        "m04_digest": f"m04:{tokens['m04_digest']}".encode(),
        "m04_lane_digest": f"lane:{tokens['m04_lane_digest']}".encode(),
        "m05_digest": f"m05:{tokens['m05_digest']}".encode(),
        "level_data_digest": f"level:{tokens['level_data_digest']}".encode(),
        "logical_art_digest": f"art:{tokens['logical_art_digest']}".encode(),
        "grid_hash": f"grid:{tokens['grid_hash']}".encode(),
        "source_provenance_digest": f"source:{tokens['source_provenance_digest']}".encode(),
        "generation_request_digest": f"request:{tokens['generation_request_digest']}".encode(),
        "generation_result_digest": f"result:{tokens['generation_result_digest']}".encode(),
        "generation_metadata_digest": f"generation:{tokens['generation_metadata_digest']}".encode(),
        "bundle_digest": f"bundle:{tokens['bundle_digest']}".encode(),
    }
    refs = {
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
    }
    refs.update(shared_refs or {})
    artifacts = {
        refs[reference_field]: raw[digest_field]
        for reference_field, digest_field in CANDIDATE_ARTIFACT_IDENTITY_FIELDS
        if refs.get(reference_field) is not None and digest_field in raw
    }
    return raw, artifacts


def _evidence(
    candidate: str,
    *,
    bundle_key: str | None = None,
    shared_tokens: dict[str, str] | None = None,
    shared_refs: dict[str, str] | None = None,
) -> CandidateEvidence:
    raw, _ = _artifact_material(
        candidate,
        bundle_key=bundle_key,
        shared_tokens=shared_tokens,
        shared_refs=shared_refs,
    )
    values = {
        **{key: hashlib.sha256(value).hexdigest() for key, value in raw.items()},
        **{
            key: value
            for key, value in {
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
            }.items()
        },
        "preview_digest": None,
        "preview_ref": None,
        "mutation_digest": None,
        "mutation_ref": None,
    }
    values.update(shared_refs or {})
    values["lineage_digest"] = lineage_digest_for(
        {"candidate_id": candidate, "lane": LaneClass.EASY.value, "m03_disposition": "ACCEPT", "m04_disposition": "ACCEPT", "m05_disposition": "ACCEPT", **values}
    )
    return CandidateEvidence(candidate_id=candidate, lane=LaneClass.EASY, m03_disposition="ACCEPT", m04_disposition="ACCEPT", m05_disposition="ACCEPT", **values)


def _population(count: int = 5) -> tuple[CandidateEvidence, ...]:
    return tuple(_evidence(f"candidate-{index}") for index in range(count))


def _artifacts_for(*candidates: CandidateEvidence) -> dict[str, bytes]:
    artifacts: dict[str, bytes] = {}
    for candidate in candidates:
        _, candidate_artifacts = _artifact_material(candidate.candidate_id)
        artifacts.update(candidate_artifacts)
    return artifacts


def test_positive_selection_is_opt_in_bounded_and_lineage_preserving() -> None:
    population = _population()
    policy = EvolutionarySelectionPolicy(population_size=3, generations=2, evaluation_budget=10, elite_count=2, seed=17)

    result = run_experimental_evolutionary_selection(
        population,
        policy,
        opt_in=EXPERIMENTAL_OPT_IN,
        artifacts=_artifacts_for(*population),
    )

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

    artifacts = _artifacts_for(*population)
    first = run_experimental_evolutionary_selection(
        population, policy, opt_in=EXPERIMENTAL_OPT_IN, artifacts=artifacts
    )
    second = run_experimental_evolutionary_selection(
        tuple(reversed(population)), policy, opt_in=EXPERIMENTAL_OPT_IN, artifacts=artifacts
    )
    changed = run_experimental_evolutionary_selection(
        population,
        replace(policy, seed=43),
        opt_in=EXPERIMENTAL_OPT_IN,
        artifacts=artifacts,
    )

    assert first.canonical_dict() == second.canonical_dict()
    assert first.digest() == second.digest()
    assert changed.digest() != first.digest()


def test_budget_is_finite_and_fails_closed_before_selection() -> None:
    population = _population()
    policy = EvolutionarySelectionPolicy(population_size=3, generations=2, evaluation_budget=9, seed=1)

    result = run_experimental_evolutionary_selection(
        population,
        policy,
        opt_in=EXPERIMENTAL_OPT_IN,
        artifacts=_artifacts_for(*population),
    )

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
        artifacts=_artifacts_for(first, _evidence("candidate-b", bundle_key="candidate-a")),
    )

    assert duplicate.disposition is SelectionDisposition.INVALID_INPUT
    assert shared_bundle.disposition is SelectionDisposition.INVALID_INPUT
    assert "identity" in duplicate.reason
    assert "bundle" in shared_bundle.reason


def test_missing_and_stale_artifact_bytes_fail_closed_before_ranking() -> None:
    policy = EvolutionarySelectionPolicy(population_size=1, generations=1, evaluation_budget=1)
    candidate = _evidence("candidate-a")
    artifacts = _artifacts_for(candidate)

    missing = dict(artifacts)
    del missing[candidate.generation_result_ref]
    stale = dict(artifacts)
    stale[candidate.generation_result_ref] = b"stale bytes"

    missing_result = run_experimental_evolutionary_selection(
        (candidate,), policy, opt_in=EXPERIMENTAL_OPT_IN, artifacts=missing
    )
    stale_result = run_experimental_evolutionary_selection(
        (candidate,), policy, opt_in=EXPERIMENTAL_OPT_IN, artifacts=stale
    )

    assert missing_result.disposition is SelectionDisposition.UNAVAILABLE
    assert stale_result.disposition is SelectionDisposition.UNAVAILABLE
    assert missing_result.selected == stale_result.selected == ()
    assert missing_result.evaluations == stale_result.evaluations == 0


@pytest.mark.parametrize("reference_field,digest_field", CANDIDATE_ARTIFACT_IDENTITY_FIELDS)
def test_every_required_artifact_identity_is_candidate_specific(
    reference_field: str, digest_field: str
) -> None:
    policy = EvolutionarySelectionPolicy(population_size=1, generations=1, evaluation_budget=2)
    first = _evidence("candidate-a")
    second_kwargs = {
        "shared_tokens": {digest_field: "candidate-a"},
        "shared_refs": {reference_field: getattr(first, reference_field)},
    }
    second = _evidence("candidate-b", **second_kwargs)
    _, first_artifacts = _artifact_material("candidate-a")
    _, second_artifacts = _artifact_material("candidate-b", **second_kwargs)
    artifacts = {**first_artifacts, **second_artifacts}

    result = run_experimental_evolutionary_selection(
        (first, second), policy, opt_in=EXPERIMENTAL_OPT_IN, artifacts=artifacts
    )

    assert result.disposition is SelectionDisposition.INVALID_INPUT


def test_identity_policy_is_explicitly_versioned_with_no_shared_exception() -> None:
    policy = EvolutionarySelectionPolicy()

    assert policy.canonical_dict()["artifact_identity_policy_version"] == CANDIDATE_ARTIFACT_IDENTITY_POLICY_VERSION
    assert policy.canonical_dict()["candidate_specific_artifact_fields"] == [
        list(pair) for pair in CANDIDATE_ARTIFACT_IDENTITY_FIELDS
    ]


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
