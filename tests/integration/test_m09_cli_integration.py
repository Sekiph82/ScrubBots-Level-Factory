from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from scrubbots_pixel_factory import DeterministicRNG, GenerationRequest, GeneratorOptions, GenerationResult, GeneratorMode, RNG_ALGORITHM, offline_runtime
from scrubbots_pixel_factory.cli import main as cli_main
from scrubbots_pixel_factory.generators.router import GeneratorRouter

cli_module = importlib.import_module("scrubbots_pixel_factory.cli.main")


ROOT = Path(__file__).parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "wfc" / "wfc-synthetic-easy-3.json"


def _run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    command_env = dict(os.environ, PYTHONPATH="src")
    if env:
        command_env.update(env)
    return subprocess.run([sys.executable, "-m", "scrubbots_pixel_factory.cli", *args], cwd=ROOT, env=command_env, text=True, capture_output=True)


def test_single_generate_reproduce_and_invalid_request_are_windows_module_friendly(tmp_path: Path) -> None:
    generated = _run("generate", "--difficulty", "EASY", "--mode", "RULES", "--width", "20", "--height", "21", "--seed", "77", "--output", str(tmp_path))
    assert generated.returncode == 0, generated.stderr
    metadata = next(tmp_path.rglob("metadata.json"))
    reproduced = _run("reproduce", str(metadata))
    assert reproduced.returncode == 0 and "MATCH" in reproduced.stdout
    invalid = _run("generate", "--difficulty", "EASY", "--mode", "RULES", "--width", "19", "--height", "20", "--seed", "77", "--output", str(tmp_path / "bad"))
    assert invalid.returncode != 0
    assert "Traceback" not in invalid.stderr


def test_reproduce_uses_recorded_request_and_rejects_tampered_bundle(tmp_path: Path) -> None:
    generated = _run("generate", "--difficulty", "EASY", "--mode", "MASK", "--width", "20", "--height", "20", "--seed", "81", "--output", str(tmp_path))
    assert generated.returncode == 0
    metadata = next(tmp_path.rglob("metadata.json"))
    value = json.loads(metadata.read_text(encoding="utf-8"))
    value["generation"]["request"]["seed"]["value"] = 82
    metadata.write_text(json.dumps(value), encoding="utf-8")
    reproduced = _run("reproduce", str(metadata))
    assert reproduced.returncode != 0
    assert "Traceback" not in reproduced.stderr


def test_wfc_generation_and_reproduction_require_the_matching_local_exemplar(tmp_path: Path) -> None:
    generated = _run("generate", "--difficulty", "EASY", "--mode", "WFC", "--width", "20", "--height", "20", "--style", "wfc-synthetic-easy-3", "--palette", "C01,C02,C03", "--seed", "41", "--exemplar-json", str(FIXTURE), "--output", str(tmp_path))
    assert generated.returncode == 0, generated.stderr
    metadata = next(tmp_path.rglob("metadata.json"))
    missing = _run("reproduce", str(metadata))
    wrong = _run("reproduce", str(metadata), "--exemplar-json", str(ROOT / "tests" / "fixtures" / "wfc" / "wfc-synthetic-medium-6.json"))
    matching = _run("reproduce", str(metadata), "--exemplar-json", str(FIXTURE))
    assert missing.returncode != 0 and wrong.returncode != 0
    assert matching.returncode == 0 and "MATCH" in matching.stdout
    assert "Traceback" not in missing.stderr + wrong.stderr


def test_batch_manifest_and_completed_resume_are_byte_stable(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first = _run("batch", "--difficulty", "EASY", "--count", "2", "--mode", "MASK", "--seed", "1000", "--max-attempts", "4", "--width", "20", "--height", "20", "--output", str(first_root))
    second = _run("batch", "--difficulty", "EASY", "--count", "2", "--mode", "MASK", "--seed", "1000", "--max-attempts", "4", "--width", "20", "--height", "20", "--output", str(second_root))
    assert first.returncode == second.returncode == 0, (first.stderr, second.stderr)
    first_manifest = first_root / "batch-manifest.json"
    second_manifest = second_root / "batch-manifest.json"
    assert first_manifest.read_bytes() == second_manifest.read_bytes()
    first_files = sorted(path.relative_to(first_root).as_posix() for path in first_root.rglob("*") if path.is_file())
    second_files = sorted(path.relative_to(second_root).as_posix() for path in second_root.rglob("*") if path.is_file())
    assert first_files == second_files
    for relative in first_files:
        assert (first_root / relative).read_bytes() == (second_root / relative).read_bytes()
    before = first_manifest.read_bytes()
    resumed = _run("batch", "--resume", str(first_manifest))
    assert resumed.returncode == 0 and "COMPLETE" in resumed.stdout
    assert first_manifest.read_bytes() == before


def test_interrupted_batch_resume_converges_to_uninterrupted_bytes(tmp_path: Path, monkeypatch) -> None:
    interrupted_root = tmp_path / "interrupted"
    clean_root = tmp_path / "clean"
    original_write = cli_module._atomic_manifest_write
    writes = {"count": 0}

    def interrupt_after_first_attempt(path, value):
        original_write(path, value)
        writes["count"] += 1
        if writes["count"] == 2:
            raise KeyboardInterrupt

    monkeypatch.setattr(cli_module, "_atomic_manifest_write", interrupt_after_first_attempt)
    with pytest.raises(KeyboardInterrupt):
        cli_main(["batch", "--difficulty", "EASY", "--count", "2", "--mode", "MASK", "--seed", "1000", "--max-attempts", "4", "--width", "20", "--height", "20", "--output", str(interrupted_root)])
    monkeypatch.setattr(cli_module, "_atomic_manifest_write", original_write)
    resumed = cli_main(["batch", "--resume", str(interrupted_root / "batch-manifest.json")])
    assert resumed == 0
    clean = _run("batch", "--difficulty", "EASY", "--count", "2", "--mode", "MASK", "--seed", "1000", "--max-attempts", "4", "--width", "20", "--height", "20", "--output", str(clean_root))
    assert clean.returncode == 0, clean.stderr
    files = sorted(path.relative_to(interrupted_root).as_posix() for path in interrupted_root.rglob("*") if path.is_file())
    clean_files = sorted(path.relative_to(clean_root).as_posix() for path in clean_root.rglob("*") if path.is_file())
    assert files == clean_files
    for relative in files:
        assert (interrupted_root / relative).read_bytes() == (clean_root / relative).read_bytes()


def test_batch_requires_explicit_finite_configuration(tmp_path: Path) -> None:
    missing_seed = _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--max-attempts", "1", "--output", str(tmp_path / "missing"))
    missing_bound = _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--seed", "1", "--output", str(tmp_path / "bound"))
    assert missing_seed.returncode != 0 and missing_bound.returncode != 0
    assert "Traceback" not in missing_seed.stderr + missing_bound.stderr


def test_batch_generator_failure_is_distinct_and_bounded(tmp_path: Path) -> None:
    exhausted = _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "WFC", "--seed", "9", "--max-attempts", "1", "--width", "20", "--height", "20", "--output", str(tmp_path))
    assert exhausted.returncode == 7
    manifest = json.loads((tmp_path / "batch-manifest.json").read_text(encoding="utf-8"))
    assert manifest["terminal_state"] == "EXHAUSTED"
    assert manifest["attempts"][0]["status"] == "GENERATOR_FAILURE"
    assert manifest["attempts"][0]["failure_code"]


def test_batch_duplicate_record_is_exact_and_does_not_mutate_grid(tmp_path: Path, monkeypatch) -> None:
    cells = tuple(color for color, rows in (("C01", 10), ("C02", 5), ("C03", 5)) for _ in range(rows * 20))

    class ConstantRouter:
        def generate_candidate(self, request):
            return GenerationResult.success(
                request=request, width=20, height=20, logical_grid=cells,
                generator_mode=GeneratorMode.MASK.value, generator_id="test-mask", generator_version="1.0.0",
                seed=request.seed, rng_algorithm=RNG_ALGORITHM, provenance={"stage_seeds": DeterministicRNG(request.seed).stage_seeds(), "retry_seeds": {"0": DeterministicRNG(request.seed).retry_seed(0)}},
            )

    monkeypatch.setattr(cli_module, "_router", lambda registry: ConstantRouter())
    assert cli_main(["batch", "--difficulty", "EASY", "--count", "2", "--mode", "MASK", "--seed", "9", "--max-attempts", "2", "--width", "20", "--height", "20", "--output", str(tmp_path)]) == 7
    manifest = json.loads((tmp_path / "batch-manifest.json").read_text(encoding="utf-8"))
    assert manifest["attempts"][0]["status"] == "ACCEPTED"
    assert manifest["attempts"][1]["status"] == "DUPLICATE"
    assert manifest["attempts"][1]["duplicate_of"] == manifest["attempts"][0]["candidate_id"]
    assert len(manifest["accepted"]) == 1


def test_cross_process_module_help_is_stable() -> None:
    first = _run("--help", env={"PYTHONHASHSEED": "1"})
    second = _run("--help", env={"PYTHONHASHSEED": "random"})
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout


def test_cli_generation_succeeds_inside_network_blocked_boundary(tmp_path: Path) -> None:
    with offline_runtime():
        result = cli_main(["generate", "--difficulty", "EASY", "--mode", "MASK", "--width", "20", "--height", "20", "--seed", "55", "--output", str(tmp_path)])
    assert result == 0
