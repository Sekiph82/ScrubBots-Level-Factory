# SB-CP00-003-C001-R01 — Current Payload Authority — Audit Criteria

## PASS rule

PASS only if the declarative payload validator accepts real current production LevelData/supply payload representation, enforces current structural safety, preserves all prior fail-closed security behavior, and the downstream CP007..009 chain is revalidated.

## A. LevelData V1 authority

Require:
- integer palette-index cells, excluding bool;
- exactly width × height cells;
- every index in 0..palette_size-1;
- width and height each within locked production envelope 20..59;
- real current Scrubbots production LevelData fixture accepted;
- string-color cell fixtures no longer masquerade as current LevelData.

## B. Supply-plan V1 authority

Require:
- exact `scrubbots.level_supply_plan.v1` / version 1;
- columnCount 3..5 and exact columns length;
- non-empty columns;
- visiblePreviewDepth exactly 3;
- positive integer `maxRobotsPerBatch`;
- every batch robot count integer in 1..maxRobotsPerBatch;
- globally unique non-empty batch IDs;
- canonical C01..C16 color IDs;
- current production supply fixture accepted;
- do not invent an intendedColumnClicks index-base/range rule that current loader does not define.

## C. Descriptor/digest/security preservation

Retain:
- strict UTF-8 JSON;
- duplicate-key rejection;
- non-finite rejection;
- deterministic resource bounds;
- exact byte SHA-256 binding;
- descriptor/content family/identity/projection checks;
- executable/script/plugin/native/resource smuggling rejection;
- no payload execution/import/I/O/network/provider/runtime mutation.

## D. Real authority evidence

Focused tests must use pinned real current Scrubbots LevelData + supply-plan evidence, or exact byte fixtures with repository path/authority SHA/digests recorded.

Task-local synthetic fixtures alone are insufficient.

## E. Downstream remediation compatibility

Update CP007/CP008 positive fixtures/tests only as necessary to use the corrected current LevelData representation.

Do not change their product semantics.

Require cumulative focused regression for SB-CP00-003..009 plus SB-CP00-001/002 and governance.

## F. Full regression

Require:
- focused R01 tests PASS;
- CP003 original tests PASS;
- CP004..009 cumulative tests PASS;
- CP001/002/R01 tests PASS;
- governance/tracker PASS;
- full pytest PASS except truthful pre-capability skips;
- compileall PASS;
- git diff --check PASS.

Codex must not edit root `TASKS.md` or `.hiveai/audits/**`.
