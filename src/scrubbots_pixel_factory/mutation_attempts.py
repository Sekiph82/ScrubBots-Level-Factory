"""SB-LF07-007 authentic bounded runner service."""

from collections.abc import Callable
import hashlib
import json

from .mutation_base import MutationCandidate, MutationDisposition, MutationEngine, MutationRequest
from .mutation_evidence import provenance_from_authentic_validation
from .m07_services import AttemptBudget, AttemptDisposition, AttemptProvenance, AttemptRecord, AttemptReport, MutationContractError, MutationDisposition, MutationResult, TypedChallengeTarget, ValidationDisposition
from .mutation_targeting import AuthenticTargetCandidate, TargetDisposition, select_authentic_target


def run_authentic_bounded_mutations(parent: MutationCandidate, *, base_seed: int, budget: AttemptBudget, request_factory: Callable[[MutationCandidate, int, int], MutationRequest], engine: MutationEngine, validator: Callable[[MutationResult], AuthenticTargetCandidate], target: TypedChallengeTarget, source_context=None) -> AttemptReport:
    from .m07_services import derive_attempt_seed
    records: list[AttemptRecord] = []
    current = parent
    terminals: list[AttemptDisposition] = []
    seed_config_digest = hashlib.sha256(json.dumps({"seed": base_seed}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if parent.source_art_sha256 is not None:
        from .mutation_source import SourceLinkedMutationContext
        if not isinstance(source_context, SourceLinkedMutationContext) or source_context.before.disposition != "PASS":
            return AttemptReport(AttemptDisposition.ERROR, budget, tuple(), None, "mandatory accepted M05 OWNER_UPLOAD preservation PASS is unavailable", target, seed_config_digest)
    for ordinal in range(budget.max_attempts):
        seed = derive_attempt_seed(base_seed, ordinal)
        request = request_factory(current, ordinal, seed)
        mutation = engine.apply(request, current)
        attempt = AttemptProvenance(ordinal, seed, mutation.request_digest, mutation.parent.candidate_id, mutation.disposition, mutation.reason, mutation.operator_id, mutation.operator_version, mutation.authority.digest(), mutation.parent.state_digest)
        if mutation.disposition is not MutationDisposition.APPLIED:
            records.append(AttemptRecord(ordinal, seed, mutation, None, None, None, attempt))
            terminals.append(AttemptDisposition.ERROR if mutation.disposition is MutationDisposition.ERROR else AttemptDisposition.UNAVAILABLE if mutation.disposition is MutationDisposition.UNAVAILABLE else AttemptDisposition.REJECTED)
            continue
        try:
            candidate = validator(mutation)
        except MutationContractError as exc:
            records.append(AttemptRecord(ordinal, seed, mutation, None, None, None, attempt))
            terminals.append(AttemptDisposition.ERROR)
            current = mutation.child or current
            continue
        selection = select_authentic_target(target, (candidate,))
        provenance = provenance_from_authentic_validation(request, mutation, candidate.envelope, candidate.solver, candidate.difficulty, candidate.qa, attempt_ordinal=ordinal)
        if source_context is not None and hasattr(source_context, "verify_after"):
            source_context = source_context.verify_after()
            if source_context.after is None or source_context.after.disposition != "PASS":
                records.append(AttemptRecord(ordinal, seed, mutation, candidate.envelope, None, provenance, attempt))
                return AttemptReport(AttemptDisposition.ERROR, budget, tuple(records), None, "accepted M05 OWNER_UPLOAD post-check failed after authentic mutation validation", target, seed_config_digest)
        records.append(AttemptRecord(ordinal, seed, mutation, candidate.envelope, selection, provenance, attempt))
        if selection.disposition is TargetDisposition.MATCH:
            return AttemptReport(AttemptDisposition.TARGET_MATCH, budget, tuple(records), candidate.envelope, "authenticated target matched before budget exhaustion", target, seed_config_digest)
        envelope_terminal = {ValidationDisposition.ERROR: AttemptDisposition.ERROR, ValidationDisposition.UNAVAILABLE: AttemptDisposition.UNAVAILABLE, ValidationDisposition.INCONCLUSIVE: AttemptDisposition.INCONCLUSIVE, ValidationDisposition.REJECTED: AttemptDisposition.REJECTED}.get(candidate.envelope.disposition)
        if envelope_terminal is not None:
            terminals.append(envelope_terminal)
        elif selection.disposition is TargetDisposition.UNAVAILABLE:
            terminals.append(AttemptDisposition.UNAVAILABLE)
        elif selection.disposition is TargetDisposition.INCONCLUSIVE:
            terminals.append(AttemptDisposition.INCONCLUSIVE)
        elif selection.disposition is not TargetDisposition.NO_MATCH:
            terminals.append(AttemptDisposition.REJECTED)
        current = mutation.child or current
    for terminal in (AttemptDisposition.ERROR, AttemptDisposition.UNAVAILABLE, AttemptDisposition.INCONCLUSIVE, AttemptDisposition.REJECTED):
        if terminal in terminals:
            return AttemptReport(terminal, budget, tuple(records), None, f"strongest observed terminal disposition: {terminal.value}", target, seed_config_digest)
    return AttemptReport(AttemptDisposition.EXHAUSTED, budget, tuple(records), None, "finite mutation budget exhausted without target success", target, seed_config_digest)


__all__ = ["run_authentic_bounded_mutations"]
