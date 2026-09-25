from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import scrubbots_pixel_factory.mutation_base as mutation_base

from scrubbots_pixel_factory import (
    AuthorityIdentity,
    AuthorityResolutionDisposition,
    CANONICAL_GAMEPLAY_REPOSITORY,
    CANONICAL_M23_CONTRACT_VERSION,
    CANONICAL_M23_SOURCE_PATH,
    CurrentMainAuthorityResolver,
    MutationCandidate,
    MutationContractError,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationRegistry,
    MutationRequest,
    resolve_current_main_authority,
)


HEAD = "281ea38218aaf24ab88c70e998f59b14df9d1c97"
SOURCE = b"current-m23-source"
SOURCE_SHA = hashlib.sha256(SOURCE).hexdigest()


def test_base_substrate_is_usable_with_no_concrete_operators() -> None:
    parent = MutationCandidate.root("empty-registry-parent", {"gameplay": {"value": 1}})
    authority = AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, HEAD, CANONICAL_M23_SOURCE_PATH, CANONICAL_M23_CONTRACT_VERSION, SOURCE_SHA)
    request = MutationRequest.for_candidate(parent, operator_id="NO_OPERATOR", operator_version="1", seed=1, intent=MutationIntent.HARDEN, authority=authority)
    registry = MutationRegistry()
    assert registry.is_empty
    result = MutationEngine(registry).apply(request, parent)
    assert result.disposition is MutationDisposition.INAPPLICABLE
    assert result.child is None


def test_current_main_resolution_binds_head_and_exact_source_blob() -> None:
    resolver = CurrentMainAuthorityResolver(lambda: HEAD, lambda commit, path: SOURCE if (commit, path) == (HEAD, CANONICAL_M23_SOURCE_PATH) else b"")
    resolved = resolve_current_main_authority(resolver, source_path=CANONICAL_M23_SOURCE_PATH, contract_version=CANONICAL_M23_CONTRACT_VERSION, expected_blob_sha256=SOURCE_SHA)
    assert resolved.disposition is AuthorityResolutionDisposition.AVAILABLE
    assert resolved.authority.commit_sha == HEAD
    assert resolved.authority.source_blob_sha256 == SOURCE_SHA


def test_source_blob_drift_and_missing_current_main_fail_closed() -> None:
    drift = CurrentMainAuthorityResolver(lambda: HEAD, lambda _commit, _path: b"different")
    result = resolve_current_main_authority(drift, source_path=CANONICAL_M23_SOURCE_PATH, contract_version=CANONICAL_M23_CONTRACT_VERSION, expected_blob_sha256=SOURCE_SHA)
    assert result.disposition is AuthorityResolutionDisposition.DRIFT
    unavailable = resolve_current_main_authority(None, source_path=CANONICAL_M23_SOURCE_PATH, contract_version=CANONICAL_M23_CONTRACT_VERSION, expected_blob_sha256=SOURCE_SHA)
    assert unavailable.disposition is AuthorityResolutionDisposition.UNAVAILABLE


def test_malformed_resolver_inputs_are_rejected_before_identity_use() -> None:
    with pytest.raises(MutationContractError):
        CurrentMainAuthorityResolver(None, lambda _commit, _path: SOURCE)  # type: ignore[arg-type]


def test_task001_substrate_surface_has_no_future_task_services() -> None:
    assert not hasattr(mutation_base, "evidence")
    assert not hasattr(mutation_base, "select_target")
    assert not hasattr(mutation_base, "run_bounded_mutations")
    assert not hasattr(mutation_base, "OwnerSourceRecord")


def test_base_substrate_is_physical_and_does_not_depend_on_service_monolith() -> None:
    source = Path(mutation_base.__file__).read_text(encoding="utf-8")
    assert "from .m07_services" not in source
    assert "import m07_services" not in source
    for symbol in ("AuthorityIdentity", "MutationCandidate", "MutationRequest", "MutationResult", "MutationRegistry", "MutationEngine"):
        assert getattr(mutation_base, symbol).__module__ == mutation_base.__name__
