# SB-LFX-018-C001-R02 — Three-Module Factory Studio Owner UI

Document role: CODEX OWNER-DIRECTED REMEDIATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Owner contract:
`docs/product/FACTORY_STUDIO_THREE_MODULE_OWNER_UI_V02.md`

Approved visual master:
`docs/product/visual-masters/FACTORY_STUDIO_THREE_MODULE_MASTER_V02.svg`

## VISUAL MASTER IS AUTHORITATIVE

Before changing UI code, open and inspect the visual master.

The owner requires the final Factory Studio to match this image **as closely as possible**.

Do not create a new visual concept.

Do not reinterpret the layout.

Do not simplify it into generic Godot forms.

Use the visual master for:
- overall window composition;
- panel geometry;
- spacing;
- left generation/batch column;
- central Visual Review Canvas;
- right artwork/details/actions column;
- bottom thumbnail strip;
- top navigation;
- dark visual language;
- blue/green action emphasis.

Owner-locked header text:
- **`PIXEL ART`**
- **`LEVEL FACTORY`**
- **`RELEASE POOL`**

The leading **`1`** in **`PIXEL ART`** is intentional. Preserve it exactly.

Functional implementation may adapt controls to real canonical capability, but the visible composition must remain faithful to the master.


Audit criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02_THREE_MODULE_UI_AUDIT_CRITERIA.md`

Standing sync/publish:
`docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`

## OWNER DIRECTION SUPERSEDES THE 8-PAGE UI

Do not continue polishing:

`HOME | CREATE | BATCH | SOLVE | REVIEW | LIBRARY | PUBLISH | SETTINGS`

That navigation is superseded.

The owner wants exactly three main modules:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

Settings is a secondary gear/panel.

## FIRST OPERATION

Follow standing safe sync.

Use exact current `origin/main`.

Preserve persistent Desktop owner work.

If needed use:

`%TEMP%\ScrubBots-Level-Factory\SB-LFX-018-C001-R02`

Never edit root `TASKS.md`.

Never write `.hiveai/audits/**`.

Builder log:

`.hiveai/codex-logs/SB-LFX-018-C001-R02_THREE_MODULE_OWNER_UI_CODEX_LOG.md`

## 1. Preserve the large Visual Review Canvas

The owner explicitly requires the large center artwork-review area shown in the current Factory Studio screenshot.

Do not remove or shrink it into a tiny thumbnail.

Implement it as a reusable `Visual Review Canvas`.

It must dominate the center workspace in:

- PIXEL ART;
- LEVEL FACTORY.

RELEASE POOL must also provide selected-level visual preview.

Requirements:

- nearest-neighbor pixel art;
- selected item immediately shown;
- correct BG/VOID presentation;
- batch selection changes the canvas;
- no engineering prose inside the canvas.

## 2. Rebuild navigation to three modules

Primary navigation exactly:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

Remove the 8-page owner navigation.

Do not expose HOME/CREATE/BATCH/SOLVE/REVIEW/LIBRARY/PUBLISH as main tabs.

Move Settings to a small gear/header control.

Keep legacy tools/services internally for canonical operations.

## 3. PIXEL ART module

Implement two modes:

### Single
- artwork request/input;
- generation/import provider controls supported by current system;
- Generate;
- Visual Review Canvas;
- Regenerate/Retry;
- Accept/Send to Level Factory.

### Batch / CSV
- CSV/batch input;
- generation progress;
- thumbnail/result list;
- select result -> Visual Review Canvas;
- retry failures;
- send selected/all valid items to Level Factory.

Do not surface provider engineering detail in the main workspace.

Unsupported capability must be truthful.

## 4. LEVEL FACTORY module

Two modes:

### Single

Show together:

- Visual Review Canvas;
- artwork identity;
- supply columns 3/4/5;
- Run Supply;
- Solve/Re-solve;
- replay;
- official Difficulty V1;
- readiness;
- Level Number;
- ACCEPT;
- REJECT;
- Send READY to Release Pool.

### Batch / CSV

Provide compact batch table/list with:

`Artwork | Level | Columns | Solver | Difficulty | Status`

Actions:

- set level number;
- set columns individually/batch;
- Run Selected;
- Run All;
- Retry failed;
- select row -> Visual Review Canvas;
- Accept/Reject;
- Send READY levels to Release Pool.

Use the existing canonical pipeline, current-game solver/replay and owner-review authority.

Do not create UI-local fake solve/difficulty/readiness state.

## 5. RELEASE POOL module

Show only READY/accepted levels.

Use compact visual cards/table:

- thumbnail;
- level number;
- identity/name;
- Difficulty V1;
- supply columns;
- READY;
- order/publish state.

Selected item -> visual preview.

Primary owner actions should be simple:

- PRECHECK
- UPLOAD / PUBLISH

Internally retain all safe gates:

Release Pool -> pack -> STAGING -> verification -> exact production approval -> Production/R2.

Do not bypass or infer production approval.

If credentials/receipt/approval are missing, fail closed and show one concise blocker.

Do not expose backend publication architecture as separate main screens.

## 6. Settings gear

Move provider, paths/runtime, R2 status, costs, diagnostics, recovery and advanced technical information into the Settings panel.

Settings is not a main production module.

## 7. Text-density rule

Default owner surfaces must be extremely concise.

No walls of:
- canonical;
- authority;
- lineage;
- provenance;
- NOT AVAILABLE matrices.

Use:
- Ready
- Processing
- Failed
- Solved
- Needs Attention
- Accepted

Technical details collapsed.

## 8. Visual evidence

Capture from durable Release runtime and compare every screenshot side-by-side with the approved visual master.

The Pixel Art Single screenshot must be recognizably the same screen as the master, including the exact visible header label `PIXEL ART`.

Capture:

1. PIXEL ART — Single
2. PIXEL ART — Batch / CSV
3. LEVEL FACTORY — Single
4. LEVEL FACTORY — Batch / CSV
5. RELEASE POOL
6. Settings panel

Evidence must clearly show the Visual Review Canvas.

Use deterministic labeled fixture state where live data is unsafe.

Fixture state must be internally coherent and display-only.

## 9. Regression

Retain all canonical backend behavior.

Fix the R01 regression environment issue using a history-complete exact-current Scrubbots checkout.

Do not weaken the LF19 VOID capability gate.

Run:
- focused three-module UI tests;
- LF19 VOID parity tests;
- Factory Studio runtime suite;
- launcher/runtime smoke;
- Godot parse/import;
- exact Route A verifier;
- full repository pytest with zero unresolved failures;
- compileall;
- diff check;
- secret scan.

## 10. Durable runtime

Install the final app into:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

using the existing installer.

Normal owner title:

`ScrubBots Factory Studio`

No DEBUG title.

## 11. Publication

Implementation/test commit first.

Evidence/log commit separately.

Normal fast-forward push only.

Final clean 0/0 parity.

Final state:

`AWAITING_GPT_SB_LFX_018_C001_R02_THREE_MODULE_STRICT_REAUDIT`

Return only the GitHub builder log URL.
