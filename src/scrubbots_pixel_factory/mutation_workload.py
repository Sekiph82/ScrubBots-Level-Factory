"""One canonical identity for authentic mutation/regeneration comparisons."""

from .core import GenerationRequest
from .m07_services import AttemptBudget, EfficiencyWorkload, MutationContractError, TypedChallengeTarget


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


__all__ = ["canonical_workload_identity"]
