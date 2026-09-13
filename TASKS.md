# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, review evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP04 — Semantic Provider / Model / Workflow Qualification**
- Current Phase: **LIVE QUALIFICATION COMPATIBILITY REMEDIATION**
- Current Task: **PAG-SP04-C005 — Safe Ancillary PNG Compatibility for Live Magnific Raw Import**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX BUILDER**
- Closing Offline Foundation Cycle: `PAG-SP04-C004` → **PASS / CLOSED**
- Closing C004 Audit: `.hiveai/audits/PAG-SP04-C004_REVIEW_ENTRY_PROOF_AND_PROVIDER_CAPTURE_EVIDENCE_CLOSURE_STRICT_AUDIT.md`
- Previous Milestone: `PAG-SP03 — Semantic Normalization Pipeline` → **PASS / CLOSED FOR CURRENT TECHNICAL FOUNDATION**
- Existing Live Smoke Evidence: `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`
- New Live Compatibility Evidence: `review/sp04/SP04_Q01_Q02_MAGNIFIC_LIVE_RAW_COMPATIBILITY_2026-09-14.md`
- C005 Prompt: `.hiveai/prompts/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_PROMPT.md`
- Owner Decision: **Magnific wizard visual direction accepted; 24x24 px accepted as first ASSET_ART baseline target**
- Live Finding: **owner-supplied Magnific PNG is 1024x1024 although provider metadata reported 2048x2048; actual file contains valid ancillary/private `caBX` and `fdEC` PNG chunks; current SP03 decoder blanket-rejects them.**
- Next Task/Action: **Implement and strictly audit C005. Preserve raw bytes/hash, accept structurally valid ancillary chunks for decoding, continue rejecting unsupported critical chunks fail-closed.**
- Credit Policy: **Do not spend additional provider credits during C005. No Magnific or PixelLab call is authorized in this remediation.**
- Blockers/Waits: **SP04-Q03/Q04, SP05 and M11 remain blocked** until C005 passes and the real local normalization path is rerun. PixelLab live qualification remains pending later authorization.
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
- Owner accepted the visual direction and exact 24x24 provider-produced derivative.
- Provider creation metadata reported 2048x2048, but the owner-supplied downloaded PNG examined locally is 1024x1024. This mismatch is retained as evidence and must not be silently reconciled.
- Actual supplied PNG SHA-256: `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`.
- Actual supplied PNG profile: 8-bit RGB, non-interlaced, valid CRCs, chunk sequence `IHDR -> caBX -> fdEC -> IDAT -> IEND`.
- Current SP03 decoder rejects the valid ancillary/private `caBX` and `fdEC` chunks; C005 is the bounded compatibility remediation.
- Diagnostic-only local 1024→24 `AREA_AVERAGE_V1` result remains outside accepted pipeline evidence until C005 passes.

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
- [~] PAG-SP04 — Semantic Provider / Model / Workflow Qualification — **offline contract foundation PASS; live compatibility remediation active**
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

# PAG-SP04 — Offline Qualification Foundation

- C001 — FAIL / REMEDIATED
- C002 — FAIL / REMEDIATED
- C003 — FAIL / REMEDIATED IN C004
- C004 — **PASS / CLOSED**

C004 accepted closure includes:

- [x] exact request/case/provider binding;
- [x] trusted attempt construction and monotonic lifecycle;
- [x] typed/sealed SP03 raw + normalization evidence;
- [x] exact raw→normalized provenance binding;
- [x] deterministic metadata-blind review identity;
- [x] sealed review-entry evidence for terminal owner disposition;
- [x] typed provider-capture evidence for `RAW_PROVIDER_CAPTURED` and later states;
- [x] exact plan-bound qualification summaries;
- [x] cost/usage outside deterministic identity;
- [x] no silent provider fallback.

Strict audits remain canonical historical evidence in `.hiveai/audits/`.

---

# PAG-SP04-C005 — Safe Ancillary PNG Compatibility for Live Magnific Raw Import

State: **READY_FOR_IMPLEMENTATION**

Trigger evidence:
`review/sp04/SP04_Q01_Q02_MAGNIFIC_LIVE_RAW_COMPATIBILITY_2026-09-14.md`

Prompt:
`.hiveai/prompts/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_PROMPT.md`

Required closure:

- [ ] Preserve exact original raw bytes and raw SHA-256.
- [ ] Accept/ignore structurally valid ancillary PNG chunks for pixel decoding.
- [ ] Keep CRC validation mandatory for all chunks.
- [ ] Reject malformed chunk types and unsupported/unknown critical chunks fail-closed.
- [ ] Preserve bounded zlib output, raw byte limit, raw dimension limit and pixel budget.
- [ ] Add synthetic regression fixture matching `IHDR -> caBX -> fdEC -> IDAT -> IEND` shape without committing the private live artifact.
- [ ] Prove ancillary-bearing and baseline variants decode to identical RGBA pixels while retaining different raw hashes/source provenance.
- [ ] Preserve SP03 provenance seals and SP04 qualification evidence binding.
- [ ] Do not alter `AREA_AVERAGE_V1`, crop/pad, palette, provider selection or benchmark policy.
- [ ] Do not call Magnific or PixelLab; spend zero credits.
- [ ] Builder must not edit this root `TASKS.md`.
- [ ] ChatGPT strict audit required before closure.

---

# PAG-SP04 — Live Qualification Gates

- [~] **SP04-Q01** Owner-supplied Magnific artifact captured locally: actual 1024x1024 PNG, 265479 bytes, SHA-256 `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`. **PARTIAL PASS:** local byte identity is proven; exact equivalence with provider-internal metadata-reported 2048x2048 original remains unresolved.
- [x] **SP04-Q02 discovery executed** and produced **FAIL / REMEDIATION REQUIRED:** current strict decoder rejects valid ancillary/private `caBX` and `fdEC` chunks. C005 is active.
- [ ] **SP04-Q03** BLOCKED pending C005 PASS. Then normalize the exact accepted local raw candidate to **24x24** through the actual SP03 pipeline and record full provenance.
- [ ] **SP04-Q04** BLOCKED pending Q03. Present the official local normalized 24x24 result metadata-blind for owner review and compare with the already accepted provider-produced 24x24 derivative.
- [ ] **SP04-Q05** Run PixelLab exact-size 24x24 qualification only when owner authorizes live API use and `PIXELLAB_SECRET` is available.
- [ ] **SP04-Q06** Compare eligible PIXFLUX / BITFORGE paths against Magnific using the same benchmark/review protocol.
- [ ] **SP04-Q07** Select any default provider/model/workflow only from technical evidence plus owner visual acceptance.

No default production provider/model/workflow is selected yet.

## Diagnostic-only Q03 preview

The owner-supplied 1024x1024 pixel data was passed through the same integer `AREA_AVERAGE_V1` mathematics outside the accepted pipeline solely to inspect likely visual behavior while Q02 is blocked.

- target: 24x24
- normalized RGBA byte SHA-256: `733503bd8e9a28443010d96e3c3b93668aaa3497526c15d673e1cc9c513a4c5e`
- diagnostic PNG SHA-256: `b7bf0475ed2064a9af1e60c8121f015ae2feb1132403462e8b25a500e281928c`
- distinct RGBA colors: **124**
- observation: area averaging creates blended edge tones around hard pixel-art boundaries.

This diagnostic is **not** SP03 acceptance evidence and does not authorize a resize-policy change. Official Q03/Q04 occurs only after C005 strict PASS.

---

## Current Stop / Action Rule

**One bounded Codex remediation cycle is authorized: PAG-SP04-C005 only.**

Do not call Magnific or PixelLab. Do not spend credits. Do not begin SP05, SP06, Studio UI, weekly batches or M11. After C005 is pushed, stop for ChatGPT strict audit. If C005 passes, return immediately to SP04-Q03/Q04 live evidence using the owner-supplied artifact.
