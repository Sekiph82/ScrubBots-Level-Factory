"""Record M05 59x59 benchmark evidence; this script defines no performance budget."""

import json
import platform
import statistics
import sys
import time
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator, WFCCandidate


ROOT = Path(__file__).parents[1]


def load_exemplar() -> Exemplar:
    raw = json.loads((ROOT / "tests/fixtures/wfc/wfc-synthetic-benchmark-10.json").read_text(encoding="utf-8"))
    return Exemplar(raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"], tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"])


def run() -> list[dict[str, object]]:
    exemplar = load_exemplar()
    generator = WFCGenerator(ExemplarRegistry((exemplar,)))
    cases = ((2, False), (2, True), (3, False), (3, True))
    rows = []
    for n, periodic in cases:
        timings = []
        last: WFCCandidate | None = None
        for seed in (9101, 9102, 9103):
            request = GenerationRequest("VERY_HARD", seed, "WFC", width=59, height=59, style=exemplar.exemplar_id, palette_subset=exemplar.source_palette, generator_options=GeneratorOptions("wfc", 1, {"pattern_size": n, "input_periodic": True, "output_periodic": periodic, "max_attempts": 4}))
            start = time.perf_counter()
            candidate = generator.generate_candidate(request)
            elapsed = (time.perf_counter() - start) * 1000
            if not isinstance(candidate, WFCCandidate):
                raise RuntimeError(f"benchmark case failed: N={n} periodic={periodic}")
            timings.append(elapsed)
            last = candidate
        assert last is not None
        ordered = sorted(timings)
        rows.append({"pattern_size": n, "output_periodic": periodic, "width": 59, "height": 59, "exemplar_id": exemplar.exemplar_id, "raw_windows": last.pattern_table.raw_extracted_window_count, "transformed_observations": last.pattern_table.transformed_observation_count, "unique_patterns": len(last.pattern_table.patterns), "placement_dimensions": list(last.wfc_metadata["placement_dimensions"].values()), "runs": 3, "median_ms": round(statistics.median(timings), 3), "p95_ms": round(ordered[min(2, len(ordered) - 1)], 3), "worst_ms": round(max(timings), 3)})
    return rows


if __name__ == "__main__":
    rows = run()
    lines = ["# M05 WFC 59×59 benchmark evidence", "", "This is measured evidence only; PAG-M10 has not established a V1 performance budget.", "", f"- Python: `{sys.version.split()[0]}`", f"- Platform: `{platform.platform()}`", "- Exemplar: `wfc-synthetic-benchmark-10` (synthetic test-only)", "", "| N | Output periodic | Placement | Raw windows | Transformed observations | Unique patterns | Runs | Median ms | P95 ms | Worst ms |", "|---:|:---:|:---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['pattern_size']} | {row['output_periodic']} | {row['placement_dimensions'][0]}×{row['placement_dimensions'][1]} | {row['raw_windows']} | {row['transformed_observations']} | {row['unique_patterns']} | {row['runs']} | {row['median_ms']} | {row['p95_ms']} | {row['worst_ms']} |")
    path = ROOT / "review/m05/M05_WFC_BENCHMARK.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
