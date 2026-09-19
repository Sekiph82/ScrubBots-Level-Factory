from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from scrubbots_pixel_factory.output import read_bundle


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
README = FACTORY / "README.md"
RUNTIME_SUITE = FACTORY / "tests" / "factory_studio_runtime_suite.gd"
LAUNCHER = FACTORY / "scripts" / "factory_core_launcher.py"
STUDIO_PASS_MARKER = "SB-LF06-002-C001-R01 committed runtime suite PASS"


def _run_godot_studio_smoke() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "godot",
            "--headless",
            "--path",
            "level_factory",
            "--script",
            "res://tests/factory_studio_runtime_suite.gd",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _run_core(*arguments: str) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        [sys.executable, str(LAUNCHER), *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def _bundle_files(root: Path) -> list[Path]:
    return sorted(
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    )


def test_lf06_012_gate_runs_real_studio_smoke_and_canonical_core_reproduction() -> None:
    studio = _run_godot_studio_smoke()
    studio_output = studio.stdout + studio.stderr
    assert studio.returncode == 0, studio_output
    assert STUDIO_PASS_MARKER in studio_output, studio_output
    assert "Parse Error" not in studio_output
    assert "SCRIPT ERROR" not in studio_output
    assert "No such file or directory" not in studio_output

    temporary_root = Path(tempfile.mkdtemp(prefix="scrubbots_lf06_012_core_smoke_"))
    try:
        generated_root = temporary_root / "generated"
        reproduced_root = temporary_root / "reproduced"
        generated = _run_core(
            "generate",
            "--difficulty",
            "MEDIUM",
            "--mode",
            "RULES",
            "--width",
            "20",
            "--height",
            "21",
            "--seed",
            "12012",
            "--candidate-id",
            "lf06-012-core-smoke",
            "--output",
            str(generated_root),
        )
        assert generated.returncode == 0, generated.stderr
        assert "SUCCESS candidate_id=" in generated.stdout
        metadata_paths = list(generated_root.rglob("metadata.json"))
        assert len(metadata_paths) == 1
        metadata_path = metadata_paths[0]
        source_bundle_root = metadata_path.parent

        source_bundle = read_bundle(source_bundle_root)
        request = source_bundle.metadata["generation"]["request"]
        assert request["schema"] == "scrubbots-generation-request"
        assert request["schema_version"] in (1, 2)
        assert request["width"] == 20
        assert request["height"] == 21
        assert request["seed"] == {"type": "int", "value": 12012}
        assert source_bundle.artwork.width == 20
        assert source_bundle.artwork.height == 21
        assert source_bundle.artwork.cells

        reproduced = _run_core(
            "reproduce",
            str(metadata_path),
            "--output",
            str(reproduced_root),
        )
        assert reproduced.returncode == 0, reproduced.stderr
        assert "MATCH" in reproduced.stdout
        reproduced_metadata_paths = list(reproduced_root.rglob("metadata.json"))
        assert len(reproduced_metadata_paths) == 1
        reproduced_bundle = read_bundle(reproduced_metadata_paths[0].parent)
        assert source_bundle.metadata_json == reproduced_bundle.metadata_json
        assert source_bundle.artwork_json == reproduced_bundle.artwork_json
        assert source_bundle.artwork_png == reproduced_bundle.artwork_png
        assert source_bundle.preview_png == reproduced_bundle.preview_png
        assert _bundle_files(generated_root) == _bundle_files(reproduced_root)
        assert all(
            (generated_root / relative).read_bytes()
            == (reproduced_root / relative).read_bytes()
            for relative in _bundle_files(generated_root)
        )
    finally:
        shutil.rmtree(temporary_root, ignore_errors=False)
    assert not temporary_root.exists()


def test_lf06_012_readme_documents_the_current_offline_smoke_gate() -> None:
    text = " ".join(README.read_text(encoding="utf-8").split())
    required = (
        "contains committed Godot-local smoke and integration tests",
        "root Python test suite remains canonical for Factory Core semantics",
        "python -m pytest -q tests/unit/test_sb_lf06_012_factory_studio_editor_smoke_and_headless_core_test_gate.py",
        "godot --headless --path level_factory --quit",
        "python -m pytest -q",
        "without GUI interaction, provider/network access, or credentials",
    )
    assert all(phrase in text for phrase in required)


def test_lf06_012_gate_has_no_provider_or_credential_dependency() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (FACTORY / "project.godot", RUNTIME_SUITE, LAUNCHER)
    ).lower()
    for forbidden in ("http://", "https://", "api_key", "credential", "magnific", "pixellab"):
        assert forbidden not in source
    assert RUNTIME_SUITE.is_file()
    assert LAUNCHER.is_file()
