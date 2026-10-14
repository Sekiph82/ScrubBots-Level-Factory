from __future__ import annotations

from dataclasses import replace
import hashlib

from scrubbots_content_pipeline.operations import (
    OperationsEvidenceError,
    operation_record_from_publication_plan,
    verify_content_health,
)
from scrubbots_content_pipeline.publication_plan import (
    ExpectedReleaseState,
    PlanCheck,
    PublicationPlan,
)


def _plan(*, accepted: bool, check: PlanCheck) -> PublicationPlan:
    return PublicationPlan(
        plan_version="1.0",
        accepted=accepted,
        complete=True,
        target_environment="STAGING",
        target_id="staging:family",
        capability_id="fake-provider",
        capability_version="1.0",
        capability_supports_staging_publish=True,
        capability_supports_production_promotion=False,
        capability_environments=("STAGING",),
        capability_features=("STAGING_PUBLISH",),
        content_id="batch-2026-10-14",
        content_digest="a" * 64,
        operations=(),
        checks=(check,),
        expected_release_state=ExpectedReleaseState(
            record_version="1.0",
            record_id=None,
            content_id=None,
            content_digest=None,
            environment="STAGING",
            state=None,
            last_sequence=0,
        ),
        owner_approved=False,
        mutation_eligible_in_principle=False,
        remote_mutation_performed=False,
    )


def test_publication_plan_maps_to_secret_free_preflight_record_in_memory() -> None:
    ready_plan = _plan(accepted=True, check=PlanCheck("payload_validation", True, "ACCEPTED"))
    ready = ready_plan.to_operation_record(
        operation_id="preflight-001",
        occurred_at="2026-10-14T12:00:00Z",
    )
    assert ready.kind == "BATCH"
    assert ready.environment == "STAGING"
    assert ready.outcome == "PREPARED"
    assert ready.reason_code == "PREFLIGHT_READY"
    assert ready.batch_id == "batch-2026-10-14"
    assert ready.manifest_sha256 is None

    blocked_plan = _plan(accepted=False, check=PlanCheck("owner_approval", False, "OWNER_APPROVAL_REQUIRED"))
    blocked = operation_record_from_publication_plan(
        blocked_plan,
        operation_id="preflight-002",
        occurred_at="2026-10-14T12:00:00Z",
    )
    assert blocked.outcome == "BLOCKED"
    assert blocked.reason_code == "OWNER_APPROVAL_REQUIRED"
    assert "fake-provider" not in blocked.canonical_bytes().decode("utf-8")

    try:
        operation_record_from_publication_plan(
            replace(ready_plan, remote_mutation_performed=True),
            operation_id="preflight-003",
            occurred_at="2026-10-14T12:00:00Z",
        )
    except OperationsEvidenceError:
        pass
    else:
        raise AssertionError("a plan claiming remote mutation must not be converted as a local preflight")


def test_health_verifier_rejects_malformed_observed_keys_before_sorting_in_memory() -> None:
    manifest = b"canonical manifest"
    manifest_sha = hashlib.sha256(manifest).hexdigest()
    expected_bytes = b"pack"
    expected_sha = hashlib.sha256(expected_bytes).hexdigest()
    expected = {"packs/level-01.scrubpack": expected_sha}

    for observed in (
        {"packs/level-01.scrubpack": expected_bytes, 7: b"unexpected"},
        {"packs/level-01.scrubpack": expected_bytes, "../outside": b"unexpected"},
    ):
        try:
            verify_content_health(
                manifest,
                expected_manifest_sha256=manifest_sha,
                expected_objects=expected,
                observed_objects=observed,  # type: ignore[arg-type]
            )
        except OperationsEvidenceError:
            pass
        else:
            raise AssertionError("malformed observed object keys must fail closed")

    extra = verify_content_health(
        manifest,
        expected_manifest_sha256=manifest_sha,
        expected_objects=expected,
        observed_objects={
            "packs/level-01.scrubpack": expected_bytes,
            "packs/level-02.scrubpack": b"unexpected",
        },
    )
    assert extra["status"] == "FAIL"
    assert extra["unexpected_object_keys"] == ["packs/level-02.scrubpack"]
