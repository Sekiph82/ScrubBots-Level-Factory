from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
PACKAGE = PIPELINE / "src" / "scrubbots_content_pipeline"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    BUILDER_RECEIPT_VERSION,
    BuilderPublicationReceipt,
    BuilderTestSummary,
    ParityResult,
    PublicationParity,
    ReceiptReasonCode,
    serialize_builder_receipt,
    validate_builder_receipt,
)


def _valid_receipt() -> BuilderPublicationReceipt:
    final = "d" * 40
    return BuilderPublicationReceipt(
        schema_version=BUILDER_RECEIPT_VERSION,
        task_id="SB-CP00-009-C001",
        prompt_path=".hiveai/prompts/SB-CP00-009-C001_CONTENT_PLATFORM_GITHUB_COORDINATION_PROMPT.md",
        builder_log_path=".hiveai/codex-logs/SB-CP00-009-C001_CONTENT_PLATFORM_GITHUB_COORDINATION_CODEX_LOG.md",
        repository_owner="Sekiph82",
        repository_name="ScrubBots-Level-Factory",
        branch="main",
        base_sha="a" * 40,
        implementation_sha="b" * 40,
        builder_log_sha=final,
        final_sha=final,
        test_summary=BuilderTestSummary(124, 0, 0, 1292, 0, 3, 0, 0),
        publication_parity=PublicationParity(ParityResult.VERIFIED_EQUAL, final, final, 0, 0),
    )


def _repo_files() -> list[Path]:
    ignored_dirs = {".git", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache"}
    return [path for path in PIPELINE.rglob("*") if path.is_file() and not ignored_dirs.intersection(path.parts)]


def test_root_tasks_is_the_only_tracker_and_content_pipeline_has_no_nested_control_plane() -> None:
    assert (ROOT / "TASKS.md").is_file()
    forbidden_names = {
        "tasks.md", "roadmap.md", "dashboard.md", "task-ledger.json", "task-state.json",
        "task-index.json", "session-index.json", "milestone-ledger.json",
    }
    for path in _repo_files():
        name = path.name.casefold()
        assert name not in forbidden_names
        assert not name.startswith("roadmap.")
        assert not name.startswith("dashboard.")
        assert not name.endswith("task-state.json")
    readme = (PIPELINE / "README.md").read_text(encoding="utf-8")
    assert "`TASKS.md` is the only live task tracker" in readme
    assert "ChatGPT owns prompts, audit criteria, audit results, and lifecycle state" in readme
    assert "Codex owns scoped implementation, tests, and child builder logs" in readme
    assert "preserve evidence only" in readme
    assert "Codex does not author" in readme and "mark itself PASS" in readme
    assert readme.count("Sekiph82/ScrubBots-Level-Factory") == 1
    assert "normal non-force update" in readme
    assert "fetch/prune and" in readme and "divergence checks" in readme
    assert "no reset, automatic rebase" in readme
    assert "Sekiph82/Scrubbots" in readme
    assert "no GitHub API" in readme


def test_active_child_prompts_put_github_sync_before_the_goal() -> None:
    tracker = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    master = (ROOT / ".hiveai/prompts/M11_CP00_003_009_MASTER_IMPLEMENTATION_PROMPT.md").read_text(encoding="utf-8")
    for number in range(3, 10):
        task = f"SB-CP00-{number:03}-C001"
        prompt_match = re.search(rf"- SB-CP00-{number:03} C001 Prompt: `([^`]+)`", tracker)
        assert prompt_match is not None
        prompt_path = ROOT / prompt_match.group(1)
        prompt = prompt_path.read_text(encoding="utf-8")
        first_sync = prompt.casefold().find("first operation")
        goal = prompt.casefold().find("## goal")
        assert 0 <= first_sync < goal
        prefix = prompt[:goal].casefold()
        assert "fetch/prune" in prefix and "origin/main" in prefix and "synchronization" in prefix
        log_match = re.search(rf"- SB-CP00-{number:03} C001 Builder Log Target: `([^`]+)`", tracker)
        assert log_match is not None
        assert log_match.group(1).startswith(".hiveai/codex-logs/")
        assert log_match.group(1).endswith("_CODEX_LOG.md")
    assert master.index("# FIRST TASK") < master.index("# Child 1")
    assert "fetch/prune" in master[:master.index("# Child 1")].casefold()


def test_m11_child_log_paths_are_all_present_distinct_and_canonical() -> None:
    tracker = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    paths: list[str] = []
    for number in range(3, 10):
        task = f"SB-CP00-{number:03}-C001"
        match = re.search(rf"- SB-CP00-{number:03} C001 Builder Log Target: `([^`]+)`", tracker)
        assert match is not None
        paths.append(match.group(1))
    assert len(paths) == 7 and len(set(paths)) == 7
    assert all(path.startswith(".hiveai/codex-logs/") and path.endswith("_CODEX_LOG.md") for path in paths)
    assert len({Path(path).name for path in paths}) == 7


def test_content_pipeline_code_cannot_write_trackers_or_audits() -> None:
    forbidden_imports = {"requests", "httpx", "urllib", "socket", "boto3", "botocore", "github", "github3", "ghapi", "PyGithub", "subprocess"}
    forbidden_calls = {"open", "write_text", "write_bytes", "unlink", "rename", "remove", "mkdir", "post", "put", "patch", "urlopen"}
    for path in PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not {item.name.split(".", 1)[0] for item in node.names} & forbidden_imports
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".", 1)[0] not in forbidden_imports
            elif isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
                assert name not in forbidden_calls


def test_content_pipeline_contains_no_github_credential_or_mutation_automation() -> None:
    candidates = [*PACKAGE.glob("*.py"), *PIPELINE.glob("**/*.json"), PIPELINE / "pyproject.toml"]
    secret_patterns = (
        re.compile(r"(?im)\b(?:api[_-]?key|password|access[_-]?token|refresh[_-]?token|client[_-]?secret|connection[_-]?string)\s*['\"]?\s*[:=]\s*['\"][^'\"\r\n]{8,}['\"]"),
        re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    )
    for path in candidates:
        source = path.read_text(encoding="utf-8")
        assert not any(pattern.search(source) for pattern in secret_patterns)
        assert not re.search(r"(?i)\b(?:GITHUB_TOKEN|github_token)\s*=", source)


def test_receipt_is_fixed_immutable_fact_evidence_without_acceptance_authority() -> None:
    receipt = _valid_receipt()
    assert validate_builder_receipt(receipt).valid
    report = json.loads(serialize_builder_receipt(receipt))
    assert report["task_id"] == receipt.task_id
    assert report["publication_parity"]["result"] == "VERIFIED_EQUAL"
    assert "acceptance" not in report and "accepted" not in report
    assert "status" not in report and "audit_result" not in report
    model_fields = {field.name for field in fields(BuilderPublicationReceipt)}
    assert not model_fields & {"status", "task_status", "audit_result", "acceptance", "accepted", "pass"}
    schema = json.loads((PIPELINE / "schemas/v1/builder-publication-receipt.schema.json").read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert not set(schema["properties"]) & {"status", "task_status", "audit_result", "acceptance", "accepted", "pass"}


@pytest.mark.parametrize(
    ("replacement", "reason"),
    (
        ({"repository_name": "Scrubbots"}, ReceiptReasonCode.INVALID_IDENTITY),
        ({"branch": "feature/other"}, ReceiptReasonCode.INVALID_IDENTITY),
        ({"prompt_path": ".hiveai/prompts/../../TASKS.md"}, ReceiptReasonCode.INVALID_PATH),
        ({"final_sha": "not-a-sha"}, ReceiptReasonCode.INVALID_SHA),
        ({"publication_parity": PublicationParity(ParityResult.VERIFIED_EQUAL, "a" * 40, "b" * 40, 1, 0)}, ReceiptReasonCode.INVALID_PARITY_FACTS),
        ({"test_summary": BuilderTestSummary(-1, 0, 0, 1, 0, 0, 0, 0)}, ReceiptReasonCode.INVALID_TEST_FACTS),
    ),
)
def test_receipt_validation_rejects_noncanonical_or_inconsistent_facts(replacement: dict[str, object], reason: ReceiptReasonCode) -> None:
    receipt = replace(_valid_receipt(), **replacement)
    result = validate_builder_receipt(receipt)
    assert not result.valid and result.reason_code is reason
    with pytest.raises(ValueError, match="invalid builder publication receipt"):
        serialize_builder_receipt(receipt)


def test_receipt_schema_cannot_represent_secrets_or_mutable_task_state() -> None:
    schema = json.loads((PIPELINE / "schemas/v1/builder-publication-receipt.schema.json").read_text(encoding="utf-8"))
    forbidden = {"api_key", "password", "access_token", "secret_value", "task_status", "audit_status", "acceptance", "accepted"}
    def keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return {str(key) for key in value} | set().union(*(keys(item) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(keys(item) for item in value)) if value else set()
        return set()
    assert not keys(schema) & forbidden
