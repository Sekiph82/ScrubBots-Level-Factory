# SB-CP02-001-C001 — Define Versioned Remote Manifest V1 Schema

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP02-001 / SB-CP02-001-C001` or M13 master authority `.hiveai/prompts/M13_CP02_001_012_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all legitimate owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard it.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP02-001-C001` if needed. M13 master mode reuses the single master worktree.
6. Do not create a Desktop sibling clone/worktree.
7. Require the execution worktree clean and 0/0 with `origin/main` before edits. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Define the local canonical V1 remote-content manifest model for future publishing/runtime consumption.

This child defines schema/model authority only. It does not publish, upload, download, contact a provider, or modify the game.

Create a versioned root contract under `content_pipeline/` with:
- schema identity `scrubbots.content.manifest.v1`;
- integer `schema_version = 1`;
- closed root object;
- deterministic `packs` collection;
- deterministic `levels` collection;
- room for later M13 fields only through explicit versioned schema evolution, never arbitrary extension properties.

Provide:
- Python immutable model types;
- deterministic `to_dict()`;
- JSON Schema draft 2020-12;
- documentation under `docs/content_platform/`;
- canonical empty/minimal V1 fixture for tests.

Manifest data must remain declarative. No executable/script/plugin/resource/native fields, provider credentials, endpoint secrets or runtime code.

Do not implement `content_version`, compatibility, disable/schedule/history semantics beyond placeholders required for a coherent V1 root. Those belong to later children.

## Verification and publication

Run focused tests, all prior M13 child regressions, M12/M11 regressions, governance/tracker tests, full `python -m pytest -q`, compileall, schema parse, and `git diff --check`.

Create/update the distinct child builder log:
`.hiveai/codex-logs/SB-CP02-001-C001_REMOTE_MANIFEST_V1_SCHEMA_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

If green:
- commit implementation;
- commit child log separately;
- fetch/prune;
- normal non-force push to `main`;
- verify execution HEAD == `origin/main`, 0/0 divergence, clean worktree.

Standalone mode: stop for ChatGPT audit.
M13 master mode: continue immediately to `SB-CP02-002-C001` without human handoff.