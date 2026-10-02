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

Before the CampaignBuilder-approved live batch publication transaction:

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

# R02.5 — Preserve Release Pool / CampaignBuilder contiguous publication authority

`OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01` supersedes the older ACCEPT-auto-publish behavior.

Required current flow:
1. owner ACCEPT performs zero game writes and enters an otherwise eligible READY level into the Release Pool only;
2. CampaignBuilder assigns Release Pool entries to the next contiguous catalog orders;
3. owner APPROVE authorizes publication of the CampaignBuilder publishable prefix;
4. publication is one all-or-nothing batch transaction.

For the approved batch:

```
next_order = max(existing catalog order) + 1
orders = CampaignBuilder-approved explicit level_number values
require orders == [next_order, next_order + 1, ..., next_order + M - 1]
for each item:
    target = current DifficultyProgressionV1.describe(item.level_number)
    require official Difficulty V1 score/class fits that exact target
validate the complete staged proposed batch through current LevelCatalog
validate the complete staged proposed batch through current DifficultyV1CatalogCheck
only then commit production files + catalog
```

The publisher must consume the current runtime `challengeTolerance.neverForceLabelOutsidePlusMinus` authority and fail closed if it is missing/malformed. Do not retain or introduce a copied numeric tolerance fallback.

Do NOT:
- publish from owner ACCEPT;
- scan forward and silently choose a later compatible order;
- write order next+2 or later while next is absent;
- publish a non-contiguous subset of an approved batch;
- renumber existing orders;
- change immutable IDs;
- change save progression;
- invent a new cadence.

This preserves current Scrubbots `GameplayLaunchResolver` frontier continuity while keeping CampaignBuilder as the catalog-order authority.

If any assigned order, difficulty target, staged catalog validation, or batch-contiguity check fails:
- preserve owner review / Release Pool / CampaignBuilder evidence;
- publication disposition is fail-closed;
- zero production game writes for the whole batch.

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
11. Owner ACCEPT enters Release Pool only and causes zero game writes.
12. An approved batch must start at the exact next catalog order; a later-only compatible candidate cannot be published across a hole.
13. A valid approved batch writes only its exact contiguous CampaignBuilder-assigned orders and preserves all existing catalog entries.
14. Any item/order/validation failure rolls back the whole batch; existing catalog remains contiguous.
15. Owner REJECT still causes zero game writes.
16. Existing R01 external-upload/load-check/Solve/Analyze/3-4-5 tests remain green.

Final gates:
- full pytest green except truthful capability skips;
- compileall PASS;
- Factory Studio headless PASS;
- live read-only 3/4/5 validation retained;
- git diff --check PASS.

# P2 — Route A game-repo PR release workstream (OWNER ADDED AFTER P1 CLOSE)

P1-M10 is now PASS/CLOSED. Execute P2 in the SAME builder cycle as R02 as a separate audited workstream.

Canonical P2 owner prompt:
`.hiveai/prompts/P2_ROUTE_A_RELEASE_PR.md`

P2 strict audit criteria:
`.hiveai/audit-criteria/P2_ROUTE_A_RELEASE_PR_AUDIT_CRITERIA.md`

Tracker:
`SB-CPX-003 — Route A Game-Repo Release PR`.

Execution rules:
- Preserve every R02 contract above.
- P2 implementation may build/test the release-PR capability now because its P1 dependency is closed.
- Do not require a real owner production batch to exist in order to implement/test the capability.
- Tests MUST use a temporary local bare remote and MUST NOT push/open a PR against the real `Sekiph82/Scrubbots` remote.
- A real release branch/PR may be created only when an actual owner-approved, current CampaignBuilder `campaign_plan.json` is explicitly supplied for release execution.
- Never push to game `main`; never force-push; never rewrite game history.
- P2 must reuse P1 explicit contiguous batch orders and the accepted publication transaction rather than reimplement campaign ordering.
- Game verification before commit/push/PR must use current game LevelCatalog, LevelLoader, SupplyPlanLoader, SolvabilitySolver replay/solve, and LevelDifficultyAnalyzerV1 score parity.
- Only the P2 owner allow-list may change in the game checkout; any other diff aborts.
- Studio must warn that the public Scrubbots repo exposes unreleased levels once the release branch is pushed.
- Successful Route A creates a Level Factory `release_receipt.json` and surfaces it in Studio.
- Failure restores the target checkout to the exact preflight state and preserves evidence.

Create the P2 builder log BEFORE P2 product edits:
`.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_CODEX_LOG.md`

Keep R02 and P2 evidence/logs separate. Neither workstream may claim independent acceptance.

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

Return only these two lines:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-R02_FINAL_CUTOVER_CODEX_LOG.md
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_CODEX_LOG.md
