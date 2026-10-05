# SB-CP02-003-C001 — minimum_game_version Compatibility

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP02-003 / SB-CP02-003-C001` or M13 master authority `.hiveai/prompts/M13_CP02_001_012_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all legitimate owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard it.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP02-003-C001` if needed. M13 master mode reuses the single master worktree.
6. Do not create a Desktop sibling clone/worktree.
7. Require the execution worktree clean and 0/0 with `origin/main` before edits. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Add required `minimum_game_version` to manifest V1 and a pure compatibility primitive.

Use one documented canonical numeric version grammar owned by Content Platform, implemented without new third-party dependencies. Prefer strict `MAJOR.MINOR.PATCH` non-negative integer triplets unless current repository authority proves another required format.

Requirements:
- canonical parser rejects malformed, negative, missing, bool, whitespace-padded and ambiguous versions;
- numeric tuple comparison, never string comparison;
- game version equal to minimum => compatible;
- newer game => compatible;
- older game => incompatible;
- compatibility evaluation is pure, deterministic and receives the current game version explicitly;
- no hidden lookup of project.godot, filesystem, clock, network or game runtime.

This is Content Platform compatibility metadata only. M15/M20 own actual runtime/release-time enforcement.

## Verification and publication

Run focused tests, prior M13 regressions, M12/M11 regressions, governance, full pytest, compileall, schema parse and diff check.

Builder log:
`.hiveai/codex-logs/SB-CP02-003-C001_MINIMUM_GAME_VERSION_COMPATIBILITY_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`. Commit implementation and child log separately. In M13 master mode continue immediately to `SB-CP02-004-C001`.
