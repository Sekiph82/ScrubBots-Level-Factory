"""M05 solver QA gate over immutable M03 evidence receipts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib

from ..baseline_search import SearchExecutionDisposition, SearchVerdict
from ..solver_budget import OperationalSolverOutcome, SolverOutcomeDisposition
from ..solver_evidence import SolverEvidenceReport
from .unified import AuthorityIdentity, QAContractError, _canonical_bytes, _digest, _sha


SOLVER_GATE_SCHEMA = "scrubbots-authoritative-solver-qa-gate"
SOLVER_GATE_VERSION = 1


class SolverGateDisposition(str, Enum):
    ACCEPTABLE_SOLVER_PROOF = "ACCEPTABLE_SOLVER_PROOF"
    REJECT_PROVEN_UNSOLVABLE = "REJECT_PROVEN_UNSOLVABLE"
    INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED = "INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class SolverGateReport:
    disposition: SolverGateDisposition
    authority: AuthorityIdentity
    level_source_sha256: str
    solver_evidence_digest: str | None
    budget_identity_digest: str | None
    reason: str
    schema: str = SOLVER_GATE_SCHEMA
    version: int = SOLVER_GATE_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, SolverGateDisposition) or not isinstance(self.authority, AuthorityIdentity):
            raise QAContractError("solver gate identity is malformed")
        _sha(self.level_source_sha256, "solver gate level source SHA-256")
        for value, label in ((self.solver_evidence_digest, "solver evidence digest"), (self.budget_identity_digest, "budget identity digest")):
            if value is not None:
                _sha(value, label)
        if type(self.reason) is not str or not self.reason.strip():
            raise QAContractError("solver gate reason is required")
        if self.schema != SOLVER_GATE_SCHEMA or self.version != SOLVER_GATE_VERSION:
            raise QAContractError("unsupported solver gate schema/version")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "disposition": self.disposition.value, "authority": self.authority.canonical_dict(), "level_source_sha256": self.level_source_sha256, "solver_evidence_digest": self.solver_evidence_digest, "budget_identity_digest": self.budget_identity_digest, "reason": self.reason}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _report(disposition: SolverGateDisposition, authority: AuthorityIdentity, source: str, evidence: str | None, budget: str | None, reason: str) -> SolverGateReport:
    return SolverGateReport(disposition, authority, source, evidence, budget, reason)


def evaluate_solver_gate(
    evidence: SolverEvidenceReport | OperationalSolverOutcome | None,
    *,
    authority: AuthorityIdentity,
    level_source_sha256: str,
    expected_budget_identity_digest: str | None = None,
    evidence_authority: AuthorityIdentity | None = None,
) -> SolverGateReport:
    """Map exact M03 evidence to QA truth without creating new proof."""

    source = _sha(level_source_sha256, "solver gate level source SHA-256")
    if evidence_authority is not None and evidence_authority != authority:
        return _report(SolverGateDisposition.ERROR, authority, source, None, None, "solver evidence authority does not match the requested M03 authority")
    if expected_budget_identity_digest is not None:
        _sha(expected_budget_identity_digest, "expected budget identity digest")
    if evidence is None:
        return _report(SolverGateDisposition.UNAVAILABLE, authority, source, None, expected_budget_identity_digest, "M03 solver evidence is unavailable")
    if isinstance(evidence, OperationalSolverOutcome):
        if evidence.canonical_result is None:
            return _report(SolverGateDisposition.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED, authority, source, None, expected_budget_identity_digest, "operational execution produced no canonical solver result")
        outcome = evidence.canonical_result
        evidence_digest = outcome.digest()
        budget_digest = outcome.policy.digest()
        if expected_budget_identity_digest is not None and budget_digest != expected_budget_identity_digest:
            return _report(SolverGateDisposition.ERROR, authority, source, evidence_digest, budget_digest, "solver budget identity does not match the requested budget")
        return _map_budget_outcome(outcome.disposition, authority, source, evidence_digest, budget_digest, outcome.reason)
    if not isinstance(evidence, SolverEvidenceReport):
        return _report(SolverGateDisposition.ERROR, authority, source, None, expected_budget_identity_digest, "solver gate received an untyped evidence object")
    evidence_digest = evidence.digest()
    budget_digest = evidence.budget_policy.digest()
    if expected_budget_identity_digest is not None and budget_digest != expected_budget_identity_digest:
        return _report(SolverGateDisposition.ERROR, authority, source, evidence_digest, budget_digest, "solver budget identity does not match the requested budget")
    if evidence.execution is SearchExecutionDisposition.UNAVAILABLE:
        return _report(SolverGateDisposition.UNAVAILABLE, authority, source, evidence_digest, budget_digest, "M03 solver provider is unavailable")
    if evidence.execution is SearchExecutionDisposition.ERROR:
        return _report(SolverGateDisposition.ERROR, authority, source, evidence_digest, budget_digest, "M03 solver evidence reports an execution error")
    if evidence.budget_result is None:
        return _report(SolverGateDisposition.ERROR, authority, source, evidence_digest, budget_digest, "M03 evidence has no deterministic budget result")
    if evidence.result.verdict is SearchVerdict.PROVEN_UNSOLVABLE and evidence.budget_result.disposition is SolverOutcomeDisposition.PROVEN_UNSOLVABLE:
        return _report(SolverGateDisposition.REJECT_PROVEN_UNSOLVABLE, authority, source, evidence_digest, budget_digest, "exact authoritative M03 evidence proves unsolvability")
    if evidence.result.verdict is SearchVerdict.SOLVED and evidence.budget_result.disposition is SolverOutcomeDisposition.SOLVED:
        return _report(SolverGateDisposition.ACCEPTABLE_SOLVER_PROOF, authority, source, evidence_digest, budget_digest, "exact authoritative M03 solved evidence accepted")
    return _map_budget_outcome(evidence.budget_result.disposition, authority, source, evidence_digest, budget_digest, evidence.budget_result.reason)


def _map_budget_outcome(disposition: SolverOutcomeDisposition, authority: AuthorityIdentity, source: str, evidence: str, budget: str, reason: str) -> SolverGateReport:
    mapped = {
        SolverOutcomeDisposition.INCONCLUSIVE: SolverGateDisposition.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED,
        SolverOutcomeDisposition.UNAVAILABLE: SolverGateDisposition.UNAVAILABLE,
        SolverOutcomeDisposition.ERROR: SolverGateDisposition.ERROR,
        SolverOutcomeDisposition.SOLVED: SolverGateDisposition.ACCEPTABLE_SOLVER_PROOF,
        SolverOutcomeDisposition.PROVEN_UNSOLVABLE: SolverGateDisposition.REJECT_PROVEN_UNSOLVABLE,
    }[disposition]
    if mapped is SolverGateDisposition.REJECT_PROVEN_UNSOLVABLE:
        reason = "proven-unsolvable disposition requires matching authoritative PROVEN_UNSOLVABLE verdict"
        mapped = SolverGateDisposition.ERROR
    return _report(mapped, authority, source, evidence, budget, reason)


__all__ = ["SOLVER_GATE_SCHEMA", "SOLVER_GATE_VERSION", "SolverGateDisposition", "SolverGateReport", "evaluate_solver_gate"]
