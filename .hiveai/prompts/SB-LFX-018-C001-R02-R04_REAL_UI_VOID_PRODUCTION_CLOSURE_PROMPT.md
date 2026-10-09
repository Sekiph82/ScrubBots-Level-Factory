# SB-LFX-018-C001-R02-R04 — Preserve R03, Build Real Three-Screen UI, Fix VOID Authority, Wire Production Publish

Document role: CODEX REMEDIATION / CONTINUATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Parent audit:
`.hiveai/audits/SB-LFX-018-C001-R02-R03_STRICT_REAUDIT_V01.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R04_REAL_UI_VOID_PRODUCTION_CLOSURE_AUDIT_CRITERIA.md`

Owner workflow:
`docs/product/FACTORY_STUDIO_OWNER_WORKFLOW_V04.md`

Bindings:
`docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md`

## CRITICAL — DO NOT THROW AWAY R03

Keep the useful R03 implementation.

Baseline product commit:
`5b975a92532b9df1e781c96cb1de37dbba73aa6e`

Current evidence head at audit:
`8ec602beee3cd867d0092a4806863f6a2fcec347`

Preserve:

- exact PIXEL ART V04 master;
- master geometry/style;
- Alpix adapter;
- CSV SHA job state;
- LIMIT/resume behavior;
- Magnific/PixelLab boundaries;
- READY auto-pool;
- Reject exclude / Accept restore;
- installer/shortcut;
- useful tests.

Before mutation publish/log a concise KEEP / ADAPT / ADD matrix.

No destructive reset/clean/rebase/force.

Never edit root `TASKS.md`.

Never write `.hiveai/audits/**`.

Builder log:
`.hiveai/codex-logs/SB-LFX-018-C001-R02-R04_REAL_UI_VOID_PRODUCTION_CLOSURE_CODEX_LOG.md`

## 1. REMOVE THE SCREENSHOT-APP ARCHITECTURE

The current application still shows a full master image as `MasterCanvas.texture` and overlays transparent buttons.

That is not acceptable as the production architecture.

The approved master images are visual references, not the live application.

Rebuild the three production screens from real Godot Controls while preserving the exact master geometry/style:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

Do not redesign.

Do not add a fourth page.

Do not add explanatory engineering prose.

The master files remain committed as audit/reference authority.

A development-only comparison overlay is allowed only if disabled in normal production runtime.

### Real dynamic data rule

Anything that can change must be a real control/state value, not text baked into the master image.

This includes all counts/statuses/details/lists/thumbnails.

## 2. PIXEL ART SCREEN

Build real controls in the master positions for:

- Single / Batch;
- Prompt;
- Size;
- Provider;
- Generate;
- CSV path/select;
- Run Batch / Resume state;
- Batch Progress;
- artwork variations/thumbnails;
- Artwork Details;
- Quick Actions;
- central Visual Review Canvas.

The center canvas and thumbnails must display actual generated/imported PNGs.

No permanent owl fixture when real data exists.

Provider selector minimum:

- `ALPIX (Claude)`
- `MAGNIFIC`
- `PIXELLAB`

Keep the existing R03 provider/job code.

Do not rewrite the job engine.

## 3. LEVEL FACTORY SCREEN

Build real controls/state in the master positions for:

- Select Artwork;
- selected artwork thumbnails;
- Level Number = Auto by default;
- supply columns 3/4/5;
- Max Robots = Auto/no cap;
- Background;
- Pipeline Steps;
- Run Pipeline;
- central actual PNG preview;
- Level Details;
- Solver Status;
- Replay Result;
- Difficulty V1;
- Supply Plan;
- Solve Again;
- Preview Replay;
- Accept Level;
- Reject;
- Level Variations.

Single/multi/CSV external PNG must use the same canonical pipeline.

## 4. RELEASE POOL SCREEN

Build real canonical projections for:

- READY levels count/list;
- real PNG thumbnails;
- search/filter;
- select/manage/select-all/clear;
- central selected PNG;
- selected-for-release cards;
- Level Details;
- STAGING / PRODUCTION;
- preflight stage statuses;
- Upload Selected;
- Preview Release Manifest.

No baked fixture levels/statuses.

## 5. FIX THE FALSE VOID BLOCKER

The previous builder used a shallow TEMP ScrubBots clone and then:

`git merge-base --is-ancestor 7d0d148... HEAD`

The ancestor object was not available locally, so the capability incorrectly reported that current game main lacked VOID.

Independent GitHub truth:

Current game main at the R03 run was:
`44c53a6da0aea1172b1f900c095b7bf20852a541`

and it DOES contain audited VOID commit:
`7d0d148b8609ec04852fdee02f6b8ef37598c616`.

Current `scripts/data/level_data.gd` contains:

- `FORMAT_VERSION_VOID := 2`
- `VOID_CELL := -1`

Fix authority/provisioning so a shallow history cannot create this false negative.

Allowed approaches include a safe history-complete/deepened exact-current TEMP checkout or an equivalent robust ancestry proof.

Requirements:

- canonical origin;
- exact current `origin/main`;
- clean detached TEMP authority;
- no Desktop game mutation;
- no weaker contract check;
- no skip/xfail.

Also make the capability distinguish `INCOMPLETE_GIT_HISTORY` from a real missing audited ancestor if relevant.

Then rerun all seven LF19 tests. They must pass.

## 6. WIRE THE REAL PRODUCTION PUBLISH BUTTON

Current R03 intentionally reports PRODUCTION unavailable. Remove that dead end.

Use existing audited authorities only:

- CP03-007 verified STAGING download;
- CPX-002 exact-current replay;
- CP03-008 `promote_verified_staging_to_production`;
- CP03-009 `activate_versioned_production_manifest`.

Do not create a shadow promotion implementation.

### Required owner confirmation

When target = PRODUCTION and Upload Selected is pressed:

1. require exact verified STAGING evidence for this selection;
2. require accepted current-main replay;
3. show a transient owner confirmation containing:
   - exact manifest SHA-256;
   - exact content version;
   - target = PRODUCTION;
4. only explicit owner confirmation creates/uses the exact `OwnerPromotionApproval`;
5. re-check approval at mutation boundary through the canonical APIs;
6. run CP03-008;
7. run CP03-009;
8. show the real receipt/result.

Wrong hash, wrong version, wrong target, missing approval, stale game authority or stale STAGING state must mutate nothing.

No hard-coded content version.

No direct UI -> R2 bypass.

## 7. COMPLETE THE MISSING R03 TEST MATRIX

Add permanent end-to-end tests for:

### External PNG

- one PNG;
- multiple PNGs;
- CSV/batch PNGs.

### Identity

For each source prove immutable matching of:

`source PNG -> LevelData -> supply -> solver proof -> replay -> Difficulty V1 -> metadata -> publication identity`

Deliberately cross-bind one derived artifact to the wrong PNG and prove rejection.

### Ordering

Use canonical CampaignBuilder/release-order authority.

Prove:

- successful READY order follows source order;
- failed/unsolved item consumes no final production level number;
- final plan is contiguous after current catalog tail;
- retry/resume does not reshuffle stable successful identities.

Do not create a parallel level-number allocator.

### Auto pool

Keep and extend tests proving:

- READY auto-enters;
- Reject excludes;
- Accept restores;
- none auto-publish.

## 8. ALPIX LIVE CAPABILITY

Keep the R03 adapter and unit tests.

Re-read the current local Claude Code config.

If an enabled real Alpix plugin/MCP now exists:

- run one real Single-mode Claude-subscription Alpix PNG generation;
- use no API key;
- validate exact requested dimensions;
- record non-secret plugin/tool identity and PNG SHA only.

If Alpix is still not installed/enabled:

- DO NOT fake;
- DO NOT install an ambiguous third-party plugin;
- DO NOT use paid Anthropic API fallback;
- finish every other R04 technical closure;
- publish the log;
- final state may be:
  `OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED`.

Do not block VOID/UI/production fixes on this external capability.

## 9. FINAL VISUAL EVIDENCE

Install the final durable runtime to the existing Release path.

Capture exactly 1536x1024:

- `PIXEL_ART_FINAL.png`
- `LEVEL_FACTORY_FINAL.png`
- `RELEASE_POOL_FINAL.png`

The screenshots must visually match the approved masters while showing real live-control rendering.

## 10. TEST EXECUTION

During implementation use focused tests.

After all code changes are stable, run one final complete regression.

Required final:

- R04 focused UI/dynamic-state suite;
- provider/resume suite;
- external-PNG identity/order suite;
- all LF19 VOID tests;
- production-publish adversarial suite;
- launcher/runtime suite;
- Godot parse/import;
- complete pytest with zero unresolved code/test failures;
- compileall;
- git diff --check;
- secret scan.

Do not weaken tests.

Do not hide failures as external if repository/current-main evidence disproves them.

## 11. PUBLICATION

Implementation/tests commit first.

Evidence/log commit separately.

Normal fast-forward push only.

Final HEAD == origin/main and clean.

Final state:

- if everything including live Alpix smoke is green:
  `AWAITING_GPT_SB_LFX_018_C001_R02_R04_STRICT_REAUDIT`

- if all code/runtime gates are green but Alpix is still absent:
  `AWAITING_GPT_SB_LFX_018_C001_R02_R04_STRICT_REAUDIT / OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED`

Final response:
return only the GitHub builder-log URL.
