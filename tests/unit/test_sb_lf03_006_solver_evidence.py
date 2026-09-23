from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory.compact_solver_state import ACTIVE_BYTE, AuthorityVerificationDisposition, CompactSolverState, LevelIdentity, SolverStateAuthority, SupplyBatch
from scrubbots_pixel_factory.legal_move_provider import CanonicalLegalMoveProvider, LegalMove, LegalMoveResult, ProviderDisposition, ProviderEvidence
from scrubbots_pixel_factory.baseline_search import SearchExecutionDisposition, SearchVerdict, TerminalObservation, TerminalTruth, TransitionObservation
from scrubbots_pixel_factory.solver_evidence import EvidenceSearchEngine
from scrubbots_pixel_factory.visited_memoization import StateKeyDisposition, StateKeyEvidence, StateKeyResult


AUTHORITY_SHA = "1144704e6c3647ed1cf76c610be5bd675585734a"
authority = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", AUTHORITY_SHA)
states: dict[str, CompactSolverState] = {}


def make_state(name: str) -> CompactSolverState:
    return CompactSolverState(authority, LevelIdentity((name.encode().hex() + "a" * 64)[:64], name, 2, 2, 4), bytes((ACTIVE_BYTE,) * 4), ((SupplyBatch(f"batch-{name}", 1, 1),), (), ()), (None,) * 5, 1, 3, 3, 4)


class LegalFixture:
    provider_id = "fixture-evidence-legal"
    provider_version = "fixture-evidence-v1"

    def query(self, request):
        evidence = ProviderEvidence(self.provider_id, self.provider_version, request.authority, ProviderDisposition.AVAILABLE, AuthorityVerificationDisposition.VERIFIED, AuthorityVerificationDisposition.VERIFIED, "CANONICAL_RUNTIME", "fixture")
        columns = {"root": (0, 1), "dead": (0,), "middle": (2,), "goal": ()}.get(request.state.level.level_id, ())
        return LegalMoveResult.from_query(request, ProviderDisposition.AVAILABLE, evidence, tuple(LegalMove(c) for c in columns))


class TransitionFixture:
    def terminal(self, current):
        truth = {"root": TerminalTruth.CONTINUE, "dead": TerminalTruth.PROVEN_UNSOLVABLE, "middle": TerminalTruth.CONTINUE, "goal": TerminalTruth.SOLVED}.get(current.level.level_id, TerminalTruth.UNKNOWN_BOUND)
        return TerminalObservation(SearchExecutionDisposition.AVAILABLE, truth, "fixture terminal")

    def transition(self, current, move):
        destination = {("root", 0): "dead", ("root", 1): "middle", ("middle", 2): "goal"}[(current.level.level_id, move.column)]
        return TransitionObservation(SearchExecutionDisposition.AVAILABLE, states[destination], None, "fixture transition")


class KeyFixture:
    provider_id = "fixture-evidence-key"
    provider_version = "fixture-key-v1"

    def key(self, current):
        evidence = StateKeyEvidence(self.provider_id, self.provider_version, current.authority, StateKeyDisposition.AVAILABLE, AuthorityVerificationDisposition.VERIFIED, AuthorityVerificationDisposition.VERIFIED, "fixture key")
        return StateKeyResult(StateKeyDisposition.AVAILABLE, current.digest(), current.authority, self.provider_id, self.provider_version, evidence, f"semantic:{current.level.level_id}", "fixture key")


def fixture() -> CompactSolverState:
    states.clear()
    for name in ("root", "dead", "middle", "goal"):
        states[name] = make_state(name)
    return states["root"]


def test_repeat_evidence_is_deterministic_and_timing_is_not_canonical() -> None:
    initial = fixture()
    first = EvidenceSearchEngine(LegalFixture(), TransitionFixture(), key_provider=KeyFixture()).search(initial)
    second = EvidenceSearchEngine(LegalFixture(), TransitionFixture(), key_provider=KeyFixture()).search(initial)
    assert first.execution is SearchExecutionDisposition.AVAILABLE
    assert first.result.verdict is SearchVerdict.SOLVED
    assert first.metrics is not None
    assert first.metrics.path == ({"kind": "CANONICAL_COLUMN_FRONT_V1", "column": 1}, {"kind": "CANONICAL_COLUMN_FRONT_V1", "column": 2})
    assert first.metrics.dead_end_count == 1
    assert first.metrics.branch_counts == (2, 1)
    assert first.metrics.visited_count == 4
    assert first.metrics.memo_hits == 0
    assert first.metrics.frontier_peak >= 2
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.telemetry_dict()["canonical"] is False
    assert "elapsed_seconds" not in first.canonical_dict()


def test_unavailable_search_has_no_fabricated_zero_metrics() -> None:
    initial = fixture()
    provider = CanonicalLegalMoveProvider()
    report = EvidenceSearchEngine(provider, TransitionFixture()).search(initial)
    assert report.execution is SearchExecutionDisposition.UNAVAILABLE
    assert report.metrics is None
    assert report.result.verdict is None


def test_evidence_is_bounded_and_does_not_mutate_input() -> None:
    initial = fixture()
    before = initial.digest()
    report = EvidenceSearchEngine(LegalFixture(), TransitionFixture()).search(initial)
    assert report.metrics is not None
    assert len(report.metrics.state_references) <= 256
    assert initial.digest() == before


def test_evidence_module_has_no_gameplay_or_wfc_implementation() -> None:
    source = (Path(__file__).resolve().parents[2] / "src" / "scrubbots_pixel_factory" / "solver_evidence.py").read_text(encoding="utf-8").lower()
    assert "legal_action_columns" not in source
    assert "apply_placement" not in source
    assert "canonical_key" not in source
    assert "wfc" not in source


def test_frontier_peak_is_pending_frontier_not_depth_plus_one() -> None:
    initial = fixture()

    class WideLegal(LegalFixture):
        def query(self, request):
            result = super().query(request)
            if request.state.level.level_id == "root":
                return LegalMoveResult.from_query(request, result.disposition, result.capability, (LegalMove(0), LegalMove(1), LegalMove(2)))
            return result

    class WideTransition(TransitionFixture):
        def transition(self, current, move):
            if current.level.level_id == "root":
                return TransitionObservation(SearchExecutionDisposition.AVAILABLE, states["dead"], None, "wide fixture")
            return super().transition(current, move)

    report = EvidenceSearchEngine(WideLegal(), WideTransition()).search(initial)
    assert report.metrics is not None
    assert report.metrics.frontier_peak == 3
    assert report.metrics.maximum_depth == 1
