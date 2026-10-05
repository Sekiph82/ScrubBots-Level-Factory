from __future__ import annotations

import ast
import hashlib
import io
import json
import sys
from dataclasses import FrozenInstanceError
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
from scrubbots_content_pipeline.scrubpack_spec import PACK_MANIFEST_PATH  # noqa: E402


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


def test_builder_packages_only_validated_payloads_at_fixed_paths() -> None:
    level = _level()
    result = build_scrubpack((level,))
    with ZipFile(io.BytesIO(result.archive_bytes)) as archive:
        assert tuple(archive.namelist()) == result.evidence.member_names
        manifest = json.loads(archive.read(PACK_MANIFEST_PATH))
        assert manifest["schema"] == "scrubbots.scrubpack.manifest.v1"
        assert manifest["version"] == 1
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
        build_scrubpack((invalid_level,))


def test_builder_rejects_arbitrary_input_paths_and_payload_digest_mutation() -> None:
    level = _level()
    descriptor = dict(level.level_data.descriptor)
    descriptor["logical_path"] = "images/level-001.png"
    invalid_path = ScrubpackPayloadInput(descriptor, level.level_data.payload)
    with pytest.raises(ScrubpackBuildError, match="descriptor rejected"):
        build_scrubpack((ScrubpackLevelInput("level-001", invalid_path, level.supply_plan, level.metadata),))

    tampered = ScrubpackPayloadInput(level.level_data.descriptor, level.level_data.payload + b" ")
    with pytest.raises(ScrubpackBuildError, match="DIGEST_MISMATCH"):
        build_scrubpack((ScrubpackLevelInput("level-001", tampered, level.supply_plan, level.metadata),))


def test_builder_binds_all_three_descriptors_to_the_explicit_level_identity() -> None:
    level = _level()
    other = _payload("metadata", "level-002")
    with pytest.raises(ScrubpackBuildError, match="descriptor level identity mismatch"):
        build_scrubpack((ScrubpackLevelInput("level-001", level.level_data, level.supply_plan, other),))


def test_builder_rejects_duplicate_and_implicit_level_inputs() -> None:
    with pytest.raises(ScrubpackBuildError, match="duplicate level ID"):
        build_scrubpack((_level(), _level()))
    with pytest.raises(ScrubpackBuildError, match="at least one level"):
        build_scrubpack(())
    with pytest.raises(ScrubpackBuildError, match="explicit sequence"):
        build_scrubpack(iter((_level(),)))  # type: ignore[arg-type]


def test_builder_can_read_only_the_explicit_local_file_and_does_not_discover_neighbors(tmp_path: Path) -> None:
    level = _level()
    explicit = tmp_path / "chosen-level.json"
    unrelated = tmp_path / "script.py"
    explicit.write_bytes(level.level_data.payload)
    unrelated.write_text("raise RuntimeError('must never be read')", encoding="utf-8")
    source = ScrubpackPayloadInput.from_path(level.level_data.descriptor, explicit)
    file_level = ScrubpackLevelInput("level-001", source, level.supply_plan, level.metadata)
    result = build_scrubpack((file_level,))
    with ZipFile(io.BytesIO(result.archive_bytes)) as archive:
        assert tuple(archive.namelist()) == result.evidence.member_names
        assert all("script.py" not in name for name in archive.namelist())
        assert archive.read("levels/level-001/level.json") == explicit.read_bytes()


def test_build_result_and_evidence_are_immutable() -> None:
    result = build_scrubpack((_level(),))
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
