# SB-CP03-007-C001 - Verify STAGING Through Real Byte Download

## FIRST OPERATION - mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-007 / SB-CP03-007-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve legitimate owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard it.
5. If persistent checkout is unsafe to synchronize, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses its single TEMP worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require execution worktree clean and 0/0 with `origin/main` before edits. Stop on unsafe identity/preservation/divergence ambiguity.

## Goal

Verify the staged release by downloading actual stored manifest and pack bytes through the provider-neutral read surface.

"Real download" here means actual bytes returned by the provider interface and independently validated. M18 still owns selection/integration of a real cloud vendor.

Requirements:
- read exact staged manifest bytes from the STAGING object store;
- require exact staging receipt manifest digest and byte length;
- strict-parse the downloaded manifest through M13 bytes parser;
- require exact content_version and candidate identity;
- download every manifest-referenced pack object;
- verify byte length and SHA-256 locally;
- M12 inspect each pack;
- run CP02-009 reference validation using reconstructed immutable M12 evidence or an equivalently exact verified representation;
- verify disabled/schedule/compatibility fields remain byte-identical to the staged candidate;
- return immutable staging-download verification receipt;
- any missing/swapped/tampered/truncated/stale object fails;
- no production mutation.

## Verification and publication

Run focused tests, prior M14 regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered full pytest, compileall, Content Pipeline JSON parse checks and diff check.

Builder log:
`.hiveai/codex-logs/SB-CP03-007-C001_VERIFY_STAGING_REAL_DOWNLOAD_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.
Commit implementation and builder log separately. Publish normally to main with fetch-before/after and 0/0 clean parity.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CPX-002-C001`.