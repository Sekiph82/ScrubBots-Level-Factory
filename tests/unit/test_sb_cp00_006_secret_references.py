from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    Environment,
    PipelineConfig,
    ReleaseState,
    SecretReference,
    SecretReferenceReasonCode,
    make_release_event,
    redact_for_evidence,
    serialize_config,
    serialize_release_event,
    serialize_secret_reference,
    validate_only,
    validate_secret_reference,
)


def _reference(environment: str = "staging") -> dict[str, object]:
    return {
        "reference_version": "1.0",
        "reference_id": "ref-content-upload-v3",
        "purpose": "content.upload",
        "environment": environment,
        "version_label": "rotation-v3",
    }


def test_only_opaque_environment_scoped_reference_is_accepted() -> None:
    result = validate_secret_reference(_reference(), expected_environment=Environment.STAGING)
    assert result.accepted
    assert result.reason_code is SecretReferenceReasonCode.VALID_REFERENCE
    assert result.reference is not None
    encoded = serialize_secret_reference(result.reference)
    assert json.loads(encoded)["reference_id"] == "ref-content-upload-v3"
    assert json.loads(encoded)["environment"] == "staging"


@pytest.mark.parametrize("field", ("password", "api_key", "access_token", "refresh_token", "token", "private_key", "client_secret", "connection_string", "secret_value"))
def test_raw_secret_bearing_fields_are_rejected_without_echoing_values(field: str) -> None:
    fixture_value = "ghp_" + "Q" * 32
    raw = _reference()
    raw[field] = fixture_value
    result = validate_secret_reference(raw)
    assert not result.accepted
    assert result.reason_code is SecretReferenceReasonCode.SECRET_MATERIAL_FIELD
    assert fixture_value not in repr(result)


def test_secret_reference_model_has_no_value_field_and_safe_repr() -> None:
    reference = SecretReference("ref-content-upload-v3", "content.upload", Environment.STAGING)
    assert "value" not in reference.__dataclass_fields__
    assert "ref-content-upload-v3" not in repr(reference)
    assert "opaque" in repr(reference)
    assert "ref-content-upload-v3" in serialize_secret_reference(reference)


def test_redaction_is_deterministic_for_secret_fields_tokens_assignments_and_pem() -> None:
    fixture_value = "ghp_" + "R" * 32
    access_key = "access_" + "token"
    evidence = {
        "api_key": fixture_value,
        "message": f"request failed; {access_key}={fixture_value}",
        "authorization": f"Bearer {fixture_value}",
        "connection": f"postgres://user:{fixture_value}@db.example.invalid/main",
        "private_key": "-----BEGIN PRIVATE KEY-----fixture-----END PRIVATE KEY-----",
    }
    first = redact_for_evidence(evidence)
    second = redact_for_evidence(evidence)
    assert first == second
    assert fixture_value not in json.dumps(first)
    assert first["api_key"] == "[REDACTED]"  # type: ignore[index]
    assert "[REDACTED]" in first["message"]  # type: ignore[index]
    assert fixture_value not in first["connection"]  # type: ignore[index]


def test_environment_bound_reference_mismatch_and_unknown_label_fail() -> None:
    result = validate_secret_reference(_reference("staging"), expected_environment=Environment.PRODUCTION)
    assert result.reason_code is SecretReferenceReasonCode.ENVIRONMENT_MISMATCH
    raw = _reference("preview")
    assert validate_secret_reference(raw).reason_code is SecretReferenceReasonCode.UNKNOWN_ENVIRONMENT


def test_config_report_and_event_serialization_do_not_expose_obvious_secret_material() -> None:
    fixture_value = "ghp_" + "S" * 32
    api_key_name = "api_" + "key"
    config = PipelineConfig(input_contract=f"{api_key_name}={fixture_value}")
    config_text = serialize_config(config)
    report = validate_only(PipelineConfig(environment=fixture_value))  # type: ignore[arg-type]
    event = make_release_event(
        sequence=1, event_id="event-1", transition_id="transition-1", record_id="record-1",
        content_id=fixture_value, content_digest="a" * 64, environment=Environment.STAGING,
        from_state=None, to_state=ReleaseState.DRAFT, expected_state=None,
        previous_event_digest="0" * 64,
    )
    event_text = serialize_release_event(event)
    report_text = json.dumps({"environment": report.environment, "schema_version": report.schema_version})
    assert fixture_value not in config_text
    assert fixture_value not in event_text
    assert fixture_value not in report_text


def test_tracked_content_pipeline_configuration_and_source_secret_guard() -> None:
    listing = subprocess.run(
        ["git", "ls-files", "content_pipeline"], cwd=ROOT, check=True,
        capture_output=True, text=True, encoding="utf-8",
    ).stdout.splitlines()
    candidates = [
        ROOT / relative for relative in listing
        if relative.startswith("content_pipeline/src/") and relative.endswith(".py")
        or relative.startswith("content_pipeline/schemas/") and relative.endswith(".json")
        or relative == "content_pipeline/pyproject.toml"
    ]
    patterns = (
        re.compile(r"(?im)\b(?:api[_-]?key|password|access[_-]?token|refresh[_-]?token|client[_-]?secret|connection[_-]?string)\s*['\"]?\s*[:=]\s*['\"][^'\"\r\n]{8,}['\"]"),
        re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    )
    violations = []
    for path in candidates:
        content = path.read_text(encoding="utf-8")
        if any(pattern.search(content) for pattern in patterns):
            violations.append(path.relative_to(ROOT).as_posix())
    assert not violations
