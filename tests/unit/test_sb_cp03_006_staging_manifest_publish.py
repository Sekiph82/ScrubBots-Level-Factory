from __future__ import annotations

import base64
import hashlib
import json
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    CONTENT_MANIFEST_SCHEMA,
    CandidateManifestBuildResult,
    Environment,
    ProviderCapability,
    ProviderFeature,
    ProviderIdentity,
    ProviderObjectBytesResult,
    ProviderResult,
    ProviderResultCategory,
    ReleaseState,
    ScrubpackLevelInput,
    ScrubpackPayloadInput,
    STAGING_TARGET,
    StagingManifestPrecondition,
    StagingManifestReasonCode,
    build_candidate_manifest,
    build_publication_plan,
    build_scrubpack,
    parse_content_manifest_v1,
    publish_candidate_manifest_to_staging,
    replay_release_events,
    serialize_staging_manifest_receipt,
    upload_candidate_packs_to_staging,
    validate_publisher_candidate,
    validate_remote_payload,
)

EXAMPLES = PIPELINE / "schemas" / "v1" / "examples"


def _payload(role: str, level_id: str) -> ScrubpackPayloadInput:
    if role == "level_data":
        value: dict[str, object] = {
            "version": 1, "id": level_id, "name": "Stage fixture", "difficulty": "EASY",
            "width": 20, "height": 20, "palette": ["C01"], "cells": [0] * 400,
        }
        filename, digest_key, logical_path = "level.json", "payload_sha256", f"levels/{level_id}.json"
    elif role == "supply_plan_data":
        value = {
            "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": level_id,
            "ownerInput": "owner-source.json", "ownerInputSha256": "a" * 64, "columnCount": 3,
            "visiblePreviewDepth": 3, "maxRobotsPerBatch": 2, "intendedColumnClicks": [],
            "columns": [[{"batchId": f"{level_id}-b{index}", "cid": "C01", "robots": 1}]
                        for index in range(3)],
        }
        filename, digest_key, logical_path = "supply-plan.json", "supply_plan_sha256", f"supply/{level_id}.json"
    else:
        value = {
            "schema": "scrubbots.level.metadata.v1", "version": 1, "builderVersion": "CP03-006-test",
            "id": level_id, "width": 20, "height": 20, "cellCount": 400, "difficulty": "EASY",
            "columnCount": 3, "visiblePreviewDepth": 3, "fileDigests": {},
        }
        filename, digest_key, logical_path = "approved-metadata.json", "payload_sha256", f"metadata/{level_id}.json"
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    descriptor = json.loads((EXAMPLES / filename).read_text(encoding="utf-8"))
    descriptor["logical_path"] = logical_path
    descriptor["attributes"]["level_id"] = level_id
    descriptor["attributes"][digest_key] = hashlib.sha256(raw).hexdigest()
    return ScrubpackPayloadInput(descriptor, raw)


def _build(pack_id: str, level_id: str):
    level = ScrubpackLevelInput(
        level_id,
        _payload("level_data", level_id),
        _payload("supply_plan_data", level_id),
        _payload("metadata", level_id),
    )
    return build_scrubpack((level,), pack_id=pack_id, pack_version=2, created_at_utc="2026-10-06T12:00:00Z")


def _candidate() -> CandidateManifestBuildResult:
    builds = (_build("pack-b", "level-b"), _build("pack-a", "level-a"))
    return build_candidate_manifest(
        builds,
        content_version=3,
        minimum_game_version="2.4.0",
        object_keys={f"pack-{name}": f"packs/pack-{name}/v2.scrubpack" for name in ("a", "b")},
        current_game_version="2.4.1",
        supported_manifest_schema_versions={CONTENT_MANIFEST_SCHEMA: {1}},
        prior_accepted_content_version=2,
    )


class MemoryProvider:
    identity = ProviderIdentity("m14-memory", "1.0")
    capabilities = ProviderCapability(
        "m14-capability", "1.0", (Environment.STAGING,),
        tuple(sorted((
            ProviderFeature.STAGING_PUBLISH,
            ProviderFeature.OBJECT_WRITE,
            ProviderFeature.INTEGRITY_VERIFY,
            ProviderFeature.CONDITIONAL_WRITE,
        ), key=lambda item: item.value)),
    )

    def __init__(self) -> None:
        self.pack_objects: dict[str, bytes] = {}
        self.manifests: dict[tuple[str, str], bytes] = {}
        self.calls: list[tuple[str, str, bytes | None]] = []
        self.manifest_expected_digests: list[str | None] = []
        self.fail_manifest = False
        self.wrong_manifest_digest = False

    def write_object_bytes(self, environment, object_key, content_digest, content_bytes, *, if_absent):
        self.calls.append(("pack-write", object_key, content_bytes))
        if environment is not Environment.STAGING or not if_absent:
            return ProviderResult("1.0", ProviderResultCategory.INVALID_REQUEST, self.identity.provider_id, environment)
        actual = hashlib.sha256(content_bytes).hexdigest()
        if actual != content_digest:
            return ProviderResult("1.0", ProviderResultCategory.INTEGRITY_MISMATCH, self.identity.provider_id, environment)
        if object_key in self.pack_objects:
            prior = hashlib.sha256(self.pack_objects[object_key]).hexdigest()
            return ProviderResult("1.0", ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                  self.identity.provider_id, environment, prior)
        self.pack_objects[object_key] = bytes(content_bytes)
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id, environment, actual)

    def verify_object(self, environment, object_key, expected_digest):
        self.calls.append(("pack-verify", object_key, None))
        raw = self.pack_objects.get(object_key)
        digest = hashlib.sha256(raw).hexdigest() if raw is not None else None
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS if digest else ProviderResultCategory.UNAVAILABLE,
                              self.identity.provider_id, environment, digest)

    def read_object_bytes(self, environment, object_key):
        self.calls.append(("pack-read", object_key, None))
        raw = self.pack_objects.get(object_key)
        return ProviderObjectBytesResult(
            "1.0", ProviderResultCategory.SUCCESS if raw is not None else ProviderResultCategory.UNAVAILABLE,
            self.identity.provider_id, environment, object_key, raw,
        )

    def write_manifest_conditionally(
        self, environment, target_id, object_key, content_digest, content_bytes, *, expected_prior_sha256
    ):
        self.calls.append(("manifest-write", object_key, content_bytes))
        self.manifest_expected_digests.append(expected_prior_sha256)
        if environment is not Environment.STAGING:
            return ProviderResult("1.0", ProviderResultCategory.INVALID_REQUEST, self.identity.provider_id, environment)
        slot = (target_id, object_key)
        existing = self.manifests.get(slot)
        actual_prior = hashlib.sha256(existing).hexdigest() if existing is not None else None
        if actual_prior != expected_prior_sha256:
            return ProviderResult("1.0", ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                  self.identity.provider_id, environment, actual_prior)
        if self.fail_manifest:
            return ProviderResult("1.0", ProviderResultCategory.TRANSIENT_FAILURE, self.identity.provider_id, environment)
        self.manifests[slot] = bytes(content_bytes)
        digest = "0" * 64 if self.wrong_manifest_digest else hashlib.sha256(content_bytes).hexdigest()
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id, environment, digest)


def _validation_report(candidate: CandidateManifestBuildResult, provider: MemoryProvider):
    descriptor = json.loads((EXAMPLES / "level.json").read_text(encoding="utf-8"))
    level_id = candidate.pack_builds[0].evidence.level_ids[0]
    payload_value = {
        "version": 1, "id": level_id, "name": "Plan fixture", "difficulty": "EASY",
        "width": 20, "height": 20, "palette": ["#000000FF", "#FFFFFFFF"],
        "cells": [0] * 399 + [1],
    }
    payload = json.dumps(payload_value, separators=(",", ":")).encode("utf-8")
    descriptor["attributes"]["level_id"] = level_id
    descriptor["attributes"]["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    payload_result = validate_remote_payload(descriptor, payload)
    replay = replay_release_events(())
    plan = build_publication_plan(
        descriptor=descriptor,
        payload=payload,
        payload_result=payload_result,
        target=STAGING_TARGET,
        replay=replay,
        current_state=None,
        capability=provider.capabilities,
        owner_approved=True,
    )
    assert plan.accepted
    return validate_publisher_candidate(
        manifest_bytes=candidate.manifest_bytes,
        pack_builds=candidate.pack_builds,
        previous_content_version=2,
        current_game_version="2.4.1",
        supported_manifest_schema_versions={CONTENT_MANIFEST_SCHEMA: (1,)},
        publication_plan=plan,
        current_target=STAGING_TARGET,
        current_replay=replay,
        current_state=None,
        current_content_digest=plan.content_digest,
        capability=provider.capabilities,
        owner_approved=True,
    )


def _case(*, prior_manifest: bytes | None = None):
    candidate = _candidate()
    provider = MemoryProvider()
    upload = upload_candidate_packs_to_staging(candidate, provider)
    validation = _validation_report(candidate, provider)
    if prior_manifest is None:
        precondition = StagingManifestPrecondition(
            STAGING_TARGET.logical_target_id, "manifests/current.json", False, None, None, None
        )
    else:
        prior = parse_content_manifest_v1(prior_manifest)
        precondition = StagingManifestPrecondition(
            STAGING_TARGET.logical_target_id, "manifests/current.json", True,
            hashlib.sha256(prior_manifest).hexdigest(), prior.content_version, prior_manifest,
        )
        provider.manifests[(STAGING_TARGET.logical_target_id, precondition.object_key)] = prior_manifest
    provider.calls.clear()
    return candidate, provider, upload, validation, precondition


def _publish(candidate, provider, upload, validation, precondition, **overrides):
    args = dict(
        candidate=candidate,
        validation_report=validation,
        pack_upload_report=upload,
        target=STAGING_TARGET,
        precondition=precondition,
        release_events=(),
        provider=provider,
    )
    args.update(overrides)
    return publish_candidate_manifest_to_staging(**args)


def test_stages_exact_manifest_after_all_pack_integrity_receipts_and_records_release_state() -> None:
    candidate, provider, upload, validation, precondition = _case()

    result = _publish(candidate, provider, upload, validation, precondition)

    assert result.accepted is True
    assert result.reason_code is StagingManifestReasonCode.STAGED
    assert result.manifest_write_attempted and result.references_revalidated
    assert result.receipt is not None
    receipt = result.receipt
    assert receipt.manifest_bytes == candidate.manifest_bytes
    assert receipt.manifest_sha256 == candidate.manifest_sha256
    assert receipt.content_version == candidate.manifest.content_version == 3
    assert receipt.expected_prior_manifest_sha256 is None
    assert receipt.target_environment == "staging"
    assert receipt.target_id == STAGING_TARGET.logical_target_id
    assert receipt.provider_id == provider.identity.provider_id
    assert receipt.capability_id == provider.capabilities.capability_id
    assert [(item.pack_id, item.sha256) for item in receipt.referenced_pack_digests] == [
        (pack.pack_id, pack.sha256) for pack in sorted(candidate.manifest.packs, key=lambda item: item.pack_id)
    ]
    assert [event.to_state for event in result.appended_release_events] == [
        ReleaseState.DRAFT, ReleaseState.VALIDATED, ReleaseState.STAGED
    ]
    replay = replay_release_events(result.appended_release_events)
    assert replay.accepted
    assert replay.snapshots[0].state is ReleaseState.STAGED
    assert receipt.release_event_digests == tuple(event.event_digest for event in result.appended_release_events)
    assert provider.calls[-1] == ("manifest-write", precondition.object_key, candidate.manifest_bytes)
    assert len([item for item in provider.calls if item[0] == "manifest-write"]) == 1
    serialized = serialize_staging_manifest_receipt(receipt)
    assert json.loads(serialized)["manifest_bytes_base64"] == base64.b64encode(candidate.manifest_bytes).decode("ascii")
    assert serialize_staging_manifest_receipt(receipt) == serialized
    with pytest.raises(FrozenInstanceError):
        receipt.content_version = 4  # type: ignore[misc]


def test_existing_manifest_requires_exact_prior_digest_and_monotonic_successor() -> None:
    candidate = _candidate()
    prior = replace(candidate.manifest, content_version=2).to_json_bytes()
    candidate, provider, upload, validation, precondition = _case(prior_manifest=prior)

    result = _publish(candidate, provider, upload, validation, precondition)

    assert result.accepted
    assert provider.manifest_expected_digests == [hashlib.sha256(prior).hexdigest()]
    assert result.receipt is not None
    assert result.receipt.expected_prior_manifest_sha256 == hashlib.sha256(prior).hexdigest()
    assert result.receipt.expected_prior_content_version == 2
    assert result.receipt.content_version == 3


def test_existing_validated_release_history_appends_only_staged_and_receipt_is_canonical() -> None:
    candidate, provider, upload, validation, precondition = _case()
    initial = _publish(candidate, provider, upload, validation, precondition)
    assert initial.accepted
    validated_history = initial.appended_release_events[:2]

    candidate, provider, upload, validation, precondition = _case()
    result = _publish(candidate, provider, upload, validation, precondition,
                      release_events=validated_history)

    assert result.accepted
    assert [event.to_state for event in result.appended_release_events] == [ReleaseState.STAGED]
    assert result.receipt is not None
    assert serialize_staging_manifest_receipt(result.receipt).endswith("\n")
    forged = replace(result.receipt, manifest_bytes=result.receipt.manifest_bytes + b" ")
    with pytest.raises(ValueError, match="invalid STAGING manifest receipt"):
        serialize_staging_manifest_receipt(forged)


@pytest.mark.parametrize("override", [
    {"validation_report": None},
    {"pack_upload_report": None},
    {"target": object()},
    {"precondition": object()},
    {"release_events": (object(),)},
])
def test_invalid_authority_receipts_targets_preconditions_or_history_make_no_manifest_write(override) -> None:
    candidate, provider, upload, validation, precondition = _case()
    values = dict(candidate=candidate, validation_report=validation, pack_upload_report=upload,
                  target=STAGING_TARGET, precondition=precondition, release_events=(), provider=provider)
    values.update(override)

    result = publish_candidate_manifest_to_staging(**values)

    assert result.accepted is False
    assert result.receipt is None
    assert not result.manifest_write_attempted
    assert not any(kind == "manifest-write" for kind, _, _ in provider.calls)


def test_rejected_validation_incomplete_pack_receipt_and_production_target_fail_closed() -> None:
    candidate, provider, upload, validation, precondition = _case()
    rejected_validation = replace(validation, accepted=False)
    bad_upload = replace(upload, uploaded_packs=upload.uploaded_packs[:-1])
    assert _publish(candidate, provider, upload, rejected_validation, precondition).reason_code is StagingManifestReasonCode.VALIDATION_REJECTED
    assert _publish(candidate, provider, bad_upload, validation, precondition).reason_code is StagingManifestReasonCode.PACKS_NOT_VERIFIED
    assert _publish(candidate, provider, upload, validation, precondition, target=replace(
        STAGING_TARGET, environment=Environment.PRODUCTION,
        logical_target_id="production:default", state_namespace="production:state",
        content_namespace="production:content", direct_publication_permitted=False,
        promotion_required=True,
    )).accepted is False
    assert not any(kind == "manifest-write" for kind, _, _ in provider.calls)


def test_bad_object_key_and_malformed_prior_manifest_are_rejected_before_mutation() -> None:
    candidate, provider, upload, validation, precondition = _case()
    bad_key = replace(precondition, object_key="../production/manifest.json")
    assert _publish(candidate, provider, upload, validation, bad_key).reason_code is StagingManifestReasonCode.INVALID_PRECONDITION
    malformed = replace(precondition, expected_present=True, expected_prior_sha256="a" * 64,
                        expected_prior_content_version=2, expected_prior_manifest_bytes=b"not-json")
    assert _publish(candidate, provider, upload, validation, malformed).reason_code is StagingManifestReasonCode.INVALID_PRECONDITION
    assert not any(kind == "manifest-write" for kind, _, _ in provider.calls)


def test_stale_cas_precondition_does_not_overwrite_and_records_failed_release_state() -> None:
    candidate, provider, upload, validation, precondition = _case()
    slot = (precondition.target_id, precondition.object_key)
    provider.manifests[slot] = b"concurrent manifest bytes"

    result = _publish(candidate, provider, upload, validation, precondition)

    assert result.accepted is False
    assert result.reason_code is StagingManifestReasonCode.STALE_PRECONDITION
    assert result.receipt is None
    assert provider.manifests[slot] == b"concurrent manifest bytes"
    assert [event.to_state for event in result.appended_release_events] == [
        ReleaseState.DRAFT, ReleaseState.VALIDATED, ReleaseState.FAILED
    ]
    assert replay_release_events(result.appended_release_events).accepted


def test_provider_failure_and_wrong_reported_manifest_digest_never_claim_staged() -> None:
    candidate, provider, upload, validation, precondition = _case()
    provider.fail_manifest = True
    failed = _publish(candidate, provider, upload, validation, precondition)
    assert failed.accepted is False and failed.reason_code is StagingManifestReasonCode.MANIFEST_WRITE_FAILED
    assert failed.appended_release_events[-1].to_state is ReleaseState.FAILED
    assert replay_release_events(failed.appended_release_events).accepted

    candidate, provider, upload, validation, precondition = _case()
    provider.wrong_manifest_digest = True
    mismatched = _publish(candidate, provider, upload, validation, precondition)
    assert mismatched.accepted is False
    assert mismatched.reason_code is StagingManifestReasonCode.MANIFEST_WRITE_FAILED
    assert mismatched.appended_release_events[-1].to_state is ReleaseState.FAILED


def test_invalid_candidate_bytes_and_inadequate_capabilities_are_rejected_without_manifest_write() -> None:
    candidate, provider, upload, validation, precondition = _case()
    stale = replace(candidate, manifest_sha256="0" * 64)
    assert _publish(stale, provider, upload, validation, precondition).reason_code is StagingManifestReasonCode.INVALID_CANDIDATE

    candidate, provider, upload, validation, precondition = _case()
    provider.capabilities = ProviderCapability("limited", "1.0", (Environment.STAGING,), ())
    denied = _publish(candidate, provider, upload, validation, precondition)
    assert denied.reason_code is StagingManifestReasonCode.CAPABILITY_REJECTED
    assert not any(kind == "manifest-write" for kind, _, _ in provider.calls)

    candidate, provider, upload, validation, precondition = _case()
    malformed_integrity_authority = replace(
        upload,
        negotiation=replace(upload.negotiation, accepted=False),
    )
    denied_integrity = _publish(candidate, provider, malformed_integrity_authority, validation, precondition)
    assert denied_integrity.reason_code is StagingManifestReasonCode.PACKS_NOT_VERIFIED
    assert not any(kind == "manifest-write" for kind, _, _ in provider.calls)
