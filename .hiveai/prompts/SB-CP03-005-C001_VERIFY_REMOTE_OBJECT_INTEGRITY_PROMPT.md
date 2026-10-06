# SB-CP03-005-C001 - Verify Remote Object Integrity

## FIRST OPERATION - mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-005 / SB-CP03-005-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve legitimate owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard it.
5. If persistent checkout is unsafe to synchronize, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses its single TEMP worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require execution worktree clean and 0/0 with `origin/main` before edits. Stop on unsafe identity/preservation/divergence ambiguity.

## Goal

Require byte-level object integrity after upload through a provider-neutral read/verify surface.

Requirements:
- extend the provider-neutral read surface only as needed to obtain exact stored bytes, not just a provider-reported hash;
- tests use the deterministic stateful test provider, not a vendor adapter;
- for each uploaded pack, re-read stored bytes;
- require exact byte length;
- recompute SHA-256 locally;
- require exact equality to candidate pack evidence;
- run M12 `inspect_scrubpack()` on downloaded bytes;
- provider-reported SUCCESS alone is insufficient;
- truncated, mutated, swapped, wrong-key, stale or wrong-digest bytes fail closed;
- no manifest write authorization on any integrity failure;
- no credentials/provider-specific network code.

Keep logical object keys provider-neutral.

## Verification and publication

Run focused tests, prior M14 regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered full pytest, compileall, Content Pipeline JSON parse checks and diff check.

Builder log:
`.hiveai/codex-logs/SB-CP03-005-C001_VERIFY_REMOTE_OBJECT_INTEGRITY_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.
Commit implementation and builder log separately. Publish normally to main with fetch-before/after and 0/0 clean parity.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CP03-006-C001`.