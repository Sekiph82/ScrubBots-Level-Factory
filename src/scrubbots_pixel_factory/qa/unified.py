"""Provenance-bound composition of Factory QA and current main-game evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Protocol, runtime_checkable

from ..contracts import CANONICAL_PALETTE
from ..contracts.production import validate_production_dimensions, validate_production_used_color_count
from ..difficulty_analysis import DifficultyAnalysis
from ..level_metrics import AnalysisDisposition

UNIFIED_QA_SCHEMA = "scrubbots-unified-qa"
UNIFIED_QA_VERSION = 1
FACTORY_QA_AUTHORITY = "FACTORY_QA_V1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{7,64}$")


class QAContractError(ValueError):
    """Raised when a QA identity, payload, or provider receipt is malformed."""


class StageDisposition(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class UnifiedQADisposition(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise QAContractError(f"{label} must be a non-empty string")
    return value.strip()


def _sha(value: object, label: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise QAContractError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _attribute(value: object, *names: str) -> object:
    for name in names:
        if isinstance(value, Mapping) and name in value:
            return value[name]
        if hasattr(value, name):
            return getattr(value, name)
    raise AttributeError(f"artifact is missing one of: {', '.join(names)}")


@dataclass(frozen=True, slots=True)
class AuthorityIdentity:
    repository: str
    commit_sha: str
    source_path: str
    contract_version: str

    def __post_init__(self) -> None:
        _text(self.repository, "authority repository")
        if type(self.commit_sha) is not str or not self.commit_sha.strip() or (self.commit_sha != "UNAVAILABLE" and _COMMIT.fullmatch(self.commit_sha) is None):
            raise QAContractError("authority commit_sha must be a Git SHA or UNAVAILABLE")
        _text(self.source_path, "authority source_path")
        _text(self.contract_version, "authority contract_version")

    def canonical_dict(self) -> dict[str, str]:
        return {"repository": self.repository, "commit_sha": self.commit_sha, "source_path": self.source_path, "contract_version": self.contract_version}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class LevelDataIdentity:
    """Exact immutable LevelData bytes plus fields derived from that payload."""

    level_id: str
    source_sha256: str
    level_data_sha256: str
    width: int
    height: int
    cell_count: int
    level_data_bytes: bytes = b""
    schema: str = "scrubbots-level-data"
    version: int = 1

    def __post_init__(self) -> None:
        _text(self.level_id, "level_id")
        _sha(self.source_sha256, "Level Data source_sha256")
        _sha(self.level_data_sha256, "Level Data level_data_sha256")
        if self.schema != "scrubbots-level-data" or self.version != 1:
            raise QAContractError("unsupported Level Data V1 schema")
        if any(type(value) is not int or value < 1 for value in (self.width, self.height, self.cell_count)):
            raise QAContractError("Level Data dimensions and cell_count must be positive exact integers")
        if self.cell_count != self.width * self.height:
            raise QAContractError("Level Data cell_count must equal width*height")
        if type(self.level_data_bytes) is not bytes:
            raise QAContractError("Level Data payload must be immutable bytes")
        if self.level_data_bytes and hashlib.sha256(self.level_data_bytes).hexdigest() != self.level_data_sha256:
            raise QAContractError("Level Data SHA-256 does not match the exact payload bytes")

    @property
    def has_exact_payload(self) -> bool:
        return bool(self.level_data_bytes)

    @classmethod
    def from_bytes(cls, level_id: str, source_sha256: str, level_data_bytes: bytes, width: int | None = None, height: int | None = None) -> "LevelDataIdentity":
        if type(level_data_bytes) is not bytes:
            raise QAContractError("Level Data bytes must be immutable bytes")
        payload: Mapping[str, object] | None = None
        try:
            decoded = json.loads(level_data_bytes.decode("utf-8"))
            if isinstance(decoded, Mapping):
                payload = decoded
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = None
        if payload is not None:
            payload_schema = payload.get("schema")
            payload_version = payload.get("version")
            if payload_schema is not None and payload_schema != "scrubbots-level-data":
                raise QAContractError("Level Data payload schema is unsupported")
            if payload_version is not None and payload_version != 1:
                raise QAContractError("Level Data payload version is unsupported")
            payload_level_id = payload.get("level_id")
            payload_width = payload.get("width")
            payload_height = payload.get("height")
            payload_cells = payload.get("cells")
            if payload_level_id is not None and payload_level_id != level_id:
                raise QAContractError("Level Data level_id does not match exact payload")
            if payload_width is not None and payload_height is not None:
                if type(payload_width) is not int or type(payload_height) is not int:
                    raise QAContractError("Level Data payload dimensions must be exact integers")
                if (width is not None and width != payload_width) or (height is not None and height != payload_height):
                    raise QAContractError("parallel Level Data dimensions disagree with exact payload")
                width, height = payload_width, payload_height
            if payload_cells is not None and (not isinstance(payload_cells, list) or width is None or height is None or len(payload_cells) != width * height):
                raise QAContractError("Level Data payload cells do not match exact dimensions")
        if type(width) is not int or type(height) is not int:
            raise QAContractError("Level Data dimensions must be supplied by or derived from exact payload")
        return cls(level_id, _sha(source_sha256, "Level Data source_sha256"), hashlib.sha256(level_data_bytes).hexdigest(), width, height, width * height, level_data_bytes)

    @classmethod
    def from_mapping(cls, level_id: str, source_sha256: str, level_data: Mapping[str, object], width: int | None = None, height: int | None = None) -> "LevelDataIdentity":
        if not isinstance(level_data, Mapping):
            raise QAContractError("Level Data must be a mapping")
        return cls.from_bytes(level_id, source_sha256, _canonical_bytes(dict(level_data)), width, height)

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "level_id": self.level_id, "source_sha256": self.source_sha256, "level_data_sha256": self.level_data_sha256, "width": self.width, "height": self.height, "cell_count": self.cell_count}

    def digest(self) -> str:
        return _digest(self.canonical_dict())


@dataclass(frozen=True, slots=True)
class ExternalValidationResult:
    disposition: StageDisposition
    authority: AuthorityIdentity
    evidence_digest: str
    reason: str
    provider_id: str = "main-game-exact-source"
    provider_version: str = "M05_PROVIDER_V1"
    level_data_sha256: str | None = None
    level_data_source_sha256: str | None = None
    level_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, StageDisposition) or not isinstance(self.authority, AuthorityIdentity):
            raise QAContractError("provider disposition or authority is malformed")
        _sha(self.evidence_digest, "provider evidence_digest")
        _text(self.reason, "provider reason")
        _text(self.provider_id, "provider_id")
        _text(self.provider_version, "provider_version")
        for value, label in ((self.level_data_sha256, "provider Level Data SHA-256"), (self.level_data_source_sha256, "provider Level Data source SHA-256")):
            if value is not None:
                _sha(value, label)
        if self.level_id is not None:
            _text(self.level_id, "provider level_id")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": "scrubbots-main-game-validation", "version": 1, "disposition": self.disposition.value, "authority": self.authority.canonical_dict(), "evidence_digest": self.evidence_digest, "reason": self.reason, "provider_id": self.provider_id, "provider_version": self.provider_version, "level_data_sha256": self.level_data_sha256, "level_data_source_sha256": self.level_data_source_sha256, "level_id": self.level_id}


@runtime_checkable
class MainGameValidationProvider(Protocol):
    def validate(self, stage: str, level_data: LevelDataIdentity, artifact: object) -> ExternalValidationResult:
        """Validate exact immutable LevelData bytes in the current main-game boundary."""


@dataclass(frozen=True, slots=True)
class QAStage:
    stage_id: str
    disposition: StageDisposition
    authority: AuthorityIdentity
    evidence_digest: str
    reason: str

    def __post_init__(self) -> None:
        _text(self.stage_id, "QA stage_id")
        if not isinstance(self.disposition, StageDisposition) or not isinstance(self.authority, AuthorityIdentity):
            raise QAContractError("QA stage disposition or authority is malformed")
        _sha(self.evidence_digest, "QA stage evidence_digest")
        _text(self.reason, "QA stage reason")

    def canonical_dict(self) -> dict[str, object]:
        return {"stage_id": self.stage_id, "disposition": self.disposition.value, "authority": self.authority.canonical_dict(), "evidence_digest": self.evidence_digest, "reason": self.reason}


def _authority_from(value: object, fallback: AuthorityIdentity) -> AuthorityIdentity:
    if isinstance(value, AuthorityIdentity):
        return value
    if isinstance(value, Mapping):
        try:
            return AuthorityIdentity(str(value["repository"]), str(value["commit_sha"]), str(value.get("proof_state_source_path", value.get("source_path"))), str(value.get("version", value.get("contract_version"))))
        except (KeyError, TypeError, QAContractError) as exc:
            raise QAContractError("M04 authority cannot be converted to exact QA authority") from exc
    canonical = getattr(value, "canonical_dict", None)
    if callable(canonical):
        return _authority_from(canonical(), fallback)
    return fallback


def _unavailable(stage_id: str, authority: AuthorityIdentity | None, reason: str) -> QAStage:
    selected = authority or AuthorityIdentity("https://github.com/Sekiph82/Scrubbots", "UNAVAILABLE", "main-game/M05", "UNAVAILABLE")
    return QAStage(stage_id, StageDisposition.UNAVAILABLE, selected, _digest({"stage": stage_id, "authority": selected.canonical_dict(), "reason": reason}), reason)


def _stage_from_provider(stage_id: str, result: ExternalValidationResult, level_data: LevelDataIdentity, expected_authority: AuthorityIdentity | None) -> QAStage:
    if expected_authority is not None and result.authority != expected_authority:
        return QAStage(stage_id, StageDisposition.ERROR, expected_authority, _digest({"stage": stage_id, "provider": result.canonical_dict(), "error": "AUTHORITY_DRIFT"}), "provider authority does not match requested exact main-game authority")
    if result.level_data_sha256 is None or result.level_data_source_sha256 is None or result.level_id is None:
        return QAStage(stage_id, StageDisposition.UNAVAILABLE, result.authority, _digest({"stage": stage_id, "provider": result.canonical_dict(), "error": "EXACT_LEVELDATA_BINDING_UNAVAILABLE"}), "provider did not return exact LevelData payload/source/level identity binding")
    if (result.level_data_sha256, result.level_data_source_sha256, result.level_id) != (level_data.level_data_sha256, level_data.source_sha256, level_data.level_id):
        return QAStage(stage_id, StageDisposition.ERROR, result.authority, _digest({"stage": stage_id, "provider": result.canonical_dict(), "error": "LEVELDATA_IDENTITY_DRIFT"}), "provider receipt is bound to different LevelData bytes, source, or level")
    return QAStage(stage_id, result.disposition, result.authority, result.evidence_digest, result.reason)


def _factory_stage(level_data: LevelDataIdentity, artifact: object, authority: AuthorityIdentity) -> QAStage:
    try:
        width = _attribute(artifact, "target_width", "width")
        height = _attribute(artifact, "target_height", "height")
        if type(width) is not int or type(height) is not int:
            raise QAContractError("factory dimensions must be exact integers")
        cells = tuple(_attribute(artifact, "logical_cells", "cells"))
        declared = tuple(_attribute(artifact, "used_palette_ids", "palette"))
        validate_production_dimensions(width, height)
        if len(cells) != width * height:
            raise QAContractError("factory artifact cell count does not match dimensions")
        used = CANONICAL_PALETTE.used_ids(cells)
        validate_production_used_color_count(cells)
        if declared != used:
            raise QAContractError("factory artifact palette is not derived from logical cells")
        source_hash = _attribute(artifact, "raw_sha256", "source_sha256") if hasattr(artifact, "raw_sha256") or hasattr(artifact, "source_sha256") or isinstance(artifact, Mapping) else None
        if source_hash is not None and source_hash != level_data.source_sha256:
            raise QAContractError("factory artifact source identity differs from Level Data source identity")
        artifact_digest = getattr(artifact, "digest", None)
        digest = artifact_digest() if callable(artifact_digest) else _digest({"width": width, "height": height, "cells": list(cells), "palette": list(declared), "level_data": level_data.digest()})
        _sha(digest, "factory artifact digest")
        return QAStage("FACTORY_PRODUCTION_ENVELOPE", StageDisposition.PASS, authority, _digest({"artifact_digest": digest, "level_data_digest": level_data.digest(), "width": width, "height": height, "used_colors": list(used)}), "current Factory production envelope and palette lineage are consistent")
    except (AttributeError, TypeError, ValueError, QAContractError) as exc:
        return QAStage("FACTORY_PRODUCTION_ENVELOPE", StageDisposition.FAIL, authority, _digest({"level_data": level_data.digest(), "reason": str(exc)}), f"factory production-envelope evidence is invalid: {exc}")


def _difficulty_stage(level_data: LevelDataIdentity, analysis: DifficultyAnalysis | None, fallback: AuthorityIdentity) -> QAStage:
    if analysis is None:
        return _unavailable("DIFFICULTY_V1", fallback, "M04 DifficultyAnalysis is unavailable")
    try:
        if not isinstance(analysis, DifficultyAnalysis) or analysis.level_source_sha256 != level_data.source_sha256:
            raise QAContractError("M04 analysis source identity differs from Level Data")
        authority = _authority_from(analysis.authority, fallback)
        disposition = {AnalysisDisposition.AVAILABLE: StageDisposition.PASS, AnalysisDisposition.INCONCLUSIVE: StageDisposition.INCONCLUSIVE, AnalysisDisposition.UNAVAILABLE: StageDisposition.UNAVAILABLE, AnalysisDisposition.ERROR: StageDisposition.ERROR}[analysis.disposition]
        return QAStage("DIFFICULTY_V1", disposition, authority, analysis.digest(), analysis.reason or "M04 Difficulty V1 analysis bound")
    except (AttributeError, TypeError, ValueError, QAContractError) as exc:
        return QAStage("DIFFICULTY_V1", StageDisposition.ERROR, fallback, _digest({"level_data": level_data.digest(), "reason": str(exc)}), f"M04 difficulty evidence is invalid: {exc}")


def _provider_result(provider: object, stage: str, level_data: LevelDataIdentity, artifact: object) -> ExternalValidationResult:
    validate = getattr(provider, "validate", None)
    if callable(validate):
        result = validate(stage, level_data, artifact)
    else:
        method = getattr(provider, f"validate_{stage.lower()}", None)
        if not callable(method):
            raise QAContractError("main-game provider exposes neither validate nor stage-specific validation")
        result = method(level_data, artifact)
    if not isinstance(result, ExternalValidationResult):
        raise QAContractError("main-game provider returned an untyped result")
    return result


def evaluate_unified_qa(level_data: LevelDataIdentity, artifact: object, *, provider: MainGameValidationProvider | object | None, main_game_authority: AuthorityIdentity | None, difficulty_analysis: DifficultyAnalysis | None, factory_authority: AuthorityIdentity | None = None) -> "UnifiedQAReport":
    if not isinstance(level_data, LevelDataIdentity):
        raise QAContractError("LevelDataIdentity is required")
    factory = factory_authority or AuthorityIdentity("https://github.com/Sekiph82/ScrubBots-Level-Factory", "UNAVAILABLE", "src/scrubbots_pixel_factory/qa", FACTORY_QA_AUTHORITY)
    stages = [QAStage("LEVEL_DATA_V1", StageDisposition.PASS if level_data.has_exact_payload else StageDisposition.UNAVAILABLE, factory, level_data.digest(), "exact LevelData bytes/source identity are bound" if level_data.has_exact_payload else "exact LevelData payload bytes are unavailable")]
    for stage_id in ("STRUCTURAL", "PRODUCTION"):
        if provider is None:
            stages.append(_unavailable(stage_id, main_game_authority, "exact main-game validation capability is unavailable"))
            continue
        try:
            stages.append(_stage_from_provider(stage_id, _provider_result(provider, stage_id, level_data, artifact), level_data, main_game_authority))
        except Exception as exc:
            authority = main_game_authority or AuthorityIdentity("https://github.com/Sekiph82/Scrubbots", "UNAVAILABLE", "main-game/M05", "UNAVAILABLE")
            stages.append(QAStage(stage_id, StageDisposition.ERROR, authority, _digest({"stage": stage_id, "error": str(exc)}), f"main-game validation provider error: {exc}"))
    stages.append(_factory_stage(level_data, artifact, factory))
    stages.append(_difficulty_stage(level_data, difficulty_analysis, factory))
    return UnifiedQAReport(level_data, tuple(stages))


@dataclass(frozen=True, slots=True)
class UnifiedQAReport:
    level_data: LevelDataIdentity
    stages: tuple[QAStage, ...]
    schema: str = UNIFIED_QA_SCHEMA
    version: int = UNIFIED_QA_VERSION

    def __post_init__(self) -> None:
        if self.schema != UNIFIED_QA_SCHEMA or self.version != UNIFIED_QA_VERSION or not isinstance(self.level_data, LevelDataIdentity) or type(self.stages) is not tuple:
            raise QAContractError("Unified QA report identity is malformed")
        expected = ("LEVEL_DATA_V1", "STRUCTURAL", "PRODUCTION", "FACTORY_PRODUCTION_ENVELOPE", "DIFFICULTY_V1")
        if tuple(stage.stage_id for stage in self.stages) != expected or any(not isinstance(stage, QAStage) for stage in self.stages):
            raise QAContractError("Unified QA stages are not the closed ordered catalog")

    @property
    def disposition(self) -> UnifiedQADisposition:
        values = [stage.disposition for stage in self.stages]
        if StageDisposition.ERROR in values:
            return UnifiedQADisposition.ERROR
        if StageDisposition.FAIL in values:
            return UnifiedQADisposition.REJECT
        if StageDisposition.INCONCLUSIVE in values:
            return UnifiedQADisposition.INCONCLUSIVE
        if StageDisposition.UNAVAILABLE in values:
            return UnifiedQADisposition.UNAVAILABLE
        return UnifiedQADisposition.ACCEPT

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "version": self.version, "level_data": self.level_data.canonical_dict(), "stages": [stage.canonical_dict() for stage in self.stages], "disposition": self.disposition.value}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


__all__ = ["FACTORY_QA_AUTHORITY", "UNIFIED_QA_SCHEMA", "UNIFIED_QA_VERSION", "AuthorityIdentity", "ExternalValidationResult", "LevelDataIdentity", "MainGameValidationProvider", "QAContractError", "QAStage", "StageDisposition", "UnifiedQAReport", "UnifiedQADisposition", "evaluate_unified_qa", "_canonical_bytes", "_digest", "_sha"]
