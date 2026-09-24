"""Versioned, provenance-bound M05 QA composition contracts."""

from .unified import (
    FACTORY_QA_AUTHORITY,
    UNIFIED_QA_SCHEMA,
    UNIFIED_QA_VERSION,
    AuthorityIdentity,
    ExternalValidationResult,
    LevelDataIdentity,
    MainGameValidationProvider,
    QAContractError,
    QAStage,
    StageDisposition,
    UnifiedQAReport,
    UnifiedQADisposition,
    evaluate_unified_qa,
)

__all__ = [
    "FACTORY_QA_AUTHORITY",
    "UNIFIED_QA_SCHEMA",
    "UNIFIED_QA_VERSION",
    "AuthorityIdentity",
    "ExternalValidationResult",
    "LevelDataIdentity",
    "MainGameValidationProvider",
    "QAContractError",
    "QAStage",
    "StageDisposition",
    "UnifiedQAReport",
    "UnifiedQADisposition",
    "evaluate_unified_qa",
]
