"""Production RULES generator integrated with the validated M02 core."""

from ...contracts import ColorUsageContractError
from ...core import (
    DeterministicRNG,
    FailureCode,
    GenerationRequest,
    GenerationResult,
    GeneratorMode,
    PixelGenerator,
    RNG_ALGORITHM,
    ResultContractError,
)
from .colorize import colorize_canvas
from .model import RuleCandidate, RuleContractError
from .recipes import RECIPE_NAMES, recipe_for, render_recipe


MAX_ATTEMPTS = 4


class RuleShapeGenerator:
    """Original offline procedural shape/rule generator; never calls MASK."""

    generator_id = "rule-shape"
    generator_version = "1.0.0"

    @staticmethod
    def _failure(code: FailureCode, reason: str, request: GenerationRequest | None) -> GenerationResult:
        return GenerationResult.failure(code=code, reason=reason, request=request)

    @staticmethod
    def _config(request: GenerationRequest) -> tuple[int, int]:
        options = request.options
        if options.namespace == "default":
            if options.values:
                raise RuleContractError("default RULES options namespace must be empty")
            return 2, 82
        if options.namespace != "rules" or options.version != 1:
            raise RuleContractError("RULES options require namespace rules and version 1")
        allowed = {"min_color_region_size", "max_color_dominance_pct"}
        if set(options.values) - allowed:
            raise RuleContractError("RULES options contain an unsupported field")
        minimum = options.values.get("min_color_region_size", 2)
        maximum = options.values.get("max_color_dominance_pct", 82)
        if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 2 or minimum > 64:
            raise RuleContractError("min_color_region_size must be an integer in 2..64")
        if isinstance(maximum, bool) or not isinstance(maximum, int) or not 50 <= maximum <= 100:
            raise RuleContractError("max_color_dominance_pct must be an integer in 50..100")
        return minimum, maximum

    def generate_candidate(self, request: GenerationRequest, rng: DeterministicRNG | None = None) -> RuleCandidate | GenerationResult:
        if not isinstance(request, GenerationRequest):
            return self._failure(FailureCode.INVALID_REQUEST, "RULES generation requires a GenerationRequest", None)
        if request.generator_mode != GeneratorMode.RULES.value:
            return self._failure(FailureCode.INVALID_REQUEST, "rule-shape accepts only RULES mode", request)
        if request.theme is not None:
            return self._failure(FailureCode.INVALID_REQUEST, "theme is unsupported by RULES V1", request)
        stream = DeterministicRNG(request.seed) if rng is None else rng
        if not isinstance(stream, DeterministicRNG):
            return self._failure(FailureCode.INVALID_REQUEST, "RULES generation requires the project DeterministicRNG", request)
        if stream.domain != "root":
            return self._failure(FailureCode.INVALID_REQUEST, "supplied RNG must be the canonical root stream", request)
        if stream.stage_seeds() != DeterministicRNG(request.seed).stage_seeds():
            return self._failure(FailureCode.INVALID_REQUEST, "supplied RNG is incoherent with the request seed", request)
        try:
            minimum, maximum = self._config(request)
            width, height = request.resolve_dimensions()
            palette = request.resolve_palette_subset()
            recipe = recipe_for(request.style, stream.stage_rng("geometry"))
        except (TypeError, ValueError, ColorUsageContractError, RuleContractError) as exc:
            return self._failure(FailureCode.INVALID_REQUEST, str(exc).split("\n", 1)[0], request)

        retry_seeds: dict[str, str] = {}
        for attempt in range(MAX_ATTEMPTS):
            retry_seeds[str(attempt)] = stream.retry_seed(attempt)
            try:
                attempt_rng = stream.retry_rng(attempt)
                canvas = render_recipe(recipe, width, height, attempt_rng.stage_rng("geometry"))
                foreground = len(canvas.occupied)
                total = width * height
                if not recipe.occupancy_floor_pct <= foreground * 100 / total <= recipe.occupancy_ceiling_pct:
                    raise RuleContractError("recipe occupancy is outside its documented bounds")
                colored = colorize_canvas(canvas, palette, attempt_rng.stage_rng("colorization"), min_region_size=minimum, max_dominance_pct=maximum)
                result = GenerationResult.success(
                    request=request,
                    width=width,
                    height=height,
                    logical_grid=colored.cells,
                    generator_mode=GeneratorMode.RULES.value,
                    generator_id=self.generator_id,
                    generator_version=self.generator_version,
                    seed=request.seed,
                    rng_algorithm=RNG_ALGORITHM,
                    provenance={"stage_seeds": stream.stage_seeds(), "retry_seeds": dict(retry_seeds)},
                )
                return RuleCandidate(canvas, recipe, palette, colored.cells, result, attempt, "COMPOSED_RULES", tuple(sorted(canvas.regions)))
            except (TypeError, ValueError, RuleContractError, ResultContractError):
                continue
        return self._failure(FailureCode.RETRY_EXHAUSTED, "bounded RULES generation attempts exhausted", request)

    def generate(self, request: GenerationRequest, rng: DeterministicRNG | None = None) -> GenerationResult:
        candidate = self.generate_candidate(request, rng)
        return candidate.result if isinstance(candidate, RuleCandidate) else candidate


def recipe_names() -> tuple[str, ...]:
    return RECIPE_NAMES
