# MAINT-ZIP-CORE-V02-C001-R01 — Product Shell Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Parent audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/MAINT-ZIP-CORE-V02-C001-LF_ONLY_STRICT_AUDIT.md

R01 criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/MAINT-ZIP-CORE-V02-C001-R01_PRODUCT_SHELL_CLOSURE_AUDIT_CRITERIA.md

Owner V02:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V02.md

Game 3/4/5 task audit:
https://github.com/Sekiph82/Scrubbots/blob/main/coordination/sessions/MAINT-SUPPLY-COLUMNS-C001/CHATGPT_AUDIT_V01.md

## Scope

Modify ONLY:
`Sekiph82/ScrubBots-Level-Factory`.

Do NOT edit Scrubbots source.

You may use the owner's canonical local Scrubbots checkout READ-ONLY for:
- solver;
- replay;
- Difficulty V1;
- shipping load-check;
- read-only catalog/progression authority inspection.

Runtime publisher code may target a configured Scrubbots project when the owner uses Level Factory. During implementation tests, publication MUST target only an isolated temporary game-project fixture/copy under `%TEMP%`, never the owner's live checkout.

The inspected EXE remains out of scope.

## Mandatory sync preflight

1. Work only in:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repository and branch `main`.
3. Fetch/prune.
4. Inspect HEAD/origin/status/stashes/worktrees/ahead-behind.
5. Fast-forward when safe.
6. Preserve owner material non-destructively.
7. No reset/rebase/stash/clean/force/discard.
8. No new Desktop clone/worktree/branch.
9. Start only after safe sync.

## DO NOT TOUCH ZIP TUNING

Preserve exactly:
- candidates=300;
- original + max 3 mutations;
- screening=3000;
- viability=3000;
- game-default real solver budget;
- SupplyScorer weights;
- mean-batch seed ranges;
- internal image-complexity/search-band heuristic;
- ScreeningSimulator ranking-only;
- solve/replay/SolutionVerifier authority;
- no global batch cap.

No mandatory ProductionGameplayHost gate.

# R01.1 — Remove requested difficulty from CURRENT artwork generation

The current production artwork request must become difficulty-free.

The existing implementation is incomplete because:
- `GenerationRequest` still requires difficulty;
- CLI generate/batch still require `--difficulty`;
- gateway still injects `--difficulty EASY`;
- dimensions/palette/quality still accept difficulty as production input.

Implement a new current request schema/version that does NOT contain requested difficulty.

Current production request inputs must include:
- width;
- height;
- seed;
- generator mode;
- optional style/theme;
- optional explicit palette subset;
- generator options;
- explicit background intent.

For current production generation:
- width and height are explicit and validated against the current production envelope;
- do not infer dimensions from a difficulty class;
- palette subset validation is based only on canonical C01..C16 and the current used-color envelope;
- if palette subset is omitted, use a deterministic difficulty-independent palette-selection policy based on the existing stable seed selection machinery;
- do not create a hidden MEDIUM/EASY proxy;
- quality validation must not classify artwork from requested difficulty.

CLI:
- remove `--difficulty` from CURRENT `generate` and `batch`;
- update help/contracts/tests.

FactoryCoreGateway:
- remove `--difficulty EASY` injection completely.

Studio:
- no Difficulty selector/readout for current artwork generation.

Legacy:
- old metadata/reproduction that already stores historical difficulty may remain reproducible through an explicit legacy schema adapter;
- legacy field is inert for NEW production generation;
- do not rewrite historical artifacts.

# R01.2 — Background intent

Add one explicit current artwork setting:
- `BACKGROUND`
- `TRANSPARENT`

Expose it in:
- Studio target controls;
- current generation request;
- CLI;
- presets;
- metadata/provenance.

Behavior:
- BACKGROUND => generator creates/fills intended background during artwork creation;
- TRANSPARENT => alpha remains transparent.

Never fill transparency later merely to pass game validation.

If a specific legacy generator cannot produce transparent art:
- return truthful unsupported/unavailable for that mode;
- do not silently output opaque background.

Generated transparent artwork may enter Library/review as artwork but ZIP production/publish must be unavailable until it has a legitimate full-canvas artwork variant.

# R01.3 — Make Solve/Analyze real capabilities

Remove hard-coded permanent Solve/Analyze UNAVAILABLE.

FactoryCoreGateway + Studio actions:
- Solve routes the selected canonical source/candidate through the SAME ZIP production route;
- Analyze reads/executes the SAME run and surfaces official Difficulty V1;
- no separate legacy solver/difficulty path.

Capability probe should report AVAILABLE only when:
- Python Factory Core available;
- canonical ZIP modules available;
- canonical read-only game checkout available;
- Godot available.

Otherwise return truthful UNAVAILABLE reason.

# R01.4 — Make external upload reviewable

For an exact valid OWNER_UPLOAD artwork:
- never mutate source bytes;
- create a derived canonical candidate bundle with immutable source lineage;
- candidate has exact cells/palette/dimensions/artwork digest;
- run candidate through the same ZIP path;
- owner review accepts candidate_id;
- ACCEPT can auto-publish if all production gates pass.

Do not create a second upload solver path.

Transparent owner upload:
- preserve;
- may produce asset/review candidate;
- must remain non-publishable while shipping LevelData cannot represent transparency.

# R01.5 — Execute shipping load-check before publish eligibility

After ZIP solve/replay/Difficulty V1/export:
- run the exact emitted level + supply through current game shipping load-check;
- bind exact file digests and selected 3/4/5 column count;
- record PASS/FAIL in pipeline evidence.

A candidate may be solver READY but publication eligibility must be false until load-check passes.

Do not convert load-check into a second gameplay solver.

# R01.6 — Actual auto-publisher to configured Scrubbots project

Replace the current LF-only “published” copy as the final publish destination.

It may remain as staging/evidence, but owner ACCEPT on a publication-eligible candidate must automatically publish to the configured game project.

Implement a bounded Level Factory publisher, e.g.:
`supply_pipeline/game_publisher.py`.

Discover target game root from explicit configuration / `SCRUBBOTS_PROJECT`, using the same authority boundary as GameRules.

Before mutation:
- validate target is a Scrubbots project;
- read current production catalog;
- ensure immutable level ID does not collide with different content;
- prepare all outputs in a temporary transaction area;
- validate level/supply/candidate metadata;
- compute catalog change;
- do not mutate if any prerequisite fails.

Publish required artifacts to current game contract:
- `data/levels/<stable-id>.json`;
- `data/levels/supply/<stable-id>_supply_v1.json`;
- `data/levels/metadata/<stable-id>.metadata.json`;
- `assets/art/levels/previews/<stable-id>.png`;
- `data/levels/catalog/production_catalog_v1.json`.

Use stable immutable internal ID; do not require a `level_###` filename identity.

Write transactionally:
- no partial publish;
- atomic file replacements where possible;
- rollback staged mutation on failure;
- never overwrite a different existing immutable level silently.

No second Publish confirmation:
`owner ACCEPT -> auto publish`.

Owner REJECT:
zero game writes.

IMPLEMENTATION TESTS:
- use a `%TEMP%` game fixture/copy only;
- never write to `C:\Users\sekip\Desktop\ScrubBots` during builder tests.

# R01.7 — Correct progression placement

Delete the simplistic production rule:
`difficulty_score ascending -> level_id`
as the game placement authority.

Read current game authority:
- `data/config/level_progression_v1.json`;
- current DifficultyProgressionV1 semantics;
- `data/levels/catalog/production_catalog_v1.json`.

Use official Difficulty V1 class + Challenge Score to compute a deterministic catalog placement compatible with the current cadence/target challenge model.

Requirements:
- tie-break documented;
- immutable ID stable;
- no destructive ID renaming;
- no silent corruption of existing progression/save numbering;
- if current catalog state cannot accept a new difficulty-derived position safely, fail closed with a specific progression-placement error.

Do not invent a new cadence.

Validate proposed catalog in the temp game fixture using current game catalog validation before commit.

# R01.8 — Retire old production solver/difficulty brain

Dependency-scan the legacy modules named in the parent audit.

For every legacy M03/M04 solver/difficulty module/test:

A. If used ONLY by retired production solver/difficulty:
- delete it;
- delete/update its dedicated active tests;
- remove active imports/docs/UI references.

B. If required strictly for legacy artifact reproduction or historical evidence:
- move/mark it explicitly legacy/non-production where practical;
- document exact retained consumer;
- ensure current Studio/CLI production path cannot import/call it as solver/difficulty authority.

No current product state may say “M03/M04 pending”.

The ZIP-derived route is the single production supply/solve/difficulty brain.

# R01.9 — Full test migration

The prior 15 full-suite failures are not accepted closure.

Update/remove tests that assert superseded:
- Difficulty UI;
- requested-difficulty current request;
- M03/M04 pending copy;
- retired competing production path.

Do NOT simply skip them.

Add tests for:
- difficulty-free current generation request;
- CLI generate/batch reject `--difficulty`;
- gateway never injects EASY;
- explicit width/height current generation;
- difficulty-independent palette selection;
- BACKGROUND vs TRANSPARENT intent;
- Solve/Analyze dynamic capability;
- external upload -> derived candidate -> ZIP -> review;
- load-check required before publish;
- ACCEPT auto-publish to temp game fixture;
- REJECT zero writes;
- transactional publish rollback;
- catalog collision rejection;
- progression policy uses current game cadence/targets, not global score sort;
- stable immutable ID;
- legacy reproduction remains possible without influencing new generation.

Final full pytest must be green except truthful environment capability skips.

# R01.10 — Live 3/4/5 revalidation

The separate Scrubbots task is now PASS/CLOSED.

Against the current canonical game checkout READ-ONLY, run:
- 3-column ZIP full solve/replay/export/load-check;
- 4-column ZIP full solve/replay/export/load-check;
- 5-column ZIP full solve/replay/export/load-check.

Require:
- SOLVED;
- replay WIN;
- official Difficulty V1;
- exact conservation;
- preview depth 3;
- baseline slot_count 5;
- selected column count preserved.

Also retain >30 batch compatibility evidence.

No Scrubbots source writes.

# Required final gates

- focused R01 tests green;
- all adapted owner ZIP tests green;
- full pytest green except truthful capability skips;
- compileall green;
- Factory Studio Godot headless/runtime contract green;
- git diff --check green;
- Level Factory only product source modified;
- root TASKS untouched by builder;
- .hiveai/audits untouched by builder.

## Builder log

Create before product edits:

`.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-R01_PRODUCT_SHELL_CLOSURE_CODEX_LOG.md`

Commit product implementation separately from log publication.

Push Level Factory `main`, fetch again, prove local/origin 0/0.

STOP for independent ChatGPT audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-R01_PRODUCT_SHELL_CLOSURE_CODEX_LOG.md
