# SB-CP01-008-C001 — Safe Unpack / Inspect Tooling

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP01-008 / SB-CP01-008-C001` or M12 master authority `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP01-008-C001` if needed. M12 master mode reuses the single master worktree.
6. No Desktop sibling clone/worktree.
7. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Implement local read-only `.scrubpack` inspection plus safe optional extraction.

Inspection must verify:
- ZIP/container validity;
- exact allowed member paths;
- one `pack.json`;
- manifest/member consistency;
- member SHA-256;
- level triplet completeness;
- duplicate/collision absence;
- supported V1 schema.

Extraction must:
- reject absolute paths, `..`, drive/UNC escapes, symlinks and special files;
- never execute/import/load payloads;
- extract only validated allowed members beneath an explicit destination;
- avoid overwriting unrelated existing files unless an explicit safe mode is separately defined and tested.

Provide human-readable and machine-readable inspect result.

No network/provider/runtime behavior.

## Verification and publication

Run focused tests, all prior M12 child regressions, M11 regressions, governance, full pytest, compileall, and `git diff --check`.

Create/update builder log:
`.hiveai/codex-logs/SB-CP01-008-C001_SAFE_UNPACK_INSPECT_TOOLING_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

If green:
- commit implementation;
- commit child log separately;
- fetch/prune;
- normal non-force push to `main`;
- verify 0/0 parity.

Standalone mode: stop for ChatGPT audit.
M12 master mode: continue immediately to `SB-CP01-009-C001` without human handoff.