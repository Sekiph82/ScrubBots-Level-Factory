# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, `review/` evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP05 — LEVEL_ART Semantic Integration**
- Current Phase: **HARD-CELL COMPILER IMPLEMENTATION**
- Current Task: **PAG-SP05-C001 — LEVEL_ART Hard-Cell Compiler, Palette Snap & Difficulty Budget**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX BUILDER**
- Current Prompt: `.hiveai/prompts/PAG-SP05-C001_LEVEL_ART_HARD_CELL_COMPILER_PALETTE_SNAP_AND_DIFFICULTY_BUDGET_PROMPT.md`
- Owner Decision Authority: `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V01.md`
- Previous Compatibility Cycle: `PAG-SP04-C006` → **PASS / CLOSED**
- C006 Strict Audit: `.hiveai/audits/PAG-SP04-C006_PNG_IDAT_CONTIGUITY_AND_STRUCTURAL_FAIL_CLOSED_CLOSURE_STRICT_AUDIT.md`
- Official Magnific Q02/Q03 Evidence: `review/sp04/SP04_Q02_Q03_MAGNIFIC_OFFICIAL_LOCAL_NORMALIZATION_2026-09-14.md`
- Owner Decisions Locked:
  - **Magnific semantic wizard direction accepted.**
  - **`AREA_AVERAGE_V1` is OWNER REJECTED for LEVEL_ART because it creates blended/intermediate edge colors.**
  - **CELL_MAJORITY is OWNER ACCEPTED as the high-resolution semantic-image → logical-cell reduction direction for LEVEL_ART.**
  - **Canonical LEVEL_ART workflow: `SEMANTIC IMAGE → CELL_MAJORITY → PALETTE SNAP → ONE LOGICAL PIXEL = ONE GAMEPLAY CELL → C01..C16 → DIFFICULTY USED-COLOR BUDGET → VALIDATION/EXPORT`.**
- Next Action: **Codex implements SP05-C001 exactly from the published prompt, pushes `main`, then stops for ChatGPT strict audit.**
- Credit Policy: **No Magnific or PixelLab call is authorized in SP05-C001. Spend zero provider credits.**
- Blockers/Waits: **M11 remains blocked** until semantic LEVEL_ART passes the owner-locked logical-grid/palette/difficulty contract and semantic review. M08/LevelData bridge remains outside C001 and follows only after the hard-cell compiler passes strict audit.
- Approved Semantic Providers: **MAGNIFIC**, **PIXELLAB**
- Provider Architecture: **provider-neutral; explicit provider/model/engine selection; no silent fallback**
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Owner-Locked Contracts

### LEVEL_ART

- EASY: width/height independently 20–29
- MEDIUM: 30–39
- HARD: 40–49
- VERY_HARD: 50–59
- rectangular boards allowed
- one logical artwork pixel = one gameplay cell
- C01..C16 logical palette only
- EASY 3–5 distinct used colors
- MEDIUM 6–7
- HARD 8–9
- VERY_HARD 10–12
- BG01 `#202533` presentation/background only
- no interpolation/antialiasing inside logical cells
- deterministic provenance/export required
- **high-resolution semantic-image reduction policy: CELL_MAJORITY**
- **palette stage: deterministic palette snap to C01..C16**
- **difficulty color-budget stage: deterministic enforcement/rejection against the requested difficulty band**
- `AREA_AVERAGE_V1` must not be used as the canonical LEVEL_ART logical-grid reduction policy.
- Canonical workflow authority: `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V01.md`.

### ASSET_ART

- Separate from LevelData/difficulty legality.
- **24x24 px is the first owner-approved ASSET_ART baseline target.**
- 24x24 is not the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART.
- ASSET_ART may retain separate normalization/palette policies when explicitly specified.
- ASSET_ART policy must never override the owner-locked LEVEL_ART workflow.

## Existing Canonical Authorities Reused by SP05-C001

- `src/scrubbots_pixel_factory/contracts/palette.py` — immutable owner-locked C01..C16 palette; BG01 forbidden as logical color.
- `src/scrubbots_pixel_factory/contracts/color_usage.py` — actual-used-color counting and difficulty-band validation.
- `src/scrubbots_pixel_factory/contracts/difficulty.py` — independent width/height difficulty bands and rectangle legality.
- accepted SP03/SP04 raw artifact, PNG decode and provenance foundation.

SP05-C001 must consume these authorities; it must not duplicate or redefine them.

## Magnific Live Evidence

Accepted source facts:

- provider/model direction: Magnific `recraft-v4-1` wizard smoke;
- owner accepted semantic/readability direction;
- provider creation metadata previously reported 2048x2048;
- owner-downloaded exact file used for local qualification is **1024x1024**, **265479 bytes**;
- source SHA-256: `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`;
- source profile: 8-bit RGB, non-interlaced;
- chunk sequence: `IHDR -> caBX -> fdEC -> IDAT -> IEND`;
- metadata-vs-downloaded-file dimension mismatch remains visible and unresolved, not silently reconciled;
- Q03 `AREA_AVERAGE_V1` 24x24 result had 124 RGBA colors and was **OWNER REJECTED for LEVEL_ART visual behavior**;
- nearest-neighbor diagnostic was not selected;
- CELL_MAJORITY diagnostic was **OWNER ACCEPTED as the LEVEL_ART logical-cell reduction direction**.

## Milestone Overview

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [x] PAG-SP03 — Semantic Normalization Pipeline technical foundation
- [~] PAG-SP04 — Semantic Provider / Model / Workflow Qualification — **Magnific live path technically qualified through Q04 owner disposition; PixelLab/comparative qualification deferred until useful/authorized**
- [~] PAG-SP05 — LEVEL_ART Semantic Integration — **C001 READY: CELL_MAJORITY → C01..C16 → difficulty-budget compiler**
- [ ] PAG-SP06 — Semantic Quality / Recognizability Gate
- [ ] PAG-SP07 — Reference / Style Generation
- [ ] PAG-SP08 — Edit / Inpaint
- [ ] PAG-SP09 — Pixel Studio Create / Gallery UI
- [ ] PAG-SP10 — Automated Weekly Semantic Batch
- [ ] PAG-SP11 — ASSET_ART Production
- [ ] PAG-SP12 — Direction / Rotation Variants
- [ ] PAG-SP13 — Animation
- [ ] PAG-SP14 — ScrubBots Level Factory Bridge

M00–M10 remain historical accepted technical foundation except the M10 visual pack, which remains **OWNER REJECTED 100/100**. M11 remains blocked pending semantic replacement acceptance.

---

# PAG-SP04 — Accepted Live Qualification State

- C004 — **PASS / CLOSED** offline qualification foundation.
- C005 — FAIL / remediated by C006.
- C006 — **PASS / CLOSED** PNG ancillary + IDAT structural compatibility.
- Q01 — local owner-supplied artifact byte identity captured; provider-metadata 2048 vs downloaded-file 1024 mismatch remains recorded.
- Q02 — **PASS**, real owner-supplied Magnific PNG accepted by strict decoder without rewriting bytes.
- Q03 — deterministic `AREA_AVERAGE_V1` execution technically passed but its blended LEVEL_ART visual policy was owner rejected.
- Q04 — **OWNER DISPOSITION RECORDED:** CELL_MAJORITY selected; AREA_AVERAGE rejected for LEVEL_ART.
- Q05/Q06/Q07 — PixelLab/comparative/default-provider selection remains deferred and must not reopen the local LEVEL_ART compiler contract.

---

# PAG-SP05-C001 — LEVEL_ART Hard-Cell Compiler, Palette Snap & Difficulty Budget

State: **READY_FOR_IMPLEMENTATION**

Prompt:
`.hiveai/prompts/PAG-SP05-C001_LEVEL_ART_HARD_CELL_COMPILER_PALETTE_SNAP_AND_DIFFICULTY_BUDGET_PROMPT.md`

Required implementation closure:

- [ ] separate typed LEVEL_ART semantic request/result/report boundary;
- [ ] `CELL_MAJORITY_V1` with exact deterministic source footprints and no averaging/interpolation;
- [ ] exact-size fast path;
- [ ] source smaller than target fails closed in V1;
- [ ] non-opaque majority winner fails closed;
- [ ] deterministic `PALETTE_SNAP_V1` to owner-locked C01..C16 only;
- [ ] BG01 never appears in logical cells;
- [ ] palette snap uses deterministic squared-RGB distance and canonical-index tie-break;
- [ ] in-band actual used-color count remains unchanged;
- [ ] below-minimum actual used-color count fails closed without fabricated colors;
- [ ] above-maximum actual used-color count reduces deterministically to the difficulty maximum using the prompt-defined weighted exact subset optimization;
- [ ] final cells pass existing `validate_used_color_count`;
- [ ] all difficulty dimension bands and rectangles remain legal through existing contracts;
- [ ] raw artifact/request/intermediate/final provenance is immutable and exact;
- [ ] accepted ASSET_ART behavior remains unchanged;
- [ ] no provider calls / zero credits;
- [ ] no M08/LevelData/solver/SP06/UI expansion in C001;
- [ ] builder does not edit root `TASKS.md`;
- [ ] ChatGPT strict audit required before closure.

---

## Current Stop / Action Rule

**Execute only PAG-SP05-C001.**

Do not re-litigate the LEVEL_ART workflow. Do not call Magnific or PixelLab. Do not spend credits. Do not begin M08/LevelData integration, solver integration, SP06, Studio UI, weekly batches or M11. After Codex pushes C001, stop for ChatGPT strict audit.