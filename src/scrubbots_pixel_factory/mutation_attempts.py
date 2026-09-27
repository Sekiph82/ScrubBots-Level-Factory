"""SB-LF07-007 authentic bounded runner service."""

from collections.abc import Callable, Mapping
import hashlib
import json

from .mutation_base import MutationCandidate, MutationDisposition, MutationEngine, MutationRequest
from .core import GenerationRequest
from .mutation_evidence import provenance_from_authentic_validation
from .m07_services import (
    AttemptBudget, AttemptDisposition, AttemptProvenance, AttemptRecord, AttemptReport,
    MutationContractError, MutationResult, TypedChallengeTarget, ValidationDisposition,
)
from .mutation_targeting import AuthenticTargetCandidate, TargetDisposition, select_authentic_target
from .mutation_workload import canonical_workload_identity, parent_generation_request_digest


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _config_identity(parent: MutationCandidate) -> tuple[str, bool]:
    """Return only an explicit full workload identity; never infer one from seed."""
    raw = parent.payload.get("generation_request")
    if not isinstance(raw, Mapping):
        return _digest({"availability": "UNAVAILABLE", "reason": "generation_request_not_bound"}), False
    required = {"seed", "difficulty", "width", "height", "generator_mode", "style", "theme", "palette_subset", "generator_options", "target_policy", "validation_policy", "budget"}
    if not required.issubset(raw):
        return _digest({"availability": "UNAVAILABLE", "reason": "generation_request_config_incomplete"}), False
    try:
        canonical = json.loads(json.dumps(dict(raw), sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    except (TypeError, ValueError):
        return _digest({"availability": "UNAVAILABLE", "reason": "generation_request_config_malformed"}), False
    return _digest(canonical), True


def _terminal_for_mutation(disposition: MutationDisposition) -> AttemptDisposition:
    return {MutationDisposition.ERROR: AttemptDisposition.ERROR, MutationDisposition.UNAVAILABLE: AttemptDisposition.UNAVAILABLE, MutationDisposition.INAPPLICABLE: AttemptDisposition.REJECTED, MutationDisposition.NO_CHANGE: AttemptDisposition.REJECTED}.get(disposition, AttemptDisposition.REJECTED)


def _postcheck(source_context):
    if source_context is None or not hasattr(source_context, "verify_after"):
        return source_context, None
    try:
        checked = source_context.verify_after()
    except Exception as exc:
        return source_context, f"M05 OWNER_UPLOAD source post-check raised {type(exc).__name__}: {exc}"
    if checked.after is None or checked.after.disposition != "PASS":
        return checked, "M05 OWNER_UPLOAD source post-check failed"
    return checked, None


def _source_entry_guard(parent: MutationCandidate, source_context):
    """Require the exact accepted M05 source context before any operation."""
    if parent.source_art_sha256 is None:
        return source_context, None
    from .mutation_source import SourceLinkedMutationContext
    if not isinstance(source_context, SourceLinkedMutationContext):
        return source_context, "source-linked parent requires an accepted M05 SourceLinkedMutationContext"
    try:
        checked = SourceLinkedMutationContext.establish(source_context.record)
        return checked.require_exact_parent_source(parent.source_art_sha256), None
    except Exception as exc:
        return source_context, f"source-linked M05 pre-check failed before operation: {type(exc).__name__}: {exc}"


def run_authentic_bounded_mutations(parent: MutationCandidate, *, base_seed: int, budget: AttemptBudget, request_factory: Callable[[MutationCandidate, int, int], MutationRequest], engine: MutationEngine, validator: Callable[[MutationResult], AuthenticTargetCandidate], target: TypedChallengeTarget, source_context=None, generation_request: GenerationRequest | None = None) -> AttemptReport:
    from .m07_services import derive_attempt_seed
    records: list[AttemptRecord] = []
    current = parent
    terminals: list[AttemptDisposition] = []
    seed_config_digest, workload_available = _config_identity(parent)
    workload = None
    if generation_request is not None:
        if type(base_seed) is not int or generation_request.seed != base_seed:
            return AttemptReport(AttemptDisposition.ERROR, budget, tuple(), None, "generation workload seed does not match the mutation base-seed contract", target, seed_config_digest, False, None)
        try:
            parent_digest = parent_generation_request_digest(parent)
            if parent_digest is not None:
                if generation_request.digest() != parent_digest:
                    return AttemptReport(AttemptDisposition.ERROR, budget, tuple(), None, "generation workload digest does not match the parent generation provenance", target, seed_config_digest, False, None)
                workload = canonical_workload_identity(generation_request, target, budget)
                seed_config_digest, workload_available = workload.seed_config_digest, True
        except MutationContractError:
            return AttemptReport(AttemptDisposition.ERROR, budget, tuple(), None, "exact GenerationRequest could not establish the canonical workload identity", target, seed_config_digest, False, None)

    if not isinstance(target, TypedChallengeTarget) or not target.is_authentic_sealed:
        return AttemptReport(AttemptDisposition.ERROR, budget, tuple(), None, "sealed authentic target authority is required", target, seed_config_digest, workload_available, workload)

    source_context, source_error = _source_entry_guard(parent, source_context)
    if source_error is not None:
        return AttemptReport(AttemptDisposition.ERROR, budget, tuple(), None, source_error, target, seed_config_digest, workload_available, workload)

    for ordinal in range(budget.max_attempts):
        seed = derive_attempt_seed(base_seed, ordinal)
        attempt_context = source_context
        mutation = None
        request = None
        attempt = None
        validation = None
        selection = None
        provenance = None
        matched_validation = None
        terminal_error = None
        try:
            if source_context is not None:
                from .mutation_source import SourceLinkedMutationContext
                attempt_context = SourceLinkedMutationContext.establish(source_context.record)
            request = request_factory(current, ordinal, seed)
            if not isinstance(request, MutationRequest):
                raise MutationContractError("request factory did not return MutationRequest")
            mutation = engine.apply(request, current)
            if not isinstance(mutation, MutationResult):
                raise MutationContractError("mutation engine did not return MutationResult")
            attempt = AttemptProvenance(ordinal, seed, mutation.request_digest, mutation.parent.candidate_id, mutation.disposition, mutation.reason, mutation.operator_id, mutation.operator_version, mutation.authority.digest(), mutation.parent.state_digest)
            if mutation.disposition is not MutationDisposition.APPLIED:
                terminals.append(_terminal_for_mutation(mutation.disposition))
                records.append(AttemptRecord(ordinal, seed, mutation, None, None, None, attempt))
                current = mutation.child or current
            else:
                candidate = validator(mutation)
                if not isinstance(candidate, AuthenticTargetCandidate):
                    raise MutationContractError("validator did not return AuthenticTargetCandidate")
                validation = candidate.envelope
                selection = select_authentic_target(target, (candidate,))
                provenance = provenance_from_authentic_validation(request, mutation, validation, candidate.solver, candidate.difficulty, candidate.qa, attempt_ordinal=ordinal)
                records.append(AttemptRecord(ordinal, seed, mutation, validation, selection, provenance, attempt))
                if selection.disposition is TargetDisposition.MATCH:
                    matched_validation = validation
                elif validation.disposition is ValidationDisposition.ERROR:
                    terminals.append(AttemptDisposition.ERROR)
                elif validation.disposition is ValidationDisposition.UNAVAILABLE:
                    terminals.append(AttemptDisposition.UNAVAILABLE)
                elif validation.disposition is ValidationDisposition.INCONCLUSIVE:
                    terminals.append(AttemptDisposition.INCONCLUSIVE)
                elif validation.disposition is ValidationDisposition.REJECTED:
                    terminals.append(AttemptDisposition.REJECTED)
                elif selection.disposition is TargetDisposition.UNAVAILABLE:
                    terminals.append(AttemptDisposition.UNAVAILABLE)
                elif selection.disposition is TargetDisposition.INCONCLUSIVE:
                    terminals.append(AttemptDisposition.INCONCLUSIVE)
                elif selection.disposition is TargetDisposition.ERROR:
                    terminals.append(AttemptDisposition.ERROR)
                elif selection.disposition is not TargetDisposition.NO_MATCH:
                    terminals.append(AttemptDisposition.REJECTED)
                current = mutation.child or current
        except Exception as exc:
            terminal_error = f"deterministic mutation attempt ERROR: {type(exc).__name__}: {exc}"
            terminals.append(AttemptDisposition.ERROR)
            if mutation is not None and attempt is not None:
                records.append(AttemptRecord(ordinal, seed, mutation, validation, selection, provenance, attempt))
        finally:
            if attempt_context is not None:
                checked_context, post_error = _postcheck(attempt_context)
                source_context = checked_context
                if post_error is not None:
                    terminals.append(AttemptDisposition.ERROR)
                    terminal_error = post_error
        if terminal_error is not None:
            return AttemptReport(AttemptDisposition.ERROR, budget, tuple(records), None, terminal_error, target, seed_config_digest, workload_available, workload)
        if matched_validation is not None:
            return AttemptReport(AttemptDisposition.TARGET_MATCH, budget, tuple(records), matched_validation, "authenticated target matched before budget exhaustion", target, seed_config_digest, workload_available, workload)

    for terminal in (AttemptDisposition.ERROR, AttemptDisposition.UNAVAILABLE, AttemptDisposition.INCONCLUSIVE, AttemptDisposition.REJECTED):
        if terminal in terminals:
            return AttemptReport(terminal, budget, tuple(records), None, f"strongest observed terminal disposition: {terminal.value}", target, seed_config_digest, workload_available, workload)
    return AttemptReport(AttemptDisposition.EXHAUSTED, budget, tuple(records), None, "finite mutation budget exhausted without target success", target, seed_config_digest, workload_available, workload)


__all__ = ["run_authentic_bounded_mutations"]
