# SB-LFX-018-C001-R02 — Exact Three-Master UI — Audit Criteria

Canonical contract:
`docs/product/FACTORY_STUDIO_EXACT_THREE_MASTER_UI_V03.md`

Visual masters:
- `docs/product/visual-masters/FACTORY_STUDIO_THREE_MODULE_MASTER_V02.svg`
- `docs/product/visual-masters/FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.svg`
- `docs/product/visual-masters/FACTORY_STUDIO_RELEASE_POOL_MASTER_V01.svg`

## A. Exactly three production screens

PASS only if visible primary navigation is exactly:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

No extra production page/tab.

Settings gear is secondary only.

## B. Pixel Art master fidelity

At 1536×1024 deterministic capture, require the PIXEL ART screen to be recognizably the same composition as its master:

- same header/nav topology;
- PIXEL ART selected;
- same left-control region;
- same dominant central Visual Review Canvas;
- same right-side region;
- same bottom thumbnail/result strip;
- same dark/navy styling and accent hierarchy;
- no visible element absent from the master.

Header text must be exactly `PIXEL ART`, with no leading 1.

## C. Level Factory master fidelity

At 1536×1024 capture require:

- LEVEL FACTORY selected;
- left Select Artwork / Level Settings / Pipeline Steps column in master geometry;
- central Visual Review Canvas with selected artwork;
- right Level Details / Solver & Difficulty / Supply Plan / Actions;
- bottom Level Variations strip;
- no extra explanatory or engineering panels;
- no missing master-defined visible controls.

## D. Release Pool master fidelity

At 1536×1024 capture require:

- RELEASE POOL selected;
- left Ready Levels pool with search/filters/list and selection actions;
- central Visual Review Canvas;
- bottom Selected for Release strip;
- right Level Details and Release Settings;
- master-defined preflight/upload controls;
- no extra production controls or backend-page navigation.

## E. No-explanation/no-extra gate

On all three production screens reject:

- explanatory paragraphs;
- technical-details links;
- canonical/authority/provenance text;
- persistent blocker essays;
- debug labels;
- extra buttons/cards/panels/tabs not shown by the master.

Dynamic status text in master-defined locations is allowed.

Transient error toast/modal after an action is allowed.

## F. Functional binding

Every active master control must delegate to existing canonical authority.

No shadow truth for:
- generation;
- batch state;
- level number;
- supply;
- solver;
- replay;
- difficulty;
- review;
- release readiness;
- STAGING;
- production approval.

If a master control is not yet executable because a real prerequisite is absent, it remains visibly in the master location and fails closed without adding new main-screen UI.

## G. Visual Review Canvas

Require the same reusable canvas behavior across all three screens:

- nearest-neighbor;
- selected item shown immediately;
- correct transparent/VOID presentation;
- no logs/prose inside canvas;
- master-matching geometry.

## H. Regression

Require:
- focused exact-master UI tests;
- node/control-count tests proving no extra main-screen elements;
- fixed-size screenshot evidence for all three screens;
- current-game VOID parity;
- Factory Studio runtime suite;
- launcher/runtime smoke;
- exact Route A verifier;
- complete repository pytest with zero unresolved failures;
- compileall;
- diff check;
- secret scan.

No skip/xfail/assertion weakening.

## I. Evidence

Builder must publish:
- PIXEL_ART_FINAL.png
- LEVEL_FACTORY_FINAL.png
- RELEASE_POOL_FINAL.png

All captured from durable Release runtime at 1536×1024.

Builder log must compare each final screenshot to its exact repository master and list any unavoidable platform/font-rendering deviation.

Any structural deviation is FAIL.

## Outcome

If A-I pass:

`TECHNICAL PASS / OWNER VISUAL REVIEW`

Owner approval of the three final screenshots closes:

`PASS / CLOSED`.
