# MAINT-ZIP-CORE-V02-C001-R02 — Final ZIP Cutover Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Parent audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/MAINT-ZIP-CORE-V02-C001-R01_PRODUCT_SHELL_CLOSURE_STRICT_AUDIT.md

R02 audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/MAINT-ZIP-CORE-V02-C001-R02_FINAL_CUTOVER_AUDIT_CRITERIA.md

Owner V02:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V02.md

Game 3/4/5 compatibility remains independently PASS/CLOSED.

## Scope

Modify ONLY:
`Sekiph82/ScrubBots-Level-Factory`.

Scrubbots is READ-ONLY authority.

Do NOT modify the owner ZIP algorithm/tuning.

Do NOT modify the inspected EXE.

## Mandatory sync preflight

1. Work only in `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
2. Verify repo/branch/main/origin.
3. `git fetch origin --prune`.
4. Inspect HEAD/origin/status/ahead-behind/stashes/worktrees.
5. Fast-forward when safe.
6. Preserve owner material non-destructively.
7. No reset/rebase/stash/clean/force/discard.
8. No new branch/worktree/Desktop clone.
9. Start product edits only after safe sync.

# LOCKED — DO NOT RETUNE

Keep exactly:
- candidates = 300;
- original + max three mutations;
- screening = 3000;
- viability = 3000;
- real solver = game default behavior;
- SupplyScorer weights;
- mean-batch seed ranges;
- internal image-complexity/search band;
- ScreeningSimulator ranking-only;
- game solve/replay + ZIP SolutionVerifier authority;
- no ProductionGameplayHost acceptance gate;
- 3/4/5 columns;
- preview 3;
- baseline five slots;
- no global robot/batch cap.

# R02.1 — Split CURRENT request from LEGACY difficulty request

Current production `GenerationRequest` must no longer contain a `difficulty` field at all.

Refactor so:
- `GenerationRequest` is current schema only;
- current constructor fields are difficulty-free;
- canonical current JSON never contains difficulty;
- current Generate/Batch code cannot pass or consume requested difficulty.

Create an explicit legacy-only compatibility path for historical v1/v2 artifacts, for example:
- `LegacyGenerationRequest`;
- or private `_LegacyGenerationRequest` + adapter.

Legacy adapter may parse stored EASY/MEDIUM/HARD/VERY_HARD solely to reproduce old bytes.

It must not be exported as a current production control.

Update:
- request parser;
- result/bundle reproduction;
- tests;
- package exports.

Do NOT break exact historical reproduction tests.

# R02.2 — Require explicit current dimensions

For current production:
- `GenerationRequest.width` required;
- `GenerationRequest.height` required;
- CLI `generate --width --height` required;
- new `batch` requires width/height when creating a new batch;
- current presets require width/height;
- Studio already supplies both.

Remove current seed-based auto-dimension selection.

Keep legacy dimension selection only inside the legacy reproduction path.

Do not reintroduce requested difficulty.

# R02.3 — Decommission old solver/difficulty public authority

Retain historical modules only where genuinely needed by research/evidence/history.

At minimum remove the retired M03/M04 solver/difficulty stack from the current package-root public production API:
- simulation_boundary
- compact_solver_state
- legal_move_provider
- baseline_search
- visited_memoization
- solver_evidence
- search_policy
- solution_analysis
- solver_budget
- level_metrics
- difficulty_analysis
- canonical_bridge

If other retained experimental/research modules need these:
- import them explicitly from their legacy module paths;
- mark the retained modules with a clear non-production/legacy authority statement;
- do not route current Studio/CLI/ZIP through them.

Add a static contract test that walks current production imports/routes and fails if current:
- CLI;
- Factory Studio bridge;
- `studio_extensions`;
- `supply_pipeline/**`
imports or invokes a retired solver/difficulty authority.

ZIP remains the sole production supply/solve/difficulty backend.

# R02.4 — Proposed catalog validation using CURRENT GAME AUTHORITY

Before live game publication transaction:

1. build/stage exact proposed:
   - level;
   - supply plan;
   - metadata;
   - preview;
   - proposed catalog.
2. validate exact level+supply with existing load-check as already implemented.
3. additionally execute current Scrubbots:
   - `LevelCatalog.load_manifest`;
   - `DifficultyV1CatalogCheck.validate_catalog`;
   against an isolated staged proposed catalog/content view.
4. require PASS.
5. clean all validation staging.
6. only then perform final production file/catalog replacements.

Do not reimplement these catalog rules in Python as the acceptance authority.

A practical allowed method:
- create a temporary validation subtree/project fixture using the configured game root as read-only source;
- or create bounded temporary res:// validation artifacts with guaranteed cleanup;
- invoke Godot headless current game scripts;
- never leave temp files behind.

Tests must use %TEMP% game fixtures and prove:
- invalid square-shell/catalog candidate fails before production write;
- malformed catalog entry fails;
- valid candidate passes.

# R02.5 — Prevent progression gaps

Current publisher must never scan forward and publish to a later empty order.

Algorithm:

```
next_order = max(existing catalog order) + 1
target = current DifficultyProgressionV1.describe(next_order)
if official Difficulty V1 score/class fits target under current owner tolerance:
    eligible order = next_order
else:
    fail closed: PROGRESSION_SLOT_MISMATCH
    zero game writes
```

You may compute later compatible slots as advisory UI/evidence only.

Do NOT:
- write order next+2 or later while next is absent;
- renumber existing orders;
- change immutable IDs;
- change save progression;
- invent a new cadence.

This is required by current Scrubbots `GameplayLaunchResolver`, which resolves the frontier by exact catalog order.

Owner ACCEPT auto-publishes only when every gate, including contiguous progression compatibility, passes.

If mismatch:
- preserve owner ACCEPT evidence in Level Factory;
- publication result = NOT_PUBLISHED / PROGRESSION_SLOT_MISMATCH;
- no game writes.

# R02.6 — Regression

Add focused tests proving:

1. Current `GenerationRequest` rejects/does not expose difficulty.
2. Legacy request adapter reproduces historical v1/v2 metadata.
3. Current Generate requires width + height.
4. Current Batch creation requires width + height.
5. Current presets require dimensions.
6. Current production import guard excludes retired solver/difficulty authorities.
7. Retained legacy modules remain usable only by explicit historical/research consumers.
8. Proposed catalog is validated by current game LevelCatalog.
9. Proposed catalog is validated by DifficultyV1CatalogCheck.
10. Invalid proposed game content causes zero production writes.
11. If next order is 11 and candidate only fits slot 13, publication fails closed and order 13 is NOT written.
12. If candidate fits next order 11, publication writes order 11.
13. Existing catalog remains contiguous.
14. Owner REJECT still zero writes.
15. Existing R01 external-upload/load-check/Solve/Analyze/3-4-5 tests remain green.

Final gates:
- full pytest green except truthful capability skips;
- compileall PASS;
- Factory Studio headless PASS;
- live read-only 3/4/5 validation retained;
- git diff --check PASS.

## Builder governance

Do not edit:
- root `TASKS.md`;
- `.hiveai/audits/**`;
- active prompt/criteria files.

Create before product edits:
`.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-R02_FINAL_CUTOVER_CODEX_LOG.md`

Commit implementation separately from final log publication.

Push Level Factory `main`.
Fetch again.
Prove local HEAD == origin/main and divergence 0/0.

STOP for independent ChatGPT audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-R02_FINAL_CUTOVER_CODEX_LOG.md
