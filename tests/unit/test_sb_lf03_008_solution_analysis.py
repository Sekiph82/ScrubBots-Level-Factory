from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory.baseline_search import SearchExecutionDisposition, TerminalObservation, TerminalTruth, TransitionObservation
from scrubbots_pixel_factory.compact_solver_state import ACTIVE_BYTE, AuthorityVerificationDisposition, CompactSolverState, LevelIdentity, SolverStateAuthority, SupplyBatch
from scrubbots_pixel_factory.legal_move_provider import LegalMove, LegalMoveResult, ProviderDisposition, ProviderEvidence
from scrubbots_pixel_factory.search_policy import REVERSE_SEARCH_POLICY
from scrubbots_pixel_factory.solution_analysis import EntropyDisposition, MOVE_SEQUENCE_EQUIVALENCE_V1, SolutionAnalysisBounds, SolutionCountDisposition, SolutionCountEngine


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", "1144704e6c3647ed1cf76c610be5bd675585734a")
STATES: dict[str, CompactSolverState] = {}


def make_state(name: str) -> CompactSolverState:
    return CompactSolverState(AUTHORITY, LevelIdentity((name.encode().hex() + "a" * 64)[:64], name, 2, 2, 4), bytes((ACTIVE_BYTE,) * 4), ((SupplyBatch(f"batch-{name}", 1, 1),), (), ()), (None,) * 5, 1, 3, 3, 4)


class LegalFixture:
    provider_id = "fixture-count-legal"
    provider_version = "fixture-count-v1"

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
        destination = self.transitions.get((current.level.level_id, move.column))
        if destination is None:
            return TransitionObservation(SearchExecutionDisposition.ERROR, None, None, "fixture transition missing")
        return TransitionObservation(SearchExecutionDisposition.AVAILABLE, STATES[destination], None, "fixture transition")


def fixture() -> tuple[LegalFixture, TransitionFixture, CompactSolverState]:
    STATES.clear()
    for name in ("root", "goal_a", "goal_b", "dead"):
        STATES[name] = make_state(name)
    return (
        LegalFixture({"root": (0,), "goal_a": (), "goal_b": (), "dead": ()}),
        TransitionFixture({"root": TerminalTruth.CONTINUE, "goal_a": TerminalTruth.SOLVED, "goal_b": TerminalTruth.SOLVED, "dead": TerminalTruth.PROVEN_UNSOLVABLE}, {("root", 0): "goal_a", ("root", 1): "goal_b"}),
        STATES["root"],
    )


def test_exact_one_solution_has_zero_entropy_and_explicit_equivalence() -> None:
    legal, transition, initial = fixture()
    result = SolutionCountEngine(legal, transition).analyze(initial)
    assert result.disposition is SolutionCountDisposition.EXACT
    assert result.solution_count == 1
    assert result.entropy == 0.0
    assert result.entropy_disposition is EntropyDisposition.EXACT
    assert result.equivalence == MOVE_SEQUENCE_EQUIVALENCE_V1


def test_exact_multiple_solutions_have_log2_entropy() -> None:
    legal, transition, initial = fixture()
    legal.moves["root"] = (0, 1)
    result = SolutionCountEngine(legal, transition, search_policy=REVERSE_SEARCH_POLICY).analyze(initial)
    assert result.disposition is SolutionCountDisposition.EXACT
    assert result.solution_count == 2
    assert result.entropy == 1.0
    assert result.entropy_disposition is EntropyDisposition.EXACT
    assert result.solution_sequences == (({"kind": "CANONICAL_COLUMN_FRONT_V1", "column": 1},), ({"kind": "CANONICAL_COLUMN_FRONT_V1", "column": 0},))


def test_exact_zero_solutions_has_explicit_zero_evidence_without_logarithm() -> None:
    legal, transition, initial = fixture()
    transition.terminals["root"] = TerminalTruth.PROVEN_UNSOLVABLE
    result = SolutionCountEngine(legal, transition).analyze(initial)
    assert result.disposition is SolutionCountDisposition.EXACT
    assert result.solution_count == 0
    assert result.entropy is None
    assert result.entropy_disposition is EntropyDisposition.ZERO


def test_solution_cap_is_lower_bound_not_exact() -> None:
    legal, transition, initial = fixture()
    legal.moves["root"] = (0, 1)
    result = SolutionCountEngine(legal, transition, SolutionAnalysisBounds(max_solutions=1)).analyze(initial)
    assert result.disposition is SolutionCountDisposition.LOWER_BOUND
    assert result.solution_count == 1
    assert result.entropy == 0.0
    assert result.entropy_disposition is EntropyDisposition.LOWER_BOUND


def test_state_and_depth_bounds_are_inconclusive() -> None:
    legal, transition, initial = fixture()
    depth_limited = SolutionCountEngine(legal, transition, SolutionAnalysisBounds(max_depth=0)).analyze(initial)
    state_limited = SolutionCountEngine(legal, transition, SolutionAnalysisBounds(max_states=1)).analyze(initial)
    assert depth_limited.disposition is SolutionCountDisposition.INCONCLUSIVE
    assert state_limited.disposition is SolutionCountDisposition.INCONCLUSIVE
    assert depth_limited.solution_count == 0
    assert state_limited.solution_count == 0


def test_repeat_is_deterministic_and_malformed_transition_fails_closed() -> None:
    legal, transition, initial = fixture()
    first = SolutionCountEngine(legal, transition).analyze(initial)
    second = SolutionCountEngine(legal, transition).analyze(initial)
    assert first.canonical_dict() == second.canonical_dict()
    transition.transitions[("root", 0)] = "missing"
    malformed = SolutionCountEngine(legal, transition).analyze(initial)
    assert malformed.disposition is SolutionCountDisposition.ERROR
    assert malformed.solution_count is None


def test_invalid_bounds_and_no_gameplay_or_wfc_implementation() -> None:
    try:
        SolutionAnalysisBounds(max_states=0)
    except ValueError:
        pass
    else:
        raise AssertionError("state cap must be positive")
    source = (Path(__file__).resolve().parents[2] / "src" / "scrubbots_pixel_factory" / "solution_analysis.py").read_text(encoding="utf-8").lower()
    assert "legal_action_columns" not in source
    assert "apply_placement" not in source
    assert "canonical_key" not in source
    assert "difficulty" not in source
    assert "wfc" not in source
