"""Offline overlapping-pattern Wave Function Collapse generator."""

from collections.abc import Mapping

from ...contracts import ColorUsageContractError, CANONICAL_PALETTE
from ...core import (
    DeterministicRNG,
    FailureCode,
    GenerationRequest,
    GenerationResult,
    GeneratorMode,
    RNG_ALGORITHM,
    ResultContractError,
)
from .exemplar import canonical_palette_mapping
from .model import Exemplar, ExemplarRegistry, WFCAttemptRecord, WFCConfig, WFCCandidate, WFCContractError
from .patterns import extract_pattern_table
from .solver import WFCContradiction, solve_pattern_table


class WFCGenerator:
    """Project-owned, deterministic overlapping-pattern WFC implementation."""

    generator_id = "wfc-overlap"
    generator_version = "1.0.0"

    def __init__(self, registry: ExemplarRegistry | None = None) -> None:
        self._registry = ExemplarRegistry() if registry is None else registry
        if not isinstance(self._registry, ExemplarRegistry):
            raise WFCContractError("WFC generator registry must be an ExemplarRegistry")

    @property
    def registry(self) -> ExemplarRegistry:
        return self._registry

    @staticmethod
    def _failure(code: FailureCode, reason: str, request: GenerationRequest | None) -> GenerationResult:
        return GenerationResult.failure(code=code, reason=reason, request=request)

    @staticmethod
    def _config(request: GenerationRequest) -> WFCConfig:
        options = request.options
        if options.namespace != "wfc" or options.version != 1:
            raise WFCContractError("WFC options require namespace wfc and version 1")
        allowed = {
            "pattern_size", "input_periodic", "output_periodic", "allow_rotations",
            "allow_reflections", "experimental_n4", "max_attempts", "palette_mapping",
        }
        if set(options.values) - allowed:
            raise WFCContractError("WFC options contain an unsupported field")
        raw_mapping = options.values.get("palette_mapping", {})
        if not isinstance(raw_mapping, Mapping):
            raise WFCContractError("palette_mapping must be a source-to-target mapping")
        pairs: list[tuple[str, str]] = []
        for source_id, target_id in raw_mapping.items():
            if type(source_id) is not str or type(target_id) is not str:
                raise WFCContractError("palette_mapping IDs must be strings")
            pairs.append((source_id, target_id))
        return WFCConfig(
            pattern_size=options.values.get("pattern_size", 2),  # type: ignore[arg-type]
            input_periodic=options.values.get("input_periodic", False),  # type: ignore[arg-type]
            output_periodic=options.values.get("output_periodic", False),  # type: ignore[arg-type]
            allow_rotations=options.values.get("allow_rotations", False),  # type: ignore[arg-type]
            allow_reflections=options.values.get("allow_reflections", False),  # type: ignore[arg-type]
            experimental_n4=options.values.get("experimental_n4", False),  # type: ignore[arg-type]
            max_attempts=options.values.get("max_attempts", 4),  # type: ignore[arg-type]
            palette_mapping=tuple(pairs),
        )

    def _select_exemplar(self, request: GenerationRequest) -> Exemplar:
        if request.style is not None:
            exemplar = self._registry.get(request.style)
        else:
            eligible = self._registry.eligible()
            if len(eligible) != 1:
                raise WFCContractError("WFC requests without style require exactly one eligible exemplar")
            exemplar = eligible[0]
        if exemplar.ownership not in {"SYNTHETIC_TEST_ONLY", "OWNER_APPROVED"}:
            raise WFCContractError("exemplar is not eligible for WFC generation")
        return exemplar

    def generate_candidate(self, request: GenerationRequest, rng: DeterministicRNG | None = None) -> WFCCandidate | GenerationResult:
        if not isinstance(request, GenerationRequest):
            return self._failure(FailureCode.INVALID_REQUEST, "WFC generation requires a GenerationRequest", None)
        if request.generator_mode != GeneratorMode.WFC.value:
            return self._failure(FailureCode.INVALID_REQUEST, "wfc-overlap accepts only WFC mode", request)
        if request.theme is not None:
            return self._failure(FailureCode.INVALID_REQUEST, "theme is unsupported by WFC V1", request)
        stream = DeterministicRNG(request.seed) if rng is None else rng
        if not isinstance(stream, DeterministicRNG):
            return self._failure(FailureCode.INVALID_REQUEST, "WFC generation requires the project DeterministicRNG", request)
        if stream.domain != "root":
            return self._failure(FailureCode.INVALID_REQUEST, "supplied RNG must be the canonical root stream", request)
        if stream.stage_seeds() != DeterministicRNG(request.seed).stage_seeds():
            return self._failure(FailureCode.INVALID_REQUEST, "supplied RNG is incoherent with the request seed", request)
        try:
            config = self._config(request)
            width, height = request.resolve_dimensions()
            target_palette = request.resolve_palette_subset()
            exemplar = self._select_exemplar(request)
            mapping = canonical_palette_mapping(exemplar, target_palette, config.palette_mapping)
            table = extract_pattern_table(exemplar, config, target_palette)
        except (TypeError, ValueError, ColorUsageContractError, WFCContractError) as exc:
            return self._failure(FailureCode.INVALID_REQUEST, str(exc).split("\n", 1)[0], request)

        retry_seeds: dict[str, str] = {}
        contradiction_history: list[WFCAttemptRecord] = []
        for attempt in range(config.max_attempts):
            retry_seeds[str(attempt)] = stream.retry_seed(attempt)
            try:
                outcome = solve_pattern_table(
                    table, width, height, stream.retry_rng(attempt).child("wfc/solve"), config.output_periodic
                )
                used = tuple(sorted(set(outcome.logical_grid), key=lambda value: int(value[1:])))
                if used != target_palette:
                    raise WFCContradiction("MISSING_TARGET_COLOR", (0, 0), "solved output does not use the complete requested palette")
                metadata = {
                    "schema": "scrubbots-wfc-metadata",
                    "version": 1,
                    "exemplar_id": exemplar.exemplar_id,
                    "provenance_identity": exemplar.provenance_identity,
                    "pattern_size": config.pattern_size,
                    "input_periodic": config.input_periodic,
                    "output_periodic": config.output_periodic,
                    "allow_rotations": config.allow_rotations,
                    "allow_reflections": config.allow_reflections,
                    "experimental_n4": config.experimental_n4,
                    "max_attempts": config.max_attempts,
                    "source_palette": list(exemplar.source_palette),
                    "target_palette": list(target_palette),
                    "palette_mapping": [[source, target] for source, target in mapping],
                    "extracted_pattern_count": table.raw_extracted_window_count,
                    "raw_extracted_window_count": table.raw_extracted_window_count,
                    "transformed_observation_count": table.transformed_observation_count,
                    "unique_pattern_count": len(table.patterns),
                    "pattern_table_digest": table.digest,
                    "attempt": attempt,
                    "contradiction_history": [record.as_dict() for record in contradiction_history],
                    "placement_dimensions": {"width": outcome.placement_width, "height": outcome.placement_height},
                    "output_dimensions": {"width": width, "height": height},
                    "observations": outcome.observations,
                    "propagation_steps": outcome.propagation_steps,
                }
                result = GenerationResult.success(
                    request=request,
                    width=width,
                    height=height,
                    logical_grid=outcome.logical_grid,
                    generator_mode=GeneratorMode.WFC.value,
                    generator_id=self.generator_id,
                    generator_version=self.generator_version,
                    seed=request.seed,
                    rng_algorithm=RNG_ALGORITHM,
                    provenance={"stage_seeds": stream.stage_seeds(), "retry_seeds": dict(retry_seeds)},
                )
                return WFCCandidate(result, exemplar, config, outcome.logical_grid, metadata, table, attempt, tuple(contradiction_history))
            except WFCContradiction as exc:
                contradiction_history.append(WFCAttemptRecord(attempt, exc.code, exc.placement, exc.detail))
            except (TypeError, ValueError, ResultContractError) as exc:
                contradiction_history.append(WFCAttemptRecord(attempt, "CONTRACT_FAILURE", (0, 0), "bounded WFC contract rejection"))
        summary = ";".join(record.compact() for record in contradiction_history)
        reason = f"bounded WFC generation attempts exhausted [{summary}]"
        return self._failure(FailureCode.RETRY_EXHAUSTED, reason[:512], request)

    def generate(self, request: GenerationRequest, rng: DeterministicRNG | None = None) -> GenerationResult:
        candidate = self.generate_candidate(request, rng)
        return candidate.result if isinstance(candidate, WFCCandidate) else candidate
