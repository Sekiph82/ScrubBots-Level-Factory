# SB-CP01-005-C001 — Deterministic Pack Serialization / Order

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP01-005 / SB-CP01-005-C001` or M12 master authority `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP01-005-C001` if needed. M12 master mode reuses the single master worktree.
6. No Desktop sibling clone/worktree.
7. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Make all logical `.scrubpack` serialization deterministic before container-byte normalization.

Require:
- canonical JSON bytes with stable key ordering, separators and UTF-8;
- deterministic level ordering independent of input iteration order;
- deterministic archive member ordering;
- deterministic manifest member records;
- no filesystem enumeration order, wall clock, random UUID, locale, timezone or hash-map order in canonical output.

Pack membership must sort by an explicit canonical key defined by the spec, not accidental source path order.

Equivalent semantic inputs presented in different order must produce identical logical member bytes/order.

## Verification and publication

Run focused tests, all prior M12 child regressions, M11 regressions, governance, full pytest, compileall, and `git diff --check`.

Create/update builder log:
`.hiveai/codex-logs/SB-CP01-005-C001_DETERMINISTIC_PACK_SERIALIZATION_ORDER_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

If green:
- commit implementation;
- commit child log separately;
- fetch/prune;
- normal non-force push to `main`;
- verify 0/0 parity.

Standalone mode: stop for ChatGPT audit.
M12 master mode: continue immediately to `SB-CP01-006-C001` without human handoff.