# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, review evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP03 — Semantic Normalization Pipeline**
- Current Sprint: **PAG-SP03-C001**
- Current Task: **Raw Capture & Deterministic 24x24 Normalization Foundation**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX**
- Previous Milestone: `PAG-SP02` → **PASS / CLOSED FOR CURRENT SCOPE**
- Previous Code Cycle: `PAG-SP02-C003` → **PASS / CLOSED**
- Previous Strict Audit: `.hiveai/audits/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_STRICT_AUDIT.md`
- Live Smoke Evidence: `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`
- Owner Decision: **Magnific wizard visual accepted; 24x24 px accepted as the first ASSET_ART baseline target**
- Current Prompt: `.hiveai/prompts/PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_PROMPT.md`
- Next Task/Action: Execute SP03-C001 only, publish builder log/tests, commit/push `main`, then stop for independent ChatGPT audit.
- Blockers/Waits: **SP04 and M11 remain blocked** until SP03 normalization receives technical acceptance. PixelLab live smoke remains optional/pending an authorized `PIXELLAB_SECRET`; it does not reopen accepted SP02 provider code.
- Approved Semantic Providers: **MAGNIFIC**, **PIXELLAB**
- Provider Architecture: **provider-neutral; no silent provider/model fallback**
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Current Product Goal

Convert the accepted deterministic Pixel Art Generator foundation into a PixelLab-like Semantic Pixel Studio:

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

These remain unchanged:

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
- Existing architecture may represent sizes such as 16x16, 24x24, 32x32, 48x48, 64x64 and rectangles.
- **24x24 px is now the first owner-approved baseline target.**
- This does not mean 24x24 is the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART unless an explicit later palette policy says so.

## Provider Decisions

### MAGNIFIC

- Approved while owner credits are available.
- External owner-authorized orchestration only; Factory must not scrape/drive private endpoints.
- Raw provider dimensions and logical target dimensions are separate provenance concepts.
- Current pinned smoke model: `recraft-v4-1`.
- Live smoke produced a 2048x2048 raw wizard and an exact 24x24 derivative.
- Owner accepted both the visual direction and 24x24 dimensions.
- Private creation identifiers/signed URLs are not committed to the repository.

### PIXELLAB

- Official SDK/API provider remains approved.
- Provider id `PIXELLAB`.
- Official Python package `pixellab`, baseline inspected version `1.0.8`.
- Secret from `PIXELLAB_SECRET` only.
- PixFlux exact-size generation and deterministic provider-seed mapping remain accepted SP02 contracts.
- BitForge STYLE + style-strength mapping remains accepted.
- Live PixelLab smoke is pending an authorized secret/environment and is not required to reopen SP02 code acceptance.

## Authority Documents

- `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
- `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`
- `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
- `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`
- `review/m10/M10_OWNER_REVIEW_DECISION.md`
- `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`
- `.hiveai/audits/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_STRICT_AUDIT.md`

---

# Milestone Overview

## Historical procedural foundation

- [x] PAG-M00 — Repository Bootstrap & Governance
- [x] PAG-M01 — Canonical SCRUBBOTS Contracts
- [x] PAG-M02 — Deterministic Generation Core
- [x] PAG-M03 — Mask / Sprite Generator
- [x] PAG-M04 — Procedural Shape / Rule Generator technical closure
- [x] PAG-M05 — Wave Function Collapse Generator
- [x] PAG-M06 — Hybrid Generator Router
- [x] PAG-M07 — Artwork Quality & Diversity Filters
- [x] PAG-M08 — Output / Export Contract
- [x] PAG-M09 — CLI & Local Batch Generation
- [x] PAG-M10 — Technical validation/performance foundation
- [!] PAG-M10 visual V1 acceptance — OWNER REJECTED 100/100
- [!] PAG-M11 — Godot/Main-Level-Factory Handoff Gate blocked pending semantic replacement acceptance

M10 technical performance decision remains accepted: RULES 59x59 offline-factory operational p95 budget approximately 15 s; `PAG-0441` technically closed.

## Semantic Pixel Studio roadmap

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [~] PAG-SP03 — Semantic Normalization Pipeline
- [ ] PAG-SP04 — Semantic Provider / Model / Workflow Qualification
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

---

# PAG-SP02 — Final Disposition

State: **PASS / CLOSED FOR CURRENT SCOPE**

Technical closure cycle: `PAG-SP02-C003`.

Strict audit: `.hiveai/audits/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_STRICT_AUDIT.md`.

Accepted facts:

- [x] explicit provider selection and no silent fallback;
- [x] Magnific pinned per-model capabilities and unknown-model fail-closed behavior;
- [x] raw provider rasters up to versioned 8192 bound without relaxing logical request dimensions;
- [x] exact Magnific request↔job↔manifest provenance binding;
- [x] exact PixelLab request↔job↔candidate↔manifest provenance binding;
- [x] mutable audit/cost/failure prose excluded from deterministic provider-result identity;
- [x] PixelLab exact-size/seed/control/style-strength mappings preserved;
- [x] no raw provider candidate can masquerade as normalized M08 artwork;
- [x] live Magnific generation succeeded using `recraft-v4-1`;
- [x] exact 24x24 derivative produced;
- [x] owner accepted the visual direction;
- [x] owner accepted 24x24 as first ASSET_ART baseline target;
- [~] local Factory ingestion of the exact live private PNG bytes was not exercised during the connector smoke; SP03 owns immutable raw-byte capture/normalization verification;
- [~] PixelLab live smoke pending secret/authorization, non-blocking for SP03.

Non-blocking documentation debt:

- [~] align Magnific snapshot observation-date wording on next docs touch.

---

# PAG-SP03 — Semantic Normalization Pipeline

State: **ACTIVE / C001 READY_FOR_IMPLEMENTATION**

Current cycle:

`PAG-SP03-C001 — Raw Capture & Deterministic 24x24 Normalization Foundation`

Prompt:

`.hiveai/prompts/PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_PROMPT.md`

C001 scope:

- [ ] SP03-C001-001 Define immutable raw semantic artifact with exact bytes/hash/provider/request provenance.
- [ ] SP03-C001-002 Prove raw source bytes/hash are never mutated by normalization.
- [ ] SP03-C001-003 Add deterministic local decode with explicit image-format/orientation/safety behavior.
- [ ] SP03-C001-004 Define immutable/versioned normalization request/report/artifact contracts.
- [ ] SP03-C001-005 Support owner-approved 24x24 ASSET_ART target as first-class baseline.
- [ ] SP03-C001-006 Exact-size 24x24 source must take a no-resize/no-interpolation fast path.
- [ ] SP03-C001-007 Add deterministic large-raster -> 24x24 baseline policy without claiming owner acceptance of the local resampler.
- [ ] SP03-C001-008 Add explicit alpha/background policy; no heuristic background deletion.
- [ ] SP03-C001-009 Add ASSET_ART `PRESERVE_SOURCE_RGBA` palette policy boundary without importing LEVEL_ART color-band rules.
- [ ] SP03-C001-010 Keep LEVEL_ART final output fail-closed until required C01..C16 canonicalization policy is implemented.
- [ ] SP03-C001-011 Preserve raw-to-normalized provenance/digests and exclude paths/secrets/private URLs from identity.
- [ ] SP03-C001-012 Provide local-file ingestion/tooling path without external provider calls.
- [ ] SP03-C001-013 Add deterministic/sensitivity/security tests including synthetic 24x24 and 2048x2048 fixtures.
- [ ] SP03-C001-014 Preserve SP01/SP02 and M00-M10 regressions.
- [ ] SP03-C001-015 No provider credit spend, no SP04, no M11.

Later SP03 scope after C001 audit:

- [ ] final LEVEL_ART C01..C16 palette mapping;
- [ ] LEVEL_ART difficulty color-band enforcement after semantic normalization;
- [ ] ASSET_ART palette-policy refinement if owner/product needs it;
- [ ] real owner-approved Magnific raw/24x24 file capture through the accepted ingestion path;
- [ ] normalization visual review comparing local deterministic output with the accepted 24x24 provider derivative.

---

# Future Milestones

## PAG-SP04 — Provider / Model / Workflow Qualification

Compare Magnific models and PixelLab PixFlux/BitForge using representative semantic subjects, provider cost/usage, exact-small-raster behavior and metadata-blind owner recognizability review.

## PAG-SP05 — LEVEL_ART Semantic Integration

Route owner-visible semantic art into existing MASK/RULES/WFC/HYBRID infrastructure while preserving exact LevelData contracts.

## PAG-SP06 — Semantic Quality / Recognizability Gate

Separate structural accept from semantic accept; owner acceptance remains authoritative.

## PAG-SP07 — Reference / Style Generation

Provider-truthful reference/style/color/init workflows with content-hash provenance.

## PAG-SP08 — Edit / Inpaint

Versioned edit lineage and re-normalization.

## PAG-SP09 — Pixel Studio Create / Gallery UI

PixelLab-inspired provider-neutral Create/Gallery workspace.

## PAG-SP10 — Automated Weekly Semantic Batch

Budget-aware attempts, failures, normalization rejects and owner review queue.

## PAG-SP11 — ASSET_ART Production

Character/enemy/item/object/icon production using owner-approved asset policies. 24x24 is the first accepted baseline, not an exclusive size.

## PAG-SP12 — Direction / Rotation Variants

Audited provider-native or local direction/rotation lineage.

## PAG-SP13 — Animation

Optional animation-frame lineage, separate from level acceptance.

## PAG-SP14 — ScrubBots Level Factory Bridge

Export only owner-accepted normalized LEVEL_ART to main ScrubBots Level Factory. Re-open M11 only after semantic replacement acceptance.

---

## Current Stop Rule

Execute **PAG-SP03-C001 only**. Do not begin SP03-C002, SP04 or M11. Do not call Magnific or PixelLab or spend provider credits. Codex must publish the matching builder log, commit/push `main`, verify local HEAD == origin/main with divergence `0 0`, then stop for independent ChatGPT strict audit.