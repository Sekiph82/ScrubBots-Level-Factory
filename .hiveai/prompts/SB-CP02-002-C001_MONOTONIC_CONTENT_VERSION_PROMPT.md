# SB-CP02-002-C001 — schema_version + Monotonic content_version

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP02-002 / SB-CP02-002-C001` or M13 master authority `.hiveai/prompts/M13_CP02_001_012_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all legitimate owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard it.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP02-002-C001` if needed. M13 master mode reuses the single master worktree.
6. Do not create a Desktop sibling clone/worktree.
7. Require the execution worktree clean and 0/0 with `origin/main` before edits. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Extend V1 manifest identity with required positive integer `content_version`.

Rules:
- `schema_version` remains exactly 1;
- `content_version` must be a real integer, not bool, >= 1;
- deterministic successor validation must require a new manifest version to be strictly greater than the prior accepted content version;
- gaps are allowed; contiguity is not required;
- equal or lower content versions fail closed;
- version comparison must be numeric, never lexicographic;
- same content_version must not be treated as a new publishable revision even if bytes differ.

Add a pure local successor/check API with deterministic reason codes.

Do not persist history yet; SB-CP02-010 owns history. Do not publish remotely.

## Verification and publication

Run focused tests, all prior M13 child regressions, M12/M11 regressions, governance/tracker tests, full `python -m pytest -q`, compileall, schema parse, and `git diff --check`.

Create/update the distinct child builder log:
`.hiveai/codex-logs/SB-CP02-002-C001_MONOTONIC_CONTENT_VERSION_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

If green, commit implementation, commit child log separately, fetch/prune, normal non-force push to `main`, verify 0/0 parity. Standalone mode stops for audit. M13 master mode continues immediately to `SB-CP02-003-C001`.
