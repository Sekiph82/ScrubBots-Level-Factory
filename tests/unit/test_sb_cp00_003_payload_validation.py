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
        payload["levelId"] = attrs["level_id"]
        payload["columnCount"] = attrs["columns"]
        payload["visiblePreviewDepth"] = attrs["preview_depth"]
        digest_key = "supply_plan_sha256"
    else:
        payload["id"] = attrs["level_id"]
        if kind == "level_data":
            payload["width"], payload["height"] = attrs["width"], attrs["height"]
        else:
            payload["width"], payload["height"] = attrs["width"], attrs["height"]
            payload["columnCount"], payload["visiblePreviewDepth"] = attrs["columns"], attrs["preview_depth"]
        digest_key = "payload_sha256"
    raw = raw if raw is not None else json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    attrs[digest_key] = hashlib.sha256(raw).hexdigest()
    return descriptor


def _payloads() -> dict[str, dict[str, object]]:
    return {
        "level_data": {
            "version": 1, "id": "level-001", "name": "Level 001", "difficulty": "EASY",
            "width": 20, "height": 20, "palette": ["C01", "C02"], "cells": ["C01"] * 399 + ["C02"],
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
        outcome = validate_remote_payload(candidate_descriptor, candidate_raw)
        assert not outcome.accepted
        assert outcome.reason_code in {PayloadReasonCode.CONTRACT_MISMATCH, PayloadReasonCode.DESCRIPTOR_MISMATCH, PayloadReasonCode.INVALID_PAYLOAD}


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
