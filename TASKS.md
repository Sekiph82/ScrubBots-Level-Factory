# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, review evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP04 — Semantic Provider / Model / Workflow Qualification**
- Current Sprint: **PAG-SP04-C002**
- Current Task: **Qualification Provenance, Capability & Blind-Review Binding Remediation**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX**
- Previous Cycle: `PAG-SP04-C001` → **FAIL / 4 MAJOR + 2 MINOR**
- Previous Strict Audit: `.hiveai/audits/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_STRICT_AUDIT.md`
- Current Prompt: `.hiveai/prompts/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_PROMPT.md`
- Previous Milestone: `PAG-SP03 — Semantic Normalization Pipeline` → **PASS / CLOSED FOR CURRENT TECHNICAL FOUNDATION**
- Live Smoke Evidence: `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`
- Owner Decision: **Magnific wizard visual direction accepted; 24x24 px accepted as first ASSET_ART baseline target**
- Next Task/Action: Execute SP04-C002 only, close C001 contract-integrity findings, publish builder log/tests, commit/push `main`, then stop for independent ChatGPT audit.
- Blockers/Waits: **SP04 live provider generation, SP05 and M11 remain blocked** until C002 receives independent PASS. No provider credits are authorized in C002.
- Approved Semantic Providers: **MAGNIFIC**, **PIXELLAB**
- Provider Architecture: **provider-neutral; explicit provider/model/engine selection; no silent fallback**
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Current Product Goal

```text
TEXT / REFERENCE / STYLE
          ↓
 EXPLICIT SEMANTIC PROVIDER
   MAGNIFIC | PIXELLAB
          ↓
 recognizable raw semantic artwork
          ↓
 SP03 deterministic normalization
          ↓
 SP04 evidence-based qualification
          ↓
 existing MASK / RULES / WFC / HYBRID
 control / puzzle / style infrastructure
          ↓
 structural QA + semantic recognizability gate
          ↓
 owner review
          ↓
 M08 export / M09 batch-reproduce / Level Factory handoff
```

The previous M10 100-image owner pack remains **REJECTED 100/100** and is permanent negative semantic regression evidence.

---

# Owner-Locked Contracts

## LEVEL_ART

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
- SP03 currently rejects final LEVEL_ART normalization requests until canonical palette+difficulty normalization is implemented in later LEVEL_ART integration scope.

## ASSET_ART

- Separate from LevelData/difficulty legality.
- **24x24 px is the first owner-approved baseline target.**
- 24x24 is not the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART.
- Current normalization baseline palette policy: `PRESERVE_SOURCE_RGBA`.

---

# Provider Decisions

## MAGNIFIC

- Approved semantic provider while owner credits are available.
- External owner-authorized orchestration only; Factory must not scrape/drive private endpoints.
- Raw provider dimensions and logical target dimensions are separate provenance concepts.
- Live `recraft-v4-1` wizard smoke generated successfully; owner accepted the visual direction and exact 24x24 derivative.
- The exact private raw Magnific PNG has **not yet** been proven through the local strict decoder/import path.
- Local `AREA_AVERAGE_V1` 2048→24 output is technically deterministic but is **not yet owner-qualified visually** against the accepted provider-produced derivative.

## PIXELLAB

- Official Developer API / Python SDK provider remains approved.
- Direct network execution is opt-in only.
- `PIXELLAB_SECRET` remains runtime-only and must never enter Git/logs/manifests.
- PixelLab exact-size generation remains strategically important for comparing native 24x24 output against Magnific + local normalization.
- PixelLab live smoke remains pending authorized secret availability and does not reopen SP02.

---

# Milestone Overview

## Historical procedural foundation

- [x] **PAG-M00 — Repository Bootstrap & Governance**
- [x] **PAG-M01 — Canonical SCRUBBOTS Contracts**
- [x] **PAG-M02 — Deterministic Generation Core**
- [x] **PAG-M03 — Mask / Sprite Generator**
- [x] **PAG-M04 — Procedural Shape / Rule Generator technical closure**
- [x] **PAG-M05 — Wave Function Collapse Generator**
- [x] **PAG-M06 — Hybrid Generator Router**
- [x] **PAG-M07 — Artwork Quality & Diversity Filters**
- [x] **PAG-M08 — Output / Export Contract**
- [x] **PAG-M09 — CLI & Local Batch Generation**
- [x] **PAG-M10 — Technical validation/performance foundation**
- [!] **PAG-M10 visual V1 acceptance — OWNER REJECTED 100/100**
- [!] **PAG-M11 — Godot/Main-Level-Factory Handoff Gate** blocked pending semantic replacement acceptance

## Semantic Pixel Studio roadmap

- [x] **PAG-SP00 — Owner Rejection & Semantic Pivot Record**
- [x] **PAG-SP01 — Semantic Contracts & Provider Boundary**
- [x] **PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion**
- [x] **PAG-SP03 — Semantic Normalization Pipeline technical foundation**
- [~] **PAG-SP04 — Semantic Provider / Model / Workflow Qualification** — C002 remediation active
- [ ] **PAG-SP05 — LEVEL_ART Semantic Integration**
- [ ] **PAG-SP06 — Semantic Quality / Recognizability Gate**
- [ ] **PAG-SP07 — Reference / Style Generation**
- [ ] **PAG-SP08 — Edit / Inpaint**
- [ ] **PAG-SP09 — Pixel Studio Create / Gallery UI**
- [ ] **PAG-SP10 — Automated Weekly Semantic Batch**
- [ ] **PAG-SP11 — ASSET_ART Production**
- [ ] **PAG-SP12 — Direction / Rotation Variants**
- [ ] **PAG-SP13 — Animation**
- [ ] **PAG-SP14 — ScrubBots Level Factory Bridge**

---

# PAG-SP01 — Semantic Contracts & Provider Boundary

Final state: **PASS / CLOSED**

Closing audit:
`.hiveai/audits/PAG-SP01-C003_NON_SUCCESS_PROVENANCE_ECHO_AND_MISMATCH_TEST_SENSITIVITY_CLOSURE_STRICT_AUDIT.md`

Accepted:

- [x] LEVEL_ART / ASSET_ART separation.
- [x] Immutable/versioned semantic request and image descriptors.
- [x] Provider-neutral boundary and typed raw candidates.
- [x] Exact role/provenance binding.
- [x] Raw semantic candidate cannot masquerade as M08 artwork.

---

# PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion

Final state for current scope: **PASS / CLOSED**

Closing audit:
`.hiveai/audits/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_STRICT_AUDIT.md`

Accepted:

- [x] Explicit MAGNIFIC / PIXELLAB provider selection.
- [x] Magnific pinned model capability snapshots and raw-raster/provenance bridge.
- [x] PixelLab official SDK boundary with exact-size/seed mapping.
- [x] Exact cross-provenance binding.
- [x] Magnific live generation PASS.
- [x] Exact 24x24 provider derivative produced.
- [x] Owner visual acceptance PASS.
- [x] Owner 24x24 ASSET_ART baseline acceptance PASS.
- [~] Real local Factory import of the exact private Magnific raw bytes remains a qualification input, not an SP02 code blocker.

---

# PAG-SP03 — Semantic Normalization Pipeline

Final state for current technical foundation: **PASS / CLOSED**

Closing cycle: `PAG-SP03-C003 — Provenance Seal & Construction Integrity Closure`

Closing audit:
`.hiveai/audits/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_STRICT_AUDIT.md`

Accepted:

- [x] raw provider bytes/hash immutable before/after normalization;
- [x] bounded strict decoder/decompression budget;
- [x] exact-size no-hidden-interpolation path;
- [x] deterministic large-raster downsample/report;
- [x] deep report immutability;
- [x] sealed exact raw/request/provider provenance against ordinary constructor/replace attacks;
- [x] ASSET_ART independent from LEVEL_ART palette/color-band rules;
- [x] LEVEL_ART final normalization fail-closed until later integration;
- [x] normalized ASSET_ART cannot masquerade as M08 LEVEL_ART.

Carried qualification inputs:

- [~] exact live private Magnific raw PNG local strict-decoder/import compatibility UNVERIFIED;
- [~] owner visual acceptance of local 2048→24 normalization UNVERIFIED.

---

# PAG-SP04 — Semantic Provider / Model / Workflow Qualification

State: **ACTIVE / C002_REMEDIATION**

## C001 — Semantic Qualification Harness, Benchmark Corpus & Cost-Safe Provider Matrix

State: **FAIL / C002 REQUIRED**

Strict audit:
`.hiveai/audits/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_STRICT_AUDIT.md`

Retained C001 work:

- [x] versioned 15-subject recognizable benchmark corpus;
- [x] 24x24 ASSET_ART baseline without LEVEL_ART leakage;
- [x] explicit Magnific / PIXFLUX / BITFORGE matrix concept;
- [x] finite bounded offline plan construction;
- [x] cost/usage separation from deterministic attempt identity;
- [x] metadata-blind visible-review intent;
- [x] positive Magnific wizard and negative M10 evidence references;
- [x] no provider call / no credit spend;
- [x] builder-reported 11 focused, 92 SP01-SP04 focused, 473 full tests green.

C001 defects:

- [!] `F-PAG-SP04-C001-001` **MAJOR** — plan builder ignores case reference/style capability requirements.
- [!] `F-PAG-SP04-C001-002` **MAJOR** — PASS raw/normalization evidence can be self-asserted with arbitrary digests instead of checked SP03 typed artifacts.
- [!] `F-PAG-SP04-C001-003` **MAJOR** — lifecycle and exact plan/provider/raw/normalized cross-provenance binding are incomplete; terminal owner states can bypass raw PASS.
- [!] `F-PAG-SP04-C001-004` **MAJOR** — blind-review visible↔hidden stable-ID binding is not invariant-checked and review identity is derived before its own link mutates attempt identity.
- [!] `F-PAG-SP04-C001-005` **MINOR** — terminal owner-accepted/rejected summaries can report `NO_READY_CANDIDATES`.
- [!] `F-PAG-SP04-C001-006` **MINOR process** — C001 builder log was not literally created before all temporary C001 edits.

## C002 — Qualification Provenance, Capability & Blind-Review Binding Remediation

State: **READY_FOR_IMPLEMENTATION**

Authoritative prompt:
`.hiveai/prompts/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_PROMPT.md`

Required closure:

- [ ] SP04-C002-001 Fail closed when a selected benchmark case requires REFERENCE/STYLE unsupported by its provider matrix cell.
- [ ] SP04-C002-002 Prove positive BITFORGE STYLE-plan semantics and negative PIXFLUX STYLE/reference sensitivity.
- [ ] SP04-C002-003 Validate every plan entry against exact case/provider matrix/attempt-index identity, not count/position only.
- [ ] SP04-C002-004 Build verified PASS qualification evidence from accepted typed/sealed SP03 raw + normalized artifacts, not free-form digests.
- [ ] SP04-C002-005 Bind raw-artifact digest + raw SHA + provider/version/workflow/model/request/result identity exactly.
- [ ] SP04-C002-006 Bind normalization source raw-artifact digest + request/output/report identity exactly to the same verified raw artifact.
- [ ] SP04-C002-007 Bind advanced attempts to exact qualification plan entry/case/provider matrix identity.
- [ ] SP04-C002-008 Require raw-import PASS for RAW_IMPORT_VERIFIED and every later lifecycle state.
- [ ] SP04-C002-009 Require checked normalization PASS for NORMALIZED and every later lifecycle state.
- [ ] SP04-C002-010 Make review visible↔hidden mapping fail closed by stable IDs under direct construction/replacement and independent of tuple position.
- [ ] SP04-C002-011 Derive review IDs from immutable pre-review identity unaffected by installing the review link or changing cost/owner metadata.
- [ ] SP04-C002-012 Correct pending/accepted/rejected qualification summary semantics.
- [ ] SP04-C002-013 Add adversarial sensitivity tests for all C001 findings.
- [ ] SP04-C002-014 Preserve C001 corpus/provider/cost/evidence-reference foundation.
- [ ] SP04-C002-015 SP01-SP04 focused + full regression + compile/import/CLI/offline/security checks green.
- [ ] SP04-C002-016 No provider execution, credits, live qualification, SP05/SP06/UI/M11.
- [ ] SP04-C002-017 Create builder log before any C002 implementation edit and keep final publication chronology truthful.

## Qualification gates blocked until C002 independent PASS

- [ ] SP04-Q01 Capture exact live Magnific raw bytes locally and compute immutable SHA-256.
- [ ] SP04-Q02 Prove exact live Magnific raw media/chunk profile is accepted by local SP03 decoder/import boundary; if not, open evidence-driven compatibility remediation.
- [ ] SP04-Q03 Normalize the real Magnific raw candidate locally to 24x24 and present it metadata-blind for owner review.
- [ ] SP04-Q04 Compare local normalized Magnific result against the already accepted provider-produced 24x24 derivative.
- [ ] SP04-Q05 Run PixelLab exact-size 24x24 qualification only when authorized API secret/credit conditions are available.
- [ ] SP04-Q06 Compare PixFlux / eligible BitForge paths against Magnific using the same benchmark/review protocol.
- [ ] SP04-Q07 Select a default provider/model/workflow only from technical evidence + owner visual acceptance.

No default production provider/model/workflow is selected yet.

---

# Later Milestones

- SP05: LEVEL_ART semantic integration
- SP06: semantic recognizability gate
- SP07: reference/style generation
- SP08: edit/inpaint
- SP09: Pixel Studio UI
- SP10: automated weekly semantic batch
- SP11: ASSET_ART production
- SP12: direction/rotation variants
- SP13: animation
- SP14: main ScrubBots Level Factory bridge

M11 remains blocked until owner-accepted semantic replacement artwork is technically qualified, normalized and accepted through downstream gates.

---

## Current Stop Rule

Execute **PAG-SP04-C002 only**.

Do not call Magnific/PixelLab or spend credits. Do not begin live SP04 generation, SP05, SP06, Studio UI or M11. Codex must not edit `TASKS.md`, must create the matching C002 builder log before any implementation edit, commit/push `main`, verify final local HEAD == origin/main divergence `0 0`, then stop for independent ChatGPT audit.
