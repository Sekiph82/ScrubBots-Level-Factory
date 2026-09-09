"""Build the self-contained PAG-M06 hybrid review manifest and contact sheet."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.router import HybridCandidate, HybridGenerator
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator


CASES = (
    ("EASY", 20, 20, 1, "MASK_GEOMETRY_RULE_COLOR_REGIONS"),
    ("EASY", 29, 23, 2, "RULE_GEOMETRY_MASK_SYMMETRY"),
    ("EASY", 20, 27, 3, "MASK_GEOMETRY_RULE_COLOR_REGIONS"),
    ("MEDIUM", 30, 30, 4, "RULE_GEOMETRY_MASK_SYMMETRY"),
    ("MEDIUM", 37, 34, 5, "MASK_GEOMETRY_RULE_COLOR_REGIONS"),
    ("MEDIUM", 30, 39, 6, "RULE_GEOMETRY_MASK_SYMMETRY"),
    ("HARD", 40, 40, 7, "MASK_GEOMETRY_RULE_COLOR_REGIONS"),
    ("HARD", 48, 41, 8, "RULE_GEOMETRY_MASK_SYMMETRY"),
    ("HARD", 40, 49, 9, "MASK_GEOMETRY_RULE_COLOR_REGIONS"),
    ("VERY_HARD", 50, 50, 10, "RULE_GEOMETRY_MASK_SYMMETRY"),
    ("VERY_HARD", 53, 59, 11, "MASK_GEOMETRY_RULE_COLOR_REGIONS"),
    ("VERY_HARD", 59, 50, 12, "RULE_GEOMETRY_MASK_SYMMETRY"),
)


def _request(difficulty: str, width: int, height: int, seed: int, strategy: str) -> GenerationRequest:
    return GenerationRequest(
        difficulty,
        seed,
        "HYBRID",
        width=width,
        height=height,
        generator_options=GeneratorOptions("hybrid", 1, {
            "strategy": strategy,
            "mask_style": "ROBOT",
            "rules_style": "ORGANIC",
            "mask_symmetry": "HORIZONTAL",
        }),
    )


def _test_exemplar() -> Exemplar:
    colors = ("C11", "C12", "C13")
    pixels = tuple(colors[(x // 2) % 3] for y in range(6) for x in range(6))
    return Exemplar(
        "scrubbots-wfc-exemplar", 1, "m06-review-synthetic-blocks", "TRAINING_MOTIF", 6, 6, pixels,
        "synthetic-test-fixture", "Project-authored review fixture; not production artwork.", "SYNTHETIC_TEST_ONLY",
    )


def build() -> dict[str, object]:
    generator = HybridGenerator()
    entries: list[dict[str, object]] = []
    for difficulty, width, height, seed, strategy in CASES:
        candidate = generator.generate_candidate(_request(difficulty, width, height, seed, strategy))
        if not isinstance(candidate, HybridCandidate):
            raise RuntimeError(f"review case failed: {difficulty}/{seed}: {candidate.failure_reason}")
        entries.append({
            "case_id": f"m06-{len(entries) + 1:02d}",
            "strategy": strategy,
            "difficulty": difficulty,
            "master_seed": seed,
            "dimensions": [width, height],
            "palette": list(candidate.result.used_palette),
            "stage_names": [stage.stage_name for stage in candidate.stages],
            "stages": [stage.as_dict() for stage in candidate.stages],
            "final_topology_digest": candidate.metadata["final_topology_digest"],
            "final_logical_grid_digest": candidate.metadata["final_logical_grid_digest"],
            "final_result_digest": candidate.result.digest(),
            "topology_evidence": {name: list(cells) for name, cells in candidate.metadata["topology_evidence"].items()},
            "logical_grid": list(candidate.logical_grid),
        })
    synthetic = _test_exemplar()
    injected = HybridGenerator(wfc_generator=WFCGenerator(ExemplarRegistry((synthetic,))))
    for difficulty, width, height, seed, strategy in (
        ("EASY", 20, 20, 101, "RULE_BASE_WFC_DETAIL"),
        ("EASY", 20, 27, 102, "MASK_BASE_WFC_DETAIL"),
    ):
        request = GenerationRequest(
            difficulty, seed, "HYBRID", width=width, height=height, palette_subset=("C01", "C02", "C03"),
            generator_options=GeneratorOptions("hybrid", 1, {
                "strategy": strategy, "mask_style": "ROBOT", "rules_style": "ORGANIC",
                "wfc_exemplar_id": synthetic.exemplar_id,
                "wfc_options": {"namespace": "wfc", "version": 1, "values": {"pattern_size": 2, "input_periodic": True, "output_periodic": True}},
            }),
        )
        candidate = injected.generate_candidate(request)
        if not isinstance(candidate, HybridCandidate):
            raise RuntimeError(f"synthetic WFC review case failed: {difficulty}/{seed}: {candidate.failure_reason}")
        entries.append({
            "case_id": f"m06-{len(entries) + 1:02d}", "strategy": strategy, "difficulty": difficulty,
            "master_seed": seed, "dimensions": [width, height], "palette": list(candidate.result.used_palette),
            "stage_names": [stage.stage_name for stage in candidate.stages], "stages": [stage.as_dict() for stage in candidate.stages],
            "final_topology_digest": candidate.metadata["final_topology_digest"],
            "final_logical_grid_digest": candidate.metadata["final_logical_grid_digest"],
            "final_result_digest": candidate.result.digest(), "topology_evidence": {name: list(cells) for name, cells in candidate.metadata["topology_evidence"].items()}, "logical_grid": list(candidate.logical_grid),
            "exemplar_id": synthetic.exemplar_id,
            "exemplar_ownership": "SYNTHETIC_TEST_ONLY",
        })
    return {"schema": "scrubbots-m06-hybrid-review-v1", "candidate_count": len(entries), "entries": entries}


def _render_grid(entry: dict[str, object]) -> str:
    width, height = entry["dimensions"]
    cells = entry["logical_grid"]
    rows = []
    for row in range(height):
        rows.append("".join(f'<span class="c-{escape(cell[1:])}"></span>' for cell in cells[row * width:(row + 1) * width]))
    return f'<div class="grid" style="--w:{width};--h:{height}">' + "".join(rows) + "</div>"


def _render_topology(cells: list[int], width: int, height: int) -> str:
    rows = []
    for row in range(height):
        rows.append("".join('<span class="occupied"></span>' if cell else '<span class="empty"></span>' for cell in cells[row * width:(row + 1) * width]))
    return f'<div class="topology" style="--w:{width};--h:{height}">' + "".join(rows) + "</div>"


def write_outputs() -> None:
    root = Path(__file__).parents[2]
    review = root / "review" / "m06"
    manifest = build()
    (review / "m06_review_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    cards = []
    for entry in manifest["entries"]:
        stages = " → ".join(escape(name) for name in entry["stage_names"])
        topology = entry["topology_evidence"]
        cards.append(f'<article><h2>{escape(entry["case_id"])} · {escape(entry["strategy"])}</h2><p>{entry["difficulty"]} · seed {entry["master_seed"]} · {entry["dimensions"][0]}×{entry["dimensions"][1]} · {", ".join(entry["palette"])}</p><p>Stages: {stages}</p><p>Topology: <code>{entry["final_topology_digest"]}</code><br>Grid: <code>{entry["final_logical_grid_digest"]}</code><br>Result: <code>{entry["final_result_digest"]}</code></p><div class="panels"><section>Before topology{_render_topology(topology["before"], entry["dimensions"][0], entry["dimensions"][1])}</section><section>After/final topology{_render_topology(topology["after"], entry["dimensions"][0], entry["dimensions"][1])}</section><section>Final colored output{_render_grid(entry)}</section></div></article>')
    html = """<!doctype html><meta charset="utf-8"><title>M06 Hybrid Contact Sheet</title><style>body{background:#202533;color:#e8cfa0;font:12px sans-serif;margin:16px}main{display:grid;grid-template-columns:repeat(3,minmax(280px,1fr));gap:12px}article{background:#30394a;padding:10px;border:1px solid #596779}h2{font-size:14px;margin:0 0 6px}p{line-height:1.35;overflow-wrap:anywhere}.panels{display:flex;gap:8px;align-items:flex-start}.panels section{font-size:10px}.grid,.topology{display:grid;grid-template-columns:repeat(var(--w),5px);grid-template-rows:repeat(var(--h),5px);gap:0;background:#202533;width:max-content;margin-top:3px}.grid span,.topology span{width:5px;height:5px;display:block}.topology .occupied{background:#e8cfa0}.topology .empty{background:#202533}.c-01{background:#E94B4B}.c-02{background:#F28C3C}.c-03{background:#F2C94C}.c-04{background:#55B85A}.c-05{background:#63D6A3}.c-06{background:#42C7D9}.c-07{background:#3E7EDB}.c-08{background:#3451A3}.c-09{background:#845EC2}.c-10{background:#E66FA5}.c-11{background:#956447}.c-12{background:#E8CFA0}.c-13{background:#B8C2CC}.c-14{background:#3D4652}.c-15{background:#FFFFFF}.c-16{background:#000000}code{font-size:10px}</style><main>""" + "".join(cards) + "</main>\n"
    (review / "M06_HYBRID_CONTACT_SHEET.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    write_outputs()
