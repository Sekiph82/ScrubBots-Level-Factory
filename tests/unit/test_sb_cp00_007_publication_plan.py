from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    Environment,
    PRODUCTION_TARGET,
    STAGING_TARGET,
    PayloadReasonCode,
    PlanReasonCode,
    ProviderCapability,
    ProviderFeature,
    ReleaseState,
    build_publication_plan,
    make_release_event,
    replay_release_events,
    serialize_publication_plan,
    validate_plan_current,
    validate_remote_payload,
)


def _content() -> tuple[dict[str, object], bytes, object]:
    descriptor = json.loads((PIPELINE / "schemas/v1/examples/level.json").read_text(encoding="utf-8"))
    attrs = descriptor["attributes"]
    assert isinstance(attrs, dict)
    payload_obj = {
        "version": 1, "id": attrs["level_id"], "name": "Plan Fixture", "difficulty": "EASY",
        "width": attrs["width"], "height": attrs["height"], "palette": ["C01", "C02"],
        "cells": ["C01"] * (attrs["width"] * attrs["height"] - 1) + ["C02"],
    }
    payload = json.dumps(payload_obj, separators=(",", ":")).encode("utf-8")
    attrs["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    return descriptor, payload, validate_remote_payload(descriptor, payload)


def _staged_history(content_id: str, digest: str) -> object:
    events = []
    for index, state in enumerate((ReleaseState.DRAFT, ReleaseState.VALIDATED, ReleaseState.STAGED), start=1):
        prior = events[-1].event_digest if events else "0" * 64
        previous = (None, ReleaseState.DRAFT, ReleaseState.VALIDATED)[index - 1]
        expected = (None, ReleaseState.DRAFT, ReleaseState.VALIDATED)[index - 1]
        events.append(make_release_event(
            sequence=index, event_id=f"event-{index}", transition_id=f"transition-{index}",
            record_id="staging-record", content_id=content_id, content_digest=digest,
            environment=Environment.STAGING, from_state=previous, to_state=state,
            expected_state=expected, previous_event_digest=prior,
        ))
    return replay_release_events(events)


def _draft_history(content_id: str, digest: str) -> object:
    event = make_release_event(
        sequence=1, event_id="event-1", transition_id="transition-1",
        record_id="other-staging-record", content_id=content_id, content_digest=digest,
        environment=Environment.STAGING, from_state=None, to_state=ReleaseState.DRAFT,
        expected_state=None, previous_event_digest="0" * 64,
    )
    return replay_release_events([event])


def _capability() -> ProviderCapability:
    features = tuple(sorted((
        ProviderFeature.STAGING_PUBLISH, ProviderFeature.PRODUCTION_PROMOTION,
        ProviderFeature.OBJECT_WRITE, ProviderFeature.INTEGRITY_VERIFY,
        ProviderFeature.CONDITIONAL_WRITE, ProviderFeature.ATOMIC_MANIFEST_PUBLISH,
    ), key=lambda feature: feature.value))
    environments = tuple(sorted((Environment.STAGING, Environment.PRODUCTION), key=lambda item: item.value))
    return ProviderCapability("local-capability-v1", "1.0", environments, features)


def test_plan_bytes_and_operation_order_are_deterministic_and_secret_free() -> None:
    descriptor, payload, result = _content()
    replay = replay_release_events([])
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=STAGING_TARGET, replay=replay, current_state=None,
        capability=_capability(), owner_approved=True,
    )
    assert plan.accepted and plan.complete and plan.mutation_eligible_in_principle
    assert plan.remote_mutation_performed is False
    assert [operation.sequence for operation in plan.operations] == [1]
    assert serialize_publication_plan(plan) == serialize_publication_plan(plan)
    raw = serialize_publication_plan(plan)
    assert "remote_mutation_performed\":false" in raw
    assert "publish_to_staging" in raw
    assert "capability_id" in raw


def test_unvalidated_or_hash_mismatched_payload_cannot_be_planned() -> None:
    descriptor, payload, _ = _content()
    rejected = validate_remote_payload(descriptor, payload + b" ")
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload + b" ", payload_result=rejected,
        target=STAGING_TARGET, replay=replay_release_events([]), current_state=None,
        capability=_capability(), owner_approved=True,
    )
    assert not plan.accepted
    assert plan.checks[0].reason_code == PlanReasonCode.UNVALIDATED_PAYLOAD.value
    assert validate_remote_payload(descriptor, payload + b" ").reason_code is PayloadReasonCode.DIGEST_MISMATCH


def test_production_requires_exact_staged_source_explicit_approval_and_capability() -> None:
    descriptor, payload, result = _content()
    attrs = descriptor["attributes"]
    assert isinstance(attrs, dict)
    content_id, digest = attrs["level_id"], attrs["payload_sha256"]
    replay = _staged_history(content_id, digest)
    source = next(item for item in replay.snapshots if item.record_id == "staging-record")
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=PRODUCTION_TARGET, replay=replay, current_state=source,
        capability=_capability(), owner_approved=True,
    )
    assert replay.accepted and source.state is ReleaseState.STAGED
    assert plan.accepted and plan.operations[0].operation == "promote_staged_record"
    assert plan.operations[0].source_record_id == source.record_id
    assert plan.expected_release_state.record_id == source.record_id

    no_approval = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=PRODUCTION_TARGET, replay=replay, current_state=source,
        capability=_capability(), owner_approved=False,
    )
    assert not no_approval.accepted and not no_approval.mutation_eligible_in_principle
    assert any(check.reason_code == PlanReasonCode.OWNER_APPROVAL_REQUIRED.value for check in no_approval.checks)


def test_staging_rejects_a_replayed_but_not_yet_validated_release_state() -> None:
    descriptor, payload, result = _content()
    attrs = descriptor["attributes"]
    assert isinstance(attrs, dict)
    replay = _draft_history(attrs["level_id"], attrs["payload_sha256"])
    draft = next(item for item in replay.snapshots if item.record_id == "other-staging-record")
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=STAGING_TARGET, replay=replay, current_state=draft,
        capability=_capability(), owner_approved=True,
    )
    assert not plan.accepted
    assert any(check.reason_code == PlanReasonCode.STATE_MISMATCH.value for check in plan.checks)


def test_invalid_or_unreplayed_state_input_fails_closed_without_echoing_it() -> None:
    descriptor, payload, result = _content()
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=STAGING_TARGET, replay=replay_release_events([]), current_state="untrusted-state",
        capability=_capability(), owner_approved=True,
    )
    assert not plan.accepted
    assert plan.expected_release_state.record_version == "invalid"
    assert "untrusted-state" not in serialize_publication_plan(plan)


def test_environment_and_release_state_mismatch_fail_closed() -> None:
    descriptor, payload, result = _content()
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=PRODUCTION_TARGET, replay=replay_release_events([]), current_state=None,
        capability=_capability(), owner_approved=True,
    )
    assert not plan.accepted
    assert any(check.reason_code == PlanReasonCode.PROMOTION_REQUIRED.value for check in plan.checks)
    assert any(check.reason_code in {PlanReasonCode.CONTENT_MISMATCH.value, PlanReasonCode.INVALID_REPLAY.value} for check in plan.checks)


def test_currentness_binds_exact_digest_target_and_replayed_state() -> None:
    descriptor, payload, result = _content()
    replay = replay_release_events([])
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=STAGING_TARGET, replay=replay, current_state=None,
        capability=_capability(), owner_approved=True,
    )
    digest = plan.content_digest
    assert validate_plan_current(plan, current_target=STAGING_TARGET, current_replay=replay, current_state=None, current_content_digest=digest).accepted
    stale = validate_plan_current(plan, current_target=PRODUCTION_TARGET, current_replay=replay, current_state=None, current_content_digest=digest)
    changed = validate_plan_current(plan, current_target=STAGING_TARGET, current_replay=replay, current_state=None, current_content_digest="f" * 64)
    assert not stale.accepted and not changed.accepted
    assert stale.reason_code == PlanReasonCode.STALE_PLAN.value

    advanced_replay = _draft_history("unrelated-content", "d" * 64)
    state_advanced = validate_plan_current(
        plan, current_target=STAGING_TARGET, current_replay=advanced_replay,
        current_state=None, current_content_digest=digest,
    )
    assert not state_advanced.accepted
    assert state_advanced.reason_code == PlanReasonCode.STALE_PLAN.value


def test_secret_bearing_descriptor_is_rejected_and_not_echoed() -> None:
    descriptor, payload, result = _content()
    descriptor["api_key"] = "ghp_" + "Q" * 32
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=STAGING_TARGET, replay=replay_release_events([]), current_state=None,
        capability=_capability(), owner_approved=True,
    )
    assert not plan.accepted
    assert "api_key" not in serialize_publication_plan(plan)


def test_secret_value_in_payload_is_rejected_even_when_payload_contract_accepts_it() -> None:
    descriptor, _, _ = _content()
    attrs = descriptor["attributes"]
    assert isinstance(attrs, dict)
    payload_value = "ghp_" + "R" * 32
    payload = json.dumps({
        "version": 1, "id": attrs["level_id"], "name": payload_value, "difficulty": "EASY",
        "width": attrs["width"], "height": attrs["height"], "palette": ["C01", "C02"],
        "cells": ["C01"] * (attrs["width"] * attrs["height"] - 1) + ["C02"],
    }, separators=(",", ":")).encode("utf-8")
    attrs["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    payload_result = validate_remote_payload(descriptor, payload)
    assert payload_result.accepted
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=payload_result,
        target=STAGING_TARGET, replay=replay_release_events([]), current_state=None,
        capability=_capability(), owner_approved=True,
    )
    assert not plan.accepted and payload_value not in serialize_publication_plan(plan)


def test_dry_run_never_calls_mutation_canary_and_cli_is_explicitly_zero_write() -> None:
    class Canary:
        calls = 0

        def publish(self) -> None:
            self.calls += 1
            raise AssertionError("mutation must never run")

        promote = publish

    descriptor, payload, result = _content()
    canary = Canary()
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=result,
        target=STAGING_TARGET, replay=replay_release_events([]), current_state=None,
        capability=_capability(), owner_approved=True,
    )
    assert plan.accepted and canary.calls == 0
    run = subprocess.run(
        [sys.executable, "-m", "scrubbots_content_pipeline", "--dry-run", "--environment", "staging"],
        cwd=PIPELINE, env={**os.environ, "PYTHONPATH": str(PIPELINE / "src")},
        capture_output=True, text=True, check=False,
    )
    assert run.returncode != 0
    report = json.loads(run.stdout)
    assert report["accepted"] is False and report["remote_mutation_performed"] is False
    assert run.stderr == ""
