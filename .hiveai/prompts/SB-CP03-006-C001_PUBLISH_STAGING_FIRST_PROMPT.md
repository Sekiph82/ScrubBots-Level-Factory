# SB-CP03-006-C001 - Publish STAGING First

## FIRST OPERATION - mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-006 / SB-CP03-006-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve legitimate owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard it.
5. If persistent checkout is unsafe to synchronize, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses its single TEMP worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require execution worktree clean and 0/0 with `origin/main` before edits. Stop on unsafe identity/preservation/divergence ambiguity.

## Goal

Publish the candidate manifest to STAGING only after every referenced pack is uploaded and byte-verified.

Requirements:
- production target is forbidden in this child;
- require current accepted CP03-001 validation report;
- require exact CP03-003 candidate manifest evidence;
- require CP03-004 pack-upload receipt;
- require CP03-005 integrity receipt for every referenced pack;
- revalidate candidate manifest references immediately before staging write;
- conditionally write the staging manifest object with an explicit expected prior staging identity/digest;
- record release-state transitions through VALIDATED -> STAGED using append-only M11 release state;
- return immutable staging receipt with manifest bytes/hash/content_version, referenced pack hashes, provider identity/capability identity, target identity and release event digests;
- any stale plan/target/evidence state blocks;
- never mutate production;
- test provider only, no real vendor adapter.

## Verification and publication

Run focused tests, prior M14 regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered full pytest, compileall, Content Pipeline JSON parse checks and diff check.

Builder log:
`.hiveai/codex-logs/SB-CP03-006-C001_PUBLISH_STAGING_FIRST_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.
Commit implementation and builder log separately. Publish normally to main with fetch-before/after and 0/0 clean parity.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CP03-007-C001`.