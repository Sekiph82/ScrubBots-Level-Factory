# SB-CP00-005-C001 - Versioned Auditable Publish/Promotion/Rollback State

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent sequence:
`SB-CP00-001..004` must be implemented and green before this child begins in M11 master mode.

## FIRST OPERATION - mandatory local <-> GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory path, repository identity, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Fetch/prune current `origin/main`.
3. Read task authority from GitHub/`origin/main:TASKS.md`. Accept either standalone authority for `SB-CP00-005 / SB-CP00-005-C001`, or the explicit M11 master authority `.hiveai/prompts/M11_CP00_003_009_MASTER_IMPLEMENTATION_PROMPT.md` that lists this child in sequence.
4. Preserve legitimate owner-local dirty work. Do not reset, clean, auto-stash, rebase, force, overwrite, restore, or discard it.
5. In standalone mode, if the persistent checkout cannot be safely synchronized, use only an explicitly authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\SB-CP00-005-C001`, based on current `origin/main`.
6. In M11 master mode, reuse the single master execution worktree. Do not create another child worktree.
7. Do not create a Desktop sibling clone/worktree.
8. Stop only if repository identity, remote authority, or safe preservation is ambiguous.

## Goal

Implement:

`SB-CP00-005 - Versioned/auditable publish/promotion/rollback state.`

Create a local deterministic control-plane state machine and append-only audit-event model. No remote mutation is allowed.

## Required state model

Represent at minimum the lifecycle concepts:
- candidate/draft;
- validated or dry-run-ready;
- staged;
- production-promoted;
- rolled back or superseded;
- failed/aborted where needed.

Exact state names are implementation-defined, but transition semantics must be explicit and fail closed.

Hard rules:
- every state record/event is versioned;
- every transition references exact content identity/digest and environment;
- history is append-only;
- rollback never erases history;
- promotion never mutates a staging record into production in place;
- invalid skips, such as draft directly to production, reject;
- duplicate transition/event IDs reject;
- stale expected-state transitions reject;
- replaying the same immutable event is idempotent or rejected deterministically, never double-applied;
- core state logic must not depend on wall-clock time or randomness. If timestamps/sequence IDs exist, they must be explicit inputs.

## Audit evidence

Provide deterministic serialization of:
- current state;
- append-only event;
- transition result.

An auditor must be able to reconstruct current logical state by replaying the event sequence and detect tampering/order violations.

Do not build a database service in this task. A pure in-memory/file-serializable model is sufficient.

## Rollback semantics

Rollback must reference a known prior content version/identity and produce a new auditable transition/event. It must not delete later history.

No remote object rollback is performed.

## Architecture preservation

Preserve SB-CP00-001..004 and all no-network/no-secret/no-runtime boundaries.

Do not implement provider mutation or pack/manifest publishing.

## Tests

Required:
- legal transition table;
- illegal transition rejection;
- direct-to-production rejection;
- staging/production environment consistency;
- append-only event replay;
- duplicate event/transition rejection;
- stale expected-state rejection;
- deterministic serialization;
- rollback preserves history and references known prior identity;
- tampered/reordered history detection;
- no wall-clock/random dependency in core;
- prior SB-CP00-001..004 regressions green.

Run focused tests, governance, full pytest, compileall, and git diff --check.

## Builder log

Create:
`.hiveai/codex-logs/SB-CP00-005-C001_VERSIONED_AUDITABLE_RELEASE_STATE_CODEX_LOG.md`

Do not edit root `TASKS.md` or audits.

## Publication

After all gates pass:
- commit implementation;
- commit this child builder log separately;
- fetch/prune;
- normal non-force update to Level Factory `main`;
- verify execution HEAD == `origin/main` and divergence 0/0.

Standalone mode: stop for independent ChatGPT audit.

M11 master mode: do not edit root `TASKS.md`, do not write an audit, do not wait for human review, and continue directly to `SB-CP00-006-C001`.

## Final response

Standalone mode: return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-005-C001_VERSIONED_AUDITABLE_RELEASE_STATE_CODEX_LOG.md

M11 master mode: no user handoff here. Return control to the master prompt.