from __future__ import annotations

import ast
import builtins
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
PACKAGE_ROOT = CONTENT_PIPELINE / "src" / "scrubbots_content_pipeline"
EXAMPLES = CONTENT_PIPELINE / "schemas" / "v1" / "examples"
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    BOUNDARY_VERSION,
    ContentDisposition,
    ReasonCode,
    classify_content,
    serialize_result,
)


def _example(name: str) -> dict[str, object]:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "filename",
    ("level.json", "supply-plan.json", "approved-metadata.json"),
)
def test_versioned_allowlisted_declarative_examples_are_remote_eligible(filename: str) -> None:
    descriptor = _example(filename)
    result = classify_content(descriptor)
    assert result.boundary_version == BOUNDARY_VERSION == "1.0"
    assert result.disposition is ContentDisposition.REMOTE_DECLARATIVE
    assert result.reason_codes == (ReasonCode.ALLOWLIST_MATCH,)


def test_classification_results_and_reason_codes_are_deterministic() -> None:
    descriptor = _example("level.json")
    first = classify_content(descriptor)
    second = classify_content(dict(reversed(tuple(descriptor.items()))))
    assert first == second
    assert serialize_result(first) == serialize_result(second)
    assert json.loads(serialize_result(first)) == {
        "boundary_version": "1.0",
        "disposition": "REMOTE_DECLARATIVE",
        "reason_codes": ["ALLOWLIST_MATCH"],
    }


@pytest.mark.parametrize(
    ("path", "disposition", "reason"),
    (
        ("scripts/level.gd", ContentDisposition.APP_OWNED, ReasonCode.APP_CODE_EXTENSION),
        ("tools/converter.py", ContentDisposition.APP_OWNED, ReasonCode.APP_CODE_EXTENSION),
        ("bin/publisher.exe", ContentDisposition.APP_OWNED, ReasonCode.APP_CODE_EXTENSION),
        ("native/libhelper.dll", ContentDisposition.APP_OWNED, ReasonCode.APP_CODE_EXTENSION),
        ("content/addons/custom_node.json", ContentDisposition.APP_OWNED, ReasonCode.PLUGIN_OR_ADDON_PATH),
        ("content/plugins/custom_node.json", ContentDisposition.APP_OWNED, ReasonCode.PLUGIN_OR_ADDON_PATH),
        ("scenes/main.tscn", ContentDisposition.APP_OWNED, ReasonCode.APP_OWNED_RESOURCE_TYPE),
        ("resources/theme.tres", ContentDisposition.APP_OWNED, ReasonCode.APP_OWNED_RESOURCE_TYPE),
    ),
)
def test_app_owned_code_plugin_and_resource_paths_are_never_remote(
    path: str, disposition: ContentDisposition, reason: ReasonCode
) -> None:
    result = classify_content({"logical_path": path})
    assert result.disposition is disposition
    assert result.reason_codes == (reason,)


@pytest.mark.parametrize(
    ("path", "reason"),
    (
        ("/levels/level-001.json", ReasonCode.ABSOLUTE_PATH),
        ("C:/levels/level-001.json", ReasonCode.ABSOLUTE_PATH),
        ("C:\\levels\\level-001.json", ReasonCode.ABSOLUTE_PATH),
        ("//server/share/level.json", ReasonCode.ABSOLUTE_PATH),
        ("../levels/level-001.json", ReasonCode.PATH_TRAVERSAL),
        ("levels/../level-001.json", ReasonCode.PATH_TRAVERSAL),
        ("levels\\..\\level-001.json", ReasonCode.PATH_TRAVERSAL),
        ("levels//level-001.json", ReasonCode.NON_CANONICAL_PATH),
    ),
)
def test_absolute_noncanonical_and_traversal_paths_fail_closed(path: str, reason: ReasonCode) -> None:
    descriptor = _example("level.json")
    descriptor["logical_path"] = path
    result = classify_content(descriptor)
    assert result.disposition is ContentDisposition.REJECTED
    assert result.reason_codes == (reason,)


@pytest.mark.parametrize(
    ("changes", "reason"),
    (
        ({"schema_id": "scrubbots.level.v999"}, ReasonCode.UNKNOWN_SCHEMA),
        ({"content_type": "script"}, ReasonCode.UNKNOWN_CONTENT_TYPE),
        ({"media_type": "application/octet-stream"}, ReasonCode.MEDIA_TYPE_MISMATCH),
        ({"logical_path": "levels/level-001.unknown"}, ReasonCode.UNKNOWN_EXTENSION),
        ({"content_type": "supply_plan_data"}, ReasonCode.SCHEMA_TYPE_MISMATCH),
        ({"extra": "unknown"}, ReasonCode.UNKNOWN_DESCRIPTOR_FIELD),
    ),
)
def test_unknown_schema_type_extension_and_descriptor_fields_are_rejected(
    changes: dict[str, object], reason: ReasonCode
) -> None:
    descriptor = _example("level.json")
    descriptor.update(changes)
    result = classify_content(descriptor)
    assert result.disposition is ContentDisposition.REJECTED
    assert result.reason_codes == (reason,)


@pytest.mark.parametrize(
    "attributes",
    (
        {"level_id": "level-001", "payload_sha256": "a" * 64, "width": 20, "height": 20, "script": "res://x.gd"},
        {"level_id": "level-001", "payload_sha256": "a" * 64, "width": 20, "height": 20, "expression": "eval('bad')"},
        {"level_id": "level-001", "payload_sha256": "a" * 64, "width": 20, "height": 20, "display_name": "res://scripts/a.gd"},
    ),
)
def test_script_references_executable_fields_and_expressions_are_rejected(
    attributes: dict[str, object],
) -> None:
    descriptor = _example("level.json")
    descriptor["attributes"] = attributes
    result = classify_content(descriptor)
    assert result.disposition is ContentDisposition.REJECTED
    assert result.reason_codes[0] in {ReasonCode.EXECUTABLE_FIELD, ReasonCode.EXECUTABLE_REFERENCE}


def test_descriptor_is_never_imported_or_executed(monkeypatch: pytest.MonkeyPatch) -> None:
    descriptor = _example("level.json")
    descriptor["attributes"] = {
        "level_id": "level-001",
        "payload_sha256": "a" * 64,
        "width": 20,
        "height": 20,
        "expression": "__import__('os').system('whoami')",
    }

    def forbid_import(*args: object, **kwargs: object) -> object:
        raise AssertionError("classifier attempted a dynamic import")

    monkeypatch.setattr(builtins, "__import__", forbid_import)
    result = classify_content(descriptor)
    assert result.disposition is ContentDisposition.REJECTED
    assert result.reason_codes == (ReasonCode.EXECUTABLE_FIELD,)


def test_contract_schema_documents_the_narrow_versioned_allow_list() -> None:
    schema_path = CONTENT_PIPELINE / "schemas" / "v1" / "content-boundary.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["properties"]["boundary_version"]["const"] == "1.0"
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]["content_type"]["enum"]) == {
        "level_data",
        "supply_plan_data",
        "approved_metadata",
    }
    assert len(schema["oneOf"]) == 3


def test_classifier_source_uses_no_dynamic_execution_network_or_game_imports() -> None:
    source_path = PACKAGE_ROOT / "content_boundary.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    forbidden_imports = {
        "httpx", "requests", "socket", "urllib", "aiohttp", "boto3",
        "scrubbots_pixel_factory", "level_factory", "godot", "gameplay", "runtime",
    }
    forbidden_calls = {"eval", "exec", "compile", "__import__", "import_module", "open"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported = {alias.name.split(".", 1)[0] for alias in node.names}
            assert not imported & forbidden_imports
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".", 1)[0] not in forbidden_imports
        elif isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else None
            assert name not in forbidden_calls
