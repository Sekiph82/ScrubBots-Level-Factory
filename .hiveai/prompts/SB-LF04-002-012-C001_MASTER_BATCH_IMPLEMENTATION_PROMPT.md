# SB-LF04-002..012-C001 — M04 Master Batch Implementation Prompt

Document role: CODEX MASTER IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

## Authorization

SB-LF04-001 is PASS/CLOSED through R01.

Execute all remaining M04 tasks in order:

SB-LF04-002 -> 003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010 -> 011 -> 012

Index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF04-002-012-C001_IMPLEMENTATION_AND_AUDIT_INDEX.md

Post-batch audit protocol:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-002-012-C001_POST_BATCH_STRICT_AUDIT_PROTOCOL.md

## Absolute governance

- Do not edit root TASKS.md.
- Do not mark tasks PASS/CLOSED.
- Do not create audit files.
- Do not rewrite prior prompts/logs/audits.
- Each task gets its own builder log, implementation commit and terminal log-only commit.
- Continue task-to-task without waiting for ChatGPT audit.
- Preserve all accepted M03 and LF04-001 behavior.
- No force-push/reset/clean/stash/discard of unrelated owner work.
- No network/provider-credit calls merely for tests.

## Desktop / worktree hygiene

Canonical local project:
C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator

Do NOT create persistent sibling folders on the Desktop such as:
- C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator-SB-LF04-...
- C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator-...-VERIFY

Builder logs belong only in the repository:
C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\.hiveai\codex-logs\

Normal task work should use the canonical project checkout after safe synchronization when isolation is not required.

If an isolated worktree/clone is technically necessary:
1. Prefer an ephemeral location under %TEMP%\ScrubBots-Level-Factory\<task-or-verify>.
2. Delete it after verification when safe.
3. If it absolutely must live under Desktop, place it only inside:
   C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\.codex-worktrees\<task-or-verify>
   never as a Desktop sibling.
4. Prevent temporary worktree folders from appearing as project artifacts or being committed.
5. Do not keep verification clones merely as logs/evidence; durable evidence belongs in .hiveai/codex-logs and GitHub.
6. Never modify/clean/reset/stash the owner's separate canonical ScrubBots gameplay checkout merely to create isolation.

## Task execution

For each task:
1. fetch current origin/main;
2. verify root TASKS.md authorizes this M04 master batch and repository-root TASKS is the sole live tracker;
3. read exact per-task prompt/criteria from the index;
4. create that task builder log before edits;
5. implement only its scope;
6. add focused tests;
7. run focused + affected predecessor + retained M03 gates;
8. run full repository pytest, compileall, Godot headless, diff-check and TASKS no-diff;
9. commit/push implementation/tests/docs + task log;
10. finalize task log and publish terminal log-only commit;
11. continue.

Do not use docs/migration/legacy-task-trackers/TASKS.md for authorization.

## Metric truth

002/003 populate guaranteed solver-witness metrics.

004-007 are canonical-provider diagnostics. If canonical semantics/trace is not safely available, production result stays UNAVAILABLE and LevelMetrics slot stays absent. Do not fake them to keep the batch moving.

008 implements the exact fixed Difficulty V1 formula and coefficients in its criteria. Optional 004-007 metrics are not V1 score inputs.

009 maps score to four lanes by fixed score thresholds only.

010 locks provenance and rejects mixed lineage.

011 is disabled/design-only calibration. No telemetry/network/user tracking is authorized.

012 creates final declarative regression + non-mutation proof and must leave the complete repository green.

## Master log

After all eleven task attempts create:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-C001_MASTER_BATCH_CODEX_LOG.md

For every task record:
- task ID;
- full GitHub builder-log URL;
- implementation SHA;
- terminal log-only SHA;
- focused test result;
- full-suite result at that task;
- skips and exact reasons;
- canonical metric provider availability/unavailability;
- TASKS zero-diff;
- temporary worktree path if one was necessary and whether it was removed.

Then run final batch-wide:
- all M04 tests;
- retained M03;
- production/difficulty tests;
- full python -m pytest -q;
- python -m compileall -q src tests;
- Level Factory Godot headless editor boot;
- real canonical bridge tests where configured;
- git diff --check;
- git diff --exit-code -- TASKS.md.

Full suite must be green. Do not skip/xfail failures to manufacture green.

Commit/push the master log and STOP.

## Final response

Return only:
1. full GitHub URL of the M04 master builder log;
2. final master-log commit SHA;
3. eleven full GitHub URLs for per-task builder logs.
