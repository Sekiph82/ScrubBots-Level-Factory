from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.codex.scrubbots_task_queue import (
    select_current_task,
    fetch_origin,
    validate_file_matches_origin,
    validate_tracked_prompt,
)


PROMPT = (
    "https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/"
    ".hiveai/prompts/SB_LFX_018_R05_V13_CD_R08_CONDITIONAL_NATIVE_GODOT_PARSE_ONLY.md"
)


def tracker(*, repository: str = "Sekiph82/ScrubBots-Level-Factory", branch: str = "main", prompt: str = PROMPT) -> str:
    return f"""# ScrubBots Level Factory

## Project Status
- Next Task/Action [2026-10-22 R08]: Run only the explicit task. Prompt: {prompt}
- Current Milestone: SB-LFX-018 R05 V13-C/D
- Current Sprint: R08
- Current Task: Execute R08. Authoritative prompt: {prompt}
- Current Task Status: READY
- Required Actor: CODEX, THEN CHATGPT
- Tracking Repository: {repository}
- Tracking Branch: {branch}

## Tasks
- [ ] SB-LFX-018 — unrelated checkbox ledger row
"""


class ScrubBotsTaskQueueTests(unittest.TestCase):
    def test_selects_only_the_explicit_current_task_and_exact_prompt(self) -> None:
        selected = select_current_task(tracker())
        self.assertEqual(selected.prompt_path, ".hiveai/prompts/SB_LFX_018_R05_V13_CD_R08_CONDITIONAL_NATIVE_GODOT_PARSE_ONLY.md")
        self.assertEqual(selected.branch, "main")
        self.assertEqual(selected.status, "READY")

    def test_rejects_wrong_repository_or_branch(self) -> None:
        for source in (tracker(repository="github.com/Sekiph82/ScrubBots-Level-Factory"), tracker(branch="work")):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    select_current_task(source)

    def test_rejects_mismatched_or_ambiguous_prompt(self) -> None:
        other = PROMPT.replace("R08_", "R09_")
        with self.assertRaisesRegex(ValueError, "same exact"):
            select_current_task(tracker().replace(f"Run only the explicit task. Prompt: {PROMPT}", f"Run only the explicit task. Prompt: {other}"))
        with self.assertRaisesRegex(ValueError, "same exact"):
            select_current_task(tracker(prompt=PROMPT + " and " + PROMPT))

    def test_rejects_duplicate_status_sections_and_non_codex_actor(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one"):
            select_current_task(tracker() + "\n## Project Status\n")
        with self.assertRaisesRegex(ValueError, "authorize CODEX"):
            select_current_task(tracker().replace("CODEX, THEN CHATGPT", "OWNER"))

    def test_tracked_prompt_guard_accepts_exact_git_path(self) -> None:
        result = type("Result", (), {"returncode": 0, "stdout": PROMPT.split("/blob/main/")[1] + "\n"})()
        with patch("scripts.codex.scrubbots_task_queue.subprocess.run", return_value=result):
            validate_tracked_prompt(Path("."), PROMPT.split("/blob/main/")[1])

    def test_tracked_prompt_guard_rejects_untracked_prompt(self) -> None:
        result = type("Result", (), {"returncode": 1, "stdout": ""})()
        with patch("scripts.codex.scrubbots_task_queue.subprocess.run", return_value=result):
            with self.assertRaisesRegex(ValueError, "not tracked"):
                validate_tracked_prompt(Path("."), PROMPT.split("/blob/main/")[1])

    def test_authority_file_guard_accepts_origin_blob_match(self) -> None:
        blob = "a" * 40
        result = type("Result", (), {"returncode": 0, "stdout": blob + "\n"})()
        with patch(
            "scripts.codex.scrubbots_task_queue.subprocess.run",
            side_effect=(result, result),
        ):
            validate_file_matches_origin(Path("."), "TASKS.md")

    def test_authority_file_guard_rejects_local_drift(self) -> None:
        remote = type("Result", (), {"returncode": 0, "stdout": "a" * 40})()
        local = type("Result", (), {"returncode": 0, "stdout": "b" * 40})()
        with patch(
            "scripts.codex.scrubbots_task_queue.subprocess.run",
            side_effect=(remote, local),
        ):
            with self.assertRaisesRegex(ValueError, "differs from authoritative origin/main"):
                validate_file_matches_origin(Path("."), "TASKS.md")

    def test_fetch_guard_accepts_successful_fetch(self) -> None:
        result = type("Result", (), {"returncode": 0, "stderr": ""})()
        with patch("scripts.codex.scrubbots_task_queue.subprocess.run", return_value=result) as run:
            fetch_origin(Path("."))
        self.assertEqual(run.call_args.args[0][-3:], ["fetch", "--prune", "origin"])

    def test_fetch_guard_fails_closed_on_network_error(self) -> None:
        result = type("Result", (), {"returncode": 128, "stderr": "network unavailable"})()
        with patch("scripts.codex.scrubbots_task_queue.subprocess.run", return_value=result):
            with self.assertRaisesRegex(ValueError, "refusing stale task authority"):
                fetch_origin(Path("."))


if __name__ == "__main__":
    unittest.main()
