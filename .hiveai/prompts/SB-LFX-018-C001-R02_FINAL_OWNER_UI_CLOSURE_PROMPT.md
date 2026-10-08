# SB-LFX-018-C001-R02 — Final Owner UI Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

R01 strict re-audit:
`.hiveai/audits/SB-LFX-018-C001-R01_STRICT_REAUDIT_V01.md`

R02 criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02_FINAL_OWNER_UI_CLOSURE_AUDIT_CRITERIA.md`

Product contract:
`docs/product/FACTORY_STUDIO_SIMPLE_OWNER_UI_V01.md`

Standing sync/publish:
`docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`

## FIRST OPERATION

Use exact current `origin/main`.

Preserve the persistent dirty Desktop checkout.

If needed use:

`%TEMP%\ScrubBots-Level-Factory\SB-LFX-018-C001-R02`

Never edit root `TASKS.md`.

Never write `.hiveai/audits/**`.

Builder log:

`.hiveai/codex-logs/SB-LFX-018-C001-R02_FINAL_OWNER_UI_CLOSURE_CODEX_LOG.md`

## RETAIN, DO NOT REDESIGN

Keep the accepted shell exactly:

`HOME | CREATE | BATCH | SOLVE | REVIEW | LIBRARY | PUBLISH | SETTINGS`

Retain the current dark visual language, header, preview layout, compact footer, collapsed Technical details and canonical owner projection.

Do not return to the old engineering UI.

Do not add more technical prose.

R02 should become **more visual and more coherent**, not denser.

## 1. HOME item cards

Replace the RichText-only batch item bullets with compact visual cards/rows.

When canonical artwork/source preview exists, show a thumbnail.

Each visible item needs concise identity + status.

Keep:

- Imported
- Solved
- Needs Attention
- Reviewed
- Accepted
- progress
- Continue Batch

Use canonical projection only.

## 2. BATCH item cards

Render multiple per-item rows/cards with:

- thumbnail when available;
- identity;
- current status/stage.

Keep direct:

- Continue Batch/Pipeline;
- Retry eligible failures;
- Resume/Recover.

Do not require the old Failures screen for the normal flow.

## 3. LIBRARY catalog

Render actual canonical results as a compact visual list/grid.

Each result should show:

- thumbnail when available;
- source/candidate identity;
- type;
- status.

Keep search + filter.

Provide a clear selected-item Open/Details route.

Revisions/Reproduce/History remain contextual.

## 4. PUBLISH direct owner workflow

The simple PUBLISH page itself must expose distinct controls for:

1. Campaign Order / accepted levels
2. Preflight
3. Publish to STAGING
4. Production Approval

Do not hide STAGING and production approval behind one generic legacy button.

Use existing trusted publisher/content-pipeline authority.

Do not duplicate publication or R2 logic in GDScript.

Production Approval must be visibly separate and fail closed.

If verified STAGING receipt / exact production approval identity / secure R2 writer environment is absent, keep Production Approval disabled or return the truthful first blocker.

Do not use `APPROVE and Open Release PR` as a substitute for remote-content Production Approval.

Never put credentials in UI/project/logs.

## 5. SETTINGS path/runtime state

Add compact durable runtime/project path status.

Keep provider/core/cost/recovery/diagnostics.

Do not expose giant absolute-path paragraphs. A compact resolved path/status row is enough.

## 6. Fix the visual-evidence architecture

Current R01 screenshot harness changes only the RichText block, leaving state cards/controls inconsistent.

Replace that approach with a coherent presentation fixture.

Preferred:

- build one display-only fixture projection/state object;
- feed it through the same owner rendering functions;
- update cards, item rows, selected controls, next-step state and button states together.

Fixture must remain clearly labeled:

`VISUAL FIXTURE — not canonical data`

It must never call mutation APIs or write evidence.

Examples that must be internally consistent:

- HOME: 8 imported / 5 solved / 1 attention / 4 reviewed / 3 accepted and item cards matching those states;
- BATCH: 6/8 progress and multiple item statuses;
- SOLVE: selected candidate + **4 columns** + SOLVED + WIN + Difficulty V1 42, with the visible selector also on 4;
- REVIEW: selected candidate + READY evidence + ACCEPT/REJECT visible, while owner decision remains not recorded;
- LIBRARY: six visible fixture results represented by cards/rows;
- PUBLISH: no release occurred, STAGING not started, Production Approval pending/disabled;
- SETTINGS: example-only provider/runtime/cost state.

## 7. Correct the R01 VOID regression environment

Do **not** change the audited VOID contract just because the R01 game clone was shallow.

Independent audit verified:

- `7d0d148b8609ec04852fdee02f6b8ef37598c616` is an ancestor of builder-tested `861d6a8a7d4a572ae7a35a9b65a55677a8e071b5`;
- current Scrubbots main still contains LevelData VOID V2.

For regression, create/resolve an exact-current clean canonical Scrubbots authority with enough history.

Before pytest prove:

`git merge-base --is-ancestor 7d0d148b8609ec04852fdee02f6b8ef37598c616 HEAD`

returns success.

If using a shallow clone, deepen/fetch history until the ancestry proof is authoritative.

Also prove:

- canonical origin;
- clean checkout;
- HEAD == origin/main.

Then set `SCRUBBOTS_PROJECT` process-locally to that authority.

Do not weaken the LF19 capability gate.

## 8. Required tests

Run the seven VOID parity tests against the corrected game authority.

Run exact Route A verifier.

Run focused R02 UI/runtime tests.

Run Factory Studio runtime suite.

Run Godot parse/import.

Then run the complete repository pytest **after the final code change**.

Required final result: zero failures.

Also:

- compileall;
- git diff --check;
- secret scan.

No permanent skip/xfail/assertion weakening.

## 9. Durable Release evidence

Install final implementation into:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

using the existing installer.

Capture final eight screenshots from that durable runtime.

Record SHA-256 for all eight.

## 10. Publication

Implementation/tests commit first.

Builder log/screenshots second.

Normal fast-forward push only.

Final:

- clean worktree;
- HEAD == origin/main;
- 0/0.

Final state:

`AWAITING_GPT_SB_LFX_018_C001_R02_STRICT_REAUDIT`

Return only the GitHub builder log URL.
