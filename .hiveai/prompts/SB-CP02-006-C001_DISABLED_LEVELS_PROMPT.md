# SB-CP02-006-C001 — disabled_levels

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP02-006 / SB-CP02-006-C001` or M13 master authority `.hiveai/prompts/M13_CP02_001_012_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all legitimate owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard it.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP02-006-C001` if needed. M13 master mode reuses the single master worktree.
6. Do not create a Desktop sibling clone/worktree.
7. Require the execution worktree clean and 0/0 with `origin/main` before edits. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Add manifest V1 `disabled_levels` metadata.

Rules:
- list contains canonical level IDs only;
- deterministic canonical ordering;
- no duplicates or case-normalized collisions;
- disabled state is manifest metadata, not deletion;
- pack references and underlying level metadata remain intact;
- disabling does not mutate .scrubpack bytes;
- unknown references may be syntactically representable here but must be rejected by the full reference validator in SB-CP02-009.

Provide pure helper semantics that answer whether a declared level is disabled, with no runtime/global state.

Do not implement Godot skip behavior; M17/M15 own runtime handling.

## Verification and publication

Run focused/prior M13, M12/M11, governance, full pytest, compileall, schema parse, diff check.

Builder log:
`.hiveai/codex-logs/SB-CP02-006-C001_DISABLED_LEVELS_CODEX_LOG.md`

Do not edit root `TASKS.md` or audits. Separate implementation/log commits. M13 master continues to `SB-CP02-007-C001`.
