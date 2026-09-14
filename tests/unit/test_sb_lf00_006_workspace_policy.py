"""Offline tests for the SB-LF00-006 workspace and ignore policy."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
POLICY_FILE = REPOSITORY_ROOT / "docs" / "FACTORY_WORKSPACE_AND_EXCLUSIONS.md"


def _check_ignored(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", "--", path],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _changed_files() -> tuple[Path, ...]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = [REPOSITORY_ROOT / line for line in result.stdout.splitlines() if line]
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths.extend(
        REPOSITORY_ROOT / line for line in untracked.stdout.splitlines() if line
    )
    return tuple(path for path in paths if path.is_file())


def test_workspace_policy_exists_and_classifies_all_required_surfaces() -> None:
    assert POLICY_FILE.is_file()
    text = POLICY_FILE.read_text(encoding="utf-8").lower()
    for phrase in (
        "tracked source",
        "durable audit/review/reference evidence",
        "generated output",
        "candidate/transient output",
        "cache/temp state",
        "local runtime logs",
        "local-only secrets",
    ):
        assert phrase in text


def test_policy_preserves_durable_evidence_distinct_from_generated_output() -> None:
    text = " ".join(POLICY_FILE.read_text(encoding="utf-8").lower().split())
    assert "`review/` is durable tracked evidence" in text
    assert "not equivalent to generated" in text
    assert "`.hiveai/codex-logs/` is tracked builder evidence" in text
    assert "ordinary runtime `logs/` is ignored" in text
    assert "`data/` and `exemplars/` remain source/evidence surfaces, not disposable caches" in text
    assert "root `tasks.md` remains the sole live task ledger" in text
    assert "no credential is required to be stored in git" in text


def test_generated_markers_and_cache_boundaries_use_gitignore_semantics() -> None:
    ignored = (
        "output/generated/sample.png",
        "output/candidates/candidate.json",
        "level_factory/output/export.zip",
        "level_factory/.godot/editor/cache",
        ".venv/Scripts/python.exe",
        "__pycache__/module.pyc",
        ".pytest_cache/v/cache/nodeids",
        ".mypy_cache/state",
        ".ruff_cache/state",
        "build/artifact.whl",
        "dist/package.whl",
        ".coverage",
        ".wfc-cache/state.bin",
        "wfc-cache/state.bin",
        "tmp/work.bin",
        "temp/work.bin",
        "logs/runtime.log",
        "runtime.log",
    )
    for path in ignored:
        assert _check_ignored(path), path

    trackable_markers = ("output/.gitkeep", "level_factory/output/.gitkeep")
    for path in trackable_markers:
        assert not _check_ignored(path), path


def test_secret_locations_are_ignored_without_extension_wide_rules() -> None:
    ignored = (
        ".env",
        ".env.local",
        ".env.production",
        ".secrets/provider.toml",
        "secrets/session.data",
        "level_factory/.secrets/local.toml",
        "level_factory/secrets/oauth.data",
    )
    for path in ignored:
        assert _check_ignored(path), path

    gitignore = (REPOSITORY_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "*.json" not in gitignore
    assert "*.md" not in gitignore
    assert "*.png" not in gitignore
    assert "*.key" not in gitignore
    assert "*.pem" not in gitignore


def test_durable_source_and_evidence_paths_are_not_ignored() -> None:
    visible = (
        "review/m03/example.json",
        "data/palette/example.json",
        "exemplars/inbox/example.json",
        "docs/example.md",
        ".hiveai/audits/example.md",
        ".hiveai/prompts/example.md",
        ".hiveai/codex-logs/example.md",
        "level_factory/project.godot",
        "TASKS.md",
    )
    for path in visible:
        assert not _check_ignored(path), path


def test_no_secret_literal_or_real_secret_fixture_was_added() -> None:
    suspicious_literal = re.compile(
        r"(?i)(?:-----begin [^-]+ private key-----|(?:sk|pk|rk)-[a-z0-9_-]{20,}|"
        r"(?:api[_-]?key|token|password|secret|credential)\s*=\s*[^\s#]{12,})"
    )
    for path in _changed_files():
        text = path.read_text(encoding="utf-8", errors="strict")
        assert suspicious_literal.search(text) is None, path


def test_root_tracker_is_not_ignored_and_no_policy_tracker_is_created() -> None:
    assert not _check_ignored("TASKS.md")
    text = POLICY_FILE.read_text(encoding="utf-8").lower()
    assert "cleanup scheduler" in text
    assert "task tracker" in text
    assert "secret manager" in text
    assert "operational control plane" in text
