"""PAG-M06 deterministic hybrid golden evidence."""

import json
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.router import HybridCandidate, HybridGenerator


GOLDENS = json.loads((Path(__file__).parent / "m06_hybrid_goldens.json").read_text(encoding="utf-8"))


def test_m06_hybrid_goldens() -> None:
    generator = HybridGenerator()
    for golden in GOLDENS["entries"]:
        raw = golden["request"]
        request = GenerationRequest(
            raw["difficulty"], raw["seed"], "HYBRID", width=raw["width"], height=raw["height"],
            generator_options=GeneratorOptions("hybrid", 1, {
                "strategy": golden["strategy"], "mask_style": "ROBOT", "rules_style": "ORGANIC",
                "mask_symmetry": "HORIZONTAL",
            }),
        )
        candidate = generator.generate_candidate(request)
        assert isinstance(candidate, HybridCandidate)
        assert candidate.result.digest() == golden["final_result_digest"]
        assert candidate.metadata["final_logical_grid_digest"] == golden["final_grid_digest"]
        assert [stage.derived_seed for stage in candidate.stages] == golden["stage_seeds"]
        assert [[stage.engine_id, stage.engine_version] for stage in candidate.stages] == golden["stage_engines"]
        assert [stage.child_request_digest for stage in candidate.stages] == golden["stage_request_digests"]
        assert [stage.child_result_digest for stage in candidate.stages] == golden["stage_result_digests"]
