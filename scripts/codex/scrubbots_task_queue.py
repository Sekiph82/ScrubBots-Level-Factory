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
FETCH_TIMEOUT_SECONDS = 30
LOCAL_GIT_TIMEOUT_SECONDS = 10
PROMPT_URL = re.compile(
    r"https://github\.com/Sekiph82/ScrubBots-Level-Factory/blob/main/"
    r"\.hiveai/prompts/[A-Za-z0-9_.-]+\.md"
)
PROMPT_TOKEN = re.compile(
    r"https://github\.com/Sekiph82/ScrubBots-Level-Factory/blob/main/"
    r"\.hiveai/prompts/\S+"
)
PROMPT_PATH = re.compile(r"\.hiveai/prompts/[A-Za-z0-9_.-]+\.md")


def _prompt_urls(text: str) -> list[str]:
    return [match.group(0).rstrip(".,;)]}") for match in PROMPT_TOKEN.finditer(text)]


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


@dataclass(frozen=True)
class AuthorityPins:
    head_sha: str
    origin_main_sha: str
    tasks_blob_sha: str
    prompt_blob_sha: str


def _run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = ["git", "-C", str(root.resolve()), *args]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=LOCAL_GIT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError(
            f"git {' '.join(args)} exceeded {LOCAL_GIT_TIMEOUT_SECONDS}s; refusing incomplete task validation"
        ) from error
    if check and result.returncode != 0:
        raise ValueError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


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
    actor_chain = [
        actor.strip()
        for actor in re.split(
            r"\s*(?:,\s*(?:THEN\s+)?|\bTHEN\s+)\s*",
            fields["Required Actor"].strip(),
        )
    ]
    if (
        not actor_chain
        or actor_chain[0] != "CODEX"
        or any(actor not in {"CODEX", "CHATGPT", "OWNER"} for actor in actor_chain)
        or len(set(actor_chain)) != len(actor_chain)
    ):
        raise ValueError("Required Actor must authorize CODEX")

    current = fields["Current Task"]
    actions = fields["Next Task/Action"]
    urls = _prompt_urls(current)
    action_urls = _prompt_urls(actions)
    if (
        len(urls) != 1
        or len(action_urls) != 1
        or urls[0] != action_urls[0]
        or PROMPT_URL.fullmatch(urls[0]) is None
    ):
        raise ValueError("Current Task and Next Task/Action must name the same exact main-branch prompt URL")

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
        return _run_git(root, *args).stdout.strip()

    actual_root = Path(git("rev-parse", "--show-toplevel")).resolve()
    if actual_root != root:
        raise ValueError("--root must be the Git repository root")
    origin = git("remote", "get-url", "origin").rstrip("/")
    if origin.removesuffix(".git") != f"https://github.com/{REPOSITORY}":
        raise ValueError("origin must be https://github.com/Sekiph82/ScrubBots-Level-Factory.git")
    if not git("branch", "--show-current"):
        raise ValueError("Detached HEAD is not an allowed task execution state")
    fetch_origin(root)
    git("rev-parse", "--verify", "origin/main")
    ancestry = _run_git(root, "merge-base", "--is-ancestor", "origin/main", "HEAD", check=False)
    if ancestry.returncode != 0:
        raise ValueError("HEAD is behind or diverged from origin/main; safe fast-forward sync is required")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Tracked working-tree changes exist; refusing to start an automated task")


def fetch_origin(root: Path) -> None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root.resolve()), "fetch", "--prune", "origin"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=FETCH_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError(
            f"git fetch --prune origin exceeded {FETCH_TIMEOUT_SECONDS}s; refusing stale task authority"
        ) from error
    if result.returncode != 0:
        detail = result.stderr.strip()
        raise ValueError(f"git fetch --prune origin failed; refusing stale task authority{': ' + detail if detail else ''}")


def validate_tracked_prompt(root: Path, prompt_path: str) -> None:
    result = _run_git(root, "ls-files", "--error-unmatch", "--", prompt_path, check=False)
    if result.returncode != 0 or result.stdout.strip() != prompt_path:
        raise ValueError(f"authoritative prompt is not tracked at HEAD: {prompt_path}")


def validate_file_matches_origin(root: Path, relative_path: str) -> None:
    root = root.resolve()
    remote = _run_git(root, "rev-parse", f"origin/main:{relative_path}", check=False)
    local = _run_git(root, "hash-object", f"--path={relative_path}", "--", relative_path, check=False)
    if remote.returncode != 0 or local.returncode != 0:
        raise ValueError(f"cannot verify {relative_path} against origin/main")
    if remote.stdout.strip() != local.stdout.strip():
        raise ValueError(f"{relative_path} differs from authoritative origin/main")


def authority_pins(root: Path, prompt_path: str) -> AuthorityPins:
    root = root.resolve()

    def git(*args: str) -> str:
        try:
            return _run_git(root, *args).stdout.strip()
        except ValueError as error:
            raise ValueError(f"cannot pin task authority with git {' '.join(args)}: {error}") from error

    return AuthorityPins(
        head_sha=git("rev-parse", "HEAD"),
        origin_main_sha=git("rev-parse", "origin/main"),
        tasks_blob_sha=git("rev-parse", "origin/main:TASKS.md"),
        prompt_blob_sha=git("rev-parse", f"origin/main:{prompt_path}"),
    )


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
        validate_file_matches_origin(args.root, "TASKS.md")
        validate_file_matches_origin(args.root, task.prompt_path)
        pins = authority_pins(args.root, task.prompt_path)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps({**asdict(task), **asdict(pins)}, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Current task validated; prompt={task.prompt_path}; status={task.status}")
        print("Read-only mode: TASKS.md was not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
