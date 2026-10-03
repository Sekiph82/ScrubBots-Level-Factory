from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
PACKAGE_ROOT = CONTENT_PIPELINE / "src" / "scrubbots_content_pipeline"
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    Environment,
    PipelineConfig,
    serialize_config,
    validate_only,
)


def _python_sources() -> list[Path]:
    return sorted(CONTENT_PIPELINE.rglob("*.py"))


def test_standalone_project_and_package_exist_in_clean_checkout() -> None:
    assert (CONTENT_PIPELINE / "pyproject.toml").is_file()
    assert (PACKAGE_ROOT / "__init__.py").is_file()
    assert (CONTENT_PIPELINE / "schemas" / "v1" / "pipeline-config.schema.json").is_file()
    assert (CONTENT_PIPELINE / "README.md").is_file()


def test_package_import_and_local_validation_only_entry_are_available() -> None:
    report = validate_only(PipelineConfig(environment=Environment.STAGING))
    assert report.accepted is True
    assert report.environment == "staging"
    assert report.actions == ("validate_config", "emit_local_report")


def test_schema_and_config_serialization_are_versioned_and_deterministic() -> None:
    schema_path = CONTENT_PIPELINE / "schemas" / "v1" / "pipeline-config.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    config = PipelineConfig(environment=Environment.PRODUCTION)
    encoded = serialize_config(config)
    assert schema["properties"]["schema_version"]["const"] == "1.0"
    assert schema["properties"]["require_owner_approval"]["const"] is True
    assert encoded == serialize_config(config)
    assert json.loads(encoded) == {
        "environment": "production",
        "input_contract": "scrubbots.level_factory.accepted-content.v1",
        "require_owner_approval": True,
        "schema_version": "1.0",
    }


def test_publish_promote_and_rollback_are_protocol_placeholders_only() -> None:
    provider_source = (PACKAGE_ROOT / "provider.py").read_text(encoding="utf-8")
    tree = ast.parse(provider_source)
    provider_class = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ProviderAdapter"
    )
    methods = {node.name: node for node in provider_class.body if isinstance(node, ast.FunctionDef)}
    assert {"validate", "publish", "promote", "rollback"} <= methods.keys()
    for name in ("publish", "promote", "rollback"):
        method = methods[name]
        assert len(method.body) == 2
        assert ast.get_docstring(method) is not None
        placeholder = method.body[-1]
        assert isinstance(placeholder, ast.Expr)
        assert isinstance(placeholder.value, ast.Constant)
        assert placeholder.value.value is Ellipsis

    orchestration_source = (PACKAGE_ROOT / "orchestration.py").read_text(encoding="utf-8")
    orchestration_tree = ast.parse(orchestration_source)
    protocols = {
        node.name: node
        for node in orchestration_tree.body
        if isinstance(node, ast.ClassDef)
    }
    expected = {
        "PublishOrchestrator": "publish",
        "PromotionOrchestrator": "promote",
        "RollbackOrchestrator": "rollback",
        "EvidenceSink": "write_report",
    }
    for class_name, method_name in expected.items():
        methods = [
            node
            for node in protocols[class_name].body
            if isinstance(node, ast.FunctionDef) and node.name == method_name
        ]
        assert len(methods) == 1
        assert isinstance(methods[0].body[-1], ast.Expr)
        assert isinstance(methods[0].body[-1].value, ast.Constant)
        assert methods[0].body[-1].value.value is Ellipsis


def test_no_secrets_credentials_or_runtime_network_mutation_code() -> None:
    source_files = [path for path in CONTENT_PIPELINE.rglob("*") if path.is_file()]
    forbidden_secret_patterns = (
        re.compile(r"(?i)\b(api[_-]?key|password|access[_-]?token)\s*[:=]\s*['\"][^'\"]+"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    )
    for path in source_files:
        if path.suffix not in {".py", ".toml", ".json", ".md"}:
            continue
        content = path.read_text(encoding="utf-8")
        assert not any(pattern.search(content) for pattern in forbidden_secret_patterns), path

    forbidden_import_roots = {
        "httpx",
        "requests",
        "socket",
        "urllib",
        "aiohttp",
        "boto3",
    }
    for path in _python_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".", 1)[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported = {node.module.split(".", 1)[0]}
            else:
                continue
            assert not imported & forbidden_import_roots, (path, imported)


def test_dependencies_are_one_way_and_no_second_tracker_exists() -> None:
    for path in _python_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.Import):
                module = ",".join(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
            assert module is None or not any(
                forbidden in module.lower()
                for forbidden in ("scrubbots_pixel_factory", "level_factory", "gameplay", "godot")
            ), (path, module)

    core_roots = (ROOT / "src", ROOT / "level_factory")
    for core_root in core_roots:
        if not core_root.exists():
            continue
        for path in core_root.rglob("*.py"):
            content = path.read_text(encoding="utf-8")
            assert "scrubbots_content_pipeline" not in content, path
            assert "content_pipeline" not in content, path

    assert (ROOT / "TASKS.md").is_file()
    assert not any(path.name.lower() == "tasks.md" for path in CONTENT_PIPELINE.rglob("*"))
