"""Validation-only Factory to main-game acceptance handoff package."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable
import hashlib

from .report import MachineReadableQAReport, QAReportDisposition
from .unified import AuthorityIdentity, QAContractError, _canonical_bytes, _sha


HANDOFF_SCHEMA = "scrubbots-main-game-acceptance-handoff"
HANDOFF_VERSION = 1


@dataclass(frozen=True, slots=True)
class HandoffValidationReceipt:
    disposition: str
    authority: AuthorityIdentity
    evidence_digest: str
    reason: str

    def __post_init__(self) -> None:
        if self.disposition not in {"PASS", "FAIL", "UNAVAILABLE", "ERROR"} or not isinstance(self.authority, AuthorityIdentity):
            raise QAContractError("handoff validation receipt is malformed")
        _sha(self.evidence_digest, "handoff validation evidence digest")
        if type(self.reason) is not str or not self.reason.strip():
            raise QAContractError("handoff validation reason is required")


@runtime_checkable
class MainGameAcceptanceProvider(Protocol):
    def validate_handoff(self, handoff: "MainGameAcceptanceHandoff") -> HandoffValidationReceipt:
        """Validate without mutating the main-game checkout or catalog."""


@dataclass(frozen=True, slots=True)
class MainGameAcceptanceHandoff:
    level_data_sha256: str
    logical_art_png_sha256: str
    source_provenance_sha256: str
    qa_report_digest: str
    solver_evidence_digest: str
    difficulty_analysis_digest: str
    semantic_evidence_digest: str
    factory_schema: str
    factory_version: int
    main_game_authority: AuthorityIdentity
    disposition: str
    validation_evidence_digest: str | None
    validation_reason: str
    downstream_gates: tuple[tuple[str, str], ...] = (("M30_COMPATIBLE", "PASS"), ("M47_ANDROID_DEVICE_TESTING", "PENDING"), ("M48_IOS_READINESS", "PENDING"))
    schema: str = HANDOFF_SCHEMA
    version: int = HANDOFF_VERSION

    def __post_init__(self) -> None:
        for value, label in ((self.level_data_sha256, "Level Data SHA-256"), (self.logical_art_png_sha256, "logical-art PNG SHA-256"), (self.source_provenance_sha256, "source provenance SHA-256"), (self.qa_report_digest, "QA report digest"), (self.solver_evidence_digest, "solver evidence digest"), (self.difficulty_analysis_digest, "difficulty analysis digest"), (self.semantic_evidence_digest, "semantic evidence digest")):
            _sha(value, label)
        if type(self.factory_schema) is not str or not self.factory_schema.strip() or type(self.factory_version) is not int or self.factory_version < 1:
            raise QAContractError("Factory schema/version is malformed")
        if not isinstance(self.main_game_authority, AuthorityIdentity):
            raise QAContractError("main-game authority is malformed")
        if self.disposition not in {"ELIGIBLE_FOR_MAIN_GAME_ACCEPTANCE_HANDOFF", "NOT_ELIGIBLE", "UNAVAILABLE", "ERROR"}:
            raise QAContractError("handoff disposition is closed")
        if self.validation_evidence_digest is not None:
            _sha(self.validation_evidence_digest, "handoff validation evidence digest")
        if type(self.validation_reason) is not str or not self.validation_reason.strip() or tuple(key for key, _ in self.downstream_gates) != ("M30_COMPATIBLE", "M47_ANDROID_DEVICE_TESTING", "M48_IOS_READINESS"):
            raise QAContractError("handoff downstream gates are malformed")
        if self.downstream_gates[1][1] != "PENDING" or self.downstream_gates[2][1] != "PENDING":
            raise QAContractError("M47/M48 cannot be marked passed by Factory QA")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "level_data_sha256": self.level_data_sha256, "logical_art_png_sha256": self.logical_art_png_sha256, "source_provenance_sha256": self.source_provenance_sha256, "qa_report_digest": self.qa_report_digest, "solver_evidence_digest": self.solver_evidence_digest, "difficulty_analysis_digest": self.difficulty_analysis_digest, "semantic_evidence_digest": self.semantic_evidence_digest, "factory": {"schema": self.factory_schema, "version": self.factory_version}, "main_game_authority": self.main_game_authority.canonical_dict(), "disposition": self.disposition, "validation_evidence_digest": self.validation_evidence_digest, "validation_reason": self.validation_reason, "downstream_gates": {key: value for key, value in self.downstream_gates}}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def build_main_game_handoff(
    *,
    level_data_sha256: str,
    logical_art_png_sha256: str,
    source_provenance_sha256: str,
    qa_report: MachineReadableQAReport,
    solver_evidence_digest: str,
    difficulty_analysis_digest: str,
    semantic_evidence_digest: str,
    factory_schema: str,
    factory_version: int,
    main_game_authority: AuthorityIdentity,
    provider: MainGameAcceptanceProvider | object | None,
) -> MainGameAcceptanceHandoff:
    """Build and optionally validate an immutable, validation-only handoff."""

    for value, label in ((level_data_sha256, "Level Data SHA-256"), (logical_art_png_sha256, "logical-art PNG SHA-256"), (source_provenance_sha256, "source provenance SHA-256"), (solver_evidence_digest, "solver evidence digest"), (difficulty_analysis_digest, "difficulty analysis digest"), (semantic_evidence_digest, "semantic evidence digest")):
        _sha(value, label)
    if not isinstance(qa_report, MachineReadableQAReport):
        raise QAContractError("MachineReadableQAReport is required")
    if qa_report.disposition is not QAReportDisposition.ACCEPT:
        return MainGameAcceptanceHandoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report.digest(), solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, main_game_authority, "NOT_ELIGIBLE", None, "Factory QA report is not ACCEPT; no main-game validation was attempted")
    provisional = MainGameAcceptanceHandoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report.digest(), solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, main_game_authority, "UNAVAILABLE" if provider is None else "ERROR", None, "main-game validation capability is unavailable" if provider is None else "main-game validation pending")
    if provider is None:
        return provisional
    try:
        method = getattr(provider, "validate_handoff", None)
        if not callable(method):
            raise QAContractError("main-game handoff provider must expose validate_handoff")
        receipt = method(provisional)
        if not isinstance(receipt, HandoffValidationReceipt):
            raise QAContractError("main-game handoff provider returned an untyped receipt")
        if receipt.authority != main_game_authority:
            return MainGameAcceptanceHandoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report.digest(), solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, main_game_authority, "ERROR", receipt.evidence_digest, "main-game authority SHA does not match the requested handoff authority")
        disposition = "ELIGIBLE_FOR_MAIN_GAME_ACCEPTANCE_HANDOFF" if receipt.disposition == "PASS" else "NOT_ELIGIBLE" if receipt.disposition == "FAIL" else receipt.disposition
        return MainGameAcceptanceHandoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report.digest(), solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, main_game_authority, disposition, receipt.evidence_digest, receipt.reason)
    except Exception as exc:
        return MainGameAcceptanceHandoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report.digest(), solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, main_game_authority, "ERROR", None, f"main-game handoff validation failed closed: {exc}")


__all__ = ["HANDOFF_SCHEMA", "HANDOFF_VERSION", "HandoffValidationReceipt", "MainGameAcceptanceHandoff", "MainGameAcceptanceProvider", "build_main_game_handoff"]
