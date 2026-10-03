# SB-CP00-001-C001 — Content Platform Control-Plane Boundary

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Tracker:
root `TASKS.md`

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory path, repository identity, branch, origin, HEAD, dirty state, stashes, and worktrees.
2. Fetch/prune current `origin/main`.
3. Read task authority from GitHub/`origin/main:TASKS.md`; require `SB-CP00-001 / SB-CP00-001-C001`.
4. Preserve legitimate owner-local dirty work. Do not reset, clean, stash, rebase, force, overwrite, or discard it.
5. If the persistent checkout cannot be safely synchronized, use only an explicitly authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\SB-CP00-001-C001`, based on current `origin/main`.
6. Do not create a Desktop sibling clone/worktree.
7. Stop if incoming remote changes overlap implementation scope ambiguously.

## Goal

Establish the first canonical Content Platform control-plane project boundary required by M11:

`SB-CP00-001 — Establish content_pipeline/ separate publisher/control-plane project.`

This task creates the architecture/skeleton only. It does not implement live remote publishing, credentials, CDN/storage, runtime download, or store release.

## Required architecture

Create a canonical root-level:
`content_pipeline/`

It must be separate from:
- gameplay/runtime code;
- `level_factory/` Godot Studio shell;
- current Factory generation/solver internals.

The boundary must make it mechanically clear that:
- Level Factory produces accepted declarative content/evidence;
- Content Platform packages/validates/publishes/promotes content;
- Scrubbots runtime consumes only approved declarative output through later separately authorized milestones.

## Required project skeleton

Provide at minimum:
- project/package entry boundary;
- versioned configuration/schema location;
- staging/production environment abstraction placeholders;
- provider adapter interface placeholder;
- validation-only/dry-run entry placeholder;
- publish/promote/rollback orchestration boundaries as interfaces only;
- audit/report/evidence output boundary;
- tests for import/boundary behavior;
- documentation describing ownership and prohibited dependencies.

Do not implement provider-specific network mutation yet.

## Hard prohibitions

`content_pipeline/` must not:
- import Godot gameplay/runtime code;
- import Scrubbots runtime implementation;
- embed credentials/secrets;
- publish remote content yet;
- mutate staging or production;
- execute arbitrary remote code;
- bypass root TASKS governance;
- duplicate Level Factory generator/solver logic;
- become a second tracker.

## Dependency direction

Allowed:
- content_pipeline consumes stable declarative Level Factory output/contracts through explicit narrow interfaces.

Forbidden:
- Level Factory product core depending on content_pipeline publisher implementation;
- game runtime importing publisher/control-plane code;
- content_pipeline reaching into private generator internals.

Add static/import regressions that fail if forbidden directions appear.

## Tests

Required:
- package/import smoke;
- clean-checkout project existence;
- no secret/config credential material;
- no network mutation in this milestone;
- no forbidden runtime/game imports;
- no reverse dependency from Level Factory core;
- no second tracker/control-plane task ledger;
- deterministic configuration/schema serialization where applicable;
- compileall;
- full pytest;
- git diff --check.

## Builder log

Create before product edits:
`.hiveai/codex-logs/SB-CP00-001-C001_CONTENT_PLATFORM_CONTROL_PLANE_BOUNDARY_CODEX_LOG.md`

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.

## Publication

After all gates pass:
- commit implementation;
- commit builder log separately;
- fetch/prune;
- normal non-force push to Level Factory `main`;
- verify local/remote 0/0;
- stop for independent ChatGPT audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-001-C001_CONTENT_PLATFORM_CONTROL_PLANE_BOUNDARY_CODEX_LOG.md
