"""R09-R02-R03 installed Studio solver-budget contract checks (no native run)."""

from __future__ import annotations

import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = Path(os.environ.get("SCRUBBOTS_FACTORY_RUNTIME_ROOT", REPOSITORY_ROOT)).resolve()
sys.path.insert(0, str(RUNTIME_ROOT / "src"))

from scrubbots_pixel_factory import studio_extensions  # noqa: E402
from scrubbots_pixel_factory.supply_pipeline import game_rules, scrubbots_solver, solver_budget, supply_exporter, supply_optimizer, verify  # noqa: E402
from scrubbots_pixel_factory.supply_pipeline.solver_budget import normalize_solver_budget  # noqa: E402


PINNED_SOURCE_ID = "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
PINNED_SOURCE_SHA = PINNED_SOURCE_ID.removeprefix("owner-upload-")
PINNED_GAME_COMMIT = "aef60a616d4ac401e9dfac15df6fe56e671c0053"


class StudioSolverContractTests(unittest.TestCase):
    def test_budget_normalizer_is_strict_and_bounded(self) -> None:
        self.assertEqual(normalize_solver_budget(25_000, 90), (25_000, 90.0))
        self.assertEqual(normalize_solver_budget(25_000, 240), (25_000, 240.0))
        self.assertEqual(normalize_solver_budget(1, 0.25), (1, 0.25))
        invalid = (
            (None, 90), (0, 90), (25_001, 90), (True, 90), ("25000", 90),
            (25_000, None), (25_000, 0), (25_000, 240.01), (25_000, True),
            (25_000, "90"), (25_000, float("inf")), (25_000, float("nan")),
        )
        for visits, timeout in invalid:
            with self.subTest(visits=visits, timeout=timeout):
                with self.assertRaises(ValueError):
                    normalize_solver_budget(visits, timeout)

    def test_actual_release_authority_and_source_are_read_only(self) -> None:
        owner_dir = RUNTIME_ROOT / "level_factory" / "output" / "owner-uploads" / PINNED_SOURCE_ID
        pin_root = RUNTIME_ROOT / "level_factory" / "output" / "current-game-runtime" / PINNED_GAME_COMMIT
        source_path = owner_dir / "source.png"
        record_path = owner_dir / "source.json"
        before = {
            source_path: hashlib.sha256(source_path.read_bytes()).hexdigest(),
            record_path: hashlib.sha256(record_path.read_bytes()).hexdigest(),
        }
        self.assertEqual(before[source_path], PINNED_SOURCE_SHA)
        for columns in (3, 4, 5):
            rules = game_rules.GameRules(pin_root, column_count=columns)
            self.assertEqual(rules.column_count, columns)
            self.assertEqual(rules.attestation["source_commit"], PINNED_GAME_COMMIT)
        validation = studio_extensions.validate_owner_source(
            PINNED_SOURCE_ID,
            persist=False,
            game_project=pin_root,
            source_directory=owner_dir,
        )
        self.assertEqual(validation["source_sha256"], PINNED_SOURCE_SHA)
        self.assertTrue(validation["exact_logical_source"])
        self.assertEqual(validation["original_dimensions"], {"width": 32, "height": 32})
        self.assertEqual(validation["void_capability"]["state"], "OPEN")
        self.assertEqual(validation["structural"]["disposition"], "PASS")
        self.assertEqual(validation["alpha"], {"transparent_count": 288, "semi_alpha_count": 0, "opaque_count": 736})
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in before}
        self.assertEqual(after, before)

    def test_actual_runtime_modules_match_tracked_files_and_signatures(self) -> None:
        modules = {
            "src/scrubbots_pixel_factory/studio_extensions.py": studio_extensions,
            "src/scrubbots_pixel_factory/supply_pipeline/supply_optimizer.py": supply_optimizer,
            "src/scrubbots_pixel_factory/supply_pipeline/scrubbots_solver.py": scrubbots_solver,
            "src/scrubbots_pixel_factory/supply_pipeline/solver_budget.py": solver_budget,
            "src/scrubbots_pixel_factory/supply_pipeline/verify.py": verify,
        }
        for relative, module in modules.items():
            runtime_file = Path(module.__file__).resolve()
            self.assertTrue(runtime_file.is_relative_to(RUNTIME_ROOT.resolve()), str(runtime_file))
            tracked_file = REPOSITORY_ROOT / relative
            self.assertEqual(hashlib.sha256(runtime_file.read_bytes()).digest(), hashlib.sha256(tracked_file.read_bytes()).digest())
        optimizer_parameters = inspect.signature(supply_optimizer.SupplyOptimizer.run_grid).parameters
        self.assertIn("real_timeout_seconds", optimizer_parameters)
        self.assertNotIn("real_timeout", optimizer_parameters)
        self.assertIn("real_max_visited", optimizer_parameters)
        self.assertIn("max_native_solver_invocations", optimizer_parameters)
        solver_parameters = inspect.signature(scrubbots_solver.ScrubBotsSolver.run).parameters
        self.assertIn("max_visited", solver_parameters)
        self.assertIn("timeout", solver_parameters)
        verify_parameters = inspect.signature(verify.verify_exported_supply).parameters
        self.assertIn("max_visited", verify_parameters)
        self.assertIn("timeout_seconds", verify_parameters)

    def test_production_route_binds_bounded_primary_and_load_check_without_native(self) -> None:
        real_run_grid = supply_optimizer.SupplyOptimizer.run_grid
        real_verify = verify.verify_exported_supply
        captured: list[tuple[int, dict[str, object], dict[str, object]]] = []

        class PinnedRules:
            def __init__(self, _project: object, *, column_count: int) -> None:
                self.column_count = column_count
                self.attestation = {"source_commit": PINNED_GAME_COMMIT}

        class NoNativeOptimizer:
            def __init__(self, rules: PinnedRules) -> None:
                self.rules = rules

            def run_grid(self, grid: object, used: object, **kwargs: object) -> dict[str, object]:
                inspect.signature(real_run_grid).bind(self, grid, used, **kwargs)
                captured.append((self.rules.column_count, dict(kwargs), {}))
                return {
                    "solver_status": "NOT_RUN",
                    "solution_final": "NOT_AVAILABLE",
                    "difficulty": None,
                    "difficulty_basis": "NOT_AVAILABLE",
                }

        class NoNativeExporter:
            def __init__(self, _rules: PinnedRules) -> None:
                pass

            def export(self, _result: object, _output: object, _level_id: str) -> dict[str, str]:
                return {"level": "stub-level.json", "supply_plan": "stub-plan.json", "result": "stub-result.json"}

        def no_native_load_check(level: str, plan: str, project: object, *, max_visited: int, timeout_seconds: float) -> dict[str, str]:
            inspect.signature(real_verify).bind(level, plan, project, max_visited=max_visited, timeout_seconds=timeout_seconds)
            column_count, primary, _ = captured[-1]
            captured[-1] = (column_count, primary, {"max_visited": max_visited, "timeout_seconds": timeout_seconds})
            return {"state": "ERROR", "disposition": "ERROR", "reason": "TEST_STUB_NO_NATIVE_LOAD_CHECK"}

        for columns in (3, 4, 5):
            with self.subTest(columns=columns):
                captured.clear()
                with (
                    patch.object(game_rules, "GameRules", PinnedRules),
                    patch.object(supply_optimizer, "SupplyOptimizer", NoNativeOptimizer),
                    patch.object(supply_exporter, "SupplyExporter", NoNativeExporter),
                    patch.object(verify, "verify_exported_supply", no_native_load_check),
                    patch.object(studio_extensions, "_canonical_cells_to_grid", return_value=([0], {0})),
                    patch.object(studio_extensions, "_pipeline_path", return_value=Path("stub-pipeline.json")),
                    patch.object(studio_extensions, "_write_json"),
                ):
                    payload = studio_extensions._run_canonical_artwork_route(
                        identity=PINNED_SOURCE_ID,
                        cells=["C04"],
                        width=32,
                        height=32,
                        evidence="owner-002-source-record",
                        request={
                            "column_count": columns,
                            "game_project": str(RUNTIME_ROOT / "level_factory" / "output" / "current-game-runtime" / PINNED_GAME_COMMIT),
                            "real_max_visited": 25_000,
                            "solver_timeout_seconds": 240,
                        },
                        source_kind="OWNER_UPLOAD",
                    )
                self.assertEqual(payload["disposition"], "UNAVAILABLE")
                self.assertIn("TEST_STUB_NO_NATIVE_LOAD_CHECK", payload["primary"]["reason"])
                self.assertEqual(len(captured), 1)
                actual_columns, primary_kwargs, load_kwargs = captured[0]
                self.assertEqual(actual_columns, columns)
                self.assertEqual(primary_kwargs["real_max_visited"], 25_000)
                self.assertEqual(primary_kwargs["real_timeout_seconds"], 240)
                self.assertEqual(primary_kwargs["max_native_solver_invocations"], 1)
                self.assertIs(primary_kwargs["auto_extend_solver_timeout"], True)
                self.assertNotIn("real_timeout", primary_kwargs)
                self.assertEqual(load_kwargs, {"max_visited": 25_000, "timeout_seconds": 240})

    def test_invalid_pinned_budgets_stop_before_optimizer_or_load_check(self) -> None:
        class PinnedRules:
            def __init__(self, _project: object, *, column_count: int) -> None:
                self.column_count = column_count
                self.attestation = {"source_commit": PINNED_GAME_COMMIT}

        for visits, timeout in ((None, 90), (0, 90), (25_001, 90), (25_000, None), (25_000, 90), (25_000, 241), (25_000, 480), (25_000, "240")):
            with self.subTest(visits=visits, timeout=timeout):
                native_boundary_calls: list[str] = []

                class MustNotRunOptimizer:
                    def __init__(self, _rules: object) -> None:
                        native_boundary_calls.append("optimizer-created")

                    def run_grid(self, *_args: object, **_kwargs: object) -> dict[str, object]:
                        native_boundary_calls.append("optimizer-run")
                        raise AssertionError("native solver boundary must not be reached")

                with (
                    patch.object(game_rules, "GameRules", PinnedRules),
                    patch.object(supply_optimizer, "SupplyOptimizer", MustNotRunOptimizer),
                    patch.object(studio_extensions, "_canonical_cells_to_grid", return_value=([0], {0})),
                    patch.object(studio_extensions, "_pipeline_path", return_value=Path("stub-pipeline.json")),
                    patch.object(studio_extensions, "_write_json"),
                ):
                    payload = studio_extensions._run_canonical_artwork_route(
                        identity=PINNED_SOURCE_ID,
                        cells=["C04"],
                        width=32,
                        height=32,
                        evidence="owner-002-source-record",
                        request={
                            "column_count": 4,
                            "game_project": str(RUNTIME_ROOT / "level_factory" / "output" / "current-game-runtime" / PINNED_GAME_COMMIT),
                            "real_max_visited": visits,
                            "solver_timeout_seconds": timeout,
                        },
                        source_kind="OWNER_UPLOAD",
                    )
                self.assertEqual(payload["disposition"], "UNAVAILABLE")
                self.assertIn("invalid pinned solver budget", payload["primary"]["reason"])
                self.assertEqual(native_boundary_calls, [])

    def test_shipping_verifier_rejects_bad_pinned_budget_before_godot(self) -> None:
        class PinnedRules:
            attestation = {"source_commit": PINNED_GAME_COMMIT}

        level = {"version": 1, "id": "stub-level", "cells": [0], "palette": ["#FF0000"]}
        plan = {
            "schema": "scrubbots.level_supply_plan.v1",
            "version": 1,
            "levelId": "stub-level",
            "columnCount": 4,
            "visiblePreviewDepth": 3,
            "maxRobotsPerBatch": 1,
            "columns": [[{"cid": "C01", "robots": 1}] for _ in range(4)],
        }

        def read_stub(path: Path, encoding: str = "utf-8") -> str:
            del encoding
            return json.dumps(level if path.name == "level.json" else plan)

        for visits, timeout in ((None, 90), (0, 90), (25_001, 90), (25_000, None), (25_000, 241)):
            with self.subTest(visits=visits, timeout=timeout):
                with (
                    patch.object(Path, "read_text", read_stub),
                    patch.object(verify, "GameRules", return_value=PinnedRules()),
                    patch.object(verify, "find_godot") as find_godot,
                    patch.object(verify.ScrubBotsSolver, "run") as solver_run,
                ):
                    result = verify.verify_exported_supply(
                        "level.json", "plan.json", "pinned-root", max_visited=visits, timeout_seconds=timeout
                    )
                self.assertEqual(result["disposition"], "ERROR")
                self.assertIn("invalid solver budget", result["reason"])
                find_godot.assert_not_called()
                solver_run.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
