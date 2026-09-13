# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, review evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP03 — Semantic Normalization Pipeline**
- Current Sprint: **PAG-SP03-C002**
- Current Task: **Bounded Decode, Deep Immutability & Raw-to-Normalized Provenance Closure**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX**
- Previous Cycle: `PAG-SP03-C001` → **FAIL / BOUNDED REMEDIATION REQUIRED**
- Previous Strict Audit: `.hiveai/audits/PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_STRICT_AUDIT.md`
- Current Prompt: `.hiveai/prompts/PAG-SP03-C002_BOUNDED_DECODE_DEEP_IMMUTABILITY_AND_RAW_TO_NORMALIZED_PROVENANCE_CLOSURE_PROMPT.md`
- Previous Milestone: `PAG-SP02` → **PASS / CLOSED FOR CURRENT SCOPE**
- Live Smoke Evidence: `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`
- Owner Decision: **Magnific wizard visual accepted; 24x24 px accepted as first ASSET_ART baseline target**
- Next Task/Action: Execute SP03-C002 only, publish builder log/tests, commit/push `main`, then stop for independent ChatGPT audit.
- Blockers/Waits: **SP04 and M11 remain blocked** until SP03 normalization receives technical acceptance.
- Approved Semantic Providers: **MAGNIFIC**, **PIXELLAB**
- Provider Architecture: **provider-neutral; no silent provider/model fallback**
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

### ASSET_ART

- Separate from LevelData/difficulty legality.
- **24x24 px is the first owner-approved baseline target.**
- 24x24 is not the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART.
- C001 baseline palette policy: `PRESERVE_SOURCE_RGBA`.

## Provider Decisions

### MAGNIFIC

- Approved while owner credits are available.
- External owner-authorized orchestration only; Factory must not scrape/drive private endpoints.
- Raw provider dimensions and logical target dimensions are separate provenance concepts.
- Live `recraft-v4-1` wizard smoke generated successfully and owner accepted the visual direction and 24x24 derivative.

### PIXELLAB

- Official API/SDK provider remains approved.
- Direct network execution is opt-in only.
- `PIXELLAB_SECRET` remains runtime-only.
- PixelLab live smoke is optional/pending authorized secret availability and does not reopen SP02.

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
- [x] **PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion** — technical PASS; live Magnific smoke/owner visual acceptance recorded
- [~] **PAG-SP03 — Semantic Normalization Pipeline** — C002 remediation active
- [ ] **PAG-SP04 — Semantic Provider / Model / Workflow Qualification**
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

Core accepted properties:

- [x] LEVEL_ART / ASSET_ART separation.
- [x] Immutable/versioned semantic request and image descriptors.
- [x] Provider-neutral boundary and typed raw candidates.
- [x] Exact role/provenance binding.
- [x] Raw semantic candidate cannot masquerade as M08 artwork.

---

# PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion

Final state for current scope: `PASS / CLOSED`

Closing code cycle: `PAG-SP02-C003`.

Closing audit: `.hiveai/audits/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_STRICT_AUDIT.md`

Live smoke evidence: `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`.

- [x] Explicit MAGNIFIC / PIXELLAB provider selection.
- [x] Magnific pinned model capability snapshots and raw-raster/provenance bridge.
- [x] PixelLab official SDK boundary with exact-size/seed mapping.
- [x] Result identity excludes mutable audit/cost/failure prose.
- [x] Exact cross-provenance binding.
- [x] Magnific live provider generation PASS.
- [x] Exact 24x24 derivative produced.
- [x] Owner visual acceptance PASS.
- [x] Owner 24x24 ASSET_ART baseline acceptance PASS.
- [~] Real local Factory import of the live private Magnific bytes remains unverified and is carried as SP03 verification input, not an SP02 code blocker.

---

# PAG-SP03 — Semantic Normalization Pipeline

State: `ACTIVE / C002_REMEDIATION`

## Cycle PAG-SP03-C001 — Raw Capture & Deterministic 24x24 Normalization Foundation

State: **FAIL / BOUNDED C002 REQUIRED**

Builder evidence:

- 10 SP03 focused tests passed;
- 74 SP01+SP02+SP03 focused tests passed;
- 455 full repository tests passed according to builder log;
- compile/import/CLI/offline checks passed;
- independent audit runtime replay UNVERIFIED because audit container could not resolve `github.com`.

Accepted implementation direction from C001:

- [x] C001-A01 Separate `SemanticRawArtifact`, normalization request/report and normalized artifact lifecycle.
- [x] C001-A02 Raw bytes/hash retained as immutable bytes.
- [x] C001-A03 Exact 24x24 RGBA -> 24x24 fast path performs no resize/resample.
- [x] C001-A04 Deterministic `AREA_AVERAGE_V1` + `FIT_CENTER_LETTERBOX_V1` baseline exists for large rasters.
- [x] C001-A05 Explicit `PRESERVE_ALPHA` and `OPAQUE_AS_IS` policies.
- [x] C001-A06 ASSET_ART baseline uses `PRESERVE_SOURCE_RGBA` and does not inherit LEVEL_ART color bands.
- [x] C001-A07 Final LEVEL_ART emission remains blocked.
- [x] C001-A08 Local CLI path is provider/network-free and protects the source path.

C001 strict-audit residuals:

- [!] `F-PAG-SP03-C001-001` **MAJOR** — zlib `flush()` is unbounded and can bypass decompression-bomb memory budget.
- [!] `F-PAG-SP03-C001-002` **MAJOR** — report `crop_pad` mapping is mutable after construction, so report/artifact digest can change over object lifetime.
- [!] `F-PAG-SP03-C001-003` **MAJOR** — duplicated provider/request provenance in normalized artifact is not cross-bound to the raw artifact source identity.
- [!] `F-PAG-SP03-C001-004` **MINOR** — LEVEL_ART normalization request can represent arbitrary generic dimensions when future palette policy is supplied instead of preserving existing difficulty legality.

Strict audit:

`.hiveai/audits/PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_STRICT_AUDIT.md`

## Cycle PAG-SP03-C002 — Bounded Decode, Deep Immutability & Raw-to-Normalized Provenance Closure

State: **READY_FOR_IMPLEMENTATION**

Authoritative prompt:

`.hiveai/prompts/PAG-SP03-C002_BOUNDED_DECODE_DEEP_IMMUTABILITY_AND_RAW_TO_NORMALIZED_PROVENANCE_CLOSURE_PROMPT.md`

Required closure:

- [ ] SP03-C002-001 Enforce hard decompressed-output budget through the entire zlib lifecycle; no unbounded flush.
- [ ] SP03-C002-002 Add compact decompression-bomb, exact-bound, overflow, truncated-stream and trailing-data tests.
- [ ] SP03-C002-003 Deep-freeze report `crop_pad` deterministic state.
- [ ] SP03-C002-004 Prove caller dict mutation cannot change report/artifact digest.
- [ ] SP03-C002-005 Cross-bind normalized provider/request provenance exactly to the source raw artifact.
- [ ] SP03-C002-006 Reject coordinated raw/provenance/report/request tampering.
- [ ] SP03-C002-007 Preserve LEVEL_ART request legality or fail all LEVEL_ART normalization-request construction until sufficient context exists.
- [ ] SP03-C002-008 Preserve exact 24x24 fast path, 2048->24 baseline, alpha policies and ASSET palette boundary.
- [ ] SP03-C002-009 Preserve offline/local CLI and no-source-overwrite behavior.
- [ ] SP03-C002-010 Focused + SP01/SP02/SP03 + full regression green.
- [ ] SP03-C002-011 No provider execution, no credits, no SP04/M11.

### SP03 technical acceptance gate after C002

- [ ] SP03-A01 Raw provider bytes/hash remain immutable before/after normalization.
- [ ] SP03-A02 Malformed/compressed input cannot exceed the explicit decode memory budget.
- [ ] SP03-A03 Exact-size source uses no hidden interpolation.
- [ ] SP03-A04 Large raster downsample is byte-deterministic and fully reported.
- [ ] SP03-A05 Deterministic report/artifact identity is deeply immutable.
- [ ] SP03-A06 Normalized provenance is cryptographically bound to the exact raw source/request/provider chain.
- [ ] SP03-A07 ASSET_ART does not inherit LEVEL_ART palette/color-band rules.
- [ ] SP03-A08 LEVEL_ART cannot bypass canonical difficulty/palette contracts.
- [ ] SP03-A09 No normalized ASSET_ART can masquerade as M08 LEVEL_ART.
- [ ] SP03-A10 Independent audit marks C002/SP03 technical foundation PASS.

---

# PAG-SP04 — Semantic Provider / Model / Workflow Qualification

Blocked until SP03 technical PASS.

Planned:

- benchmark concrete recognizable subjects;
- compare Magnific models/workflows within owner-approved credit budget;
- compare PixelLab PixFlux/BitForge when API access is authorized;
- measure costs separately from accepted results;
- metadata-blind small-resolution visual review;
- compare PixelLab exact-small output against Magnific + local normalization;
- select default provider/model/workflow only from evidence and owner acceptance.

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

M11 remains blocked until owner-accepted semantic replacement artwork is technically normalized and accepted through downstream gates.

---

## Current Stop Rule

Execute **PAG-SP03-C002 only**.

Do not begin SP04, SP05, Studio UI or M11. Do not call Magnific/PixelLab or spend credits. Codex must not edit `TASKS.md`, must publish the matching builder log, commit/push `main`, verify local HEAD == origin/main divergence `0 0`, then stop for independent ChatGPT audit.
