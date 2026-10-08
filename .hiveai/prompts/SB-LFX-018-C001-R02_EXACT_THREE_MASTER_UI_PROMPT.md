# SB-LFX-018-C001-R02 — Exact Three-Master Factory Studio UI

Document role: CODEX IMPLEMENTATION / REMEDIATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Canonical UI contract:
`docs/product/FACTORY_STUDIO_EXACT_THREE_MASTER_UI_V03.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02_EXACT_THREE_MASTER_UI_AUDIT_CRITERIA.md`

Visual masters:
1. `docs/product/visual-masters/FACTORY_STUDIO_PIXEL_ART_MASTER_V03.webp`
2. `docs/product/visual-masters/FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.svg`
3. `docs/product/visual-masters/FACTORY_STUDIO_RELEASE_POOL_MASTER_V01.svg`

Standing sync/publish:
`docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`

## MASTER INTEGRITY PREFLIGHT

Before implementation, decode/render all three canonical masters from the repository and verify their declared dimensions/content are readable. The PIXEL ART master is the repaired standalone WebP `FACTORY_STUDIO_PIXEL_ART_MASTER_V03.webp`; do not use the historical broken V01/V02 dependency chain. If any current indexed master is unreadable, stop before product mutation and report the exact file/hash.

## OWNER LOCK

The application must look like these three masters.

Do not design anything else.

Do not add anything else.

Do not explain the workflow on the production screens.

Do not preserve the eight-page shell.

Do not preserve legacy engineering surfaces as visible owner pages.

The three masters are the owner-facing screen specification.

## FIRST OPERATION

Follow the standing safe sync rule.

Use exact current `origin/main`.

Preserve owner-local Desktop work byte-for-byte.

Use a clean TEMP worktree if required.

Never edit root `TASKS.md`.

Never write `.hiveai/audits/**`.

Builder log:
`.hiveai/codex-logs/SB-LFX-018-C001-R02_EXACT_THREE_MASTER_UI_CODEX_LOG.md`

## 1. Delete the old owner-facing information architecture

The visible primary owner UI must not contain:

- HOME
- CREATE
- BATCH
- SOLVE
- REVIEW
- LIBRARY
- PUBLISH
- technical workspace navigation
- Technical details
- engineering placeholder pages.

Do not merely hide them behind another main-screen menu.

Legacy backend code/services may remain if required by canonical actions.

## 2. Build exactly three visible production screens

Header navigation exactly:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

No leading 1 before PIXEL ART.

No fourth production tab.

Settings is gear/modal/secondary only.

## 3. PIXEL ART = master 1

Open master 1 before coding.

Reproduce its visible composition.

Match:
- header;
- selected PIXEL ART tab;
- left generation controls;
- single/batch behavior in the same visible structure;
- dominant Visual Review Canvas;
- right artwork/result actions;
- bottom result thumbnail strip;
- colors;
- spacing;
- proportions;
- control count.

Do not add help copy.

Do not add technical copy.

Do not add extra actions.

Bind master-defined actions to existing generation/import/batch authority.

## 4. LEVEL FACTORY = master 2

Open master 2 before coding.

Reproduce it.

Match:
- LEVEL FACTORY selected;
- Select Artwork region;
- Single / Batch-CSV control if represented;
- Level Settings;
- Level Number;
- supply columns 3/4/5;
- Max Robots / Background / Target Difficulty controls where shown;
- Pipeline Steps;
- Run Pipeline;
- central Visual Review Canvas;
- Level Details;
- Solver & Difficulty;
- Supply Plan;
- Solve Again;
- Preview Replay where shown;
- Accept Level;
- Reject;
- Level Variations strip;
- status bar.

Real values come from canonical Level Factory/game authorities.

No extra explanatory prose.

## 5. RELEASE POOL = master 3

Open master 3 before coding.

Reproduce it.

Match:
- RELEASE POOL selected;
- Ready Levels count;
- search;
- difficulty/column filters;
- ready-level rows;
- Manage Selection;
- Select All / Clear;
- central Visual Review Canvas;
- Selected for Release strip;
- Level Details;
- Release Settings;
- target environment;
- preflight/validation/pack/upload states;
- Upload Selected;
- Preview Release Manifest;
- bottom status summary.

Do not add a separate PUBLISH page.

Do not add a release explanation page.

Actual release actions must delegate to existing safe Content Pipeline authority.

Do not bypass STAGING/production separation or exact approval.

No secrets in UI/logs/source.

## 6. No-explanation implementation rule

Main screens may contain only master-defined labels and dynamic values.

Remove:
- instructional paragraphs;
- "what this page does";
- engineering warnings;
- authority/provenance text;
- persistent blocker descriptions;
- Technical details links;
- debug labels.

If an action is blocked, keep the master layout and use disabled state or a short transient interaction message.

## 7. No-extra implementation rule

At runtime, audit the visible control tree.

No production-screen element may exist unless it maps to a visible master element.

Do not add convenience buttons because they seem useful.

Do not add dashboard cards.

Do not add side panels.

Do not add status rows beyond the master.

Do not add more navigation.

## 8. Preserve backend truth

Visual simplification does not change canonical behavior.

Retain:
- VOID;
- official current-game loader/validator;
- supply conservation;
- official solver/replay;
- Difficulty V1;
- owner Accept/Reject;
- Release Pool readiness;
- release ordering;
- STAGING;
- exact production approval;
- R2 secret handling.

UI calls existing authority. It does not recreate it.

## 9. Fixed-size visual verification

Run durable Release runtime at 1536×1024.

Capture exactly:
- `.hiveai/codex-logs/SB-LFX-018-C001-R02-exact-master/PIXEL_ART_FINAL.png`
- `.hiveai/codex-logs/SB-LFX-018-C001-R02-exact-master/LEVEL_FACTORY_FINAL.png`
- `.hiveai/codex-logs/SB-LFX-018-C001-R02-exact-master/RELEASE_POOL_FINAL.png`

Compare each side-by-side with its master.

Treat structural mismatch as a defect and iterate before handoff.

## 10. Regression authority

Use a history-complete exact-current ScrubBots checkout.

Do not weaken the audited LF19 VOID ancestry gate.

Require:
- exact current canonical origin;
- clean checkout;
- HEAD == origin/main;
- audited VOID ancestor provable.

Then run all existing required parity/regression suites.

## 11. Tests

Add permanent tests for:
- exactly three primary buttons;
- exact button labels;
- no leading 1;
- no old eight-page primary navigation;
- no Technical details visible on production screens;
- no extra visible production-screen regions;
- master-defined control presence;
- control delegation;
- Visual Review Canvas presence/geometry;
- Release Pool only receives accepted/READY levels;
- fail-closed publication safety.

Run:
- focused UI tests;
- Factory Studio runtime suite;
- LF19 VOID parity;
- launcher/runtime smoke;
- Godot import/parse;
- exact Route A verifier;
- complete repository pytest with zero unresolved failures;
- compileall;
- diff check;
- secret scan.

## 12. Durable runtime

Install final application into:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

The Desktop shortcut must continue to launch this durable runtime.

Window title:
`ScrubBots Factory Studio`

Never `(DEBUG)`.

## 13. Publication

Implementation/tests commit first.

Builder log/screenshots commit separately.

Normal fast-forward push only.

Final:
- HEAD == origin/main;
- 0 ahead / 0 behind;
- clean execution worktree.

Final state:
`AWAITING_GPT_SB_LFX_018_C001_R02_EXACT_MASTER_STRICT_REAUDIT`

Final response:
return only the GitHub builder-log URL.
