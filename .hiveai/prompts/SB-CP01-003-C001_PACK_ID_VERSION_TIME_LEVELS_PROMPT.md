# SB-CP01-003-C001 — Record Pack ID / Version / Time / Levels

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP01-003 / SB-CP01-003-C001` or M12 master authority `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP01-003-C001` if needed. M12 master mode reuses the single master worktree.
6. No Desktop sibling clone/worktree.
7. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Extend `pack.json` with canonical identity metadata:
- schema/spec version;
- non-empty pack ID;
- positive pack version;
- explicit `created_at_utc`;
- exact ordered level-ID membership;
- level count.

Time must be an explicit normalized UTC input, never hidden wall-clock authority in deterministic core logic.

Pack ID/version/time/membership must be immutable build inputs and survive inspect/unpack round-trip.

Reject malformed IDs, duplicate member IDs, invalid timestamps, zero/negative versions and count mismatches.

## Verification and publication

Run focused tests, all prior M12 child regressions, M11 regressions, governance, full pytest, compileall, and `git diff --check`.

Create/update builder log:
`.hiveai/codex-logs/SB-CP01-003-C001_PACK_ID_VERSION_TIME_LEVELS_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

If green:
- commit implementation;
- commit child log separately;
- fetch/prune;
- normal non-force push to `main`;
- verify 0/0 parity.

Standalone mode: stop for ChatGPT audit.
M12 master mode: continue immediately to `SB-CP01-004-C001` without human handoff.