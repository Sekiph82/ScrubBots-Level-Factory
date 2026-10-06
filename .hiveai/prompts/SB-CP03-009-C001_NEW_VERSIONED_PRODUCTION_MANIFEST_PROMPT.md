# SB-CP03-009-C001 - New Versioned Production Manifest

## FIRST OPERATION - mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-009 / SB-CP03-009-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard.
5. If persistent checkout cannot be safely synchronized, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses the single master worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority before edits.

## Goal

Activate the exact staged candidate as a new monotonic PRODUCTION manifest version only after CP03-008 pack promotion succeeds.

Requirements:
- downloaded verified STAGING manifest bytes are the promotion source;
- do not reserialize a semantically equivalent but byte-different manifest;
- candidate content_version must be strictly greater than current accepted PRODUCTION content_version;
- schema/minimum-game/pack hashes/level ownership/disable/schedule fields remain exact;
- production pack bytes already verified before manifest write;
- perform conditional production manifest write using explicit expected prior production digest/version;
- after write, download exact production manifest bytes and require byte equality to staging candidate;
- run strict parser, reference validation, app compatibility and exact production pack byte/hash verification;
- append exact production manifest bytes to M13 manifest history with explicit caller-supplied UTC record time;
- append M11 release-state transition to PRODUCTION_PROMOTED;
- return immutable production-manifest receipt;
- no silent overwrite and no rollback in this child.

## Verification and publication

Run focused tests, prior M14 regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered full pytest, compileall, Content Pipeline JSON parse and diff checks.

Builder log:
`.hiveai/codex-logs/SB-CP03-009-C001_NEW_VERSIONED_PRODUCTION_MANIFEST_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`. Separate implementation/log commits. Fetch/prune, normal non-force push, fetch again, require 0/0 clean parity.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CP03-010-C001`.