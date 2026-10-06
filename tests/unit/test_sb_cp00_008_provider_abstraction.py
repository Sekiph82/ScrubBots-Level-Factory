from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
PACKAGE = PIPELINE / "src" / "scrubbots_content_pipeline"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    Environment,
    ProviderCapability,
    ProviderFeature,
    ProviderIdentity,
    ProviderResult,
    ProviderResultCategory,
    ReadOnlyProvider,
    STAGING_TARGET,
    build_publication_plan,
    negotiate_capabilities,
    replay_release_events,
    serialize_provider_result,
    serialize_provider_identity,
    serialize_publication_plan,
    validate_provider_capability,
    validate_provider_identity,
    validate_remote_payload,
)


def _capability(features: tuple[ProviderFeature, ...] | None = None) -> ProviderCapability:
    values = features if features is not None else (
        ProviderFeature.STAGING_PUBLISH,
        ProviderFeature.OBJECT_WRITE,
        ProviderFeature.INTEGRITY_VERIFY,
        ProviderFeature.CONDITIONAL_WRITE,
    )
    return ProviderCapability(
        "neutral-capability-v1", "1.0", (Environment.STAGING,),
        tuple(sorted(values, key=lambda item: item.value)),
    )


def _content() -> tuple[dict[str, object], bytes, object]:
    descriptor = json.loads((PIPELINE / "schemas/v1/examples/level.json").read_text(encoding="utf-8"))
    attrs = descriptor["attributes"]
    assert isinstance(attrs, dict)
    payload_value = {
        "version": 1, "id": attrs["level_id"], "name": "Provider neutral fixture", "difficulty": "EASY",
        "width": attrs["width"], "height": attrs["height"], "palette": ["#000000FF", "#FFFFFFFF"],
        "cells": [0] * (attrs["width"] * attrs["height"] - 1) + [1],
    }
    payload = json.dumps(payload_value, separators=(",", ":")).encode("utf-8")
    attrs["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    return descriptor, payload, validate_remote_payload(descriptor, payload)


class FakeAlphaProvider:
    def __init__(self, capability: ProviderCapability) -> None:
        self.identity = ProviderIdentity("fake-alpha", "2.0")
        self.capabilities = capability

    def inspect(self, environment: Environment, logical_object_id: str, expected_digest: str) -> ProviderResult:
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id, environment, expected_digest)

    def validate_content(self, environment: Environment, logical_object_id: str, content_digest: str) -> ProviderResult:
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id, environment, content_digest)


class FakeBetaProvider(FakeAlphaProvider):
    def __init__(self, capability: ProviderCapability) -> None:
        self.identity = ProviderIdentity("fake-beta", "9.0")
        self.capabilities = capability


def test_contracts_are_versioned_and_read_and_mutation_protocols_are_separate() -> None:
    from scrubbots_content_pipeline.provider import MutatingProvider, ProviderAdapter

    assert validate_provider_identity(ProviderIdentity("fake-provider", "1.0"))
    capability = _capability()
    assert validate_provider_capability(capability)
    assert capability.contract_version == "1.0"
    assert "inspect" in ReadOnlyProvider.__dict__ or "inspect" in getattr(ReadOnlyProvider, "__annotations__", {})
    assert "read_object_bytes" in ReadOnlyProvider.__dict__
    assert "write_object" in MutatingProvider.__dict__
    assert "delete_object" in MutatingProvider.__dict__
    assert "verify_object" in MutatingProvider.__dict__
    assert "publish" not in ReadOnlyProvider.__dict__
    # CP001's old combined protocol remains a compatibility placeholder only.
    assert "publish" in ProviderAdapter.__dict__


def test_capability_negotiation_is_deterministic_and_fails_closed() -> None:
    capability = _capability()
    required = (
        ProviderFeature.CONDITIONAL_WRITE,
        ProviderFeature.OBJECT_WRITE,
        ProviderFeature.INTEGRITY_VERIFY,
    )
    accepted = negotiate_capabilities(capability, Environment.STAGING, required)
    assert accepted.accepted
    assert accepted.required_features == tuple(sorted(feature.value for feature in required))
    missing = negotiate_capabilities(_capability((ProviderFeature.OBJECT_WRITE,)), Environment.STAGING, required)
    assert not missing.accepted
    assert missing.result_category is ProviderResultCategory.UNSUPPORTED_CAPABILITY
    assert missing.missing_features == tuple(sorted({ProviderFeature.CONDITIONAL_WRITE.value, ProviderFeature.INTEGRITY_VERIFY.value}))
    wrong_environment = negotiate_capabilities(capability, Environment.PRODUCTION, required)
    assert not wrong_environment.accepted
    duplicate = negotiate_capabilities(capability, Environment.STAGING, (ProviderFeature.OBJECT_WRITE, ProviderFeature.OBJECT_WRITE))
    assert not duplicate.accepted and duplicate.result_category is ProviderResultCategory.INVALID_REQUEST


def test_two_fake_providers_with_equal_capabilities_produce_equivalent_plan_bytes() -> None:
    descriptor, payload, result = _content()
    capability = _capability()
    providers = (FakeAlphaProvider(capability), FakeBetaProvider(capability))
    assert providers[0].identity != providers[1].identity
    plans = [build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=STAGING_TARGET, replay=replay_release_events([]), current_state=None,
        capability=provider.capabilities, owner_approved=True,
    ) for provider in providers]
    assert all(plan.accepted for plan in plans)
    assert serialize_publication_plan(plans[0]) == serialize_publication_plan(plans[1])


def test_unsupported_required_capability_blocks_plan_before_any_mutator_exists() -> None:
    descriptor, payload, result = _content()
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=STAGING_TARGET, replay=replay_release_events([]), current_state=None,
        capability=_capability((ProviderFeature.OBJECT_WRITE,)), owner_approved=True,
    )
    assert not plan.accepted
    assert not plan.mutation_eligible_in_principle
    assert any(check.check_id == "capability_negotiation" and not check.accepted for check in plan.checks)


def test_provider_result_categories_are_fixed_secret_free_codes() -> None:
    secret = "ghp_" + "S" * 32
    result = ProviderResult("1.0", ProviderResultCategory.UNAUTHORIZED_REFERENCE, secret, Environment.STAGING)
    encoded = serialize_provider_result(result)
    report = json.loads(encoded)
    assert report["category"] == "UNAUTHORIZED_REFERENCE"
    assert report["provider_id"] == "[INVALID]"
    assert secret not in encoded
    assert "message" not in report and "detail" not in report
    identity = ProviderIdentity(secret, "1.0")
    assert secret not in serialize_provider_identity(identity)
    assert secret not in json.dumps(ProviderIdentity("safe-id", "safe-version", secret).to_dict())
    unsafe_capability = ProviderCapability("safe-id", secret, (Environment.STAGING,), (), secret)
    assert secret not in json.dumps(unsafe_capability.to_dict())


def test_provider_contract_and_planner_have_no_vendor_or_network_dependencies() -> None:
    forbidden = {"boto3", "botocore", "httpx", "requests", "urllib", "socket", "azure", "google"}
    for path in (PACKAGE / "provider.py", PACKAGE / "publication_plan.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not {alias.name.split(".", 1)[0] for alias in node.names} & forbidden
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".", 1)[0] not in forbidden
    assert not list(PACKAGE.glob("*provider_impl*"))
    planner_source = (PACKAGE / "publication_plan.py").read_text(encoding="utf-8")
    assert "MutatingProvider" not in planner_source
    orchestration_source = (PACKAGE / "orchestration.py").read_text(encoding="utf-8")
    assert "ReadOnlyProvider" in orchestration_source
    assert "MutatingProvider" not in orchestration_source
