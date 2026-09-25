"""Closed M05 QA outcome semantics and truthful rejection statistics."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
import hashlib

from .solver_gate import SolverGateDisposition
from .unified import QAContractError, _canonical_bytes


QA_OUTCOME_SCHEMA = "scrubbots-qa-outcome-semantics"
QA_OUTCOME_VERSION = 1


class QAOutcome(str, Enum):
    ACCEPTABLE_SOLVER_PROOF = "ACCEPTABLE_SOLVER_PROOF"
    REJECT_PROVEN_UNSOLVABLE = "REJECT_PROVEN_UNSOLVABLE"
    INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED = "INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


QA_OUTCOME_CATALOG = tuple(item.value for item in QAOutcome)
QA_OUTCOME_REASON_CODES = frozenset({
    "ACCEPTABLE_SOLVER_PROOF", "REJECT_PROVEN_UNSOLVABLE", "INCONCLUSIVE", "UNKNOWN_BOUND",
    "TIMEOUT_BEFORE_RESULT", "UNAVAILABLE", "ERROR",
})


@dataclass(frozen=True, slots=True)
class QAOutcomeRecord:
    outcome: str
    reason_code: str

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, QAOutcome):
            try:
                object.__setattr__(self, "outcome", QAOutcome(self.outcome))
            except (TypeError, ValueError) as exc:
                raise QAContractError("unknown closed QA outcome") from exc
        if type(self.reason_code) is not str or self.reason_code not in QA_OUTCOME_REASON_CODES:
            raise QAContractError("unknown closed QA outcome")

    def canonical_dict(self) -> dict[str, str]:
        return {"outcome": self.outcome.value, "reason_code": self.reason_code}


@dataclass(frozen=True, slots=True)
class QAOutcomeStatistics:
    total: int
    counts: tuple[tuple[str, int], ...]
    schema: str = QA_OUTCOME_SCHEMA
    version: int = QA_OUTCOME_VERSION

    def __post_init__(self) -> None:
        if type(self.total) is not int or self.total < 0 or type(self.counts) is not tuple or self.schema != QA_OUTCOME_SCHEMA or self.version != QA_OUTCOME_VERSION:
            raise QAContractError("QA outcome statistics are malformed")
        keys = [key for key, _ in self.counts]
        if len(keys) != len(set(keys)) or any(not isinstance(key, QAOutcome) for key in keys) or sum(count for _, count in self.counts) != self.total or any(type(count) is not int or count < 0 for _, count in self.counts):
            raise QAContractError("QA outcome statistics do not sum to total")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "total": self.total, "counts": {key.value: value for key, value in self.counts}}

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
    selected_reason = reason_code or str(normalized)
    if selected_reason not in QA_OUTCOME_REASON_CODES:
        raise QAContractError("unknown closed QA outcome reason code")
    return QAOutcomeRecord(outcome, selected_reason)


def summarize_solver_qa(values: tuple[QAOutcomeRecord, ...] | list[QAOutcomeRecord]) -> QAOutcomeStatistics:
    records = tuple(values)
    if any(not isinstance(value, QAOutcomeRecord) for value in records):
        raise QAContractError("solver QA statistics require typed outcome records")
    counts = Counter(record.outcome for record in records)
    return QAOutcomeStatistics(len(records), tuple(sorted(counts.items(), key=lambda item: item[0].value)))


__all__ = ["QA_OUTCOME_SCHEMA", "QA_OUTCOME_VERSION", "QA_OUTCOME_CATALOG", "QA_OUTCOME_REASON_CODES", "QAOutcome", "QAOutcomeRecord", "QAOutcomeStatistics", "classify_solver_qa", "summarize_solver_qa"]
