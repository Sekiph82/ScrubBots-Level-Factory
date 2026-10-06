from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))

from scrubbots_content_pipeline.manifest_v1 import (  # noqa: E402
    CONTENT_MANIFEST_SCHEMA,
    CONTENT_MANIFEST_SCHEMA_VERSION,
    ContentManifestError,
    ContentManifestV1,
    ManifestCompatibilityReasonCode,
    ManifestSuccessorReasonCode,
    ManifestLevelV1,
    ManifestPackV1,
    check_game_version_compatibility,
    check_manifest_successor,
    is_level_disabled,
    parse_canonical_game_version,
)


def test_minimal_fixture_round_trips_as_the_canonical_empty_manifest() -> None:
    fixture_path = CONTENT_PIPELINE / "schemas/v1/examples/content-manifest-minimal.json"
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    manifest = ContentManifestV1.from_dict(raw)
    assert manifest == ContentManifestV1()
    assert manifest.to_dict() == raw
    assert manifest.to_json_bytes() == fixture_path.read_bytes().rstrip(b"\r\n")
    assert manifest.schema == CONTENT_MANIFEST_SCHEMA
    assert manifest.schema_version == CONTENT_MANIFEST_SCHEMA_VERSION == 1
    assert manifest.content_version == 1


def test_model_owns_explicit_types_and_preserves_declared_level_order() -> None:
    manifest = ContentManifestV1(
        packs=(pack_record("pack-z"), pack_record("pack-a")),
        levels=(ManifestLevelV1("tutorial-alpha", "pack-z"), ManifestLevelV1("level-004", "pack-a")),
    )
    assert [item.pack_id for item in manifest.packs] == ["pack-a", "pack-z"]
    assert [item.level_id for item in manifest.levels] == ["tutorial-alpha", "level-004"]
    assert manifest.to_json_bytes() == manifest.to_json_bytes()
    assert ContentManifestV1.from_dict(manifest.to_dict()) == manifest


def test_noncontiguous_level_ids_are_preserved_without_numeric_order_derivation() -> None:
    source_order = ["level-100", "tutorial-alpha", "9", "level-004"]
    manifest = ContentManifestV1(
        levels=tuple(ManifestLevelV1(level_id, "pack-a") for level_id in source_order)
    )
    parsed = ContentManifestV1.from_dict(manifest.to_dict())
    assert [item.level_id for item in parsed.levels] == source_order
    assert [item["level_id"] for item in manifest.to_dict()["levels"]] == source_order


@pytest.mark.parametrize(
    "change, message",
    [
        ({"unexpected": True}, "invalid manifest fields"),
        ({"schema": "scrubbots.content.manifest.v2"}, "unsupported manifest schema"),
        ({"schema_version": True}, "unsupported manifest schema_version"),
        ({"schema_version": 2}, "unsupported manifest schema_version"),
        ({"packs": {"pack_id": "pack-a"}}, "packs, levels, and disabled_levels must be arrays"),
    ],
)
def test_root_is_closed_and_identity_or_version_fail_closed(change, message: str) -> None:
    raw = ContentManifestV1().to_dict()
    raw.update(change)
    with pytest.raises(ContentManifestError, match=message):
        ContentManifestV1.from_dict(raw)


def test_item_shapes_and_duplicate_identities_are_rejected() -> None:
    with pytest.raises(ContentManifestError, match="invalid pack fields"):
        ContentManifestV1.from_dict({**ContentManifestV1().to_dict(), "packs": [{"pack_id": "p", "url": "x"}]})
    with pytest.raises(ContentManifestError, match="duplicate pack_id"):
        ContentManifestV1(packs=(pack_record("pack-a"), pack_record("pack-a")))
    with pytest.raises(ContentManifestError, match="duplicate level_id"):
        ContentManifestV1(
            levels=(ManifestLevelV1("level-a", "pack-a"), ManifestLevelV1("level-a", "pack-b"))
        )


def test_schema_and_fixture_are_closed_and_declarative() -> None:
    schema = json.loads((CONTENT_PIPELINE / "schemas/v1/content-manifest.schema.json").read_text(encoding="utf-8"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["schema"]["const"] == CONTENT_MANIFEST_SCHEMA
    assert schema["properties"]["schema_version"] == {"type": "integer", "const": 1}
    assert set(schema["required"]) == {
        "schema", "schema_version", "content_version", "minimum_game_version", "disabled_levels", "packs", "levels"
    }
    assert schema["properties"]["content_version"] == {"type": "integer", "minimum": 1}
    assert schema["properties"]["minimum_game_version"]["pattern"] == (
        r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"
    )
    pack_schema = schema["properties"]["packs"]["items"]
    assert set(pack_schema["required"]) == {"pack_id", "pack_version", "object_key", "sha256", "byte_length"}
    assert pack_schema["additionalProperties"] is False
    disabled_schema = schema["properties"]["disabled_levels"]
    assert disabled_schema["type"] == "array" and disabled_schema["uniqueItems"] is True


@pytest.mark.parametrize("version", [True, False, 0, -1, 1.0, "1", None])
def test_content_version_is_a_required_real_positive_integer(version: object) -> None:
    raw = ContentManifestV1().to_dict()
    raw["content_version"] = version
    with pytest.raises(ContentManifestError, match="content_version"):
        ContentManifestV1.from_dict(raw)


def test_content_version_is_required_by_parser_and_model() -> None:
    raw = ContentManifestV1().to_dict()
    del raw["content_version"]
    with pytest.raises(ContentManifestError, match="invalid manifest fields"):
        ContentManifestV1.from_dict(raw)
    with pytest.raises(ContentManifestError, match="content_version"):
        ContentManifestV1(content_version=True)


@pytest.mark.parametrize("candidate_version", [2, 7, 10])
def test_successor_check_accepts_numeric_increases_and_gaps(candidate_version: int) -> None:
    candidate = {**ContentManifestV1().to_dict(), "content_version": candidate_version}
    result = check_manifest_successor(1, candidate)
    assert result.accepted
    assert result.reason_code is ManifestSuccessorReasonCode.VALID_SUCCESSOR


@pytest.mark.parametrize("previous_version, candidate_version", [(1, 1), (2, 1)])
def test_successor_check_rejects_equal_or_lower_versions(previous_version: int, candidate_version: int) -> None:
    candidate = {**ContentManifestV1().to_dict(), "content_version": candidate_version}
    result = check_manifest_successor(previous_version, candidate)
    assert not result.accepted
    assert result.reason_code is ManifestSuccessorReasonCode.CONTENT_VERSION_NOT_INCREASED


def test_successor_check_compares_numbers_not_lexicographic_strings() -> None:
    candidate = {**ContentManifestV1().to_dict(), "content_version": 10}
    assert check_manifest_successor(9, candidate).accepted
    assert check_manifest_successor(10, candidate).reason_code is (
        ManifestSuccessorReasonCode.CONTENT_VERSION_NOT_INCREASED
    )


@pytest.mark.parametrize("previous_version", [True, False, 0, -1, 1.0, "1", None])
def test_successor_check_rejects_malformed_previous_versions(previous_version: object) -> None:
    result = check_manifest_successor(previous_version, ContentManifestV1().to_dict())
    assert not result.accepted
    assert result.reason_code is ManifestSuccessorReasonCode.INVALID_PREVIOUS_CONTENT_VERSION


def test_successor_check_rejects_malformed_candidate_with_stable_reason() -> None:
    result = check_manifest_successor(1, {"schema": "unknown"})
    assert not result.accepted
    assert result.reason_code is ManifestSuccessorReasonCode.INVALID_CANDIDATE_MANIFEST


def test_changed_bytes_with_same_content_version_are_not_a_successor() -> None:
    previous = ContentManifestV1(content_version=4).to_dict()
    changed_bytes = {**previous, "packs": [pack_record("new-pack").to_dict()]}
    assert previous != changed_bytes
    result = check_manifest_successor(4, changed_bytes)
    assert not result.accepted
    assert result.reason_code is ManifestSuccessorReasonCode.CONTENT_VERSION_NOT_INCREASED


@pytest.mark.parametrize(
    "version, expected",
    [("0.0.0", (0, 0, 0)), ("1.2.3", (1, 2, 3)), ("10.4.25", (10, 4, 25))],
)
def test_canonical_game_version_parser(version: str, expected: tuple[int, int, int]) -> None:
    assert parse_canonical_game_version(version) == expected


@pytest.mark.parametrize("version", [None, True, 1, "", "1", "1.2", "1.2.3.4", "01.2.3", "1.02.3", "1.2.03", "-1.2.3", "1.+2.3", " 1.2.3", "1.2.3 ", "1. 2.3"])
def test_canonical_game_version_parser_rejects_malformed_ambiguous_values(version: object) -> None:
    with pytest.raises(ContentManifestError):
        parse_canonical_game_version(version)


@pytest.mark.parametrize("version", [None, True, 1, "1.2", " 1.2.3"])
def test_manifest_requires_a_canonical_minimum_game_version(version: object) -> None:
    raw = ContentManifestV1().to_dict()
    raw["minimum_game_version"] = version
    with pytest.raises(ContentManifestError, match="game version"):
        ContentManifestV1.from_dict(raw)


def test_manifest_requires_minimum_game_version_field() -> None:
    raw = ContentManifestV1().to_dict()
    del raw["minimum_game_version"]
    with pytest.raises(ContentManifestError, match="invalid manifest fields"):
        ContentManifestV1.from_dict(raw)


@pytest.mark.parametrize(
    "minimum,current,compatible,reason",
    [
        ("1.2.3", "1.2.3", True, ManifestCompatibilityReasonCode.COMPATIBLE),
        ("1.2.3", "1.2.4", True, ManifestCompatibilityReasonCode.COMPATIBLE),
        ("1.2.3", "1.3.0", True, ManifestCompatibilityReasonCode.COMPATIBLE),
        ("1.2.3", "2.0.0", True, ManifestCompatibilityReasonCode.COMPATIBLE),
        ("1.2.3", "1.2.2", False, ManifestCompatibilityReasonCode.GAME_VERSION_TOO_OLD),
        ("1.10.0", "1.9.99", False, ManifestCompatibilityReasonCode.GAME_VERSION_TOO_OLD),
    ],
)
def test_game_version_compatibility_uses_explicit_numeric_tuple_order(
    minimum: str, current: str, compatible: bool, reason: ManifestCompatibilityReasonCode
) -> None:
    result = check_game_version_compatibility(minimum, current)
    assert result.compatible is compatible
    assert result.reason_code is reason


def test_game_version_compatibility_rejects_malformed_inputs_deterministically() -> None:
    assert check_game_version_compatibility("1.2.3", "1.2").reason_code is (
        ManifestCompatibilityReasonCode.INVALID_CURRENT_GAME_VERSION
    )
    assert check_game_version_compatibility("1.2", "1.2.3").reason_code is (
        ManifestCompatibilityReasonCode.INVALID_MINIMUM_GAME_VERSION
    )


def pack_record(pack_id: str) -> ManifestPackV1:
    return ManifestPackV1(pack_id, 1, f"packs/{pack_id}/v1.scrubpack", "a" * 64, 128)


def test_pack_record_serialization_is_deterministic_and_provider_neutral() -> None:
    record = pack_record("pack-a")
    assert record.to_dict() == {
        "pack_id": "pack-a",
        "pack_version": 1,
        "object_key": "packs/pack-a/v1.scrubpack",
        "sha256": "a" * 64,
        "byte_length": 128,
    }
    assert record.to_json_bytes() == record.to_json_bytes()
    assert record.to_json_bytes() == (
        b'{"byte_length":128,"object_key":"packs/pack-a/v1.scrubpack","pack_id":"pack-a",'
        b'"pack_version":1,"sha256":"' + b"a" * 64 + b'"}'
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"pack_version": True},
        {"pack_version": 0},
        {"pack_version": -1},
        {"object_key": "https://cdn.example.invalid/packs/a/v1.scrubpack"},
        {"object_key": "cdn.example.invalid/packs/a/v1.scrubpack"},
        {"object_key": "/packs/a/v1.scrubpack"},
        {"object_key": "C:/packs/a/v1.scrubpack"},
        {"object_key": "//server/share/a.scrubpack"},
        {"object_key": "packs/a/../b.scrubpack"},
        {"object_key": "packs/a/%2e%2e/b.scrubpack"},
        {"object_key": "packs/a\\b/v1.scrubpack"},
        {"object_key": "packs/a/v1.scrubpack?download=1"},
        {"object_key": "packs/a/v1.scrubpack#fragment"},
        {"object_key": "packs/a/user:password@host/v1.scrubpack"},
        {"object_key": "packs/a/v1.zip"},
        {"sha256": "A" * 64},
        {"sha256": "g" * 64},
        {"sha256": "a" * 63},
        {"byte_length": True},
        {"byte_length": 0},
        {"byte_length": -1},
    ],
)
def test_malformed_pack_reference_fields_fail_closed(kwargs: dict[str, object]) -> None:
    values: dict[str, object] = {
        "pack_id": "pack-a",
        "pack_version": 1,
        "object_key": "packs/pack-a/v1.scrubpack",
        "sha256": "a" * 64,
        "byte_length": 128,
    }
    values.update(kwargs)
    with pytest.raises(ContentManifestError):
        ManifestPackV1(**values)  # type: ignore[arg-type]


def test_pack_id_grammar_is_canonical_lowercase_and_blocks_case_collisions() -> None:
    with pytest.raises(ContentManifestError, match="invalid pack_id"):
        pack_record("Pack-A")
    with pytest.raises(ContentManifestError, match="duplicate pack_id"):
        ContentManifestV1(packs=(pack_record("pack-a"), pack_record("pack-a")))


def test_disabled_levels_sort_canonically_and_preserve_unrelated_metadata() -> None:
    pack = pack_record("pack-a")
    level = ManifestLevelV1("level-004", "pack-a")
    manifest = ContentManifestV1(
        packs=(pack,),
        levels=(level,),
        disabled_levels=("future-level", "level-004"),
    )
    before_pack_bytes = pack.to_json_bytes()
    parsed = ContentManifestV1.from_dict(manifest.to_dict())
    assert parsed.disabled_levels == ("future-level", "level-004")
    assert [item.level_id for item in parsed.levels] == ["level-004"]
    assert [item.pack_id for item in parsed.packs] == ["pack-a"]
    assert is_level_disabled(parsed, "future-level")
    assert is_level_disabled(parsed, "level-004")
    assert not is_level_disabled(parsed, "another-valid-id")
    assert pack.to_json_bytes() == before_pack_bytes


@pytest.mark.parametrize(
    "disabled_levels",
    [
        ("level-a", "level-a"),
        ("Level-A", "level-a"),
        ("../level",),
        ("level/a",),
        (True,),
        ["level-a"],
    ],
)
def test_invalid_disabled_level_ids_and_collisions_fail_closed(disabled_levels: object) -> None:
    with pytest.raises(ContentManifestError):
        ContentManifestV1(disabled_levels=disabled_levels)  # type: ignore[arg-type]


def test_disabled_level_query_rejects_invalid_inputs() -> None:
    manifest = ContentManifestV1()
    with pytest.raises(ContentManifestError, match="invalid level_id"):
        is_level_disabled(manifest, "../level")
    with pytest.raises(ContentManifestError, match="manifest must"):
        is_level_disabled(object(), "level-a")  # type: ignore[arg-type]
