# SB-CP03-003-C001 — Hashes + Candidate Manifest

## FIRST OPERATION — mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-003 / SB-CP03-003-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve every byte of legitimate owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard it.
5. If the persistent checkout is not safely synchronizable, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses its single TEMP worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require the execution worktree clean and 0/0 with `origin/main` before edits. Stop for unsafe identity/preservation/divergence ambiguity.

## Goal

Build a deterministic local M13 candidate manifest from CP03-002 pack evidence.

Requirements:
- explicit positive `content_version`;
- explicit canonical `minimum_game_version`;
- every pack record binds exact pack_id, pack_version, provider-neutral object_key, final archive SHA-256 and exact byte length;
- exact level -> pack ownership;
- optional disabled/schedule metadata uses M13 contracts;
- run strict manifest serialize/parse round-trip;
- run CP02-009 reference validation against the exact M12 build evidence;
- run app/content compatibility with explicitly supplied app capability/version;
- candidate manifest is not publishable if any check fails;
- exact candidate-manifest SHA-256 and bytes returned as immutable local evidence;
- if prior accepted manifest/version is supplied, require monotonic successor;
- no provider/network mutation.

## Verification and publication

Run focused tests, all prior M14 child regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered `python -m pytest -q`, compileall, Content Pipeline JSON parse checks and `git diff --check`.

Builder log:
`.hiveai/codex-logs/SB-CP03-003-C001_HASHES_CANDIDATE_MANIFEST_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

Commit implementation and builder log separately. Fetch/prune, normal non-force push to `main`, fetch again, require 0/0 parity and clean worktree.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CP03-004-C001`.