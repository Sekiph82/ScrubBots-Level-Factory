"""SB-LF07-001 immutable mutation substrate API.

This module is the dependency boundary for the base mutation contract.  Later
M07 services are intentionally exposed through :mod:`m07_services`; callers
writing substrate tests import this module and cannot rely on policy services.
The compatibility implementation remains shared during the forward migration
so existing accepted contracts retain their exact digest behavior.
"""

from .m07_services import (
    AuthorityIdentity,
    AuthorityResolution,
    AuthorityResolutionDisposition,
    CANONICAL_GAMEPLAY_REPOSITORY,
    CANONICAL_GAMEPLAY_SHA,
    CandidateIdentity,
    CurrentMainAuthorityResolver,
    LineageEdge,
    MutationCandidate,
    MutationContractError,
    MutationDisposition,
    MutationEngine,
    MutationIntent,
    MutationOperator,
    MutationRegistry,
    MutationRequest,
    MutationResult,
    resolve_current_main_authority,
)

__all__ = [
    "AuthorityIdentity", "AuthorityResolution", "AuthorityResolutionDisposition",
    "CANONICAL_GAMEPLAY_REPOSITORY", "CANONICAL_GAMEPLAY_SHA", "CandidateIdentity",
    "CurrentMainAuthorityResolver", "LineageEdge", "MutationCandidate",
    "MutationContractError", "MutationDisposition", "MutationEngine", "MutationIntent",
    "MutationOperator", "MutationRegistry", "MutationRequest", "MutationResult",
    "resolve_current_main_authority",
]
