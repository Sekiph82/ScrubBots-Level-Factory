# SB-CP00-009-C001 - Content Platform GitHub Coordination

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent sequence:
`SB-CP00-001..008` must be implemented and green before this child begins in M11 master mode.

## FIRST OPERATION - mandatory local <-> GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory path, repository identity, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Fetch/prune current `origin/main`.
3. Read task authority from GitHub/`origin/main:TASKS.md`. Accept either standalone authority for `SB-CP00-009 / SB-CP00-009-C001`, or the explicit M11 master authority `.hiveai/prompts/M11_CP00_003_009_MASTER_IMPLEMENTATION_PROMPT.md` that lists this child in sequence.
4. Preserve legitimate owner-local dirty work. Do not reset, clean, auto-stash, rebase, force, overwrite, restore, or discard it.
5. In standalone mode, if the persistent checkout cannot be safely synchronized, use only an explicitly authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\SB-CP00-009-C001`, based on current `origin/main`.
6. In M11 master mode, reuse the single master execution worktree. Do not create another child worktree.
7. Do not create a Desktop sibling clone/worktree.
8. Stop only if repository identity, remote authority, or safe preservation is ambiguous.

## Goal

Implement:

`SB-CP00-009 - Content Pipeline GitHub coordination under ChatGPT-owned root tracker.`

This is a governance/migration closure. It must formalize Content Platform coordination without creating a second roadmap, tracker, dashboard, or task ledger.

## Canonical ownership contract

Document and mechanically guard:
- root `TASKS.md` is the only live LF/CP tracker;
- ChatGPT owns prompts, audit criteria, strict audits, and root tracker lifecycle state;
- Codex owns implementation/testing and child builder logs only;
- Codex must not mark itself PASS or edit audit results;
- every implementation/remediation prompt begins with local <-> GitHub synchronization;
- builder logs are evidence archives, not trackers;
- Content Pipeline work publishes to this canonical repository unless a future owner prompt explicitly authorizes another repository;
- game-runtime implementation remains in `Sekiph82/Scrubbots`.

## GitHub evidence contract

Add a small versioned, deterministic local evidence/receipt model or schema for Content Platform builder publication records containing only immutable facts such as:
- task ID;
- prompt path;
- builder-log path;
- repository identity;
- branch;
- base/implementation/log/final commit SHAs;
- test summary;
- publication parity result.

It must NOT contain:
- mutable task status authority;
- acceptance/PASS authority;
- owner secrets;
- a duplicate roadmap.

This evidence contract is optional as code if a schema/document + tests is cleaner, but it must be mechanically validated.

## Repository hygiene

Add tests/guards that fail if Content Pipeline introduces:
- another `TASKS.md`;
- roadmap/dashboard/task-state files under `content_pipeline/`;
- code that writes root `TASKS.md` or `.hiveai/audits/**`;
- hard-coded credentials;
- a second canonical repository declaration for LF/CP tracking.

Do not scan generated/cache folders as governance truth.

## Main/branch behavior

Document:
- normal work publishes by non-force update to `main` after fetch/prune and divergence checks unless a specific prompt authorizes branch/PR behavior;
- no force push;
- no silent reset/rebase/discard of owner-local work;
- temp worktrees are allowed only under prompt-authorized `%TEMP%` locations.

Do not implement GitHub API mutation automation or credentials in this task.

## M11 closure evidence

This child must include a focused regression that all M11 Content Platform child builder-log target paths for SB-CP00-003..009 are distinct and under `.hiveai/codex-logs/`, while root `TASKS.md` remains sole tracker.

Do not write the audits. ChatGPT will independently audit each child after the master run.

## Tests

Required:
- root tracker sole-authority guard;
- no nested tracker/roadmap/dashboard;
- Codex-write boundary guard;
- versioned evidence receipt validation;
- no acceptance field in builder receipt;
- no GitHub credential/API mutation;
- distinct M11 child log paths;
- prior SB-CP00-001..008 regressions;
- governance, full pytest, compileall, diff check.

## Builder log

Create:
`.hiveai/codex-logs/SB-CP00-009-C001_CONTENT_PLATFORM_GITHUB_COORDINATION_CODEX_LOG.md`

Do not edit root `TASKS.md` or audits.

## Publication

After all gates pass:
- commit implementation;
- commit this child builder log separately;
- fetch/prune;
- normal non-force update to Level Factory `main`;
- verify execution HEAD == `origin/main` and divergence 0/0.

Standalone mode: stop for independent ChatGPT audit.

M11 master mode: return control to the master prompt for final milestone verification. Do not wait for human review and do not edit `TASKS.md`.

## Final response

Standalone mode: return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-009-C001_CONTENT_PLATFORM_GITHUB_COORDINATION_CODEX_LOG.md

M11 master mode: no user handoff here. Return control to the master.