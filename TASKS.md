# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, review evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP04 — Semantic Provider / Model / Workflow Qualification**
- Current Phase: **LIVE QUALIFICATION COMPATIBILITY REMEDIATION**
- Current Task: **PAG-SP04-C006 — PNG IDAT Contiguity & Structural Fail-Closed Closure**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX BUILDER**
- Closing Offline Foundation Cycle: `PAG-SP04-C004` → **PASS / CLOSED**
- SP04-C005: **FAIL / BOUNDED REMEDIATION REQUIRED**
- C005 Strict Audit: `.hiveai/audits/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_STRICT_AUDIT.md`
- C006 Prompt: `.hiveai/prompts/PAG-SP04-C006_PNG_IDAT_CONTIGUITY_AND_STRUCTURAL_FAIL_CLOSED_CLOSURE_PROMPT.md`
- Previous Milestone: `PAG-SP03 — Semantic Normalization Pipeline` → **PASS / CLOSED FOR CURRENT TECHNICAL FOUNDATION**
- Live Evidence: `review/sp04/SP04_Q01_Q02_MAGNIFIC_LIVE_RAW_COMPATIBILITY_2026-09-14.md`
- Owner Decision: **Magnific wizard visual direction accepted; 24x24 px accepted as first ASSET_ART baseline target**
- C005 Positive Closure Retained: **real live-shaped `IHDR -> caBX -> fdEC -> IDAT -> IEND` is now compatible without rewriting raw bytes; critical/type/CRC/bounded-decode protections remain.**
- C005 Residual: **parser also accepts structurally invalid non-consecutive IDAT runs when an ancillary chunk is inserted between split IDAT chunks.**
- Next Task/Action: **Implement C006 only: enforce one contiguous IDAT run while preserving all accepted C005 live compatibility.**
- Credit Policy: **Do not call Magnific or PixelLab and spend zero provider credits during C006.**
- Blockers/Waits: **official SP04-Q02 acceptance, Q03/Q04, SP05 and M11 remain blocked** until C006 passes. PixelLab live qualification remains pending later owner authorization.
- Approved Semantic Providers: **MAGNIFIC**, **PIXELLAB**
- Provider Architecture: **provider-neutral; explicit provider/model/engine selection; no silent fallback**
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Owner-Locked Contracts

### LEVEL_ART

Unchanged:

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
- final LEVEL_ART semantic normalization remains blocked until SP05 integration.

### ASSET_ART

- Separate from LevelData/difficulty legality.
- **24x24 px is the first owner-approved baseline target.**
- 24x24 is not the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART.
- Current normalization baseline palette policy: `PRESERVE_SOURCE_RGBA`.
- Current accepted resize baseline remains `AREA_AVERAGE_V1` until owner review proves a policy change is needed.

## Provider Decisions

### MAGNIFIC

- Approved semantic provider while owner credits are available.
- External owner-authorized orchestration only.
- Live `recraft-v4-1` wizard smoke generated successfully.
- Owner accepted visual direction and exact 24x24 provider-produced derivative.
- Provider creation metadata reported 2048x2048, while owner-downloaded PNG examined locally is 1024x1024. This mismatch remains visible and unresolved.
- Actual supplied PNG: **1024x1024**, **265479 bytes**, SHA-256 `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`.
- Actual supplied PNG profile: 8-bit RGB, non-interlaced, valid CRCs, chunk sequence `IHDR -> caBX -> fdEC -> IDAT -> IEND`.
- C005 now accepts this live-shaped ancillary profile without stripping/re-encoding raw bytes.
- Official Q02 remains unaccepted until C006 closes generic IDAT structural strictness.
- Diagnostic-only local 1024→24 `AREA_AVERAGE_V1` result remains outside accepted pipeline evidence until C006 PASS and official Q03 execution.

### PIXELLAB

- Official Developer API / Python SDK provider remains approved.
- Direct network execution is opt-in only.
- `PIXELLAB_SECRET` remains runtime-only and must never enter Git/logs/manifests.
- PixelLab exact-size 24x24 remains strategically important for later provider comparison.

---

# Milestone Overview

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [x] PAG-SP03 — Semantic Normalization Pipeline technical foundation
- [~] PAG-SP04 — Semantic Provider / Model / Workflow Qualification — **offline foundation PASS; live compatibility remediation active**
- [ ] PAG-SP05 — LEVEL_ART Semantic Integration
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

# PAG-SP04 — Cycle History

- C001 — FAIL / REMEDIATED
- C002 — FAIL / REMEDIATED
- C003 — FAIL / REMEDIATED IN C004
- C004 — **PASS / CLOSED**
- C005 — **FAIL / REMEDIATION IN C006**

## C005 — Safe Ancillary PNG Compatibility for Live Magnific Raw Import

State: **FAIL / POSITIVE CLOSURE RETAINED / C006 REQUIRED**

Strict audit:
`.hiveai/audits/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_STRICT_AUDIT.md`

Accepted C005 closure retained:

- [x] generic valid ancillary chunks are no longer blanket-rejected;
- [x] live-shaped `caBX` + `fdEC` compatibility works;
- [x] raw bytes/SHA remain immutable and byte-sensitive;
- [x] CRC validation remains mandatory;
- [x] malformed chunk type / invalid reserved bit fail closed;
- [x] unsupported critical chunks fail closed;
- [x] bounded zlib/raster protections remain unchanged;
- [x] synthetic baseline/ancillary inputs normalize to identical RGBA while source provenance remains distinct;
- [x] `AREA_AVERAGE_V1`, crop/pad, palette and provider policy were not changed;
- [x] zero provider credits spent.

Open C005 finding:

- [ ] **MAJOR F-PAG-SP04-C005-001:** C005 permits `IDAT(part1) -> ancillary -> IDAT(part2)` because the decoder later concatenates all IDAT payloads. IDAT must remain one contiguous run.

Process debt:

- [~] MINOR: builder read `.hiveai/CYCLE_INDEX.md` despite current-authority restriction.
- [~] MINOR: logged final equality checkpoint predates later log-only terminal commits.

## C006 — PNG IDAT Contiguity & Structural Fail-Closed Closure

State: **READY_FOR_IMPLEMENTATION**

Prompt:
`.hiveai/prompts/PAG-SP04-C006_PNG_IDAT_CONTIGUITY_AND_STRUCTURAL_FAIL_CLOSED_CLOSURE_PROMPT.md`

Required closure:

- [ ] one IDAT accepted;
- [ ] multiple consecutive IDAT chunks accepted;
- [ ] no ancillary/other chunk may split the IDAT run;
- [ ] live `IHDR -> caBX -> fdEC -> IDAT -> IEND` remains accepted;
- [ ] valid ancillary before/after the complete IDAT run remains supported;
- [ ] all C005 CRC/type/reserved-bit/critical/decode bounds remain intact;
- [ ] raw identity/provenance unchanged;
- [ ] normalization policy unchanged;
- [ ] no provider call / zero credits;
- [ ] true terminal publication evidence recorded;
- [ ] ChatGPT strict audit required before closure.

---

# PAG-SP04 — Live Qualification Gates

- [~] **SP04-Q01** Owner-supplied Magnific artifact captured locally: actual 1024x1024 PNG, 265479 bytes, SHA-256 `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`. **PARTIAL PASS:** local byte identity is proven; exact equivalence with provider-internal metadata-reported 2048x2048 original remains unresolved.
- [~] **SP04-Q02** Live-shaped compatibility is functionally demonstrated by C005, but **NOT YET ACCEPTED** because C005 introduced a generic IDAT-contiguity structural regression. C006 must pass first.
- [ ] **SP04-Q03** BLOCKED pending C006 PASS. Then run the exact accepted local raw candidate through the actual SP03 pipeline to 24x24 and record full provenance.
- [ ] **SP04-Q04** BLOCKED pending Q03. Present the official local normalized 24x24 result metadata-blind for owner review and compare with the accepted provider-produced 24x24 derivative.
- [ ] **SP04-Q05** Run PixelLab exact-size 24x24 qualification only when owner authorizes live API use and `PIXELLAB_SECRET` is available.
- [ ] **SP04-Q06** Compare eligible PIXFLUX / BITFORGE paths against Magnific using the same benchmark/review protocol.
- [ ] **SP04-Q07** Select any default provider/model/workflow only from technical evidence plus owner visual acceptance.

No default production provider/model/workflow is selected yet.

## Diagnostic-only Q03 preview

Existing diagnostic-only local 1024→24 `AREA_AVERAGE_V1` observation remains:

- target: 24x24
- normalized RGBA byte SHA-256: `733503bd8e9a28443010d96e3c3b93668aaa3497526c15d673e1cc9c513a4c5e`
- diagnostic PNG SHA-256: `b7bf0475ed2064a9af1e60c8121f015ae2feb1132403462e8b25a500e281928c`
- distinct RGBA colors: **124**
- observation: area averaging creates blended edge tones around hard pixel-art boundaries.

This remains diagnostic only and does not authorize a resize-policy change.

---

## Current Stop / Action Rule

**One bounded Codex remediation cycle is authorized: PAG-SP04-C006 only.**

Do not call Magnific or PixelLab. Do not spend credits. Do not begin SP05, SP06, Studio UI, weekly batches or M11. After C006 is pushed, stop for ChatGPT strict audit. If C006 passes, return immediately to official SP04-Q02/Q03/Q04 using the owner-supplied 1024x1024 artifact.