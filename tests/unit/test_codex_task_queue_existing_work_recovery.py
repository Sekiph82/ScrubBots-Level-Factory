"""Owner-authorized in-place recovery: dirty task files cannot strand the goal.

The read-only queue still verifies canonical checkout/GitHub authority; only
the previous unconditional refusal of unrelated tracked edits is optional.
These mocks never touch the user's checkout or filesystem.
"""
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

from scripts.codex import scrubbots_task_queue as queue


def _git_for(root: Path, tracked_status: str):
    def fake(root_arg: Path, *args: str, check: bool = True):
        assert root_arg == root
        mapping = {
            ("rev-parse", "--show-toplevel"): (str(root), 0),
            ("remote", "get-url", "origin"): ("https://github.com/Sekiph82/ScrubBots-Level-Factory.git", 0),
            ("branch", "--show-current"): ("main", 0),
            ("rev-parse", "--verify", "origin/main"): ("abc123", 0),
            ("merge-base", "--is-ancestor", "origin/main", "HEAD"): ("", 0),
            ("status", "--porcelain=v1", "--untracked-files=no"): (tracked_status, 0),
        }
        out, rc = mapping[args]
        return CompletedProcess(args, rc, stdout=out, stderr="")

    return fake


def _check_checkout(tracked_status: str, *, recover: bool):
    root = Path.cwd().resolve()
    with (
        patch.object(queue, "CANONICAL_ROOT", root),
        patch.object(queue, "_run_git", side_effect=_git_for(root, tracked_status)),
        patch.object(queue, "fetch_origin"),
    ):
        return queue.validate_checkout(root, allow_existing_work=recover)


def test_recovery_mode_preserves_and_reports_existing_tracked_edits():
    entries = " M src/scrubbots_pixel_factory/alpix_batch.py\n M src/scrubbots_pixel_factory/studio_lifecycle.py"
    assert _check_checkout(entries, recover=True) == entries.splitlines()


def test_strict_mode_still_refuses_tracked_edits():
    with pytest.raises(ValueError, match="Tracked working-tree changes exist"):
        _check_checkout(" M level_factory/scripts/factory_studio_exact_ui.gd", recover=False)


def test_both_modes_accept_clean_checkout():
    assert _check_checkout("", recover=False) == []
    assert _check_checkout("", recover=True) == []


def test_active_task_and_prompt_mismatch_are_not_waived_by_recovery_mode():
    # The separate source authority guard remains intact on recovery runs.
    root = Path.cwd().resolve()
    with patch.object(queue, "_run_git") as git:
        git.side_effect = [
            CompletedProcess([], 0, stdout="aaaa\n", stderr=""),
            CompletedProcess([], 0, stdout="bbbb\n", stderr=""),
        ]
        with pytest.raises(ValueError, match="differs from authoritative origin/main"):
            queue.validate_file_matches_origin(root, "TASKS.md")
