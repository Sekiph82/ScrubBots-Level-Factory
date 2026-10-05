# SB-CP01-009-C001 — Deterministic .scrubpack Bytes

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP01-009 / SB-CP01-009-C001` or M12 master authority `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP01-009-C001` if needed. M12 master mode reuses the single master worktree.
6. No Desktop sibling clone/worktree.
7. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Make final ZIP container bytes deterministic for identical semantic inputs.

Normalize all ZIP metadata under our control:
- fixed entry ordering from SB-CP01-005;
- fixed timestamp policy independent of host clock;
- fixed compression method/level;
- fixed filename encoding;
- fixed file mode/external attributes;
- no comments, host paths, OS-specific extras or nondeterministic extra fields;
- canonical JSON bytes.

Build the same pack repeatedly in separate directories/processes and require identical bytes and identical final SHA-256.

If Python/ZIP implementation exposes an unavoidable nondeterministic field, document it and fail this child rather than silently weakening the deterministic-bytes contract.

## Verification and publication

Run focused tests, all prior M12 child regressions, M11 regressions, governance, full pytest, compileall, and `git diff --check`.

Create/update builder log:
`.hiveai/codex-logs/SB-CP01-009-C001_DETERMINISTIC_SCRUBPACK_BYTES_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

If green:
- commit implementation;
- commit child log separately;
- fetch/prune;
- normal non-force push to `main`;
- verify 0/0 parity.

Standalone mode: stop for ChatGPT audit.
M12 master mode: continue immediately to `SB-CP01-010-C001` without human handoff.