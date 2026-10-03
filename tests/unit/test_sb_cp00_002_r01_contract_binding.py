from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
FIXTURES = ROOT / "tests" / "fixtures" / "sb_cp00_002_r01"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import ContentDisposition, ReasonCode, classify_content  # noqa: E402


def _fixture() -> dict[str, object]:
    return json.loads((FIXTURES / "current_scrubbots_contracts.json").read_text(encoding="utf-8"))


def _assignment_dict(function: ast.FunctionDef, assignment_name: str) -> ast.Dict:
    matches: list[ast.Dict] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        if any(isinstance(target, ast.Name) and target.id == assignment_name for target in node.targets):
            matches.append(node.value)
    assert len(matches) == 1, f"expected one {assignment_name} mapping in {function.name}"
    return matches[0]


def _mapping_keys(node: ast.Dict) -> set[str]:
    return {key.value for key in node.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)}


def _literal_value(node: ast.Dict, key_name: str) -> object:
    for key, value in zip(node.keys, node.values):
        if isinstance(key, ast.Constant) and key.value == key_name:
            return ast.literal_eval(value)
    raise AssertionError(f"{key_name} missing from production authority mapping")


def _factory_export_assignments() -> tuple[ast.Dict, ast.Dict]:
    path = ROOT / "src" / "scrubbots_pixel_factory" / "supply_pipeline" / "supply_exporter.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    exporter = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SupplyExporter"
    )
    export = next(
        node for node in exporter.body if isinstance(node, ast.FunctionDef) and node.name == "export"
    )
    return _assignment_dict(export, "level"), _assignment_dict(export, "plan")


def _publisher_metadata_assignment() -> ast.Dict:
    path = ROOT / "src" / "scrubbots_pixel_factory" / "supply_pipeline" / "game_publisher.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    publish = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "publish_level"
    )
    return _assignment_dict(publish, "metadata")


def _example(name: str) -> dict[str, object]:
    path = PIPELINE / "schemas" / "v1" / "examples" / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_level_data_v1_export_shape_maps_to_level_data_descriptor() -> None:
    fixture = _fixture()
    assert fixture["authority_repository"] == "Sekiph82/Scrubbots"
    assert fixture["authority_commit"] == "5881a68eefdb8a25f28f15f4fc3047e19fbc64df"
    authority = fixture["level_data"]
    assert isinstance(authority, dict)
    level_node, _ = _factory_export_assignments()
    fields = _mapping_keys(level_node)

    assert fields == set(authority["required_fields"])
    assert _literal_value(level_node, "version") == authority["version"] == 1
    assert authority["version_field"] == "version"
    assert authority["embedded_schema_field"] is None

    descriptor = _example("level.json")
    assert "schema_id" not in descriptor
    assert descriptor["descriptor_contract_id"] == "scrubbots.content-pipeline.level-data.v1"
    descriptor["payload_contract"] = {"authority": authority["authority"], "version": 1}
    result = classify_content(descriptor)
    assert result.disposition is ContentDisposition.REMOTE_DECLARATIVE
    assert result.reason_codes == (ReasonCode.ALLOWLIST_MATCH,)


def test_supply_exporter_and_current_game_loader_schema_are_bound() -> None:
    authority = _fixture()["supply_plan"]
    assert isinstance(authority, dict)
    _, plan_node = _factory_export_assignments()
    assert _mapping_keys(plan_node) >= {
        "schema",
        "version",
        "levelId",
        "columnCount",
        "visiblePreviewDepth",
        "columns",
    }
    schema = _literal_value(plan_node, "schema")
    version = _literal_value(plan_node, "version")
    assert (schema, version) == (authority["schema"], authority["version"])
    assert (authority["schema_field"], authority["version_field"]) == ("schema", "version")

    descriptor = _example("supply-plan.json")
    assert {"level_id", "columns", "preview_depth"} <= set(descriptor["attributes"])
    assert {"levelId", "columnCount", "visiblePreviewDepth"} <= _mapping_keys(plan_node)
    descriptor["payload_contract"] = {"schema": schema, "version": version}
    result = classify_content(descriptor)
    assert result.disposition is ContentDisposition.REMOTE_DECLARATIVE
    assert result.reason_codes == (ReasonCode.ALLOWLIST_MATCH,)


def test_current_publisher_metadata_schema_and_projection_are_bound() -> None:
    metadata_node = _publisher_metadata_assignment()
    assert _literal_value(metadata_node, "schema") == "scrubbots.level.metadata.v1"
    assert _literal_value(metadata_node, "version") == 1
    source_fields = _mapping_keys(metadata_node)
    assert {"schema", "version", "id", "width", "height", "columnCount", "visiblePreviewDepth"} <= source_fields

    descriptor = _example("approved-metadata.json")
    assert {"level_id", "columns", "preview_depth"} <= set(descriptor["attributes"])
    assert {"id", "columnCount", "visiblePreviewDepth"} <= source_fields
    result = classify_content(descriptor)
    assert result.disposition is ContentDisposition.REMOTE_DECLARATIVE
    assert result.reason_codes == (ReasonCode.ALLOWLIST_MATCH,)


def test_previous_synthetic_payload_schema_names_are_not_current_authority() -> None:
    supply = _example("supply-plan.json")
    supply["payload_contract"] = {"schema": "scrubbots.supply-plan.v1", "version": 1}
    result = classify_content(supply)
    assert result.disposition is ContentDisposition.REJECTED
    assert result.reason_codes == (ReasonCode.PAYLOAD_CONTRACT_MISMATCH,)

    metadata = _example("approved-metadata.json")
    metadata["payload_contract"] = {"schema": "scrubbots.approved-metadata.v1", "version": 1}
    result = classify_content(metadata)
    assert result.disposition is ContentDisposition.REJECTED
    assert result.reason_codes == (ReasonCode.PAYLOAD_CONTRACT_MISMATCH,)

    level = _example("level.json")
    level["descriptor_contract_id"] = "scrubbots.level.v1"
    result = classify_content(level)
    assert result.disposition is ContentDisposition.REJECTED
    assert result.reason_codes == (ReasonCode.UNKNOWN_SCHEMA,)


def test_descriptor_schema_separates_boundary_identity_from_payload_authority() -> None:
    schema_path = PIPELINE / "schemas" / "v1" / "content-boundary.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "schema_id" not in schema["properties"]
    assert "descriptor_contract_id" in schema["properties"]
    assert "payload_contract" in schema["properties"]
    assert schema["additionalProperties"] is False


def test_executable_camel_case_and_compound_fields_remain_rejected() -> None:
    for key in ("scriptPath", "nativeCode", "modulePath"):
        descriptor = _example("level.json")
        descriptor[key] = "untrusted"
        result = classify_content(descriptor)
        assert result.disposition is ContentDisposition.REJECTED
        assert result.reason_codes == (ReasonCode.EXECUTABLE_FIELD,)
