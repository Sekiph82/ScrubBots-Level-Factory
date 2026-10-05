from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
import sys

sys.path.insert(0, str(CONTENT_PIPELINE / "src"))

from scrubbots_content_pipeline.scrubpack_spec import (  # noqa: E402
    PACK_MANIFEST_PATH,
    SCRUBPACK_EXTENSION,
    SCRUBPACK_MEDIA_TYPE,
    SCRUBPACK_SCHEMA,
    SCRUBPACK_VERSION,
    ScrubpackLevelV1,
    ScrubpackManifestV1,
    ScrubpackSpecError,
    expected_member_names,
    validate_member_name,
    validate_member_names,
)


def test_versioned_manifest_model_and_fixed_paths_are_explicit() -> None:
    level = ScrubpackLevelV1("level-001")
    manifest = ScrubpackManifestV1(
        (level,), pack_id="pack-001", pack_version=1, created_at_utc="2026-10-05T10:00:00Z"
    )
    assert SCRUBPACK_EXTENSION == ".scrubpack"
    assert (manifest.schema, manifest.version, manifest.media_type) == (
        SCRUBPACK_SCHEMA,
        SCRUBPACK_VERSION,
        SCRUBPACK_MEDIA_TYPE,
    )
    assert manifest.to_dict() == {
        "schema": "scrubbots.scrubpack.manifest.v1",
        "version": 1,
        "mediaType": "application/vnd.scrubbots.scrubpack+zip",
        "packId": "pack-001",
        "packVersion": 1,
        "createdAtUtc": "2026-10-05T10:00:00Z",
        "levelCount": 1,
        "levels": [
            {
                "id": "level-001",
                "files": {
                    "levelData": "levels/level-001/level.json",
                    "supplyPlan": "levels/level-001/supply-plan.json",
                    "metadata": "levels/level-001/metadata.json",
                },
            }
        ],
    }
    assert PACK_MANIFEST_PATH == "pack.json"
    assert expected_member_names((level,)) == (
        "pack.json",
        "levels/level-001/level.json",
        "levels/level-001/supply-plan.json",
        "levels/level-001/metadata.json",
    )
    assert ScrubpackManifestV1.from_dict(manifest.to_dict()) == manifest


def test_manifest_round_trip_rejects_count_and_path_identity_mismatches() -> None:
    manifest = ScrubpackManifestV1(
        (ScrubpackLevelV1("level-001"),),
        pack_id="pack-001",
        pack_version=1,
        created_at_utc="2026-10-05T10:00:00Z",
    ).to_dict()
    manifest["levelCount"] = 2
    with pytest.raises(ScrubpackSpecError, match="level count mismatch"):
        ScrubpackManifestV1.from_dict(manifest)
    manifest["levelCount"] = 1
    manifest["levels"][0]["files"]["levelData"] = "levels/other/level.json"
    with pytest.raises(ScrubpackSpecError, match="paths do not match"):
        ScrubpackManifestV1.from_dict(manifest)


@pytest.mark.parametrize(
    "name",
    (
        "pack.json",
        "levels/level-001/level.json",
        "levels/level-001/supply-plan.json",
        "levels/level-001/metadata.json",
    ),
)
def test_fixed_relative_json_members_are_accepted(name: str) -> None:
    assert validate_member_name(name)


@pytest.mark.parametrize(
    "name",
    (
        "",
        "/pack.json",
        "C:/pack.json",
        "levels\\level-001\\level.json",
        "levels//level-001/level.json",
        "levels/../pack.json",
        "levels/./level-001/level.json",
        "levels/level-001/../../pack.json",
        "levels/level-001/run.py",
        "scripts/start.gd",
        "levels/level-001/scene.tscn",
        "levels/level-001/custom.json",
        "levels/-bad/level.json",
        "pack.json/",
    ),
)
def test_noncanonical_traversal_and_non_data_member_paths_fail_closed(name: str) -> None:
    assert not validate_member_name(name)


def test_duplicate_archive_names_and_duplicate_level_ids_fail_closed() -> None:
    name = "levels/level-001/level.json"
    assert not validate_member_names((PACK_MANIFEST_PATH, name, name))
    with pytest.raises(ScrubpackSpecError, match="duplicate level ID"):
        ScrubpackManifestV1(
            (ScrubpackLevelV1("level-001"), ScrubpackLevelV1("level-001")),
            pack_id="pack-001",
            pack_version=1,
            created_at_utc="2026-10-05T10:00:00Z",
        )


@pytest.mark.parametrize("level_id", ("../escape", "a/b", "", "x" * 65, "has space"))
def test_level_id_cannot_escape_or_change_the_path_grammar(level_id: str) -> None:
    with pytest.raises(ScrubpackSpecError, match="invalid level ID"):
        ScrubpackLevelV1(level_id)


def test_manifest_schema_is_closed_and_binds_v1_media_identity() -> None:
    schema_path = CONTENT_PIPELINE / "schemas" / "v1" / "scrubpack-manifest.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["properties"]["schema"]["const"] == SCRUBPACK_SCHEMA
    assert schema["properties"]["version"]["const"] == SCRUBPACK_VERSION
    assert schema["properties"]["mediaType"]["const"] == SCRUBPACK_MEDIA_TYPE
    assert schema["properties"]["packVersion"]["minimum"] == 1
    assert schema["properties"]["levelCount"]["minimum"] == 1
    assert schema["required"] == [
        "schema", "version", "mediaType", "packId", "packVersion", "createdAtUtc", "levelCount", "levels"
    ]
    assert set(schema["properties"]["levels"]["items"]["properties"]["files"]["properties"]) == {
        "levelData",
        "supplyPlan",
        "metadata",
    }
    file_properties = schema["properties"]["levels"]["items"]["properties"]["files"]["properties"]
    for field, filename in (
        ("levelData", "level.json"),
        ("supplyPlan", "supply-plan.json"),
        ("metadata", "metadata.json"),
    ):
        assert re.fullmatch(file_properties[field]["pattern"], f"levels/level-001/{filename}")
        assert not re.fullmatch(file_properties[field]["pattern"], f"levels/../level-001/{filename}")


def test_spec_explicitly_forbids_executable_capable_archive_types() -> None:
    specification = (ROOT / "docs" / "content_platform" / "SCRUBPACK_V1_SPEC.md").read_text(encoding="utf-8")
    for term in ("symlinks", "executable permissions", "scripts", "native binaries", "never execute"):
        assert term in specification


def test_spec_contract_adds_no_archive_execution_or_network_imports() -> None:
    source = (CONTENT_PIPELINE / "src" / "scrubbots_content_pipeline" / "scrubpack_spec.py").read_text(
        encoding="utf-8"
    )
    for forbidden in ("zipfile", "httpx", "requests", "urllib", "socket", "subprocess", "eval(", "exec("):
        assert forbidden not in source
