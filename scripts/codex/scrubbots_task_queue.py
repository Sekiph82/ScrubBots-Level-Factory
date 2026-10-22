"""Read and validate ScrubBots Level Factory's explicit current task.

This adapter is deliberately read-only. It never claims, edits, or publishes
TASKS.md and never scans checkbox rows to guess which task should run.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

REPOSITORY = "Sekiph82/ScrubBots-Level-Factory"
TRACKING_BRANCH = "main"
CANONICAL_ROOT = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
PROMPT_URL = re.compile(
    r"https://github\.com/Sekiph82/ScrubBots-Level-Factory/blob/main/"
    r"\.hiveai/prompts/[A-Za-z0-9_.-]+\.md"
)
PROMPT_PATH = re.compile(r"\.hiveai/prompts/[A-Za-z0-9_.-]+\.md")


@dataclass(frozen=True)
class CurrentTask:
    repository: str
    branch: str
    current_task: str
    next_task_action: str
    status: str
    required_actor: str
    prompt_url: str
    prompt_path: str


def _project_status(source: str) -> dict[str, str]:
    lines = source.splitlines()
    headings = [index for index, line in enumerate(lines) if line == "## Project Status"]
    if len(headings) != 1:
        raise ValueError("TASKS.md must contain exactly one ## Project Status section")
    end = next(
        (index for index in range(headings[0] + 1, len(lines)) if lines[index].startswith("## ") or lines[index].startswith("# ")),
        len(lines),
    )
    fields: dict[str, list[str]] = {}
    for line in lines[headings[0] + 1 : end]:
        match = re.fullmatch(r"- ([A-Za-z][A-Za-z /-]*?):\s*(.+)", line)
        if match:
            fields.setdefault(match.group(1), []).append(match.group(2).strip())
            continue
        action = re.fullmatch(r"- Next Task/Action(?:\s+\[[^\]]+\])?:\s*(.+)", line)
        if action:
            fields.setdefault("Next Task/Action", []).append(action.group(1).strip())
    required = (
        "Current Task",
        "Current Task Status",
        "Next Task/Action",
        "Required Actor",
        "Tracking Repository",
        "Tracking Branch",
    )
    result: dict[str, str] = {}
    for name in required:
        values = fields.get(name, [])
        if len(values) != 1:
            raise ValueError(f"Project Status field {name!r} must appear exactly once")
        result[name] = values[0]
    return result


def select_current_task(source: str) -> CurrentTask:
    fields = _project_status(source)
    if fields["Tracking Repository"].rstrip("/").removesuffix(".git") != REPOSITORY:
        raise ValueError("Tracking Repository must be Sekiph82/ScrubBots-Level-Factory")
    if fields["Tracking Branch"] != TRACKING_BRANCH:
        raise ValueError("Tracking Branch must be main")
    if not fields["Required Actor"].startswith("CODEX"):
        raise ValueError("Required Actor must authorize CODEX")

    current = fields["Current Task"]
    actions = fields["Next Task/Action"]
    urls = PROMPT_URL.findall(current)
    action_urls = PROMPT_URL.findall(actions)
    if len(urls) != 1 or len(action_urls) != 1 or urls[0] != action_urls[0]:
        raise ValueError("Current Task and Next Task/Action must name the same exact main-branch prompt URL")
    if urls[0].count("?") or "#" in urls[0]:
        raise ValueError("Prompt URL must not contain a query or fragment")

    prompt_file = PROMPT_PATH.search(urls[0])
    assert prompt_file is not None
    status = fields["Current Task Status"]
    if not status:
        raise ValueError("Current Task Status must not be blank")
    return CurrentTask(
        repository=REPOSITORY,
        branch=TRACKING_BRANCH,
        current_task=current,
        next_task_action=actions,
        status=status,
        required_actor=fields["Required Actor"],
        prompt_url=urls[0],
        prompt_path=prompt_file.group(0),
    )


def validate_checkout(root: Path) -> None:
    root = root.resolve()
    if root != CANONICAL_ROOT.resolve():
        raise ValueError(f"task execution is limited to the canonical checkout: {CANONICAL_ROOT}")

    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            raise ValueError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
        return result.stdout.strip()

    actual_root = Path(git("rev-parse", "--show-toplevel")).resolve()
    if actual_root != root:
        raise ValueError("--root must be the Git repository root")
    origin = git("remote", "get-url", "origin").rstrip("/")
    if origin.removesuffix(".git") != f"https://github.com/{REPOSITORY}":
        raise ValueError("origin must be https://github.com/Sekiph82/ScrubBots-Level-Factory.git")
    if not git("branch", "--show-current"):
        raise ValueError("Detached HEAD is not an allowed task execution state")
    git("rev-parse", "--verify", "origin/main")
    ancestry = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", "origin/main", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if ancestry.returncode != 0:
        raise ValueError("HEAD is behind or diverged from origin/main; safe fast-forward sync is required")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Tracked working-tree changes exist; refusing to start an automated task")


def validate_tracked_prompt(root: Path, prompt_path: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(root.resolve()), "ls-files", "--error-unmatch", "--", prompt_path],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0 or result.stdout.strip() != prompt_path:
        raise ValueError(f"authoritative prompt is not tracked at HEAD: {prompt_path}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json", action="store_true", help="Print the validated task envelope as JSON")
    args = parser.parse_args(argv)
    try:
        validate_checkout(args.root)
        task = select_current_task((args.root / "TASKS.md").read_text(encoding="utf-8"))
        if not (args.root / task.prompt_path).is_file():
            raise ValueError(f"Authoritative prompt is missing from this checkout: {task.prompt_path}")
        validate_tracked_prompt(args.root, task.prompt_path)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(asdict(task), ensure_ascii=False, sort_keys=True))
    else:
        print(f"Current task validated; prompt={task.prompt_path}; status={task.status}")
        print("Read-only mode: TASKS.md was not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
