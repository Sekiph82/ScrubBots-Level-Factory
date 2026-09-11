# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical H!veAI control-plane trackers are not current authority. Detailed historic M00-M10 implementation evidence remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, and the published project documents.

## Project Status

- Current Milestone: **PAG-SP02 — Magnific Provider Bridge & Result Ingestion**
- Current Sprint: **PAG-SP02-C001**
- Current Task: **Magnific Job Spec & Result Import Bridge**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX**
- Next Task/Action: Execute the authoritative SP02-C001 prompt, implement the provider-specific job-spec/import bridge without browser scraping or undocumented API use, publish tests/log, then stop for independent ChatGPT audit and owner-authorized Magnific smoke generation.
- Blockers/Waits: SP03+ blocked until SP02 bridge receives independent technical acceptance. M11 remains blocked until the semantic pipeline later produces an owner-accepted replacement visual review pack.
- Primary Semantic Provider: **Magnific** while owner credits are available.
- Provider Architecture: **provider-neutral**; Magnific may be replaced later without rewriting the Factory core.
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Current Product Goal

Convert the accepted deterministic Pixel Art Generator foundation into a **PixelLab-like Semantic Pixel Studio** that can generate recognizable small pixel art from text/reference/style inputs, then route it through the existing ScrubBots validation, provenance, review, batch and export machinery.

Target owner-visible flow:

```text
TEXT / REFERENCE / STYLE
          ↓
   SEMANTIC AI PROVIDER
        (Magnific)
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

The previous 100-image M10 owner pack is **REJECTED 100/100** as semantic artwork. It remains a permanent negative regression set. The failure was semantic recognizability, not board resolution.

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
- deterministic provenance and exact export remain required

`ASSET_ART` is separate from LevelData and may use explicit sizes such as 16x16, 24x24, 32x32, 48x48, 64x64 and rectangles under its own later asset policy.

## Authority Documents

- `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
- `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
- `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`
- `review/m10/M10_OWNER_REVIEW_DECISION.md`

## Milestone Overview

### Historical procedural foundation

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

### Semantic Pixel Studio roadmap

- [x] **PAG-SP00 — Owner Rejection & Semantic Pivot Record**
- [x] **PAG-SP01 — Semantic Contracts & Provider Boundary**
- [~] **PAG-SP02 — Magnific Provider Bridge & Result Ingestion**
- [ ] **PAG-SP03 — Semantic Normalization Pipeline**
- [ ] **PAG-SP04 — Magnific Model / Workflow Qualification**
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
- [x] SP00-004 Select Magnific as primary semantic provider while credits are available.
- [x] SP00-005 Preserve provider-neutral architecture.

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

# PAG-SP02 — Magnific Provider Bridge & Result Ingestion

State: `ACTIVE / READY_FOR_IMPLEMENTATION`

## Sprint PAG-SP02-C001 — Magnific Job Spec & Result Import Bridge

Authoritative prompt:

`.hiveai/prompts/PAG-SP02-C001_MAGNIFIC_JOB_SPEC_AND_RESULT_IMPORT_BRIDGE_PROMPT.md`

- [ ] SP02-001 Define stable `MAGNIFIC` provider identity/version/config contract.
- [ ] SP02-002 Define canonical versioned Magnific job specification derived from `SemanticGenerationRequest`.
- [ ] SP02-003 Require explicit model slug for reproducible provider intent; no silently drifting `auto` default for canonical jobs.
- [ ] SP02-004 Deterministically render semantic controls into the provider prompt/job payload.
- [ ] SP02-005 Map target dimensions to an explicit supported provider aspect ratio while preserving requested logical dimensions separately.
- [ ] SP02-006 Define external execution bindings from content-hash image descriptors to authorized Magnific creation identifiers.
- [ ] SP02-007 Validate exact reference/style binding coverage and reject ambiguous/missing/duplicate bindings.
- [ ] SP02-008 Declare only Magnific capabilities actually exposed by the authorized integration surface.
- [ ] SP02-009 Define versioned Magnific result/import manifest.
- [ ] SP02-010 Import immutable raw image bytes and verify SHA-256 against the manifest.
- [ ] SP02-011 Construct exact `SemanticImageCandidate` success/failure results with full request/provider provenance.
- [ ] SP02-012 Record creation identifier, model slug and available provider metadata without making transient URLs part of canonical identity.
- [ ] SP02-013 Fail closed on request/job/result/model/creation/image-hash mismatch.
- [ ] SP02-014 Keep browser scraping, credential extraction and undocumented private endpoints forbidden.
- [ ] SP02-015 Add mocked/offline bridge tests.
- [ ] SP02-016 Prepare one owner-authorized live Magnific smoke job for independent audit; Codex itself does not spend credits unless explicitly given an authorized execution surface.

### SP02 acceptance

- [ ] SP02-017 Same semantic request + same execution bindings produces byte-identical canonical job spec.
- [ ] SP02-018 Imported raw result is cryptographically bound to the exact request/job/provider/model.
- [ ] SP02-019 A normal provider failure remains provenance-complete and typed.
- [ ] SP02-020 No raw provider image is treated as normalized logical artwork.
- [ ] SP02-021 Full existing regression suite remains green.
- [ ] SP02-022 Independent owner-authorized Magnific smoke generation proves the published bridge metadata can represent a real provider creation.

---

# PAG-SP03 — Semantic Normalization Pipeline

- [ ] SP03-001 Preserve raw provider image bytes/hash immutably.
- [ ] SP03-002 Decode provider image deterministically.
- [ ] SP03-003 Handle transparency/background explicitly.
- [ ] SP03-004 Detect or derive logical-pixel structure without hidden interpolation.
- [ ] SP03-005 Define deterministic crop/pad/nearest-neighbor/segmentation rules.
- [ ] SP03-006 For LEVEL_ART, map colors deterministically to C01..C16.
- [ ] SP03-007 Enforce LEVEL_ART difficulty used-color bands.
- [ ] SP03-008 Define separate ASSET_ART palette policy boundary.
- [ ] SP03-009 Emit immutable normalized logical grid with raw-source provenance.
- [ ] SP03-010 Prove raw source is never overwritten.

---

# PAG-SP04 — Magnific Model / Workflow Qualification

- [ ] SP04-001 Build semantic benchmark labels including wizard, dwarf, elf, robot, fish, sea creature, mushroom, ghost, rocket, tree, skull, potion, crab, alien and simple building/object.
- [ ] SP04-002 Compare multiple available Magnific models/workflows.
- [ ] SP04-003 Measure credit use separately from accepted normalized candidates.
- [ ] SP04-004 Review small-resolution recognizability metadata-blind.
- [ ] SP04-005 Choose default model/workflow only from evidence.
- [ ] SP04-006 Do not treat photorealistic quality as pixel-art acceptance.

---

# PAG-SP05 — LEVEL_ART Semantic Integration

- [ ] SP05-001 Use semantic provider output as owner-visible art source.
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

- [ ] SP07-001 Support multiple reference images.
- [ ] SP07-002 Support explicit style references.
- [ ] SP07-003 Support palette/color references when the chosen provider surface truthfully supports them.
- [ ] SP07-004 Support init-image semantics only when provider behavior is explicit/tested.
- [ ] SP07-005 Preserve source content hashes and execution bindings.
- [ ] SP07-006 Build owner-approved style collections.

---

# PAG-SP08 — Edit / Inpaint

- [ ] SP08-001 Define mask-based edit request lineage.
- [ ] SP08-002 Support selected-region repair/replacement when provider capability exists.
- [ ] SP08-003 Support deterministic recolor/palette remap locally.
- [ ] SP08-004 Re-run normalization and all downstream validation after edits.
- [ ] SP08-005 Preserve parent/child provenance.

---

# PAG-SP09 — Pixel Studio Create / Gallery UI

- [ ] SP09-001 Build local Create panel inspired by PixelLab product controls without copying proprietary implementation.
- [ ] SP09-002 Description and negative-description controls.
- [ ] SP09-003 LEVEL_ART / ASSET_ART selector.
- [ ] SP09-004 Difficulty or explicit logical size controls.
- [ ] SP09-005 Reference/style controls.
- [ ] SP09-006 Seed and candidate-count controls.
- [ ] SP09-007 Outline/shading/detail/view/direction controls.
- [ ] SP09-008 Gallery with raw and normalized previews.
- [ ] SP09-009 ACCEPT / REJECT / edit / reproduce / export actions.
- [ ] SP09-010 Canonical request/manifests remain source of truth, not UI state.

---

# PAG-SP10 — Automated Weekly Semantic Batch

- [ ] SP10-001 Request accepted counts by difficulty/category.
- [ ] SP10-002 Bound Magnific credit/generation budgets explicitly.
- [ ] SP10-003 Separate provider attempts from normalized accepted candidates.
- [ ] SP10-004 Resume/retry without unbounded loops.
- [ ] SP10-005 Duplicate/diversity filtering.
- [ ] SP10-006 Owner review queue.
- [ ] SP10-007 Exact M08/M09 handoff.

---

# PAG-SP11 — ASSET_ART Production

- [ ] SP11-001 Support 16/24/32/48/64 and rectangular logical assets.
- [ ] SP11-002 Characters, enemies, objects, items and icons.
- [ ] SP11-003 Transparent-background workflow.
- [ ] SP11-004 Separate richer asset palette policy from LevelData.
- [ ] SP11-005 Asset-specific export contract.

---

# PAG-SP12 — Direction / Rotation Variants

- [ ] SP12-001 N/NE/E/SE/S/SW/W/NW variants where provider supports them.
- [ ] SP12-002 Identity-preservation review.
- [ ] SP12-003 Consistent palette/style across directions.
- [ ] SP12-004 Sprite-set export.

---

# PAG-SP13 — Animation

- [ ] SP13-001 Define animation provider/request boundary.
- [ ] SP13-002 Text-action generation where available.
- [ ] SP13-003 Skeleton/pose-guided frames where available.
- [ ] SP13-004 Frame identity/palette consistency.
- [ ] SP13-005 Sprite-sheet export.

---

# PAG-SP14 — ScrubBots Level Factory Bridge

- [ ] SP14-001 Reinspect the current `Sekiph82/Scrubbots` Level Factory contract before integration.
- [ ] SP14-002 Consume accepted semantic LEVEL_ART as Factory visual/art input.
- [ ] SP14-003 Preserve width/height and row-major logical cells exactly.
- [ ] SP14-004 Preserve canonical palette IDs exactly.
- [ ] SP14-005 Keep Python/provider runtime out of the mobile game runtime.
- [ ] SP14-006 Integrate with solver/difficulty/human-editor/content-pipeline work instead of duplicating it.
- [ ] SP14-007 Require owner-approved replacement visual pack before final handoff closure.

## Global Execution Rules

1. Only ChatGPT, acting as independent auditor/tracker owner, may mark milestones/tasks accepted/closed.
2. Codex builder logs are claims/evidence, never final acceptance.
3. Work only on the explicitly authorized cycle.
4. Preserve accepted M00-M10 infrastructure unless an owner-approved semantic task explicitly changes a boundary.
5. Never silently reinterpret LEVEL_ART dimensions, C01..C16 palette, used-color bands, or one-logical-pixel-per-cell rules.
6. Provider integrations must fail closed and retain exact request/result provenance.
7. No browser scraping, credential extraction or undocumented private provider endpoints.
8. Magnific credit use must be explicit, visible and bounded.
9. Raw provider images are not normalized logical artwork until SP03.
10. Structural QA does not equal semantic recognizability.
11. Owner-visible semantic art requires explicit owner acceptance before production promotion.
12. M11/mobile-game handoff remains blocked until semantic visual acceptance is repaired.
