from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

import pytest

from scrubbots_pixel_factory import (
    CandidateEvidence,
    CandidateFitness,
    CANDIDATE_ARTIFACT_IDENTITY_FIELDS,
    DEFAULT_FITNESS_METRIC_CATALOG,
    EXPERIMENTAL_OPT_IN,
    FITNESS_SCORE_SCALE,
    FitnessMetricError,
    FitnessMetricValue,
    FitnessPolicy,
    SelectionDisposition,
    EvolutionarySelectionPolicy,
    evaluate_fitness,
    run_experimental_evolutionary_selection,
    validate_fitness_result,
)
from scrubbots_pixel_factory.difficulty_analysis import LaneClass
from scrubbots_pixel_factory.m08_batch import lineage_digest_for


def _candidate(name: str, *, optional: bool = False) -> tuple[CandidateEvidence, dict[str, bytes]]:
    raw = {
        "level_data_digest": f"level:{name}".encode(),
        "logical_art_digest": f"art:{name}".encode(),
        "bundle_digest": f"bundle:{name}".encode(),
        "source_provenance_digest": f"source:{name}".encode(),
        "m03_digest": f"m03:{name}".encode(),
        "m04_digest": f"m04:{name}".encode(),
        "m05_digest": f"m05:{name}".encode(),
        "generation_request_digest": f"request:{name}".encode(),
        "generation_result_digest": f"result:{name}".encode(),
        "generation_metadata_digest": f"metadata:{name}".encode(),
    }
    refs = {
        "level_data_ref": f"level-data/{name}.json",
        "logical_art_ref": f"art/{name}.png",
        "bundle_ref": f"bundles/{name}",
        "source_provenance_ref": f"provenance/{name}.json",
        "m03_ref": f"evidence/m03-{name}.json",
        "m04_ref": f"evidence/m04-{name}.json",
        "m05_ref": f"evidence/m05-{name}.json",
        "generation_request_ref": f"generation/request-{name}.json",
        "generation_result_ref": f"generation/result-{name}.json",
        "generation_metadata_ref": f"generation/metadata-{name}.json",
        "preview_ref": f"previews/{name}.png" if optional else None,
        "mutation_ref": f"mutations/{name}.json" if optional else None,
    }
    if optional:
        raw["preview_digest"] = f"preview:{name}".encode()
        raw["mutation_digest"] = f"mutation:{name}".encode()
    values = {key: hashlib.sha256(value).hexdigest() for key, value in raw.items()}
    values["m04_lane_digest"] = hashlib.sha256(f"lane:{name}".encode()).hexdigest()
    values["grid_hash"] = hashlib.sha256(f"grid:{name}".encode()).hexdigest()
    values.setdefault("preview_digest", None)
    values.setdefault("mutation_digest", None)
    values.update(refs)
    values["lineage_digest"] = lineage_digest_for({
        "candidate_id": name,
        "lane": LaneClass.EASY.value,
        "m03_disposition": "ACCEPT",
        "m04_disposition": "ACCEPT",
        "m05_disposition": "ACCEPT",
        **values,
    })
    evidence = CandidateEvidence(
        candidate_id=name,
        lane=LaneClass.EASY,
        m03_disposition="ACCEPT",
        m03_digest=values["m03_digest"],
        m04_disposition="ACCEPT",
        m04_digest=values["m04_digest"],
        m04_lane_digest=values["m04_lane_digest"],
        m05_disposition="ACCEPT",
        m05_digest=values["m05_digest"],
        level_data_digest=values["level_data_digest"],
        logical_art_digest=values["logical_art_digest"],
        grid_hash=values["grid_hash"],
        source_provenance_digest=values["source_provenance_digest"],
        generation_request_digest=values["generation_request_digest"],
        generation_request_ref=values["generation_request_ref"],
        generation_result_digest=values["generation_result_digest"],
        generation_result_ref=values["generation_result_ref"],
        generation_metadata_digest=values["generation_metadata_digest"],
        generation_metadata_ref=values["generation_metadata_ref"],
        bundle_digest=values["bundle_digest"],
        lineage_digest=values["lineage_digest"],
        level_data_ref=values["level_data_ref"],
        logical_art_ref=values["logical_art_ref"],
        bundle_ref=values["bundle_ref"],
        source_provenance_ref=values["source_provenance_ref"],
        m03_ref=values["m03_ref"],
        m04_ref=values["m04_ref"],
        m05_ref=values["m05_ref"],
        preview_digest=values.get("preview_digest"),
        preview_ref=values.get("preview_ref"),
        mutation_digest=values.get("mutation_digest"),
        mutation_ref=values.get("mutation_ref"),
    )
    artifacts = {
        refs[field]: raw[digest_field]
        for field, digest_field in CANDIDATE_ARTIFACT_IDENTITY_FIELDS
        if refs[field] is not None and digest_field in raw
    }
    return evidence, artifacts


def _population() -> tuple[tuple[CandidateEvidence, ...], dict[str, bytes]]:
    items = tuple(_candidate(f"candidate-{index}", optional=index == 0) for index in range(3))
    candidates = tuple(item[0] for item in items)
    artifacts: dict[str, bytes] = {}
    for _, item_artifacts in items:
        artifacts.update(item_artifacts)
    return candidates, artifacts


def test_closed_catalog_and_policy_digest_are_canonical_and_versioned() -> None:
    policy = FitnessPolicy()
    restored = FitnessPolicy.from_dict(policy.canonical_dict())

    assert policy.canonical_dict() == restored.canonical_dict()
    assert policy.digest() == restored.digest()
    assert tuple(item.metric_id for item in policy.metric_catalog) == (
        "artifact_identity_coverage", "optional_artifact_coverage"
    )
    assert all(item.unit == "basis_points" and item.direction == "MAXIMIZE" for item in DEFAULT_FITNESS_METRIC_CATALOG)
    assert "fitness_policy" in EvolutionarySelectionPolicy().canonical_dict()


def test_fitness_replay_is_byte_identical_and_finite() -> None:
    candidates, artifacts = _population()
    policy = FitnessPolicy()

    first = evaluate_fitness(candidates, policy, artifacts)
    second = evaluate_fitness(tuple(reversed(candidates)), policy, artifacts)

    assert first.canonical_dict() == second.canonical_dict()
    assert first.evaluation_digest == second.evaluation_digest
    assert all(0 <= item.aggregate_score <= FITNESS_SCORE_SCALE for item in first.results)
    assert all(type(value.normalized_value) is int for item in first.results for value in item.metrics)


def test_each_result_binds_exact_candidate_lineage_and_policy() -> None:
    candidates, artifacts = _population()
    policy = FitnessPolicy()
    evaluation = evaluate_fitness(candidates, policy, artifacts)
    result = evaluation.for_candidate(candidates[0], policy)

    assert validate_fitness_result(candidates[0], result, policy, artifacts) == result
    with pytest.raises(FitnessMetricError, match="another candidate|forged|stale"):
        validate_fitness_result(candidates[1], result, policy, artifacts)
    with pytest.raises(FitnessMetricError):
        replace(result, aggregate_score=0)


def test_missing_or_forged_metric_evidence_fails_closed() -> None:
    candidates, artifacts = _population()
    candidate = candidates[0]
    missing = dict(artifacts)
    del missing[candidate.generation_result_ref]

    with pytest.raises(FitnessMetricError, match="missing|stale|unavailable"):
        evaluate_fitness((candidate,), FitnessPolicy(), missing)
    with pytest.raises(FitnessMetricError):
        FitnessMetricValue("artifact_identity_coverage", FITNESS_SCORE_SCALE + 1)
    with pytest.raises(FitnessMetricError):
        CandidateFitness.from_dict({"schema": "scrubbots-experimental-fitness"})


def test_selection_publishes_fitness_bindings_without_production_promotion() -> None:
    candidates, artifacts = _population()
    result = run_experimental_evolutionary_selection(
        candidates,
        EvolutionarySelectionPolicy(population_size=2, generations=1, evaluation_budget=3),
        opt_in=EXPERIMENTAL_OPT_IN,
        artifacts=artifacts,
    )

    assert result.disposition is SelectionDisposition.SELECTED
    assert result.fitness is not None
    assert result.provenance is not None
    assert result.provenance.fitness_policy_digest == FitnessPolicy().digest()
    assert result.provenance.fitness_evaluation_digest == result.fitness.evaluation_digest
    assert "promotion" not in result.canonical_dict()


def test_metric_module_remains_offline_and_production_isolated() -> None:
    root = Path(__file__).resolve().parents[2]
    module = (root / "src" / "scrubbots_pixel_factory" / "fitness_metrics.py").read_text(encoding="utf-8")
    router = (root / "src" / "scrubbots_pixel_factory" / "generators" / "router" / "router.py").read_text(encoding="utf-8")
    cli = (root / "src" / "scrubbots_pixel_factory" / "cli" / "main.py").read_text(encoding="utf-8")

    assert "guarded_network_request" not in module
    assert "urlopen" not in module
    assert "evolutionary_selection" not in router
    assert "evolutionary_selection" not in cli
