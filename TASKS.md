# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical H!veAI control-plane trackers are not current authority. Detailed M00-M10 evidence remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, and published project documents.

## Project Status

- Current Milestone: **PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion**
- Current Sprint: **PAG-SP02-C001**
- Current Task: **Magnific + PixelLab Provider Bridges & Result Ingestion**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX**
- Next Task/Action: Execute the authoritative multi-provider SP02-C001 prompt; implement Magnific external job/result bridge plus PixelLab official direct API/SDK provider; publish tests/log; stop for independent ChatGPT audit.
- Blockers/Waits: SP03+ blocked until SP02 receives independent technical acceptance. M11 remains blocked until the semantic pipeline produces an owner-accepted replacement visual review pack.
- Approved Semantic Providers: **MAGNIFIC**, **PIXELLAB**
- Provider Selection: **explicit per request/job; no silent fallback**
- Magnific Mode: owner-authorized external orchestration while credits are available.
- PixelLab Mode: official Developer API / Python SDK direct provider, opt-in network execution only.
- Provider Architecture: **provider-neutral**; providers may later be replaced without rewriting Factory core.
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Current Product Goal

Convert the accepted deterministic Pixel Art Generator foundation into a **PixelLab-like Semantic Pixel Studio** that can generate recognizable small pixel art from text/reference/style inputs, then route it through existing ScrubBots provenance, validation, review, batch and export machinery.

Target owner-visible flow:

```text
TEXT / REFERENCE / STYLE
          ↓
 EXPLICIT SEMANTIC PROVIDER
   MAGNIFIC | PIXELLAB
          ↓
 recognizable raw pixel-art candidate
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
 M08 export / M09 batch-reproduce / future Level Factory handoff
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

`ASSET_ART` is separate from LevelData and may use explicit sizes such as 16x16, 24x24, 32x32, 48x48, 64x64 and rectangles under its own later asset policy.

## Provider Rules

### MAGNIFIC

- approved semantic provider while owner credits are available;
- local Factory does not scrape/drive Magnific website;
- no undocumented/private endpoint usage;
- execution begins as owner-authorized external orchestration;
- current surfaced integration does not expose exact logical raster size or provider seed;
- raw result must be imported with exact job/provider/image provenance.

### PIXELLAB

Official inspected SDK authority: `https://github.com/pixellab-code/pixellab-python`.

- provider id: `PIXELLAB`;
- official package: `pixellab`;
- inspected SDK version: `1.0.8`;
- default API base: `https://api.pixellab.ai/v1`;
- secret from `PIXELLAB_SECRET` only;
- optional base URL from `PIXELLAB_BASE_URL`;
- official PixFlux generation supports exact `image_size`, negative prompt, outline, shading, detail, view/direction, isometric, transparent/no-background, coverage, init image, color/forced-palette image and integer seed;
- official BitForge additionally exposes style image and richer edit/reference inputs;
- direct PixelLab network access is allowed only inside explicit PIXELLAB provider execution;
- package import, job preparation and historical procedural generation remain network-free;
- secrets never enter source control, canonical JSON, manifests or logs.

## Authority Documents

- `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
- `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`
- `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
- `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`
- `review/m10/M10_OWNER_REVIEW_DECISION.md`

Current authoritative implementation prompt:

`.hiveai/prompts/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_PROMPT.md`

The previous Magnific-only SP02 prompt is **SUPERSEDED** and must not be executed.

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

Closing cycle:

`PAG-SP01-C003 — Non-Success Provenance Echo & Mismatch-Test Sensitivity Closure`

Closing audit:

`.hiveai/audits/PAG-SP01-C003_NON_SUCCESS_PROVENANCE_ECHO_AND_MISMATCH_TEST_SENSITIVITY_CLOSURE_STRICT_AUDIT.md`

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

State: `ACTIVE / READY_FOR_IMPLEMENTATION`

## Sprint PAG-SP02-C001 — Magnific + PixelLab Provider Bridges & Result Ingestion

Authoritative prompt:

`.hiveai/prompts/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_PROMPT.md`

### Shared provider layer

- [ ] SP02-001 Define deterministic explicit provider registry for `MAGNIFIC` and `PIXELLAB`.
- [ ] SP02-002 Reject unknown providers and silent cross-provider fallback.
- [ ] SP02-003 Preserve SP01 exact request/provider/result provenance binding.
- [ ] SP02-004 Keep provider SDK/network imports isolated from Factory core and historical generators.

### Magnific bridge

- [ ] SP02-005 Define stable `MAGNIFIC` provider identity/version/config contract.
- [ ] SP02-006 Define canonical versioned Magnific job spec from `SemanticGenerationRequest`.
- [ ] SP02-007 Require explicit Magnific model slug for canonical provider intent.
- [ ] SP02-008 Deterministically render supported art-direction intent into Magnific prompt/job payload.
- [ ] SP02-009 Deterministically map logical aspect ratio while retaining logical dimensions separately.
- [ ] SP02-010 Define content-hash -> Magnific creation execution bindings.
- [ ] SP02-011 Define Magnific success/failure result manifest.
- [ ] SP02-012 Verify raw bytes SHA-256 and import exact provenance-complete `SemanticImageCandidate`.
- [ ] SP02-013 Keep Magnific browser scraping/private endpoint use forbidden.

### PixelLab direct API bridge

- [ ] SP02-014 Define stable `PIXELLAB` provider identity/version/config contract.
- [ ] SP02-015 Integrate official `pixellab` SDK as an optional/lazy provider dependency; do not vendor SDK source.
- [ ] SP02-016 Read PixelLab secret only from environment and prove secret non-leakage.
- [ ] SP02-017 Define explicit PixelLab engine identity, at least `pixflux`; BitForge may be added only if truthfully mapped/tested.
- [ ] SP02-018 Define canonical versioned PixelLab job spec.
- [ ] SP02-019 Deterministically map ScrubBots int/string seed to PixelLab integer seed without Python `hash()`.
- [ ] SP02-020 Send exact resolved SP01 logical width/height as PixelLab `image_size`.
- [ ] SP02-021 Implement explicit tested SP01 -> PixelLab outline/shading/detail/view/direction/isometric mappings.
- [ ] SP02-022 Support native negative description and no-background where exposed by official API.
- [ ] SP02-023 Support PixFlux INIT and COLOR_REFERENCE bindings only when bytes/hash/role verify exactly.
- [ ] SP02-024 Support BitForge STYLE mapping only if BitForge is actually implemented/tested in C001.
- [ ] SP02-025 Reject generic REFERENCE/unsupported semantic controls where no truthful PixelLab mapping exists.
- [ ] SP02-026 Implement injectable/mockable direct PixelLab SDK execution adapter.
- [ ] SP02-027 Capture PixelLab returned raw image bytes/hash/dimensions and available usage USD without making cost metadata identity.
- [ ] SP02-028 Define PixelLab success/failure result manifest with exact request/job/engine/seed provenance.
- [ ] SP02-029 Scope direct network permission only to deliberate PIXELLAB provider execution.
- [ ] SP02-030 Prove package import/job preparation/historical procedural generation remain offline.

### Smoke fixtures and tests

- [ ] SP02-031 Publish one deterministic 16x16 wizard Magnific smoke fixture without executing it from Codex.
- [ ] SP02-032 Publish one deterministic exact-16x16 PixFlux wizard smoke fixture with fixed seed without executing paid API from Codex.
- [ ] SP02-033 Add mocked/offline Magnific bridge tests.
- [ ] SP02-034 Add mocked/offline PixelLab SDK/API tests.
- [ ] SP02-035 Add provider-secret leak tests.
- [ ] SP02-036 Full SP01 and repository regression suites remain green.

### SP02 acceptance

- [ ] SP02-037 Same semantic request + same provider bindings produces byte-identical canonical provider job spec.
- [ ] SP02-038 Imported/generated raw result is cryptographically/provenance bound to exact request/job/provider/engine/model.
- [ ] SP02-039 Normal provider failure remains provenance-complete and typed for both provider paths.
- [ ] SP02-040 No raw provider image is treated as normalized logical artwork.
- [ ] SP02-041 Historical offline procedural paths remain unaffected.
- [ ] SP02-042 Independent owner-authorized Magnific smoke proves real external bridge metadata.
- [ ] SP02-043 Owner-authorized PixelLab smoke, when `PIXELLAB_SECRET` is available, proves exact 16x16 direct API generation path.

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

Do not begin SP03, SP04 or M11 until SP02-C001 is implemented, independently audited, and its required provider bridge evidence is accepted.
