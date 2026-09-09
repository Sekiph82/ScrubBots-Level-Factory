"""Build self-contained, review-only M05 WFC evidence from synthetic fixtures."""

import json
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator, WFCCandidate


OUTPUT = Path(__file__).parent
FIXTURES = Path(__file__).parents[2] / "tests" / "fixtures" / "wfc"
CASES = (
    ("wfc-synthetic-easy-3.json", "EASY", (29, 23), 801, {"pattern_size": 2, "input_periodic": False, "output_periodic": False}),
    ("wfc-synthetic-easy-3.json", "EASY", (21, 21), 802, {"pattern_size": 2, "input_periodic": True, "output_periodic": True}),
    ("wfc-synthetic-easy-3.json", "EASY", (28, 24), 803, {"pattern_size": 3, "input_periodic": False, "output_periodic": False}),
    ("wfc-synthetic-easy-3.json", "EASY", (26, 22), 804, {"pattern_size": 3, "input_periodic": True, "output_periodic": False, "allow_rotations": True}),
    ("wfc-synthetic-medium-6.json", "MEDIUM", (30, 39), 805, {"pattern_size": 2, "input_periodic": False, "output_periodic": False}),
    ("wfc-synthetic-medium-6.json", "MEDIUM", (36, 33), 806, {"pattern_size": 3, "input_periodic": True, "output_periodic": False, "allow_rotations": True}),
    ("wfc-synthetic-medium-6.json", "MEDIUM", (30, 30), 807, {"pattern_size": 3, "input_periodic": True, "output_periodic": True}),
    ("wfc-synthetic-medium-6.json", "MEDIUM", (38, 31), 808, {"pattern_size": 2, "input_periodic": True, "output_periodic": False, "allow_reflections": True}),
    ("wfc-synthetic-hard-8.json", "HARD", (48, 41), 809, {"pattern_size": 2, "input_periodic": False, "output_periodic": False}),
    ("wfc-synthetic-hard-8.json", "HARD", (47, 43), 810, {"pattern_size": 3, "input_periodic": False, "output_periodic": False}),
    ("wfc-synthetic-hard-8.json", "HARD", (48, 48), 811, {"pattern_size": 2, "input_periodic": True, "output_periodic": True}),
    ("wfc-synthetic-hard-8.json", "HARD", (46, 42), 812, {"pattern_size": 3, "input_periodic": True, "output_periodic": False, "allow_rotations": True, "allow_reflections": True}),
    ("wfc-synthetic-very-hard-10.json", "VERY_HARD", (59, 50), 813, {"pattern_size": 2, "input_periodic": False, "output_periodic": False}),
    ("wfc-synthetic-very-hard-10.json", "VERY_HARD", (58, 53), 814, {"pattern_size": 3, "input_periodic": True, "output_periodic": False, "allow_rotations": True}),
    ("wfc-synthetic-very-hard-10.json", "VERY_HARD", (50, 50), 815, {"pattern_size": 2, "input_periodic": True, "output_periodic": True}),
    ("wfc-synthetic-very-hard-10.json", "VERY_HARD", (57, 51), 816, {"pattern_size": 3, "input_periodic": False, "output_periodic": False, "allow_rotations": True, "allow_reflections": True}),
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
            "exemplar_digest": exemplar.digest,
            "exemplar": {
                "width": exemplar.width,
                "height": exemplar.height,
                "logical_pixels": list(exemplar.pixels),
                "source_palette": list(exemplar.source_palette),
                "digest": exemplar.digest,
            },
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
    return f"""<!doctype html><meta charset='utf-8'><title>M05 WFC Review</title><style>body{{background:#202533;color:#fff;font:12px sans-serif}}article{{display:inline-block;vertical-align:top;margin:8px;padding:8px;background:#303849;max-width:300px}}canvas{{image-rendering:pixelated;display:block;margin:4px 0;max-width:280px;height:auto}}small{{color:#b8c2cc;display:block}}</style><main id='sheet'></main><script>const manifest={data};const colors={colors};const root=document.getElementById('sheet');function canvasFor(cells,w,h,label){{const a=document.createElement('div');const l=document.createElement('small');l.textContent=label;a.appendChild(l);const canvas=document.createElement('canvas');const scale=Math.max(1,Math.floor(280/w));canvas.width=w*scale;canvas.height=h*scale;const x=canvas.getContext('2d');x.imageSmoothingEnabled=false;for(let i=0;i<cells.length;i++){{x.fillStyle=colors[cells[i]];x.fillRect((i%w)*scale,Math.floor(i/w)*scale,scale,scale);}}a.appendChild(canvas);return a;}}for(const c of manifest.candidates){{const a=document.createElement('article');const h=document.createElement('h3');h.textContent=c.exemplar_id+' · N'+c.metadata.pattern_size+' · seed '+c.seed;a.appendChild(h);a.appendChild(canvasFor(c.exemplar.logical_pixels,c.exemplar.width,c.exemplar.height,'Exemplar motif'));a.appendChild(canvasFor(c.logical_grid,c.dimensions[0],c.dimensions[1],'Generated WFC output'));const p=document.createElement('small');p.textContent='difficulty '+c.difficulty+' · output '+c.dimensions.join('×')+' · raw '+c.metadata.raw_extracted_window_count+' · transformed '+c.metadata.transformed_observation_count+' · unique '+c.metadata.unique_pattern_count+' · attempt '+c.metadata.attempt;a.appendChild(p);root.appendChild(a);}}</script>"""


if __name__ == "__main__":
    manifest = build_manifest()
    (OUTPUT / "m05_review_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "M05_WFC_CONTACT_SHEET.html").write_text(build_html(manifest), encoding="utf-8")
    print(f"M05 review candidates: {manifest['candidate_count']}")
