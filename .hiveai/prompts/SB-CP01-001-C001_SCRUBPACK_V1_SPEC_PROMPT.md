# SB-CP01-001-C001 — Define Versioned .scrubpack Spec

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP01-001 / SB-CP01-001-C001` or M12 master authority `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP01-001-C001` if needed. M12 master mode reuses the single master worktree.
6. No Desktop sibling clone/worktree.
7. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Define the canonical versioned `.scrubpack` V1 container contract under `content_pipeline/`.

V1 must be a ZIP-based data container with a fixed declarative layout. Define at minimum:
- extension `.scrubpack`;
- pack manifest path `pack.json`;
- per-level LevelData JSON paths;
- per-level supply-plan JSON paths;
- per-level metadata JSON paths;
- version fields and media/type identifiers;
- deterministic path grammar;
- no absolute paths, traversal, duplicate archive names, symlinks, executable entries, scripts, scenes, resources, shaders, plugins or native binaries.

Do not implement full packing yet beyond minimal spec fixtures/helpers needed to prove the contract.

The spec must explicitly preserve M11 declarative-only policy and state that V1 carries no executable behavior.

Document the container layout in `docs/content_platform/SCRUBPACK_V1_SPEC.md` and provide machine-readable schema/model definitions.

## Verification and publication

Run focused tests, all prior M12 child regressions, M11 regressions, governance, full pytest, compileall, and `git diff --check`.

Create/update builder log:
`.hiveai/codex-logs/SB-CP01-001-C001_SCRUBPACK_V1_SPEC_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

If green:
- commit implementation;
- commit child log separately;
- fetch/prune;
- normal non-force push to `main`;
- verify 0/0 parity.

Standalone mode: stop for ChatGPT audit.
M12 master mode: continue immediately to `SB-CP01-002-C001` without human handoff.