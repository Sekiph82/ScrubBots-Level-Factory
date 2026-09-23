from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory.baseline_search import (
    BaselineSearchEngine,
    BaselineSearchPolicy,
    SearchExecutionDisposition,
    SearchVerdict,
    TerminalObservation,
    TerminalTruth,
    TransitionObservation,
)
from scrubbots_pixel_factory.compact_solver_state import ACTIVE_BYTE, AuthorityVerificationDisposition, CompactSolverState, LevelIdentity, SolverStateAuthority, SupplyBatch
from scrubbots_pixel_factory.legal_move_provider import LegalMove, LegalMoveResult, ProviderDisposition, ProviderEvidence
from scrubbots_pixel_factory.reproduction import ReproductionManifest
from scrubbots_pixel_factory.search_policy import BASELINE_SEARCH_POLICY
from scrubbots_pixel_factory.solution_analysis import SolutionAnalysisBounds, SolutionCountEngine
from scrubbots_pixel_factory.solver_budget import (
    BudgetExhaustionReason,
    SolverBudgetError,
    SolverBudgetPolicy,
    SolverOutcomeDisposition,
    classify_search_result,
    classify_solution_count_result,
)
from scrubbots_pixel_factory.solver_evidence import EvidenceSearchEngine
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, CANONICAL_PROOF_STATE_SOURCE_SHA256


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA)
STATES: dict[str, CompactSolverState] = {}


def make_state(name: str) -> CompactSolverState:
    return CompactSolverState(
        AUTHORITY,
        LevelIdentity((name.encode().hex() + "a" * 64)[:64], name, 2, 2, 4),
        bytes((ACTIVE_BYTE,) * 4),
        ((SupplyBatch(f"batch-{name}", 1, 1),), (), ()),
        (None,) * 5,
        1,
        3,
        3,
        4,
    )


class LegalFixture:
    provider_id = "fixture-budget-legal"
    provider_version = "fixture-budget-v1"

    def __init__(self, moves: dict[str, tuple[int, ...]]) -> None:
        self.moves = moves

    def query(self, request):
        evidence = ProviderEvidence(
            self.provider_id,
            self.provider_version,
            request.authority,
            ProviderDisposition.AVAILABLE,
            AuthorityVerificationDisposition.VERIFIED,
            AuthorityVerificationDisposition.VERIFIED,
            "CANONICAL_RUNTIME",
            "fixture",
        )
        return LegalMoveResult.from_query(request, ProviderDisposition.AVAILABLE, evidence, tuple(LegalMove(column) for column in self.moves.get(request.state.level.level_id, ())))


class TransitionFixture:
    def __init__(self, terminals: dict[str, TerminalTruth], transitions: dict[tuple[str, int], str]) -> None:
        self.terminals = terminals
        self.transitions = transitions

    def terminal(self, current):
        return TerminalObservation(SearchExecutionDisposition.AVAILABLE, self.terminals.get(current.level.level_id, TerminalTruth.CONTINUE), "fixture terminal")

    def transition(self, current, move):
        destination = self.transitions.get((current.level.level_id, move.column))
        if destination is None:
            return TransitionObservation(SearchExecutionDisposition.ERROR, None, None, "fixture transition missing")
        return TransitionObservation(SearchExecutionDisposition.AVAILABLE, STATES[destination], None, "fixture transition")


def fixture() -> tuple[LegalFixture, TransitionFixture, CompactSolverState]:
    STATES.clear()
    for name in ("root", "goal", "dead", "unknown"):
        STATES[name] = make_state(name)
    return (
        LegalFixture({"root": (0,), "goal": (), "dead": (), "unknown": ()}),
        TransitionFixture(
            {"root": TerminalTruth.CONTINUE, "goal": TerminalTruth.SOLVED, "dead": TerminalTruth.PROVEN_UNSOLVABLE, "unknown": TerminalTruth.UNKNOWN_BOUND},
            {("root", 0): "goal"},
        ),
        STATES["root"],
    )


def test_budget_policy_exact_boundaries_and_malformed_values() -> None:
    policy = SolverBudgetPolicy(max_visited_states=1, max_depth=0, max_solutions=1)
    assert policy.canonical_dict()["max_depth"] == 0
    assert policy.to_baseline_policy() == BaselineSearchPolicy(max_depth=0)
    assert policy.to_solution_bounds() == SolutionAnalysisBounds(max_depth=0, max_states=1, max_solutions=1)
    for kwargs in ({"max_visited_states": 0}, {"max_depth": -1}, {"max_solutions": False}, {"operational_timeout_seconds": 0.0}):
        try:
            SolverBudgetPolicy(**kwargs)
        except SolverBudgetError:
            pass
        else:
            raise AssertionError(f"malformed budget accepted: {kwargs}")


def test_solved_and_proven_no_solution_are_distinct_from_inconclusive() -> None:
    legal, transition, initial = fixture()
    solved = BaselineSearchEngine(legal, transition).search(initial)
    dead = BaselineSearchEngine(legal, transition).search(STATES["dead"])
    assert classify_search_result(solved).disposition is SolverOutcomeDisposition.SOLVED
    assert classify_search_result(dead).disposition is SolverOutcomeDisposition.PROVEN_UNSOLVABLE

    count_dead = SolutionCountEngine(legal, transition).analyze(STATES["dead"])
    assert classify_solution_count_result(count_dead).disposition is SolverOutcomeDisposition.PROVEN_UNSOLVABLE


def test_state_depth_solution_and_unknown_bounds_are_inconclusive() -> None:
    legal, transition, initial = fixture()
    depth_limited = BaselineSearchEngine(legal, transition, BaselineSearchPolicy(max_depth=0)).search(initial)
    state_limited = SolutionCountEngine(legal, transition, SolutionAnalysisBounds(max_states=1)).analyze(initial)
    solution_limited = SolutionCountEngine(legal, transition, SolutionAnalysisBounds(max_solutions=1)).analyze(initial)
    unknown = BaselineSearchEngine(legal, transition).search(STATES["unknown"])

    depth_result = classify_search_result(depth_limited, policy=SolverBudgetPolicy(max_depth=0))
    state_result = classify_solution_count_result(state_limited)
    solution_result = classify_solution_count_result(solution_limited)
    unknown_result = classify_search_result(unknown)

    assert depth_result.disposition is SolverOutcomeDisposition.INCONCLUSIVE
    assert depth_result.exhaustion is BudgetExhaustionReason.MAX_DEPTH
    assert state_result.disposition is SolverOutcomeDisposition.INCONCLUSIVE
    assert state_result.exhaustion is BudgetExhaustionReason.MAX_VISITED_STATES
    assert solution_result.disposition is SolverOutcomeDisposition.INCONCLUSIVE
    assert solution_result.exhaustion is BudgetExhaustionReason.MAX_SOLUTIONS
    assert unknown_result.disposition is SolverOutcomeDisposition.INCONCLUSIVE
    assert unknown_result.exhaustion is BudgetExhaustionReason.UNKNOWN_BOUND


def test_operational_timeout_maps_only_to_inconclusive() -> None:
    legal, transition, initial = fixture()
    search = BaselineSearchEngine(legal, transition).search(initial)
    result = classify_search_result(search, policy=SolverBudgetPolicy(operational_timeout_seconds=0.1), operational_timeout_exhausted=True)
    repeat = classify_search_result(search, policy=SolverBudgetPolicy(operational_timeout_seconds=9.0), operational_timeout_exhausted=True)
    assert result.disposition is SolverOutcomeDisposition.INCONCLUSIVE
    assert result.exhaustion is BudgetExhaustionReason.OPERATIONAL_TIMEOUT
    assert result.operational_timeout_exhausted is True
    assert result.canonical_dict() == repeat.canonical_dict()
    assert "OPERATIONAL_TIMEOUT" not in str(result.canonical_dict())
    assert result.operational_dict() != repeat.operational_dict()


def test_evidence_engine_stops_at_real_visited_state_bound() -> None:
    legal, transition, initial = fixture()
    report = EvidenceSearchEngine(legal, transition, budget_policy=SolverBudgetPolicy(max_visited_states=1)).search(initial)
    assert report.metrics is not None
    assert report.metrics.visited_count == 1
    assert report.budget_result is not None
    assert report.budget_result.disposition is SolverOutcomeDisposition.INCONCLUSIVE
    assert report.budget_result.exhaustion is BudgetExhaustionReason.MAX_VISITED_STATES
    assert report.result.verdict is SearchVerdict.INCONCLUSIVE


def test_budgeted_evidence_and_reproduction_are_deterministic() -> None:
    legal, transition, initial = fixture()
    policy = SolverBudgetPolicy(max_visited_states=20, max_depth=4, max_solutions=5)
    first = EvidenceSearchEngine(legal, transition, budget_policy=policy).search(initial)
    second = EvidenceSearchEngine(legal, transition, budget_policy=policy).search(initial)
    assert first.result.verdict is SearchVerdict.SOLVED
    assert first.budget_result is not None
    assert first.budget_result.disposition is SolverOutcomeDisposition.SOLVED
    assert first.canonical_bytes() == second.canonical_bytes()

    manifest = ReproductionManifest(
        candidate_source_sha256="1" * 64,
        level_data_source_sha256="2" * 64,
        seed=1,
        normalized_config={"lane": "test"},
        generator_version="generator-v1",
        authority=AUTHORITY,
        source_contract_sha256=CANONICAL_PROOF_STATE_SOURCE_SHA256,
        provider_id=legal.provider_id,
        provider_version=legal.provider_version,
        bridge_version="bridge-v1",
        search_version="DFS_CANONICAL_PROVIDER_ORDER_V1",
        memo_provider_id=None,
        memo_provider_version=None,
        search_policy=BASELINE_SEARCH_POLICY,
        budgets=policy,
        operation="SOLVE",
        goal="SOLVED",
        expected_disposition="SOLVED",
    )
    assert manifest.canonical_dict()["budgets"]["schema"] == "scrubbots-solver-budget-policy"


def test_budget_module_has_no_ambiguous_unsolved_or_gameplay_implementation() -> None:
    source = (Path(__file__).resolve().parents[2] / "src" / "scrubbots_pixel_factory" / "solver_budget.py").read_text(encoding="utf-8").lower()
    assert "unsolved" not in source
    assert "legal_action_columns" not in source
    assert "apply_placement" not in source
    assert "canonical_key" not in source
    assert "wfc" not in source
