"""SB-LF07-007 authentic bounded runner service."""

from collections.abc import Callable

from .mutation_base import MutationCandidate, MutationDisposition, MutationEngine, MutationRequest
from .mutation_evidence import provenance_from_authentic_validation
from .m07_services import AttemptBudget, AttemptDisposition, AttemptProvenance, AttemptRecord, AttemptReport, MutationProvenance, MutationResult, TypedChallengeTarget
from .mutation_targeting import AuthenticTargetCandidate, select_authentic_target


def run_authentic_bounded_mutations(parent: MutationCandidate, *, base_seed: int, budget: AttemptBudget, request_factory: Callable[[MutationCandidate, int, int], MutationRequest], engine: MutationEngine, validator: Callable[[MutationResult], AuthenticTargetCandidate], target: TypedChallengeTarget, source_context=None) -> AttemptReport:
    from .m07_services import derive_attempt_seed
    records: list[AttemptRecord] = []
    current = parent
    terminals: list[AttemptDisposition] = []
    if parent.source_art_sha256 is not None:
        if source_context is None or not getattr(source_context, "passed", False):
            return AttemptReport(AttemptDisposition.ERROR, budget, tuple(), None, "mandatory accepted M05 OWNER_UPLOAD preservation PASS is unavailable")
    for ordinal in range(budget.max_attempts):
        seed = derive_attempt_seed(base_seed, ordinal)
        request = request_factory(current, ordinal, seed)
        mutation = engine.apply(request, current)
        attempt = AttemptProvenance(ordinal, seed, mutation.request_digest, mutation.parent.candidate_id, mutation.disposition, mutation.reason, mutation.operator_id, mutation.operator_version, mutation.authority.digest(), mutation.parent.state_digest)
        if mutation.disposition is not MutationDisposition.APPLIED:
            records.append(AttemptRecord(ordinal, seed, mutation, None, None, None, attempt))
            terminals.append(AttemptDisposition.ERROR if mutation.disposition is MutationDisposition.ERROR else AttemptDisposition.UNAVAILABLE if mutation.disposition is MutationDisposition.UNAVAILABLE else AttemptDisposition.REJECTED)
            continue
        candidate = validator(mutation)
        selection = select_authentic_target(target, (candidate,))
        provenance = provenance_from_authentic_validation(request, mutation, candidate.envelope, candidate.solver, candidate.difficulty, candidate.qa, attempt_ordinal=ordinal)
        records.append(AttemptRecord(ordinal, seed, mutation, candidate.envelope, selection, provenance, attempt))
        if selection.disposition.value == "MATCH":
            return AttemptReport(AttemptDisposition.TARGET_MATCH, budget, tuple(records), candidate.envelope, "authenticated target matched before budget exhaustion")
        terminals.append(AttemptDisposition.UNAVAILABLE if selection.disposition.value == "UNAVAILABLE" else AttemptDisposition.INCONCLUSIVE if selection.disposition.value == "INCONCLUSIVE" else AttemptDisposition.REJECTED)
        current = mutation.child or current
    for terminal in (AttemptDisposition.ERROR, AttemptDisposition.UNAVAILABLE, AttemptDisposition.INCONCLUSIVE, AttemptDisposition.REJECTED):
        if terminal in terminals:
            return AttemptReport(terminal, budget, tuple(records), None, f"strongest observed terminal disposition: {terminal.value}")
    return AttemptReport(AttemptDisposition.EXHAUSTED, budget, tuple(records), None, "finite mutation budget exhausted without target success")


__all__ = ["run_authentic_bounded_mutations"]
