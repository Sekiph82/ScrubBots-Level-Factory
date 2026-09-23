from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchEngine, BaselineSearchPolicy, SearchExecutionDisposition, SearchVerdict, TerminalObservation, TerminalTruth, TransitionObservation
from scrubbots_pixel_factory.canonical_bridge import CanonicalBridgeConfiguration, CanonicalBridgeDisposition, CanonicalHeadlessBridge
from scrubbots_pixel_factory.compact_solver_state import (
    ACTIVE_BYTE,
    CANONICAL_PROOF_STATE_AUTHORITY_SHA,
    CANONICAL_PROOF_STATE_SOURCE_SHA256,
    AuthorityVerificationDisposition,
    CompactSolverState,
    LevelIdentity,
    SolverStateAuthority,
    SupplyBatch,
)
from scrubbots_pixel_factory.legal_move_provider import LegalMove, LegalMoveQuery, LegalMoveResult, ProviderDisposition, ProviderEvidence
from scrubbots_pixel_factory.reproduction import ReplayDisposition, ReplayObservation, ReproductionBundle, ReproductionContractError, ReproductionManifest, ReproductionReplay
from scrubbots_pixel_factory.search_policy import BASELINE_SEARCH_POLICY, REVERSE_SEARCH_POLICY
from scrubbots_pixel_factory.solution_analysis import SolutionAnalysisBounds, SolutionCountDisposition, SolutionCountEngine
from scrubbots_pixel_factory.solver_budget import BudgetExhaustionReason, SolverBudgetPolicy, SolverOutcomeDisposition, classify_search_result, classify_solution_count_result
from scrubbots_pixel_factory.solver_evidence import EvidenceSearchEngine
from scrubbots_pixel_factory.visited_memoization import DeterministicVisitedMemo, MemoDisposition, StateKeyDisposition, StateKeyEvidence, StateKeyResult


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "lf03_solver_regression_v1.json"
AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)
STATES: dict[str, CompactSolverState] = {}


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_corpus() -> dict[str, object]:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert data["schema"] == "scrubbots-lf03-solver-regression-fixtures"
    assert data["version"] == 1
    seen: set[str] = set()
    for fixture in data["fixtures"]:
        assert fixture["id"] not in seen
        seen.add(fixture["id"])
        assert fixture["payload"]["production"] is False
        assert canonical_digest(fixture["payload"]) == fixture["payload_sha256"]
    return data


def payload(fixture_id: str) -> dict[str, object]:
    for fixture in load_corpus()["fixtures"]:
        if fixture["id"] == fixture_id:
            return fixture["payload"]
    raise AssertionError(f"missing fixture: {fixture_id}")


def make_state(name: str, dimensions: dict[str, int]) -> CompactSolverState:
    width = dimensions["width"]
    height = dimensions["height"]
    palette_size = dimensions["palette_size"]
    return CompactSolverState(
        AUTHORITY,
        LevelIdentity((name.encode().hex() + "a" * 64)[:64], name, width, height, width * height),
        bytes((ACTIVE_BYTE,) * (width * height)),
        ((SupplyBatch(f"batch-{name}", 1, 1),), (), (), ()),
        (None,) * 5,
        1,
        4,
        3,
        palette_size,
    )


class FixtureLegalProvider:
    provider_id = "lf03-regression-fake-legal-provider"
    provider_version = "fixture-only-v1"

    def __init__(self, graph: dict[str, object]) -> None:
        self.graph = graph

    def query(self, request):
        evidence = ProviderEvidence(
            self.provider_id,
            self.provider_version,
            request.authority,
            ProviderDisposition.AVAILABLE,
            AuthorityVerificationDisposition.VERIFIED,
            AuthorityVerificationDisposition.VERIFIED,
            "CANONICAL_RUNTIME",
            "fixture-only fake graph provider",
        )
        node = self.graph["nodes"][request.state.level.level_id]
        return LegalMoveResult.from_query(request, ProviderDisposition.AVAILABLE, evidence, tuple(LegalMove(column) for column in node["moves"]))


class FixtureTransitionProvider:
    def __init__(self, graph: dict[str, object]) -> None:
        self.graph = graph

    def terminal(self, current):
        truth = TerminalTruth(self.graph["nodes"][current.level.level_id]["truth"])
        return TerminalObservation(SearchExecutionDisposition.AVAILABLE, truth, "fixture terminal truth")

    def transition(self, current, move):
        edges = self.graph["nodes"][current.level.level_id]["edges"]
        destination = edges.get(str(move.column))
        if destination is None:
            return TransitionObservation(SearchExecutionDisposition.ERROR, None, None, "fixture transition missing")
        return TransitionObservation(SearchExecutionDisposition.AVAILABLE, STATES[destination], None, "fixture transition")


def build_graph() -> tuple[dict[str, object], FixtureLegalProvider, FixtureTransitionProvider, CompactSolverState]:
    graph = payload("LF03_FAKE_GRAPH_BRANCHING_SOLVED_V1")
    assert graph["label"] == "fixture-only fake provider graph"
    assert graph["state_dimensions"]["width"] != graph["state_dimensions"]["height"]
    STATES.clear()
    for name in graph["nodes"]:
        STATES[name] = make_state(name, graph["state_dimensions"])
    return graph, FixtureLegalProvider(graph), FixtureTransitionProvider(graph), STATES[graph["initial"]]


def state_key_result(compact: CompactSolverState, key: str) -> StateKeyResult:
    evidence = StateKeyEvidence("lf03-regression-key", "fixture-only-v1", AUTHORITY, StateKeyDisposition.AVAILABLE, AuthorityVerificationDisposition.VERIFIED, AuthorityVerificationDisposition.VERIFIED, "fixture-only key")
    return StateKeyResult(StateKeyDisposition.AVAILABLE, compact.digest(), AUTHORITY, evidence.provider_id, evidence.provider_version, evidence, key, "fixture-only key")


def test_fixture_corpus_schema_ids_and_payload_checksums() -> None:
    data = load_corpus()
    ids = {fixture["id"] for fixture in data["fixtures"]}
    assert {
        "LF03_FAKE_GRAPH_BRANCHING_SOLVED_V1",
        "LF03_DUPLICATE_MEMO_KEYS_V1",
        "LF03_REPRODUCTION_MATCH_DIVERGED_V1",
        "LF03_AUTHORITY_TAMPER_FAIL_CLOSED_V1",
    } <= ids
    bridge = data["canonical_bridge_fixture"]
    assert bridge["id"] == "LF03_CANONICAL_BRIDGE_CAPABILITY_V1"
    assert bridge["authority_sha"] == CANONICAL_PROOF_STATE_AUTHORITY_SHA


def test_provider_schema_branching_search_and_proven_no_solution_fixture() -> None:
    graph, legal, transition, initial = build_graph()
    query = LegalMoveQuery(initial, initial.digest(), AUTHORITY, legal.provider_id, legal.provider_version)
    request_result = legal.query(query)
    assert request_result.disposition is ProviderDisposition.AVAILABLE
    assert [move.column for move in request_result.moves] == graph["nodes"]["root"]["moves"]

    solved = BaselineSearchEngine(legal, transition).search(initial)
    dead = BaselineSearchEngine(legal, transition).search(STATES[graph["expected"]["proven_unsolvable_node"]])
    assert solved.verdict is SearchVerdict.SOLVED
    assert [move.column for move in solved.path] == graph["expected"]["first_solution_path"]
    assert dead.verdict is SearchVerdict.PROVEN_UNSOLVABLE


def test_duplicate_state_memo_fixture() -> None:
    memo_payload = payload("LF03_DUPLICATE_MEMO_KEYS_V1")
    states = {item["state"]: make_state(item["state"], {"width": 2, "height": 2, "palette_size": 4}) for item in memo_payload["observations"]}
    memo = DeterministicVisitedMemo(AUTHORITY, "lf03-regression-key", "fixture-only-v1")
    observed = []
    for item in memo_payload["observations"]:
        result = memo.observe(state_key_result(states[item["state"]], item["key"]))
        observed.append(result.disposition.value)
    assert observed == [item["expected"] for item in memo_payload["observations"]]
    assert result.visited_count == memo_payload["expected"]["visited_count"]
    assert result.memo_hits == memo_payload["expected"]["memo_hits"]
    assert result.disposition is MemoDisposition.FIRST_VISIT


def test_bound_exhaustion_and_unknown_bound_are_inconclusive() -> None:
    _graph, legal, transition, initial = build_graph()
    depth_limited = BaselineSearchEngine(legal, transition, BaselineSearchPolicy(max_depth=0)).search(initial)
    state_limited = SolutionCountEngine(legal, transition, SolutionAnalysisBounds(max_states=1)).analyze(initial)
    unknown = BaselineSearchEngine(legal, transition).search(STATES["unknown"])
    depth_outcome = classify_search_result(depth_limited, policy=SolverBudgetPolicy(max_depth=0))
    state_outcome = classify_solution_count_result(state_limited)
    unknown_outcome = classify_search_result(unknown)
    assert depth_outcome.disposition is SolverOutcomeDisposition.INCONCLUSIVE
    assert depth_outcome.exhaustion is BudgetExhaustionReason.MAX_DEPTH
    assert state_outcome.disposition is SolverOutcomeDisposition.INCONCLUSIVE
    assert state_outcome.exhaustion is BudgetExhaustionReason.MAX_VISITED_STATES
    assert unknown_outcome.disposition is SolverOutcomeDisposition.INCONCLUSIVE
    assert unknown_outcome.exhaustion is BudgetExhaustionReason.UNKNOWN_BOUND


def test_zero_one_and_multiple_solution_count_fixtures() -> None:
    graph, legal, transition, initial = build_graph()
    zero = SolutionCountEngine(legal, transition).analyze(STATES[graph["expected"]["proven_unsolvable_node"]])
    one = SolutionCountEngine(legal, transition).analyze(STATES["goal_a"])
    multiple = SolutionCountEngine(legal, transition, search_policy=REVERSE_SEARCH_POLICY).analyze(initial)
    assert zero.disposition is SolutionCountDisposition.EXACT and zero.solution_count == 0
    assert one.disposition is SolutionCountDisposition.EXACT and one.solution_count == 1
    assert multiple.disposition is SolutionCountDisposition.EXACT
    assert multiple.solution_count == graph["expected"]["solution_count"]


def test_solver_evidence_metrics_are_deterministic() -> None:
    graph, legal, transition, initial = build_graph()
    first = EvidenceSearchEngine(legal, transition).search(initial)
    second = EvidenceSearchEngine(legal, transition).search(initial)
    assert first.metrics is not None
    assert first.metrics.dead_end_count == graph["expected"]["dead_end_count"]
    assert first.metrics.branch_counts == tuple(graph["expected"]["branch_counts"])
    assert first.budget_result is not None
    assert first.budget_result.disposition is SolverOutcomeDisposition.SOLVED
    assert first.canonical_bytes() == second.canonical_bytes()


def test_reproduction_match_diverged_and_authority_tamper_fail_closed() -> None:
    repro = payload("LF03_REPRODUCTION_MATCH_DIVERGED_V1")
    evidence_digest = hashlib.sha256(repro["evidence_source"].encode("utf-8")).hexdigest()
    manifest = ReproductionManifest(
        candidate_source_sha256=hashlib.sha256(repro["candidate_source"].encode("utf-8")).hexdigest(),
        level_data_source_sha256=hashlib.sha256(repro["level_data_source"].encode("utf-8")).hexdigest(),
        seed=repro["seed"],
        normalized_config=repro["normalized_config"],
        generator_version="lf03-regression-generator-v1",
        authority=AUTHORITY,
        source_contract_sha256=CANONICAL_PROOF_STATE_SOURCE_SHA256,
        provider_id="lf03-regression-fake-legal-provider",
        provider_version="fixture-only-v1",
        bridge_version="external-godot-runner-v1",
        search_version="DFS_CANONICAL_PROVIDER_ORDER_V1",
        memo_provider_id=None,
        memo_provider_version=None,
        search_policy=BASELINE_SEARCH_POLICY,
        budgets=SolverBudgetPolicy(max_visited_states=50, max_depth=8, max_solutions=10),
        operation="SOLVE",
        goal="SOLVED",
        expected_disposition=repro["expected_disposition"],
        observed_evidence_digest=evidence_digest,
        observed_path=tuple(repro["path"]),
    )
    bundle = ReproductionBundle.create(manifest)
    replay = ReproductionReplay()
    assert replay.replay(bundle, ReplayObservation("SOLVED", evidence_digest, tuple(repro["path"]))).disposition is ReplayDisposition.MATCH
    assert replay.replay(bundle, ReplayObservation("SOLVED", hashlib.sha256(b"other").hexdigest(), tuple(repro["path"]))).disposition is ReplayDisposition.DIVERGED

    tamper = payload("LF03_AUTHORITY_TAMPER_FAIL_CLOSED_V1")
    with pytest.raises(ReproductionContractError):
        ReproductionManifest(
            candidate_source_sha256="1" * 64,
            level_data_source_sha256="2" * 64,
            seed=1,
            normalized_config={},
            generator_version="lf03-regression-generator-v1",
            authority=SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", tamper["invalid_authority_sha"]),
            source_contract_sha256=CANONICAL_PROOF_STATE_SOURCE_SHA256,
            provider_id="provider",
            provider_version="v1",
            bridge_version="bridge-v1",
            search_version="search-v1",
            memo_provider_id=None,
            memo_provider_version=None,
            search_policy=BASELINE_SEARCH_POLICY,
            budgets=SolverBudgetPolicy(),
            operation="SOLVE",
            goal="SOLVED",
            expected_disposition="SOLVED",
        )


def test_real_canonical_bridge_fixture_is_capability_gated() -> None:
    bridge_fixture = load_corpus()["canonical_bridge_fixture"]
    missing = [name for name in bridge_fixture["requires_env"] if not os.environ.get(name)]
    if missing:
        pytest.skip(bridge_fixture["skip_reason"])
    checkout = Path(os.environ["SCRUBBOTS_CANONICAL_CHECKOUT"]).resolve()
    runner = Path(os.environ["SCRUBBOTS_CANONICAL_BRIDGE_RUNNER"]).resolve()
    before_status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=checkout, capture_output=True, text=True, check=False).stdout
    before_source = (checkout / "scripts/gameplay/solver/proof_state.gd").read_bytes()
    bridge = CanonicalHeadlessBridge(CanonicalBridgeConfiguration(str(checkout), str(runner)))
    capability = bridge.capability(AUTHORITY)
    assert capability.disposition is CanonicalBridgeDisposition.AVAILABLE
    after_status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=checkout, capture_output=True, text=True, check=False).stdout
    after_source = (checkout / "scripts/gameplay/solver/proof_state.gd").read_bytes()
    assert before_status == after_status
    assert before_source == after_source


def test_regression_fixture_suite_has_no_gameplay_or_wfc_implementation() -> None:
    source = FIXTURE_PATH.read_text(encoding="utf-8").lower()
    assert "legal_action_columns" not in source
    assert "apply_placement" not in source
    assert "canonical_key" not in source
    assert "wfc" not in source
