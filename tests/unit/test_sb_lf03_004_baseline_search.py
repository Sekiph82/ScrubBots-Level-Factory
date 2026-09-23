from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from scrubbots_pixel_factory.compact_solver_state import (
    ACTIVE_BYTE,
    CompactSolverState,
    LevelIdentity,
    SolverStateAuthority,
    SupplyBatch,
)
from scrubbots_pixel_factory.legal_move_provider import (
    LegalMove,
    LegalMoveResult,
    LegalMoveQuery,
    ProviderDisposition,
    ProviderEvidence,
)
from scrubbots_pixel_factory.compact_solver_state import AuthorityVerificationDisposition
from scrubbots_pixel_factory.baseline_search import (
    BaselineSearchEngine,
    BaselineSearchPolicy,
    SearchExecutionDisposition,
    SearchVerdict,
    TerminalObservation,
    TerminalTruth,
    TransitionObservation,
)


AUTHORITY_SHA = "1144704e6c3647ed1cf76c610be5bd675585734a"


def authority() -> SolverStateAuthority:
    return SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", AUTHORITY_SHA)


def state(name: str) -> CompactSolverState:
    return CompactSolverState(
        authority=authority(),
        level=LevelIdentity((name.encode().hex() + "a" * 64)[:64], name, 2, 2, 4),
        active_mask=bytes((ACTIVE_BYTE,) * 4),
        supply=((SupplyBatch(f"batch-{name}", 1, 1),), (), ()),
        slots=(None,) * 5,
        next_seq=1,
        column_count=3,
        preview_depth=3,
        palette_size=4,
    )


class FixtureLegalProvider:
    provider_id = "fixture-search-legal-provider"
    provider_version = "fixture-search-v1"

    def __init__(self, moves: dict[str, tuple[int, ...]]) -> None:
        self._moves = moves

    def query(self, request):
        from scrubbots_pixel_factory.legal_move_provider import LegalMoveQuery

        assert isinstance(request, LegalMoveQuery)
        evidence = ProviderEvidence(
            self.provider_id,
            self.provider_version,
            request.authority,
            ProviderDisposition.AVAILABLE,
            AuthorityVerificationDisposition.VERIFIED,
            AuthorityVerificationDisposition.VERIFIED,
            "CANONICAL_RUNTIME",
            "fixture-only provider",
        )
        moves = tuple(LegalMove(column) for column in self._moves.get(request.state.level.level_id, ()))
        return LegalMoveResult.from_query(request, ProviderDisposition.AVAILABLE, evidence, moves)


class FixtureTransitionProvider:
    def __init__(self, terminals: dict[str, TerminalTruth], transitions: dict[tuple[str, int], str | None]) -> None:
        self.terminals = terminals
        self.transitions = transitions
        self.calls: list[tuple[str, int]] = []

    def terminal(self, state: CompactSolverState) -> TerminalObservation:
        return TerminalObservation(SearchExecutionDisposition.AVAILABLE, self.terminals.get(state.level.level_id, TerminalTruth.CONTINUE), "fixture terminal truth")

    def transition(self, state: CompactSolverState, move: LegalMove) -> TransitionObservation:
        self.calls.append((state.level.level_id, move.column))
        child_name = self.transitions.get((state.level.level_id, move.column))
        if child_name is None:
            return TransitionObservation(SearchExecutionDisposition.ERROR, None, None, "fixture transition missing")
        return TransitionObservation(SearchExecutionDisposition.AVAILABLE, state_by_name[child_name], None, "fixture transition")


state_by_name: dict[str, CompactSolverState] = {}


def build_fixture() -> tuple[FixtureLegalProvider, FixtureTransitionProvider, CompactSolverState]:
    state_by_name.clear()
    for name in ("root", "dead", "middle", "goal", "zero"):
        state_by_name[name] = state(name)
    legal = FixtureLegalProvider({"root": (0, 1), "dead": (0,), "middle": (2,), "zero": ()})
    transitions = FixtureTransitionProvider(
        {"root": TerminalTruth.CONTINUE, "dead": TerminalTruth.PROVEN_UNSOLVABLE, "middle": TerminalTruth.CONTINUE, "goal": TerminalTruth.SOLVED, "zero": TerminalTruth.CONTINUE},
        {("root", 0): "dead", ("root", 1): "middle", ("middle", 2): "goal"},
    )
    return legal, transitions, state_by_name["root"]


def test_repeat_search_is_deterministic_and_finds_alternate_success() -> None:
    legal, transitions, initial = build_fixture()
    first = BaselineSearchEngine(legal, transitions).search(initial)
    second = BaselineSearchEngine(legal, transitions).search(initial)
    assert first.execution is SearchExecutionDisposition.AVAILABLE
    assert first.verdict is SearchVerdict.SOLVED
    assert [move.column for move in first.path] == [1, 2]
    assert first.canonical_dict() == second.canonical_dict()


def test_zero_move_terminal_behavior_is_provider_defined_not_guessed() -> None:
    legal, transitions, _ = build_fixture()
    result = BaselineSearchEngine(legal, transitions).search(state_by_name["zero"])
    assert result.execution is SearchExecutionDisposition.AVAILABLE
    assert result.verdict is SearchVerdict.INCONCLUSIVE
    assert "zero legal moves" in result.reason


def test_proven_unsolvable_requires_provider_terminal_truth() -> None:
    legal, transitions, _ = build_fixture()
    result = BaselineSearchEngine(legal, transitions).search(state_by_name["dead"])
    assert result.verdict is SearchVerdict.PROVEN_UNSOLVABLE


def test_depth_bound_is_inconclusive_and_inputs_remain_unchanged() -> None:
    legal, transitions, initial = build_fixture()
    before = initial.digest()
    result = BaselineSearchEngine(legal, transitions, BaselineSearchPolicy(max_depth=0)).search(initial)
    assert result.verdict is SearchVerdict.INCONCLUSIVE
    assert initial.digest() == before


def test_unavailable_and_provider_error_fail_closed() -> None:
    class UnavailableLegal(FixtureLegalProvider):
        def query(self, request):
            evidence = ProviderEvidence(self.provider_id, self.provider_version, request.authority, ProviderDisposition.UNAVAILABLE, AuthorityVerificationDisposition.UNAVAILABLE, AuthorityVerificationDisposition.UNAVAILABLE, "FIXTURE_ONLY", "unavailable")
            return LegalMoveResult.from_query(request, ProviderDisposition.UNAVAILABLE, evidence)

    _, transitions, initial = build_fixture()
    result = BaselineSearchEngine(UnavailableLegal({}), transitions).search(initial)
    assert result.execution is SearchExecutionDisposition.UNAVAILABLE
    assert result.verdict is None


def test_wrong_query_result_and_child_authority_fail_closed() -> None:
    legal, transitions, initial = build_fixture()

    class WrongQueryLegal(FixtureLegalProvider):
        def query(self, request):
            other = LegalMoveQuery(state_by_name["dead"], state_by_name["dead"].digest(), request.authority, self.provider_id, self.provider_version)
            evidence = ProviderEvidence(self.provider_id, self.provider_version, request.authority, ProviderDisposition.AVAILABLE, AuthorityVerificationDisposition.VERIFIED, AuthorityVerificationDisposition.VERIFIED, "CANONICAL_RUNTIME", "fixture")
            return LegalMoveResult.from_query(other, ProviderDisposition.AVAILABLE, evidence, (LegalMove(0),))

    wrong = BaselineSearchEngine(WrongQueryLegal({}), transitions).search(initial)
    assert wrong.execution is SearchExecutionDisposition.ERROR
    transitions_bad = FixtureTransitionProvider({"root": TerminalTruth.CONTINUE}, {("root", 0): "dead"})
    bad_child = state("foreign")
    foreign_authority = object.__new__(SolverStateAuthority)
    object.__setattr__(foreign_authority, "repository", "https://github.com/Sekiph82/Scrubbots")
    object.__setattr__(foreign_authority, "commit_sha", "0" * 40)
    object.__setattr__(foreign_authority, "proof_state_source_path", "scripts/gameplay/solver/proof_state.gd")
    object.__setattr__(foreign_authority, "authority_version", 1)
    object.__setattr__(bad_child, "authority", foreign_authority)
    original = state_by_name.get("dead")
    state_by_name["dead"] = bad_child
    try:
        result = BaselineSearchEngine(legal, transitions_bad).search(initial)
        assert result.execution is SearchExecutionDisposition.ERROR
    finally:
        if original is not None:
            state_by_name["dead"] = original


def test_search_module_does_not_implement_gameplay_rules() -> None:
    source = (Path(__file__).resolve().parents[2] / "src" / "scrubbots_pixel_factory" / "baseline_search.py").read_text(encoding="utf-8")
    assert "legal_action_columns" not in source
    assert "apply_placement" not in source
    assert "canonical_key" not in source
    assert "wfc" not in source.lower()
