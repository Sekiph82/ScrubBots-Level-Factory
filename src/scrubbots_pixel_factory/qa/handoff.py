"""Validation-only Factory to current main-game acceptance handoff."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable
import hashlib

from .report import MachineReadableQAReport, QAReportDisposition
from .unified import AuthorityIdentity, QAContractError, _canonical_bytes, _sha

HANDOFF_SCHEMA = "scrubbots-main-game-acceptance-handoff"
HANDOFF_VERSION = 2


@dataclass(frozen=True, slots=True)
class CurrentMainResolution:
    disposition: str
    authority: AuthorityIdentity
    clean_checkout: bool
    reason: str

    def __post_init__(self) -> None:
        if self.disposition not in {"RESOLVED", "UNAVAILABLE", "ERROR"} or not isinstance(self.authority, AuthorityIdentity) or type(self.clean_checkout) is not bool or type(self.reason) is not str or not self.reason.strip():
            raise QAContractError("current main resolution is malformed")

    def canonical_dict(self) -> dict[str, object]:
        return {"disposition": self.disposition, "authority": self.authority.canonical_dict(), "clean_checkout": self.clean_checkout, "reason": self.reason}


@runtime_checkable
class CurrentMainResolver(Protocol):
    def resolve_current_main(self) -> CurrentMainResolution:
        """Resolve and pin the current canonical main-game checkout read-only."""


@dataclass(frozen=True, slots=True)
class HandoffValidationReceipt:
    disposition: str
    authority: AuthorityIdentity
    evidence_digest: str
    reason: str
    level_data_sha256: str | None = None
    logical_art_png_sha256: str | None = None
    source_provenance_sha256: str | None = None
    qa_report_digest: str | None = None
    solver_evidence_digest: str | None = None
    difficulty_analysis_digest: str | None = None
    semantic_evidence_digest: str | None = None
    current_main_sha: str | None = None
    level_validator_passed: bool | None = None
    production_validator_passed: bool | None = None
    m09_round_trip_passed: bool | None = None
    clean_checkout: bool | None = None
    non_mutating: bool | None = None

    def __post_init__(self) -> None:
        if self.disposition not in {"PASS", "FAIL", "UNAVAILABLE", "ERROR"} or not isinstance(self.authority, AuthorityIdentity):
            raise QAContractError("handoff validation receipt is malformed")
        _sha(self.evidence_digest, "handoff validation evidence digest")
        if type(self.reason) is not str or not self.reason.strip():
            raise QAContractError("handoff validation reason is required")
        for value, label in ((self.level_data_sha256, "handoff LevelData SHA-256"), (self.logical_art_png_sha256, "handoff logical-art SHA-256"), (self.source_provenance_sha256, "handoff source provenance SHA-256"), (self.qa_report_digest, "handoff QA report digest"), (self.solver_evidence_digest, "handoff solver digest"), (self.difficulty_analysis_digest, "handoff difficulty digest"), (self.semantic_evidence_digest, "handoff semantic digest")):
            if value is not None:
                _sha(value, label)
        if self.current_main_sha is not None and (type(self.current_main_sha) is not str or len(self.current_main_sha) < 7):
            raise QAContractError("handoff current-main SHA is malformed")
        for value, label in ((self.level_validator_passed, "LevelValidator proof"), (self.production_validator_passed, "ProductionLevelValidator proof"), (self.m09_round_trip_passed, "M09 proof"), (self.clean_checkout, "clean checkout proof"), (self.non_mutating, "non-mutation proof")):
            if value is not None and type(value) is not bool:
                raise QAContractError(f"{label} is malformed")


@runtime_checkable
class MainGameAcceptanceProvider(Protocol):
    def validate_handoff(self, handoff: "MainGameAcceptanceHandoff") -> HandoffValidationReceipt:
        """Validate without mutating main-game checkout or catalog."""


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
    downstream_gates: tuple[tuple[str, str], ...] = (("M30_COMPATIBLE", "PENDING"), ("M47_ANDROID_DEVICE_TESTING", "PENDING"), ("M48_IOS_READINESS", "PENDING"))
    schema: str = HANDOFF_SCHEMA
    version: int = HANDOFF_VERSION

    def __post_init__(self) -> None:
        for value, label in ((self.level_data_sha256, "Level Data SHA-256"), (self.logical_art_png_sha256, "logical-art PNG SHA-256"), (self.source_provenance_sha256, "source provenance SHA-256"), (self.qa_report_digest, "QA report digest"), (self.solver_evidence_digest, "solver evidence digest"), (self.difficulty_analysis_digest, "difficulty analysis digest"), (self.semantic_evidence_digest, "semantic evidence digest")):
            _sha(value, label)
        if type(self.factory_schema) is not str or not self.factory_schema.strip() or type(self.factory_version) is not int or self.factory_version < 1 or not isinstance(self.main_game_authority, AuthorityIdentity):
            raise QAContractError("Factory/handoff identity is malformed")
        if self.disposition not in {"ELIGIBLE_FOR_MAIN_GAME_ACCEPTANCE_HANDOFF", "NOT_ELIGIBLE", "UNAVAILABLE", "ERROR"} or (self.validation_evidence_digest is not None and not isinstance(self.validation_evidence_digest, str)) or type(self.validation_reason) is not str or not self.validation_reason.strip():
            raise QAContractError("handoff disposition/evidence is malformed")
        if self.validation_evidence_digest is not None:
            _sha(self.validation_evidence_digest, "handoff validation evidence digest")
        if tuple(key for key, _ in self.downstream_gates) != ("M30_COMPATIBLE", "M47_ANDROID_DEVICE_TESTING", "M48_IOS_READINESS") or self.downstream_gates[1][1] != "PENDING" or self.downstream_gates[2][1] != "PENDING" or self.downstream_gates[0][1] not in {"PASS", "PENDING"}:
            raise QAContractError("handoff downstream gates are malformed")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "level_data_sha256": self.level_data_sha256, "logical_art_png_sha256": self.logical_art_png_sha256, "source_provenance_sha256": self.source_provenance_sha256, "qa_report_digest": self.qa_report_digest, "solver_evidence_digest": self.solver_evidence_digest, "difficulty_analysis_digest": self.difficulty_analysis_digest, "semantic_evidence_digest": self.semantic_evidence_digest, "factory": {"schema": self.factory_schema, "version": self.factory_version}, "main_game_authority": self.main_game_authority.canonical_dict(), "disposition": self.disposition, "validation_evidence_digest": self.validation_evidence_digest, "validation_reason": self.validation_reason, "downstream_gates": {key: value for key, value in self.downstream_gates}}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _handoff(level_data_sha256: str, logical_art_png_sha256: str, source_provenance_sha256: str, qa_report: MachineReadableQAReport, solver_evidence_digest: str, difficulty_analysis_digest: str, semantic_evidence_digest: str, factory_schema: str, factory_version: int, authority: AuthorityIdentity, disposition: str, evidence: str | None, reason: str, m30: str) -> MainGameAcceptanceHandoff:
    return MainGameAcceptanceHandoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report.digest(), solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, authority, disposition, evidence, reason, (("M30_COMPATIBLE", m30), ("M47_ANDROID_DEVICE_TESTING", "PENDING"), ("M48_IOS_READINESS", "PENDING")))


def build_main_game_handoff(*, level_data_sha256: str, logical_art_png_sha256: str, source_provenance_sha256: str, qa_report: MachineReadableQAReport, solver_evidence_digest: str, difficulty_analysis_digest: str, semantic_evidence_digest: str, factory_schema: str, factory_version: int, main_game_authority: AuthorityIdentity | None = None, provider: MainGameAcceptanceProvider | object | None, main_game_resolver: CurrentMainResolver | object | None = None) -> MainGameAcceptanceHandoff:
    for value, label in ((level_data_sha256, "Level Data SHA-256"), (logical_art_png_sha256, "logical-art PNG SHA-256"), (source_provenance_sha256, "source provenance SHA-256"), (solver_evidence_digest, "solver evidence digest"), (difficulty_analysis_digest, "difficulty analysis digest"), (semantic_evidence_digest, "semantic evidence digest")):
        _sha(value, label)
    if not isinstance(qa_report, MachineReadableQAReport):
        raise QAContractError("MachineReadableQAReport is required")
    if qa_report.disposition is not QAReportDisposition.ACCEPT:
        authority = main_game_authority or AuthorityIdentity("https://github.com/Sekiph82/Scrubbots", "UNAVAILABLE", "main-game/main", "UNAVAILABLE")
        return _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, authority, "NOT_ELIGIBLE", None, "Factory QA report is not ACCEPT; no main-game validation was attempted", "PENDING")
    if (qa_report.level_data_digest != level_data_sha256 or qa_report.logical_art_digest != logical_art_png_sha256 or qa_report.source_sha256 != source_provenance_sha256):
        authority = main_game_authority or AuthorityIdentity("https://github.com/Sekiph82/Scrubbots", "UNAVAILABLE", "main-game/main", "UNAVAILABLE")
        return _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, authority, "ERROR", None, "handoff hashes are not cross-bound to QA report identities", "PENDING")
    if ((qa_report.solver_evidence_digest is not None and qa_report.solver_evidence_digest != solver_evidence_digest) or (qa_report.difficulty_analysis_digest is not None and qa_report.difficulty_analysis_digest != difficulty_analysis_digest) or (qa_report.semantic_evidence_digest is not None and qa_report.semantic_evidence_digest != semantic_evidence_digest)):
        return _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, main_game_authority or AuthorityIdentity("https://github.com/Sekiph82/Scrubbots", "UNAVAILABLE", "main-game/main", "UNAVAILABLE"), "ERROR", None, "handoff solver/difficulty/semantic identities are not cross-bound to QA report", "PENDING")
    authority = main_game_authority or AuthorityIdentity("https://github.com/Sekiph82/Scrubbots", "UNAVAILABLE", "main-game/main", "UNAVAILABLE")
    if main_game_resolver is None:
        return _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, authority, "UNAVAILABLE", None, "current Sekiph82/Scrubbots main resolution capability is unavailable", "PENDING")
    try:
        resolve = getattr(main_game_resolver, "resolve_current_main", None)
        if not callable(resolve):
            raise QAContractError("current-main resolver must expose resolve_current_main")
        resolution = resolve()
        if not isinstance(resolution, CurrentMainResolution) or resolution.disposition != "RESOLVED" or not resolution.clean_checkout:
            return _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, resolution.authority if isinstance(resolution, CurrentMainResolution) else authority, "UNAVAILABLE" if isinstance(resolution, CurrentMainResolution) and resolution.disposition == "UNAVAILABLE" else "ERROR", None, "current main resolution did not produce an exact clean checkout", "PENDING")
        authority = resolution.authority
        if authority.repository.rstrip("/") != "https://github.com/Sekiph82/Scrubbots" or authority.commit_sha == "UNAVAILABLE":
            return _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, authority, "UNAVAILABLE", None, "current main resolution did not pin canonical Sekiph82/Scrubbots@main", "PENDING")
        if provider is None:
            return _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, authority, "UNAVAILABLE", None, "exact current-main validator/M09 capability is unavailable", "PENDING")
        provisional = _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, authority, "UNAVAILABLE", None, "current-main validation pending", "PENDING")
        validate = getattr(provider, "validate_handoff", None)
        if not callable(validate):
            raise QAContractError("main-game handoff provider must expose validate_handoff")
        receipt = validate(provisional)
        if not isinstance(receipt, HandoffValidationReceipt):
            raise QAContractError("main-game handoff provider returned an untyped receipt")
        expected = (level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report.digest(), solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest)
        actual = (receipt.level_data_sha256, receipt.logical_art_png_sha256, receipt.source_provenance_sha256, receipt.qa_report_digest, receipt.solver_evidence_digest, receipt.difficulty_analysis_digest, receipt.semantic_evidence_digest)
        proofs = (receipt.level_validator_passed, receipt.production_validator_passed, receipt.m09_round_trip_passed, receipt.clean_checkout, receipt.non_mutating)
        if receipt.authority != authority or actual != expected or receipt.current_main_sha != authority.commit_sha or any(value is not True for value in proofs):
            return _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, authority, "NOT_ELIGIBLE", receipt.evidence_digest, "current-main receipt is missing exact cross-lineage validator, M09, clean-checkout, or non-mutation proof", "PENDING")
        disposition = "ELIGIBLE_FOR_MAIN_GAME_ACCEPTANCE_HANDOFF" if receipt.disposition == "PASS" else "NOT_ELIGIBLE" if receipt.disposition == "FAIL" else receipt.disposition
        return _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, authority, disposition, receipt.evidence_digest, receipt.reason, "PASS" if disposition == "ELIGIBLE_FOR_MAIN_GAME_ACCEPTANCE_HANDOFF" else "PENDING")
    except Exception as exc:
        return _handoff(level_data_sha256, logical_art_png_sha256, source_provenance_sha256, qa_report, solver_evidence_digest, difficulty_analysis_digest, semantic_evidence_digest, factory_schema, factory_version, authority, "ERROR", None, f"main-game handoff validation failed closed: {exc}", "PENDING")


__all__ = ["HANDOFF_SCHEMA", "HANDOFF_VERSION", "CurrentMainResolution", "CurrentMainResolver", "HandoffValidationReceipt", "MainGameAcceptanceHandoff", "MainGameAcceptanceProvider", "build_main_game_handoff"]
