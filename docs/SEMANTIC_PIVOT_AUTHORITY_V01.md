# Semantic Pivot Authority V01

Date: 2026-09-11
Status: OWNER-APPROVED

This document resolves the historical procedural-V1 wording and the owner-approved Semantic Pixel Studio conversion.

## Authority order for new work

1. root `TASKS.md` — current project-status tracker and active milestone state
2. Owner decision: `review/m10/M10_OWNER_REVIEW_DECISION.md`
3. Current conversion master plan: `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
4. Owner provider decision: `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
5. Active versioned ChatGPT implementation prompt under `.hiveai/prompts/`
6. Independent strict audits under `.hiveai/audits/`

If provider-specific wording in the conversion master plan conflicts with `MAGNIFIC_PROVIDER_AUTHORITY_V01.md`, the Magnific provider authority wins. Magnific is the primary semantic AI provider while owner credits are available; provider-neutral boundaries remain mandatory.

## Superseded post-M10 assumptions

The following old V1 assumptions must NOT control new implementation after the M10 owner rejection:

- owner-visible art must be produced only by offline procedural MASK/WFC/RULES generation;
- AI/semantic image generation is permanently out of scope;
- M11 handoff may begin before semantic visual acceptance is repaired;
- structural-quality acceptance is equivalent to semantic visual acceptance;
- local ComfyUI is the required/default first semantic provider.

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

Provider generation itself may be non-deterministic where the authorized provider surface does not expose a seed. In that case reproducibility means exact immutable raw-result provenance/import, not a false promise that the external model will regenerate identical bytes.

## SP01 Closure

SP01 — Semantic Contracts & Provider Boundary is **PASS / CLOSED**.

Cycle history:

- `PAG-SP01-C001 — Semantic Contracts & Provider Boundary` -> FAIL, remediated
- `PAG-SP01-C002 — Semantic Provenance Binding & Role Integrity Remediation` -> FAIL, one residual
- `PAG-SP01-C003 — Non-Success Provenance Echo & Mismatch-Test Sensitivity Closure` -> **PASS / CLOSED**

Closing strict audit:

`.hiveai/audits/PAG-SP01-C003_NON_SUCCESS_PROVENANCE_ECHO_AND_MISMATCH_TEST_SENSITIVITY_CLOSURE_STRICT_AUDIT.md`

## Current implementation cycle

`PAG-SP02-C001 — Magnific Job Spec & Result Import Bridge`

Authoritative prompt:

`.hiveai/prompts/PAG-SP02-C001_MAGNIFIC_JOB_SPEC_AND_RESULT_IMPORT_BRIDGE_PROMPT.md`

SP02 is now authorized.

The SP02 local code boundary prepares canonical jobs and imports owner-authorized Magnific results. It must not scrape the Magnific website or use undocumented/private endpoints. The first real Magnific smoke generation is reserved for owner-authorized independent audit/orchestration after Codex publishes the bridge implementation.

## Downstream gates

SP03 normalization remains blocked until SP02 receives independent technical acceptance.

SP04 model/workflow qualification remains separate from SP02 connectivity/bridge proof.

M11 remains blocked until a semantic generation path produces an owner-accepted replacement visual review pack.
