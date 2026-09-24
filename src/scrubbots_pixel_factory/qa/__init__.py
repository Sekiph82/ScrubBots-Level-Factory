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
from .round_trip import (
    M09_ROUND_TRIP_SCHEMA,
    M09_ROUND_TRIP_VERSION,
    M09RoundTripReceipt,
    M09RoundTripReport,
    MainGameM09RoundTripProvider,
    evaluate_m09_round_trip,
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
    "M09_ROUND_TRIP_SCHEMA",
    "M09_ROUND_TRIP_VERSION",
    "M09RoundTripReceipt",
    "M09RoundTripReport",
    "MainGameM09RoundTripProvider",
    "evaluate_m09_round_trip",
]
