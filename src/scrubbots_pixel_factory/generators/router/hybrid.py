"""Offline deterministic composition of the accepted M03--M05 engines."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
from types import MappingProxyType
from typing import Any

from ...contracts import CANONICAL_PALETTE, ColorUsageContractError
from ...core import (
    DeterministicRNG,
    FailureCode,
    GenerationRequest,
    GenerationResult,
    GeneratorOptions,
    GeneratorMode,
    RNG_ALGORITHM,
    ResultContractError,
)
from ..mask import MaskCandidate, MaskSpriteGenerator, SymmetryMode
from ..mask.engine import symmetry_orbits
from ..rules import RuleShapeGenerator
from ..rules.colorize import color_component_sizes as rule_color_component_sizes, colorize_canvas
from ..rules.model import RuleCandidate, RuleCanvas, RuleContractError
from ..wfc import WFCGenerator, WFCCandidate


HYBRID_ENGINE_ID = "hybrid-compose"
HYBRID_ENGINE_VERSION = "1.0.0"
MAX_HYBRID_ATTEMPTS = 8


class HybridStrategy(str, Enum):
    MASK_GEOMETRY_RULE_COLOR_REGIONS = "MASK_GEOMETRY_RULE_COLOR_REGIONS"
    RULE_GEOMETRY_MASK_SYMMETRY = "RULE_GEOMETRY_MASK_SYMMETRY"
    RULE_BASE_WFC_DETAIL = "RULE_BASE_WFC_DETAIL"
    MASK_BASE_WFC_DETAIL = "MASK_BASE_WFC_DETAIL"

    @classmethod
    def values(cls) -> tuple[str, ...]:
        return (
            cls.MASK_GEOMETRY_RULE_COLOR_REGIONS,
            cls.RULE_GEOMETRY_MASK_SYMMETRY,
            cls.RULE_BASE_WFC_DETAIL,
            cls.MASK_BASE_WFC_DETAIL,
        )


def _freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _grid_digest(grid: tuple[str, ...]) -> str:
    return _digest_bytes("\n".join(grid).encode("ascii"))


def _topology_digest(occupied: set[int] | frozenset[int], width: int, height: int) -> str:
    return _digest_bytes(bytes(1 if index in occupied else 0 for index in range(width * height)))


def _stage_seed(root: DeterministicRNG, path: str) -> str:
    # The derived stream is used only to derive a seed. Engines always receive
    # a fresh root stream made from that seed, never this child stream.
    return root.child(path).next_bytes(32).hex()


def _child_request(
    outer: GenerationRequest,
    mode: str,
    seed: str,
    width: int,
    height: int,
    palette: tuple[str, ...],
    *,
    style: str | None,
    theme: str | None,
    options: Mapping[str, object] | None,
) -> GenerationRequest:
    return GenerationRequest(
        outer.difficulty,
        seed,
        mode,
        width=width,
        height=height,
        style=style,
        theme=theme,
        palette_subset=palette,
        generator_options=options,
    )


def _result_digest(result: GenerationResult) -> str:
    return result.digest()


@dataclass(frozen=True, slots=True)
class HybridStageMetadata:
    stage_index: int
    stage_name: str
    stage_kind: str
    derived_seed: str
    child_request_digest: str
    child_request: Mapping[str, object]
    engine_id: str | None
    engine_version: str | None
    child_result_digest: str | None
    failure_code: str | None
    geometry_digest: str | None
    extra: Mapping[str, object]

    def __post_init__(self) -> None:
        if self.stage_index < 0 or not self.stage_name or not self.stage_kind:
            raise ValueError("hybrid stage identity is invalid")
        object.__setattr__(self, "child_request", _freeze(self.child_request))
        object.__setattr__(self, "extra", _freeze(self.extra))

    @property
    def stage_seed(self) -> str:
        return self.derived_seed

    def as_dict(self) -> dict[str, object]:
        return {
            "stage_index": self.stage_index,
            "stage_name": self.stage_name,
            "stage_kind": self.stage_kind,
            "derived_seed": self.derived_seed,
            "child_request_digest": self.child_request_digest,
            "child_request": _thaw(self.child_request),
            "engine_id": self.engine_id,
            "engine_version": self.engine_version,
            "child_result_digest": self.child_result_digest,
            "failure_code": self.failure_code,
            "geometry_digest": self.geometry_digest,
            "extra": _thaw(self.extra),
        }


@dataclass(frozen=True, slots=True)
class HybridCandidate:
    result: GenerationResult
    strategy: str
    stages: tuple[HybridStageMetadata, ...]
    logical_grid: tuple[str, ...]
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "stages", tuple(self.stages))
        object.__setattr__(self, "logical_grid", tuple(self.logical_grid))
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def hybrid_metadata(self) -> Mapping[str, object]:
        return self.metadata


def _stage_record(
    index: int,
    name: str,
    kind: str,
    seed: str,
    request: GenerationRequest,
    candidate: object,
    extra: Mapping[str, object] | None = None,
) -> HybridStageMetadata:
    result = candidate.result if isinstance(candidate, (MaskCandidate, RuleCandidate, WFCCandidate)) else candidate
    result_ok = isinstance(result, GenerationResult) and result.is_success
    return HybridStageMetadata(
        index,
        name,
        kind,
        seed,
        request.digest(),
        request.canonical_dict(),
        getattr(result, "generator_id", None) if result_ok else None,
        getattr(result, "generator_version", None) if result_ok else None,
        _result_digest(result) if result_ok else None,
        None if result_ok else (result.failure_code.value if isinstance(result, GenerationResult) and result.failure_code else "STAGE_FAILED"),
        _candidate_geometry_digest(candidate) if result_ok else None,
        extra or {},
    )


def _candidate_geometry_digest(candidate: object) -> str | None:
    if isinstance(candidate, MaskCandidate):
        return _topology_digest(
            {index for index, value in enumerate(candidate.mask.foreground_cells) if value},
            candidate.mask.width,
            candidate.mask.height,
        )
    if isinstance(candidate, RuleCandidate):
        return candidate.canvas.geometry_digest()
    if isinstance(candidate, WFCCandidate):
        return _grid_digest(candidate.logical_grid)
    return None


def _request_from_canonical(value: object) -> GenerationRequest:
    if not isinstance(value, Mapping):
        raise ValueError("INVALID_STAGE_METADATA: child request is not a mapping")
    try:
        typed_seed = value["seed"]
        if not isinstance(typed_seed, Mapping) or typed_seed.get("type") not in {"int", "string"}:
            raise ValueError
        options = value["generator_options"]
        if not isinstance(options, Mapping):
            raise ValueError
        return GenerationRequest(
            value["difficulty"], typed_seed["value"], value["generator_mode"],
            width=value.get("width"), height=value.get("height"), style=value.get("style"),
            theme=value.get("theme"), palette_subset=value.get("palette_subset"),
            generator_options=GeneratorOptions(options["namespace"], options["version"], options["values"]),
            schema_version=value.get("schema_version", 1),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("INVALID_STAGE_METADATA: child request cannot be reconstructed") from exc


def _record_from_metadata(value: object) -> HybridStageMetadata:
    if not isinstance(value, Mapping):
        raise ValueError("INVALID_STAGE_METADATA: stage record is not a mapping")
    try:
        return HybridStageMetadata(
            value["stage_index"], value["stage_name"], value["stage_kind"], value["derived_seed"],
            value["child_request_digest"], value["child_request"], value.get("engine_id"),
            value.get("engine_version"), value.get("child_result_digest"), value.get("failure_code"),
            value.get("geometry_digest"), value.get("extra", {}),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("INVALID_STAGE_METADATA: malformed stage record") from exc


def _stage_failure(candidate: object) -> GenerationResult | None:
    if isinstance(candidate, GenerationResult) and not candidate.is_success:
        return candidate
    return None


def _mask_occupied(candidate: MaskCandidate) -> set[int]:
    return {index for index, value in enumerate(candidate.mask.foreground_cells) if value}


def _canvas_from_occupied(width: int, height: int, occupied: set[int], label: str) -> RuleCanvas:
    canvas = RuleCanvas(width, height)
    canvas.mark_many(occupied, label)
    return canvas


def _colorize_geometry(canvas: RuleCanvas, palette: tuple[str, ...], rng: DeterministicRNG) -> tuple[str, ...]:
    return colorize_canvas(canvas, palette, rng, min_region_size=2).cells


def _validate_final(
    grid: tuple[str, ...],
    width: int,
    height: int,
    palette: tuple[str, ...],
    expected_occupied: set[int],
    *,
    base_color: str,
) -> None:
    if len(grid) != width * height:
        raise ValueError("DIMENSION_DRIFT")
    if any(cell not in CANONICAL_PALETTE.ids for cell in grid):
        raise ValueError("PALETTE_DRIFT")
    if set(grid) != set(palette):
        raise ValueError("PALETTE_DRIFT")
    occupied = {index for index, cell in enumerate(grid) if cell != base_color}
    if occupied != expected_occupied:
        raise ValueError("TOPOLOGY_DESTROYED")
    components = rule_color_component_sizes(grid, width, height)
    if any(size < 2 for sizes in components.values() for size in sizes):
        raise ValueError("SINGLETON_COLOR_REGION")


class HybridGenerator:
    """Compose accepted engines while keeping each child invocation canonical."""

    generator_id = HYBRID_ENGINE_ID
    generator_version = HYBRID_ENGINE_VERSION

    def __init__(
        self,
        mask_generator: MaskSpriteGenerator | None = None,
        rules_generator: RuleShapeGenerator | None = None,
        wfc_generator: WFCGenerator | None = None,
    ) -> None:
        self.mask_generator = mask_generator or MaskSpriteGenerator()
        self.rules_generator = rules_generator or RuleShapeGenerator()
        self.wfc_generator = wfc_generator or WFCGenerator()

    @staticmethod
    def _failure(code: FailureCode, reason: str, request: GenerationRequest | None) -> GenerationResult:
        return GenerationResult.failure(code=code, reason=reason[:512], request=request)

    @staticmethod
    def _options(request: GenerationRequest) -> Mapping[str, object]:
        options = request.options
        if options.namespace != "hybrid" or options.version != 1:
            raise RuleContractError("HYBRID options require namespace hybrid and version 1")
        allowed = {
            "strategy", "mask_style", "rules_style", "wfc_exemplar_id", "mask_options",
            "rules_options", "wfc_options", "mask_symmetry", "max_attempts",
        }
        if set(options.values) - allowed:
            raise RuleContractError("HYBRID options contain an unsupported field")
        strategy = options.values.get("strategy")
        if type(strategy) is not str or strategy not in HybridStrategy.values():
            raise RuleContractError("HYBRID strategy is unsupported")
        attempts = options.values.get("max_attempts", 4)
        if isinstance(attempts, bool) or not isinstance(attempts, int) or not 1 <= attempts <= MAX_HYBRID_ATTEMPTS:
            raise RuleContractError("HYBRID max_attempts must be bounded to 1..8")
        if strategy in {HybridStrategy.RULE_BASE_WFC_DETAIL, HybridStrategy.MASK_BASE_WFC_DETAIL}:
            exemplar_id = options.values.get("wfc_exemplar_id")
            if type(exemplar_id) is not str or not exemplar_id:
                raise RuleContractError("WFC-detail HYBRID strategies require wfc_exemplar_id")
        for key in ("mask_style", "rules_style", "wfc_exemplar_id"):
            if key in options.values and type(options.values[key]) is not str:
                raise RuleContractError(f"HYBRID option {key} must be a string")
        if "mask_symmetry" in options.values:
            SymmetryMode.parse(options.values["mask_symmetry"])
        for key in ("mask_options", "rules_options", "wfc_options"):
            if key in options.values and not isinstance(options.values[key], Mapping):
                raise RuleContractError(f"{key} must be a generator-options mapping")
        return options.values

    @staticmethod
    def _nested_options(value: object, default: Mapping[str, object]) -> Mapping[str, object]:
        return value if isinstance(value, Mapping) else default

    @staticmethod
    def _validate_nested_options(value: Mapping[str, object], namespace: str, allowed: set[str]) -> None:
        if set(value) != {"namespace", "version", "values"} or value.get("namespace") != namespace or value.get("version") != 1 or not isinstance(value.get("values"), Mapping):
            raise RuleContractError(f"{namespace} nested options require namespace {namespace} and version 1")
        if set(value["values"]) - allowed:  # type: ignore[index]
            raise RuleContractError(f"{namespace} nested options contain an unsupported field")

    def _run_stage(
        self,
        outer: GenerationRequest,
        width: int,
        height: int,
        palette: tuple[str, ...],
        root: DeterministicRNG,
        strategy: str,
        attempt: int,
        index: int,
        name: str,
        mode: str,
        *,
        style: str | None,
        theme: str | None,
        options: Mapping[str, object] | None,
    ) -> tuple[object, HybridStageMetadata]:
        seed = _stage_seed(root, f"hybrid/{strategy}/{attempt}/{index}/{name}")
        child = _child_request(outer, mode, seed, width, height, palette, style=style, theme=theme, options=options)
        child_rng = DeterministicRNG(seed)
        if mode == GeneratorMode.MASK.value:
            candidate = self.mask_generator.generate_candidate(child, child_rng)
        elif mode == GeneratorMode.RULES.value:
            candidate = self.rules_generator.generate_candidate(child, child_rng)
        else:
            candidate = self.wfc_generator.generate_candidate(child, child_rng)
        extra: dict[str, object] = {}
        if isinstance(candidate, MaskCandidate):
            extra["family"] = candidate.family.value
            extra["mask_digest"] = _candidate_geometry_digest(candidate)
        elif isinstance(candidate, RuleCandidate):
            extra["recipe_id"] = candidate.recipe.recipe_id
            extra["canvas_digest"] = candidate.canvas.geometry_digest()
            extra["region_digest"] = candidate.canvas.region_digest()
        elif isinstance(candidate, WFCCandidate):
            extra["exemplar_id"] = candidate.exemplar.exemplar_id
            extra["pattern_table_digest"] = candidate.pattern_table.digest
            extra["attempt"] = candidate.attempt
        return candidate, _stage_record(index, name, mode, seed, child, candidate, extra)

    def _compose_attempt(
        self,
        request: GenerationRequest,
        width: int,
        height: int,
        palette: tuple[str, ...],
        root: DeterministicRNG,
        strategy: str,
        attempt: int,
        values: Mapping[str, object],
    ) -> tuple[tuple[str, ...], set[int], tuple[HybridStageMetadata, ...], str, Mapping[str, set[int]]]:
        mask_options = self._nested_options(values.get("mask_options"), {"namespace": "mask", "version": 1, "values": {"symmetry": "HORIZONTAL"}})
        rules_options = self._nested_options(values.get("rules_options"), {"namespace": "rules", "version": 1, "values": {}})
        wfc_options = self._nested_options(values.get("wfc_options"), {"namespace": "wfc", "version": 1, "values": {}})
        self._validate_nested_options(mask_options, "mask", {"symmetry", "mutation", "offset_x", "offset_y", "occupancy_floor_pct", "occupancy_ceiling_pct"})
        self._validate_nested_options(rules_options, "rules", {"min_color_region_size", "max_color_dominance_pct"})
        self._validate_nested_options(wfc_options, "wfc", {"pattern_size", "input_periodic", "output_periodic", "allow_rotations", "allow_reflections", "experimental_n4", "max_attempts", "palette_mapping"})
        mask_style = values.get("mask_style") if isinstance(values.get("mask_style"), str) else None
        rules_style = values.get("rules_style") if isinstance(values.get("rules_style"), str) else None
        stages: list[HybridStageMetadata] = []
        if strategy == HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS:
            mask, record = self._run_stage(request, width, height, palette, root, strategy, attempt, 0, "MASK_GEOMETRY", GeneratorMode.MASK.value, style=mask_style, theme=None, options=mask_options)
            stages.append(record)
            failure = _stage_failure(mask)
            if failure or not isinstance(mask, MaskCandidate):
                raise RuntimeError("STAGE_FAILED:MASK_GEOMETRY")
            occupied = _mask_occupied(mask)
            canvas = _canvas_from_occupied(width, height, occupied, "MASK_FOREGROUND")
            colors = _colorize_geometry(canvas, palette, DeterministicRNG(_stage_seed(root, f"hybrid/{strategy}/{attempt}/1/RULE_COLOR_REGIONS")))
            stage_seed = _stage_seed(root, f"hybrid/{strategy}/{attempt}/1/RULE_COLOR_REGIONS")
            synthetic = GenerationRequest(request.difficulty, stage_seed, GeneratorMode.RULES.value, width=width, height=height, palette_subset=palette, generator_options=rules_options)
            stages.append(HybridStageMetadata(1, "RULE_COLOR_REGIONS", "COMPOSITION", stage_seed, synthetic.digest(), synthetic.canonical_dict(), "rule-colorize", "1.0.0", _grid_digest(colors), None, canvas.geometry_digest(), {"canvas_digest": canvas.geometry_digest()}))
            return colors, occupied, tuple(stages), _topology_digest(occupied, width, height), {"before": occupied, "after": occupied, "final": occupied}
        if strategy == HybridStrategy.RULE_GEOMETRY_MASK_SYMMETRY:
            rules, record = self._run_stage(request, width, height, palette, root, strategy, attempt, 0, "RULE_GEOMETRY", GeneratorMode.RULES.value, style=rules_style, theme=None, options=rules_options)
            stages.append(record)
            if _stage_failure(rules) or not isinstance(rules, RuleCandidate):
                raise RuntimeError("STAGE_FAILED:RULE_GEOMETRY")
            raw = set(rules.canvas.occupied)
            symmetry_value = values.get("mask_symmetry", SymmetryMode.HORIZONTAL.value)
            symmetry = SymmetryMode.parse(symmetry_value)
            if symmetry is SymmetryMode.ASYMMETRIC:
                raise ValueError("TOPOLOGY_DESTROYED:MASK_SYMMETRY_ASYMMETRIC")
            occupied = set(raw)
            for orbit in symmetry_orbits(width, height, symmetry):
                if set(orbit) & raw:
                    occupied.update(orbit)
            canvas = _canvas_from_occupied(width, height, occupied, "MASK_SYMMETRY")
            color_seed = _stage_seed(root, f"hybrid/{strategy}/{attempt}/1/MASK_SYMMETRY_COLOR_REGIONS")
            colors = _colorize_geometry(canvas, palette, DeterministicRNG(color_seed))
            synthetic = GenerationRequest(request.difficulty, color_seed, GeneratorMode.RULES.value, width=width, height=height, palette_subset=palette, generator_options=rules_options)
            stages.append(HybridStageMetadata(1, "MASK_SYMMETRY_COLOR_REGIONS", "COMPOSITION", color_seed, synthetic.digest(), synthetic.canonical_dict(), "mask-symmetry-compose", "1.0.0", _grid_digest(colors), None, canvas.geometry_digest(), {"symmetry": symmetry.value, "before_topology_digest": _topology_digest(raw, width, height), "after_topology_digest": _topology_digest(occupied, width, height)}))
            return colors, occupied, tuple(stages), _topology_digest(occupied, width, height), {"before": raw, "after": occupied, "final": occupied}
        base_mode = GeneratorMode.RULES.value if strategy == HybridStrategy.RULE_BASE_WFC_DETAIL else GeneratorMode.MASK.value
        base_name = "RULE_BASE" if base_mode == GeneratorMode.RULES.value else "MASK_BASE"
        base, base_record = self._run_stage(request, width, height, palette, root, strategy, attempt, 0, base_name, base_mode, style=rules_style if base_mode == GeneratorMode.RULES.value else mask_style, theme=None, options=rules_options if base_mode == GeneratorMode.RULES.value else mask_options)
        stages.append(base_record)
        if _stage_failure(base) or not isinstance(base, (RuleCandidate, MaskCandidate)):
            raise RuntimeError(f"STAGE_FAILED:{base_name}")
        occupied = set(base.canvas.occupied) if isinstance(base, RuleCandidate) else _mask_occupied(base)
        base_grid = tuple(base.logical_grid if isinstance(base, RuleCandidate) else base.result.logical_grid or ())
        exemplar_id = values["wfc_exemplar_id"]
        wfc_values = dict(wfc_options.get("values", {})) if isinstance(wfc_options.get("values"), Mapping) else {}
        # Leave the mapping absent unless the caller supplied one. M05 then
        # performs its canonical source-palette -> outer-palette mapping.
        wfc_child_options = {"namespace": "wfc", "version": 1, "values": wfc_values}
        detail, detail_record = self._run_stage(request, width, height, palette, root, strategy, attempt, 1, "WFC_DETAIL", GeneratorMode.WFC.value, style=exemplar_id, theme=None, options=wfc_child_options)
        stages.append(detail_record)
        if _stage_failure(detail) or not isinstance(detail, WFCCandidate):
            raise RuntimeError("STAGE_FAILED:WFC_DETAIL")
        detail_record = stages[-1]
        detail_extra = dict(detail_record.extra)
        detail_extra["palette_mapping"] = [[source, target] for source, target in detail.wfc_metadata["palette_mapping"]]
        stages[-1] = HybridStageMetadata(
            detail_record.stage_index, detail_record.stage_name, detail_record.stage_kind,
            detail_record.derived_seed, detail_record.child_request_digest, detail_record.child_request,
            detail_record.engine_id, detail_record.engine_version, detail_record.child_result_digest,
            detail_record.failure_code, detail_record.geometry_digest, detail_extra,
        )
        base_color = palette[0]
        final = list(base_grid)
        for index in sorted(occupied):
            if detail.logical_grid[index] != base_color:
                final[index] = detail.logical_grid[index]
        return tuple(final), occupied, tuple(stages), _topology_digest(occupied, width, height), {"before": occupied, "after": occupied, "final": occupied}

    def generate_candidate(self, request: GenerationRequest, rng: DeterministicRNG | None = None) -> HybridCandidate | GenerationResult:
        if not isinstance(request, GenerationRequest):
            return self._failure(FailureCode.INVALID_REQUEST, "HYBRID generation requires a GenerationRequest", None)
        if request.generator_mode != GeneratorMode.HYBRID.value:
            return self._failure(FailureCode.INVALID_REQUEST, "hybrid-compose accepts only HYBRID mode", request)
        stream = DeterministicRNG(request.seed) if rng is None else rng
        if not isinstance(stream, DeterministicRNG) or stream.domain != "root":
            return self._failure(FailureCode.INVALID_REQUEST, "supplied RNG must be the canonical root stream", request)
        if stream.stage_seeds() != DeterministicRNG(request.seed).stage_seeds():
            return self._failure(FailureCode.INVALID_REQUEST, "supplied RNG is incoherent with the request seed", request)
        try:
            values = self._options(request)
            width, height = request.resolve_dimensions()
            palette = request.resolve_palette_subset()
        except (TypeError, ValueError, ColorUsageContractError, RuleContractError) as exc:
            return self._failure(FailureCode.INVALID_REQUEST, str(exc).split("\n", 1)[0], request)
        strategy = values["strategy"]
        attempts = int(values.get("max_attempts", 4))
        failures: list[str] = []
        for attempt in range(attempts):
            try:
                grid, occupied, stages, topology_digest, topology_evidence = self._compose_attempt(request, width, height, palette, stream, strategy, attempt, values)
                _validate_final(grid, width, height, palette, occupied, base_color=palette[0])
                result = GenerationResult.success(request=request, width=width, height=height, logical_grid=grid, generator_mode=GeneratorMode.HYBRID.value, generator_id=self.generator_id, generator_version=self.generator_version, seed=request.seed, rng_algorithm=RNG_ALGORITHM, provenance={"stage_seeds": stream.stage_seeds(), "retry_seeds": {str(index): stream.retry_seed(index) for index in range(attempt + 1)}})
                metadata = {
                    "schema": "scrubbots-hybrid-metadata",
                    "version": 1,
                    "strategy": strategy,
                    "outer_master_seed": request.seed,
                    "resolved_dimensions": {"width": width, "height": height},
                    "resolved_palette": list(palette),
                    "outer_attempt": attempt,
                    "stages": [stage.as_dict() for stage in stages],
                    "final_topology_digest": topology_digest,
                    "final_logical_grid_digest": _grid_digest(grid),
                    "final_result_digest": result.digest(),
                    "topology_evidence": {
                        name: [1 if index in cells else 0 for index in range(width * height)]
                        for name, cells in topology_evidence.items()
                    },
                }
                return HybridCandidate(result, strategy, stages, grid, metadata)
            except (RuntimeError, ValueError, TypeError, ResultContractError, RuleContractError) as exc:
                failures.append(f"{attempt}:{str(exc).split(':', 1)[0]}")
        return self._failure(FailureCode.RETRY_EXHAUSTED, f"bounded HYBRID generation attempts exhausted [{';'.join(failures)}]", request)

    def replay_candidate(self, request: GenerationRequest, candidate: HybridCandidate) -> HybridCandidate:
        """Replay every recorded engine/helper stage and verify its evidence."""
        if not isinstance(request, GenerationRequest) or not isinstance(candidate, HybridCandidate):
            raise ValueError("INVALID_STAGE_METADATA: replay requires a request and HybridCandidate")
        if request.generator_mode != GeneratorMode.HYBRID.value:
            raise ValueError("INVALID_STAGE_METADATA: replay requires HYBRID mode")
        try:
            values = self._options(request)
            metadata = candidate.metadata
            strategy = metadata["strategy"]
            attempt = metadata["outer_attempt"]
            if strategy != values["strategy"] or candidate.strategy != strategy or type(attempt) is not int or attempt < 0:
                raise ValueError
            if metadata["outer_master_seed"] != request.seed:
                raise ValueError
            width, height = request.resolve_dimensions()
            palette = request.resolve_palette_subset()
            if tuple(metadata["resolved_palette"]) != palette or metadata["resolved_dimensions"]["width"] != width or metadata["resolved_dimensions"]["height"] != height:
                raise ValueError
            raw_stages = metadata["stages"]
            records = tuple(_record_from_metadata(value) for value in raw_stages)
        except (KeyError, TypeError, ValueError, RuleContractError, ColorUsageContractError) as exc:
            raise ValueError("INVALID_STAGE_METADATA: outer metadata is corrupted") from exc
        expected_layout = {
            HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS: (("MASK_GEOMETRY", "MASK"), ("RULE_COLOR_REGIONS", "COMPOSITION")),
            HybridStrategy.RULE_GEOMETRY_MASK_SYMMETRY: (("RULE_GEOMETRY", "RULES"), ("MASK_SYMMETRY_COLOR_REGIONS", "COMPOSITION")),
            HybridStrategy.RULE_BASE_WFC_DETAIL: (("RULE_BASE", "RULES"), ("WFC_DETAIL", "WFC")),
            HybridStrategy.MASK_BASE_WFC_DETAIL: (("MASK_BASE", "MASK"), ("WFC_DETAIL", "WFC")),
        }.get(strategy)
        if expected_layout is None or len(records) != len(expected_layout):
            raise ValueError("INVALID_STAGE_METADATA: stage order is invalid")
        if tuple((record.stage_name, record.stage_kind) for record in records) != expected_layout:
            raise ValueError("INVALID_STAGE_METADATA: stage order/name/kind mismatch")
        if tuple(stage.as_dict() for stage in candidate.stages) != tuple(record.as_dict() for record in records):
            raise ValueError("INVALID_STAGE_METADATA: candidate and serialized stage metadata differ")

        root = DeterministicRNG(request.seed)
        replayed: list[dict[str, object]] = []
        replay_records: list[HybridStageMetadata] = []
        for index, record in enumerate(records):
            expected_seed = _stage_seed(root, f"hybrid/{strategy}/{attempt}/{index}/{record.stage_name}")
            if record.stage_index != index or record.derived_seed != expected_seed:
                raise ValueError("INVALID_STAGE_METADATA: stage seed/order mismatch")
            child = _request_from_canonical(record.child_request)
            if child.digest() != record.child_request_digest or child.seed != record.derived_seed:
                raise ValueError("INVALID_STAGE_METADATA: child request digest mismatch")
            runtime: dict[str, object]
            if record.stage_kind == "COMPOSITION":
                if not replayed:
                    raise ValueError("INVALID_STAGE_METADATA: composition has no input stage")
                previous = replayed[0]
                if record.stage_name == "RULE_COLOR_REGIONS":
                    mask = previous["candidate"]
                    if not isinstance(mask, MaskCandidate):
                        raise ValueError("INVALID_STAGE_METADATA: MASK composition input is invalid")
                    occupied = _mask_occupied(mask)
                    canvas = _canvas_from_occupied(width, height, occupied, "MASK_FOREGROUND")
                    grid = _colorize_geometry(canvas, palette, DeterministicRNG(record.derived_seed))
                    runtime = {"candidate": None, "grid": grid, "occupied": occupied, "engine_id": "rule-colorize", "engine_version": "1.0.0", "result_digest": _grid_digest(grid), "geometry_digest": canvas.geometry_digest(), "extra": {"canvas_digest": canvas.geometry_digest()}}
                else:
                    rules = previous["candidate"]
                    if not isinstance(rules, RuleCandidate):
                        raise ValueError("INVALID_STAGE_METADATA: symmetry composition input is invalid")
                    extra = record.extra
                    symmetry = SymmetryMode.parse(extra["symmetry"])
                    raw = set(rules.canvas.occupied)
                    occupied = set(raw)
                    for orbit in symmetry_orbits(width, height, symmetry):
                        if set(orbit) & raw:
                            occupied.update(orbit)
                    canvas = _canvas_from_occupied(width, height, occupied, "MASK_SYMMETRY")
                    grid = _colorize_geometry(canvas, palette, DeterministicRNG(record.derived_seed))
                    runtime = {"candidate": None, "grid": grid, "occupied": occupied, "engine_id": "mask-symmetry-compose", "engine_version": "1.0.0", "result_digest": _grid_digest(grid), "geometry_digest": canvas.geometry_digest(), "extra": {"symmetry": symmetry.value, "before_topology_digest": _topology_digest(raw, width, height), "after_topology_digest": _topology_digest(occupied, width, height)}}
            else:
                engine = {"MASK": self.mask_generator, "RULES": self.rules_generator, "WFC": self.wfc_generator}.get(record.stage_kind)
                if engine is None:
                    raise ValueError("INVALID_STAGE_METADATA: unknown stage engine")
                value = engine.generate_candidate(child, DeterministicRNG(record.derived_seed))
                if isinstance(value, GenerationResult) or not isinstance(value, (MaskCandidate, RuleCandidate, WFCCandidate)):
                    raise ValueError("INVALID_STAGE_METADATA: recorded stage no longer succeeds")
                extra: dict[str, object] = {}
                if isinstance(value, MaskCandidate):
                    extra = {"family": value.family.value, "mask_digest": _candidate_geometry_digest(value)}
                elif isinstance(value, RuleCandidate):
                    extra = {"recipe_id": value.recipe.recipe_id, "canvas_digest": value.canvas.geometry_digest(), "region_digest": value.canvas.region_digest()}
                else:
                    extra = {"exemplar_id": value.exemplar.exemplar_id, "pattern_table_digest": value.pattern_table.digest, "attempt": value.attempt, "palette_mapping": [[source, target] for source, target in value.wfc_metadata["palette_mapping"]]}
                runtime = {"candidate": value, "grid": value.result.logical_grid, "occupied": _mask_occupied(value) if isinstance(value, MaskCandidate) else set(value.canvas.occupied) if isinstance(value, RuleCandidate) else set(), "engine_id": value.result.generator_id, "engine_version": value.result.generator_version, "result_digest": value.result.digest(), "geometry_digest": _candidate_geometry_digest(value), "extra": extra}
                if record.stage_name == "WFC_DETAIL" and replayed:
                    base = replayed[0]
                    base_candidate = base["candidate"]
                    if not isinstance(base_candidate, (MaskCandidate, RuleCandidate)) or not isinstance(value, WFCCandidate):
                        raise ValueError("INVALID_STAGE_METADATA: WFC detail input is invalid")
                    occupied = _mask_occupied(base_candidate) if isinstance(base_candidate, MaskCandidate) else set(base_candidate.canvas.occupied)
                    base_grid = tuple(base["grid"])
                    final = list(base_grid)
                    for cell_index in sorted(occupied):
                        if value.logical_grid[cell_index] != palette[0]:
                            final[cell_index] = value.logical_grid[cell_index]
                    runtime["grid"] = tuple(final)
                    runtime["occupied"] = occupied
                    runtime["geometry_digest"] = _grid_digest(value.logical_grid)
            actual_extra = runtime["extra"]
            required_extra = {"family", "mask_digest"} if record.stage_kind == "MASK" else {"recipe_id", "canvas_digest", "region_digest"} if record.stage_kind == "RULES" else {"exemplar_id", "pattern_table_digest", "attempt", "palette_mapping"} if record.stage_kind == "WFC" else {"canvas_digest"} if record.stage_name == "RULE_COLOR_REGIONS" else {"symmetry", "before_topology_digest", "after_topology_digest"}
            if not required_extra.issubset(set(record.extra)) or any(record.extra[key] != actual_extra.get(key) for key in required_extra):
                raise ValueError("INVALID_STAGE_METADATA: engine-specific metadata mismatch")
            for key in ("engine_id", "engine_version", "child_result_digest", "geometry_digest"):
                if getattr(record, key) != runtime.get({"engine_id": "engine_id", "engine_version": "engine_version", "child_result_digest": "result_digest", "geometry_digest": "geometry_digest"}[key]):
                    raise ValueError(f"INVALID_STAGE_METADATA: {key} mismatch")
            replayed.append(runtime)
            replay_records.append(record)

        final_grid = tuple(replayed[-1]["grid"])
        final_occupied = set(replayed[-1]["occupied"])
        final_topology_digest = _topology_digest(final_occupied, width, height)
        if metadata["final_topology_digest"] != final_topology_digest or metadata["final_logical_grid_digest"] != _grid_digest(final_grid):
            raise ValueError("INVALID_STAGE_METADATA: final digest mismatch")
        _validate_final(final_grid, width, height, palette, final_occupied, base_color=palette[0])
        result = GenerationResult.success(request=request, width=width, height=height, logical_grid=final_grid, generator_mode=GeneratorMode.HYBRID.value, generator_id=self.generator_id, generator_version=self.generator_version, seed=request.seed, rng_algorithm=RNG_ALGORITHM, provenance={"stage_seeds": root.stage_seeds(), "retry_seeds": {str(index): root.retry_seed(index) for index in range(attempt + 1)}})
        if metadata["final_result_digest"] != result.digest() or candidate.result.digest() != result.digest() or tuple(candidate.logical_grid) != final_grid:
            raise ValueError("INVALID_STAGE_METADATA: final result digest mismatch")
        return HybridCandidate(result, strategy, tuple(replay_records), final_grid, dict(metadata))

    def generate(self, request: GenerationRequest, rng: DeterministicRNG | None = None) -> GenerationResult:
        candidate = self.generate_candidate(request, rng)
        return candidate.result if isinstance(candidate, HybridCandidate) else candidate


def reproduce_hybrid(generator: HybridGenerator, request: GenerationRequest, candidate: HybridCandidate) -> HybridCandidate | GenerationResult:
    """Replay and verify every recorded engine and composition stage."""
    return generator.replay_candidate(request, candidate)
