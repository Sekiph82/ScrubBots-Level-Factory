from __future__ import annotations

import hashlib
import io
import json
import stat
import sys
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    ScrubpackLevelInput,
    ScrubpackPayloadInput,
    build_scrubpack,
    extract_scrubpack,
    inspect_scrubpack,
)
from scrubbots_content_pipeline.cli import main  # noqa: E402
from scrubbots_content_pipeline.scrubpack_spec import (  # noqa: E402
    PACK_MANIFEST_PATH,
    SUPPORTED_SCRUBPACK_VERSIONS,
)


EXAMPLES = CONTENT_PIPELINE / "schemas" / "v1" / "examples"


def _json_bytes(value: dict[str, object]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _source(role: str, level_id: str = "inspect-level") -> ScrubpackPayloadInput:
    if role == "level_data":
        value: dict[str, object] = {
            "version": 1,
            "id": level_id,
            "name": "Inspect Level",
            "difficulty": "EASY",
            "width": 20,
            "height": 20,
            "palette": ["C01"],
            "cells": [0] * 400,
        }
        filename, digest_field = "level.json", "payload_sha256"
    elif role == "supply_plan":
        value = {
            "schema": "scrubbots.level_supply_plan.v1",
            "version": 1,
            "levelId": level_id,
            "ownerInput": "owner-source.json",
            "ownerInputSha256": "a" * 64,
            "columnCount": 3,
            "visiblePreviewDepth": 3,
            "maxRobotsPerBatch": 2,
            "intendedColumnClicks": [],
            "columns": [[{"batchId": f"{level_id}-{index}", "cid": "C01", "robots": 1}] for index in range(3)],
        }
        filename, digest_field = "supply-plan.json", "supply_plan_sha256"
    else:
        value = {
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
        filename, digest_field = "approved-metadata.json", "payload_sha256"
    raw = _json_bytes(value)
    descriptor = json.loads((EXAMPLES / filename).read_text(encoding="utf-8"))
    descriptor["attributes"]["level_id"] = level_id
    descriptor["attributes"][digest_field] = hashlib.sha256(raw).hexdigest()
    return ScrubpackPayloadInput(descriptor, raw)


def _pack_bytes(level_id: str = "inspect-level") -> bytes:
    level = ScrubpackLevelInput(
        level_id,
        _source("level_data", level_id),
        _source("supply_plan", level_id),
        _source("metadata", level_id),
    )
    return build_scrubpack(
        (level,),
        pack_id="inspect-pack",
        pack_version=2,
        created_at_utc="2026-10-05T10:00:00Z",
    ).archive_bytes


def _rewrite(raw: bytes, mutate) -> bytes:
    output = io.BytesIO()
    with ZipFile(io.BytesIO(raw)) as source, ZipFile(output, "w", compression=ZIP_STORED) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            item = mutate(info, data)
            if item is None:
                continue
            new_info, new_data = item
            target.writestr(new_info, new_data)
    return output.getvalue()


def test_inspection_returns_human_and_machine_results_without_writing(tmp_path: Path) -> None:
    archive_path = tmp_path / "valid.scrubpack"
    archive_path.write_bytes(_pack_bytes())
    before = archive_path.read_bytes()
    report = inspect_scrubpack(archive_path)
    assert report.accepted and report.reason_code == "VALID"
    assert report.pack_id == "inspect-pack" and report.pack_version == 2
    assert report.level_ids == ("inspect-level",)
    assert report.archive_sha256 == hashlib.sha256(before).hexdigest()
    assert "valid" in report.render_human().lower()
    machine = report.to_dict()
    assert machine["accepted"] is True and machine["level_count"] == 1
    assert machine["member_names"] == [
        "pack.json",
        "levels/inspect-level/level.json",
        "levels/inspect-level/supply-plan.json",
        "levels/inspect-level/metadata.json",
    ]
    assert archive_path.read_bytes() == before
    assert tuple(tmp_path.iterdir()) == (archive_path,)


def test_inspection_rejects_corrupt_zip_wrong_layout_manifest_and_digest(tmp_path: Path) -> None:
    archive_path = tmp_path / "input.scrubpack"
    archive_path.write_bytes(b"not a zip")
    assert inspect_scrubpack(archive_path).reason_code == "INVALID_ZIP"

    valid = _pack_bytes()
    def add_unsafe_path(info, data):
        if info.filename == "pack.json":
            return ZipInfo("../escape.json"), data
        return info, data

    archive_path.write_bytes(_rewrite(valid, add_unsafe_path))
    assert inspect_scrubpack(archive_path).reason_code == "INVALID_MEMBER_LAYOUT"
    unsafe_destination = tmp_path / "unsafe-extract"
    assert extract_scrubpack(archive_path, unsafe_destination).reason_code == "INVALID_MEMBER_LAYOUT"
    assert not unsafe_destination.exists()

    def mutate_manifest(info, data):
        if info.filename == "pack.json":
            manifest = json.loads(data)
            manifest["version"] = 2
            return info, _json_bytes(manifest)
        return info, data

    archive_path.write_bytes(_rewrite(valid, mutate_manifest))
    assert inspect_scrubpack(archive_path).reason_code == "UNSUPPORTED_VERSION"

    def tamper_payload(info, data):
        if info.filename.endswith("/level.json"):
            data = data.replace(b"Inspect Level", b"Tamper Level")
        return info, data

    archive_path.write_bytes(_rewrite(valid, tamper_payload))
    assert inspect_scrubpack(archive_path).reason_code == "MEMBER_DIGEST_MISMATCH"


@pytest.mark.parametrize(
    ("field", "value", "remove", "expected"),
    (
        ("version", None, True, "INVALID_MANIFEST"),
        ("schema", None, True, "INVALID_MANIFEST"),
        ("version", True, False, "INVALID_MANIFEST"),
        ("version", "1", False, "INVALID_MANIFEST"),
        ("version", 0, False, "INVALID_MANIFEST"),
        ("version", -1, False, "INVALID_MANIFEST"),
        ("version", 2, False, "UNSUPPORTED_VERSION"),
        ("schema", "scrubbots.scrubpack.manifest.v2", False, "UNSUPPORTED_VERSION"),
    ),
)
def test_inspection_and_extraction_reject_malformed_or_unsupported_manifest_version(
    tmp_path: Path, field: str, value: object, remove: bool, expected: str
) -> None:
    archive_path = tmp_path / "versioned.scrubpack"
    destination = tmp_path / "extract-versioned"
    raw = _pack_bytes()

    def alter_manifest(info, data):
        if info.filename == PACK_MANIFEST_PATH:
            manifest = json.loads(data)
            if remove:
                manifest.pop(field)
            else:
                manifest[field] = value
            return info, _json_bytes(manifest)
        return info, data

    archive_path.write_bytes(_rewrite(raw, alter_manifest))
    source_before = archive_path.read_bytes()
    inspected = inspect_scrubpack(archive_path)
    assert inspected.reason_code == expected
    extracted = extract_scrubpack(archive_path, destination)
    assert extracted.reason_code == expected
    assert archive_path.read_bytes() == source_before
    assert not destination.exists()


@pytest.mark.parametrize(
    ("member_name", "field", "value", "expected"),
    (
        ("levels/inspect-level/level.json", "version", 2, "UNSUPPORTED_VERSION"),
        (
            "levels/inspect-level/supply-plan.json",
            "schema",
            "scrubbots.level_supply_plan.v2",
            "UNSUPPORTED_VERSION",
        ),
        ("levels/inspect-level/metadata.json", "version", True, "INVALID_MEMBER_VERSION"),
    ),
)
def test_inspection_rejects_mixed_or_malformed_member_contract_versions(
    tmp_path: Path, member_name: str, field: str, value: object, expected: str
) -> None:
    raw = _pack_bytes()
    with ZipFile(io.BytesIO(raw)) as source:
        entries = {info.filename: (info, source.read(info.filename)) for info in source.infolist()}
    member_info, member_bytes = entries[member_name]
    member_value = json.loads(member_bytes)
    member_value[field] = value
    member_bytes = _json_bytes(member_value)
    entries[member_name] = (member_info, member_bytes)
    manifest_info, manifest_bytes = entries[PACK_MANIFEST_PATH]
    manifest = json.loads(manifest_bytes)
    role = {
        "levels/inspect-level/level.json": "levelData",
        "levels/inspect-level/supply-plan.json": "supplyPlan",
        "levels/inspect-level/metadata.json": "metadata",
    }[member_name]
    manifest["levels"][0]["sha256"][role] = hashlib.sha256(member_bytes).hexdigest()
    entries[PACK_MANIFEST_PATH] = (manifest_info, _json_bytes(manifest))
    rewritten = io.BytesIO()
    with ZipFile(rewritten, "w", compression=ZIP_STORED) as target:
        for info, data in entries.values():
            target.writestr(info, data)

    archive_path = tmp_path / "mixed-versions.scrubpack"
    destination = tmp_path / "must-not-extract"
    archive_path.write_bytes(rewritten.getvalue())
    source_before = archive_path.read_bytes()
    inspected = inspect_scrubpack(archive_path)
    assert inspected.reason_code == expected
    extracted = extract_scrubpack(archive_path, destination)
    assert extracted.reason_code == expected
    assert archive_path.read_bytes() == source_before
    assert not destination.exists()


def test_supported_scrubpack_version_set_is_explicitly_v1_only() -> None:
    assert SUPPORTED_SCRUBPACK_VERSIONS == frozenset({1})


def test_inspection_rejects_duplicate_paths_and_symlinks(tmp_path: Path) -> None:
    valid = _pack_bytes()
    output = io.BytesIO()
    with ZipFile(io.BytesIO(valid)) as source, ZipFile(output, "w", compression=ZIP_STORED) as target:
        for info in source.infolist():
            target.writestr(info, source.read(info.filename))
        with pytest.warns(UserWarning, match="Duplicate name"):
            target.writestr("levels/inspect-level/level.json", b"{}")
    duplicate_path = tmp_path / "duplicate.scrubpack"
    duplicate_path.write_bytes(output.getvalue())
    assert inspect_scrubpack(duplicate_path).reason_code == "INVALID_MEMBER_LAYOUT"

    def symlink_member(info, data):
        if info.filename.endswith("/level.json"):
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
        return info, data

    symlink_path = tmp_path / "symlink.scrubpack"
    symlink_path.write_bytes(_rewrite(valid, symlink_member))
    assert inspect_scrubpack(symlink_path).reason_code == "UNSUPPORTED_ZIP_METADATA"


def test_safe_extraction_uses_new_destination_and_never_overwrites(tmp_path: Path) -> None:
    archive_path = tmp_path / "valid.scrubpack"
    archive_path.write_bytes(_pack_bytes())
    destination = tmp_path / "extracted"
    report = extract_scrubpack(archive_path, destination)
    assert report.accepted and report.extracted
    assert (destination / "pack.json").is_file()
    assert (destination / "levels/inspect-level/level.json").is_file()
    assert (destination / "levels/inspect-level/supply-plan.json").is_file()
    assert (destination / "levels/inspect-level/metadata.json").is_file()
    sentinel = tmp_path / "existing"
    sentinel.mkdir()
    (sentinel / "keep.txt").write_text("untouched", encoding="utf-8")
    rejected = extract_scrubpack(archive_path, sentinel)
    assert not rejected.accepted and rejected.reason_code == "DESTINATION_EXISTS"
    assert (sentinel / "keep.txt").read_text(encoding="utf-8") == "untouched"


def test_cli_provides_human_and_machine_inspection(tmp_path: Path, monkeypatch, capsys) -> None:
    archive_path = tmp_path / "valid.scrubpack"
    archive_path.write_bytes(_pack_bytes())
    monkeypatch.setattr(sys, "argv", ["scrubbots-content-pipeline", "--inspect-pack", str(archive_path)])
    assert main() == 0
    assert "Scrubpack is valid" in capsys.readouterr().out
    monkeypatch.setattr(
        sys,
        "argv",
        ["scrubbots-content-pipeline", "--inspect-pack", str(archive_path), "--output-format", "json"],
    )
    assert main() == 0
    result = json.loads(capsys.readouterr().out)
    assert result["accepted"] is True and result["pack_id"] == "inspect-pack"
