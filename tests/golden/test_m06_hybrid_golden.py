"""PAG-M06 deterministic hybrid golden evidence."""

import json
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.router import HybridCandidate, HybridGenerator
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator


GOLDENS = json.loads((Path(__file__).parent / "m06_hybrid_goldens.json").read_text(encoding="utf-8"))


def _synthetic_exemplar() -> Exemplar:
    colors = ("C11", "C12", "C13")
    pixels = tuple(colors[(x // 2) % 3] for y in range(6) for x in range(6))
    return Exemplar(
        "scrubbots-wfc-exemplar", 1, "m06-review-synthetic-blocks", "TRAINING_MOTIF", 6, 6, pixels,
        "synthetic-test-fixture", "Project-authored golden fixture; not production artwork.", "SYNTHETIC_TEST_ONLY",
    )


def test_m06_hybrid_goldens() -> None:
    generator = HybridGenerator()
    for golden in GOLDENS["entries"]:
        raw = golden["request"]
        if "exemplar" in golden:
            exemplar = _synthetic_exemplar()
            assert golden["exemplar"]["id"] == exemplar.exemplar_id
            assert golden["exemplar"]["ownership"] == exemplar.ownership == "SYNTHETIC_TEST_ONLY"
            generator = HybridGenerator(wfc_generator=WFCGenerator(ExemplarRegistry((exemplar,))))
            palette_subset = tuple(raw["palette_subset"])
            generator_options = raw["generator_options"]
        else:
            generator = HybridGenerator()
            palette_subset = None
            generator_options = {
                "namespace": "hybrid", "version": 1, "values": {
                    "strategy": golden["strategy"], "mask_style": "ROBOT", "rules_style": "ORGANIC",
                    "mask_symmetry": "HORIZONTAL",
                },
            }
        request = GenerationRequest(
            raw["difficulty"], raw["seed"], "HYBRID", width=raw["width"], height=raw["height"],
            palette_subset=palette_subset,
            generator_options=GeneratorOptions(generator_options["namespace"], generator_options["version"], generator_options["values"]),
        )
        candidate = generator.generate_candidate(request)
        assert isinstance(candidate, HybridCandidate)
        assert candidate.result.digest() == golden["final_result_digest"]
        assert candidate.metadata["final_logical_grid_digest"] == golden["final_grid_digest"]
        assert [stage.derived_seed for stage in candidate.stages] == golden["stage_seeds"]
        assert [[stage.engine_id, stage.engine_version] for stage in candidate.stages] == golden["stage_engines"]
        assert [stage.child_request_digest for stage in candidate.stages] == golden["stage_request_digests"]
        assert [stage.child_result_digest for stage in candidate.stages] == golden["stage_result_digests"]
        assert list(candidate.result.used_palette) == golden["palette"]
        if "exemplar" in golden:
            assert candidate.stages[-1].extra["exemplar_id"] == golden["exemplar"]["id"]
            assert [list(pair) for pair in candidate.stages[-1].extra["palette_mapping"]] == golden["palette_mapping"]
