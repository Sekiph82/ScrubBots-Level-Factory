"""Offline governance and H!veAI TASKS-only authority contract tests."""

from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TASKS_FILE = REPOSITORY_ROOT / "TASKS.md"
TASK_ROW_RE = re.compile(r"^\s*-\s*\[([ x~!])\]\s+(.*?)\s*$")
TASK_ID_RE = re.compile(r"\b(?:SB-[A-Z0-9]+-\d{3}|PAG-SP\d+)\b")
TAG_RE = re.compile(r"\[([A-Z][A-Z0-9_]*)\]")
PROJECT_STATUS_LABELS = (
    "Current Milestone:",
    "Current Sprint:",
    "Current Task:",
    "Current Task Status:",
    "Next Task/Action:",
    "Required Actor:",
)
NORMALIZATION_BASE_REF = "1952657cfa1832d90f4e077e67f4b6a2917b8861"
NORMALIZATION_IMPLEMENTATION_REF = "dd3311ef8ef35ac88f1d12b91b5f306e2408bed4"
EXPECTED_NORMALIZATION_STATE_COUNTS = Counter({"x": 30, "~": 1, " ": 196, "!": 0})
EXPECTED_NORMALIZATION_METADATA_COUNTS = Counter(
    {"MIGRATION": 6, "PARTIAL": 52, "GAME_RUNTIME": 28, "EXTENSION": 3}
)
LEGACY_TRACKER_FILES = (
    ".hiveai/PROJECT.json",
    ".hiveai/RULES.md",
    ".hiveai/TASKS.md",
    ".hiveai/STATE.json",
    ".hiveai/HANDOFF.md",
    ".hiveai/EVENTS.jsonl",
    ".hiveai/PROJECT_DASHBOARD.md",
    ".hiveai/ACTIVE_CYCLES.md",
    ".hiveai/ARTIFACT_MAP.md",
    ".hiveai/PROGRESS_SNAPSHOT.md",
    ".hiveai/CYCLE_INDEX.md",
    "tasks.md",
)
GOVERNANCE_DOCS = (
    REPOSITORY_ROOT / "README.md",
    REPOSITORY_ROOT / "GOVERNANCE.md",
    REPOSITORY_ROOT / "AGENTS.md",
    REPOSITORY_ROOT / "CLAUDE.md",
)


def _git_lines(*args: str) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return tuple(line for line in result.stdout.splitlines() if line)


def _git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def _effective_tracked_paths() -> set[str]:
    tracked = set(_git_lines("ls-files"))
    deleted = set(_git_lines("diff", "--name-only", "--diff-filter=D"))
    return tracked - deleted


def _exact_relative_exists(relative: str) -> bool:
    current = REPOSITORY_ROOT
    for component in relative.replace("\\", "/").split("/"):
        matches = [child for child in current.iterdir() if child.name == component]
        if not matches:
            return False
        current = matches[0]
    return True


def _parse_rows(text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        match = TASK_ROW_RE.match(line)
        if match is None:
            continue
        state = match.group(1)
        body = match.group(2)
        before, title = body.split(" — ", 1)
        identifier = TASK_ID_RE.search(before)
        assert identifier is not None, (line_number, line)
        prefix_tags = TAG_RE.findall(before[: identifier.start()])
        suffix_tags = TAG_RE.findall(title)
        title_core = re.sub(r"(?:\s+\[[A-Z][A-Z0-9_]*\])+\s*$", "", title)
        rows.append(
            {
                "state": state,
                "id": identifier.group(0),
                "title": title_core.rstrip(),
                "prefix_tags": tuple(prefix_tags),
                "suffix_tags": tuple(suffix_tags),
                "all_tags": tuple(prefix_tags + suffix_tags),
            }
        )
    return rows


def _historical_tasks_text(ref: str) -> str:
    return _git_text("show", f"{ref}:TASKS.md")


def test_root_tracker_and_legacy_control_plane_boundaries() -> None:
    assert TASKS_FILE.is_file()
    effective = _effective_tracked_paths()
    assert "TASKS.md" in effective
    assert "tasks.md" not in effective
    assert all(path not in effective and not _exact_relative_exists(path) for path in LEGACY_TRACKER_FILES)
    hiveai_entries = {path.name for path in (REPOSITORY_ROOT / ".hiveai").iterdir()}
    assert hiveai_entries <= {"audit-criteria", "audits", "codex-logs", "prompts"}


def test_governance_docs_use_tasks_only_authority_and_evidence_archives() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in GOVERNANCE_DOCS).lower()
    assert text.count("root `tasks.md`") >= 1
    assert "sole project-management tracker" in text
    assert "prompts/" in text and "codex-logs/" in text and "audits/" in text
    assert "process/evidence archives" in text or "not tracker inputs" in text
    for stale in ("`.hiveai/rules.md`", "`.hiveai/project.json`", "`.hiveai/tasks.md`", "`.hiveai/events.jsonl`"):
        assert stale not in text
    assert "tasks.md` is the canonical task ledger" not in text
    readme = " ".join(GOVERNANCE_DOCS[0].read_text(encoding="utf-8").lower().split())
    for phrase in (
        "canonical scrubbots level factory + content platform",
        "root `tasks.md` is the sole project-management tracker",
        "h!veai task tracking requires no other repository file",
        "python factory core",
        "independently openable `level_factory/` godot shell",
        "main-game runtime belongs in `sekiph82/scrubbots` only when separately authorized",
    ):
        assert phrase in readme


def test_historical_normalization_is_parser_safe_and_preserved_exactly() -> None:
    before_text = _historical_tasks_text(NORMALIZATION_BASE_REF)
    normalized_text = _historical_tasks_text(NORMALIZATION_IMPLEMENTATION_REF)
    before = _parse_rows(before_text)
    normalized = _parse_rows(normalized_text)

    assert len(before) == len(normalized) == 227
    assert Counter(row["state"] for row in before) == EXPECTED_NORMALIZATION_STATE_COUNTS
    assert Counter(row["id"] for row in before) == Counter(row["id"] for row in normalized)
    assert len({row["id"] for row in normalized}) == 227
    assert Counter(tag for row in before for tag in row["all_tags"]) == EXPECTED_NORMALIZATION_METADATA_COUNTS
    assert Counter(tag for row in normalized for tag in row["all_tags"]) == EXPECTED_NORMALIZATION_METADATA_COUNTS
    assert all(not row["prefix_tags"] for row in normalized)
    assert [row["state"] for row in before] == [row["state"] for row in normalized]
    assert [row["id"] for row in before] == [row["id"] for row in normalized]
    assert [row["title"] for row in before] == [row["title"] for row in normalized]
    assert [row["all_tags"] for row in before] == [row["all_tags"] for row in normalized]

    before_lines = before_text.splitlines()
    normalized_lines = normalized_text.splitlines()
    assert len(before_lines) == len(normalized_lines)
    for before_line, normalized_line in zip(before_lines, normalized_lines):
        if TASK_ROW_RE.match(before_line):
            assert TASK_ROW_RE.match(normalized_line)
        else:
            assert before_line == normalized_line


def test_current_tasks_rows_are_parser_safe_and_declared_denominator_matches() -> None:
    current_text = TASKS_FILE.read_text(encoding="utf-8")
    rows = _parse_rows(current_text)
    assert rows
    assert all(not row["prefix_tags"] for row in rows)
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))
    declared = re.search(r"Unified live task denominator:\s+\*\*(\d+)\*\*", current_text)
    assert declared is not None
    assert int(declared.group(1)) == len(rows)
    assert "canonical live source-requirement denominator is exactly 224" in current_text


def test_project_status_and_active_task_contract_are_exact() -> None:
    current = TASKS_FILE.read_text(encoding="utf-8")
    for label in PROJECT_STATUS_LABELS:
        assert any(line.startswith(f"- {label}") for line in current.splitlines())
    active = [row for row in _parse_rows(current) if row["state"] == "~"]
    current_task = re.search(r"(?m)^- Current Task:\s+([A-Z0-9]+(?:-[A-Z0-9]+)+)\s+—", current)
    assert current_task is not None
    assert current_task.group(1) == "SB-LF07-001"
    status = re.search(r"(?m)^- Current Task Status:\s+(.+)$", current)
    assert status is not None and status.group(1).strip() == "CHANGES_REQUIRED / R02_AUTHORIZED / REMEDIATE_ALL_THEN_REAUDIT"
    assert [row["id"] for row in active] == ["SB-LF07-001"]


def test_level_factory_governance_defers_to_root_without_second_tracker() -> None:
    text = (REPOSITORY_ROOT / "level_factory" / "GOVERNANCE.md").read_text(
        encoding="utf-8"
    ).lower()
    assert "root `tasks.md`" in text
    assert "does not create a competing" in text
    assert "tracker" in text
    assert "does not create a competing h!veai control plane" in text


def test_sb_lf00_007_historical_diff_contains_no_product_implementation_change() -> None:
    changed = set(
        _git_lines(
            "diff",
            "--name-only",
            NORMALIZATION_BASE_REF,
            NORMALIZATION_IMPLEMENTATION_REF,
        )
    )
    forbidden = {
        path
        for path in changed
        if path.startswith("src/")
        or path.startswith("level_factory/scripts/")
        or path.startswith("level_factory/scenes/")
        or path == "level_factory/project.godot"
    }
    assert not forbidden
