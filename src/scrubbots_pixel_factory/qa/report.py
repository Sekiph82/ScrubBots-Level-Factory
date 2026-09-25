"""Closed canonical machine-readable M05 QA report."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib

from .unified import QAContractError, _canonical_bytes, _sha


QA_REPORT_SCHEMA = "scrubbots-machine-readable-qa-report"
QA_REPORT_VERSION = 1


class SemanticReviewDisposition(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    UNREVIEWED = "UNREVIEWED"


class QAReportDisposition(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


def _stage_value(value: object) -> str:
    return getattr(value, "value", value) if isinstance(getattr(value, "value", value), str) else str(value)


@dataclass(frozen=True, slots=True)
class MachineReadableQAReport:
    source_sha256: str
    level_data_digest: str
    logical_art_digest: str
    stages: tuple[tuple[str, str], ...]
    semantic_review: SemanticReviewDisposition
    reason_codes: tuple[str, ...]
    schema: str = QA_REPORT_SCHEMA
    version: int = QA_REPORT_VERSION

    def __post_init__(self) -> None:
        for value, label in ((self.source_sha256, "source SHA-256"), (self.level_data_digest, "Level Data digest"), (self.logical_art_digest, "logical art digest")):
            _sha(value, label)
        if type(self.stages) is not tuple or any(type(item) is not tuple or len(item) != 2 or not item[0] or not item[1] for item in self.stages):
            raise QAContractError("QA report stages are malformed")
        if not isinstance(self.semantic_review, SemanticReviewDisposition) or type(self.reason_codes) is not tuple:
            raise QAContractError("QA report semantic review or reasons are malformed")
        if any(type(reason) is not str or not reason.strip() for reason in self.reason_codes):
            raise QAContractError("QA report reason codes are malformed")
        if self.schema != QA_REPORT_SCHEMA or self.version != QA_REPORT_VERSION:
            raise QAContractError("unsupported QA report schema/version")

    @property
    def disposition(self) -> QAReportDisposition:
        values = {value for _, value in self.stages}
        if "ERROR" in values:
            return QAReportDisposition.ERROR
        if "FAIL" in values or "REJECT" in values or self.semantic_review is SemanticReviewDisposition.REJECT:
            return QAReportDisposition.REJECT
        if "INCONCLUSIVE" in values or self.semantic_review is SemanticReviewDisposition.UNREVIEWED:
            return QAReportDisposition.INCONCLUSIVE
        if "UNAVAILABLE" in values:
            return QAReportDisposition.UNAVAILABLE
        return QAReportDisposition.ACCEPT

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "source_sha256": self.source_sha256, "level_data_digest": self.level_data_digest, "logical_art_digest": self.logical_art_digest, "stages": {key: value for key, value in self.stages}, "semantic_review": self.semantic_review.value, "reason_codes": list(self.reason_codes), "disposition": self.disposition.value}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "MachineReadableQAReport":
        fields = {"schema", "version", "source_sha256", "level_data_digest", "logical_art_digest", "stages", "semantic_review", "reason_codes", "disposition"}
        if not isinstance(value, Mapping) or set(value) != fields or value.get("schema") != QA_REPORT_SCHEMA or value.get("version") != QA_REPORT_VERSION:
            raise QAContractError("QA report fields or schema/version are unsupported")
        stages = value["stages"]
        if not isinstance(stages, Mapping):
            raise QAContractError("QA report stages must be an object")
        try:
            semantic = SemanticReviewDisposition(value["semantic_review"])
        except (TypeError, ValueError) as exc:
            raise QAContractError("QA report semantic review is unsupported") from exc
        report = cls(value["source_sha256"], value["level_data_digest"], value["logical_art_digest"], tuple(sorted((str(key), str(item)) for key, item in stages.items())), semantic, tuple(value["reason_codes"]))
        if value["disposition"] != report.disposition.value:
            raise QAContractError("QA report disposition is caller-supplied or inconsistent")
        return report


def build_qa_report(*, source_sha256: str, level_data_digest: str, logical_art_digest: str, stages: Mapping[str, object], semantic_review: SemanticReviewDisposition, reason_codes: tuple[str, ...] = ()) -> MachineReadableQAReport:
    if not isinstance(stages, Mapping) or any(type(key) is not str for key in stages):
        raise QAContractError("QA report stages must be a string-keyed mapping")
    normalized = tuple(sorted((key, _stage_value(value)) for key, value in stages.items()))
    return MachineReadableQAReport(source_sha256, level_data_digest, logical_art_digest, normalized, semantic_review, tuple(reason_codes))


__all__ = ["QA_REPORT_SCHEMA", "QA_REPORT_VERSION", "MachineReadableQAReport", "QAReportDisposition", "SemanticReviewDisposition", "build_qa_report"]
