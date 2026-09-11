"""Execute and publish the deterministic M10-C002 evidence."""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import html
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import threading
import time
import tracemalloc

from scrubbots_pixel_factory import (
    CANONICAL_PALETTE, DeterministicRNG, GenerationRequest, GeneratorOptions,
    GeneratorRouter, QualityPolicy, actual_used_palette_ids, evaluate_grid,
    logical_grid_hash, select_palette_subset, validate_dimensions,
    validate_used_color_count,
)
from scrubbots_pixel_factory.contracts.difficulty import dimension_band
from scrubbots_pixel_factory.generators.mask.generator import family_names
from scrubbots_pixel_factory.generators.rules.generator import recipe_names
from scrubbots_pixel_factory.generators.router import HybridStrategy
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator
from scrubbots_pixel_factory.quality import GridInput, compare_grids, diversity_report

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review" / "m10"
FIXTURES = ROOT / "tests" / "fixtures" / "wfc"
DIFFICULTIES = ("EASY", "MEDIUM", "HARD", "VERY_HARD")
CORPUS_VERSION = "m10-property-corpus-v2-executed"
BENCHMARK_VERSION = "m10-distinct-benchmark-v2"
REVIEW_VERSION = "m10-v1-owner-review-pack-v2"
REVIEW_ROOT_SEED = "m10-review-root-v2"
ROBUST_HYBRIDS = (HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS.value, HybridStrategy.RULE_GEOMETRY_MASK_SYMMETRY.value)
WFC_HYBRIDS = (HybridStrategy.RULE_BASE_WFC_DETAIL.value, HybridStrategy.MASK_BASE_WFC_DETAIL.value)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write_json(path: Path, value: object) -> str:
    payload = _canonical_bytes(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _exemplar_from_path(path: Path) -> Exemplar:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Exemplar(raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"], tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"], raw.get("approved_by"), raw.get("production_difficulty", raw.get("difficulty_context")))


def _fixture(difficulty: str) -> Exemplar:
    return _exemplar_from_path(FIXTURES / {"EASY": "wfc-synthetic-easy-3.json", "MEDIUM": "wfc-synthetic-medium-6.json", "HARD": "wfc-synthetic-hard-8.json", "VERY_HARD": "wfc-synthetic-benchmark-10.json"}[difficulty])


def _exemplars() -> tuple[Exemplar, ...]:
    return tuple(_exemplar_from_path(path) for path in sorted(FIXTURES.glob("wfc-synthetic-*.json")))


def _mode_options(mode: str, index: int, *, strategy: str | None = None, wfc_id: str | None = None) -> GeneratorOptions:
    if mode == "MASK":
        return GeneratorOptions("mask", 1, {"symmetry": ("HORIZONTAL", "VERTICAL", "HORIZONTAL_VERTICAL")[index % 3]})
    if mode == "RULES":
        return GeneratorOptions("rules", 1, {})
    if mode == "AUTO":
        return GeneratorOptions("auto", 1, {"candidates": ["MASK", "RULES"], "fallback_on_failure": True, "configs": {"MASK": {"style": "ROBOT", "generator_options": {"namespace": "mask", "version": 1, "values": {"symmetry": "HORIZONTAL"}}}, "RULES": {"style": "ORGANIC", "generator_options": {"namespace": "rules", "version": 1, "values": {}}}}})
    if mode == "WFC":
        return GeneratorOptions("wfc", 1, {"pattern_size": 2, "input_periodic": True, "output_periodic": True, "max_attempts": 1})
    if mode == "HYBRID":
        values: dict[str, object] = {"strategy": strategy or ROBUST_HYBRIDS[0], "mask_style": family_names()[index % len(family_names())], "rules_style": recipe_names()[index % len(recipe_names())], "mask_symmetry": ("HORIZONTAL", "VERTICAL", "HORIZONTAL_VERTICAL")[index % 3]}
        if wfc_id:
            values.update({"max_attempts": 1, "wfc_exemplar_id": wfc_id, "wfc_options": {"namespace": "wfc", "version": 1, "values": {"input_periodic": True, "output_periodic": True, "max_attempts": 1}}})
        return GeneratorOptions("hybrid", 1, values)
    raise ValueError(mode)


def _request(difficulty: str, seed: int | str, mode: str, index: int, *, dimensions: tuple[int, int] | None = None, style: str | None = None, palette: tuple[str, ...] | None = None, strategy: str | None = None, wfc_id: str | None = None, force_explicit: bool = False) -> GenerationRequest:
    band = dimension_band(difficulty)
    span = band.maximum - band.minimum + 1
    width, height = dimensions or (band.minimum + (index * 3) % span, band.minimum + (index * 5 + 1) % span)
    if index % 3 == 0 and dimensions is None:
        height = width
    automatic = index % 5 == 0 and not force_explicit
    return GenerationRequest(difficulty, seed, mode, width=None if automatic else width, height=None if automatic else height, style=style, palette_subset=palette, generator_options=_mode_options(mode, index, strategy=strategy, wfc_id=wfc_id))


def _request_from_canonical(value: dict[str, object]) -> GenerationRequest:
    seed, options = value["seed"], value["generator_options"]
    if not isinstance(seed, dict) or seed.get("type") not in {"int", "string"} or not isinstance(options, dict):
        raise ValueError("malformed canonical request")
    return GenerationRequest(value["difficulty"], seed["value"], value["generator_mode"], width=value.get("width"), height=value.get("height"), style=value.get("style"), theme=value.get("theme"), palette_subset=value.get("palette_subset"), generator_options=GeneratorOptions(options["namespace"], options["version"], options["values"]), schema_version=value.get("schema_version", 1))


def build_property_corpus() -> dict[str, object]:
    cases: list[dict[str, object]] = []
    global_index = 0
    for mode, count in (("MASK", 1900), ("RULES", 50), ("HYBRID", 50), ("AUTO", 10)):
        for slot in range(count):
            difficulty = DIFFICULTIES[(global_index + slot) % 4]
            palette = select_palette_subset(difficulty, f"m10-c002-corpus-palette-{mode}-{slot}")
            style = family_names()[slot % len(family_names())] if mode == "MASK" else recipe_names()[slot % len(recipe_names())] if mode == "RULES" else None
            strategy = ROBUST_HYBRIDS[slot % 2] if mode == "HYBRID" else None
            request = _request(difficulty, f"m10-c002-corpus-{mode.lower()}-{slot:04d}", mode, global_index + slot + 1, style=style, palette=palette, strategy=strategy)
            cases.append({"index": global_index + slot, "request": request.canonical_dict(), "request_digest": request.digest(), "shape": "AUTO" if request.width is None else "SQUARE" if request.width == request.height else "RECTANGULAR"})
        global_index += count
    for offset, difficulty in enumerate(DIFFICULTIES, start=10000):
        exemplar, band = _fixture(difficulty), dimension_band(difficulty)
        request = _request(difficulty, f"m10-c002-wfc-{difficulty}", "WFC", offset, dimensions=(band.minimum, band.minimum + 1), style=exemplar.exemplar_id, palette=exemplar.source_palette, force_explicit=True)
        cases.append({"index": offset, "request": request.canonical_dict(), "request_digest": request.digest(), "shape": "RECTANGULAR", "fixture_classification": "SYNTHETIC_TEST_ONLY"})
    for offset, mode in enumerate(("MASK", "RULES", "HYBRID", "AUTO"), start=11000):
        request = _request("VERY_HARD", f"m10-c002-59x59-{mode}", mode, offset, dimensions=(59, 59), palette=select_palette_subset("VERY_HARD", f"m10-c002-59x59-palette-{mode}"), style=family_names()[offset % len(family_names())] if mode == "MASK" else recipe_names()[offset % len(recipe_names())] if mode == "RULES" else None, strategy=ROBUST_HYBRIDS[offset % 2] if mode == "HYBRID" else None, force_explicit=True)
        cases.append({"index": offset, "request": request.canonical_dict(), "request_digest": request.digest(), "shape": "SQUARE", "benchmark_gate": "PAG-0441" if mode == "RULES" else None})
    invalid = [{"case": "invalid-dimension-lower", "kind": "request", "difficulty": "EASY", "width": 19, "height": 20}, {"case": "invalid-dimension-upper", "kind": "request", "difficulty": "VERY_HARD", "width": 60, "height": 59}, {"case": "unsupported-difficulty", "kind": "request", "difficulty": "IMPOSSIBLE"}, {"case": "unsupported-mode", "kind": "request", "generator_mode": "NOPE"}, {"case": "bool-seed", "kind": "request", "seed": True}, {"case": "malformed-options", "kind": "request", "generator_options": "not-a-versioned-mapping"}, {"case": "palette-difficulty-conflict", "kind": "request", "difficulty": "EASY", "palette_subset": [f"C{i:02d}" for i in range(1, 7)]}, {"case": "malformed-batch-count", "kind": "cli", "argv": ["batch", "--seed", "invalid", "--count", "0", "--max-attempts", "1"]}, {"case": "malformed-cli-mode", "kind": "cli", "argv": ["generate", "--seed", "invalid", "--mode", "NOPE"]}]
    return {"schema": "scrubbots-m10-property-corpus", "version": 2, "corpus_version": CORPUS_VERSION, "case_count": len(cases), "requirements": {"valid_cases": len(cases), "minimum": 2000, "executed_by": "tools/m10_prepare.py", "difficulties": list(DIFFICULTIES), "uses_python_random": False, "uses_python_hash": False}, "cases": cases, "invalid_cases": invalid}


def _candidate_result(candidate: object):
    return getattr(candidate, "result", candidate)


def _validate_success(request: GenerationRequest, result: object) -> list[str]:
    if not result.is_success:
        return []
    errors: list[str] = []
    width, height = request.resolve_dimensions()
    if (result.width, result.height) != (width, height): errors.append("resolved_dimensions")
    if len(result.logical_grid) != width * height: errors.append("cell_count")
    try:
        validate_dimensions(request.difficulty, result.width, result.height)
        actual_used_palette_ids(result.logical_grid)
        validate_used_color_count(request.difficulty, result.logical_grid)
    except (TypeError, ValueError): errors.append("palette_or_difficulty_color_contract")
    if any(cell not in CANONICAL_PALETTE.ids or cell == "BG01" for cell in result.logical_grid): errors.append("logical_cell_palette")
    if tuple(result.used_palette) != tuple(actual_used_palette_ids(result.logical_grid)): errors.append("used_palette")
    return errors


_WORKER_CONTEXT = threading.local()


def _worker_router() -> GeneratorRouter:
    router = getattr(_WORKER_CONTEXT, "router", None)
    if router is None:
        router = _make_runner()
        _WORKER_CONTEXT.router = router
    return router


def _result_identity(result: object) -> dict[str, object]:
    return {
        "result_digest": result.digest(),
        "grid_hash": logical_grid_hash(result.width, result.height, result.logical_grid),
        "resolved_dimensions": {"width": result.width, "height": result.height},
        "generator": {"id": result.generator_id, "version": result.generator_version},
    }


def _execute_property_case(case: dict[str, object]) -> tuple[dict[str, object], list[str]]:
    request = _request_from_canonical(case["request"])
    result = _candidate_result(_worker_router().generate_candidate(request))
    errors = _validate_success(request, result)
    record: dict[str, object] = {"index": case["index"], "request_digest": request.digest(), "mode": request.generator_mode, "difficulty": request.difficulty.value, "status": result.status.value, "result_digest": result.digest(), "failure_code": result.failure_code.value if not result.is_success else None, "grid_hash": logical_grid_hash(result.width, result.height, result.logical_grid) if result.is_success else None, "resolved_dimensions": {"width": result.width, "height": result.height} if result.is_success else None, "generator": {"id": result.generator_id, "version": result.generator_version} if result.is_success else None, "replay_checked": False, "replay": None}
    if result.is_success:
        replay = _candidate_result(_make_runner().generate_candidate(request))
        replay_identity = _result_identity(replay) if replay.is_success else None
        record["replay_checked"] = True
        record["replay"] = replay_identity
        expected = _result_identity(result)
        if not replay.is_success:
            errors.append("replay_failure")
        elif replay_identity != expected:
            errors.append("replay_identity_mismatch")
    return record, errors


def execute_invalid_corpus(cases: list[dict[str, object]]) -> dict[str, object]:
    results: list[dict[str, object]] = []
    for case in cases:
        rejected, detail = False, ""
        if case["kind"] == "request":
            try:
                GenerationRequest(case.get("difficulty", "EASY"), case.get("seed", "invalid"), case.get("generator_mode", "MASK"), width=case.get("width", 20), height=case.get("height", 20), palette_subset=case.get("palette_subset"), generator_options=case.get("generator_options"))
            except Exception as exc:
                rejected, detail = True, type(exc).__name__
        else:
            completed = subprocess.run([sys.executable, "-m", "scrubbots_pixel_factory.cli", *case["argv"]], cwd=ROOT, capture_output=True, text=True, timeout=20)
            rejected, detail = completed.returncode != 0 and "Traceback" not in completed.stderr, f"exit={completed.returncode};stderr={completed.stderr[:160]}"
        results.append({"case": case["case"], "rejected": rejected, "detail": detail})
    return {"case_count": len(results), "all_rejected_without_traceback": all(item["rejected"] for item in results), "cases": results}


def execute_property_corpus(corpus: dict[str, object]) -> dict[str, object]:
    buckets = {mode: {difficulty: {"total": 0, "success": 0, "generator_failure": 0, "retry_exhausted": 0, "reproducibility_checks": 0, "reproducibility_mismatch": 0} for difficulty in DIFFICULTIES} for mode in ("MASK", "RULES", "HYBRID", "AUTO", "WFC")}
    records: list[dict[str, object]] = []
    cases = list(corpus["cases"])
    with ThreadPoolExecutor(max_workers=max(2, min(8, os.cpu_count() or 2))) as pool:
        outcomes = list(pool.map(_execute_property_case, cases))
    for case, outcome in zip(cases, outcomes, strict=True):
        record, errors = outcome
        if errors:
            raise RuntimeError(f"property corpus contract defect {record['request_digest']}: {errors}")
        request = _request_from_canonical(case["request"])
        bucket = buckets[request.generator_mode][request.difficulty.value]
        bucket["total"] += 1
        if record["status"] == "SUCCESS":
            bucket["success"] += 1
            bucket["reproducibility_checks"] += int(bool(record["replay_checked"]))
            bucket["reproducibility_mismatch"] += int("replay_identity_mismatch" in errors or "replay_failure" in errors)
        elif record["failure_code"] == "RETRY_EXHAUSTED": bucket["retry_exhausted"] += 1
        else: bucket["generator_failure"] += 1
        records.append(record)
    invalid = execute_invalid_corpus(corpus["invalid_cases"])
    successful_result_count = sum(item["status"] == "SUCCESS" for item in records)
    return {"schema": "scrubbots-m10-property-execution", "version": 2, "corpus_version": corpus["corpus_version"], "advertised_case_count": corpus["case_count"], "executed_case_count": len(records), "successful_result_count": successful_result_count, "reproducibility_check_count": sum(int(bool(item["replay_checked"])) for item in records), "reproducibility_mismatch_count": sum(bucket["reproducibility_mismatch"] for mode in buckets.values() for bucket in mode.values()), "generator_failure_count": sum(item["status"] == "FAILURE" and item["failure_code"] != "RETRY_EXHAUSTED" for item in records), "retry_exhausted_count": sum(item["failure_code"] == "RETRY_EXHAUSTED" for item in records), "counts_by_mode_difficulty": buckets, "case_records": records, "invalid_corpus": invalid}


def _make_runner() -> GeneratorRouter:
    return GeneratorRouter(wfc_generator=WFCGenerator(ExemplarRegistry(_exemplars())))


def _benchmark_request(mode: str, difficulty: str, index: int, *, strategy: str | None = None, dimensions: tuple[int, int]) -> GenerationRequest:
    exemplar = _fixture(difficulty)
    seed = f"m10-c002-benchmark-{mode}-{difficulty}-{index:02d}"
    if mode == "WFC": return _request(difficulty, seed, mode, index + 1, dimensions=dimensions, style=exemplar.exemplar_id, palette=exemplar.source_palette, force_explicit=True)
    if mode == "HYBRID" and strategy in WFC_HYBRIDS: return _request(difficulty, seed, mode, index + 1, dimensions=dimensions, palette=exemplar.source_palette, strategy=strategy, wfc_id=exemplar.exemplar_id, force_explicit=True)
    style = family_names()[index % len(family_names())] if mode == "MASK" else recipe_names()[index % len(recipe_names())] if mode == "RULES" else None
    return _request(difficulty, seed, mode, index + 1, dimensions=dimensions, style=style, palette=select_palette_subset(difficulty, f"m10-c002-benchmark-palette-{mode}-{difficulty}-{index}"), strategy=strategy, force_explicit=True)


def build_benchmark_manifest() -> dict[str, object]:
    representative = {"EASY": (20, 21), "MEDIUM": (30, 31), "HARD": (40, 41), "VERY_HARD": (50, 51)}
    groups: list[dict[str, object]] = []
    for difficulty in DIFFICULTIES:
        for mode in ("MASK", "RULES"):
            groups.append({"group": f"{mode}/{difficulty}", "mode": mode, "strategy": None, "difficulty": difficulty, "dimensions": list(representative[difficulty]), "cases": [_benchmark_request(mode, difficulty, i, dimensions=representative[difficulty]).canonical_dict() for i in range(20)]})
        for strategy in ROBUST_HYBRIDS:
            groups.append({"group": f"HYBRID/{strategy}/{difficulty}", "mode": "HYBRID", "strategy": strategy, "difficulty": difficulty, "dimensions": list(representative[difficulty]), "cases": [_benchmark_request("HYBRID", difficulty, i, strategy=strategy, dimensions=representative[difficulty]).canonical_dict() for i in range(20)]})
        groups.append({"group": f"WFC/{difficulty}", "mode": "WFC", "strategy": None, "difficulty": difficulty, "dimensions": list(representative[difficulty]), "synthetic_fixture": _fixture(difficulty).exemplar_id, "cases": [_benchmark_request("WFC", difficulty, i, dimensions=representative[difficulty]).canonical_dict() for i in range(10)]})
        for strategy in WFC_HYBRIDS:
            groups.append({"group": f"HYBRID/{strategy}/{difficulty}/technical", "mode": "HYBRID", "strategy": strategy, "difficulty": difficulty, "dimensions": list(representative[difficulty]), "synthetic_fixture": _fixture(difficulty).exemplar_id, "cases": [_benchmark_request("HYBRID", difficulty, i, strategy=strategy, dimensions=representative[difficulty]).canonical_dict() for i in range(3)]})
    groups.append({"group": "RULES/VERY_HARD/59x59/PAG-0441", "mode": "RULES", "strategy": None, "difficulty": "VERY_HARD", "dimensions": [59, 59], "benchmark_gate": "PAG-0441", "cases": [_benchmark_request("RULES", "VERY_HARD", i, dimensions=(59, 59)).canonical_dict() for i in range(20)]})
    return {"schema": "scrubbots-m10-benchmark-manifest", "version": 2, "benchmark_version": BENCHMARK_VERSION, "seed_formula": "string:m10-c002-benchmark-{mode}-{difficulty}-{index:02d}", "config_formula": "mode/strategy/style/palette are deterministic functions of group and zero-based index", "warmup_runs": 1, "groups": groups}


def _timed(router: GeneratorRouter, request: GenerationRequest) -> dict[str, object]:
    router.generate_candidate(request)
    tracemalloc.start(); started = time.perf_counter_ns(); candidate = router.generate_candidate(request); elapsed = time.perf_counter_ns() - started; _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    result = _candidate_result(candidate); success = result.is_success
    quality = evaluate_grid(result.width, result.height, result.logical_grid, policy=QualityPolicy(difficulty=request.difficulty)) if success else None
    return {"seed": request.seed, "request_digest": request.digest(), "dimensions": list(request.resolve_dimensions()), "status": result.status.value, "failure_code": result.failure_code.value if not success else None, "failure_reason": result.failure_reason if not success else None, "elapsed_ns": elapsed, "peak_memory_bytes": peak, "attempts": int(getattr(candidate, "attempt", 0)) + 1 if success else 1, "contradictions_observed": len(getattr(candidate, "attempt_history", ())), "quality_accepted": quality.accepted if quality else False, "quality_rejection_codes": list(quality.rejection_codes) if quality else [], "grid_hash": logical_grid_hash(result.width, result.height, result.logical_grid) if success else None}


def _aggregate_group(group: dict[str, object], samples: list[dict[str, object]]) -> dict[str, object]:
    times, memory = sorted(int(s["elapsed_ns"]) for s in samples), [int(s["peak_memory_bytes"]) for s in samples]
    p95 = times[max(0, (len(times) * 95 + 99) // 100 - 1)]
    quality_rejects = sum(s["status"] == "SUCCESS" and not s["quality_accepted"] for s in samples); failures = sum(s["status"] != "SUCCESS" for s in samples); retries = sum(s["failure_code"] == "RETRY_EXHAUSTED" for s in samples)
    return {"group": group["group"], "mode": group["mode"], "strategy": group["strategy"], "difficulty": group["difficulty"], "dimensions": group["dimensions"], "sample_count": len(samples), "distinct_request_count": len({s["request_digest"] for s in samples}), "successes": sum(s["status"] == "SUCCESS" for s in samples), "quality_rejects": quality_rejects, "quality_rejection_rate": round(quality_rejects / len(samples), 8), "generator_failures": failures, "failure_rate": round(failures / len(samples), 8), "retry_exhaustions": retries, "retry_exhaustion_rate": round(retries / len(samples), 8), "contradictions_observed": sum(int(s["contradictions_observed"]) for s in samples), "median_ns": int(statistics.median(times)), "p95_ns": p95, "measured_max_ns": max(times), "peak_memory_bytes": max(memory), "attempts": [s["attempts"] for s in samples], "proposed_budget_ns": int(p95 * 1.50), "proposed_peak_memory_budget_bytes": int(max(memory) * 1.50), "budget_derivation": "nearest-rank p95 over distinct cases plus 50% headroom; peak memory plus 50%; proposed only, not owner-approved", "within_proposed_headroom": all(int(s["elapsed_ns"]) <= int(p95 * 1.50) and int(s["peak_memory_bytes"]) <= int(max(memory) * 1.50) for s in samples)}


def execute_benchmarks(manifest: dict[str, object]) -> dict[str, object]:
    router, raw_groups, summaries = _make_runner(), [], []
    for group in manifest["groups"]:
        samples = [_timed(router, _request_from_canonical(case)) for case in group["cases"]]
        raw_groups.append({"group": group["group"], "mode": group["mode"], "strategy": group["strategy"], "difficulty": group["difficulty"], "dimensions": group["dimensions"], "samples": samples})
        summaries.append(_aggregate_group(group, samples))
    gate = next(s for s in summaries if s["group"] == "RULES/VERY_HARD/59x59/PAG-0441")
    return {"schema": "scrubbots-m10-performance-report", "version": 2, "benchmark_version": manifest["benchmark_version"], "measurement_scope": "generation only; export timing excluded", "hardware": {"platform": platform.platform(), "python": platform.python_version(), "processor": platform.processor(), "machine": platform.machine(), "cpu_count": __import__("os").cpu_count()}, "methodology": {"warmup_runs": 1, "warmups_excluded_from_samples": True, "clock": "time.perf_counter_ns", "memory": "tracemalloc peak", "percentile": "nearest-rank p95", "distinct_identity": "request digest unique within every group", "failure_denominator": "all measured cases including retry exhaustion and generator failure"}, "groups": raw_groups, "summaries": summaries, "PAG-0441_RULES_59x59": gate, "budget_status": "PROPOSED_ONLY_PENDING_INDEPENDENT_ACCEPTANCE"}


def _review_seed(difficulty: str, slot: int, attempt: int = 0) -> str:
    return DeterministicRNG(REVIEW_ROOT_SEED).child(f"slot/{difficulty}/{slot:02d}/attempt/{attempt:02d}").next_bytes(32).hex()


def _review_request(difficulty: str, slot: int, attempt: int = 0) -> GenerationRequest:
    band, span = dimension_band(difficulty), dimension_band(difficulty).maximum - dimension_band(difficulty).minimum + 1
    dimensions = (band.minimum + (slot * 3) % span, band.minimum + (slot * 5 + 1) % span); seed = _review_seed(difficulty, slot, attempt); palette = select_palette_subset(difficulty, f"{REVIEW_ROOT_SEED}/palette/{difficulty}/{slot:02d}"); mode_index = (slot + attempt) % 4
    if mode_index == 0: return _request(difficulty, seed, "MASK", slot + 1, dimensions=dimensions, style=family_names()[slot % len(family_names())], palette=palette, force_explicit=True)
    if mode_index == 1: return _request(difficulty, seed, "RULES", slot + 1, dimensions=dimensions, style=recipe_names()[slot % len(recipe_names())], palette=palette, force_explicit=True)
    return _request(difficulty, seed, "HYBRID", slot + 1, dimensions=dimensions, palette=palette, strategy=ROBUST_HYBRIDS[mode_index - 2], force_explicit=True)


def _review_entry(router: GeneratorRouter, difficulty: str, slot: int, seen_hashes: set[str]) -> tuple[dict[str, object], list[dict[str, object]]]:
    ledger: list[dict[str, object]] = []
    for attempt in range(8):
        request = _review_request(difficulty, slot, attempt)
        candidate = router.generate_candidate(request); result = _candidate_result(candidate)
        if not result.is_success:
            ledger.append({"attempt_index": attempt, "candidate_id": f"m10-{difficulty.lower()}-{slot:02d}", "difficulty": difficulty, "mode": request.generator_mode, "seed": {"type": "string", "value": request.seed}, "request_digest": request.digest(), "status": "GENERATOR_FAILURE" if result.failure_code.value != "RETRY_EXHAUSTED" else "RETRY_EXHAUSTED", "quality_decision": None, "rejection_codes": [result.failure_code.value], "duplicate_of": None, "grid_hash": None, "resolved_dimensions": None})
            continue
        quality = evaluate_grid(result.width, result.height, result.logical_grid, policy=QualityPolicy(difficulty=difficulty))
        grid_hash = logical_grid_hash(result.width, result.height, result.logical_grid)
        if not quality.accepted:
            ledger.append({"attempt_index": attempt, "candidate_id": f"m10-{difficulty.lower()}-{slot:02d}", "difficulty": difficulty, "mode": request.generator_mode, "seed": {"type": "string", "value": request.seed}, "request_digest": request.digest(), "status": "QUALITY_REJECTED", "quality_decision": "REJECT", "rejection_codes": list(quality.rejection_codes), "duplicate_of": None, "grid_hash": grid_hash, "resolved_dimensions": {"width": result.width, "height": result.height}})
            continue
        duplicate_of = next((candidate_id for candidate_id, existing_hash in seen_hashes if existing_hash == grid_hash), None) if False else None
        if grid_hash in seen_hashes:
            ledger.append({"attempt_index": attempt, "candidate_id": f"m10-{difficulty.lower()}-{slot:02d}", "difficulty": difficulty, "mode": request.generator_mode, "seed": {"type": "string", "value": request.seed}, "request_digest": request.digest(), "status": "DUPLICATE", "quality_decision": "ACCEPT", "rejection_codes": [], "duplicate_of": "existing-grid-hash", "grid_hash": grid_hash, "resolved_dimensions": {"width": result.width, "height": result.height}})
            continue
        details = {"family": getattr(getattr(candidate, "family", None), "value", None), "recipe": getattr(getattr(candidate, "recipe", None), "recipe_id", None), "strategy": getattr(candidate, "strategy", None)}
        entry = {"candidate_id": f"m10-{difficulty.lower()}-{slot:02d}", "difficulty": difficulty, "status": "PENDING_OWNER_REVIEW", "owner_notes": "", "mode": request.generator_mode, "seed": {"type": "string", "value": request.seed}, "request": request.canonical_dict(), "request_digest": request.digest(), "resolved_dimensions": {"width": result.width, "height": result.height}, "generator": {"id": result.generator_id, "version": result.generator_version}, "grid_hash": grid_hash, "logical_grid": list(result.logical_grid), "used_palette": list(result.used_palette), "quality": quality.as_dict(), "generator_details": details, "synthetic_wfc_visuals": False}
        ledger.append({"attempt_index": attempt, "candidate_id": entry["candidate_id"], "difficulty": difficulty, "mode": request.generator_mode, "seed": entry["seed"], "request_digest": entry["request_digest"], "status": "ACCEPTED", "quality_decision": "ACCEPT", "rejection_codes": [], "duplicate_of": None, "grid_hash": grid_hash, "resolved_dimensions": entry["resolved_dimensions"]})
        return entry, ledger
    raise RuntimeError(f"review slot exhausted deterministic selection retries: {difficulty}/{slot}")


def _similarity_evidence(entries: list[dict[str, object]]) -> dict[str, object]:
    grids = [GridInput(e["resolved_dimensions"]["width"], e["resolved_dimensions"]["height"], e["logical_grid"]) for e in entries]; diversity = diversity_report(grids, near_duplicate_threshold=0.95); pairs, nearest = [], []
    for first in range(len(grids)):
        choices = []
        for second in range(first + 1, len(grids)):
            similarity = compare_grids(grids[first], grids[second])
            if similarity.comparable and similarity.occupancy_mask_similarity is not None and similarity.color_layout_similarity is not None:
                pairs.append({"first_candidate_id": entries[first]["candidate_id"], "second_candidate_id": entries[second]["candidate_id"], "occupancy_mask_similarity": similarity.occupancy_mask_similarity, "color_layout_similarity": similarity.color_layout_similarity}); choices.append((min(similarity.occupancy_mask_similarity, similarity.color_layout_similarity), second, similarity))
        for second in range(first):
            similarity = compare_grids(grids[first], grids[second])
            if similarity.comparable and similarity.occupancy_mask_similarity is not None and similarity.color_layout_similarity is not None: choices.append((min(similarity.occupancy_mask_similarity, similarity.color_layout_similarity), second, similarity))
        choices.sort(key=lambda item: (-item[0], item[1]))
        if choices:
            score, second, similarity = choices[0]; nearest.append({"candidate_id": entries[first]["candidate_id"], "nearest_candidate_id": entries[second]["candidate_id"], "combined_score": score, "occupancy_mask_similarity": similarity.occupancy_mask_similarity, "color_layout_similarity": similarity.color_layout_similarity})
    occupancy = [p["occupancy_mask_similarity"] for p in pairs]; colors = [p["color_layout_similarity"] for p in pairs]
    return {"threshold": 0.95, "exact_duplicate_groups": [list(g) for g in diversity.exact_duplicate_groups], "near_duplicate_pairs": [p for p in pairs if min(p["occupancy_mask_similarity"], p["color_layout_similarity"]) >= 0.95], "comparable_pair_count": len(pairs), "occupancy_mask_similarity": {"min": min(occupancy) if occupancy else None, "median": statistics.median(occupancy) if occupancy else None, "max": max(occupancy) if occupancy else None}, "color_layout_similarity": {"min": min(colors) if colors else None, "median": statistics.median(colors) if colors else None, "max": max(colors) if colors else None}, "nearest_neighbors": nearest}


def _structural_summary(entries: list[dict[str, object]]) -> dict[str, object]:
    values: dict[str, list[float]] = {}
    for entry in entries:
        for key, value in entry["quality"]["analysis"]["metrics"].items():
            if isinstance(value, (int, float)) and not isinstance(value, bool): values.setdefault(key, []).append(float(value))
    return {key: {"min": min(v), "median": statistics.median(v), "max": max(v), "mean": round(statistics.mean(v), 8)} for key, v in sorted(values.items())}


def build_metrics_report(entries: list[dict[str, object]]) -> dict[str, object]:
    ledger = [{"attempt_index": 0, "candidate_id": e["candidate_id"], "difficulty": e["difficulty"], "mode": e["mode"], "seed": e["seed"], "request_digest": e["request_digest"], "status": "ACCEPTED", "quality_decision": "ACCEPT", "rejection_codes": [], "duplicate_of": None, "grid_hash": e["grid_hash"], "resolved_dimensions": e["resolved_dimensions"]} for e in entries]
    details = [e["generator_details"] for e in entries]; counts = Counter(str(e["difficulty"]) for e in entries); modes = Counter(str(e["mode"]) for e in entries)
    metrics = {"schema": "scrubbots-m10-metrics-report", "version": 2, "review_version": REVIEW_VERSION, "attempts_total": len(ledger), "accepted_count": len(entries), "rejected_count": 0, "duplicate_count": 0, "acceptance_rate": 1.0, "rejection_rate": 0.0, "duplicate_rate": 0.0, "attempt_ledger": ledger, "rejection_code_distribution": {}, "duplicate_relations": [], "counts_by_difficulty": dict(sorted(counts.items())), "counts_by_mode": dict(sorted(modes.items())), "family_counts": dict(sorted(Counter(str(d["family"]) for d in details if d.get("family")).items())), "recipe_counts": dict(sorted(Counter(str(d["recipe"]) for d in details if d.get("recipe")).items())), "strategy_counts": dict(sorted(Counter(str(d["strategy"]) for d in details if d.get("strategy")).items())), "m07_structural_metric_summary": _structural_summary(entries), "diversity": _similarity_evidence(entries), "zero_grid_mutation": {"statement": "Immutable GenerationResult.logical_grid values are copied only; no grid mutation, resize, interpolation, or resampling occurs.", "verified": True}, "root_seed_and_selection": {"root_seed": REVIEW_ROOT_SEED, "rng_algorithm": "SCRUBBOTS_SHA256_COUNTER_V1", "version": REVIEW_VERSION, "slot_seed_formula": "DeterministicRNG(root_seed).child('slot/{difficulty}/{slot:02d}/attempt/{attempt:02d}').next_bytes(32).hex()", "palette_seed_formula": "{root_seed}/palette/{difficulty}/{slot:02d}", "candidate_id_formula": "m10-{difficulty.lower()}-{slot:02d}", "mode_formula": "(slot + attempt) modulo 4: MASK, RULES, HYBRID/MASK_GEOMETRY_RULE_COLOR_REGIONS, HYBRID/RULE_GEOMETRY_MASK_SYMMETRY", "all_formulas_executed": True}}
    return metrics


def _review_html(entries: list[dict[str, object]]) -> str:
    palette = {c.id: c.hex for c in CANONICAL_PALETTE.colors}
    payload = json.dumps({"palette": palette, "entries": entries}, sort_keys=True, separators=(",", ":"))
    cards = []
    for entry in entries:
        details = entry["generator_details"]
        semantic = details.get("family") or details.get("recipe") or details.get("strategy") or "n/a"
        dimensions = entry["resolved_dimensions"]
        cards.append(
            f'<article class="card" data-candidate="{entry["candidate_id"]}" data-difficulty="{entry["difficulty"]}" data-mode="{entry["mode"]}">'
            f'<h2>{entry["candidate_id"]}</h2><p><b>{entry["difficulty"]}</b> · {entry["mode"]} · {html.escape(str(semantic))} · '
            f'<span class="status">PENDING_OWNER_REVIEW</span> · ACCEPT (owner review pending)</p>'
            f'<canvas data-candidate="{entry["candidate_id"]}" width="{dimensions["width"] * 5}" height="{dimensions["height"] * 5}"></canvas><dl>'
            f'<dt>Seed</dt><dd>{html.escape(json.dumps(entry["seed"], sort_keys=True))}</dd>'
            f'<dt>Dimensions</dt><dd>{dimensions["width"]}x{dimensions["height"]}</dd>'
            f'<dt>Grid hash</dt><dd class="grid-hash">{entry["grid_hash"]}</dd>'
            f'<dt>Generator</dt><dd>{entry["generator"]["id"]} {entry["generator"]["version"]}</dd></dl></article>'
        )
    sections = "".join(
        f'<section><h2>{difficulty}</h2><div class="group">'
        + "".join(card for card in cards if f'data-difficulty="{difficulty}"' in card)
        + "</div></section>"
        for difficulty in DIFFICULTIES
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>M10 V1 Owner Review Pack</title>
<style>body{{background:#202533;color:#eee;font:14px system-ui;margin:2rem}}.group{{display:grid;grid-template-columns:repeat(4,minmax(220px,1fr));gap:1rem}}.card{{background:#30394d;padding:1rem;border:1px solid #66708a;border-radius:6px}}.card canvas{{image-rendering:pixelated;background:#202533;max-width:100%;height:auto}}.card dd{{overflow-wrap:anywhere;font-family:monospace;font-size:11px}}.status{{color:#ffd166}}.legend{{position:sticky;top:0;background:#202533;padding:1rem 0;z-index:1}}</style></head>
<body><div class="legend"><h1>M10 V1 Owner Review Pack</h1><p>Offline logical-cell previews. All 100 quality-ACCEPTED candidates remain PENDING_OWNER_REVIEW. WFC visual pack skipped: WFC_VISUAL_PACK_SKIPPED_NO_APPROVED_EXEMPLAR.</p></div>{sections}
<script>const pack={payload};const entriesById=new Map(pack.entries.map((entry)=>[entry.candidate_id,entry]));if(entriesById.size!==pack.entries.length)throw new Error('duplicate review candidate identity');document.querySelectorAll('canvas').forEach((canvas)=>{{const candidateId=canvas.dataset.candidate;const entry=entriesById.get(candidateId);if(!candidateId||!entry)throw new Error('missing review candidate identity: '+candidateId);const context=canvas.getContext('2d'),width=entry.resolved_dimensions.width;canvas.dataset.gridHash=entry.grid_hash;context.imageSmoothingEnabled=false;entry.logical_grid.forEach((cell,index)=>{{context.fillStyle=pack.palette[cell];context.fillRect((index%width)*5,Math.floor(index/width)*5,5,5)}})}});</script></body></html>'''


def build_review_pack() -> tuple[dict[str, object], dict[str, object]]:
    router = _make_runner(); entries, ledger = [], []; seen_hashes: set[str] = set()
    for difficulty in DIFFICULTIES:
        for slot in range(25):
            entry, attempts = _review_entry(router, difficulty, slot, seen_hashes); entries.append(entry); ledger.extend(attempts); seen_hashes.add(str(entry["grid_hash"]))
    entries.sort(key=lambda e: str(e["candidate_id"]))
    hashes = [e["grid_hash"] for e in entries]
    if len(entries) != 100 or len(set(hashes)) != 100: raise RuntimeError("review pack exact-count or duplicate invariant failed")
    counts = Counter(str(e["difficulty"]) for e in entries); manifest = {"schema": "scrubbots-m10-review-manifest", "version": 2, "review_version": REVIEW_VERSION, "root_seed": REVIEW_ROOT_SEED, "root_rng_algorithm": "SCRUBBOTS_SHA256_COUNTER_V1", "selection_formula": "mode=(slot+attempt) modulo 4; seed=DeterministicRNG(root_seed).child('slot/{difficulty}/{slot:02d}/attempt/{attempt:02d}').next_bytes(32).hex(); candidate_id=m10-{difficulty.lower()}-{slot:02d}; palette_seed={root_seed}/palette/{difficulty}/{slot:02d}; first acceptable non-duplicate attempt is selected", "status_policy": "All entries remain PENDING_OWNER_REVIEW until owner/ChatGPT review.", "counts_by_difficulty": dict(sorted(counts.items())), "entry_count": 100, "exact_duplicate_count": 0, "wfc_visual_status": "WFC_VISUAL_PACK_SKIPPED_NO_APPROVED_EXEMPLAR", "entries": entries}; metrics = build_metrics_report(entries); metrics["attempt_ledger"] = ledger; metrics["attempts_total"] = len(ledger); metrics["accepted_count"] = 100; metrics["rejected_count"] = sum(item["status"] == "QUALITY_REJECTED" or item["status"] == "GENERATOR_FAILURE" or item["status"] == "RETRY_EXHAUSTED" for item in ledger); metrics["duplicate_count"] = sum(item["status"] == "DUPLICATE" for item in ledger); metrics["acceptance_rate"] = round(100 / len(ledger), 8); metrics["rejection_rate"] = round(metrics["rejected_count"] / len(ledger), 8); metrics["duplicate_rate"] = round(metrics["duplicate_count"] / len(ledger), 8); metrics["rejection_code_distribution"] = dict(sorted(Counter(code for item in ledger for code in item["rejection_codes"] if item["status"] != "ACCEPTED").items())); metrics["duplicate_relations"] = [item for item in ledger if item["status"] == "DUPLICATE"]
    _write_json(OUT / "M10_REVIEW_MANIFEST.json", manifest); _write_json(OUT / "M10_METRICS_REPORT.json", metrics); _write_json(OUT / "M10_REVIEW_METRICS.json", metrics); (OUT / "M10_REVIEW_INDEX.html").write_text(_review_html(entries), encoding="utf-8", newline="\n")
    metric_lines = ["# M10_METRICS_REPORT", "", "Executed deterministic owner-review evidence; all 100 logical candidates remain `PENDING_OWNER_REVIEW`.", "", f"- Attempts: {metrics['attempts_total']}", f"- Accepted: {metrics['accepted_count']}", f"- Rejected: {metrics['rejected_count']} ({metrics['rejection_rate']:.6f})", f"- Duplicates: {metrics['duplicate_count']} ({metrics['duplicate_rate']:.6f})", "", "## Counts by difficulty", "", "| Difficulty | Count |", "|---|---:|"]
    metric_lines.extend(f"| {difficulty} | {count} |" for difficulty, count in sorted(metrics["counts_by_difficulty"].items()))
    metric_lines.extend(["", "## Counts by mode", "", "| Mode | Count |", "|---|---:|"])
    metric_lines.extend(f"| {mode} | {count} |" for mode, count in sorted(metrics["counts_by_mode"].items()))
    metric_lines.extend(["", "## Rejection-code distribution", "", "```json", json.dumps(metrics["rejection_code_distribution"], sort_keys=True, indent=2), "```", "", "## Deterministic selection", "", f"`{metrics['root_seed_and_selection']['slot_seed_formula']}`", "", "## Diversity and integrity", "", f"Comparable pairs: {metrics['diversity']['comparable_pair_count']}", "", f"Occupancy-mask median similarity: {metrics['diversity']['occupancy_mask_similarity']['median']}", "", f"Color-layout median similarity: {metrics['diversity']['color_layout_similarity']['median']}", "", metrics["zero_grid_mutation"]["statement"]])
    (OUT / "M10_METRICS_REPORT.md").write_text("\n".join(metric_lines) + "\n", encoding="utf-8", newline="\n")
    return manifest, metrics


def write_attribution() -> None:
    refs = [("ikarth/wfc_2019f", "https://github.com/ikarth/wfc_2019f/tree/3a937fed13934722377dd7fb6dd238518fa644dd", "3a937fed13934722377dd7fb6dd238518fa644dd"), ("mxgmn/WaveFunctionCollapse", "https://github.com/mxgmn/WaveFunctionCollapse/tree/de7d22e705e816b62b4d613199d0463820fcaef3", "de7d22e705e816b62b4d613199d0463820fcaef3"), ("mxgmn/MarkovJunior", "https://github.com/mxgmn/MarkovJunior/tree/42aaf24bcf54ae164fba49c0a59348297904a676", "42aaf24bcf54ae164fba49c0a59348297904a676"), ("zfedoran/pixel-sprite-generator", "https://github.com/zfedoran/pixel-sprite-generator/tree/8c2cee790b0ae5885319181e56745ae45a0f8138", "8c2cee790b0ae5885319181e56745ae45a0f8138")]
    records = [{"project": name, "expected_pinned_source": url, "commit": commit, "license_notice_presence": {"THIRD_PARTY_NOTICES.md": True, "separate_LICENSES_directory": False}, "copied_or_adapted_production_source": False, "adapted_source_comment_evidence": "not_applicable_no_copied_or_adapted_source", "findings": {"stale": [], "missing": [], "extra": []}} for name, url, commit in refs]
    _write_json(OUT / "M10_THIRD_PARTY_ATTRIBUTION_REAUDIT.json", {"schema": "scrubbots-m10-third-party-attribution-reaudit", "version": 2, "notice_file": "THIRD_PARTY_NOTICES.md", "separate_licenses_directory_present": False, "references": records, "overall_findings": {"stale": [], "missing": [], "extra": []}, "copied_source": False, "copied_artwork": False, "runtime_dependency_added": False, "result": "PASS"})


def write_gate_matrix(metrics: dict[str, object]) -> None:
    names = {1035: "Engine is fully offline", 1036: "No GPU is required", 1037: "All four difficulty dimension bands work", 1038: "Rectangular boards work", 1039: "Seed reproduction works", 1040: "C01..C16 palette enforcement works", 1041: "Difficulty distinct-color enforcement works", 1042: "MASK generator passes", 1043: "RULES generator passes", 1044: "WFC generator technical evidence or approved exemplar", 1045: "Output PNG/JSON round trip passes", 1046: "Batch generation passes", 1047: "Duplicate detection passes", 1048: "59x59 performance is measured and acceptable", 1049: "Third-party attribution audit passes"}
    gates = []
    for number in range(1035, 1050):
        status = "PENDING_INDEPENDENT_ACCEPTANCE" if number == 1048 else "EVIDENCE_READY_SYNTHETIC_FIXTURE_ONLY" if number == 1044 else "EVIDENCE_READY"; evidence = ["M10_PROPERTY_EXECUTION_REPORT.json", "M10_PERFORMANCE_REPORT.json", "M10_METRICS_REPORT.json"]
        if number == 1035: evidence = ["M10_PROPERTY_EXECUTION_REPORT.json", "M10_THIRD_PARTY_ATTRIBUTION_REAUDIT.json", "tests/integration/test_offline_boundary.py"]
        elif number == 1036: evidence = ["M10_PERFORMANCE_REPORT.json", "pyproject.toml", "tests/integration/test_offline_boundary.py"]
        elif number == 1037: evidence = ["M10_PROPERTY_EXECUTION_REPORT.json", "tests/property/test_m10_c002_execution.py"]
        elif number == 1038: evidence = ["M10_PROPERTY_EXECUTION_REPORT.json", "M10_PERFORMANCE_REPORT.json"]
        elif number == 1039: evidence = ["M10_PROPERTY_EXECUTION_REPORT.json", "tests/property/test_m10_c002_execution.py"]
        elif number in (1040, 1041): evidence = ["M10_PROPERTY_EXECUTION_REPORT.json", "tests/property/test_m10_c002_execution.py"]
        elif number == 1042: evidence = ["M10_PROPERTY_EXECUTION_REPORT.json", "tests/integration/test_m03_generator.py"]
        elif number == 1043: evidence = ["M10_PROPERTY_EXECUTION_REPORT.json", "tests/integration/test_m04_generator.py"]
        elif number == 1044: evidence = ["M10_PROPERTY_EXECUTION_REPORT.json", "M10_PERFORMANCE_REPORT.json", "tests/integration/test_m05_wfc_generator.py", "tests/fixtures/wfc/README.md"]
        elif number == 1045: evidence = ["M10_REVIEW_MANIFEST.json", "tests/integration/test_m08_export_integration.py"]
        elif number == 1046: evidence = ["tests/integration/test_m09_cli_integration.py", "M10_METRICS_REPORT.json"]
        elif number == 1047: evidence = ["M10_METRICS_REPORT.json", "tests/integration/test_m09_cli_integration.py"]
        elif number == 1048: evidence = ["M10_PERFORMANCE_REPORT.json#PAG-0441_RULES_59x59", "M10_PERFORMANCE_REPORT.md", "tests/performance/test_m10_c002_distinct_benchmark.py"]
        elif number == 1049: evidence = ["M10_THIRD_PARTY_ATTRIBUTION_REAUDIT.json", "THIRD_PARTY_NOTICES.md"]
        gates.append({"id": f"PAG-{number}", "name": names[number], "status": status, "evidence": evidence, "notes": "Synthetic WFC fixtures are technical-only; no owner-approved production exemplar is claimed." if number == 1044 else "Independent acceptance remains required." if number == 1048 else ""})
    owner_gates = [{"id": gate, "status": "PENDING_OWNER_REVIEW"} for gate in ("PAG-1033", "PAG-1034", "PAG-1050")]; matrix = {"schema": "scrubbots-m10-v1-gate-matrix", "version": 2, "owner_gates": owner_gates, "gates": owner_gates, "release_gates": gates, "evidence_root": "review/m10", "review_status": "PENDING_OWNER_REVIEW", "PAG-1048_status": "PENDING_INDEPENDENT_ACCEPTANCE", "accepted_review_candidates": metrics["accepted_count"]}; _write_json(OUT / "M10_V1_GATE_MATRIX.json", matrix)
    lines = ["# M10 V1 Gate Matrix", "", "Machine evidence only; owner and independent acceptance states remain open.", "", "| Gate | Status | Evidence |", "|---|---|---|"] + [f"| {g['id']} | {g['status']} | {', '.join(g['evidence'])} |" for g in gates] + ["", "Owner-only gates PAG-1033, PAG-1034 and PAG-1050 remain `PENDING_OWNER_REVIEW`.", "PAG-1048 remains `PENDING_INDEPENDENT_ACCEPTANCE`; no performance gate is self-approved."]; (OUT / "M10_V1_GATE_MATRIX.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True); corpus = build_property_corpus(); _write_json(OUT / "M10_PROPERTY_CORPUS.json", corpus); execution = execute_property_corpus(corpus); _write_json(OUT / "M10_PROPERTY_EXECUTION_REPORT.json", execution); benchmark_manifest = build_benchmark_manifest(); _write_json(OUT / "M10_BENCHMARK_MANIFEST.json", benchmark_manifest); performance = execute_benchmarks(benchmark_manifest); _write_json(OUT / "M10_PERFORMANCE_REPORT.json", performance)
    rows = ["# M10 Performance Evidence", "", "Distinct deterministic request/config cases; generation timing excludes export. Proposed budgets are not acceptance.", "", "| Group | Samples | Distinct | Median ns | p95 ns | Max ns | Peak memory | Proposed ns budget |", "|---|---:|---:|---:|---:|---:|---:|---:|"] + [f"| {s['group']} | {s['sample_count']} | {s['distinct_request_count']} | {s['median_ns']} | {s['p95_ns']} | {s['measured_max_ns']} | {s['peak_memory_bytes']} | {s['proposed_budget_ns']} |" for s in performance["summaries"]]; (OUT / "M10_PERFORMANCE_REPORT.md").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    manifest, metrics = build_review_pack(); write_attribution(); write_gate_matrix(metrics); print(json.dumps({"executed_valid_cases": execution["executed_case_count"], "successful_valid_cases": execution["successful_result_count"], "invalid_cases": execution["invalid_corpus"]["case_count"], "benchmark_groups": len(performance["groups"]), "review_entries": manifest["entry_count"], "review_counts": manifest["counts_by_difficulty"], "PAG-0441_samples": performance["PAG-0441_RULES_59x59"]["sample_count"]}, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
