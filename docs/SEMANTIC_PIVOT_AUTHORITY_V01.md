# Semantic Pivot Authority V01

Date: 2026-09-13
Status: OWNER-APPROVED

This document resolves the historical procedural-V1 wording and the owner-approved Semantic Pixel Studio conversion.

## Authority order for new work

1. root `TASKS.md` — current project-status tracker and active milestone state
2. Owner decision: `review/m10/M10_OWNER_REVIEW_DECISION.md`
3. Current conversion master plan: `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
4. Current provider authority: `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`
5. Magnific-specific authority: `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
6. Active versioned ChatGPT implementation prompt under `.hiveai/prompts/`
7. Independent strict audits under `.hiveai/audits/`

`SEMANTIC_PROVIDER_AUTHORITY_V02.md` supersedes provider-selection wording that implied Magnific was the only authorized semantic provider.

Approved SP02 providers are:

- `MAGNIFIC` — owner-authorized external orchestration;
- `PIXELLAB` — official PixelLab Developer API / Python SDK direct provider.

Provider-neutral SP01 boundaries remain mandatory.

## Superseded post-M10 assumptions

The following old V1 assumptions must NOT control new implementation after the M10 owner rejection:

- owner-visible art must be produced only by offline procedural MASK/WFC/RULES generation;
- AI/semantic image generation is permanently out of scope;
- M11 handoff may begin before semantic visual acceptance is repaired;
- structural-quality acceptance is equivalent to semantic visual acceptance;
- local ComfyUI is the required/default first semantic provider;
- Magnific is the only authorized semantic provider.

## Preserved assumptions

The semantic pivot does NOT supersede accepted technical contracts unless the owner explicitly changes them:

- LEVEL_ART difficulty dimensions;
- rectangular-board legality;
- C01..C16 LevelData palette legality;
- difficulty used-color bands;
- deterministic project provenance requirements;
- M07 structural quality;
- M08 export;
- M09 batch/reproduce;
- M10 performance/property evidence;
- runtime separation from the ScrubBots mobile game.

Provider generation itself may be non-deterministic where an authorized provider surface does not expose a seed. In that case reproducibility means exact immutable raw-result provenance/import, not a false promise that the external model will regenerate identical bytes.

PixelLab exposes an integer generation seed in the inspected official SDK. ScrubBots therefore requires deterministic request-to-PixelLab-seed mapping and recorded provider provenance, while still avoiding a false promise of permanent byte-identical cloud regeneration across future service/model revisions.

Raw provider raster dimensions are separate from requested logical artwork dimensions. Allowing a large raw provider raster does not change LEVEL_ART board legality or ASSET_ART requested-dimension policy. SP03 remains the only normalization stage.

## Network boundary after semantic pivot

The historical M00-M10 procedural pipeline remains offline-safe.

Post-M10 provider execution is an explicit scoped exception:

- Magnific local Factory bridge remains non-networked and uses owner-authorized external orchestration.
- PixelLab direct network access is allowed only inside the explicit `PIXELLAB` provider execution operation using the official API/SDK.

Package import, job preparation, procedural generation, normalization, validation and export must remain network-free unless an explicit network provider is deliberately executed.

## SP01 Closure

SP01 — Semantic Contracts & Provider Boundary is **PASS / CLOSED**.

Cycle history:

- `PAG-SP01-C001 — Semantic Contracts & Provider Boundary` -> FAIL, remediated
- `PAG-SP01-C002 — Semantic Provenance Binding & Role Integrity Remediation` -> FAIL, one residual
- `PAG-SP01-C003 — Non-Success Provenance Echo & Mismatch-Test Sensitivity Closure` -> **PASS / CLOSED**

Closing strict audit:

`.hiveai/audits/PAG-SP01-C003_NON_SUCCESS_PROVENANCE_ECHO_AND_MISMATCH_TEST_SENSITIVITY_CLOSURE_STRICT_AUDIT.md`

## SP02 Cycle History

### C001

`PAG-SP02-C001 — Magnific + PixelLab Provider Bridges & Result Ingestion` -> **FAIL / REMEDIATED BY C002**

Strict audit:

`.hiveai/audits/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_STRICT_AUDIT.md`

C001 established the useful multi-provider bridge foundation but failed on Magnific raw-raster handling, aspect/capability truth, result identity separation, model binding, BitForge style strength, and smoke fixture readiness.

### C002

`PAG-SP02-C002 — Provider Contract Fidelity, Result Identity & Smoke Readiness Remediation` -> **FAIL / BOUNDED C003 REQUIRED**

Strict audit:

`.hiveai/audits/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_STRICT_AUDIT.md`

C002 successfully closed:

- Magnific logical-target vs raw-raster equality bug up to the current raw-candidate ceiling;
- prompt-only Magnific native capability overclaim for negative prompt/transparency/view/isometric;
- success result audit/cost metadata contamination;
- Magnific request/job/actual-model drift;
- BitForge `style_strength` omission;
- stale Magnific smoke model slug;
- legacy hidden-tracker authority misuse.

C002 residuals requiring C003:

1. raw `SemanticImageCandidate` returned-raster dimensions are still capped at 1024 even though authorized providers can return 2k/4k and the Magnific manifest accepts up to 8192;
2. Magnific per-model capability snapshots are inaccurate/fail-open and do not truthfully constrain aspect ratios/reference roles/resolution/quality;
3. provider result-manifest identity still includes mutable free-text `failure_reason`;
4. exact request <-> job <-> candidate/manifest coordinated provenance binding is incomplete;
5. Magnific failure `actual_model_slug` semantics should not fabricate an observed model when execution may not have occurred.

## Current implementation cycle

`PAG-SP02-C003 — Model Capability Snapshot, Raw Raster Ceiling & Cross-Provenance Closure`

Authoritative prompt:

`.hiveai/prompts/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_PROMPT.md`

C003 must preserve:

- explicit provider selection;
- no provider/model fallback;
- Magnific external-orchestration boundary;
- PixelLab official direct API/SDK provider path;
- secret-safe PixelLab configuration;
- PixelLab exact-size and deterministic seed mapping;
- BitForge style-strength mapping;
- accepted M00-M10 foundation;
- SP01 architecture and logical dimension contracts;
- raw provider art remaining unnormalized until SP03;
- no paid live generation from Codex.

C003 is a bounded contract closure. It is not an architecture restart.

A real provider smoke is deferred until independent audit accepts C003 and SP02 as technically smoke-ready.

A real PixelLab smoke additionally requires owner-provided `PIXELLAB_SECRET` and explicit live-run authorization.

## Downstream gates

SP03 normalization remains blocked until SP02 receives independent technical acceptance.

SP04 — Semantic Provider / Model / Workflow Qualification remains blocked until provider bridges are accepted.

M11 remains blocked until a semantic generation path produces an owner-accepted replacement visual review pack.
