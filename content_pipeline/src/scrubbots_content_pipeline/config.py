"""Versioned, deterministic configuration for the control-plane boundary."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum


class Environment(StrEnum):
    """Logical target labels; they do not identify or contact real services."""

    STAGING = "staging"
    PRODUCTION = "production"


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Secret-free configuration for validation and future orchestration."""

    schema_version: str = "1.0"
    environment: Environment = Environment.STAGING
    input_contract: str = "scrubbots.level_factory.accepted-content.v1"
    require_owner_approval: bool = True


def serialize_config(config: PipelineConfig) -> str:
    """Serialize configuration to stable UTF-8-compatible JSON text."""

    value = asdict(config)
    value["environment"] = config.environment.value
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
