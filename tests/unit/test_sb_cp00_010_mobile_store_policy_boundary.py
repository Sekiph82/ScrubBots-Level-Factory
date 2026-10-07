from __future__ import annotations

import ast
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/security/MOBILE_STORE_POLICY_BOUNDARY_V01.md"
SNAPSHOT = ROOT / "content_pipeline/policy/mobile_store_policy_boundary_v1.json"
SCHEMA = ROOT / "content_pipeline/schemas/v1/mobile-store-policy-boundary.schema.json"
PACKAGE = ROOT / "content_pipeline/src/scrubbots_content_pipeline"
FORBIDDEN_IMPORT_ROOTS = {
    "aiohttp", "boto3", "botocore", "google", "http", "httpx", "requests", "socket",
    "subprocess", "urllib", "websocket", "websockets",
}
FORBIDDEN_DYNAMIC_IMPORTS = {"__import__", "import_module"}


def _validate_schema(schema: object, value: object, path: str = "$", errors: list[str] | None = None) -> list[str]:
    """Validate the schema subset used here without adding a runtime dependency."""
    if errors is None:
        errors = []
    if not isinstance(schema, dict):
        errors.append(f"{path}: schema node is not an object")
        return errors
    allowed = {
        "$schema", "$id", "title", "type", "additionalProperties", "required", "properties",
        "items", "minItems", "minLength", "enum", "const", "format", "pattern",
    }
    unsupported = set(schema) - allowed
    if unsupported:
        errors.append(f"{path}: unsupported schema keywords {sorted(unsupported)}")
        return errors
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is not in enum")
    kind = schema.get("type")
    valid_type = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "boolean": lambda v: type(v) is bool,
        "integer": lambda v: type(v) is int,
        "number": lambda v: type(v) in (int, float),
    }
    if kind is not None and (kind not in valid_type or not valid_type[kind](value)):
        errors.append(f"{path}: expected type {kind}")
        return errors
    if isinstance(value, dict) and kind == "object":
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value.keys() - properties.keys():
                errors.append(f"{path}: unexpected property {key}")
        for key, subschema in properties.items():
            if key in value:
                _validate_schema(subschema, value[key], f"{path}.{key}", errors)
    if isinstance(value, list) and kind == "array":
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: fewer than minItems")
        for index, item in enumerate(value):
            _validate_schema(schema.get("items", {}), item, f"{path}[{index}]", errors)
    if isinstance(value, str) and kind == "string":
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            errors.append(f"{path}: pattern mismatch")
        if schema.get("format") == "date-time":
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{path}: invalid date-time")
        if schema.get("format") == "uri":
            parsed = urlparse(value)
            if not parsed.scheme or not parsed.netloc:
                errors.append(f"{path}: invalid URI")
    return errors


def _evidence() -> tuple[dict[str, object], dict[str, object], str]:
    assert REPORT.is_file()
    assert SNAPSHOT.is_file()
    assert SCHEMA.is_file()
    report = REPORT.read_text(encoding="utf-8")
    snapshot_bytes = SNAPSHOT.read_bytes()
    snapshot = json.loads(snapshot_bytes)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert snapshot_bytes == (json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    return snapshot, schema, report


def _forbidden_content_pipeline_imports(package: Path) -> list[str]:
    violations: list[str] = []
    for source_path in sorted(package.rglob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [item.name.split(".", 1)[0] for item in node.names]
                if source_path.name == "r2_provider.py":
                    imported = [root for root in imported if root not in {"boto3", "botocore"}]
                if set(imported) & FORBIDDEN_IMPORT_ROOTS:
                    violations.append(f"{source_path}:{node.lineno}: {', '.join(imported)}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                if source_path.name == "r2_provider.py" and root == "botocore":
                    continue
                if root in FORBIDDEN_IMPORT_ROOTS:
                    violations.append(f"{source_path}:{node.lineno}: {node.module}")
            elif isinstance(node, ast.Call):
                called_name = node.func.id if isinstance(node.func, ast.Name) else (
                    node.func.attr if isinstance(node.func, ast.Attribute) else ""
                )
                if called_name in FORBIDDEN_DYNAMIC_IMPORTS:
                    violations.append(f"{source_path}:{node.lineno}: dynamic import {called_name}")
    return violations


def test_snapshot_is_deterministic_and_validates_against_versioned_schema() -> None:
    snapshot, schema, _ = _evidence()
    assert _validate_schema(schema, snapshot) == []
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"


def test_sources_are_official_current_and_section_specific() -> None:
    snapshot, _, report = _evidence()
    sources = snapshot["sources"]
    expected = {
        "google_play_device_network_abuse": ("GOOGLE_PLAY", "Device and Network Abuse"),
        "google_play_deceptive_behavior": ("GOOGLE_PLAY", "Deceptive Behavior"),
        "google_play_policy_archive": ("GOOGLE_PLAY", "Policy Archive"),
        "apple_app_review_guidelines": ("APPLE", "App Review Guidelines"),
        "apple_developer_program_license": ("APPLE", "Apple Developer Program License Agreement"),
    }
    assert {source["source_id"] for source in sources} == set(expected)
    for source in sources:
        platform, title = expected[source["source_id"]]
        parsed = urlparse(source["url"])
        assert parsed.scheme == "https"
        assert parsed.hostname in {"support.google.com", "developer.apple.com"}
        assert source["platform"] == platform
        assert source["title"] == title
        assert source["sections"]
        assert source["checked_at_utc"] == snapshot["checked_at_utc"]
        assert source["checked_at_utc"].endswith("Z")
        assert source["title"] in report
        assert source["url"] in report
    by_id = {source["source_id"]: source for source in sources}
    assert {"3.1", "3.2", "5 Behavior Transparency"} <= set(by_id["google_play_deceptive_behavior"]["sections"])
    assert {"2.5.2", "4.7"} <= set(by_id["apple_app_review_guidelines"]["sections"])
    assert any(section.startswith("3.3.1(B)") for section in by_id["apple_developer_program_license"]["sections"])
    assert any(section.startswith("3.3.1(C)") for section in by_id["apple_developer_program_license"]["sections"])
    assert "August 26, 2026" in by_id["google_play_policy_archive"]["policy_paraphrase"]


def test_release_recheck_and_m20_ownership_are_explicit() -> None:
    snapshot, _, report = _evidence()
    assert snapshot["final_recheck_required"] is True
    assert snapshot["architecture_dispositions"]["final_release_recheck"] == "REQUIRED"
    assert snapshot["m20_ownership"]["milestone"] == "M20"
    assert {item["id"] for item in snapshot["m20_ownership"]["required_tasks"]} == {"SB-CP09-001", "SB-CP09-002"}
    assert "M20" in report and "SB-CP09-001" in report and "SB-CP09-002" in report


def test_architecture_mapping_and_forbidden_behavior_are_explicit() -> None:
    snapshot, _, report = _evidence()
    rules = {rule["id"]: rule for rule in snapshot["boundary_rules"]}
    assert {
        "level_data_v1", "supply_plan_v1", "level_metadata_v1", "remote_executable_or_behavior_payloads",
        "publisher_dry_run", "provider_abstraction", "credential_boundary", "runtime_and_provider_delivery",
    } <= set(rules)
    assert rules["level_data_v1"]["disposition"] == "DECLARATIVE_DATA_ONLY"
    assert rules["supply_plan_v1"]["disposition"] == "DECLARATIVE_DATA_ONLY"
    assert rules["level_metadata_v1"]["disposition"] == "DECLARATIVE_DATA_ONLY"
    assert rules["remote_executable_or_behavior_payloads"]["disposition"] == "FORBIDDEN"
    assert rules["publisher_dry_run"]["disposition"] == "NO_REMOTE_MUTATION"
    assert rules["provider_abstraction"]["disposition"] == "NO_CONCRETE_PROVIDER"
    assert rules["credential_boundary"]["disposition"] == "NO_GIT_CREDENTIALS"
    assert rules["runtime_and_provider_delivery"]["disposition"] == "NOT_YET_VERIFIED"
    for token in (
        "scrubbots.level_supply_plan.v1", "scrubbots.level.metadata.v1", "LevelData V1",
        "executable", "plugins", "addons", "autoloads", "eval/exec", "review-environment",
        "hidden", "M15/M16", "M18", "remote_mutation_performed",
    ):
        assert token.casefold() in report.casefold() or any(token.casefold() in rule["rule"].casefold() for rule in rules.values())
    assert "Guideline 4.7 is not a blanket" in report


def test_evidence_makes_no_definitive_approval_or_certification_claims() -> None:
    _, _, report = _evidence()
    combined = report + "\n" + SNAPSHOT.read_text(encoding="utf-8")
    prohibited_claims = (
        r"\bAPP_STORE_APPROVED\b", r"\bPLAY_APPROVED\b", r"\bLEGALLY_COMPLIANT\b",
        r"guaranteed\s+(?:store\s+)?acceptance", r"policy\s+certification",
        r"legally\s+compliant", r"approved\s+by\s+(?:the\s+)?(?:app\s+store|google\s+play)",
    )
    assert not any(re.search(pattern, combined, re.IGNORECASE) for pattern in prohibited_claims)
    assert "not legal advice" in report
    assert "not" in report.casefold() and "store review decision" in report


def test_cp010_adds_no_runtime_provider_network_or_tracker_implementation() -> None:
    assert (ROOT / "TASKS.md").is_file()
    tracker_diff = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", "TASKS.md"], cwd=ROOT, check=False,
    )
    assert tracker_diff.returncode == 0
    tracked_task_files = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    task_paths = {path for path in tracked_task_files if Path(path).name.casefold() == "tasks.md"}
    assert "TASKS.md" in task_paths
    assert "content_pipeline/TASKS.md" not in task_paths
    readme = (ROOT / "content_pipeline/README.md").read_text(encoding="utf-8")
    assert "`TASKS.md` is the only live task tracker" in readme
    assert _forbidden_content_pipeline_imports(PACKAGE) == []


@pytest.mark.parametrize(
    "source",
    [
        "import httpx\n",
        "from google.cloud import storage\n",
        "import subprocess\n",
        "__import__('requests')\n",
    ],
)
def test_cp010_recursive_guard_rejects_forbidden_nested_imports(tmp_path: Path, source: str) -> None:
    package = tmp_path / "package"
    nested = package / "declarative" / "nested"
    nested.mkdir(parents=True)
    (nested / "new_manifest_child.py").write_text(source, encoding="utf-8")
    violations = _forbidden_content_pipeline_imports(package)
    assert len(violations) == 1
    assert "new_manifest_child.py" in violations[0]


def test_cp010_recursive_guard_allows_nested_declarative_modules(tmp_path: Path) -> None:
    package = tmp_path / "package"
    nested = package / "declarative" / "nested"
    nested.mkdir(parents=True)
    (nested / "manifest_child.py").write_text("from dataclasses import dataclass\n", encoding="utf-8")
    assert _forbidden_content_pipeline_imports(package) == []
