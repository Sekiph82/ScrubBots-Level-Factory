"""SB-LF07-004 adapters over accepted M03/M04/M05 producer objects."""

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .baseline_search import SearchExecutionDisposition, SearchVerdict
from .compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA, SolverStateAuthority
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


def _canonical_digest(value: object) -> str | None:
    canonical = getattr(value, "canonical_dict", None)
    if not callable(canonical):
        return None
    try:
        return hashlib.sha256(json.dumps(canonical(), ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    except (TypeError, ValueError):
        return None


def _require_child_source(mutation: MutationResult) -> str:
    if mutation.child is None:
        raise MutationContractError("authentic producer evidence requires an applied child")
    source = mutation.child.source_art_sha256 or mutation.child.level_data_sha256
    if source is None:
        raise MutationContractError("authentic producer source identity is UNAVAILABLE")
    return source


def _child_level_id(mutation: MutationResult) -> str:
    if mutation.child is None:
        raise MutationContractError("authentic producer evidence requires an applied child")
    payload_level_id = mutation.child.payload.get("level_id")
    return payload_level_id if isinstance(payload_level_id, str) and payload_level_id else mutation.child.candidate_id


def _require_authority(actual: object, mutation: MutationResult, label: str) -> None:
    if actual is None:
        raise MutationContractError(f"{label} native authority identity is UNAVAILABLE")
    actual_canonical = getattr(actual, "canonical_dict", None)
    if not callable(actual_canonical):
        raise MutationContractError(f"{label} native authority is not bound to the mutation authority")
    try:
        identity = actual_canonical()
    except (TypeError, ValueError):
        raise MutationContractError(f"{label} native authority is not bound to the mutation authority")
    if identity.get("repository") != mutation.authority.repository or identity.get("commit_sha") in (None, "UNAVAILABLE"):
        raise MutationContractError(f"{label} native authority is not bound to the mutation authority")
    if isinstance(actual, SolverStateAuthority) and actual.commit_sha != CANONICAL_PROOF_STATE_AUTHORITY_SHA:
        raise MutationContractError(f"{label} native M03 authority is stale or not accepted")


def adapt_m03_solver(report: SolverEvidenceReport, mutation: MutationResult) -> AuthenticEvidenceAdapter:
    if not isinstance(report, SolverEvidenceReport):
        raise MutationContractError("M03 adapter requires SolverEvidenceReport")
    source = _require_child_source(mutation)
    if not report.level_id or report.level_id != _child_level_id(mutation) or report.level_source_sha256 != source:
        raise MutationContractError("M03 SolverEvidenceReport is not bound to the exact mutation child/source")
    if report.request_id != mutation.request_digest or report.state_digest != mutation.child.state_digest:
        raise MutationContractError("M03 SolverEvidenceReport is not bound to the exact mutation request/state")
    if not report.provider_id or not report.provider_version:
        raise MutationContractError("M03 SolverEvidenceReport provider provenance is UNAVAILABLE")
    _require_authority(report.authority, mutation, "M03")
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


def adapt_m04_difficulty(analysis: DifficultyAnalysis, score: ChallengeScoreResult, mutation: MutationResult, *, solver: AuthenticEvidenceAdapter | None = None) -> AuthenticEvidenceAdapter:
    if not isinstance(analysis, DifficultyAnalysis) or not isinstance(score, ChallengeScoreResult):
        raise MutationContractError("M04 adapter requires DifficultyAnalysis and ChallengeScoreResult")
    source = _require_child_source(mutation)
    if analysis.level_source_sha256 != source:
        raise MutationContractError("M04 DifficultyAnalysis is not bound to the exact mutation source")
    if solver is None or solver.stage != "M03_SOLVER" or not isinstance(solver.producer, SolverEvidenceReport):
        raise MutationContractError("M04 DifficultyAnalysis requires the authentic M03 solver adapter")
    if analysis.solver_evidence.digest != solver.producer.digest():
        raise MutationContractError("M04 DifficultyAnalysis is not bound to the authentic M03 solver evidence")
    _require_authority(analysis.authority, mutation, "M04")
    if analysis.challenge_score_digest != score.digest() or analysis.challenge_score_policy_version != score.policy_version:
        raise MutationContractError("M04 Challenge Score is not bound to DifficultyAnalysis")
    if score.source_metrics_digest != analysis.level_metrics_digest:
        raise MutationContractError("M04 Challenge Score source metrics are not bound to DifficultyAnalysis")
    status = EvidenceDisposition.AVAILABLE if analysis.disposition is AnalysisDisposition.AVAILABLE else EvidenceDisposition.UNAVAILABLE if analysis.disposition is AnalysisDisposition.UNAVAILABLE else EvidenceDisposition.INCONCLUSIVE
    record = _record("M04_DIFFICULTY", status, mutation, {"producer_schema": "scrubbots-difficulty-analysis", "producer_version": 1, "producer_digest": analysis.digest(), "challenge_score_digest": score.digest(), "challenge_score": float(score.score), "policy_version": score.policy_version})
    return AuthenticEvidenceAdapter("M04_DIFFICULTY", analysis, "scrubbots-difficulty-analysis", 1, record, analysis.digest())


def adapt_m05_qa(report: UnifiedQAReport, mutation: MutationResult) -> AuthenticEvidenceAdapter:
    if not isinstance(report, UnifiedQAReport):
        raise MutationContractError("M05 adapter requires UnifiedQAReport")
    source = _require_child_source(mutation)
    level_data = report.level_data
    if not level_data.has_exact_payload or level_data.level_id != _child_level_id(mutation):
        raise MutationContractError("M05 UnifiedQAReport is not bound to the exact mutation LevelData identity")
    if level_data.source_sha256 != source or level_data.level_data_sha256 != mutation.child.level_data_sha256:
        raise MutationContractError("M05 UnifiedQAReport source or LevelData digest is not bound to the mutation child")
    if not any(stage.disposition.value in {"PASS", "FAIL", "ERROR", "UNAVAILABLE", "INCONCLUSIVE"} for stage in report.stages):
        raise MutationContractError("M05 UnifiedQAReport stages are unavailable")
    authorities = [stage.authority.canonical_dict() for stage in report.stages]
    if not authorities or any(item.get("repository") != mutation.authority.repository or item.get("commit_sha") in (None, "UNAVAILABLE") for item in authorities) or len({json.dumps(item, sort_keys=True) for item in authorities}) != 1:
        raise MutationContractError("M05 UnifiedQAReport stages do not share one accepted authority identity")
    status_map = {UnifiedQADisposition.ACCEPT: EvidenceDisposition.PASS, UnifiedQADisposition.REJECT: EvidenceDisposition.REJECT, UnifiedQADisposition.INCONCLUSIVE: EvidenceDisposition.INCONCLUSIVE, UnifiedQADisposition.UNAVAILABLE: EvidenceDisposition.UNAVAILABLE, UnifiedQADisposition.ERROR: EvidenceDisposition.ERROR}
    status = status_map[report.disposition]
    record = _record("M05_QA", status, mutation, {"producer_schema": report.schema, "producer_version": report.version, "producer_digest": report.digest(), "disposition": report.disposition.value})
    return AuthenticEvidenceAdapter("M05_QA", report, report.schema, report.version, record, report.digest())


def revalidate_mutation_from_authentic_adapters(mutation: MutationResult, solver: AuthenticEvidenceAdapter, difficulty: AuthenticEvidenceAdapter, qa: AuthenticEvidenceAdapter) -> ValidationEnvelope:
    if not all(isinstance(item, AuthenticEvidenceAdapter) for item in (solver, difficulty, qa)):
        raise MutationContractError("production eligibility requires authentic M03/M04/M05 adapters")
    if (solver.stage, difficulty.stage, qa.stage) != ("M03_SOLVER", "M04_DIFFICULTY", "M05_QA"):
        raise MutationContractError("authentic producer stages are incomplete or reordered")
    if mutation.child is None:
        raise MutationContractError("authentic producer validation requires an applied child")
    for adapter in (solver, difficulty, qa):
        if adapter.record.child_state_digest != mutation.child.state_digest or adapter.record.request_digest != mutation.request_digest or adapter.record.parent_state_digest != mutation.parent.state_digest:
            raise MutationContractError("authentic producer record is not bound to the exact mutation child/request/parent")
        if adapter.producer_digest != getattr(adapter.producer, "digest")():
            raise MutationContractError("authentic producer digest drift")
    return revalidate_mutation(mutation, solver.record, difficulty.record, qa.record)


__all__ = ["AuthenticEvidenceAdapter", "adapt_m03_solver", "adapt_m04_difficulty", "adapt_m05_qa", "revalidate_mutation_from_authentic_adapters"]
