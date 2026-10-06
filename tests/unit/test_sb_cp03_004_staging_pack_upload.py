from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

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
    ScrubpackLevelInput,
    ScrubpackPayloadInput,
    build_candidate_manifest,
    build_scrubpack,
    inspect_scrubpack,
    upload_candidate_packs_to_staging,
)

EXAMPLES = PIPELINE / "schemas" / "v1" / "examples"


def _payload(role: str, level_id: str) -> ScrubpackPayloadInput:
    if role == "level_data":
        value: dict[str, object] = {
            "version": 1, "id": level_id, "name": "Upload fixture", "difficulty": "EASY",
            "width": 20, "height": 20, "palette": ["C01"], "cells": [0] * 400,
        }
        example, digest_key, path = "level.json", "payload_sha256", f"levels/{level_id}.json"
    elif role == "supply_plan_data":
        value = {
            "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": level_id,
            "ownerInput": "owner-source.json", "ownerInputSha256": "a" * 64, "columnCount": 3,
            "visiblePreviewDepth": 3, "maxRobotsPerBatch": 2, "intendedColumnClicks": [],
            "columns": [[{"batchId": f"{level_id}-b{index}", "cid": "C01", "robots": 1}]
                        for index in range(3)],
        }
        example, digest_key, path = "supply-plan.json", "supply_plan_sha256", f"supply/{level_id}.json"
    else:
        value = {
            "schema": "scrubbots.level.metadata.v1", "version": 1, "builderVersion": "CP03-004-test",
            "id": level_id, "width": 20, "height": 20, "cellCount": 400, "difficulty": "EASY",
            "columnCount": 3, "visiblePreviewDepth": 3, "fileDigests": {},
        }
        example, digest_key, path = "approved-metadata.json", "payload_sha256", f"metadata/{level_id}.json"
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    descriptor = json.loads((EXAMPLES / example).read_text(encoding="utf-8"))
    descriptor["logical_path"] = path
    descriptor["attributes"]["level_id"] = level_id
    descriptor["attributes"][digest_key] = hashlib.sha256(raw).hexdigest()
    return ScrubpackPayloadInput(descriptor, raw)


def _pack(pack_id: str, level_id: str):
    level = ScrubpackLevelInput(
        level_id, _payload("level_data", level_id),
        _payload("supply_plan_data", level_id), _payload("metadata", level_id),
    )
    return build_scrubpack(
        (level,), pack_id=pack_id, pack_version=2, created_at_utc="2026-10-06T12:00:00Z"
    )


def _candidate() -> CandidateManifestBuildResult:
    builds = (_pack("pack-b", "level-b"), _pack("pack-a", "level-a"))
    return build_candidate_manifest(
        builds,
        content_version=3,
        minimum_game_version="2.4.0",
        object_keys={f"pack-{name}": f"packs/pack-{name}/v2.scrubpack" for name in ("a", "b")},
        current_game_version="2.4.1",
        supported_manifest_schema_versions={CONTENT_MANIFEST_SCHEMA: {1}},
    )


class MemoryProvider:
    identity = ProviderIdentity("test-memory", "1.0")
    capabilities = ProviderCapability(
        "memory-capability", "1.0", (Environment.STAGING,),
        tuple(sorted((ProviderFeature.OBJECT_WRITE, ProviderFeature.INTEGRITY_VERIFY,
                      ProviderFeature.CONDITIONAL_WRITE), key=lambda feature: feature.value)),
    )

    def __init__(self, *, fail_key: str | None = None, omit_integrity: bool = False) -> None:
        self.objects: dict[str, bytes] = {}
        self.calls: list[tuple[str, str, bytes | None]] = []
        self.fail_key = fail_key
        self.omit_integrity = omit_integrity
        self.read_overrides: dict[str, tuple[str, bytes]] = {}

    def write_object_bytes(
        self, environment: Environment, object_key: str, content_digest: str,
        content_bytes: bytes, *, if_absent: bool,
    ) -> ProviderResult:
        self.calls.append(("write", object_key, content_bytes))
        if environment is not Environment.STAGING or not if_absent:
            return ProviderResult("1.0", ProviderResultCategory.INVALID_REQUEST, self.identity.provider_id, environment)
        if object_key == self.fail_key:
            return ProviderResult("1.0", ProviderResultCategory.TRANSIENT_FAILURE, self.identity.provider_id, environment)
        actual = hashlib.sha256(content_bytes).hexdigest()
        if actual != content_digest:
            return ProviderResult("1.0", ProviderResultCategory.INTEGRITY_MISMATCH, self.identity.provider_id, environment)
        if object_key in self.objects:
            prior = hashlib.sha256(self.objects[object_key]).hexdigest()
            return ProviderResult("1.0", ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                  self.identity.provider_id, environment, prior)
        self.objects[object_key] = bytes(content_bytes)
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id, environment, actual)

    def verify_object(self, environment: Environment, object_key: str, expected_digest: str) -> ProviderResult:
        self.calls.append(("verify", object_key, None))
        raw = self.objects.get(object_key)
        digest = hashlib.sha256(raw).hexdigest() if raw is not None else None
        if self.omit_integrity:
            digest = None
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS if raw is not None else ProviderResultCategory.UNAVAILABLE,
                              self.identity.provider_id, environment, digest)

    def read_object_bytes(self, environment: Environment, object_key: str) -> ProviderObjectBytesResult:
        self.calls.append(("read", object_key, None))
        returned_key, raw = self.read_overrides.get(
            object_key, (object_key, self.objects.get(object_key, b""))
        )
        return ProviderObjectBytesResult(
            "1.0", ProviderResultCategory.SUCCESS if object_key in self.objects else ProviderResultCategory.UNAVAILABLE,
            self.identity.provider_id, environment, returned_key, raw,
        )


def test_uploads_exact_packs_in_deterministic_order_then_authorizes_manifest_step() -> None:
    candidate = _candidate()
    provider = MemoryProvider()

    report = upload_candidate_packs_to_staging(candidate, provider)

    assert candidate.publishable is True
    assert report.accepted is True and report.manifest_write_authorized is True
    assert report.manifest_sha256 == candidate.manifest_sha256
    assert report.reason_code.value == "COMPLETE"
    assert [(kind, key) for kind, key, _ in provider.calls] == [
        ("write", "packs/pack-a/v2.scrubpack"), ("verify", "packs/pack-a/v2.scrubpack"),
        ("read", "packs/pack-a/v2.scrubpack"),
        ("write", "packs/pack-b/v2.scrubpack"), ("verify", "packs/pack-b/v2.scrubpack"),
        ("read", "packs/pack-b/v2.scrubpack"),
    ]
    for pack in candidate.manifest.packs:
        build = next(item for item in candidate.pack_builds if item.evidence.pack_id == pack.pack_id)
        assert provider.objects[pack.object_key] == build.archive_bytes
        inspected = inspect_scrubpack(provider.objects[pack.object_key])
        assert inspected.accepted is True
        assert inspected.pack_id == pack.pack_id
    assert [item.sequence for item in report.uploaded_packs] == [1, 2]
    assert all(item.idempotent_existing_object is False for item in report.uploaded_packs)


def test_identical_existing_objects_are_idempotent_only_after_digest_verification() -> None:
    candidate = _candidate()
    provider = MemoryProvider()
    for pack in candidate.manifest.packs:
        build = next(item for item in candidate.pack_builds if item.evidence.pack_id == pack.pack_id)
        provider.objects[pack.object_key] = build.archive_bytes

    report = upload_candidate_packs_to_staging(candidate, provider)

    assert report.accepted and report.manifest_write_authorized
    assert all(item.idempotent_existing_object for item in report.uploaded_packs)
    assert [kind for kind, _, _ in provider.calls] == [
        "write", "verify", "read", "write", "verify", "read"
    ]


def test_conflicting_existing_digest_stops_before_later_packs_and_withholds_manifest_authority() -> None:
    candidate = _candidate()
    provider = MemoryProvider()
    first = candidate.manifest.packs[0]
    provider.objects[first.object_key] = b"different existing bytes"

    report = upload_candidate_packs_to_staging(candidate, provider)

    assert report.accepted is False and report.manifest_write_authorized is False
    assert report.failed_object_key == first.object_key
    assert report.reason_code.value == "OBJECT_INTEGRITY_FAILED"
    assert [(kind, key) for kind, key, _ in provider.calls] == [
        ("write", first.object_key), ("verify", first.object_key)
    ]


def test_first_write_failure_or_missing_integrity_proof_blocks_authority_immediately() -> None:
    candidate = _candidate()
    first = candidate.manifest.packs[0]
    failed = upload_candidate_packs_to_staging(candidate, MemoryProvider(fail_key=first.object_key))
    unverified = upload_candidate_packs_to_staging(candidate, MemoryProvider(omit_integrity=True))

    assert failed.accepted is False and failed.manifest_write_authorized is False
    assert failed.reason_code.value == "OBJECT_WRITE_FAILED"
    assert len(failed.uploaded_packs) == 0
    assert unverified.accepted is False and unverified.manifest_write_authorized is False
    assert unverified.reason_code.value == "OBJECT_INTEGRITY_FAILED"
    assert len(unverified.uploaded_packs) == 0


def test_missing_capability_and_invalid_candidate_make_no_provider_calls() -> None:
    candidate = _candidate()
    missing = MemoryProvider()
    missing.capabilities = ProviderCapability("limited-capability", "1.0", (Environment.STAGING,), ())
    denied = upload_candidate_packs_to_staging(candidate, missing)
    invalid = upload_candidate_packs_to_staging(object(), MemoryProvider())

    assert denied.manifest_write_authorized is False
    assert denied.reason_code.value == "CAPABILITY_REJECTED"
    assert missing.calls == []
    assert invalid.manifest_write_authorized is False
    assert invalid.reason_code.value == "INVALID_CANDIDATE"


def test_reported_provider_success_cannot_hide_truncated_mutated_or_swapped_read_bytes() -> None:
    candidate = _candidate()
    first, second = candidate.manifest.packs
    second_build = next(item for item in candidate.pack_builds if item.evidence.pack_id == second.pack_id)
    first_build = next(item for item in candidate.pack_builds if item.evidence.pack_id == first.pack_id)
    variants = (
        (first.object_key, (first.object_key, first_build.archive_bytes[:-1])),
        (first.object_key, (first.object_key, first_build.archive_bytes[:-1] + b"x")),
        (first.object_key, (first.object_key, second_build.archive_bytes)),
        (first.object_key, ("packs/wrong-key/v2.scrubpack", first_build.archive_bytes)),
    )

    for object_key, override in variants:
        provider = MemoryProvider()
        provider.read_overrides[object_key] = override
        report = upload_candidate_packs_to_staging(candidate, provider)
        assert report.accepted is False
        assert report.manifest_write_authorized is False
        assert report.reason_code.value == "OBJECT_INTEGRITY_FAILED"
        assert report.failed_object_key == object_key


def test_candidate_with_stale_manifest_digest_is_rejected_before_any_object_write() -> None:
    candidate = _candidate()
    provider = MemoryProvider()
    stale = CandidateManifestBuildResult(
        candidate.manifest, candidate.manifest_bytes, "0" * 64, candidate.pack_builds,
        candidate.strict_round_trip_valid, candidate.references, candidate.compatibility, candidate.successor,
    )

    report = upload_candidate_packs_to_staging(stale, provider)

    assert report.manifest_write_authorized is False
    assert report.reason_code.value == "INVALID_CANDIDATE"
    assert provider.calls == []
