"""One canonical identity for authentic mutation/regeneration comparisons."""

from .core import GenerationRequest
from .m07_services import AttemptBudget, EfficiencyWorkload, MutationCandidate, MutationContractError, TypedChallengeTarget

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
    """Read only the factory-sealed producer binding; ignore payload claims."""
    if not isinstance(parent, MutationCandidate):
        raise MutationContractError("parent generation provenance requires a MutationCandidate")
    provenance = parent.generation_provenance
    if provenance is None or not provenance.is_authentic_sealed or provenance.parent != parent.identity:
        return None
    return provenance.request_digest


__all__ = ["canonical_workload_identity", "parent_generation_request_digest"]
