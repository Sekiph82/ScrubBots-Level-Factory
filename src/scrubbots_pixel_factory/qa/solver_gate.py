"""M05 solver QA gate over provenance-bearing M03 evidence receipts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib

from ..baseline_search import SearchExecutionDisposition, SearchVerdict
from ..solver_budget import OperationalSolverOutcome, SolverOutcomeDisposition
from ..solver_evidence import SolverEvidenceReport
from .unified import AuthorityIdentity, QAContractError, _canonical_bytes, _sha

SOLVER_GATE_SCHEMA = "scrubbots-authoritative-solver-qa-gate"
SOLVER_GATE_VERSION = 1


class SolverGateDisposition(str, Enum):
    ACCEPTABLE_SOLVER_PROOF = "ACCEPTABLE_SOLVER_PROOF"
    REJECT_PROVEN_UNSOLVABLE = "REJECT_PROVEN_UNSOLVABLE"
    INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED = "INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class SolverEvidenceProvenance:
    level_id: str
    level_source_sha256: str
    request_id: str
    authority: AuthorityIdentity
    provider_id: str
    provider_version: str
    evidence_digest: str
    budget_identity_digest: str
    state_digest: str | None = None

    def __post_init__(self) -> None:
        for value, label in ((self.level_id, "solver level_id"), (self.request_id, "solver request_id"), (self.provider_id, "solver provider_id"), (self.provider_version, "solver provider_version")):
            if type(value) is not str or not value.strip():
                raise QAContractError(f"{label} is malformed")
        if not isinstance(self.authority, AuthorityIdentity):
            raise QAContractError("solver evidence authority is malformed")
        _sha(self.level_source_sha256, "solver provenance source SHA-256")
        _sha(self.evidence_digest, "solver provenance evidence digest")
        _sha(self.budget_identity_digest, "solver provenance budget digest")
        if self.state_digest is not None:
            _sha(self.state_digest, "solver provenance state digest")

    def canonical_dict(self) -> dict[str, object]:
        return {"level_id": self.level_id, "level_source_sha256": self.level_source_sha256, "request_id": self.request_id, "authority": self.authority.canonical_dict(), "provider_id": self.provider_id, "provider_version": self.provider_version, "evidence_digest": self.evidence_digest, "budget_identity_digest": self.budget_identity_digest, "state_digest": self.state_digest}


SolverEvidenceEnvelope = SolverEvidenceProvenance


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
    level_id: str | None = None
    request_id: str | None = None
    state_digest: str | None = None
    provider_id: str | None = None
    provider_version: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, SolverGateDisposition) or not isinstance(self.authority, AuthorityIdentity):
            raise QAContractError("solver gate identity is malformed")
        _sha(self.level_source_sha256, "solver gate level source SHA-256")
        for value, label in ((self.solver_evidence_digest, "solver evidence digest"), (self.budget_identity_digest, "budget identity digest"), (self.state_digest, "solver state digest")):
            if value is not None:
                _sha(value, label)
        if type(self.reason) is not str or not self.reason.strip() or self.schema != SOLVER_GATE_SCHEMA or self.version != SOLVER_GATE_VERSION:
            raise QAContractError("solver gate report is malformed")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "disposition": self.disposition.value, "authority": self.authority.canonical_dict(), "level_source_sha256": self.level_source_sha256, "solver_evidence_digest": self.solver_evidence_digest, "budget_identity_digest": self.budget_identity_digest, "level_id": self.level_id, "request_id": self.request_id, "state_digest": self.state_digest, "provider_id": self.provider_id, "provider_version": self.provider_version, "reason": self.reason}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _report(disposition: SolverGateDisposition, authority: AuthorityIdentity, source: str, evidence: str | None, budget: str | None, reason: str, provenance: SolverEvidenceProvenance | None = None) -> SolverGateReport:
    return SolverGateReport(disposition, authority, source, evidence, budget, reason, level_id=provenance.level_id if provenance else None, request_id=provenance.request_id if provenance else None, state_digest=provenance.state_digest if provenance else None, provider_id=provenance.provider_id if provenance else None, provider_version=provenance.provider_version if provenance else None)


def _provenance_from_evidence(evidence: object, authority: AuthorityIdentity, source: str) -> SolverEvidenceProvenance | None:
    if not isinstance(evidence, SolverEvidenceReport):
        return None
    values = (getattr(evidence, "level_id", None), getattr(evidence, "level_source_sha256", None), getattr(evidence, "request_id", None), getattr(evidence, "authority", None), getattr(evidence, "provider_id", None), getattr(evidence, "provider_version", None))
    if any(value is None for value in values):
        return None
    return SolverEvidenceProvenance(values[0], values[1], values[2], values[3], values[4], values[5], evidence.digest(), evidence.budget_policy.digest(), getattr(evidence, "state_digest", None))


def evaluate_solver_gate(evidence: SolverEvidenceReport | OperationalSolverOutcome | None, *, authority: AuthorityIdentity, level_source_sha256: str, expected_budget_identity_digest: str | None = None, evidence_authority: AuthorityIdentity | None = None, level_id: str | None = None, request_id: str | None = None, expected_state_digest: str | None = None, expected_provider_id: str | None = None, expected_provider_version: str | None = None, evidence_provenance: SolverEvidenceProvenance | None = None) -> SolverGateReport:
    source = _sha(level_source_sha256, "solver gate level source SHA-256")
    if evidence_authority is not None and evidence_authority != authority:
        return _report(SolverGateDisposition.ERROR, authority, source, None, None, "solver evidence authority does not match requested M03 authority")
    if expected_budget_identity_digest is not None:
        _sha(expected_budget_identity_digest, "expected budget identity digest")
    if expected_state_digest is not None:
        _sha(expected_state_digest, "expected solver state digest")
    if evidence_provenance is not None and not isinstance(evidence_provenance, SolverEvidenceProvenance):
        return _report(SolverGateDisposition.ERROR, authority, source, None, expected_budget_identity_digest, "solver evidence provenance envelope is malformed")
    if evidence_provenance is None and (level_id is not None or request_id is not None or expected_state_digest is not None or expected_provider_id is not None or expected_provider_version is not None):
        evidence_provenance = _provenance_from_evidence(evidence, authority, source)
        if evidence_provenance is None:
            return _report(SolverGateDisposition.ERROR, authority, source, evidence.digest() if hasattr(evidence, "digest") else None, expected_budget_identity_digest, "solver evidence lacks exact level/source/request provenance")
    if evidence_provenance is not None and (evidence_provenance.authority != authority or evidence_provenance.level_source_sha256 != source or (level_id is not None and evidence_provenance.level_id != level_id) or (request_id is not None and evidence_provenance.request_id != request_id) or (expected_state_digest is not None and evidence_provenance.state_digest != expected_state_digest) or (expected_budget_identity_digest is not None and evidence_provenance.budget_identity_digest != expected_budget_identity_digest) or (expected_provider_id is not None and evidence_provenance.provider_id != expected_provider_id) or (expected_provider_version is not None and evidence_provenance.provider_version != expected_provider_version)):
        return _report(SolverGateDisposition.ERROR, authority, source, evidence_provenance.evidence_digest, evidence_provenance.budget_identity_digest, "solver evidence provenance does not match requested identity", evidence_provenance)
    if evidence is None:
        return _report(SolverGateDisposition.UNAVAILABLE, authority, source, None, expected_budget_identity_digest, "M03 solver evidence is unavailable", evidence_provenance)
    if isinstance(evidence, OperationalSolverOutcome):
        if evidence.canonical_result is None:
            return _report(SolverGateDisposition.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED, authority, source, None, expected_budget_identity_digest, "operational execution produced no canonical solver result", evidence_provenance)
        outcome = evidence.canonical_result
        evidence_digest, budget_digest = outcome.digest(), outcome.policy.digest()
        if evidence_provenance is not None and (evidence_provenance.evidence_digest != evidence_digest or evidence_provenance.budget_identity_digest != budget_digest):
            return _report(SolverGateDisposition.ERROR, authority, source, evidence_digest, budget_digest, "solver evidence envelope digest does not match canonical operational result", evidence_provenance)
        if expected_budget_identity_digest is not None and budget_digest != expected_budget_identity_digest:
            return _report(SolverGateDisposition.ERROR, authority, source, evidence_digest, budget_digest, "solver budget identity does not match requested budget", evidence_provenance)
        return _map_budget_outcome(outcome.disposition, authority, source, evidence_digest, budget_digest, outcome.reason, evidence_provenance)
    if not isinstance(evidence, SolverEvidenceReport):
        return _report(SolverGateDisposition.ERROR, authority, source, None, expected_budget_identity_digest, "solver gate received an untyped evidence object", evidence_provenance)
    evidence_digest, budget_digest = evidence.digest(), evidence.budget_policy.digest()
    if evidence_provenance is not None and (evidence_provenance.evidence_digest != evidence_digest or evidence_provenance.budget_identity_digest != budget_digest):
        return _report(SolverGateDisposition.ERROR, authority, source, evidence_digest, budget_digest, "solver evidence envelope digest does not match canonical M03 evidence", evidence_provenance)
    if expected_budget_identity_digest is not None and budget_digest != expected_budget_identity_digest:
        return _report(SolverGateDisposition.ERROR, authority, source, evidence_digest, budget_digest, "solver budget identity does not match requested budget", evidence_provenance)
    if evidence.execution is SearchExecutionDisposition.UNAVAILABLE:
        return _report(SolverGateDisposition.UNAVAILABLE, authority, source, evidence_digest, budget_digest, "M03 solver provider is unavailable", evidence_provenance)
    if evidence.execution is SearchExecutionDisposition.ERROR:
        return _report(SolverGateDisposition.ERROR, authority, source, evidence_digest, budget_digest, "M03 solver evidence reports an execution error", evidence_provenance)
    if evidence.budget_result is None:
        return _report(SolverGateDisposition.ERROR, authority, source, evidence_digest, budget_digest, "M03 evidence has no deterministic budget result", evidence_provenance)
    if evidence.result.verdict is SearchVerdict.PROVEN_UNSOLVABLE and evidence.budget_result.disposition is SolverOutcomeDisposition.PROVEN_UNSOLVABLE:
        return _report(SolverGateDisposition.REJECT_PROVEN_UNSOLVABLE, authority, source, evidence_digest, budget_digest, "exact authoritative M03 evidence proves unsolvability", evidence_provenance)
    if evidence.result.verdict is SearchVerdict.SOLVED and evidence.budget_result.disposition is SolverOutcomeDisposition.SOLVED:
        return _report(SolverGateDisposition.ACCEPTABLE_SOLVER_PROOF, authority, source, evidence_digest, budget_digest, "exact authoritative M03 solved evidence accepted", evidence_provenance)
    return _map_budget_outcome(evidence.budget_result.disposition, authority, source, evidence_digest, budget_digest, evidence.budget_result.reason, evidence_provenance)


def _map_budget_outcome(disposition: SolverOutcomeDisposition, authority: AuthorityIdentity, source: str, evidence: str, budget: str, reason: str, provenance: SolverEvidenceProvenance | None = None) -> SolverGateReport:
    mapped = {SolverOutcomeDisposition.INCONCLUSIVE: SolverGateDisposition.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED, SolverOutcomeDisposition.UNAVAILABLE: SolverGateDisposition.UNAVAILABLE, SolverOutcomeDisposition.ERROR: SolverGateDisposition.ERROR, SolverOutcomeDisposition.SOLVED: SolverGateDisposition.ACCEPTABLE_SOLVER_PROOF, SolverOutcomeDisposition.PROVEN_UNSOLVABLE: SolverGateDisposition.ERROR}[disposition]
    if mapped is SolverGateDisposition.ERROR and disposition is SolverOutcomeDisposition.PROVEN_UNSOLVABLE:
        reason = "proven-unsolvable disposition requires matching authoritative PROVEN_UNSOLVABLE verdict"
    return _report(mapped, authority, source, evidence, budget, reason, provenance)


__all__ = ["SOLVER_GATE_SCHEMA", "SOLVER_GATE_VERSION", "SolverEvidenceEnvelope", "SolverEvidenceProvenance", "SolverGateDisposition", "SolverGateReport", "evaluate_solver_gate"]
