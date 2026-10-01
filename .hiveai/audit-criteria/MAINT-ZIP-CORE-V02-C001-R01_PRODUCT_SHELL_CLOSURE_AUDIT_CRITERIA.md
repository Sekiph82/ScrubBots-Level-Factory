# MAINT-ZIP-CORE-V02-C001-R01 — Product Shell Closure — Audit Criteria

Parent audit:
`.hiveai/audits/MAINT-ZIP-CORE-V02-C001-LF_ONLY_STRICT_AUDIT.md`

Parent verdict:
`CHANGES_REQUIRED`

Game prerequisite:
`Sekiph82/Scrubbots/coordination/sessions/MAINT-SUPPLY-COLUMNS-C001/CHATGPT_AUDIT_V01.md = PASS/CLOSED`

## PASS rule

PASS only if all F01..F10 parent findings are closed while the owner ZIP algorithm remains unchanged except for already-approved explicit 3/4/5 column support.

## A. ZIP core immutability

Do not retune:
- candidates = 300;
- original + max 3 mutations;
- screening budget = 3000;
- viability budget = 3000;
- real solver budget default behavior;
- SupplyScorer weights;
- mean-batch-size seed ranges;
- internal automatic image-complexity/search-band heuristic;
- ScreeningSimulator ranking-only role;
- solve/replay/SolutionVerifier acceptance authority.

No ProductionGameplayHost acceptance gate.

## B. Difficulty-free current artwork request

Current production artwork generation contains no requested difficulty field.

Required:
- no current Studio Difficulty selector;
- no current CLI `--difficulty` for generate/batch;
- no gateway-injected EASY/MEDIUM/HARD/VERY_HARD;
- no current GenerationRequest difficulty field;
- dimension validation uses production envelope, not difficulty bands;
- palette subset validation/selection uses canonical palette + production used-color envelope, not difficulty;
- artwork quality validation is not keyed by requested difficulty.

New production generation must use explicit width/height so no hidden difficulty is needed for size selection.

Legacy artifact reproduction may read historical stored difficulty only through a clearly isolated legacy compatibility path. Historical difficulty must not influence new production generation.

## C. Background intent

Current artwork generation must carry explicit background intent.

Required states:
- BACKGROUND: background is produced/filled during artwork creation;
- TRANSPARENT: alpha is preserved.

No post-hoc silent background fill.

If a chosen generator cannot honor TRANSPARENT, return truthful UNAVAILABLE/unsupported for that generator instead of fabricating a background.

Transparent artwork may exist but is not game-publishable while current LevelData requires full logical cells.

## D. Canonical Solve/Analyze capability

When game checkout + Godot + ZIP bridge are available:
- FactoryCoreGateway Solve = AVAILABLE;
- Analyze = AVAILABLE;
- both execute/inspect the same canonical ZIP run.

When unavailable:
- truthful UNAVAILABLE reason.

No legacy solver/difficulty route.

## E. External upload -> derived reviewable candidate

Exact valid OWNER_UPLOAD source:
- immutable source bytes unchanged;
- derived canonical candidate/bundle created with source provenance;
- candidate enters same ZIP path as generated artwork;
- owner review can ACCEPT/REJECT it;
- ACCEPT can reach publish if production-ready.

Transparent/non-publishable upload remains preserved and cannot be silently filled.

## F. Shipping load-check before publish

The exact exported level + supply plan must pass the current game's shipping loader/load-check before publication is eligible.

Load-check is compatibility validation, not a second solver authority.

Evidence binds:
- level file digest;
- supply file digest;
- selected column count;
- game authority.

## G. Actual configured-game auto publish

Owner ACCEPT on a READY, load-checked canonical candidate automatically publishes to the configured Scrubbots project.

Publisher is implemented in Level Factory source only.

At runtime it must safely write the required content artifacts to the configured game root, including:
- level JSON;
- supply plan;
- preview artwork;
- required metadata;
- production catalog entry/update.

Owner REJECT never publishes.

No second Publish approval.

Publication must be transactional/fail-closed and must not leave a partial catalog/content state.

Builder tests must use an isolated temporary game-project copy/fixture, never the owner's live game checkout.

## H. Progression placement

Placement uses:
- official Difficulty V1 / Challenge Score;
- current game `level_progression_v1.json` / DifficultyProgressionV1 campaign authority;
- current production catalog.

It must NOT be a simple global ascending score sort.

Required:
- deterministic placement policy;
- deterministic tie-break;
- immutable level ID independent of displayed/order position;
- no destructive ID renaming;
- no silent save/progression breakage;
- if safe placement cannot be proven under current game contract, fail closed with a clear progression-placement error rather than inventing a new campaign law.

## I. Legacy production backend retired

Dependency scan must prove the ZIP route is the only production supply/solve/difficulty backend.

Modules/tests used solely by retired M03/M04 production solver/difficulty are removed.

Anything retained for historical/reproduction/evidence purposes must:
- be explicitly documented as legacy/non-production;
- be unreachable from current production Studio/CLI ZIP path.

No current UI copy claims M03/M04 pending production authority.

## J. Full regression green

Final:
- full pytest green except truthful capability skips;
- no stale Difficulty-control/M03/M04 tests failing;
- compileall green;
- Factory Studio headless/runtime contract green;
- git diff check green.

## K. Live current-game validation

Against read-only current `Sekiph82/Scrubbots` main, now containing audited 3/4/5 support:
- 3-column full ZIP solve/replay/export/load-check PASS;
- 4-column full ZIP solve/replay/export/load-check PASS;
- 5-column full ZIP solve/replay/export/load-check PASS;
- preview depth = 3;
- baseline five-slot generation;
- >30 batch compatibility retained.

No Scrubbots source writes from this task.
