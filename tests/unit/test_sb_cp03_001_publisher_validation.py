from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    ContentManifestV1,
    Environment,
    ManifestLevelV1,
    ManifestPackV1,
    ProviderCapability,
    ProviderFeature,
    ScrubpackLevelInput,
    ScrubpackPayloadInput,
    STAGING_TARGET,
    build_publication_plan,
    build_scrubpack,
    parse_content_manifest_v1,
    replay_release_events,
    serialize_publisher_validation_report,
    validate_publisher_candidate,
    validate_remote_payload,
)

EXAMPLES = PIPELINE / "schemas" / "v1" / "examples"


def _payload(role: str, level_id: str) -> ScrubpackPayloadInput:
    if role == "level_data":
        value: dict[str, object] = {
            "version": 1, "id": level_id, "name": "Test Level", "difficulty": "EASY",
            "width": 20, "height": 20, "palette": ["C01"], "cells": [0] * 400,
        }
        filename, digest_field = "level.json", "payload_sha256"
    elif role == "supply_plan_data":
        value = {
            "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": level_id,
            "ownerInput": "owner-source.json", "ownerInputSha256": "a" * 64, "columnCount": 3,
            "visiblePreviewDepth": 3, "maxRobotsPerBatch": 2, "intendedColumnClicks": [],
            "columns": [[{"batchId": f"{level_id}-b{column}", "cid": "C01", "robots": 1}]
                        for column in range(3)],
        }
        filename, digest_field = "supply-plan.json", "supply_plan_sha256"
    else:
        value = {
            "schema": "scrubbots.level.metadata.v1", "version": 1, "builderVersion": "test",
            "id": level_id, "width": 20, "height": 20, "cellCount": 400, "difficulty": "EASY",
            "columnCount": 3, "visiblePreviewDepth": 3, "fileDigests": {},
        }
        filename, digest_field = "approved-metadata.json", "payload_sha256"
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    descriptor = json.loads((EXAMPLES / filename).read_text(encoding="utf-8"))
    descriptor["attributes"]["level_id"] = level_id
    descriptor["attributes"][digest_field] = hashlib.sha256(raw).hexdigest()
    return ScrubpackPayloadInput(descriptor, raw)


def _fixture():
    level = ScrubpackLevelInput(
        "level-001", _payload("level_data", "level-001"),
        _payload("supply_plan_data", "level-001"), _payload("metadata", "level-001"),
    )
    build = build_scrubpack((level,), pack_id="test-pack", pack_version=3, created_at_utc="2026-10-05T10:00:00Z")
    manifest = ContentManifestV1(
        content_version=2,
        packs=(ManifestPackV1(
            "test-pack", 3, "packs/test-pack/v3.scrubpack", build.evidence.archive_sha256,
            build.evidence.archive_byte_length,
        ),),
        levels=(ManifestLevelV1("level-001", "test-pack"),),
    )

    descriptor = json.loads((EXAMPLES / "level.json").read_text(encoding="utf-8"))
    attrs = descriptor["attributes"]
    payload_obj = {
        "version": 1, "id": attrs["level_id"], "name": "Plan Fixture", "difficulty": "EASY",
        "width": attrs["width"], "height": attrs["height"], "palette": ["#000000FF", "#FFFFFFFF"],
        "cells": [0] * (attrs["width"] * attrs["height"] - 1) + [1],
    }
    payload = json.dumps(payload_obj, separators=(",", ":")).encode()
    attrs["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    payload_result = validate_remote_payload(descriptor, payload)
    capability = ProviderCapability(
        "local-capability-v1", "1.0",
        tuple(sorted((Environment.STAGING, Environment.PRODUCTION), key=lambda item: item.value)),
        tuple(sorted((
            ProviderFeature.STAGING_PUBLISH, ProviderFeature.PRODUCTION_PROMOTION,
            ProviderFeature.OBJECT_WRITE, ProviderFeature.INTEGRITY_VERIFY,
            ProviderFeature.CONDITIONAL_WRITE, ProviderFeature.ATOMIC_MANIFEST_PUBLISH,
        ), key=lambda item: item.value)),
    )
    replay = replay_release_events([])
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=payload_result,
        target=STAGING_TARGET, replay=replay, current_state=None,
        capability=capability, owner_approved=True,
    )
    assert plan.accepted
    return manifest, build, plan, replay, capability


def _validate(manifest=None, build=None, plan=None, replay=None, capability=None, **overrides):
    defaults = _fixture()
    manifest = manifest or defaults[0]
    build = build or defaults[1]
    plan = plan or defaults[2]
    replay = replay or defaults[3]
    capability = capability or defaults[4]
    args = dict(
        manifest_bytes=manifest.to_json_bytes(), pack_builds=(build,), previous_content_version=1,
        current_game_version="1.0.0", supported_manifest_schema_versions={"scrubbots.content.manifest.v1": (1,)},
        publication_plan=plan, current_target=STAGING_TARGET, current_replay=replay,
        current_state=None, current_content_digest=plan.content_digest,
        capability=capability, owner_approved=True,
    )
    args.update(overrides)
    return validate_publisher_candidate(**args)


def test_valid_candidate_is_immutable_deterministic_and_zero_write() -> None:
    report = _validate()
    assert report.accepted is True
    assert all(item.accepted for item in report.checks)
    assert report.remote_mutation_performed is False
    assert report.manifest_sha256 == hashlib.sha256(_fixture()[0].to_json_bytes()).hexdigest()
    assert serialize_publisher_validation_report(report) == serialize_publisher_validation_report(report)
    assert json.loads(serialize_publisher_validation_report(report))["remote_mutation_performed"] is False
    with pytest.raises(FrozenInstanceError):
        report.accepted = False  # type: ignore[misc]


@pytest.mark.parametrize("overrides", [
    {"manifest_bytes": b"{not json"},
    {"pack_builds": ()},
    {"previous_content_version": 2},
    {"current_game_version": "not-a-version"},
    {"supported_manifest_schema_versions": {"scrubbots.content.manifest.v1": ()}},
    {"owner_approved": False},
    {"current_content_digest": "f" * 64},
])
def test_invalid_stale_or_unapproved_inputs_reject_without_echo(overrides) -> None:
    report = _validate(**overrides)
    assert report.accepted is False
    assert report.remote_mutation_performed is False
    assert all(item.reason_code.isupper() and " " not in item.reason_code for item in report.checks)
    assert "{not json" not in serialize_publisher_validation_report(report)


def test_capability_change_and_target_change_reject() -> None:
    manifest, build, plan, replay, capability = _fixture()
    changed = ProviderCapability(
        capability.capability_id, "2.0", capability.environments, capability.features,
    )
    assert _validate(manifest, build, plan, replay, changed).accepted is False
    assert _validate(manifest, build, plan, replay, capability, current_target=object()).accepted is False


def test_manifest_minimum_game_version_rejects_an_older_game() -> None:
    from dataclasses import replace

    manifest, build, plan, replay, capability = _fixture()
    incompatible = replace(manifest, minimum_game_version="2.0.0")
    report = _validate(
        incompatible, build, plan, replay, capability,
        current_game_version="1.0.0",
    )
    assert report.accepted is False
    assert any(check.check_id == "content_compatibility" and not check.accepted for check in report.checks)


def test_secret_bearing_m11_inputs_and_malformed_plan_fail_closed() -> None:
    manifest, build, _, replay, capability = _fixture()
    descriptor = {"content_type": "level_data", "attributes": {"level_id": "level-001", "payload_sha256": "0" * 64},
                  "token": "ghp_" + "R" * 32}
    payload = b"{}"
    bad_plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=validate_remote_payload(descriptor, payload),
        target=STAGING_TARGET, replay=replay, current_state=None, capability=capability, owner_approved=True,
    )
    report = _validate(manifest, build, bad_plan, replay, capability, current_content_digest=bad_plan.content_digest)
    assert report.accepted is False
    serialized = serialize_publisher_validation_report(report)
    assert "ghp_" not in serialized and "token" not in serialized

    malformed = _validate(publication_plan=object())
    assert malformed.accepted is False
    assert malformed.remote_mutation_performed is False


def test_strict_manifest_parser_is_used_and_report_is_secret_free() -> None:
    manifest, *_ = _fixture()
    parsed = parse_content_manifest_v1(manifest.to_json_bytes())
    assert parsed == manifest
    report = _validate(manifest_bytes=manifest.to_json_bytes() + b"\n")
    assert report.accepted is True
    assert "token" not in serialize_publisher_validation_report(report)
