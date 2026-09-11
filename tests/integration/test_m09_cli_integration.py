from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from scrubbots_pixel_factory import DeterministicRNG, GenerationRequest, GeneratorOptions, GenerationResult, GeneratorMode, QualityPolicy, RNG_ALGORITHM, evaluate_grid, offline_runtime
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


def test_batch_outputs_are_identical_across_processes_and_hash_seeds(tmp_path: Path) -> None:
    roots = [tmp_path / "hash-one", tmp_path / "hash-two"]
    results = [
        _run("batch", "--difficulty", "EASY", "--count", "2", "--mode", "MASK", "--seed", "hash-seed", "--max-attempts", "4", "--width", "20", "--height", "21", "--output", str(root), env={"PYTHONHASHSEED": value})
        for root, value in zip(roots, ("1", "random"), strict=True)
    ]
    assert all(result.returncode == 0 for result in results), [result.stderr for result in results]
    files = sorted(path.relative_to(roots[0]).as_posix() for path in roots[0].rglob("*") if path.is_file())
    assert files == sorted(path.relative_to(roots[1]).as_posix() for path in roots[1].rglob("*") if path.is_file())
    assert all((roots[0] / relative).read_bytes() == (roots[1] / relative).read_bytes() for relative in files)


def test_batch_identity_and_candidate_ids_bind_exemplar_environment(tmp_path: Path) -> None:
    plain_root = tmp_path / "plain"
    exemplar_root = tmp_path / "exemplar"
    plain = _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--seed", "901", "--max-attempts", "2", "--width", "20", "--height", "20", "--output", str(plain_root))
    with_exemplar = _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--seed", "901", "--max-attempts", "2", "--width", "20", "--height", "20", "--exemplar-json", str(FIXTURE), "--output", str(exemplar_root))
    assert plain.returncode == with_exemplar.returncode == 0
    first = json.loads((plain_root / "batch-manifest.json").read_text(encoding="utf-8"))
    second = json.loads((exemplar_root / "batch-manifest.json").read_text(encoding="utf-8"))
    assert first["batch_id"] != second["batch_id"]
    assert first["accepted"][0]["candidate_id"] != second["accepted"][0]["candidate_id"]
    assert second["exemplar_identities"][0]["provenance_description"]


def test_batch_autodimensions_and_rectangular_manifest_bindings(tmp_path: Path) -> None:
    auto_root = tmp_path / "auto"
    rectangular_root = tmp_path / "rectangular"
    auto = _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--seed", "902", "--max-attempts", "2", "--output", str(auto_root))
    rectangular = _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "RULES", "--seed", "903", "--max-attempts", "2", "--width", "20", "--height", "21", "--output", str(rectangular_root))
    assert auto.returncode == rectangular.returncode == 0
    auto_manifest = json.loads((auto_root / "batch-manifest.json").read_text(encoding="utf-8"))
    rect_manifest = json.loads((rectangular_root / "batch-manifest.json").read_text(encoding="utf-8"))
    assert auto_manifest["request_template"]["width"] is None and auto_manifest["request_template"]["height"] is None
    assert auto_manifest["accepted"][0]["width"] > 0 and auto_manifest["accepted"][0]["height"] > 0
    assert (rect_manifest["accepted"][0]["width"], rect_manifest["accepted"][0]["height"]) == (20, 21)


def test_reproduce_uses_non_default_recorded_quality_policy(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.json"
    policy = QualityPolicy(difficulty="EASY", max_isolated_ratio=0.31)
    policy_path.write_text(json.dumps(policy.as_dict()), encoding="utf-8")
    generated = _run("generate", "--difficulty", "EASY", "--mode", "MASK", "--width", "20", "--height", "20", "--seed", "904", "--quality-policy-json", str(policy_path), "--output", str(tmp_path / "bundle"))
    assert generated.returncode == 0, generated.stderr
    metadata = next((tmp_path / "bundle").rglob("metadata.json"))
    value = json.loads(metadata.read_text(encoding="utf-8"))
    assert value["quality"]["report"]["policy"] == policy.as_dict()
    reproduced = _run("reproduce", str(metadata))
    assert reproduced.returncode == 0 and "MATCH" in reproduced.stdout


def test_quality_policy_can_produce_a_truthful_rejected_batch_attempt(tmp_path: Path) -> None:
    policy_path = tmp_path / "reject-policy.json"
    policy = QualityPolicy(difficulty="EASY", max_largest_region_ratio=0.0)
    policy_path.write_text(json.dumps(policy.as_dict()), encoding="utf-8")
    result = _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--seed", "905", "--max-attempts", "1", "--width", "20", "--height", "20", "--quality-policy-json", str(policy_path), "--output", str(tmp_path / "rejected"))
    assert result.returncode == 7
    manifest = json.loads((tmp_path / "rejected" / "batch-manifest.json").read_text(encoding="utf-8"))
    attempt = manifest["attempts"][0]
    assert attempt["status"] == "QUALITY_REJECTED" and attempt["quality_decision"] == "REJECT" and attempt["rejection_codes"]
    assert attempt["candidate_id"] is None and attempt["relative_path"] is None


@pytest.mark.parametrize(
    "mutation",
    (
        lambda value: value["attempts"][0]["attempt_seed"].update(value="tampered"),
        lambda value: value["attempts"][0].update(status="QUALITY_REJECTED"),
        lambda value: value["attempts"][0].update(grid_hash="0" * 64),
        lambda value: value["attempts"][0].update(rejection_codes=["FORGED"]),
        lambda value: value["accepted"][0].update(candidate_id="forged-candidate"),
        lambda value: value["accepted"][0].update(relative_path="../escape"),
        lambda value: value["accepted"][0].update(width=21),
        lambda value: value.update(accepted_count=0),
        lambda value: value.update(next_attempt_index=0),
        lambda value: value.update(terminal_state="EXHAUSTED"),
    ),
)
def test_resume_rejects_semantically_tampered_manifest_history(tmp_path: Path, mutation) -> None:
    root = tmp_path / "batch"
    generated = _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--seed", "906", "--max-attempts", "2", "--width", "20", "--height", "20", "--output", str(root))
    assert generated.returncode == 0, generated.stderr
    manifest_path = root / "batch-manifest.json"
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutation(value)
    manifest_path.write_text(json.dumps(value), encoding="utf-8")
    resumed = _run("batch", "--resume", str(manifest_path))
    assert resumed.returncode != 0
    assert "Traceback" not in resumed.stderr


@pytest.mark.parametrize(
    "mutation",
    (
        lambda value: value.update(schema="forged-schema"),
        lambda value: value["generation"]["request"].pop("generator_options"),
        lambda value: value["generation"]["request"]["seed"].update(value="forged-seed"),
        lambda value: value["generation"].update(generator_mode="RULES"),
        lambda value: value["generation"]["result"].update(logical_grid=["C01"] + value["generation"]["result"]["logical_grid"][1:]),
        lambda value: value["quality"]["report"]["policy"].update(max_largest_region_ratio=0.0),
    ),
)
def test_reproduce_rejects_each_metadata_corruption_class(tmp_path: Path, mutation) -> None:
    generated = _run("generate", "--difficulty", "EASY", "--mode", "MASK", "--width", "20", "--height", "20", "--seed", "907", "--output", str(tmp_path))
    assert generated.returncode == 0
    metadata = next(tmp_path.rglob("metadata.json"))
    original = json.loads(metadata.read_text(encoding="utf-8"))
    mutation(original)
    metadata.write_text(json.dumps(original), encoding="utf-8")
    reproduced = _run("reproduce", str(metadata))
    assert reproduced.returncode != 0
    assert "Traceback" not in reproduced.stderr


def test_mask_reproduce_is_byte_exact_and_candidate_path_is_local(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    generated = _run("generate", "--difficulty", "EASY", "--mode", "MASK", "--width", "20", "--height", "21", "--seed", "908", "--output", str(first_root))
    assert generated.returncode == 0
    metadata = next(first_root.rglob("metadata.json"))
    reproduced = _run("reproduce", str(metadata), "--output", str(second_root))
    assert reproduced.returncode == 0
    first_files = sorted(path.relative_to(first_root).as_posix() for path in first_root.rglob("*") if path.is_file())
    second_files = sorted(path.relative_to(second_root).as_posix() for path in second_root.rglob("*") if path.is_file())
    assert first_files == second_files
    assert all((first_root / relative).read_bytes() == (second_root / relative).read_bytes() for relative in first_files)
    traversal = _run("generate", "--difficulty", "EASY", "--mode", "MASK", "--width", "20", "--height", "20", "--seed", "909", "--candidate-id", "../escape", "--output", str(tmp_path / "traversal"))
    assert traversal.returncode != 0
