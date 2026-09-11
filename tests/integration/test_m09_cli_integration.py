from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from scrubbots_pixel_factory import DeterministicRNG, GenerationRequest, GeneratorOptions, GenerationResult, GeneratorMode, QualityPolicy, RNG_ALGORITHM, evaluate_grid, offline_runtime
from scrubbots_pixel_factory.cli import main as cli_main
from scrubbots_pixel_factory.generators.router import GeneratorRouter
from scrubbots_pixel_factory.output import canonical_json_bytes, read_bundle

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


def test_single_explicit_request_has_default_id_and_byte_identical_bundles(tmp_path: Path) -> None:
    roots = (tmp_path / "one", tmp_path / "two")
    results = [_run("generate", "--difficulty", "EASY", "--mode", "RULES", "--width", "20", "--height", "20", "--seed", "910", "--output", str(root), env={"PYTHONHASHSEED": seed}) for root, seed in zip(roots, ("1", "random"), strict=True)]
    assert all(result.returncode == 0 for result in results), [result.stderr for result in results]
    bundles = [next(root.rglob("metadata.json")).parent for root in roots]
    assert bundles[0].name == bundles[1].name
    files = sorted(path.name for path in bundles[0].iterdir() if path.is_file())
    assert files == sorted(path.name for path in bundles[1].iterdir() if path.is_file())
    assert all((bundles[0] / name).read_bytes() == (bundles[1] / name).read_bytes() for name in files)


def test_single_auto_dimensions_record_exact_legal_resolution(tmp_path: Path) -> None:
    result = _run("generate", "--difficulty", "EASY", "--mode", "MASK", "--seed", "911", "--output", str(tmp_path))
    assert result.returncode == 0, result.stderr
    bundle = read_bundle(next(tmp_path.rglob("metadata.json")).parent)
    request = bundle.metadata["generation"]["request"]
    resolved = bundle.metadata["generation"]["result"]["resolved_dimensions"]
    assert request["width"] is None and request["height"] is None
    assert resolved == {"width": bundle.artwork.width, "height": bundle.artwork.height}
    assert 20 <= bundle.artwork.width <= 29 and 20 <= bundle.artwork.height <= 29


@pytest.mark.parametrize("kind", ("invalid-mode", "malformed-options", "unsupported-options"))
def test_invalid_mode_and_options_are_stable_nonzero_without_traceback(tmp_path: Path, kind: str) -> None:
    args: tuple[str, ...]
    if kind == "invalid-mode":
        args = ("--mode", "NOT_A_MODE")
    else:
        options = tmp_path / f"{kind}.json"
        options.write_text("{malformed}" if kind == "malformed-options" else json.dumps({"namespace": "unsupported", "version": 99, "values": {}}), encoding="utf-8")
        args = ("--options-json", str(options))
    result = _run("generate", "--difficulty", "EASY", "--mode", "MASK", "--seed", "912", *args, "--output", str(tmp_path / "bad"))
    assert result.returncode != 0 and "Traceback" not in result.stderr


def test_every_attempt_seed_and_candidate_id_use_the_canonical_helpers(tmp_path: Path) -> None:
    result = _run("batch", "--difficulty", "EASY", "--count", "3", "--mode", "MASK", "--seed", "913", "--max-attempts", "4", "--width", "20", "--height", "20", "--output", str(tmp_path))
    assert result.returncode == 0, result.stderr
    manifest = json.loads((tmp_path / "batch-manifest.json").read_text(encoding="utf-8"))
    from scrubbots_pixel_factory.cli.main import _batch_candidate_id
    root_seed = manifest["root_seed"]["value"]
    for index, attempt in enumerate(manifest["attempts"]):
        assert attempt["attempt_seed"] == {"type": "string", "value": DeterministicRNG(root_seed).retry_seed(index)}
        if attempt["status"] == "ACCEPTED":
            assert attempt["candidate_id"] == _batch_candidate_id(manifest, index)
    accepted_ids = [record["candidate_id"] for record in manifest["accepted"]]
    assert len(accepted_ids) == len(set(accepted_ids)) == 3


def test_two_known_root_seeds_produce_different_accepted_sets(tmp_path: Path) -> None:
    roots = (tmp_path / "seed-a", tmp_path / "seed-b")
    for root, seed in zip(roots, ("1", "2"), strict=True):
        result = _run("batch", "--difficulty", "EASY", "--count", "2", "--mode", "MASK", "--seed", seed, "--max-attempts", "3", "--width", "20", "--height", "20", "--output", str(root))
        assert result.returncode == 0, result.stderr
    accepted_sets = [
        {record["grid_hash"] for record in json.loads((root / "batch-manifest.json").read_text(encoding="utf-8"))["accepted"]}
        for root in roots
    ]
    assert accepted_sets[0] != accepted_sets[1]


def test_single_quality_rejection_has_exact_exit_and_stable_codes(tmp_path: Path) -> None:
    policy = QualityPolicy(difficulty="EASY", max_largest_region_ratio=0.0)
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy.as_dict()), encoding="utf-8")
    result = _run("generate", "--difficulty", "EASY", "--mode", "MASK", "--width", "20", "--height", "20", "--seed", "916", "--quality-policy-json", str(policy_path), "--output", str(tmp_path / "output"))
    assert result.returncode == 5
    assert "QUALITY_REJECTED" in result.stderr and "DOMINANCE_VIOLATION" in result.stderr
    assert not (tmp_path / "output").exists() or not list((tmp_path / "output").rglob("metadata.json"))


def test_direct_reproduce_negative_matrix_includes_remaining_m08_cases(tmp_path: Path) -> None:
    generated = _run("generate", "--difficulty", "EASY", "--mode", "MASK", "--width", "20", "--height", "20", "--seed", "10", "--output", str(tmp_path))
    assert generated.returncode == 0
    metadata = next(tmp_path.rglob("metadata.json"))
    original = metadata.read_bytes()
    mutations = ("malformed-json", "request-version", "options-namespace", "options-version", "generator-version", "original-grid-hash")
    for name in mutations:
        shutil.rmtree(tmp_path / name, ignore_errors=True)
        case = tmp_path / name
        shutil.copytree(metadata.parent, case)
        case_metadata = case / "metadata.json"
        case_artwork = case / "artwork.json"
        if name == "malformed-json":
            case_metadata.write_text("{not-json", encoding="utf-8")
        elif name == "original-grid-hash":
            artwork = json.loads(case_artwork.read_text(encoding="utf-8"))
            artwork["grid_hash"] = "0" * 64
            case_artwork.write_bytes(canonical_json_bytes(artwork))
        else:
            value = json.loads(case_metadata.read_text(encoding="utf-8"))
            if name == "request-version":
                value["generation"]["request"]["schema_version"] = 99
            elif name == "options-namespace":
                value["generation"]["request"]["generator_options"]["namespace"] = "unsupported"
            elif name == "options-version":
                value["generation"]["request"]["generator_options"]["version"] = 99
            else:
                value["generation"]["generator_version"] = "9.9.9"
            case_metadata.write_bytes(canonical_json_bytes(value))
        reproduced = _run("reproduce", str(case_metadata))
        assert reproduced.returncode != 0 and "Traceback" not in reproduced.stderr, name


def test_controlled_regeneration_with_different_grid_returns_reproduce_mismatch(tmp_path: Path, monkeypatch) -> None:
    generated = _run("generate", "--difficulty", "EASY", "--mode", "MASK", "--width", "20", "--height", "20", "--seed", "918", "--output", str(tmp_path))
    assert generated.returncode == 0
    metadata = next(tmp_path.rglob("metadata.json"))
    bundle = read_bundle(metadata.parent)
    request = cli_module._request_from_canonical(bundle.metadata["generation"]["request"])
    cells = list(bundle.artwork.cells)
    cells[0] = next(color for color in cells[1:] if color != cells[0])
    changed = GenerationResult.success(request=request, width=bundle.artwork.width, height=bundle.artwork.height, logical_grid=cells, generator_mode="MASK", generator_id="mask-sprite", generator_version="1.0.0", seed=request.seed, rng_algorithm=RNG_ALGORITHM, provenance={"stage_seeds": DeterministicRNG(request.seed).stage_seeds()})

    class DifferentRouter:
        def generate_candidate(self, _request):
            return changed

    monkeypatch.setattr(cli_module, "_router", lambda registry: DifferentRouter())
    assert cli_main(["reproduce", str(metadata)]) == 6


def test_coordinated_candidate_id_path_and_m08_binding_rewrite_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "batch"
    generated = _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--seed", "919", "--max-attempts", "2", "--width", "20", "--height", "20", "--output", str(root))
    assert generated.returncode == 0
    manifest_path = root / "batch-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    old_id = manifest["accepted"][0]["candidate_id"]
    new_id = old_id + "-rewritten"
    old_dir = root / "candidates" / old_id
    new_dir = root / "candidates" / new_id
    for filename in ("artwork.json", "metadata.json"):
        file_path = old_dir / filename
        value = json.loads(file_path.read_text(encoding="utf-8"))
        if filename == "artwork.json":
            value["candidate_id"] = new_id
        else:
            value["candidate_id"] = new_id
            value["artwork"]["candidate_id"] = new_id
            value["quality"]["candidate_id"] = new_id
        file_path.write_bytes(canonical_json_bytes(value))
    old_dir.rename(new_dir)
    manifest["attempts"][0]["candidate_id"] = new_id
    manifest["attempts"][0]["relative_path"] = f"candidates/{new_id}"
    manifest["accepted"][0]["candidate_id"] = new_id
    manifest["accepted"][0]["relative_path"] = f"candidates/{new_id}"
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    assert read_bundle(new_dir).artwork.candidate_id == new_id
    resumed = _run("batch", "--resume", str(manifest_path))
    assert resumed.returncode != 0 and "Traceback" not in resumed.stderr


@pytest.mark.parametrize("relative_path", ("C:/absolute/path", "candidates\\unsafe"))
def test_resume_rejects_absolute_and_nonportable_accepted_paths(tmp_path: Path, relative_path: str) -> None:
    root = tmp_path / "batch"
    assert _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--seed", "920", "--max-attempts", "2", "--width", "20", "--height", "20", "--output", str(root)).returncode == 0
    manifest_path = root / "batch-manifest.json"
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    value["accepted"][0]["relative_path"] = relative_path
    manifest_path.write_bytes(canonical_json_bytes(value))
    assert _run("batch", "--resume", str(manifest_path)).returncode != 0


@pytest.mark.parametrize("tamper", ("bundle-hash", "embedded-seed"))
def test_resume_rejects_accepted_bundle_cross_binding_tamper(tmp_path: Path, tamper: str) -> None:
    root = tmp_path / tamper
    assert _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--seed", "921", "--max-attempts", "2", "--width", "20", "--height", "20", "--output", str(root)).returncode == 0
    manifest = json.loads((root / "batch-manifest.json").read_text(encoding="utf-8"))
    bundle_dir = root / manifest["accepted"][0]["relative_path"]
    if tamper == "bundle-hash":
        artwork = json.loads((bundle_dir / "artwork.json").read_text(encoding="utf-8"))
        artwork["grid_hash"] = "0" * 64
        (bundle_dir / "artwork.json").write_bytes(canonical_json_bytes(artwork))
    else:
        metadata = json.loads((bundle_dir / "metadata.json").read_text(encoding="utf-8"))
        metadata["generation"]["request"]["seed"] = {"type": "string", "value": "wrong-seed"}
        (bundle_dir / "metadata.json").write_bytes(canonical_json_bytes(metadata))
    resumed = _run("batch", "--resume", str(root / "batch-manifest.json"))
    assert resumed.returncode != 0 and "Traceback" not in resumed.stderr


@pytest.mark.parametrize("state", ("COMPLETE", "IN_PROGRESS"))
def test_resume_rejects_forged_terminal_states_on_exhausted_history(tmp_path: Path, state: str) -> None:
    root = tmp_path / state
    assert _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "WFC", "--seed", "922", "--max-attempts", "1", "--width", "20", "--height", "20", "--output", str(root)).returncode == 7
    manifest_path = root / "batch-manifest.json"
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    value["terminal_state"] = state
    manifest_path.write_bytes(canonical_json_bytes(value))
    assert _run("batch", "--resume", str(manifest_path)).returncode != 0


def test_resume_rejects_forged_exhausted_state_on_complete_history(tmp_path: Path) -> None:
    root = tmp_path / "complete"
    assert _run("batch", "--difficulty", "EASY", "--count", "1", "--mode", "MASK", "--seed", "923", "--max-attempts", "2", "--width", "20", "--height", "20", "--output", str(root)).returncode == 0
    manifest_path = root / "batch-manifest.json"
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    value["terminal_state"] = "EXHAUSTED"
    manifest_path.write_bytes(canonical_json_bytes(value))
    assert _run("batch", "--resume", str(manifest_path)).returncode != 0


@pytest.mark.parametrize("field", ("candidate_id", "relative_path"))
def test_resume_rejects_duplicate_accepted_identity_or_path(tmp_path: Path, field: str) -> None:
    root = tmp_path / field
    assert _run("batch", "--difficulty", "EASY", "--count", "2", "--mode", "MASK", "--seed", "924", "--max-attempts", "3", "--width", "20", "--height", "20", "--output", str(root)).returncode == 0
    manifest_path = root / "batch-manifest.json"
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    value["accepted"][1][field] = value["accepted"][0][field]
    manifest_path.write_bytes(canonical_json_bytes(value))
    assert _run("batch", "--resume", str(manifest_path)).returncode != 0
