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

Before any production publish:
- stage proposed level/supply/metadata/preview + proposed catalog safely;
- run current Scrubbots `LevelCatalog` validation against the proposed content;
- run current `DifficultyV1CatalogCheck`;
- require both PASS;
- temporary validation artifacts are cleaned;
- validation failure => zero production writes.

Tests use temporary game fixtures only.

## E. Contiguous difficulty placement

Let:
`next_order = max(existing catalog order) + 1`.

Publication may write the new level only if official Difficulty V1 is compatible with the current game DifficultyProgressionV1 target for exactly `next_order`.

Must NOT:
- skip to order next+2/next+N;
- create catalog gaps;
- renumber existing immutable content;
- invent a new cadence.

If difficulty does not fit:
- disposition is fail-closed `PROGRESSION_SLOT_MISMATCH` or equivalent;
- zero game writes;
- optional future-slot suggestions are advisory only.

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
