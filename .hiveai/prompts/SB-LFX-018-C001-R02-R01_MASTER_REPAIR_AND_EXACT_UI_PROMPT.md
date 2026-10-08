# SB-LFX-018-C001-R02-R01 — Master Repair + Exact Three-Master UI

Document role: CODEX REMEDIATION / IMPLEMENTATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Strict audit:
`.hiveai/audits/SB-LFX-018-C001-R02_EXACT_THREE_MASTER_UI_STRICT_AUDIT_V01.md`

Canonical UI contract:
`docs/product/FACTORY_STUDIO_EXACT_THREE_MASTER_UI_V03.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R01_MASTER_REPAIR_AND_EXACT_UI_AUDIT_CRITERIA.md`

Standing sync:
`docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`

## OWNER LOCK

The final owner UI is exactly three production screens:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

No leading 1.

No HOME/CREATE/BATCH/SOLVE/REVIEW/LIBRARY/PUBLISH production pages.

No explanatory paragraphs.

No Technical details.

No extra panels/cards/buttons.

The three owner-approved visual masters win for visible layout.

## FIRST OPERATION — SAFE SYNC

Use exact current `origin/main`.

Preserve the persistent Desktop checkout byte-for-byte.

Use a clean TEMP worktree when needed.

Never edit root `TASKS.md`.

Never write `.hiveai/audits/**`.

Builder log:
`.hiveai/codex-logs/SB-LFX-018-C001-R02-R01_MASTER_REPAIR_AND_EXACT_UI_CODEX_LOG.md`

## 0. HARD MASTER-ASSET GATE

The previous builder correctly stopped because the PIXEL ART master was corrupt.

Do not trust:
- historical `FACTORY_STUDIO_THREE_MODULE_MASTER_V01.webp`;
- V02 wrapper;
- current `FACTORY_STUDIO_PIXEL_ART_MASTER_V03.webp` unless its bytes have been replaced by a real image.

Before any product code change, require the canonical indexed PIXEL ART master to:
- decode successfully with Pillow and/or Godot;
- have dimensions exactly 1536x1024;
- have a real PNG signature or `RIFF....WEBP` signature;
- visibly show header `PIXEL ART | LEVEL FACTORY | RELEASE POOL` with no leading numeral;
- visibly show the owl Visual Review Canvas and the owner-approved PIXEL ART layout.

If the exact recovered source is present in the persistent owner workspace under a recognizable filename such as `ScrubBots Pixel Art Studio.png`, copy it byte-preservingly into the canonical visual-master path in the execution worktree and commit it. Do not modify/delete the owner source.

If the exact owner-approved source is not locally available and the indexed GitHub image is still invalid, STOP before product mutation and report `OWNER_MASTER_BINARY_REQUIRED`. Do not invent or redraw the master.

After a valid binary is committed, update the master index/contract references if the canonical filename changes.

## 1. IMPLEMENT EXACT THREE-SCREEN UI

Once all three masters are valid, execute the existing exact-master specification in full.

### PIXEL ART
Match the master:
- same header/topology;
- same left generation area;
- Single / Batch-CSV;
- same dominant central Visual Review Canvas;
- same right Artwork Details / Quick Actions / Preview Variations;
- same bottom thumbnail strip;
- same proportions and visual hierarchy.

### LEVEL FACTORY
Match its master:
- Select Artwork / Level Settings / Pipeline Steps left;
- central owl Visual Review Canvas;
- Level Details / Solver & Difficulty / Supply Plan / Actions right;
- Level Variations bottom;
- real canonical Level Factory bindings.

### RELEASE POOL
Match its master:
- Ready Levels pool/search/filter left;
- central Visual Review Canvas;
- selected-for-release strip;
- Level Details / Release Settings right;
- canonical preflight/upload controls only;
- no separate PUBLISH page.

## 2. BACKEND TRUTH

Keep all existing canonical authorities:
- VOID;
- supply conservation;
- official solver/replay;
- Difficulty V1;
- Accept/Reject;
- Release Pool;
- STAGING vs production separation;
- exact production approval;
- R2 secret handling.

No shadow truth.

## 3. DURABLE RUNTIME

Install final runtime into:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

Desktop shortcut continues to launch it.

Window title exactly:
`ScrubBots Factory Studio`

No DEBUG.

## 4. EVIDENCE

Capture from durable Release runtime at 1536x1024:
- `PIXEL_ART_FINAL.png`
- `LEVEL_FACTORY_FINAL.png`
- `RELEASE_POOL_FINAL.png`

Compare each against its repository master. Any structural deviation is a defect.

## 5. TESTS

Run:
- focused exact-master UI tests;
- exactly-three-primary-navigation tests;
- no-old-navigation/no-Technical-details tests;
- master-defined control presence/count tests;
- Visual Review Canvas tests;
- current-game VOID parity;
- Factory Studio runtime suite;
- durable launcher smoke;
- exact Route A verifier;
- Godot parse/import;
- complete repository pytest with zero unresolved failures;
- compileall;
- git diff --check;
- secret scan.

No skip/xfail/assertion weakening.

## 6. PUBLICATION

Implementation/tests commit first.

Evidence/log commit separately.

Normal fast-forward push only.

Final HEAD == origin/main, 0 ahead/0 behind, clean execution worktree.

Final state:
`AWAITING_GPT_SB_LFX_018_C001_R02_R01_STRICT_REAUDIT`

Final response:
return only the GitHub builder-log URL.
