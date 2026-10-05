# SB-CP01-007-C001 — Validate Every Level Before Pack

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP01-007 / SB-CP01-007-C001` or M12 master authority `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP01-007-C001` if needed. M12 master mode reuses the single master worktree.
6. No Desktop sibling clone/worktree.
7. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Add a mandatory fail-closed pre-pack validation transaction.

For every level membership require:
- Content Boundary classification accepted;
- exact CP003 payload validation for LevelData, supply and metadata;
- all three records share the same level identity;
- descriptor projections agree with payload;
- file digests/declared digests agree;
- current allowed schema/version only;
- no duplicate ownership;
- no partial level triplet.

If any one level fails, emit no final pack artifact and no success receipt.

Return deterministic per-level validation diagnostics without secret/runtime/provider data.

Do not invoke gameplay solver here; SB-CPX-001 owns solver-proven supply identity.

## Verification and publication

Run focused tests, all prior M12 child regressions, M11 regressions, governance, full pytest, compileall, and `git diff --check`.

Create/update builder log:
`.hiveai/codex-logs/SB-CP01-007-C001_VALIDATE_EVERY_LEVEL_BEFORE_PACK_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

If green:
- commit implementation;
- commit child log separately;
- fetch/prune;
- normal non-force push to `main`;
- verify 0/0 parity.

Standalone mode: stop for ChatGPT audit.
M12 master mode: continue immediately to `SB-CP01-008-C001` without human handoff.