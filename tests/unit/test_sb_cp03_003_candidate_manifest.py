from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    CONTENT_MANIFEST_SCHEMA,
    CandidateManifestError,
    ManifestScheduleV1,
    ScrubpackLevelInput,
    ScrubpackPayloadInput,
    build_candidate_manifest,
    build_scrubpack,
    parse_content_manifest_v1,
)

EXAMPLES = CONTENT_PIPELINE / "schemas" / "v1" / "examples"


def _payload(role: str, level_id: str) -> ScrubpackPayloadInput:
    if role == "level_data":
        value: dict[str, object] = {
            "version": 1, "id": level_id, "name": "Manifest fixture", "difficulty": "EASY",
            "width": 20, "height": 20, "palette": ["C01"], "cells": [0] * 400,
        }
        example, digest_key, logical_path = "level.json", "payload_sha256", f"levels/{level_id}.json"
    elif role == "supply_plan_data":
        value = {
            "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": level_id,
            "ownerInput": "owner-source.json", "ownerInputSha256": "a" * 64, "columnCount": 3,
            "visiblePreviewDepth": 3, "maxRobotsPerBatch": 2, "intendedColumnClicks": [],
            "columns": [[{"batchId": f"{level_id}-b{index}", "cid": "C01", "robots": 1}]
                        for index in range(3)],
        }
        example, digest_key, logical_path = "supply-plan.json", "supply_plan_sha256", f"supply/{level_id}.json"
    else:
        value = {
            "schema": "scrubbots.level.metadata.v1", "version": 1, "builderVersion": "CP03-003-test",
            "id": level_id, "width": 20, "height": 20, "cellCount": 400, "difficulty": "EASY",
            "columnCount": 3, "visiblePreviewDepth": 3, "fileDigests": {},
        }
        example, digest_key, logical_path = "approved-metadata.json", "payload_sha256", f"metadata/{level_id}.json"
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    descriptor = json.loads((EXAMPLES / example).read_text(encoding="utf-8"))
    descriptor["logical_path"] = logical_path
    descriptor["attributes"]["level_id"] = level_id
    descriptor["attributes"][digest_key] = hashlib.sha256(raw).hexdigest()
    return ScrubpackPayloadInput(descriptor, raw)


def _pack(pack_id: str, *level_ids: str):
    levels = tuple(
        ScrubpackLevelInput(level_id, _payload("level_data", level_id),
                            _payload("supply_plan_data", level_id), _payload("metadata", level_id))
        for level_id in level_ids
    )
    return build_scrubpack(
        levels, pack_id=pack_id, pack_version=3, created_at_utc="2026-10-06T12:00:00Z"
    )


def _candidate(builds, **overrides):
    values: dict[str, object] = {
        "content_version": 7,
        "minimum_game_version": "2.4.0",
        "object_keys": {build.evidence.pack_id: f"packs/{build.evidence.pack_id}/v3.scrubpack" for build in builds},
        "current_game_version": "2.4.1",
        "supported_manifest_schema_versions": {CONTENT_MANIFEST_SCHEMA: {1}},
    }
    values.update(overrides)
    return build_candidate_manifest(builds, **values)


def test_candidate_manifest_hashes_exact_m12_builds_and_is_deterministic() -> None:
    build = _pack("pack-one", "level-001", "level-002")
    first = _candidate(
        (build,), disabled_levels=("level-002",),
        schedules=(ManifestScheduleV1("level", "level-001", "2026-10-06T12:00:00Z"),),
        prior_accepted_content_version=6,
    )
    second = _candidate(
        (build,), disabled_levels=("level-002",),
        schedules=(ManifestScheduleV1("level", "level-001", "2026-10-06T12:00:00Z"),),
        prior_accepted_content_version=6,
    )

    assert first.publishable is True
    assert first.strict_round_trip_valid is True
    assert first.references.eligible is True
    assert first.compatibility.compatible is True
    assert first.successor is not None and first.successor.accepted is True
    assert first.manifest_bytes == second.manifest_bytes
    assert first.manifest_sha256 == hashlib.sha256(first.manifest_bytes).hexdigest()
    assert first.manifest_bytes == parse_content_manifest_v1(first.manifest_bytes).to_json_bytes()
    assert first.manifest.packs[0].sha256 == hashlib.sha256(build.archive_bytes).hexdigest()
    assert first.manifest.packs[0].byte_length == len(build.archive_bytes)
    assert [(level.level_id, level.pack_id) for level in first.manifest.levels] == [
        ("level-001", "pack-one"), ("level-002", "pack-one")
    ]
    assert first.manifest.disabled_levels == ("level-002",)
    assert first.manifest.schedules[0].target_id == "level-001"


def test_candidate_is_not_publishable_when_exact_pack_evidence_or_metadata_fails() -> None:
    build = _pack("pack-one", "level-001")
    damaged = replace(build, archive_bytes=build.archive_bytes + b"tamper")
    bad_reference = _candidate((damaged,))
    bad_disabled = _candidate((build,), disabled_levels=("unknown-level",))
    bad_schedule = _candidate(
        (build,), schedules=(ManifestScheduleV1("pack", "unknown-pack", "2026-10-06T12:00:00Z"),)
    )

    assert bad_reference.publishable is False
    assert bad_reference.references.eligible is False
    assert any(not check.accepted for check in bad_reference.references.checks)
    assert bad_disabled.publishable is False
    assert bad_disabled.references.eligible is False
    assert bad_schedule.publishable is False
    assert bad_schedule.references.eligible is False


def test_compatibility_and_prior_version_are_explicit_publishability_gates() -> None:
    build = _pack("pack-one", "level-001")
    too_old = _candidate((build,), current_game_version="2.3.9")
    same_version = _candidate((build,), prior_accepted_content_version=7)

    assert too_old.compatibility.compatible is False
    assert too_old.publishable is False
    assert same_version.successor is not None and same_version.successor.accepted is False
    assert same_version.publishable is False


def test_candidate_rejects_missing_or_extra_explicit_pack_object_keys() -> None:
    build = _pack("pack-one", "level-001")
    for keys in ({}, {"pack-one": "packs/pack-one/v3.scrubpack", "extra": "packs/extra/v1.scrubpack"}):
        with pytest.raises(CandidateManifestError, match="exactly cover"):
            _candidate((build,), object_keys=keys)


def test_candidate_rejects_empty_pack_evidence_and_duplicate_level_ownership() -> None:
    with pytest.raises(CandidateManifestError, match="at least one"):
        _candidate(())
    first, second = _pack("pack-one", "level-001"), _pack("pack-two", "level-001")
    with pytest.raises(CandidateManifestError, match="M13 contracts"):
        _candidate((first, second))
