from __future__ import annotations

import ast
from pathlib import Path

import pytest

from scrubbots_pixel_factory.compact_solver_state import (
    ACTIVE_BYTE,
    CLEARED_BYTE,
    CompactSolverState,
    LevelIdentity,
    SolverStateAuthority,
)
from scrubbots_pixel_factory.legal_move_provider import (
    CANONICAL_PROVIDER_ID,
    CANONICAL_PROVIDER_VERSION,
    LEGAL_MOVE_KIND,
    CanonicalLegalMoveProvider,
    LegalMove,
    LegalMoveProviderError,
    LegalMoveQuery,
    LegalMoveResult,
    ProviderDisposition,
    ProviderEvidence,
)
from scrubbots_pixel_factory.compact_solver_state import AuthorityVerificationDisposition


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "scrubbots_pixel_factory" / "legal_move_provider.py"
AUTHORITY_SHA = "1144704e6c3647ed1cf76c610be5bd675585734a"


def authority() -> SolverStateAuthority:
    return SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", AUTHORITY_SHA)


def state() -> CompactSolverState:
    from scrubbots_pixel_factory.compact_solver_state import SupplyBatch

    return CompactSolverState(
        authority=authority(),
        level=LevelIdentity("a" * 64, "provider-level", 2, 2, 4),
        active_mask=bytes((ACTIVE_BYTE, CLEARED_BYTE, ACTIVE_BYTE, CLEARED_BYTE)),
        supply=((SupplyBatch("batch-a", 1, 1),), (), ()),
        slots=(None,) * 5,
        next_seq=1,
        column_count=3,
        preview_depth=3,
        palette_size=4,
    )


def capability(provider_id: str = "fixture-legal-moves-v1", provider_version: str = "fixture-v1") -> ProviderEvidence:
    return ProviderEvidence(
        provider_id,
        provider_version,
        authority(),
        ProviderDisposition.AVAILABLE,
        AuthorityVerificationDisposition.VERIFIED,
        AuthorityVerificationDisposition.VERIFIED,
        "CANONICAL_RUNTIME",
        "fixture provider is explicitly test-only",
    )


def query(provider_id: str = "fixture-legal-moves-v1", provider_version: str = "fixture-v1") -> LegalMoveQuery:
    compact = state()
    return LegalMoveQuery(compact, compact.digest(), compact.authority, provider_id, provider_version)


def test_request_result_and_move_are_versioned_and_bound() -> None:
    request = query()
    result = LegalMoveResult.from_query(request, ProviderDisposition.AVAILABLE, capability(), (LegalMove(0), LegalMove(2)))
    assert result.moves[0].kind == LEGAL_MOVE_KIND
    assert result.state_digest == request.state_digest
    assert result.query_digest == request.digest()
    assert result.authority == request.authority
    assert result.canonical_bytes() == LegalMoveResult.from_query(request, ProviderDisposition.AVAILABLE, capability(), (LegalMove(0), LegalMove(2))).canonical_bytes()


def test_zero_available_moves_are_valid_without_a_solver_verdict() -> None:
    result = LegalMoveResult.from_query(query(), ProviderDisposition.AVAILABLE, capability(), ())
    assert result.disposition is ProviderDisposition.AVAILABLE
    assert result.moves == ()
    assert "solv" not in result.canonical_dict()


def test_validation_rejects_duplicate_unsorted_out_of_range_and_malformed_moves() -> None:
    request = query()
    with pytest.raises(LegalMoveProviderError):
        LegalMoveResult.from_query(request, ProviderDisposition.AVAILABLE, capability(), (LegalMove(1), LegalMove(1)))
    with pytest.raises(LegalMoveProviderError):
        LegalMoveResult.from_query(request, ProviderDisposition.AVAILABLE, capability(), (LegalMove(2), LegalMove(0)))
    with pytest.raises(LegalMoveProviderError):
        LegalMoveResult.from_query(request, ProviderDisposition.AVAILABLE, capability(), (LegalMove(3),))
    with pytest.raises(LegalMoveProviderError):
        LegalMove(True)  # type: ignore[arg-type]
    with pytest.raises(LegalMoveProviderError):
        LegalMove(0, "OTHER_KIND")


def test_unavailable_and_error_results_cannot_fabricate_moves() -> None:
    request = query()
    unavailable = LegalMoveResult.from_query(request, ProviderDisposition.UNAVAILABLE, ProviderEvidence("fixture-legal-moves-v1", "fixture-v1", authority(), ProviderDisposition.UNAVAILABLE, AuthorityVerificationDisposition.UNAVAILABLE, AuthorityVerificationDisposition.UNAVAILABLE, "FIXTURE_ONLY", "not production"))
    assert unavailable.moves == ()
    with pytest.raises(LegalMoveProviderError):
        LegalMoveResult.from_query(request, ProviderDisposition.ERROR, capability(), (LegalMove(0),))


def test_canonical_provider_is_truthfully_unavailable_without_execution_and_does_not_derive_moves() -> None:
    compact = state()
    provider = CanonicalLegalMoveProvider()
    request = LegalMoveQuery(compact, compact.digest(), compact.authority, CANONICAL_PROVIDER_ID, CANONICAL_PROVIDER_VERSION)
    result = provider.query(request)
    assert result.disposition is ProviderDisposition.UNAVAILABLE
    assert result.moves == ()
    assert result.capability.execution_mode == "NOT_CONFIGURED"
    assert result.capability.authority_verification is AuthorityVerificationDisposition.UNAVAILABLE


def test_query_rejects_state_digest_or_authority_mismatch_and_does_not_mutate_state() -> None:
    compact = state()
    digest_before = compact.digest()
    with pytest.raises(LegalMoveProviderError):
        LegalMoveQuery(compact, "0" * 64, compact.authority, "fixture", "v1")
    other = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", "0" * 40)
    with pytest.raises(LegalMoveProviderError):
        LegalMoveQuery(compact, compact.digest(), other, "fixture", "v1")
    assert compact.digest() == digest_before


def test_provider_module_has_no_python_legal_move_derivation_or_gameplay_transition_surface() -> None:
    source = SOURCE.read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    methods = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "legal_action_columns" not in source
    assert "apply_placement" not in source
    assert "wfc" not in source
    assert "canonical_key" not in methods
    assert "search" not in methods
