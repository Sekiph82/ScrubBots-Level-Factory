from __future__ import annotations

import ast
import base64
import dataclasses
import hashlib
import io
import json
import os
import sys
import subprocess
import stat
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    ScrubpackBuildError,
    ScrubpackLevelInput,
    ScrubpackPayloadInput,
    build_scrubpack,
    verify_scrubpack_build,
    validate_scrubpack_levels,
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
        assert manifest["levels"][0]["sha256"] == {
            "levelData": hashlib.sha256(level.level_data.payload).hexdigest(),
            "supplyPlan": hashlib.sha256(level.supply_plan.payload).hexdigest(),
            "metadata": hashlib.sha256(level.metadata.payload).hexdigest(),
        }
        assert archive.read("levels/level-001/level.json") == level.level_data.payload
        assert archive.read("levels/level-001/supply-plan.json") == level.supply_plan.payload
        assert archive.read("levels/level-001/metadata.json") == level.metadata.payload
    assert result.evidence.level_ids == ("level-001",)
    assert len(result.evidence.levels[0].payloads) == 3
    assert result.evidence.levels[0].payloads[0].validation_reason == "VALID_PAYLOAD"
    assert result.evidence.archive_sha256 == hashlib.sha256(result.archive_bytes).hexdigest()
    assert result.evidence.archive_byte_length == len(result.archive_bytes)
    assert result.evidence.pack_id == "test-pack" and result.evidence.pack_version == 1
    assert result.evidence.validation_report.accepted
    assert all(level.accepted for level in result.evidence.validation_report.levels)
    assert verify_scrubpack_build(result.archive_bytes, result.evidence)


def test_builder_normalizes_all_zip_metadata_fields() -> None:
    result = _build((_level(),))
    with ZipFile(io.BytesIO(result.archive_bytes)) as archive:
        assert archive.comment == b""
        for info in archive.infolist():
            assert info.date_time == (1980, 1, 1, 0, 0, 0)
            assert info.compress_type == ZIP_STORED
            assert info.create_system == 3
            assert info.create_version == info.extract_version == 20
            assert info.flag_bits == 0
            assert info.volume == 0
            assert info.internal_attr == 0
            assert info.external_attr == ((stat.S_IFREG | 0o644) << 16)
            assert info.extra == b""
            assert info.comment == b""
            assert info.filename.isascii()


def test_identical_inputs_build_identical_bytes_across_processes_and_directories(tmp_path: Path) -> None:
    level = _level()

    def thaw(value):
        if hasattr(value, "items"):
            return {key: thaw(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [thaw(item) for item in value]
        return value

    specification = {
        "level_id": level.level_id,
        "payloads": {
            "level_data": {
                "descriptor": thaw(level.level_data.descriptor),
                "payload": base64.b64encode(level.level_data.payload).decode("ascii"),
            },
            "supply_plan": {
                "descriptor": thaw(level.supply_plan.descriptor),
                "payload": base64.b64encode(level.supply_plan.payload).decode("ascii"),
            },
            "metadata": {
                "descriptor": thaw(level.metadata.descriptor),
                "payload": base64.b64encode(level.metadata.payload).decode("ascii"),
            },
        },
    }
    source = """
import base64, hashlib, json, sys
from pathlib import Path
from scrubbots_content_pipeline import ScrubpackLevelInput, ScrubpackPayloadInput, build_scrubpack
spec = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
parts = {name: ScrubpackPayloadInput(value['descriptor'], base64.b64decode(value['payload']))
         for name, value in spec['payloads'].items()}
result = build_scrubpack((ScrubpackLevelInput(spec['level_id'], parts['level_data'], parts['supply_plan'], parts['metadata']),),
                         pack_id='test-pack', pack_version=1, created_at_utc='2026-10-05T10:00:00Z')
Path('result.scrubpack').write_bytes(result.archive_bytes)
print(hashlib.sha256(result.archive_bytes).hexdigest())
"""
    content_root = CONTENT_PIPELINE / "src"
    child_environment = os.environ.copy()
    child_environment["PYTHONPATH"] = str(content_root) + os.pathsep + child_environment.get("PYTHONPATH", "")
    archives = []
    reported_hashes = []
    for directory_name in ("build-a", "build-b"):
        build_directory = tmp_path / directory_name
        build_directory.mkdir()
        spec_path = build_directory / "inputs.json"
        spec_path.write_text(json.dumps(specification, sort_keys=True), encoding="utf-8")
        process = subprocess.run(
            [sys.executable, "-c", source, str(spec_path)],
            cwd=build_directory,
            env=child_environment,
            check=True,
            capture_output=True,
            text=True,
        )
        archives.append((build_directory / "result.scrubpack").read_bytes())
        reported_hashes.append(process.stdout.strip())

    assert archives[0] == archives[1]
    assert reported_hashes[0] == reported_hashes[1] == hashlib.sha256(archives[0]).hexdigest()


def test_build_receipt_detects_exact_archive_tampering_and_identity_mismatch() -> None:
    result = _build((_level(),))
    changed = result.archive_bytes[:-1] + bytes((result.archive_bytes[-1] ^ 1,))
    assert not verify_scrubpack_build(changed, result.evidence)
    assert not verify_scrubpack_build(result.archive_bytes + b"tampered", result.evidence)
    with ZipFile(io.BytesIO(result.archive_bytes)) as original:
        members = [(name, original.read(name)) for name in original.namelist()]
    rewritten = io.BytesIO()
    with ZipFile(rewritten, "w") as archive:
        for name, payload in members:
            if name == "levels/level-001/level.json":
                payload = payload.replace(b"Test Level", b"Best Level")
            archive.writestr(name, payload)
    rewritten_bytes = rewritten.getvalue()
    rewritten_receipt = dataclasses.replace(
        result.evidence,
        archive_sha256=hashlib.sha256(rewritten_bytes).hexdigest(),
        archive_byte_length=len(rewritten_bytes),
    )
    assert not verify_scrubpack_build(rewritten_bytes, rewritten_receipt)
    forged_identity = dataclasses.replace(result.evidence, pack_id="another-pack")
    assert not verify_scrubpack_build(result.archive_bytes, forged_identity)
    payloads = result.evidence.levels[0].payloads
    forged_payload_evidence = dataclasses.replace(
        result.evidence,
        levels=(
            dataclasses.replace(
                result.evidence.levels[0],
                payloads=(dataclasses.replace(payloads[0], payload_sha256="f" * 64), *payloads[1:]),
            ),
        ),
    )
    assert not verify_scrubpack_build(result.archive_bytes, forged_payload_evidence)


def test_manifest_member_digests_are_lowercase_sha256_and_immutable() -> None:
    result = _build((_level(),))
    with ZipFile(io.BytesIO(result.archive_bytes)) as archive:
        manifest = json.loads(archive.read(PACK_MANIFEST_PATH))
    manifest["levels"][0]["sha256"]["levelData"] = "A" * 64
    with pytest.raises(ValueError, match="SHA-256"):
        ScrubpackManifestV1.from_dict(manifest)
    manifest["levels"][0]["sha256"]["levelData"] = "a" * 64
    restored = ScrubpackManifestV1.from_dict(manifest)
    with pytest.raises(TypeError):
        restored.member_sha256["levels/level-001/level.json"] = "b" * 64  # type: ignore[index]


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
    invalid = ScrubpackLevelInput("level-001", level.level_data, level.supply_plan, other)
    with pytest.raises(ScrubpackBuildError, match="pre-pack validation failed") as caught:
        _build((invalid,))
    report = caught.value.validation_report
    assert report is not None and not report.accepted
    assert tuple(role.role for role in report.levels[0].roles) == ("level_data", "supply_plan", "metadata")
    assert tuple(role.reason_code for role in report.levels[0].roles) == (
        "VALIDATED", "VALIDATED", "LEVEL_IDENTITY_MISMATCH"
    )


def test_validation_transaction_checks_every_level_and_returns_safe_ordered_diagnostics() -> None:
    first = _level("level-a")
    second = _level("level-z")
    invalid_metadata = _payload("metadata", "foreign-level")
    invalid_first = ScrubpackLevelInput(
        "level-a", first.level_data, first.supply_plan, invalid_metadata
    )
    report = validate_scrubpack_levels((second, invalid_first))
    assert not report.accepted
    assert tuple(level.level_id for level in report.levels) == ("level-a", "level-z")
    assert report.levels[0].accepted is False
    assert report.levels[1].accepted is True
    assert all(len(level.roles) == 3 for level in report.levels)
    assert "owner-source.json" not in repr(report)
    with pytest.raises(ScrubpackBuildError) as caught:
        _build((second, invalid_first))
    assert caught.value.validation_report == report


def test_validation_report_is_complete_for_successful_triplets() -> None:
    report = validate_scrubpack_levels((_level(),))
    assert report.accepted
    assert report.levels[0].accepted
    assert tuple((item.role, item.reason_code) for item in report.levels[0].roles) == (
        ("level_data", "VALIDATED"),
        ("supply_plan", "VALIDATED"),
        ("metadata", "VALIDATED"),
    )


def test_builder_rejects_duplicate_and_implicit_level_inputs() -> None:
    with pytest.raises(ScrubpackBuildError, match="duplicate level ID"):
        _build((_level(), _level()))
    with pytest.raises(ScrubpackBuildError, match="at least one level"):
        _build(())
    with pytest.raises(ScrubpackBuildError, match="explicit sequence"):
        _build(iter((_level(),)))  # type: ignore[arg-type]


def test_builder_rejects_case_normalized_duplicate_ownership_before_output() -> None:
    with pytest.raises(ScrubpackBuildError, match="case-normalized"):
        _build((_level("Level-A"), _level("level-a")))


def test_pack_identity_and_explicit_utc_time_round_trip_in_canonical_level_order() -> None:
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
    assert result.evidence.level_ids == ("level-a", "level-z")
    with ZipFile(io.BytesIO(result.archive_bytes)) as archive:
        restored = json.loads(archive.read(PACK_MANIFEST_PATH))
    restored_model = ScrubpackManifestV1.from_dict(restored)
    assert restored_model == ScrubpackManifestV1.from_dict(restored_model.to_dict())
    assert restored["packId"] == "release-pack-01"
    assert restored["packVersion"] == 7
    assert restored["createdAtUtc"] == "2026-10-05T10:00:00Z"
    assert restored["levelCount"] == 2
    assert tuple(level["id"] for level in restored["levels"]) == ("level-a", "level-z")


def test_logical_pack_members_are_independent_of_level_input_order() -> None:
    levels = (_level("m-level"), _level("a-level"), _level("Z-level"))
    forward = _build(levels)
    reverse = _build(tuple(reversed(levels)))
    assert forward.evidence.level_ids == reverse.evidence.level_ids == ("Z-level", "a-level", "m-level")
    assert forward.evidence.member_names == reverse.evidence.member_names
    assert forward.evidence.member_names == (
        "pack.json",
        "levels/Z-level/level.json", "levels/Z-level/supply-plan.json", "levels/Z-level/metadata.json",
        "levels/a-level/level.json", "levels/a-level/supply-plan.json", "levels/a-level/metadata.json",
        "levels/m-level/level.json", "levels/m-level/supply-plan.json", "levels/m-level/metadata.json",
    )
    with ZipFile(io.BytesIO(forward.archive_bytes)) as first, ZipFile(io.BytesIO(reverse.archive_bytes)) as second:
        assert first.namelist() == second.namelist()
        assert {name: first.read(name) for name in first.namelist()} == {
            name: second.read(name) for name in second.namelist()
        }


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
    with pytest.raises(FrozenInstanceError):
        result.evidence.archive_sha256 = "0" * 64  # type: ignore[misc]
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
