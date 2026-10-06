from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    MAX_MANIFEST_BYTES,
    MAX_MANIFEST_COLLECTION_ITEMS,
    MAX_MANIFEST_NESTING_DEPTH,
    MAX_MANIFEST_STRING_LENGTH,
    ContentManifestV1,
    ManifestHistoryV1,
    ManifestLevelV1,
    ManifestPackV1,
    ManifestScheduleV1,
    ManifestParseError,
    ManifestParseReasonCode as Reason,
    append_manifest_history,
    check_app_content_compatibility,
    check_manifest_successor,
    parse_content_manifest_v1,
    serialize_manifest_history,
    validate_manifest_references,
    verify_manifest_history,
)


def _bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _valid_dict() -> dict[str, object]:
    return ContentManifestV1().to_dict()


def _parse_error(raw: bytes, reason: Reason) -> None:
    with pytest.raises(ManifestParseError) as exc:
        parse_content_manifest_v1(raw)
    assert exc.value.reason_code is reason


def test_bytes_to_model_canonical_round_trip_and_noncontiguous_version_gaps() -> None:
    pack = ManifestPackV1("pack-a", 2, "packs/pack-a/v2.scrubpack", "a" * 64, 128)
    model = ContentManifestV1(
        packs=(pack,),
        levels=(ManifestLevelV1("level-100", "pack-a"), ManifestLevelV1("tutorial-alpha", "pack-a")),
        content_version=9,
        disabled_levels=("future-level",),
        schedules=(ManifestScheduleV1("level", "tutorial-alpha", "2030-01-01T00:00:00Z"),),
    )
    raw = model.to_json_bytes()
    parsed = parse_content_manifest_v1(raw)
    assert parsed == model
    assert parsed.to_json_bytes() == raw
    assert parse_content_manifest_v1(parsed.to_json_bytes()).to_json_bytes() == raw
    assert check_manifest_successor(8, parsed.to_dict()).accepted
    compatibility = check_app_content_compatibility(
        current_game_version="1.0.0",
        supported_manifest_schema_versions={model.schema: {1}},
        manifest_schema=model.schema,
        manifest_schema_version=model.schema_version,
        minimum_game_version="2.0.0",
    )
    assert compatibility.reason_code.value == "GAME_VERSION_TOO_OLD"


def test_parser_accepts_the_canonical_minimal_fixture_bytes() -> None:
    raw = (PIPELINE / "schemas/v1/examples/content-manifest-minimal.json").read_bytes().rstrip(b"\r\n")
    parsed = parse_content_manifest_v1(raw)
    assert parsed == ContentManifestV1()
    assert parsed.to_json_bytes() == raw


@pytest.mark.parametrize(
    "raw,reason",
    [
        (b"{} {}", Reason.INVALID_JSON),
        (b"\xff", Reason.INVALID_UTF8),
        (b"[]", Reason.ROOT_NOT_OBJECT),
        (b'{"schema":"scrubbots.content.manifest.v1","schema":"scrubbots.content.manifest.v1"}', Reason.DUPLICATE_JSON_KEY),
        (b'{"x":{"x":1,"x":2}}', Reason.DUPLICATE_JSON_KEY),
        (b'{"x":NaN}', Reason.NONFINITE_NUMBER),
        (b'{"x":Infinity}', Reason.NONFINITE_NUMBER),
        (b'{"x":-Infinity}', Reason.NONFINITE_NUMBER),
        (b'{"x":1e999}', Reason.NONFINITE_NUMBER),
    ],
)
def test_parser_rejects_invalid_utf8_json_duplicate_keys_and_nonfinite_values(raw: bytes, reason: Reason) -> None:
    _parse_error(raw, reason)


def test_parser_enforces_deterministic_size_depth_collection_and_string_limits() -> None:
    _parse_error(b" " * (MAX_MANIFEST_BYTES + 1), Reason.MANIFEST_TOO_LARGE)
    nested = b"[" * (MAX_MANIFEST_NESTING_DEPTH + 1) + b"0" + b"]" * (MAX_MANIFEST_NESTING_DEPTH + 1)
    _parse_error(nested, Reason.NESTING_TOO_DEEP)
    _parse_error(_bytes({**_valid_dict(), "packs": [None] * (MAX_MANIFEST_COLLECTION_ITEMS + 1)}), Reason.COLLECTION_TOO_LARGE)
    _parse_error(_bytes({**_valid_dict(), "minimum_game_version": "x" * (MAX_MANIFEST_STRING_LENGTH + 1)}), Reason.STRING_TOO_LONG)
    with pytest.raises(ManifestParseError) as exc:
        parse_content_manifest_v1(bytearray(_bytes(_valid_dict())))  # type: ignore[arg-type]
    assert exc.value.reason_code is Reason.INPUT_NOT_BYTES


def test_parser_rejects_future_schema_root_fields_and_nested_unknown_fields() -> None:
    _parse_error(_bytes({**_valid_dict(), "schema": "scrubbots.content.manifest.v99"}), Reason.UNSUPPORTED_SCHEMA)
    _parse_error(_bytes({**_valid_dict(), "schema_version": 2}), Reason.UNSUPPORTED_SCHEMA_VERSION)
    _parse_error(_bytes({**_valid_dict(), "unexpected": True}), Reason.INVALID_ROOT_FIELDS)
    pack = {"pack_id": "pack-a", "pack_version": 1, "object_key": "packs/pack-a/v1.scrubpack", "sha256": "a" * 64, "byte_length": 10, "unexpected": True}
    _parse_error(_bytes({**_valid_dict(), "packs": [pack]}), Reason.INVALID_MANIFEST)


def test_parser_rejects_invalid_pack_urls_secrets_ownership_and_schedule_windows() -> None:
    base_pack = {"pack_id": "pack-a", "pack_version": 1, "object_key": "packs/pack-a/v1.scrubpack", "sha256": "a" * 64, "byte_length": 10}
    for object_key in (
        "https://cdn.example/packs/a/v1.scrubpack",
        "packs/a/user:secret@example/v1.scrubpack",
        "packs/a/../v1.scrubpack",
    ):
        _parse_error(_bytes({**_valid_dict(), "packs": [{**base_pack, "object_key": object_key}]}), Reason.INVALID_MANIFEST)
    owner_collision = {
        **_valid_dict(),
        "packs": [base_pack, {**base_pack, "pack_id": "pack-b", "object_key": "packs/pack-b/v1.scrubpack", "sha256": "b" * 64}],
        "levels": [{"level_id": "shared-level", "pack_id": "pack-a"}, {"level_id": "shared-level", "pack_id": "pack-b"}],
    }
    _parse_error(_bytes(owner_collision), Reason.INVALID_MANIFEST)
    schedule = {"target_kind": "level", "target_id": "level-a", "not_before": "2030-02-30T00:00:00Z"}
    _parse_error(_bytes({**_valid_dict(), "schedules": [schedule]}), Reason.INVALID_MANIFEST)


def test_parser_leaves_unknown_references_for_the_separate_cp009_gate() -> None:
    value = {
        **_valid_dict(),
        "levels": [{"level_id": "level-a", "pack_id": "unknown-pack"}],
        "disabled_levels": ["future-level"],
        "schedules": [{"target_kind": "pack", "target_id": "unknown-pack", "not_before": "2030-01-01T00:00:00Z"}],
    }
    parsed = parse_content_manifest_v1(_bytes(value))
    assert parsed.levels[0].pack_id == "unknown-pack"
    result = validate_manifest_references(parsed, ())
    assert result.eligible is False
    reasons = {check.check_id: check.reason_code.value for check in result.checks}
    assert reasons["level_pack_references"] == "LEVEL_PACK_NOT_DECLARED"
    assert reasons["disabled_level_references"] == "DISABLED_LEVEL_NOT_DECLARED"
    assert reasons["schedule_target_references"] == "SCHEDULE_TARGET_NOT_DECLARED"


def test_parser_corpus_includes_and_detects_tampered_manifest_history() -> None:
    first = append_manifest_history(ManifestHistoryV1(), _bytes(_valid_dict()), recorded_at_utc="2026-10-06T10:00:00Z")
    second_manifest = _bytes({**_valid_dict(), "content_version": 5})
    history = append_manifest_history(first, second_manifest, recorded_at_utc="2026-10-06T10:01:00Z")
    assert verify_manifest_history(history).accepted
    tampered_record = replace(history.records[1], manifest_bytes=history.records[1].manifest_bytes + b" ")
    tampered = ManifestHistoryV1((history.records[0], tampered_record), history.tip_sha256)
    assert not verify_manifest_history(tampered).accepted
    with pytest.raises(ValueError):
        serialize_manifest_history(tampered)
