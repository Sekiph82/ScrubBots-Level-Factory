from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, CANONICAL_PROOF_STATE_SOURCE_SHA256, SolverStateAuthority
from scrubbots_pixel_factory.reproduction import ReplayDisposition, ReplayObservation, ReproductionBundle, ReproductionContractError, ReproductionManifest, ReproductionReplay
from scrubbots_pixel_factory.search_policy import BASELINE_SEARCH_POLICY
from scrubbots_pixel_factory.solution_analysis import SolutionAnalysisBounds


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)
HASH_A = hashlib.sha256(b"candidate-a").hexdigest()
HASH_LEVEL = hashlib.sha256(b"level-a").hexdigest()
EVIDENCE = hashlib.sha256(b"evidence-a").hexdigest()
PATH = ({"kind": "CANONICAL_COLUMN_FRONT_V1", "column": 1},)


def manifest(seed: int = 7) -> ReproductionManifest:
    return ReproductionManifest(
        candidate_source_sha256=HASH_A,
        level_data_source_sha256=HASH_LEVEL,
        seed=seed,
        normalized_config={"width": 4, "palette": [0, 1, 2], "nested": {"strength": 0.5}},
        generator_version="factory-generator-v1",
        authority=AUTHORITY,
        source_contract_sha256=CANONICAL_PROOF_STATE_SOURCE_SHA256,
        provider_id="fixture-legal-provider",
        provider_version="fixture-legal-v1",
        bridge_version="canonical-proof-kernel-bridge-v1",
        search_version="DFS_CANONICAL_PROVIDER_ORDER_V1",
        memo_provider_id="fixture-key-provider",
        memo_provider_version="fixture-key-v1",
        search_policy=BASELINE_SEARCH_POLICY,
        budgets=SolutionAnalysisBounds(max_depth=8, max_states=100, max_solutions=10),
        operation="SOLVE",
        goal="SOLVED",
        expected_disposition="SOLVED",
        observed_evidence_digest=EVIDENCE,
        observed_path=PATH,
    )


def test_identical_manifest_and_bundle_bytes_are_deterministic() -> None:
    first = ReproductionBundle.create(manifest())
    second = ReproductionBundle.create(manifest())
    assert first.manifest.digest() == second.manifest.digest()
    assert first.canonical_bytes() == second.canonical_bytes()


def test_replay_matches_existing_layer_observation() -> None:
    bundle = ReproductionBundle.create(manifest())
    result = ReproductionReplay().replay(bundle, ReplayObservation("SOLVED", EVIDENCE, PATH))
    assert result.disposition is ReplayDisposition.MATCH


def test_seed_config_and_version_changes_diverge_identity() -> None:
    baseline = manifest()
    assert replace(baseline, seed=8).digest() != baseline.digest()
    assert replace(baseline, normalized_config={"width": 5}).digest() != baseline.digest()
    assert replace(baseline, generator_version="factory-generator-v2").digest() != baseline.digest()
    assert replace(baseline, search_version="DFS_OTHER_V1").digest() != baseline.digest()


def test_tampered_hash_or_authority_fails_closed() -> None:
    baseline = manifest()
    try:
        ReproductionBundle(baseline, "0" * 64)
    except ReproductionContractError:
        pass
    else:
        raise AssertionError("tampered manifest digest must be rejected")
    wrong_authority = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", "0" * 40)
    try:
        replace(baseline, authority=wrong_authority)
    except ReproductionContractError:
        pass
    else:
        raise AssertionError("authority drift must be rejected")


def test_replay_diverges_and_unavailable_is_distinct() -> None:
    bundle = ReproductionBundle.create(manifest())
    replay = ReproductionReplay()
    assert replay.replay(bundle, ReplayObservation("PROVEN_UNSOLVABLE", EVIDENCE, PATH)).disposition is ReplayDisposition.DIVERGED
    assert replay.replay(bundle, None).disposition is ReplayDisposition.UNAVAILABLE
    assert replay.replay(bundle, ReplayObservation("UNAVAILABLE")).disposition is ReplayDisposition.UNAVAILABLE
    assert replay.replay(bundle, ReplayObservation("ERROR")).disposition is ReplayDisposition.ERROR


def test_replay_revalidates_all_execution_identity_context_fields() -> None:
    bundle = ReproductionBundle.create(manifest())
    context = bundle.manifest.execution_context()
    for field, value in (("candidate_source_sha256", "0" * 64), ("level_data_source_sha256", "1" * 64), ("seed", 8), ("generator_version", "other"), ("provider_version", "other"), ("bridge_version", "other"), ("search_version", "other"), ("operation", "OTHER")):
        tampered = dict(context)
        tampered[field] = value
        result = ReproductionReplay().replay(bundle, ReplayObservation("SOLVED", EVIDENCE, PATH, tampered))
        assert result.disposition is ReplayDisposition.DIVERGED, field


def test_no_secrets_absolute_paths_or_gameplay_reimplementation() -> None:
    try:
        replace(manifest(), normalized_config={"api_key": "secret-value"})
    except ReproductionContractError:
        pass
    else:
        raise AssertionError("secrets must be rejected")
    try:
        replace(manifest(), normalized_config={"output": "C:\\private\\candidate.png"})
    except ReproductionContractError:
        pass
    else:
        raise AssertionError("absolute paths must be rejected")
    source = (Path(__file__).resolve().parents[2] / "src" / "scrubbots_pixel_factory" / "reproduction.py").read_text(encoding="utf-8").lower()
    assert "apply_placement" not in source
    assert "legal_action_columns" not in source
    assert "wfc" not in source
