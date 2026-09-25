"""SB-LF07-004 adapters over accepted M03/M04/M05 producer objects."""

from dataclasses import dataclass
from typing import Any

from .baseline_search import SearchExecutionDisposition, SearchVerdict
from .difficulty_analysis import AnalysisDisposition, ChallengeScoreResult, DifficultyAnalysis
from .qa.unified import UnifiedQAReport, UnifiedQADisposition
from .solver_evidence import SolverEvidenceReport
from .mutation_base import MutationContractError
from .m07_services import EvidenceDisposition, EvidenceRecord, MutationDisposition, MutationResult, ValidationEnvelope, revalidate_mutation


@dataclass(frozen=True, slots=True)
class AuthenticEvidenceAdapter:
    stage: str
    producer: object
    producer_schema: str
    producer_version: int
    record: EvidenceRecord
    producer_digest: str

    def __post_init__(self) -> None:
        if type(self.stage) is not str or not self.stage:
            raise MutationContractError("authentic evidence stage is malformed")
        if not callable(getattr(self.producer, "digest", None)) or self.producer_digest != self.producer.digest():
            raise MutationContractError("producer digest is not derived from the accepted producer object")
        if self.record.stage != self.stage or self.record.evidence_digest is None:
            raise MutationContractError("authentic evidence record is malformed")


def _record(stage: str, disposition: EvidenceDisposition, mutation: MutationResult, payload: dict[str, object]) -> EvidenceRecord:
    if mutation.disposition is not MutationDisposition.APPLIED or mutation.child is None:
        raise MutationContractError("authentic producer evidence requires an applied mutation")
    return EvidenceRecord(stage, disposition, mutation.child.state_digest, mutation.request_digest, mutation.parent.state_digest, mutation.operator_id, mutation.authority.digest(), payload)


def adapt_m03_solver(report: SolverEvidenceReport, mutation: MutationResult) -> AuthenticEvidenceAdapter:
    if not isinstance(report, SolverEvidenceReport):
        raise MutationContractError("M03 adapter requires SolverEvidenceReport")
    if report.execution is SearchExecutionDisposition.UNAVAILABLE:
        status = EvidenceDisposition.UNAVAILABLE
    elif report.execution is SearchExecutionDisposition.ERROR:
        status = EvidenceDisposition.ERROR
    elif report.result.verdict is SearchVerdict.SOLVED:
        status = EvidenceDisposition.SOLVED
    elif report.result.verdict is SearchVerdict.PROVEN_UNSOLVABLE:
        status = EvidenceDisposition.PROVEN_UNSOLVABLE
    else:
        status = EvidenceDisposition.INCONCLUSIVE
    record = _record("M03_SOLVER", status, mutation, {"producer_schema": "scrubbots-solver-evidence", "producer_version": 1, "producer_digest": report.digest(), "verdict": report.result.verdict.value if report.result.verdict else None})
    return AuthenticEvidenceAdapter("M03_SOLVER", report, "scrubbots-solver-evidence", 1, record, report.digest())


def adapt_m04_difficulty(analysis: DifficultyAnalysis, score: ChallengeScoreResult, mutation: MutationResult) -> AuthenticEvidenceAdapter:
    if not isinstance(analysis, DifficultyAnalysis) or not isinstance(score, ChallengeScoreResult):
        raise MutationContractError("M04 adapter requires DifficultyAnalysis and ChallengeScoreResult")
    if analysis.challenge_score_digest != score.digest() or analysis.challenge_score_policy_version != score.policy_version:
        raise MutationContractError("M04 Challenge Score is not bound to DifficultyAnalysis")
    status = EvidenceDisposition.AVAILABLE if analysis.disposition is AnalysisDisposition.AVAILABLE else EvidenceDisposition.UNAVAILABLE if analysis.disposition is AnalysisDisposition.UNAVAILABLE else EvidenceDisposition.INCONCLUSIVE
    record = _record("M04_DIFFICULTY", status, mutation, {"producer_schema": "scrubbots-difficulty-analysis", "producer_version": 1, "producer_digest": analysis.digest(), "challenge_score_digest": score.digest(), "challenge_score": float(score.score), "policy_version": score.policy_version})
    return AuthenticEvidenceAdapter("M04_DIFFICULTY", analysis, "scrubbots-difficulty-analysis", 1, record, analysis.digest())


def adapt_m05_qa(report: UnifiedQAReport, mutation: MutationResult) -> AuthenticEvidenceAdapter:
    if not isinstance(report, UnifiedQAReport):
        raise MutationContractError("M05 adapter requires UnifiedQAReport")
    status_map = {UnifiedQADisposition.ACCEPT: EvidenceDisposition.PASS, UnifiedQADisposition.REJECT: EvidenceDisposition.REJECT, UnifiedQADisposition.INCONCLUSIVE: EvidenceDisposition.INCONCLUSIVE, UnifiedQADisposition.UNAVAILABLE: EvidenceDisposition.UNAVAILABLE, UnifiedQADisposition.ERROR: EvidenceDisposition.ERROR}
    status = status_map[report.disposition]
    record = _record("M05_QA", status, mutation, {"producer_schema": report.schema, "producer_version": report.version, "producer_digest": report.digest(), "disposition": report.disposition.value})
    return AuthenticEvidenceAdapter("M05_QA", report, report.schema, report.version, record, report.digest())


def revalidate_mutation_from_authentic_adapters(mutation: MutationResult, solver: AuthenticEvidenceAdapter, difficulty: AuthenticEvidenceAdapter, qa: AuthenticEvidenceAdapter) -> ValidationEnvelope:
    if not all(isinstance(item, AuthenticEvidenceAdapter) for item in (solver, difficulty, qa)):
        raise MutationContractError("production eligibility requires authentic M03/M04/M05 adapters")
    if (solver.stage, difficulty.stage, qa.stage) != ("M03_SOLVER", "M04_DIFFICULTY", "M05_QA"):
        raise MutationContractError("authentic producer stages are incomplete or reordered")
    return revalidate_mutation(mutation, solver.record, difficulty.record, qa.record)


__all__ = ["AuthenticEvidenceAdapter", "adapt_m03_solver", "adapt_m04_difficulty", "adapt_m05_qa", "revalidate_mutation_from_authentic_adapters"]
