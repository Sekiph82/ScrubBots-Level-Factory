"""SB-LF07-008 route evidence adapters from actual execution results."""

from dataclasses import dataclass
import hashlib
import json

from .core import GenerationResult, ResultStatus
from .m07_services import AttemptBudget, AttemptReport, EfficiencyComparison, EfficiencyCounters, EfficiencyWorkload, MutationContractError, TypedChallengeTarget
from .mutation_workload import canonical_workload_identity
from .semantic.qualification.models import CostUsageRecord


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class TrustedAccountingEvidence:
    record: CostUsageRecord
    evidence_digest: str

    @classmethod
    def from_cost_usage(cls, record: CostUsageRecord) -> "TrustedAccountingEvidence":
        raise MutationContractError("authoritative provider/job accounting is unavailable; CostUsageRecord cannot establish trusted evidence")


@dataclass(frozen=True, slots=True)
class MutationAttemptRouteEvidence:
    report: AttemptReport
    workload: EfficiencyWorkload

    @classmethod
    def from_attempt_report(cls, report: AttemptReport, workload: EfficiencyWorkload | None = None) -> "MutationAttemptRouteEvidence":
        if not isinstance(report, AttemptReport) or not isinstance(report.target, TypedChallengeTarget) or type(report.seed_config_digest) is not str or not isinstance(report.budget, AttemptBudget):
            raise MutationContractError("mutation route requires an authentic AttemptReport with target, seed/config, and budget identity")
        actual = report.workload
        if actual is None:
            actual = EfficiencyWorkload(report.target.digest(), _digest({"availability": "UNAVAILABLE", "reason": "exact_generation_request_not_bound"}), _digest({"availability": "UNAVAILABLE", "reason": "validation_policy_not_bound"}), report.budget.digest(), "UNAVAILABLE")
        if workload is not None and workload != actual:
            raise MutationContractError("caller-supplied mutation workload is not the actual AttemptReport workload")
        return cls(report, actual)

    @property
    def counters(self) -> EfficiencyCounters:
        produced = sum(item.mutation.disposition.value == "APPLIED" for item in self.report.attempts)
        accepted = sum(item.validation is not None and item.validation.disposition.value == "ELIGIBLE" and item.provenance is not None and item.provenance.is_authentic_sealed for item in self.report.attempts)
        inconclusive = sum((item.validation is not None and item.validation.disposition.value in {"INCONCLUSIVE", "UNAVAILABLE"}) or (item.validation is None and item.mutation.disposition.value == "UNAVAILABLE") for item in self.report.attempts)
        rejected = sum((item.validation is not None and item.validation.disposition.value in {"REJECTED", "ERROR"}) or (item.validation is None and item.mutation.disposition.value in {"ERROR", "INAPPLICABLE"}) for item in self.report.attempts)
        values = [item.validation.solver.payload.get("states_visited") for item in self.report.attempts if item.validation is not None]
        available = bool(values) and all(type(value) is int and value >= 0 for value in values)
        solver_workload = sum(value for value in values if type(value) is int and value >= 0)
        return EfficiencyCounters(len(self.report.attempts), produced, accepted, inconclusive, rejected, solver_workload, available)


@dataclass(frozen=True, slots=True)
class RegenerationRouteEvidence:
    result: GenerationResult
    workload: EfficiencyWorkload
    route_id: str
    route_version: str
    request_digest: str
    config_digest: str
    accounting: TrustedAccountingEvidence | None = None

    @classmethod
    def from_generation_result(cls, result: GenerationResult, workload: EfficiencyWorkload | None = None, *, target: TypedChallengeTarget | None = None, budget: AttemptBudget | None = None, config_digest: str | None = None, accounting: TrustedAccountingEvidence | None = None) -> "RegenerationRouteEvidence":
        if not isinstance(result, GenerationResult) or not isinstance(target, TypedChallengeTarget) or not isinstance(budget, AttemptBudget):
            raise MutationContractError("regeneration route requires actual GenerationResult, typed target, and attempt budget")
        if result.request is None:
            raise MutationContractError("regeneration result must retain its exact request identity")
        if config_digest is not None or accounting is not None:
            raise MutationContractError("caller config/accounting evidence is not authoritative")
        actual = canonical_workload_identity(result.request, target, budget)
        config_digest = result.request.digest()
        if workload is not None and workload != actual:
            raise MutationContractError("caller-supplied regeneration workload is not the actual route workload")
        return cls(result, actual, result.generator_id or "UNAVAILABLE", result.generator_version or "UNAVAILABLE", result.request.digest(), config_digest, None)

    @property
    def counters(self) -> EfficiencyCounters:
        success = self.result.status is ResultStatus.SUCCESS
        # A raw GenerationResult has no accepted M03/M04/M05 validation chain.
        # Therefore success is an inconclusive regeneration observation, never an
        # accepted production candidate.
        return EfficiencyCounters(1, 1 if success else 0, 0, 1 if success else 0, 0 if success else 1, 0, False)


def compare_efficiency_from_authentic_routes(mutation: MutationAttemptRouteEvidence, regenerate: RegenerationRouteEvidence) -> EfficiencyComparison:
    if mutation.workload != regenerate.workload:
        unavailable = EfficiencyWorkload(mutation.workload.target_digest, _digest({"availability": "UNAVAILABLE", "reason": "matched_full_workload_unavailable"}), mutation.workload.validation_policy_digest, mutation.workload.budget_digest, "UNAVAILABLE")
        return EfficiencyComparison(unavailable, mutation.counters, regenerate.counters, mutation_cost=None, regenerate_cost=None, telemetry=None, disposition="UNAVAILABLE", reason="mutate-vs-regenerate comparison requires the same full workload identity")
    mutation_cost = None
    regenerate_cost = None
    return EfficiencyComparison(mutation.workload, mutation.counters, regenerate.counters, mutation_cost=mutation_cost, regenerate_cost=regenerate_cost, telemetry=None, disposition="MATCHED")


__all__ = ["MutationAttemptRouteEvidence", "RegenerationRouteEvidence", "TrustedAccountingEvidence", "compare_efficiency_from_authentic_routes"]
