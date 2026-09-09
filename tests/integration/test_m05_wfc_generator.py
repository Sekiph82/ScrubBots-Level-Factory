import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scrubbots_pixel_factory import DeterministicRNG, FailureCode, GenerationRequest, GeneratorOptions, PixelGenerator, offline_runtime
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator, WFCCandidate


FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "wfc"
FIXTURE_SPECS = (
    ("wfc-synthetic-easy-3.json", "EASY", (20, 20)),
    ("wfc-synthetic-medium-6.json", "MEDIUM", (30, 30)),
    ("wfc-synthetic-hard-8.json", "HARD", (40, 40)),
    ("wfc-synthetic-very-hard-10.json", "VERY_HARD", (50, 50)),
)


def _load(name: str) -> Exemplar:
    raw = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    return Exemplar(raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"], tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"])


def _request(exemplar: Exemplar, difficulty: str, dimensions: tuple[int, int], seed: int | str = 41, **values: object) -> GenerationRequest:
    return GenerationRequest(
        difficulty, seed, "WFC", width=dimensions[0], height=dimensions[1], style=exemplar.exemplar_id,
        palette_subset=exemplar.source_palette,
        generator_options=GeneratorOptions("wfc", 1, {"pattern_size": 2, "input_periodic": True, **values}),
    )


def test_wfc_integrates_with_m02_and_is_offline_deterministic() -> None:
    exemplar = _load(FIXTURE_SPECS[0][0])
    generator = WFCGenerator(ExemplarRegistry((exemplar,)))
    assert isinstance(generator, PixelGenerator)
    request = _request(exemplar, "EASY", (20, 20), "offline")
    with offline_runtime():
        first = generator.generate(request)
        second = generator.generate(request)
    assert first.is_success and first.canonical_bytes() == second.canonical_bytes()
    assert set(first.logical_grid) == set(first.used_palette) == set(exemplar.source_palette)


def test_wfc_rejects_wrong_mode_root_rng_theme_and_ineligible_exemplar() -> None:
    exemplar = _load(FIXTURE_SPECS[0][0])
    generator = WFCGenerator(ExemplarRegistry((exemplar,)))
    request = _request(exemplar, "EASY", (20, 20))
    assert generator.generate(GenerationRequest("EASY", 1, "MASK")).failure_code is FailureCode.INVALID_REQUEST
    assert generator.generate(request, DeterministicRNG(41, "geometry")).failure_code is FailureCode.INVALID_REQUEST
    assert generator.generate(_request(exemplar, "EASY", (20, 20), theme="forbidden")).failure_code is FailureCode.INVALID_REQUEST
    unapproved = Exemplar(exemplar.schema, exemplar.version, "unapproved", exemplar.role, exemplar.width, exemplar.height, exemplar.pixels, exemplar.provenance_type, exemplar.provenance_description, "OWNER_SUPPLIED_UNAPPROVED")
    assert WFCGenerator(ExemplarRegistry((unapproved,))).generate(_request(unapproved, "EASY", (20, 20))).failure_code is FailureCode.INVALID_REQUEST


def test_wfc_mapping_provenance_dimensions_and_metadata() -> None:
    exemplar = _load(FIXTURE_SPECS[0][0])
    request = GenerationRequest("EASY", 91, "WFC", width=21, height=21, style=exemplar.exemplar_id, palette_subset=("C04", "C05", "C06"), generator_options=GeneratorOptions("wfc", 1, {"pattern_size": 2, "input_periodic": True, "output_periodic": True, "palette_mapping": {"C01": "C04", "C02": "C05", "C03": "C06"}}))
    candidate = WFCGenerator(ExemplarRegistry((exemplar,))).generate_candidate(request)
    assert isinstance(candidate, WFCCandidate)
    assert candidate.result.is_success
    assert (candidate.result.width, candidate.result.height) == (21, 21)
    assert set(candidate.result.logical_grid) == {"C04", "C05", "C06"}
    assert candidate.wfc_metadata["attempt"] == candidate.attempt
    assert candidate.wfc_metadata["palette_mapping"] == [["C01", "C04"], ["C02", "C05"], ["C03", "C06"]]
    assert candidate.result.provenance["stage_seeds"] == DeterministicRNG(91).stage_seeds()


def test_wfc_n3_and_experimental_n4_are_explicit() -> None:
    exemplar = _load(FIXTURE_SPECS[0][0])
    generator = WFCGenerator(ExemplarRegistry((exemplar,)))
    n3 = generator.generate_candidate(_request(exemplar, "EASY", (20, 20), 71, pattern_size=3))
    n4 = generator.generate_candidate(_request(exemplar, "EASY", (20, 20), 71, pattern_size=4, experimental_n4=True))
    assert isinstance(n3, WFCCandidate) and isinstance(n4, WFCCandidate)
    assert n3.wfc_metadata["pattern_size"] == 3 and n4.wfc_metadata["experimental_n4"] is True


def test_wfc_cross_process_digest_is_stable() -> None:
    code = """import json\nfrom pathlib import Path\nfrom scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator\nfrom scrubbots_pixel_factory import GenerationRequest, GeneratorOptions\nr=json.loads(Path('tests/fixtures/wfc/wfc-synthetic-easy-3.json').read_text())\ne=Exemplar(r['schema'],r['version'],r['exemplar_id'],r['role'],r['width'],r['height'],tuple(r['pixels']),r['provenance_type'],r['provenance_description'],r['ownership'])\nq=GenerationRequest('EASY','cross','WFC',width=20,height=20,style=e.exemplar_id,palette_subset=e.source_palette,generator_options=GeneratorOptions('wfc',1,{'pattern_size':2,'input_periodic':True}))\nprint(WFCGenerator(ExemplarRegistry((e,))).generate(q).digest())\n"""
    outputs = []
    for hash_seed in ("1", "random"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed)
        outputs.append(subprocess.check_output([sys.executable, "-c", code], text=True, env=env).strip())
    assert outputs[0] == outputs[1]
