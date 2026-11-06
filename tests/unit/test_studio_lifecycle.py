"""Bounded in-memory checks for Factory Studio worker shutdown signals."""

from __future__ import annotations

import ast
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


class StudioGodotCallSiteTests(unittest.TestCase):
    def test_studio_godot_call_sites_use_shutdown_aware_process_runner(self) -> None:
        root = Path(__file__).resolve().parents[2]
        targets = (
            ("src/scrubbots_pixel_factory/canonical_bridge.py", "CanonicalHeadlessBridge", "invoke"),
            ("src/scrubbots_pixel_factory/canonical_bridge.py", "CanonicalHeadlessBridge", "_verify"),
            ("src/scrubbots_pixel_factory/supply_pipeline/real_play_gate.py", None, "_preflight"),
            ("src/scrubbots_pixel_factory/supply_pipeline/real_play_gate.py", None, "_invoke"),
            ("src/scrubbots_pixel_factory/supply_pipeline/release_pool.py", None, "_pinned_profile_from_godot"),
            ("src/scrubbots_pixel_factory/supply_pipeline/game_publisher.py", None, "_validate_proposed_catalog"),
            ("src/scrubbots_pixel_factory/supply_pipeline/release_route_a.py", None, "_verify_game"),
            ("src/scrubbots_pixel_factory/supply_pipeline/release_route_a.py", None, "_run"),
        )

        for relative, class_name, function_name in targets:
            with self.subTest(module=relative, function=function_name):
                tree = ast.parse((root / relative).read_text(encoding="utf-8"))
                if class_name is None:
                    function = next(node for node in ast.walk(tree)
                                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                                    and node.name == function_name)
                else:
                    class_node = next(node for node in tree.body
                                      if isinstance(node, ast.ClassDef) and node.name == class_name)
                    function = next(node for node in class_node.body
                                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                                    and node.name == function_name)

                calls = []
                for node in ast.walk(function):
                    if not isinstance(node, ast.Call):
                        continue
                    parts = []
                    current = node.func
                    while isinstance(current, ast.Attribute):
                        parts.append(current.attr)
                        current = current.value
                    if isinstance(current, ast.Name):
                        parts.append(current.id)
                    calls.append(".".join(reversed(parts)))

                self.assertIn("run_studio_child_interruptibly", calls)
                self.assertNotIn("subprocess.run", calls)

    def test_level_factory_activity_panel_is_screen_scoped(self) -> None:
        root = Path(__file__).resolve().parents[2]
        source = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
        helper = source.split("func _sync_pipeline_activity_visibility() -> void:", 1)[1].split("\n\n", 1)[0]

        self.assertIn("_activity_panel.visible = _screen == \"LEVEL FACTORY\"", helper)
        self.assertEqual(source.count("_activity_panel.visible ="), 3)
        self.assertIn("_sync_pipeline_activity_visibility()", source.split("func _update_live_chrome() -> void:", 1)[1].split("\n\n", 1)[0])

if __name__ == "__main__":
    unittest.main(verbosity=2)
