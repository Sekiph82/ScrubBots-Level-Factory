"""Build committed, review-only M03 manifest and self-contained contact sheet."""

import json
from html import escape
from pathlib import Path

from scrubbots_pixel_factory import CANONICAL_PALETTE
from scrubbots_pixel_factory.core import GenerationRequest
from scrubbots_pixel_factory.generators import FAMILY_NAMES
from scrubbots_pixel_factory.generators import MaskSpriteGenerator
from scrubbots_pixel_factory.generators.mask import color_component_sizes


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent
RECTANGLES = {
    "EASY": (29, 23),
    "MEDIUM": (30, 39),
    "HARD": (48, 41),
    "VERY_HARD": (59, 50),
}
SEEDS = (11, 23, 47)


def build_manifest() -> dict[str, object]:
    generator = MaskSpriteGenerator()
    candidates = []
    for difficulty_index, (difficulty, (width, height)) in enumerate(RECTANGLES.items()):
        for family_index, family in enumerate(FAMILY_NAMES):
            seed = SEEDS[(difficulty_index + family_index) % len(SEEDS)]
            request = GenerationRequest(difficulty=difficulty, seed=seed, generator_mode="MASK", style=family, width=width, height=height)
            candidate = generator.generate_candidate(request)
            if not hasattr(candidate, "result") or not candidate.result.is_success:
                raise RuntimeError(f"review candidate failed: {difficulty}/{family}/{seed}")
            result = candidate.result
            grid = list(result.logical_grid)
            component_sizes = color_component_sizes(grid, width, height)
            candidates.append({
                "label": f"M03-{family_index + 1:02d}-{difficulty}-{seed}",
                "family": family,
                "seed": seed,
                "difficulty": difficulty,
                "width": width,
                "height": height,
                "resolved_palette": list(result.used_palette),
                "foreground_mask": [1 if value else 0 for value in candidate.mask.foreground_cells],
                "logical_grid": grid,
                "diagnostics": {
                    "occupancy_pct": round(sum(candidate.mask.foreground_cells) * 100 / (width * height), 3),
                    "singleton_color_components": sum(size == 1 for sizes in component_sizes.values() for size in sizes),
                    "total_color_components": sum(len(sizes) for sizes in component_sizes.values()),
                    "role_counts": {
                        role.value: candidate.roles.count(role)
                        for role in sorted(set(candidate.roles), key=lambda value: value.value)
                    },
                },
            })
    for candidate in candidates:
        peers = [
            other for other in candidates
            if other["width"] == candidate["width"] and other["height"] == candidate["height"] and other is not candidate
        ]
        mask = candidate["foreground_mask"]
        scores = []
        for other in peers:
            other_mask = other["foreground_mask"]
            intersection = sum(left and right for left, right in zip(mask, other_mask))
            union = sum(left or right for left, right in zip(mask, other_mask))
            scores.append(intersection / union if union else 0.0)
        candidate["diagnostics"]["top_pairwise_jaccard"] = round(max(scores, default=0.0), 6)
    return {
        "evidence_type": "review-only / non-production / M03 manual audit evidence",
        "generator": "mask-sprite 1.0.0",
        "palette_source": "SCRUBBOTS canonical palette C01..C16",
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def build_html(manifest: dict[str, object]) -> str:
    palette = {color_id: CANONICAL_PALETTE.hex_for(color_id) for color_id in CANONICAL_PALETTE.ids}
    data = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    colors = json.dumps(palette, separators=(",", ":"))
    title = escape(str(manifest["evidence_type"]))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>M03 Mask Contact Sheet</title>
<style>body{{margin:24px;background:#202533;color:#fff;font:14px system-ui,sans-serif}}h1{{font-size:24px}}.note{{color:#b8c2cc}}.sheet{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}article{{background:#303949;border:1px solid #596579;border-radius:8px;padding:10px}}h2{{font-size:14px;margin:0 0 8px}}canvas{{display:block;background:#202533;image-rendering:pixelated;max-width:100%;height:auto;border:1px solid #596579}}p{{margin:6px 0;color:#d8dee8;font-size:12px}}</style></head>
<body><h1>M03 Mask / Sprite Contact Sheet</h1><p class="note">{title}. Presentation only: logical source cells remain row-major C-IDs; this sheet uses integer canvas blocks and does not export production art.</p><section id="sheet" class="sheet"></section>
<script>
const manifest={data};const colors={colors};const sheet=document.getElementById('sheet');
for(const candidate of manifest.candidates){{const article=document.createElement('article');const heading=document.createElement('h2');heading.textContent=candidate.label+' · '+candidate.family;article.appendChild(heading);const block=4;const silhouette=document.createElement('canvas');silhouette.width=candidate.width*block;silhouette.height=candidate.height*block;silhouette.style.width=(candidate.width*block)+'px';silhouette.style.height=(candidate.height*block)+'px';const silhouetteContext=silhouette.getContext('2d');silhouetteContext.imageSmoothingEnabled=false;for(let i=0;i<candidate.foreground_mask.length;i++){{const x=i%candidate.width;const y=Math.floor(i/candidate.width);silhouetteContext.fillStyle=candidate.foreground_mask[i]?'#ffffff':'#202533';silhouetteContext.fillRect(x*block,y*block,block,block);}}article.appendChild(silhouette);const canvas=document.createElement('canvas');canvas.width=candidate.width*block;canvas.height=candidate.height*block;canvas.style.width=(candidate.width*block)+'px';canvas.style.height=(candidate.height*block)+'px';const context=canvas.getContext('2d');context.imageSmoothingEnabled=false;for(let i=0;i<candidate.logical_grid.length;i++){{const x=i%candidate.width;const y=Math.floor(i/candidate.width);context.fillStyle=colors[candidate.logical_grid[i]];context.fillRect(x*block,y*block,block,block);}}article.appendChild(canvas);const meta=document.createElement('p');meta.textContent=candidate.difficulty+' · '+candidate.width+'×'+candidate.height+' · seed '+candidate.seed+' · '+candidate.resolved_palette.join(', ')+' · singleton '+candidate.diagnostics.singleton_color_components+' · components '+candidate.diagnostics.total_color_components+' · top Jaccard '+candidate.diagnostics.top_pairwise_jaccard;article.appendChild(meta);sheet.appendChild(article);}}
</script></body></html>"""


if __name__ == "__main__":
    manifest = build_manifest()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "m03_review_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUTPUT / "M03_MASK_CONTACT_SHEET.html").write_text(build_html(manifest), encoding="utf-8")
    print(f"review candidates: {manifest['candidate_count']}")
