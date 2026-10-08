# SB-LFX-018-C001-R02-R01 — Master Repair + Exact Three-Master UI — Audit Criteria

Strict-audit authority:
`.hiveai/audits/SB-LFX-018-C001-R02_EXACT_THREE_MASTER_UI_STRICT_AUDIT_V01.md`

Base exact-master criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02_EXACT_THREE_MASTER_UI_AUDIT_CRITERIA.md`

## 0. Master binary closure

PASS only if the repository's indexed PIXEL ART master is a real image and:
- decodes successfully;
- is exactly 1536x1024;
- has a valid PNG or RIFF/WEBP signature;
- visibly matches the owner-approved PIXEL ART composition;
- header is exactly `PIXEL ART | LEVEL FACTORY | RELEASE POOL`;
- no leading `1` exists.

Historical corrupt V01/V02/V03 bytes are not acceptable authority.

If the exact owner master cannot be sourced, result is `OWNER_MASTER_BINARY_REQUIRED` and product mutation must not occur.

## A. Exactly three production screens

Visible primary production navigation is exactly:
`PIXEL ART | LEVEL FACTORY | RELEASE POOL`.

Settings may be secondary only.

No old eight-page shell.

## B. PIXEL ART visual fidelity

At 1536x1024:
- left Generate Pixel Art / Single / Batch-CSV / Batch Progress composition matches master;
- central owl Visual Review Canvas dominates;
- right Artwork Details / Quick Actions / Preview Variations matches master;
- bottom result thumbnail strip matches master;
- no extra explanatory UI;
- no Technical details;
- no extra buttons/cards/panels.

## C. LEVEL FACTORY visual fidelity

At 1536x1024:
- left Select Artwork / Level Settings / Pipeline Steps;
- central owl Visual Review Canvas;
- right Level Details / Solver & Difficulty / Supply Plan / Actions;
- bottom Level Variations;
- master geometry, hierarchy and visible control set retained;
- no extra explanatory/engineering UI.

## D. RELEASE POOL visual fidelity

At 1536x1024:
- Ready Levels pool/search/filter;
- central Visual Review Canvas;
- Selected for Release strip;
- right Level Details / Release Settings;
- master-defined preflight/upload controls;
- no separate PUBLISH page;
- no extra backend navigation.

## E. Canonical functional binding

All visible actions delegate to current canonical authority. No shadow truth for generation, batch, level numbering, supply, solver/replay, Difficulty V1, review, release readiness, STAGING, production approval or R2.

## F. VOID parity

Transparent/VOID behavior remains identical to the already-closed LF19 contract. Exact-current history-complete ScrubBots authority must prove audited VOID ancestry and all parity tests must pass.

## G. Durable runtime

Final application installed under:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

Desktop shortcut launches that durable runtime without Godot editor.

Window title is exactly `ScrubBots Factory Studio`.

## H. Evidence

Required 1536x1024 screenshots from durable runtime:
- PIXEL_ART_FINAL.png
- LEVEL_FACTORY_FINAL.png
- RELEASE_POOL_FINAL.png

Independent audit compares each against its exact repository master. Structural mismatch fails.

## I. Regression

Require zero unresolved failures across:
- focused exact-master UI tests;
- navigation/control-count/no-extra tests;
- Factory Studio runtime suite;
- VOID parity;
- launcher/runtime smoke;
- exact Route A verifier;
- Godot parse/import;
- complete repository pytest;
- compileall;
- diff check;
- secret scan.

No skip/xfail/assertion weakening.

## J. Governance

Builder does not edit root TASKS.md or .hiveai/audits/**.

Implementation/tests commit first.

Evidence/log commit separately.

Normal fast-forward push only.

Final execution authority clean and 0/0 with origin/main.

## Outcome

Technical success:
`TECHNICAL PASS / OWNER VISUAL REVIEW`

Closure only after owner accepts all three final screenshots:
`PASS / CLOSED`.
