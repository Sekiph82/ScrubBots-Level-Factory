# V15 GPT Independent Uploaded PNG Pixel-Level Comparison (2026-10-21)

**Corrected scope (owner screenshot re-check 2026-10-21):** The owner's earlier message actually included **both groups**. The 19 previously checked sources (035–055) **and all 15 later REJECTED (129–143), plus 3 of 4 FAILED (056/058/060)** exist as real PNG bytes in `/mnt/data` and have now been independently read. **The ONLY requested FAILED source not found is `019_32x32px.png`; an unrelated `014_32x32px.png` was supplied instead**, and its pixels were separately inspected. Prior statement that 15+4 were not attached was incorrect and is explicitly superseded. Reports below compare attached files' actual PNG pixels to saved builder metrics; no claim of installed immutable Release source SHA equivalence without its original source record.

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

## 2026-10-21 owner screenshot correction: 15 late REJECTED + 3 FAILED actually arrived earlier

**Apology/correction:** Assistant originally overlooked the already mounted second upload and reported it as not received. Fresh filesystem inspection showed **15/15 `129_...` through `143_...`** and **3/4 FAILED `056,058,060`** already present and available. Only `019_32x32px.png` missing; `014_32x32px.png` was present, a different source. No request to upload the 18 already-received files again.

Fresh RGBA pixel-by-pixel analysis using exact sixteen V3 palette values independently matched Codex V13-A persisted log **15/15** late rejected files: dimensions, valid canonical colors, fully opaque off-palette pixel counts, intermediate alpha counts and non-transparent artwork counts.

| PNG | Dimensions | V3 colors exactly used | Off-palette opaque pixels | Semi-alpha | Nontransparent pixels | Minimum artwork | Codex table |
|---|---:|---:|---:|---:|---:|---|---|
| `129_32x32px.png` | 32×32 | 0 | 330 | 0 | 330 | PASS | MATCH |
| `130_35x35px.png` | 35×35 | 1 | 466 | 0 | 472 | PASS | MATCH |
| `131_32x32px.png` | 32×32 | 0 | 442 | 0 | 442 | PASS | MATCH |
| `132_36x36px.png` | 36×36 | 1 | 660 | 0 | 661 | PASS | MATCH |
| `133_32x32px.png` | 32×32 | 1 | 488 | 0 | 489 | PASS | MATCH |
| `134_34x34px.png` | 34×34 | 1 | 733 | 0 | 738 | PASS | MATCH |
| `135_34x34px.png` | 34×34 | 0 | 295 | 0 | 295 | PASS | MATCH |
| `136_34x34px.png` | 34×34 | 0 | 753 | 0 | 753 | PASS | MATCH |
| `137_32x32px.png` | 32×32 | 0 | 322 | 0 | 322 | PASS | MATCH |
| `138_32x32px.png` | 32×32 | 0 | 407 | 0 | 407 | PASS | MATCH |
| `139_37x37px.png` | 37×37 | 1 | 669 | 0 | 673 | PASS | MATCH |
| `140_32x32px.png` | 32×32 | 1 | 531 | 0 | 541 | PASS | MATCH |
| `141_32x32px.png` | 32×32 | 1 | 268 | 0 | 283 | PASS | MATCH |
| `142_33x33px.png` | 33×33 | 1 | 670 | 0 | 683 | PASS | MATCH |
| `143_37x37px.png` | 37×37 | 1 | 705 | 0 | 706 | PASS | MATCH |

All 15 violate `FOREIGN_COLORS` and `USED_COLOR_COUNT`, with zero semitransparent pixels and minimum-artwork PASS. These facts reproduce every V13-A table count, no aesthetic opinions or color conversion needed.

**3 actually uploaded FAILED PNGs, strict source validation:**

| PNG | Pixels | V3 colors used | Foreign pixels | Semi-alpha | Art cells | Strict source result | Saved failure |
|---|---|---:|---:|---:|---:|---|---|
| `056_50x50px.png` | 50×50 | 9 | 0 | 0 | 2,500 | **PASS** | Solver reached 240s timeout |
| `058_50x50px.png` | 50×50 | 10 | 0 | 0 | 2,500 | **PASS** | Solver reached 240s timeout |
| `060_50x50px.png` | 50×50 | 12 | 0 | 0 | 2,500 | **PASS** | Solver reached 240s timeout |

These three are **not failed artwork validation**: they are exact-palette, fully opaque 50×50s with allowed 9/10/12 color counts. Their **solver timeout cannot be proven from PNG bytes**, but the linked Codex run receipt separately records native bounded solve at 240s for each. One `014_32x32px.png` was also uploaded; strict source validation PASS: 7 canonical colors, zero foreign, zero semi-alpha, 588/1024 nontransparent cells. `014` is **not** the absent `019` and must not be treated as proof for the Windows access-denied error.

**Overall independent attachment metric coverage now:** all **34/34 REJECTED PNGs** (19 previous +15 newly recognized), **3/4 FAILED PNG source validations**, and **1 unrelated 014 source**. **37 of 38 requested problem PNGs directly examined**, all 34 reject findings confirmed, 3 solver PNGs passed source rules. `019` PNG absent, and even if uploaded its bytes alone cannot prove the WinError5 path/ACL root cause. Current total READY 102 and batch COMPLETE 140 unchanged. No Godot solve runs, palette quantization or source alterations. Scoped V13-C installation and V13-D staged 240→480 native solver source implementation remain pending.

