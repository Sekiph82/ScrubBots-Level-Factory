"""Deterministic explicit engine router and opt-in fallback AUTO mode."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType

from ...core import DeterministicRNG, FailureCode, GenerationRequest, GenerationResult, GeneratorMode
from ...core.request import LegacyGenerationRequest
from ...quality import QualityPolicy, evaluate_grid, logical_grid_hash
from ..mask import MaskCandidate, MaskSpriteGenerator
from ..rules import RuleCandidate, RuleShapeGenerator
from ..wfc import WFCCandidate, WFCGenerator
from .hybrid import HybridCandidate, HybridGenerator, _child_request, _stage_seed


def _freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class AutoAttempt:
    mode: str
    stage_seed: str
    result_digest: str | None
    engine_id: str | None
    engine_version: str | None
    failure_code: str | None

    def as_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "stage_seed": self.stage_seed,
            "result_digest": self.result_digest,
            "engine_id": self.engine_id,
            "engine_version": self.engine_version,
            "failure_code": self.failure_code,
        }


@dataclass(frozen=True, slots=True)
class AutoCandidate:
    result: GenerationResult
    selected_mode: str
    candidate_order: tuple[str, ...]
    attempts: tuple[AutoAttempt, ...]
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "attempts", tuple(self.attempts))
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def auto_metadata(self) -> Mapping[str, object]:
        return self.metadata


class GeneratorRouter:
    """Route explicit modes without fallback; AUTO fallback is opt-in."""

    def __init__(self, mask_generator=None, rules_generator=None, wfc_generator=None, hybrid_generator=None) -> None:
        self.mask_generator = mask_generator or MaskSpriteGenerator()
        self.rules_generator = rules_generator or RuleShapeGenerator()
        self.wfc_generator = wfc_generator or WFCGenerator()
        self.hybrid_generator = hybrid_generator or HybridGenerator(self.mask_generator, self.rules_generator, self.wfc_generator)

    @staticmethod
    def _failure(code: FailureCode, reason: str, request: GenerationRequest | None) -> GenerationResult:
        return GenerationResult.failure(code=code, reason=reason[:512], request=request)

    @staticmethod
    def _auto_config(request: GenerationRequest) -> tuple[tuple[str, ...], Mapping[str, object], bool]:
        options = request.options
        if options.namespace != "auto" or options.version != 1:
            raise ValueError("AUTO options require namespace auto and version 1")
        allowed = {"candidates", "configs", "fallback_on_failure", "evaluator_guided"}
        if set(options.values) - allowed:
            raise ValueError("AUTO options contain an unsupported field")
        raw_candidates = options.values.get("candidates", (GeneratorMode.MASK.value, GeneratorMode.RULES.value))
        if not isinstance(raw_candidates, (list, tuple)) or not raw_candidates:
            raise ValueError("AUTO candidates must be a non-empty ordered list")
        candidates = tuple(raw_candidates)
        explicit = {GeneratorMode.MASK.value, GeneratorMode.RULES.value, GeneratorMode.WFC.value, GeneratorMode.HYBRID.value}
        if any(type(value) is not str or value not in explicit for value in candidates) or len(set(candidates)) != len(candidates):
            raise ValueError("AUTO candidates must be unique explicit generator modes")
        configs = options.values.get("configs", {})
        if not isinstance(configs, Mapping) or any(key not in explicit or not isinstance(value, Mapping) for key, value in configs.items()):
            raise ValueError("AUTO configs must map explicit modes to child configs")
        for mode, config in configs.items():
            if set(config) - {"style", "theme", "generator_options"}:
                raise ValueError(f"AUTO child config for {mode} contains an unsupported field")
            for key in ("style", "theme"):
                if key in config and (config[key] is not None and type(config[key]) is not str):
                    raise ValueError(f"AUTO child config {mode}.{key} must be a string")
            if "generator_options" in config and not isinstance(config["generator_options"], Mapping):
                raise ValueError("AUTO child generator_options must be a mapping")
        fallback = options.values.get("fallback_on_failure", False)
        if type(fallback) is not bool:
            raise ValueError("AUTO fallback_on_failure must be boolean")
        if "evaluator_guided" in options.values:
            policy = options.values["evaluator_guided"]
            if not isinstance(policy, Mapping) or set(policy) != {"version", "proposal_budget", "quality_policy"}:
                raise ValueError("AUTO evaluator_guided requires exactly version, proposal_budget, and quality_policy")
            if type(policy["version"]) is not int or policy["version"] != 1:
                raise ValueError("AUTO evaluator_guided version must be 1")
            if type(policy["proposal_budget"]) is not int or not 2 <= policy["proposal_budget"] <= 8:
                raise ValueError("AUTO evaluator proposal_budget must be an integer in 2..8")
            quality_policy = policy["quality_policy"]
            if not isinstance(quality_policy, Mapping):
                raise ValueError("AUTO evaluator quality_policy must be a mapping")
            allowed_quality = set(QualityPolicy().as_dict())
            if set(quality_policy) != allowed_quality:
                raise ValueError("AUTO evaluator quality_policy requires the exact versioned M07 policy fields")
            try:
                QualityPolicy(**dict(quality_policy))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"AUTO evaluator quality_policy is invalid: {exc}") from exc
        return candidates, configs, fallback

    def _engine(self, mode: str):
        return {
            GeneratorMode.MASK.value: self.mask_generator,
            GeneratorMode.RULES.value: self.rules_generator,
            GeneratorMode.WFC.value: self.wfc_generator,
            GeneratorMode.HYBRID.value: self.hybrid_generator,
        }[mode]

    def _auto_child(self, outer: GenerationRequest, mode: str, seed: str, width: int, height: int, palette: tuple[str, ...], config: Mapping[str, object]) -> GenerationRequest:
        options = config.get("generator_options") if isinstance(config, Mapping) else None
        style = config.get("style") if isinstance(config.get("style"), str) else None
        theme = config.get("theme") if isinstance(config.get("theme"), str) else None
        return _child_request(outer, mode, seed, width, height, palette, style=style, theme=theme, options=options if isinstance(options, Mapping) else None)

    def _auto(self, request: GenerationRequest, rng: DeterministicRNG) -> AutoCandidate | GenerationResult:
        try:
            candidates, configs, fallback = self._auto_config(request)
            width, height = request.resolve_dimensions()
            palette = request.resolve_palette_subset()
        except (TypeError, ValueError) as exc:
            return self._failure(FailureCode.INVALID_REQUEST, str(exc), request)
        if "evaluator_guided" in request.options.values:
            return self._auto_evaluator_guided(request, rng, candidates, configs, fallback)
        selected_index = rng.child("auto/selection").randbelow(len(candidates))
        selected = candidates[selected_index]
        order = (candidates[selected_index:], candidates[:selected_index])
        attempt_modes = tuple(value for group in order for value in group) if fallback else (selected,)
        attempts: list[AutoAttempt] = []
        for attempt_index, mode in enumerate(attempt_modes):
            seed = _stage_seed(rng, f"auto/{mode}/{attempt_index}")
            child = self._auto_child(request, mode, seed, width, height, palette, configs.get(mode, {}))
            child_result_or_candidate = self._engine(mode).generate_candidate(child, DeterministicRNG(seed))
            child_result = child_result_or_candidate.result if isinstance(child_result_or_candidate, (MaskCandidate, RuleCandidate, WFCCandidate, HybridCandidate)) else child_result_or_candidate
            success = isinstance(child_result, GenerationResult) and child_result.is_success
            attempts.append(AutoAttempt(mode, seed, child_result.digest() if success else None, child_result.generator_id if success else None, child_result.generator_version if success else None, None if success else (child_result.failure_code.value if isinstance(child_result, GenerationResult) and child_result.failure_code else "GENERATION_FAILED")))
            if not success:
                if not fallback:
                    return self._failure(FailureCode.GENERATION_FAILED, f"AUTO selected {mode} failed: {child_result.failure_reason if isinstance(child_result, GenerationResult) else 'GENERATION_FAILED'}", request)
                continue
            result = GenerationResult.success(request=request, width=width, height=height, logical_grid=child_result.logical_grid, generator_mode=GeneratorMode.AUTO.value, generator_id=child_result.generator_id, generator_version=child_result.generator_version, seed=request.seed, rng_algorithm=child_result.rng_algorithm, provenance={"stage_seeds": rng.stage_seeds(), "retry_seeds": {str(index): rng.retry_seed(index) for index in range(attempt_index + 1)}})
            metadata = {
                "schema": "scrubbots-auto-metadata",
                "version": 1,
                "candidate_order": list(candidates),
                "initial_selection": selected,
                "fallback_on_failure": fallback,
                "attempts": [attempt.as_dict() for attempt in attempts],
                "selected_engine_id": result.generator_id,
                "selected_engine_version": result.generator_version,
            }
            return AutoCandidate(result, mode, candidates, tuple(attempts), metadata)
        return self._failure(FailureCode.RETRY_EXHAUSTED, f"AUTO candidates exhausted: {','.join(attempt.mode + ':' + (attempt.failure_code or 'FAILED') for attempt in attempts)}", request)

    @staticmethod
    def _guided_rank(result: GenerationResult, report) -> tuple[object, ...]:
        metrics = report.analysis.metrics if report.analysis is not None else None
        return (
            0 if report.accepted else 1,
            len(report.rejection_codes),
            metrics.tiny_region_count if metrics else 1 << 30,
            metrics.isolated_occupied_count if metrics else 1 << 30,
            abs(metrics.occupied_ratio - 0.45) if metrics else 1.0,
            -metrics.aggregate_symmetry_score if metrics else 0.0,
            logical_grid_hash(result.width, result.height, result.logical_grid),
        )

    def _auto_evaluator_guided(self, request, rng, candidates, configs, fallback):
        policy_config = json.loads(request.canonical_json())["generator_options"]["values"]["evaluator_guided"]
        budget = policy_config["proposal_budget"]
        quality_policy = QualityPolicy(**dict(policy_config["quality_policy"]))
        width, height = request.resolve_dimensions()
        palette = request.resolve_palette_subset()
        attempts: list[dict[str, object]] = []
        valid: list[tuple[tuple[object, ...], int, GenerationResult, object]] = []
        result_seeds: dict[str, str] = {}
        for index in range(budget):
            mode = candidates[index % len(candidates)]
            seed = rng.child(f"evaluator-guided/proposal/{index}").next_bytes(32).hex()
            result_seeds[str(index)] = rng.retry_seed(index)
            child = self._auto_child(request, mode, seed, width, height, palette, configs.get(mode, {}))
            proposed = self._engine(mode).generate_candidate(child, DeterministicRNG(seed))
            result = proposed.result if isinstance(proposed, (MaskCandidate, RuleCandidate, WFCCandidate, HybridCandidate)) else proposed
            if not isinstance(result, GenerationResult) or not result.is_success:
                failure = result.failure_code.value if isinstance(result, GenerationResult) and result.failure_code else "GENERATION_FAILED"
                attempts.append({"index": index, "mode": mode, "seed": seed, "result": None, "result_digest": None, "quality": None, "failure_code": failure})
                continue
            report = evaluate_grid(result.width, result.height, result.logical_grid, policy=quality_policy)
            result_dict = result.canonical_dict()
            entry = {
                "index": index, "mode": mode, "seed": seed,
                "result": result_dict, "result_digest": result.digest(),
                "quality": report.as_dict(), "failure_code": None,
            }
            attempts.append(entry)
            valid.append((self._guided_rank(result, report), index, result, report))
        accepted = [item for item in valid if item[3].accepted]
        if not accepted:
            return self._failure(FailureCode.QUALITY_REJECTED, "evaluator-guided proposals produced no M07-accepted candidate", request)
        _, winner_index, winner, winner_report = min(accepted, key=lambda item: item[0])
        final = GenerationResult.success(
            request=request, width=winner.width, height=winner.height, logical_grid=winner.logical_grid,
            generator_mode=GeneratorMode.AUTO.value, generator_id=winner.generator_id,
            generator_version=winner.generator_version, seed=request.seed, rng_algorithm=winner.rng_algorithm,
            provenance={"stage_seeds": rng.stage_seeds(), "retry_seeds": result_seeds},
        )
        policy_digest = hashlib.sha256(json.dumps(dict(policy_config), ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        metadata = {
            "schema": "scrubbots-evaluator-guided-metadata", "version": 1,
            "request_digest": request.digest(), "policy": dict(policy_config), "policy_digest": policy_digest,
            "candidate_order": list(candidates), "fallback_on_failure": fallback,
            "attempts": attempts, "selected_index": winner_index,
            "selected_result_digest": winner.digest(),
            "selected_grid_hash": logical_grid_hash(winner.width, winner.height, winner.logical_grid),
            "selected_quality": winner_report.as_dict(),
            "selected_engine_id": final.generator_id, "selected_engine_version": final.generator_version,
            "selection_class": "TEST",
        }
        return AutoCandidate(final, attempts[winner_index]["mode"], candidates, (), metadata)

    def generate_candidate(self, request: GenerationRequest, rng: DeterministicRNG | None = None):
        if not isinstance(request, (GenerationRequest, LegacyGenerationRequest)):
            return self._failure(FailureCode.INVALID_REQUEST, "router requires a GenerationRequest", None)
        stream = DeterministicRNG(request.seed) if rng is None else rng
        if not isinstance(stream, DeterministicRNG) or stream.domain != "root" or stream.stage_seeds() != DeterministicRNG(request.seed).stage_seeds():
            return self._failure(FailureCode.INVALID_REQUEST, "supplied RNG must be the canonical root stream", request)
        if request.generator_mode == GeneratorMode.AUTO.value:
            return self._auto(request, stream)
        try:
            return self._engine(request.generator_mode).generate_candidate(request, stream)
        except KeyError:
            return self._failure(FailureCode.INVALID_REQUEST, "router mode is unsupported", request)

    def generate(self, request: GenerationRequest, rng: DeterministicRNG | None = None) -> GenerationResult:
        candidate = self.generate_candidate(request, rng)
        return candidate.result if isinstance(candidate, (MaskCandidate, RuleCandidate, WFCCandidate, HybridCandidate, AutoCandidate)) else candidate
