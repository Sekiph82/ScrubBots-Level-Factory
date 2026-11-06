"""Bounded in-memory checks for Factory Studio worker shutdown signals."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from scrubbots_pixel_factory.studio_lifecycle import (  # noqa: E402
    studio_shutdown_requested,
    terminate_studio_child_tree,
)


class StudioShutdownSignalTests(unittest.TestCase):
    def test_cancel_marker_stops_worker(self) -> None:
        with patch.dict(os.environ, {"SCRUBBOTS_FACTORY_STUDIO_CANCEL_FILE": "cancel.flag"}, clear=True):
            with patch.object(Path, "read_text", return_value="CANCEL_NOW\n"):
                self.assertTrue(studio_shutdown_requested())

    def test_missing_marker_and_live_parent_keep_worker_running(self) -> None:
        with patch.dict(os.environ, {
            "SCRUBBOTS_FACTORY_STUDIO_CANCEL_FILE": "missing.flag",
            "SCRUBBOTS_FACTORY_STUDIO_PID": "1234",
        }, clear=True):
            with patch.object(Path, "read_text", side_effect=FileNotFoundError):
                with patch("scrubbots_pixel_factory.studio_lifecycle._owner_process_is_alive", return_value=True):
                    self.assertFalse(studio_shutdown_requested())

    def test_dead_parent_stops_worker(self) -> None:
        with patch.dict(os.environ, {"SCRUBBOTS_FACTORY_STUDIO_PID": "1234"}, clear=True):
            with patch("scrubbots_pixel_factory.studio_lifecycle._owner_process_is_alive", return_value=False):
                self.assertTrue(studio_shutdown_requested())

    def test_unreadable_marker_fails_closed(self) -> None:
        with patch.dict(os.environ, {"SCRUBBOTS_FACTORY_STUDIO_CANCEL_FILE": "cancel.flag"}, clear=True):
            with patch.object(Path, "read_text", side_effect=UnicodeError):
                self.assertTrue(studio_shutdown_requested())


class StudioChildTreeTerminationTests(unittest.TestCase):
    def test_windows_termination_targets_only_held_child_pid_tree(self) -> None:
        process = Mock()
        process.pid = 4321
        process.poll.return_value = None
        process.wait.return_value = 0
        with patch("scrubbots_pixel_factory.studio_lifecycle.os.name", "nt"):
            with patch.object(Path, "is_file", return_value=True):
                with patch("scrubbots_pixel_factory.studio_lifecycle.subprocess.run") as run:
                    terminate_studio_child_tree(process)
        self.assertEqual(run.call_args.args[0][1:], ["/PID", "4321", "/T", "/F"])
        process.wait.assert_called_once_with(timeout=5)
        process.kill.assert_not_called()

    def test_already_exited_child_is_not_signalled(self) -> None:
        process = Mock(spec=subprocess.Popen)
        process.pid = 4321
        process.poll.return_value = 0
        with patch("scrubbots_pixel_factory.studio_lifecycle.subprocess.run") as run:
            terminate_studio_child_tree(process)
        run.assert_not_called()
        process.kill.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
