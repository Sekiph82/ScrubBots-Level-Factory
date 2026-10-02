# MAINT-ZIP-CORE-V02-C001-R02 — Final Cutover Audit Criteria

Parent audit:
`.hiveai/audits/MAINT-ZIP-CORE-V02-C001-R01_PRODUCT_SHELL_CLOSURE_STRICT_AUDIT.md`

Parent verdict:
`CHANGES_REQUIRED`

## PASS rule

PASS only if the five remaining R01 findings close without changing owner-locked ZIP behavior.

## A. Current request has no requested difficulty

Current production `GenerationRequest`:
- has no `difficulty` field;
- cannot be constructed with EASY/MEDIUM/HARD/VERY_HARD;
- canonical current schema contains no difficulty;
- current CLI/Studio/presets cannot inject one.

Historical v1/v2 reproduction:
- remains possible only through an explicit legacy adapter/type/path;
- never enters new production Generate/Batch semantics.

## B. Current width/height explicit

For new production Generate and new Batch:
- width required;
- height required;
- both exact integers;
- both within current production envelope;
- no seed-based current auto dimension selection.

Historical reproduction keeps exact recorded behavior.

## C. Legacy solver/difficulty decommissioned as production authority

Retained old M03/M04 modules may remain only for:
- historical artifact reproduction;
- research/evidence modules that explicitly need them.

Required:
- no package-root first-class production exports for retired solver/difficulty authorities;
- current CLI/Studio/ZIP path cannot import/call them as solve/difficulty authority;
- retained files clearly marked non-production/legacy;
- static regression guard proves production path uses ZIP supply/solve/difficulty only.

## D. Real game catalog validation before publication

Before any CampaignBuilder-approved production batch publish:
- stage proposed level/supply/metadata/preview + proposed catalog safely;
- run current Scrubbots `LevelCatalog` validation against the proposed content;
- run current `DifficultyV1CatalogCheck`;
- require both PASS;
- temporary validation artifacts are cleaned;
- validation failure => zero production writes.

Tests use temporary game fixtures only.

## E. Release Pool / CampaignBuilder contiguous batch placement

`OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01` is authoritative:
- owner ACCEPT performs zero game writes and enters Release Pool only;
- CampaignBuilder assigns exact catalog orders;
- owner APPROVE authorizes publication of the contiguous publishable prefix.

Let:
`next_order = max(existing catalog order) + 1`.

The approved publication orders must equal:
`[next_order, next_order + 1, ..., next_order + M - 1]`.

For every batch member:
- official Difficulty V1 must match the current game DifficultyProgressionV1 target for its exact explicit assigned order;
- current `challengeTolerance.neverForceLabelOutsidePlusMinus` must be consumed fail-closed from runtime authority, with no copied numeric fallback.

Must NOT:
- publish from owner ACCEPT;
- scan forward to a later compatible order;
- skip to order next+2/next+N while an earlier order is absent;
- publish a non-contiguous subset;
- create catalog gaps;
- renumber existing immutable content;
- invent a new cadence.

If any batch member, exact-order target, proposed-catalog validation, or batch-contiguity check fails:
- disposition is fail-closed;
- the entire batch performs zero production writes / rolls back;
- owner review, Release Pool, and CampaignBuilder evidence remain preserved.

This preserves GameplayLaunchResolver frontier continuity.

## F. Retained R01 PASS contracts

Do not change:
- 300 candidates;
- original + max 3 mutations;
- screening 3000;
- viability 3000;
- real-solver game default;
- scorer weights;
- mean-batch seed ranges;
- ZIP automatic internal search band;
- screening ranking-only;
- game solve/replay + SolutionVerifier;
- no ProductionGameplayHost gate;
- 3/4/5 columns;
- preview depth 3;
- baseline five slots;
- uncapped global batch robots;
- external owner-upload derivation;
- load-check gate;
- Solve/Analyze dynamic capability;
- configured-game publisher;
- background intent behavior.

## G. Regression

Required:
- focused R02 tests;
- current generation CLI tests;
- legacy reproduction tests;
- publisher transaction tests;
- publisher proposed-catalog game validation test;
- progression gap negative test;
- next contiguous slot positive test;
- 3/4/5 live read-only game revalidation retained;
- full pytest green except truthful capability skips;
- compileall PASS;
- Factory Studio headless PASS;
- git diff --check PASS.

Builder must not edit root `TASKS.md` or `.hiveai/audits/**`.


# J. Co-current P2 Route A Release PR

P2 is owner-provided and authorized after P1-M10 PASS/CLOSED.

Canonical P2 prompt:
`.hiveai/prompts/P2_ROUTE_A_RELEASE_PR.md`

Canonical P2 audit criteria:
`.hiveai/audit-criteria/P2_ROUTE_A_RELEASE_PR_AUDIT_CRITERIA.md`

The combined R02 builder cycle is not PASS unless:
- R02 independently satisfies sections A-I of this file; and
- P2 independently satisfies every criterion in the P2 audit-criteria file.

P2 must not weaken, bypass, or replace R02/P1 publication gates.
A real remote push/PR is not required for implementation audit; tests must use a temporary local bare remote. Real Route A execution requires an actual owner-approved current CampaignBuilder plan.
