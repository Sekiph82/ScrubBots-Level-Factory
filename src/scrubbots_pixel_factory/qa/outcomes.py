"""Closed M05 QA outcome semantics and truthful rejection statistics."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib

from .solver_gate import SolverGateDisposition
from .unified import QAContractError, _canonical_bytes


QA_OUTCOME_SCHEMA = "scrubbots-qa-outcome-semantics"
QA_OUTCOME_VERSION = 1


class QAOutcome(str):
    ACCEPTABLE_SOLVER_PROOF = "ACCEPTABLE_SOLVER_PROOF"
    REJECT_PROVEN_UNSOLVABLE = "REJECT_PROVEN_UNSOLVABLE"
    INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED = "INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class QAOutcomeRecord:
    outcome: str
    reason_code: str

    def __post_init__(self) -> None:
        if self.outcome not in {value for value in QAOutcome.__dict__.values() if isinstance(value, str)}:
            raise QAContractError("unknown closed QA outcome")
        if type(self.reason_code) is not str or not self.reason_code.strip():
            raise QAContractError("QA outcome reason_code is required")

    def canonical_dict(self) -> dict[str, str]:
        return {"outcome": self.outcome, "reason_code": self.reason_code}


@dataclass(frozen=True, slots=True)
class QAOutcomeStatistics:
    total: int
    counts: tuple[tuple[str, int], ...]
    schema: str = QA_OUTCOME_SCHEMA
    version: int = QA_OUTCOME_VERSION

    def __post_init__(self) -> None:
        if type(self.total) is not int or self.total < 0 or type(self.counts) is not tuple:
            raise QAContractError("QA outcome statistics are malformed")
        if sum(count for _, count in self.counts) != self.total or any(type(count) is not int or count < 0 for _, count in self.counts):
            raise QAContractError("QA outcome statistics do not sum to total")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "total": self.total, "counts": {key: value for key, value in self.counts}}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def classify_solver_qa(value: SolverGateDisposition | str, *, reason_code: str | None = None) -> QAOutcomeRecord:
    """Map solver gate truth without collapsing inconclusive into rejection."""

    normalized = value.value if isinstance(value, SolverGateDisposition) else value
    mapping = {
        SolverGateDisposition.ACCEPTABLE_SOLVER_PROOF.value: QAOutcome.ACCEPTABLE_SOLVER_PROOF,
        SolverGateDisposition.REJECT_PROVEN_UNSOLVABLE.value: QAOutcome.REJECT_PROVEN_UNSOLVABLE,
        SolverGateDisposition.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED.value: QAOutcome.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED,
        SolverGateDisposition.UNAVAILABLE.value: QAOutcome.UNAVAILABLE,
        SolverGateDisposition.ERROR.value: QAOutcome.ERROR,
        "UNKNOWN_BOUND": QAOutcome.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED,
        "TIMEOUT_BEFORE_RESULT": QAOutcome.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED,
        "INCONCLUSIVE": QAOutcome.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED,
    }
    try:
        outcome = mapping[str(normalized)]
    except KeyError as exc:
        raise QAContractError("unknown solver QA disposition") from exc
    return QAOutcomeRecord(outcome, reason_code or str(normalized))


def summarize_solver_qa(values: tuple[QAOutcomeRecord, ...] | list[QAOutcomeRecord]) -> QAOutcomeStatistics:
    records = tuple(values)
    if any(not isinstance(value, QAOutcomeRecord) for value in records):
        raise QAContractError("solver QA statistics require typed outcome records")
    counts = Counter(record.outcome for record in records)
    return QAOutcomeStatistics(len(records), tuple(sorted(counts.items())))


__all__ = ["QA_OUTCOME_SCHEMA", "QA_OUTCOME_VERSION", "QAOutcome", "QAOutcomeRecord", "QAOutcomeStatistics", "classify_solver_qa", "summarize_solver_qa"]
