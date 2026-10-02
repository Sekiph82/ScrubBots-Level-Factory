# MAINT-ZIP-CORE-V02-C001-R02 — Final Cutover — Independent Strict Audit

Date: 2026-10-02
Auditor: ChatGPT
Verdict: **PASS / CLOSED**

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Builder log:
`.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-R02_FINAL_CUTOVER_CODEX_LOG.md`

Implementation commit:
`5f4e30a6929d89ae6aa3545304c062122cf244bf`

Parent audit:
`.hiveai/audits/MAINT-ZIP-CORE-V02-C001-R01_PRODUCT_SHELL_CLOSURE_STRICT_AUDIT.md`

Audit criteria:
`.hiveai/audit-criteria/MAINT-ZIP-CORE-V02-C001-R02_FINAL_CUTOVER_AUDIT_CRITERIA.md`

## Executive result

The five remaining R01 cutover findings are closed without changing owner-locked ZIP behavior.

## A. Current request is difficulty-free — PASS

Current `GenerationRequest` is a distinct current-production type with:
- explicit `seed`;
- explicit integer `width`;
- explicit integer `height`;
- no `difficulty` field;
- canonical v3/current serialization with no requested difficulty.

Historical requested-difficulty semantics remain behind the explicit `LegacyGenerationRequest` path.

Current Studio runtime fixtures/presets and current CLI/batch paths were migrated away from requested difficulty.

## B. Explicit width/height — PASS

Current Generate and Batch semantics require explicit dimensions and use the current production dimension contract. The current request path does not seed-select dimensions.

Historical reproduction retains the legacy adapter behavior separately.

## C. Retired solver/difficulty production authority removed — PASS

The package root no longer exposes the retired M03/M04 solver/difficulty authority classes as first-class production exports.

Retained historical/research modules are marked `LEGACY_NON_PRODUCTION`.

A static AST regression guard verifies that the current CLI, Studio, and supply-pipeline production paths do not import the retired authority modules.

## D. Real proposed-catalog validation — PASS

`publish_batch()` now stages the complete proposed batch in an isolated temporary project before live production writes and runs current Scrubbots authority:
- `LevelCatalog.load_manifest()`;
- `LevelCatalog.validate_all()`;
- `DifficultyV1CatalogCheck.validate_catalog()`.

The stage requires explicit `FACTORY_PROPOSED_CATALOG_PASS`; timeout/nonzero/rejection raises before production publication.

## E. Contiguous CampaignBuilder placement — PASS

The batch publisher:
- reads current catalog orders;
- requires explicit orders to begin at exactly `max(existing order)+1`;
- requires the full batch to remain contiguous;
- forbids scan-forward/gaps;
- preserves existing catalog entries;
- consumes current `challengeTolerance.neverForceLabelOutsidePlusMinus` through fail-closed `challenge_tolerance()`, with no copied numeric fallback.

This is consistent with the owner Release Pool / CampaignBuilder contract:
- ACCEPT => Release Pool only;
- CampaignBuilder => exact next contiguous orders;
- APPROVE => publication authorization.

## Regression evidence

Builder evidence:
- focused R02/P2/current-authority set: **119 passed**;
- focused recovery set: **39 passed**;
- Factory Studio committed runtime suite: PASS;
- Factory Studio action integration suite: PASS;
- compileall: PASS;
- git diff --check: PASS;
- full repository run before tracker repair: **1163 passed, 3 skipped, 2 failed**.

The two full-suite failures were not product/R02 failures. Both were ChatGPT-owned tracker inconsistencies introduced when P2 was added:
1. live denominator declared 246 while 247 rows existed;
2. `Current Task` contained two IDs joined by `+`, violating the governance parser contract.

ChatGPT repaired those tracker-only failures in commit:
`3f35678c48a04120f8eb839a069ea00d0946805e`.

Independent parser verification after the repair:
- parsed task rows: 247;
- unique task IDs: 247;
- declared unified denominator: 247;
- Current Task identity parses as `MAINT-ZIP-CORE-V02-C001-R02`.

No R02 product code was changed by that tracker repair.

## Final disposition

`MAINT-ZIP-CORE-V02-C001-R02 = PASS / CLOSED`

`MAINT-ZIP-CORE-V02-C001 = PASS / CLOSED`

The ZIP final-cutover workstream is closed. Co-current P2 Route A is audited independently and does not inherit this PASS.
