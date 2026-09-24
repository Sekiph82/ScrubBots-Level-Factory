# SB-LF04-007..012-C001 — M04 Master Batch Continuation / Finalization

Document role: CODEX CONTINUATION MASTER PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

## Authoritative state

This prompt continues the already-authorized M04 batch:

`SB-LF04-002..012-C001 — IMPLEMENT_ALL_THEN_AUDIT`

Canonical original master prompt:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF04-002-012-C001_MASTER_BATCH_IMPLEMENTATION_PROMPT.md

Canonical batch index:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF04-002-012-C001_IMPLEMENTATION_AND_AUDIT_INDEX.md

At continuation preparation, GitHub `main` is:

`6d6561da7a16d188bfd618c2f5a915c6b7c96451`

Resolve current `origin/main` again at execution time.

## Already published builder work

Do not reimplement or rewrite:
- SB-LF04-002
- SB-LF04-003
- SB-LF04-004
- SB-LF04-005
- SB-LF04-006

Their builder logs and implementation/log-finalization commits are already on `main`.

The remaining builder cursor is:

`SB-LF04-007`

Tracker checkboxes remain ChatGPT-owned and therefore root `TASKS.md` may still show SB-LF04-002 as the sole active audit frontier. That is expected and does not mean the builder should restart 002.

## Execute exactly

Continue in order:

`SB-LF04-007 -> SB-LF04-008 -> SB-LF04-009 -> SB-LF04-010 -> SB-LF04-011 -> SB-LF04-012`

Then create and publish the final M04 master builder log.

Do not wait for ChatGPT audit between tasks.

## Required per-task prompt / criteria

Read exact paths from:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF04-002-012-C001_IMPLEMENTATION_AND_AUDIT_INDEX.md

For each remaining task:

1. safely fetch/synchronize current `origin/main`;
2. read repository-root `TASKS.md`, AGENTS.md, GOVERNANCE.md;
3. read all already-published M04 002–006 product code/logs as dependencies;
4. read exact task prompt and audit criteria;
5. create that task builder log before product/test edits;
6. implement only its scope;
7. add focused tests;
8. run focused + affected predecessor + retained M03 tests;
9. run full repository pytest, compileall, Godot headless, diff-check and TASKS no-diff;
10. commit/push implementation/tests/docs + builder log;
11. finalize log and publish terminal log-only commit;
12. continue.

Do not edit root `TASKS.md`.

## Desktop / worktree hygiene

Canonical local project:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not create Desktop sibling folders such as:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator-SB-LF04-007`

or any `...-VERIFY` variant.

Durable builder logs belong only under:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\.hiveai\codex-logs\`

If isolation is needed:

1. Prefer `%TEMP%\ScrubBots-Level-Factory\<task-or-verify>`.
2. Remove the temporary checkout/worktree after use when safe.
3. If a Desktop-resident worktree is absolutely required, use only:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\.codex-worktrees\<task-or-verify>`
4. Never create a new Desktop sibling project folder.
5. Do not keep verification worktrees as durable evidence.
6. Record durable evidence in GitHub logs, not separate Desktop folders.
7. Do not modify/clean/reset/stash the owner's separate ScrubBots gameplay checkout.

## M04 semantic guards

### SB-LF04-007
Canonical state volatility only. If required canonical trace quantities are unavailable, production remains UNAVAILABLE. Never use image fragmentation.

### SB-LF04-008
Implement exact fixed Difficulty V1 formula from its audit criteria. Inputs only:
- move_count
- states_visited
- dead_ends
- branching
- forced_moves

Do not use 004–007 optional diagnostics in V1 score.

### SB-LF04-009
Map score only:
- EASY [0,25)
- MEDIUM [25,50)
- HARD [50,75)
- VERY_HARD [75,100]

Never mutate board/art/metadata to fit a lane.

### SB-LF04-010
Bind all M04 results through exact provenance/version/digest. Reject mixed lineage.

### SB-LF04-011
Design/disabled calibration only. No telemetry/network/user identifiers/analytics collection.

### SB-LF04-012
Final declarative checksummed regression + non-mutation closure. Full repository must be green.

## Final master log

After SB-LF04-012 publication, create:

`.hiveai/codex-logs/SB-LF04-C001_MASTER_BATCH_CODEX_LOG.md`

Full GitHub target:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-C001_MASTER_BATCH_CODEX_LOG.md

The master log must cover all eleven tasks:

`SB-LF04-002,003,004,005,006,007,008,009,010,011,012`

For 002–006, read the already-published logs/commits. Do not rewrite them.

For every task record:
- task ID;
- full GitHub builder-log URL;
- implementation SHA;
- terminal log/finalization SHA;
- focused result;
- full-suite result at that task;
- skips and exact reasons;
- canonical metric provider availability/unavailability;
- TASKS zero-diff;
- temporary worktree path if used and whether removed.

## Final batch-wide verification

Run after 012:
- all M04 tests;
- retained M03;
- production/difficulty tests;
- full `python -m pytest -q` with zero failures;
- `python -m compileall -q src tests`;
- Level Factory Godot headless editor boot;
- real canonical bridge tests where configured;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

Do not hide failures with deselection/skip/xfail unless a pre-existing capability-gated test explicitly defines that skip behavior.

Commit/push the final master log.

Then STOP for independent ChatGPT task-by-task audit of SB-LF04-002..012.

## Final response

Return only:
1. full GitHub URL of the M04 master builder log;
2. final master-log commit SHA;
3. full GitHub URLs of the six new builder logs for SB-LF04-007..012.

Then STOP.
