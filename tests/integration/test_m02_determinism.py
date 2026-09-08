import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from scrubbots_pixel_factory.core import GenerationRequest
from tests.support.deterministic_probe import DeterministicContractProbeGenerator


REPO_ROOT = Path(__file__).parents[2]
SRC_ROOT = REPO_ROOT / "src"


def test_same_request_repeats_grid_and_canonical_result_bytes() -> None:
    request = GenerationRequest(difficulty="VERY_HARD", seed=734, generator_mode="HYBRID")
    generator = DeterministicContractProbeGenerator()
    first = generator.generate(request)
    second = generator.generate(request)
    assert first.logical_grid == second.logical_grid
    assert first.canonical_bytes() == second.canonical_bytes()


def test_different_seed_changes_fixed_probe_output() -> None:
    generator = DeterministicContractProbeGenerator()
    first = generator.generate(GenerationRequest(difficulty="MEDIUM", seed=1, generator_mode="RULES"))
    second = generator.generate(GenerationRequest(difficulty="MEDIUM", seed=2, generator_mode="RULES"))
    assert first.logical_grid != second.logical_grid or first.canonical_bytes() != second.canonical_bytes()


def test_canonical_bytes_are_stable_across_python_hash_seeds() -> None:
    code = """
from scrubbots_pixel_factory.core import GenerationRequest
from tests.support.deterministic_probe import DeterministicContractProbeGenerator
request = GenerationRequest(difficulty='HARD', seed='cross-process', generator_mode='WFC', generator_options={'namespace':'probe','version':1,'values':{'b':2,'a':[3,1]}})
print(DeterministicContractProbeGenerator().generate(request).digest())
print(DeterministicContractProbeGenerator().generate(request).canonical_json())
"""
    outputs = []
    for hash_seed in ("1", "987654321"):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_ROOT)
        env["PYTHONHASHSEED"] = hash_seed
        outputs.append(subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=True).stdout)
    assert outputs[0] == outputs[1]
    assert json.loads(outputs[0].splitlines()[1])["status"] == "SUCCESS"


def test_empty_string_seed_is_stable_across_processes() -> None:
    code = """
from scrubbots_pixel_factory.core import DeterministicRNG, GenerationRequest
request = GenerationRequest(difficulty='EASY', seed='', generator_mode='MASK')
print(request.canonical_json())
print(DeterministicRNG('').stage_seed('geometry'))
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT)
    env["PYTHONHASHSEED"] = "random"
    first = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=True).stdout
    env["PYTHONHASHSEED"] = "42"
    second = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=True).stdout
    assert first == second
