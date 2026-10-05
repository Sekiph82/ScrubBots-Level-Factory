from __future__ import annotations

import ast
import hashlib
import io
import json
import sys
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    ScrubpackBuildError,
    ScrubpackLevelInput,
    ScrubpackPayloadInput,
    build_scrubpack,
)
from scrubbots_content_pipeline.scrubpack_spec import (  # noqa: E402
    PACK_MANIFEST_PATH,
    ScrubpackManifestV1,
    normalize_created_at_utc,
)


EXAMPLES = CONTENT_PIPELINE / "schemas" / "v1" / "examples"


def _json_bytes(value: dict[str, object]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _payload(role: str, level_id: str = "level-001") -> ScrubpackPayloadInput:
    if role == "level_data":
        payload_value: dict[str, object] = {
            "version": 1,
            "id": level_id,
            "name": "Test Level",
            "difficulty": "EASY",
            "width": 20,
            "height": 20,
            "palette": ["C01"],
            "cells": [0] * 400,
        }
        filename = "level.json"
        digest_field = "payload_sha256"
    elif role == "supply_plan_data":
        payload_value = {
            "schema": "scrubbots.level_supply_plan.v1",
            "version": 1,
            "levelId": level_id,
            "ownerInput": "owner-source.json",
            "ownerInputSha256": "a" * 64,
            "columnCount": 3,
            "visiblePreviewDepth": 3,
            "maxRobotsPerBatch": 2,
            "intendedColumnClicks": [],
            "columns": [
                [{"batchId": f"{level_id}-b{column}", "cid": "C01", "robots": 1}]
                for column in range(3)
            ],
        }
        filename = "supply-plan.json"
        digest_field = "supply_plan_sha256"
    else:
        payload_value = {
            "schema": "scrubbots.level.metadata.v1",
            "version": 1,
            "builderVersion": "test",
            "id": level_id,
            "width": 20,
            "height": 20,
            "cellCount": 400,
            "difficulty": "EASY",
            "columnCount": 3,
            "visiblePreviewDepth": 3,
            "fileDigests": {},
        }
        filename = "approved-metadata.json"
        digest_field = "payload_sha256"

    payload_bytes = _json_bytes(payload_value)
    descriptor = json.loads((EXAMPLES / filename).read_text(encoding="utf-8"))
    descriptor["attributes"]["level_id"] = level_id
    descriptor["attributes"][digest_field] = hashlib.sha256(payload_bytes).hexdigest()
    return ScrubpackPayloadInput(descriptor, payload_bytes)


def _level(level_id: str = "level-001") -> ScrubpackLevelInput:
    return ScrubpackLevelInput(
        level_id=level_id,
        level_data=_payload("level_data", level_id),
        supply_plan=_payload("supply_plan_data", level_id),
        metadata=_payload("metadata", level_id),
    )


def _build(
    levels,
    *,
    pack_id: str = "test-pack",
    pack_version: int = 1,
    created_at_utc: str = "2026-10-05T10:00:00Z",
) -> object:
    return build_scrubpack(
        levels,
        pack_id=pack_id,
        pack_version=pack_version,
        created_at_utc=created_at_utc,
    )


def test_builder_packages_only_validated_payloads_at_fixed_paths() -> None:
    level = _level()
    result = _build((level,))
    with ZipFile(io.BytesIO(result.archive_bytes)) as archive:
        assert tuple(archive.namelist()) == result.evidence.member_names
        manifest = json.loads(archive.read(PACK_MANIFEST_PATH))
        assert manifest["schema"] == "scrubbots.scrubpack.manifest.v1"
        assert manifest["version"] == 1
        assert manifest["packId"] == "test-pack"
        assert manifest["packVersion"] == 1
        assert manifest["createdAtUtc"] == "2026-10-05T10:00:00Z"
        assert manifest["levelCount"] == len(manifest["levels"]) == 1
        assert manifest["levels"][0]["id"] == "level-001"
        assert archive.read("levels/level-001/level.json") == level.level_data.payload
        assert archive.read("levels/level-001/supply-plan.json") == level.supply_plan.payload
        assert archive.read("levels/level-001/metadata.json") == level.metadata.payload
    assert result.evidence.level_ids == ("level-001",)
    assert len(result.evidence.levels[0].payloads) == 3
    assert result.evidence.levels[0].payloads[0].validation_reason == "VALID_PAYLOAD"


def test_builder_accepts_only_the_three_expected_contract_families() -> None:
    level = _level()
    descriptor = dict(level.level_data.descriptor)
    descriptor["content_type"] = "image"
    rejected = ScrubpackPayloadInput(descriptor, level.level_data.payload)
    invalid_level = ScrubpackLevelInput("level-001", rejected, level.supply_plan, level.metadata)
    with pytest.raises(ScrubpackBuildError, match="descriptor rejected"):
        _build((invalid_level,))


def test_builder_rejects_arbitrary_input_paths_and_payload_digest_mutation() -> None:
    level = _level()
    descriptor = dict(level.level_data.descriptor)
    descriptor["logical_path"] = "images/level-001.png"
    invalid_path = ScrubpackPayloadInput(descriptor, level.level_data.payload)
    with pytest.raises(ScrubpackBuildError, match="descriptor rejected"):
        _build((ScrubpackLevelInput("level-001", invalid_path, level.supply_plan, level.metadata),))

    tampered = ScrubpackPayloadInput(level.level_data.descriptor, level.level_data.payload + b" ")
    with pytest.raises(ScrubpackBuildError, match="DIGEST_MISMATCH"):
        _build((ScrubpackLevelInput("level-001", tampered, level.supply_plan, level.metadata),))


def test_builder_binds_all_three_descriptors_to_the_explicit_level_identity() -> None:
    level = _level()
    other = _payload("metadata", "level-002")
    with pytest.raises(ScrubpackBuildError, match="descriptor level identity mismatch"):
        _build((ScrubpackLevelInput("level-001", level.level_data, level.supply_plan, other),))


def test_builder_rejects_duplicate_and_implicit_level_inputs() -> None:
    with pytest.raises(ScrubpackBuildError, match="duplicate level ID"):
        _build((_level(), _level()))
    with pytest.raises(ScrubpackBuildError, match="at least one level"):
        _build(())
    with pytest.raises(ScrubpackBuildError, match="explicit sequence"):
        _build(iter((_level(),)))  # type: ignore[arg-type]


def test_pack_identity_and_explicit_utc_time_round_trip_in_exact_level_order() -> None:
    result = _build(
        (_level("level-z"), _level("level-a")),
        pack_id="release-pack-01",
        pack_version=7,
        created_at_utc="2026-10-05T13:00:00+03:00",
    )
    assert result.evidence.pack_id == "release-pack-01"
    assert result.evidence.pack_version == 7
    assert result.evidence.created_at_utc == "2026-10-05T10:00:00Z"
    assert result.evidence.level_count == 2
    assert result.evidence.level_ids == ("level-z", "level-a")
    with ZipFile(io.BytesIO(result.archive_bytes)) as archive:
        restored = json.loads(archive.read(PACK_MANIFEST_PATH))
    restored_model = ScrubpackManifestV1.from_dict(restored)
    assert restored_model == ScrubpackManifestV1.from_dict(restored_model.to_dict())
    assert restored["packId"] == "release-pack-01"
    assert restored["packVersion"] == 7
    assert restored["createdAtUtc"] == "2026-10-05T10:00:00Z"
    assert restored["levelCount"] == 2
    assert tuple(level["id"] for level in restored["levels"]) == ("level-z", "level-a")


@pytest.mark.parametrize("pack_id", ("", "../escape", "Uppercase", "has space", "x" * 65))
def test_malformed_pack_ids_fail_closed(pack_id: str) -> None:
    with pytest.raises(ScrubpackBuildError, match="invalid pack ID"):
        _build((_level(),), pack_id=pack_id)


@pytest.mark.parametrize("pack_version", (0, -1, True, 1.0))
def test_nonpositive_or_noninteger_pack_versions_fail_closed(pack_version: object) -> None:
    with pytest.raises(ScrubpackBuildError, match="positive integer"):
        _build((_level(),), pack_version=pack_version)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "created_at_utc",
    (
        "",
        "2026-10-05T10:00:00",
        "2026-02-30T10:00:00Z",
        "2026-10-05T10:00:00.500Z",
        "not-a-timestamp",
    ),
)
def test_invalid_or_ambiguous_timestamps_fail_closed(created_at_utc: str) -> None:
    with pytest.raises(ScrubpackBuildError, match="created_at_utc"):
        _build((_level(),), created_at_utc=created_at_utc)


def test_builder_has_no_hidden_wall_clock_dependency() -> None:
    source_path = CONTENT_PIPELINE / "src" / "scrubbots_content_pipeline" / "scrubpack_builder.py"
    source = source_path.read_text(encoding="utf-8")
    assert "datetime.now" not in source
    assert "utcnow" not in source
    with pytest.raises(TypeError):
        build_scrubpack((_level(),))  # type: ignore[call-arg]


def test_timezone_aware_datetime_is_normalized_and_naive_datetime_is_rejected() -> None:
    explicit = datetime(2026, 10, 5, 13, 0, tzinfo=timezone(timedelta(hours=3)))
    assert normalize_created_at_utc(explicit) == "2026-10-05T10:00:00Z"
    with pytest.raises(ScrubpackBuildError, match="created_at_utc"):
        _build((_level(),), created_at_utc=datetime(2026, 10, 5, 10, 0))  # type: ignore[arg-type]


def test_builder_can_read_only_the_explicit_local_file_and_does_not_discover_neighbors(tmp_path: Path) -> None:
    level = _level()
    explicit = tmp_path / "chosen-level.json"
    unrelated = tmp_path / "script.py"
    explicit.write_bytes(level.level_data.payload)
    unrelated.write_text("raise RuntimeError('must never be read')", encoding="utf-8")
    source = ScrubpackPayloadInput.from_path(level.level_data.descriptor, explicit)
    file_level = ScrubpackLevelInput("level-001", source, level.supply_plan, level.metadata)
    result = _build((file_level,))
    with ZipFile(io.BytesIO(result.archive_bytes)) as archive:
        assert tuple(archive.namelist()) == result.evidence.member_names
        assert all("script.py" not in name for name in archive.namelist())
        assert archive.read("levels/level-001/level.json") == explicit.read_bytes()


def test_build_result_and_evidence_are_immutable() -> None:
    result = _build((_level(),))
    with pytest.raises(FrozenInstanceError):
        result.evidence.version = 2  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.evidence.levels[0].level_id = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.evidence.level_ids[0] = "changed"  # type: ignore[index]
    assert isinstance(result.archive_bytes, bytes)


def test_builder_validation_is_m11_owned_and_has_no_remote_runtime_dependencies() -> None:
    source_path = CONTENT_PIPELINE / "src" / "scrubbots_content_pipeline" / "scrubpack_builder.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    forbidden_imports = {"httpx", "requests", "socket", "urllib", "aiohttp", "boto3", "scrubbots_pixel_factory", "godot"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".", 1)[0])
    assert not imported & forbidden_imports
    text = source_path.read_text(encoding="utf-8")
    assert "validate_remote_payload" in text
    assert "classify_content" in text
