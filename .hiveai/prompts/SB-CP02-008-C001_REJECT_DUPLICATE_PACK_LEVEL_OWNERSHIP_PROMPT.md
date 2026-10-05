# SB-CP02-008-C001 — Reject Duplicate Pack / Level Ownership Conflicts

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, worktrees.
2. Fetch/prune origin.
3. Read current TASKS and require standalone `SB-CP02-008-C001` or M13 master authority.
4. Preserve owner-local work byte-for-byte; never reset/clean/auto-stash/rebase/force/restore/discard.
5. Standalone TEMP path only: `%TEMP%\ScrubBots-Level-Factory\SB-CP02-008-C001`; master mode reuses master worktree.
6. No Desktop sibling clone/worktree.
7. Require clean 0/0 execution worktree.

## Goal

Fail closed on ownership/collision ambiguity across the manifest.

Reject at minimum:
- duplicate pack IDs;
- case-normalized pack-ID collisions;
- duplicate level IDs;
- case-normalized level-ID collisions;
- one logical level claimed by multiple pack records/ownership records;
- duplicate logical object keys for different packs;
- duplicate optional catalog-order values where the current schema requires uniqueness;
- duplicate schedule target identity where only one window is allowed.

No first-wins / last-wins behavior.

Error diagnostics must be deterministic and identify the conflict category without leaking secrets.

Do not perform remote lookup or pack upload.

## Verification and publication

Run focused/prior M13, M12/M11, governance, full pytest, compileall, schema parse, diff check.

Builder log:
`.hiveai/codex-logs/SB-CP02-008-C001_REJECT_DUPLICATE_PACK_LEVEL_OWNERSHIP_CODEX_LOG.md`

No TASKS/audit edits. Separate commits. Master continues to `SB-CP02-009-C001`.
