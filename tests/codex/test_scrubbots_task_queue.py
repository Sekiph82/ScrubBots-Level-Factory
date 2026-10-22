from __future__ import annotations

import unittest

from scripts.codex.scrubbots_task_queue import select_current_task


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


if __name__ == "__main__":
    unittest.main()
