# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, `review/` evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP04 — Semantic Provider / Model / Workflow Qualification**
- Current Phase: **LIVE QUALIFICATION OWNER REVIEW**
- Current Task: **SP04-Q04 — Owner review of official local 24x24 Magnific normalization**
- Current Task Status: **AWAITING_OWNER_VISUAL_DISPOSITION**
- Required Actor: **OWNER / CHATGPT**
- Closing Offline Foundation Cycle: `PAG-SP04-C004` → **PASS / CLOSED**
- Compatibility Remediation: `PAG-SP04-C005` → FAIL / remediated by `PAG-SP04-C006`
- Closing Compatibility Cycle: `PAG-SP04-C006` → **PASS / CLOSED**
- C006 Strict Audit: `.hiveai/audits/PAG-SP04-C006_PNG_IDAT_CONTIGUITY_AND_STRUCTURAL_FAIL_CLOSED_CLOSURE_STRICT_AUDIT.md`
- Official Q02/Q03 Evidence: `review/sp04/SP04_Q02_Q03_MAGNIFIC_OFFICIAL_LOCAL_NORMALIZATION_2026-09-14.md`
- Owner Decision Already Locked: **Magnific semantic wizard direction accepted; 24x24 px accepted as first ASSET_ART baseline target.**
- Next Action: **Owner reviews the official local `AREA_AVERAGE_V1` 24x24 wizard. Do not change resize policy until owner disposition is recorded.**
- Credit Policy: **No additional provider spend is required for Q04. Any later paid Magnific/PixelLab generation requires owner authorization.**
- Blockers/Waits: **SP05 and M11 remain blocked** until SP04 live qualification disposition is accepted. PixelLab live qualification remains pending later owner-authorized API conditions.
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
- final LEVEL_ART semantic normalization remains blocked until SP05 integration.

### ASSET_ART

- Separate from LevelData/difficulty legality.
- **24x24 px is the first owner-approved baseline target.**
- 24x24 is not the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART.
- Current baseline palette policy: `PRESERVE_SOURCE_RGBA`.
- Current accepted resize baseline remains `AREA_AVERAGE_V1` **until Q04 owner review decides whether its blended-edge behavior is visually acceptable.**

## Magnific Live Evidence

Accepted source facts:

- provider/model direction: Magnific `recraft-v4-1` wizard smoke;
- owner accepted semantic/readability direction;
- provider creation metadata previously reported 2048x2048;
- owner-downloaded exact file used for local qualification is **1024x1024**, **265479 bytes**;
- source SHA-256: `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`;
- source profile: 8-bit RGB, non-interlaced;
- chunk sequence: `IHDR -> caBX -> fdEC -> IDAT -> IEND`;
- metadata-vs-downloaded-file dimension mismatch remains visible and unresolved, not silently reconciled.

## Milestone Overview

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [x] PAG-SP03 — Semantic Normalization Pipeline technical foundation
- [~] PAG-SP04 — Semantic Provider / Model / Workflow Qualification — **Q04 owner review active**
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
- C005 — FAIL / positive ancillary compatibility retained / IDAT residual found
- C006 — **PASS / CLOSED**

## C006 Accepted Closure

- [x] one IDAT accepted;
- [x] multiple consecutive IDAT chunks accepted;
- [x] any non-IDAT chunk splitting an IDAT run rejected fail-closed;
- [x] live `IHDR -> caBX -> fdEC -> IDAT -> IEND` remains accepted;
- [x] valid ancillary before/after complete IDAT run supported;
- [x] C005 CRC/type/reserved-bit/critical/decode bounds remain intact;
- [x] raw identity/provenance unchanged;
- [x] normalization policy unchanged;
- [x] zero provider calls / zero credits;
- [x] ChatGPT strict audit PASS.

No C007 decoder remediation is authorized.

---

# PAG-SP04 — Live Qualification Gates

- [~] **SP04-Q01** Captured owner-supplied artifact: 1024x1024, 265479 bytes, exact SHA proven. **PARTIAL PASS** only because equivalence with provider metadata-reported 2048x2048 original remains unresolved.
- [x] **SP04-Q02 — PASS.** Post-C006 strict decoder accepts the exact owner-supplied Magnific PNG without rewriting raw bytes; split-IDAT structural regression is closed.
- [x] **SP04-Q03 — PASS.** Exact local artifact normalized through accepted deterministic policy to **24x24**.
  - output class: `ASSET_ART`
  - resize: `AREA_AVERAGE_V1`
  - alpha: `PRESERVE_ALPHA`
  - crop/pad: `FIT_CENTER_LETTERBOX_V1`
  - palette: `PRESERVE_SOURCE_RGBA`
  - normalized RGBA SHA-256: `733503bd8e9a28443010d96e3c3b93668aaa3497526c15d673e1cc9c513a4c5e`
  - normalized artifact digest: `b69312f889f41c7d78495c7e4433f5a186c0e3d30e5fe764b6034289c9430f7f`
  - distinct normalized RGBA colors: **124**
- [~] **SP04-Q04 — OWNER REVIEW ACTIVE.** Determine whether the official local 24x24 `AREA_AVERAGE_V1` result is crisp/readable enough or whether blended edge tones justify a bounded pixel-art-specific resize-policy experiment.
- [ ] **SP04-Q05** PixelLab exact-size 24x24 qualification only when owner authorizes live API use and `PIXELLAB_SECRET` is available.
- [ ] **SP04-Q06** Compare eligible PIXFLUX / BITFORGE paths against Magnific using the same benchmark/review protocol.
- [ ] **SP04-Q07** Select any default provider/model/workflow only from technical evidence plus owner visual acceptance.

No default production provider/model/workflow is selected yet.

---

## Current Stop / Action Rule

**Do not start another Codex cycle yet.**

The next action is owner visual review of Q04. If the owner accepts the official local 24x24 output, record acceptance and continue SP04 qualification planning. If the owner rejects it specifically because `AREA_AVERAGE_V1` introduces blended edge tones, open one evidence-driven bounded resize-policy experiment rather than changing provider/palette/LEVEL_ART contracts broadly.
