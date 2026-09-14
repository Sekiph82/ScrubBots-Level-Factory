# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker** for the active Semantic Pixel Studio / Level Factory work. Historical cycle detail remains in Git history, `.hiveai/prompts/`, `.hiveai/codex-logs/`, `.hiveai/audits/`, `review/` evidence and published owner-decision documents.

Only ChatGPT, acting as independent auditor/tracker owner, may promote task state or mark a cycle/milestone accepted or closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP05 — LEVEL_ART Semantic Integration**
- Current Phase: **TRUSTED EVIDENCE REMEDIATION**
- Current Task: **PAG-SP05-C003 — Trusted Report Binding & Acceptance Evidence Closure**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX BUILDER**
- Current Prompt: `.hiveai/prompts/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_PROMPT.md`
- Current Owner Decision Authority: `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md`
- C002 Builder Log: `.hiveai/codex-logs/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_CODEX_LOG.md`
- C002 Strict Audit: `.hiveai/audits/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_STRICT_AUDIT.md`
- C002 Revalidation: **2026-09-14 — FAIL verdict independently rechecked after builder-log receipt; verdict unchanged.**
- C001 Strict Audit: `.hiveai/audits/PAG-SP05-C001_LEVEL_ART_HARD_CELL_COMPILER_PALETTE_SNAP_AND_DIFFICULTY_BUDGET_STRICT_AUDIT.md`
- Previous Compatibility Cycle: `PAG-SP04-C006` → **PASS / CLOSED**
- SP05-C001: **FAIL / SUPERSEDED BY C002 REMEDIATION**
- SP05-C002: **FAIL / CORE DIFFICULTY V1 CONVERGENCE RETAINED; TRUST BINDING REMEDIATION REQUIRED**
- Next Action: **Codex executes only SP05-C003 from the published prompt, pushes `main`, then stops for ChatGPT strict audit.**
- Credit Policy: **No Magnific or PixelLab call is authorized in SP05-C003. Spend zero provider credits.**
- Blockers/Waits: **M08/LevelData bridge, solver integration, SP06 semantic recognizability, Studio feature expansion, weekly batching and M11 remain blocked until SP05-C003 passes independent audit.**
- Approved Semantic Providers: **MAGNIFIC**, **PIXELLAB**
- Provider Architecture: **provider-neutral; explicit provider/model/engine selection; no silent fallback**
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\\Users\\sekip\\Desktop\\Scrubbots - Pixel Art Generator`

## Current Owner-Locked LEVEL_ART Contract

Current Difficulty V1 production legality is independent of EASY/MEDIUM/HARD/VERY_HARD class bands.

- width: **20..59 inclusive**;
- height: **20..59 inclusive**;
- width and height validated independently;
- rectangular boards legal;
- one logical artwork pixel = one gameplay cell;
- logical palette: **C01..C16 only**;
- BG01 `#202533` remains presentation/background only;
- production used-color envelope: **3..12 distinct C01..C16 colors**, independent of lane/class;
- 3..12 snapped grids remain unchanged merely because lane/class metadata changes;
- fewer than 3 colors fail closed; no fabricated accents/colors;
- more than 12 colors reduce deterministically to exactly 12 using the retained exact weighted subset/remap policy;
- envelope reduction may not introduce a C-ID absent from the snapped used set;
- high-resolution semantic-image reduction policy: **CELL_MAJORITY_V1**;
- palette stage: **PALETTE_SNAP_V1**;
- no averaging/interpolation/antialiasing inside logical cells;
- deterministic exact provenance/export required;
- lane/class metadata may remain for lineage but must be non-transformative;
- Challenge Score / Session Load / Frustration / solver / campaign fit remain downstream concerns, not hard-cell compiler legality.

Historical class-specific rules remain compatibility evidence only:

- EASY 20–29 / 3–5 colors;
- MEDIUM 30–39 / 6–7 colors;
- HARD 40–49 / 8–9 colors;
- VERY_HARD 50–59 / 10–12 colors.

They must not be reintroduced as current production semantic-compiler truth.

Canonical workflow authority:

`docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md`

## Trusted Evidence Contract

A trusted LEVEL_ART artifact/report must bind the actual canonical stages, not caller assertions.

Required invariant chain:

`SemanticRawArtifact → CELL_MAJORITY_V1 → PALETTE_SNAP_V1 → PRODUCTION_COLOR_ENVELOPE_V1 → final logical cells`

Trusted evidence must bind:

- exact source raw-artifact digest;
- exact source raw SHA-256;
- request digest and target dimensions;
- majority RGBA digest;
- snapped-grid digest and original used IDs/count;
- retained subset and weighted subset cost when >12 reduction occurs;
- final used IDs/count;
- final logical-grid digest;
- exact source provenance.

SP05-C003 exists because C002 does not yet explicitly enforce:

`report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256`

and its focused tests do not yet provide every required adversarial/equivalence proof.

## ASSET_ART Contract

- Separate from LevelData/difficulty legality.
- **24x24 px is the first owner-approved ASSET_ART baseline target.**
- 24x24 is not the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART.
- ASSET_ART may retain separate normalization/palette policies when explicitly specified.
- ASSET_ART policy must never override the owner-locked LEVEL_ART workflow.

## Magnific Live Evidence

Accepted source facts remain:

- provider/model direction: Magnific `recraft-v4-1` wizard smoke;
- owner accepted semantic/readability direction;
- provider creation metadata previously reported 2048x2048;
- owner-downloaded exact file used for local qualification is **1024x1024**, **265479 bytes**;
- source SHA-256: `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`;
- source profile: 8-bit RGB, non-interlaced;
- chunk sequence: `IHDR -> caBX -> fdEC -> IDAT -> IEND`;
- metadata-vs-downloaded-file dimension mismatch remains visible and unresolved, not silently reconciled;
- Q03 `AREA_AVERAGE_V1` result was technically reproducible but **OWNER REJECTED for LEVEL_ART visual behavior**;
- CELL_MAJORITY diagnostic was **OWNER ACCEPTED** as the LEVEL_ART logical-cell reduction direction.

No live provider call is needed or authorized for SP05-C003.

## Milestone Overview

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [x] PAG-SP03 — Semantic Normalization Pipeline technical foundation
- [~] PAG-SP04 — Semantic Provider / Model / Workflow Qualification — **Magnific live path technically qualified through Q04 owner disposition; PixelLab/comparative qualification deferred until useful/authorized**
- [~] PAG-SP05 — LEVEL_ART Semantic Integration — **C001 FAIL → C002 core convergence retained → C003 trust/evidence closure READY**
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

State: **FAIL / REMEDIATED BY C002 DIRECTION**

Strict audit:

`.hiveai/audits/PAG-SP05-C001_LEVEL_ART_HARD_CELL_COMPILER_PALETTE_SNAP_AND_DIFFICULTY_BUDGET_STRICT_AUDIT.md`

Retained technical evidence:

- [x] CELL_MAJORITY_V1 deterministic hard-cell reduction;
- [x] PALETTE_SNAP_V1 to canonical C01..C16;
- [x] weighted exact subset optimizer foundation;
- [x] raw-artifact/provenance foundation;
- [x] ASSET_ART separation.

Rejected/superseded C001 behavior:

- [x] class-specific dimension/color legality identified as stale for current production;
- [x] public trusted-construction gap identified.

C001 is historical implementation evidence, not accepted final SP05 closure.

---

# PAG-SP05-C002 — Difficulty V1 Contract Convergence & Trusted Compilation Evidence Closure

State: **FAIL / PARTIAL TECHNICAL ACCEPTANCE; C003 REQUIRED**

Implementation commit:

`f9c0aaf9043f2f90c1a422e075aebcad9807ecbe`

Builder-log publication commit:

`1a2c29bec920abdf7f90cc914b18ba1ac18ca166`

Builder log:

`.hiveai/codex-logs/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_CODEX_LOG.md`

Strict audit:

`.hiveai/audits/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_STRICT_AUDIT.md`

Revalidation checkpoint — 2026-09-14:

- [x] builder log re-read after publication;
- [x] current `level_art.py` trust boundary re-inspected;
- [x] C002 builder-reported focused/full regression results retained as builder evidence;
- [x] independent audit verdict remains **FAIL**;
- [x] missing explicit `report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256` binding reconfirmed in current source;
- [x] C003 remains the only authorized active implementation cycle.

Accepted/retained C002 technical work:

- [x] explicit current production 20..59 dimension contract;
- [x] rectangle legality independent of lane/class;
- [x] explicit current global 3..12 used-color envelope;
- [x] 3..12 preserved without class-specific recoloring;
- [x] <3 fail closed;
- [x] >12 exact weighted reduction to 12 retained;
- [x] removed colors map to nearest retained colors;
- [x] no new C-ID introduced by envelope reduction;
- [x] current `PRODUCTION_COLOR_ENVELOPE_V1` policy identity;
- [x] public historical `from_compilation()` changed to canonical recomputation rather than assertion-based sealing;
- [x] direct/replace report/artifact construction protections materially improved;
- [x] no provider execution/credits;
- [x] no M08/solver/SP06/main-game product expansion.

Open C002 audit defects:

- [ ] **MAJOR:** trusted report raw SHA must be explicitly bound to artifact/source raw SHA;
- [ ] lane-invariant majority/snapped/final digest equality must be explicitly tested;
- [ ] 14- and 15-color >12 envelope cases must be explicitly tested;
- [ ] adversarial report-field tamper probes must cover raw SHA, majority digest, snapped evidence, retained subset/cost and final evidence.

---

# PAG-SP05-C003 — Trusted Report Binding & Acceptance Evidence Closure

State: **READY_FOR_IMPLEMENTATION**

Prompt:

`.hiveai/prompts/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_PROMPT.md`

Required closure:

- [ ] enforce `report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256`;
- [ ] wrong report raw SHA fails trusted validation;
- [ ] forged majority digest fails trusted validation;
- [ ] forged snapped digest / original-used evidence fails trusted validation;
- [ ] forged retained subset / weighted objective fails trusted validation;
- [ ] forged final used/grid evidence fails trusted validation;
- [ ] public `SemanticLevelArtArtifact.from_compilation()` remains non-minting and recomputes canonically;
- [ ] EASY vs VERY_HARD same raw+target yields identical majority digest;
- [ ] same case yields identical snapped-grid digest;
- [ ] same case yields identical final logical cells/grid digest;
- [ ] 13 used colors reduce deterministically to exactly 12;
- [ ] 14 used colors reduce deterministically to exactly 12;
- [ ] 15 used colors reduce deterministically to exactly 12;
- [ ] 16 used colors reduce deterministically to exactly 12;
- [ ] no reduction introduces a new C-ID;
- [ ] CELL_MAJORITY_V1 unchanged;
- [ ] PALETTE_SNAP_V1 unchanged;
- [ ] production 20..59 dimensions unchanged;
- [ ] production 3..12 used-color envelope unchanged;
- [ ] legacy compatibility tests remain green;
- [ ] ASSET_ART behavior remains green;
- [ ] strict PNG behavior remains green;
- [ ] zero provider calls / zero credits;
- [ ] no M08/LevelData/solver/SP06/Studio/publishing/M11 expansion;
- [ ] no main-game writes;
- [ ] builder does not edit root `TASKS.md`;
- [ ] focused and full regressions green;
- [ ] ChatGPT strict audit required before SP05 closure.

---

## Current Stop / Action Rule

**Execute only PAG-SP05-C003.**

Do not reopen the Difficulty V1 architecture. Do not alter CELL_MAJORITY or PALETTE_SNAP. Do not call Magnific or PixelLab. Do not spend credits. Do not begin M08/LevelData integration, solver integration, SP06, Studio UI, publishing, weekly batches or M11.

After Codex pushes C003, stop for ChatGPT strict audit.
