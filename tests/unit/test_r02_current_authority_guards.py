from __future__ import annotations

import ast
from pathlib import Path

import scrubbots_pixel_factory as factory


ROOT = Path(__file__).parents[2]
RETIRED = {
    "baseline_search", "canonical_bridge", "compact_solver_state", "difficulty_analysis",
    "legal_move_provider", "level_metrics", "search_policy", "simulation_boundary",
    "solution_analysis", "solver_budget", "solver_evidence", "telemetry_calibration",
    "visited_memoization",
}
CURRENT_PATHS = [ROOT / "src/scrubbots_pixel_factory/cli/main.py", ROOT / "src/scrubbots_pixel_factory/studio_extensions.py", *sorted((ROOT / "src/scrubbots_pixel_factory/supply_pipeline").glob("*.py"))]
LEGACY_FILES = [ROOT / "src/scrubbots_pixel_factory" / f"{name}.py" for name in RETIRED]


def test_current_cli_studio_and_zip_pipeline_do_not_import_retired_authorities():
    forbidden = {f"scrubbots_pixel_factory.{name}" for name in RETIRED}
    for path in CURRENT_PATHS:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            imported = []
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                imported = [f"{base}.{alias.name}" if base else alias.name for alias in node.names]
                imported.append(base)
            assert not (forbidden & set(imported)), f"{path.relative_to(ROOT)} imports retired production authority: {forbidden & set(imported)}"


def test_retired_root_exports_are_absent_and_retained_modules_are_marked_legacy():
    for name in ("CompactSolverState", "SimulationRequest", "TelemetryCalibration"):
        assert not hasattr(factory, name)
    for path in LEGACY_FILES:
        assert path.is_file()
        text = path.read_text(encoding="utf-8")[:2048]
        assert "LEGACY_NON_PRODUCTION" in text or "LEGACY / NON-PRODUCTION" in text, path.name
