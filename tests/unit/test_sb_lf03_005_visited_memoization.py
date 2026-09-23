from __future__ import annotations

from pathlib import Path

import pytest

from scrubbots_pixel_factory.compact_solver_state import ACTIVE_BYTE, AuthorityVerificationDisposition, CompactSolverState, LevelIdentity, SolverStateAuthority, SupplyBatch
from scrubbots_pixel_factory.visited_memoization import (
    DeterministicVisitedMemo,
    MemoDisposition,
    MemoizationContractError,
    StateKeyDisposition,
    StateKeyEvidence,
    StateKeyResult,
    UnavailableCanonicalStateKeyProvider,
)


AUTHORITY_SHA = "1144704e6c3647ed1cf76c610be5bd675585734a"


def authority() -> SolverStateAuthority:
    return SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", AUTHORITY_SHA)


def state(name: str) -> CompactSolverState:
    return CompactSolverState(authority(), LevelIdentity((name.encode().hex() + "a" * 64)[:64], name, 1, 2, 2), bytes((ACTIVE_BYTE, ACTIVE_BYTE)), ((SupplyBatch(f"batch-{name}", 0, 1),), (), ()), (None,) * 5, 1, 3, 3, 1)


def evidence() -> StateKeyEvidence:
    return StateKeyEvidence("fixture-key", "fixture-v1", authority(), StateKeyDisposition.AVAILABLE, AuthorityVerificationDisposition.VERIFIED, AuthorityVerificationDisposition.VERIFIED, "fixture-only semantic key")


def key_result(compact: CompactSolverState, key: str) -> StateKeyResult:
    e = evidence()
    return StateKeyResult(StateKeyDisposition.AVAILABLE, compact.digest(), compact.authority, e.provider_id, e.provider_version, e, key, "fixture key")


def test_duplicate_canonical_fixture_keys_collapse_and_hits_are_separate() -> None:
    first_state = state("one")
    second_state = state("two")
    memo = DeterministicVisitedMemo(authority(), "fixture-key", "fixture-v1")
    first = memo.observe(first_state, key_result(first_state, "semantic-A"))
    duplicate = memo.observe(second_state, key_result(second_state, "semantic-A"))
    distinct = memo.observe(second_state, key_result(second_state, "semantic-B"))
    assert first.disposition is MemoDisposition.FIRST_VISIT
    assert duplicate.disposition is MemoDisposition.MEMO_HIT
    assert distinct.disposition is MemoDisposition.FIRST_VISIT
    assert duplicate.visited_count == 1 and duplicate.memo_hits == 1
    assert distinct.visited_count == 2 and distinct.memo_hits == 1


def test_repeat_identical_observation_counts_and_serialization_are_deterministic() -> None:
    compact = state("repeat")
    def run() -> list[dict[str, object]]:
        memo = DeterministicVisitedMemo(authority(), "fixture-key", "fixture-v1")
        return [memo.observe(compact, key_result(compact, key)).canonical_dict() for key in ("A", "B", "A", "A")]
    assert run() == run()


def test_malformed_key_provider_mismatch_and_factory_digest_substitution_fail_closed() -> None:
    compact = state("malformed")
    with pytest.raises(MemoizationContractError):
        StateKeyResult(StateKeyDisposition.AVAILABLE, compact.digest(), compact.authority, "fixture-key", "fixture-v1", evidence(), "not a safe key", "bad")
    memo = DeterministicVisitedMemo(authority(), "fixture-key", "fixture-v1")
    mismatch_evidence = StateKeyEvidence("other", "fixture-v1", authority(), StateKeyDisposition.AVAILABLE, AuthorityVerificationDisposition.VERIFIED, AuthorityVerificationDisposition.VERIFIED, "mismatch")
    mismatch = StateKeyResult(StateKeyDisposition.AVAILABLE, compact.digest(), compact.authority, "other", "fixture-v1", mismatch_evidence, "key", "mismatch")
    assert memo.observe(compact, mismatch).disposition is MemoDisposition.ERROR
    substituted = memo.observe(compact, key_result(compact, compact.digest()))
    assert substituted.disposition is MemoDisposition.ERROR
    assert "digest" in substituted.reason


def test_unavailable_key_authority_does_not_fabricate_a_structural_key() -> None:
    compact = state("unavailable")
    result = UnavailableCanonicalStateKeyProvider().key(compact)
    assert result.disposition is StateKeyDisposition.UNAVAILABLE
    assert result.opaque_key is None
    memo = DeterministicVisitedMemo(authority(), result.provider_id, result.provider_version)
    assert memo.observe(compact, result).disposition is MemoDisposition.UNAVAILABLE


def test_memo_does_not_mutate_compact_state_and_factory_digest_is_not_key_authority() -> None:
    compact = state("immutable")
    before = compact.digest()
    memo = DeterministicVisitedMemo(authority(), "fixture-key", "fixture-v1")
    memo.observe(compact, key_result(compact, "semantic-immutable"))
    assert compact.digest() == before
    source = (Path(__file__).resolve().parents[2] / "src" / "scrubbots_pixel_factory" / "visited_memoization.py").read_text(encoding="utf-8")
    assert "canonical_key()" not in source
    assert "active_mask" not in source
    assert "wfc" not in source.lower()


def test_bound_observation_rejects_key_for_another_state_without_count_mutation() -> None:
    first_state = state("bound-a")
    second_state = state("bound-b")
    memo = DeterministicVisitedMemo(authority(), "fixture-key", "fixture-v1")
    result = memo.observe(first_state, key_result(second_state, "semantic-b"))
    assert result.disposition is MemoDisposition.ERROR
    assert result.visited_count == 0
    assert result.memo_hits == 0


def test_bare_key_result_observation_is_rejected() -> None:
    compact = state("bare")
    memo = DeterministicVisitedMemo(authority(), "fixture-key", "fixture-v1")
    with pytest.raises(TypeError):
        memo.observe(key_result(compact, "unbound"))  # type: ignore[call-arg]
