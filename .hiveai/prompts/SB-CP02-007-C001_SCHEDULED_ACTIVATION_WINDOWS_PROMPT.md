# SB-CP02-007-C001 — Scheduled Activation Windows

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP02-007 / SB-CP02-007-C001` or M13 master authority `.hiveai/prompts/M13_CP02_001_012_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve owner-local work. No reset/clean/stash/rebase/force/restore/discard.
5. Standalone TEMP path: `%TEMP%\ScrubBots-Level-Factory\SB-CP02-007-C001`; master mode reuses the M13 worktree.
6. No Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority before edits.

## Goal

Add declarative scheduled activation windows to manifest V1.

Use explicit records targeting declared packs and/or levels.

Each schedule must include:
- target kind (`pack` or `level`);
- target ID;
- explicit UTC `not_before`;
- optional UTC `not_after`.

Rules:
- whole-second normalized UTC;
- if end exists, end > start;
- one canonical schedule per target unless the spec explicitly defines non-overlapping multi-window behavior and proves it deterministic;
- pure evaluation receives `at_utc` explicitly;
- no hidden `now()`, local timezone, environment clock, network time or filesystem time;
- before start => inactive;
- at start => active;
- at/after end => inactive if end exists.

Reference existence is closed in SB-CP02-009. Runtime activation is M17/M15 scope.

## Verification and publication

Run focused/prior M13, M12/M11, governance, full pytest, compileall, schema parse, diff check.

Builder log:
`.hiveai/codex-logs/SB-CP02-007-C001_SCHEDULED_ACTIVATION_WINDOWS_CODEX_LOG.md`

No TASKS/audit edits. Separate commits. Master continues to `SB-CP02-008-C001`.
