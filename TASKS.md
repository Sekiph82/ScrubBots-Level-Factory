# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, review evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP03 — Semantic Normalization Pipeline**
- Current Sprint: **PAG-SP03-C003**
- Current Task: **Provenance Seal & Construction Integrity Closure**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX**
- Previous Cycle: `PAG-SP03-C002` → **FAIL / ONE BOUNDED PROVENANCE REMEDIATION REQUIRED**
- Previous Strict Audit: `.hiveai/audits/PAG-SP03-C002_BOUNDED_DECODE_DEEP_IMMUTABILITY_AND_RAW_TO_NORMALIZED_PROVENANCE_CLOSURE_STRICT_AUDIT.md`
- Current Prompt: `.hiveai/prompts/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_PROMPT.md`
- Previous Milestone: `PAG-SP02` → **PASS / CLOSED FOR CURRENT SCOPE**
- Live Smoke Evidence: `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`
- Owner Decision: **Magnific wizard visual accepted; 24x24 px accepted as first ASSET_ART baseline target**
- Next Task/Action: Execute SP03-C003 only, close the resettable provenance-seal defect, publish builder log/tests, commit/push `main`, then stop for independent ChatGPT audit.
- Blockers/Waits: **SP04 and M11 remain blocked** until SP03 receives technical PASS.
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
- SP03 currently rejects all final LEVEL_ART normalization requests until canonical palette+difficulty normalization is implemented.

### ASSET_ART

- Separate from LevelData/difficulty legality.
- **24x24 px is the first owner-approved baseline target.**
- 24x24 is not the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART.
- Current baseline palette policy: `PRESERVE_SOURCE_RGBA`.

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
- [~] **PAG-SP03 — Semantic Normalization Pipeline** — C003 provenance-seal remediation active
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
- [x] Magnific live generation PASS and owner visual acceptance PASS.
- [x] Owner 24x24 ASSET_ART baseline acceptance PASS.
- [~] Local Factory import of the private live Magnific bytes remains a downstream SP03 verification input, not an SP02 code blocker.

---

# PAG-SP03 — Semantic Normalization Pipeline

State: `ACTIVE / C003_REMEDIATION`

## C001 — Raw Capture & Deterministic 24x24 Normalization Foundation

State: `FAIL / REMEDIATED BY C002, WITH PROVENANCE RESIDUAL CARRIED FORWARD`

Accepted direction:

- [x] Separate raw/request/report/normalized lifecycle.
- [x] Immutable raw bytes/hash.
- [x] Exact 24x24 no-resize path.
- [x] Deterministic `AREA_AVERAGE_V1` + `FIT_CENTER_LETTERBOX_V1` baseline.
- [x] Explicit alpha policies.
- [x] ASSET_ART `PRESERVE_SOURCE_RGBA` boundary.
- [x] M08 LEVEL_ART masquerade blocked.

C001 audit: `.hiveai/audits/PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_STRICT_AUDIT.md`.

## C002 — Bounded Decode, Deep Immutability & Raw-to-Normalized Provenance Closure

State: **FAIL / ONE C003 REQUIRED**

Builder reported:

- 14 SP03 focused tests passed;
- 78 SP01+SP02+SP03 focused tests passed;
- 459 full repository tests passed;
- compile/import/CLI/offline checks passed.

Independent audit replay: **UNVERIFIED** because audit container could not resolve `github.com`.

C002 disposition:

- [x] `F-PAG-SP03-C001-001` decompression-bomb bound bypass CLOSED.
- [x] `F-PAG-SP03-C001-002` mutable report state CLOSED.
- [~] `F-PAG-SP03-C001-003` raw-to-normalized provenance PARTIALLY CLOSED; residual construction-seal defect moved to `F-PAG-SP03-C002-001`.
- [x] `F-PAG-SP03-C001-004` LEVEL_ART request legality CLOSED by fail-all strategy.

C002 strict audit: `.hiveai/audits/PAG-SP03-C002_BOUNDED_DECODE_DEEP_IMMUTABILITY_AND_RAW_TO_NORMALIZED_PROVENANCE_CLOSURE_STRICT_AUDIT.md`.

Residual:

- [!] `F-PAG-SP03-C002-001` **MAJOR** — source provenance plus normalized construction fingerprint can be re-sealed through coordinated `dataclasses.replace()` because source snapshot is publicly forgeable and token/fingerprint are caller-replaceable init fields.
- [~] `F-PAG-SP03-C002-002` **MINOR process** — builder authority chronology used deprecated hidden `.hiveai` tracker/control-plane inputs despite prompt prohibition.

## C003 — Provenance Seal & Construction Integrity Closure

State: **READY_FOR_IMPLEMENTATION**

Authoritative prompt: `.hiveai/prompts/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_PROMPT.md`

Required closure:

- [ ] SP03-C003-001 Seal `SemanticSourceProvenance` so arbitrary direct/`replace()` construction cannot claim an existing raw-artifact digest with changed source provenance.
- [ ] SP03-C003-002 Make normalized internal construction token/fingerprint non-caller-resettable through normal constructor/`dataclasses.replace()` paths.
- [ ] SP03-C003-003 Reject coordinated source-snapshot + provider/version/workflow/model/request replacement even when all fields are syntactically valid.
- [ ] SP03-C003-004 Add exact coordinated-tamper sensitivity tests.
- [ ] SP03-C003-005 Preserve all accepted C001/C002 image output byte behavior.
- [ ] SP03-C003-006 Preserve bounded zlib and deep report immutability.
- [ ] SP03-C003-007 Preserve LEVEL_ART fail-closed behavior and 24x24 ASSET_ART independence.
- [ ] SP03-C003-008 Use only current root tracker/current prompt/audit/governance as authority; no legacy hidden tracker inputs.
- [ ] SP03-C003-009 Focused + SP01/SP02/SP03 + full regression green.
- [ ] SP03-C003-010 No provider execution, credits, SP04 or M11.

### SP03 technical acceptance gate after C003

- [x] SP03-A01 Raw provider bytes/hash immutable before/after normalization.
- [x] SP03-A02 Malformed/compressed input bounded by explicit decode budget.
- [x] SP03-A03 Exact-size source uses no hidden interpolation.
- [x] SP03-A04 Large-raster downsample is deterministic and fully reported.
- [x] SP03-A05 Report deterministic identity is deeply immutable.
- [ ] SP03-A06 Normalized provenance is non-forgeably bound to exact raw source/request/provider chain.
- [x] SP03-A07 ASSET_ART does not inherit LEVEL_ART palette/color-band rules.
- [x] SP03-A08 LEVEL_ART cannot bypass current canonical contracts.
- [x] SP03-A09 No normalized ASSET_ART can masquerade as M08 LEVEL_ART.
- [ ] SP03-A10 Independent audit marks C003/SP03 technical foundation PASS.

---

# PAG-SP04 — Semantic Provider / Model / Workflow Qualification

**BLOCKED until SP03 technical PASS.**

Planned:

- benchmark concrete recognizable subjects;
- compare Magnific models/workflows within owner-approved credit budget;
- compare PixelLab PixFlux/BitForge when API access is authorized;
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

Execute **PAG-SP03-C003 only**.

Do not begin SP04, SP05, Studio UI or M11. Do not call Magnific/PixelLab or spend credits. Codex must not edit `TASKS.md`, must create the matching builder log before source edits, commit/push `main`, verify local HEAD == origin/main divergence `0 0`, then stop for independent ChatGPT audit.