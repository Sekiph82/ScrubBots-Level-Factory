# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical H!veAI control-plane trackers are not current authority. Detailed M00-M10 evidence remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion**
- Current Sprint: **PAG-SP02-C003**
- Current Task: **Model Capability Snapshot, Raw Raster Ceiling & Cross-Provenance Closure**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX**
- Previous Cycle: `PAG-SP02-C002` → **FAIL / BOUNDED REMEDIATION REQUIRED**
- Previous Strict Audit: `.hiveai/audits/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_STRICT_AUDIT.md`
- Current Prompt: `.hiveai/prompts/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_PROMPT.md`
- Next Task/Action: Execute SP02-C003 only, close the four remaining provider-contract findings, publish tests/log, commit/push `main`, then stop for independent ChatGPT audit.
- Blockers/Waits: **SP03, SP04, live provider smoke and M11 remain blocked** until SP02 receives independent technical acceptance.
- Approved Semantic Providers: **MAGNIFIC**, **PIXELLAB**
- Provider Selection: **explicit per request/job; no silent provider or model fallback**
- Magnific Mode: owner-authorized external orchestration while owner credits are available.
- PixelLab Mode: official Developer API / Python SDK direct provider, opt-in network execution only.
- Provider Architecture: **provider-neutral**; providers may later be replaced without rewriting Factory core.
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Current Product Goal

Convert the accepted deterministic Pixel Art Generator foundation into a **PixelLab-like Semantic Pixel Studio** that can generate recognizable small pixel art from text/reference/style inputs, then route it through existing ScrubBots provenance, validation, review, batch and export machinery.

```text
TEXT / REFERENCE / STYLE
          ↓
 EXPLICIT SEMANTIC PROVIDER
   MAGNIFIC | PIXELLAB
          ↓
 recognizable raw semantic artwork
          ↓
 deterministic ingestion / normalization
          ↓
 existing MASK / RULES / WFC / HYBRID
 as control / puzzle / style infrastructure
          ↓
 structural QA + semantic recognizability gate
          ↓
 owner review
          ↓
 M08 export / M09 batch-reproduce / Level Factory handoff
```

The previous M10 100-image owner pack is **REJECTED 100/100** as semantic artwork. It remains a permanent negative regression set. The failure was semantic recognizability, not board resolution.

## Preserved Owner-Locked LEVEL_ART Contracts

These remain hard legality unless the owner explicitly changes them:

- EASY: width/height independently 20-29
- MEDIUM: 30-39
- HARD: 40-49
- VERY_HARD: 50-59
- rectangular boards allowed
- one logical artwork pixel = one gameplay cell
- C01..C16 logical palette only
- EASY 3-5 distinct used colors
- MEDIUM 6-7
- HARD 8-9
- VERY_HARD 10-12
- BG01 `#202533` is presentation/background only
- no interpolation/antialiasing inside logical cells
- deterministic project provenance and exact export remain required

`ASSET_ART` is separate from LevelData and may use explicit sizes such as 16x16, 24x24, 32x32, 48x48, 64x64 and rectangles under its own asset policy.

Raw provider output dimensions are a separate concept from logical requested dimensions. A provider may return a much larger raster, but that raw raster cannot become logical artwork until SP03 normalization.

## Provider Rules

### MAGNIFIC

- approved semantic provider while owner credits are available;
- local Factory must not scrape/drive Magnific website or use undocumented/private endpoints;
- initial execution is owner-authorized external orchestration;
- current surfaced integration does not expose provider seed or exact logical raster size;
- requested logical dimensions and returned provider raster dimensions are separate provenance fields;
- raw provider raster remains raw until SP03 normalization;
- provider-native capability truth is **model-specific** where the connected catalog differs by model;
- model capability snapshots used by deterministic jobs must be pinned/versioned and truthful;
- unknown/unpinned model slugs must fail closed in SP02;
- provider/model selection is explicit, never silent fallback.

### PIXELLAB

Official SDK authority: `https://github.com/pixellab-code/pixellab-python`.

- provider id: `PIXELLAB`;
- official package: `pixellab`;
- inspected SDK version: `1.0.8`;
- default API base: `https://api.pixellab.ai/v1`;
- secret from `PIXELLAB_SECRET` only;
- optional base URL from `PIXELLAB_BASE_URL`;
- PixFlux supports exact `image_size`, negative description, outline, shading, detail, view/direction, isometric, no-background, coverage, init image, forced color image and integer seed;
- BitForge additionally exposes style image and `style_strength`, plus richer edit/reference inputs;
- direct PixelLab network access is allowed only inside explicit PIXELLAB provider execution;
- package import, job preparation and historical procedural generation remain network-free;
- secrets never enter source control, canonical identity, manifests or logs.

## Authority Documents

- `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
- `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`
- `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
- `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`
- `review/m10/M10_OWNER_REVIEW_DECISION.md`

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

M10 technical performance decision retained: RULES 59x59 V1 offline-factory budget accepted at approximately **15 s operational p95 budget**; `PAG-0441` is technically closed.

## Semantic Pixel Studio roadmap

- [x] **PAG-SP00 — Owner Rejection & Semantic Pivot Record**
- [x] **PAG-SP01 — Semantic Contracts & Provider Boundary**
- [~] **PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion**
- [ ] **PAG-SP03 — Semantic Normalization Pipeline**
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

# PAG-SP00 — Owner Rejection & Semantic Pivot Record

Final state: `PASS / CLOSED`

- [x] SP00-001 Record owner rejection of the entire M10 100-image review pack.
- [x] SP00-002 Preserve the rejected pack as negative regression evidence.
- [x] SP00-003 Publish Semantic Pixel Studio conversion plan.
- [x] SP00-004 Select Magnific as an approved semantic provider while credits are available.
- [x] SP00-005 Preserve provider-neutral architecture.
- [x] SP00-006 Authorize PixelLab official Developer API / Python SDK as an additional direct semantic provider.

---

# PAG-SP01 — Semantic Contracts & Provider Boundary

Final state: `PASS / CLOSED`

Closing cycle: `PAG-SP01-C003 — Non-Success Provenance Echo & Mismatch-Test Sensitivity Closure`

Closing audit: `.hiveai/audits/PAG-SP01-C003_NON_SUCCESS_PROVENANCE_ECHO_AND_MISMATCH_TEST_SENSITIVITY_CLOSURE_STRICT_AUDIT.md`

- [x] SP01-001 Define `LEVEL_ART` and `ASSET_ART` output classes.
- [x] SP01-002 Define immutable/versioned `SemanticGenerationRequest`.
- [x] SP01-003 Define content-identified image input descriptors.
- [x] SP01-004 Define provider-neutral `SemanticGeneratorProvider` boundary.
- [x] SP01-005 Define typed raw `SemanticImageCandidate` success/failure boundary.
- [x] SP01-006 Define truthful provider capability schema.
- [x] SP01-007 Define deterministic request/result identity rules.
- [x] SP01-008 Bind LEVEL_ART dimensions to existing ScrubBots difficulty contracts.
- [x] SP01-009 Keep ASSET_ART independent of LevelData difficulty legality.
- [x] SP01-010 Enforce REFERENCE / STYLE / INIT / COLOR_REFERENCE role integrity.
- [x] SP01-011 Bind provider/result provenance exactly to the checked request.
- [x] SP01-012 Make non-success candidates provenance-complete.
- [x] SP01-013 Prevent raw semantic candidates from masquerading as M08 logical artwork before normalization.

---

# PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion

State: `ACTIVE / C003_REMEDIATION`

## Cycle PAG-SP02-C001 — Magnific + PixelLab Provider Bridges & Result Ingestion

State: **FAIL / REMEDIATED BY C002**

Strict audit: `.hiveai/audits/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_STRICT_AUDIT.md`

C001 established the useful multi-provider foundation but failed on Magnific raw-raster handling, executable capability truth, result identity, exact model binding, BitForge style strength and smoke readiness.

C001 strict-audit findings:

- [x] `F-PAG-SP02-C001-001` original logical==raw raster equality defect removed in C002; a >1024 cross-layer residual remains under C002 finding 001.
- [~] `F-PAG-SP02-C001-002` arbitrary ratio algorithm/native prompt-control overclaim largely fixed in C002; model-specific snapshot fidelity remains under C002 finding 002.
- [~] `F-PAG-SP02-C001-003` audit/cost identity contamination fixed for success/audit metadata; failure diagnostic identity residual remains under C002 finding 003.
- [x] `F-PAG-SP02-C001-004` request/job/actual success-model drift closed in C002; broader cross-object binding tracked separately under C002 finding 004.
- [x] `F-PAG-SP02-C001-005` BitForge style-strength omission closed in C002.
- [x] `F-PAG-SP02-C001-006` stale Magnific smoke slug replaced with current `recraft-v4-1` in C002.
- [x] `F-PAG-SP02-C001-007` legacy hidden tracker authority misuse corrected in C002 builder process.

## Cycle PAG-SP02-C002 — Provider Contract Fidelity, Result Identity & Smoke Readiness Remediation

State: **FAIL / BOUNDED C003 REQUIRED**

Authoritative prompt: `.hiveai/prompts/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_PROMPT.md`

Strict audit: `.hiveai/audits/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_STRICT_AUDIT.md`

Builder reported 54 focused SP01+SP02 tests and 435 full repository tests passing. Independent audit runtime replay was blocked by audit-container GitHub DNS, but static/provider-contract findings are definitive.

C002 task disposition:

- [~] SP02-C002-001 Logical requested dimensions are separated from Magnific raw dimensions, but raw `SemanticImageCandidate` still caps returned rasters at 1024.
- [~] SP02-C002-002 Deterministic ratio mapping exists, but pinned per-model capability sets are inaccurate/fail-open.
- [x] SP02-C002-003 Magnific negative prompt/transparency/view/isometric prompt hints are no longer advertised as native capabilities.
- [~] SP02-C002-004 Audit/cost/transient metadata are excluded from success identity, but free-text failure diagnostics still affect manifest digest.
- [x] SP02-C002-005 Exact request/job/actual success-model drift is rejected.
- [x] SP02-C002-006 BitForge `style_strength` maps 0..1 -> 0..100 and reaches SDK kwargs.
- [x] SP02-C002-007 Smoke fixture now uses current catalog-valid `recraft-v4-1` model slug.
- [~] SP02-C002-008 Success/failure manifest consistency improved, but coordinated cross-object binding and failure actual-model semantics remain incomplete.
- [~] SP02-C002-009 Sensitivity tests improved but do not cover >1024 rasters, model-specific catalog truth, failure-reason identity or coordinated mismatches.
- [x] SP02-C002-010 Optional/lazy PixelLab SDK loading, env-secret safety, exact image-size/seed mapping and provider isolation preserved.
- [~] SP02-C002-011 SP01 architecture preserved, but exact request↔job↔candidate/manifest binding still has residual gaps.
- [~] SP02-C002-012 Builder full suite green; independent replay UNVERIFIED due auditor DNS.
- [x] SP02-C002-013 Builder used root `TASKS.md` and current GitHub authority docs rather than stale hidden trackers.

C002 strict-audit residuals:

- [!] `F-PAG-SP02-C002-001` raw semantic candidate returned dimensions still reject valid provider rasters above 1024.
- [!] `F-PAG-SP02-C002-002` Magnific model capability snapshots are inaccurate/fail-open for aspect ratios/reference roles and explicit resolution/quality.
- [!] `F-PAG-SP02-C002-003` provider result-manifest digest still includes mutable free-text `failure_reason`.
- [!] `F-PAG-SP02-C002-004` exact request↔job↔candidate/manifest coordinated provenance binding remains incomplete.
- [!] `F-PAG-SP02-C002-005` Magnific failure `actual_model_slug` is over-specified when no actual execution model was observed.

## Cycle PAG-SP02-C003 — Model Capability Snapshot, Raw Raster Ceiling & Cross-Provenance Closure

State: **READY_FOR_IMPLEMENTATION**

Authoritative prompt: `.hiveai/prompts/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_PROMPT.md`

- [ ] SP02-C003-001 Separate raw returned-provider raster validation bound from requested/logical dimensions; support at least 2048 and 4096 raw output without normalization.
- [ ] SP02-C003-002 Keep LEVEL_ART and ASSET_ART requested/logical dimension legality unchanged.
- [ ] SP02-C003-003 Replace permissive Magnific metadata with a versioned per-model capability snapshot.
- [ ] SP02-C003-004 Pin exact model-specific aspect ratios for the deliberately supported Magnific smoke/SP04 candidate set.
- [ ] SP02-C003-005 Validate selected-model REFERENCE/STYLE role support; do not treat provider union capability as model truth.
- [ ] SP02-C003-006 Reject unknown/unpinned Magnific model slugs in SP02 instead of inheriting a global permissive default.
- [ ] SP02-C003-007 Validate explicit Magnific resolution/quality overrides against pinned model capability or reject them when unsupported/unpinned.
- [ ] SP02-C003-008 Regenerate the `recraft-v4-1` smoke fixture with its exact pinned capability snapshot, excluding unsupported `21:9`.
- [ ] SP02-C003-009 Remove free-text `failure_reason` from Magnific and PixelLab result-manifest deterministic digest identity while retaining full audit serialization.
- [ ] SP02-C003-010 Add exact Magnific request↔job binding before manifest import and reject coordinated request-A/job-B mismatches.
- [ ] SP02-C003-011 Add exact PixelLab request↔job↔candidate binding before result-manifest creation and reject coordinated mismatches.
- [ ] SP02-C003-012 Make Magnific failure observed-actual-model provenance optional/truthful while retaining requested model provenance.
- [ ] SP02-C003-013 Add sensitivity tests for >1024 raw rasters, pinned model capabilities, unknown models, failure identity invariance and coordinated provenance mismatches.
- [ ] SP02-C003-014 Preserve all accepted C002 PixelLab seed/size/style-strength/secret/isolation behavior.
- [ ] SP02-C003-015 Full focused + SP01 + full repository regression green.
- [ ] SP02-C003-016 No paid provider execution, no live PixelLab call, no Magnific browser/private API automation.

### SP02 technical acceptance after C003

- [ ] SP02-A01 Same semantic request + same explicit provider/model bindings produces byte-identical canonical provider job identity.
- [ ] SP02-A02 Raw result is cryptographically/provenance bound to the exact request/job/provider/engine/model chain.
- [ ] SP02-A03 Audit URL/timestamp/cost/failure diagnostic prose changes do not alter deterministic provider-result identity.
- [ ] SP02-A04 Magnific can represent a normal 2k/4k raw provider raster while retaining logical target dimensions for future SP03.
- [ ] SP02-A05 Magnific job capabilities are truthful for the selected pinned model and unknown models fail closed.
- [ ] SP02-A06 PixelLab retains exact-size provider intent and deterministic request-to-provider-seed mapping.
- [ ] SP02-A07 BitForge STYLE retains explicit style-strength semantics.
- [ ] SP02-A08 Normal provider failures remain provenance-complete and typed without fabricated observed execution facts.
- [ ] SP02-A09 No raw provider image is treated as normalized logical artwork.
- [ ] SP02-A10 Historical offline procedural paths remain unaffected.
- [ ] SP02-A11 Independent audit marks C003/SP02 technically smoke-ready.
- [ ] SP02-A12 Owner-authorized live Magnific smoke may run only after technical PASS.
- [ ] SP02-A13 Owner-authorized PixelLab smoke may run only after technical PASS plus available `PIXELLAB_SECRET` and explicit authorization.

---

# PAG-SP03 — Semantic Normalization Pipeline

- [ ] SP03-001 Preserve raw provider image bytes/hash immutably.
- [ ] SP03-002 Decode provider image deterministically.
- [ ] SP03-003 Handle transparency/background explicitly.
- [ ] SP03-004 Detect/derive logical-pixel structure without hidden interpolation.
- [ ] SP03-005 Define deterministic crop/pad/nearest-neighbor/segmentation rules where required.
- [ ] SP03-006 For LEVEL_ART, map colors deterministically to C01..C16 when provider output is not already canonical.
- [ ] SP03-007 Enforce LEVEL_ART difficulty used-color bands.
- [ ] SP03-008 Define separate ASSET_ART palette policy boundary.
- [ ] SP03-009 Emit immutable normalized logical grid with raw-source provenance.
- [ ] SP03-010 Prove raw source is never overwritten.
- [ ] SP03-011 Preserve PixelLab exact-size output without unnecessary resizing when it already matches requested logical dimensions.

---

# PAG-SP04 — Semantic Provider / Model / Workflow Qualification

- [ ] SP04-001 Build benchmark labels including wizard, dwarf, elf, robot, fish, sea creature, mushroom, ghost, rocket, tree, skull, potion, crab, alien and simple building/object.
- [ ] SP04-002 Compare multiple Magnific models/workflows where owner credits permit.
- [ ] SP04-003 Compare PixelLab PixFlux and eligible BitForge paths where API access permits.
- [ ] SP04-004 Measure provider cost/usage separately from accepted normalized candidates.
- [ ] SP04-005 Review small-resolution recognizability metadata-blind.
- [ ] SP04-006 Compare exact-small-raster PixelLab generation against Magnific + SP03 normalization.
- [ ] SP04-007 Select default provider/model/workflow only from evidence and owner acceptance.
- [ ] SP04-008 Do not treat photorealistic quality as pixel-art acceptance.

---

# PAG-SP05 — LEVEL_ART Semantic Integration

- [ ] SP05-001 Use accepted semantic provider output as owner-visible art source.
- [ ] SP05-002 Keep MASK as silhouette/occupancy/control infrastructure.
- [ ] SP05-003 Keep RULES as region/layout/puzzle-control infrastructure.
- [ ] SP05-004 Keep WFC for approved style/detail propagation where evidence supports it.
- [ ] SP05-005 Preserve exact LevelData dimensions/palette/export contracts.
- [ ] SP05-006 Preserve deterministic raw-to-normalized provenance.

---

# PAG-SP06 — Semantic Quality / Recognizability Gate

- [ ] SP06-001 Define versioned `SemanticQualityReport`.
- [ ] SP06-002 Structural M07 ACCEPT must not auto-promote semantic art.
- [ ] SP06-003 Add metadata-blind owner review status.
- [ ] SP06-004 Preserve M10 rejected 100-pack as negative regression set.
- [ ] SP06-005 Add advisory automated semantic scoring only if evidence supports it.
- [ ] SP06-006 Production semantic art requires explicit owner acceptance.

---

# PAG-SP07 — Reference / Style Generation

- [ ] SP07-001 Support multiple references only where provider semantics are truthful.
- [ ] SP07-002 Support explicit style references.
- [ ] SP07-003 Support palette/color references where provider surface truthfully supports them.
- [ ] SP07-004 Support init-image semantics only when provider behavior is explicit/tested.
- [ ] SP07-005 Preserve source content hashes and execution bindings.
- [ ] SP07-006 Build owner-approved style collections.

---

# PAG-SP08 — Edit / Inpaint

- [ ] SP08-001 Define mask-based edit request lineage.
- [ ] SP08-002 Support selected-region repair/replacement when provider capability exists.
- [ ] SP08-003 Add PixelLab BitForge/inpaint path only through official API mapping and audited contracts.
- [ ] SP08-004 Support deterministic recolor/palette remap locally.
- [ ] SP08-005 Re-run normalization and downstream validation after edits.
- [ ] SP08-006 Preserve parent/child provenance.

---

# PAG-SP09 — Pixel Studio Create / Gallery UI

- [ ] SP09-001 Build PixelLab-inspired Create workspace over provider-neutral contracts.
- [ ] SP09-002 Provider selector exposes Magnific/PixelLab explicitly.
- [ ] SP09-003 Controls expose only capabilities valid for selected provider/engine.
- [ ] SP09-004 Add prompt/reference/style/seed/size controls.
- [ ] SP09-005 Add candidate gallery and provenance inspection.
- [ ] SP09-006 Accept/reject never bypasses validation.

---

# PAG-SP10 — Automated Weekly Semantic Batch

- [ ] SP10-001 Define provider-aware batch budget limits.
- [ ] SP10-002 Separate provider attempts, provider failures, normalization rejects and accepted candidates.
- [ ] SP10-003 Prevent unbounded paid-provider retries.
- [ ] SP10-004 Keep provider/cost/usage provenance per attempt.
- [ ] SP10-005 Produce owner review queue and production handoff only after acceptance.

---

# PAG-SP11 — ASSET_ART Production

- [ ] SP11-001 Finalize asset-size and palette policies.
- [ ] SP11-002 Support character/enemy/item/object/icon asset classes.
- [ ] SP11-003 Preserve transparent-background provenance.
- [ ] SP11-004 Support exact 16x16 and larger sprite targets.

---

# PAG-SP12 — Direction / Rotation Variants

- [ ] SP12-001 Define directional variant lineage.
- [ ] SP12-002 Use provider-native rotation/direction features only when audited.
- [ ] SP12-003 Evaluate PixelLab rotate API as a native option.
- [ ] SP12-004 Preserve cross-direction style/identity consistency.

---

# PAG-SP13 — Animation

- [ ] SP13-001 Define animation-frame lineage and contracts.
- [ ] SP13-002 Evaluate PixelLab text/skeleton animation APIs where useful.
- [ ] SP13-003 Keep animation optional and separate from level generation acceptance.

---

# PAG-SP14 — ScrubBots Level Factory Bridge

- [ ] SP14-001 Export only owner-accepted normalized LEVEL_ART.
- [ ] SP14-002 Preserve source semantic/provider provenance in handoff metadata.
- [ ] SP14-003 Integrate with main ScrubBots Level Factory without runtime semantic-provider dependency.
- [ ] SP14-004 Re-open M11 only after owner semantic replacement acceptance.

---

## Current Stop Rule

Do not begin SP03, SP04 or M11. Do not spend provider credits. First execute **PAG-SP02-C003**, publish the builder log, and obtain independent ChatGPT strict audit. Only a technical PASS may authorize a real owner-approved provider smoke generation and later downstream work.
