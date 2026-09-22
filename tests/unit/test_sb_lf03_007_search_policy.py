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
from scrubbots_pixel_factory.search_policy import BASELINE_SEARCH_POLICY, NONE_PRUNING_V1, MoveOrderingPolicy, PruningPolicy, REVERSE_PROVIDER_ORDER_V1, REVERSE_SEARCH_POLICY, SearchPolicyError
from scrubbots_pixel_factory.solver_evidence import EvidenceSearchEngine


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", "1144704e6c3647ed1cf76c610be5bd675585734a")
STATES: dict[str, CompactSolverState] = {}


def make_state(name: str) -> CompactSolverState:
    return CompactSolverState(AUTHORITY, LevelIdentity((name.encode().hex() + "a" * 64)[:64], name, 2, 2, 4), bytes((ACTIVE_BYTE,) * 4), ((SupplyBatch(f"batch-{name}", 1, 1),), (), ()), (None,) * 5, 1, 3, 3, 4)


class LegalFixture:
    provider_id = "fixture-policy-legal"
    provider_version = "fixture-policy-v1"

    def __init__(self, moves: dict[str, tuple[int, ...]]) -> None:
        self.moves = moves

    def query(self, request):
        evidence = ProviderEvidence(self.provider_id, self.provider_version, request.authority, ProviderDisposition.AVAILABLE, AuthorityVerificationDisposition.VERIFIED, AuthorityVerificationDisposition.VERIFIED, "CANONICAL_RUNTIME", "fixture")
        return LegalMoveResult.from_query(request, ProviderDisposition.AVAILABLE, evidence, tuple(LegalMove(column) for column in self.moves.get(request.state.level.level_id, ())))


class TransitionFixture:
    def __init__(self, terminals: dict[str, TerminalTruth], transitions: dict[tuple[str, int], str]) -> None:
        self.terminals = terminals
        self.transitions = transitions

    def terminal(self, current):
        return TerminalObservation(SearchExecutionDisposition.AVAILABLE, self.terminals.get(current.level.level_id, TerminalTruth.CONTINUE), "fixture terminal")

    def transition(self, current, move):
        return TransitionObservation(SearchExecutionDisposition.AVAILABLE, STATES[self.transitions[(current.level.level_id, move.column)]], None, "fixture transition")


def fixture() -> tuple[LegalFixture, TransitionFixture, CompactSolverState]:
    STATES.clear()
    for name in ("root", "dead", "middle", "goal"):
        STATES[name] = make_state(name)
    legal = LegalFixture({"root": (0, 1), "dead": (), "middle": (2,), "goal": ()})
    transition = TransitionFixture(
        {"root": TerminalTruth.CONTINUE, "dead": TerminalTruth.PROVEN_UNSOLVABLE, "middle": TerminalTruth.CONTINUE, "goal": TerminalTruth.SOLVED},
        {("root", 0): "dead", ("root", 1): "middle", ("middle", 2): "goal"},
    )
    return legal, transition, STATES["root"]


def test_baseline_and_reordered_policy_preserve_exhaustive_solved_truth() -> None:
    legal, transition, initial = fixture()
    baseline = BaselineSearchEngine(legal, transition, search_policy=BASELINE_SEARCH_POLICY).search(initial)
    reordered = BaselineSearchEngine(legal, transition, search_policy=REVERSE_SEARCH_POLICY).search(initial)
    assert baseline.verdict is SearchVerdict.SOLVED
    assert reordered.verdict is SearchVerdict.SOLVED
    assert [move.column for move in baseline.path] == [1, 2]
    assert [move.column for move in reordered.path] == [1, 2]


def test_reordered_policy_preserves_exhaustive_unsolvable_truth() -> None:
    legal, transition, initial = fixture()
    transition.terminals.update({"middle": TerminalTruth.PROVEN_UNSOLVABLE})
    transition.transitions.update({("middle", 2): "dead"})
    baseline = BaselineSearchEngine(legal, transition, search_policy=BASELINE_SEARCH_POLICY).search(initial)
    reordered = BaselineSearchEngine(legal, transition, search_policy=REVERSE_SEARCH_POLICY).search(initial)
    assert baseline.verdict is SearchVerdict.PROVEN_UNSOLVABLE
    assert reordered.verdict is SearchVerdict.PROVEN_UNSOLVABLE


def test_policy_is_recorded_and_bounded_outcome_stays_inconclusive() -> None:
    legal, transition, initial = fixture()
    report = EvidenceSearchEngine(legal, transition, BaselineSearchPolicy(max_depth=0), search_policy=REVERSE_SEARCH_POLICY).search(initial)
    assert report.result.verdict is SearchVerdict.INCONCLUSIVE
    assert report.search_policy.ordering.version == REVERSE_PROVIDER_ORDER_V1
    assert report.search_policy.pruning.version == NONE_PRUNING_V1
    assert report.canonical_dict()["search_policy"] == REVERSE_SEARCH_POLICY.canonical_dict()


def test_none_pruning_is_explicit_for_repeated_equivalent_state_fixture() -> None:
    legal, transition, initial = fixture()
    legal.moves["root"] = (0, 1)
    transition.transitions.update({("root", 0): "dead", ("root", 1): "dead"})
    report = EvidenceSearchEngine(legal, transition, search_policy=BASELINE_SEARCH_POLICY).search(initial)
    assert report.result.verdict is SearchVerdict.PROVEN_UNSOLVABLE
    assert report.search_policy.pruning.canonical_dict()["policy"] == NONE_PRUNING_V1
    assert report.metrics is not None and report.metrics.visited_count == 3


def test_policy_values_are_immutable_and_reject_unproven_pruning() -> None:
    ordering = MoveOrderingPolicy()
    try:
        ordering.version = REVERSE_PROVIDER_ORDER_V1  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("ordering policy must be immutable")
    try:
        PruningPolicy("HEURISTIC_V1")
    except SearchPolicyError:
        pass
    else:
        raise AssertionError("unproven pruning must be rejected")


def test_policy_module_has_no_gameplay_or_wfc_implementation() -> None:
    source = (Path(__file__).resolve().parents[2] / "src" / "scrubbots_pixel_factory" / "search_policy.py").read_text(encoding="utf-8").lower()
    assert "legal_action_columns" not in source
    assert "apply_placement" not in source
    assert "canonical_key" not in source
    assert "wfc" not in source
