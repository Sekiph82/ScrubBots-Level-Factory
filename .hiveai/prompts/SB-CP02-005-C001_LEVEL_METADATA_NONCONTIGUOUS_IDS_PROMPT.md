# SB-CP02-005-C001 — Level Metadata Without Contiguous-ID Assumption

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP02-005 / SB-CP02-005-C001` or M13 master authority `.hiveai/prompts/M13_CP02_001_012_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all legitimate owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard it.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP02-005-C001` if needed. M13 master mode reuses the single master worktree.
6. Do not create a Desktop sibling clone/worktree.
7. Require execution worktree clean and 0/0 with `origin/main` before edits. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Define manifest level metadata without assuming numeric or contiguous level IDs.

Each level record must at minimum bind:
- canonical `level_id`;
- owning `pack_id`;
- optional explicit presentation/catalog order that is independent from level ID;
- no derivation of order from numeric suffixes or ID sorting.

Rules:
- arbitrary safe canonical level IDs are allowed within the existing M12 path-safe grammar;
- no requirement that IDs be 1..N, sequential, numeric, or gap-free;
- if an explicit order field exists, it must be a real positive integer and its uniqueness semantics must be documented;
- level-to-pack ownership is explicit;
- deterministic serialization must not silently renumber levels.

Do not add runtime catalog behavior. M15 owns gameplay exposure.

## Verification and publication

Run focused tests, prior M13 regressions, M12/M11 regressions, governance, full pytest, compileall, schema parse and diff check.

Builder log:
`.hiveai/codex-logs/SB-CP02-005-C001_LEVEL_METADATA_NONCONTIGUOUS_IDS_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`. Commit implementation and child log separately. In M13 master mode continue immediately to `SB-CP02-006-C001`.
