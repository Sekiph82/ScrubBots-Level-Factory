# SB-LFX-018-C001-R02-R02 — Owner Master Handoff + Exact Three-Master UI — Audit Criteria

Parent strict re-audit:
`.hiveai/audits/SB-LFX-018-C001-R02-R01_STRICT_REAUDIT_V01.md`

Base exact-master criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R01_MASTER_REPAIR_AND_EXACT_UI_AUDIT_CRITERIA.md`

## 0. Exact owner binary identity

Before product mutation, the recovered PIXEL ART owner source must satisfy all of:

- valid PNG;
- 1536 x 1024;
- SHA-256 exactly:
  `b03f00cf01374a5cf884ce572637cbf06a654bb30a6262e28f4e0d76efd10def`;
- visible header exactly:
  `PIXEL ART | LEVEL FACTORY | RELEASE POOL`;
- no leading numeral;
- owl Visual Review Canvas and owner-approved PIXEL ART composition.

No re-encoding, redraw, substitute, generated replacement, crop, rescale or recomposition may be used as the master source.

## A. Canonical master repair

PASS only if:
- the invalid current PIXEL ART master is replaced by the exact owner source bytes, or a new canonical PNG path contains those exact bytes;
- repository index and UI contract point to the valid canonical source;
- Pillow and Godot decode it;
- dimensions are exactly 1536x1024;
- signature is valid;
- LEVEL FACTORY and RELEASE POOL masters remain unchanged unless a strictly necessary path-only reference update is required.

## B. Exactly three production screens

Primary production navigation is exactly:
`PIXEL ART | LEVEL FACTORY | RELEASE POOL`.

No HOME, CREATE, BATCH, SOLVE, REVIEW, LIBRARY, PUBLISH or fourth production page.

Settings is secondary only.

## C. Visual fidelity

At 1536x1024:
- PIXEL ART matches the exact recovered PNG master;
- LEVEL FACTORY matches its locked SVG master;
- RELEASE POOL matches its locked SVG master;
- same topology, panel proportions, control placement and Visual Review Canvas dominance;
- no extra explanation, Technical details, engineering prose, debug UI or extra controls.

## D. Functional truth

All master controls bind only to existing canonical authority:
generation, CSV batch, VOID, supply, official solver/replay, Difficulty V1, owner review, Release Pool, STAGING, exact production approval and R2.

No shadow truth.

## E. Durable runtime

Install under:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

Desktop shortcut launches that runtime without Godot editor.

Window title exactly `ScrubBots Factory Studio`.

## F. Evidence

Required durable-runtime screenshots:
- `PIXEL_ART_FINAL.png`
- `LEVEL_FACTORY_FINAL.png`
- `RELEASE_POOL_FINAL.png`

All exactly 1536x1024.

## G. Regression

Zero unresolved failures across:
- focused exact-master UI tests;
- navigation/control-count/no-extra tests;
- current-game VOID parity;
- Factory Studio runtime suite;
- durable launcher smoke;
- exact Route A verifier;
- Godot parse/import;
- complete repository pytest;
- compileall;
- diff check;
- secret scan.

No skip/xfail/assertion weakening.

## H. Governance

Builder never edits root `TASKS.md` or `.hiveai/audits/**`.

Implementation/tests commit before evidence/log commit.

Normal fast-forward push only.

Final execution worktree clean, HEAD == origin/main, 0 ahead/0 behind.

## Outcome

Technical success:
`TECHNICAL PASS / OWNER VISUAL REVIEW`

Final closure only after owner accepts the three final screenshots:
`PASS / CLOSED`.
