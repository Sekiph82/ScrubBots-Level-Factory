# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical H!veAI control-plane trackers are not current authority. Detailed M00-M10 evidence and previous cycle detail remain in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion**
- Current Sprint: **SP02 Live Provider Smoke**
- Current Task: **Owner-authorized Magnific smoke using the accepted `recraft-v4-1` wizard fixture**
- Current Task Status: **TECHNICAL_PASS / READY_FOR_OWNER_SMOKE**
- Required Actor: **CHATGPT + OWNER-AUTHORIZED MAGNIFIC CONNECTION**
- Closing Code Cycle: `PAG-SP02-C003` → **PASS / CLOSED**
- Closing Strict Audit: `.hiveai/audits/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_STRICT_AUDIT.md`
- Next Task/Action: Run exactly one controlled Magnific smoke candidate, capture provider/model/creation/result provenance, then record smoke disposition.
- Blockers/Waits: **SP04 qualification and M11 remain blocked** until real provider evidence exists. SP03 normalization implementation should begin only after the first raw provider smoke artifact is captured so normalization tests can include real evidence.
- Approved Semantic Providers: **MAGNIFIC**, **PIXELLAB**
- Provider Selection: **explicit per request/job; no silent provider or model fallback**
- Magnific Mode: owner-authorized external orchestration while owner credits are available.
- PixelLab Mode: official Developer API / Python SDK direct provider, opt-in network execution only.
- Provider Architecture: **provider-neutral**; providers may later be replaced without rewriting Factory core.
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Current Product Goal

Convert the accepted deterministic Pixel Art Generator foundation into a **PixelLab-like Semantic Pixel Studio** that generates recognizable small pixel art from text/reference/style inputs, then routes raw provider artwork through deterministic ScrubBots normalization, validation, provenance, review, batch and export machinery.

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

Raw provider output dimensions are separate from logical requested dimensions. Provider rasters may be much larger, up to the versioned semantic raw-raster bound, but raw provider output cannot become logical artwork until SP03 normalization.

## Provider Rules

### MAGNIFIC

- approved semantic provider while owner credits are available;
- local Factory must not scrape/drive Magnific website or use undocumented/private endpoints;
- execution is owner-authorized external orchestration;
- provider seed and exact logical raster size are not claimed where the surfaced provider does not expose them;
- requested logical dimensions and returned provider raster dimensions are separate provenance fields;
- raw provider raster remains raw until SP03 normalization;
- provider capability truth is model-specific;
- deterministic jobs use pinned/versioned model capability snapshots;
- unknown/unpinned model slugs fail closed;
- current smoke model: `recraft-v4-1`, 1:1, count 1, wizard fixture;
- provider/model selection is explicit, never silent fallback.

### PIXELLAB

Official SDK authority: `https://github.com/pixellab-code/pixellab-python`.

- provider id: `PIXELLAB`;
- official package: `pixellab`;
- inspected SDK version baseline: `1.0.8`;
- default API base: `https://api.pixellab.ai/v1`;
- secret from `PIXELLAB_SECRET` only;
- optional base URL from `PIXELLAB_BASE_URL`;
- PixFlux supports exact `image_size`, negative description, outline, shading, detail, view/direction, isometric, no-background, coverage, init image, forced color image and integer seed;
- BitForge additionally exposes style image and `style_strength` plus richer edit/reference inputs;
- direct PixelLab network access is allowed only inside explicit PIXELLAB execution;
- package import, job preparation and historical procedural generation remain network-free;
- secrets never enter source control, canonical identity, manifests or logs.

## Authority Documents

- `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
- `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`
- `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
- `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`
- `review/m10/M10_OWNER_REVIEW_DECISION.md`
- `.hiveai/audits/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_STRICT_AUDIT.md`

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
- [~] **PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion** — code technical PASS, live smoke pending
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

- [x] Record owner rejection of the M10 100-image review pack.
- [x] Preserve rejected pack as negative regression evidence.
- [x] Publish Semantic Pixel Studio conversion plan.
- [x] Approve Magnific as semantic provider while owner credits are available.
- [x] Preserve provider-neutral architecture.
- [x] Authorize PixelLab official Developer API / Python SDK as an additional provider.

---

# PAG-SP01 — Semantic Contracts & Provider Boundary

Final state: `PASS / CLOSED`

Closing cycle: `PAG-SP01-C003 — Non-Success Provenance Echo & Mismatch-Test Sensitivity Closure`

Closing audit: `.hiveai/audits/PAG-SP01-C003_NON_SUCCESS_PROVENANCE_ECHO_AND_MISMATCH_TEST_SENSITIVITY_CLOSURE_STRICT_AUDIT.md`

- [x] `LEVEL_ART` and `ASSET_ART` output classes.
- [x] Immutable/versioned `SemanticGenerationRequest`.
- [x] Content-identified image input descriptors.
- [x] Provider-neutral `SemanticGeneratorProvider` boundary.
- [x] Typed raw `SemanticImageCandidate` success/failure boundary.
- [x] Truthful provider capability schema.
- [x] Deterministic request/result identity rules.
- [x] LEVEL_ART dimensions bound to existing ScrubBots difficulty contracts.
- [x] ASSET_ART independent from LevelData difficulty legality.
- [x] REFERENCE / STYLE / INIT / COLOR_REFERENCE role integrity.
- [x] Exact provider/result provenance binding.
- [x] Provenance-complete non-success candidates.
- [x] Raw semantic candidates blocked from M08 artwork before normalization.

---

# PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion

State: `TECHNICAL_PASS / LIVE_SMOKE_PENDING`

Cycle history:

- `PAG-SP02-C001` → FAIL, bounded remediation opened.
- `PAG-SP02-C002` → FAIL, four production-facing residuals remained.
- `PAG-SP02-C003` → **PASS / CLOSED**.

Closing strict audit:

`.hiveai/audits/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_STRICT_AUDIT.md`

C003 technical closure:

- [x] SP02-C003-001 Raw returned-provider raster validation separated from logical/requested dimensions; 2048/4096/8192 accepted.
- [x] SP02-C003-002 LEVEL_ART and ASSET_ART requested/logical legality preserved.
- [x] SP02-C003-003 Versioned per-model Magnific capability snapshot implemented.
- [x] SP02-C003-004 Exact supported aspect-ratio sets pinned for deliberate Magnific candidate models.
- [x] SP02-C003-005 Model-specific REFERENCE/STYLE role support enforced during job preparation.
- [x] SP02-C003-006 Unknown/unpinned Magnific models fail closed before canonical job creation.
- [x] SP02-C003-007 Explicit Magnific resolution/quality overrides validated against pinned model support.
- [x] SP02-C003-008 `recraft-v4-1` smoke fixture regenerated with exact pinned capability snapshot and no unsupported `21:9`.
- [x] SP02-C003-009 Free-text failure diagnostics removed from Magnific/PixelLab deterministic result-manifest digest identity.
- [x] SP02-C003-010 Magnific request↔job↔manifest coordinated provenance binding closed.
- [x] SP02-C003-011 PixelLab request↔job↔candidate↔manifest coordinated provenance binding closed.
- [x] SP02-C003-012 Magnific failure observed-actual-model provenance is optional/truthful; reported drift fails closed.
- [x] SP02-C003-013 Sensitivity tests added for raw raster bounds, pinned model truth, unknown models, failure identity and coordinated mismatches.
- [x] SP02-C003-014 Accepted C002 PixelLab seed/size/style-strength/secret/isolation behavior preserved.
- [x] SP02-C003-015 Builder reports final 445-test repository regression green; independent auditor replay UNVERIFIED due audit-container DNS.
- [x] SP02-C003-016 No paid provider execution, live PixelLab call or Magnific browser/private endpoint automation occurred.

SP02 technical acceptance:

- [x] SP02-A01 Same semantic request + same explicit provider/model bindings produces byte-identical canonical provider job identity.
- [x] SP02-A02 Raw result is cryptographically/provenance bound to exact request/job/provider/engine/model chain.
- [x] SP02-A03 Audit URL/timestamp/cost/failure prose do not alter deterministic provider-result identity.
- [x] SP02-A04 Magnific can represent normal 2k/4k raw provider raster while retaining logical target dimensions.
- [x] SP02-A05 Magnific capability truth is pinned per selected model; unknown models fail closed.
- [x] SP02-A06 PixelLab retains exact-size provider intent and deterministic request-to-provider-seed mapping.
- [x] SP02-A07 BitForge STYLE retains explicit style-strength semantics.
- [x] SP02-A08 Provider failures remain typed/provenance-complete without fabricated observed execution facts.
- [x] SP02-A09 Raw provider image remains blocked from normalized logical artwork.
- [x] SP02-A10 Historical offline procedural paths remain unaffected.
- [x] SP02-A11 Independent C003 audit marks bridge technically smoke-ready.
- [ ] SP02-A12 Run one owner-authorized live Magnific smoke and record creation/result/import evidence.
- [ ] SP02-A13 Run owner-authorized PixelLab smoke when `PIXELLAB_SECRET` is available in the authorized execution environment.

Non-blocking C003 MINOR:

- [~] Align documentation-only Magnific snapshot observation date (`2026-09-11` code vs `2026-09-12` README) on next docs touch. It is excluded from deterministic identity.

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

No further SP02 Codex remediation is authorized from C003. Do not begin SP04 qualification or M11 yet. First run **one controlled owner-authorized Magnific smoke** using the accepted `recraft-v4-1` wizard fixture and capture provider/result provenance. After that smoke evidence is recorded, SP03 normalization may begin against both synthetic fixtures and the real provider artifact.
