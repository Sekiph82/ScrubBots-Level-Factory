from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    ContentManifestV1,
    ManifestLevelV1,
    ManifestPackV1,
    ManifestScheduleV1,
    ScrubpackLevelInput,
    ScrubpackPayloadInput,
    build_scrubpack,
    is_level_disabled,
    validate_manifest_references,
)

EXAMPLES = CONTENT_PIPELINE / "schemas" / "v1" / "examples"


def _payload(role: str, level_id: str) -> ScrubpackPayloadInput:
    if role == "level_data":
        data: dict[str, object] = {
            "version": 1, "id": level_id, "name": "Test Level", "difficulty": "EASY",
            "width": 20, "height": 20, "palette": ["C01"], "cells": [0] * 400,
        }
        filename, digest_field = "level.json", "payload_sha256"
    elif role == "supply_plan_data":
        data = {
            "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": level_id,
            "ownerInput": "owner-source.json", "ownerInputSha256": "a" * 64, "columnCount": 3,
            "visiblePreviewDepth": 3, "maxRobotsPerBatch": 2, "intendedColumnClicks": [],
            "columns": [[{"batchId": f"{level_id}-b{column}", "cid": "C01", "robots": 1}]
                        for column in range(3)],
        }
        filename, digest_field = "supply-plan.json", "supply_plan_sha256"
    else:
        data = {
            "schema": "scrubbots.level.metadata.v1", "version": 1, "builderVersion": "test",
            "id": level_id, "width": 20, "height": 20, "cellCount": 400, "difficulty": "EASY",
            "columnCount": 3, "visiblePreviewDepth": 3, "fileDigests": {},
        }
        filename, digest_field = "approved-metadata.json", "payload_sha256"
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    descriptor = json.loads((EXAMPLES / filename).read_text(encoding="utf-8"))
    descriptor["attributes"]["level_id"] = level_id
    descriptor["attributes"][digest_field] = hashlib.sha256(raw).hexdigest()
    return ScrubpackPayloadInput(descriptor, raw)


def _build(level_id: str = "level-001"):
    level = ScrubpackLevelInput(
        level_id, _payload("level_data", level_id), _payload("supply_plan_data", level_id),
        _payload("metadata", level_id),
    )
    return build_scrubpack((level,), pack_id="test-pack", pack_version=3, created_at_utc="2026-10-05T10:00:00Z")


def _manifest(build, **changes):
    pack = ManifestPackV1(
        "test-pack", 3, "packs/test-pack/v3.scrubpack", build.evidence.archive_sha256,
        build.evidence.archive_byte_length,
    )
    values = dict(
        packs=(pack,), levels=(ManifestLevelV1("level-001", "test-pack"),),
        disabled_levels=("level-001",),
        schedules=(ManifestScheduleV1("level", "level-001", "2026-10-05T10:00:00Z"),),
    )
    values.update(changes)
    return ContentManifestV1(**values)


def _reason(result, check_id: str) -> str:
    return next(check.reason_code.value for check in result.checks if check.check_id == check_id)


def test_local_m12_build_evidence_binds_every_manifest_reference() -> None:
    build = _build()
    result = validate_manifest_references(_manifest(build), (build,))
    assert result.eligible is True
    assert all(check.accepted for check in result.checks)
    assert result.to_dict() == validate_manifest_references(_manifest(build), (build,)).to_dict()


def test_case_variant_disabled_reference_and_helper_agree_with_local_m12_evidence() -> None:
    build = _build("Level-A")
    manifest = _manifest(
        build,
        levels=(ManifestLevelV1("Level-A", "test-pack"),),
        disabled_levels=("level-a",),
        schedules=(ManifestScheduleV1("level", "LEVEL-A", "2026-10-05T10:00:00Z"),),
    )

    result = validate_manifest_references(manifest, (build,))

    assert result.eligible is True
    assert all(check.accepted for check in result.checks)
    assert is_level_disabled(manifest, "Level-A") is True


def test_reference_gate_fails_closed_for_missing_pack_or_level_evidence() -> None:
    build = _build()
    missing_evidence = validate_manifest_references(_manifest(build), ())
    assert missing_evidence.eligible is False
    assert _reason(missing_evidence, "pack_evidence_set") == "MISSING_PACK_EVIDENCE"

    missing_level = validate_manifest_references(
        _manifest(build, disabled_levels=("unknown-level",)), (build,)
    )
    assert missing_level.eligible is False
    assert _reason(missing_level, "disabled_level_references") == "DISABLED_LEVEL_NOT_DECLARED"

    missing_schedule_target = validate_manifest_references(
        _manifest(build, schedules=(ManifestScheduleV1("pack", "unknown-pack", "2026-10-05T10:00:00Z"),)),
        (build,),
    )
    assert missing_schedule_target.eligible is False
    assert _reason(missing_schedule_target, "schedule_target_references") == "SCHEDULE_TARGET_NOT_DECLARED"


def test_reference_gate_binds_archive_version_membership_and_integrity() -> None:
    build = _build()
    manifest = _manifest(build)
    wrong_version = replace(build, evidence=replace(build.evidence, pack_version=4))
    result = validate_manifest_references(manifest, (wrong_version,))
    assert result.eligible is False
    assert _reason(result, "pack_version_binding") == "PACK_VERSION_MISMATCH"

    wrong_membership = replace(build, evidence=replace(build.evidence, level_ids=("different-level",)))
    result = validate_manifest_references(manifest, (wrong_membership,))
    assert result.eligible is False
    assert _reason(result, "pack_level_membership") == "PACK_MEMBERSHIP_MISMATCH"

    damaged_archive = replace(build, archive_bytes=build.archive_bytes + b"x")
    result = validate_manifest_references(manifest, (damaged_archive,))
    assert result.eligible is False
    assert _reason(result, "pack_archive_integrity") == "PACK_ARCHIVE_INVALID"


def test_reference_gate_rejects_undeclared_and_duplicate_build_evidence() -> None:
    build = _build()
    other = build_scrubpack(
        (ScrubpackLevelInput("level-002", _payload("level_data", "level-002"),
                             _payload("supply_plan_data", "level-002"), _payload("metadata", "level-002")),),
        pack_id="other-pack", pack_version=1, created_at_utc="2026-10-05T10:00:00Z",
    )
    result = validate_manifest_references(_manifest(build), (build, other))
    assert result.eligible is False
    assert _reason(result, "pack_evidence_set") == "UNDECLARED_PACK_EVIDENCE"

    result = validate_manifest_references(_manifest(build), (build, build))
    assert result.eligible is False
    assert _reason(result, "pack_evidence_set") == "DUPLICATE_PACK_EVIDENCE"

    malformed = replace(build, evidence=object())
    result = validate_manifest_references(_manifest(build), (malformed,))
    assert result.eligible is False
    assert _reason(result, "pack_evidence_set") == "INVALID_EVIDENCE_SET"


def test_reference_gate_rejects_unowned_level_and_non_manifest_inputs() -> None:
    build = _build()
    manifest = _manifest(build, levels=(ManifestLevelV1("level-001", "unknown-pack"),))
    result = validate_manifest_references(manifest, (build,))
    assert result.eligible is False
    assert _reason(result, "level_pack_references") == "LEVEL_PACK_NOT_DECLARED"
    assert _reason(result, "pack_level_membership") == "PACK_MEMBERSHIP_MISMATCH"

    invalid = validate_manifest_references(object(), (build,))
    assert invalid.eligible is False
    assert _reason(invalid, "manifest_contract") == "INVALID_MANIFEST"
