"""Closed, canonical, provenance-bearing M05 QA evidence envelope."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib

from .unified import QAContractError, _canonical_bytes, _sha

QA_REPORT_SCHEMA = "scrubbots-machine-readable-qa-report"
QA_REPORT_VERSION = 1
QA_STAGE_ORDER = ("LEVEL_DATA", "SOURCE_PRESERVATION", "LEVEL_ART", "M09_ROUND_TRIP", "STRUCTURAL", "PRODUCTION", "FACTORY_PRODUCTION", "SOLVER", "DIFFICULTY", "SEMANTIC")
QA_STAGE_DISPOSITIONS = frozenset({"PASS", "FAIL", "INCONCLUSIVE", "UNAVAILABLE", "ERROR"})
QA_REASON_CODES = frozenset({"NONE", "AUTHORITY_DRIFT", "LINEAGE_MISMATCH", "PROVIDER_UNAVAILABLE", "PROVEN_UNSOLVABLE", "INCONCLUSIVE", "SEMANTIC_REVIEW_REQUIRED", "SOURCE_PRESERVATION_FAILED", "VALIDATION_FAILED", "ERROR"})


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
    candidate = getattr(value, "value", value)
    if hasattr(value, "disposition"):
        candidate = getattr(getattr(value, "disposition"), "value", getattr(value, "disposition"))
    if type(candidate) is not str or candidate not in QA_STAGE_DISPOSITIONS:
        raise QAContractError("QA report stage disposition is outside the closed catalog")
    return candidate


def _optional_sha(value: str | None, label: str) -> str | None:
    if value is None:
        return None
    return _sha(value, label)


@dataclass(frozen=True, slots=True)
class MachineReadableQAReport:
    source_sha256: str
    level_data_digest: str
    logical_art_digest: str
    stages: tuple[tuple[str, str], ...]
    semantic_review: SemanticReviewDisposition
    reason_codes: tuple[str, ...]
    main_game_authority_digest: str | None = None
    main_game_result_digest: str | None = None
    production_facts_digest: str | None = None
    solver_evidence_digest: str | None = None
    difficulty_analysis_digest: str | None = None
    difficulty_score_digest: str | None = None
    difficulty_lane_digest: str | None = None
    semantic_evidence_digest: str | None = None
    schema: str = QA_REPORT_SCHEMA
    version: int = QA_REPORT_VERSION

    def __post_init__(self) -> None:
        for value, label in ((self.source_sha256, "source SHA-256"), (self.level_data_digest, "Level Data digest"), (self.logical_art_digest, "logical art digest")):
            _sha(value, label)
        if type(self.stages) is not tuple or any(type(item) is not tuple or len(item) != 2 or item[0] not in QA_STAGE_ORDER for item in self.stages):
            raise QAContractError("QA report stages are malformed")
        keys = [key for key, _ in self.stages]
        if len(keys) != len(set(keys)) or tuple(key for key, _ in self.stages) != tuple(key for key in QA_STAGE_ORDER if key in keys):
            raise QAContractError("QA report stages must use the closed ordered catalog")
        if any(value not in QA_STAGE_DISPOSITIONS for _, value in self.stages):
            raise QAContractError("QA report stage disposition is unsupported")
        if not isinstance(self.semantic_review, SemanticReviewDisposition) or type(self.reason_codes) is not tuple or any(reason not in QA_REASON_CODES for reason in self.reason_codes):
            raise QAContractError("QA report semantic review or reason catalog is malformed")
        if self.schema != QA_REPORT_SCHEMA or self.version != QA_REPORT_VERSION:
            raise QAContractError("unsupported QA report schema/version")
        for value, label in ((self.main_game_authority_digest, "main-game authority digest"), (self.main_game_result_digest, "main-game result digest"), (self.production_facts_digest, "production facts digest"), (self.solver_evidence_digest, "solver evidence digest"), (self.difficulty_analysis_digest, "difficulty analysis digest"), (self.difficulty_score_digest, "difficulty score digest"), (self.difficulty_lane_digest, "difficulty lane digest"), (self.semantic_evidence_digest, "semantic evidence digest")):
            _optional_sha(value, label)
        stage_map = dict(self.stages)
        required = {
            "STRUCTURAL": self.main_game_authority_digest is not None and self.main_game_result_digest is not None,
            "PRODUCTION": self.production_facts_digest is not None,
            "SOLVER": self.solver_evidence_digest is not None,
            "DIFFICULTY": self.difficulty_analysis_digest is not None and self.difficulty_score_digest is not None and self.difficulty_lane_digest is not None,
            "SEMANTIC": self.semantic_evidence_digest is not None,
        }
        missing = [stage for stage, present in required.items() if stage_map.get(stage) == "PASS" and not present]
        if missing:
            raise QAContractError(f"QA report is missing required provenance identities for: {', '.join(missing)}")

    @property
    def disposition(self) -> QAReportDisposition:
        values = [value for _, value in self.stages]
        if "ERROR" in values:
            return QAReportDisposition.ERROR
        if "FAIL" in values or self.semantic_review is SemanticReviewDisposition.REJECT:
            return QAReportDisposition.REJECT
        if "INCONCLUSIVE" in values or self.semantic_review is SemanticReviewDisposition.UNREVIEWED:
            return QAReportDisposition.INCONCLUSIVE
        if "UNAVAILABLE" in values:
            return QAReportDisposition.UNAVAILABLE
        return QAReportDisposition.ACCEPT

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "source_sha256": self.source_sha256, "level_data_digest": self.level_data_digest, "logical_art_digest": self.logical_art_digest, "stages": {key: value for key, value in self.stages}, "semantic_review": self.semantic_review.value, "reason_codes": list(self.reason_codes), "main_game_authority_digest": self.main_game_authority_digest, "main_game_result_digest": self.main_game_result_digest, "production_facts_digest": self.production_facts_digest, "solver_evidence_digest": self.solver_evidence_digest, "difficulty_analysis_digest": self.difficulty_analysis_digest, "difficulty_score_digest": self.difficulty_score_digest, "difficulty_lane_digest": self.difficulty_lane_digest, "semantic_evidence_digest": self.semantic_evidence_digest, "disposition": self.disposition.value}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "MachineReadableQAReport":
        fields = set(cls.__dataclass_fields__) | {"disposition"}
        if not isinstance(value, Mapping) or set(value) != fields:
            raise QAContractError("QA report fields are unsupported or incomplete")
        if value.get("schema") != QA_REPORT_SCHEMA or value.get("version") != QA_REPORT_VERSION:
            raise QAContractError("QA report schema/version is unsupported")
        stages = value.get("stages")
        if not isinstance(stages, Mapping):
            raise QAContractError("QA report stages must be an object")
        try:
            semantic = SemanticReviewDisposition(value["semantic_review"])
        except (TypeError, ValueError) as exc:
            raise QAContractError("QA report semantic review is unsupported") from exc
        report = cls(value["source_sha256"], value["level_data_digest"], value["logical_art_digest"], tuple((key, _stage_value(item)) for key, item in stages.items()), semantic, tuple(value["reason_codes"]), value.get("main_game_authority_digest"), value.get("main_game_result_digest"), value.get("production_facts_digest"), value.get("solver_evidence_digest"), value.get("difficulty_analysis_digest"), value.get("difficulty_score_digest"), value.get("difficulty_lane_digest"), value.get("semantic_evidence_digest"), value["schema"], value["version"])
        if value.get("disposition") != report.disposition.value:
            raise QAContractError("QA report disposition is caller-supplied or inconsistent")
        return report


def build_qa_report(*, source_sha256: str, level_data_digest: str, logical_art_digest: str, stages: Mapping[str, object], semantic_review: SemanticReviewDisposition, reason_codes: tuple[str, ...] = (), main_game_authority_digest: str | None = None, main_game_result_digest: str | None = None, production_facts_digest: str | None = None, solver_evidence_digest: str | None = None, difficulty_analysis_digest: str | None = None, difficulty_score_digest: str | None = None, difficulty_lane_digest: str | None = None, semantic_evidence_digest: str | None = None) -> MachineReadableQAReport:
    if not isinstance(stages, Mapping) or any(type(key) is not str or key not in QA_STAGE_ORDER for key in stages):
        raise QAContractError("QA report stages contain an unknown stage")
    normalized = tuple((key, _stage_value(stages[key])) for key in QA_STAGE_ORDER if key in stages)
    return MachineReadableQAReport(source_sha256, level_data_digest, logical_art_digest, normalized, semantic_review, tuple(reason_codes), main_game_authority_digest, main_game_result_digest, production_facts_digest, solver_evidence_digest, difficulty_analysis_digest, difficulty_score_digest, difficulty_lane_digest, semantic_evidence_digest)


__all__ = ["QA_REPORT_SCHEMA", "QA_REPORT_VERSION", "QA_STAGE_ORDER", "QA_STAGE_DISPOSITIONS", "QA_REASON_CODES", "MachineReadableQAReport", "QAReportDisposition", "SemanticReviewDisposition", "build_qa_report"]
