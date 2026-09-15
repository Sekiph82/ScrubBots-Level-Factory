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
EXPECTED_STATE_COUNTS = Counter({"x": 30, "~": 1, " ": 196, "!": 0})
EXPECTED_METADATA_COUNTS = Counter(
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


def _pre_edit_tasks_text() -> str:
    """Recover the pre-edit blob both before and after the implementation commit."""

    if subprocess.run(
        ["git", "diff", "--quiet", "--", "TASKS.md"],
        cwd=REPOSITORY_ROOT,
        check=False,
    ).returncode != 0:
        return subprocess.run(
            ["git", "show", "HEAD:TASKS.md"],
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
    task_commit = _git_lines("log", "-1", "--format=%H", "--", "TASKS.md")[0]
    return subprocess.run(
        ["git", "show", f"{task_commit}^:TASKS.md"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def test_root_tracker_and_legacy_control_plane_boundaries() -> None:
    assert TASKS_FILE.is_file()
    effective = _effective_tracked_paths()
    assert "TASKS.md" in effective
    assert "tasks.md" not in effective
    assert all(path not in effective and not _exact_relative_exists(path) for path in LEGACY_TRACKER_FILES)
    hiveai_entries = {path.name for path in (REPOSITORY_ROOT / ".hiveai").iterdir()}
    assert hiveai_entries <= {"audits", "codex-logs", "prompts"}


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


def test_tasks_rows_are_parser_safe_and_preserve_pre_edit_inventory() -> None:
    before_text = _pre_edit_tasks_text()
    after_text = TASKS_FILE.read_text(encoding="utf-8")
    before = _parse_rows(before_text)
    after = _parse_rows(after_text)

    assert len(before) == len(after) == 227
    assert Counter(row["state"] for row in before) == EXPECTED_STATE_COUNTS
    assert Counter(row["id"] for row in before) == Counter(row["id"] for row in after)
    assert len({row["id"] for row in after}) == 227
    assert Counter(
        tag
        for row in before
        for tag in row["all_tags"]
    ) == EXPECTED_METADATA_COUNTS
    assert Counter(
        tag
        for row in after
        for tag in row["all_tags"]
    ) == EXPECTED_METADATA_COUNTS
    assert all(not row["prefix_tags"] for row in after)
    assert [row["state"] for row in before] == [row["state"] for row in after]
    assert [row["id"] for row in before] == [row["id"] for row in after]
    assert [row["title"] for row in before] == [row["title"] for row in after]
    assert [row["all_tags"] for row in before] == [row["all_tags"] for row in after]

    before_lines = before_text.splitlines()
    after_lines = after_text.splitlines()
    assert len(before_lines) == len(after_lines)
    for before_line, after_line in zip(before_lines, after_lines):
        if TASK_ROW_RE.match(before_line):
            assert TASK_ROW_RE.match(after_line)
        else:
            assert before_line == after_line


def test_project_status_and_active_task_contract_are_unchanged_and_exact() -> None:
    before = _pre_edit_tasks_text()
    after = TASKS_FILE.read_text(encoding="utf-8")
    for label in PROJECT_STATUS_LABELS:
        before_line = next(line for line in before.splitlines() if line.startswith(f"- {label}"))
        after_line = next(line for line in after.splitlines() if line.startswith(f"- {label}"))
        assert before_line == after_line
    active = [row for row in _parse_rows(after) if row["state"] == "~"]
    assert len(active) == 1
    current_task = re.search(r"(?m)^- Current Task:\s+(SB-[A-Z0-9]+-\d{3})\s+—", after)
    assert current_task is not None
    assert current_task.group(1) == active[0]["id"] == "SB-LF00-007"
    assert "canonical live source-requirement denominator is exactly 224" in after
    assert "Unified live task denominator: **227**" in after


def test_level_factory_governance_defers_to_root_without_second_tracker() -> None:
    text = (REPOSITORY_ROOT / "level_factory" / "GOVERNANCE.md").read_text(
        encoding="utf-8"
    ).lower()
    assert "root `tasks.md`" in text
    assert "does not create a competing" in text
    assert "tracker" in text
    assert "does not create a competing h!veai control plane" in text


def test_no_product_python_or_godot_implementation_changed() -> None:
    changed = set(_git_lines("diff", "--name-only", "HEAD"))
    forbidden = {
        path
        for path in changed
        if path.startswith("src/")
        or Path(path).suffix.lower() in {".py", ".gd", ".tscn", ".godot"}
    }
    assert not forbidden
