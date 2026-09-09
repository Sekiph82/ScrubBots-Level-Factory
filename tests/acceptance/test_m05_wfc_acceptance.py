import json
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator, WFCCandidate


FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "wfc"
CASES = (
    ("wfc-synthetic-easy-3.json", "EASY", (20, 20)),
    ("wfc-synthetic-medium-6.json", "MEDIUM", (30, 30)),
    ("wfc-synthetic-hard-8.json", "HARD", (40, 40)),
    ("wfc-synthetic-very-hard-10.json", "VERY_HARD", (50, 50)),
)


def _load(name: str) -> Exemplar:
    raw = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    return Exemplar(raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"], tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"])


def test_120_candidate_acceptance_matrix_has_at_least_100_accepted() -> None:
    accepted = 0
    total = 0
    for fixture_index, (name, difficulty, dimensions) in enumerate(CASES):
        exemplar = _load(name)
        generator = WFCGenerator(ExemplarRegistry((exemplar,)))
        for seed_offset in range(30):
            total += 1
            values = {
                "pattern_size": 2 if seed_offset % 2 == 0 else 3,
                "input_periodic": seed_offset % 3 != 0,
                "output_periodic": seed_offset % 4 == 0,
                "allow_rotations": seed_offset % 5 == 0,
                "allow_reflections": seed_offset % 7 == 0,
                "max_attempts": 4,
            }
            request = GenerationRequest(difficulty, 1000 + fixture_index * 100 + seed_offset, "WFC", width=dimensions[0], height=dimensions[1], style=exemplar.exemplar_id, palette_subset=exemplar.source_palette, generator_options=GeneratorOptions("wfc", 1, values))
            candidate = generator.generate_candidate(request)
            if isinstance(candidate, WFCCandidate):
                accepted += 1
                assert candidate.result.is_success
                assert len(candidate.logical_grid) == dimensions[0] * dimensions[1]
                assert set(candidate.logical_grid) == set(exemplar.source_palette)
                assert candidate.wfc_metadata["attempt"] < values["max_attempts"]
    assert total == 120
    assert accepted >= 100
