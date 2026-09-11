# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical H!veAI control-plane trackers are not current authority. Detailed M00-M10 evidence remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion**
- Current Sprint: **PAG-SP02-C002**
- Current Task: **Provider Contract Fidelity, Result Identity & Smoke Readiness Remediation**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX**
- Previous Cycle: `PAG-SP02-C001` → **FAIL / REMEDIATION REQUIRED**
- Previous Strict Audit: `.hiveai/audits/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_STRICT_AUDIT.md`
- Current Prompt: `.hiveai/prompts/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_PROMPT.md`
- Next Task/Action: Execute SP02-C002 only, close the bounded provider-contract findings, publish tests/log, commit/push `main`, then stop for independent ChatGPT audit.
- Blockers/Waits: **SP03, SP04 and M11 remain blocked** until SP02 receives independent technical acceptance. Live paid provider smoke is also blocked until the corrected bridge is independently accepted as smoke-ready.
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

## Provider Rules

### MAGNIFIC

- approved semantic provider while owner credits are available;
- local Factory must not scrape/drive Magnific website or use undocumented/private endpoints;
- initial execution is owner-authorized external orchestration;
- current surfaced integration does not expose provider seed or exact logical raster size;
- requested logical dimensions and returned provider raster dimensions are separate provenance fields;
- raw provider raster remains raw until SP03 normalization;
- only provider-native capabilities may be advertised as native;
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

State: `ACTIVE / C002_REMEDIATION`

## Cycle PAG-SP02-C001 — Magnific + PixelLab Provider Bridges & Result Ingestion

State: **FAIL / REMEDIATION REQUIRED**

Strict audit: `.hiveai/audits/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_STRICT_AUDIT.md`

Builder evidence established useful foundations:

- [~] SP02-001 deterministic explicit provider registry for `MAGNIFIC` and `PIXELLAB`; technically present, final acceptance pending C002
- [~] SP02-002 unknown provider/silent fallback rejection; final acceptance pending C002
- [~] SP02-003 SP01 exact provider/result provenance integration; residual model/result-identity defects pending C002
- [~] SP02-004 provider SDK/network isolation from Factory core; technically present, final acceptance pending C002
- [~] SP02-005 Magnific identity/version/config contracts present
- [~] SP02-006 Magnific job spec present but aspect-ratio/model contracts require C002
- [~] SP02-010 Magnific content-hash creation bindings present
- [~] SP02-011 Magnific result manifest present but requires C002 corrections
- [~] SP02-014 PixelLab identity/version/config contracts present
- [~] SP02-015 official `pixellab` SDK added as optional/lazy dependency
- [~] SP02-016 PixelLab env-secret boundary implemented; final acceptance pending C002
- [~] SP02-017 PIXFLUX/BITFORGE explicit engine selection present
- [~] SP02-018 PixelLab job spec present
- [~] SP02-019 deterministic ScrubBots seed -> PixelLab integer seed present
- [~] SP02-020 exact PixelLab requested image size mapping present
- [~] SP02-021 explicit control mapping present; unsupported mappings fail closed
- [~] SP02-023 PixFlux INIT/COLOR_REFERENCE byte/hash binding present
- [~] SP02-024 BitForge STYLE path present but style-strength fidelity requires C002
- [~] SP02-026 injectable/mockable PixelLab client path present
- [~] SP02-031/SP02-032 smoke fixtures present but Magnific fixture requires a current valid model slug
- [~] SP02-033/SP02-034/SP02-035 focused offline tests present but C002 sensitivity coverage required
- [~] SP02-036 builder reported full repository regression green; final acceptance pending independent C002 audit

C001 strict-audit findings:

- [!] `F-PAG-SP02-C001-001` Magnific returned provider raster was incorrectly required to equal logical target dimensions.
- [!] `F-PAG-SP02-C001-002` Magnific arbitrary aspect ratios and prompt-only controls were misrepresented as executable/native capabilities.
- [!] `F-PAG-SP02-C001-003` result identity included audit/cost/transient metadata.
- [!] `F-PAG-SP02-C001-004` Magnific request/job/actual-model provenance was not fail-closed.
- [!] `F-PAG-SP02-C001-005` BitForge STYLE support silently omitted native `style_strength`.
- [!] `F-PAG-SP02-C001-006` Magnific smoke fixture used a model slug not present in the current connected catalog.
- [!] `F-PAG-SP02-C001-007` builder consulted stale hidden `.hiveai` trackers as current authority.

## Cycle PAG-SP02-C002 — Provider Contract Fidelity, Result Identity & Smoke Readiness Remediation

State: **READY_FOR_IMPLEMENTATION**

Authoritative prompt: `.hiveai/prompts/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_PROMPT.md`

- [ ] SP02-C002-001 Preserve logical requested dimensions separately from Magnific returned provider raster dimensions; allow valid larger raw raster imports.
- [ ] SP02-C002-002 Implement deterministic supported Magnific aspect-ratio mapping with documented tie-break and model/surface compatibility.
- [ ] SP02-C002-003 Make Magnific native capability declarations truthful; keep prompt-guidance distinct from native provider capability.
- [ ] SP02-C002-004 Split deterministic result identity from audit/cost/transient metadata for both Magnific and PixelLab.
- [ ] SP02-C002-005 Enforce exact Magnific request/job/actual-model binding with no silent model override/fallback.
- [ ] SP02-C002-006 Map BitForge `style_strength` truthfully to official SDK semantics or disable advertised STYLE support.
- [ ] SP02-C002-007 Replace Magnific smoke fixture with a current catalog-valid explicit model slug without executing a paid generation.
- [ ] SP02-C002-008 Harden Magnific success/failure manifest consistency without fabricated creation/image data.
- [ ] SP02-C002-009 Add sensitivity-safe tests for raw raster vs logical size, ratios, capability truth, identity invariance, model binding and BitForge style strength.
- [ ] SP02-C002-010 Preserve optional/lazy PixelLab SDK loading, env-secret safety, exact image-size/seed mapping and provider isolation.
- [ ] SP02-C002-011 Preserve SP01 exact provenance contracts and accepted M00-M10 behavior.
- [ ] SP02-C002-012 Full focused + full repository regression remains green.
- [ ] SP02-C002-013 Builder uses root `TASKS.md` and current GitHub authority docs only, not stale hidden H!veAI trackers.

### SP02 acceptance after C002

- [ ] SP02-A01 Same semantic request + same provider bindings produces byte-identical canonical provider job identity.
- [ ] SP02-A02 Raw result is cryptographically/provenance bound to exact request/job/provider/engine/model.
- [ ] SP02-A03 Audit URL/timestamp/cost changes do not alter deterministic result identity.
- [ ] SP02-A04 Magnific can import a normal larger provider raster while retaining logical target dimensions for future SP03.
- [ ] SP02-A05 PixelLab retains exact-size provider intent and deterministic request-to-provider-seed mapping.
- [ ] SP02-A06 Normal provider failures remain provenance-complete and typed.
- [ ] SP02-A07 No raw provider image is treated as normalized logical artwork.
- [ ] SP02-A08 Historical offline procedural paths remain unaffected.
- [ ] SP02-A09 Independent audit marks bridge technically smoke-ready.
- [ ] SP02-A10 Owner-authorized live Magnific smoke proves real external bridge metadata after technical PASS.
- [ ] SP02-A11 Owner-authorized PixelLab smoke, when `PIXELLAB_SECRET` is available, proves exact 16x16 direct API path after technical PASS.

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

Do not begin SP03, SP04 or M11. Do not spend provider credits. First execute **PAG-SP02-C002**, publish the builder log, and obtain independent ChatGPT strict audit. Only a technical PASS may authorize a real owner-approved smoke generation and later downstream work.
