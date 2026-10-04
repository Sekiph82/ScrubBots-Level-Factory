"""Local validation-only entry boundary and evidence result."""

from __future__ import annotations

from dataclasses import dataclass

from .config import PipelineConfig, validate_target_binding


@dataclass(frozen=True, slots=True)
class DryRunReport:
    """Deterministic description of a local validation-only run."""

    schema_version: str
    environment: str
    target_version: str | None
    target_id: str | None
    state_namespace: str | None
    content_namespace: str | None
    promotion_required: bool | None
    accepted: bool
    actions: tuple[str, ...]


def validate_only(config: PipelineConfig) -> DryRunReport:
    """Validate control-plane configuration without I/O or remote mutation."""

    from .secret_refs import redact_for_evidence

    target = config.resolved_target
    environment = config.environment.value if hasattr(config.environment, "value") else config.environment
    if not isinstance(environment, str):
        environment = "unknown"
    binding = validate_target_binding(config.environment, target)
    accepted = (
        config.schema_version == "1.0"
        and isinstance(config.input_contract, str)
        and bool(config.input_contract)
        and config.require_owner_approval is True
        and binding.accepted
    )
    actions = ("validate_config", "emit_local_report") if accepted else ()
    return DryRunReport(
        schema_version=redact_for_evidence(config.schema_version),
        environment=redact_for_evidence(environment),
        target_version=target.target_version if target is not None else None,
        target_id=target.logical_target_id if target is not None else None,
        state_namespace=target.state_namespace if target is not None else None,
        content_namespace=target.content_namespace if target is not None else None,
        promotion_required=target.promotion_required if target is not None else None,
        accepted=accepted,
        actions=actions,
    )
