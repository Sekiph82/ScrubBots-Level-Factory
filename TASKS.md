# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, review evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP04 — Semantic Provider / Model / Workflow Qualification**
- Current Sprint: **PAG-SP04-C001**
- Current Task: **Semantic Qualification Harness, Benchmark Corpus & Cost-Safe Provider Matrix**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX**
- Previous Milestone: `PAG-SP03 — Semantic Normalization Pipeline` → **PASS / CLOSED FOR CURRENT TECHNICAL FOUNDATION**
- Closing SP03 Cycle: `PAG-SP03-C003` → **PASS / CLOSED**
- Closing SP03 Audit: `.hiveai/audits/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_STRICT_AUDIT.md`
- Current Prompt: `.hiveai/prompts/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_PROMPT.md`
- Live Smoke Evidence: `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`
- Owner Decision: **Magnific wizard visual accepted; 24x24 px accepted as first ASSET_ART baseline target**
- Next Task/Action: Execute SP04-C001 only, build the offline qualification/evidence harness, publish builder log/tests, commit/push `main`, then stop for independent ChatGPT audit.
- Blockers/Waits: **SP05 and M11 remain blocked**. Live provider generation is not authorized in SP04-C001. Exact private Magnific raw-byte local import/decoder compatibility remains a mandatory SP04 qualification gate before Magnific can be considered end-to-end normalized.
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
- SP03 currently rejects all final LEVEL_ART normalization requests until canonical palette+difficulty normalization is implemented in the later LEVEL_ART integration scope.

### ASSET_ART

- Separate from LevelData/difficulty legality.
- **24x24 px is the first owner-approved baseline target.**
- 24x24 is not the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART.
- Current normalization baseline palette policy: `PRESERVE_SOURCE_RGBA`.

## Provider Decisions

### MAGNIFIC

- Approved semantic provider while owner credits are available.
- External owner-authorized orchestration only; Factory must not scrape/drive private endpoints.
- Raw provider dimensions and logical target dimensions are separate provenance concepts.
- Live `recraft-v4-1` wizard smoke generated successfully; owner accepted the visual direction and exact 24x24 derivative.
- The exact private raw Magnific PNG has **not yet** been proven through the local strict decoder/import path. This is now an SP04 qualification prerequisite, not a reason to reopen accepted SP03 code unless real evidence exposes a compatibility defect.
- Local `AREA_AVERAGE_V1` 2048→24 output is technically deterministic but is **not yet owner-qualified visually** against the accepted provider-produced derivative.

### PIXELLAB

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
- [~] **PAG-SP04 — Semantic Provider / Model / Workflow Qualification** — C001 active
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

Final state: `PASS / CLOSED`

Closing audit: `.hiveai/audits/PAG-SP01-C003_NON_SUCCESS_PROVENANCE_ECHO_AND_MISMATCH_TEST_SENSITIVITY_CLOSURE_STRICT_AUDIT.md`

- [x] LEVEL_ART / ASSET_ART separation.
- [x] Immutable/versioned semantic request and image descriptors.
- [x] Provider-neutral boundary and typed raw candidates.
- [x] Exact role/provenance binding.
- [x] Raw semantic candidate cannot masquerade as M08 artwork.

---

# PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion

Final state for current scope: `PASS / CLOSED`

Closing audit: `.hiveai/audits/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_STRICT_AUDIT.md`

Live smoke evidence: `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`.

- [x] Explicit MAGNIFIC / PIXELLAB provider selection.
- [x] Magnific pinned model capability snapshots and raw-raster/provenance bridge.
- [x] PixelLab official SDK boundary with exact-size/seed mapping.
- [x] Result identity excludes mutable audit/cost/failure prose.
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

Closing audit: `.hiveai/audits/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_STRICT_AUDIT.md`

Cycle history:

- `PAG-SP03-C001` → FAIL; bounded decode/immutability/provenance/LEVEL legality remediation opened.
- `PAG-SP03-C002` → FAIL; bounded decode, deep report immutability and LEVEL request legality closed; one provenance-seal residual remained.
- `PAG-SP03-C003` → **PASS / CLOSED**; resettable/reissuable provenance-seal defect closed.

Technical acceptance:

- [x] SP03-A01 Raw provider bytes/hash immutable before/after normalization.
- [x] SP03-A02 Malformed/compressed input bounded by explicit decode budget.
- [x] SP03-A03 Exact-size source uses no hidden interpolation.
- [x] SP03-A04 Large-raster downsample is deterministic and fully reported.
- [x] SP03-A05 Report deterministic identity is deeply immutable.
- [x] SP03-A06 Normalized provenance is sealed to the exact raw source/request/provider chain against ordinary public dataclass construction/replacement attacks.
- [x] SP03-A07 ASSET_ART does not inherit LEVEL_ART palette/color-band rules.
- [x] SP03-A08 LEVEL_ART cannot bypass current canonical contracts; final LEVEL normalization requests fail closed.
- [x] SP03-A09 No normalized ASSET_ART can masquerade as M08 LEVEL_ART.
- [x] SP03-A10 Independent audit marks C003/SP03 technical foundation PASS.
- [x] SP03-A11 Builder reports 14 SP03 focused, 78 SP01-SP03 focused and 459 full tests green for C003.
- [~] SP03-Q01 Exact live private Magnific raw PNG local strict-decoder/import compatibility is UNVERIFIED and carried into SP04 as a mandatory qualification gate.
- [~] SP03-Q02 Owner visual acceptance of local 2048→24 `AREA_AVERAGE_V1` result is UNVERIFIED and carried into SP04.

No further SP03 remediation cycle is authorized solely from C003.

---

# PAG-SP04 — Semantic Provider / Model / Workflow Qualification

State: **ACTIVE / C001 READY_FOR_IMPLEMENTATION**

Current prompt:

`.hiveai/prompts/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_PROMPT.md`

## C001 goals

- [ ] SP04-C001-001 Add provider-neutral qualification lifecycle/schema/harness.
- [ ] SP04-C001-002 Add versioned benchmark corpus with recognizable subjects: wizard, dwarf/warrior, elf, robot, fish, sea creature, mushroom, ghost, rocket, tree, skull, potion, crab, alien, simple building/object.
- [ ] SP04-C001-003 Keep 24x24 as first owner-approved ASSET_ART qualification baseline without importing LEVEL_ART rules.
- [ ] SP04-C001-004 Build explicit MAGNIFIC / PIXELLAB provider-engine-workflow qualification matrix with no silent fallback.
- [ ] SP04-C001-005 Model Magnific raw→SP03 normalization path and PixelLab exact-size/no-resize path distinctly.
- [ ] SP04-C001-006 Require local raw import/normalization compatibility PASS before any real candidate becomes blind-review-ready.
- [ ] SP04-C001-007 Build metadata-blind review records with stable ID binding, never positional binding.
- [ ] SP04-C001-008 Keep owner visual disposition separate from technical generation/normalization status.
- [ ] SP04-C001-009 Keep provider cost/usage separate from deterministic artwork/review identity.
- [ ] SP04-C001-010 Make future paid attempt count/budget explicit and finite before execution.
- [ ] SP04-C001-011 Reference owner-approved wizard positive evidence and M10 rejected 100-pack negative evidence without committing private provider ids/URLs.
- [ ] SP04-C001-012 Add deterministic technical metrics only; no fake automated recognizability oracle.
- [ ] SP04-C001-013 Full focused/regression/offline/security verification green.
- [ ] SP04-C001-014 No provider execution or credit spend in C001.

## Qualification gates carried into later SP04 live cycles

- [ ] SP04-Q01 Capture exact live Magnific raw bytes locally and compute immutable SHA-256.
- [ ] SP04-Q02 Prove exact live Magnific raw media/chunk profile is accepted by local SP03 decoder/import boundary; if not, open evidence-driven compatibility remediation rather than broadening formats speculatively.
- [ ] SP04-Q03 Normalize the real Magnific raw candidate locally to 24x24 and present it metadata-blind for owner review.
- [ ] SP04-Q04 Compare the local normalized Magnific result against the already accepted provider-produced 24x24 derivative.
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

Execute **PAG-SP04-C001 only**.

Do not call Magnific/PixelLab or spend credits in C001. Do not begin SP04 live generation, SP05, Studio UI or M11. Codex must not edit `TASKS.md`, must create the matching builder log before source edits, commit/push `main`, verify local HEAD == origin/main divergence `0 0`, then stop for independent ChatGPT audit.
