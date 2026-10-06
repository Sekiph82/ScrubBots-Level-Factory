from __future__ import annotations

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
    ManifestScheduleV1,
    ProviderCapability,
    ProviderFeature,
    ProviderIdentity,
    ProviderObjectBytesResult,
    ProviderResult,
    ProviderResultCategory,
    ScrubpackLevelInput,
    ScrubpackPayloadInput,
    StagingDownloadReasonCode,
    StagingManifestPackDigest,
    StagingManifestReceipt,
    build_candidate_manifest,
    build_scrubpack,
    serialize_staging_download_verification_receipt,
    verify_staged_manifest_download,
)

EXAMPLES = PIPELINE / "schemas" / "v1" / "examples"
MANIFEST_KEY = "manifests/current.json"


def _payload(role: str, level_id: str) -> ScrubpackPayloadInput:
    if role == "level_data":
        value: dict[str, object] = {
            "version": 1, "id": level_id, "name": "Downloaded fixture", "difficulty": "EASY",
            "width": 20, "height": 20, "palette": ["C01"], "cells": [0] * 400,
        }
        filename, digest_key, logical_path = "level.json", "payload_sha256", f"levels/{level_id}.json"
    elif role == "supply_plan_data":
        value = {
            "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": level_id,
            "ownerInput": "owner-source.json", "ownerInputSha256": "a" * 64, "columnCount": 3,
            "visiblePreviewDepth": 3, "maxRobotsPerBatch": 2, "intendedColumnClicks": [],
            "columns": [[{"batchId": f"{level_id}-b{column}", "cid": "C01", "robots": 1}]
                        for column in range(3)],
        }
        filename, digest_key, logical_path = "supply-plan.json", "supply_plan_sha256", f"supply/{level_id}.json"
    else:
        value = {
            "schema": "scrubbots.level.metadata.v1", "version": 1, "builderVersion": "CP03-007-test",
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


def _candidate() -> CandidateManifestBuildResult:
    builds = tuple(
        build_scrubpack((ScrubpackLevelInput(
            level_id,
            _payload("level_data", level_id),
            _payload("supply_plan_data", level_id),
            _payload("metadata", level_id),
        ),), pack_id=f"pack-{suffix}", pack_version=2, created_at_utc="2026-10-06T12:00:00Z")
        for suffix, level_id in (("a", "level-a"), ("b", "level-b"))
    )
    return build_candidate_manifest(
        builds,
        content_version=3,
        minimum_game_version="2.4.0",
        object_keys={f"pack-{suffix}": f"packs/pack-{suffix}/v2.scrubpack" for suffix in ("a", "b")},
        current_game_version="2.4.1",
        supported_manifest_schema_versions={CONTENT_MANIFEST_SCHEMA: {1}},
        disabled_levels=("level-a",),
        schedules=(ManifestScheduleV1("level", "level-b", "2026-10-06T12:00:00Z"),),
        prior_accepted_content_version=2,
    )


class MemoryReader:
    identity = ProviderIdentity("m14-memory-reader", "1.0")
    capabilities = ProviderCapability(
        "m14-read-capability", "1.0", (Environment.STAGING,), (ProviderFeature.INTEGRITY_VERIFY,)
    )

    def __init__(self, objects: dict[str, bytes]) -> None:
        self.objects = dict(objects)
        self.calls: list[tuple[Environment, str]] = []
        self.wrong_key: str | None = None
        self.unavailable: set[str] = set()
        self.metadata_only = False

    def read_object_bytes(self, environment: Environment, object_key: str) -> ProviderObjectBytesResult:
        self.calls.append((environment, object_key))
        if self.metadata_only:
            return ProviderResult(
                "1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id,
                environment, hashlib.sha256(self.objects[object_key]).hexdigest(),
            )
        if object_key in self.unavailable or object_key not in self.objects:
            return ProviderObjectBytesResult(
                "1.0", ProviderResultCategory.UNAVAILABLE, self.identity.provider_id,
                environment, object_key, None,
            )
        return ProviderObjectBytesResult(
            "1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id,
            environment,
            self.wrong_key if self.wrong_key is not None and object_key != MANIFEST_KEY else object_key,
            self.objects[object_key],
        )


def _setup():
    candidate = _candidate()
    receipt = StagingManifestReceipt(
        "1.0",
        candidate.manifest_bytes,
        candidate.manifest_sha256,
        candidate.manifest.content_version,
        MANIFEST_KEY,
        tuple(StagingManifestPackDigest(
            pack.pack_id, pack.object_key, pack.sha256, pack.byte_length
        ) for pack in sorted(candidate.manifest.packs, key=lambda item: item.pack_id.encode("ascii"))),
        "m14-memory-reader", "1.0", "1.0", "m14-write-capability", "1.0",
        Environment.STAGING.value, "staging:default", None, None, ("a" * 64,),
    )
    objects = {MANIFEST_KEY: candidate.manifest_bytes}
    objects.update({pack.object_key: build.archive_bytes
                    for pack, build in zip(candidate.manifest.packs, candidate.pack_builds)})
    return candidate, receipt, MemoryReader(objects)


def test_downloads_actual_manifest_and_every_pack_and_returns_immutable_exact_receipt() -> None:
    candidate, staging_receipt, provider = _setup()

    result = verify_staged_manifest_download(
        candidate=candidate, staging_receipt=staging_receipt, provider=provider
    )

    assert result.accepted
    assert result.reason_code is StagingDownloadReasonCode.VERIFIED
    assert result.manifest_read
    assert result.downloaded_pack_ids == ("pack-a", "pack-b")
    assert provider.calls == [
        (Environment.STAGING, MANIFEST_KEY),
        (Environment.STAGING, "packs/pack-a/v2.scrubpack"),
        (Environment.STAGING, "packs/pack-b/v2.scrubpack"),
    ]
    assert result.receipt is not None
    receipt = result.receipt
    assert receipt.manifest_bytes == candidate.manifest_bytes
    assert receipt.manifest_sha256 == candidate.manifest_sha256
    assert receipt.manifest_byte_length == len(candidate.manifest_bytes)
    assert receipt.content_version == candidate.manifest.content_version
    assert receipt.minimum_game_version == candidate.manifest.minimum_game_version
    assert receipt.disabled_levels == candidate.manifest.disabled_levels
    assert receipt.schedules == candidate.manifest.schedules
    assert [(pack.pack_id, pack.sha256, pack.byte_length) for pack in receipt.packs] == [
        (pack.pack_id, pack.sha256, pack.byte_length) for pack in candidate.manifest.packs
    ]
    serialized = serialize_staging_download_verification_receipt(receipt)
    assert serialized.endswith("\n")
    assert serialize_staging_download_verification_receipt(receipt) == serialized
    with pytest.raises(FrozenInstanceError):
        receipt.content_version = 4  # type: ignore[misc]


@pytest.mark.parametrize("bad_manifest", [b"", b"not a manifest", b"{} "])
def test_missing_truncated_or_tampered_manifest_bytes_fail_closed(bad_manifest: bytes) -> None:
    candidate, receipt, provider = _setup()
    provider.objects[MANIFEST_KEY] = bad_manifest

    result = verify_staged_manifest_download(candidate=candidate, staging_receipt=receipt, provider=provider)

    assert not result.accepted
    assert result.receipt is None
    assert result.reason_code in {
        StagingDownloadReasonCode.MANIFEST_INTEGRITY_FAILED,
        StagingDownloadReasonCode.MANIFEST_PARSE_FAILED,
    }
    assert len(provider.calls) == 1


def test_downloaded_manifest_from_other_valid_candidate_is_rejected_as_stale_candidate() -> None:
    candidate, receipt, provider = _setup()
    newer = replace(candidate.manifest, content_version=4).to_json_bytes()
    provider.objects[MANIFEST_KEY] = newer

    result = verify_staged_manifest_download(candidate=candidate, staging_receipt=receipt, provider=provider)

    assert not result.accepted
    assert result.reason_code is StagingDownloadReasonCode.MANIFEST_INTEGRITY_FAILED
    assert not any(key != MANIFEST_KEY for _, key in provider.calls)


@pytest.mark.parametrize("failure", ["missing", "truncated", "swapped", "wrong-key"])
def test_missing_tampered_swapped_or_wrong_key_pack_download_fails(failure: str) -> None:
    candidate, receipt, provider = _setup()
    pack = candidate.manifest.packs[0]
    if failure == "missing":
        provider.unavailable.add(pack.object_key)
    elif failure == "truncated":
        provider.objects[pack.object_key] = provider.objects[pack.object_key][:-1]
    elif failure == "swapped":
        other = candidate.manifest.packs[1]
        provider.objects[pack.object_key] = provider.objects[other.object_key]
    else:
        provider.wrong_key = "packs/wrong/v2.scrubpack"

    result = verify_staged_manifest_download(candidate=candidate, staging_receipt=receipt, provider=provider)

    assert not result.accepted
    assert result.receipt is None
    assert result.reason_code in {
        StagingDownloadReasonCode.PACK_READ_FAILED,
        StagingDownloadReasonCode.PACK_INTEGRITY_FAILED,
    }


def test_invalid_stage_receipt_candidate_and_missing_integrity_capability_fail_before_reads() -> None:
    candidate, receipt, provider = _setup()
    invalid_receipt = replace(receipt, manifest_sha256="0" * 64)
    denied_receipt = verify_staged_manifest_download(
        candidate=candidate, staging_receipt=invalid_receipt, provider=provider
    )
    assert denied_receipt.reason_code is StagingDownloadReasonCode.INVALID_STAGING_RECEIPT
    assert provider.calls == []

    provider.identity = ProviderIdentity("different-storage", "1.0")
    denied_identity = verify_staged_manifest_download(
        candidate=candidate, staging_receipt=receipt, provider=provider
    )
    assert denied_identity.reason_code is StagingDownloadReasonCode.INVALID_PROVIDER
    assert provider.calls == []

    provider.identity = MemoryReader.identity
    provider.capabilities = ProviderCapability("read-limited", "1.0", (Environment.STAGING,), ())
    denied_capability = verify_staged_manifest_download(
        candidate=candidate, staging_receipt=receipt, provider=provider
    )
    assert denied_capability.reason_code is StagingDownloadReasonCode.CAPABILITY_REJECTED
    assert provider.calls == []


def test_provider_metadata_success_without_actual_bytes_cannot_pass() -> None:
    candidate, receipt, provider = _setup()
    provider.metadata_only = True

    result = verify_staged_manifest_download(candidate=candidate, staging_receipt=receipt, provider=provider)

    assert result.reason_code is StagingDownloadReasonCode.MANIFEST_READ_FAILED
    assert result.receipt is None
    assert len(provider.calls) == 1
