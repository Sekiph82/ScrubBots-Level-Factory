from __future__ import annotations

import ast
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
PACKAGE = PIPELINE / "src" / "scrubbots_content_pipeline"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    PRODUCTION_TARGET,
    STAGING_TARGET,
    Environment,
    EnvironmentTarget,
    PipelineConfig,
    TargetReasonCode,
    serialize_config,
    target_for,
    validate_environment_pair,
    validate_target_binding,
    validate_target_use,
    validate_only,
)


def test_staging_and_production_targets_have_distinct_versioned_identities() -> None:
    result = validate_environment_pair(STAGING_TARGET, PRODUCTION_TARGET)
    assert result.accepted
    assert STAGING_TARGET.target_version == PRODUCTION_TARGET.target_version == "1.0"
    assert STAGING_TARGET.environment is Environment.STAGING
    assert PRODUCTION_TARGET.environment is Environment.PRODUCTION
    assert STAGING_TARGET.logical_target_id != PRODUCTION_TARGET.logical_target_id
    assert STAGING_TARGET.state_namespace != PRODUCTION_TARGET.state_namespace
    assert STAGING_TARGET.content_namespace != PRODUCTION_TARGET.content_namespace
    assert STAGING_TARGET.direct_publication_permitted is True
    assert PRODUCTION_TARGET.direct_publication_permitted is False
    assert PRODUCTION_TARGET.promotion_required is True


def test_colliding_state_or_content_namespace_cannot_serve_both_environments() -> None:
    colliding = replace(PRODUCTION_TARGET, state_namespace="shared:state")
    staging = replace(STAGING_TARGET, state_namespace="shared:state")
    result = validate_environment_pair(staging, colliding)
    assert not result.accepted
    assert result.reason_code is TargetReasonCode.NAMESPACE_COLLISION
    same_content = replace(PRODUCTION_TARGET, content_namespace="shared:content")
    staging_content = replace(STAGING_TARGET, content_namespace="shared:content")
    assert validate_environment_pair(staging_content, same_content).reason_code is TargetReasonCode.NAMESPACE_COLLISION


def test_staging_only_identity_cannot_be_used_as_a_production_target() -> None:
    assert target_for(Environment.STAGING) is STAGING_TARGET
    assert validate_target_binding(Environment.PRODUCTION, STAGING_TARGET).reason_code is TargetReasonCode.ENVIRONMENT_MISMATCH
    mislabeled = replace(PRODUCTION_TARGET, state_namespace="staging:state")
    assert validate_target_binding(Environment.PRODUCTION, mislabeled).reason_code is TargetReasonCode.INVALID_TARGET_IDENTITY


def test_unknown_environment_fails_closed_in_target_resolution_validation_and_report() -> None:
    with pytest.raises(ValueError, match="unknown"):
        target_for("preview")
    assert validate_target_binding("preview", STAGING_TARGET).reason_code is TargetReasonCode.UNKNOWN_ENVIRONMENT
    report = validate_only(PipelineConfig(environment="preview"))  # type: ignore[arg-type]
    assert report.accepted is False
    assert report.environment == "preview"
    assert report.target_id is None
    assert report.actions == ()


def test_plan_report_target_mismatch_fails_closed_and_names_environment() -> None:
    assert validate_target_binding(Environment.STAGING, PRODUCTION_TARGET).reason_code is TargetReasonCode.ENVIRONMENT_MISMATCH
    report = validate_only(PipelineConfig(environment=Environment.STAGING))
    assert report.accepted
    assert report.environment == "staging"
    assert report.target_id == STAGING_TARGET.logical_target_id
    assert report.state_namespace == STAGING_TARGET.state_namespace
    assert report.content_namespace == STAGING_TARGET.content_namespace


def test_staging_artifact_requires_explicit_promotion_intent_for_production() -> None:
    denied = validate_target_use(PRODUCTION_TARGET, Environment.STAGING)
    assert not denied.accepted
    assert denied.reason_code is TargetReasonCode.PROMOTION_REQUIRED
    allowed = validate_target_use(PRODUCTION_TARGET, Environment.STAGING, promotion_intent=True)
    assert allowed.accepted
    assert validate_target_use(PRODUCTION_TARGET, None).reason_code is TargetReasonCode.PROMOTION_REQUIRED


def test_target_config_and_report_serialization_are_versioned_and_deterministic() -> None:
    config = PipelineConfig(environment=Environment.STAGING)
    first = serialize_config(config)
    assert first == serialize_config(config)
    decoded = json.loads(first)
    assert decoded["target"] == STAGING_TARGET.to_dict()
    report = validate_only(config)
    report_json = json.dumps(report.__dict__ if hasattr(report, "__dict__") else {
        "environment": report.environment,
        "target_version": report.target_version,
        "target_id": report.target_id,
        "state_namespace": report.state_namespace,
        "content_namespace": report.content_namespace,
        "promotion_required": report.promotion_required,
    }, sort_keys=True, separators=(",", ":"))
    assert json.loads(report_json)["environment"] == "staging"


def test_target_model_requires_no_endpoint_credentials_or_provider_network_code() -> None:
    source = (PACKAGE / "config.py").read_text(encoding="utf-8")
    serialized = serialize_config(PipelineConfig()).lower()
    assert "endpoint" not in serialized
    assert "password" not in serialized
    assert "access_token" not in serialized
    forbidden = {"httpx", "requests", "socket", "urllib", "aiohttp", "boto3", "scrubbots_pixel_factory", "godot"}
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not {alias.name.split(".", 1)[0] for alias in node.names} & forbidden
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".", 1)[0] not in forbidden


def test_malformed_target_object_fails_closed() -> None:
    malformed = EnvironmentTarget(Environment.PRODUCTION, "staging:target", "staging:state", "staging:content", True, False)
    assert not validate_target_binding(Environment.PRODUCTION, malformed).accepted
