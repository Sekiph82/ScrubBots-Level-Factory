"""SB-LF07-008 route evidence adapters from actual execution results."""

from dataclasses import dataclass
import hashlib
import json

from .core import GenerationResult, ResultStatus
from .m07_services import AttemptReport, EfficiencyComparison, EfficiencyCounters, EfficiencyWorkload, MutationContractError
from .semantic.qualification.models import CostUsageRecord


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class TrustedAccountingEvidence:
    record: CostUsageRecord
    evidence_digest: str

    @classmethod
    def from_cost_usage(cls, record: CostUsageRecord) -> "TrustedAccountingEvidence":
        if not isinstance(record, CostUsageRecord):
            raise MutationContractError("accounting evidence requires accepted CostUsageRecord")
        return cls(record, _digest(record.canonical_dict()))


@dataclass(frozen=True, slots=True)
class MutationAttemptRouteEvidence:
    report: AttemptReport
    workload: EfficiencyWorkload

    @classmethod
    def from_attempt_report(cls, report: AttemptReport, workload: EfficiencyWorkload) -> "MutationAttemptRouteEvidence":
        if not isinstance(report, AttemptReport) or not isinstance(workload, EfficiencyWorkload):
            raise MutationContractError("mutation route requires actual AttemptReport and workload")
        return cls(report, workload)

    @property
    def counters(self) -> EfficiencyCounters:
        produced = sum(item.mutation.disposition.value == "APPLIED" for item in self.report.attempts)
        accepted = sum(item.validation is not None and item.validation.disposition.value == "ELIGIBLE" for item in self.report.attempts)
        inconclusive = sum(item.validation is not None and item.validation.disposition.value in {"INCONCLUSIVE", "UNAVAILABLE"} for item in self.report.attempts)
        rejected = sum(item.validation is not None and item.validation.disposition.value in {"REJECTED", "ERROR"} for item in self.report.attempts)
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
    def from_generation_result(cls, result: GenerationResult, workload: EfficiencyWorkload, *, config_digest: str, accounting: TrustedAccountingEvidence | None = None) -> "RegenerationRouteEvidence":
        if not isinstance(result, GenerationResult) or not isinstance(workload, EfficiencyWorkload) or type(config_digest) is not str or len(config_digest) != 64:
            raise MutationContractError("regeneration route requires actual GenerationResult, workload, and config identity")
        if result.request is None:
            raise MutationContractError("regeneration result must retain its exact request identity")
        return cls(result, workload, result.generator_id or "UNAVAILABLE", result.generator_version or "UNAVAILABLE", result.request.digest(), config_digest, accounting)

    @property
    def counters(self) -> EfficiencyCounters:
        success = self.result.status is ResultStatus.SUCCESS
        return EfficiencyCounters(1, 1 if success else 0, 1 if success else 0, 0, 0 if success else 1, 0)


def compare_efficiency_from_authentic_routes(mutation: MutationAttemptRouteEvidence, regenerate: RegenerationRouteEvidence) -> EfficiencyComparison:
    if mutation.workload != regenerate.workload:
        raise MutationContractError("actual route workloads are not matched")
    mutation_cost = None
    regenerate_cost = None
    if regenerate.accounting is not None:
        regenerate_cost = {"evidence_digest": regenerate.accounting.evidence_digest, "provider_attempt_count": regenerate.accounting.record.provider_attempt_count, "trusted": True}
    return EfficiencyComparison(mutation.workload, mutation.counters, regenerate.counters, mutation_cost=mutation_cost, regenerate_cost=regenerate_cost, telemetry=None)


__all__ = ["MutationAttemptRouteEvidence", "RegenerationRouteEvidence", "TrustedAccountingEvidence", "compare_efficiency_from_authentic_routes"]
