"""One canonical identity for authentic mutation/regeneration comparisons."""

from collections.abc import Mapping
import re

from .core import GenerationRequest
from .m07_services import AttemptBudget, EfficiencyWorkload, MutationCandidate, MutationContractError, TypedChallengeTarget


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def canonical_workload_identity(request: GenerationRequest, target: TypedChallengeTarget, budget: AttemptBudget) -> EfficiencyWorkload:
    """Bind the exact request, target policy, and finite budget into one identity."""
    if not isinstance(request, GenerationRequest):
        raise MutationContractError("canonical workload identity requires an exact GenerationRequest")
    if not isinstance(target, TypedChallengeTarget) or not target.is_authentic_sealed:
        raise MutationContractError("canonical workload identity requires a sealed authentic target")
    if not isinstance(budget, AttemptBudget):
        raise MutationContractError("canonical workload identity requires an AttemptBudget")
    return EfficiencyWorkload(
        target.digest(),
        request.digest(),
        target.policy_digest,
        budget.digest(),
        "AVAILABLE",
    )


def parent_generation_request_digest(parent: MutationCandidate) -> str | None:
    """Read only an explicit, canonical parent generation binding.

    Raw generation configuration is deliberately not hashed here. A caller
    must provide the accepted digest as provenance; otherwise comparison stays
    unavailable rather than inferring authority from mutable payload data.
    """
    if not isinstance(parent, MutationCandidate):
        raise MutationContractError("parent generation provenance requires a MutationCandidate")
    direct = parent.payload.get("generation_request_digest")
    if type(direct) is str and _SHA256.fullmatch(direct) is not None:
        return direct
    provenance = parent.payload.get("generation_provenance")
    if isinstance(provenance, Mapping):
        nested = provenance.get("generation_request_digest")
        if type(nested) is str and _SHA256.fullmatch(nested) is not None:
            return nested
    return None


__all__ = ["canonical_workload_identity", "parent_generation_request_digest"]
