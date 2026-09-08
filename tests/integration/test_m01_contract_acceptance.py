import os
import subprocess
import sys
from pathlib import Path

from scrubbots_pixel_factory.contracts import (
    Difficulty,
    actual_used_palette_ids,
    resolve_dimensions,
    resolve_palette_subset,
    validate_dimensions,
    validate_used_color_count,
)


REPO_ROOT = Path(__file__).parents[2]
SRC_ROOT = REPO_ROOT / "src"


def test_every_production_difficulty_resolves_a_coherent_contract() -> None:
    for difficulty in Difficulty:
        width, height = resolve_dimensions(difficulty, seed="m01-acceptance")
        subset = resolve_palette_subset(difficulty, seed="m01-acceptance")
        assert validate_dimensions(difficulty, width, height) == (width, height)
        assert len(subset) in {
            Difficulty.EASY: range(3, 6),
            Difficulty.MEDIUM: range(6, 8),
            Difficulty.HARD: range(8, 10),
            Difficulty.VERY_HARD: range(10, 13),
        }[difficulty]
        cells = list(subset)
        assert actual_used_palette_ids(cells) == subset
        assert validate_used_color_count(difficulty, cells) == subset


def test_repeated_contract_resolution_is_byte_stable_in_fresh_processes() -> None:
    code = """
from scrubbots_pixel_factory.contracts import Difficulty, resolve_dimensions, resolve_palette_subset
for difficulty in Difficulty:
    print(difficulty.value, resolve_dimensions(difficulty, seed='stable'), resolve_palette_subset(difficulty, seed='stable'))
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT)
    outputs = [
        subprocess.run(
            [sys.executable, "-c", code],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        for _ in range(2)
    ]
    assert outputs[0] == outputs[1]


def test_m01_contract_layer_has_no_network_imports_or_generator_dependency() -> None:
    forbidden = ("import socket", "from socket", "import requests", "import httpx", "import urllib")
    contract_root = SRC_ROOT / "scrubbots_pixel_factory" / "contracts"
    for source_path in contract_root.rglob("*.py"):
        source = source_path.read_text(encoding="utf-8")
        assert not any(token in source for token in forbidden), source_path
    assert not any(name.startswith("scrubbots_pixel_factory.generators") for name in sys.modules)
