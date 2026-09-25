"""SB-LF07-008 route evidence adapters from actual execution results."""

from dataclasses import dataclass
import hashlib
import json

from .core import GenerationResult, ResultStatus
from .m07_services import AttemptBudget, AttemptReport, EfficiencyComparison, EfficiencyCounters, EfficiencyWorkload, MutationContractError, TypedChallengeTarget
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
        actual = EfficiencyWorkload(report.target.digest(), report.seed_config_digest, _digest({"validation_policy_digest": report.target.policy_digest}), report.budget.digest())
        if workload is not None and workload != actual:
            raise MutationContractError("caller-supplied mutation workload is not the actual AttemptReport workload")
        return cls(report, actual)

    @property
    def counters(self) -> EfficiencyCounters:
        produced = sum(item.mutation.disposition.value == "APPLIED" for item in self.report.attempts)
        accepted = sum(item.validation is not None and item.validation.disposition.value == "ELIGIBLE" for item in self.report.attempts)
        inconclusive = sum((item.validation is not None and item.validation.disposition.value in {"INCONCLUSIVE", "UNAVAILABLE"}) or (item.validation is None and item.mutation.disposition.value == "UNAVAILABLE") for item in self.report.attempts)
        rejected = sum((item.validation is not None and item.validation.disposition.value in {"REJECTED", "ERROR"}) or (item.validation is None and item.mutation.disposition.value in {"ERROR", "INAPPLICABLE"}) for item in self.report.attempts)
        solver_workload = sum(item.validation.solver.payload.get("states_visited", 0) for item in self.report.attempts if item.validation is not None and type(item.validation.solver.payload.get("states_visited", 0)) is int)
        return EfficiencyCounters(len(self.report.attempts), produced, accepted, inconclusive, rejected, solver_workload)


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
        seed_digest = _digest({"seed": result.request.seed})
        actual = EfficiencyWorkload(target.digest(), seed_digest, _digest({"validation_policy_digest": target.policy_digest}), budget.digest())
        if workload is not None and workload != actual:
            raise MutationContractError("caller-supplied regeneration workload is not the actual route workload")
        return cls(result, actual, result.generator_id or "UNAVAILABLE", result.generator_version or "UNAVAILABLE", result.request.digest(), result.request.digest(), None)

    @property
    def counters(self) -> EfficiencyCounters:
        success = self.result.status is ResultStatus.SUCCESS
        return EfficiencyCounters(1, 1 if success else 0, 1 if success else 0, 0, 0 if success else 1, 0)


def compare_efficiency_from_authentic_routes(mutation: MutationAttemptRouteEvidence, regenerate: RegenerationRouteEvidence) -> EfficiencyComparison:
    if mutation.workload != regenerate.workload:
        raise MutationContractError("actual route workloads are not matched")
    mutation_cost = None
    regenerate_cost = None
    return EfficiencyComparison(mutation.workload, mutation.counters, regenerate.counters, mutation_cost=mutation_cost, regenerate_cost=regenerate_cost, telemetry=None)


__all__ = ["MutationAttemptRouteEvidence", "RegenerationRouteEvidence", "TrustedAccountingEvidence", "compare_efficiency_from_authentic_routes"]
