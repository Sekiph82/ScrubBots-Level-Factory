"""Production M03 MASK generator integrated with the M02 contracts."""

from collections.abc import Mapping
from dataclasses import dataclass, replace

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
from .colorize import ColorRole, ColorRoleAssignment, colorize_with_roles
from .engine import MaskContractError, resolve_mask
from .model import MaskConfig, ResolvedMask, SymmetryMode
from .templates import FAMILY_NAMES, TemplateFamily, preferred_symmetry, template_for


MAX_ATTEMPTS = 4


@dataclass(frozen=True, slots=True)
class MaskCandidate:
    result: GenerationResult
    mask: ResolvedMask
    family: TemplateFamily
    attempt: int
    palette: tuple[str, ...]
    roles: tuple[ColorRole, ...]
    role_assignments: tuple[ColorRoleAssignment, ...]


class MaskSpriteGenerator:
    """Original, offline, deterministic procedural SCRUBBOTS mask generator."""

    generator_id = "mask-sprite"
    generator_version = "1.0.0"

    def _failure(self, code: FailureCode, reason: str, request: GenerationRequest | None) -> GenerationResult:
        return GenerationResult.failure(code=code, reason=reason, request=request)

    @staticmethod
    def _config(request: GenerationRequest) -> tuple[MaskConfig, bool]:
        options = request.options
        if options.namespace == "default":
            if options.values:
                raise MaskContractError("default MASK options namespace must be empty")
            return MaskConfig(), False
        if options.namespace != "mask" or options.version != 1:
            raise MaskContractError("MASK options require namespace mask and version 1")
        allowed = {"symmetry", "mutation", "offset_x", "offset_y", "occupancy_floor_pct", "occupancy_ceiling_pct"}
        values = options.values
        if set(values) - allowed:
            raise MaskContractError("MASK options contain an unsupported field")
        kwargs: dict[str, object] = {}
        if "symmetry" in values:
            kwargs["symmetry"] = SymmetryMode.parse(values["symmetry"])
        for key in ("mutation", "offset_x", "offset_y", "occupancy_floor_pct", "occupancy_ceiling_pct"):
            if key in values:
                value = values[key]
                if isinstance(value, bool) or not isinstance(value, int):
                    raise MaskContractError(f"MASK option {key} must be an integer")
                kwargs[key] = value
        return MaskConfig(**kwargs), "symmetry" in values  # type: ignore[arg-type]

    @staticmethod
    def _family(request: GenerationRequest, geometry_rng: DeterministicRNG) -> TemplateFamily:
        if request.style is None:
            selected = geometry_rng.child("family-selection").choice(FAMILY_NAMES)
            return TemplateFamily(selected)
        try:
            return TemplateFamily(request.style)
        except (TypeError, ValueError) as exc:
            raise MaskContractError("style must be one of the ten supported MASK families") from exc

    def generate_candidate(self, request: GenerationRequest, rng: DeterministicRNG | None = None) -> MaskCandidate | GenerationResult:
        if not isinstance(request, GenerationRequest):
            return self._failure(FailureCode.INVALID_REQUEST, "MASK generation requires a GenerationRequest", None)
        if request.generator_mode != GeneratorMode.MASK.value:
            return self._failure(FailureCode.INVALID_REQUEST, "mask-sprite accepts only MASK mode", request)
        if request.theme is not None:
            return self._failure(FailureCode.INVALID_REQUEST, "theme is unsupported by MASK V1", request)
        stream = DeterministicRNG(request.seed) if rng is None else rng
        if not isinstance(stream, DeterministicRNG):
            return self._failure(FailureCode.INVALID_REQUEST, "MASK generation requires the project DeterministicRNG", request)
        if stream.domain != "root":
            return self._failure(FailureCode.INVALID_REQUEST, "supplied RNG must be the canonical root stream", request)
        if stream.stage_seeds() != DeterministicRNG(request.seed).stage_seeds():
            return self._failure(FailureCode.INVALID_REQUEST, "supplied RNG is incoherent with the request seed", request)
        try:
            config, explicit_symmetry = self._config(request)
            width, height = request.resolve_dimensions()
            palette = request.resolve_palette_subset()
            base_geometry = stream.stage_rng("geometry")
            family = self._family(request, base_geometry)
            if not explicit_symmetry:
                config = replace(config, symmetry=preferred_symmetry(family))
        except (TypeError, ValueError, ColorUsageContractError, MaskContractError) as exc:
            message = str(exc).split("\n", 1)[0]
            return self._failure(FailureCode.INVALID_REQUEST, message, request)

        retry_seeds: dict[str, str] = {}
        for attempt in range(MAX_ATTEMPTS):
            retry_seeds[str(attempt)] = stream.retry_seed(attempt)
            try:
                attempt_rng = stream.retry_rng(attempt)
                definition = template_for(
                    family,
                    width,
                    height,
                    config.offset_x,
                    config.offset_y,
                    config.symmetry,
                )
                mask = resolve_mask(definition, attempt_rng.stage_rng("geometry"), config)
                colorized = colorize_with_roles(mask, palette, attempt_rng.stage_rng("colorization"))
                result = GenerationResult.success(
                    request=request,
                    width=width,
                    height=height,
                    logical_grid=colorized.cells,
                    generator_mode=GeneratorMode.MASK.value,
                    generator_id=self.generator_id,
                    generator_version=self.generator_version,
                    seed=request.seed,
                    rng_algorithm=RNG_ALGORITHM,
                    provenance={"stage_seeds": stream.stage_seeds(), "retry_seeds": dict(retry_seeds)},
                )
                return MaskCandidate(result, mask, family, attempt, palette, colorized.roles, colorized.role_assignments)
            except (TypeError, ValueError, MaskContractError, ResultContractError):
                continue
        return self._failure(FailureCode.RETRY_EXHAUSTED, "bounded MASK generation attempts exhausted", request)

    def generate(self, request: GenerationRequest, rng: DeterministicRNG | None = None) -> GenerationResult:
        """Return only a complete validated M02 result or an explicit failure."""
        candidate = self.generate_candidate(request, rng)
        return candidate.result if isinstance(candidate, MaskCandidate) else candidate


def family_names() -> tuple[str, ...]:
    return FAMILY_NAMES
