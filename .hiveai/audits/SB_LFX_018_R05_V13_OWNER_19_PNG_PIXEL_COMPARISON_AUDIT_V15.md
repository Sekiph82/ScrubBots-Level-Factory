# V15 GPT Independent Uploaded PNG Pixel-Level Comparison (2026-10-21)

**Scope:** 19 PNGs physically attached by the owner in this conversation and available in the current model's working sandbox: named 035, 036, 037–043, 045–051, 053–055. **These are NOT the previously requested 15 later 129–143 or 4 FAILED 019,056,058,060; those 19 requested files remain absent from the uploaded runtime.** This report intentionally does not claim to validate 38 original source bytes. Do not derive provenance or claim SHA equality to immutable owner Release sources without a matching signed source record.

**Method:** direct image-byte inspection with Pillow RGBA decode; canonical owner-locked palette `data/palette/scrubbots_palette_v3.json` 16 exact RGB values; pixels with alpha0 are VOID and their RGB ignored, alpha 1..254 is invalid, alpha255 is checked for exact color membership; valid distinct colors are counted **only among RGB matching canonical swatches**. Minimum artwork if transparent: at least 200 nontransparent pixels AND >=25% of area. Compared to published builder V13-A table rows near lines 480–501 for the identical filenames. No image edits, no quantization or solver runs.

**Result: 19/19 uploaded images have the EXACT SAME measured dimensions, canonical-color count, foreign-pixel count, semi-alpha count, and nontransparent art pixels as Codex's historical table.** This strongly independently corroborates the PNG validator behavior on these supplied file bytes, but cannot alone prove that all app source hashes and full solver behavior are correct.

| Attached PNG | Dimensions | Exact-V3 used colors | Fully-opaque foreign-color pixels | Semi-alpha pixels | Nontransparent pixels | Min artwork | Builder V13-A metric agreement |
|---|---:|---:|---:|---:|---:|---|---|
| `035_32x32px.png` | 32×32 | 1 | 461 | 0 | 481 | PASS | **MATCH** |
| `036_50x50px.png` | 50×50 | 1 | 0 | 1443 | 1444 | PASS | **MATCH** |
| `037_56x56px.png` | 56×56 | 0 | 611 | 0 | 611 | FAIL | **MATCH** |
| `038_32x32px.png` | 32×32 | 1 | 401 | 0 | 583 | PASS | **MATCH** |
| `039_56x56px.png` | 56×56 | 0 | 603 | 0 | 603 | FAIL | **MATCH** |
| `040_32x32px.png` | 32×32 | 1 | 645 | 0 | 703 | PASS | **MATCH** |
| `041_32x32px.png` | 32×32 | 2 | 213 | 0 | 435 | PASS | **MATCH** |
| `042_32x32px.png` | 32×32 | 0 | 397 | 0 | 397 | PASS | **MATCH** |
| `043_32x32px.png` | 32×32 | 1 | 485 | 0 | 595 | PASS | **MATCH** |
| `045_56x56px.png` | 56×56 | 0 | 773 | 0 | 773 | FAIL | **MATCH** |
| `046_32x32px.png` | 32×32 | 0 | 426 | 0 | 426 | PASS | **MATCH** |
| `047_56x56px.png` | 56×56 | 0 | 841 | 0 | 841 | PASS | **MATCH** |
| `048_32x32px.png` | 32×32 | 0 | 753 | 0 | 753 | PASS | **MATCH** |
| `049_32x32px.png` | 32×32 | 2 | 651 | 0 | 679 | PASS | **MATCH** |
| `050_56x56px.png` | 56×56 | 0 | 427 | 0 | 427 | FAIL | **MATCH** |
| `051_32x32px.png` | 32×32 | 0 | 163 | 0 | 163 | FAIL | **MATCH** |
| `053_56x56px.png` | 56×56 | 0 | 199 | 0 | 199 | FAIL | **MATCH** |
| `054_56x56px.png` | 56×56 | 0 | 1269 | 0 | 1269 | PASS | **MATCH** |
| `055_32x32px.png` | 32×32 | 0 | 427 | 0 | 427 | PASS | **MATCH** |

**Observed:** 18/19 images have fully opaque RGBs outside the 16-color game palette. The only exception `036_50x50px.png` has **1,443 semitransparent pixels** and 1 canonical opaque RGB color; its color-count gate also fails. All 19 have only 0–2 canonical used colors (required 3–12), although the images visibly contain many actual unique colors (several tens): the code counts only colors that EXACTLY match v3, rather than visible distinct foreign colors. 6/19 additionally fail the geometric/art-area threshold. Exact rejection for all 19 is therefore consistent with the locked source-validation contract. `PNG is visually attractive` is not the same as `satisfies current logical-cell palette and alpha contract`.

**No automatic remediation**: user explicitly doubts that repairing these older rejected PNGs is worth effort; do not recolor original files, relax the palette, silently snap colors, requeue 34 or change 102 READY pool without separately scoped owner authority. Only use comparison as a validator correctness checkpoint.

**Separate owner change on native solver timing:** Owner requested at t=0 a 240s budget, and *if the SAME native solver process is still running unsolved at 240s*, extend its **total** time cap to 480s, not restart and not 240+480=720s. Implement as an auditable soft deadline at 240 and hard deadline at 480, preserving pinned-runtime SHA, job identity, cancel semantics, max-visited/memory bounds, stdout reader and no duplicate native job, then offline/fake-time tests. Never auto-rerun old FAILED 056/058/060 or override current completed 140 job. This is a design/implementation instruction only, **no code or actual solve test yet**.

**Source references:** owner attachments above, `src/scrubbots_pixel_factory/studio_extensions.py::_owner_source_grid,validate_owner_source`, `data/palette/scrubbots_palette_v3.json`, builder 38-issue table, `src/scrubbots_pixel_factory/supply_pipeline/solver_budget.py`, `.../scrubbots_solver.py`. 
