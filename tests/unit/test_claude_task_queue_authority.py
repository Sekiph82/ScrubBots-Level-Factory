"""2026-11-10 owner handoff: Claude can be the sole active TASKS operator.

The legacy queue script remains read-only and continues to parse old Codex receipts.
"""
from pathlib import Path

import pytest

from scripts.codex.scrubbots_task_queue import select_current_task


PROMPT = (
    "https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/"
    ".hiveai/prompts/SB_LFX_OWNER_CLAUDE_AUTONOMOUS_RECOVERY_PIXEL_ART_BATCH_MISMATCH_20261110.md"
)


def _tracker(actor: str) -> str:
    return (
        "# ScrubBots Factory\n"
        "## Project Status\n"
        f"- Current Task: Fix PixelLab batch. Active prompt: {PROMPT}\n"
        f"- Next Task/Action: Fix PixelLab batch. Active prompt: {PROMPT}\n"
        "- Current Task Status: IN_PROGRESS\n"
        f"- Required Actor: {actor}\n"
        "- Tracking Repository: Sekiph82/ScrubBots-Level-Factory\n"
        "- Tracking Branch: main\n"
        "## Tasks\n"
    )


def test_claude_can_be_the_only_active_executor():
    task = select_current_task(_tracker("CLAUDE"))
    assert task.required_actor == "CLAUDE"
    assert task.prompt_url == PROMPT


def test_existing_codex_receipts_remain_compatible():
    assert select_current_task(_tracker("CODEX")).required_actor == "CODEX"


def test_chatgpt_cannot_become_primary_executor():
    with pytest.raises(ValueError, match="Required Actor"):
        select_current_task(_tracker("CHATGPT"))


def test_canonical_tracker_names_claude():
    project = Path(__file__).resolve().parents[2]
    current = select_current_task((project / "TASKS.md").read_text(encoding="utf-8"))
    assert current.required_actor == "CLAUDE"
    assert current.prompt_url == PROMPT
