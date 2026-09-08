"""A tiny deterministic contract probe used only by M02 tests and golden fixtures."""

from scrubbots_pixel_factory.core import (
    DeterministicRNG,
    GenerationRequest,
    GenerationResult,
    RNG_ALGORITHM,
)


class DeterministicContractProbeGenerator:
    """Exercise request/RNG/result contracts without implementing a game engine."""

    generator_id = "m02-deterministic-contract-probe"
    generator_version = "1.0.0"

    def generate(self, request: GenerationRequest, rng: DeterministicRNG | None = None) -> GenerationResult:
        stream = rng or DeterministicRNG(request.seed)
        width, height = request.resolve_dimensions()
        palette = request.resolve_palette_subset()
        colorization = stream.stage_rng("colorization")
        cells = [palette[colorization.randbelow(len(palette))] for _ in range(width * height)]
        positions = stream.stage_rng("geometry").shuffle(list(range(width * height)))
        for index, color_id in enumerate(palette):
            cells[positions[index]] = color_id
        return GenerationResult.success(
            request=request,
            width=width,
            height=height,
            logical_grid=cells,
            generator_id=self.generator_id,
            generator_version=self.generator_version,
            rng_algorithm=RNG_ALGORITHM,
            provenance={
                "stage_seeds": stream.stage_seeds(),
                "retry_seeds": {"0": stream.retry_seed(0)},
            },
        )
