from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.codex.scrubbots_task_queue import (
    CANONICAL_ROOT,
    authority_pins,
    validate_checkout,
    fetch_origin,
    validate_file_matches_origin,
    validate_tracked_prompt,
    select_current_task,
    _run_git,
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
    def test_checkout_guard_rejects_noncanonical_root_before_git_calls(self) -> None:
        with patch("scripts.codex.scrubbots_task_queue.subprocess.run") as run:
            with self.assertRaisesRegex(ValueError, "canonical checkout"):
                validate_checkout(Path(r"C:\other\ScrubBots-Level-Factory"))
        run.assert_not_called()

    def test_checkout_guard_rejects_remote_ahead_or_diverged_head_after_fetch(self) -> None:
        root_output = str(CANONICAL_ROOT.resolve())
        responses = (
            subprocess.CompletedProcess([], 0, root_output, ""),
            subprocess.CompletedProcess([], 0, "https://github.com/Sekiph82/ScrubBots-Level-Factory.git", ""),
            subprocess.CompletedProcess([], 0, "codex/task", ""),
            subprocess.CompletedProcess([], 0, "a" * 40, ""),
            subprocess.CompletedProcess([], 1, "", ""),
        )
        with patch("scripts.codex.scrubbots_task_queue.fetch_origin") as fetch, patch(
            "scripts.codex.scrubbots_task_queue._run_git",
            side_effect=responses,
        ):
            with self.assertRaisesRegex(ValueError, "behind or diverged from origin/main"):
                validate_checkout(CANONICAL_ROOT)
        fetch.assert_called_once_with(CANONICAL_ROOT.resolve())

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

    def test_rejects_prompt_query_and_fragment_suffixes(self) -> None:
        for suffix in ("?plain=1", "#readme"):
            with self.subTest(suffix=suffix):
                with self.assertRaisesRegex(ValueError, "same exact"):
                    select_current_task(tracker(prompt=PROMPT + suffix))

    def test_rejects_duplicate_status_sections_and_non_codex_actor(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one"):
            select_current_task(tracker() + "\n## Project Status\n")
        with self.assertRaisesRegex(ValueError, "authorize CODEX"):
            select_current_task(tracker().replace("CODEX, THEN CHATGPT", "OWNER"))
        with self.assertRaisesRegex(ValueError, "authorize CODEX"):
            select_current_task(tracker().replace("CODEX, THEN CHATGPT", "CODEX - NOT AUTHORIZED"))

    def test_rejects_empty_actor_chain_segments(self) -> None:
        for malformed in (
            "CODEX,, CHATGPT",
            "CODEX, , CHATGPT",
            "CODEX THEN THEN CHATGPT",
            "CODEX, CHATGPT, CHATGPT",
        ):
            with self.subTest(actor_chain=malformed):
                with self.assertRaisesRegex(ValueError, "authorize CODEX"):
                    select_current_task(tracker().replace("CODEX, THEN CHATGPT", malformed))

    def test_accepts_comma_and_then_actor_delimiters(self) -> None:
        for actor_chain in ("CODEX, CHATGPT", "CODEX THEN CHATGPT", "CODEX, THEN CHATGPT"):
            with self.subTest(actor_chain=actor_chain):
                self.assertEqual(
                    select_current_task(tracker().replace("CODEX, THEN CHATGPT", actor_chain)).required_actor,
                    actor_chain,
                )

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

    def test_authority_pins_capture_commits_and_exact_task_blobs(self) -> None:
        values = ("1" * 40, "2" * 40, "3" * 40, "4" * 40)
        results = [type("Result", (), {"returncode": 0, "stdout": value + "\n"})() for value in values]
        with patch("scripts.codex.scrubbots_task_queue.subprocess.run", side_effect=results):
            pins = authority_pins(Path("."), PROMPT.split("/blob/main/")[1])
        self.assertEqual(
            (pins.head_sha, pins.origin_main_sha, pins.tasks_blob_sha, pins.prompt_blob_sha),
            values,
        )

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
        self.assertEqual(run.call_args.kwargs["timeout"], 30)

    def test_fetch_guard_fails_closed_on_network_error(self) -> None:
        result = type("Result", (), {"returncode": 128, "stderr": "network unavailable"})()
        with patch("scripts.codex.scrubbots_task_queue.subprocess.run", return_value=result):
            with self.assertRaisesRegex(ValueError, "refusing stale task authority"):
                fetch_origin(Path("."))

    def test_fetch_guard_fails_closed_on_timeout(self) -> None:
        with patch(
            "scripts.codex.scrubbots_task_queue.subprocess.run",
            side_effect=subprocess.TimeoutExpired("git fetch", 30),
        ):
            with self.assertRaisesRegex(ValueError, "exceeded 30s"):
                fetch_origin(Path("."))

    def test_local_git_guard_fails_closed_on_timeout(self) -> None:
        with patch(
            "scripts.codex.scrubbots_task_queue.subprocess.run",
            side_effect=subprocess.TimeoutExpired("git status", 10),
        ) as run:
            with self.assertRaisesRegex(ValueError, "exceeded 10s"):
                _run_git(Path("."), "status", "--porcelain")
        self.assertEqual(run.call_args.kwargs["timeout"], 10)


if __name__ == "__main__":
    unittest.main()
