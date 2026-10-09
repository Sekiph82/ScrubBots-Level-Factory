# SB-LFX-018-C001-R02-R02 — Owner Master Handoff + Exact Three-Master UI

Document role: CODEX CONTINUATION / IMPLEMENTATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Parent audit:
`.hiveai/audits/SB-LFX-018-C001-R02-R01_STRICT_REAUDIT_V01.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R02_OWNER_MASTER_HANDOFF_EXACT_UI_AUDIT_CRITERIA.md`

Standing sync:
`docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`

Mandatory functional control contract:
`docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V01.md`

## OWNER LOCK

Exactly three production screens:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

No leading 1.

No extra production pages.

No explanatory prose.

No Technical details.

No extra visible controls beyond the masters.

## FIRST OPERATION

Use exact current `origin/main`.

Preserve all owner-local Desktop changes byte-for-byte.

If persistent checkout is unsafe/stale/dirty, use a clean exact-current TEMP worktree.

Never edit root `TASKS.md`.

Never write `.hiveai/audits/**`.

Builder log:
`.hiveai/codex-logs/SB-LFX-018-C001-R02-R02_OWNER_MASTER_HANDOFF_EXACT_UI_CODEX_LOG.md`

## OWNER-PROVIDED SOURCE PATH

The owner has now placed the exact PIXEL ART master at:

`C:\Users\sekip\Downloads\pixel art exact master.png`

Use this path first.

Before copying it anywhere, verify its SHA-256 is exactly:

`b03f00cf01374a5cf884ce572637cbf06a654bb30a6262e28f4e0d76efd10def`

If the SHA matches, use it byte-for-byte as the canonical PIXEL ART master source.

If the SHA does not match, STOP with `OWNER_MASTER_SHA_MISMATCH`. Do not substitute, redraw, re-encode, crop, resize or regenerate it.

## 0. OWNER MASTER BINARY GATE

The exact owner-approved PIXEL ART master has a fixed identity:

- PNG
- 1536 x 1024
- SHA-256:
  `b03f00cf01374a5cf884ce572637cbf06a654bb30a6262e28f4e0d76efd10def`
- header:
  `PIXEL ART | LEVEL FACTORY | RELEASE POOL`
- no leading numeral
- owl Visual Review Canvas

Search read-only by exact SHA-256, not merely by filename, in this order:

1. `C:\\Users\\sekip\\Desktop\\Scrubbots - Pixel Art Generator`
2. `C:\\Users\\sekip\\Downloads`
3. `C:\\Users\\sekip\\Desktop`
4. `C:\\Users\\sekip\\Documents`

Preferred source filename if present:
`ScrubBots Pixel Art Studio.png`

The filename is not authoritative; the SHA-256 is. Do not re-encode or modify the source. Do not scan unrelated system locations.

If the exact SHA is not available locally, stop with:
`OWNER_MASTER_BINARY_REQUIRED`

If found:
1. copy it byte-for-byte into the execution worktree as the canonical PIXEL ART master, preferably:
   `docs/product/visual-masters/FACTORY_STUDIO_PIXEL_ART_MASTER_V04.png`;
2. verify SHA remains exact;
3. verify PNG signature and Pillow/Godot decode;
4. verify 1536x1024;
5. update:
   - `FACTORY_STUDIO_VISUAL_MASTER_INDEX_V01.md`;
   - `FACTORY_STUDIO_EXACT_THREE_MASTER_UI_V03.md`;
   - any exact-master tests/reference paths;
6. quarantine/remove invalid V03 from current authority without rewriting history.

Only after this gate passes may product implementation begin.

## 0B. ALL MASTER CONTROLS MUST WORK

Read `docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V01.md` before editing product code.

The master images are NOT decorative backgrounds.

Implement every interactive control in that contract.

Hard requirements:

- no inert hotspot;
- no decorative fake dropdown/button;
- no primary action that only prints "UNAVAILABLE";
- no prompt/style/provider field whose value is ignored;
- no CSV batch path that uses a weaker generator than Single mode;
- no Run Pipeline path that bypasses the canonical primary supply/solver/replay/Difficulty V1 route;
- no Preview Replay button that merely reports WIN;
- no ACCEPT without canonical READY;
- no release selection outside canonical owner-accepted READY entries;
- no direct UI -> R2 call;
- no PRODUCTION upload without exact manifest SHA + content version + production-target owner approval;
- no hard-coded content version for real publishing.

The three masters define appearance. The binding contract defines what every visible control does.

## 1. EXACT THREE-MASTER IMPLEMENTATION

Implement the three visible screens exactly from the current masters.

### PIXEL ART
- left Generate Pixel Art;
- Single / Batch-CSV;
- Batch Progress;
- dominant owl Visual Review Canvas;
- Artwork Details / Quick Actions / Preview Variations right;
- bottom artwork thumbnail strip.

### LEVEL FACTORY
- Select Artwork / Level Settings / Pipeline Steps left;
- central owl Visual Review Canvas;
- Level Details / Solver & Difficulty / Supply Plan / Actions right;
- bottom Level Variations;
- real supply columns 3/4/5, solver/replay, Difficulty V1, level number, Accept/Reject.

### RELEASE POOL
- Ready Levels/search/filter left;
- central Visual Review Canvas;
- Selected for Release strip;
- Level Details / Release Settings right;
- canonical preflight/upload actions only.

No legacy eight-page owner shell remains visible.

## 2. CANONICAL BACKEND

Preserve current authorities unchanged:
- VOID semantics;
- supply conservation;
- official solver/replay;
- Difficulty V1;
- owner review;
- Release Pool;
- STAGING vs production separation;
- exact production approval;
- R2 credential secrecy;
- declarative-only remote payload.

## 3. DURABLE RELEASE

Install into:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

Desktop shortcut must launch it directly.

Window title:
`ScrubBots Factory Studio`

No DEBUG.

## 4. EVIDENCE

From the durable Release runtime capture exactly 1536x1024:
- `PIXEL_ART_FINAL.png`
- `LEVEL_FACTORY_FINAL.png`
- `RELEASE_POOL_FINAL.png`

## 5. TESTS

Run all audit-criteria gates, including complete repository pytest with zero unresolved failures.

No skip/xfail/assertion weakening.

## 6. PUBLICATION

Implementation/tests commit first.

Evidence/log commit separately.

Normal fast-forward push only.

Final HEAD == origin/main, 0 ahead/0 behind, clean execution worktree.

Final state:
`AWAITING_GPT_SB_LFX_018_C001_R02_R02_STRICT_REAUDIT`

Final response:
return only the GitHub builder-log URL.
