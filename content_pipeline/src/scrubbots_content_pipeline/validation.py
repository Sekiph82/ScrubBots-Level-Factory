"""Local validation-only entry boundary and evidence result."""

from __future__ import annotations

from dataclasses import dataclass

from .config import PipelineConfig


@dataclass(frozen=True, slots=True)
class DryRunReport:
    """Deterministic description of a local validation-only run."""

    schema_version: str
    environment: str
    accepted: bool
    actions: tuple[str, ...]


def validate_only(config: PipelineConfig) -> DryRunReport:
    """Validate control-plane configuration without I/O or remote mutation."""

    accepted = config.schema_version == "1.0" and bool(config.input_contract)
    actions = ("validate_config", "emit_local_report") if accepted else ()
    return DryRunReport(
        schema_version=config.schema_version,
        environment=config.environment.value,
        accepted=accepted,
        actions=actions,
    )
