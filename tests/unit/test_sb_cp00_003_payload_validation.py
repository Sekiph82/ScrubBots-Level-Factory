from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
PACKAGE = PIPELINE / "src" / "scrubbots_content_pipeline"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    ContentDisposition,
    PayloadReasonCode,
    classify_content,
    serialize_payload_result,
    validate_remote_payload,
)
from scrubbots_content_pipeline.payload_validation import (  # noqa: E402
    MAX_NESTING_DEPTH,
    MAX_PAYLOAD_BYTES,
    MAX_STRING_CHARACTERS,
)


def _descriptor(kind: str, payload: dict[str, object], *, raw: bytes | None = None) -> dict[str, object]:
    examples = PIPELINE / "schemas" / "v1" / "examples"
    name = {"level_data": "level.json", "supply_plan_data": "supply-plan.json", "approved_metadata": "approved-metadata.json"}[kind]
    descriptor = json.loads((examples / name).read_text(encoding="utf-8"))
    attrs = descriptor["attributes"]
    assert isinstance(attrs, dict)
    if kind == "supply_plan_data":
        attrs["level_id"] = payload.setdefault("levelId", attrs["level_id"])
        attrs["columns"] = payload.setdefault("columnCount", attrs["columns"])
        attrs["preview_depth"] = payload.setdefault("visiblePreviewDepth", attrs["preview_depth"])
        digest_key = "supply_plan_sha256"
    else:
        attrs["level_id"] = payload.setdefault("id", attrs["level_id"])
        if kind == "level_data":
            attrs["width"] = payload.setdefault("width", attrs["width"])
            attrs["height"] = payload.setdefault("height", attrs["height"])
        else:
            attrs["width"] = payload.setdefault("width", attrs["width"])
            attrs["height"] = payload.setdefault("height", attrs["height"])
            attrs["columns"] = payload.setdefault("columnCount", attrs["columns"])
            attrs["preview_depth"] = payload.setdefault("visiblePreviewDepth", attrs["preview_depth"])
        digest_key = "payload_sha256"
    raw = raw if raw is not None else json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    attrs[digest_key] = hashlib.sha256(raw).hexdigest()
    return descriptor


def _payloads() -> dict[str, dict[str, object]]:
    return {
        "level_data": {
            "version": 1, "id": "level-001", "name": "Level 001", "difficulty": "EASY",
            "width": 20, "height": 20, "palette": ["#000000FF", "#FFFFFFFF"], "cells": [0] * 399 + [1],
        },
        "supply_plan_data": {
            "schema": "scrubbots.level_supply_plan.v1", "version": 1,
            "ownerInput": "PixelArtStudio supply pipeline (solver-proven)", "ownerInputSha256": "a" * 64,
            "maxRobotsPerBatch": 2, "intendedColumnClicks": [0, 1, 2],
            "columns": [[{"batchId": f"level-001-K{i + 1}-01", "cid": "C01", "robots": 2}] for i in range(3)],
        },
        "approved_metadata": {
            "schema": "scrubbots.level.metadata.v1", "version": 1, "builderVersion": "LevelFactory-ZIP-V02-R01/v1",
            "width": 20, "height": 20, "cellCount": 400, "difficulty": "EASY", "challengeScore": 12.5,
            "columnCount": 3, "visiblePreviewDepth": 3, "fileDigests": {"level": "a" * 64},
        },
    }


@pytest.mark.parametrize("kind", ("level_data", "supply_plan_data", "approved_metadata"))
def test_current_declarative_payload_families_validate_and_bind_exact_bytes(kind: str) -> None:
    payload = _payloads()[kind]
    descriptor = _descriptor(kind, payload)
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    descriptor = _descriptor(kind, payload, raw=raw)
    assert classify_content(descriptor).disposition is ContentDisposition.REMOTE_DECLARATIVE
    result = validate_remote_payload(descriptor, raw)
    assert result.accepted
    assert result.reason_code is PayloadReasonCode.VALID_PAYLOAD
    assert json.loads(serialize_payload_result(result)) == {
        "validation_version": "1.0", "accepted": True, "reason_code": "VALID_PAYLOAD",
    }


def test_pinned_current_scrubbots_production_payload_bytes_validate_with_truthful_descriptors() -> None:
    fixtures = ROOT / "tests" / "fixtures" / "sb_cp00_003_r01"
    provenance = json.loads((fixtures / "authority.json").read_text(encoding="utf-8"))
    assert provenance["authority_repository"] == "Sekiph82/Scrubbots"
    assert provenance["authority_commit"] == "31f8e8f03807cacb00bd7ea0d91a2b727b784f35"
    expected_sources = {
        "level_002_apple.json": (
            "data/levels/level_002_apple.json",
            "f0cf2a00898582979e9078a00ce2d0935030bc67ba7d7295360cea40ca889486",
        ),
        "level_002_apple_supply_v1.json": (
            "data/levels/supply/level_002_apple_supply_v1.json",
            "d7207fbc766f9da28b37c4ecab319720fa4b882af79cea5f19961b60abfcb2ec",
        ),
    }

    for kind, filename, digest_key in (
        ("level_data", "level_002_apple.json", "payload_sha256"),
        ("supply_plan_data", "level_002_apple_supply_v1.json", "supply_plan_sha256"),
    ):
        raw = (fixtures / filename).read_bytes()
        record = provenance["fixtures"][filename]
        assert record["source_path"] == expected_sources[filename][0]
        assert record["sha256"] == expected_sources[filename][1] == hashlib.sha256(raw).hexdigest()
        assert record["size_bytes"] == len(raw)
        parsed = json.loads(raw)
        descriptor = _descriptor(kind, parsed, raw=raw)
        attrs = descriptor["attributes"]
        assert attrs[digest_key] == hashlib.sha256(raw).hexdigest()
        result = validate_remote_payload(descriptor, raw)
        assert result.accepted, (filename, result.reason_code)

    level = json.loads((fixtures / "level_002_apple.json").read_bytes())
    supply = json.loads((fixtures / "level_002_apple_supply_v1.json").read_bytes())
    assert level["width"] == level["height"] == 32
    assert len(level["cells"]) == 32 * 32
    assert all(type(cell) is int for cell in level["cells"])
    assert supply["intendedColumnClicks"][:3] == [1, 2, 3]


@pytest.mark.parametrize(
    ("raw", "reason"),
    (
        (b"{", PayloadReasonCode.MALFORMED_JSON),
        (b'{"id":"a","id":"b"}', PayloadReasonCode.DUPLICATE_KEY),
        (b'{"value":NaN}', PayloadReasonCode.NON_FINITE_NUMBER),
        (b'{"value":Infinity}', PayloadReasonCode.NON_FINITE_NUMBER),
        (b"\xff", PayloadReasonCode.INVALID_UTF8),
        (b"[]", PayloadReasonCode.WRONG_TOP_LEVEL_TYPE),
    ),
)
def test_strict_json_failures_are_deterministic(raw: bytes, reason: PayloadReasonCode) -> None:
    payload = _payloads()["level_data"]
    descriptor = _descriptor("level_data", payload)
    result = validate_remote_payload(descriptor, raw)
    assert not result.accepted
    assert result.reason_code is reason


def test_rejects_invalid_descriptor_and_parsed_data_without_digest_provenance() -> None:
    result = validate_remote_payload({"logical_path": "code.gd"}, b"{}")
    assert result.reason_code is PayloadReasonCode.INVALID_DESCRIPTOR
    payload = _payloads()["level_data"]
    descriptor = _descriptor("level_data", payload)
    assert validate_remote_payload(descriptor, payload).reason_code is PayloadReasonCode.DIGEST_MISMATCH


@pytest.mark.parametrize(
    "field",
    ("script", "scriptPath", "expression", "plugin", "addon", "nativeCode", "modulePath", "resource", "command", "networkOperation"),
)
def test_executable_behavior_fields_are_rejected(field: str) -> None:
    payload = _payloads()["level_data"]
    payload[field] = "res://unsafe.gd"
    raw = json.dumps(payload, separators=(",", ":")).encode()
    descriptor = _descriptor("level_data", payload, raw=raw)
    result = validate_remote_payload(descriptor, raw)
    assert result.reason_code is PayloadReasonCode.EXECUTABLE_CONTENT


@pytest.mark.parametrize("marker", ("eval('x')", "res://scripts/a.gd", "user://thing.tscn", "${command}", "{{ execute }}"))
def test_executable_references_in_values_are_rejected(marker: str) -> None:
    payload = _payloads()["level_data"]
    payload["name"] = marker
    raw = json.dumps(payload, separators=(",", ":")).encode()
    descriptor = _descriptor("level_data", payload, raw=raw)
    assert validate_remote_payload(descriptor, raw).reason_code is PayloadReasonCode.EXECUTABLE_CONTENT


def test_unknown_fields_schema_and_descriptor_projections_fail_closed() -> None:
    payload = _payloads()["level_data"]
    payload["futureBehavior"] = "enabled"
    raw = json.dumps(payload, separators=(",", ":")).encode()
    descriptor = _descriptor("level_data", payload, raw=raw)
    assert validate_remote_payload(descriptor, raw).reason_code is PayloadReasonCode.UNKNOWN_PAYLOAD_FIELD

    for field, value in (("id", "different"), ("width", 21), ("version", 2)):
        candidate = _payloads()["level_data"]
        candidate[field] = value
        candidate_raw = json.dumps(candidate, separators=(",", ":")).encode()
        candidate_descriptor = _descriptor("level_data", candidate, raw=candidate_raw)
        candidate_descriptor["attributes"].update(level_id="level-001", width=20, height=20)
        outcome = validate_remote_payload(candidate_descriptor, candidate_raw)
        assert not outcome.accepted
        assert outcome.reason_code in {PayloadReasonCode.CONTRACT_MISMATCH, PayloadReasonCode.DESCRIPTOR_MISMATCH, PayloadReasonCode.INVALID_PAYLOAD}


@pytest.mark.parametrize("cell", (True, -1, 2, "C01"))
def test_level_data_cells_are_integer_palette_indices_and_reject_bool(cell: object) -> None:
    payload = _payloads()["level_data"]
    assert isinstance(payload["cells"], list)
    payload["cells"][0] = cell
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    descriptor = _descriptor("level_data", payload, raw=raw)
    result = validate_remote_payload(descriptor, raw)
    assert not result.accepted
    assert result.reason_code is PayloadReasonCode.INVALID_PAYLOAD


@pytest.mark.parametrize("width,height", ((20, 59), (59, 20), (19, 20), (20, 19), (60, 20), (20, 60)))
def test_level_data_dimensions_use_independent_locked_production_bounds(width: int, height: int) -> None:
    payload = _payloads()["level_data"]
    payload["width"], payload["height"] = width, height
    payload["cells"] = [0] * (width * height)
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    descriptor = _descriptor("level_data", payload, raw=raw)
    result = validate_remote_payload(descriptor, raw)
    if 20 <= width <= 59 and 20 <= height <= 59:
        assert result.accepted
    else:
        assert result.reason_code is PayloadReasonCode.INVALID_PAYLOAD


@pytest.mark.parametrize(
    ("mutate",),
    (
        (lambda plan: plan["columns"][0][0].update(robots=3),),
        (lambda plan: plan["columns"][1][0].update(batchId=plan["columns"][0][0]["batchId"]),),
        (lambda plan: plan["columns"][0][0].update(cid="C17"),),
        (lambda plan: plan["columns"][0][0].update(extra="ignored"),),
        (lambda plan: plan["columns"][0][0].update(robots=True),),
    ),
)
def test_supply_plan_enforces_current_structural_authority(mutate: object) -> None:
    payload = _payloads()["supply_plan_data"]
    assert callable(mutate)
    _descriptor("supply_plan_data", payload)
    mutate(payload)
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    descriptor = _descriptor("supply_plan_data", payload, raw=raw)
    result = validate_remote_payload(descriptor, raw)
    assert result.reason_code is PayloadReasonCode.INVALID_PAYLOAD


def test_intended_column_clicks_are_validated_as_inert_integer_structure_without_index_rules() -> None:
    payload = _payloads()["supply_plan_data"]
    _descriptor("supply_plan_data", payload)
    payload["intendedColumnClicks"] = [1, 2, 3]
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    descriptor = _descriptor("supply_plan_data", payload, raw=raw)
    assert validate_remote_payload(descriptor, raw).accepted


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("maxRobotsPerBatch", 0),
        ("maxRobotsPerBatch", True),
        ("intendedColumnClicks", [True]),
        ("intendedColumnClicks", "1,2,3"),
    ),
)
def test_supply_plan_integer_bounds_exclude_nonpositive_and_bool_values(field: str, value: object) -> None:
    payload = _payloads()["supply_plan_data"]
    _descriptor("supply_plan_data", payload)
    payload[field] = value
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    descriptor = _descriptor("supply_plan_data", payload, raw=raw)
    assert validate_remote_payload(descriptor, raw).reason_code is PayloadReasonCode.INVALID_PAYLOAD


def test_digest_mismatch_and_payload_size_limit_fail_closed() -> None:
    payload = _payloads()["level_data"]
    raw = json.dumps(payload, separators=(",", ":")).encode()
    descriptor = _descriptor("level_data", payload, raw=raw)
    assert validate_remote_payload(descriptor, raw + b" ").reason_code is PayloadReasonCode.DIGEST_MISMATCH
    assert validate_remote_payload(descriptor, b" " * (MAX_PAYLOAD_BYTES + 1)).reason_code is PayloadReasonCode.PAYLOAD_TOO_LARGE


def test_nesting_collection_and_string_limits_are_enforced() -> None:
    payload = _payloads()["level_data"]
    payload["name"] = "x" * (MAX_STRING_CHARACTERS + 1)
    raw = json.dumps(payload, separators=(",", ":")).encode()
    descriptor = _descriptor("level_data", payload, raw=raw)
    assert validate_remote_payload(descriptor, raw).reason_code is PayloadReasonCode.LIMIT_EXCEEDED

    payload = _payloads()["level_data"]
    nested: object = "leaf"
    for _ in range(MAX_NESTING_DEPTH + 1):
        nested = [nested]
    payload["nested"] = nested
    raw = json.dumps(payload, separators=(",", ":")).encode()
    descriptor = _descriptor("level_data", payload, raw=raw)
    assert validate_remote_payload(descriptor, raw).reason_code is PayloadReasonCode.LIMIT_EXCEEDED


def test_validator_source_has_no_dynamic_execution_io_network_or_game_imports() -> None:
    tree = ast.parse((PACKAGE / "payload_validation.py").read_text(encoding="utf-8"))
    forbidden_modules = {"httpx", "requests", "socket", "urllib", "aiohttp", "boto3", "scrubbots_pixel_factory", "godot", "gameplay", "runtime"}
    forbidden_calls = {"eval", "exec", "compile", "__import__", "import_module", "open"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not {alias.name.split(".", 1)[0] for alias in node.names} & forbidden_modules
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".", 1)[0] not in forbidden_modules
        elif isinstance(node, ast.Call):
            assert not (isinstance(node.func, ast.Name) and node.func.id in forbidden_calls)
