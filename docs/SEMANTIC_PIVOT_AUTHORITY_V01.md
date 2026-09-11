# Semantic Pivot Authority V01

Date: 2026-09-11
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

Approved SP02 providers are now:

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

PixelLab does expose an integer generation seed in the inspected official SDK. ScrubBots therefore requires deterministic request-to-PixelLab-seed mapping and recorded provider provenance, while still avoiding a false promise of permanent byte-identical cloud regeneration across future service/model revisions.

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

## Current implementation cycle

`PAG-SP02-C001 — Magnific + PixelLab Provider Bridges & Result Ingestion`

Authoritative prompt:

`.hiveai/prompts/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_PROMPT.md`

The previous Magnific-only SP02 prompt is superseded and must not be executed.

SP02 is authorized.

SP02 must implement:

- Magnific canonical external job-spec/result-import bridge;
- PixelLab official direct API/SDK provider path;
- explicit provider selection;
- secret-safe PixelLab configuration;
- exact provider/request/result provenance;
- mocked/offline implementation tests;
- no semantic image normalization yet.

A real Magnific smoke generation may be run later through the connected owner-authorized Magnific integration.

A real PixelLab smoke generation requires owner-provided `PIXELLAB_SECRET` and explicit live-run authorization. Codex must not spend provider credits by default.

## Downstream gates

SP03 normalization remains blocked until SP02 receives independent technical acceptance.

SP04 is now **Semantic Provider / Model / Workflow Qualification** and must compare Magnific and PixelLab where access/cost permits.

M11 remains blocked until a semantic generation path produces an owner-accepted replacement visual review pack.
