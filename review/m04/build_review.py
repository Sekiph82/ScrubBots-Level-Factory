"""Build self-contained, review-only M04 primitive and recipe evidence."""

import json
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest
from scrubbots_pixel_factory.core import DeterministicRNG
from scrubbots_pixel_factory.generators.rules import (
    PRIMITIVE_NAMES,
    RECIPE_NAMES,
    RuleCandidate,
    RuleCanvas,
    RuleShapeGenerator,
    apply_primitive,
    color_component_sizes,
    connected_components,
)


OUTPUT = Path(__file__).parent
RECTANGLES = {"EASY": (29, 23), "MEDIUM": (30, 39), "HARD": (48, 41), "VERY_HARD": (59, 50)}
PRIMITIVE_PARAMETERS = {
    "BLOB": {"target": 35}, "ISLAND": {"target": 24}, "RING": {"radius": 7, "thickness": 1},
    "CORRIDOR": {"width_cells": 2}, "POCKET": {"size": 3}, "SNAKE": {"max_steps": 32},
    "BRANCH": {"depth": 8, "branch_count": 3}, "CHAMBER": {"chamber_width": 11, "chamber_height": 9},
    "SPIRAL": {"turns": 3}, "WAVE": {"period": 5, "amplitude": 3},
    "RADIAL": {"rays": 8, "length": 7}, "VORONOI": {"regions": 4},
}


def _primitive_entry(name: str) -> dict[str, object]:
    canvas = RuleCanvas(29, 23)
    primitive_rng = DeterministicRNG(41)
    pre_carve = None
    if name == "POCKET":
        apply_primitive(canvas, "CHAMBER", primitive_rng.child("context"), chamber_width=11, chamber_height=9)
        pre_carve = set(canvas.occupied)
        geometry = apply_primitive(canvas, name, primitive_rng.child("target"), **PRIMITIVE_PARAMETERS[name])
    else:
        geometry = apply_primitive(canvas, name, primitive_rng, **PRIMITIVE_PARAMETERS[name])
    occupied = set(canvas.occupied)
    grid = ["C01" if index in occupied else "C02" for index in range(canvas.size)]
    components = connected_components(occupied, canvas) if occupied else ()
    component_sizes = [len(component) for component in components]
    diagnostics = {
        "occupied_cells": len(occupied), "occupied_component_count": len(components),
        "geometry_sha256": canvas.region_digest() if isinstance(geometry, dict) else canvas.geometry_digest(),
        "primitive_parameters": PRIMITIVE_PARAMETERS[name],
        "singleton_count": sum(size == 1 for size in component_sizes),
        "occupied_component_sizes": component_sizes,
    }
    if pre_carve is not None:
        diagnostics.update({
            "pre_carve_occupied_cells": len(pre_carve),
            "carved_cells": len(pre_carve - occupied),
            "pocket_carves_only": (pre_carve - occupied).issubset(pre_carve) and len(occupied) < len(pre_carve),
        })
    return {
        "kind": "primitive", "primitive": name, "seed": 41, "dimensions": [29, 23],
        "geometry_mask": [1 if index in occupied else 0 for index in range(canvas.size)],
        "logical_grid": grid, "resolved_palette": ["C01", "C02"],
        "diagnostics": diagnostics,
    }


def _recipe_entry(generator: RuleShapeGenerator, recipe: str, difficulty: str, seed: int) -> dict[str, object]:
    width, height = RECTANGLES[difficulty]
    request = GenerationRequest(difficulty=difficulty, seed=seed, generator_mode="RULES", style=recipe, width=width, height=height)
    candidate = generator.generate_candidate(request)
    if not isinstance(candidate, RuleCandidate):
        raise RuntimeError(f"review candidate failed: {recipe}/{difficulty}/{seed}")
    result = candidate.result
    component_sizes = color_component_sizes(result.logical_grid, width, height)
    base_color = result.used_palette[0]
    occupied = set(candidate.canvas.occupied)
    negative = set(candidate.canvas.negative)
    base_on_occupied = sum(index in occupied and result.logical_grid[index] == base_color for index in range(width * height))
    non_base_on_negative = sum(index in negative and result.logical_grid[index] != base_color for index in range(width * height))
    accent_color = candidate.accent_color
    accent_sizes = list(component_sizes.get(accent_color, ())) if accent_color else []
    effective_cap = candidate.recipe.max_color_dominance_pct
    return {
        "kind": "recipe", "recipe": recipe, "recipe_version": candidate.recipe.version, "difficulty": difficulty, "seed": seed,
        "dimensions": [width, height], "geometry_mask": [1 if index in candidate.canvas.occupied else 0 for index in range(width * height)],
        "logical_grid": list(result.logical_grid), "resolved_palette": list(result.used_palette),
        "diagnostics": {
            "occupancy_pct": round(len(candidate.canvas.occupied) * 100 / (width * height), 3),
            "occupied_component_count": len(connected_components(set(candidate.canvas.occupied), candidate.canvas)),
            "color_components": {key: list(value) for key, value in component_sizes.items()},
            "singleton_count": sum(size == 1 for sizes in component_sizes.values() for size in sizes),
            "max_color_dominance_pct": round(max(result.logical_grid.count(color) for color in result.used_palette) * 100 / (width * height), 3),
            "effective_max_dominance_pct": effective_cap,
            "base_color": base_color,
            "negative_space_count": len(negative),
            "occupied_count": len(occupied),
            "base_on_occupied": base_on_occupied,
            "non_base_on_negative": non_base_on_negative,
            "geometry_color_fidelity": base_on_occupied == 0 and non_base_on_negative == 0 and all((result.logical_grid[index] != base_color) == (index in occupied) for index in range(width * height)),
            "accent_color": accent_color,
            "accent_component_sizes": accent_sizes,
            "color_roles": {color: role for color, role in candidate.color_roles},
            "geometry_sha256": candidate.canvas.geometry_digest(), "region_sha256": candidate.canvas.region_digest(),
        },
    }


def build_manifest() -> dict[str, object]:
    candidates = [_primitive_entry(name) for name in PRIMITIVE_NAMES]
    generator = RuleShapeGenerator()
    for difficulty_index, difficulty in enumerate(RECTANGLES):
        for recipe_index, recipe in enumerate(RECIPE_NAMES):
            candidates.append(_recipe_entry(generator, recipe, difficulty, 401 + difficulty_index * 31 + recipe_index))
    return {
        "evidence_type": "review-only / non-production / M04 manual audit evidence",
        "generator": "rule-shape 1.0.0", "palette_source": "SCRUBBOTS canonical palette C01..C16",
        "primitive_count": len(PRIMITIVE_NAMES), "recipe_count": len(RECIPE_NAMES), "candidate_count": len(candidates),
        "candidates": candidates,
    }


def build_html(manifest: dict[str, object]) -> str:
    palette = {f"C{index:02d}": color for index, color in enumerate(("#E94B4B", "#F28C3C", "#F2C94C", "#55B85A", "#63D6A3", "#42C7D9", "#3E7EDB", "#3451A3", "#845EC2", "#E66FA5", "#956447", "#E8CFA0", "#B8C2CC", "#3D4652", "#FFFFFF", "#000000"), 1)}
    data = json.dumps(manifest, separators=(",", ":"), ensure_ascii=False)
    colors = json.dumps(palette, separators=(",", ":"))
    return f"""<!doctype html><meta charset='utf-8'><title>M04 RULES Review</title><style>body{{background:#202533;color:#fff;font:12px sans-serif}}article{{display:inline-block;vertical-align:top;margin:8px;padding:8px;background:#303849}}canvas{{image-rendering:pixelated;display:block;margin:4px 0}}</style><main id='sheet'></main><script>const manifest={data};const colors={colors};const root=document.getElementById('sheet');for(const c of manifest.candidates){{const a=document.createElement('article');const h=document.createElement('h3');h.textContent=(c.kind==='primitive'?c.primitive:c.recipe)+' · '+(c.difficulty||'PRIMITIVE')+' · seed '+c.seed;a.appendChild(h);for(const mode of ['geometry_mask','logical_grid']){{const canvas=document.createElement('canvas');canvas.width=c.dimensions[0]*4;canvas.height=c.dimensions[1]*4;canvas.style.width=canvas.width+'px';canvas.style.height=canvas.height+'px';const x=canvas.getContext('2d');x.imageSmoothingEnabled=false;const cells=c[mode];for(let i=0;i<cells.length;i++){{const value=mode==='geometry_mask'?(cells[i]?'#FFFFFF':'#202533'):colors[cells[i]];x.fillStyle=value;x.fillRect((i%c.dimensions[0])*4,Math.floor(i/c.dimensions[0])*4,4,4);}}a.appendChild(canvas);}}const p=document.createElement('p');p.textContent='occupancy '+(c.diagnostics.occupancy_pct??(c.diagnostics.occupied_cells*100/(c.dimensions[0]*c.dimensions[1])).toFixed(2))+' · singleton '+c.diagnostics.singleton_count;p.style.margin='0';a.appendChild(p);root.appendChild(a);}}</script>"""


if __name__ == "__main__":
    manifest = build_manifest()
    (OUTPUT / "m04_review_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "M04_RULES_CONTACT_SHEET.html").write_text(build_html(manifest), encoding="utf-8")
    print(f"M04 review candidates: {manifest['candidate_count']}")
