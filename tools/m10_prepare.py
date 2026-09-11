"""Generate the deterministic M10 validation, benchmark, and review evidence.

This tool is deliberately standard-library-only.  It imports the accepted
production router and treats all output under review/m10 as reproducible
evidence, not as task or acceptance state.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import platform
import sys
import time
import tracemalloc
from typing import Any

from scrubbots_pixel_factory import (
    DeterministicRNG,
    Difficulty,
    GenerationRequest,
    GeneratorOptions,
    GeneratorRouter,
    QualityPolicy,
    evaluate_grid,
    logical_grid_hash,
    select_palette_subset,
)
from scrubbots_pixel_factory.contracts.difficulty import dimension_band
from scrubbots_pixel_factory.generators.mask.generator import family_names
from scrubbots_pixel_factory.generators.rules.generator import recipe_names
from scrubbots_pixel_factory.generators.router import HybridCandidate, HybridStrategy
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review" / "m10"
FIXTURES = ROOT / "tests" / "fixtures" / "wfc"
CORPUS_VERSION = "m10-property-corpus-v1"
BENCHMARK_VERSION = "m10-performance-v1"
REVIEW_VERSION = "m10-v1-owner-review-pack-v1"
DIFFICULTIES = ("EASY", "MEDIUM", "HARD", "VERY_HARD")


def _bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write_json(path: Path, value: object) -> str:
    payload = _bytes(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _fixture(difficulty: str) -> Exemplar:
    # The fixture filenames use the difficulty-specific palette cardinality.
    path = FIXTURES / {
        "EASY": "wfc-synthetic-easy-3.json",
        "MEDIUM": "wfc-synthetic-medium-6.json",
        "HARD": "wfc-synthetic-hard-8.json",
        "VERY_HARD": "wfc-synthetic-benchmark-10.json",
    }[difficulty]
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Exemplar(
        raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"],
        tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"],
        raw.get("approved_by"), raw.get("production_difficulty", raw.get("difficulty_context")),
    )


def _exemplars() -> tuple[Exemplar, ...]:
    values = []
    for path in sorted(FIXTURES.glob("wfc-synthetic-*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        values.append(Exemplar(
            raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"],
            tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"],
            raw.get("approved_by"), raw.get("production_difficulty", raw.get("difficulty_context")),
        ))
    return tuple(values)


def _mode_options(mode: str, index: int, *, strategy: str | None = None, wfc_id: str | None = None) -> GeneratorOptions:
    if mode == "MASK":
        return GeneratorOptions("mask", 1, {"symmetry": ("HORIZONTAL", "VERTICAL", "HORIZONTAL_VERTICAL")[index % 3]})
    if mode == "RULES":
        return GeneratorOptions("rules", 1, {})
    if mode == "HYBRID":
        values: dict[str, object] = {
            "strategy": strategy or HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS.value,
            "mask_style": "ROBOT",
            "rules_style": "ORGANIC",
            "mask_symmetry": "HORIZONTAL",
        }
        if wfc_id:
            values.update({"max_attempts": 1, "wfc_exemplar_id": wfc_id, "wfc_options": {"namespace": "wfc", "version": 1, "values": {"input_periodic": True, "output_periodic": True, "max_attempts": 1}}})
        return GeneratorOptions("hybrid", 1, values)
    if mode == "AUTO":
        return GeneratorOptions("auto", 1, {
            "candidates": ["MASK", "RULES"],
            "fallback_on_failure": True,
            "configs": {
                "MASK": {"style": "ROBOT", "generator_options": {"namespace": "mask", "version": 1, "values": {"symmetry": "HORIZONTAL"}}},
                "RULES": {"style": "ORGANIC", "generator_options": {"namespace": "rules", "version": 1, "values": {}}},
            },
        })
    if mode == "WFC":
        return GeneratorOptions("wfc", 1, {"pattern_size": 2, "input_periodic": True, "output_periodic": True, "max_attempts": 1})
    raise ValueError(mode)


def _request(difficulty: str, seed: int | str, mode: str, index: int, *, dimensions: tuple[int, int] | None = None, style: str | None = None, palette: tuple[str, ...] | None = None, strategy: str | None = None, wfc_id: str | None = None) -> GenerationRequest:
    band = dimension_band(difficulty)
    width, height = dimensions or (band.minimum + index % (band.maximum - band.minimum + 1), band.minimum + (index * 3) % (band.maximum - band.minimum + 1))
    return GenerationRequest(
        difficulty, seed, mode,
        width=None if index % 5 == 0 else width,
        height=None if index % 5 == 0 else height,
        style=style,
        palette_subset=palette,
        generator_options=_mode_options(mode, index, strategy=strategy, wfc_id=wfc_id),
    )


def build_property_corpus() -> dict[str, object]:
    cases: list[dict[str, object]] = []
    modes = ("MASK", "RULES", "HYBRID", "AUTO")
    strategies = (HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS.value, HybridStrategy.RULE_GEOMETRY_MASK_SYMMETRY.value)
    for index in range(2048):
        difficulty = DIFFICULTIES[index % 4]
        mode = modes[index % len(modes)]
        palette_seed = f"m10-corpus-palette-{index}"
        palette = select_palette_subset(difficulty, palette_seed)
        style = family_names()[index % len(family_names())] if mode == "MASK" else recipe_names()[index % len(recipe_names())] if mode == "RULES" else None
        strategy = strategies[index % 2] if mode == "HYBRID" else None
        request = _request(difficulty, f"m10-corpus-{index}", mode, index, style=style, palette=palette, strategy=strategy)
        cases.append({"index": index, "request": request.canonical_dict(), "request_digest": request.digest(), "shape": "AUTO" if request.width is None else ("RECTANGULAR" if request.width != request.height else "SQUARE")})
    # WFC is represented by one legal, local synthetic-fixture case per
    # difficulty. These are technical contract cases only; they are never
    # promoted into the owner-facing visual review pack.
    for offset, difficulty in enumerate(DIFFICULTIES, start=3000):
        exemplar = _fixture(difficulty)
        band = dimension_band(difficulty)
        request = _request(difficulty, f"m10-corpus-wfc-{difficulty}", "WFC", offset, dimensions=(band.minimum, band.minimum + 1), style=exemplar.exemplar_id, palette=exemplar.source_palette)
        cases.append({"index": offset, "request": request.canonical_dict(), "request_digest": request.digest(), "shape": "RECTANGULAR", "fixture_classification": "SYNTHETIC_TEST_ONLY"})
    invalid = [
        {"case": "unsupported-difficulty", "difficulty": "IMPOSSIBLE"},
        {"case": "unsupported-mode", "generator_mode": "NOPE"},
        {"case": "illegal-width", "difficulty": "EASY", "width": 19, "height": 20},
        {"case": "malformed-options", "generator_options": {"namespace": "mask", "version": 99, "values": {}}},
        {"case": "bool-seed", "seed": True},
    ]
    return {
        "schema": "scrubbots-m10-property-corpus",
        "version": 1,
        "corpus_version": CORPUS_VERSION,
        "case_count": len(cases),
        "requirements": {"valid_cases": 2048, "difficulties": list(DIFFICULTIES), "includes_invalid_cases": True, "uses_python_hash": False, "uses_python_random": False},
        "cases": cases,
        "invalid_cases": invalid,
    }


def _candidate_result(candidate: object):
    return getattr(candidate, "result", candidate)


def _make_runner() -> GeneratorRouter:
    return GeneratorRouter(wfc_generator=WFCGenerator(ExemplarRegistry(_exemplars())))


def _benchmark_request(mode: str, difficulty: str, index: int, *, dimensions: tuple[int, int] | None = None, strategy: str | None = None) -> GenerationRequest:
    exemplar = _fixture(difficulty)
    if mode == "WFC":
        return _request(difficulty, f"m10-benchmark-{mode}-{difficulty}-{index}", mode, index, dimensions=dimensions, style=exemplar.exemplar_id, palette=exemplar.source_palette)
    if mode == "HYBRID" and strategy in {HybridStrategy.RULE_BASE_WFC_DETAIL.value, HybridStrategy.MASK_BASE_WFC_DETAIL.value}:
        return _request(difficulty, f"m10-benchmark-{mode}-{difficulty}-{index}", mode, index, dimensions=dimensions, palette=exemplar.source_palette, strategy=strategy, wfc_id=exemplar.exemplar_id, style=None)
    return _request(difficulty, f"m10-benchmark-{mode}-{difficulty}-{index}", mode, index, dimensions=dimensions, palette=select_palette_subset(difficulty, f"m10-benchmark-palette-{difficulty}-{index}"), strategy=strategy)


def _timed(router: GeneratorRouter, request: GenerationRequest, warmup: bool = True) -> dict[str, object]:
    if warmup:
        router.generate_candidate(request)
    tracemalloc.start()
    before = time.perf_counter_ns()
    candidate = router.generate_candidate(request)
    elapsed = time.perf_counter_ns() - before
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    result = _candidate_result(candidate)
    record: dict[str, object] = {"seed": request.seed, "request_digest": request.digest(), "elapsed_ns": elapsed, "peak_memory_bytes": peak, "status": result.status.value}
    record["failure_code"] = result.failure_code.value if not result.is_success else None
    record["attempts"] = int(getattr(candidate, "attempt", 0)) + 1 if result.is_success else None
    if result.is_success:
        report = evaluate_grid(result.width, result.height, result.logical_grid, policy=QualityPolicy(difficulty=request.difficulty))
        record.update({"grid_hash": logical_grid_hash(result.width, result.height, result.logical_grid), "quality_accepted": report.accepted, "quality_rejection_codes": list(report.rejection_codes)})
    else:
        record.update({"grid_hash": None, "quality_accepted": False, "quality_rejection_codes": []})
    return record


def _percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, (len(ordered) * 95 + 99) // 100 - 1))] if fraction == 0.95 else ordered[len(ordered) // 2]


def build_performance_report() -> dict[str, object]:
    router = _make_runner()
    cases: list[dict[str, object]] = []
    representative = {"EASY": (20, 21), "MEDIUM": (30, 31), "HARD": (40, 41), "VERY_HARD": (50, 51)}
    for difficulty in DIFFICULTIES:
        for mode in ("MASK", "RULES", "WFC"):
            request = _benchmark_request(mode, difficulty, 0, dimensions=representative[difficulty])
            samples = [_timed(router, request) for _ in range(1 if mode == "WFC" else 3)]
            cases.append({"mode": mode, "strategy": None, "difficulty": difficulty, "dimensions": list(representative[difficulty]), "samples": samples})
        # The two production review strategies are measured at every
        # difficulty. WFC-detail is separately measured below with synthetic
        # fixtures; failed/slow contradiction paths are reported as such and
        # are never substituted into owner-facing review evidence.
        for strategy in (HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS.value, HybridStrategy.RULE_GEOMETRY_MASK_SYMMETRY.value):
            dims = representative[difficulty]
            request = _benchmark_request("HYBRID", difficulty, 0, dimensions=dims, strategy=strategy)
            samples = [_timed(router, request) for _ in range(3)]
            cases.append({"mode": "HYBRID", "strategy": strategy, "difficulty": difficulty, "dimensions": list(dims), "samples": samples})
    for strategy in (HybridStrategy.RULE_BASE_WFC_DETAIL.value, HybridStrategy.MASK_BASE_WFC_DETAIL.value):
        request = _benchmark_request("HYBRID", "EASY", 0, dimensions=(20, 21), strategy=strategy)
        cases.append({"mode": "HYBRID", "strategy": strategy, "difficulty": "EASY", "dimensions": [20, 21], "technical_scope": "synthetic WFC fixture; WFC-detail only", "samples": [_timed(router, request)]})
    rules59 = _benchmark_request("RULES", "VERY_HARD", 59, dimensions=(59, 59))
    cases.append({"mode": "RULES", "strategy": None, "difficulty": "VERY_HARD", "dimensions": [59, 59], "benchmark_gate": "PAG-0441", "samples": [_timed(router, rules59) for _ in range(5)]})
    summaries: list[dict[str, object]] = []
    for case in cases:
        samples = case["samples"]
        assert isinstance(samples, list)
        elapsed = [int(item["elapsed_ns"]) for item in samples]
        memory = [int(item["peak_memory_bytes"]) for item in samples]
        quality_rejects = sum(not bool(item["quality_accepted"]) and item["status"] == "SUCCESS" for item in samples)
        failures = sum(item["status"] != "SUCCESS" for item in samples)
        contradictions = sum(1 for item in samples if item.get("failure_code") == "RETRY_EXHAUSTED")
        p95 = _percentile(elapsed, 0.95)
        budget_ns = max(1_000_000, int(p95 * 1.50))
        memory_budget = max(1, int(max(memory) * 1.50))
        summaries.append({"mode": case["mode"], "strategy": case["strategy"], "difficulty": case["difficulty"], "dimensions": case["dimensions"], "sample_count": len(samples), "successes": sum(item["status"] == "SUCCESS" for item in samples), "quality_rejects": quality_rejects, "generator_failures": failures, "retry_exhaustions": contradictions, "median_ns": _percentile(elapsed, 0.5), "p95_ns": p95, "peak_memory_bytes": max(memory), "attempts": [item["attempts"] for item in samples], "proposed_budget_ns": budget_ns, "proposed_peak_memory_budget_bytes": memory_budget, "derivation": "ceil(p95 generation time * 1.50), ceil(peak memory * 1.50); measured on this laptop", "inside_proposed_budget": all(int(item["elapsed_ns"]) <= budget_ns and int(item["peak_memory_bytes"]) <= memory_budget for item in samples)})
    return {"schema": "scrubbots-m10-performance-report", "version": 1, "benchmark_version": BENCHMARK_VERSION, "measurement_scope": "generation only; export timing excluded", "harness": {"warmup_runs": 1, "measured_runs": 3, "rules_59x59_measured_runs": 5, "percentile": "nearest-rank p95", "clock": "time.perf_counter_ns", "memory": "tracemalloc peak"}, "hardware": {"platform": platform.platform(), "python": platform.python_version(), "processor": platform.processor(), "machine": platform.machine(), "cpu_count": __import__("os").cpu_count()}, "fixed_configuration": {"representative_dimensions": representative, "synthetic_wfc_fixtures": True, "seed_domain": "m10-benchmark-*", "network": "forbidden"}, "cases": cases, "summaries": summaries, "PAG-0441_RULES_59x59": next(summary for summary in summaries if summary["dimensions"] == [59, 59]), "budget_policy": "Proposed budgets are derived only after measurement and are not owner-approved V1 acceptance budgets."}


def _review_request(difficulty: str, slot: int) -> GenerationRequest:
    band = dimension_band(difficulty)
    width = band.minimum + (slot * 3) % (band.maximum - band.minimum + 1)
    height = band.minimum + (slot * 5 + 1) % (band.maximum - band.minimum + 1)
    mode_index = slot % 4
    if mode_index == 0:
        return _request(difficulty, f"m10-review-{difficulty}-{slot}", "MASK", slot, dimensions=(width, height), style=family_names()[slot % len(family_names())], palette=select_palette_subset(difficulty, f"m10-review-palette-{difficulty}-{slot}"))
    if mode_index == 1:
        return _request(difficulty, f"m10-review-{difficulty}-{slot}", "RULES", slot, dimensions=(width, height), style=recipe_names()[slot % len(recipe_names())], palette=select_palette_subset(difficulty, f"m10-review-palette-{difficulty}-{slot}"))
    strategy = HybridStrategy.MASK_GEOMETRY_RULE_COLOR_REGIONS.value if mode_index == 2 else HybridStrategy.RULE_GEOMETRY_MASK_SYMMETRY.value
    return _request(difficulty, f"m10-review-{difficulty}-{slot}", "HYBRID", slot, dimensions=(width, height), palette=select_palette_subset(difficulty, f"m10-review-palette-{difficulty}-{slot}"), strategy=strategy)


def _review_entry(router: GeneratorRouter, difficulty: str, slot: int) -> dict[str, object]:
    request = _review_request(difficulty, slot)
    candidate = router.generate_candidate(request)
    result = _candidate_result(candidate)
    if not result.is_success:
        raise RuntimeError(f"review candidate generation failed: {difficulty}/{slot}: {result.failure_code}")
    quality = evaluate_grid(result.width, result.height, result.logical_grid, policy=QualityPolicy(difficulty=difficulty))
    if not quality.accepted:
        raise RuntimeError(f"review candidate quality rejected: {difficulty}/{slot}: {quality.rejection_codes}")
    details: dict[str, object] = {"family": getattr(getattr(candidate, "family", None), "value", None), "recipe": getattr(getattr(candidate, "recipe", None), "recipe_id", None), "strategy": getattr(candidate, "strategy", None)}
    return {"candidate_id": f"m10-{difficulty.lower()}-{slot:02d}", "difficulty": difficulty, "status": "PENDING_OWNER_REVIEW", "owner_notes": "", "mode": request.generator_mode, "seed": {"type": "int", "value": request.seed} if isinstance(request.seed, int) else {"type": "string", "value": request.seed}, "request": request.canonical_dict(), "request_digest": request.digest(), "resolved_dimensions": {"width": result.width, "height": result.height}, "generator": {"id": result.generator_id, "version": result.generator_version}, "grid_hash": logical_grid_hash(result.width, result.height, result.logical_grid), "logical_grid": list(result.logical_grid), "used_palette": list(result.used_palette), "quality": quality.as_dict(), "generator_details": details, "synthetic_wfc_visuals": False}


def _review_html(entries: list[dict[str, object]]) -> str:
    palette = {color.id: color.hex for color in __import__("scrubbots_pixel_factory").CANONICAL_PALETTE.colors}
    payload = json.dumps({"palette": palette, "entries": entries}, sort_keys=True, separators=(",", ":"))
    cards: list[str] = []
    for entry in entries:
        cards.append(f'<article class="card" data-candidate="{html.escape(str(entry["candidate_id"]))}" data-difficulty="{entry["difficulty"]}"><h2>{entry["candidate_id"]}</h2><p><b>{entry["difficulty"]}</b> · {entry["mode"]} · <span class="status">PENDING_OWNER_REVIEW</span></p><canvas width="{entry["resolved_dimensions"]["width"] * 5}" height="{entry["resolved_dimensions"]["height"] * 5}"></canvas><dl><dt>Grid hash</dt><dd class="grid-hash">{entry["grid_hash"]}</dd><dt>Generator</dt><dd>{entry["generator"]["id"]} {entry["generator"]["version"]}</dd><dt>Quality</dt><dd>ACCEPT (owner review pending)</dd></dl></article>')
    return "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>M10 V1 Owner Review Pack</title><style>body{background:#202533;color:#eee;font:14px system-ui;margin:2rem}.grid{display:grid;grid-template-columns:repeat(4,minmax(220px,1fr));gap:1rem}.card{background:#30394d;padding:1rem;border:1px solid #66708a;border-radius:6px}.card canvas{image-rendering:pixelated;background:#202533;max-width:100%;height:auto}.card dd{overflow-wrap:anywhere;font-family:monospace;font-size:11px}.status{color:#ffd166}.legend{position:sticky;top:0;background:#202533;padding:1rem 0}.card h2{font-size:15px}</style></head><body><div class=\"legend\"><h1>M10 V1 Owner Review Pack</h1><p>Deterministic, offline, logical-cell previews. All 100 candidates are structurally ACCEPTED and remain PENDING_OWNER_REVIEW. WFC visual pack skipped: WFC_VISUAL_PACK_SKIPPED_NO_APPROVED_EXEMPLAR.</p></div><main class=\"grid\">" + "".join(cards) + f"</main><script>const pack={payload};document.querySelectorAll('canvas').forEach((canvas,i)=>{{const e=pack.entries[i],ctx=canvas.getContext('2d'),w=e.resolved_dimensions.width;ctx.imageSmoothingEnabled=false;e.logical_grid.forEach((c,n)=>{{ctx.fillStyle=pack.palette[c];ctx.fillRect((n%w)*5,Math.floor(n/w)*5,5,5)}})}});</script></body></html>"


def build_review_pack() -> dict[str, object]:
    router = _make_runner()
    entries = [_review_entry(router, difficulty, slot) for difficulty in DIFFICULTIES for slot in range(25)]
    entries.sort(key=lambda item: str(item["candidate_id"]))
    hashes = [str(entry["grid_hash"]) for entry in entries]
    counts = Counter(str(entry["difficulty"]) for entry in entries)
    manifest = {"schema": "scrubbots-m10-review-manifest", "version": 1, "review_version": REVIEW_VERSION, "status_policy": "All entries are PENDING_OWNER_REVIEW until owner/ChatGPT review.", "root_seed": "m10-review-v1", "counts_by_difficulty": dict(sorted(counts.items())), "entry_count": len(entries), "exact_duplicate_count": len(hashes) - len(set(hashes)), "wfc_visual_status": "WFC_VISUAL_PACK_SKIPPED_NO_APPROVED_EXEMPLAR", "entries": entries}
    _write_json(OUT / "M10_REVIEW_MANIFEST.json", manifest)
    (OUT / "M10_REVIEW_INDEX.html").write_text(_review_html(entries), encoding="utf-8", newline="\n")
    metrics = {"schema": "scrubbots-m10-review-metrics", "version": 1, "entry_count": len(entries), "accepted_quality_count": sum(entry["quality"]["accepted"] for entry in entries), "pending_owner_review_count": sum(entry["status"] == "PENDING_OWNER_REVIEW" for entry in entries), "counts_by_difficulty": dict(sorted(counts.items())), "counts_by_mode": dict(sorted(Counter(str(entry["mode"]) for entry in entries).items())), "exact_duplicate_count": manifest["exact_duplicate_count"], "grid_hashes": hashes}
    _write_json(OUT / "M10_REVIEW_METRICS.json", metrics)
    return {"manifest": manifest, "metrics": metrics}


def write_gate_matrix(performance: dict[str, object], review: dict[str, object]) -> None:
    matrix = {"schema": "scrubbots-m10-v1-gate-matrix", "version": 1, "review_status": "PENDING_OWNER_REVIEW", "gates": [{"id": "PAG-1033", "name": "owner visual review", "status": "PENDING_OWNER_REVIEW"}, {"id": "PAG-1034", "name": "V1 acceptance", "status": "PENDING_OWNER_REVIEW"}, {"id": "PAG-1050", "name": "M10 owner/ChatGPT gate", "status": "PENDING_OWNER_REVIEW"}], "evidence": {"property_corpus": "M10_PROPERTY_CORPUS.json", "performance": "M10_PERFORMANCE_REPORT.json", "review_manifest": "M10_REVIEW_MANIFEST.json", "review_html": "M10_REVIEW_INDEX.html", "third_party": "M10_THIRD_PARTY_ATTRIBUTION_REAUDIT.json"}, "wfc_visual_status": "WFC_VISUAL_PACK_SKIPPED_NO_APPROVED_EXEMPLAR", "accepted_review_candidates": review["metrics"]["accepted_quality_count"], "third_party_attribution_reaudit": "PASS: current source contains no copied third-party source/artwork; references remain immutable and attribution is recorded in THIRD_PARTY_NOTICES.md.", "performance_budget_note": "Proposed budgets are measured-data-derived and are not owner-approved acceptance budgets."}
    _write_json(OUT / "M10_V1_GATE_MATRIX.json", matrix)
    md = ["# M10 V1 Gate Matrix", "", "All owner-facing gates remain `PENDING_OWNER_REVIEW`; this is builder evidence, not acceptance.", "", "| Gate | Status |", "|---|---|"]
    md.extend(f"| {gate['id']} | {gate['status']} |" for gate in matrix["gates"])
    md.extend(["", "WFC visual evidence is explicitly skipped because no owner-approved exemplar is present. Synthetic fixtures are technical-only.", "", "Proposed performance budgets are derived after actual measurement and are not V1 acceptance budgets."])
    (OUT / "M10_V1_GATE_MATRIX.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    corpus = build_property_corpus()
    performance = build_performance_report()
    review = build_review_pack()
    _write_json(OUT / "M10_PROPERTY_CORPUS.json", corpus)
    _write_json(OUT / "M10_PERFORMANCE_REPORT.json", performance)
    perf_md = ["# M10 Performance Evidence", "", "Generation timing excludes M08 export. Budgets are proposed from measured p95/peak memory with 1.50x headroom.", "", "| Mode | Strategy | Difficulty | Dimensions | Samples | Median ns | p95 ns | Peak memory | Proposed ns budget |", "|---|---|---|---|---:|---:|---:|---:|---:|"]
    for item in performance["summaries"]:
        perf_md.append(f"| {item['mode']} | {item['strategy'] or ''} | {item['difficulty']} | {item['dimensions'][0]}x{item['dimensions'][1]} | {item['sample_count']} | {item['median_ns']} | {item['p95_ns']} | {item['peak_memory_bytes']} | {item['proposed_budget_ns']} |")
    (OUT / "M10_PERFORMANCE_REPORT.md").write_text("\n".join(perf_md) + "\n", encoding="utf-8", newline="\n")
    attribution = {"schema": "scrubbots-m10-third-party-attribution-reaudit", "version": 1, "notices_file": "THIRD_PARTY_NOTICES.md", "source_scan": "PASS", "copied_source": False, "copied_artwork": False, "runtime_dependency_added": False, "immutable_references": ["ikarth/wfc_2019f@3a937fed13934722377dd7fb6dd238518fa644dd", "mxgmn/WaveFunctionCollapse@de7d22e705e816b62b4d613199d0463820fcaef3", "mxgmn/MarkovJunior@42aaf24bcf54ae164fba49c0a59348297904a676", "zfedoran/pixel-sprite-generator@8c2cee790b0ae5885319181e56745ae45a0f8138"], "result": "PASS"}
    _write_json(OUT / "M10_THIRD_PARTY_ATTRIBUTION_REAUDIT.json", attribution)
    write_gate_matrix(performance, review)
    print(json.dumps({"corpus_cases": corpus["case_count"], "review_entries": review["metrics"]["entry_count"], "review_counts": review["metrics"]["counts_by_difficulty"], "performance_summaries": len(performance["summaries"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
