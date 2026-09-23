from __future__ import annotations

import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
import shutil
import subprocess

import pytest

from scrubbots_pixel_factory.baseline_search import BaselineSearchEngine, BaselineSearchPolicy, SearchExecutionDisposition, SearchVerdict, TerminalObservation, TerminalTruth, TransitionObservation
from scrubbots_pixel_factory.canonical_bridge import CanonicalBridgeConfiguration, CanonicalBridgeDisposition, CanonicalBridgeError, CanonicalBridgeRequest, CanonicalHeadlessBridge
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
from scrubbots_pixel_factory.legal_move_provider import LegalMove, LegalMoveProviderError, LegalMoveQuery, LegalMoveResult, ProviderDisposition, ProviderEvidence
from scrubbots_pixel_factory.reproduction import ReplayDisposition, ReplayExecutionContext, ReplayObservation, ReproductionBundle, ReproductionContractError, ReproductionManifest, ReproductionReplay
from scrubbots_pixel_factory.search_policy import BASELINE_SEARCH_POLICY, REVERSE_SEARCH_POLICY
from scrubbots_pixel_factory.solution_analysis import SolutionAnalysisBounds, SolutionCountDisposition, SolutionCountEngine
from scrubbots_pixel_factory.solver_budget import BudgetExhaustionReason, OperationalExecutionDisposition, SolverBudgetPolicy, SolverOutcomeDisposition, classify_search_result, classify_solution_count_result, wrap_operational_execution
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
    for fixture in data["negative_fixtures"]:
        assert fixture["version"] == 1
        assert fixture["payload"]["production"] is False
        assert canonical_digest(fixture["payload"]) == fixture["payload_sha256"]
    return data


def payload(fixture_id: str) -> dict[str, object]:
    for fixture in load_corpus()["fixtures"]:
        if fixture["id"] == fixture_id:
            return fixture["payload"]
    raise AssertionError(f"missing fixture: {fixture_id}")


def negative_payload(fixture_id: str) -> dict[str, object]:
    for fixture in load_corpus()["negative_fixtures"]:
        if fixture["id"] == fixture_id:
            return fixture["payload"]
    raise AssertionError(f"missing negative fixture: {fixture_id}")


def make_state(name: str, dimensions: dict[str, int], authority: SolverStateAuthority = AUTHORITY) -> CompactSolverState:
    width = dimensions["width"]
    height = dimensions["height"]
    palette_size = dimensions["palette_size"]
    return CompactSolverState(
        authority,
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


class ForeignAuthorityTransitionProvider:
    def __init__(self, graph: dict[str, object], foreign_state: CompactSolverState) -> None:
        self.graph = graph
        self.foreign_state = foreign_state
        self.foreign_terminal_calls = 0

    def terminal(self, current):
        if current is self.foreign_state:
            self.foreign_terminal_calls += 1
        truth = TerminalTruth(self.graph["nodes"][current.level.level_id]["truth"])
        return TerminalObservation(SearchExecutionDisposition.AVAILABLE, truth, "fixture terminal truth")

    def transition(self, current, move):
        return TransitionObservation(SearchExecutionDisposition.AVAILABLE, self.foreign_state, None, "fixture foreign-authority child")


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
    assert bridge["runner_path"] == "tools/scrubbots_canonical_bridge_runner.gd"
    assert {fixture["id"] for fixture in data["negative_fixtures"]} == {
        "LF03_WRONG_QUERY_RESULT_BINDING_V1",
        "LF03_WRONG_STATE_KEY_BINDING_V1",
        "LF03_TRANSITION_AUTHORITY_DRIFT_V1",
        "LF03_ENUMERATION_BINDING_V1",
        "LF03_FRONTIER_PEAK_WIDE_SHALLOW_V1",
        "LF03_REPLAY_IDENTITY_TAMPER_V1",
        "LF03_MAX_VISITED_EXECUTION_STOP_V1",
        "LF03_TIMEOUT_NONCANONICAL_V1",
        "LF03_LEVELDATA_STALE_HASH_TAMPER_V1",
    }


def test_negative_fixture_payloads_execute_all_historical_defect_families() -> None:
    wrong_query = negative_payload("LF03_WRONG_QUERY_RESULT_BINDING_V1")
    graph, legal, _transition, initial = build_graph()
    query = LegalMoveQuery(initial, initial.digest(), AUTHORITY, legal.provider_id, legal.provider_version)
    result = legal.query(query)
    with pytest.raises(LegalMoveProviderError):
        replace(result, query_digest=wrong_query["mutation"]["value"]).validate_for_query(query)

    wrong_key = negative_payload("LF03_WRONG_STATE_KEY_BINDING_V1")
    states = {name: make_state(name, {"width": 3, "height": 2, "palette_size": 4}) for name in (wrong_key["state"], wrong_key["result_state"])}
    memo = DeterministicVisitedMemo(AUTHORITY, "lf03-regression-key", "fixture-only-v1")
    assert memo.observe(states[wrong_key["state"]], state_key_result(states[wrong_key["result_state"]], wrong_key["key"])).disposition.value == wrong_key["expected"]["disposition"]

    drift = negative_payload("LF03_TRANSITION_AUTHORITY_DRIFT_V1")
    foreign_authority = SolverStateAuthority(AUTHORITY.repository, drift["foreign_authority_sha"])
    foreign_state = make_state("foreign-child", graph["state_dimensions"], foreign_authority)
    foreign_transition = ForeignAuthorityTransitionProvider(graph, foreign_state)
    drift_result = BaselineSearchEngine(legal, foreign_transition).search(STATES[drift["state"]])
    assert drift_result.execution.value == drift["expected"]["disposition"]
    assert drift_result.verdict is None
    assert foreign_transition.foreign_terminal_calls == 0

    enumeration = negative_payload("LF03_ENUMERATION_BINDING_V1")
    enumeration_result = SolutionCountEngine(legal, foreign_transition).analyze(STATES[enumeration["state"]])
    assert enumeration_result.disposition.value == enumeration["expected"]["disposition"]
    assert enumeration_result.disposition is not SolutionCountDisposition.EXACT
    assert enumeration_result.disposition is not SolutionCountDisposition.LOWER_BOUND
    assert enumeration_result.disposition is not SolutionCountDisposition.INCONCLUSIVE
    assert foreign_transition.foreign_terminal_calls == 0

    frontier = negative_payload("LF03_FRONTIER_PEAK_WIDE_SHALLOW_V1")
    frontier_report = EvidenceSearchEngine(legal, FixtureTransitionProvider(graph)).search(initial)
    assert frontier_report.metrics is not None
    assert frontier_report.metrics.frontier_peak == frontier["expected"]["frontier_peak"]

    replay_tamper = negative_payload("LF03_REPLAY_IDENTITY_TAMPER_V1")
    repro = payload("LF03_REPRODUCTION_MATCH_DIVERGED_V1")
    manifest = ReproductionManifest(
        candidate_source_sha256=hashlib.sha256(repro["candidate_source"].encode()).hexdigest(),
        level_data_source_sha256=hashlib.sha256(repro["level_data_source"].encode()).hexdigest(),
        seed=repro["seed"], normalized_config=repro["normalized_config"], generator_version="lf03-regression-generator-v1", authority=AUTHORITY,
        source_contract_sha256=CANONICAL_PROOF_STATE_SOURCE_SHA256, provider_id="lf03-regression-fake-legal-provider", provider_version="fixture-only-v1", bridge_version="external-godot-runner-v1", search_version="DFS_CANONICAL_PROVIDER_ORDER_V1", memo_provider_id=None, memo_provider_version=None, search_policy=BASELINE_SEARCH_POLICY, budgets=SolverBudgetPolicy(max_visited_states=50, max_depth=8, max_solutions=10), operation="SOLVE", goal="SOLVED", expected_disposition="SOLVED", observed_evidence_digest=hashlib.sha256(repro["evidence_source"].encode()).hexdigest(), observed_path=tuple(repro["path"]),
    )
    bundle = ReproductionBundle.create(manifest)
    tampered = replace(manifest, seed=replay_tamper["tampered_value"])
    tampered_bundle = ReproductionBundle.create(tampered)
    assert ReproductionReplay().replay(bundle, ReplayObservation("SOLVED", manifest.observed_evidence_digest, manifest.observed_path, ReplayExecutionContext.from_manifest(tampered_bundle.manifest))).disposition.value == replay_tamper["expected"]["disposition"]

    max_visited = negative_payload("LF03_MAX_VISITED_EXECUTION_STOP_V1")
    limited = EvidenceSearchEngine(legal, FixtureTransitionProvider(graph), budget_policy=SolverBudgetPolicy(max_visited_states=max_visited["max_visited_states"])).search(initial)
    assert limited.metrics is not None and limited.metrics.visited_count == max_visited["expected"]["visited_count"]
    assert limited.budget_result is not None and limited.budget_result.disposition.value == max_visited["expected"]["disposition"]

    timeout = negative_payload("LF03_TIMEOUT_NONCANONICAL_V1")
    timeout_outcome = wrap_operational_execution(None, timeout_seconds=timeout["before_result"]["timeout_seconds"], timeout_occurred=True)
    assert timeout_outcome.disposition.value == timeout["before_result"]["expected"]["operational_disposition"]
    assert timeout_outcome.canonical_dict() == timeout["before_result"]["expected"]["canonical_result"]
    solved_budget = classify_search_result(BaselineSearchEngine(legal, FixtureTransitionProvider(graph)).search(initial))
    attached = wrap_operational_execution(solved_budget, timeout_seconds=timeout["attached_result"]["timeout_seconds"], timeout_occurred=True)
    assert attached.disposition.value == timeout["attached_result"]["expected"]["operational_disposition"]
    assert (attached.canonical_bytes() == solved_budget.canonical_bytes()) is timeout["attached_result"]["expected"]["canonical_equal"]
    assert (attached.digest() == solved_budget.digest()) is timeout["attached_result"]["expected"]["canonical_equal"]

    stale = negative_payload("LF03_LEVELDATA_STALE_HASH_TAMPER_V1")
    bridge_fixture = load_corpus()["canonical_bridge_fixture"]
    stale_payload = dict(bridge_fixture["payload"])
    stale_payload["level_data_source_base64"] = stale["tampered_source_base64"]
    stale_bytes = json.dumps(stale_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with pytest.raises(CanonicalBridgeError):
        CanonicalBridgeRequest(AUTHORITY, "legal_moves", stale_bytes, hashlib.sha256(stale_bytes).hexdigest(), stale["stale_source_sha256"])


def test_r01_regression_runner_is_committed_and_fixture_only_graphs_stay_nonproduction() -> None:
    runner = Path(__file__).resolve().parents[2] / "tools" / "scrubbots_canonical_bridge_runner.gd"
    assert runner.is_file()
    source = runner.read_text(encoding="utf-8")
    assert "ProofState" in source and "ProofKernel" in source and "SolvabilitySolver" in source
    assert "legal_action_columns" not in (Path(__file__).resolve().parents[2] / "src" / "scrubbots_pixel_factory" / "canonical_bridge.py").read_text(encoding="utf-8")


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
        result = memo.observe(states[item["state"]], state_key_result(states[item["state"]], item["key"]))
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
    from scrubbots_pixel_factory.reproduction import ReplayExecutionContext
    context = ReplayExecutionContext.from_manifest(bundle.manifest)
    assert replay.replay(bundle, ReplayObservation("SOLVED", evidence_digest, tuple(repro["path"]), context)).disposition is ReplayDisposition.MATCH
    assert replay.replay(bundle, ReplayObservation("SOLVED", hashlib.sha256(b"other").hexdigest(), tuple(repro["path"]), context)).disposition is ReplayDisposition.DIVERGED

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


@pytest.mark.skipif(not Path(r"C:\Users\sekip\Desktop\ScrubBots").is_dir() or shutil.which("godot_console.exe") is None, reason="canonical owner repository or Godot executable is unavailable")
def test_real_canonical_bridge_fixture_executes_declarative_operations(tmp_path: Path) -> None:
    bridge_fixture = load_corpus()["canonical_bridge_fixture"]
    checkout = tmp_path / "scrubbots-canonical"
    subprocess.run(["git", "-c", "core.autocrlf=false", "clone", "--local", "--no-hardlinks", r"C:\Users\sekip\Desktop\ScrubBots", str(checkout)], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(checkout), "config", "core.autocrlf", "false"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(checkout), "checkout", "--force", "--detach", AUTHORITY.commit_sha], check=True, capture_output=True, text=True)
    runner = (Path(__file__).resolve().parents[2] / bridge_fixture["runner_path"]).resolve()
    before_status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=checkout, capture_output=True, text=True, check=False).stdout
    before_source = (checkout / "scripts/gameplay/solver/proof_state.gd").read_bytes()
    bridge = CanonicalHeadlessBridge(CanonicalBridgeConfiguration(str(checkout), str(runner)))
    capability = bridge.capability(AUTHORITY)
    assert capability.disposition is CanonicalBridgeDisposition.AVAILABLE
    payload_base = dict(bridge_fixture["payload"])
    for operation in bridge_fixture["operations"]:
        payload = dict(payload_base)
        if operation["operation"] == "apply_placement":
            payload["column"] = operation["column"]
        payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        request = CanonicalBridgeRequest(AUTHORITY, operation["operation"], payload_bytes, hashlib.sha256(payload_bytes).hexdigest(), payload["level_data_source_sha256"])
        first = bridge.invoke(request)
        second = bridge.invoke(request)
        assert first.disposition is CanonicalBridgeDisposition.AVAILABLE
        assert second.canonical_dict() == first.canonical_dict()
        if operation["operation"] == "legal_moves":
            assert first.result == operation["expected"]
    stale = negative_payload("LF03_LEVELDATA_STALE_HASH_TAMPER_V1")
    stale_payload = dict(payload_base)
    stale_payload["level_data_source_base64"] = stale["tampered_source_base64"]
    stale_bytes = json.dumps(stale_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with pytest.raises(CanonicalBridgeError):
        CanonicalBridgeRequest(AUTHORITY, "legal_moves", stale_bytes, hashlib.sha256(stale_bytes).hexdigest(), stale["stale_source_sha256"])
    after_status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=checkout, capture_output=True, text=True, check=False).stdout
    after_source = (checkout / "scripts/gameplay/solver/proof_state.gd").read_bytes()
    assert before_status == after_status
    assert before_source == after_source


def test_regression_fixture_suite_has_no_gameplay_or_wfc_implementation() -> None:
    source = FIXTURE_PATH.read_text(encoding="utf-8").lower()
    assert "legal_action_columns" not in source
    assert '"operation": "apply_placement"' in source
    assert "canonical_key" not in source
    assert "wfc" not in source
