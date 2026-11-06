"""Bounded in-memory checks for Factory Studio worker shutdown signals."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from scrubbots_pixel_factory.studio_lifecycle import (  # noqa: E402
    StudioShutdownRequested,
    run_studio_child_interruptibly,
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


class InterruptibleStudioChildTests(unittest.TestCase):
    def test_shutdown_stops_only_the_child_started_by_helper(self) -> None:
        process = Mock()
        process.pid = 9876
        process.poll.return_value = None
        process.communicate.side_effect = [subprocess.TimeoutExpired(["child"], 0.25), ("", "")]
        with patch("scrubbots_pixel_factory.studio_lifecycle.studio_shutdown_requested", side_effect=[False, False, True]):
            with patch("scrubbots_pixel_factory.studio_lifecycle.subprocess.Popen", return_value=process) as popen:
                with patch("scrubbots_pixel_factory.studio_lifecycle.terminate_studio_child_tree") as terminate:
                    with self.assertRaises(StudioShutdownRequested):
                        run_studio_child_interruptibly(["child"])
        popen.assert_called_once()
        terminate.assert_called_once_with(process)
        self.assertEqual(process.communicate.call_args_list[0].kwargs, {"timeout": 0.25})
        self.assertEqual(process.communicate.call_args_list[1].kwargs, {"timeout": 2})

    def test_shutdown_before_start_does_not_spawn_a_child(self) -> None:
        with patch("scrubbots_pixel_factory.studio_lifecycle.studio_shutdown_requested", return_value=True):
            with patch("scrubbots_pixel_factory.studio_lifecycle.subprocess.Popen") as popen:
                with self.assertRaises(StudioShutdownRequested):
                    run_studio_child_interruptibly(["child"])
        popen.assert_not_called()

    def test_successful_child_returns_captured_result(self) -> None:
        process = Mock()
        process.returncode = 3
        process.communicate.return_value = ("stdout", "stderr")
        with patch("scrubbots_pixel_factory.studio_lifecycle.studio_shutdown_requested", return_value=False):
            with patch("scrubbots_pixel_factory.studio_lifecycle.subprocess.Popen", return_value=process):
                result = run_studio_child_interruptibly(["child"])
        self.assertEqual((result.returncode, result.stdout, result.stderr), (3, "stdout", "stderr"))

    def test_live_child_exits_when_shutdown_is_signalled(self) -> None:
        shutdown = threading.Event()
        started: list[subprocess.Popen[str]] = []
        real_popen = subprocess.Popen

        def observed_popen(*args: object, **kwargs: object) -> subprocess.Popen[str]:
            process = real_popen(*args, **kwargs)
            command = args[0] if args else kwargs.get("args")
            if isinstance(command, (list, tuple)) and command[:1] == [sys.executable]:
                started.append(process)
            return process

        timer = threading.Timer(0.4, shutdown.set)
        timer.start()
        try:
            with patch("scrubbots_pixel_factory.studio_lifecycle.studio_shutdown_requested", side_effect=shutdown.is_set):
                with patch("scrubbots_pixel_factory.studio_lifecycle.subprocess.Popen", side_effect=observed_popen):
                    with self.assertRaises(StudioShutdownRequested):
                        run_studio_child_interruptibly([sys.executable, "-c", "import time; time.sleep(60)"])
        finally:
            timer.cancel()
        self.assertEqual(len(started), 1)
        self.assertIsNotNone(started[0].poll(), "the Studio-owned child remained alive after shutdown")

if __name__ == "__main__":
    unittest.main(verbosity=2)
