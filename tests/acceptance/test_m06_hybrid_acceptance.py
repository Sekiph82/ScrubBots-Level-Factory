"""Deterministic M06 acceptance matrix for both robust strategies."""

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.router import HybridCandidate, HybridGenerator


CASES = (
    ("EASY", (20, 27)), ("MEDIUM", (37, 34)), ("HARD", (48, 41)), ("VERY_HARD", (53, 59)),
)


def test_m06_robust_strategy_matrix_has_24_accepted_replays() -> None:
    generator = HybridGenerator()
    accepted = 0
    for strategy in ("MASK_GEOMETRY_RULE_COLOR_REGIONS", "RULE_GEOMETRY_MASK_SYMMETRY"):
        for difficulty, (width, height) in CASES:
            for seed in (17, 29, 43):
                request = GenerationRequest(
                    difficulty, seed, "HYBRID", width=width, height=height,
                    generator_options=GeneratorOptions("hybrid", 1, {
                        "strategy": strategy, "mask_style": "ROBOT", "rules_style": "ORGANIC", "mask_symmetry": "HORIZONTAL",
                    }),
                )
                first = generator.generate_candidate(request)
                second = generator.generate_candidate(request)
                assert isinstance(first, HybridCandidate) and isinstance(second, HybridCandidate)
                assert first.result.canonical_bytes() == second.result.canonical_bytes()
                assert first.result.width == width and first.result.height == height
                assert tuple(first.metadata["resolved_palette"]) == first.result.used_palette
                accepted += 1
    assert accepted == 24
