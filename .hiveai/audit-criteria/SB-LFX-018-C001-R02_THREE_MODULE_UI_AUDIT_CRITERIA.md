# SB-LFX-018-C001-R02 — Three-Module Owner UI — Audit Criteria

Product contract:
`docs/product/FACTORY_STUDIO_THREE_MODULE_OWNER_UI_V02.md`

Visual master:
`docs/product/visual-masters/FACTORY_STUDIO_THREE_MODULE_MASTER_V02.svg`

## Visual-master fidelity gate

The final durable-runtime UI must visually track the approved master, not merely satisfy the same information architecture.

Strictly verify:

- same three-button header composition;
- exact visible header labels: **`PIXEL ART`**, **`LEVEL FACTORY`**, **`RELEASE POOL`**;
- first module selected in blue in the Pixel Art screenshot;
- large central Visual Review Canvas dominates the workspace;
- left control column, central canvas, right detail/action column and bottom thumbnail strip remain recognizable in the same proportions;
- dark navy/charcoal visual language and blue accent hierarchy match the master;
- no extra primary navigation;
- no dense engineering text walls;
- no replacement with a generic Godot form layout.

Audit may accept minor rendering/font/platform differences, but not structural reinterpretation.


## PASS rule

PASS requires the owner-facing application to expose exactly three main production modules:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

Settings is secondary only.

## A. Navigation

Require exactly three main modules.

Reject any primary:
- HOME
- CREATE
- BATCH
- SOLVE
- REVIEW
- LIBRARY
- PUBLISH
- other engineering routes.

Legacy tools may exist internally/contextually.

## B. Visual Review Canvas

Mandatory.

Require:

- large central visual area;
- artwork/level rendered nearest-neighbor;
- current selected batch item shown;
- used in PIXEL ART and LEVEL FACTORY;
- selected-level preview available in RELEASE POOL;
- no technical text wall occupying the canvas;
- VOID/game background presentation remains correct.

## C. PIXEL ART module

Require Single and Batch/CSV workflows.

Single:
- generate/import supported artwork;
- Visual Review Canvas;
- regenerate/retry;
- accept/send to Level Factory.

Batch:
- CSV/batch input;
- progress;
- thumbnail/result list;
- select item -> canvas;
- retry failures;
- send valid items to Level Factory.

Use real existing provider/generation authority. Unsupported provider state must fail truthfully.

## D. LEVEL FACTORY module

Require Single and Batch/CSV workflows.

Single:
- selected artwork preview;
- supply columns 3/4/5;
- supply;
- solve/re-solve;
- replay;
- Difficulty V1;
- readiness;
- level number;
- Accept/Reject;
- Send READY to Release Pool.

Batch:
- compact row/table/card list;
- artwork;
- level number;
- columns;
- solver;
- difficulty;
- status;
- Run Selected;
- Run All;
- Retry;
- selected row -> Visual Review Canvas;
- Send READY levels to Release Pool.

All truth delegated to canonical pipeline/game authorities.

## E. RELEASE POOL module

Require only fully prepared/accepted levels.

Show:
- thumbnail;
- level number;
- identity;
- difficulty;
- columns;
- READY;
- order/publication state.

Require:
- visual preview for selected level;
- PRECHECK;
- UPLOAD/PUBLISH.

Internal STAGING/production/R2 gates remain fail-closed and canonical.

The simple UI may hide backend complexity but cannot bypass it.

## F. Settings

Settings gear/panel only.

Provider/path/runtime/R2/cost/diagnostics/recovery/advanced details live here.

Not a fourth primary production module.

## G. No shadow truth

No new authoritative state for:
- artwork acceptance;
- batch state;
- supply;
- solver;
- difficulty;
- level number;
- release acceptance;
- production approval.

Presentation projections may aggregate canonical state read-only.

Owner actions delegate to existing authorities.

## H. Visual evidence

Capture durable-runtime screenshots demonstrating:

1. PIXEL ART Single
2. PIXEL ART Batch/CSV
3. LEVEL FACTORY Single
4. LEVEL FACTORY Batch/CSV
5. RELEASE POOL
6. Settings panel

At least one screenshot must clearly show the large Visual Review Canvas with a real/fixture pixel artwork.

Evidence fixture must be coherent and labeled if synthetic.

## I. Regression

Require:
- focused three-module UI tests;
- Visual Review Canvas tests;
- canonical action delegation tests;
- VOID preview regression;
- current-game LF19 parity tests;
- Factory Studio runtime suite;
- launcher/runtime smoke;
- exact Route A verifier;
- complete repository pytest zero unresolved failures;
- compileall;
- diff check;
- secret scan.

No permanent skip/xfail/assertion weakening.

## Outcome

If technically complete:

`TECHNICAL PASS / OWNER VISUAL REVIEW`

Owner screenshot approval closes:
`PASS / CLOSED`.
