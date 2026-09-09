"""Build self-contained, review-only M05 WFC evidence from synthetic fixtures."""

import json
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator, WFCCandidate


OUTPUT = Path(__file__).parent
FIXTURES = Path(__file__).parents[2] / "tests" / "fixtures" / "wfc"
CASES = (
    ("wfc-synthetic-easy-3.json", "EASY", (20, 20), 801, {"pattern_size": 2, "input_periodic": True, "output_periodic": False}),
    ("wfc-synthetic-medium-6.json", "MEDIUM", (30, 30), 802, {"pattern_size": 3, "input_periodic": True, "output_periodic": False, "allow_rotations": True}),
    ("wfc-synthetic-hard-8.json", "HARD", (40, 40), 803, {"pattern_size": 2, "input_periodic": True, "output_periodic": True}),
    ("wfc-synthetic-very-hard-10.json", "VERY_HARD", (50, 50), 804, {"pattern_size": 3, "input_periodic": True, "output_periodic": False, "allow_rotations": True, "allow_reflections": True}),
)


def load_exemplar(name: str) -> Exemplar:
    raw = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return Exemplar(raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"], tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"])


def build_manifest() -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    for name, difficulty, dimensions, seed, values in CASES:
        exemplar = load_exemplar(name)
        request = GenerationRequest(difficulty, seed, "WFC", width=dimensions[0], height=dimensions[1], style=exemplar.exemplar_id, palette_subset=exemplar.source_palette, generator_options=GeneratorOptions("wfc", 1, values))
        candidate = WFCGenerator(ExemplarRegistry((exemplar,))).generate_candidate(request)
        if not isinstance(candidate, WFCCandidate):
            raise RuntimeError(f"review candidate failed: {name}")
        candidates.append({
            "exemplar_id": exemplar.exemplar_id,
            "fixture": name,
            "ownership": exemplar.ownership,
            "provenance_identity": exemplar.provenance_identity,
            "difficulty": difficulty,
            "seed": seed,
            "dimensions": list(dimensions),
            "options": values,
            "logical_grid": list(candidate.logical_grid),
            "metadata": dict(candidate.wfc_metadata),
            "result_digest": candidate.result.digest(),
        })
    return {
        "evidence_type": "review-only / non-production / M05 WFC evidence",
        "generator": "wfc-overlap 1.0.0",
        "exemplar_source": "project-authored synthetic test fixtures only",
        "production_exemplar_registry": "empty",
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def build_html(manifest: dict[str, object]) -> str:
    palette = {f"C{index:02d}": color for index, color in enumerate(("#E94B4B", "#F28C3C", "#F2C94C", "#55B85A", "#63D6A3", "#42C7D9", "#3E7EDB", "#3451A3", "#845EC2", "#E66FA5", "#956447", "#E8CFA0", "#B8C2CC", "#3D4652", "#FFFFFF", "#000000"), 1)}
    data = json.dumps(manifest, separators=(",", ":"), ensure_ascii=False)
    colors = json.dumps(palette, separators=(",", ":"))
    return f"""<!doctype html><meta charset='utf-8'><title>M05 WFC Review</title><style>body{{background:#202533;color:#fff;font:12px sans-serif}}article{{display:inline-block;vertical-align:top;margin:8px;padding:8px;background:#303849;max-width:300px}}canvas{{image-rendering:pixelated;display:block;margin:4px 0;max-width:280px;height:auto}}small{{color:#b8c2cc}}</style><main id='sheet'></main><script>const manifest={data};const colors={colors};const root=document.getElementById('sheet');for(const c of manifest.candidates){{const a=document.createElement('article');const h=document.createElement('h3');h.textContent=c.exemplar_id+' · N'+c.metadata.pattern_size+' · seed '+c.seed;a.appendChild(h);const canvas=document.createElement('canvas');const w=c.dimensions[0],hgt=c.dimensions[1],scale=Math.max(1,Math.floor(280/w));canvas.width=w*scale;canvas.height=hgt*scale;const x=canvas.getContext('2d');x.imageSmoothingEnabled=false;for(let i=0;i<c.logical_grid.length;i++){{x.fillStyle=colors[c.logical_grid[i]];x.fillRect((i%w)*scale,Math.floor(i/w)*scale,scale,scale);}}a.appendChild(canvas);const p=document.createElement('small');p.textContent='palette '+c.metadata.target_palette.join(',')+' · patterns '+c.metadata.unique_pattern_count+' · digest '+c.result_digest.slice(0,12);a.appendChild(p);root.appendChild(a);}}</script>"""


if __name__ == "__main__":
    manifest = build_manifest()
    (OUTPUT / "m05_review_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "M05_WFC_CONTACT_SHEET.html").write_text(build_html(manifest), encoding="utf-8")
    print(f"M05 review candidates: {manifest['candidate_count']}")
