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
    ManifestLevelV1,
    ManifestPackV1,
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


def test_model_owns_explicit_types_and_sorts_collections_deterministically() -> None:
    manifest = ContentManifestV1(
        packs=(ManifestPackV1("pack-z"), ManifestPackV1("pack-a")),
        levels=(ManifestLevelV1("level-z", "pack-z"), ManifestLevelV1("level-a", "pack-a")),
    )
    assert [item.pack_id for item in manifest.packs] == ["pack-a", "pack-z"]
    assert [item.level_id for item in manifest.levels] == ["level-a", "level-z"]
    assert manifest.to_json_bytes() == manifest.to_json_bytes()
    assert ContentManifestV1.from_dict(manifest.to_dict()) == manifest


@pytest.mark.parametrize(
    "change, message",
    [
        ({"unexpected": True}, "invalid manifest fields"),
        ({"schema": "scrubbots.content.manifest.v2"}, "unsupported manifest schema"),
        ({"schema_version": True}, "unsupported manifest schema_version"),
        ({"schema_version": 2}, "unsupported manifest schema_version"),
        ({"packs": {"pack_id": "pack-a"}}, "packs and levels must be arrays"),
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
        ContentManifestV1(packs=(ManifestPackV1("pack-a"), ManifestPackV1("pack-a")))
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
    assert set(schema["required"]) == {"schema", "schema_version", "packs", "levels"}
