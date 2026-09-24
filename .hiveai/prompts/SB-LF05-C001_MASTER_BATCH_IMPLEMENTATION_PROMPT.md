# SB-LF05-C001 — M05 Unified QA Master Batch Implementation Prompt

Document role: CODEX MASTER IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

## Authorization

M04 is COMPLETE / VERIFIED.

Retain as PASS/CLOSED:
- SB-LF05-006
- SB-LF05-009

Implement all remaining M05 tasks in order:

`SB-LF05-001 -> 002 -> 003 -> 004 -> 005 -> 007 -> 008 -> 010`

Index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF05-C001_IMPLEMENTATION_AND_AUDIT_INDEX.md

Post-batch audit protocol:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF05-C001_POST_BATCH_STRICT_AUDIT_PROTOCOL.md

## Canonical authorities

At execution time re-resolve both repositories:
- Level Factory: https://github.com/Sekiph82/ScrubBots-Level-Factory
- Main game: https://github.com/Sekiph82/Scrubbots

Observed main-game authority when this prompt was prepared:
`6d13c56d89a71a2183db3398502d7be5f455ecf6`

Do not assume that SHA if main has advanced. Record the exact SHA actually used.

Use independent clean exact-SHA main-game checkout/worktree for validation-only cross-repo tests. Never clean/reset/stash/modify the owner's primary ScrubBots checkout.

## Governance

- Do not edit root TASKS.md.
- Do not create audit files.
- Do not mark tasks PASS/CLOSED.
- Each task gets separate builder log, implementation commit and terminal log-only commit.
- Continue task-to-task without waiting for ChatGPT.
- No gameplay/validator clone.
- No provider-credit/network calls merely for tests.
- No source/art/LevelData mutation.
- No skip/xfail/deselection to manufacture green.

## Desktop / worktree hygiene

Canonical local project:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not create Desktop sibling task/VERIFY folders.

If isolation is needed:
1. prefer `%TEMP%\ScrubBots-Level-Factory\<task-or-verify>`;
2. remove it after use when safe;
3. Desktop fallback only under:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\.codex-worktrees\<task-or-verify>`;
4. durable logs only under repo `.hiveai/codex-logs/`.

## M05 truth rules

### Current production
- width/height 20..59 independently;
- rectangular legal;
- C01..C16 only for final logical LEVEL_ART;
- used colors 3..12;
- final logical gameplay cells opaque;
- difficulty not derived from board size or used-color count.

### Solver
- only exact authoritative PROVEN_UNSOLVABLE rejects under unsolvable reason;
- INCONCLUSIVE/UNKNOWN_BOUND remain distinct;
- timeout is operational, not canonical proof.

### Semantic readability
Retain accepted SB-LF05-009 / SP06 rule:
structural diagnostics never auto-accept recognizability.
Explicit bound review evidence is required for semantic ACCEPT.

### Owner source
OWNER_UPLOAD/source-library bytes remain immutable. Derived artifacts never overwrite source.

### Main-game handoff
Factory QA ACCEPT means only “eligible for main-game acceptance handoff”.

Do not directly publish/overwrite production catalog.

M30 win/lose/retry authority is already closed and must not be redefined.

M47 Android device testing and M48 iOS readiness are still open. Never claim them passed from Factory QA.

## Execution per task

1. fetch/sync current origin/main;
2. verify repository-root TASKS authorizes this M05 master batch;
3. read exact per-task prompt/criteria;
4. create builder log before edits;
5. implement bounded task;
6. add focused tests;
7. run affected prior M05 + retained M03/M04 + owner-upload/semantic-quality tests;
8. run full pytest, compileall, Godot, diff-check, TASKS no-diff;
9. commit/push implementation/tests/docs + builder log;
10. finalize task log + terminal log-only commit;
11. continue.

## Final M05 master log

After SB-LF05-010, create:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF05-C001_MASTER_BATCH_CODEX_LOG.md

For every implemented task record:
- full GitHub builder-log URL;
- implementation SHA;
- terminal log SHA;
- focused/full test result;
- cross-repo capability and exact main-game SHA if used;
- skip reasons;
- source non-mutation evidence;
- TASKS zero diff;
- temporary worktree path/cleanup status.

Final batch-wide gates:
- all M05 tests;
- retained M03/M04;
- SB-LF05-006/009 regressions;
- owner-upload/source-library;
- semantic-quality;
- full pytest zero failures;
- compileall PASS;
- Godot headless PASS;
- cross-repo validation/handoff tests where capability exists;
- git diff --check;
- TASKS zero diff.

Commit/push master log and STOP.

## Final response

Return only:
1. full GitHub URL of the M05 master builder log;
2. final master-log commit SHA;
3. eight full GitHub URLs for per-task builder logs.
