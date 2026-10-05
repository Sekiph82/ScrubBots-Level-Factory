# SB-CP01-002-C001 — Package Declarative Levels Only

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP01-002 / SB-CP01-002-C001` or M12 master authority `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP01-002-C001` if needed. M12 master mode reuses the single master worktree.
6. No Desktop sibling clone/worktree.
7. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Implement the first local `.scrubpack` builder using the V1 spec.

Accepted payload families are only:
- LevelData V1;
- `scrubbots.level_supply_plan.v1`;
- `scrubbots.level.metadata.v1`.

Every payload must pass the existing M11 Content Boundary + payload validator before entering a pack.

V1 must reject images, scripts, scenes/resources, shaders, plugins/addons, binaries, arbitrary files, unknown content types and unknown archive paths.

The builder must operate locally only. No upload, CDN, manifest publication, game runtime or credentials.

Use explicit input objects/paths and return immutable build evidence. Do not silently discover unrelated files.

## Verification and publication

Run focused tests, all prior M12 child regressions, M11 regressions, governance, full pytest, compileall, and `git diff --check`.

Create/update builder log:
`.hiveai/codex-logs/SB-CP01-002-C001_PACKAGE_DECLARATIVE_LEVELS_ONLY_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

If green:
- commit implementation;
- commit child log separately;
- fetch/prune;
- normal non-force push to `main`;
- verify 0/0 parity.

Standalone mode: stop for ChatGPT audit.
M12 master mode: continue immediately to `SB-CP01-003-C001` without human handoff.